# Consolidated verdict — strongest defensible contribution

Updates `AUDIT_DESIGN_ANALYSIS.md`'s verdict (D, given mid-session) with
everything since: T-C's completed real human audit, IFEval's verifier-bug
discovery and reproducibility quantification, and two failed IFEval
human-audit rounds (paused by decision, not silently dropped). **Verdict
stands, and is now better supported than when first given — with one new,
honestly-reported open problem.**

## The verdict: D — audit-estimation uncertainty (B) + audit design (C)

**Current benchmark-comparison scoring has a hidden, underpowered
measurement layer, and this project provides a principled, verified
framework for sizing and fixing it.** Not A (scorer-induced ranking
sensitivity as the headline finding) — the reconciliation showed
scorer-only unresolved pairs (15/136, 11.0%) barely exceed the sampling
baseline (12/136, 8.8%); real, but too modest to centerpiece alone. Not C
alone — the audit-design methodology's whole motivation is B's finding; a
"how to audit efficiently" paper reads as solving an invented problem
without first showing the problem (current audits are underpowered) is real.

## What's new since D was first given, and why it strengthens rather than weakens the verdict

**T-C: the audit-estimation story is now confirmed with real, not just
modeled, human data.** 69 real audited trials, 0 scorer-wrong events
(`TC_REAL_ANALYSIS.md`) — underpowered on its own terms (P(0 events | true
rate ≈3%, n=69) ≈ 11%, consistent with the targeted rate, not evidence
against it), but folding these real trials into the pooled α/β estimate
(`TC_ALPHA_BETA_UPDATE.md`) produced a genuine, verified secondary finding:
**a small, targeted audit shifts identification conclusions for models it
never directly touched**, because empirical-Bayes pooling shares one anchor
across all models (confirmed directly on `tiiuae/falcon-40b` and
`01-ai/Yi-34B`, neither audited, both shifting by the anchor's own
proportion). This is exactly the kind of audit-design subtlety C's
framework is built to reason about — it is new evidence *for* the
B+C story, not a new, separate finding competing with it.

**IFEval: the framework generalizes to a second benchmark and finds a
second real issue.** Source-verified, causally-confirmed (seeded vs.
unseeded fresh-process replicates) verifier nondeterminism in 96/541 items
(17.7%, corrected from an initially-incomplete 33-item scan) —
`IFEVAL_REPRODUCIBILITY_CHECK.md`. Its effect on the numbers that matter
most is small: benchmark-score spread of 0.0004, maximum single-model rank
displacement of 2/27, the #1 model never changes across 15 replicates. It
explains 16.8% of real strict/loose disagreement (64/380, corrected from an
initial 8.2%) — meaningful, but leaving 83.2% genuinely unexplained by any
known mechanism. This is a second, independent confirmation that
scorer/verifier issues are real and quantifiable across benchmarks, using
the exact same audit-and-reconcile discipline as MATH-Hard — supporting
generality, not just a one-off MATH-Hard artifact.

**IFEval's human-audit layer: attempted properly, twice, and honestly
paused — a real, reportable limitation, not a hidden failure.** Two full
rounds of human labeling on the 454-item sample were checked directly
against the real per-instruction verifier before being trusted (not
assumed): round 1, 89.3% of "compliant" marks contradicted by a concrete,
deterministic constraint failure; round 2, after rewriting the labeling
instructions to lead with the exact prior failure and a per-constraint
mechanical checklist, 90.5% — no measurable improvement. Per your decision,
this angle is paused rather than pursued with a third attempt.

This is not neutral information — it is itself a small, honest,
methodologically interesting finding: **casual human labeling of
fine-grained, mechanically-checkable instruction-following is unreliable at
this volume and format**, which is a real-world instance of exactly the
"how much human audit, allocated how, actually buys you information" question
the C (audit-design) contribution is about. It belongs in the paper as a
limitation and a motivating example, not as a gap to paper over. The 83.2%
of IFEval disagreement that remains unexplained stays *genuinely* unexplained
— per your standing instruction, this is not assumed to be scorer error in
either direction; it is reported as unresolved.

## What the paper's centerpiece looks like, concretely

1. **The problem (B)**: on MATH-Hard, a 73.5% flip-rate headline
   (`TB_COMPOUND.md`) is shown, via a corrected four-layer reconciliation
   (`RECONCILIATION_FOUR_LAYERS.md`), to be driven mostly by finite
   audit-sample uncertainty (91/136 pairs unresolved under audit-only vs.
   15/136 under scorer-sensitivity-only) — not primarily by scorer bias
   itself. Reported transparently alongside the original number, not
   instead of it.
2. **The framework (T-A/T-B/T-H)**: the Scorer Sensitivity Model and its
   sharpness/boundary properties, [0,1]-bounded partial identification
   (`fb_reconcile_layers.py`'s `bounded_single_model_extrema`), giving a
   principled way to separate these uncertainty sources at all.
3. **The fix (C)**: a verified audit-design methodology answering six
   concrete questions with real numbers — required-n (median 415 for full
   resolution-parity with the scorer-only layer), a proven and fixable
   allocation inefficiency (current design's real allocation misses the
   Neyman-optimal split by a median gap of 0.482; correcting it cuts
   variance 77% for free), a shrinkage curve showing diminishing but real
   returns, a decisive audit-vs-benchmark-size crossover (16/16 models
   already past it — audit size, not benchmark size, binds), and a bound
   showing a full adaptive system wouldn't beat a correctly-computed static
   allocation.
4. **Generalization and honest limits (IFEval)**: the same discipline
   applied to a second, structurally different benchmark finds a second
   real, source-verified scorer issue with small but nonzero effect on
   benchmark conclusions — and an honest report that the obvious next step
   (human-validate the rest) did not succeed on the first two attempts,
   itself informative about where this whole research program's practical
   limits currently sit.

## What remains open, stated plainly

- T-C's core scorer-error-correlation question is still underpowered (0
  events across all real audits to date) — not resolved, not claimed to be.
- IFEval's 83.2% unexplained disagreement remains unexplained — no claim
  either way about whether it reflects genuine scorer error.
- No working human-audit protocol for fine-grained IFEval-style
  instruction-following exists yet in this project; if pursued again later,
  it needs a fundamentally different approach (narrower task scope, or
  tooling that surfaces the specific constraint per row), not a third
  attempt at a better-worded README on the same format.
