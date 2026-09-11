# E-E feature-selection design check — before any new labeling

Per your instruction: do not label E-E's 6,742 items until this is resolved. Script:
`scripts/fb_ee_feature_stability.py`. Results:
`results/flipbudget/ee_feature_stability.json`.

## 1. Reconstruction

The 5 features (`n_newlines`, `ends_with_period`, `has_therefore`, `n_frac`,
`char_length`) were the top-5 by `|standardized coefficient|` from a
`class_weight="balanced"` logistic regression fit on all 350 records — **5 positive
events**. That is genuinely selection-on-the-outcome at a sample size far below
where such a ranking is normally trusted. Correct to be suspicious of it; tested
below rather than assumed either way.

## 2–3. Stability (leave-one-out, leave-one-positive-out, 2000-resample bootstrap)

**The picture is not uniform across the 5 — and that's the real finding.** Four
features are robustly stable by every check:

| Feature | Bootstrap top-5 selection freq. | Sign consistency | LOO (5 positive-event removals) |
|---|---|---|---|
| `n_newlines` | 1.000 | 1.000 | unanimous |
| `ends_with_period` | 0.983 | 0.995 | unanimous |
| `has_therefore` | 0.975 | 1.000 | unanimous |
| `n_frac` | 0.780 | 1.000 | unanimous |
| **`char_length`** | **0.570** | **0.663** | **flips in 1 of 5 removals** |

`char_length` is the weak link — its bootstrap selection frequency (0.570) is
barely above chance and is in a near-tie with `n_dollar_signs` (0.521, not in the
original set) for the 5th slot; its sign also flips in a third of the bootstraps
where it's selected at all (0.663, vs ≥0.995 for the other four). The one real
leave-one-positive-out disagreement (dropping event #54) is driven exactly by this:
`char_length` gets replaced by `n_dollar_signs`. Two independent methods
(bootstrap, LOO) agree on *where* the instability is, which is itself evidence the
finding is real, not resampling noise.

Pre-registered (written into the script before running it) verdict rule — "≥3 of 5
features selected in ≥50% of bootstraps AND ≥3 of 5 LOO removals match" — is
cleared, mechanically. **Stated plainly: that rule is blunt and passes the full
5-feature set on a technicality (char_length clears 0.50 by two points).** Looking
past the mechanical rule at the full pattern is a better read of the same numbers,
not a different result.

## 4. Comparison against the two alternatives

- **Full 9-feature spec**: needs 90 events. Ceiling is 52.7. Unreachable, confirmed
  last pass.
- **Data-driven top-5**: needs 50 events. The 6,742-item worklist already built for
  this reaches 50.1.
- **Pre-specified mechanism set** (`has_boxed`, `n_frac`, `n_dollar_signs` — chosen
  from the scorer's actual extraction algorithm and Phase 1's own E2 `dfrac`
  false-miss finding, **not** from fitting against wrongness): needs only 30
  events. `has_boxed` turns out to be a poor individual predictor at this n — not
  because the mechanism reasoning is wrong, but because 329 of 350 responses
  (94%) already contain `\boxed{}`; there's almost no variance left for a
  350-row logistic fit to use. `n_frac` is the one feature that is *both*
  mechanistically pre-specified *and* among the most stable data-driven features —
  the strongest convergent evidence in this whole check.

## The actually-smallest defensible set: 4 features, not 5

Dropping `char_length` — the one feature that fails cleanly on both selection
frequency and sign stability — leaves `n_newlines`, `ends_with_period`,
`has_therefore`, `n_frac`: **all four ≥0.78 selection frequency, ≥0.995 sign
consistency, unanimous under every leave-one-positive-out removal.** This needs
only **40 events** (EPV≥10×4), smaller than the 50-event target the current
6,742-item worklist targets. This is not chosen to shrink the labeling ask for its
own sake — it falls out of removing the one demonstrably weak feature, and the
smaller ask is a consequence, not the reason. Flagging that directly since the
alignment could look convenient: dropping a bad predictor and needing fewer labels
both follow from the same evidence, independently.

**This cut point (4 vs 5) was chosen after seeing the numbers**, not
pre-registered like the mechanical rule above — said plainly, not hidden. The
justification (a visible, large gap in both metrics, not a threshold tuned to
produce this exact split) is stated so you can judge it yourself rather than take
my word for it.

## Verdict

Not a clean binary — the data don't force either "fully stable, proceed as-is" or
"unstable, abandon E-E." **Partial:** 4 of 5 originally-selected features are
genuinely robust; the 5th was a coin flip that the mechanical rule let through.
Three real options, not defaulting to any of them:

1. **4-feature core** (`n_newlines`, `ends_with_period`, `has_therefore`, `n_frac`)
   — smallest event target (40), strongest stability evidence, drops the one weak
   feature. My recommendation, but not assumed.
2. **Original 5-feature set** — technically clears the pre-registered bar, needs
   50 events, carries one demonstrably shaky feature into a large labeling
   investment.
3. **Mechanism-3 set** (`has_boxed`, `n_frac`, `n_dollar_signs`) — smallest event
   target (30), zero dependence on the fragile fit, but includes `has_boxed`,
   which this data shows has little discriminative power at current n (may still
   matter with more events; can't tell yet).

Have not rebuilt the labeling worklist for any of these — waiting for you to pick,
since dropping to 4 features changes what "6,742 items" even means and I don't
want to silently replace a number you're weighing a decision against.
