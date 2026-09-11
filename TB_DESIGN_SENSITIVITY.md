# T-B — design sensitivity Λ̃

Full derivation + real-data run: `scripts/fb_tb_design_sensitivity.py`. Results:
`results/flipbudget/tb_design_sensitivity.json`.

## What Λ̃ means

Using T-A's Λ-bounded (α,β) rectangles (each model's own nominal audited rate, no
cross-model sharing), Λ̃ is the smallest Λ at which the identified interval for
Δ*=A1*-A2* — evaluated at the true observed accuracies, no sampling noise — first
contains 0. Below Λ̃ the sign of Δ* is identified *regardless of how much benchmark
data is collected*; above it, no amount of data resolves the sign, because the
ambiguity is about scorer non-uniformity, not estimation noise (T-A's n-invariance
result is why this is meaningful at all).

## A real bug this caught

First version reused E-A's `α+β≥0.95` corner-exclusion floor inside the Λ-sweep. That
floor is correct for E-A (protects against thin-audit Wilson CIs landing pathologically
close to the singularity) but wrong here: large Λ is *supposed* to push corners toward
α+β→1, and dropping those corners shrinks the box's effective corner set as Λ grows,
which breaks min/max monotonicity in Λ. Caught because bisection (found "robust, no
flip") and a direct 20,000-point grid scan (found a flip at Λ=1.44) disagreed — the
same "two independent methods must agree" check that caught the T3 bug earlier in this
project. Fixed by clipping to the feasible boundary instead of dropping (T2's original
convention, restored). After the fix, bisection and grid scan agree to 4 decimal places.

## Closed form: attempted, found, and correctly scoped

Which corner of each model's Λ-box binds is regime-dependent (T1: sign(∂g/∂α) is not
fixed). Solved all 16 corner-pairing branches symbolically on a worked example; the
binding branch gives a **degree-3 polynomial in Λ, solvable by radicals**, root
confirmed to match bisection (1.44039 vs 1.44086). So a closed form exists — but
finding it requires first knowing which of 16 branches binds, which is itself
regime-dependent. **Bisection is reported as the practical, general method; the closed
form is real but not the short quotable formula the masterplan sketch hoped for.**

## Real result, MATH-Hard roster (17 qualifying models, 136 real pairs)

- **122 of 136 pairs (89.7%) are robust** — not flippable even at Λ=10,000, an
  extreme odds-ratio deviation from the model's own nominal rate.
- **14 of 136 (10.3%) are flippable** at some finite Λ. Among those: median
  Λ̃=7.26 (IQR [5.87, 8.03]) — a substantial deviation.
- **Only 2 of 136 pairs (1.5%) flip at Λ≤2** — the range Rosenbaum's literature
  usually treats as "a modest, plausible amount of hidden bias." Most fragile:
  **Qwen2-7B vs Yi-1.5-34B-Chat**, Λ̃=1.655, point-corrected gap +0.018.

## This does not contradict E-A — it answers a different question

E-A found identification width (from **Wilson-CI estimation uncertainty** in α,β,
given a median audit of 11 items/model) dominates sampling width almost everywhere.
T-B asks a different question: *given α,β known exactly, how non-uniform would the
scorer's true per-item error need to be to flip the ranking* — and finds most real
pairs are robust to quite large assumed non-uniformity. These are complementary, not
conflicting: **E-A says the current audit is too thin to pin down α,β precisely
(fixable by auditing more items — see the audit-expansion design); T-B says that even
once α,β are known, most rankings are not fragile to plausible scorer non-uniformity,
though a real ~10% minority is, and 1.5% are fragile to a genuinely modest
assumption.** The paper must state both, explicitly reconciled like this — reporting
only E-A would overstate fragility; reporting only T-B would understate it.

## What this does NOT establish

Same scope limits as T-A: own-model-nominal baseline only (no cross-model
correlation — T-C's job), and the two uncertainty sources (Wilson-CI estimation
noise and Λ-sensitivity) are not yet composed into one number.
