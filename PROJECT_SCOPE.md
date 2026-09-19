# Job Card ↔ Account Book Verification System

## 1. Problem Statement

Businesses using handwritten job cards and account books manually verify serial
numbers and amounts. With many daily records, this is slow, repetitive, and
prone to human error.

## 2. Architecture

```
[Job Card Images]  --Vision/OCR-->  extract_job_card()   --\
                                                             >-- [Match & Compare] --> [Verify & Decide] --> [Notify: end-of-batch popup]
[Account Book Images] --Vision/OCR--> extract_account_book() --/                                                        |
                                                                                                                          v
                                                                                                        [Dashboard / Report Export]
```

- **Box 1 — Vision/OCR (Job Card):** one image in, one structured record out.
- **Box 2 — Vision/OCR (Account Book):** one image in, many structured row
  records out (a page has multiple client entries).
- **Box 3 — Match & Compare:** groups account book rows by serial number,
  sums their amounts, and pairs the result with the job card sharing that
  serial number. Pure Python, no AI — see [[architecture-separation]] rationale
  below.
- **Box 4 — Verify & Decide:** applies confidence thresholds and the amount
  comparison, assigns exactly one status per job card.
- **Box 5 — Notify (new):** after a full batch finishes processing, shows a
  single desktop popup summarizing every job card flagged as
  `AMOUNT_MISMATCH`, `MISSING_RECORD`, or `MANUAL_REVIEW`. It does not fire
  per-record — only once, at the end of the run.

**Why AI is isolated to Boxes 1–2 only:** reading handwriting is the one part
of this problem a computer can't do reliably without AI. Matching serial
numbers and comparing amounts is 100% deterministic — plain Python is more
reliable, cheaper, faster, and easier to debug than asking an LLM to also do
arithmetic/matching. If a number is wrong, the bug is in Box 1/2. If a
MATCH/MISMATCH verdict is wrong, the bug is in Box 3/4.

## 3. Field Schema (from analyzing the two sample images)

### Job Card (per image → one record)
| Field | Notes |
|---|---|
| `serial_number` | e.g. "1244" — primary key used for matching |
| `client_name` | e.g. "Asha" |
| `contact_number` | e.g. "9000000000" |
| `service_total` | the single bottom-line total to verify (e.g. 30500) |
| `confidence` | model's self-reported confidence, 0.0–1.0 |

Line items (Service / Provider / payment mode / per-row Sale amount) exist on
the card but are **not required** for verification — only the Service Total
matters for matching. Not extracted in v1 unless a future need arises.

### Account Book (per image → list of records)
| Field | Notes |
|---|---|
| `serial_number` | matches a job card's serial number |
| `client_name` | may differ slightly in spelling from the job card — not used for matching, only informational |
| `contact_number` | often missing/blank in the ledger |
| `amount` | one ledger row = one amount; **a single serial number can appear as multiple rows/line-items** (e.g. multiple services logged separately for the same client) |
| `confidence` | model's self-reported confidence, 0.0–1.0 |

## 4. Matching Rule (decided)

A job card's `service_total` is compared against the **sum of every account
book amount sharing that serial number** (not a single-row lookup). If a
serial number appears once in the ledger, this is just that one amount; if it
appears multiple times, all of them are added together first.

## 5. Verification Statuses (unchanged from original design)

- `VERIFIED` — serial found, job card total == summed account book amount.
- `AMOUNT_MISMATCH` — serial found, totals differ.
- `MISSING_RECORD` — serial not found anywhere in the account book.
- `MANUAL_REVIEW` — confidence too low (job card or any matched row) or an
  account book amount was illegible, so the system won't auto-decide.

## 6. In Scope (v1)

- Batch processing: many job card images + many account book page images per
  run (not just one hardcoded pair).
- Vision-LLM extraction (Gemini) for both document types.
- Serial-number matching with multi-line summing (Section 4).
- Confidence-gated verification (4 statuses above).
- End-of-batch popup notification summarizing abnormalities.
- Desktop UI + dashboard showing all results.
- Report export (format TBD in the 21–23 Sep phase).

## 7. Out of Scope (v1) / Known Edge Cases

- **Handwritten corrections/cancellations:** the sample job card has "Cancel"
  / "Bill cut" written in a different pen over the total. v1 does **not**
  detect or interpret these annotations — a cancelled card will still be
  extracted and verified at face value. Flagged as a known limitation to
  revisit later, not solved now.
- **Fuzzy serial-number matching:** matching is exact-string only. An OCR
  misread of the serial itself (e.g. "1244" read as "124A") will incorrectly
  produce `MISSING_RECORD` rather than being reconciled. Not handled in v1.
- Live camera capture — input is pre-taken photos only.
- Multi-user accounts/auth, cloud hosting/deployment.
- Cross-run history/persistence — to be decided when the dashboard is built
  (21–23 Sep); v1 dashboard may only show the current batch's results.

## 8. Next Step

Per the execution plan, 12–14 Sep starts building/testing the Job Card
extraction (Box 1) against real samples, using this schema and the Gemini
vision approach validated earlier.
