# T-C correlated-error bound (item 4)

Script: `scripts/fb_tc_correlated_error_bound.py`. Output: `results/flipbudget/tc_correlated_error_bound.json`. Builds on `THEORY_EXTENSIONS.md` §1 (Propositions 1–3), which already establishes the qualitative mechanism (shared item difficulty induces non-negative covariance, which shrinks pairwise identification width) but explicitly could not fit `π, p_hard, p_easy` from 0/69 real events. This does not re-attempt that point estimate — it derives the strongest defensible statement without inventing precision.

## A. What the real 0/51 audit actually bounds

Zero either-wrong events out of 51 paired (same-item, two-model) observations gives an **exact Clopper-Pearson 95% upper bound of 6.98%** on `P(either model wrong)`. Translated through the two correlation extremes:

| Assumption | Implied upper bound on marginal error rate p |
|---|---|
| ρ=0 (independent) | p ≤ 3.55% |
| ρ=1 (fully shared) | p ≤ 6.98% |

**Both bounds are consistent with, not evidence against, the pooled α anchor (~3%) used throughout the reconciliation** — the audit is uninformative about ρ (0 events either way), but it does not contradict the existing pooling.

## B/C. Independent vs. correlated vs. worst-case, on the real 66 valid scorer-only pairs

First-order sensitivity (Prop. 2's `Var(diff) = 2p(1-p)(1-ρ)` relation — a linearized approximation, explicitly not a nonlinear correction to `bounded_comparison`, per `THEORY_EXTENSIONS.md`'s own stated limitation):

| ρ | Unresolved pairs | % |
|---|---|---|
| 0.00 (independent — **A**, what `EVIDENCE_TABLE.md` A4 actually uses) | 15/66 | 22.7% |
| 0.25 | 15/66 | 22.7% |
| 0.50 | 13/66 | 19.7% |
| 0.75 | 8/66 | 12.1% |
| 1.00 (fully correlated — **C**, worst-case/most-optimistic) | 0/66 | 0.0% |

**Maximum possible change from correlation: 15 pairs (22.7 points), and only if ρ were exactly 1** — a real upper bound on how much correlation could matter, not an estimate of how much it does. **B (the actual correlated bound) cannot be reported as a single number** — ρ is not estimable from this data — so B is reported as this parametric curve rather than a point, which is the honest answer, not a gap.

## Required additional labels for a usable ρ estimate

Using a minimum-cell-count convention (≥20 either-wrong events, stated as a convention, not a formal power target) at the pooled p≈3%: **≈458 raw audited rows would be needed (≈6.6× the current 69-row T-C audit)** to fit even a coarse association. Notably, this number is close to `AUDIT_DESIGN_ANALYSIS.md`'s independently-derived required-n (~415, for a different purpose — audit/scorer-layer parity) — two different calculations converging on a similar order of magnitude, which is a modest but real cross-check, not a coincidence to lean on hard.

## Bottom line

The 136-pair reconciliation's scorer-only-layer conclusion (22.7% unresolved, under the independence assumption already in use) could be anywhere from unchanged to fully resolved (0%) depending on a correlation this project's current data cannot estimate. This is now stated as an explicit, bounded range rather than an implicit assumption — the reconciliation's use of independence is conservative in one direction (Prop. 2) but its magnitude is genuinely unknown, not merely unreported.
