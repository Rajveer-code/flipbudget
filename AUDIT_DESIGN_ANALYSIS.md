# Audit-design analysis — evaluating a second contribution

Per your instruction, evaluated as a candidate second contribution before touching
E-E. Script: `scripts/fb_audit_design_analysis.py`. Results:
`results/flipbudget/audit_design_analysis.json`. Scope: this repo currently has
**one benchmark, one scorer** — "per benchmark/scorer/model" reduces to "per
model" here, stated explicitly, not silently narrowed.

## Preserved, not rewritten

Per your explicit instruction: the original **73.5% saturated-at-Λ=1** figure
(`TB_COMPOUND.md`) stands as the original uncorrected compound result. The
**four-layer reconciliation** (`RECONCILIATION_FOUR_LAYERS.md`, verdict B) stands
as its correction. Neither is touched here. This document adds a third layer —
audit *design*, not audit *diagnosis* — on top of both.

## Q1 — required sample size, from observed effect sizes

Target widths read directly off the reconciliation table, not guessed: Target A
= audit-only width ≤ scorer-only median (0.039); Target B = audit-only width ≤
sampling median (0.043). Bisected the real per-model audit-only identified width
(same `[0,1]`-bounded methodology as the reconciliation) against scaled-up audit
counts, holding each model's own shrunk rate fixed (standard power-analysis
convention — plan around the best current estimate).

**Both targets reachable for all 17 qualifying models.** Median total audit n
needed: **415** (Target A) / **362** (Target B) — up from a current median of
roughly 15–20. Per-model range is wide (falcon-40b needs only ~6 more items since
its current audit already happens to be informative at its specific rate;
gemma-7b needs ~1,320 to hit Target A) — the aggregate figure is a planning
number, not a uniform per-model rule.

## Q2/Q3 — is stratifying on scorer outcome, and the current allocation, optimal?

Classical result (Neyman 1934): variance-minimizing allocation across strata is
`n_h ∝ σ_h = √(p_h(1-p_h))`, not equal or population-proportional allocation.

**A real bug caught computing this**: `β_pooled = 0.0` exactly for every model
(0 of 188 audited wrong-parsed items roster-wide showed a false miss — a real
fact, already established in `TIER1_VERDICT.md`, not new). Used raw, this makes
`σ_wrong = 0` for every model, degenerating to "put 100% of budget in the
credited stratum" — overstating certainty that 0/188 does not actually
warrant. Fixed with Jeffreys smoothing on the pipeline's own `shrinkage_k`
(effective-n it already computes, not a new parameter) — matching the exact
raw-anchor discipline from `TA_BOUNDARY_AUDIT.md`.

**Corrected result**: Neyman-optimal allocation is **~77% credited-stratum,
~23% wrong-parsed**, fairly consistent across models. The **current design's
actual allocation** (median 28.6% credited) is **systematically inverted** —
under-auditing the higher-variance credited stratum, over-auditing wrong-parsed
(where β is already known to be near-zero, hence low marginal information).
Median `|gap|` between actual and Neyman-optimal: **0.482** — a large,
real inefficiency. The current audit's stratification *variable* (scorer
outcome) is reasonable; its *allocation* across that stratification is not.

## Q4 — combined-region shrinkage vs. audit budget

| Audit multiplier | Median combined width | Unresolved pairs |
|---|---|---|
| 1× (current) | 0.435 | 125/136 (91.9%) |
| 2× | 0.295 | 99/136 (72.8%) |
| 5× | 0.190 | 80/136 (58.8%) |
| 10× | 0.129 | 68/136 (50.0%) |
| 20× | 0.098 | 63/136 (46.3%) |
| 50× | 0.078 | 50/136 (36.8%) |

Note on the 91.9% vs. the reconciliation's 80.9%: this curve is a **planning
projection** — it reconstructs audit counts from each model's shrunk rate at
every multiplier (so 1× isn't bit-identical to the historical audit's actual
counts), not a re-statement of the reconciliation's own number. Real, useful
finding: return on audit investment is real but has diminishing returns — even
50× the current audit (a large, expensive undertaking) leaves over a third of
pairs unresolved. Full identification is not on the table at any realistic
budget; *substantial* improvement is.

## Q5 — when do more benchmark items stop helping?

Sampling width shrinks with benchmark n; audit-only width does not (proven,
`TA_SSM_DERIVATION.md`). Solved the crossover benchmark-n per model directly.
**16 of 16 models are already past it** — MATH-Hard's ~1,324 items is already
far more than enough; audit size, not benchmark size, is the binding constraint
for every model on this roster. A clean, decisive, unambiguous result.

## Q6 — how much would adaptive/active auditing add over a static optimal design?

Not a full active-learning system — an honest bound. Compared, at the same total
budget (10× current): current design scaled up vs. Neyman-optimal fixed
allocation vs. a theoretical oracle. **Neyman reallocation alone cuts total
variance by 77.0%** versus naively scaling up the current design. **Neyman and
the oracle bound coincide exactly** — a classical result (the same allocation
that minimizes sum-of-variances also IS the theoretical optimum for this
objective), not a coincidence of this data. **Practical conclusion: a full
adaptive/active-learning audit system would not out-perform a correctly computed
static Neyman allocation on this objective** — any further gain from adaptivity
would come from a different mechanism (e.g. early stopping per cell), a real but
second-order effect, not the large win reallocation alone already captures.

## Reassessment

Six real, verified, data-grounded results: a defensible required-n figure, a
quantified and fixable allocation inefficiency (77% variance reduction
available, for free, by reallocating existing budget), a shrinkage curve for
planning, a decisive crossover finding, and a bounded answer on adaptivity that
tells you *not* to build a complex system you don't need. This is a coherent,
publishable methodology, not a grab-bag — and B (audit-estimation uncertainty
dominates) is precisely what *motivates* needing C (how to fix it). They are not
two competing stories; B identifies the problem, C is the solution built to
answer it.

## Verdict: **D — combination of B and C**

Not A: scorer-only unresolved (11.0%) barely exceeds the sampling baseline
(8.8%) — real but too modest to centerpiece alone, confirmed again here (Q1-Q6
never needed the scorer-sensitivity layer to produce their results).

Not C alone: the audit-design methodology's motivation *is* B's finding — a
design contribution about "how to audit efficiently" reads as solving an
invented problem without first establishing, as the reconciliation already did,
that the problem (current audits are underpowered) is real and large.

**B + C is the strongest supported centerpiece**: current benchmark-comparison
scoring has a hidden, underpowered measurement layer (B, reconciled and
quantified); we provide a principled, verified framework for sizing and
allocating the human audit that resolves it — required-n from observed effect
sizes, a proven allocation inefficiency with a concrete fix, a shrinkage curve,
a decisive audit-vs-benchmark crossover, and a bounded case against over-engineering
an adaptive system. Chosen on the numbers above, not on how the framing sounds.

## What this does not do

Does not implement a real active-learning system (the Q6 bound argues against
needing one for this objective, not that it's impossible to build). Does not
extend to a second benchmark or scorer (E-B). Does not start E-E.
