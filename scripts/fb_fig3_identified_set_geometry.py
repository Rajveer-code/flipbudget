"""Figure 3: identified-set geometry. Illustrates T-H (sharpness): the
identified interval for A*=g(a,alpha,beta) over a Lambda-bounded box is
exactly the envelope of the four corner curves, intersected with [0,1] --
not a claim needing a grid search to verify, but shown here as one.

Anchor: score_boxed's own global pooled (alpha,beta) = (3.137%, 0%)
(results/flipbudget/tc_alpha_beta_update.json global_anchor_old), Lambda=2 --
the same reference values used throughout the empirical results, not a
figure-specific pick.

Run: python scripts/fb_fig3_identified_set_geometry.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "scripts")
from fb_t2_flipbudget import g
from fb_ta_ssm import lambda_bounds
from fb_reconcile_layers import bounded_single_model_extrema

plt.rcParams.update({"font.family": "serif", "font.size": 11,
                      "axes.spines.top": False, "axes.spines.right": False})

L = 2.0
with open("results/flipbudget/tc_alpha_beta_update.json") as f:
    anchor = json.load(f)["global_anchor_old"]
alpha, beta = anchor["alpha"], anchor["beta"]
alpha_lo, alpha_hi = lambda_bounds(alpha, L)
beta_lo, beta_hi = lambda_bounds(beta, L)

a_grid = np.linspace(0.0, 1.0, 400)
lo_env, hi_env = [], []
corners = {(al, be): [] for al in (alpha_lo, alpha_hi) for be in (beta_lo, beta_hi)}
for a in a_grid:
    lo, hi = bounded_single_model_extrema(a, alpha_lo, alpha_hi, beta_lo, beta_hi)
    lo_env.append(lo)
    hi_env.append(hi)
    for (al, be) in corners:
        corners[(al, be)].append(min(1.0, max(0.0, g(a, al, be))))

fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.fill_between(a_grid, lo_env, hi_env, color="#0072B2", alpha=0.18, label="Sharp identified set (envelope)")
styles = {0: "--", 1: ":"}
for i, ((al, be), vals) in enumerate(corners.items()):
    ax.plot(a_grid, vals, styles[i % 2], linewidth=1.0, color="#555555", alpha=0.8)
ax.plot(a_grid, a_grid, "-", linewidth=1.2, color="#D55E00", label=r"$\Lambda=1$ (no correction, $A^*=a$)")
ax.set_xlabel(r"Observed (scorer-recorded) accuracy $a$")
ax.set_ylabel(r"Identified set for true accuracy $A^*$")
ax.set_title(rf"Identified-set geometry: corner envelope = sharp interval ($\Lambda={L:.0f}$)", fontsize=11)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
fig.text(0.01, -0.02,
          rf"Anchor: score_boxed global pooled $(\alpha,\beta)=({alpha:.4f},{beta:.4f})$, "
          rf"$\Lambda$-box $\alpha\in[{alpha_lo:.4f},{alpha_hi:.4f}]$, $\beta\in[{beta_lo:.4f},{beta_hi:.4f}]$. "
          "Dashed/dotted lines: the four corner curves (T-H vertex theorem); their pointwise "
          "min/max IS the shaded envelope, confirming no interior point of the box can produce "
          "a more extreme $A^*$ than a corner.",
          fontsize=7.5, ha="left", va="top", wrap=True)
fig.tight_layout(rect=[0, 0.09, 1, 1])
fig.savefig("figures/fig3_identified_set_geometry.png", dpi=300, bbox_inches="tight")
print("Written to figures/fig3_identified_set_geometry.png")
