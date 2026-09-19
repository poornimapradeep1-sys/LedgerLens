"""
pipeline.py

Orchestration layer (19-20 Sep phase: "exception handling + integrate
complete AI pipeline"). Its ONLY job is to call the other modules in
order across MANY files and hold the whole batch together even when
individual files fail:

    vision_extractor.extract_job_card()      (per job card image)
    vision_extractor.extract_account_book()  (per account book image)
        -> verifier.verify_all()
        -> database.save_run()

No extraction/matching/decision logic belongs here — this file is
deliberately thin. If a number is wrong, the bug is in vision_extractor.py.
If a verdict is wrong, the bug is in verifier.py. If a whole run crashes
instead of degrading gracefully, the bug is in here.

FAIL-SOFT DESIGN: one bad/corrupt image must not kill the rest of the
batch. Every per-image extraction is wrapped so a failure is recorded as
its own result row ("EXTRACTION_FAILED") instead of raising and aborting
everything else that would have succeeded.
"""

from vision_extractor import extract_job_card, extract_account_book_reconciled, MissingApiKeyError
import verifier
import database

ACCOUNT_BOOK_RUNS = 3  # cross-run reconciliation passes per account book image — see vision_extractor.py


def run_batch(
    job_card_paths: list,
    account_book_paths: list,
    confidence_threshold: float = verifier.CONFIDENCE_THRESHOLD_DEFAULT,
    progress_callback=None,
    should_stop=None,
) -> dict:
    """
    Runs the full pipeline over a batch of job card images and account
    book images, saves the run to the database, and returns a summary.

    Account book pages are read via extract_account_book_reconciled(),
    which makes ACCOUNT_BOOK_RUNS extraction passes per image and only
    trusts a serial number's total if every pass agrees — see that
    function's docstring for why a single pass isn't reliable enough on
    dense ledger pages.

    progress_callback(done, total, message): optional, called after each
    extraction pass (including each of the ACCOUNT_BOOK_RUNS passes per
    account book image) so a UI progress bar reflects the real work.

    should_stop(): optional, checked before starting each image's
    extraction. A single in-flight API call can't be interrupted
    mid-request, but the batch stops picking up new images the moment
    this returns True — whatever was already extracted is still
    verified and saved (same fail-soft spirit as one bad image not
    aborting the rest of the batch).

    Returns:
        {
          "run_id": int,
          "results": [ {..verdict.., "source_image": path}, ... ],
          "failed_extractions": [ {"image": path, "error": str}, ... ],
          "stopped_early": bool,
        }
    """
    total_steps = len(job_card_paths) + len(account_book_paths) * ACCOUNT_BOOK_RUNS
    done_steps = 0

    def _tick(message: str):
        nonlocal done_steps
        done_steps += 1
        if progress_callback:
            progress_callback(done_steps, total_steps, message)

    job_cards = []
    account_rows = []
    failed_extractions = []
    stopped_early = False

    for path in job_card_paths:
        if should_stop and should_stop():
            stopped_early = True
            break
        try:
            card = extract_job_card(path)
            if card is None:
                failed_extractions.append({"image": path, "error": "Could not parse job card response."})
            else:
                card["source_image"] = path
                job_cards.append(card)
        except MissingApiKeyError:
            raise
        except Exception as e:
            failed_extractions.append({"image": path, "error": str(e)})
        _tick(f"Read job card: {path}")

    for path in account_book_paths:
        if should_stop and should_stop():
            stopped_early = True
            break
        try:
            rows = extract_account_book_reconciled(
                path,
                runs=ACCOUNT_BOOK_RUNS,
                progress_callback=lambda done, total: _tick(
                    f"Reading account book page ({done}/{total} verification passes): {path}"
                ),
            )
            if not rows:
                failed_extractions.append({"image": path, "error": "No rows extracted from account book page."})
            for row in rows:
                row["source_image"] = path
                account_rows.append(row)
        except MissingApiKeyError:
            raise
        except Exception as e:
            failed_extractions.append({"image": path, "error": str(e)})

    results = verifier.verify_all(job_cards, account_rows, confidence_threshold)

    for r, card in zip(results, job_cards):
        r["source_image"] = card.get("source_image")

    database.init_db()
    run_id = database.save_run(
        results,
        job_card_count=len(job_card_paths),
        account_book_image_count=len(account_book_paths),
    )

    return {
        "run_id": run_id,
        "results": results,
        "failed_extractions": failed_extractions,
        "stopped_early": stopped_early,
    }


def summarize(results: list) -> dict:
    """Counts results by status — used by both the dashboard and the
    end-of-batch notification popup so they agree on the same numbers."""
    counts = {"VERIFIED": 0, "AMOUNT_MISMATCH": 0, "MISSING_RECORD": 0, "MANUAL_REVIEW": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return counts
