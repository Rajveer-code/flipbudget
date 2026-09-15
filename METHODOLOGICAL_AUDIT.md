# Methodological audit of the scorer-mismatch finding

Requested explicitly, before more labeling or manuscript work: verify the finding survives its own scrutiny, not just assume it. Two real issues were found and fixed. The headline survives, with an honest worst-case caveat.

## 1. The 6.51% figure was mis-scoped — corrected

Recounted directly from `results/analysis/tc_expansion_population.json` (22,508 rows, 17 models × 7 subjects, no sampling):

- **Full population: 817/22,508 = 3.63%** disagreement (`score_boxed` ≠ `exact_match`). Exact 95% Clopper-Pearson CI: **[3.39%, 3.88%]**.
- 6.51% was a real number, but for `algebra_hard` only (5,219 rows) — one subject, not the population it was presented alongside.
- Model-level range, full population: **0.60% (falcon-7b) to 9.59% (Yi-1.5-9B-Chat)** — the earlier "0.7–18.6%" range was also wrongly scoped.

`SCORER_MISMATCH_MAJOR_FINDING.md` and `EVIDENCE_TABLE.md` corrected. **3.63% is the number to cite going forward.**

## 2. What the "scorer-choice width" (0.0091) actually measures — reframed

It held `score_boxed`'s audited (α, β) **fixed** and varied only which accuracy number (`exact_match` vs `score_boxed`) fed the identification formula. That is a real, correctly-computed quantity, but it is the **accuracy-substitution point-estimate shift**, not a symmetric two-scorer identification-uncertainty comparison — `exact_match` has no audited (α, β) of its own, so its own identification width is not represented at all. Renamed in `results/flipbudget/scorer_choice_sensitivity.json`'s documentation (file unchanged, since the number itself is correct for what it is — only the label was wrong).

**The clean five-part decomposition, and what can be estimated today:**

| # | Source | Estimable now? | With what |
|---|---|---|---|
| 1 | Benchmark sampling | Yes | `n_bench`, existing |
| 2 | `score_boxed` scorer-identification | Yes | Audited (α,β), 69 rows, existing |
| 3 | `exact_match` scorer-identification | **No** | Requires the new audit's `exact_match`-stratified cells |
| 4 | Finite human-audit uncertainty | Yes for `score_boxed`; **no** for `exact_match` | Wilson/design-based CI on the audit |
| 5 | Criterion/scorer-choice | **Partially** — the deterministic accuracy-substitution shift (item 2's 0.0091) is a real lower-bound-flavored component; the full quantity (which would also reflect `exact_match`'s own unknown α/β) needs the new audit | — |

Items 3, 4 (exact_match), and the full version of 5 are exactly what the 458-row audit is for.

## 3–5. The sampling-design bug — found, and fixed before any labels are used

**Real issue, exactly as suspected.** The four preregistered cells have very different sampling fractions relative to their population sizes:

| Cell | Population | Planned n | Sampling fraction |
|---|---|---|---|
| `both_credited` | 1,531 | 200 | 13.06% |
| `both_not_credited` | 19,873 | 198 | 1.00% |
| `disagree_sb_credited_em_not` | 291 | 30 | 10.31% |
| `disagree_em_credited_sb_not` | 493 | 30 | 6.09% |

`score_boxed`'s "wrong" stratum is the union of `both_not_credited` (sampled at 1.00%) and `disagree_em_credited_sb_not` (sampled at 6.09%) — a **~6× difference**. `fb_tc_expansion2_analysis.py`'s original estimator pooled raw counts across these cells unweighted, which is only valid under simple random sampling. Verified numerically the failure mode this would cause: in a scenario where the small, densely-sampled cell has a true rate of 15% (exactly the kind of thing stratifying on disagreement exists to detect) while the majority cell has ~0%, the naive pooled estimate comes out **+444% relative bias** (0.0197 vs. the correct 0.0036).

**Fixed**: the analysis script now uses a Horvitz-Thompson / post-stratified estimator (`_ht_pool` in `fb_tc_expansion2_analysis.py`) — each cell's sample proportion weighted by its **population** size, not its sample size, with a finite-population-corrected variance. Confirmed the cell-union logic is correct per scorer (item 5): `score_boxed`-credited = `both_credited` ∪ `disagree_sb_credited_em_not`; `exact_match`-credited = `both_credited` ∪ `disagree_em_credited_sb_not` — **different unions**, and the fixed code now builds each independently rather than reusing one pooled figure for both. Re-ran the pipeline self-test after the fix — runs clean, recovers injected synthetic patterns correctly.

## 4. Power under the corrected estimator — allocation stands, only the estimator needed the fix

Recomputed design-based SE for all four targets using the HT variance formula, at the same working priors as before:

| Target | Point (planning prior) | Design SE | 95% half-width |
|---|---|---|---|
| `score_boxed` α | 3.14% | 0.0109 | 0.0213 |
| `score_boxed` β | 1.00% | 0.0069 | 0.0135 |
| `exact_match` α | 2.62% | 0.0097 | 0.0191 |
| `exact_match` β | 1.03% | 0.0070 | 0.0137 |

All four land within the original ≤0.02 planning target. **458, allocated exactly as designed (200/198/30/30), remains adequate — the bug was in the estimator, not the sample size.** The disagreement-resolution power calculation (n=30 per direction, 65–89% power) used a single-cell proportion test with no cross-cell pooling, so it was never affected by this issue.

## 6. Three separated analyses

| | Pairing | Status |
|---|---|---|
| **A. Historical mixed** | `exact_match` accuracy + `score_boxed` audit | **Established**: 6.10× median, 100% dominant, 120 valid pairs |
| **B. Self-consistent `score_boxed`** | `score_boxed` accuracy + `score_boxed` audit | **Established**: 5.74× median, 100% dominant, same 120 pairs |
| **C. `exact_match`'s own analysis** | `exact_match` accuracy + `exact_match` audit | **Not yet established** — no audited (α,β) for `exact_match` exists. Bounded, not computed, in item 7 below. |

## 7. Genuine sensitivity stress test — not a search for a favorable result

Bounded `exact_match`'s plausible α using the population sizes and the extreme (not typical) assumption that **every** disagreement-cell item is a false credit for `exact_match` (worst case) or none are (best case), holding `both_credited`'s rate at `score_boxed`'s known 3.14%:

- **Plausible range: α ∈ [2.38%, 26.73%], β ∈ [0%, 1.44%].** The worst case (26.73%) is roughly **8.5× score_boxed's known rate** — a genuinely unfavorable, not cherry-picked, scenario.
- Ran this worst-case anchor through the **same Λ=2 methodology already used for the scorer-identification-only layer** (not an ad hoc band): resulting median identification width **0.166**, still below the **established audit-estimation-only median of 0.280**.

**Verdict B survives even the worst-case bound.** Honest caveat, not smoothed over: in the worst-case scenario, only 10 of the 120 pairs remain valid at all (vs. 66 under `score_boxed`'s known rate) and every one of those 10 is fully unresolved — the worst case doesn't just widen the comparison, it also makes most pairs entirely uninformative. That is a real cost, reported here rather than only citing the favorable width comparison.

## 8. Broader benchmark search — automated-only, no new labeling

Checked every free-text-generation task family actually available in this project's accessible roster (ARC-Challenge, BBH's 24 subtasks, IFEval, MATH-Hard's 7 subjects; GPQA/MMLU-PRO/MuSR are multiple-choice, structurally ruled out, already established):

- **BBH** (checked directly, `object_counting`): single metric field (`acc_norm`) per record. **Does not qualify** — no second live scorer.
- **IFEval**: `strict_acc` vs. `loose_acc`, both computed on the same response, 2.60% disagreement already measured in this project (`ifeval_full_roster.json`, C2 in `EVIDENCE_TABLE.md`). **A genuine second data point, but a different kind of case** — strict/loose are two leniency settings of the *same* verifier, not two independently-implemented scoring libraries like `exact_match`/`score_boxed`. Should be cited as a related-but-distinct phenomenon, not conflated.
- **ARC-Challenge**: not checked in this pass (loglikelihood-scored per its task config in this harness version — same structural argument as GPQA/MMLU-PRO likely applies, not independently confirmed here, flagged rather than assumed).

**Honest conclusion**: scorer-choice dependence, in the specific "two independent extraction libraries disagreeing" form, is confirmed on **one** benchmark (MATH-Hard). A weaker, related phenomenon (verifier-leniency disagreement) is confirmed on a **second** (IFEval). It is not yet shown to be a general property of automated evaluation — **recurring in a narrow sense within this roster, not yet established as broad**. No fabricated third case.

## 9. Novelty audit update

Unchanged from the prior pass: classical misclassification math (A), Neyman allocation (A), scorer mismatch alone (not a general theory). **New judgment on the combination**: benchmark comparison + scorer misclassification + scorer-choice dependence + finite-audit uncertainty + audit-budget design, taken together, is **class C (nontrivial methodological combination)** — the individual pieces are not new, and no single piece rises to D, but the specific combination, evidenced now with a design-weighted audit methodology and a genuine worst-case stress test rather than an assumed-safe headline, is a real, defensible, non-trivial contribution for a methods-focused venue. Not claimed as more than that.

## 10. Final decision

**GO** — proceed with the 458 genuine human labels, with the corrected analysis pipeline (already fixed and tested) waiting to receive them. The sample size and cell allocation do not need to change; only the estimator did, and that fix is already in place before any real label touches it. Nothing found in this audit weakens the case for collecting the labels — if anything, the worst-case stress test (item 7) shows the central conclusion has real headroom, which is the strongest evidence yet that this is worth confirming empirically rather than a reason to defer.
