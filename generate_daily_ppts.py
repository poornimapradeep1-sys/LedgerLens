"""
generate_daily_ppts.py

Builds ONE separate .pptx file per calendar day of the project (11 Sep
through 26 Sep 2026), for individual daily mentor check-ins, into
daily_ppts/. Each file is self-contained (its own cover + content
slide(s)) rather than one slide cut out of a shared deck.

Two days (11, 12 Sep) have REAL completed work and get full detail
slides. The rest get an honest status slide — several "upcoming" plan
phases were actually already finished early during the Day 1 build, so
those days say so explicitly rather than pretending nothing happened
yet; only 13-14 Sep (ongoing accuracy hardening) and 24-26 Sep
(packaging/final testing, genuinely not started) are left open.

Run directly: `python generate_daily_ppts.py`. Re-run any time to
regenerate (e.g. after a placeholder day becomes real work — update its
entry in DAY_PLAN below and re-run).
"""

import os
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from ppt_helpers import (
    new_presentation, add_slide, set_bg, textbox, bullets, rounded_box,
    day_header, footer, INDIGO, NAVY, TEXT_DARK, TEXT_GRAY, WHITE, LIGHT_BG,
    GREEN, GREEN_BG, AMBER, AMBER_BG, GRAY_BG,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_ppts")
SCREENSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ppt_screenshot.png")
os.makedirs(OUT_DIR, exist_ok=True)


def cover_slide(prs, day_num, date_label, title, kind):
    """kind: 'done' | 'ongoing' | 'upcoming' — colors the accent bar."""
    color = {"done": GREEN, "ongoing": INDIGO, "upcoming": AMBER}[kind]
    s = add_slide(prs)
    set_bg(s, NAVY)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.18), Inches(7.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    bar.shadow.inherit = False
    textbox(s, Inches(0.9), Inches(2.5), Inches(4), Inches(0.6), f"DAY {day_num}", size=28, bold=True, color=color)
    textbox(s, Inches(0.9), Inches(3.15), Inches(6), Inches(0.5), date_label, size=16, color=RGBColor(0x9C, 0xA3, 0xAF))
    textbox(s, Inches(0.9), Inches(3.7), Inches(11), Inches(1.2), title, size=30, bold=True, color=WHITE, line_spacing=1.1)
    textbox(s, Inches(0.9), Inches(6.8), Inches(9), Inches(0.4),
            "Job Card ↔ Account Book Verification System", size=11, color=RGBColor(0x6B, 0x72, 0x80))
    return s


DAY_PLAN = [
    # (day_num, date, plan_phase_label) — content built per-day below
    (1, "11 September 2026", "Problem, Architecture, Scope + Full System Build"),
    (2, "12 September 2026", "Accuracy Investigation & Fixes"),
    (3, "13 September 2026", "Job Card Extraction — Accuracy Hardening (continued)"),
    (4, "14 September 2026", "Job Card Extraction — Accuracy Hardening (continued)"),
    (5, "15 September 2026", "Account Book Extraction + Structured Output"),
    (6, "16 September 2026", "Account Book Extraction + Structured Output"),
    (7, "17 September 2026", "Record Matching + Amount Verification"),
    (8, "18 September 2026", "Record Matching + Amount Verification"),
    (9, "19 September 2026", "Exception Handling + Complete AI Pipeline"),
    (10, "20 September 2026", "Exception Handling + Complete AI Pipeline"),
    (11, "21 September 2026", "Desktop UI + Dashboard + Alerts/Report Export"),
    (12, "22 September 2026", "Desktop UI + Dashboard + Alerts/Report Export"),
    (13, "23 September 2026", "Desktop UI + Dashboard + Alerts/Report Export"),
    (14, "24 September 2026", "End-to-End Testing, Fixes, Packaging & Documentation"),
    (15, "25 September 2026", "End-to-End Testing, Fixes, Packaging & Documentation"),
    (16, "26 September 2026", "Final Testing, PPT, Demo & Submission"),
]

ALREADY_COMPLETE_NOTES = {
    5: "Account Book vision extraction (extract_account_book) was already built and tested on Day 1 (11 Sep), and hardened with 3-run reconciliation on Day 2 (12 Sep).",
    6: "Account Book vision extraction (extract_account_book) was already built and tested on Day 1 (11 Sep), and hardened with 3-run reconciliation on Day 2 (12 Sep).",
    7: "Record matching (group-by-serial, sum-of-lines rule) and amount verification (4-status decision logic) were already built and tested in verifier.py on Day 1.",
    8: "Record matching (group-by-serial, sum-of-lines rule) and amount verification (4-status decision logic) were already built and tested in verifier.py on Day 1.",
    9: "Exception handling (fail-soft batch processing) and full pipeline integration were already built in pipeline.py on Day 1, including retry logic for API errors.",
    10: "Exception handling (fail-soft batch processing) and full pipeline integration were already built in pipeline.py on Day 1, including retry logic for API errors.",
    11: "Desktop UI, dashboard, end-of-batch popup alerts, and Excel/PDF report export were already built on Day 1 and given a premium redesign (sidebar nav, card layout, status pill badges).",
    12: "Desktop UI, dashboard, end-of-batch popup alerts, and Excel/PDF report export were already built on Day 1 and given a premium redesign (sidebar nav, card layout, status pill badges).",
    13: "Desktop UI, dashboard, end-of-batch popup alerts, and Excel/PDF report export were already built on Day 1 and given a premium redesign (sidebar nav, card layout, status pill badges).",
}


def build_day1(prs):
    cover_slide(prs, 1, "11 September 2026",
                "Problem, Architecture & Scope Finalized\n+ Full System Built", "done")

    s = add_slide(prs)
    day_header(s, "DAY 1", "11 September 2026", "Problem Statement, Architecture & Scope")
    textbox(s, Inches(0.6), Inches(1.4), Inches(5.8), Inches(0.4), "Problem Statement", size=16, bold=True, color=INDIGO)
    textbox(s, Inches(0.6), Inches(1.8), Inches(5.8), Inches(1.5),
            "Businesses using handwritten job cards and account books "
            "manually verify serial numbers and amounts. With many daily "
            "records, this is slow, repetitive, and prone to human error.",
            size=13.5, color=TEXT_DARK, italic=True)
    textbox(s, Inches(0.6), Inches(3.3), Inches(5.8), Inches(0.4), "Scope Decisions", size=16, bold=True, color=INDIGO)
    bullets(s, Inches(0.6), Inches(3.7), Inches(5.9), Inches(3),
            [
                "Matching rule: job card total vs. SUM of every account book line sharing that serial number",
                "In scope: batch processing, AI vision extraction, confidence-gated verification, popup alerts, dashboard, report export",
                "Out of scope (documented): handwritten correction/cancellation detection; fuzzy serial-number matching",
            ], size=12.5)
    textbox(s, Inches(6.8), Inches(1.4), Inches(6), Inches(0.4), "Architecture (5 Boxes)", size=16, bold=True, color=INDIGO)
    bx, by, bw, bh, gap = Inches(6.8), Inches(1.9), Inches(2.5), Inches(0.55), Inches(0.25)
    rounded_box(s, bx, by, bw, bh, INDIGO, "1. Job Card\nVision/OCR", WHITE, size=11)
    rounded_box(s, bx + bw + gap, by, bw, bh, INDIGO, "2. Account Book\nVision/OCR", WHITE, size=11)
    rounded_box(s, bx + Inches(1.25), by + bh + gap, bw, bh, NAVY, "3. Match & Compare\n(sum by serial)", WHITE, size=11)
    rounded_box(s, bx + Inches(1.25), by + 2 * (bh + gap), bw, bh, NAVY, "4. Verify & Decide\n(4 statuses)", WHITE, size=11)
    rounded_box(s, bx + Inches(1.25), by + 3 * (bh + gap), bw, bh, RGBColor(0xB4, 0x50, 0x9E), "5. Notify\n(end-of-batch popup)", WHITE, size=11)
    footer(s, 2)

    s = add_slide(prs)
    day_header(s, "DAY 1", "11 September 2026", "Sample Collection & Field Analysis")
    textbox(s, Inches(0.6), Inches(1.35), Inches(11.9), Inches(0.5),
            "Analyzed the two real sample images (job card + account book page) to define the extraction schema:",
            14, color=TEXT_GRAY, italic=True)
    bullets(s, Inches(0.6), Inches(2.05), Inches(5.8), Inches(4),
            [
                "Job Card fields: serial_number, client_name, contact_number, service_total",
                "Account Book fields (per line): serial_number, client_name, contact_number, amount",
                {"text": "Key real-world finding:", "indent": 0},
                {"text": "a single serial number can have MULTIPLE line items in the ledger", "indent": 1},
                {"text": "→ decided matching must SUM all lines for a serial, not look up a single row", "indent": 1},
            ], size=13)
    textbox(s, Inches(6.8), Inches(2.05), Inches(6), Inches(0.4), "Sample Documents Used", size=16, bold=True, color=INDIGO)
    bullets(s, Inches(6.8), Inches(2.6), Inches(5.8), Inches(3),
            [
                "1000138303.jpg — sample salon Job Card (Serial 1244, client Asha)",
                "1000138302.jpg — handwritten Account Book ledger page (~11 client rows)",
            ], size=13)
    footer(s, 3)

    s = add_slide(prs)
    day_header(s, "DAY 1", "11 September 2026", "Full System Built — Ahead of Schedule")
    textbox(s, Inches(0.6), Inches(1.35), Inches(11.7), Inches(0.5),
            "Compressed timeline meant Day 1 also covered plan phases normally spread across 12–23 Sep:",
            size=13.5, color=TEXT_GRAY, italic=True)
    modules = [
        ("vision_extractor.py", "Gemini vision extraction for both document types; lazy API-key handling; retry logic; output validation"),
        ("verifier.py", "Serial-number matching, sum-of-lines rule, 4-status decision logic"),
        ("database.py", "SQLite persistence — run history survives across app restarts"),
        ("pipeline.py", "Orchestration; fail-soft batch processing; progress reporting hook"),
        ("report_export.py", "Excel (.xlsx) and PDF export, color-coded by status"),
        ("notifier.py", "End-of-batch popup summarizing every abnormal result"),
        ("main.py (PySide6 GUI)", "Desktop app: folder/file picker, background-threaded runs, dashboard, history browser"),
    ]
    top = Inches(2.0)
    row_h = Inches(0.66)
    for i, (name, desc) in enumerate(modules):
        y = top + i * row_h
        rounded_box(s, Inches(0.6), y, Inches(2.5), Inches(0.55), NAVY, name, WHITE, size=10.5)
        textbox(s, Inches(3.3), y + Inches(0.02), Inches(9.4), Inches(0.6), desc, size=11, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)
    footer(s, 4)

    s = add_slide(prs)
    day_header(s, "DAY 1", "11 September 2026", "Real End-to-End Testing + Premium UI")
    textbox(s, Inches(0.6), Inches(1.35), Inches(5.6), Inches(0.4), "Validated With Real Data", size=15, bold=True, color=INDIGO)
    bullets(s, Inches(0.6), Inches(1.75), Inches(5.6), Inches(2.2),
            [
                "Ran real Gemini extraction against both sample images",
                "Full pipeline tested end-to-end: extraction → matching → verdict → DB save → notification",
                "Correctly flagged a genuine AMOUNT_MISMATCH on real data",
            ], size=12.5)
    textbox(s, Inches(0.6), Inches(4.0), Inches(5.6), Inches(0.4), "Premium UI Redesign", size=15, bold=True, color=INDIGO)
    bullets(s, Inches(0.6), Inches(4.4), Inches(5.6), Inches(2.5),
            [
                "Dark navy/indigo sidebar navigation (replaced plain tabs)",
                "Card-based layout with drop shadows",
                "Color-coded rounded status pill badges",
                "Programmatically generated app icon; opens maximized",
            ], size=12.5)
    if os.path.exists(SCREENSHOT):
        s.shapes.add_picture(SCREENSHOT, Inches(6.6), Inches(1.5), width=Inches(6.2))
    footer(s, 5)


def build_day2(prs):
    cover_slide(prs, 2, "12 September 2026", "Accuracy Investigation & Fixes", "done")

    s = add_slide(prs)
    day_header(s, "DAY 2", "12 September 2026", "Accuracy Investigation & Fixes")
    textbox(s, Inches(0.6), Inches(1.35), Inches(11.9), Inches(0.4),
            "User ran the app and reported wrong extracted/summed values — investigated with real data, not assumptions:",
            size=13.5, color=TEXT_GRAY, italic=True)
    textbox(s, Inches(0.6), Inches(1.9), Inches(5.9), Inches(0.4), "Root Cause Found", size=15, bold=True, color=INDIGO)
    bullets(s, Inches(0.6), Inches(2.3), Inches(5.9), Inches(3.5),
            [
                "Job card total: genuinely ambiguous handwriting (5 vs 8) — misread as 30800 instead of 30500, at 98% confidence",
                "Account book: ran extraction 3x on same image → got 3 DIFFERENT results each time, despite temperature=0",
                "One run even attributed serial 1244's real amount to a different serial (1264) entirely",
                "Conclusion: single-pass extraction on dense ledger pages is not reliable enough to trust blindly",
            ], size=12)
    textbox(s, Inches(6.9), Inches(1.9), Inches(5.9), Inches(0.4), "Fixes Implemented", size=15, bold=True, color=INDIGO)
    bullets(s, Inches(6.9), Inches(2.3), Inches(5.9), Inches(3.5),
            [
                "Job card: line-item cross-check — sums individual services and flags mismatch vs. stated total",
                "Account book: 3-run reconciliation — only trusts a serial's total if ALL 3 passes agree",
                "Disagreement now correctly forces MANUAL_REVIEW instead of silently trusting a wrong guess",
                "Both prompts strengthened with digit-confusion and row-alignment warnings",
            ], size=12)
    rounded_box(s, Inches(0.6), Inches(6.1), Inches(11.9), Inches(0.75), GREEN_BG,
                "Verified: re-ran the fixed pipeline on real data — correctly produced MANUAL_REVIEW "
                "instead of a confidently-wrong answer.", GREEN, size=12, bold=False)
    footer(s, 2)


def build_ongoing_day(prs, day_num, date_label, title):
    cover_slide(prs, day_num, date_label, title, "ongoing")
    s = add_slide(prs)
    day_header(s, f"DAY {day_num}", date_label, title)
    rounded_box(s, Inches(0.6), Inches(1.5), Inches(11.9), Inches(0.9),
                RGBColor(0xEE, 0xF2, 0xFF),
                "IN PROGRESS — continuing from Day 2's accuracy fixes. Update this slide with the day's specific findings once complete.",
                INDIGO, size=13, bold=False)
    bullets(s, Inches(0.6), Inches(2.8), Inches(11.5), Inches(3.5),
            [
                "Carrying forward: job card line-item cross-check and account book 3-run reconciliation (built Day 2)",
                "Open question to resolve: whether job card extraction also needs multi-run reconciliation (cost vs. accuracy tradeoff)",
                "Plan: test against additional real job card / account book photos as they become available",
            ], size=14)
    footer(s, 2)


def build_already_complete_day(prs, day_num, date_label, title, note):
    cover_slide(prs, day_num, date_label, title, "done")
    s = add_slide(prs)
    day_header(s, f"DAY {day_num}", date_label, title)
    rounded_box(s, Inches(0.6), Inches(1.5), Inches(11.9), Inches(1.1), GREEN_BG,
                "ALREADY COMPLETE — delivered ahead of schedule during Day 1's compressed build.",
                GREEN, size=14)
    textbox(s, Inches(0.6), Inches(2.9), Inches(11.7), Inches(1.5), note, size=13.5, color=TEXT_DARK)
    textbox(s, Inches(0.6), Inches(4.6), Inches(11.7), Inches(0.5),
            "No additional work planned for this day unless further testing surfaces new issues.",
            size=12.5, color=TEXT_GRAY, italic=True)
    footer(s, 2)


def build_upcoming_day(prs, day_num, date_label, title, planned_items):
    cover_slide(prs, day_num, date_label, title, "upcoming")
    s = add_slide(prs)
    day_header(s, f"DAY {day_num}", date_label, title)
    rounded_box(s, Inches(0.6), Inches(1.5), Inches(11.9), Inches(0.75), AMBER_BG,
                "NOT YET STARTED — planned for this day per the execution plan.", AMBER, size=13)
    bullets(s, Inches(0.6), Inches(2.6), Inches(11.5), Inches(3.5), planned_items, size=14)
    footer(s, 2)


UPCOMING_ITEMS = {
    14: [
        "End-to-end testing across a wider variety of real job card / account book photos",
        "Fix any remaining extraction/matching issues found during testing",
        "Package the application into a standalone .exe (PyInstaller)",
        "Write/finalize user-facing documentation",
    ],
    15: [
        "Continue end-to-end testing and packaging from Day 14",
        "Finalize documentation and installation instructions",
    ],
    16: [
        "Final full-system test pass",
        "Prepare and rehearse the demo",
        "Finalize the submission PPT",
        "Submit the project",
    ],
}


for day_num, date_label, title in DAY_PLAN:
    prs = new_presentation()
    if day_num == 1:
        build_day1(prs)
    elif day_num == 2:
        build_day2(prs)
    elif day_num in (3, 4):
        build_ongoing_day(prs, day_num, date_label, title)
    elif day_num in ALREADY_COMPLETE_NOTES:
        build_already_complete_day(prs, day_num, date_label, title, ALREADY_COMPLETE_NOTES[day_num])
    else:
        build_upcoming_day(prs, day_num, date_label, title, UPCOMING_ITEMS[day_num])

    date_slug = date_label.split()[0].zfill(2) + "-Sep"
    filename = f"Day{day_num:02d}_{date_slug}.pptx"
    path = os.path.join(OUT_DIR, filename)
    prs.save(path)
    print("Saved:", path)

print(f"\nAll {len(DAY_PLAN)} daily files written to: {OUT_DIR}")
