# Five hostile reviewers (item 23)

Real rejection arguments, not softened. Then what would actually defeat
each, and whether that fix has been applied.

## 1. Statistics / econometrics reviewer

**Attack**: "Your 'Scorer Sensitivity Model' is a relabeled marginal
sensitivity model with nothing new. Your correlated-error section
(`THEORY_EXTENSIONS.md` §1) proves a textbook variance identity
(`Var(X-Y)=Var(X)+Var(Y)-2Cov`) and calls it a proposition. Your
imperfect-reference section admits a latent-class model isn't identified at
your sample size and substitutes an ad hoc sensitivity curve you invented on
the spot. This is applied statistics with theorem numbering, not new
statistics."

**What defeats it**: Nothing does, entirely — the paper must NOT claim new
mathematics for the MSM adaptation (`MASTERPLAN_PHASE2_FLAGSHIP.md` §2.3
already commits to "importing, extending, not inventing," correctly). What
partially defeats it: the paper's actual contribution is the **specific
adaptation and empirical instantiation** — sharp bounds under Λ for a
measurement-error (not confounding) structure, applied to a real, verified
scorer-error dataset with a genuine, checked reconciliation. That is a
legitimate applied-methods contribution in the diagnostic-testing/
measurement-error tradition, comparable to how a new marginal-sensitivity-
model application paper gets accepted in epidemiology — but the paper must
say exactly this, in exactly those terms, and never claim T-A/T-H as novel
mathematics. **Status: the framing is already correct in the masterplan;
risk is in execution — a drafted paper must not drift into overclaiming
during writing.**

## 2. ML evaluation reviewer

**Attack**: "You found a real bug in the standard MATH comparator caused
by SIGALRM not existing on Windows. That's a Windows bug report, not a
methodological finding — anyone running this on Linux (which is how nearly
every real evaluation pipeline runs) never sees it. You are dressing up an
environment-specific defect as insight."

**What defeats it, partially**: correct that the SIGALRM manifestation is
Windows-specific — this must be stated plainly, not implied to be universal
(`MATH_COMPARATOR_BUG.md` already does this). What survives the attack: (a)
the underlying `try/except: return False` pattern that SWALLOWED this bug
silently is not Windows-specific — any transient failure in `parse_latex`
or `sympy.simplify` (a real timeout on a genuinely hard expression, a
memory issue, an unexpected exception) degrades to the same silent
"treat as non-equivalent" behavior on ANY platform, and this project's own
adversarial suite is the only place that ever checked; (b) the 2 remaining
comparator limitations (interval/set reordering, unit-word stripping) are
platform-independent and real. **Status: not yet verified whether the
non-Windows code path (real `signal.alarm`) has its OWN failure modes
(e.g., does the 1-second timeout silently misclassify genuinely-hard-to-
simplify-but-equivalent expressions as non-equivalent on Linux too?) — a
real, not-yet-closed follow-up, named in `MANUSCRIPT_ARCHITECTURE.md`.**

## 3. Benchmark researcher

**Attack**: "Your entire empirical case rests on one benchmark (MATH-Hard)
with a real audit, plus IFEval where your human-audit layer failed twice
and you're left reporting a verifier bug with no human validation of what
it actually means for correctness. You call this 'generalization.' It
isn't — you have one working case study and one broken one."

**What defeats it**: nothing fully does — this is the single most
legitimate attack available against the current evidence, and
`CONSOLIDATED_VERDICT.md` and `MANUSCRIPT_ARCHITECTURE.md` already concede
it rather than dress it up. Partial defense: IFEval's verifier-bug finding
is real and independently useful (a documented, source-verified,
causally-confirmed bug in a standard harness) regardless of the failed
human-audit layer — it is legitimate evidence that the AUDIT-MECHANISM
discipline (source-code verification, seeded-vs-unseeded replication)
generalizes even when the HUMAN-LABEL layer does not. The paper should
frame this precisely: **the methodology generalizes; a fully resolved
second empirical pillar does not yet exist.** Do not claim more.
**Highest-value remaining fix**: a genuinely independent third
benchmark/roster (blocked, needs new data access — named in
`MANUSCRIPT_ARCHITECTURE.md`).

## 4. Skeptical NeurIPS reviewer (evaluations & datasets track)

**Attack**: "Your headline dominance number was wrong by an order of
magnitude until this week, discovered because you finally re-ran your own
script under your own corrected methodology. Your second human-audit round
made the label quality WORSE (89.3%→90.5%), not better, after you rewrote
the instructions. Your comparator has been silently broken for possibly the
entire project. How many other silent errors are still in this repo that
you haven't found because nothing forced you to re-check them?"

**What defeats it**: this cannot be argued away — the honest answer is
"we don't know, and that is exactly why `EVIDENCE_TABLE.md` and this
flagship-strengthening pass exist." The actual defense is procedural, not
rhetorical: **every number in this repo now has a script, a provenance
entry (`PROVENANCE_MANIFEST.json`), and — critically — this session
demonstrably found and corrected 3 independent real errors (E-A's
magnitude, is_equiv's Windows bug, IFEval's mechanism undercounting) by
building adversarial/verification tooling specifically because
first-pass numbers are not trusted by default in this project's own stated
discipline.** A reviewer who values process over a claim of zero remaining
bugs should find this more credible, not less — but the paper must show
this discipline explicitly (a methods-integrity subsection), not just
apply it silently. **Not yet written as a manuscript section — flagged.**

## 5. Reproducibility reviewer

**Attack**: "You have 45+ scripts and 40+ result files with ad hoc
dependencies between them, at least one result file (`ea_dominance_
corrected.json`) that was never produced by a standalone, re-runnable
script, human-labeled data mixed with programmatic results with no single
command to regenerate everything, and you've admitted you haven't checked
whether your own bug exists on the OS most people will actually run this
on."

**What defeats it, partially**: `PROVENANCE_MANIFEST.json` (item 17) now
maps every result to its script or an honest ad hoc note. What does NOT yet
defeat it: **there is no single end-to-end "reproduce everything" entry
point** (item 16) — this is a real, concrete, currently-open gap, not yet
built in this pass (see status report). The two ad hoc-derived corrected
E-A files should be converted into small standalone scripts before
submission, not left as manifest footnotes — a cheap, concrete fix not yet
done.

## Highest-value fixes selected from the above (not everything — the ones that change a reviewer's verdict, not just annoy them less)

1. **Verify `is_equiv`'s non-Windows (real SIGALRM) code path independently**
   — currently assumed correct, never checked. (Reviewer 2's strongest point.)
2. **A genuinely independent third benchmark/model roster** — the single
   biggest lever on Reviewer 3's attack, currently blocked on data access,
   not effort.
3. **A one-command reproducibility entry point** — cheap relative to its
   value against Reviewer 5, not yet built.
4. **A "methods integrity" subsection in the eventual paper**, narrating
   the three real errors found and fixed this session as evidence of
   process rather than something to bury — directly answers Reviewer 4,
   costs nothing but honesty already established in this repo.

Lower-value, not pursued further here: re-litigating T-A/T-H's novelty
framing (Reviewer 1) — the masterplan's existing language is already the
correct, defensible position; further hedging would read as insecure, not
rigorous.
