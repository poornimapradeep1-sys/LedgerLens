"""
notifier.py

Box 5 on the architecture diagram: end-of-batch abnormality notification.
Fires ONCE per batch run (not once per record) and summarizes every
result that isn't a clean VERIFIED.

Kept separate from main.py so the "what counts as an abnormality and how
it's summarized" logic can be tested/reused without needing a running
Qt application.
"""

from PySide6.QtWidgets import QMessageBox

ABNORMAL_STATUSES = {"AMOUNT_MISMATCH", "MISSING_RECORD", "MANUAL_REVIEW"}


def build_summary_text(results: list) -> str:
    abnormal = [r for r in results if r.get("status") in ABNORMAL_STATUSES]
    if not abnormal:
        return "All job cards verified successfully. No abnormalities found."

    lines = [f"{len(abnormal)} abnormal record(s) out of {len(results)} found:\n"]
    for r in abnormal:
        serial = r.get("serial_number", "?")
        status = r.get("status")
        reason = r.get("reason", "")
        lines.append(f"  • Serial {serial} — {status}: {reason}")
    return "\n".join(lines)


def show_batch_summary_popup(results: list, parent=None) -> None:
    """
    Shows ONE popup at the end of a batch run. Uses a warning icon if
    anything abnormal was found, an information icon otherwise, so the
    icon itself communicates the outcome at a glance.
    """
    abnormal_count = sum(1 for r in results if r.get("status") in ABNORMAL_STATUSES)
    text = build_summary_text(results)

    box = QMessageBox(parent)
    box.setWindowTitle("Verification Complete")
    if abnormal_count > 0:
        box.setIcon(QMessageBox.Warning)
    else:
        box.setIcon(QMessageBox.Information)
    box.setText(f"Batch finished: {len(results)} job card(s) processed.")
    box.setDetailedText(text)
    box.setInformativeText(
        "See details below." if abnormal_count > 0 else "No abnormalities found."
    )
    box.exec()
