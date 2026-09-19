# Final scientific re-audit (2026-09-19)

Scope: whether the corrected estimand, the results, and the rebuilt paper's
narrative are right, and what the paper should claim.

Evidence and scripts:

| Script | Output |
|---|---|
| `scripts/fb_core_estimand_audit.py` | `core_estimand_audit.json` |
| `scripts/fb_rebuild_analysis.py` | `rebuild_results.json` |
| `scripts/fb_reaudit.py` | `reaudit_results.json`, log `reaudit.log` |
| `scripts/fb_joint_verifier.py` | `joint_verifier_results.json` |
| `scripts/fb_disagreement_sample.py` | new sheet and provenance |

All output paths are under `results/flipbudget/`.

**Outcome in one paragraph.** The corrected single-verifier analysis is
right. But it answers a weak question: a small audit spread over 17 models
cannot certify per-model rankings, and that is expected by construction. The
data contain a stronger, better-supported result that the single-verifier
framing hid. The two live verifiers largely agree with human judgment when
they agree with each other: 1 error in 287 audited concordant items. Error is
concentrated where they disagree (3.6% of responses) and is model-specific
there. Stratifying on the joint verifier outcome lets **the existing 400-item
audit identify 84 of 136 pairwise orderings, against 118 identifiable from
sampling error alone at the same confidence level**. The single-verifier
per-model analysis identifies 1 (0 once sampling error is included). The thesis changes accordingly (§10). The
458-row audit is **MODIFY**: it is redesigned to target disagreements (§12).

---

## 1. Estimand, locked down

**Definitions.**
- Y* is the human reference.
  - Precisely: the labeler's transcription of the response's committed final
    answer is judged equivalent to the reference answer by the harness's
    `normalize_final_answer` + `is_equiv`. See §8.
  - Primary definition: a response judged to commit to no answer
    (NONE / CONTRADICTORY) has Y* = 0.
- Ŷ is a verifier's decision: `score_boxed` (last `\boxed{}`) or
  `exact_match` (Minerva "final answer" phrase). Both use the same
  normalization and equivalence routine
  (`knowledgeshift/scripts/19_l1_rescore_leaderboard.py`, checked).
- A* = P(Y* = 1): true accuracy. It belongs to the model and the reference,
  not to either verifier.
- Single verifier:
  - a = P(Ŷ = 1)
  - q = P(Y* = 0 | Ŷ = 1)
  - r = P(Y* = 1 | Ŷ = 0)
  - α = P(Ŷ = 1 | Y* = 0), β = P(Ŷ = 0 | Y* = 1). These enter only through
    Bayes' rule.
- Two verifiers:
  - cells c ∈ {11, 10, 01, 00}, shares s_c (census);
  - p_c = P(Y* = 1 | cell c).

**What the audit identifies.** The audit is stratified on score_boxed outcome
× subject × length quartile. Within a stratum, inclusion does not depend on
Y* or on exact_match. It therefore identifies P(Y* | score_boxed stratum)
and, by domain estimation, P(Y* | joint cell). Items per joint cell for the
17 models: 142 / 32 / 1 / 145.

**Identities.**
- A* = a(1 − q) + (1 − a)r.
- A* = Σ_c s_c p_c.
- Verified in three ways:
  - algebraically (sympy residual 0);
  - by simulation (bias ≤ 3e-4 in every scenario; the plug-in g(a, q, r) has
    bias −0.56 and a 60% empty rate at low accuracy);
  - on real data (the coherence rows below).

**Construct validity of every analysis:**

| Analysis | Accuracy scorer | Audit scorer / strata | Valid? | Reason |
|---|---|---|---|---|
| Old A (paper headline 6.10×) | exact_match | score_boxed q/r fed to g as α/β | **No** | wrong parameterization, and a mismatched scorer |
| Old B (5.74×) | score_boxed | score_boxed q/r fed to g as α/β | **No** | wrong parameterization |
| "18.9×" (my 2026-09-19 report) | exact_match | score_boxed q/r in the PV map | **No** | q/r condition on score_boxed; a must too |
| Rebuilt single-verifier (3/136) | score_boxed | score_boxed strata | Yes | same verifier throughout |
| Joint-verifier (this audit) | none: s_c from both censuses | domain estimates of p_c from the score_boxed-stratified audit | Yes | cells defined by both censuses; within-stratum inclusion is independent of exact_match |
| Census disagreement 3.63% | both | none | Yes | descriptive census |

**Remaining design caveat.** Per-cell p_c estimates are unweighted within the
pooled sample. Design weights vary by subject × length. With 1 error in 287
concordant items, weighting cannot move them materially. It matters for the
32-item cell, where the per-model treatment uses worst-case bounds anyway
(§4).

## 2. The 3/136 result, audited

Recomputed from raw data (`rebuild_results.json`, `reaudit_results.json`
`why`):

| Uncertainty accounted for | Pairs identified (of 136) |
|---|---|
| Sampling only | 119 |
| Per-parameter audit intervals | 3 |
| Joint 95% audit intervals | 1 |

**Why so few.**
- 94% of each model's interval width comes from the rejected stratum.
  - Median width contributions: r-part 0.382 vs q-part 0.026.
  - The r-part is the Wilson upper bound for r at 0 false rejections in 1–17
    audited items, multiplied by the (1 − a) ≈ 0.8–0.99 share of responses.
- Corrected *point* estimates reorder only **2 of 136** pairs, both involving
  c4ai-command-r-v01.

**Verdict: D.**
- **B:** verifier error is small and does not overturn orderings at the
  point level. The old "audit uncertainty dominates" thesis was overstated
  as a claim about benchmarks.
- **C:** this audit is too small *for a per-model single-verifier design*.
- **Not A** in any general sense. "Audit uncertainty dominates" is a property
  of this design, not of benchmarks.

## 3. Is 3/136 important, or just a small audit?

The answer is "just a small audit", quantified. Simulation: 200 replicates,
4 truth scenarios, fresh audits at k × the current 289 determinate labels.
Median share of 136 pairs identified at joint 95%, best single-verifier rule:

| Budget | ×1 | ×2 | ×4 | ×8 | ×16 | ×32 | ×64 |
|---|---|---|---|---|---|---|---|
| Heterogeneous-posterior truth | 0% | 9% | 31% | 50% | 65% | 76% | 83% |
| Low-error truth | 0% | 8% | 38% | 53% | 70% | 81% | 88% |

Reaching half of the identifiable pairs needs about 2,300 labels, and
two-thirds needs about 4,600. The single-verifier finding is therefore the
design statement "we conducted a small audit", not a discovery. It does not
support a paper on its own.

## 4. Audit design, rebuilt

**Allocation rules compared at equal total budget** (`reaudit_results.json`,
`budget.curves`):

| Rule | Result |
|---|---|
| Plug-in Neyman | **0% at every budget in every scenario**. With zero-event pilots it puts nothing where it matters. |
| Neyman with Jeffreys pseudo-counts | viable |
| Uniform | viable |
| Scaled current design | viable |
| "Width-optimal" | best or tied-best everywhere |

"Width-optimal" means n ∝ sqrt(a_m) for the credited stratum and
n ∝ sqrt(1 − a_m) for the rejected one. It is the exact minimizer of the
summed zero-event Wilson widths (Lagrange). That is the only sense in which
it is optimal, and it is not optimal for the resolved-pairs count.

**The real design gain is stratification, not allocation.** Stratifying on
the joint verifier outcome and auditing disagreements dominates every
single-verifier allocation:

| Strategy | Assumption | Identified (audit alone) | Identified (audit + sampling) |
|---|---|---|---|
| Joint cells: concordant pooled, disagreement [0,1] per model, existing audit | concordant-cell rates common across models | 101 | **84** |
| Same, concordant error allowed ×2 per model | weaker | 100 | 81 |
| Same, concordant error allowed ×5 per model | weaker | 89 | 64 |
| Joint cells, disagreement cells also pooled | + common disagreement rates | 127 | 103 |
| Existing audit + 458 labels on disagreement rows (stratified by model) | concordant common | – | median 95–98 |
| Every disagreement row audited (projection) | concordant common | 135 | 110–112 |
| Sampling-only ceiling at the same level | – | – | 118 |

For the 458-label row, the 10th–90th percentiles across three truth
scenarios lie between 94 and 101.

Indeterminates dropped instead of counted as Y* = 0: joint 84, pooled 104,
census 112 with sampling. The conclusions are unchanged.

## 5. The 458 labels, re-powered

- **The original 458 design (200/198/30/30, pooled over models).** Added to
  the single-verifier per-model analysis, it identifies a median 7–9%
  (uniform) or 10–15% (width-optimal) of pairs, depending on scenario.
  Scenarios: low error, moderate error, heterogeneous posterior, one
  model-specific error. It **cannot** materially change the single-verifier
  result, so it is not worth collecting for that question.
- **The same 458 labels spent on disagreement rows, stratified by model.**
  They raise the joint-verifier result from 84 to a median of about 95–98 of
  118 identifiable pairs. The rows are drawn in proportion to each model's
  exact_match-only / score_boxed-only row counts; the truth scenarios vary
  p10 and p01.
- **Answer.** 458 is a worthwhile size *only if redirected to disagreements*.
  It is not a dependency for the main claim, which rests on the existing
  audit.

## 6. exact_match vs score_boxed, resolved

1. **What the leaderboard reports.** It reports `exact_match`. The previous
   rebuilt manuscript "corrected" `score_boxed` accuracy. That is not wrong:
   by the identity, the target is scorer-free A*. But it was framed as if the
   non-reported metric were the object.
2. **Which verifier was audited.** The audit was stratified on
   `score_boxed`. The joint cells recover exact_match information from the
   same audit:
   - the exact_match-rejected / score_boxed-credited cell has 32 audited
     items: 16 correct, 4 wrong, 12 indeterminate;
   - the exact_match-credited / score_boxed-rejected cell has only 1 audited
     item, out of 493 rows in the population. It is the least-audited cell,
     and the redesign allocates 226 rows to it.
3. **Internal consistency.**
   - The rebuilt manuscript's analyses are consistent (same verifier for a,
     q and r).
   - Its Limitation 3 ("exact_match cannot be corrected") was wrong: A* is
     scorer-free, and the joint cells already use exact_match.
4. **Must the new audit finish first?** No. The main joint-verifier claim
   uses existing labels. The 01 cell is bounded worst-case [0,1] per model,
   so its thin audit is already accounted for. It is not pooled.

**Scorer choice alone reverses orderings.**
- Switching between `exact_match` and `score_boxed` reverses 8 of 136
  orderings.
- In 7 of those, the difference is significant under *both* verifiers'
  sampling error.
- 6 of the 7 involve c4ai-command-r-v01. The audit adjudicates that model:
  4 of its 6 audited score_boxed-credited items are human-wrong, so
  exact_match (accuracy 0) is closer to the truth for it.

## 7. Common-mechanism test, reassessed

- The full likelihood ratio is 24.8.
- c4ai-command-r-v01 contributes 15.3 of it on its own.
- Leave-one-model-out:
  - dropping command-r: LR falls to 6.1;
  - dropping any other model: LR stays between 22.0 and 24.7.
- Counting indeterminates as errors breaks the model fit (LR 224, β̂ at the
  grid boundary 0.3), so that specification is not usable.
- **Decision:** move it to the supplement as a one-model diagnostic. The main
  text does not need it. The joint-cell result explains the same observation
  more directly: command-r's errors all sit in the disagreement cell, which
  the joint design treats model by model.

## 8. What the audit measures (wording fixed)

The human transcribes the final answer the response commits to. The *same*
normalization and equivalence code used by both verifiers then compares that
transcription with the reference.

- **Validated:** answer extraction (which answer the response commits to,
  and whether it commits to one).
- **Not validated:**
  - semantic equivalence judgment (shared code, invisible);
  - reference-answer correctness;
  - reasoning.

Consequence: "human judgment" and "human correctness" are no longer used
anywhere. The paper says "human-transcribed answer, checked by the harness's
equivalence routine" and names the blind spot.

## 9. Prior art, head to head

Lee et al. is verified from arXiv 2511.21140 HTML. The others are summarized
from their abstracts.

| | Estimand | Sampling design | Uncertainty | Ranking? | Label allocation | Establishes | We add |
|---|---|---|---|---|---|---|---|
| Rogan–Gladen / Lang & Reiczigel | prevalence | Se/Sp from samples of known true status | CI for estimated Se/Sp | no | – | classical correction | a design sampled on the test result instead (two-phase), for many models |
| Begg & Greenes; Neyman 1938; Tenenbein 1970 | Se/Sp; mean | verification depends on test result; double sampling | ML / design-based | no | Tenenbein: phase sizes | **our estimator** | nothing new in estimation |
| Lee et al. (ICML 2026) | one model's accuracy under an LLM judge | calibration drawn **by true label** (m₀, m₁) | CI from test + calibration | no | m₀ : m₁ ratio | practical bias-corrected reporting | many models, pairwise ranking, model-specific error, verifier-output sampling |
| Stratified PPI (Fisch et al. 2024) | mean metric | stratified human + autorater | valid CIs | no | across strata | stratification tightens PPI | two deterministic verifiers as strata; ranking identification; shows the agreement cell carries almost no error |
| PP-Ranking (Chatzi et al. 2024) | rank-sets from pairwise preferences | human + LLM pairwise comparisons | coverage of rank-sets | **yes** | – | valid rank-sets | accuracy benchmarks with verifiers; per-model partial identification with model-specific error |
| AutoEval Done Right (Boyeau et al. 2025) | model accuracy / ranking via PPI | human + AI labels | PPI CIs | partly | – | efficiency of PPI for evaluation | model-specific error, joint-verifier stratification, audit sizing |

**Verdict on novelty.** No new estimator or inference method; earlier
novelty claims about the identification theory were too strong. What remains
is empirical and design-level, but concrete:
1. Two independent verifiers' agreement predicts correctness almost
   perfectly on this benchmark, and error sits in disagreements.
2. Stratifying the audit on joint verifier outcome turns an audit that
   certifies 1/136 orderings into one that certifies 84/136, under an
   assumption confined to concordant responses and tested by sensitivity.
3. Verifier choice alone reverses 7 statistically clear orderings.
4. A human-label budget of about 458, spent on disagreements, approaches the
   sampling ceiling.

This is a solid workshop contribution and a plausible TMLR paper once it is
replicated on a second benchmark. Stated as the rebuilt paper had it, as a
single-verifier sizing law, it would be thin.

## 10. Thesis selection

| Framing | Supported? |
|---|---|
| A. Partial identification under imperfect validation | Weak. Identification is point-wise given the audit; genuine partial identification is limited to indeterminates and the [0,1] disagreement bounds. |
| B. Human-audit uncertainty limits rankings | True only for the single-verifier design; a design artifact. |
| C. Audit design for resolving comparisons | Supported, but only with the joint-verifier stratification. |
| **D. Measurement + audit design** | **Best supported.** Measurement: what the audit measures (extraction), the correct estimator, two-verifier agreement as a correctness signal, scorer-choice reversals. Design: stratify on joint verifier outcome and audit disagreements. |

**Chosen: D.** Working title: *Audit the Disagreements: Certifying
Leaderboard Rankings with Two Verifiers and a Small Human Audit*.

## 11. Hostile review: why does this matter?

A reviewer asks: "3/136 by audit vs 119/136 by sampling — so what?"

**Answer.** Under the design people actually use (one verifier, a small
random or verifier-stratified audit), a human audit cannot certify a
leaderboard ranking: 1/136 at joint 95%. Pooling a single verifier's error
rates across models would certify everything, but only by assuming away
model-specific error, which this benchmark exhibits (command-r). With a second
verifier that the harness already computes, the same 400 labels certify
84/136, against a ceiling of 118. A 458-label disagreement-targeted audit
reaches a median of about 95–98. The cost of certification falls from
thousands of labels to hundreds.

**Weaknesses a reviewer will still raise:**
1. One benchmark and an older roster.
2. The concordant-homogeneity assumption rests on 1 event in 287. The ×5
   sensitivity costs 20 identified orderings (84 → 64).
3. The audit measures extraction only.
4. The two verifiers share normalization code, so their agreement is not
   independent evidence about equivalence errors.

**Verdict:**
- workshop-ready now;
- TMLR after a second benchmark with the same design;
- **not top-tier main-track ready**;
- NeurIPS E&D borderline without the replication.

The strengthening step is empirical, not rhetorical: replicate on a second
math benchmark. There, only disagreement rows plus a concordant check need
human labels, which is a few hundred labels.

## 12. Decision on the 458 labels: **MODIFY**

**Statistical reason.** As designed (pooled over models, 60 disagreement
rows), 458 labels move per-model identification by at most about 15%, the
upper end of §5's range. Spent on disagreement rows stratified by model, they
reach a median of about 95–98/118.

**New design (generated):**
- `labeling/audit_v2_l1.csv`: 457 rows, blinded, order shuffled, no model or
  verifier names in the file.
  - 358 disagreement rows, proportional by model × cell: 226 exact_match-only
    and 132 score_boxed-only.
  - 99 concordant rows: 49 both-credited and 50 both-rejected, spread evenly
    over models. These blind the disagreement rows and test the
    concordant-homogeneity assumption per model.
- Provenance with inclusion probabilities:
  `results/analysis/audit_v2_provenance.json` (not for distribution).
- Preregistration: Amendment 2 in `TC_EXPANSION_PREREGISTRATION.md`.

This remains optional for the paper's main claim. It must be labeled by a
person reading each response.

## 13. Updates made after this audit

- The manuscript is rewritten around thesis D.
- The single-verifier sizing curve is moved to a supporting role.
- The common-mechanism test is moved to the appendix.
- New figure: identification by design. New table: joint cells.
- Claim ledger, preregistration amendment and status file are regenerated.
- The full pipeline is re-run.

See `FINAL_STATUS.md`.
