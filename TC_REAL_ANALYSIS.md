# T-C real analysis — L1 + L2 in, L3 still pending

Script: `scripts/fb_tc_real_analysis.py`. Results:
`results/flipbudget/tc_real_analysis.json`. Real human labels, copied into the
repo: `labeling/tc_expansion_l1_completed.csv` (70 rows),
`labeling/tc_expansion_l2_answers.csv` (26 rows).

## Data status

- **L1 (70 rows / 30 items): valid.** 4 rows show a bare `0`/`1` — checked each
  individually against its response text before trusting them (not assumed):
  all 4 are genuine boxed answers of exactly 0 or 1 (e.g. `a+b=\boxed{1}`), not
  leftover broken labels. Real, usable.
- **L2 (26 rows / 11 items): valid.** Delivered as a separate answers-only
  file; uid set cross-checked against the committed sheet, exact match.
- **L3 (14 rows / 6 items): still the broken binary scheme.** Checked one row
  directly: item `22f02e1657e860a9`'s answer is `-\frac{35}{9}` in both L1 and
  L2 — L3 shows `1`. Not used here. **Needed to complete the 3-way design** —
  the L2 answers-file format (uid + your_answer only, no need to retype
  problem/response) is the easiest way to redo it.

## Item-level paired test — honestly underpowered again

51 real paired observations (same item, ≥2 models) from the 69 usable L1
rows. **Zero scorer-wrong events in this entire targeted audit** — the items
were specifically chosen as the highest-priority (model, stratum) pools from
the audit-design analysis, and still, no scorer error showed up. Correctly
reported as **UNDERPOWERED**, not "no correlation" — 0 events supports neither
direction.

**Is 0/69 surprising, or just chance?** Checked, not assumed: at the shrunk
rates these items were targeted from (roughly 3–7%), the expected count in 69
trials is ~2–3, and P(observing 0 | true rate ≈3%) ≈ 13% — plausible by chance
alone. This is *not* evidence the targeting or the underlying rate estimates
were wrong; it's consistent with them, just an unlucky (or genuinely
low-error) draw. Stated plainly rather than spun either way.

## L1×L2 agreement — the strong, real result of this round

Raw string agreement: 21/26 (80.8%) — expected, formatting varies
(`5x+2y-3z-0=0` vs `5x + 2y - 3z - 0 = 0`). **Derived agreement (does the
transcription match gold under the same real comparator both scores are
checked against): 26/26 — 100%.** Two independent people, given only the
model's raw response, arrived at the identical correctness judgment on every
single overlapping item. This is a genuine, reportable inter-rater-reliability
result for the manuscript's methods section, independent of whether the
item-level correlation test itself is powered yet.

## What this does not do

Does not complete 3-way agreement (needs L3 fixed). Does not resolve T-C's
central correlation question (still underpowered — 0 events, same structural
issue Tier 1 already hit, now confirmed again on freshly-targeted data). Does
not imply the targeting approach failed — 0/69 is statistically unremarkable
at these rates.
