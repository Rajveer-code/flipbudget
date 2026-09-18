# Core estimand audit (2026-09-19)

Scope: what the scorer-stratified human audit actually identifies, and what
the paper can legitimately claim from it. All manuscript polishing is frozen
until this is resolved.

Evidence:
- `scripts/fb_core_estimand_audit.py` → `results/flipbudget/core_estimand_audit.json`
- `scripts/fb_458_redesign.py` → `results/flipbudget/redesign_458.json`
- `tests/test_core_estimand.py`

Every number below is printed by those scripts.

**Verdict in one line.** The old pipeline plugged predictive-value
quantities into a sensitivity/specificity formula. The corrected analysis
has these consequences:
- the old headline (6.10× / 5.74×) is invalid;
- the empty-set "finding" is an artifact;
- "analysis A" and the "scorer-choice width" are incoherent;
- with this audit, almost no per-model ranking is identified (3 of 136 pairs);
- the 458-row design is **MODIFY, not GO**.

---

## 1. Original formulation

Paper §3 defines the following:
- latent correctness Y*;
- scorer output Ŷ;
- α = P(Ŷ=1 | Y*=0);
- β = P(Ŷ=0 | Y*=1);
- a = A*(1−β) + (1−A*)α;
- A* = g(a,α,β) = (a−α)/(1−α−β).

The (α,β) box B is a product of Wilson intervals. The pairwise set for Δ* is
the interval difference.

## 2. Exact error

The original audit (`results/analysis/mathhard_frame.json`) is a stratified
sample of 400 (model, item) rows drawn from a pooled population of 35,613
rows across 28 models:
- strata: **score_boxed outcome** (credited / wrong_parsed / unparsed) × subject × length quartile;
- the sample is not stratified by model, and not by Y*.

`fb_e4_mathhard.py:per_model_rates` computes `alpha_raw` as false credits
among audited credited items. That estimates **q = P(Y*=0 | Ŷ=1)**, not α.
Likewise `beta_raw` estimates **r = P(Y*=1 | Ŷ=0)**, not β.
`ea_dominance_study.py` then feeds q̂ and r̂ into g as if they were α and β.

The error is **not** the formula g. It is feeding g the wrong conditional
probabilities.

Sympy (`algebra` block in the JSON) confirms that g(a, q, r) − A* is a
nonzero rational function. It vanishes only in degenerate cases such as α = 0
with β = 0.

## 3. Correct formulation

Symbols are kept distinct:

| Symbol | Meaning | Conditions on | Estimable from Ŷ-stratified audit? |
|---|---|---|---|
| A* = P(Y*=1) | true accuracy | – | yes, via q and r |
| a = P(Ŷ=1) | scorer accuracy | – | census (observed for every item) |
| α = P(Ŷ=1\|Y*=0), β = P(Ŷ=0\|Y*=1) | error rates | truth | only indirectly (Bayes, needs a) |
| q = P(Y*=0\|Ŷ=1), r = P(Y*=1\|Ŷ=0) | predictive-value complements | scorer output | **directly** |

## 4. Derivation

By the law of total probability over Ŷ:

A* = P(Y*=1|Ŷ=1)P(Ŷ=1) + P(Y*=1|Ŷ=0)P(Ŷ=0) = **a(1−q) + (1−a)r**.

Conversion (sympy residual 0):
- α = a·q/(1−A*)
- β = (1−a)·r/A*

Properties:
- The map is affine in (q,r) and bounded. A* ∈ [0,1] for every q,r ∈ [0,1],
  so **the identified set can never be empty** and there is no straddle or
  divergence case.
- This is the classical estimator for a two-phase design (Neyman 1938):
  - phase 1 is a census of Ŷ;
  - phase 2 samples within Ŷ strata;
  - it is equivalent to the Begg–Greenes (1983) verification-bias correction,
    because verification depends only on the test result and the sampling
    probabilities are known.

What is identified depends on the estimand:
- **Finite-benchmark estimand** A*_N (mean of Y* over the benchmark's items):
  a is known exactly. Â = a(1−q̂)+(1−a)r̂ is design-consistent, with the q̂, r̂
  stratum-weighted (Hájek) within the audit design.
- **Superpopulation estimand**: the item-sampling variance of a is added on
  top.
- Given an infinite audit, A* is **point-identified**. Every width attributed
  to "audit estimation" is therefore **estimation uncertainty, not
  identification**. Calling it an "identified set" was a category error.
  Genuine partial identification appears only through:
  - indeterminate labels (§7);
  - an imperfect human reference;
  - transport of q and r to models that were not audited;
  - a mismatch between the scorer that produces a and the scorer that defines
    the strata.

**Coherence condition.** The identity requires that a, q and r all refer to
the **same scorer's** Ŷ. The original strata are score_boxed, so only
score_boxed accuracy can be corrected with them. "Analysis A" (exact_match
accuracy plus a score_boxed-stratified audit) has no valid interpretation and
must be removed. The same holds for the "scorer-choice width" (0.0091), which
substitutes one scorer's accuracy while keeping the other scorer's box.

## 5. Identification implications

- **Single model.** A*_m ∈ [a(1−q_hi) + (1−a)r_lo, a(1−q_lo) + (1−a)r_hi].
  This is sharp: the map is affine and the box is a rectangle.
- **Pairwise.** Δ* = A*_1 − A*_2.
  - Model 1's and model 2's audited rows are disjoint, so their parameters
    vary independently and the interval difference is sharp.
  - A joint ≥95% confidence set comes from the Šidák projection, with each of
    the 4 parameters at level 0.95^(1/4). This is a valid conservative
    confidence set, which fixes the old coverage problem (R1.1).
- **Ranking preservation.** The ranking is preserved iff 0 ∉ Δ*(B). This
  follows trivially from the formula.
- **Homogeneous mechanism.** If all models share one (α,β), then
  Δ* = (a1−a2)/(1−α−β), so **rankings can never flip**. Only
  *differential*, model-dependent error can flip a ranking.

## 6. Simulation verification

Setup: 4,000 reps per scenario; finite benchmark N = 1324; SRS within Ŷ
strata; 95% Šidák-Wilson projection.

| Scenario | PV bias | Old-map bias | PV coverage | Old-map coverage (non-empty) | Old-map empty rate |
|---|---|---|---|---|---|
| typical (A=.20, α=.01, β=.02) | −0.0001 | −0.027 | 1.000 | 0.998 | 0.000 |
| low accuracy (A=.02) | +0.0002 | **−0.560** | 1.000 | **0.237** | **0.597** |
| zero-accuracy model | 0.0000 | undefined | 1.000 | – | **1.000** |
| high error (α=.10, β=.15) | −0.0003 | −0.078 | 1.000 | 0.961 | 0.000 |
| perfect scorer | 0.0000 | 0.000 | 1.000 | 1.000 | 0.000 |

- The PV estimator is unbiased in every scenario.
- The old map is biased and can be empty exactly when accuracy is low. That
  is the command-r case (a_em = 0), which reproduces the 16 "empty" pairs.
- PV coverage of 1.000 means the per-stratum Wilson sets at n ≈ 6–40 are very
  conservative. The sets are valid but wide.

## 7. Real-data re-analysis (17 qualifying models, 136 pairs)

**Stratum check.** 320 of 320 audit items that are also in the population
have a consistent score_boxed stratum.

| Analysis | Valid | Empty | Median ratio | Min | % dominant | Median audit width | Median sampling width | Pairs resolved |
|---|---|---|---|---|---|---|---|---|
| A_old (paper headline) | 120 | 16 | 6.095 | 2.153 | 100 | 0.277 | 0.0438 | 29 |
| B_old (paper "self-consistent") | 120 | 16 | 5.735 | 1.375 | 100 | 0.254 | 0.0425 | 28 |
| A_pv, incoherent (my 2026-09-19 "18.9×") | 136 | 0 | 18.884 | 7.904 | 100 | 0.724 | 0.0431 | 5 |
| **B_pv, per-parameter 95%** | **136** | **0** | **20.191** | **8.148** | **100** | **0.718** | **0.0416** | **3** |
| **B_pv, Šidák joint ≥95%** | 136 | 0 | 25.528 | 11.272 | 100 | 0.942 | 0.0416 | **1** |

**Correction to my own earlier report.** The "18.9×" I quoted on 2026-09-19
mixed exact_match accuracy with score_boxed strata. It was incoherent under
the corrected formulation too. The valid figure is B_pv.

**What the larger ratio actually means.** It does not mean a stronger
finding. The false-miss side drives the width:
- the whole audit has **0 false misses in 127 wrong-stratum items**, spread
  over per-model n of 1 to 17;
- the Wilson upper bound for r at 0 of 1–4 items is 0.5–0.8, multiplied by
  the (1−a) ≈ 0.8–0.99 mass;
- as a result, per-model nonparametric identification from this audit is
  **almost uninformative**: 3 of 136 pairs are resolved (1 of 136 jointly).

**Audit size needed** (`crossover`; zero events per stratum, N = 1324): the
audit width drops below the sampling width at about the following audit sizes
per stratum, per model:

| Model accuracy a | Audit items needed per stratum |
|---|---|
| 0.35 | 71 |
| 0.20 | 86 |
| 0.05 | 160 |

For 17 models that is roughly 2,400–5,400 labels, against the current 289
usable. The old "audit dominates sampling" headline is a direct consequence
of this design ratio. It should be stated as this design result, not as a
property of the benchmark.

**Error is differential (new, real finding).**
- Across 162 credited items there are 5 false credits: 4 of 6 in command-r-v01
  and 1 of 29 in Yi-1.5-34B.
- Homogeneity of q across models: permutation p = 0.00035. This alone is
  expected, because q depends on a.
- The correct test is a **common-mechanism model**, with one (α,β) for all
  models and q_m and r_m implied through a_m:
  - ML estimates: α̂ = 0.0015, β̂ = 0;
  - likelihood ratio vs saturated = 24.8;
  - parametric bootstrap p ≈ 0.010 (300 reps);
  - α > 0.0023 is infeasible for the lowest-accuracy models.
- command-r's 4/6 cannot be produced by a scorer-wide error rate. Scorer error
  depends on the model's output format.
- Differential error is exactly the condition under which rankings can flip,
  so it justifies the per-model treatment. The per-model audit is too thin to
  use it.

**Indeterminate labels** (NONE/CONTRADICTORY, currently dropped):
- 12 credited-stratum items, including Yi-1.5-9B-Chat with **8 of 14**;
- 19 wrong-stratum items.

A scorer-credited response with no committed answer is plausibly a false
credit. Dropping these rows is a missing-not-at-random choice. The correct
treatment is Manski-style bounds: indeterminate counted as correct vs as
incorrect. This is one of the few **genuine** partial-identification layers
in the paper.

## 8. Consequences for every existing theorem

| Result | Status | Action |
|---|---|---|
| Problem formulation §3 (g with audited α, β) | **Wrong input** | Rewrite in (q,r). Keep α, β only via the Bayes conversion. |
| Empty identified set "subtlety" | **Artifact of the error** | Remove from paper and contributions. Keep the audit trail (this file; `RECONCILIATION_EMPTY_SET_*.md`). Under a common-mechanism model, emptiness is a specification failure, which §7's test detects directly. |
| T-A scorer sensitivity model (Λ odds ratio on α, β; straddle case) | Modify | Re-derive Λ-bounded *differential* departure on (q,r) or on the mechanism. The straddle case disappears. |
| T-H sharpness (linear-fractional vertex argument) | Survives trivially | Replace with a one-line affine-map argument. Class A. |
| Ranking preservation | Survives, trivial | Add the homogeneous-mechanism corollary: no flips without differential error. |
| T-B design-sensitivity impossibility | Modify | Re-derive under PV. The claim plausibly survives: a Λ box keeps nonzero width as n→∞. It must be recomputed. |
| Correlated-error proposition (one-factor) | Re-verify | Concerns item-level error covariance. Recheck the algebra under the PV parameterization before keeping it. |
| T-D imperfect reference q_max(η) | Modify | Re-derive: η contaminates the q̂ and r̂ labels directly. |
| T-E "formally distinct from verification bias" | **False claim** | This *is* the Begg–Greenes design (verification depends only on the test result, known probabilities) and Neyman's (1938) two-phase stratification. Remove "distinct" and cite it as the standard estimator. |
| Flip budget d* | Modify | Redefine the perturbation on (q,r). Recompute the bootstrap. |
| EB partial pooling (anchor 0.0314) | Remove or rebuild | Shrinking q toward a common value is inconsistent with q depending on a, and the common mechanism is rejected. |
| Neyman "dominated by proportional" (75.8/74.2/21.7%) | Recompute | The objective used the old map. The Neyman-vs-proportional logic must be re-run on the PV objective with Monte Carlo over plausible rates. |
| Worst-case exact_match bound (0.166; 10 of 120 valid) | Remove | Built on incoherent analysis A. |
| Scorer-choice width 0.0091 | Remove | Incoherent accuracy substitution. Replace with a_em − a_sb plus disagreement-cell resolution. |
| Scorer mismatch 3.63% (817/22,508) | **Unaffected** | A census fact, independent of any map. |

## 9. Consequences for the 458-row audit

**What the design identifies.** The 4 joint cells {sb, em} ∈ {0,1}² partition
the 22,184-row population (not yet labeled; 320 already-labeled rows
excluded) with known sizes:

| Cell | Population size |
|---|---|
| both credited | 1,531 |
| both not credited | 19,873 |
| score_boxed only | 291 |
| exact_match only | 493 |

A Horvitz–Thompson estimator over the cells therefore gives pooled, design
unbiased estimates of:
- A*;
- q and r for **both** scorers, because each scorer's Ŷ=1 domain is a union
  of cells;
- α and β for both scorers, via the Bayes conversion;
- the disagreement resolution.

The design is **valid for pooled estimands**. It is **not** a per-model design.

**Existing analysis code.** `fb_tc_expansion2_analysis.py` HT-pools q
correctly within cells. It then feeds q into the old map for the
reconciliation step. That step has to be rewritten.

**Efficiency under the corrected targets.**
- Planning priors: P(Y*=1 | cell) = 0.97 / 0.01 / 0.5 / 0.5.
- Efficiency = variance of the target-specific Neyman allocation divided by
  the variance of the candidate allocation.

| Target | Current 200/198/30/30 | Minimax 96/126/98/138 |
|---|---|---|
| pooled A* | 0.66 | 0.46 |
| q_em | **0.18** | 0.40 |
| q_sb | 0.26 | 0.30 |
| r_em | 0.47 | 0.31 |
| r_sb | 0.49 | 0.34 |
| disagreement gap | **0.055** | 0.30 |

The current design spends 398 of 458 rows on the two concordant cells, which
carry almost no information about which scorer errs. The minimax design:
- raises the worst-case efficiency from 5.5% to 30%;
- depends on planning priors that are assumptions, and must be re-run if the
  priors change.

**Also add model-proportional sub-stratification inside each cell.** Then
per-model domain estimates exist and the differential-error test (§7) can be
repeated for exact_match.

## 10. Consequences for the paper's claims

The following are invalid and must go:
- the 6.10× and 5.74× figures;
- "100% dominant among 120 valid";
- the 16–70 empty-set pairs;
- the audit-estimation width of 0.280;
- the four-layer figure and table (Fig 1, Table 3);
- analysis rows A and C as currently specified;
- Fig 5 and the worst-case paragraph;
- the Neyman numbers in Table 4 and Fig 2 until recomputed;
- the flip-budget values;
- the empty-set row in the appendix bug table;
- the T-E "distinct" claim.

What survives, stated correctly:
1. **Census fact:** the two live MATH-Hard scorers disagree on 3.63% of
   responses.
2. **Scorer error is rare but differential by model**, with a formal
   common-mechanism rejection, p ≈ 0.01.
   - Under a common mechanism, rankings cannot flip.
   - Under differential error they can.
3. **Design result:** a per-model nonparametric correction needs about 70–160
   audited items per stratum per model before audit uncertainty stops
   dominating sampling uncertainty. The existing 350-item pooled audit
   resolves 3 of 136 pairs. This is a quantitative audit-sizing law for
   leaderboards.
4. **A genuine partial-identification layer:** indeterminate labels,
   concentrated in specific models.

This is a smaller paper than the current draft, but it is a correct one.

## 11. Literature comparison (verified by search 2026-09-19)

- **The corrected estimator is standard. It is not a contribution.**
  - Neyman (1938), two-phase sampling for stratification (JASA 33).
  - Tenenbein (1970), double sampling for misclassified binomial data,
    including optimal n allocation (JASA 65:1350–1361).
  - Begg & Greenes (1983), verification-bias correction when verification
    depends only on the test result (Biometrics 39:207–215).
- **ML evaluation analogues:**
  - PPI (Angelopoulos et al. 2023);
  - Stratified PPI (Fisch et al., NeurIPS 2024), stratified hybrid evaluation
    of LMs with allocation;
  - Prediction-Powered Ranking (Chatzi et al., NeurIPS 2024), which covers
    ranking uncertainty;
  - AutoEval Done Right (Boyeau et al., ICML 2025);
  - Lee et al., "How to Correctly Report LLM-as-a-Judge Evaluations"
    (ICML 2026). Uses a sens/spec correction with a calibration-set CI and
    adaptive calibration allocation. Its calibration set is sampled on truth,
    so the sens/spec parameterization is right *for their design*. That is
    precisely the distinction this audit found.
- **What remains novel, precisely:**
  - evidence that deterministic-verifier error on a public leaderboard is
    *differential by model*, with a formal test;
  - the audit-sizing law for per-model ranking identification on leaderboards
    (and the StratPPI / Tenenbein-style allocation specialized to a
    number-of-resolved-pairs objective, only if it is re-derived and beats
    their allocations);
  - a joint two-scorer stratified design that resolves scorer choice;
  - indeterminate-label bounds.
- **Honest ceiling.** None of these is a new statistical method. It is an
  empirical and design contribution. NeurIPS E&D or a workshop is realistic.
  A methods-track claim is not.

## 12. Hostile statistics review of the corrected derivation

- **Observed:** a census of each scorer's Ŷ on every (model, item). a_m is
  exact for the finite benchmark.
- **Sampled:** about 400 rows, stratified by (score_boxed outcome × subject ×
  length), pooled over 28 models, with unequal inclusion probabilities.
  Per-model n is *random*, so per-model estimates are domain estimates and
  need Hájek weights. They coincide with the unweighted estimates here only
  because 15 of 17 models have 0 events.
- **The "human label" is a transcription.** Y* is then decided by the same
  normalize + is_equiv comparator family, so the audit measures *extraction*
  error only. Equivalence-checking errors shared with the reference are
  invisible. This is a construct assumption and must be stated as one.
- **Assumptions needed to get from the audit to a ranking statement:**
  1. the reference (transcription + comparator) equals true correctness;
  2. the indeterminate-row policy, otherwise bounded;
  3. a, q and r all come from the same scorer;
  4. models that were not audited need a transport assumption, and the
     common-mechanism transport is rejected by the data;
  5. the superpopulation versus finite-benchmark estimand is declared;
  6. coverage uses the joint projection, not per-parameter Wilson intervals.
- **Remaining attack:** planning priors drive the redesign efficiencies.
  Report the sensitivity to them.

## 13. Human audit decision: **MODIFY (do not GO)**

1. Amend the preregistration explicitly. The original estimand, (α,β) plugged
   into g, was a **pre-analysis estimand error**. No genuine labels have been
   collected, so the amendment is clean.
   - The original design is kept, marked superseded.
   - The new estimands are A*, q, r and (α,β) via Bayes, for both scorers,
     plus disagreement resolution.
2. Reallocate to about 96 / 126 / 98 / 138 (minimax), with
   model-proportional sub-stratification.
3. Redraw with a new fixed seed and a new sheet. Do **not** label the old
   `tc_expansion2_l1.csv`.
4. Rewrite the analysis to use the PV map, the Šidák projection, and
   indeterminate bounds.

**Labels received 2026-09-19** (`final labeled by me properly.csv`):
- 458 of 458 answers are identical to the already-excluded submission 3.
- 49 NONE and 0 CONTRADICTORY, the same signature.
- Not used. Under decision 3 it is moot anyway, because it labels the
  superseded sheet.

## Next (awaiting approval; nothing below started)

1. Rebuild `src/flipbudget/identification.py` and the analysis scripts on the
   PV map (tests first).
2. Implement the amended preregistration and redraw the sheet.
3. Rewrite theory and manuscript around §10's surviving claims.
4. Regenerate all figures and tables, then run a clean 38-step reproduction.
