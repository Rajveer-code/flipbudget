# T-B for the compound model — a saturation finding, not just an extension

Per your instruction: derive design sensitivity for the actual final (compound)
model, checking sharpness and boundary cases thoroughly. Script:
`scripts/fb_tb_compound_design_sensitivity.py`. Results:
`results/flipbudget/tb_compound_design_sensitivity.json`. **The boundary-case
check surfaced something bigger than an extension: most real pairs on this
roster are formally unidentified from Wilson-CI uncertainty alone, no Λ
required.**

**Superseded, see `RECONCILIATION_FOUR_LAYERS.md`.** Two corrections there: (1)
"unbounded" is wrong vocabulary — accuracy is a proportion, bounded in [0,1] by
definition; the correction *expression* diverges, not the identified accuracy
itself (fixed: identified sets now intersect with [0,1], correctly capped at
width 1, not literal infinity). (2) The 73.5%-saturated figure conflated audit
thinness with genuine scorer non-uniformity. Properly separated: audit-estimation
uncertainty alone explains 91/136 pairs (66.9%), scorer-sensitivity alone only
15/136 (11.0%, barely above the 8.8% sampling baseline) — **verdict B, mostly
finite-audit uncertainty, not a demonstrated scorer-non-uniformity mechanism.**
The saturation *mathematics* below (lambda_saturate, the vertex-theorem
precondition failing past the singularity) is still correct and still the right
diagnostic; only the "unbounded" description and the un-decomposed headline
number are corrected.

## What "checking boundary cases thoroughly" found

First version reused `fb_ta_compound_interval.py`'s clip-to-boundary convention at
the larger Λ values a real search has to explore. The sharpness spot-check
(grid vs. corners) **failed**: grid max 106 vs. corner max 1.4 — not close. Root
cause, verified directly: at Λ=3 with a moderate audit, `alpha_hi + beta_hi =
1.276` — **the compound box's worst corner exceeds the α+β=1 singularity.**

This is not a numerical bug. The linear-fractional vertex theorem (T-H) requires
the denominator to have constant sign over the *whole* region being optimized.
Once a box straddles α+β=1, its feasible part contains points arbitrarily close
to the true singularity, where `g` is genuinely unbounded — confirmed directly:
grid max grows 8.4 → 73.7 → 693 → 4,602 as the feasibility cap tightens toward 1,
never settling. Clipping the corner to a fixed epsilon past that point produces
an arbitrary finite number with no principled meaning — exactly what the failed
check caught.

## The fix

`lambda_saturate(x_alpha, n_alpha, x_beta, n_beta)`: the smallest Λ at which a
model's own box first reaches the singularity. `design_sensitivity_compound` now
bisects **only** within the region where both models' boxes remain strictly
feasible, and reports crossing into saturation as a distinct status
(`saturated_at_L1`, `flippable_via_saturation`) rather than folding it into an
ordinary "flippable" verdict with a meaningless number. Re-verified sharpness
*below* saturation (grid matches corners exactly) and genuine divergence *above*
it (grid max diverges as the cap tightens, not a clipping artifact) — both pass.
One more real bug caught fixing this: the Λ=1 boundary check initially picked an
already-saturated pair (`01-ai/Yi-1.5-9B-Chat`, n1_audit=1) without checking,
comparing two meaningless numbers. Fixed by selecting a pair verified
not-yet-saturated at Λ=1 first.

## Real result — the headline

Of 136 real MATH-Hard pairs:

| Status | n | % | Meaning |
|---|---|---|---|
| **saturated_at_L1** | **100** | **73.5%** | Wilson CI alone, zero Λ, already unbounded |
| degenerate | 24 | 17.6% | Bounded Wilson-only interval already contains 0 |
| flippable | 12 | 8.8% | Genuine bounded sign change, median Λ̃=1.10 |
| robust | 0 | 0% | — |

**Zero pairs are robust.** Every one of 136 real comparisons is either already
formally unidentified from audit uncertainty alone (100), already ambiguous at
the point-CI level (24), or flips at a Λ barely above 1 (12, median 1.10 — not
even a "modest" sensitivity value, essentially at the point estimate already).

## This does not contradict E-A — it reveals E-A's floor was hiding this

E-A's `denom_floor=0.95` **drops** near-singular corners — a defensible choice
for that analysis, but it means E-A's own headline numbers never had the chance
to show a box that's actually unbounded; dropping a corner produces a smaller,
finite-looking width instead of "undefined." This script does not drop —
it detects saturation explicitly and reports it as its own category. **The
100/136 saturated figure is not a new phenomenon E-A missed; it's the same
audit-thinness E-A already found (median audit n=11/model), now shown at full
mathematical strength instead of through a floor that silently produces a finite
number where the honest answer is "unbounded."**

**Not resolved here, deliberately:** whether to update E-A's own headline
methodology in light of this is a real, separate decision — flagged, not made
unilaterally. This result stands on its own as T-B's contribution; reconciling
it with E-A's published numbers is a manuscript-level judgment call, yours to
make.

## Other boundary cases, confirmed

- Λ=1 collapses exactly to the pure Wilson-CI comparison (on a genuinely
  non-saturated pair, verified after fixing the selection bug above).
- Benchmark-n invariance holds by construction (the function has no `n_bench`
  argument).
- Audit n=0 excluded via `build_model_table`'s own qualifying-model filter
  (reused, not reimplemented).

## What this does not do

Does not reconcile with E-A's headline. Does not attempt Λ-only anchoring (the
shrunk-vs-raw question from `TA_BOUNDARY_AUDIT.md`) inside the compound model —
compound never anchors at a single point, so that question doesn't apply here.
