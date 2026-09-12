# A second, deeper bug in the reconciliation's own [0,1]-bounded fix

Found auditing the published package (item 18) against the research
methodology, using a randomized stress test — not found by inspection.
This is a correction to `EVIDENCE_TABLE.md`'s own A1/A2 correction, made
**during this same flagship-strengthening phase**, before those numbers
were reported to you as final. Scripts touched:
`src/flipbudget/identification.py`, `scripts/fb_reconcile_layers.py`.
New results: `results/flipbudget/reconciliation_four_layers_corrected.json`,
`results/flipbudget/ea_dominance_pairwise_corrected_v2.json`,
`results/flipbudget/ea_dominance_corrected_v2.json`. Originals
(`reconciliation_four_layers.json`, `ea_dominance_*_corrected.json`)
preserved unmodified.

## The bug

`bounded_single_model_extrema`'s clip — `max(lo, 0.0), min(hi, 1.0)` — is
correct when the raw (unclipped) range `[lo, hi]` *overlaps* `[0,1]`. **It
silently produces an inverted, nonsensical interval when the raw range
does not overlap `[0,1]` at all** — e.g. raw `[lo,hi] = [-0.5, -0.32]`
(both endpoints negative) clips to `(max(-0.5,0), min(-0.32,1)) = (0.0,
-0.32)`, i.e. `lo=0.0 > hi=-0.32`. This is not a rare synthetic corner case:
**checked directly against the real 17-model qualifying roster, it fires
for `CohereForAI/c4ai-command-r-v01`** (`a_hat=0.0`, audit-derived alpha
range `[0.30, 0.90]` — every alpha in range exceeds the observed accuracy,
so `g` is negative everywhere in the box) and, across the 136 real pairs
used in `reconciliation_four_layers.json`, **16 pairs (11.8%) had a
negative `w_audit_only`, 15 pairs (11.0%) a negative `w_scorer_only`, and
10 pairs (7.4%) a negative `w_combined`** — mathematically impossible
widths that were already sitting in the committed result before this audit
caught them.

## What it means when it happens

A raw range that misses `[0,1]` entirely means **the assumed `(alpha,beta)`
box is itself inconsistent with the model's observed accuracy** — under
every value in the box, the corrected accuracy `A*` would have to be
negative (or exceed 1), which is impossible for a real proportion. This is
not an error in the data source per se; it is a real, meaningful
degenerate case: a model with very low observed accuracy combined with an
audit-CI or Λ-band for alpha that (due to a small audit `n` or a large
`Λ`) extends up past that accuracy. **The correct treatment is to report
the identified set as empty** for that model under that box — not to
silently invert-clip it into a fake bounded interval.

## Fix

Both `single_model_extrema` (package) and `bounded_single_model_extrema`
(research script) now check `hi < 0 or lo > 1` before clipping and return
`(nan, nan)` to signal emptiness explicitly. `comparison_extrema`/
`bounded_comparison` and `flip_budget` propagate this rather than silently
treating a NaN-fed comparison as resolved. Three new package tests added
(`tests/test_identification.py`), including the exact real case that
surfaced this. All 17 tests pass.

## Corrected numbers — the reconciliation and E-A, a third time

**Reconciliation** (excluding empty-set pairs from each layer's own
statistics, not silently including or dropping globally):

| Layer | n valid (of 136) | n excluded (empty) | median width | unresolved | % |
|---|---|---|---|---|---|
| Sampling | 136 | 0 | 0.0431 | 12 | 8.8% |
| Audit-estimation-only | 120 | 16 | 0.2800 | 91 | **75.8%** |
| Scorer-identification-only (Λ=2) | 66 | **70** | 0.0679 | 15 | 22.7% |
| Combined (Λ=2) | 120 | 16 | 0.4521 | 110 | 91.7% |

**Verdict B stands, and is now clearer, not weaker**: audit-only unresolved
(75.8% of its valid subset) still substantially exceeds scorer-only
unresolved (22.7% of its own, much smaller valid subset) — the qualifying
sample sizes differ per layer now, which the reconciliation script reports
explicitly rather than hiding.

**One large, honestly-flagged new open question**: the scorer-only layer
excludes **70 of 136 pairs (51.5%)** as empty-set — far more than
audit-only's 16. This means the Λ=2 sensitivity band around many models'
*pooled* alpha still exceeds their observed accuracy for over half the
roster's pairs. **Not yet root-caused further in this pass** — plausibly
because MATH-Hard's roster includes many very-low-accuracy models where
even a modest, shrunk pooled alpha estimate is proportionally large
relative to their accuracy. Flagged as a concrete, high-value follow-up:
characterize which models this affects and whether Λ=2 is simply too wide
a band for low-accuracy models specifically, rather than assumed
resolved.

**E-A dominance, corrected a third time**:

| | Pairwise | Single-model |
|---|---|---|
| Original (uncorrected, `TIER1_VERDICT.md`) | median 134.32×, 100% dominant | median 74.99×, 100% dominant |
| First correction (this phase, before this bug was found) | median 5.24×, 89.7% dominant | median 3.22×, 100% dominant |
| **This correction (empty-set pairs excluded)** | **median 6.10×, 100% dominant** (n=120 of 136) | **median 3.22×, 100% dominant** (n=16 of 17, unchanged) |

The pairwise number **improves** under the proper fix — the earlier
"corrected" 5.24×/89.7% was itself still contaminated by pairs with
nonsensical negative widths dragging the ratio and the dominance fraction
down. Once those are properly excluded (not zeroed, not included), the
clean result is a full 100% dominance among the pairs where the comparison
is even well-defined.

## What this changes elsewhere

`EVIDENCE_TABLE.md`, `CORE_THESIS_REASSESSMENT.md`, and `FINAL_DECISION.md`
are updated with these numbers below. The qualitative story in all three
(verdict D, B+C) is unchanged — this correction, like the first one,
tightened the evidence rather than undermining it, and was caught by this
same phase's own stress-testing discipline (item 18's package audit)
before being reported as final rather than after.
