"""Figure 1: uncertainty decomposition. Regenerates fig1_uncertainty_decomposition.png
from results already on disk -- no numbers typed by hand into the plotting code.

Run: python scripts/fb_fig1_uncertainty_decomposition.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Colorblind-safe (Okabe-Ito), qualitative, distinct hues
COLORS = {
    "sampling": "#0072B2",
    "scorer_only": "#E69F00",
    "scorer_choice": "#009E73",
    "audit_only": "#D55E00",
}

with open("results/flipbudget/reconciliation_four_layers_corrected.json") as f:
    recon = json.load(f)
with open("results/flipbudget/scorer_choice_sensitivity.json") as f:
    choice = json.load(f)

layers = [
    ("Benchmark\nsampling", recon["layer_stats"]["w_sampling"]["median_width"], COLORS["sampling"],
     f"n={recon['layer_stats']['w_sampling']['n_valid']}"),
    ("Scorer-\nidentification\n(score_boxed, $\\Lambda$=2)", recon["layer_stats"]["w_scorer_only"]["median_width"],
     COLORS["scorer_only"], f"n={recon['layer_stats']['w_scorer_only']['n_valid']}"),
    ("Scorer-choice\n(exact_match vs.\nscore_boxed)", choice["scorer_choice_width"]["median"],
     COLORS["scorer_choice"], f"n={choice['scorer_choice_width']['n_pairs']}"),
    ("Audit-\nestimation\n(score_boxed)", recon["layer_stats"]["w_audit_only"]["median_width"],
     COLORS["audit_only"], f"n={recon['layer_stats']['w_audit_only']['n_valid']}"),
]

fig, ax = plt.subplots(figsize=(6.2, 4.2))
xs = range(len(layers))
heights = [l[1] for l in layers]
colors = [l[2] for l in layers]
bars = ax.bar(xs, heights, color=colors, width=0.62, edgecolor="black", linewidth=0.6)

for i, (label, h, c, n) in enumerate(layers):
    ax.text(i, h + max(heights) * 0.02, f"{h:.3f}\n({n})", ha="center", va="bottom", fontsize=9)

ax.set_xticks(list(xs))
ax.set_xticklabels([l[0] for l in layers], fontsize=9)
ax.set_ylabel("Median identified-set / CI width\n(same 136 real MATH-Hard pairs)")
ax.set_title("Four measured uncertainty sources, same pairwise comparisons", fontsize=11, pad=12)
ax.set_ylim(0, max(heights) * 1.22)

fig.text(0.01, -0.02,
          "Audit-estimation uncertainty (finite human-audit sample) is the largest measured source, "
          "~4x the sampling width and ~4x the scorer-sensitivity width. Scorer-choice width (exact_match "
          "vs. score_boxed accuracy) is the smallest -- an accuracy-substitution point-estimate shift, not "
          "a full symmetric two-scorer comparison (see METHODOLOGICAL_AUDIT.md item 2).",
          fontsize=7.5, ha="left", va="top", wrap=True)

fig.tight_layout(rect=[0, 0.08, 1, 1])
fig.savefig("figures/fig1_uncertainty_decomposition.png", dpi=300, bbox_inches="tight")
print("Written to figures/fig1_uncertainty_decomposition.png")
for label, h, c, n in layers:
    print(f"  {label.replace(chr(10), ' ')}: {h:.4f} ({n})")
