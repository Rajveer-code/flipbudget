"""Figures for the rebuilt paper, from results/flipbudget/rebuild_results.json.
figA per-model intervals, figB audit sizing, figC differential scorer error."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300})
BLUE, ORANGE, GREY, RED = "#0072B2", "#E69F00", "#777777", "#D55E00"
R = json.load(open("results/flipbudget/rebuild_results.json"))


def short(m):
    return m.split("/")[-1].replace("-Instruct", "-Inst").replace("c4ai-", "")[:22]


def fig_a():
    rows = R["per_model"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    y = np.arange(len(rows))
    for i, r in enumerate(rows):
        ax.plot([r["A_lo"], r["A_hi"]], [i + 0.15] * 2, color=ORANGE, lw=3, solid_capstyle="butt")
        ax.plot([r["sampling_lo"], r["sampling_hi"]], [i - 0.15] * 2, color=BLUE, lw=3, solid_capstyle="butt")
        ax.plot(r["a_sb"], i - 0.15, "|", color="k", ms=6)
    ax.set_yticks(y, [short(r["model"]) for r in rows], fontsize=7.5)
    ax.set_xlabel("MATH-Hard accuracy")
    ax.set_xlim(0, 1)
    ax.plot([], [], color=BLUE, lw=3, label="sampling 95% CI of scorer accuracy")
    ax.plot([], [], color=ORANGE, lw=3, label="true-accuracy 95% set given the human audit")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig("figures/figA_per_model_intervals.png")


def fig_b():
    c = R["C3_sizing"]["curve"]
    n = [x["n_per_stratum"] for x in c]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.plot(n, [x["pct_resolved"] for x in c], "o-", color=ORANGE, ms=4, label="audit-corrected (joint 95%)")
    ax.axhline(c[0]["pct_resolved_by_sampling_alone"], color=BLUE, ls="--", lw=1.2,
               label="sampling uncertainty only")
    cur = np.median([r["n_q"] + r["n_r"] for r in R["per_model"]]) / 2
    ax.axvline(cur, color=GREY, ls=":", lw=1)
    ax.text(cur * 1.1, 60, f"current audit\n(median {cur:.0f}/stratum)", fontsize=8, color=GREY)
    ax.set_xscale("log")
    ax.set_xlabel("audited items per stratum per model")
    ax.set_ylabel("% of 136 pairs with sign identified")
    ax.set_ylim(0, 100)
    ax.legend(fontsize=8, frameon=False, loc="lower right", bbox_to_anchor=(1.0, 0.08))
    fig.tight_layout()
    fig.savefig("figures/figB_audit_sizing.png")


def fig_c():
    from scipy.stats import beta as B
    rows = R["per_model"]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    for r in rows:
        x, n = r["x_q"], r["n_q"]
        lo = B.ppf(0.025, x, n - x + 1) if x else 0.0
        hi = B.ppf(0.975, x + 1, n - x) if x < n else 1.0
        col = RED if x else GREY
        ax.plot([r["a_sb"]] * 2, [lo, hi], color=col, lw=1, alpha=0.8)
        ax.plot(r["a_sb"], x / n, "o", color=col, ms=3 + n / 6)
    al = R["C2_common_mechanism"]["alpha_hat"]
    a = np.linspace(0.002, 0.36, 300)
    A = a - al  # beta_hat = 0
    ax.plot(a, al * (1 - A) / a, color=BLUE, lw=1.5,
            label=rf"common mechanism fit ($\hat\alpha$={al:.4f})")
    ax.set_xscale("log")
    ax.set_xlabel("score_boxed accuracy $a_m$ (log)")
    ax.set_ylabel(r"$\hat q_m$ = P(human: wrong | credited)")
    ax.annotate("command-r-v01 (4/6)", (0.025, 0.667), xytext=(0.075, 0.62), fontsize=8,
                arrowprops=dict(arrowstyle="-", color=GREY))
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig("figures/figC_differential_error.png")


def fig_d():
    """Design comparison at 458 added labels (simulation, homogeneous analysis)."""
    JJ = json.load(open("results/flipbudget/joint_verifier_results.json"))
    D = JJ["as_incorrect"]["designs"]["p10~Beta(audit),p01~U(0,1)"]
    names = {"uniform": "uniform random", "one_verifier": "one-verifier strata",
             "concordant_only": "concordant only", "balanced_check": "229 disagreement\n+ 229 concordant check",
             "prop_disagreement_plus_check": "358 disagreement\n+ 100 concordant",
             "width_min_disagreement": "all disagreement\n(width-minimizing)",
             "full_disagreement": "all disagreement\n(proportional)"}
    base = JJ["as_incorrect"]["shared"]["combined_resolved"]
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    y = np.arange(len(D))[::-1]
    for yi, d in zip(y, D):
        ax.plot([d["p10"], d["p90"]], [yi, yi], color="k", lw=1)
        ax.plot(d["median"], yi, "o", color=ORANGE, ms=6)
        ax.text(101.5, yi, f"{100 * d['falsification_power_rho10_median']:.0f}%", va="center", fontsize=7.5, color=GREY)
    ax.axvline(base, color=GREY, ls=":", lw=1)
    ax.text(base + 0.3, y[0] + 0.5, f"existing audit ({base})", fontsize=7.5, color=GREY)
    ax.text(101.5, y[0] + 0.6, "power*", fontsize=7.5, color=GREY)
    ax.set_yticks(y, [names[d["design"]] for d in D], fontsize=7.5)
    ax.set_xlim(82, 104)
    ax.set_xlabel("orderings resolved with 458 more labels (simulated; median, 10th-90th pct)", fontsize=8.5)
    fig.tight_layout()
    fig.savefig("figures/figD_design_comparison.png")


def fig_e():
    """Resolved orderings vs allowed cross-model heterogeneity of concordant error."""
    JJ = json.load(open("results/flipbudget/joint_verifier_results.json"))
    J = JJ["as_incorrect"]
    H = J["hetero"]
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    ax.plot([h["L"] for h in H], [h["combined"] for h in H], "o-", color=ORANGE, ms=4,
            label="each model's concordant rate free within L x pooled bound")
    ax.axhline(J["shared"]["combined_resolved"], color=ORANGE, ls="--", lw=1,
               label=f"homogeneous (pooled): {J['shared']['combined_resolved']}")
    ax.axhline(JJ["sampling_ceiling"], color=BLUE, ls=":", lw=1.2, label=f"sampling-only ceiling: {JJ['sampling_ceiling']}")
    ax.set_xscale("log")
    ax.set_xticks([1, 2, 5, 10, 20, 50], ["1", "2", "5", "10", "20", "50"])
    ax.set_xlabel("heterogeneity factor L")
    ax.set_ylabel("orderings resolved (of 136)")
    ax.set_ylim(0, 136)
    ax.legend(fontsize=7.5, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.45))
    fig.tight_layout()
    fig.savefig("figures/figE_homogeneity_sensitivity.png")


if __name__ == "__main__":
    fig_a(); fig_b(); fig_c(); fig_d(); fig_e()
    print("wrote figures A-E")
