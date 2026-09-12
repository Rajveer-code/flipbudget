# Audit-design stress test (item 5)

Script: `scripts/fb_audit_design_stress_test.py`. Result:
`results/flipbudget/audit_design_stress_test.json`. Question: do
`AUDIT_DESIGN_ANALYSIS.md`'s conclusions (Neyman allocation beats the
current design; adaptive doesn't beat static Neyman) hold outside MATH-Hard's
exact observed numbers, or are they an artifact of this one configuration?

## Neyman allocation: qualitative conclusion survives everywhere tested

Six scenarios (MATH-Hard-like, rare-error <1%, common-error >20%, balanced
strata, one very small stratum, IFEval-like 3-strata) plus a heterogeneous
30-model sweep: **Neyman allocation weakly dominates both proportional-by-
size and equal allocation in every single scenario** — never loses, exactly
as the classical result (Neyman 1934) guarantees, cited and reused rather
than re-derived.

**The *magnitude* of the gain is highly scenario-dependent, and this
contextualizes rather than contradicts `AUDIT_DESIGN_ANALYSIS.md`'s
headline 77% figure.** Against a *proportional-by-population* baseline, the
variance cut ranges from 0.0% (one stratum population so small it barely
matters which allocation is used) to 7.0% (IFEval-like, where one stratum
sits at `p≈0.9` and another at `p≈0.025` — the widest spread in variance
structure tested). **The original 77% figure was never a comparison against
proportional allocation** — it compared Neyman-optimal against MATH-Hard's
*actual historical* allocation (median 28.6% credited vs. Neyman's ~77%,
`|gap|=0.482` — a large, specific mismatch), which is a much worse baseline
than "proportional" in this case. Both numbers are correct; they answer
different questions ("how much better is Neyman than a sensible default"
vs. "how much better is Neyman than what was actually done"), and the paper
should state which comparison is being made every time this number appears,
not use the 77% figure as if it generalizes to "Neyman always saves ~77%."

## Confidence-level and precision-target sensitivity: sane, monotonic

Required audit-n for a fixed target width (0.02) at `p̂=0.03`: **803 (90%
CI) → 1,139 (95%) → 1,987 (99%)** — monotonically increasing with
confidence, as it must. Required-n across precision targets at 95%
confidence: **17,906 (width 0.005) → 4,499 (0.01) → 1,139 (0.02) → 201
(0.05) → 63 (0.10)** — monotonically decreasing as the target loosens.
Both are sanity checks on the existing Q1 machinery, not new findings —
included because a monotonicity failure would have indicated a real bug in
the required-n calculation, and neither did.

## Model heterogeneity: a real but modest, quantified regret

30 simulated models with heterogeneous true `α ~ U(0.01, 0.15)` and a
shared, near-zero `β` (mirroring the real MATH-Hard structure — `β_pooled
≈ 0` for nearly every real model). Using one shared Neyman allocation
(computed from the *pooled* `α`, since a model's own rate is exactly what
auditing is meant to discover, not known in advance) instead of each
model's individually-optimal allocation costs **1.2% higher average
variance** across the 30 simulated models. **Small, and worth stating
plainly as small** — a single, roster-wide Neyman allocation is a good
approximation to per-model-optimal even under real heterogeneity in this
regime, because Neyman's dependence on `p` through `√(p(1-p))` is fairly
flat except very near `p∈{0,1}`.

## What this does not test

This stress test varies the *inputs* to the existing Neyman/required-n
formulas, not the formulas themselves — it is a robustness check on
**conclusions**, not a new derivation. It does not simulate a full
correlated-error or imperfect-reference scenario jointly with the audit-
design question (those are handled separately in `THEORY_EXTENSIONS.md` §1
and §4); combining all three into one joint simulation is a real, larger
undertaking flagged as future work, not attempted here.
