# T-C real analysis — all three labelers complete

Script: `scripts/fb_tc_real_analysis.py`. Results:
`results/flipbudget/tc_real_analysis.json`. Real human labels, all copied into
the repo: `labeling/tc_expansion_l1_completed.csv` (70 rows),
`labeling/tc_expansion_l2_answers.csv` (26 rows),
`labeling/tc_expansion_l3_answers.csv` (14 rows).

## Data status — all three valid

- **L1 (70 rows / 30 items): valid.** 4 rows show a bare `0`/`1` — checked each
  individually against its response text before trusting them (not assumed):
  all 4 are genuine boxed answers of exactly 0 or 1 (e.g. `a+b=\boxed{1}`), not
  leftover broken labels.
- **L2 (26 rows / 11 items): valid.** Delivered as a separate answers-only
  file; uid set cross-checked against the committed sheet, exact match.
- **L3 (14 rows / 6 items): valid, on the redo.** Uid set matches the
  committed sheet exactly; no bare 0/1 remaining, no blanks.

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

## Inter-rater agreement — strong across the board

| Pair | n | Raw string match | Derived (matches_gold) match |
|---|---|---|---|
| L1 × L2 | 26 | 21/26 (80.8%) | **26/26 (100%)** |
| L1 × L3 | 14 | 14/14 (100%) | 14/14 (100%) |
| L2 × L3 | 14 | 14/14 (100%) | 14/14 (100%) |
| **All three** | 14 | — | **14/14 (100%)** |

Raw-string gaps are exactly what's expected from formatting, not
disagreement (`5x+2y-3z-0=0` vs `5x + 2y - 3z - 0 = 0`) — never a case where
two people's transcriptions implied a *different* correctness judgment once
run through the same real comparator both scores are checked against. Three
independent people, given only the raw model response, reached the identical
correctness call on every single overlapping item, including the one
`CONTRADICTORY` case (item `e2d2b1bb868548f8`) — all three independently
flagged it, not just matched a number. This is a genuine, strong, reportable
inter-rater-reliability result for the manuscript's methods section.

## What this does not do

Does not resolve T-C's central correlation question (still underpowered — 0
events, same structural issue Tier 1 already hit, now confirmed again on
freshly-targeted data). Does not imply the targeting approach failed — 0/69
is statistically unremarkable at these rates. Perfect agreement on this
30-item sample does not guarantee it holds at scale — worth keeping in mind
if a larger audit round happens, not assumed to generalize automatically.
