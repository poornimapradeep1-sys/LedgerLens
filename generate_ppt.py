"""
generate_ppt.py

One-off script (not part of the app) that builds a SINGLE combined
progress deck covering every day so far, based on the real dated log in
README.md. Run directly: `python generate_ppt.py`.

For one .pptx PER individual day (for daily mentor check-ins), see
generate_daily_ppts.py instead — both scripts share slide-building code
from ppt_helpers.py.
"""

from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from ppt_helpers import (
    new_presentation, add_slide, set_bg, textbox, bullets, rounded_box,
    day_header, footer, set_notes, INDIGO, NAVY, TEXT_DARK, TEXT_GRAY, WHITE, LIGHT_BG,
    GREEN, GREEN_BG, AMBER, AMBER_BG, GRAY_BG,
)

TEAM = "Poornima Pradeep  •  Navya Ponnachan"

prs = new_presentation()

# ----------------------------------------------------------------------
# Slide 1: Title
# ----------------------------------------------------------------------
s = add_slide(prs)
set_bg(s, NAVY)
textbox(s, Inches(1), Inches(1.9), Inches(11.3), Inches(1.2),
        "LedgerLens", size=48, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
textbox(s, Inches(1), Inches(2.75), Inches(11.3), Inches(0.7),
        "Job Card ↔ Account Book Verification System", size=22, color=INDIGO, bold=True)
textbox(s, Inches(1), Inches(3.35), Inches(11), Inches(0.5),
        "Daily Progress Report", size=16, color=RGBColor(0x9C, 0xA3, 0xAF))
textbox(s, Inches(1), Inches(3.95), Inches(11), Inches(0.5),
        "Execution window: 9 Sep – 26 Sep 2026   |   Report as of: 15 Sep 2026",
        size=13, color=RGBColor(0x9C, 0xA3, 0xAF))
textbox(s, Inches(1), Inches(4.7), Inches(11), Inches(0.5),
        f"Team: {TEAM}", size=14, color=WHITE, bold=True)
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(1.75), Inches(1.2), Pt(4))
line.fill.solid()
line.fill.fore_color.rgb = INDIGO
line.line.fill.background()
line.shadow.inherit = False
set_notes(s,
    "Good [morning/afternoon]. We're Poornima Pradeep and Navya Ponnachan, "
    "and this is LedgerLens — a desktop tool that automatically checks a "
    "handwritten job card's total against a handwritten account book "
    "ledger, using AI to read the handwriting and plain code to do the "
    "actual comparison. This report covers everything built from 9 "
    "September through today, 15 September, against our original "
    "execution plan.")

# ----------------------------------------------------------------------
# Slide 2: Execution Plan recap
# ----------------------------------------------------------------------
s = add_slide(prs)
set_bg(s, LIGHT_BG)
textbox(s, Inches(0.6), Inches(0.35), Inches(10), Inches(0.6), "Execution Plan (9–26 Sep)",
        size=28, bold=True, color=TEXT_DARK)
plan_rows = [
    ("9 Sep", "Finalize problem, architecture & scope"),
    ("10–11 Sep", "Collect samples & analyze image/field requirements"),
    ("12–14 Sep", "Test Vision/OCR + build/improve Job Card extraction"),
    ("15–16 Sep", "Build Account Book extraction + structured output"),
    ("17–18 Sep", "Record matching + amount verification"),
    ("19–20 Sep", "Exception handling + integrate complete AI pipeline"),
    ("21–23 Sep", "Desktop UI + dashboard + alerts/report export"),
    ("24–25 Sep", "End-to-end testing, fixes, packaging & documentation"),
    ("26 Sep", "Final testing, PPT, demo & submission"),
]
top = Inches(1.25)
row_h = Inches(0.58)
for i, (date, desc) in enumerate(plan_rows):
    y = top + i * row_h
    is_done = i <= 7
    status_color = GREEN_BG if is_done else GRAY_BG
    status_text_color = GREEN if is_done else TEXT_GRAY
    status_label = "DONE (ahead of schedule)" if is_done else "UPCOMING"
    rounded_box(s, Inches(0.6), y, Inches(1.5), Inches(0.46), NAVY, date, WHITE, size=12)
    textbox(s, Inches(2.3), y + Inches(0.03), Inches(7.3), Inches(0.42), desc, size=13, color=TEXT_DARK,
            anchor=MSO_ANCHOR.MIDDLE)
    rounded_box(s, Inches(9.8), y, Inches(2.9), Inches(0.44), status_color, status_label, status_text_color, size=10.5)
footer(s, 2)
set_notes(s,
    "Here's the plan we were given, 9 through 26 September, mapped to what's "
    "actually done. Because Day 1 was a compressed, intensive build, we "
    "ended up completing phases that were originally scheduled all the way "
    "through 24–25 September — extraction, matching, the desktop UI, and "
    "now packaging into an installable app — well ahead of schedule. Only "
    "the final submission day, the 26th, remains as originally planned.")

# ----------------------------------------------------------------------
# Slide 3: Day 1 (11 Sep) Part A — Problem, Architecture, Scope
# ----------------------------------------------------------------------
s = add_slide(prs)
day_header(s, "DAY 1", "11 September 2026", "Problem Statement, Architecture & Scope Finalized")
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
footer(s, 3)
set_notes(s,
    "We started by defining the problem precisely: matching isn't a "
    "simple one-to-one lookup, because one job card serial number can "
    "have multiple line entries in the account book — so the rule we "
    "locked in was job card total versus the SUM of every matching "
    "ledger line. The whole system breaks down into five boxes: two "
    "AI reading steps, a matching step, a decision step, and a "
    "notification step. We also explicitly wrote down what's OUT of "
    "scope — like fuzzy serial matching — so expectations are clear.")

# ----------------------------------------------------------------------
# Slide 4: Day 1 Part B — Sample Collection & Field Analysis
# ----------------------------------------------------------------------
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
            {"text": "a single serial number can have MULTIPLE line items in the ledger (e.g. 2 services logged separately)", "indent": 1},
            {"text": "→ decided matching must SUM all lines for a serial, not look up a single row", "indent": 1},
        ], size=13)
textbox(s, Inches(6.8), Inches(2.05), Inches(6), Inches(0.4), "Sample Documents Used", size=16, bold=True, color=INDIGO)
bullets(s, Inches(6.8), Inches(2.6), Inches(5.8), Inches(3),
        [
            "1000138303.jpg — sample salon Job Card (Serial 1244, client Asha)",
            "1000138302.jpg — handwritten Account Book ledger page (~11 client rows)",
        ], size=13)
footer(s, 4)
set_notes(s,
    "Before writing any extraction code, we looked closely at the real "
    "sample documents to define exactly what fields we needed — not a "
    "guessed schema. That's where we discovered the multi-line-per-serial "
    "pattern that shaped the whole matching rule on the previous slide. "
    "These same two sample images are still what we use for every demo "
    "and every regression check throughout the project.")

# ----------------------------------------------------------------------
# Slide 5: Day 1 Part C — Full system built (ahead of schedule)
# ----------------------------------------------------------------------
s = add_slide(prs)
day_header(s, "DAY 1", "11 September 2026", "Full System Built — Ahead of Schedule")
textbox(s, Inches(0.6), Inches(1.35), Inches(11.7), Inches(0.5),
        "Compressed timeline meant Day 1 also covered plan phases normally spread across 12–23 Sep:",
        size=13.5, color=TEXT_GRAY, italic=True)

modules = [
    ("vision_extractor.py", "Gemini vision extraction for both document types; lazy API-key handling; retry logic for 5xx/429 errors; output schema validation"),
    ("verifier.py", "Serial-number matching, sum-of-lines rule, 4-status decision logic (VERIFIED / AMOUNT_MISMATCH / MISSING_RECORD / MANUAL_REVIEW)"),
    ("database.py", "SQLite persistence — run history survives across app restarts"),
    ("pipeline.py", "Orchestration layer; fail-soft (one bad image can't crash a whole batch); progress reporting hook"),
    ("report_export.py", "Excel (.xlsx) and PDF export, color-coded by status"),
    ("notifier.py", "End-of-batch popup summarizing every abnormal result"),
    ("main.py (PySide6 GUI)", "Desktop app: folder/file picker, background-threaded batch runs, live progress, results dashboard, history browser"),
]
top = Inches(2.0)
row_h = Inches(0.66)
for i, (name, desc) in enumerate(modules):
    y = top + i * row_h
    rounded_box(s, Inches(0.6), y, Inches(2.5), Inches(0.55), NAVY, name, WHITE, size=10.5)
    textbox(s, Inches(3.3), y + Inches(0.02), Inches(9.4), Inches(0.6), desc, size=11, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 5)
set_notes(s,
    "This is the full module breakdown. The important design decision "
    "here, worth calling out to a reviewer: AI extraction and the actual "
    "verification math are in completely separate files. vision_extractor "
    "is the only file that talks to the AI model — verifier.py that "
    "decides VERIFIED or MISMATCH contains zero AI calls, it's plain, "
    "auditable Python. For a tool that's checking financial numbers, "
    "we wanted the pass/fail decision to be something we can reason "
    "about and test deterministically, not just 'the AI said so'.")

# ----------------------------------------------------------------------
# Slide 6: Day 1 Part D — Real end-to-end test + Premium UI
# ----------------------------------------------------------------------
s = add_slide(prs)
day_header(s, "DAY 1", "11 September 2026", "Real End-to-End Testing + Premium UI")
textbox(s, Inches(0.6), Inches(1.35), Inches(5.6), Inches(0.4), "Validated With Real Data", size=15, bold=True, color=INDIGO)
bullets(s, Inches(0.6), Inches(1.75), Inches(5.6), Inches(2.2),
        [
            "Ran real Gemini extraction against both sample images",
            "Full pipeline tested end-to-end: extraction → matching → verdict → DB save → notification",
            "Correctly flagged a genuine AMOUNT_MISMATCH on real data",
        ], size=12.5)
textbox(s, Inches(0.6), Inches(4.0), Inches(5.6), Inches(0.4), "Premium UI (v1)", size=15, bold=True, color=INDIGO)
bullets(s, Inches(0.6), Inches(4.4), Inches(5.6), Inches(2.5),
        [
            "Dark navy/indigo sidebar navigation (replaced plain tabs)",
            "Card-based layout with drop shadows",
            "Color-coded rounded status pill badges",
            "Programmatically generated app icon; opens maximized",
        ], size=12.5)
import os
_screenshot = r"D:\GenAI_BIA\verification_system\ppt_screenshot.png"
if os.path.exists(_screenshot):
    s.shapes.add_picture(_screenshot, Inches(6.6), Inches(1.5), width=Inches(6.2))
footer(s, 6)
set_notes(s,
    "By the end of Day 1 we hadn't just built the pipeline, we'd run it "
    "for real — no mocked data — and it correctly caught a genuine "
    "amount mismatch. We also moved past default Qt styling into this "
    "first 'premium' look, shown on the right: dark sidebar, card "
    "layout, colored status pills. This was version 1 of the UI — it "
    "gets a full second redesign later, which we'll show near the end.")

# ----------------------------------------------------------------------
# Slide 7: Day 2 (12 Sep) — Accuracy investigation & fixes
# ----------------------------------------------------------------------
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
            "Both prompts strengthened with explicit digit-confusion and row-alignment warnings",
        ], size=12)

rounded_box(s, Inches(0.6), Inches(6.1), Inches(11.9), Inches(0.75), GREEN_BG,
            "Verified: re-ran the fixed pipeline on real data — correctly produced MANUAL_REVIEW "
            "instead of a confidently-wrong answer.", GREEN, size=12, bold=False)
footer(s, 7)
set_notes(s,
    "This is probably the most important slide for a technical reviewer, "
    "because it's a real bug we found and fixed, not something that "
    "worked perfectly the first time. We discovered the AI could be "
    "'confidently wrong' — 98% confidence on a genuinely misread digit. "
    "And running the same ledger image three times gave three DIFFERENT "
    "answers, including once assigning money to the wrong client entirely. "
    "So we stopped trusting a single pass: now we cross-check the job "
    "card's line items against its stated total, and for account book "
    "pages we run extraction three times and only accept an answer all "
    "three agree on. Disagreement doesn't get hidden — it routes to "
    "Manual Review so a human checks it.")

# ----------------------------------------------------------------------
# Slide 8: UI redesign, interactivity & packaging (15 Sep)
# ----------------------------------------------------------------------
s = add_slide(prs)
day_header(s, "UPDATE", "15 September 2026  ·  ahead of the 21–25 Sep plan", "Aurora Dark Redesign, Interactivity & Packaging")
textbox(s, Inches(0.6), Inches(1.3), Inches(5.7), Inches(0.35), "Redesigned & Renamed: \u201cLedgerLens\u201d", size=14, bold=True, color=INDIGO)
bullets(s, Inches(0.6), Inches(1.68), Inches(5.7), Inches(2.3),
        [
            "Full dark theme (\u201caurora\u201d navy + violet\u2192cyan accent), replacing the v1 light/indigo look",
            "Drag-and-drop image/folder upload with thumbnail previews (not just file names)",
            "Live dashboard stat tiles \u2014 Verified / Mismatch / Missing / Review counts at a glance",
            "Animated toast notifications for routine feedback; modal popups kept only for errors and abnormal results needing acknowledgement",
        ], size=11)
textbox(s, Inches(0.6), Inches(4.05), Inches(5.7), Inches(0.35), "Packaged as a Real Installable App", size=14, bold=True, color=INDIGO)
bullets(s, Inches(0.6), Inches(4.43), Inches(5.7), Inches(2.5),
        [
            "Built a standalone .exe (PyInstaller) \u2014 runs without Python installed",
            "Fixed config/database to persist correctly outside the source folder (%LOCALAPPDATA%) once packaged",
            "Built a real Windows installer (Inno Setup): Start Menu shortcut, uninstaller, standard install wizard",
            "Next: publish publicly via GitHub Releases so it's searchable and downloadable \u2014 pending GitHub account setup",
        ], size=11)
_ll_screenshot = r"D:\GenAI_BIA\verification_system\ppt_screenshot_ledgerlens.png"
if os.path.exists(_ll_screenshot):
    s.shapes.add_picture(_ll_screenshot, Inches(6.7), Inches(1.35), width=Inches(6.0))
    textbox(s, Inches(6.7), Inches(4.6), Inches(6.0), Inches(0.4),
            "LedgerLens v2 \u2014 a real run against our sample job card + account book images",
            size=10.5, color=TEXT_GRAY, italic=True)
footer(s, 8)
set_notes(s,
    "Most recently we took the working system and made it feel like a "
    "real product instead of a prototype. Two separate things happened "
    "here. First, a full visual and interaction redesign — dark theme, "
    "drag-and-drop, thumbnails, a live dashboard strip so you can see "
    "the shape of a batch at a glance instead of scrolling a table, and "
    "toast notifications instead of interrupting every small action with "
    "a popup. We also renamed the app to LedgerLens. Second, and "
    "separately, we packaged it: it now runs as a standalone .exe with "
    "no Python installation required, and we built an actual Windows "
    "installer with a Start Menu shortcut and uninstaller — the "
    "screenshot below is this exact build, running a real verification "
    "on our sample images. The one thing not finished yet is public "
    "distribution — putting it somewhere people can search for and "
    "download it — because that requires a GitHub account we're still "
    "setting up.")

# ----------------------------------------------------------------------
# Slide 9: Current status summary
# ----------------------------------------------------------------------
s = add_slide(prs)
set_bg(s, LIGHT_BG)
textbox(s, Inches(0.6), Inches(0.35), Inches(10), Inches(0.6), "Current Status Summary",
        size=28, bold=True, color=TEXT_DARK)

status_items = [
    ("Problem, Architecture & Scope", "Complete", GREEN_BG, GREEN),
    ("Job Card Extraction (Vision/OCR)", "Complete + accuracy hardening (line-item cross-check)", GREEN_BG, GREEN),
    ("Account Book Extraction", "Complete + 3-run reconciliation", GREEN_BG, GREEN),
    ("Matching & Verification Logic", "Complete", GREEN_BG, GREEN),
    ("Exception Handling & Pipeline", "Complete (fail-soft batch processing)", GREEN_BG, GREEN),
    ("Desktop UI + Dashboard", "Complete (aurora dark redesign, v2)", GREEN_BG, GREEN),
    ("Alerts / Report Export", "Complete (toasts + popup + Excel + PDF)", GREEN_BG, GREEN),
    ("Packaging (.exe + installer)", "Complete \u2014 LedgerLensSetup.exe built & verified", GREEN_BG, GREEN),
    ("Public Distribution (GitHub)", "Pending \u2014 needs team GitHub account", AMBER_BG, AMBER),
    ("Final End-to-End Testing on Varied Samples", "Ongoing", AMBER_BG, AMBER),
]
top = Inches(1.2)
row_h = Inches(0.57)
for i, (name, status, bg, fg) in enumerate(status_items):
    y = top + i * row_h
    textbox(s, Inches(0.6), y + Inches(0.04), Inches(5.8), Inches(0.48), name, size=12.5, color=TEXT_DARK, anchor=MSO_ANCHOR.MIDDLE)
    rounded_box(s, Inches(6.7), y, Inches(6.0), Inches(0.46), bg, status, fg, size=11, align=PP_ALIGN.LEFT)
footer(s, 9)
set_notes(s,
    "Quick summary of where every part of the plan stands today. "
    "Everything through packaging is complete and verified. Two items "
    "remain open: public distribution, which is blocked only on "
    "creating a GitHub account, not on any technical work; and continued "
    "testing on a wider variety of real sample photos beyond our two "
    "originals, which is ongoing.")

# ----------------------------------------------------------------------
# Slide 10: Next steps
# ----------------------------------------------------------------------
s = add_slide(prs)
set_bg(s, NAVY)
textbox(s, Inches(0.6), Inches(0.5), Inches(10), Inches(0.6), "Next Steps",
        size=30, bold=True, color=WHITE)
bullets(s, Inches(0.8), Inches(1.6), Inches(11.5), Inches(4.5),
        [
            "Create a GitHub account for the team and publish LedgerLens (public repo + Releases page) so it's searchable and downloadable",
            "Continue real-sample testing with additional job card / account book photos beyond the original two samples",
            "Decide whether job card extraction also needs multi-run reconciliation (cost vs. accuracy tradeoff)",
            "Final end-to-end testing, documentation polish, and demo rehearsal — 26 Sep",
        ], size=16, color=WHITE)
textbox(s, Inches(0.6), Inches(7.0), Inches(11), Inches(0.4), "Thank you", size=14, color=RGBColor(0x9C, 0xA3, 0xAF))
footer(s, 10)
set_notes(s,
    "So, what's left: getting this published so it's actually reachable "
    "by someone searching for it, broadening our real-world test set "
    "beyond the two sample images we've used throughout, one open "
    "decision on extraction cost versus accuracy for job cards, and "
    "then final polish and rehearsal ahead of the 26th. Thank you — "
    "happy to answer questions or do a live demo now.")

output_path = r"D:\GenAI_BIA\verification_system\Daily_Progress_Report.pptx"
prs.save(output_path)
print("Saved:", output_path)
