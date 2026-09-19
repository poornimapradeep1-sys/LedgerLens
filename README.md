# Project Log — Job Card ↔ Account Book Verification System

This file tracks what has been built and every significant change, in
order, so the project's history can be referenced later without digging
through chat logs. Updated after every meaningful change.

See [PROJECT_SCOPE.md](PROJECT_SCOPE.md) for the problem statement,
architecture, field schema, and scope decisions.

## Log

### 2026-09-11 — Reset & re-scoped
- Deleted the earlier prototype code (`vision_extractor.py`, `verifier.py`,
  `test_gemini_extraction_v2.py`) per decision to restart from the
  execution plan's Day 1. Sample images (`1000138302.jpg`,
  `1000138303.jpg`) were kept.
- Analyzed the two sample images and wrote `PROJECT_SCOPE.md`: finalized
  problem statement, architecture (5 boxes: Job Card OCR, Account Book
  OCR, Match & Compare, Verify & Decide, Notify), field schema for both
  document types, and the matching rule (job card `service_total` vs.
  **sum** of every account book line sharing that serial number, since a
  serial can have multiple line items in the ledger).
- Documented known out-of-scope edge cases: handwritten
  cancel/correction annotations on job cards are not detected; serial
  number matching is exact-string only (no fuzzy matching for OCR
  misreads of the serial itself).

### 2026-09-11 — Full build started
Decisions locked in before building:
- **UI toolkit: PySide6** (not PyQt6) — PySide6 is LGPL-licensed and
  free to use in a closed-source app; PyQt6 is GPL/commercial-licensed.
- **Input method**: must support BOTH picking a whole folder of images
  and picking individual files, selectable per run.
- **Persistence**: SQLite (`verification.db`), so run history survives
  across app restarts, not just the current batch.
- **Report export**: both Excel (`.xlsx`) and PDF.
- **Notification**: a single summary popup at the END of a batch run
  (not one popup per record), listing every abnormal (non-VERIFIED)
  result.

Flaws identified and fixed during the rebuild (see chat for full list):
- API key check moved out of module import time (was `raise SystemExit`
  on import — would have crashed a GUI app before its window even
  opened) into a lazy `get_client()` that raises a catchable
  `MissingApiKeyError` instead.
- Added schema/type validation on all AI JSON output
  (`_validate_job_card`, `_validate_account_book_row`) so a malformed or
  missing field fails loudly and specifically, instead of causing a
  confusing crash or silent wrong comparison later in verification.
- Added retry handling for rate-limit errors (HTTP 429), not just
  server-busy (5xx) errors, since a real batch of many images is more
  likely to hit quota limits.
- Verified `gemini-3.6-flash` (the model name from the original
  prototype) is a real, current model — not a leftover mistake — via
  web search against Google's official docs.

Files built so far:
- `vision_extractor.py` — Box 1 (`extract_job_card`) and Box 2
  (`extract_account_book`), rewritten with lazy client init, retry
  handling for both 5xx and 429, and output validation.
- `verifier.py` — Box 3 (`group_account_book_by_serial`) and Box 4
  (`verify_job_card`, `verify_all`), implementing the sum-of-lines
  matching rule and the four-status decision logic
  (VERIFIED / AMOUNT_MISMATCH / MISSING_RECORD / MANUAL_REVIEW).
  Confidence threshold is a parameter, not a hardcoded constant.
- `database.py` — SQLite persistence (`init_db`, `save_run`,
  `list_runs`, `get_run_results`, `get_all_results`) so the dashboard
  can show history across runs.
- `pipeline.py` — orchestration layer tying extraction → verification →
  persistence together across a whole batch. Fail-soft: one bad/corrupt
  image is recorded as a failed extraction and does not abort the rest
  of the batch. Exposes a `progress_callback` hook for the GUI's
  progress bar.

- `report_export.py` — `export_excel()` and `export_pdf()`, both consuming
  the exact same verdict-list structure the UI/database use (no separate
  "what a report contains" logic path). Rows color-coded by status in
  both formats.
- `notifier.py` — Box 5. `show_batch_summary_popup()` fires once per
  batch (not once per record), listing every non-VERIFIED result.
- `main.py` — PySide6 desktop GUI:
  - "New Run" tab: add job card / account book images via **either** a
    folder picker or a multi-file picker (both supported, per
    requirement); confidence threshold is user-adjustable; batch runs on
    a background `QThread` (`BatchWorker`) so the UI never freezes;
    progress bar updates per image via `pipeline.py`'s
    `progress_callback` hook; results table color-coded by status;
    Export Excel / Export PDF buttons.
  - "History" tab: browses every past run from `verification.db`
    (status counts per run, drill into any run's full result table).
  - API key: prompted via a dialog on first run if not already set
    (env var or a local `config.json`), never crashes the app if
    missing — see `ensure_api_key()`.
- `requirements.txt` — `google-genai`, `PySide6`, `openpyxl`, `fpdf2`.

**Testing done so far:**
- All modules compile and import cleanly (`py_compile` + import smoke
  test) — confirms the lazy API-key fix works (no crash on import with
  no key set).
- `verifier.py`'s matching/summing rule validated against synthetic data
  covering all 4 statuses, including the case that mattered most: a
  serial number split across TWO account book lines that correctly sum
  to match the job card total.
- `database.py` round-trip (save → list → fetch) validated.
- `report_export.py` Excel + PDF generation validated (files produced,
  non-empty).
- GUI launch smoke-tested (`python main.py`) — opens without crashing.

### 2026-09-11 — Real end-to-end test (API key provided)
- User supplied a Gemini API key, saved to `config.json` (gitignored,
  never committed — added `.gitignore` for this + `verification.db` +
  `__pycache__`).
- Ran `vision_extractor.extract_job_card()` and `extract_account_book()`
  against the real sample images — both returned valid, schema-conformant
  JSON. Noted (not a bug): the AI read the job card total as 30800 while
  the account book's two "1244" lines summed to 42500 — a genuine
  handwriting ambiguity, exactly the kind of thing this system exists to
  surface for human review rather than silently resolve.
- Ran the full `pipeline.run_batch()` end-to-end on real data: extraction
  → matching/summing → verdict (`AMOUNT_MISMATCH`, correctly) →
  `database.save_run()` → `notifier.build_summary_text()`. All worked
  without a single mock — this is the first fully-real (no synthetic
  data) validation of the whole system.

### 2026-09-11 — Premium UI redesign
User asked for the UI to feel professional/premium rather than default
Qt styling. Added:
- `theme.py` — a single design-system file: color tokens (deep
  navy/indigo sidebar, indigo accent, light content area, muted status
  colors) and one QSS stylesheet applied app-wide, plus a
  programmatically-generated app icon (no external image asset needed).
- Restructured `main.py`: replaced the plain `QTabWidget` with a proper
  sidebar navigation (checkable nav buttons + `QStackedWidget`), wrapped
  inputs/settings/results in card-style `QGroupBox`es with drop shadows,
  and added `StatusBadgeDelegate` — renders the Status column as a
  rounded colored pill instead of a flat cell, which is what actually
  makes it read as a dashboard rather than a spreadsheet.
- App now opens maximized by default for more working room.

**Visual verification process (worth noting for future reference):** the
GUI was actually launched and screenshotted to confirm the redesign
renders correctly, not just assumed from code. Two lessons learned
mid-way:
  1. An early screenshot attempt used `SetForegroundWindow` +
     whole-screen capture, which briefly brought a different window
     (the user's browser) to the foreground and captured it instead of
     the app — that image was deleted immediately without being
     inspected further. Switched to capturing via `PrintWindow`, which
     renders directly from the target window's own buffer and cannot
     ever capture a different window, regardless of what's on top —
     used for every screenshot since.
  2. What first looked like a layout bug (cards clipped at the window's
     right edge) was actually a DPI-virtualization artifact in the
     screenshot script itself (PowerShell wasn't DPI-aware while the Qt
     app is per-monitor-DPI-aware, so `GetWindowRect` returned scaled-down
     coordinates while `PrintWindow` rendered at true resolution). Fixed
     by calling `SetProcessDPIAware()` in the capture script — the actual
     app layout was correct all along.

### 2026-09-12 — Accuracy investigation & fixes (user-reported errors)
User ran the app themselves and reported wrong extracted/summed values.
Investigated with real data rather than guessing:
- Zoomed into the job card's actual "Service Total" field — the digit
  genuinely reads ambiguously between 5 and 8 in the handwriting itself.
  The AI consistently read it as 30800 instead of the correct 30500,
  while reporting 98% confidence — a "confidently wrong" failure mode
  that self-reported confidence alone doesn't catch.
- Ran `extract_account_book()` 3 times on the same ledger image
  (temperature=0): got 3 DIFFERENT results each time, including one run
  that attributed serial 1244's real amount (18500) to a different
  serial (1264) entirely. Confirmed this is a genuine extraction
  instability on dense multi-row ledger pages, not a `verifier.py`
  summing bug (the summing logic was correct given whatever rows it was
  handed).

Fixes implemented in `vision_extractor.py`:
- `_cross_check_job_card_total()`: job card prompt now also extracts
  each line-item's sale amount; if their sum doesn't match the stated
  Service Total (beyond a 1.0 tolerance), confidence is capped at 0.3,
  forcing `MANUAL_REVIEW` via verifier.py's existing threshold check —
  no verifier.py changes needed.
- `extract_account_book_reconciled(image_path, runs=3)`: makes 3
  extraction passes per account book image and only trusts a serial
  number's total if ALL 3 agree; disagreement produces a placeholder
  row with `amount=None, confidence=0.0`, which again routes to
  `MANUAL_REVIEW` through existing verifier.py logic. User explicitly
  chose 3-run unanimous agreement over 2-run or prompt-only fixes,
  accepting the 3x API cost/time for account book pages specifically
  (job cards remain single-pass).
- Both prompts strengthened with explicit warnings about commonly
  confused handwritten digits (3/8, 5/8, 0/6, 1/7) and, for the account
  book, explicit row-alignment guidance (an amount must be re-verified
  as belonging to the same horizontal row as its serial number).
- `pipeline.py` updated to call the reconciled extractor and to weight
  the progress bar correctly (`ACCOUNT_BOOK_RUNS = 3` per account book
  image vs. 1 per job card).

**Verified the fix works**: re-ran the full pipeline on the real sample
images — the account book reconciliation correctly failed to reach
3-way agreement on this specific (genuinely hard to read) photo, so the
job card now correctly lands on `MANUAL_REVIEW` instead of a
confidently-wrong `AMOUNT_MISMATCH`/`VERIFIED`. This is the intended,
safe behavior for a financial audit tool: honest uncertainty beats a
wrong confident answer.

**Known residual limitation**: the job card's line-item cross-check
didn't catch the 5→8 misread in this specific case, because the same
wrong digit appeared consistently in both a line item and the total
within one extraction pass (they agreed with each other, just both
wrong). This doesn't cause a silent false-VERIFIED, though — the wrong
total still fails to match the account book side once that's stable, so
it's still caught, just later in the pipeline. Decided NOT to extend the
3-run reconciliation to job cards too (would 3x job card cost as well)
since the mismatch path already provides a safety net.

### 2026-09-12 — Daily progress PPT for mentor review
- Added `generate_ppt.py` — builds `Daily_Progress_Report.pptx` from the
  dated entries in this log, so the deck can be regenerated any time
  README.md gains new entries rather than maintained by hand.
- 9 slides: title, execution plan recap (with done/upcoming status per
  phase), Day 1 (11 Sep) across problem/architecture/scope, sample
  analysis, full system build, and real end-to-end testing + UI
  redesign; Day 2 (12 Sep) accuracy investigation & fixes; current
  status summary; next steps.
- Rendered every slide to PNG via PowerPoint COM automation to visually
  verify layout rather than assuming python-pptx positioning was
  correct — caught and fixed one real overlap bug (intro text colliding
  with a heading on the sample-analysis slide) before delivering it.

### 2026-09-12 — Split into per-day PPT files
User wanted a separate `.pptx` per calendar day for individual daily
mentor check-ins, rather than one combined deck.
- Refactored shared slide-building code out of `generate_ppt.py` into
  `ppt_helpers.py` so both generators build slides the same way.
- Added `generate_daily_ppts.py` — writes 16 files to `daily_ppts/`
  (`Day01_11-Sep.pptx` through `Day16_26-Sep.pptx`).
- Days 1 (11 Sep) and 2 (12 Sep) get full real-content slides (same
  material as the combined deck). Days 3–4 (13–14 Sep) get an "IN
  PROGRESS" placeholder for the ongoing accuracy-hardening work. Days
  5–13 (15–23 Sep) are marked **ALREADY COMPLETE** rather than
  "upcoming" — those plan phases (account book extraction, matching,
  exception handling, UI/dashboard/export) were genuinely finished
  during Day 1's compressed build, so the daily files say so honestly
  instead of pretending nothing happened until that calendar date.
  Days 14–16 (24–26 Sep) are genuinely "NOT YET STARTED" (packaging,
  final testing, demo).
- `generate_ppt.py` (the combined deck) kept as-is for a single-file
  overview; both scripts can be re-run any time to regenerate.
- Verified a sample of each day-type (real, in-progress, already-
  complete, not-started) by rendering to PNG via PowerPoint COM
  automation — no layout issues found.

**Not yet built:** packaging into a standalone `.exe` (PyInstaller) —
planned for the 24–25 Sep phase per the execution plan.

### 2026-09-15 — "Aurora dark" redesign + standalone .exe packaging
User asked for a "beautiful, interactive, unique" desktop app and, for
distributing it to other users without Python installed, brought the
24–25 Sep PyInstaller packaging phase forward to now.

- `theme.py` — full palette rewrite: near-black charcoal/navy surfaces
  with a two-tone violet→cyan accent (was a light indigo/white SaaS
  look), dark-mode status badge colors, QSS for QMessageBox/QToolTip/
  stat tiles/toast/drag-active drop zones, gradient app icon.
- `main.py` interactivity additions:
  - `DropListWidget` — drag-and-drop of image files/folders onto the
    Job Card / Account Book panels (alternative to the existing
    Add Folder / Add Files buttons), with a highlighted drop state.
  - Thumbnail previews in both image lists instead of bare filenames.
  - `StatTile` / `build_stat_strip()` — a colored VERIFIED/MISMATCH/
    MISSING/REVIEW count strip on both the New Run results card and
    the History page's per-run view.
  - `Toast` — a self-dismissing, animated (fade in/out) corner
    notification for routine feedback (files added, export saved, an
    all-clear run); modal `QMessageBox` is kept only for things that
    need acknowledgement (errors, abnormal verification results).
  - `fade_in()` — the results card fades in after a run finishes
    instead of snapping into place.
  - Emoji used throughout the UI (nav, buttons, status badges/tiles,
    toasts) per explicit user request for visual personality.
- `paths.py` (new) — `app_data_dir()`: writable-data location resolver.
  In dev, unchanged (next to the source files). In a PyInstaller build,
  redirects to `%LOCALAPPDATA%\VerificationStudio` instead, since a
  frozen app's own folder may not be writable (or, for `--onefile`,
  is a temp extraction dir) — required for `config.json` (API key) and
  `verification.db` to persist across runs of the packaged .exe.
  `database.py`'s `DB_PATH` and `main.py`'s `CONFIG_PATH` now go
  through it.
- `build_icon.py` (new, build-time only) — renders the same gradient
  checkmark icon as `theme.make_app_icon()` to a multi-size `icon.ico`
  file on disk, since PyInstaller's `--icon` needs a file, not the
  in-memory `QIcon` the Qt app itself uses.
- Packaged with `pyinstaller --windowed --icon icon.ico --name
  VerificationStudio main.py` (onedir build — faster startup than
  `--onefile`, distributed by zipping the `dist/VerificationStudio/`
  folder). `requirements-dev.txt` added (`pyinstaller`, `Pillow`) so
  the base `requirements.txt` needed to just run the app stays
  unchanged. `build/`, `dist/`, `*.spec` gitignored.

**Verified**: ran the app from source and screenshotted it (dev mode)
to confirm the redesign renders correctly; separately built and
launched the actual packaged `VerificationStudio.exe` from
`dist/VerificationStudio/` and screenshotted that too — confirms the
packaging (not just the source) works standalone, and that
`%LOCALAPPDATA%\VerificationStudio` gets created for config/db as
intended. Thumbnails, drag-and-drop highlight state, and the stat
strip were exercised via a scripted smoke test (bypassing native file
dialogs) with real sample images and synthetic verdict data, then
screenshotted.

**Known limitation carried over**: multi-user here means multiple
independent installs (each copy has its own local `verification.db`
and its own Gemini API key) — not shared/centralized run history or
login. True multi-user (shared backend) remains out of v1 scope per
`PROJECT_SCOPE.md` section 7.
