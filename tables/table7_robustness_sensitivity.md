# Table 7: Robustness / worst-case sensitivity

| Quantity | Value |
|---|---|
| score_boxed anchor alpha (global pooled, pre-shrinkage) | 3.14% |
| exact_match alpha, best case | 2.37% |
| exact_match alpha, worst case | 26.73% |
| exact_match beta, worst case | 1.44% |
| Worst-case median identified-set width | 0.1659 |
| Worst-case n valid / n unresolved | 10 / 10 |
| Established audit-estimation-only median (for comparison) | 0.2800 |
| Verdict B survives the worst case | True |

Honest caveat: in the worst case only 10 of 120 pairs remain valid at all, and every one of those 10 is fully unresolved -- the worst case narrows the comparison's scope even as its width stays favorable.
