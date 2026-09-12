# Adversarial / worst-case scorer suite (items 13-14)

Script: `scripts/fb_adversarial_suite.py`. Result:
`results/flipbudget/adversarial_suite.json`. Constructed cases with known
ground truth (built by hand, so correctness isn't in question), run through
the real scorers already used throughout this project. Purpose: validate
the theory's assumptions about scorer behavior, not build a new benchmark.

## MATH-Hard comparator: found a real, serious, now-fixed bug

The headline result of this exercise. 8 of 14 constructed cases initially
disagreed with the expected verdict. Investigated rather than shrugged off
— full account in `MATH_COMPARATOR_BUG.md`:

- **6 of 8 were one root cause**: `is_equiv`'s internal timeout depends on
  `signal.SIGALRM`, which does not exist on Windows, silently making
  `is_equiv` return `False` unconditionally. Confirmed, root-caused, fixed
  (`scripts/fb_math_comparator_fixed.py`). **Checked directly against every
  real dataset in this project**: T-C's own 69-row audit is unaffected (0
  rows change); the original 400-item companion audit had exactly 1 row
  affected (a real, previously-missed equivalence, `\frac{411}{333}` =
  `\frac{137}{111}` — both reduce by 3). Total true scorer-wrong events on
  that audit: 6, not 5 — flagged, not silently propagated into
  `EE_FEATURE_STABILITY_CHECK.md`'s AUC without re-running that fit.
- **2 of 8 are genuine, separate findings, unaffected by the bug fix**:
  reordered interval/set-union notation is not recognized as equivalent (a
  real structural limitation of the scalar-algebra-oriented symbolic
  approach); a bare numeral matches the same numeral with a unit word
  appended (`"9"` = `"9 meters"`) — traced to a deliberate
  `REMOVED_EXPRESSIONS` unit-stripping list in the vendor code, almost
  certainly intentional given MATH's unit-free gold-answer convention, not
  a bug — this suite's own test expectation was likely wrong on that one
  case, not the comparator.

## IFEval verifier: no genuine bug found in this pass

12 constructed cases across 6 checker types (`punctuation:no_comma`,
`keywords:letter_frequency`, `keywords:existence`,
`detectable_format:json_format`, `startend:end_checker`,
`change_case:capital_word_frequency`). 1 apparent mismatch
(`letter_frequency_valid_letter_just_under_threshold`) traced to **my own
test-construction error**, not a checker bug: the response `"banana has two
a letters"` actually contains 4 occurrences of `'a'` (3 in "banana" alone
+1 standalone), not fewer than the 3-occurrence threshold as the case name
assumed — miscounted when writing the test. Verifier's real behavior
(strict=True) was correct; the test's expected value was wrong. Corrected
understanding recorded here rather than left as an open "bug candidate."

**Net result: 11/12 IFEval cases confirm correct behavior once the one
test-authoring error is accounted for — no new IFEval verifier bugs found
by this suite** (distinct from the already-known, already-fixed
`keywords:letter_frequency`-invalid-letter and unseeded-`langdetect` issues
in `IFEVAL_REPRODUCIBILITY_CHECK.md`, which this suite did not re-target).

## What this validates about the theory

The MATH-Hard finding is direct evidence *for* this project's central
mechanism claim: real scorer error exists and is concentrated in specific,
identifiable formatting/notation classes (here: set/interval notation) —
exactly the kind of thing T-C's format-association work (`EE_FEATURE_
STABILITY_CHECK.md`) was underpowered to confirm statistically. It is not,
by itself, proof that this mechanism drives a large fraction of real-world
error (T-C's real audit still found 0/69 wrongness events on MATH-Hard's
current roster) — it demonstrates the mechanism *exists and is triggerable*,
which is what an adversarial/worst-case suite is for, not what an
average-case audit measures.
