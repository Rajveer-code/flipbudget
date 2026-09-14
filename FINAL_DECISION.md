# Final decision (item 25, updated by the final validation phase — item 18)

**Updated verdict, after a full second round of self-audit (18-item final
validation phase, this session): B stands — strong, ready for the
Evaluations & Datasets track, on firmer footing than the previous pass, not
yet ICML/JMLR-standalone.** Nothing here overturns the prior verdict; this
phase closed the two biggest remaining honesty gaps (a canonical,
fully-cascaded headline number; the empty-set root cause) and found one
more genuine, reportable limitation (naive Neyman allocation is dominated
by proportional on this real sparse data) that makes the audit-design
contribution more credible, not less, for having been caught and fixed
before submission rather than by a reviewer after. Full detail:
`EVIDENCE_TABLE.md`, `CANONICAL_EA_RESULT.md`, `RECONCILIATION_EMPTY_SET_ROOTCAUSE.md`,
`AUDIT_DESIGN_OPTIMIZATION.md`, `TC_CORRELATED_ERROR_BOUND.md`,
`NEGATIVE_CONTROLS.md`, `MATH_COMPARATOR_LINUX_VALIDATION.md`,
`NOVELTY_AUDIT.md`, `CLAIM_AUDIT.md`, `REVIEWER_ATTACK.md`.

**What changed this phase, concretely:**
1. The 6.10×/100% figure is now traced to a saved, re-runnable script with
   every exclusion stage counted (378 candidate → 136 scored → 120 valid),
   not an untracked calculation that happened to match.
2. The 70/136 scorer-only empty-set rate — an open question last time — is
   fully closed: 5 specific low-accuracy models, 100% driven by the pooled
   anchor exceeding their own accuracy, 0% by the Λ-band width.
3. `is_equiv`'s fix is verified on real Linux CI, not assumed equivalent —
   and building that CI surfaced a second real bug (hardcoded absolute
   paths in the T-C loader), fixed, re-verified identical output.
4. T-C's correlated-error question now has an honest bound (not a point
   estimate): 0–22.7% of the 66 valid scorer-only pairs could flip
   depending on an unmeasurable correlation, with an exact required-n
   (~458) to close it.
5. Audit-design's classical Neyman recommendation is now qualified with a
   real, quantified failure mode on this project's own sparse data (74%
   stuck vs. proportional's 22% at the same budget) and a concrete fix
   (pooled estimates or greedy search) — a more honest, more useful
   practical contribution than an untested "Neyman is optimal" claim.
6. Negative controls confirm the method is falsifiable: three of five
   constructed scenarios correctly report "stable," including one sized to
   this project's own required-n target.
7. A close 2026 neighbor (Chen, Rambachan & Tamer, "Partial Identification
   from LLM Prompts") was found, read carefully, and distinguished — a
   must-cite, not a collision, and the A/B/C/D classification instructed
   by item 13 is now applied to every result in the project (nothing above
   B individually; novelty is in the combination).
8. Full 21-step reproducibility pipeline passes clean end-to-end for the
   first time (previously blocked on a timeout using pre-fix code).

**What did not change:** verdict D/B's qualitative content, the strongest
theorem (T-B), and the weakest link (T-C's correlation question, IFEval's
failed human-audit layer) — both still open, now with sharper, honestly
bounded statements instead of silence.

---

# Original decision (superseded in framing, not in substance, by the update above)

Evidence-based, drawing on `EVIDENCE_TABLE.md`, `THEORY_EXTENSIONS.md`,
`AUDIT_DESIGN_STRESS_TEST.md`, `MATH_COMPARATOR_BUG.md`,
`MANUSCRIPT_ARCHITECTURE.md`, `REVIEWER_ATTACK.md`, `NOVELTY_AUDIT.md`.

## Strongest scientific contribution

**Verdict D**: current benchmark-comparison methodology has a hidden,
under-reported measurement layer (audit-estimation uncertainty, not just
scorer bias) that is often larger than the sampling uncertainty already
reported, and this project supplies a verified, principled framework for
both diagnosing it (SSM, four-layer reconciliation) and fixing it (Neyman
audit-design, stress-tested across 6 out-of-configuration scenarios). Not
A alone (scorer-only effect is modest, 11.0% vs. 8.8% sampling baseline) and
not C alone (a design methodology needs B's finding to motivate it) — the
combination is what the evidence supports, unchanged in kind but
strengthened in credibility by this phase (the headline number was checked,
found overstated, corrected, and the qualitative claim survived).

## Strongest theorem

**T-B, the design-sensitivity impossibility result** (Λ̃, closed form,
`TB_DESIGN_SENSITIVITY.md`/`TB_COMPOUND.md`): short, quotable, and directly
answers the field's standard reflex to any uncertainty finding ("just
collect more benchmark items") with a proof that some comparisons are
unidentifiable at *any* benchmark size for a fixed audit. Stronger as a
standalone citable object than T-H's sharpness proof (necessary but a
corollary-generating tool, not a headline result) or the new ranking-
preservation theorem (`THEORY_EXTENSIONS.md` §2 — real, but explicitly a
restatement of T-H, not new content).

## Strongest empirical result

**The corrected E-A dominance finding**: median 6.10× (pairwise, n=120 of
136 well-defined pairs) / 3.22× (single-model), **100% dominant** — not
because the number is large (it is an order of magnitude smaller than
first reported) but because it is now the most heavily fact-checked number
in the project: found overstated ~26× by the original corner-drop method,
re-derived under a `[0,1]`-bounded fix, then found that fix itself
mishandled 16 of 136 pairs (silently inverting an empty identified set into
a nonsensical negative width) — caught auditing the published package
against its own research methodology (item 18) — and re-derived a third
time. Each pass made the number more conservative and more correct, and
the direction (audit-estimation width exceeds sampling width) survived all
three. A number that gets re-derived twice under its own project's
increasing scrutiny and comes out cleaner each time is stronger evidence
than one that was never checked at all.

## Strongest practical contribution

**The audit-design methodology** (`AUDIT_DESIGN_ANALYSIS.md` +
`AUDIT_DESIGN_STRESS_TEST.md`): required-n, Neyman allocation, and the
benchmark-vs-audit crossover are usable by anyone auditing any scorer on
any benchmark, independent of whether they adopt the SSM/Λ framework at
all. Stress-tested to hold across rare-error, common-error, balanced and
extremely imbalanced strata, and three-stratum designs — the part of this
project most likely to be *used*, not just cited.

## A new open question, found in this pass, not yet closed

Auditing the package (item 18) surfaced that the scorer-identification-only
layer's Λ=2 band is empty (inconsistent with observed accuracy) for **51.5%
of the 136 real pairs (70/136)** — more than double the audit-only layer's
16/136. Not yet root-caused beyond a plausible hypothesis (many low-accuracy
models on this roster have a pooled alpha estimate that, even shrunk, still
exceeds their own accuracy under a Λ=2 band). This does not change verdict
B (still robustly supported on its own, smaller, valid subset), but it is a
real, open methodological question about how informative the
scorer-sensitivity layer even is for this roster's weaker models — named
here rather than left implicit in a percentage that quietly excludes over
half the data.

## Weakest remaining link

**IFEval's human-audit layer failed twice (89.3%, then 90.5% contradiction
against the real per-instruction verifier) and 83.2% of its real
disagreement remains genuinely unexplained.** This means the project's
*second* empirical pillar is incomplete in a way MATH-Hard's is not — IFEval
supplies real generalization evidence for the *mechanism-discovery*
discipline (a second, real, causally-confirmed verifier bug) but not a
second *resolved* audit. Combined with T-C's own correlation question
remaining unpowered after two audit rounds (companion project: 1/41; this
session: 0/69), **the project currently has exactly one fully-closed
empirical result (E-A/reconciliation) and two open threads presented
honestly as open, not as smaller versions of closed ones.**

## Highest-value remaining experiment

Not blocked, not yet done: **a targeted, larger human audit of MATH-Hard's
credited stratum specifically**, sized to `AUDIT_DESIGN_ANALYSIS.md` Q1's
own number (median 415 for audit-only/scorer-only parity) — this is the
single audit that would most directly close the weakest link (T-C's
correlation question) using the project's own derived, defensible sample-
size target rather than a guess. **This requires new human labeling and is
therefore the one action item for you, not something to execute
autonomously.**

**Update: `is_equiv` non-Windows verification is no longer blocked** —
resolved via GitHub Actions on `ubuntu-latest`
(`MATH_COMPARATOR_LINUX_VALIDATION.md`), not WSL, which remains
unavailable. **The independent-third-benchmark question is also no longer
a dead end**: HELM and AlpacaEval are real, licensed, response-level
candidates (`INDEPENDENT_BENCHMARK_SEARCH.md`) — what remains blocked is
narrower: executing a full replication needs a new human-audit round on
whichever source is chosen, the same kind of action item as the T-C
expansion above, not a data-access problem anymore.

## Is this genuinely strong enough for NeurIPS 2027?

**For the Evaluations & Datasets track: yes, with the honest framing
already established, not the framing from four days ago.** The paper this
evidence supports is: a verified methodological import (sensitivity
analysis for scorer error, explicitly not claimed as new mathematics) with
one fully-closed, heavily-scrutinized empirical result (corrected E-A +
reconciliation), a genuinely useful, stress-tested practical tool
(audit-design), a real second-benchmark finding (IFEval's verifier bug),
and an honestly-reported methods-integrity narrative (three real errors
caught and fixed by this project's own adversarial tooling during this
phase alone). That is a real, defensible, accepted-shape paper for that
venue. **Not yet strong enough for ICML/JMLR as a self-standing theory
paper** — masterplan's own Tier 3/4 items (T-D/T-E's full latent-class
treatment, T-F/T-G, a genuinely independent replication) are correctly
scoped as extensions, not this paper's spine.

## What would still prevent it from being exceptional

1. **A second fully-closed empirical result.** Right now there is one. A
   larger, properly-powered T-C audit (the highest-value experiment above)
   or a genuinely independent third benchmark would give the paper two
   independent legs instead of one plus two honest partial ones.
2. **The correlated-error theory (`THEORY_EXTENSIONS.md` §1) still has no
   point estimate of the actual correlation.** Updated this phase
   (`TC_CORRELATED_ERROR_BOUND.md`): the real 0/51 audit now yields an
   honest bound (0–22.7% of the 66 valid scorer-only pairs could flip
   depending on an unmeasurable ρ) and an exact required-n (~458) to close
   it — real progress, but "we prove the mechanism exists and bound its
   maximum possible effect" is still a weaker sentence than "we show it
   operates at rate X," which needs those ~458 rows.
3. ~~`is_equiv`'s behavior off this specific machine is unverified.~~
   **Resolved this phase** — see the update above.
4. **No manuscript prose exists yet.** Every piece above is real,
   verified, and mapped (`MANUSCRIPT_ARCHITECTURE.md`) — but the actual
   writing, where repetition gets killed and the argument gets one
   continuous spine, has not started. That is expected at this stage, not
   a deficiency of the research — named so it isn't mistaken for one.
