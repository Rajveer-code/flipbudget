# Table 8: Negative controls

## Single-model ratio scenarios

| Scenario | a_hat | n_bench | audit n (credited/wrong) | w_sampling | w_identification | ratio |
|---|---|---|---|---|---|---|
| perfect_scorer_realistic_audit_n | 0.500 | 1000 | 11/11 | 0.0620 | 0.3492 | 5.635x |
| perfect_scorer_large_audit | 0.500 | 1000 | 2000/2000 | 0.0620 | 0.0019 | 0.031x |
| high_accuracy_scorer_modest_audit | 0.600 | 1000 | 100/100 | 0.0607 | 0.0559 | 0.920x |
| audit_sized_to_own_required_n | 0.500 | 1000 | 415/415 | 0.0620 | 0.0371 | 0.599x |

## Null-effect (identical-model) pairwise scenarios

| Scenario | a1 | a2 | Sampling interval contains 0 | Identification interval contains 0 |
|---|---|---|---|---|
| null_true_effect_identical_models | 0.500 | 0.500 | True | True |

Purpose: confirm the ratio-based dominance claim isn't an artifact by constructing scenarios (e.g. a perfect scorer with only n=11 audit trials) where a large ratio is expected for reasons unrelated to the real data's scorer-error structure -- the small-n audit inflates the ratio here too, which is exactly the D-class caveat this project already carries (NEGATIVE_CONTROLS.md).
