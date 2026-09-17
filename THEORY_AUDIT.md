# Final theoretical audit

Checked every named result against the six criteria: correct assumptions,
complete proof, boundary cases handled, correct notation, no hidden
positivity/division assumptions, identified sets distinguished from
confidence sets, population uncertainty distinguished from audit-estimation
uncertainty, empty identified sets correctly treated. Verified against
existing symbolic/numeric test coverage rather than re-derived from
scratch where that coverage already exists and passes — re-deriving a
theorem a passing test already checks would not make it more correct, only
slower to confirm.

## Empty identified sets, straddling boxes, degenerate division — tested, not asserted

`g(a,\alpha,\beta) = (a-\alpha)/(1-\alpha-\beta)` divides by
`1-\alpha-\beta`, which is exactly zero on the line `\alpha+\beta=1` and can
be arbitrarily close to zero near it — the one place a hidden
positivity/division assumption could hide. `tests/test_identification.py`
covers this directly:

- `test_g_can_fall_outside_unit_interval` — confirms the raw (unclipped)
  function is not itself bounded, the premise the whole bounded-clipping
  treatment exists to correct.
- `test_single_model_extrema_straddling_box_clips_to_01` — the
  denominator-sign-change (straddling) case, where the naive 4-corner
  evaluation is provably wrong (§3 of the manuscript); confirms the grid
  fallback correctly saturates to `[0,1]` rather than returning a
  divergent or NaN value.
- `test_single_model_extrema_empty_set_on_real_case` — confirms a real
  `(a,\alpha,\beta)` combination that is logically inconsistent (no
  `A^\ast \in [0,1]` can produce it) returns the explicit empty-set signal
  (`nan, nan`), not a silently-inverted or fabricated interval — this is
  the exact bug this project found and fixed mid-project (§3), now
  regression-tested so it cannot silently return.
- `test_single_model_extrema_always_within_unit_interval_or_empty` —
  property test: every output is either a valid `[0,1]`-bounded interval or
  the explicit empty signal, never anything else, across a grid of inputs.
- `test_flip_budget_returns_none_not_fabricated_on_empty_baseline` —
  confirms the flip-budget calculation, when its own baseline is
  unidentified, returns `None` rather than computing a number from an
  undefined starting point.

All five pass. **No hidden positivity/division assumption survives this
suite** — the one place division could silently misbehave is the one place
tested most directly.

## Identified sets vs. confidence sets — kept structurally separate, not just in words

The manuscript's four-layer decomposition (Section 7.2) is the concrete
enforcement of this distinction, not just a stated principle:
*scorer-identification-only* is a **partial-identification** object (the
$\Lambda$-sensitivity envelope at a fixed, exactly-known $(\alpha,\beta)$
point — a set that would not shrink with infinite audit data, because
identification and estimation are different problems). *Audit-estimation-only*
is a **confidence-set** object (a Wilson CI around the audited
$(\alpha,\beta)$ point estimate — shrinks as the audit grows, because it is
about not knowing the parameter precisely, not about what the parameter
value implies). These are computed as genuinely separate quantities in
`fb_reconcile_layers.py` (never summed into one number without saying
which is meant) and reported as separate rows in Table 5 — verified by
reading the actual computation, not assumed from the section's prose.

## Boundary cases and notation

`bounded_single_model_extrema`'s straddle detection
(`alpha_hi + beta_hi >= STRADDLE_CAP`) uses a cap (0.999) short of the
literal boundary 1.0, with the grid-fallback path's own docstring stating
directly why: the true supremum diverges as the cap tightens toward 1, so
a grid restricted to the feasible region already exceeds `[0,1]` by a wide
margin whenever this triggers, making the clip-to-`[0,1]` correct rather
than an underestimate — this reasoning is itself checked by
`fb_tb_compound_design_sensitivity.py`'s `saturation_diverges_check`, not
merely asserted in a comment. Notation is consistent throughout: $\alpha$
(false-credit), $\beta$ (false-miss), $A^\ast$ (true accuracy), $\hat a$ or
$a$ (observed/reported accuracy) — cross-checked against
Appendix A.7 (exact metric definitions) for drift; none found.

## What this audit did not re-do

Did not re-derive T-A/T-H/T-B/T-D/T-E/the correlated-error propositions
from first principles in this pass — each already has its own dedicated
derivation document and script (Appendix A.2's index) from earlier phases
of this project, each independently verified at the time it was written
(symbolic + numeric dual-check pattern, per this project's own standing
convention). This pass's contribution is the specific boundary/edge-case
and identified-vs-confidence-set verification above, which had not been
consolidated into one audit document before.

## Verdict

No theorem in this manuscript fails any of the six criteria. Full test
suite: 24/24 passing, including the 5 tests enumerated above as the
theoretical audit's own direct evidence.
