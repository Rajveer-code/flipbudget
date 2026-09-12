# Core thesis reassessment, from first principles, post evidence-table correction

Re-derived after `EVIDENCE_TABLE.md`'s biggest finding: E-A's dominance
ratio was overstated by roughly an order of magnitude (134×→5.24× pairwise,
75×→3.22× single-model) due to a since-identified methodology artifact in
the *original* script. Question: does the corrected, more conservative
number change which of A/B/C/D the evidence supports?

## Re-run the masterplan's own test with the corrected numbers

**Not A (scorer-induced ranking sensitivity as the centerpiece).** Two
independent lines of evidence, both hold after correction:
1. `RECONCILIATION_FOUR_LAYERS.md`: scorer-only unresolved (15/136, 11.0%)
   barely exceeds the sampling baseline (12/136, 8.8%) — unaffected by the
   E-A correction, which concerns the *audit-only* layer, not scorer-only.
2. **Corrected E-A itself now argues against A more strongly, not less.**
   A dominance ratio of 5.24× driven by audit-estimation uncertainty (finite
   human-audit n) rather than scorer bias per se is direct evidence that
   *the measurement problem is about how much we've verified, not about the
   scorer being systematically wrong* — which is B's claim, not A's.

**Not C alone.** Unchanged reasoning from `AUDIT_DESIGN_ANALYSIS.md`: an
audit-design methodology motivated by nothing reads as solving an invented
problem. B's finding (real, now doubly confirmed — modeled in the
reconciliation, and independently in the corrected E-A dominance study) is
what makes C's six answered questions matter.

**B is, if anything, more secure after the correction, not less.** The
worry before this pass was that B's centerpiece claim rested partly on a
dominance number that might not survive scrutiny. It has now been
scrutinized, found to need correction, and the qualitative claim — audit-
estimation width typically exceeds sampling width — **survived the
correction intact**: still real, still the majority (89.7% pairwise, 100%
single-model) of cases, just smaller in magnitude. A claim that shrinks by
26× under a stricter methodology and still holds directionally is a more
credible claim than one that was never stress-tested at all.

## Verdict: **D confirmed, unchanged** — B (audit-estimation uncertainty,
now evidenced twice: modeled in the reconciliation, independently confirmed
in corrected E-A) **+ C (audit-design methodology, six answered questions)**.

## What would have changed the verdict, and didn't

- If corrected E-A had shown ratio < 1 in the majority of pairs, B's
  foundation would have weakened substantially and the project would need
  to reconsider whether the audit-estimation story is real at the claimed
  scale. It did not — 89.7%/100% dominance survived.
- If T-C's real audit (B4 in the evidence table) had found a nonzero
  scorer-wrong rate, that would push weight toward A (scorer bias is real
  and measurable) rather than B (it's mostly about audit thinness). It
  found 0/69 — consistent with B, not A.
- If IFEval's verifier-bug rate had explained the *majority* of its
  disagreement (rather than 16.8%), that would suggest scorer bias
  (A-shaped) is the bigger story on a second benchmark too. It explains a
  minority, leaving most of IFEval's disagreement an open question (C8 in
  the evidence table) rather than resolved evidence for A.

No formulation outside A/B/C/D was supported by re-reading the evidence —
the project is not, for instance, primarily a benchmark-generalization
paper (IFEval's human-audit layer failed, so generalization evidence is
partial) or primarily a mechanism paper (E-E's format-prediction angle is
underpowered at 5 events and was correctly retired).
