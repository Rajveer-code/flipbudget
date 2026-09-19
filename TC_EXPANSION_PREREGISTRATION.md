# T-C expansion: preregistered design (~458 rows, approved this phase)

Written and committed **before** any new label is seen — this is the preregistration itself, not a post-hoc description. Scripts: `scripts/fb_tc_expansion_population.py` (population), `scripts/fb_tc_expansion_sample.py` (sampling + CSV). Sampling seed fixed at 42 (this project's standing convention) before drawing.

## Why ~458, precisely (not reused as a round number)

Three distinct sub-goals, each with its own target-n, computed via this project's own Wilson-CI machinery (not a generic formula):

1. **exact_match's own false-credit rate (α) — never measured before this phase.** Working prior for planning: 3.14% (score_boxed's pooled α, the closest available estimate — standard practice: plan around the best current estimate, revise after data returns). Target: Wilson-CI half-width ≤0.02 on the credited-stratum estimate. Computed directly (not approximated): **n≈300 achieves half-width 0.0201.**
2. **The scorer-disagreement resolution question — new this phase.** Of the cases where `exact_match` and `score_boxed` disagree, does one tend to be right more often, or is it close to a coin flip? Power calculation (one-sample proportion test, H0: p=0.5): **n=60 gives 89% power to detect a 70/30 split, 65% power for a more modest 65/35 split** — adequate for an exploratory-but-real answer, not overpowered for a secondary question.
3. **score_boxed's own α/β — the established target, continuity with the existing 69-row result.** Folded into the "both agree" cells below rather than budgeted separately (see design).

## The sampling design (4 cells, joint on both scorers)

| Cell | Definition | Target n | What it powers |
|---|---|---|---|
| `both_credited` | score_boxed=credited AND exact_match=credited | 200 | α for BOTH scorers simultaneously (the credited-stratum question that matters most for the reconciliation, since a_hat's correctness rests here) |
| `both_not_credited` | score_boxed≠credited AND exact_match≠credited | 198 | β for BOTH scorers simultaneously |
| `disagree_sb_credited_em_not` | score_boxed=credited, exact_match=not | 30 | Disagreement resolution (direction 1) |
| `disagree_em_credited_sb_not` | exact_match=credited, score_boxed=not | 30 | Disagreement resolution (direction 2) |
| **Total** | | **458** | |

**Why disagreement is split into two directional cells of 30 each, not one pooled cell of 60**: the two directions could have different true rates (e.g., `exact_match`'s unit-stripping false-credit found in the adversarial suite is a different failure mode than `score_boxed`'s missed-unboxed-answer false-miss) — collapsing them would average over two potentially different phenomena. Reported separately, optionally pooled at analysis time if they turn out similar.

## Population, exclusions, blinding

- Population: all (model, item) pairs for the **17 qualifying models** (the ones already in the reconciliation) across **all 7 MATH-Hard subjects**, freshly fetched (22,508 rows, `results/analysis/tc_expansion_population.json`).
- **Excluded**: any (model, item_id) already in the existing 400-item T-C population (`mathhard_labelling_key.json`) — 320 of those 400 belong to these 17 models and are excluded from the new sample, avoiding overlap where avoidable, per instruction. (The other 80 belong to non-qualifying models, not part of this population at all.)
- **Blinding**: identical to the existing, verified T-C protocol (`fb_tc_labeling_package.py`'s exact CSV format: `uid, problem, response, your_answer`) — no model name, no scorer stratum, no cell label, no gold answer in the distributed file. Row order shuffled (seed 43) so cell membership isn't inferable from position. Provenance (model/item/cell/gold) kept in a **separate, non-distributed** file (`results/analysis/tc_expansion2_provenance.json`), matched back to labels by `uid` only after they return, exactly as the existing protocol already does.
- **Labeling task unchanged**: the labeler transcribes the response's final answer (or writes NONE/CONTRADICTORY per the existing rules) — the SAME task as the original 69/70-row round. The comparison against gold, and against each of the two automated scorers, all happens at analysis time, after labels return. Nothing about the labeling task itself needed to change to resolve the scorer-mismatch question — only which items get shown.

## What this audit is intended to determine, exactly

1. **Does `exact_match`'s own α (never measured) resemble `score_boxed`'s (~3.1%), or differ meaningfully?** Directly tests whether the audit-estimation-uncertainty finding, built on `score_boxed`'s audited rate, would look different if built on the scorer that actually produces `a_hat`.
2. **When the two scorers disagree, which one tends to track human judgment?** Directly informs whether `a_hat` (exact_match-based) or the historically-audited number (score_boxed-based) is the more trustworthy accuracy signal going forward.
3. **Does more audit power (458 new + up to 320 excludable-overlap-avoided from the old 400) shrink the audit-estimation-uncertainty width, and does the "even a perfect scorer at n=11 shows 5.6x dominance" finding (`NEGATIVE_CONTROLS.md`) actually resolve at this larger n, as the theory predicts?** The direct test of whether the current central conclusion survives adequate power — not assumed to survive, per instruction.

## Efficient human-labeling protocol (added after two AI-generated submissions were excluded)

The task and blinding are unchanged (see above). Given 458 rows is a real time commitment and the failure mode just observed (an AI tool substituted for reading), the protocol going forward:

1. **Batch it.** Split the 458-row sheet into ~8 sessions of ~55-60 rows each (a sitting of well under an hour at a sustainable pace), not one continuous pass — the two excluded submissions arrived 6-7 minutes apart for 458 rows each, which is itself the tell; a real pace is closer to 5-15 seconds per row for the ~369 template-following rows and 1-3 minutes for the ~77-90 that need actual reading, i.e. several hours total, not several minutes.
2. **Submit in the same batches**, not all at once — makes a quality-gate check on each batch (`fb_tc_expansion2_analysis.py`'s gate) meaningful before the whole 458 rows are sunk into one submission.
3. **No AI tool in the loop for this specific task** — not a compliance rule for its own sake: the whole point of T-C is a judgment independent of automated extraction, so running the response text through any LLM/extraction tool first (even "just to help transcribe") reintroduces exactly the dependency the audit exists to check against. Reading the raw text and typing what it says is the entire task.
4. **The self-correction and NONE/CONTRADICTORY rules already in the README are the hard part** — those are also exactly what the 12-category adversarial suite targeted, so getting them right here is directly informative for the paper, not busywork.

## Analysis plan, fixed now, before any label is seen

Once labels return: (1) recompute α, β separately for `exact_match` and `score_boxed` from the `both_credited`/`both_not_credited` cells; (2) recompute the disagreement-resolution rate from the two disagreement cells; (3) recompute scorer-identification, audit-estimation, and combined uncertainty for BOTH scorer targets using the existing, unmodified `fb_reconcile_layers.py` machinery; (4) recompute pairwise identification and compare directly against the 69-row result; (5) report the A/B/C/D interpretation (scorer-error-dominant / audit-uncertainty-dominant / both / small-audit-artifact) strictly from what the numbers show — not decided in advance.


---

## AMENDMENT 1 (2026-09-19): pre-analysis estimand error; design superseded before any usable label

**What was wrong.** This design and its analysis plan target "alpha, beta" computed within the credited / not-credited cells. Sampling within scorer-output cells identifies q = P(human wrong | scorer credited) and r = P(human right | scorer not credited), not the error rates alpha = P(credited | wrong), beta = P(not credited | right). Analysis step (3) then fed these stratum rates into g(a, alpha, beta), which is biased. This is an error in the preregistered estimand, identified before any usable (human) label existed. It is recorded here as such, not folded in as an ordinary analysis update. Full derivation: CORE_ESTIMAND_AUDIT.md.

**Status of the original design.** Superseded, kept for the record. The 4-cell joint partition itself does identify pooled A*, q and r for both scorers, and alpha, beta via Bayes' rule, but the 200/198/30/30 allocation is inefficient for the corrected targets (5.5% efficiency for the disagreement-resolution contrast, 18% for q_em; results/flipbudget/redesign_458.json). The sheet labeling/tc_expansion2_l1.csv should not be labeled.

**If this audit is run later** (optional; the rebuilt paper does not depend on it): estimands A*, q, r for each scorer and the disagreement-cell resolution rates, design-weighted by cell population; allocation 96/126/98/138 (minimax efficiency under the planning priors in scripts/fb_458_redesign.py, re-run if priors change), with model-proportional sub-stratification inside each cell; new seed and a new sheet; analysis with flipbudget.pv. Any such run must be preceded by its own written amendment fixing the seed and sheet before labeling.

---

## AMENDMENT 2 (2026-09-19): disagreement-targeted redesign, written before any label on the new sheet

Supersedes the allocation in Amendment 1. Reason and power analysis: REAUDIT.md sections 4, 5, 12. The existing audit shows error concentrated where the two live verifiers disagree (concordant cells: 1 error in 287 audited items). Human labels therefore go to disagreement rows.

- Sheet: labeling/audit_v2_l1.csv (457 rows; seed 20260919; scripts/fb_disagreement_sample.py). Provenance with inclusion probabilities: results/analysis/audit_v2_provenance.json.
- Strata: model x joint cell, unlabeled rows only. 358 disagreement rows (226 exact_match-only, 132 score_boxed-only), stratified SRS proportional to stratum size. 99 concordant rows (49 both-credited, 50 both-rejected), spread evenly over models.
- Label task unchanged (transcribe the committed final answer; NONE / CONTRADICTORY). Indeterminate = Y*=0 (primary); dropped (sensitivity).
- Estimands: per-model p10_m, p01_m (disagreement cells), pooled p11, p00; A*_m = sum_c s_c p_c; pairwise Delta*. Concordant-homogeneity check: per-model concordant error counts, reported as observed.
- Analysis: scripts/fb_joint_verifier.py extended to use the new labels with design weights (inclusion probabilities); Sidak joint 95% over estimated parameters; sampling combined by Sidak split. Primary outcome: number of the 136 orderings identified with sampling included.
- The labels must be typed by a person reading each response. The quality gate (timestamps, agreement signatures, transcription artifacts) applies.

---

## AMENDMENT 3 (2026-09-19): balanced design, written before any label on the sheet

Supersedes Amendment 2's allocation (358 disagreement + 100 concordant; that draw also had an accidental 457-row shortfall from a capacity cap, fixed). Reason (STRESS_TEST.md): the stress test showed every ordering the joint analysis resolves depends on concordant-cell homogeneity across models (0 resolved without pooling; 43 at 2x heterogeneity). Under homogeneity, disagreement-heavy designs resolve a median 95-97 vs 94-95 for this design; this design raises the median per-model probability of detecting a model with a 10% concordant error rate from 88% to 94% (worst model 65% to 77%). The audit therefore both resolves orderings and tests the assumption they rest on.

- Sheet: labeling/audit_v2_l1.csv, 458 rows (seed 20260919; scripts/fb_disagreement_sample.py): 229 disagreement rows (144 exact_match-only, 85 score_boxed-only), proportional by model x cell; 229 concordant rows (102 both-credited, 127 both-rejected), capacity-aware round-robin over model x cell (3-8 per stratum). Inclusion probabilities in results/analysis/audit_v2_provenance.json.
- Primary outcomes: (1) per-model concordant error counts (falsification check of homogeneity, reported as observed); (2) resolved orderings, homogeneous analysis; (3) the same under bounded heterogeneity L = 1, 2, 5 and without pooling.
- Coverage: per ordering >= 95%, audit 0.975 (Clopper-Pearson, Sidak over estimated parameters) + sampling 0.975, union bound; design weights = 1 / inclusion probability within stratum.
- Labels must be typed by a person reading each response; the quality gate applies.
