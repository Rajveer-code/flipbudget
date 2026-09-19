# Tier 2 plan — post Tier-1-verdict-B

Per TIER1_VERDICT.md point 4: T-A/T-B unaffected by verdict, pure theory, proceed
independently. Audit-expansion (point 3) is the concrete empirical next step but its
*execution* (new labelling) is the user's own labour — I can only design it.

Scope for this pass: T-A + T-H (theory), T-B (theory), audit-expansion design
(computation only, no new labels). NOT started: E-C, E-H, T-D, T-E, T-G, E-B, H-A-F —
correctly out of scope per masterplan §14 Tier 2/3 ordering and per the verdict.

## Tasks

- [x] 1. **T-A — Scorer Sensitivity Model.** Replace the additive (α,β) box with an
      odds-ratio-Λ-bounded family (MSM analogue, unit-level-own-nominal baseline, matching
      Tan 2006 / Zhao-Small-Bhattacharya 2019 convention — NOT a cross-model shared
      baseline, that is T-C's job). Derive: the Λ-transform, nesting/monotonicity in Λ,
      Λ=1 recovery of the point estimate, and the resulting (α,β) rectangle endpoints.
      Verify: sympy symbolic + numeric grid, same dual-check pattern as T1.
      Script: `scripts/fb_ta_ssm.py`. Doc: `TA_SSM_DERIVATION.md`.
      Verify step: script runs clean, symbolic checks pass, numeric grid confirms nesting
      and corner property on real E4 (a, α̂, β̂) triples.

- [x] 2. **T-H — sharpness under the SSM.** State plainly whether this is new machinery or
      a corollary of T1's corner-extrema theorem (my derivation suggests the latter,
      since the Λ-region is still an axis-aligned rectangle in (α,β) — just reparameterized
      in odds space). Do not claim more novelty than is true.
      Verify step: numeric grid search over the Λ-rectangle confirms extrema at corners,
      matching T1's established check.

- [x] 3. **T-B — design sensitivity Λ̃.** For a real model pair, find the Λ at which the
      Λ-bounded identified interval for Δ*=A1*-A2* first contains 0, using n=∞ (population,
      i.e. plug in observed a1,a2 directly — no sampling noise) so the result does not
      depend on benchmark n. Attempt sympy closed-form solve; if none exists, bisection
      (adapt `flip_budget()` from `fb_t2_flipbudget.py`) and report that honestly rather
      than overclaiming "closed form" from the masterplan sketch.
      Script: `scripts/fb_tb_design_sensitivity.py`. Run on real E4 per-model pairs.
      Verify step: script runs, bisection root confirmed against direct grid scan,
      Λ̃ values reported for real pairs with no fabricated numbers.

- [x] 4. **Audit-expansion design (computation only).** Reuse `ea_dominance_study.py`'s
      data-loading path for per-model (n0=n_used_wrong, n1=n_used_credited, α̂, β̂). Compute,
      for T-C's item-overlap test and E-E's AUC test, the additional wrongness-event count
      needed for adequate power (target 80%), stratified toward low-accuracy and any-α>0
      models (oversample, not proportional). Output: a concrete prioritized worklist
      (which models, how many more items, expected event yield under current α̂,β̂) —
      NOT new labels. Flag explicitly at the end: executing this requires the user's own
      manual labelling, a genuine blocker I cannot do myself.
      Script: `scripts/fb_audit_expansion_design.py`. Output:
      `results/flipbudget/audit_expansion_design.json` +
      `AUDIT_EXPANSION_DESIGN.md`.
      Verify step: script runs, numbers trace to real per-model audit counts, no invented
      figures.

- [x] 5. Commit each of 1-4 separately (real granularity), push.

## Explicit non-goals this pass

E-C, E-H (Tier 2 empirical — need compute/model runs, larger undertaking, not blocked by
audit expansion per se but not requested this turn). T-D, T-E, T-G, E-B, E-D, H-A-F (Tier
3 — explicitly wait for audit expansion per verdict). No new human labelling performed by
me under any circumstance.
