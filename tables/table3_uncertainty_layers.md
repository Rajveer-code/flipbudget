# Table 3: Uncertainty-layer comparison

| Layer | Status | n valid pairs | n unresolved | Median width |
|---|---|---|---|---|
| Benchmark sampling | measured | 136 | 12 | 0.0431 |
| Audit-estimation-only (score_boxed) | measured | 120 | 91 | 0.2800 |
| Scorer-identification-only (score_boxed, Lambda=2) | measured | 66 | 15 | 0.0679 |
| Combined (score_boxed) | measured | 120 | 110 | 0.4521 |
| Scorer-choice (accuracy substitution) | measured | 120 | -- | 0.0091 |
| exact_match best-case (bound, Lambda=2) | worst/best-case bound, NOT measured | 105 | 25 | 0.0453 |
| exact_match worst-case (bound, Lambda=2) | worst/best-case bound, NOT measured | 10 | 10 | 0.1659 |

Audit-estimation-only is the dominant measured source. Both exact_match rows are a population-weighted worst/best-case bound (`fb_worst_case_sensitivity.py`), not a measured quantity -- exact_match's own audit is pending.
