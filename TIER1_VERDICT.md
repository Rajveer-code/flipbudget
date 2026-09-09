# Tier 1 verdict — 2026-09-09

Run in the specified order: E-A → T-C → E-E. Real data throughout. Three real bugs
caught and fixed before any number was reported (an indexing bug and a near-singular
denominator blowup in E-A; a CI-blind verdict threshold in E-E). Full derivation in the
commit history — `ea_dominance_study.py`, `tc_correlated_error.py`,
`ee_format_association.py`, and their three result JSONs.

## The three results

**E-A (dominance) — STRONG, POSITIVE, ROBUST.**
Identification width (from real Wilson CIs on audit-estimated α, β) exceeds sampling
width (the field's current textbook CI, which assumes α=β=0) in **100% of scored models
and 100% of scored pairs.** Full-sample median ratio 74.99× (single-model) / 134.32×
(pairwise). Under the strictest reasonable filter — both models with ≥5 audited items on
both the credited and wrong strata, a conventional minimum-cell-count rule, not a
threshold chosen to flatter the result — the ratio drops but survives: **6.14×
(single-model) / 22.26× (pairwise) median, still 100% dominant.**

**T-C (correlated error) — INCONCLUSIVE.**
The direct test (exact same problem shared across ≥2 models, 46 of 350 items) found only
1 of 41 paired observations with any wrongness event at all — too few to estimate
correlation in either direction. A higher-power complementary test (wrongness rate
across 28 subject×length cells, pooling all ~350 items) found no significant variation
(χ²=18.63, df=27, p=0.88). Both point to the same cause: scorer wrongness is rare on
this benchmark (β≈0 for nearly every model, per E4). **This neither confirms nor refutes
whether correlated error makes the independent-error bound conservative.**

**E-E (format association) — UNDERPOWERED, NOT CONFIRMED.**
A cross-validated logistic regression predicting wrongness from 9 response-format
features gave AUC=0.830 — a number that would look like a real finding if reported
alone. Its own bootstrap 95% CI is **[0.492, 0.991]** — the lower bound sits at chance.
Only 5 of 350 usable records have a wrongness event. **The point estimate cannot be
trusted in either direction; this is not evidence of a format mechanism.**

## Why T-C and E-E failed the same way

Both hit the identical wall: MATH-Hard's current 400-item audit has too few
scorer-wrongness *events* (as opposed to too few *items*) to power either test. E4
already established β_pooled ≈ 0 almost everywhere on this roster; that same fact is
what starves T-C and E-E of the events they need. This is not three independent
failures — it is one structural limitation of the current audit's event density,
surfacing in two different experiments.

**This also qualifies E-A's own result, honestly.** Part of why identification width is
so large is that several models' α, β point estimates come from very small counts
(including zero successes), which produces genuinely wide Wilson intervals. E-A's
dominance finding is real and survives the strict n≥5 filter — but it is currently a
statement about *how little we know*, not yet a fully characterized statement about
*what the true error process looks like*. Those are related but not identical claims,
and the paper must not blur them.

## Verdict: **B — evidence supports a narrower version**

Not A. Two of three Tier 1 experiments returned "inconclusive," not "confirmed." Running
E-B through E-I, the full theory program (T-A/T-B/T-D–H), or the large human audit on
the strength of E-A alone would be building on a mechanism that is asserted, not shown.

Not C. Nothing here contradicts the central hypothesis. None of the three hard kill
criteria fired: E-A's ratio is not <1 anywhere (it dominates everywhere, even
restricted); T-C did not show near-total cancellation (it showed *no data either way*);
E-H (execution control) has not even run yet. Declaring the hypothesis unsupported would
manufacture a negative finding from ambiguous data — the same error as manufacturing a
positive one.

**What "narrower" means concretely:**

1. **Keep and lead with E-A.** "Reported benchmark uncertainty omits a component that
   dominates the reported one" is real, robust to the strictest filter applied, and
   defensible right now. This is publishable as its own honest, bounded finding.
2. **Do not yet claim a mechanism.** No claim that differential error is predictable
   from format (E-E), correlated across models (T-C either direction), or that the
   independent-error bound is conservative or anti-conservative. State this as an open
   question, explicitly, not as a gap papered over.
3. **The concrete next step is not "more Tier 2 theory."** It is a **targeted audit
   expansion** — not more items generally, but items *stratified to be wrongness-event-
   rich* (oversample low-accuracy models and models with any observed α > 0, rather than
   proportional-to-population sampling) — sized to actually power T-C and E-E before
   either is attempted again. That is real, bounded, and can resolve the open question
   directly rather than theorizing around it.
4. **T-A/T-B (the sensitivity-analysis reframe and the design-sensitivity theorem) are
   unaffected by this verdict** — they are pure theory, not contingent on T-C/E-E's
   empirical outcome, and can proceed independently if wanted. **T-C's own theoretical
   derivation, T-D, T-E, and the rest of the empirical program (E-B onward) should wait**
   for the audit expansion in point 3, since several of them assume a resolved
   correlation structure or a working format-predictor that Tier 1 did not deliver.

## What I will not do without your say-so

Not expanding scope past this. No E-B, no T-A/T-B execution, no audit expansion planning
beyond naming it above, until you've seen this verdict.
