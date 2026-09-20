"""G4.3 -- AISTATS figures F1-F4, regenerated from the committed JSON results.

F1 rank intervals per model: sampling only, agreement-stratified (eps = 0), eps-robust
   (eps0), and without pooling -- all simultaneous over the 351 orderings.
F2 certified orderings against eps, K=3 and K=2, with the preregistered eps0 marked.
F3 human-judged correctness by K=3 verifier cell, with exact intervals and cell sizes.
F4 the certification-falsification frontier (PROJECTED), with the chosen operating point.

Run: python scripts/fb_figures_aistats.py     Out: figures/aistats/f{1..4}.{png,pdf}
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flipbudget import certify as C  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "flipbudget"
OUT = ROOT / "figures" / "aistats"
# Okabe-Ito, colour-blind safe
BLUE, ORANGE, GREEN, VERMILLION, GREY = "#0072B2", "#E69F00", "#009E73", "#D55E00", "#666666"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.dpi": 300, "figure.constrained_layout.use": True})


def short(m):
    return m.split("/")[-1]


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / f"{name}.png")


def f1_rank_intervals(cert):
    K3 = cert["K3"]
    layers = [("sampling only (verifier taken as truth)", K3["rank_intervals_sampling_only"]["em"], GREY, "o"),
              ("agreement-stratified, ε = 0", K3["rank_intervals_simultaneous_eps0"], BLUE, "s"),
              (f"ε-robust (ε = {cert['config']['eps0_preregistered']})",
               K3["rank_intervals_simultaneous_eps_preregistered"], GREEN, "D"),
              ("no pooling across models", K3["rank_intervals_simultaneous_no_pooling"], VERMILLION, "^")]
    order = sorted(layers[0][1], key=lambda m: (layers[0][1][m][0], layers[1][1][m][0]))
    fig, ax = plt.subplots(figsize=(6.6, 7.2))
    off = np.linspace(0.3, -0.3, len(layers))
    for (label, ri, colour, mark), dy in zip(layers, off):
        for i, m in enumerate(order):
            lo, hi = ri[m]
            ax.plot([lo, hi], [i + dy] * 2, color=colour, lw=1.6, solid_capstyle="butt",
                    label=label if i == 0 else None)
            ax.plot([lo, hi], [i + dy] * 2, mark, color=colour, ms=2.4)
    ax.set_yticks(range(len(order)), [short(m) for m in order], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("rank among the 27 models (simultaneous 95% intervals)")
    ax.set_xlim(0.5, len(order) + 0.5)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=2, fontsize=7.5, frameon=False)
    ax.grid(axis="x", color="#DDDDDD", lw=0.5)
    ax.set_axisbelow(True)
    save(fig, "f1_rank_intervals")


def f2_eps_curve(cert):
    eps0 = cert["config"]["eps0_preregistered"]
    fig, ax = plt.subplots(figsize=(5.4, 3.4))
    for K, colour, style in (("K3", BLUE, "-"), ("K2", ORANGE, "--")):
        c = cert[K]["eps_curve"]
        x = [p["eps"] for p in c]
        ax.plot(x, [p["combined"] for p in c], style, color=colour, lw=1.8,
                label=f"{K[0]}={K[1]} verifiers, per ordering")
        ax.plot(x, [p["combined_simultaneous"] for p in c], style, color=colour, lw=1.0, alpha=0.6,
                label=f"{K[0]}={K[1]}, simultaneous")
    n_pairs = len(cert["K3"]["eps0_pairs"])
    ax.axvline(eps0, color=GREY, lw=0.9, ls=":")
    ax.annotate(f"preregistered\ntolerance {eps0}", (eps0, ax.get_ylim()[1] * 0.92), xytext=(eps0 + 0.006,
                ax.get_ylim()[1] * 0.86), fontsize=7.5, color=GREY)
    ax.set_xlabel("cross-model heterogeneity of concordant correctness, ε")
    ax.set_ylabel(f"certified orderings (of {n_pairs})")
    ax.set_ylim(0, n_pairs * 0.62)
    ax.set_xlim(-0.002, max(x) + 0.002)
    ax.legend(fontsize=7.5, frameon=False)
    ax.grid(color="#EEEEEE", lw=0.5)
    ax.set_axisbelow(True)
    save(fig, "f2_certified_vs_eps")


def f3_cells(cert, amap):
    cells = amap["census_cells"]["k3_sympy"]["27"]
    audit = {c: v for c, v in amap["audit_cells"]["27|k3_sympy|sympy|as_incorrect"].items()}
    conc = cert["K3"]["inputs"]["conc_intervals"]
    order = sorted(cells, key=lambda c: -cells[c])
    fig, ax = plt.subplots(figsize=(5.8, 3.4))
    for i, c in enumerate(order):
        a = audit.get(c)
        if a and a["n"]:
            p = a["x_correct"] / a["n"]
            # concordant cells show the pooled interval used in the analysis; audited discordant
            # cells show the same KL interval for display only (inference uses per-model bounds)
            lo, hi = conc[c] if c in conc else C.kl_interval(a["x_correct"], a["n"], C.sidak(2, 0.975))
            ax.plot([i], [p], "o", color=BLUE, ms=5)
            ax.plot([i, i], [lo, hi], color=BLUE, lw=1.6)
            ax.annotate(f"{a['x_correct']}/{a['n']}", (i, p), xytext=(i + 0.16, p), fontsize=7, color=GREY)
        else:
            ax.plot([i, i], [0, 1], color=VERMILLION, lw=1.6, alpha=0.5)
            ax.annotate("no labels", (i, 0.5), xytext=(i + 0.16, 0.5), fontsize=7, color=VERMILLION)
    ax.set_xticks(range(len(order)), [f"{c}\nn={cells[c]}" for c in order], fontsize=7.5)
    ax.set_xlabel("verifier cell (leaderboard 2024, boxed, Math-Verify)")
    ax.set_ylabel("share the human reference judges correct")
    ax.set_ylim(-0.03, 1.03)
    ax.grid(axis="y", color="#EEEEEE", lw=0.5)
    ax.set_axisbelow(True)
    save(fig, "f3_correctness_by_cell")


def f4_frontier(front, op, cert):
    pts = [p for p in front["points"] if p["F"]]
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    for cell, colour, mark in (("000", BLUE, "o"), ("111", ORANGE, "s")):
        xs, ys = [], []
        for p in pts:
            rho = p["falsification"][cell]["detectable_rho_80"]
            if rho is None:
                continue
            xs.append(rho)
            ys.append(p["certified_uniform_eps0.01"]["median"])
        ax.plot(xs, ys, mark, color=colour, ms=4, alpha=0.75, label=f"cell {cell}")
    base = cert["K3"]["eps_curve"][int(round(op["eps0"] / 0.0025))]["combined"]
    ax.axhline(base, color=GREY, lw=0.9, ls=":")
    ax.annotate(f"existing audit alone ({base})", (0.595, base + 0.15), fontsize=7.5, color=GREY, ha="right")
    chosen = next(p for p in pts if p.get("is_operating_point"))
    ax.plot([chosen["falsification"]["000"]["detectable_rho_80"]], [chosen["certified_uniform_eps0.01"]["median"]],
            "*", color=GREEN, ms=13, zorder=5)
    ax.annotate("chosen operating point", (chosen["falsification"]["000"]["detectable_rho_80"] + 0.004,
                chosen["certified_uniform_eps0.01"]["median"]), xytext=(0.255, base + 1.6), fontsize=7.5,
                arrowprops={"arrowstyle": "->", "color": GREY, "lw": 0.8}, color=GREY, va="center")
    ax.set_xlabel("per-model concordant error detectable at 80% power")
    ax.set_ylabel(f"projected certified orderings at ε = {op['eps0']}")
    ax.set_title("PROJECTED: simulated label outcomes, not observed", fontsize=8, color=VERMILLION)
    ax.legend(fontsize=7.5, frameon=False, title="falsification screen", title_fontsize=7.5)
    ax.grid(color="#EEEEEE", lw=0.5)
    ax.set_axisbelow(True)
    save(fig, "f4_frontier_projected")


def main():
    cert = json.load(open(RES / "certify_results.json", encoding="utf-8"))
    amap = json.load(open(RES / "audit_k3_map.json", encoding="utf-8"))
    front = json.load(open(RES / "g3_frontier.json", encoding="utf-8"))
    op = json.load(open(RES / "g3_operating_point.json", encoding="utf-8"))
    f1_rank_intervals(cert)
    f2_eps_curve(cert)
    f3_cells(cert, amap)
    f4_frontier(front, op, cert)


if __name__ == "__main__":
    main()
