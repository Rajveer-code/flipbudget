# T-A boundary audit — the zero-width finding was a parameterization artifact

Per your instruction: audit whether "15 of 17 models have zero Λ-only width" is a
genuine structural property of the SSM or a boundary artifact. Script:
`scripts/fb_ta_boundary_audit.py`. Results: `results/flipbudget/ta_boundary_audit.json`.
**Verdict: artifact, confirmed, and now corrected.** This revises a claim in
`TA_COMPOUND_INTERVAL.md` — flagged here, not silently rewritten there.

## 1. The algebra is correct; the anchoring choice was not the right one

`λ(0,Λ) = 0` and `λ(1,Λ) = 1` for every Λ — confirmed symbolically as genuine
fixed points, not a bug. A raw proportion of exactly 0 has zero odds; scaling zero
by any finite factor is still zero. That's real. The question was whether this
changed the headline finding — it did, substantially.

## 2. Cross-tabulation exposed an overstatement I hadn't caught

The original claim didn't separate the 15 zero-width models by audit robustness.
Doing that now:

- **Robust subset (n0≥5, n1≥5), 3 of 5 models zero-λ**: `c4ai-command-r-plus`,
  `Qwen2-7B`, `Llama-3-70B-Instruct`. Their compound widths (5.89, 0.92, 0.40) are
  **sane, non-pathological** — this part of the original claim holds up.
- **Thin subset (excluded from any headline by E-A's own filter), 12 of 12 models
  zero-λ**: compound widths range from 0.8 to **880**. These are the same
  near-singular-audit pathology E-A's `denom_floor=0.95` exists to guard against.
  My original write-up reported "15 of 17... compound is the only signal" without
  separating these from the 3 robust cases — technically true of the count, but it
  let numbers up to 880 stand next to a claim of "the main signal" without the same
  caveat I'd already applied to the headline stat elsewhere in the same document.
  **That was an overstatement; corrected here.**

## 3. Raw vs. shrunk anchor — the actual fix

Recomputed Λ-only width anchoring at `alpha_pooled`/`beta_pooled` (the E4
pipeline's own existing empirical-Bayes shrinkage estimate — not a new invention)
instead of the raw per-model rate, for all 17 models:

**15 of 15 degenerate (zero-width) cases resolve under shrunk anchoring — 100%.**
Every model that showed `w_lambda=0` under the raw anchor gets a real, non-zero,
sensible width (0.025–0.048, a tight, plausible band) once anchored at the pooled
estimate instead. This is decisive: **the raw point estimate — not the SSM's
mathematical structure — was the source of the degeneracy.**

## The fix, adopted

**T-A's pure Λ-only construction should anchor at the shrunk (α_pooled, β_pooled)
estimate, not the raw one, going forward.** Justification: the shrunk estimate is
already the project's own best estimate of "this model's typical rate" under
audit sparsity (used for exactly this reason in `fb_audit_expansion_design.py`) —
using the raw, possibly-zero-by-chance count as the Λ=1 anchor was inconsistent
with that established practice, not a considered choice.

**The compound construction does not need this fix.** It never anchors at a
single point — it Λ-widens outward from the Wilson CI's own endpoints, and a
Wilson upper bound is never exactly 0 even when the raw count is 0. Compound
width was never degenerate; its only real issue (thin-audit blowup) was already
known and already excluded from the headline via the robust-subset filter. That
part of `TA_COMPOUND_INTERVAL.md` stands.

## Corrected reading of the original claim

"15 of 17 models have zero Λ-only width" → **true under the raw anchor, an
artifact of that anchor, and not true at all under the shrunk anchor (0 of 17
degenerate).** "Compound is the only signal" → **true and meaningful for the 3
robust-subset zero-λ models (sane compound values); not a claim that should have
been extended to the 12 thin-audit models whose large compound values were
already known to be unreliable for an unrelated, already-documented reason.**

## What this does not do

Does not re-run the full real-data compound/Wilson/Λ table with the shrunk
anchor substituted everywhere — the scientific question (artifact vs. structural)
is answered decisively by the 15/15 result above; re-generating every downstream
table is a mechanical follow-up, not a new finding, and is deferred given T-B is
next in the priority order you set.
