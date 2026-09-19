# Final stress test of the two-verifier thesis (2026-09-19)

Scripts:
- `scripts/fb_joint_verifier.py` → `results/flipbudget/joint_verifier_results.json`
- `scripts/fb_reaudit.py` → `reaudit_results.json`
- `scripts/fb_disagreement_sample.py` → new sheet

Every value below comes from those files. Paper numbers are macros generated
from the same files.

**Bottom line.** The 84 resolved orderings survive exact-coverage
recomputation, but they depend entirely on concordant-cell homogeneity across
models:
- 62 resolved if each model's concordant error may sit anywhere in the pooled
  bound (L=1);
- 43 at 2×;
- 7 at 5×;
- 0 with no pooling;
- about 27,200 labels to reach 84 without the assumption.

My earlier "64 under 5×" was a bug: it widened one shared box instead of
letting models vary independently. The paper, its title and its 458-row design
were changed to put the assumption at the center.

| # | Item | Finding | Action |
|---|---|---|---|
| 1 | 457 vs 458 | One concordant stratum (gpt-j-6b, both-credited) had 3 unlabeled rows but was assigned 4 by round-robin; the cap dropped the row instead of reassigning it. Accidental. | Capacity-aware allocation; sheet redrawn at 458 (then redesigned, #16). |
| 2 | 84/118 recomputed | 136 pairs; sampling-only 118 at the paper's coverage split; homogeneous joint design 84 (audit-only 101); simultaneous over all orderings 76 of 103. Unchanged after switching to exact intervals. | Numbers regenerated. |
| 3 | Pooling stress | Resolved count vs L (independent per-model concordant rates within L × pooled bound): 1→62, 1.5→55, 2→43, 3→26, 5→7, ≥10→0. No pooling→0. | Figure E is now the paper's central figure; the manuscript leads with the dependence, not with 84. |
| 4 | Concordant evidence | Recounted from raw audit: 11 cell 141/142 correct, 00 cell 0/145, 10 cell 16/32, 01 cell 0/1. Concordant error 1/287; exact 95% upper bound 1.9% (3.9% and 2.5% by cell). Per model: 0–37 items per concordant cell. | Worded as a low observed rate with a finite-sample bound; the paper states that it cannot establish homogeneity. |
| 5 | Is disagreement targeting optimal? | Simulated at 458 extra labels, homogeneous analysis, three truth scenarios, 200 replicates. Median resolved: uniform 88, one-verifier 89–90, concordant-only 89, balanced 94–95, 358+100 95–97, all-disagreement 95–97 (proportional or width-minimizing). Disagreement-heavy designs are tied and none is provably optimal. Falsification power for a model with 10% concordant error (median / worst model): all-disagreement 77/47%, 358+100 88/65%, balanced 94/77%, concordant-only 99/97%. | The paper does not call any design optimal. |
| 6 | The 458 simulation | 200 replicates per design and scenario. Binomial draws within strata (a mild approximation to sampling without replacement). Truths: concordant rates from the audit posterior; p10 from the pooled posterior, p01 uniform; or fixed 0.5/0.5 and 0.9/0.1. It conditions on the existing audit and adds new labels. **Leakage:** truths come from the same audit that motivated the design. | Labeled "Projected, not observed" in the figure caption and text; the leakage is disclosed in the text and Limitations. |
| 7 | "110 of 118" | Holds only if disagreement rates equal the pooled value exactly. 9 sampling-permitted orderings fail because correcting disagreement mass shrinks the gap below sampling error (5 involve command-r); one other ordering gains. Net 110. | Appendix C explains this; the projection is described as illustrative. |
| 8 | 8 reversals | Recomputed: 8/136; 7 significant under both verifiers (6 involving command-r, plus Yi-9B vs zephyr); Yi-9B vs Qwen2-7B is significant under exact_match only. Audited score_boxed-only responses correct: command-r 2/6, Yi-9B 1/9 (8 without a committed answer), zephyr 2/2, Qwen2-7B 2/2. In each reversal the small audit evidence favours exact_match's order. | Table 1 in the paper (generated). |
| 9 | Common mechanism | LR 24.8, p=0.010; command-r contributes 15.3. Leave-one-out, 500 bootstrap reps each: drop command-r → p=0.42; drop any other model → p 0.002–0.026. | Appendix diagnostic only. |
| 10 | What the audit measures | Confirmed in code: the human transcribes the committed answer; `normalize_final_answer` + `is_equiv` compare it with the reference; the verifiers use the same routine. Extraction is validated; shared equivalence errors are not identified. | Manuscript contains no "judgment"/"human correctness" wording (grep 0). |
| 11 | Coverage logic | Wilson (approximate) replaced by Clopper–Pearson (guaranteed). The product-of-levels split (assumes independence) replaced by a Bonferroni 0.975 + 0.975 union bound. Šidák only within the audit, over independent samples. Coverage stated per ordering, plus a simultaneous variant; conditional on the stated assumption. Single-verifier result recomputed the same way: 0. | Appendix B gives the derivation. |
| 12 | Prior art | Table in appendix H: estimand, human sampling, ranking, two verifiers, allocation. No novelty claimed for the estimators. | Done. |
| 13 | Title | "Certifying" was not supported, because the count rests on an untested assumption. | New title: *What Can a Small Human Audit Establish About a Leaderboard Ranking? Two Verifiers and the Assumption That Does the Work*. "Resolve" is defined in the introduction. |
| 14 | Why care | (a) The standard one-verifier, per-model audit resolves 0 orderings. (b) Two verifiers already in the harness concentrate the observed errors in 3.6% of responses. (c) A small audit then supports a ranking only through a cross-model homogeneity assumption worth about 27,000 labels, which the paper makes explicit and quantifies. It is not a benchmark-specific trick: the analysis (joint-cell identity, bounded-heterogeneity sensitivity, falsification-aware design) applies to any pair of verifiers. The magnitudes are benchmark-specific. | Stated in the introduction and conclusion. |
| 15 | Second benchmark | No second benchmark with two independent live verifiers and an existing human audit was found. None invented. The paper is framed as a single-benchmark methodological case study, stated as a limitation. | Stays in Limitations. |
| 16 | 458 decision | **MODIFY → GO on the balanced design.** 229 disagreement + 229 concordant, 458 rows, blinded, no blanks or duplicates, provenance with inclusion probabilities, Amendment 3. | Ready. Labels must be human-typed. |
| 17 | Final steps | Full pipeline, PDF check, package, commit. | See FINAL_STATUS.md. |
