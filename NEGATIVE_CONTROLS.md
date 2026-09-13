# Negative controls (item 11)

Script: `scripts/fb_negative_controls.py`. Output: `results/flipbudget/negative_controls.json`. Uses the same imported `bounded_single_model_extrema`/`bounded_comparison`/`wilson_ci` as the real pipeline — no separate, looser implementation that could pass by construction.

## Result: the method is falsifiable, not structurally biased toward "more uncertainty"

| Scenario | Audit n (each stratum) | Ratio (W_id / W_sampling) | Verdict |
|---|---|---|---|
| Perfect scorer, audit sized like the real median (n=11) | 11 | **5.635** | still dominant |
| Perfect scorer, large audit | 2000 | **0.031** | stable |
| High-accuracy scorer (1% error), modest audit | 100 | **0.920** | stable |
| Audit sized to this project's own required-n target (`AUDIT_DESIGN_ANALYSIS.md` Q1, ~415) | 415 | **0.599** | stable |
| Null true effect (two identical models) | 11 | interval `[-0.349, 0.349]`, contains zero in both layers | correctly recovered as null |

Three of five constructed scenarios show ratio **below 1** (stable) once the audit sample is genuinely adequate or the scorer genuinely accurate — the framework does not unconditionally report dominance regardless of input. The null-effect scenario confirms two identical models are correctly recovered as statistically indistinguishable in both the sampling and identification layers, not inflated into a manufactured gap.

## The connection this surfaces to the audit-design result

Scenario 1 is the important one: **even a perfect scorer (0 observed errors) still shows 5.6× dominance at the real project's median audit size (n=11).** The real MATH-Hard roster's dominance finding is therefore not primarily a statement about scorer error being large — it is a statement about audit samples this small being unable to rule out scorer error, however small it might truly be. Scenario 4 closes the loop: auditing at exactly this project's own derived required-n (~415, from `AUDIT_DESIGN_ANALYSIS.md`) drops the ratio to 0.599 — genuinely stable. **The audit-design recommendation is not an arbitrary add-on; it is the specific fix that would flip the headline finding from "dominant" to "stable" on data of this kind**, which is the strongest form of validation the audit-design contribution could have.
