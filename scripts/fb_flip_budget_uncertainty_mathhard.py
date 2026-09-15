"""Flip-budget uncertainty on REAL, CURRENT MATH-Hard data (item 1 of the
latest directive: "flip-budget uncertainty" theory completion).

Supersedes fb_t5_budget_ci.py's result, which ran on a stale MMLU roster
(gemini-3.6-flash, nemotron-3-super-120b -- not part of this project's
current 27-model MATH-Hard roster) with a placeholder alpha=0.01 floor,
explicitly noted in its own output as not a real per-model estimate. That
script and result are left on disk unmodified (historical), not deleted;
this is the current, real result, using the ALREADY-VALIDATED
paired_bootstrap_delta from the published package
(src/flipbudget/inference.py, has its own passing unit test) on:
  - bench1/bench2: REAL per-item score_boxed correctness, all 1324 items,
    from tc_expansion_population.json (the same fresh pull used throughout
    the scorer-mismatch work).
  - audit_ystar/audit_yhat: reconstructed from the REAL audited counts
    (x_alpha, n0, x_beta, n1 from e4_mathhard_per_model.json) -- an
    array with the exact same false-credit/false-miss COUNT as the real
    audit, which is sufficient for a resampling bootstrap (it only needs
    the empirical count distribution, not item identity).

Run: python scripts/fb_flip_budget_uncertainty_mathhard.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
from ea_dominance_study import load, build_model_table
from flipbudget.inference import paired_bootstrap_delta


def bench_array(model, population):
    return np.array([1 if r["score_boxed_stratum"] == "credited" else 0
                      for r in population if r["model"] == model], dtype=float)


def audit_arrays(row):
    """Reconstruct count-equivalent ystar/yhat arrays from (x_alpha, n0, x_beta, n1).
    ystar=human/true label, yhat=scorer label, both 0/1. Credited stratum
    (scorer says 1): x_alpha of n0 are false credits (ystar=0,yhat=1), rest
    true credits (ystar=1,yhat=1). Wrong stratum (scorer says 0): x_beta of
    n1 are false misses (ystar=1,yhat=0), rest true misses (ystar=0,yhat=0)."""
    n0, x0 = row["n0_audit"], row["x_alpha"]
    n1, x1 = row["n1_audit"], row["x_beta"]
    ystar = np.array([0] * x0 + [1] * (n0 - x0) + [1] * x1 + [0] * (n1 - x1))
    yhat = np.array([1] * n0 + [0] * n1)
    return ystar, yhat


def main():
    with open("results/analysis/tc_expansion_population.json") as f:
        population = json.load(f)["population"]
    accs, margins = load()
    rows, excl = build_model_table(accs, margins)
    with open("results/analysis/pair_identification_human.json") as f:
        pairs = pi = json.load(f)["headline"]["pairs"]

    # Find the most fragile (smallest flip budget among non-degenerate real
    # pairs) and a robustly-dominant pair, from the already-established
    # canonical set, for a real, non-cherry-picked illustration.
    from fb_reconcile_layers import bounded_comparison
    candidates = []
    for p in pairs:
        lo_m, hi_m = p["lo"], p["hi"]
        if lo_m not in rows or hi_m not in rows:
            continue
        r1, r2 = rows[hi_m], rows[lo_m]
        box1 = r1["alpha_ci"] + r1["beta_ci"]
        box2 = r2["alpha_ci"] + r2["beta_ci"]
        lo_c, hi_c = bounded_comparison(r1["a_hat"], box1, r2["a_hat"], box2)
        if np.isnan(lo_c) or (lo_c <= 0 <= hi_c):
            continue  # skip empty-set and already-unresolved pairs
        candidates.append((hi_m, lo_m, hi_c - lo_c))
    candidates.sort(key=lambda x: x[2])
    tightest = candidates[0]
    widest = candidates[-1]
    print(f"Most fragile real resolved pair (narrowest identification width): {tightest}")
    print(f"Most robust real resolved pair (widest identification width): {widest}")

    results = {}
    for label, (m1, m2, w) in [("most_fragile", tightest), ("most_robust", widest)]:
        b1 = bench_array(m1, population)
        b2 = bench_array(m2, population)
        ys1, yh1 = audit_arrays(rows[m1])
        ys2, yh2 = audit_arrays(rows[m2])
        if len(ys1) < 2 or len(ys2) < 2:
            print(f"  {label} ({m1} vs {m2}): insufficient audit array length, skipped")
            continue
        out = paired_bootstrap_delta(b1, b2, ys1, yh1, ys2, yh2, n_boot=2000, seed=42)
        print(f"\n{label}: {m1} vs {m2}")
        print(f"  a1={out['a1']:.4f} a2={out['a2']:.4f}")
        print(f"  corrected_delta_point={out['corrected_delta_point']:.4f}")
        print(f"  delta_interval (95%)={out['delta_interval']}")
        print(f"  flip_budget_point={out['flip_budget_point']}  degenerate={out['flip_budget_degenerate']}")
        print(f"  flip_budget_lower_5pct={out['flip_budget_lower_5pct']}")
        results[label] = {"model_hi": m1, "model_lo": m2, **out}

    with open("results/flipbudget/flip_budget_uncertainty_mathhard.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\nWritten to results/flipbudget/flip_budget_uncertainty_mathhard.json")


if __name__ == "__main__":
    main()
