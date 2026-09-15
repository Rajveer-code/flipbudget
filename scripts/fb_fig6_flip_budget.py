"""Figure 6: flip-budget / ranking-preservation. For the most-fragile and
most-robust real pairs (fb_flip_budget_uncertainty_mathhard.py), shows the
bootstrap interval for Delta* against 0 (the flip point) and reports the
flip budget as a number -- not as a second geometric mark on the same axis,
since d* is a magnitude in a different space (differential-error
perturbation), not itself a location on the Delta* axis; drawing it as an
x-axis offset would overclaim a relationship never actually verified.

Run: python scripts/fb_fig6_flip_budget.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "serif", "font.size": 11,
                      "axes.spines.top": False, "axes.spines.right": False,
                      "axes.spines.left": False})

with open("results/flipbudget/flip_budget_uncertainty_mathhard.json") as f:
    d = json.load(f)

fig, axes = plt.subplots(2, 1, figsize=(6.6, 4.0), sharex=False)
for ax, (key, title, color) in zip(axes, [
    ("most_fragile", "Most fragile pair", "#D55E00"),
    ("most_robust", "Most robust pair", "#009E73"),
]):
    r = d[key]
    lo, hi = r["delta_interval"]
    pt = r["corrected_delta_point"]
    fb = r["flip_budget_point"]
    ax.errorbar([pt], [0], xerr=[[pt - lo], [hi - pt]], fmt="o", color=color, capsize=4, markersize=6, zorder=3)
    ax.axvline(0, color="#333333", linewidth=1.0, linestyle="-", zorder=1)
    ax.text(0.006, 0.55, "0 (flip point)", fontsize=7.5, ha="left", va="bottom", color="#333333")
    ax.text(hi + 0.012, 0, f"$d^*$={fb:.3f}", fontsize=8.5, ha="left", va="center", color=color)
    ax.set_yticks([])
    ax.set_title(f"{title}: {r['model_hi'].split('/')[-1]} vs {r['model_lo'].split('/')[-1]}", fontsize=9.5)
    ax.set_xlim(min(0, lo) - 0.03, hi + 0.09)
    ax.set_ylim(-0.4, 0.8)

axes[-1].set_xlabel(r"$\Delta^* = A_1^* - A_2^*$")
fig.suptitle("Ranking preservation: the bootstrap interval stays clear of the\nflip point, for both the most fragile and most robust pair tested",
             fontsize=10.5, y=1.03)
fig.text(0.01, -0.06,
          r"$d^*$: minimum additional differential-error perturbation (beyond the audited margins) needed to "
          "make the comparison's sign ambiguous -- a magnitude, not itself a point on this axis. Interval is a "
          "raw percentile bootstrap over both benchmark items and audit items jointly (paired_bootstrap_delta); "
          "coverage caveat: simulated ~0.90-0.92 empirical coverage at a 0.95 nominal target for realistic audit "
          "sizes, not an exact calibrated CI -- see THEORY_EXTENSIONS.md S7.",
          fontsize=7.3, ha="left", va="top", wrap=True)
fig.tight_layout(rect=[0, 0.14, 1, 0.94])
fig.savefig("figures/fig6_flip_budget.png", dpi=300, bbox_inches="tight")
print("Written to figures/fig6_flip_budget.png")
