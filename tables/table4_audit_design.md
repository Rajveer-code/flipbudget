# Table 4: Audit-design / allocation results

Current budget: 289 labels. % of 120 valid pairs still unresolved (audit-only layer) at each additional-budget multiple:

| Budget multiple | Proportional | Naive Neyman (plug-in) | Pooled-estimate Neyman |
|---|---|---|---|
| 0x | 75.8% | 75.8% | 75.8% |
| 1x | 60.0% | 74.2% | 61.7% |
| 2x | 53.3% | 74.2% | 54.2% |
| 4x | 47.5% | 74.2% | 45.8% |
| 8x | 35.0% | 74.2% | 36.7% |
| 16x | 21.7% | 74.2% | 30.8% |

Greedy search on the actual discrete objective, 4x budget only: 40.0% unresolved -- best of all tested strategies.

Naive Neyman stalls because 15 of 17 qualifying models have zero observed false-credit events; it concentrates budget on the one noisy nonzero cell instead of spreading it.
