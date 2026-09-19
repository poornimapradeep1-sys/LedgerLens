"""
verifier.py

Boxes 3 and 4 on the architecture diagram (see PROJECT_SCOPE.md):
  Box 3: Match & Compare -> group account book rows by serial, sum amounts
  Box 4: Verify & Decide -> VERIFIED / AMOUNT_MISMATCH / MISSING_RECORD /
                             MANUAL_REVIEW

IMPORTANT: this file contains NO AI calls. It only works with the JSON
dicts that vision_extractor.py already produced and validated. Matching
and comparing numbers is something plain Python is 100% reliable at, so
AI is kept out of it entirely.

MATCHING RULE (PROJECT_SCOPE.md section 4): a job card's service_total is
compared against the SUM of every account book row sharing that serial
number, not a single-row lookup — a serial number can legitimately have
multiple line items in the ledger (e.g. two services logged separately).

A small tolerance (AMOUNT_TOLERANCE) is applied to the comparison to
absorb harmless float rounding from JSON round-tripping — it is NOT meant
to mask real discrepancies, so it's kept tiny.
"""

CONFIDENCE_THRESHOLD_DEFAULT = 0.75
AMOUNT_TOLERANCE = 0.01


def group_account_book_by_serial(account_rows: list) -> dict:
    """
    Groups a flat list of account book rows (possibly from MANY page
    images) by serial_number, so verify_job_card() can look up "every
    row for this serial" in one place rather than re-scanning the full
    list per job card.

    Returns: {serial_number: [row, row, ...], ...}
    """
    grouped = {}
    for row in account_rows:
        serial = row.get("serial_number")
        grouped.setdefault(serial, []).append(row)
    return grouped


def verify_job_card(
    job_card: dict,
    account_rows_by_serial: dict,
    confidence_threshold: float = CONFIDENCE_THRESHOLD_DEFAULT,
) -> dict:
    """
    Takes ONE job card's extracted data and a serial-number-grouped
    lookup of ALL account book rows (from any number of account book
    images), and returns a verdict dict with a "status" of:

      VERIFIED         - serial found; job card total == summed rows.
      AMOUNT_MISMATCH  - serial found; totals differ.
      MISSING_RECORD   - serial does not appear in the account book.
      MANUAL_REVIEW    - confidence too low somewhere, or an account
                          book row's amount was illegible (null). We
                          never let low-confidence AI output silently
                          decide a financial match/mismatch.
    """
    serial = job_card.get("serial_number")

    if job_card.get("confidence", 0) < confidence_threshold:
        return {
            "serial_number": serial,
            "status": "MANUAL_REVIEW",
            "reason": "Job card reading confidence too low to trust.",
            "job_card_client": job_card.get("client_name"),
            "job_card_service_total": job_card.get("service_total"),
            "account_book_total": None,
        }

    matching_rows = account_rows_by_serial.get(serial)

    if not matching_rows:
        return {
            "serial_number": serial,
            "status": "MISSING_RECORD",
            "reason": "Serial number not found anywhere in the account book.",
            "job_card_client": job_card.get("client_name"),
            "job_card_service_total": job_card.get("service_total"),
            "account_book_total": None,
        }

    low_confidence_rows = [r for r in matching_rows if r.get("confidence", 0) < confidence_threshold]
    if low_confidence_rows:
        return {
            "serial_number": serial,
            "status": "MANUAL_REVIEW",
            "reason": f"{len(low_confidence_rows)} matching account book row(s) had low confidence.",
            "job_card_client": job_card.get("client_name"),
            "job_card_service_total": job_card.get("service_total"),
            "account_book_total": None,
            "account_book_line_count": len(matching_rows),
        }

    null_amount_rows = [r for r in matching_rows if r.get("amount") is None]
    if null_amount_rows:
        return {
            "serial_number": serial,
            "status": "MANUAL_REVIEW",
            "reason": f"{len(null_amount_rows)} matching account book row(s) had an illegible (null) amount.",
            "job_card_client": job_card.get("client_name"),
            "job_card_service_total": job_card.get("service_total"),
            "account_book_total": None,
            "account_book_line_count": len(matching_rows),
        }

    book_total = sum(r["amount"] for r in matching_rows)
    job_total = job_card.get("service_total")

    is_match = job_total is not None and abs(job_total - book_total) <= AMOUNT_TOLERANCE
    status = "VERIFIED" if is_match else "AMOUNT_MISMATCH"

    return {
        "serial_number": serial,
        "status": status,
        "reason": "Amounts match." if is_match else "Job card total does not match summed account book amount.",
        "job_card_client": job_card.get("client_name"),
        "job_card_service_total": job_total,
        "account_book_total": book_total,
        "account_book_line_count": len(matching_rows),
    }


def verify_all(
    job_cards: list,
    account_rows: list,
    confidence_threshold: float = CONFIDENCE_THRESHOLD_DEFAULT,
) -> list:
    """
    Runs verify_job_card() for every job card in the batch against the
    FULL combined pool of account book rows (from all account book
    images in the batch). Works for any number of job cards/pages.
    """
    grouped = group_account_book_by_serial(account_rows)
    return [verify_job_card(jc, grouped, confidence_threshold) for jc in job_cards]
