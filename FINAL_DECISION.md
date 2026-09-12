# Final decision (item 25)

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

**The corrected E-A dominance finding**: median 5.24× (pairwise) / 3.22×
(single-model), 89.7%/100% of cases dominant — not because the number is
large (it is an order of magnitude smaller than first reported) but because
it is now the most heavily fact-checked number in the project: found
overstated by its own project's later-established correct method, recomputed
from already-verified data, and the direction survived. A number that
shrinks 26× under its own project's scrutiny and still supports the claim
is stronger evidence than a number that was never checked.

## Strongest practical contribution

**The audit-design methodology** (`AUDIT_DESIGN_ANALYSIS.md` +
`AUDIT_DESIGN_STRESS_TEST.md`): required-n, Neyman allocation, and the
benchmark-vs-audit crossover are usable by anyone auditing any scorer on
any benchmark, independent of whether they adopt the SSM/Λ framework at
all. Stress-tested to hold across rare-error, common-error, balanced and
extremely imbalanced strata, and three-stratum designs — the part of this
project most likely to be *used*, not just cited.

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

Among what genuinely is blocked pending external access (not effort):
independent verification of `is_equiv` on a non-Windows environment (needs
WSL, not installed, an OS-level change I should not make autonomously), and
a fully independent third benchmark/model roster (needs a data source
beyond the already-authenticated open-llm-leaderboard details repos, which
contain no execution- or judge-scored tasks — confirmed directly by listing
every available task file).

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
2. **The correlated-error theory (`THEORY_EXTENSIONS.md` §1) has zero
   fitted real data.** It is real, verified-by-simulation theory answering
   a real reviewer objection, but "we prove the mechanism exists" is a
   weaker sentence than "we show it operates at rate X on real data" — the
   latter needs more scorer-wrong events than either audit round has
   produced.
3. **`is_equiv`'s behavior off this specific machine is unverified.** A
   one-line, high-consequence gap for a reproducibility reviewer, cheap to
   close once WSL or any Linux environment is available.
4. **No manuscript prose exists yet.** Every piece above is real,
   verified, and mapped (`MANUSCRIPT_ARCHITECTURE.md`) — but the actual
   writing, where repetition gets killed and the argument gets one
   continuous spine, has not started. That is expected at this stage, not
   a deficiency of the research — named so it isn't mistaken for one.
