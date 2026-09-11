# T-A compound step — Wilson-CI + Λ-sensitivity, composed

Script: `scripts/fb_ta_compound_interval.py`. Results:
`results/flipbudget/ta_compound_interval.json`. Closes the item both
`TA_SSM_DERIVATION.md` and `TB_DESIGN_SENSITIVITY.md` flagged as not yet done.

## Construction

`compound_bounds(x, n, L) = (λ(wilson_lo, 1/L), λ(wilson_hi, L))` — Λ-widen
outward from each end of the audit's Wilson CI, instead of from a single point
estimate. Proven: a new symbolic check not done in T-A (`d(λ)/dp > 0`, needed
because compounding requires monotonicity in *both* arguments, not just Λ);
collapses exactly to the pure Wilson CI at Λ=1 and to the pure Λ-band as audit n
grows (excess width shrinks ~365× over 6 decades of n, <0.5% of the band's own
width by n=4,000,000); matches an exhaustive 5,000-point union-over-CI grid to
1e-6.

## Three real bugs, caught before trusting any number

1. **Reintroduced T-B's exact corner-drop bug** in the real-data illustration by
   writing ad hoc inline loops instead of reusing tested functions — produced the
   same symptom (widths in the hundreds, some pools showing exactly 0). Fixed by
   calling E-A's own `single_model_widths()` directly for the Wilson-only number
   instead of a near-copy.
2. **Test tolerance miscalibrated**: expected compound bounds to closely match the
   pure Λ-band at n=4,000 — but Wilson-CI width only shrinks as 1/√n, so a
   "moderate" n still has real width the Λ-transform visibly amplifies. Fixed by
   checking the convergence *trend* across 6 decades of n instead of a single-n
   tolerance.
3. **The nesting guarantee broke on real data**: `bigcode/starcoder2-15b` showed
   compound width (1.86) *smaller* than Wilson-only width (1.95) — impossible,
   since compound's (α,β) region is a proven superset of Wilson's. Root cause:
   using E-A's drop+0.95 floor on compound's wider corners drops *more* of them
   (they sit further from center), so the survivor set can produce a narrower
   range than a smaller, fully-retained box. Fixed by evaluating compound *and*
   its Wilson-only comparison point with the *same* method (clip, T2's original
   convention) — E-A's official drop+0.95 number is kept, unchanged, for
   continuity, but is explicitly not used in the nesting claim, which needs a
   same-method comparison to be mathematically guaranteed rather than assumed.

## Real result

**Headline, E-A's own robust subset (n0≥5 AND n1≥5, 5 of 17 models), Λ=2.0
("modest" sensitivity):** median compound/Wilson-only ratio **2.66×**. Individual
ratios 2.0×–6.6×, except `CohereForAI/c4ai-command-r-v01` at 1.05× — an
already-documented outlier (Phase 1's own "false-credit outlier model" finding:
this model's audited false-credit rate is 66.7%, not a thin-audit artifact, so
both its Wilson-only and compound widths are legitimately huge).

**15 of 17 models have `w_lambda = 0` exactly** — the Λ-transform's fixed point
at `p=0` (observed zero error in a thin audit can't be moved by any Λ). For these,
**compound width is the only non-degenerate identification-uncertainty source at
all** — the clearest, most concrete demonstration of why compounding matters:
the pure-point Λ-model silently claims zero sensitivity for exactly the models
whose audit gives the least information.

## What this does not do

T-B's Λ̃ has not been recomputed under the compound bounds (a natural, clearly
scoped follow-up — swap `lambda_bounds` for `compound_bounds` inside the existing
bisection — not done this pass, flagged rather than rushed given how much
subtlety turned up in T-A's own version).
