"""Single entry point for the rebuilt paper's numbers (PLAN_REBUILD.md task 2).

Estimand: A*_m = a_m(1-q_m) + (1-a_m) r_m for score_boxed, from the
score_boxed-stratified 400-item audit (CORE_ESTIMAND_AUDIT.md). Claims:
  C1 census disagreement between the two live scorers
  C2 differential scorer error (common-mechanism LR test, leave-one-out)
  C3 audit-sizing law for per-model ranking identification
  C4 indeterminate-label (Manski) bounds
Output: results/flipbudget/rebuild_results.json
Usage: python scripts/fb_rebuild_analysis.py [n_boot]   (default 1000)
"""
import json
import sys
from itertools import combinations

import numpy as np

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")
from fb_core_estimand_audit import load_real, heterogeneity, mechanism_model  # noqa: E402
from flipbudget.pv import (accuracy, accuracy_interval, difference_interval,  # noqa: E402
                           wilson, sidak_z, indeterminate_counts)

Z = 1.959964
OUT = "results/flipbudget/rebuild_results.json"
SIZES = [2, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 1000]


def census():
    pop = json.load(open("results/analysis/tc_expansion_population.json"))["population"]
    n = len(pop)
    d = sum(r["disagree"] for r in pop)
    sb_only = sum(r["score_boxed_stratum"] == "credited" and r["exact_match"] != 1 for r in pop)
    em_only = sum(r["score_boxed_stratum"] != "credited" and r["exact_match"] == 1 for r in pop)
    per = {}
    for r in pop:
        per.setdefault(r["model"], []).append(r["disagree"])
    rates = {m: float(np.mean(v)) for m, v in per.items()}
    return {"n_rows": n, "n_disagree": d, "rate": d / n, "wilson95": wilson(d, n),
            "sb_credited_em_not": sb_only, "em_credited_sb_not": em_only,
            "model_rate_min": min(rates.values()), "model_rate_max": max(rates.values())}


def boxes(models, z, indeterminate=None):
    """Per-model (q, r) Wilson box. indeterminate: None (drop), 'as_error'."""
    out = {}
    for m, v in models.items():
        xq, nq, xr, nr = v["x_q"], v["n_q"], v["x_r"], v["n_r"]
        if indeterminate == "as_error":
            (_, _), (xq, nq) = indeterminate_counts(xq, nq, v["indet_cred"])
            (_, _), (xr, nr) = indeterminate_counts(xr, nr, v["indet_wrong"])
        if nq == 0 or nr == 0:
            continue
        out[m] = wilson(xq, nq, z) + wilson(xr, nr, z)
    return out


def pairwise(models, bx):
    ms = sorted(bx)
    rows = []
    for m1, m2 in combinations(ms, 2):
        v1, v2 = models[m1], models[m2]
        a1, a2 = v1["a_sb"], v2["a_sb"]
        ws = 2 * Z * np.sqrt(a1 * (1 - a1) / v1["N"] + a2 * (1 - a2) / v2["N"])
        lo, hi = difference_interval(a1, bx[m1], a2, bx[m2])
        rows.append({"pair": [m1, m2], "lo": lo, "hi": hi, "w_audit": hi - lo, "w_sampling": ws,
                     "resolved": bool(lo > 0 or hi < 0),
                     "sampling_resolved": bool(abs(a1 - a2) > ws / 2)})
    return {"n_models": len(ms), "n_pairs": len(rows),
            "n_resolved": int(sum(r["resolved"] for r in rows)),
            "n_resolved_by_sampling_alone": int(sum(r["sampling_resolved"] for r in rows)),
            "median_w_audit": float(np.median([r["w_audit"] for r in rows])),
            "median_w_sampling": float(np.median([r["w_sampling"] for r in rows])),
            "median_ratio": float(np.median([r["w_audit"] / r["w_sampling"] for r in rows])),
            "min_ratio": float(min(r["w_audit"] / r["w_sampling"] for r in rows)),
            "pairs": rows}


def sizing(models):
    """Projection: every qualifying model audited with n items per stratum,
    events at each model's observed rate (0 stays 0). % pairs resolved at
    joint 95% (Sidak over the 4 parameters of a pair)."""
    z4 = sidak_z(0.95, 4)
    qual = {m: v for m, v in models.items() if v["n_q"] and v["n_r"]}
    curve = []
    for n in SIZES:
        bx = {m: wilson(round(v["x_q"] / v["n_q"] * n), n, z4) + wilson(round(v["x_r"] / v["n_r"] * n), n, z4)
              for m, v in qual.items()}
        res = pairwise(qual, bx)
        curve.append({"n_per_stratum": n, "labels_total": 2 * n * len(qual),
                      "pct_resolved": 100 * res["n_resolved"] / res["n_pairs"],
                      "pct_resolved_by_sampling_alone": 100 * res["n_resolved_by_sampling_alone"] / res["n_pairs"]})
    # closed form, zero events: audit width z^2/(n+z^2) vs sampling 2z sqrt(a(1-a)/N)
    law = []
    for a in (0.05, 0.2, 0.35):
        ws = 2 * Z * np.sqrt(a * (1 - a) / 1324)
        exact = next(n for n in range(1, 10**5)
                     if np.subtract(*accuracy_interval(a, wilson(0, n) + wilson(0, n))[::-1]) < ws)
        approx = Z / 2 * np.sqrt(1324 / (a * (1 - a))) - Z**2
        law.append({"a": a, "N": 1324, "n_star_exact": exact, "n_star_closed_form": float(approx)})
    return {"curve": curve, "crossover_law": law}


def per_model_table(models):
    z2 = sidak_z(0.95, 2)
    rows = []
    for m, v in sorted(models.items(), key=lambda kv: kv[1]["a_sb"]):
        if not (v["n_q"] and v["n_r"]):
            continue
        box = wilson(v["x_q"], v["n_q"], z2) + wilson(v["x_r"], v["n_r"], z2)
        lo, hi = accuracy_interval(v["a_sb"], box)
        ws = 2 * Z * np.sqrt(v["a_sb"] * (1 - v["a_sb"]) / v["N"])
        rows.append({"model": m, "a_sb": v["a_sb"], "a_em": v["a_em"], "N": v["N"],
                     "x_q": v["x_q"], "n_q": v["n_q"], "x_r": v["x_r"], "n_r": v["n_r"],
                     "indet_cred": v["indet_cred"], "indet_wrong": v["indet_wrong"],
                     "A_point": accuracy(v["a_sb"], v["x_q"] / v["n_q"], v["x_r"] / v["n_r"]),
                     "A_lo": lo, "A_hi": hi, "sampling_lo": v["a_sb"] - ws / 2, "sampling_hi": v["a_sb"] + ws / 2})
    return rows


def main():
    n_boot = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    models, strat = load_real()
    res = {"n_boot": n_boot, "stratum_check": strat, "C1_census": census()}
    print("C1", {k: v for k, v in res["C1_census"].items()})
    res["per_model"] = per_model_table(models)
    z4 = sidak_z(0.95, 4)
    res["pairwise"] = {
        "per_parameter_95": pairwise(models, boxes(models, Z)),
        "joint_95_sidak": pairwise(models, boxes(models, z4)),
        "joint_95_indeterminate_as_error": pairwise(models, boxes(models, z4, "as_error")),
    }
    for k, v in res["pairwise"].items():
        print(f"PAIR {k:34s} models={v['n_models']} pairs={v['n_pairs']} resolved={v['n_resolved']} "
              f"sampling-only={v['n_resolved_by_sampling_alone']} w_audit={v['median_w_audit']:.3f} "
              f"w_samp={v['median_w_sampling']:.4f} ratio={v['median_ratio']:.1f} (min {v['min_ratio']:.1f})")
    res["C2_heterogeneity_q"] = heterogeneity(models)
    res["C2_common_mechanism"] = mechanism_model(models, n_boot=n_boot)
    loo = {m: v for m, v in models.items() if m != "CohereForAI/c4ai-command-r-v01"}
    res["C2_common_mechanism_without_command_r"] = mechanism_model(loo, n_boot=n_boot)
    for k in ("C2_common_mechanism", "C2_common_mechanism_without_command_r"):
        print(k, {x: y for x, y in res[k].items() if x != "per_model_a_sb"})
    res["C3_sizing"] = sizing(models)
    print("C3 law", res["C3_sizing"]["crossover_law"])
    for c in res["C3_sizing"]["curve"]:
        print(f"   n={c['n_per_stratum']:5d} labels={c['labels_total']:6d} resolved={c['pct_resolved']:.1f}%"
              f" (sampling-only {c['pct_resolved_by_sampling_alone']:.1f}%)")
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
