"""Final scientific re-audit (REAUDIT.md). Output: results/flipbudget/reaudit_results.json

 1. why 3/136: width decomposition (q-part vs r-part), point-estimate ranking changes
 2. scorer choice on rankings: a_em vs a_sb orderings
 3. audit-budget curves by simulation (multipliers of the current audit, 4 truth
    scenarios, 4 allocation rules at equal total budget)
 4. the planned 458 labels: what they can do for per-model ranking
 5. common-mechanism diagnostics: per-model LR contributions, leave-one-out,
    indeterminate-as-error variant
 6. exact_match information in the existing audit (joint cells)
"""
import json
import sys
from itertools import combinations

import numpy as np

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")
from fb_core_estimand_audit import load_real  # noqa: E402
from flipbudget.pv import accuracy, difference_interval, wilson, sidak_z  # noqa: E402

SEED = 42
Z = 1.959964
Z4 = sidak_z(0.95, 4)
OUT = "results/flipbudget/reaudit_results.json"
N_REP = 200
MULTS = [1, 2, 4, 8, 16, 32, 64]


def qualifying(models):
    return {m: v for m, v in models.items() if v["n_q"] and v["n_r"]}


def resolved_pairs(ms, a, box):
    """Pairs whose joint interval excludes 0 (box: dict m -> (qlo,qhi,rlo,rhi))."""
    out = []
    for m1, m2 in combinations(ms, 2):
        lo, hi = difference_interval(a[m1], box[m1], a[m2], box[m2])
        out.append(lo > 0 or hi < 0)
    return np.array(out)


def sampling_resolved(ms, a, N, key="a"):
    res = []
    for m1, m2 in combinations(ms, 2):
        ws = Z * np.sqrt(a[m1] * (1 - a[m1]) / N[m1] + a[m2] * (1 - a[m2]) / N[m2])
        res.append(abs(a[m1] - a[m2]) > ws)
    return np.array(res)


# ------------------------------------------------------------------ 1, 2
def why(models):
    Q = qualifying(models)
    ms = sorted(Q)
    a = {m: Q[m]["a_sb"] for m in ms}
    z2 = sidak_z(0.95, 2)
    parts = []
    for m in ms:
        v = Q[m]
        ql, qh = wilson(v["x_q"], v["n_q"], z2)
        rl, rh = wilson(v["x_r"], v["n_r"], z2)
        parts.append({"model": m, "q_part": a[m] * (qh - ql), "r_part": (1 - a[m]) * (rh - rl)})
    point = {m: accuracy(a[m], Q[m]["x_q"] / Q[m]["n_q"], Q[m]["x_r"] / Q[m]["n_r"]) for m in ms}
    flips = sum((a[m1] - a[m2]) * (point[m1] - point[m2]) < 0 for m1, m2 in combinations(ms, 2))
    flip_pairs = [[m1, m2] for m1, m2 in combinations(ms, 2) if (a[m1] - a[m2]) * (point[m1] - point[m2]) < 0]
    # scorer choice: exact_match vs score_boxed orderings, and sampling-significant ones
    em = {m: Q[m]["a_em"] for m in ms}
    N = {m: Q[m]["N"] for m in ms}
    sc_flip = [[m1, m2] for m1, m2 in combinations(ms, 2) if (a[m1] - a[m2]) * (em[m1] - em[m2]) < 0]
    sig_sb = dict(zip(combinations(ms, 2), sampling_resolved(ms, a, N)))
    sig_em = dict(zip(combinations(ms, 2), sampling_resolved(ms, em, N)))
    sc_flip_sig = [p for p in sc_flip if sig_sb[tuple(p)] and sig_em[tuple(p)]]
    order = sorted(ms, key=lambda m: -a[m])
    adjacent = [tuple(sorted(p)) for p in zip(order, order[1:])]
    return {"median_q_part": float(np.median([p["q_part"] for p in parts])),
            "median_r_part": float(np.median([p["r_part"] for p in parts])),
            "share_width_from_r": float(np.mean([p["r_part"] / (p["q_part"] + p["r_part"]) for p in parts])),
            "per_model_parts": parts,
            "point_estimate_order_flips_vs_a_sb": int(flips), "point_flip_pairs": flip_pairs,
            "scorer_choice_order_flips": len(sc_flip), "scorer_choice_flip_pairs": sc_flip,
            "scorer_choice_flip_detail": [{"pair": p, "a_sb": [a[p[0]], a[p[1]]], "a_em": [em[p[0]], em[p[1]]], "sig_sb": bool(sig_sb[tuple(p)]), "sig_em": bool(sig_em[tuple(p)])} for p in sc_flip], "scorer_choice_flips_both_sampling_significant": len(sc_flip_sig),
            "scorer_choice_flip_pairs_significant": sc_flip_sig,
            "n_adjacent_pairs": len(adjacent),
            "adjacent_resolved_by_sampling": int(sum(sig_sb[p] for p in adjacent))}


# ------------------------------------------------------------------ 3, 4
def allocations(Q, ms, budget, pilot):
    """Per-(model, stratum) sample sizes summing to `budget`.
    pilot: dict m -> (x_q, n_q, x_r, n_r) used by the data-driven rules."""
    a = np.array([Q[m]["a_sb"] for m in ms])
    cur = np.array([[Q[m]["n_q"], Q[m]["n_r"]] for m in ms], float)

    def normalize(w):
        w = np.maximum(w, 1e-12)
        n = np.maximum(1, np.floor(budget * w / w.sum()))
        return n.astype(int)

    rules = {}
    rules["scaled_current"] = normalize(cur)
    rules["uniform"] = normalize(np.ones_like(cur))
    # width-optimal under the zero-event Wilson approximation:
    # minimize sum_m [a_m c/n_qm + (1-a_m) c/n_rm]  ->  n proportional to sqrt(weight)
    rules["width_optimal"] = normalize(np.stack([np.sqrt(a), np.sqrt(1 - a)], 1))
    # plug-in Neyman on each model's stratum SD, stratum sizes a_m N, (1-a_m) N
    p = np.array([[pilot[m][0] / pilot[m][1], pilot[m][2] / pilot[m][3]] for m in ms])
    size = np.stack([a, 1 - a], 1)
    rules["plugin_neyman"] = normalize(size * np.sqrt(p * (1 - p)))
    pj = np.array([[(pilot[m][0] + .5) / (pilot[m][1] + 1), (pilot[m][2] + .5) / (pilot[m][3] + 1)] for m in ms])
    rules["neyman_jeffreys"] = normalize(size * np.sqrt(pj * (1 - pj)))
    return rules


def truth_draw(scenario, Q, ms, rng):
    if scenario == "low_error":
        return np.full((len(ms), 2), 0.002)
    if scenario == "moderate_error":
        return np.tile([0.03, 0.01], (len(ms), 1))
    if scenario == "heterogeneous_posterior":  # Jeffreys posterior of the current audit, per model
        return np.array([[rng.beta(Q[m]["x_q"] + .5, Q[m]["n_q"] - Q[m]["x_q"] + .5),
                          rng.beta(Q[m]["x_r"] + .5, Q[m]["n_r"] - Q[m]["x_r"] + .5)] for m in ms])
    if scenario == "one_model_specific":  # observed pattern: one format-driven model
        t = np.full((len(ms), 2), 0.002)
        t[ms.index("CohereForAI/c4ai-command-r-v01"), 0] = 0.67
        return t
    raise ValueError(scenario)


def simulate_budget(Q, ms, total, rule, scenario, rng, base=None):
    """Fraction of 136 pairs resolved (joint 95%). base: optional existing counts to add to."""
    a = {m: Q[m]["a_sb"] for m in ms}
    pilot = {m: (Q[m]["x_q"], Q[m]["n_q"], Q[m]["x_r"], Q[m]["n_r"]) for m in ms}
    n = allocations(Q, ms, total, pilot)[rule]
    fr = []
    for _ in range(N_REP):
        t = truth_draw(scenario, Q, ms, rng)
        x = rng.binomial(n, t)
        nn, xx = n.copy(), x.copy()
        if base is not None:
            nn, xx = nn + base[0], xx + rng.binomial(base[0], t)
        box = {m: wilson(xx[i, 0], nn[i, 0], Z4) + wilson(xx[i, 1], nn[i, 1], Z4) for i, m in enumerate(ms)}
        fr.append(resolved_pairs(ms, a, box).mean())
    fr = np.array(fr)
    return {"median": float(np.median(fr)), "p10": float(np.quantile(fr, .1)), "p90": float(np.quantile(fr, .9))}


def budget_curves(models):
    rng = np.random.default_rng(SEED)
    Q = qualifying(models)
    ms = sorted(Q)
    cur_total = sum(Q[m]["n_q"] + Q[m]["n_r"] for m in ms)
    out = {"current_total_labels": cur_total, "curves": {}}
    for scen in ["low_error", "moderate_error", "heterogeneous_posterior", "one_model_specific"]:
        for rule in ["scaled_current", "uniform", "width_optimal", "plugin_neyman", "neyman_jeffreys"]:
            out["curves"][f"{scen}|{rule}"] = [
                {"mult": k, "labels": k * cur_total, **simulate_budget(Q, ms, k * cur_total, rule, scen, rng)}
                for k in MULTS]
    # the planned 458 labels added to the existing audit, spread evenly across models/strata
    base = (np.array([[Q[m]["n_q"], Q[m]["n_r"]] for m in ms]),)
    out["plus_458"] = {scen: {rule: simulate_budget(Q, ms, 458, rule, scen, rng, base=base)
                              for rule in ["uniform", "width_optimal"]}
                       for scen in ["low_error", "moderate_error", "heterogeneous_posterior", "one_model_specific"]}
    return out


# ------------------------------------------------------------------ 5
def mech_fit(a, xq, nq, xr, nr):
    """ML (alpha, beta) under a common mechanism, grid. Returns (ll, alpha, beta, per-model ll)."""
    def binll(x, n, p):
        p = np.clip(p, 1e-12, 1 - 1e-12)
        return x * np.log(p) + (n - x) * np.log(1 - p)
    AL = np.linspace(0, 0.05, 501)[:, None, None]
    BE = np.linspace(0, 0.3, 61)[None, :, None]
    A = (a - AL) / (1 - AL - BE)                           # grid x grid x models
    q = AL * (1 - A) / np.where(a > 0, a, 1)
    r = BE * A / (1 - a)
    llm = binll(xq, nq, q) + binll(xr, nr, r)
    tot = np.where(np.all((A >= 0) & (A <= 1), axis=2), llm.sum(axis=2), -np.inf)
    i, j = np.unravel_index(np.argmax(tot), tot.shape)
    return float(tot[i, j]), float(AL[i, 0, 0]), float(BE[0, j, 0]), llm[i, j]


def boot_p(a, xq, nq, xr, nr, n_boot, rng):
    """Parametric bootstrap p for the LR (common mechanism vs per-model)."""
    ll0, al, be, _ = mech_fit(a, xq, nq, xr, nr)
    lr = 2 * (saturated(xq, nq, xr, nr).sum() - ll0)
    A = (a - al) / (1 - al - be)
    q0 = np.clip(al * (1 - A) / np.where(a > 0, a, 1), 0, 1)
    r0 = np.clip(be * A / (1 - a), 0, 1)
    ge = 0
    for _ in range(n_boot):
        bq, br = rng.binomial(nq, q0), rng.binomial(nr, r0)
        lb = mech_fit(a, bq, nq, br, nr)[0]
        ge += 2 * (saturated(bq, nq, br, nr).sum() - lb) >= lr - 1e-9
    return (ge + 1) / (n_boot + 1)


def saturated(xq, nq, xr, nr):
    def binll(x, n):
        p = np.clip(x / n, 1e-12, 1 - 1e-12)
        return x * np.log(p) + (n - x) * np.log(1 - p)
    return binll(xq, nq) + binll(xr, nr)


def mechanism_diagnostics(models):
    Q = qualifying(models)
    ms = sorted(Q)

    def arrays(ms_, indet_as_error=False):
        a = np.array([Q[m]["a_sb"] for m in ms_])
        xq = np.array([Q[m]["x_q"] + (Q[m]["indet_cred"] if indet_as_error else 0) for m in ms_])
        nq = np.array([Q[m]["n_q"] + (Q[m]["indet_cred"] if indet_as_error else 0) for m in ms_])
        xr = np.array([Q[m]["x_r"] + (Q[m]["indet_wrong"] if indet_as_error else 0) for m in ms_])
        nr = np.array([Q[m]["n_r"] + (Q[m]["indet_wrong"] if indet_as_error else 0) for m in ms_])
        return a, xq, nq, xr, nr

    a, xq, nq, xr, nr = arrays(ms)
    ll0, al, be, llm = mech_fit(a, xq, nq, xr, nr)
    sat = saturated(xq, nq, xr, nr)
    contrib = {m: float(2 * (sat[i] - llm[i])) for i, m in enumerate(ms)}
    loo = {}
    for drop in ms:
        k = [m for m in ms if m != drop]
        a2, xq2, nq2, xr2, nr2 = arrays(k)
        l, al2, _, _ = mech_fit(a2, xq2, nq2, xr2, nr2)
        loo[drop] = {"LR": float(2 * (saturated(xq2, nq2, xr2, nr2).sum() - l)), "alpha_hat": float(al2),
                     "bootstrap_p": float(boot_p(a2, xq2, nq2, xr2, nr2, 500, np.random.default_rng(SEED)))}
    a3, xq3, nq3, xr3, nr3 = arrays(ms, indet_as_error=True)
    l3, al3, be3, _ = mech_fit(a3, xq3, nq3, xr3, nr3)
    return {"LR_full": float(2 * (sat.sum() - ll0)), "alpha_hat": float(al), "beta_hat": float(be),
            "per_model_LR_contribution": dict(sorted(contrib.items(), key=lambda kv: -kv[1])),
            "leave_one_out": loo,
            "indeterminate_as_error": {"LR": float(2 * (saturated(xq3, nq3, xr3, nr3).sum() - l3)),
                                       "alpha_hat": float(al3), "beta_hat": float(be3)},
            "df_note": "saturated has 2 params per model; null has 2 in total"}


# ------------------------------------------------------------------ 6
def exact_match_in_audit():
    key = json.load(open("results/analysis/mathhard_labelling_key.json"))
    pop = json.load(open("results/analysis/tc_expansion_population.json"))["population"]
    em = {(r["model"], r["item_id"]): r["exact_match"] for r in pop}
    cells = {}
    for it in key:
        k = (it["model"], it["item_id"])
        if k not in em:
            continue
        sb = it["stratum"] == "credited"
        c = f"sb={int(sb)},em={int(em[k] == 1)}"
        cells[c] = cells.get(c, 0) + 1
    return {"audit_items_by_joint_cell": cells}


def main():
    models, _ = load_real()
    res = {"n_rep": N_REP, "multipliers": MULTS}
    res["why"] = why(models)
    print("WHY", {k: v for k, v in res["why"].items() if k not in ("per_model_parts",)})
    res["exact_match_in_audit"] = exact_match_in_audit()
    print("EM", res["exact_match_in_audit"])
    res["mechanism"] = mechanism_diagnostics(models)
    mech = res["mechanism"]
    print("MECH LR", mech["LR_full"], "indet-as-error", mech["indeterminate_as_error"])
    print("  top contributions", list(mech["per_model_LR_contribution"].items())[:4])
    print("  LOO LR", {k.split('/')[-1]: round(v["LR"], 1) for k, v in mech["leave_one_out"].items()})
    res["budget"] = budget_curves(models)
    for k, v in res["budget"]["curves"].items():
        print(k, [(c["mult"], round(100 * c["median"])) for c in v])
    print("PLUS458", json.dumps(res["budget"]["plus_458"]))
    json.dump(res, open(OUT, "w"), indent=1, default=float)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
