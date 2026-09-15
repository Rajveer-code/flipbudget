# Table 5: Scorer-comparison findings (exact_match vs. score_boxed)

| Quantity | Value |
|---|---|
| Full-population disagreement rate | 3.63% (817/22508) |
| Disagreement rate, exact 95% Clopper-Pearson CI | [3.39%, 3.88%] |
| Model-level disagreement range, full population | 0.60% (tiiuae/falcon-7b) -- 9.59% (01-ai/Yi-1.5-9B-Chat) |
| Directionality | Bidirectional; does not favor either scorer |
| Self-consistent pairing, exact_match accuracy + exact_match's own audited box | n/a -- pending human audit (analysis C) |
| Self-consistent pairing, exact_match accuracy + score_boxed's audited box (historical, mixed) | median ratio 6.095x, 100% dominant, n=120 |
| Self-consistent pairing, score_boxed accuracy + score_boxed's audited box | median ratio 5.735x, 100% dominant, n=120 |

Historical audits (T-C, 400+458 items) measured alpha,beta against score_boxed specifically. exact_match's own alpha,beta are unmeasured pending the 458-row human audit; do not substitute score_boxed's audited values as if they applied unchanged to exact_match (see METHODOLOGICAL_AUDIT.md).
