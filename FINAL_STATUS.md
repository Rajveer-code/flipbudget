# FINAL_STATUS (2026-09-19, after the stress test)

**Superseding note.** The stress test (STRESS_TEST.md) showed the 84/118 count depends entirely on
concordant-cell homogeneity across models (L=2: 43, L=5: 7, no pooling: 0). The earlier "64 at 5x" was a
bug and is withdrawn. The 458-row sheet is now the balanced design (Amendment 3), itself to be superseded by
Amendment 4 under the AISTATS plan (PLAN_AISTATS2027.md, G3). Rows below predate this note where they conflict.

Earlier status: `archive/FINAL_STATUS_pre_rebuild.md`. Reasoning for every
decision below: `CORE_ESTIMAND_AUDIT.md` (estimand) and `REAUDIT.md`
(narrative, design, 458 decision, prior art, venue).

## Thesis (selected on evidence)

**Audit the Disagreements: Certifying Leaderboard Rankings with Two
Verifiers and a Small Human Audit.** Measurement + audit design:

| Finding | Value | Source |
|---|---|---|
| Verifiers disagree | 3.63% of 22,508 responses | census |
| Verifier choice reverses orderings | 8 of 136; 7 significant under both | `reaudit_results.json` why |
| One verifier, per-model audit | certifies 0/136 with sampling (1 audit-only) | `joint_verifier_results.json`, `rebuild_results.json` |
| Where error lives | concordant cells 1 error / 287; disagreement cell 16 correct / 32 | joint cells |
| Two verifiers, existing audit | 84 of 118 sampling-permitted orderings (x5 concordant error: 64) | `joint_verifier_results.json` |
| +458 labels on disagreements (sim.) | median 95-98 | same |
| +458 labels, one-verifier design (sim.) | 7-15% of pairs | `reaudit_results.json` budget |

Withdrawn over the two passes: 6.10x/5.74x dominance, empty identified sets,
four-layer decomposition, Neyman-vs-proportional headline, flip-budget
values, worst-case exact_match bound, scorer-choice width, "audit uncertainty
dominates" as a claim about benchmarks, the common-mechanism test as a main
result (now an appendix diagnostic: one model drives it).

## Human audit decision: MODIFY (done)

`labeling/audit_v2_l1.csv`: 457 rows, blinded (358 disagreement rows
stratified by model x cell, 99 concordant check rows). Preregistration
Amendment 2. Optional for the paper's main claim; must be human-typed.

## Venue verdict (not inflated)

Workshop-ready now. TMLR plausible after replicating on a second benchmark
(labels needed only on disagreements + a concordant check, a few hundred).
Not top-tier main-track ready; NeurIPS E&D borderline without replication.

## Verification

- Tests 34/34.
- Manuscript: 0 overfull / undefined, 9 pages (6 main + refs + appendix); every
  number is a generated macro (`numbers.tex`, `CLAIM_LEDGER.md`).
- Figures A-D viewed; defects fixed.
- Full pipeline: `results/flipbudget/reproducibility_run_2026-09-19.log`.

## Open

1. Second-benchmark replication (the strengthening step).
2. Anonymization before any double-blind submission.
3. Optional disagreement-targeted labels (sheet ready).
4. Companion TMLR paper: its bound looked valid on a quick read; not fully audited.
