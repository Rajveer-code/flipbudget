# Gap audit: what stands between this paper and top-tier (2026-09-19)

Fresh hostile read of `manuscript/latex/` + code. Earlier audits
(`FINAL_STATUS.md`, `FINAL_VENUE_DECISION.md`, `REVIEWER_ATTACK_FINAL.md`)
mark every bar except the 458 labels as met. This pass disagrees: it found
problems those passes missed. Ranked by severity.

## BLOCKER 1: the estimand is mis-parameterized (verified)

- Paper §3 defines α = P(Ŷ=1 | Y*=0) and β = P(Ŷ=0 | Y*=1) (sensitivity/specificity
  scale) and uses g = (a−α)/(1−α−β).
- The audit samples **on the scorer's output** (credited / wrong strata). So
  `alpha_raw` = false credits / credited-audited = **P(Y*=0 | Ŷ=1)**, which is a
  predictive value, not α. Same for β. (`scripts/fb_e4_mathhard.py:per_model_rates`,
  `scripts/ea_dominance_study.py:build_model_table`, `src/flipbudget/identification.py:g`.)
- With predictive values q, r, the correct identity is **linear**:
  A* = a(1−q) + (1−a)r. It can never be empty and never straddles.
- `scripts/fb_pv_param_check.py` output:
  - current map: 120 valid, 16 empty, median ratio 6.095, min 2.153 (reproduces the paper)
  - correct map: 136 valid, 0 empty, median 18.884, min 7.904, 100% > 1
- **What follows:** the direction of the headline holds (it gets stronger).
  Every number derived from g has to be recomputed: 6.10×, 5.74×, 120/136, the
  0.280/0.068/0.452 widths, the 16–70 empty-set pairs, the worst-case 0.166, the
  audit-design curves, and flip-budget d*. Several "results" are **artifacts of
  the wrong map** and must be removed or re-derived: the empty-set "subtlety" (§3),
  the straddle/divergence case in T-A, the linear-fractional vertex argument in T-H,
  and whatever T-B / ranking-preservation rely on.
- A statistics reviewer who knows PPV vs sensitivity will catch this. Nothing
  else on this list matters until it is fixed.

## BLOCKER 2: close prior work is missing (verified via search)

The paper cites 14 references. None of the prediction-powered-inference line
or the Rogan–Gladen line is among them:

| Work | Overlap |
|---|---|
| Lee et al., "How to Correctly Report LLM-as-a-Judge Evaluations", arXiv 2511.21140, **ICML 2026** | Bias-corrected accuracy from judge sens/spec on a human calibration set, CIs covering test + calibration uncertainty, **adaptive calibration-sample allocation**. Close to contributions 1–3. |
| Fisch et al., Stratified PPI, NeurIPS 2024 | Stratified human + auto-labeler evaluation of LMs, with allocation across strata. Overlaps contribution 3. |
| Chatzi et al., Prediction-Powered Ranking of LLMs, NeurIPS 2024 | Rankings with valid uncertainty from a small human set plus automated judgments. |
| Boyeau et al., AutoEval Done Right, ICML 2025 | PPI for model evaluation. |
| Angelopoulos et al., PPI, Science 2023; Zrnic & Candès, Active Statistical Inference, ICML 2024 | Base framework; label allocation. |
| Rogan & Gladen 1978; Lang & Reiczigel 2014 | g(·) is the Rogan–Gladen estimator; CIs adjusted for estimated Se/Sp already exist. |

Novelty has to be rebuilt around what these do not cover: partial identification
under **differential, model-specific** scorer error (they assume one
judge-level Se/Sp); pairwise **ranking** identification; and a design
objective based on the number of resolved pairs rather than MSE. Lee et al. and
StratPPI are also the baselines to compare against.

Also missing: MATH (Hendrycks 2021), Minerva normalization (Lewkowycz 2022),
Open LLM Leaderboard v2, lm-eval-harness (Biderman 2024), Northcutt 2021
(test-label errors), Miller 2024 (error bars on evals). A realistic target is
30 or more references.

## MAJOR (existing data is enough; no new labels needed)

1. **The headline is mostly a statement about audit size.** Per-model audits
   are 1–42 items per stratum (falcon-7b: 0/1 credited, 0/3 wrong). In the
   whole audit there are 5 false credits (4 of them in command-r) and 0 false
   misses. Needed:
   (a) a closed-form or plotted crossover audit size, n* ∝ √(n_test), past which
   sampling uncertainty dominates;
   (b) pooled (non-differential) vs partially pooled vs per-model results.
   Under common error rates, rankings never flip, so every unresolved pair comes
   from allowing differential error;
   (c) a heterogeneity test (Fisher exact on false credits by model). command-r's
   4/6 is likely significant. That becomes the real story: error is rare but
   **differential by output format**.
2. **Construct.** A human "label" is a transcribed final answer. Correctness is
   then decided by `normalize_final_answer` + `is_equiv` against gold, so the
   reference shares the equivalence checker. The audit measures **extraction
   error only**. Known `is_equiv` blind spots (Limitation 3) are invisible by
   construction. Limitation 9 ("a human reader determines correctness")
   misdescribes the procedure. Either say this plainly or have humans judge
   equivalence directly on flagged items.
3. **Coverage (R1.1) is disclosed but not fixed.** Use a projection confidence
   set: a joint (1−γ) region for all (q, r) plus the sampling of a, projected
   through the (now linear) map. That gives valid, conservative coverage by
   construction.
4. **Audit-design claim.** Plug-in Neyman with zero-event pilots is a known
   degenerate case (strawman risk). Compare against Neyman with a pseudo-count
   or floor, the Lee et al. adaptive allocation, and StratPPI. Report Monte Carlo
   over posterior draws of the true rates, not a deterministic projection, and
   call it a simulation rather than "empirical".
5. **Worst-case paragraph is spin.** "Verdict B survives" when 110/120 pairs
   become unidentifiable. Reframe: the bound is uninformative, and that is why
   the exact_match audit is needed.
6. **Numbers that disagree within the paper:**
   - abstract 6.10× vs Table 4 6.09× (raw value 6.095);
   - §7.2 orders layers as "0.043 < 0.068 < 0.009", which is false;
   - Fig 1 caption says "~4× sampling" but 0.280/0.043 ≈ 6.5×;
   - "qualifying" means 27 in Table 1 but 17 in the abstract and §6;
   - the "decomposition" compares medians over different pair sets (136/66/120)
     and the widths are not additive, so call it a comparison and use a common
     pair set.

## MAJOR (writing and presentation)

- The prose reads like a lab notebook: "found and fixed during this project's
  development", "a second, real bug", "honestly", "(limited, not fabricated)",
  "Verdict B", "T-C round", "class A/B/C" ×4, and a pointer to
  `VENUE_AND_OVERLAP_AUDIT.md`. Present the methodological points (HT pooling,
  why clipping fails) as methods and drop the development narrative. Remove the
  Windows-bug and performance-bug mentions.
- "Three AI-generated substitutions" (§6). In a sole-author paper where the
  author is labeler L1, this invites the question "from whom?". No result uses
  them. Replace it with a standard annotator-QA sentence; the provenance stays
  in the repo. (Author's call.)
- There is no page-1 teaser figure. Suggested: a leaderboard showing point
  estimates next to identified intervals.
- The roster is dated (Falcon, MPT, GPT-J; the OLL v2 snapshot), with no current
  reasoning models. Name this as a limitation, or extend.

## Generalization (single benchmark; R2.2)

A route that needs no new labeling: VerifyBench and CompassVerifier's
VerifierBench (already cited) ship human correctness labels for
(response, reference) pairs. Use them to audit exact_match, math-verify and
score_boxed on more datasets. Check licenses and schemas first.

## Still blocked: the 458 human labels

Only a human reading the responses unblocks analysis C. The practical path is
the author labeling the sheet over 2–3 sessions (the instructions are already
written), plus one peer on a ~20% overlap for agreement. The quality gate
rejects machine-produced files, and a machine-produced file that passed it
would be fabricated data.

## Suggested order

1. Fix the parameterization in `src/` and `scripts/`, with a regression test.
   Rerun `fb_reproduce_all.py`, then rewrite every affected number and theory item.
2. Related work plus a novelty rebuild against Lee et al. and StratPPI (plus
   an empirical baseline comparison).
3. MAJOR items 1–6 above (all use existing data).
4. Writing pass (manuscript-flow), teaser figure, anonymization.
5. The 458 labels, whenever they are genuinely done, then `fb_final_evidence_update.py`.
6. Optional: VerifyBench generalization.

Venue: a workshop in parallel is still the safe move. Do not submit to archival
E&D until step 1 is done.
