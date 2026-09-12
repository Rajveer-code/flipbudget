# T-C — three labelers, nested overlap

Per your offer to bring in two other people. Script:
`scripts/fb_tc_multi_labeler_split.py`. Splits the ALREADY-COMMITTED 70-row
sample (unchanged, not redrawn) into three sheets — mirrors this project's own
established convention for the main MATH-Hard audit
(`mathhard_l1/l2/l3.csv`, 400/151/75) and the masterplan's own H-B item
("≥3 blind labellers; per-stratum agreement... cross-vendor adjudication").

## The three files

- **`tc_expansion_l1.csv`** — full 70 rows, 30 items. **You label this one.**
- **`tc_expansion_l2.csv`** — 26 rows, 11 items (36.7% of items — same ratio
  as the original protocol's 151/400). **Labeler 2.**
- **`tc_expansion_l3.csv`** — 14 rows, 6 items (20.0% — same ratio as 75/400),
  **nested inside** l2's 11 items. **Labeler 3.**

Overlap is stratified by *item*, not row: whichever items land in l2/l3, both
of that item's rows (the paired observation T-C needs) travel together — so
agreement can be checked on genuinely paired items once labels come back, not
fragments of a pair split across sheets. l3 ⊂ l2 ⊂ l1 exactly, so you get
pairwise (l1×l2, l1×l3, l2×l3) and three-way agreement once all three return —
not just single-pair comparisons.

## Same blinding, unchanged

Same `uid, problem, response, your_answer` columns, same hash construction, no
model name/item_id/stratum anywhere — checked directly on both new files
(grepped every roster model name, zero matches), same as l1.

## Instructions for labelers 2 and 3

Identical to `TC_LABELING_PACKAGE.md`'s rules (same as the main project's
`HUMAN_LABELING_GUIDE.md`): type the transcribed final answer exactly as
written, `NONE` for no commitment, `CONTRADICTORY` for two unresolved final
answers, self-correction resolves to the last stated value. Fill only
`your_answer`. They should **not** see `tc_expansion_l1.csv`'s answers before
labeling their own sheet — that would defeat the independence the overlap
exists to measure.

## What this does not do

Doesn't pick who labelers 2/3 actually are — that's yours. Doesn't run any
agreement analysis yet — nothing to check until sheets come back.
