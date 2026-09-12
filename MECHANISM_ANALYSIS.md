# Mechanism analysis (item 10) + placement decisions (items 20-21)

## What causes scorer error — honest state, not inflated

**MATH-Hard.** Two real, identified mechanisms, both from direct code
inspection and adversarial testing, neither from a fitted statistical
model (which remains underpowered):
1. **Reordered interval/set-union notation** is not recognized as
   equivalent by the symbolic comparator (`ADVERSARIAL_SUITE.md`) — a
   structural limitation of a scalar-algebra-oriented `sympy` pipeline
   applied to set-valued answers.
2. **`\dfrac` vs `\frac`** — already known from Phase 1's E2 finding,
   independently reconfirmed here (was one of the cases resolved once the
   `SIGALRM` bug, `MATH_COMPARATOR_BUG.md`, was fixed and re-tested).

**What the data does NOT support**: a general, fitted "format predicts
wrongness" model. `EE_FEATURE_STABILITY_CHECK.md`'s logistic regression
(4 stable features: `n_newlines`, `ends_with_period`, `has_therefore`,
`n_frac`) is real but built on only 5-6 positive events (corrected from 5
per `MATH_COMPARATOR_BUG.md`; still far below the ~40 needed for a
trustworthy fit). **Do not claim verbosity, response length, or reasoning
traces predict scorer error on this data** — that claim was never powered
and was correctly retired (`EE_REASSESSMENT.md`).

**IFEval.** Two real, causally-confirmed mechanisms (`IFEVAL_REPRODUCIBILITY
_CHECK.md`): unseeded `langdetect` (affects any of 3 checker types that call
it — `language:response_language`, `change_case:english_capital`,
`change_case:english_lowercase`) and `keywords:letter_frequency`'s
random-letter fallback when its `letter` kwarg is invalid. Both are
**implementation-mechanism findings** (a specific code path), not
response-feature findings — a different, more mechanistic kind of "cause"
than MATH-Hard's format-association angle, and arguably a stronger one
(source-code-verified and reproducibility-quantified, not a small-n fit).

**Not testable with current data**: verbosity, answer placement, model
family, or item-difficulty effects on scorer error, for either benchmark —
none of these were fit with adequate power. Do not claim them.

## Item 20 — IFEval's placement in the paper

**Decision: supporting case study, not an appendix afterthought and not
"nowhere."** Justification, from evidence not preference:
- It independently confirms the audit-design/measurement-uncertainty thesis
  on a structurally different benchmark and scoring paradigm
  (`generate_until` + programmatic multi-instruction verification vs.
  MATH-Hard's single-answer extraction) — this is real generalization
  evidence for verdict D, not decoration.
- Its own contribution (the verifier-nondeterminism finding, causally
  confirmed) stands alone as a real, citable result independent of any
  human audit.
- Its human-audit layer failed twice and is honestly reported as a
  limitation, not hidden — this belongs in the same section as a
  cautionary, informative result, not quietly dropped to avoid a mixed
  narrative. A paper that shows generalization *and* is honest about where
  the follow-up audit didn't work is stronger than one that only shows the
  clean parts.

**Not primary**: IFEval doesn't carry a resolved human-validated
scorer-error rate the way T-C does, so it cannot be a co-equal pillar with
MATH-Hard — it is a second, real data point supporting generality, correctly
scoped below the main result.

## Item 21 — what T-C establishes, and what it critically does not

**Establishes**: (a) 100% cross-labeler agreement across 3 independent
raters on a real, previously-unaudited sample (a genuine reliability
result); (b) the empirical-Bayes anchor-propagation effect
(`TC_ALPHA_BETA_UPDATE.md`) — a real, general methodological finding about
partial pooling, independent of the specific error rate; (c) together with
the original 400-item audit (corrected to 6 events, `MATH_COMPARATOR_BUG
.md`), a combined real-event count still low enough to keep the central
correlation/mechanism question open rather than resolved.

**Does NOT establish, and must not be implied to**: (a) that scorer error
is rare on MATH-Hard in general — 0/69 new events is consistent with the
~3-7% rate the audit was targeted at (P≈11-13% by chance), not evidence the
true rate is near zero; (b) anything about correlated error across models
(0 events means no paired-wrongness data exists at all, in either
direction) — `THEORY_EXTENSIONS.md` §1's cancellation result is a
theoretical mechanism, not fit to T-C's data because there is no event data
to fit it to; (c) that β (false-miss) coverage improved — **T-C's 69 new
trials were 100% credited-stratum by design; zero new wrong-stratum trials
were added, so β coverage is exactly where the original 400-item audit left
it (188 items), not improved by this round at all.** This must be stated
explicitly in any manuscript text describing T-C's contribution — it is
easy to imply "we added 69 audited items" without noting they added nothing
to the specific quantity (β) that most needs more data.
