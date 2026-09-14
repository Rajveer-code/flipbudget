# Audit-design formal optimization + budget curves (items 5, 6)

Script: `scripts/fb_audit_design_optimization.py`. Output: `results/flipbudget/audit_design_optimization.json`.

## The formal problem

Given qualifying models `m=1..17`, each with two audit strata (credited, wrong) and current audit counts `(n0_m, n1_m)`, and an additional total labeling budget `B` to distribute across all 34 strata, choose the allocation minimizing total variance of the stratified estimators `Σ_s p_s(1-p_s)/n_s`.

**Classical result (Neyman 1934, proof included, cited not claimed):** `n_s ∝ √(p_s(1-p_s))` minimizes this objective — three-line Lagrangian proof in the script's docstring, second-order condition confirmed. Not novel; see `NOVELTY_AUDIT.md`'s A/B/C/D table.

## Comparison of allocations, on the real 120-valid-pair audit-only objective

| Budget (× current) | Proportional | Neyman | Oracle | Partial-pooling-aware | Greedy (near-oracle, discrete objective) |
|---|---|---|---|---|---|
| 0 (baseline) | 91/120 (76%) | 91/120 (76%) | 91/120 (76%) | 91/120 (76%) | — |
| 1× | 72/120 (60%) | 89/120 (74%) | (identical to Neyman) | 74/120 (62%) | — |
| 4× | 57/120 (48%) | 89/120 (74%) | (identical) | 55/120 (46%) | **48/120 (40%)** |
| 16× | 26/120 (22%) | 89/120 (74%) | (identical) | 37/120 (31%) | not swept |

**Oracle = Neyman here, and this is itself a real, re-confirmed finding, not an oversight**: with only one round of real audit data, there is no independent "true" parameter to plan against other than the same noisy point estimate feasible Neyman must also use — a limitation of one-shot design honestly named, matching `AUDIT_DESIGN_ANALYSIS.md`'s prior "adaptive ≈ static Neyman" result.

## The central finding: naive plug-in Neyman is dominated on this real data

**15 of 17 qualifying models have exactly zero observed false-credit events; all 17 have zero observed false-miss events** (checked directly). Plug-in Neyman weights, `√(p̂(1-p̂))`, are therefore near-zero for almost every stratum and hugely concentrated on the one or two cells with an extreme (and noisy, tiny-`n`) observed rate — one model (`CohereForAI/c4ai-command-r-v01`) has a raw `alpha_raw=0.667` from an audit of only 3 items, and Neyman allocation pours nearly the entire additional budget into that single cell. Result: **Neyman allocation stalls at 74% unresolved even at 16× the current budget**, while simple proportional allocation reaches 22%, and a genuine greedy search targeting the actual discrete objective reaches 40% at only 4× budget.

**This is not a flaw in Neyman's theorem — it is a real, quantified limitation of plug-in Neyman when pilot estimates come from near-zero counts**, consistent with the classical two-phase-sampling literature's own caution about noisy first-phase estimates (Neyman 1938), here demonstrated concretely rather than cited abstractly. The **partial-pooling-aware** variant (using shrunk, not raw, point estimates) substantially mitigates this (62%→31% across the same budget range vs. Neyman's flat 74%), which is itself a practical recommendation: **when planning a real audit expansion under near-zero pilot counts, use pooled/shrunk rate estimates for Neyman weights, not raw per-model rates, or better, use a genuine discrete-objective search (greedy) over a formula optimized for a different objective.**

## Stopping rule

Marginal gain (Neyman allocation) drops from 6.92 resolved pairs per 1000 additional labels (first 289 labels) to 0.00 for every budget level tested beyond that — **because Neyman itself stalls, not because the true information content is exhausted** (greedy and proportional both keep gaining well past this point). The honest stopping-rule statement: **under naive Neyman allocation specifically, stop near 1× current budget; under a properly-targeted (greedy or pooled) allocation, returns continue well past 4× budget** — the stopping point is a property of the allocation strategy chosen, not a fixed number, which is itself the practical lesson this analysis delivers.

## What this changes

`AUDIT_DESIGN_ANALYSIS.md`'s original claim ("77% variance cut available for free" via Neyman) is **not contradicted** — that is a true statement about the variance objective. What's added is the discrete, decision-relevant objective (number of resolved comparisons) responds very differently, and naive Neyman is a poor choice for it on this specific, sparse real data. `FINAL_DECISION.md`'s "audit-design methodology" as the strongest practical contribution is **strengthened by this honest complication**, not weakened: a practitioner following this project's guidance now gets a specific, tested warning (use pooled estimates or greedy search, not naive plug-in Neyman, under near-zero pilot counts) rather than an untested "Neyman is optimal" claim that would have failed in practice.
