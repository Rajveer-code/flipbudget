# Table 2: Theoretical results summary

| Result | Statement | Novelty class | Reference |
|---|---|---|---|
| T-A (SSM) | Odds-ratio Lambda-bounded sensitivity family for (alpha,beta) | B (adaptation of Tan 2006 / Zhao-Small-Bhattacharya 2019 MSM) | `TA_SSM_DERIVATION.md` |
| T-H (sharpness) | Identified interval = corner envelope of the Lambda-box, intersected with [0,1] | A/B (corollary of the linear-fractional vertex theorem) | `TA_SSM_DERIVATION.md`, fig3 |
| T-B (design sensitivity) | Lambda-tilde at which a pairwise comparison first becomes unresolved | B (bisection/closed-form on an established functional form) | `TB_DESIGN_SENSITIVITY.md`, `TB_COMPOUND.md` |
| Correlated-error bound | Propositions 1-3 bounding shared-scorer-error correlation's effect | C (nontrivial extension, no prior direct analogue found) | `THEORY_EXTENSIONS.md` S1 |
| T-D (imperfect reference) | q_max(eta) bound under a non-omniscient human reference | C | `THEORY_EXTENSIONS.md` S4 |
| T-E (verification bias) | Horvitz-Thompson validity under disproportionate audit sampling | A (classical HT/post-stratification) applied in a new setting (B) | `THEORY_EXTENSIONS.md` S5, `fb_tc_expansion2_analysis.py::_ht_pool` |
| Ranking-preservation theorem | Exact conditions under which Delta*'s sign cannot flip | C | `THEORY_EXTENSIONS.md` S2 |
| Flip-budget uncertainty | Minimum differential-error perturbation to flip a comparison's sign | C | `THEORY_EXTENSIONS.md` S7, `fb_flip_budget_uncertainty_mathhard.py` |
| Neyman allocation | Classical optimal stratified allocation, found DOMINATED by proportional on real sparse audit data | A (classical proof) + empirical finding (C) | `fb_audit_design_optimization.py` |

No individual result rises above class C; the claimed contribution is the specific combination (benchmark comparison + scorer misclassification + partial identification + audit-estimation uncertainty + audit design + scorer-choice dependence), not any one piece. See `NOVELTY_AUDIT.md`.
