# Claim ledger

Every quantitative claim in `manuscript/MANUSCRIPT_DRAFT.md`, traced:
manuscript sentence -> table/figure -> result JSON -> generating script -> raw data.
Built for the finalization-phase directive (2026-09-17). Every number below was
re-read directly from its JSON file during this pass, not copied from memory or
from an earlier draft of this ledger.

Status legend: **TRACED** = verified end to end this pass. **PENDING** =
depends on the 458 human labels, correctly marked `[PENDING]` in the
manuscript, not a number to trace.

| Claim | Exact value | Manuscript location | Table/Figure | Result JSON | Script | Raw data | Status |
|---|---|---|---|---|---|---|---|
| Headline dominance ratio (analysis A) | 6.10x (median 6.094641689747292) | Abstract; §7.1 table | Table 6 | `ea_dominance_canonical.json` (`ratio_median`) | `fb_ea_dominance_canonical.py` | `pair_identification_human.json`, `e4_mathhard_per_model.json` | TRACED |
| % dominant (analysis A) | 100.0% | Abstract; §7.1 | Table 6 | `ea_dominance_canonical.json` (`pct_dominant_among_valid`) | `fb_ea_dominance_canonical.py` | same | TRACED |
| Valid pairs / scored pairs | 120 / 136 | Abstract; §7.1 | Table 1, 6 | `ea_dominance_canonical.json` (`n_valid`, `pairs_scored`) | `fb_ea_dominance_canonical.py` | same | TRACED |
| Candidate pairs (base roster) | 378 (= C(28,2)) | §7.1 | Table 1 | `ea_dominance_canonical.json` (`total_candidate_pairs`, `n_unique_models_in_human_pair_list`=28) | `fb_ea_dominance_canonical.py` | `pair_identification_human.json` | TRACED |
| Minimum ratio across 120 valid pairs | 2.15x (2.153073768483647) | Abstract | Table 6 | `ea_dominance_canonical.json` (`ratio_min`) | `fb_ea_dominance_canonical.py` | same | TRACED |
| Self-consistency ratio (analysis B) | 5.74x (5.7345981282619345) | Abstract; §7.1 table | Table 5 | `scorer_choice_sensitivity.json` (`self_consistent_test.score_boxed_pairing.median_ratio`) | `fb_scorer_choice_sensitivity.py` | `scorer_accuracy_comparison.json`, `e4_mathhard_per_model.json` | TRACED |
| exact_match-pairing ratio (= analysis A, cross-check) | 6.10x (6.094641689747292) | Table 5 | Table 5 | `scorer_choice_sensitivity.json` (`self_consistent_test.exact_match_pairing.median_ratio`) | `fb_scorer_choice_sensitivity.py` | same | TRACED — identical to the A row above, confirming the two computations agree exactly, not just "closely" |
| Scorer-choice width, median | 0.0091 (0.009058698388721033) | §7.2; Figure 1, 4 | Table 3 | `scorer_choice_sensitivity.json` (`scorer_choice_width.median`) | `fb_scorer_choice_sensitivity.py` | same | TRACED |
| Full-population scorer disagreement | 3.63% (817/22508 = 3.6298...%) | Abstract; §7.4 | Table 5 | `tc_expansion_population.json` (`n_disagree`, `n_rows`) | `fb_tc_expansion_population.py` | raw `population` array, 22,508 rows, direct harness re-scoring | TRACED |
| Disagreement 95% CI | [3.39%, 3.88%] | Abstract; §7.4 | Table 5 | computed in `fb_build_tables.py::clopper_pearson(817,22508)` | `fb_build_tables.py` | `tc_expansion_population.json` | TRACED — exact Clopper-Pearson, re-derived in-script, not hand-typed |
| Model-level disagreement range | 0.60%-9.59% | §7.4 (via METHODOLOGICAL_AUDIT.md) | Table 5 | computed in `fb_build_tables.py::_per_model_disagreement_range` | `fb_build_tables.py` | `tc_expansion_population.json` (`disagree` field per row) | TRACED — this exact computation caught and fixed a wrong first-attempt (69%-100%, wrong field compared) earlier this session; current version uses the authoritative `disagree` boolean |
| Worst-case alpha bound | [2.37-2.38%, 26.73%] | §7.4 | Table 7; Figure 5 | `worst_case_sensitivity.json` (`bounds.exact_match_alpha_best/_worst`) | `fb_worst_case_sensitivity.py` | `tc_alpha_beta_update.json` (`global_anchor_old`), `CELL_POPULATION` in `fb_tc_expansion2_analysis.py` | TRACED |
| Worst-case beta bound | [0%, 1.44%] | §7.4 | Table 7 | `worst_case_sensitivity.json` (`bounds.exact_match_beta_worst`) | `fb_worst_case_sensitivity.py` | same | TRACED |
| Worst-case median width | 0.166 (0.1659...) | §7.4 | Table 7; Figure 5 | `worst_case_sensitivity.json` (`worst_case.median_width`) | `fb_worst_case_sensitivity.py` | `scorer_accuracy_comparison.json`, `pair_identification_human.json` | TRACED |
| Worst-case n valid / unresolved | 10 / 10 | §7.4 | Table 7 | `worst_case_sensitivity.json` (`worst_case.n_valid`, `n_unresolved`) | `fb_worst_case_sensitivity.py` | same | TRACED |
| Four-layer widths: sampling | 0.0431 (0.04307...), n=136, 12 unresolved | §7.2 | Table 3; Figure 1 | `reconciliation_four_layers_corrected.json` (`layer_stats.w_sampling`) | `fb_reconcile_layers.py` | `ea_dominance_canonical.json` inputs | TRACED |
| Four-layer widths: audit-estimation-only | 0.2800 (0.28000766...), n=120, 91 unresolved | §7.2 | Table 3; Figure 1, 5 | `reconciliation_four_layers_corrected.json` (`layer_stats.w_audit_only`) | `fb_reconcile_layers.py` | same | TRACED — this is the "established audit-estimation median" the worst-case bound (0.166) is compared against |
| Four-layer widths: scorer-identification-only | 0.0679 (0.06787...), n=66, 15 unresolved | §7.2 | Table 3; Figure 1 | `reconciliation_four_layers_corrected.json` (`layer_stats.w_scorer_only`) | `fb_reconcile_layers.py` | same | TRACED |
| Four-layer widths: combined | 0.4521 (0.45214...), n=120, 110 unresolved | (Table 3 only, not narrated in main text) | Table 3 | `reconciliation_four_layers_corrected.json` (`layer_stats.w_combined`) | `fb_reconcile_layers.py` | same | TRACED |
| Audit-design: naive Neyman stall | 74% unresolved at 16x budget | §5 | Table 4; Figure 2 | `audit_design_optimization.json` (`curves.neyman[-1]`) | `fb_audit_design_optimization.py` | `e4_mathhard_per_model.json` | TRACED — re-verified after this pass's performance fix (byte-identical output before/after, see commit `cda1b93`) |
| Audit-design: proportional at 16x | 22% unresolved | §5 | Table 4; Figure 2 | `audit_design_optimization.json` (`curves.proportional[-1]`) | `fb_audit_design_optimization.py` | same | TRACED |
| Audit-design: greedy at 4x | 40% unresolved | §5 | Table 4; Figure 2 | `audit_design_optimization.json` (`greedy_at_4x`) | `fb_audit_design_optimization.py` | same | TRACED |
| 15 of 17 models, zero false-credit events | 15/17 | §5 | (narrated, not tabulated separately) | `e4_mathhard_per_model.json` (`alpha_raw`/`n_credited` per model) | `fb_e4_mathhard.py` (source), inspected directly | `mathhard_labelling_key.json` + `mathhard_l1.csv` | TRACED |
| HT-pooling bias demonstration | +444% relative bias | §5 (via METHODOLOGICAL_AUDIT.md) | (supplementary, S2) | `tests/test_tc_expansion2_estimator.py` (regression test) | `fb_tc_expansion2_analysis.py::_ht_pool` | synthetic scenario, documented in the test itself | TRACED — a demonstrated worst-case on constructed inputs, not a real-data measurement; described as such everywhere it's cited |
| Original human audit size | 400 submitted, 350 usable (162 credited + 188 wrong), 27 models | §6 (2026-09-17 revision) | Table 1 | `e4_mathhard_per_model.json` (summed `n_used_credited`/`n_used_wrong`/`n_total_audited` across all models) | `fb_e4_mathhard.py` | `mathhard_labelling_key.json` (400 items), `mathhard_l1.csv` | TRACED |
| T-C round size | 69 usable (of 70 L1 rows), 0/69 scorer-wrong | §6 | (narrated) | `tc_real_analysis.json` (`l1_n_usable`, `l1_n_scorer_wrong`) | `fb_tc_real_analysis.py` | `labeling/tc_expansion_l1_completed.csv` | TRACED |
| T-C-round pooling shift (not yet merged) | anchor 0.0314 -> 0.0216, 17 -> 25 qualifying | §6 Limitations item 7 | (narrated) | `tc_alpha_beta_update.json` (`global_anchor_old/new`, `n_qualifying_old/new`) | `fb_tc_alpha_beta_update.py` | same as above + `mathhard_l1.csv` | TRACED |
| Eligible T-C-expansion population | 22,508 rows; 320 already-labeled excluded; 22,188 eligible | §6; Table 1 | Table 1 | `tc_expansion_population.json` (`n_rows`, `n_already_labeled`) | `fb_tc_expansion_population.py` | raw per-item harness re-scoring | TRACED |
| T-C-expansion2 sample design | 458 = 200+198+30+30 | §6 | Table 1 | `tc_expansion2_provenance.json` (row counts per cell) | `fb_tc_expansion_sample.py` | `tc_expansion_population.json` | TRACED |
| HF math-verify postmortem numbers (Qwen "more than doubled," DeepSeek "nearly tripled") | qualitative, not a number this project computed | §2 Related Work | (external citation, not a project result) | n/a — external source | n/a | `https://huggingface.co/blog/math_verify_leaderboard` (fetched and read directly this session) | TRACED to source, external to this project's own pipeline |
| `exact_match`'s own audited alpha, beta | — | §7.1 (analysis C), §7.4 | Table 3, 5, 6 (rows marked PENDING) | n/a | `fb_tc_expansion2_analysis.py` (ready, untriggered) | `labeling/tc_expansion2_l1.csv` (458 real labels, not yet collected) | **PENDING — human audit** |
| Analysis C ratio / % dominant | — | §7.1 | Table 6 | n/a | same | same | **PENDING** |
| Fully self-consistent `exact_match` four-layer decomposition | — | §7.2 (implied) | Table 3 (rows not present) | n/a | same | same | **PENDING** |

## Method

Every "TRACED" row was produced by opening the cited JSON this pass (`python -c "import json; ..."`)
and reading the field directly, or by re-running the cited script and diffing its
output against the committed file. No number above was carried forward from an
earlier summary without re-reading its source.

## Outcome

No claim in the manuscript failed to trace. No number required removal or
qualification beyond what the manuscript already states (the `[PENDING]`
markers). The two real defects found this pass were in **citations**, not
in numerical claims — see the reference-audit section of `NOVELTY_AUDIT.md`
and commit `c9d711e`.
