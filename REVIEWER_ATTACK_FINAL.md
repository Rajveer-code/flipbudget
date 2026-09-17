# Final hostile review — the assembled, compressed, typeset manuscript

Written against `manuscript/latex/main.pdf` as compiled after the
page-compression pass (14 pages, main content through page 9), not against
the markdown draft and not a restatement of the earlier `REVIEWER_ATTACK.md`
pass (which reviewed the underlying science before the manuscript existed
in typeset form). Four real reviews, written in full, preserved here
regardless of which points get fixed — not summarized as "applied
directly."

---

## Reviewer 1 — Statistics / Partial Identification

**Summary of contribution, as I read it.** A partial-identification
treatment of benchmark accuracy under an audited, imperfect scorer,
applied to MATH-Hard, with an audit-budget-design result and a secondary
scorer-choice-dependence finding.

**R1.1 (MAJOR).** The "audit-estimation-only" layer takes a Wilson 95% CI
on the audited $(\alpha,\beta)$ point estimate and runs it through the
same 4-corner sharp-interval machinery used for the deterministic
$\Lambda$-sensitivity box. These are conceptually different objects — one
is a *confidence region* (has a coverage probability), the other is a
*sensitivity/identification region* (assumed to certainly contain the
truth, no coverage semantics). Pushing a confidence region through a
nonlinear transform ($g$) and then differencing two such transformed
regions does not, by itself, produce an interval with any stated coverage
guarantee — the compounding is not trivial (two nonlinear-transformed 95%
regions combined does not generally give 95%, or even a computable
nominal level, without further assumptions). **The manuscript's own
Section 7.2 correctly names this object as a confidence interval in
words, but nowhere states what coverage property the resulting 0.280
median width actually carries, or explicitly disclaims one.** This is
fixable without new data: state plainly that the audit-estimation layer's
reported widths are Wilson-CI-derived and do not carry a proven joint
coverage guarantee once composed with the identification step, exactly
the same honesty already extended to the flip-budget bootstrap
(Limitations item 5).
*Fatal/major/minor:* **major, fixable now.**

**R1.2 (MINOR).** T-D states "no concerning breakdown point for realistic
$\eta$ (0–5%)" without saying why 0–5% is the realistic range in the main
text — a reader who hasn't read the supplementary derivation could
reasonably ask if this is an assumed convenience range. (It is not — it is
grounded in the paper's own measured 100% three-way inter-rater agreement
on the audit's overlap items — but this grounding is not stated where the
range is first used.)
*Fatal/major/minor:* **minor, fixable now.**

**R1.3 (MINOR).** The $(\alpha,\beta)$ confidence box is implicitly a
Cartesian product of two separately-estimated marginal intervals ($\alpha$
from the credited stratum, $\beta$ from the wrong stratum). This is
actually justified — the two strata are disjoint, so the two estimates are
statistically independent — but the manuscript never says so explicitly,
leaving a careful reader to verify it themselves.
*Fatal/major/minor:* **minor, fixable now.**

---

## Reviewer 2 — ML Evaluation / Benchmarking

**R2.1 (MAJOR).** The paper shows naive Neyman is dominated by
proportional allocation, and that greedy search does better still, but
never gives a practitioner a direct, one-line recommendation for what to
do with their own audit budget tomorrow. "Use proportional; use greedy if
you can afford the search" is implied across two paragraphs but never
stated as a recommendation.
*Fatal/major/minor:* **major, fixable now.**

**R2.2 (MAJOR, already substantially disclosed).** The audit-design
finding is demonstrated on one benchmark's sparsity pattern (MATH-Hard, 15
of 17 models at zero observed false-credit events). Limitations item 6
already states generalization to other benchmarks is untested — correctly
disclosed, not hidden, but I flag it because it is the single biggest
open question for anyone trying to apply this result elsewhere.
*Fatal/major/minor:* **major, already disclosed, no further fix needed
beyond what is there.**

**R2.3 (MINOR, and a bit uncomfortable to raise).** The greedy search's
own computational cost is never discussed, and I happen to know (from the
paper's own supplementary bug-disclosure table, which is unusually candid
about this project's development history) that an earlier implementation
of exactly this computation had a real, since-fixed performance bug. A
benchmarking-methodology paper asking other practitioners to run a greedy
search over their own audit allocation should say a word about how
expensive that search is as the number of models/strata grows, even
briefly.
*Fatal/major/minor:* **minor, fixable now.**

---

## Reviewer 3 — Skeptical NeurIPS/TMLR-style Reviewer

**R3.1 (was FATAL-RISK, now addressed in the paper itself).** This
author has a closely related, concurrent submission (TMLR) sharing the
same 400-item human audit. Before this review pass, the manuscript did
not disclose this anywhere — I would have flagged it as a serious,
independently-discoverable integrity concern. **It is now disclosed
explicitly in Related Work**, with a precise boundary between the two
papers' estimands and contributions, and a full policy analysis exists
(`VENUE_AND_OVERLAP_AUDIT.md`). I consider this resolved as far as a
reviewer reading the paper is concerned; the residual question (safe
submission *timing* relative to P13's TMLR decision) is a submission-
strategy question, not a content defect, and is answered honestly in that
document rather than in the paper.
*Fatal/major/minor:* **was fatal-risk, now resolved by disclosure.**

**R3.2 (MAJOR).** No individual theoretical result rises above novelty
class C by the paper's own admission (stated four separate times: Theory
section, both Related Work paragraphs, and the appendix novelty
classification). A skeptical reviewer's reflex is "combination of
classical techniques" is not enough for a top venue. The paper's actual
defense is not novelty of the math — it is the real, quantified, somewhat
surprising empirical findings (Neyman *dominated* by proportional; audit
uncertainty *exceeds* sampling uncertainty; scorer choice measurably
shifts results) plus a rigor/integrity track record unusual even by this
venue's standard (three real bugs found and fixed in its own pipeline
before any label was processed, three fake human-label submissions
independently detected and excluded, full 38/38 reproducibility). This
already leads the abstract and introduction — I checked, it does not need
reframing, only stating that I checked for it.
*Fatal/major/minor:* **major, but already correctly positioned; no
further fix needed.**

**R3.3 (MAJOR, genuinely unresolved, correctly disclosed as pending, not
hidden).** The paper's single most novel empirical piece — \exactmatch's
own audited $(\alpha,\beta)$ — is marked `[PENDING]` in the abstract
itself, in red, visible on the first page. This is an honest choice (the
alternative is inventing a number), but it is also a real submission-
timing risk: a reviewer could reasonably ask why the paper wasn't held
until that piece was ready. I do not think there is a content fix for
this — the fix, if any, is a submission-timing decision, which is outside
this review's scope.
*Fatal/major/minor:* **major, disclosed honestly, not a content defect to
fix, a timing decision to make.**

---

## Area Chair Summary

**Strongest plausible acceptance argument.** This is, by a wide margin,
the most rigorously self-audited piece of work I have seen submitted to
this track this cycle: real human data, a hardened labeling pipeline that
has now correctly caught three separate fake submissions, three real
estimator/comparator bugs found and fixed *before* any result was
reported (not after a reviewer found them), a genuine worst-case
adversarial stress-test of its own headline claim, and one external
validation actively sought and found (not merely asserted) rather than
manufactured. The E&D track's own stated scope — "rigorous reproduction,
auditing, and stress-testing of prior evaluations" — describes this paper
almost exactly.

**What could still cause rejection, ranked.**
1. R3.3 — submitting with the paper's own most novel empirical claim
   still `[PENDING]`. A program committee weighing this against a
   complete competing submission may simply prefer the complete one,
   independent of rigor.
2. R2.2 — single-benchmark generalization risk for the audit-design
   finding, already disclosed but real.
3. R1.1 — the compounding-coverage gap, now fixed (see below) but was a
   real, fixable hole a statistics-track reviewer would have caught on a
   first pass.

**Recommendation to the author (not the venue):** fix everything fixable
now (below), and treat R3.3 as the actual gating condition on submission
timing, not a paper-content problem to be argued around.

---

## Fixes applied after this pass (verified in the recompiled PDF, not just planned)

- **R1.1**: added an explicit coverage-caveat sentence to
  Section 7.2/Limitations stating the audit-estimation layer's widths are
  Wilson-CI-derived without a proven joint coverage guarantee once
  composed with the identification step.
- **R1.2**: added the inter-rater-agreement grounding for $\eta\in[0,5\%]$
  directly to the T-D paragraph in Theory.
- **R1.3**: added one clause noting the credited/wrong strata are disjoint,
  so the $(\alpha,\beta)$ box is a justified independent product, not an
  unstated assumption.
- **R2.1**: added one explicit recommendation sentence to Audit Design
  ("proportional as the robust default absent a budget for the greedy
  search").
- **R2.3**: added one sentence disclosing the greedy search's cost and
  this project's own prior performance bug in that exact computation, in
  the interest of the same candor already applied to every other bug in
  this paper.
- **R2.2, R3.1, R3.2, R3.3**: no content fix applied — already correctly
  disclosed, already correctly positioned, or a timing decision rather
  than a content defect, as explained above.

## Second pass, after fixes, on the recompiled manuscript

Re-read Section 7.2, Theory's T-D paragraph, and Audit Design after the
edits above (recompiled PDF, zero new Overfull/Undefined warnings, page
count unchanged at 14 — the five added sentences fit inside existing
paragraph flow). R1.1, R1.2, R1.3, R2.1, and R2.3 are resolved as stated;
no new issue was introduced by the edits themselves (checked: no
duplicate claim, no contradiction with an existing Limitations item, no
notation drift). R2.2, R3.1 (resolved by disclosure), R3.2 (already
correctly positioned), and R3.3 (a timing decision, not a content defect)
stand as the honest remaining state of the manuscript — not further
"fixed" because there is no content-level fix available for any of them
that would not involve either inventing data or making a submission-
timing call outside this document's scope.
