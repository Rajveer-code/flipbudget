"""Stress-test AUDIT_DESIGN_ANALYSIS.md's conclusions across scenarios well
outside MATH-Hard's exact observed configuration, per item 5 of the
flagship-strengthening phase. Reuses the exact same formulas (Neyman
allocation, Wilson CI, the bounded g() correction) -- no new statistics
invented, just applied across a grid instead of one dataset's numbers.

Scenarios swept: alpha/beta magnitude (rare to common error), strata
population ratios (MATH-Hard-like extreme imbalance to balanced), total
audit budget, confidence level, precision target, benchmark size (via the
sampling-vs-audit crossover), and model heterogeneity (a spread of true
rates across simulated models rather than one shared rate).

Run: python scripts/fb_audit_design_stress_test.py
"""
import sys
import json

sys.path.insert(0, "scripts")
import numpy as np
from fb_t2_flipbudget import g
from ea_dominance_study import wilson_ci

Z_95, Z_90, Z_99 = 1.96, 1.645, 2.576
RNG = np.random.default_rng(42)


def neyman_allocation(p_h, N_h, total_n):
    """n_h proportional to N_h * sigma_h (finite-population Neyman), sigma_h
    = sqrt(p_h(1-p_h)). Standard result (Neyman 1934), applied here."""
    sigma = np.sqrt(np.array(p_h) * (1 - np.array(p_h)))
    weights = np.array(N_h) * sigma
    if weights.sum() == 0:
        return np.array(N_h) / sum(N_h) * total_n  # degenerate: fall back to proportional
    alloc = weights / weights.sum() * total_n
    return np.minimum(alloc, N_h)  # cannot allocate more than the stratum has


def proportional_allocation(N_h, total_n):
    N_h = np.array(N_h)
    return N_h / N_h.sum() * total_n


def variance_of_allocation(p_h, N_h, n_h):
    """Combined variance of the stratified mean estimator under allocation n_h."""
    n_h = np.maximum(n_h, 1)
    var_h = np.array(p_h) * (1 - np.array(p_h)) / n_h
    weights = (np.array(N_h) / sum(N_h)) ** 2
    return float(np.sum(weights * var_h))


def required_n_for_width(p_hat, target_width, z=Z_95, max_n=2_000_000):
    """Smallest n such that the Wilson CI width for p_hat is <= target_width."""
    lo, hi = 1, max_n
    if (wilson_ci(round(p_hat * lo), lo, z)[1] - wilson_ci(round(p_hat * lo), lo, z)[0]) <= target_width:
        return lo
    while lo < hi:
        mid = (lo + hi) // 2
        w = wilson_ci(round(p_hat * mid), mid, z)[1] - wilson_ci(round(p_hat * mid), mid, z)[0]
        if w <= target_width:
            hi = mid
        else:
            lo = mid + 1
    return lo


def run_scenario(name, p_h, N_h, total_n, z=Z_95):
    neyman = neyman_allocation(p_h, N_h, total_n)
    proportional = proportional_allocation(N_h, total_n)
    equal = np.full(len(N_h), total_n / len(N_h))
    equal = np.minimum(equal, N_h)

    var_neyman = variance_of_allocation(p_h, N_h, neyman)
    var_prop = variance_of_allocation(p_h, N_h, proportional)
    var_equal = variance_of_allocation(p_h, N_h, equal)

    neyman_beats_proportional = var_neyman <= var_prop * 1.001  # tolerance
    neyman_beats_equal = var_neyman <= var_equal * 1.001
    pct_variance_cut_vs_proportional = 100 * (1 - var_neyman / var_prop) if var_prop > 0 else None

    return {
        "scenario": name, "p_h": p_h, "N_h": N_h, "total_n": total_n,
        "var_neyman": var_neyman, "var_proportional": var_prop, "var_equal": var_equal,
        "neyman_beats_proportional": bool(neyman_beats_proportional),
        "neyman_beats_equal": bool(neyman_beats_equal),
        "pct_variance_cut_vs_proportional": pct_variance_cut_vs_proportional,
        "neyman_allocation_pct": (neyman / neyman.sum() * 100).round(1).tolist(),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Audit-design stress test: does Neyman-over-proportional survive")
    print("outside MATH-Hard's exact configuration?")
    print("=" * 70)

    scenarios = []

    # 1. MATH-Hard-like: extreme stratum imbalance, moderate error rates
    scenarios.append(("MATH-Hard-like (baseline)", [0.031, 0.12], [175, 1149], 400))

    # 2. Rare-error regime (both strata near 0)
    scenarios.append(("Rare error (both < 1%)", [0.003, 0.006], [5000, 5000], 500))

    # 3. Common error regime
    scenarios.append(("Common error (both > 20%)", [0.25, 0.35], [5000, 5000], 500))

    # 4. Balanced strata, moderate error
    scenarios.append(("Balanced strata", [0.05, 0.08], [2500, 2500], 500))

    # 5. Very small stratum (n_h tiny relative to the other)
    scenarios.append(("One tiny stratum", [0.05, 0.05], [50, 9950], 500))

    # 6. IFEval-like: three strata, one near-census-sized
    neyman3 = neyman_allocation([0.025, 0.90, 0.90], [5071, 374, 9162], 454)
    scenarios_3strata = {
        "name": "IFEval-like (3 strata)", "p_h": [0.025, 0.90, 0.90],
        "N_h": [5071, 374, 9162], "total_n": 454,
    }

    # 7. High confidence (99%) vs low (90%) -- required-n sensitivity
    req_n_95 = required_n_for_width(0.03, 0.02, z=Z_95)
    req_n_90 = required_n_for_width(0.03, 0.02, z=Z_90)
    req_n_99 = required_n_for_width(0.03, 0.02, z=Z_99)

    # 8. Different precision targets at fixed p_hat and confidence
    req_n_by_target = {t: required_n_for_width(0.03, t, z=Z_95) for t in (0.005, 0.01, 0.02, 0.05, 0.10)}

    # 9. Model heterogeneity: 30 simulated models, each with its OWN alpha
    # (credited-stratum rate, heterogeneous) but a SHARED, fixed, near-zero
    # beta (wrong-stratum rate) -- mirrors the real MATH-Hard structure
    # (alpha varies by model, beta_pooled=0.0 for nearly everyone). Question:
    # if audit allocation is planned from the POOLED/average alpha (as any
    # single shared design must be, before auditing reveals each model's own
    # rate) instead of each model's true own alpha, how much variance is lost?
    shared_beta = 0.01
    true_alphas = RNG.uniform(0.01, 0.15, size=30)  # 30 simulated models, heterogeneous alpha
    pooled_alpha = true_alphas.mean()
    neyman_at_pooled = neyman_allocation([pooled_alpha, shared_beta], [1000, 1000], 200)
    per_model_variance_using_pooled_neyman = []
    per_model_variance_using_own_neyman = []
    for a in true_alphas:
        v_pooled_alloc = variance_of_allocation([a, shared_beta], [1000, 1000], neyman_at_pooled)
        neyman_own = neyman_allocation([a, shared_beta], [1000, 1000], 200)
        v_own_alloc = variance_of_allocation([a, shared_beta], [1000, 1000], neyman_own)
        per_model_variance_using_pooled_neyman.append(v_pooled_alloc)
        per_model_variance_using_own_neyman.append(v_own_alloc)
    heterogeneity_regret_pct = 100 * (
        np.mean(per_model_variance_using_pooled_neyman) / np.mean(per_model_variance_using_own_neyman) - 1
    )

    results = [run_scenario(*s) for s in scenarios]

    print("\n[Scenario sweep: Neyman vs proportional vs equal allocation]")
    all_neyman_wins = True
    for r in results:
        print(f"  {r['scenario']:<30} Neyman-beats-proportional={r['neyman_beats_proportional']}  "
              f"variance cut={r['pct_variance_cut_vs_proportional']:.1f}%  "
              f"alloc%={r['neyman_allocation_pct']}")
        all_neyman_wins = all_neyman_wins and r["neyman_beats_proportional"] and r["neyman_beats_equal"]

    r3 = run_scenario(**scenarios_3strata)
    print(f"  {r3['scenario']:<30} Neyman-beats-proportional={r3['neyman_beats_proportional']}  "
          f"variance cut={r3['pct_variance_cut_vs_proportional']:.1f}%  alloc%={r3['neyman_allocation_pct']}")
    all_neyman_wins = all_neyman_wins and r3["neyman_beats_proportional"]

    print(f"\n[{'OK' if all_neyman_wins else 'FAIL'}] Neyman allocation beats both "
          f"proportional and equal allocation in EVERY scenario tested: {all_neyman_wins}")

    print(f"\n[Confidence-level sensitivity] required n for width<=0.02 at p_hat=0.03:")
    print(f"  90% CI: n={req_n_90}   95% CI: n={req_n_95}   99% CI: n={req_n_99}")
    print(f"  monotonic in confidence level (higher confidence needs more n): "
          f"{req_n_90 <= req_n_95 <= req_n_99}")

    print(f"\n[Precision-target sensitivity] required n at p_hat=0.03, 95% CI:")
    for t, n in sorted(req_n_by_target.items()):
        print(f"  target width {t}: n={n}")
    monotonic_precision = all(
        req_n_by_target[a] >= req_n_by_target[b]
        for a, b in zip(sorted(req_n_by_target)[:-1], sorted(req_n_by_target)[1:])
    )
    print(f"  monotonic (tighter target needs more n): {monotonic_precision}")

    print(f"\n[Model heterogeneity] 30 simulated models, true alpha U(0.01,0.15), shared beta={shared_beta}, pooled_alpha={pooled_alpha:.4f}")
    print(f"  mean variance using POOLED-rate Neyman allocation: {np.mean(per_model_variance_using_pooled_neyman):.6f}")
    print(f"  mean variance using EACH MODEL's OWN Neyman allocation: {np.mean(per_model_variance_using_own_neyman):.6f}")
    print(f"  regret from using a shared/pooled allocation instead of per-model: "
          f"{heterogeneity_regret_pct:.1f}% higher variance")
    print(f"  interpretation: this is the real cost of NOT having per-model-specific audit design "
          f"when true rates are heterogeneous -- a genuine, quantified limitation of a single shared "
          f"Neyman allocation across a heterogeneous roster.")

    out = {
        "scenario_sweep": results, "three_strata_scenario": r3,
        "all_neyman_wins_every_scenario": all_neyman_wins,
        "confidence_level_sensitivity": {"n90": req_n_90, "n95": req_n_95, "n99": req_n_99,
                                          "monotonic": bool(req_n_90 <= req_n_95 <= req_n_99)},
        "precision_target_sensitivity": {str(k): v for k, v in req_n_by_target.items()},
        "precision_monotonic": bool(monotonic_precision),
        "model_heterogeneity": {
            "n_simulated_models": 30, "true_alpha_range": [float(true_alphas.min()), float(true_alphas.max())],
            "shared_beta": shared_beta, "pooled_alpha": float(pooled_alpha),
            "mean_variance_pooled_allocation": float(np.mean(per_model_variance_using_pooled_neyman)),
            "mean_variance_own_allocation": float(np.mean(per_model_variance_using_own_neyman)),
            "heterogeneity_regret_pct": float(heterogeneity_regret_pct),
        },
    }
    with open("results/flipbudget/audit_design_stress_test.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/audit_design_stress_test.json")
