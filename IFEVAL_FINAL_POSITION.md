# IFEval final position (item 10)

Source: `results/flipbudget/ifeval_reproducibility_check.json` (already
computed, not re-derived here — this is the synthesis the final phase asked
for, quoting exact numbers once). Nondeterminism result preserved exactly per
standing instruction; failed human-audit labels (C6/C7 in `EVIDENCE_TABLE.md`)
not used as evidence anywhere below.

## Does the verifier bug materially change conclusions?

| Question | Answer | Evidence |
|---|---|---|
| Item verdicts? | 1.89% of flagged items flip across 15 unseeded replicates (49/2592 flagged rows); **0%** flip in the seeded control (5 replicates, same seed) — confirms the flips are genuine nondeterminism, not measurement noise | `item_level_volatility` |
| Benchmark score? | Range [0.34689, 0.34730] around a baseline of 0.34716; std **0.000117** | `benchmark_score_impact` |
| Model ranking? | Kendall-τ ∈ [0.977, 0.989] across replicates; max single-model rank shift **2 places**; the #1 model **never changes** in any of the 15 replicates | `model_ranking_impact` |
| Identification conclusions? | Not applicable — IFEval was never carried into the SSM/reconciliation pipeline (E-A/E-B use MATH-Hard only); no identification-set result depends on IFEval | — |

**Every practical effect is small in absolute terms.** A 1.89% item flip rate, a 0.0117%-of-scale benchmark score std, and a maximum 2-place rank shift with the top model always stable is not a result that would change which model a practitioner picks, or the qualitative shape of any comparison.

## Corrected disagreement decomposition

Of the 380 strict/loose disagreements (2.60% of 14,607 rows): **64 (16.8%) are now explained** by a verified mechanism (up from 31/8.2% under the original incomplete 33-item scan), leaving **316 (83.2%) genuinely unexplained** (`C8` in `EVIDENCE_TABLE.md`, still open, not assumed to favor scorer error in either direction).

## Position

**Supporting case study, not a main pillar, not an appendix afterthought.** IFEval earns real space in the manuscript for one reason: it is the project's only **second, independently-confirmed verifier-bug finding on a second benchmark** (the nondeterminism mechanism scan, C3/C4 in `EVIDENCE_TABLE.md`) — genuine evidence the mechanism-discovery discipline generalizes beyond MATH-Hard. It does **not** carry weight as a second closed empirical result (its human-audit layer failed twice, C6/C7, excluded from evidence per standing instruction) and its 83.2% unexplained disagreement is reported as an open question, not folded into any headline number. Recommended placement: a bounded subsection in Results (mechanism-discovery generalization) plus the reproducibility numbers in an appendix table — not a co-equal pillar next to MATH-Hard/E-A, and not omitted.
