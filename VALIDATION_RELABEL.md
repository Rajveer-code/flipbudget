# Preregistered re-labeling validation of the 458-row audit

Written 2026-09-24, **before the check sheet was drawn and before any re-labeling**. The
criteria below are fixed now so that the outcome cannot be chosen after seeing it.

## Why this exists

The 458-row tc_expansion2 sheet was labeled and submitted three times (2026-09-13 to 09-17)
and excluded each time on a provenance judgement: turnaround time, a bulk edit between two
submissions, and an agreement rate with the automated extractors that was high relative to the
author's earlier 400-item audit. The author states the labels are their own work.

A judgement cannot settle this; a measurement can. The relevant statistic, measured
2026-09-24 with the composition-adjusted baseline:

| Label set | typed answer exactly equals a regex extraction |
|---|---|
| Genuine 400-item audit (accepted, used throughout) | 289/371 = 77.9% |
| tc_expansion2 round 1 | 388/406 = 95.6% |
| tc_expansion2 round 3 | 391/406 = 96.3% |

The gap is real, but it is **not diagnostic on its own**. Competing explanations: (a) the
round-2 instructions added an explicit "copy exactly what is inside the box" rule that the
first audit's guide did not contain, which mechanically raises exact agreement; (b) the two
sheets contain different responses, and this one over-samples cells with clean boxed answers;
(c) the labels were produced by an extraction tool rather than by reading.

(a) and (b) are properties of the sheet and the instructions. (c) is a property of the
process. A fresh pass through the instrumented app separates them, because the app blocks
pasting, times every item, and records an immutable batch id and export hash.

## The check

A random, cell-stratified subsample of 60 rows of the same sheet, drawn by
`scripts/fb_relabel_sample.py` with seed 20260924, is re-labeled in
`labeling/app/label.html`. The check sheet does not contain the earlier answers, and the
author does not consult them while labeling.

## Criteria, fixed in advance

**Gate (must hold for the check itself to count):** the batch passes
`scripts/fb_audit_v3_gate.py` — zero paste attempts, median dwell at least 15 s, no run of
more than 20 items under 3 s.

**Primary agreement:** on Y\*, the correct/incorrect verdict the analysis actually uses
(harness routine, indeterminate counted as incorrect), between the fresh labels and the
round-3 submission on the same uids.
- **Pass:** Cohen's κ ≥ 0.8 **and** raw agreement ≥ 0.90.
- Otherwise: fail.

**Secondary, reported but not gating:** exact-string agreement; the extraction-equality rate
of the fresh timed labels, with its composition-adjusted p-value; median dwell; the same
statistics against round 1.

## What each outcome means, decided now

**Pass.** The earlier labels are treated as valid and all 458 enter the analysis. The paper
reports the re-labeling reliability as a measured quantity, states that the labels were
produced in three sittings whose provenance was challenged internally, and reports that the
challenge was resolved by an instrumented replication. If the fresh timed labels also show a
high extraction-equality rate, that is direct evidence the rate is a property of this sheet
and its instructions rather than of the labeling process, and it is reported as such.

**Fail.** The 458 labels stay excluded. The analysis uses the 400-item audit plus whatever is
labeled fresh, and the exclusion and its measured basis are stated in the limitations.

Either way the outcome is reported. Neither outcome is hidden, and the sheet is not re-drawn
or re-labeled to obtain a different one.
