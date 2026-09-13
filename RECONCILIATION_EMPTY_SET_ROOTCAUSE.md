# Root-causing the 70/136 scorer-only-layer empty identified sets (item 2)

Previously flagged in `RECONCILIATION_EMPTY_SET_BUG.md` and `FINAL_DECISION.md`
as "not yet root-caused beyond a plausible hypothesis." Now resolved.
Script: `scripts/fb_rootcause_empty_scorer_layer.py`. Output:
`results/flipbudget/rootcause_empty_scorer_layer.json`.

## Answer: it is one cause, cleanly, not several

**Emptiness at the scorer-identification-only layer (Λ=2, anchored at the
pooled/shrunk α,β estimate) is a per-model property.** Exactly **5 of the 17
qualifying models** have an empty box; every pair involving any of these 5
is excluded, which rolls up to 70 of 136 pairs (60 with exactly one side
empty, 10 with both sides empty — independently re-derived here and matches
the previously-reported 70 exactly).

| Model | a_hat | alpha_pooled | Margin below zero |
|---|---|---|---|
| `CohereForAI/c4ai-command-r-v01` | 0.000 | 0.0541 | 0.0286 |
| `tiiuae/falcon-7b` | 0.005 | 0.0312 | 0.0107 |
| `EleutherAI/gpt-j-6b` | 0.012 | 0.0312 | 0.0038 |
| `mosaicml/mpt-7b` | 0.013 | 0.0310 | 0.0029 |
| `tiiuae/falcon-40b` | 0.015 | 0.0312 | 0.0007 |

All five have MATH-Hard accuracy under 0.02 — the weakest models on the
roster. All five are excluded for **exactly the same reason** (checked, not
assumed): the binding corner is `(alpha_lo, beta_lo)` in every case, and
**the point estimate alone, at Λ=1 with no sensitivity widening at all, is
already inconsistent** (`a_hat < alpha_pooled`) for all 5. Zero of the 5 are
"Lambda-widening-driven" (a case that would look consistent at Λ=1 but break
once Λ=2 widens the band) — the full breakdown asked for in item 2's list
reduces to two non-empty buckets:

| Candidate cause | Models |
|---|---|
| α+β constraint interacting with the Λ=2 band | 0 |
| Audit-estimation uncertainty (Wilson-CI width) | 0 — this is the Λ layer, not the Wilson-CI layer; audit-only emptiness is a separate, already-reported 16/136 |
| Observed accuracy | Necessary condition for all 5 (each has a_hat < 0.02) |
| **Partial pooling / empirical-Bayes shrinkage** | **5/5 — the actual mechanism** |
| Model-specific estimation | Subsumed by pooling: these models individually have 0 raw false-credit events observed (`alpha_raw` is `None` or ~0 for several — see `TC_ALPHA_BETA_UPDATE.md`), so their *own* data alone would give alpha≈0; it is the pooling toward the roster-wide anchor (~0.03, set by higher-accuracy models with real false-credit events) that pushes their box above their own tiny accuracy |
| Scorer-model mismatch | Not indicated — no evidence the scorer behaves differently on these models specifically |
| Numerical boundary (α+β→1) | Not triggered — margins are small (0.0007–0.0286), nowhere near the straddle boundary |
| Incompatibility of the measurement model itself | This IS what "empty set" formally means here — see definition below |

## The mechanism, precisely

The global pooled anchor `alpha_pooled ≈ 0.03` is shared across the roster
(via the empirical-Bayes shrinkage documented in `TC_ALPHA_BETA_UPDATE.md`)
because it is estimated mostly from models with enough accuracy headroom to
produce observable false-credit events. A model whose own accuracy is below
that anchor (0.000–0.015 here) is told, in effect, "your false-credit rate is
assumed to be around 3%, but that would require more of your credited answers
to be secretly wrong than you have *correct* answers at all" — which is
exactly the accuracy-identity contradiction the empty-set check is designed
to catch. **This is a real, correct behavior of the pooling model on very-low-
accuracy models, not a bug and not a coincidence affecting an arbitrary 5.**

## Is "empty identified set" a formal diagnostic — and its definition

**Yes.** Formal statement, stated once so it can be cited directly:

> **Definition (empty identified set under Λ-sensitivity).** Given observed
> accuracy `a`, pooled point estimate `(alpha_pooled, beta_pooled)`, and
> sensitivity level `Λ ≥ 1`, the identified set for the true accuracy `A*` is
> empty iff no `(alpha, beta)` within odds-ratio `Λ` of `(alpha_pooled,
> beta_pooled)` satisfies the measurement identity `a = A*(1-beta) +
> (1-A*)alpha` for any `A* ∈ [0,1]`. This is a falsifiable, checkable
> condition on the triple `(a, alpha_pooled/beta_pooled, Λ)`, not an
> estimation failure — it means the assumed scorer-error model (this Λ, this
> anchor) is logically inconsistent with this model's observed performance,
> and the correct response is to REPORT no identified comparison exists for
> that model under that assumption, not to widen Λ post hoc until it
   disappears (which would be Λ-shopping) or to silently clip to a
   spuriously bounded interval (the original bug).

## What this changes

`FINAL_DECISION.md`'s "new open question, found in this pass, not yet
closed" is now closed: the 51.5% scorer-only exclusion rate is fully
explained by 5 specific, named, very-low-accuracy models whose roster-wide
pooled anchor exceeds their own accuracy — not a general problem with the
Λ=2 band choice, and not evidence the scorer-sensitivity layer is broadly
uninformative for this roster (12 of 17 models, and all pairs among them,
remain well-defined). `EVIDENCE_TABLE.md` and `FINAL_DECISION.md` updated
accordingly.
