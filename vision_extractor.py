"""
vision_extractor.py

Boxes 1 and 2 on the architecture diagram (see PROJECT_SCOPE.md):
  Box 1: Job Card Images    -> Vision/OCR -> extract_job_card()
  Box 2: Account Book Images -> Vision/OCR -> extract_account_book()

This is the only file that talks to the AI model. Matching/verification
logic (deterministic, no AI) lives in verifier.py.

IMPORTANT: the Gemini client is created lazily (get_client()), not at
import time. A GUI app needs to be able to import this module, show its
window, and THEN ask the user for an API key if one isn't set yet —
crashing at import time (like the old CLI-only version did) would mean
the window never opens.
"""

import os
import json
import time
from google import genai
from google.genai import types
from google.genai import errors


MODEL_NAME = "gemini-3.6-flash"

_client = None


class MissingApiKeyError(Exception):
    """Raised when GEMINI_API_KEY isn't set. Callers (e.g. the GUI) should
    catch this and prompt the user, instead of the process crashing."""


def get_client():
    """
    Lazily creates (and caches) the Gemini client. Reads the key fresh
    from the environment each time it's called with no cached client, so
    a GUI can set os.environ["GEMINI_API_KEY"] after prompting the user
    and then call this again successfully in the same run.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise MissingApiKeyError(
            "No GEMINI_API_KEY set. Get a free key at "
            "https://aistudio.google.com/app/apikey and set it, e.g. "
            'PowerShell: $env:GEMINI_API_KEY="your_key_here"'
        )
    _client = genai.Client(api_key=api_key)
    return _client


def reset_client():
    """Forces get_client() to re-read the API key next call. Used after
    the GUI saves a new/changed key so it takes effect immediately."""
    global _client
    _client = None


JOB_CARD_PROMPT = """
You are reading a handwritten salon JOB CARD image.

Extract ONLY the following into valid JSON, with no extra text before
or after the JSON:

{
  "serial_number": "<the Serial No. field, as text>",
  "client_name": "<Full Name field>",
  "contact_number": "<Contact Details / phone number field, digits only>",
  "line_items": [
    {"service": "<service name from the table>", "sale_amount": <that row's Sale column amount as a number>}
  ],
  "service_total": <the Service Total amount as written at the bottom, as a number, no currency symbol or commas>,
  "confidence": <your confidence from 0.0 to 1.0 that every field above is correct>
}

Include one entry in "line_items" for every row in the service table
that has a Sale amount filled in, even if other columns in that row are
blank.

Handwritten digits are frequently confused with each other in this kind
of document (3 vs 8, 5 vs 8, 0 vs 6, 1 vs 7). Look carefully at each
digit's actual stroke shape rather than guessing from context, and do
not assume a loop or curl makes a digit an 8 unless you are genuinely
confident.

If any field is illegible or you are not confident, still fill it with
your best guess but LOWER the confidence score accordingly. Do not
invent a serial number or amount that isn't visibly written.
"""

ACCOUNT_BOOK_PROMPT = """
You are reading a handwritten ACCOUNT BOOK ledger page containing MANY
rows for different clients, stacked close together. It may contain
several client entries, and a single client's serial number may appear
with MORE THAN ONE amount line (e.g. multiple services logged
separately for the same visit or client) — extract every line
separately, do not merge or pre-sum them.

CRITICAL — row alignment: a serial number, client name, and amount that
belong together are always on the exact SAME horizontal row. In a dense
page like this it is easy for your eye to drift and pair an amount with
the row above or below it — before finalizing each line, re-check that
the amount you assigned actually sits on the same row as that serial
number and name, not an adjacent one.

Handwritten digits are frequently confused with each other (3 vs 8, 5
vs 8, 0 vs 6, 1 vs 7) — look at each digit's actual stroke shape.

Extract EVERY line you can identify into a JSON array, with no extra
text before or after the JSON:

[
  {
    "serial_number": "<serial number for this line>",
    "client_name": "<name associated with this line, if present>",
    "contact_number": "<phone number for this line, digits only, if present>",
    "amount": <the amount for this line as a number, or null if unclear>,
    "confidence": <0.0 to 1.0>
  }
]

If a line's amount is not clearly legible, or you are not sure it
belongs to that row, set "amount" to null and lower the confidence
rather than guessing.
"""


def _call_gemini(image_path: str, prompt: str, max_retries: int = 3) -> str:
    """
    Sends ONE image + ONE prompt to Gemini and returns the raw text.

    WHY temperature=0: we want the same, most-likely reading every time,
    not a different guess per run.

    WHY the retry loop: covers three distinct transient failure modes
    that a real batch run can hit (not just "server busy"):
      - ServerError (5xx): the API itself is temporarily down/overloaded.
      - ClientError with 429: rate limit / quota hit — back off longer.
      - Anything else: not retried, re-raised immediately (e.g. a bad
        request shouldn't be retried 3 times, it'll just fail 3 times).
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = image_path.split(".")[-1].lower()
    mime_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
    client = get_client()

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(temperature=0),
            )
            return response.text
        except errors.ServerError as e:
            if attempt == max_retries:
                raise
            wait_seconds = 5 * attempt
            print(f"[!] Server busy (attempt {attempt}/{max_retries}): {e}")
            print(f"    Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)
        except errors.ClientError as e:
            is_rate_limit = getattr(e, "code", None) == 429
            if not is_rate_limit or attempt == max_retries:
                raise
            wait_seconds = 15 * attempt
            print(f"[!] Rate limited (attempt {attempt}/{max_retries}): {e}")
            print(f"    Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)


def _clean_json_text(raw_text: str) -> str:
    """Gemini sometimes wraps JSON in ```json fences — strip those off."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def _validate_job_card(data: dict) -> dict:
    """
    Defensive schema check: makes sure the fields the rest of the
    pipeline depends on actually exist and are the right type, so a
    malformed AI response fails loudly here instead of causing a
    confusing crash (or silent wrong comparison) deep in verifier.py.
    """
    required = ["serial_number", "client_name", "contact_number", "service_total", "confidence"]
    for field in required:
        if field not in data:
            raise ValueError(f"Job card JSON missing required field: {field}")

    data["serial_number"] = str(data["serial_number"]).strip()
    data["client_name"] = str(data.get("client_name") or "").strip()
    data["contact_number"] = str(data.get("contact_number") or "").strip()

    try:
        data["service_total"] = float(data["service_total"]) if data["service_total"] is not None else None
    except (TypeError, ValueError):
        raise ValueError(f"Job card service_total is not numeric: {data['service_total']!r}")

    try:
        data["confidence"] = float(data["confidence"])
    except (TypeError, ValueError):
        data["confidence"] = 0.0

    _cross_check_job_card_total(data)
    return data


LINE_ITEM_TOLERANCE = 1.0


def _cross_check_job_card_total(data: dict) -> None:
    """
    Independent sanity check: the line items on the card SHOULD sum to
    the stated Service Total. If they don't, that's a strong signal the
    total (or a line item) was misread — stronger than the model's own
    self-reported confidence, which can be high even when wrong (e.g. a
    handwritten 5 that looks like an 8). Mutates `data` in place, adding
    "line_item_sum" and "cross_check_mismatch", and caps confidence down
    when they disagree so verifier.py's existing confidence-threshold
    check routes it to MANUAL_REVIEW instead of auto-deciding on a
    number that doesn't add up.
    """
    line_items = data.get("line_items") or []
    amounts = []
    for item in line_items:
        try:
            amounts.append(float(item.get("sale_amount")))
        except (TypeError, ValueError):
            continue

    if not amounts or data.get("service_total") is None:
        data["line_item_sum"] = None
        data["cross_check_mismatch"] = False
        return

    line_item_sum = round(sum(amounts), 2)
    data["line_item_sum"] = line_item_sum
    mismatch = abs(line_item_sum - data["service_total"]) > LINE_ITEM_TOLERANCE
    data["cross_check_mismatch"] = mismatch
    if mismatch:
        data["confidence"] = min(data["confidence"], 0.3)


def _validate_account_book_row(row: dict) -> dict:
    """Same defensive validation as _validate_job_card, for one row."""
    required = ["serial_number", "amount", "confidence"]
    for field in required:
        if field not in row:
            raise ValueError(f"Account book row missing required field: {field}")

    row["serial_number"] = str(row["serial_number"]).strip()
    row["client_name"] = str(row.get("client_name") or "").strip()
    row["contact_number"] = str(row.get("contact_number") or "").strip()

    if row["amount"] is not None:
        try:
            row["amount"] = float(row["amount"])
        except (TypeError, ValueError):
            raise ValueError(f"Account book amount is not numeric: {row['amount']!r}")

    try:
        row["confidence"] = float(row["confidence"])
    except (TypeError, ValueError):
        row["confidence"] = 0.0

    return row


def extract_job_card(image_path: str) -> dict:
    """
    Box 1: Job Card Image -> Serial + Name + Contact + Service Total.

    Returns a validated dict, e.g.:
        {"serial_number": "1244", "client_name": "Asha",
         "contact_number": "9000000000", "service_total": 30500.0,
         "confidence": 0.9}

    Returns None (and prints why) if the response couldn't be parsed
    or didn't match the expected schema — callers must handle None.
    """
    raw = _call_gemini(image_path, JOB_CARD_PROMPT)
    try:
        data = json.loads(_clean_json_text(raw))
        return _validate_job_card(data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[!] Job card extraction failed for {image_path}: {e}")
        print(f"    Raw response was: {raw!r}")
        return None


def extract_account_book(image_path: str) -> list:
    """
    Box 2: Account Book Image -> list of ledger line records.

    Returns a validated list of dicts (possibly empty). A parse/schema
    failure on the WHOLE response returns []; a failure on a single row
    within an otherwise-valid array skips just that row (logged) so one
    bad row doesn't discard an entire page's worth of good ones.
    """
    raw = _call_gemini(image_path, ACCOUNT_BOOK_PROMPT)
    try:
        rows = json.loads(_clean_json_text(raw))
        if not isinstance(rows, list):
            raise ValueError("Expected a JSON array of rows")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[!] Account book extraction failed for {image_path}: {e}")
        print(f"    Raw response was: {raw!r}")
        return []

    validated = []
    for i, row in enumerate(rows):
        try:
            validated.append(_validate_account_book_row(row))
        except ValueError as e:
            print(f"[!] Skipping malformed row {i} in {image_path}: {e}")
    return validated


def _sum_rows_by_serial(rows: list) -> dict:
    """Groups raw rows by serial, returns {serial: total_or_None}. A
    serial's total is None if ANY of its rows in this run had a null
    (illegible) amount — that run can't vouch for this serial at all."""
    grouped = {}
    for row in rows:
        grouped.setdefault(row["serial_number"], []).append(row)

    totals = {}
    for serial, serial_rows in grouped.items():
        if any(r["amount"] is None for r in serial_rows):
            totals[serial] = None
        else:
            totals[serial] = round(sum(r["amount"] for r in serial_rows), 2)
    return totals


def extract_account_book_reconciled(image_path: str, runs: int = 3, progress_callback=None) -> list:
    """
    Runs extract_account_book() `runs` times on the SAME image and
    reconciles per-serial totals across runs, instead of trusting a
    single pass.

    WHY: empirically (see README.md), extraction on a dense multi-row
    handwritten ledger page is NOT perfectly stable even at
    temperature=0 — repeated runs can attribute an amount to the wrong
    serial number, and a wrong reading can still carry high
    self-reported confidence. Cross-run agreement on a serial's SUMMED
    total is a far stronger correctness signal than any single run's
    confidence score.

    For a serial where every run agrees on the same total: returns that
    serial's actual line rows (from one of the agreeing runs), with
    confidence boosted to reflect the cross-run confirmation.

    For a serial where runs disagree (different totals, or the serial
    missing from some runs): returns ONE placeholder row with
    amount=None, confidence=0.0 — verifier.py's existing
    illegible-amount / low-confidence rules already route that to
    MANUAL_REVIEW, so no changes to verifier.py are needed.

    progress_callback(done, total), if given, is called after each of
    the `runs` individual extraction passes (not just once per image),
    so a UI progress bar can reflect the real work being done.
    """
    run_rows = []
    for i in range(runs):
        run_rows.append(extract_account_book(image_path))
        if progress_callback:
            progress_callback(i + 1, runs)

    run_totals = [_sum_rows_by_serial(rows) for rows in run_rows]

    all_serials = set()
    for totals in run_totals:
        all_serials.update(totals.keys())

    def _first_value(serial, field):
        for rows in run_rows:
            for r in rows:
                if r["serial_number"] == serial:
                    return r.get(field, "")
        return ""

    reconciled = []
    for serial in all_serials:
        values = [totals.get(serial) for totals in run_totals]
        is_stable = all(v is not None for v in values) and len(set(values)) == 1

        if is_stable:
            agreeing_run = next(rows for rows, totals in zip(run_rows, run_totals) if serial in totals)
            for row in agreeing_run:
                if row["serial_number"] == serial:
                    reconciled.append({**row, "confidence": max(row["confidence"], 0.9)})
        else:
            reconciled.append({
                "serial_number": serial,
                "client_name": _first_value(serial, "client_name"),
                "contact_number": _first_value(serial, "contact_number"),
                "amount": None,
                "confidence": 0.0,
            })

    return reconciled


if __name__ == "__main__":
    job_card = extract_job_card("1000138303.jpg")
    print("JOB CARD:", json.dumps(job_card, indent=2))

    account_rows = extract_account_book("1000138302.jpg")
    print("ACCOUNT BOOK ROWS:", json.dumps(account_rows, indent=2))
