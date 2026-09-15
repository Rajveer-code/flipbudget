"""Figure 5: worst-case sensitivity. Extends fig1's four established layers
with the two exact_match-conditional bars from
scripts/fb_worst_case_sensitivity.py -- visually separated (hatched, marked
"NOT MEASURED -- bound") from the established score_boxed-anchored layers,
so the figure cannot be misread as claiming exact_match's own audit exists.

Run: python scripts/fb_fig5_worst_case_sensitivity.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 11,
                      "axes.spines.top": False, "axes.spines.right": False})

with open("results/flipbudget/reconciliation_four_layers_corrected.json") as f:
    layers = json.load(f)["layer_stats"]
with open("results/flipbudget/worst_case_sensitivity.json") as f:
    wc = json.load(f)

established = [
    ("Sampling\n(alpha=beta=0)", layers["w_sampling"]["median_width"]),
    ("Audit-estimation-only\n(score_boxed, measured)", layers["w_audit_only"]["median_width"]),
    ("Scorer-ID-only\n(score_boxed, Lambda=2)", layers["w_scorer_only"]["median_width"]),
    ("Combined\n(score_boxed, measured+Lambda=2)", layers["w_combined"]["median_width"]),
]
conditional = [
    ("exact_match best-case\n(bound, Lambda=2)", wc["best_case"]["median_width"]),
    ("exact_match worst-case\n(bound, Lambda=2)", wc["worst_case"]["median_width"]),
]

fig, ax = plt.subplots(figsize=(7.2, 4.6))
labels_e = [x[0] for x in established]
vals_e = [x[1] for x in established]
labels_c = [x[0] for x in conditional]
vals_c = [x[1] for x in conditional]
x_e = range(len(vals_e))
x_c = range(len(vals_e), len(vals_e) + len(vals_c))
ax.bar(x_e, vals_e, color="#0072B2", label="Established (measured on score_boxed's audit)")
ax.bar(x_c, vals_c, color="#D55E00", hatch="//", edgecolor="black", linewidth=0.6,
       label="exact_match -- NOT measured, worst/best-case bound only")
ax.set_xticks(list(x_e) + list(x_c))
ax.set_xticklabels(labels_e + labels_c, fontsize=8, rotation=20, ha="right")
ax.set_ylabel("Median identified-set width (120 pairs)")
ax.set_title("Even exact_match's worst-case bound stays below the established\naudit-estimation-only median",
              fontsize=11)
ax.axhline(layers["w_audit_only"]["median_width"], color="#0072B2", linestyle=":", linewidth=1.0, alpha=0.7)
ax.legend(fontsize=8, frameon=False, loc="upper left")
fig.text(0.01, -0.05,
          f"exact_match worst-case (alpha=26.73%, beta=1.44%, population-weighted extreme, see "
          f"scripts/fb_worst_case_sensitivity.py): only {wc['worst_case']['n_valid']} of 120 pairs remain "
          f"valid at all, and all {wc['worst_case']['n_unresolved']} of those are fully unresolved -- the "
          "worst case doesn't just widen the comparison, it removes most of it. Reported honestly, not "
          "smoothed into the headline bar.",
          fontsize=7.5, ha="left", va="top", wrap=True)
fig.tight_layout(rect=[0, 0.13, 1, 1])
fig.savefig("figures/fig5_worst_case_sensitivity.png", dpi=300, bbox_inches="tight")
print("Written to figures/fig5_worst_case_sensitivity.png")
