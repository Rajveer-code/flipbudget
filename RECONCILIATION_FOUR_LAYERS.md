# Four-layer reconciliation — verdict B, and a math correction

Per your instruction. Script: `scripts/fb_reconcile_layers.py`. Results:
`results/flipbudget/reconciliation_four_layers.json`. **This supersedes the
73.5%/"unbounded" framing in `TB_COMPOUND.md` — corrected here, not silently
rewritten there (see the pointer added to that file).**

## Part 1 — the math correction, made precise

"Accuracy is unbounded" was wrong and should not have been written. `A*` is a
proportion — bounded in `[0,1]` by definition, always. What actually happens:
the **unconstrained correction expression** `g(a,α,β) = (a-α)/(1-α-β)` diverges
as `α+β→1`. That is a statement about an algebraic expression, not about a
probability.

**Precise statement.** The identity `a = A*(1-β) + (1-A*)α` (law of total
probability) has a solution with `A*∈[0,1]` only for *some* `(α,β)` pairs. When
`g(a,α,β)` falls outside `[0,1]` for a candidate `(α,β)`, that `(α,β)` is
**logically inconsistent with the observed data under any valid accuracy** — not
evidence that accuracy itself left `[0,1]`. The correct identified set is
`{g(a,α,β) : (α,β) ∈ box, denom>0} ∩ [0,1]`, and its width is consequently
**always ≤ 1**.

Implemented directly (`bounded_single_model_extrema`): corners give the exact
range when the box doesn't straddle `α+β=1` (T-H's vertex theorem, valid there);
when it does straddle, a grid restricted to the feasible region empirically
confirms the range already exceeds `[0,1]` by a wide margin (the divergence
proven in `TB_COMPOUND.md` guarantees this), so clipping to `[0,1]` is the
correct answer, not an approximation. Sanity-checked both paths before trusting
any downstream number: non-straddling boxes match exact corner evaluation
exactly; the known-straddling example from the T-B audit returns exactly
`[0,1]`, not a smaller or literally-infinite number.

## Part 2 — the reconciliation table

136 real pairs, reference Λ=2.0 (the "modest sensitivity" value used throughout
this project) for the two Λ-dependent columns:

| Layer | Median width | Unresolved (contains 0) | % |
|---|---|---|---|
| **Sampling** (field's current practice, α=β=0 assumed) | 0.043 | 12/136 | 8.8% |
| **Audit-estimation-only** (Wilson CI, Λ=1, no sensitivity) | 0.264 | 91/136 | 66.9% |
| **Scorer-identification-only** (pure Λ=2, shrunk anchor, α/β treated as known) | 0.039 | 15/136 | 11.0% |
| **Combined** (Wilson CI further Λ-widened, Λ=2) | 0.423 | 110/136 | 80.9% |

## Part 3 — decomposition

- **Unresolved under audit-only but NOT scorer-only: 76** — driven purely by the
  finite audit sample.
- **Unresolved under scorer-only but NOT audit-only: 0.**
- **Unresolved under both: 15.**
- **Unresolved only when combined (neither alone sufficient): 19.**

**76 of the 110 combined-unresolved pairs (69%) are explained by audit thinness
alone**, with zero pairs driven purely by scorer-sensitivity in isolation.
Scorer-identification-only (11.0%) sits close to the sampling baseline (8.8%) —
a real but modest gap of 3 pairs out of 136, not the dramatic effect the
"73.5% saturated" framing implied.

## Verdict: **B — mostly finite-audit uncertainty**

Audit-estimation-only unresolved count (91) is more than 6× scorer-only (15).
The dominant driver of "we don't know if this comparison is real" is **the
audit sample is too small to pin down α, β** — not that the scorer's errors are
highly non-uniform across items. Not manufactured to look stronger or weaker
than the numbers support: scorer-only is genuinely above the sampling baseline
(11.0% vs 8.8%), so it is not *nothing* — but it does not carry the finding on
its own.

## What this means for the headline, stated plainly

**This does not kill the program — it relocates its center of gravity.**
E-A's *original* "identification width dominates sampling width" finding
(Tier 1, before T-A/Λ existed at all) was **always**, in substance, about this
same audit-estimation-only quantity — E-A never had a separate Λ-layer to begin
with. This reconciliation shows that finding was correctly diagnosing a real
phenomenon: the audit is too thin. What it does **not** support is treating
"scorer errors are non-uniform enough to flip rankings" as a demonstrated
mechanism — that claim needs the scorer-only layer, which is modest.

**Concretely:** the strongest, best-supported claim this project can make right
now is *"reported benchmark comparisons carry an unreported uncertainty
component driven by how imprecisely the scorer's true error rate is currently
known — fixable by auditing more items"* — not *"scorer error is inherently and
substantially non-uniform across items."* The former is a measurement/audit-design
finding; the latter is a mechanism claim this data does not yet support at Λ=2.
This also directly connects to the audit-expansion work already done earlier
this session (`AUDIT_EXPANSION_DESIGN.md`) — more audited items is not just useful
for T-C/E-E, it is the direct fix for the single largest source of ambiguity
found here.

## What this does not do

Does not test other reference Λ values (2.0 was a design choice, stated as such
— a sensitivity check across Λ=1.5/3/5 would strengthen this further, not done
this pass). Does not update `TIER1_VERDICT.md`'s own verdict B — that was about
a different question (T-C/E-E power) and stands independently.
