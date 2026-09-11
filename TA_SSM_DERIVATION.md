# T-A / T-H — the Scorer Sensitivity Model and its sharpness

Full derivation + verification: `scripts/fb_ta_ssm.py`. All checks pass (symbolic +
numeric). This doc states what was proven and what was a design choice.

## The model

Phase 1 (T1/T2) perturbs a model's audited (α̂, β̂) by a fixed additive ±d. Objection:
arbitrary parameterization, not reparameterization-invariant.

**Replacement (T-A):** an odds-ratio bound, the marginal-sensitivity-model (MSM)
analogue from causal sensitivity analysis (Tan 2006; Zhao–Small–Bhattacharya 2019).
For sensitivity parameter Λ≥1, the true rate is allowed to deviate from the model's
**own** audited nominal rate by at most Λ in odds:

```
lambda_transform(p, L) = L*p / (1 + (L-1)*p)        [odds(result) = L * odds(p)]
alpha_lo(L) = lambda_transform(alpha_hat, 1/L)   alpha_hi(L) = lambda_transform(alpha_hat, L)
```
same for β. Λ=1 recovers the point estimate exactly.

**Explicit choice, stated so it isn't silently assumed:** the baseline is each model's
*own* audited (α̂,β̂), not a baseline shared across models. A shared/correlated baseline
is a different, harder model — that is T-C's job (item-level correlation across
models), not this one. Conflating the two would overclaim what T-A establishes.

## What was actually proven

1. **λ-transform properties** (symbolic, sympy): L=1 → identity; odds identity exact;
   strictly increasing in L; involution `λ(λ(p,L),1/L)=p`. All confirmed exactly, no
   floating-point tolerance needed on the symbolic checks.
2. **Range**: unlike the additive box, `λ(p,L) ∈ (0,1)` for every L>0 — no clipping
   needed at the probability boundary.
3. **Nesting**: L1<L2 ⟹ region(L1) ⊂ region(L2), confirmed across 500×30 sweeps. This
   is what makes T-B's bisection well-posed, the same role d-monotonicity played for
   T2's flip-budget bisection.
4. **The collapse to a rectangle.** Because the false-credit process (items with true
   Y=0) and the false-miss process (Y=1) are disjoint populations, any population
   mixture of item-level rates within a shared Λ-band achieves exactly the band's own
   endpoints. So an item-indexed Λ-bound collapses to `[α_lo(Λ),α_hi(Λ)] ×
   [β_lo(Λ),β_hi(Λ)]` — still a rectangle, just with odds-derived endpoints instead of
   Wilson-CI-derived ones.
5. **T-H sharpness — stronger and shorter than expected.** `g(a,α,β)=(a-α)/(1-α-β)`
   is linear-fractional in (α,β): both numerator and denominator are affine. Its upper
   level sets `{g≥t}` are half-planes (confirmed symbolically — the boundary expands
   to degree ≤1 in both α and β, no cross term). A quasi-linear function's extrema
   over **any convex polytope** occur at a vertex — the classical linear-fractional
   programming vertex theorem (Charnes & Cooper, 1962). This is a cleaner and more
   general proof than Phase 1's grid-search-based corner check: it needs no
   axis-alignment, so it covers the Λ-rectangle for free and, as a bonus check, a
   non-rectangular triangle too (verified: 300k interior samples never exceed the
   3-vertex extrema). **T-H is therefore not new machinery — it is a corollary,
   proven properly instead of only grid-checked.**
6. **N-invariance — the mechanism behind "does not shrink with more data."** At fixed
   Λ, the Λ-band width is exactly constant across audit n = 5 to 100,000, while the
   Wilson-CI width (Phase 1's box) shrinks from 0.43 to 0.003 over the same range.
   These are different uncertainty sources: Wilson-CI width is estimation uncertainty
   in α̂,β̂ (shrinks with audit data); Λ-band width is a modeling assumption about
   how non-uniform the scorer's error could be (does not shrink with any amount of
   data, audit or benchmark).

## What this does NOT establish

- Not a claim about which Λ is realistic for any given scorer — that's an empirical
  question (T-B applies this to real pairs; a future adversarial study, E-D, would be
  the way to calibrate plausible Λ ranges from worst-case constructions).
- Not a claim that item-level rates are independent across models — deliberately left
  open for T-C.
- The two uncertainty sources (Wilson-CI estimation uncertainty and Λ-sensitivity) are
  **not yet composed** into one interval here. §T-A of the masterplan notes this
  compound step; it is straightforward (nest the Λ-band around each point in the
  CI region) but not done in this pass — flagged, not silently skipped.
