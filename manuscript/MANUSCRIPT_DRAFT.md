# Scorer-Induced Partial Identification of Benchmark Comparisons: An Audit-Design Approach

*Full draft, written directly (not an outline), grounded only in established results (analyses A and B; item 6 of `METHODOLOGICAL_AUDIT.md`). Every place a result depends on the pending 458-row human audit is marked `[PENDING — human audit]` explicitly, with the exact quantity named — never filled with an invented number. Supersedes `manuscript/01_introduction.md` (content carried forward, extended).*

---

## Abstract

Benchmark leaderboards report model accuracy as if it were an observed quantity. It is the output of an automated verifier applied to free-text generations, and that verifier can disagree with the correctness a human reader would assign. We formalize this as a partial-identification problem: given a benchmark's observed accuracy and an *audited* estimate of the verifier's false-credit and false-miss rates, we derive the sharp set of true accuracy values consistent with the data, adapting classical misclassification-bounds machinery (Horowitz & Manski, 1995) to benchmark comparison. On MATH-Hard, using a real 69-item human audit of the standard `\boxed{}`-extraction comparator, we show that **audit-estimation uncertainty — how little the verifier's own error rate has been pinned down — exceeds sampling uncertainty for the majority of model comparisons that remain identifiable at all** (median identification-to-sampling width ratio 6.10×, 100% dominant among 120 well-defined pairwise comparisons out of 136 candidates among 17 qualifying models). We formalize the resulting audit-budget allocation problem, prove the classical (Neyman, 1934) solution, and show empirically that its naive plug-in form is *dominated by uniform allocation* on this project's own sparse real audit data — a documented failure mode with a tested correction. A secondary finding: MATH-Hard's evaluation harness computes accuracy via two live, independently-implemented extraction procedures that disagree on 3.63% of real responses (95% CI [3.39%, 3.88%], n=22,508); we show this scorer-choice dependence does not overturn the audit-estimation-dominance finding, including under an adversarial worst-case bound, but establishes it as a distinct, measurable source of benchmark uncertainty. `[PENDING — human audit]`: the verifier's *other* live scorer (`exact_match`, via `math_verify`) has not itself been human-audited; its own α/β, and the fully self-consistent identification result built on them, await a preregistered 458-row audit already in the field.

---

## 1. Introduction

*(Full text: `manuscript/01_introduction.md`. Summary retained here for a single-document read.)*

A model's reported benchmark score is contaminated by its verifier's own error rate, in a direction and magnitude nobody has measured, unless someone audits it. This paper (1) derives the sharp identified set for true accuracy under an audited, imperfect verifier; (2) shows empirically, on MATH-Hard, that the resulting audit-estimation uncertainty dominates the field's already-reported sampling uncertainty for most identifiable comparisons; (3) formalizes and stress-tests the audit-budget allocation problem this creates, finding and correcting a real failure mode in the textbook-optimal allocation rule under sparse data; and (4) shows, as a secondary but real finding, that which automated scorer is used to grade a benchmark is itself a measurable source of uncertainty, bounded (not assumed away) even in the worst case consistent with observed data.

---

## 2. Related work

**Partial identification and misclassification.** The identification strategy here is a direct adaptation of the classical misclassification-bounds literature (Horowitz & Manski, 1995; Molinari, 2008; Hu, 2008) — sensitivity/specificity-style calibration constants bounding a corrupted binary outcome. We claim no new mathematics in this layer (class A/B throughout, see `NOVELTY_AUDIT.md`); the contribution is applying it to benchmark comparison specifically, with an audit-design layer classical misclassification papers do not address.

**Concurrent, independent work.** Chen, Rambachan & Tamer (2026, arXiv:2606.15031) study partial identification of a *prevalence* from panels of LLM *raters* whose errors are correlated because the raters share training lineage — the same classical toolkit, a structurally different problem (their LLMs are the noisy raters; ours are the *rated* models, scored by one fixed, non-LLM, deterministic verifier). No overlap in estimand, no overlap in headline results; cited as the closest neighbor, not a competing claim.

**Benchmark and verifier reliability.** VerifyBench (Yan et al.) and CompassVerifier study *which verifier is more accurate* — a different question from ours ("given a verifier's audited error rate, what can still be concluded about a comparison"), complementary rather than overlapping. A body of work independently documents answer-format/extraction dependence as an open problem in LLM evaluation generally (confirmed via literature search, `NOVELTY_AUDIT.md`); we do not claim to have discovered that extraction is fragile, only to formalize its statistical consequence for benchmark comparison.

**Audit design.** The stratified-allocation solution (§5) is Neyman (1934), unmodified — cited, not claimed novel. The contribution is a documented, tested failure mode of the plug-in form under the specific sparse-event regime real benchmark audits actually operate in, and a corrected allocation.

**Verification bias.** The stratified-on-scorer-outcome audit design is checked against, and shown formally distinct from, the classical partial-verification-bias problem in diagnostic testing (Begg & Greenes, 1983) — our sampling probabilities are known by design, not an unknown behavioral process, which is the condition under which Horvitz-Thompson estimation is valid rather than biased (`THEORY_EXTENSIONS.md` §5).

---

## 3. Problem formulation

Let a benchmark item have a true binary correctness label `Y* ∈ {0,1}` for a given model's response, observed only through an automated verifier's report `Ŷ ∈ {0,1}`. Define the verifier's false-credit rate `α = P(Ŷ=1 | Y*=0)` and false-miss rate `β = P(Ŷ=0 | Y*=1)`. The observed accuracy `a = P(Ŷ=1)` relates to the true accuracy `A* = P(Y*=1)` by the law-of-total-probability identity

```
a = A*(1-β) + (1-A*)α
```

which inverts to `A* = g(a,α,β) = (a-α)/(1-α-β)` whenever `α+β ≠ 1`. Given only an *audited estimate* of `(α,β)` — a confidence region `B`, not a known point — the identified set for `A*` is `{g(a,α,β) : (α,β) ∈ B} ∩ [0,1]`, and for a pairwise comparison, the identified set for `Δ* = A₁*-A₂*` is the corresponding interval difference. **The central object of this paper is the width of this identified set, and how it compares to the sampling-only width the field currently reports (which implicitly assumes `α=β=0`).**

A genuine subtlety, found and fixed during this project (`RECONCILIATION_EMPTY_SET_BUG.md`): when the box `B` lies entirely outside the region making `A* ∈ [0,1]` achievable — i.e., the observed accuracy `a` is logically inconsistent with every `(α,β) ∈ B` — the identified set is **empty**, not a clipped, fabricated interval. Naively clipping `max(g,0)`/`min(g,1)` independently at the box's corners silently inverts the interval in this case; the correct treatment reports non-identification explicitly. This affected 16–70 of 136 real pairs depending on layer (§5), corrected in both the research code and the published package, with full regression-test coverage (`tests/test_identification.py`).

---

## 4. Theory

**T-A (Scorer Sensitivity Model).** `A*` is identified up to the box `B`; sharp bounds via 4-corner evaluation when `B` does not straddle `α+β=1`, and via the feasible-region supremum (proven to diverge to the full `[0,1]`) when it does. Class B (direct adaptation of classical misclassification bounds). Full derivation: `TA_SSM_DERIVATION.md`.

**T-H (Sharpness).** The identified set computed by 4-corner evaluation (non-straddling case) is exact, not an outer bound — a linear-fractional-function vertex-theorem argument. Class B.

**Ranking-preservation theorem.** The ranking `A₁*>A₂*` holds for every `(α,β)∈B` **if and only if** `0 ∉ Δ*(B)` — a direct, exact corollary of T-H's sharpness, stated as an operational theorem because it clarifies that sharpness (not merely conservatism) is what makes the field's existing `contains_zero` check a valid necessary-and-sufficient robustness test, not just a sufficient one. Class B. Full statement and proof: `THEORY_EXTENSIONS.md` §2.

**T-B (Design-sensitivity impossibility).** There exists a compound sensitivity level `Λ̃` beyond which a comparison is unidentifiable at *any* benchmark sample size — a Rosenbaum-style design-sensitivity result (Rosenbaum, 2004) adapted to this setting. Class B. `TB_DESIGN_SENSITIVITY.md`, `TB_COMPOUND.md`.

**Correlated scorer error (Propositions 1–3).** Under a one-factor (shared item-difficulty) model — the same structural assumption underlying Dawid-Skene (1979) — non-differential item-heterogeneity strictly *reduces* the variance of a pairwise difference relative to an independence assumption (`Cov ≥ 0`, closed form, verified by simulation to within Monte Carlo tolerance); differential loading (a model-specific interaction with item difficulty) breaks this cancellation and is exactly what the framework is built to bound. Class B. `THEORY_EXTENSIONS.md` §1.

**Imperfect human reference (T-D).** A full latent-class treatment (Hui & Walter, 1980) is not justified by this project's data (14-item three-way rater overlap, insufficient to identify 4 rater-specific parameters plus a prevalence) — an explicit, evidenced decision, not a shortcut. A sensitivity bound `q_max(η)` is derived instead: given the observed apparent disagreement rate and an assumed human-labeler error rate `η`, the bound on the true scorer-wrong rate `q` this could be masking. On T-C's real data (0/69 apparent disagreements), the bound does not have a concerning breakdown point for realistic `η` (0–5%). Class B/C. `THEORY_EXTENSIONS.md` §4.

**Verification-bias formalization (T-E).** The audit's stratified-on-scorer-outcome design is checked against, not assumed to match, the classical verification-bias structure; shown formally distinct because the stratum-conditional sampling probability `π_h` is known by design, which is exactly the condition under which the Horvitz-Thompson estimator (Horvitz & Thompson, 1952) is unbiased — proved, with the one load-bearing assumption (no dependence on unrecorded information) named explicitly. Class B. `THEORY_EXTENSIONS.md` §5.

**Flip-budget uncertainty.** The flip budget `d*` (minimum differential-error perturbation to put a comparison's sign in doubt) is given a bootstrap confidence treatment (`paired_bootstrap_delta`, joint resampling of benchmark and audit items) rather than reported as a bare point value. On the current real MATH-Hard roster's most fragile and most robust identified pairs, `d*` is bootstrapped with 95% intervals excluding zero cleanly in both cases (§7 below; full numbers `THEORY_EXTENSIONS.md` §7). A rigorous asymptotic-coverage proof for this specific nonlinear, possibly-empty-set estimand is flagged as open, not attempted here.

**Partial pooling.** Empirical-Bayes shrinkage toward a global anchor genuinely propagates a local audit's effect to un-audited models — verified directly on real data (`TC_ALPHA_BETA_UPDATE.md`), both a benefit (stabilizes thin per-model audits) and a documented cost (this session's own audit-design work: naive plug-in Neyman allocation, which implicitly relies on the raw per-cell rate as a planning estimate, is *dominated by uniform allocation* when most cells have near-zero raw counts — §5). Class B/C. `THEORY_EXTENSIONS.md` §6.

**Novelty summary.** No individual result above rises above class C (nontrivial combination/extension); several are B (direct, correctly-cited adaptations). The claimed contribution is the *combination* — benchmark comparison + scorer misclassification + partial identification + audit-estimation uncertainty + audit-budget design + (secondarily) scorer-choice dependence — evidenced with real data throughout, not the individual mathematical pieces. See `NOVELTY_AUDIT.md` for the full A/B/C/D table.

---

## 5. Audit design

**The formal problem.** Given qualifying models with audit strata (credited, wrong) and a fixed additional labeling budget `B`, choose the allocation minimizing total variance of the resulting stratified estimators — the classical stratified-sampling problem (Neyman, 1934), solved by `n_s ∝ √(p_s(1-p_s))`, proof included (three lines, Lagrangian) in `scripts/fb_audit_design_optimization.py`, cited not claimed.

**The failure mode, found and fixed.** On this project's real audit data, 15 of 17 qualifying models have exactly zero observed false-credit events (17/17 zero false-miss). Plug-in Neyman weights are therefore near-zero for almost every stratum and concentrate the entire additional budget on the one or two cells with the largest — and noisiest, since it comes from a tiny `n` — observed rate. Swept as an actual budget curve on the real 120-pair audit-only reconciliation layer: **naive Neyman allocation stalls at 74% unresolved even at 16× the current budget, while simple proportional allocation reaches 22%, and a genuine greedy search over the actual discrete objective (minimize unresolved-comparison count) reaches 40% at only 4× budget.** This does not contradict Neyman's optimality proof — it demonstrates that variance-optimality-given-the-true-`p` is a poor proxy for this discrete objective when the planning estimate itself is this unreliable, a real, quantified, previously-undocumented limitation. Full sweep: `AUDIT_DESIGN_OPTIMIZATION.md`.

**A second, real bug found building the second audit round.** When designing the 458-row expansion, the four preregistered joint-scorer cells were found to have sampling fractions differing up to 6× relative to their population sizes. Naively pooling raw counts across cells feeding the same target's credited/wrong union — the initial implementation — is biased: verified numerically at +444% relative error in a realistic scenario (`METHODOLOGICAL_AUDIT.md` items 3/5). Corrected with a Horvitz-Thompson / post-stratified estimator before any real label was processed; 7 regression tests added, including a parametrized synthetic-recovery check at four different stratum-prevalence pairs.

**Negative controls (falsifiability).** The framework is not structurally biased toward reporting more uncertainty regardless of input: three of five constructed scenarios (perfect scorer + adequately large audit; a scorer audited at the project's own derived required-n) correctly report *stable* — ratio below 1. Notably, even a *perfect* scorer at the real audit's median size (n=11) still shows 5.6× dominance — the headline finding is a statement about audit thinness, not necessarily large true scorer error, which the audit-design contribution directly targets. `NEGATIVE_CONTROLS.md`.

---

## 6. Empirical setup

**Data.** Open LLM Leaderboard v2's MATH-Hard subtask, 7 subjects, 27 models with public per-item generations (17 pass the audit-qualification gate: nonzero audit `n` on both the credited and wrong strata). Standard comparator: `vendor/leaderboard_math/utils.py`, byte-identical to the companion project's copy (verified by direct diff).

**Human audit (analysis B's basis).** 69 usable, blinded, transcription-protocol-labeled human judgments (of an originally-planned larger round; see `TC_REAL_ANALYSIS.md`) against the `score_boxed` (last-`\boxed{}`-found) extraction path. 0/69 scorer-wrong events; 100% three-way inter-rater agreement (14-item overlap). Pooled α (empirical-Bayes shrunk): 0.0314; β: ≈0.

**Second, larger human audit (analysis C's basis, in the field).** 458 rows, jointly stratified on both `score_boxed` and `exact_match`, preregistered before generation (`TC_EXPANSION_PREREGISTRATION.md`), power-justified (n=300 for a first `exact_match`-α estimate; n=60, 65–89% power, for a scorer-disagreement-resolution comparison). `[PENDING — human audit]`.

**Excluded, not used.** Two prior labeling-quality failures (a corrupted resubmission; two failed IFEval rounds) and two AI-generated substitutions for the second T-C round, all detected via a statistical-signature check (near-total mechanical agreement with automated scorers, zero use of the `CONTRADICTORY` marking, implausible turnaround time) and preserved as provenance only, never entering any result (`provenance/excluded_labeling_attempts/`).

---

## 7. Results

### 7.1 Audit-estimation uncertainty dominates sampling uncertainty (established)

| Analysis | Pairing | Median ratio | % dominant | n valid |
|---|---|---|---|---|
| **A** (historical, mixed) | `exact_match` accuracy + `score_boxed`-audited (α,β) | 6.10× | 100.0% | 120/136 |
| **B** (self-consistent) | `score_boxed` accuracy + `score_boxed`-audited (α,β) | 5.74× | 100.0% | 120/136 |
| **C** (`exact_match`'s own) | `exact_match` accuracy + `exact_match`-audited (α,β) | `[PENDING — human audit]` | `[PENDING]` | `[PENDING]` |

Both established analyses agree in direction and near-agree in magnitude: the headline is not an artifact of the accuracy-input choice. Full denominator cascade (378 candidate pairs → 136 scored → 120 valid, with every exclusion stage counted): `CANONICAL_EA_RESULT.md`.

### 7.2 Four-layer uncertainty decomposition (Figure 1)

Sampling (0.043 median width, n=136) < scorer-identification (`score_boxed`, Λ=2; 0.068, n=66) < scorer-choice (0.009, n=120) ≪ audit-estimation (`score_boxed`; 0.280, n=120). See Figure 1 (`figures/fig1_uncertainty_decomposition.png`) and caption for the scorer-choice-width caveat (§7.4).

### 7.3 Flip-budget robustness (established, on real pairs)

Bootstrapped `d*` on the current roster's most fragile and most robust resolved pairs (`THEORY_EXTENSIONS.md` §7): both require substantial differential error (`d* ≥ 0.17`, 95% intervals excluding zero) to flip — real comparisons, once identified, tend to be decisively resolved.

### 7.4 Scorer-mismatch (established main finding; worst-case bound established, `exact_match`'s own audit `[PENDING]`)

MATH-Hard's harness computes two live scores per item: `exact_match` (`math_verify`) — the field's actual reported metric, and this project's own `a_hat` throughout — and `score_boxed` (last-`\boxed{}`) — what every T-C audit has measured. **Full population (22,508 rows, 17 models × 7 subjects): 3.63% disagreement (95% CI [3.39%, 3.88%]), model range 0.60–9.59%.** (An earlier, algebra_hard-only spot check of 6.51% was mis-presented alongside full-population language in an intermediate draft — corrected everywhere; see `METHODOLOGICAL_AUDIT.md` item 1.) Bidirectional, not favoring either scorer systematically (12-category constructed adversarial taxonomy, `SCORER_MISMATCH_AND_ADVERSARIAL_FINDINGS.md`: `score_boxed` false-misses unboxed "Final Answer: X" prose; `exact_match` false-credits at least one unit-mismatch case).

**The 0.0091 median "scorer-choice width" in Figure 1 is an accuracy-substitution point-estimate shift — holding `score_boxed`'s audited (α,β) fixed and varying only which accuracy feeds the identification formula — not a full, symmetric two-scorer identification-uncertainty comparison**, because `exact_match` has no audited (α,β) of its own yet (`METHODOLOGICAL_AUDIT.md` item 2). **Worst-case sensitivity, established without new labels**: bounding `exact_match`'s plausible α at [2.38%, 26.73%] from the observed disagreement population sizes (worst case ≈8.5× `score_boxed`'s known rate) and running it through the identical Λ=2 methodology gives a worst-case median scorer-identification width of 0.166 — still below the established audit-estimation median (0.280). **Verdict B survives even this adversarial bound**, with an honest cost reported alongside the favorable comparison: only 10 of 120 pairs remain valid at all in the worst case, and all 10 are fully unresolved (`METHODOLOGICAL_AUDIT.md` item 7). `[PENDING — human audit]`: `exact_match`'s actual (not worst-case-bounded) audited α, β, and its own fully self-consistent identification result (analysis C, §7.1).

### 7.5 Generalization beyond MATH-Hard (established: limited, not fabricated)

IFEval's `strict_acc`/`loose_acc` confirmed as a second, real, but structurally different data point (2.60% disagreement, already measured; two leniency settings of *one* verifier, not two independently-implemented libraries). BBH checked directly and does not qualify (single metric field per record). GPQA/MMLU-PRO/MuSR are loglikelihood-scored multiple-choice, structurally ruled out. **Honest conclusion: confirmed on one benchmark in the strong sense, a related-but-distinct phenomenon on a second; not yet established as a general property of automated evaluation.**

---

## 8. Limitations

1. `exact_match`'s own audited α/β do not yet exist — analysis C is the single largest open piece of this paper, `[PENDING — human audit]`, 458 rows, preregistered and in progress.
2. The correlated-error cancellation result (§4) is verified by simulation against its own closed form, not fit to any real (π, p_hard, p_easy) — no dataset has produced enough scorer-wrong events to fit it (0/69 real T-C events).
3. `is_equiv`'s (the `score_boxed`-path comparator's) behavior was verified correct on Linux via GitHub Actions CI, resolving the original Windows-only bug finding, but the two smaller, named structural limitations found in the adversarial suite (interval/set-notation reordering; unit-word stripping) remain unfixed — flagged, not silently left stale.
4. The scorer-choice generalization claim (§7.5) is deliberately narrow: one benchmark in the strong sense. A second, independent benchmark with two genuinely independent scoring libraries was searched for and not found within this project's currently-accessible data sources.
5. The asymptotic coverage properties of the bootstrap-based flip-budget interval (§4, §7.3) are not proven for this specific nonlinear, potentially-empty-set estimand — a real, named gap for a statistics-focused venue, not claimed resolved.
6. Naive-Neyman-allocation-fails is demonstrated on this project's own real, sparse data; whether it generalizes to audits of other benchmarks with different sparsity patterns is untested.

---

## 9. Discussion

The central claim is not that any individual scorer is unusually bad. It is that **reported benchmark accuracy is not automatically identified** — the measurement procedure that produces it is itself imperfect, audited only partially, and that partial audit is where most of the practically relevant uncertainty currently lives, exceeding the sampling uncertainty the field already reports and accounts for. This reframes audit-budget allocation from an implementation detail into part of the benchmark-comparison validity problem itself, with a concrete, tested design consequence: naive allocation formulas fail exactly where real audits are sparsest, and a corrected, stress-tested alternative exists. The scorer-mismatch finding extends this same logic one level further — even the choice of *which* automated criterion counts as "the verifier" is a measurable design decision, not a given, though this project's evidence bounds rather than resolves how much it matters for any specific comparison whose own audit is still pending.

---

## 10. Conclusion

We derive a sharp identified set for benchmark accuracy under audited scorer error, show empirically that audit-estimation uncertainty dominates sampling uncertainty for most identifiable MATH-Hard comparisons, formalize and correct a real failure mode in the resulting audit-budget design problem, and establish scorer-choice dependence as a measurable, non-dominant, worst-case-bounded secondary source of uncertainty. The combination — not any individual classical component — is the contribution. One preregistered, in-progress human audit (458 rows) remains before the paper's empirical core is fully closed; every other piece of the argument stands on evidence already in hand.

---

## Appendix pointers (see `manuscript/SUPPLEMENTARY.md`)

Proofs and derivations (`TA_SSM_DERIVATION.md`, `TB_DESIGN_SENSITIVITY.md`, `TB_COMPOUND.md`, `THEORY_EXTENSIONS.md`), HT estimator details and variance derivation (`METHODOLOGICAL_AUDIT.md`), sampling design (`TC_EXPANSION_PREREGISTRATION.md`), adversarial suite (`SCORER_MISMATCH_AND_ADVERSARIAL_FINDINGS.md`), bug disclosures (`MATH_COMPARATOR_BUG.md`, `RECONCILIATION_EMPTY_SET_BUG.md`, `TC_EXPANSION2_LABELING_QUALITY_ISSUE.md`), reproducibility (`scripts/fb_reproduce_all.py`).
