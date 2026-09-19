"""
generate_script_pdf.py

One-off script (not part of the app) that renders the LedgerLens
presentation script — the spoken talking points for each slide of
Daily_Progress_Report.pptx — as a standalone PDF handout, for
rehearsing or reading from without needing PowerPoint open. The same
text also lives inside the .pptx itself as per-slide speaker notes
(see set_notes() calls in generate_ppt.py) — this file is the
"print it and read it" version of the same script.

Run directly: `python generate_script_pdf.py`
"""

from datetime import datetime
from fpdf import FPDF

TEAM = "Poornima Pradeep  |  Navya Ponnachan"
INDIGO = (79, 70, 229)
TEXT_GRAY = (107, 114, 128)
TEXT_DARK = (17, 24, 39)

SLIDES = [
    ("Slide 1 - Title",
     "Good [morning/afternoon]. We're Poornima Pradeep and Navya Ponnachan, and "
     "this is LedgerLens - a desktop tool that automatically checks a handwritten "
     "job card's total against a handwritten account book ledger, using AI to "
     "read the handwriting and plain code to do the actual comparison. This "
     "report covers everything built from 9 September through today, 15 "
     "September, against our original execution plan."),

    ("Slide 2 - Execution Plan Recap",
     "Here's the plan we were given, 9 through 26 September, mapped to what's "
     "actually done. Because Day 1 was a compressed, intensive build, we ended "
     "up completing phases that were originally scheduled all the way through "
     "24-25 September - extraction, matching, the desktop UI, and now packaging "
     "into an installable app - well ahead of schedule. Only the final "
     "submission day, the 26th, remains as originally planned."),

    ("Slide 3 - Day 1A: Problem, Architecture & Scope",
     "We started by defining the problem precisely: matching isn't a simple "
     "one-to-one lookup, because one job card serial number can have multiple "
     "line entries in the account book - so the rule we locked in was job card "
     "total versus the SUM of every matching ledger line. The whole system "
     "breaks down into five boxes: two AI reading steps, a matching step, a "
     "decision step, and a notification step. We also explicitly wrote down "
     "what's OUT of scope - like fuzzy serial matching - so expectations are "
     "clear."),

    ("Slide 4 - Day 1B: Sample Collection & Field Analysis",
     "Before writing any extraction code, we looked closely at the real sample "
     "documents to define exactly what fields we needed - not a guessed "
     "schema. That's where we discovered the multi-line-per-serial pattern "
     "that shaped the whole matching rule on the previous slide. These same "
     "two sample images are still what we use for every demo and every "
     "regression check throughout the project."),

    ("Slide 5 - Day 1C: Full System Built",
     "This is the full module breakdown. The important design decision here, "
     "worth calling out to a reviewer: AI extraction and the actual "
     "verification math are in completely separate files. vision_extractor is "
     "the only file that talks to the AI model - verifier.py, which decides "
     "VERIFIED or MISMATCH, contains ZERO AI calls; it's plain, auditable "
     "Python. For a tool that's checking financial numbers, we wanted the "
     "pass/fail decision to be something we can reason about and test "
     "deterministically, not just \"the AI said so.\""),

    ("Slide 6 - Day 1D: Real Testing + Premium UI (v1)",
     "By the end of Day 1 we hadn't just built the pipeline, we'd run it for "
     "real - no mocked data - and it correctly caught a genuine amount "
     "mismatch. We also moved past default Qt styling into this first "
     "\"premium\" look, shown on the right: dark sidebar, card layout, colored "
     "status pills. This was version 1 of the UI - it gets a full second "
     "redesign later, which we'll show near the end."),

    ("Slide 7 - Day 2: Accuracy Investigation & Fixes",
     "This is probably the most important slide for a technical reviewer, "
     "because it's a real bug we found and fixed, not something that worked "
     "perfectly the first time. We discovered the AI could be \"confidently "
     "wrong\" - 98% confidence on a genuinely misread digit. And running the "
     "same ledger image three times gave three DIFFERENT answers, including "
     "once assigning money to the wrong client entirely. So we stopped "
     "trusting a single pass: now we cross-check the job card's line items "
     "against its stated total, and for account book pages we run extraction "
     "three times and only accept an answer all three agree on. Disagreement "
     "doesn't get hidden - it routes to Manual Review so a human checks it."),

    ("Slide 8 - Aurora Dark Redesign & Packaging (15 Sep)",
     "Most recently we took the working system and made it feel like a real "
     "product instead of a prototype. Two separate things happened here. "
     "First, a full visual and interaction redesign - dark theme, "
     "drag-and-drop, thumbnails, a live dashboard strip so you can see the "
     "shape of a batch at a glance instead of scrolling a table, and toast "
     "notifications instead of interrupting every small action with a popup. "
     "We also renamed the app to LedgerLens. Second, and separately, we "
     "packaged it: it now runs as a standalone .exe with no Python "
     "installation required, and we built an actual Windows installer with a "
     "Start Menu shortcut and uninstaller - the screenshot on this slide is "
     "this exact build, running a real verification on our sample images. The "
     "one thing not finished yet is public distribution - putting it "
     "somewhere people can search for and download it - because that "
     "requires a GitHub account we're still setting up."),

    ("Slide 9 - Current Status Summary",
     "Quick summary of where every part of the plan stands today. Everything "
     "through packaging is complete and verified. Two items remain open: "
     "public distribution, which is blocked only on creating a GitHub "
     "account, not on any technical work; and continued testing on a wider "
     "variety of real sample photos beyond our two originals, which is "
     "ongoing."),

    ("Slide 10 - Next Steps",
     "So, what's left: getting this published so it's actually reachable by "
     "someone searching for it, broadening our real-world test set beyond "
     "the two sample images we've used throughout, one open decision on "
     "extraction cost versus accuracy for job cards, and then final polish "
     "and rehearsal ahead of the 26th. Thank you - happy to answer questions "
     "or do a live demo now."),
]


def build_pdf(output_path: str) -> str:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*TEXT_DARK)
    pdf.cell(0, 12, "LedgerLens", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 8, "Presentation Script", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*TEXT_GRAY)
    pdf.cell(0, 6, "Job Card <-> Account Book Verification System - Daily Progress Report", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Team: {TEAM}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    for title, body in SLIDES:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*INDIGO)
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*TEXT_DARK)
        pdf.multi_cell(0, 6.2, body)
        pdf.ln(4)

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*TEXT_GRAY)
    pdf.multi_cell(
        0, 5.5,
        "Presenting tips: total read-through is roughly 4-5 minutes. A natural "
        "split is one presenter for Slides 1-7 (the build story) and the other "
        "for Slides 8-10 (redesign, packaging, status, next steps) - or "
        "alternate slide by slide. This same script is also embedded as "
        "per-slide speaker notes inside Daily_Progress_Report.pptx (visible in "
        "PowerPoint's Presenter View).",
    )

    pdf.output(output_path)
    return output_path


if __name__ == "__main__":
    path = build_pdf(r"D:\GenAI_BIA\verification_system\LedgerLens_Presentation_Script.pdf")
    print("Saved:", path)
