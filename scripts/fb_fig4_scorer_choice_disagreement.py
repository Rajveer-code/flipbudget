"""Figure 4: scorer-choice disagreement. For each of the 120 real pairs,
plots the point estimate of Delta*=A1*-A2* computed under exact_match
accuracy vs. under score_boxed accuracy (same audited alpha,beta box both
times) -- the accuracy-substitution shift this project calls "scorer-choice
width" (median 0.0091), NOT a full symmetric two-scorer uncertainty layer
(each scorer's own alpha,beta is a separate, only-partially-measured
quantity -- see fig5).

Run: python scripts/fb_fig4_scorer_choice_disagreement.py
"""
import json

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 11,
                      "axes.spines.top": False, "axes.spines.right": False})

with open("results/flipbudget/scorer_choice_sensitivity.json") as f:
    d = json.load(f)

pts_em = np.array([p["point_exact_match"] for p in d["scorer_choice_width"]["per_pair"]])
pts_sb = np.array([p["point_score_boxed"] for p in d["scorer_choice_width"]["per_pair"]])
widths = np.array([p["scorer_choice_width"] for p in d["scorer_choice_width"]["per_pair"]])

fig, ax = plt.subplots(figsize=(5.6, 5.2))
lims = [min(pts_em.min(), pts_sb.min()) - 0.03, max(pts_em.max(), pts_sb.max()) + 0.03]
ax.plot(lims, lims, "-", color="#999999", linewidth=1.0, zorder=1, label=r"$y=x$ (no scorer-choice effect)")
sc = ax.scatter(pts_sb, pts_em, c=widths, cmap="viridis", s=22, edgecolor="none", zorder=2)
cb = fig.colorbar(sc, ax=ax, shrink=0.85)
cb.set_label("Scorer-choice width", fontsize=9)
ax.set_xlim(lims)
ax.set_ylim(lims)
ax.set_xlabel(r"Point $\hat\Delta^*$ under score_boxed accuracy")
ax.set_ylabel(r"Point $\hat\Delta^*$ under exact_match accuracy")
ax.set_title("Scorer-choice as an accuracy-substitution shift, not a full\nsymmetric two-scorer comparison", fontsize=10.5)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
fig.text(0.01, -0.03,
          f"n={len(widths)} real pairs; median width {np.median(widths):.4f}, max {widths.max():.4f}. "
          "Both axes use the SAME audited (alpha,beta) box (score_boxed's -- the only one fully audited); "
          "only the accuracy plugged into g(a,alpha,beta) differs. Points near the diagonal are "
          "pairs where the two scorers' accuracy estimates barely move the comparison.",
          fontsize=7.5, ha="left", va="top", wrap=True)
fig.tight_layout(rect=[0, 0.08, 1, 1])
fig.savefig("figures/fig4_scorer_choice_disagreement.png", dpi=300, bbox_inches="tight")
print("Written to figures/fig4_scorer_choice_disagreement.png")
