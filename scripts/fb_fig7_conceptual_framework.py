"""Figure 7: conceptual framework. Schematic (no data) illustrating the
paper's central argument: a benchmark comparison is non-identified because
the evaluation procedure (scorer) is an imperfect measurement mechanism, and
audit uncertainty/audit design are themselves part of the validity problem.

Laid out as a strict staircase (top row -> straight down -> bottom row ->
straight down) so no arrow crosses through an unrelated box -- an earlier
3x3-grid version had arrows cutting diagonally across the whole figure and
was replaced after a visual check found it unreadable.

Run: python scripts/fb_fig7_conceptual_framework.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "serif", "font.size": 10})

fig, ax = plt.subplots(figsize=(7.6, 5.4))
ax.set_xlim(0, 9.3)
ax.set_ylim(-1.9, 7.3)
ax.axis("off")

BOX = dict(boxstyle="round,pad=0.35", linewidth=1.1)


def box(x, y, w, h, text, fc, ec="#333333"):
    p = FancyBboxPatch((x, y), w, h, facecolor=fc, edgecolor=ec, **BOX)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.7)
    return (x, y, w, h)


def hop(b1, b2):
    """Straight arrow, right edge of b1 to left edge of b2 (same row)."""
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    a = FancyArrowPatch((x1 + w1, y1 + h1 / 2), (x2, y2 + h2 / 2),
                         arrowstyle="-|>", mutation_scale=12, linewidth=1.0, color="#333333")
    ax.add_patch(a)


def drop(b1, b2, dx1=None, dx2=None):
    """Straight-down arrow, bottom of b1 to top of b2."""
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2
    cx1 = x1 + (dx1 if dx1 is not None else w1 / 2)
    cx2 = x2 + (dx2 if dx2 is not None else w2 / 2)
    a = FancyArrowPatch((cx1, y1), (cx2, y2 + h2),
                         arrowstyle="-|>", mutation_scale=12, linewidth=1.0, color="#333333")
    ax.add_patch(a)


# Row 1 (y=5.3): the scoring pipeline
b_model = box(0.3, 5.3, 2.2, 1.2, "Model\nresponse", "#EEEEEE")
b_scorer = box(2.9, 5.3, 2.6, 1.2, "Scorer\n(exact_match / score_boxed)", "#FFE9CC")
b_recorded = box(5.9, 5.3, 2.3, 1.2, "Recorded\ncorrectness $a$", "#EEEEEE")
hop(b_model, b_scorer)
hop(b_scorer, b_recorded)

# Row 2 (y=3.3): what a produces once it's aggregated
b_sample = box(5.9, 3.3, 2.3, 1.2, "Benchmark\nsampling", "#D6E8F5")
drop(b_recorded, b_sample)

# Row 3 (y=1.3): identification, fed by both the audit and the sampled accuracy
b_audit = box(0.3, 1.3, 2.6, 1.2, "Human audit\n$(\\alpha,\\beta)$", "#D9F0E3")
b_partid = box(3.3, 1.3, 2.9, 1.2, "Partial identification\n(T-A / T-H)", "#F5D6E8")
b_idset = box(6.6, 1.3, 2.3, 1.2, "Identified set\nfor $\\Delta^*$", "#F5D6E8")
hop(b_audit, b_partid)
hop(b_partid, b_idset)
drop(b_sample, b_partid, dx1=1.15, dx2=2.5)  # sampled accuracy feeds identification too

# Row 4 (y=-1.1): the uncertainty layer that turns out to dominate
b_auditest = box(3.3, -1.1, 5.6, 1.2, "Audit-estimation + audit-design uncertainty (dominant layer)", "#FFF3B0")
drop(b_auditest, b_idset, dx1=4.6, dx2=2.15)

ax.text(4.65, 6.85, "The scorer is an imperfect measurement mechanism, not a ground-truth oracle",
        ha="center", fontsize=9.3, style="italic", color="#333333")
ax.text(4.65, -1.65,
        "Every arrow into the identified set carries its own uncertainty; audit-estimation dominates in practice.",
        ha="center", fontsize=7.8, color="#555555")

fig.tight_layout()
fig.savefig("figures/fig7_conceptual_framework.png", dpi=300, bbox_inches="tight")
print("Written to figures/fig7_conceptual_framework.png")
