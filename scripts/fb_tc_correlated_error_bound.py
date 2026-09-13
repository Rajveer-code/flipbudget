"""Item 4: T-C correlated-error analysis. The real audit (TC_REAL_ANALYSIS.md,
evidence table B4) has 0/69 scorer-wrong events and 0/51 paired either-wrong
observations -- literally no events to fit a hard/easy split or a correlation
coefficient from (THEORY_EXTENSIONS.md Prop 1-3 already says this honestly).
This script does NOT invent a point estimate. It derives what CAN be said
without inventing precision:

  (A) an exact Clopper-Pearson upper bound on the marginal item-difficulty
      "either wrong" rate from the observed 0/51, translated into upper
      bounds on the per-model error rate p under the two extreme correlation
      assumptions (rho=0 independent, rho=1 fully shared);
  (B) a first-order sensitivity curve (Prop 2's Var(diff) = 2p(1-p)(1-rho)
      relation) showing how many of the 136 pairs' scorer-only-layer verdicts
      WOULD change if correlation rho took various values -- NOT a claim
      about what rho actually is;
  (C) the required additional audit-n to get a usable (non-degenerate) point
      estimate of rho, via a simple event-count target, stated as a formal
      calculation, not a guess.

Independent (A) vs correlated (B, parametric) vs worst-case (C, rho=1) are
reported side by side, as the item explicitly asks.

Run: python scripts/fb_tc_correlated_error_bound.py
"""
import json
import sys

import numpy as np
from scipy.stats import beta as beta_dist

sys.path.insert(0, "scripts")
from ea_dominance_study import load, build_model_table
from fb_ta_ssm import lambda_bounds
from fb_reconcile_layers import bounded_comparison, L_REFERENCE

Z = 1.96


def clopper_pearson_upper(x, n, conf=0.95):
    """Exact upper confidence bound for a binomial proportion. For x=0 this
    is the standard 'rule of three'-generalizing exact bound, not an
    approximation."""
    if x == n:
        return 1.0
    return float(beta_dist.ppf(1 - (1 - conf) / 2, x + 1, n - x))


def main():
    print("=" * 78)
    print("T-C CORRELATED-ERROR BOUND (item 4) -- independent vs correlated vs worst-case")
    print("=" * 78)

    # ---- (A) What the 0/51 real paired audit actually bounds ----
    n_paired, x_either_wrong = 51, 0
    upper_either_wrong = clopper_pearson_upper(x_either_wrong, n_paired)
    print(f"\n(A) Real data: {x_either_wrong}/{n_paired} paired either-wrong events")
    print(f"    Exact 95% upper bound on P(either wrong): {upper_either_wrong:.4f}")
    # Under rho=0 (independent): P(either wrong) = 2p - p^2 ~= 2p for small p
    p_upper_indep = 1 - np.sqrt(1 - upper_either_wrong)  # solve 2p-p^2=U for p
    # Under rho=1 (fully shared, both-or-neither): P(either wrong) = p exactly
    p_upper_shared = upper_either_wrong
    print(f"    -> implied upper bound on marginal error rate p:")
    print(f"       if rho=0 (independent):  p <= {p_upper_indep:.4f}")
    print(f"       if rho=1 (fully shared): p <= {p_upper_shared:.4f}")
    print(f"    Both bounds are CONSISTENT WITH, not contradicting, the pooled alpha")
    print(f"    estimate (~0.03) used throughout the reconciliation -- the real audit")
    print(f"    rules out large error rates under either correlation assumption, but")
    print(f"    cannot distinguish rho=0 from rho=1 (0 events either way).")

    # ---- (B)/(C) Sensitivity of the 136-pair scorer-only verdict to rho ----
    accs, margins = load()
    rows, excl = build_model_table(accs, margins)
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4 = json.load(f)["per_model"]
    with open("results/analysis/pair_identification_human.json") as f:
        pi = json.load(f)

    pair_data = []
    for p in pi["headline"]["pairs"]:
        m_lo, m_hi = p["lo"], p["hi"]
        if m_lo not in rows or m_hi not in rows:
            continue
        r1, r2 = rows[m_hi], rows[m_lo]
        a1, a2 = r1["a_hat"], r2["a_hat"]
        m1, m2 = e4[m_hi], e4[m_lo]
        box1 = lambda_bounds(m1["alpha_pooled"], L_REFERENCE) + lambda_bounds(m1["beta_pooled"], L_REFERENCE)
        box2 = lambda_bounds(m2["alpha_pooled"], L_REFERENCE) + lambda_bounds(m2["beta_pooled"], L_REFERENCE)
        lo_c, hi_c = bounded_comparison(a1, box1, a2, box2)
        if np.isnan(lo_c):
            continue
        pair_data.append({"hi": m_hi, "lo": m_lo, "lo_c": lo_c, "hi_c": hi_c})

    print(f"\n(B)/(C) Sensitivity of scorer-only-layer verdicts to assumed correlation rho")
    print(f"    (n={len(pair_data)} valid scorer-only pairs; first-order approximation --")
    print(f"    shrink each pair's identified interval toward its own center by sqrt(1-rho),")
    print(f"    per THEORY_EXTENSIONS.md Prop 2's Var(diff) = 2p(1-p)(1-rho) relation.")
    print(f"    This is NOT a claim about the true rho -- rho is not estimable from 0 events.)")

    rho_grid = [0.0, 0.25, 0.5, 0.75, 1.0]
    sensitivity = []
    for rho in rho_grid:
        shrink = np.sqrt(1 - rho)
        n_unresolved = 0
        for pd in pair_data:
            center = (pd["lo_c"] + pd["hi_c"]) / 2
            half = (pd["hi_c"] - pd["lo_c"]) / 2 * shrink
            lo_s, hi_s = center - half, center + half
            if lo_s <= 0 <= hi_s:
                n_unresolved += 1
        pct = 100 * n_unresolved / len(pair_data)
        sensitivity.append({"rho": rho, "n_unresolved": n_unresolved, "pct_unresolved": pct})
        print(f"    rho={rho:.2f}: {n_unresolved}/{len(pair_data)} unresolved ({pct:.1f}%)")

    print()
    print(f"    Independent (rho=0, what's actually used in EVIDENCE_TABLE.md/A4): "
          f"{sensitivity[0]['n_unresolved']}/{len(pair_data)} ({sensitivity[0]['pct_unresolved']:.1f}%)")
    print(f"    Worst-case / fully-correlated (rho=1, upper bound on possible benefit): "
          f"{sensitivity[-1]['n_unresolved']}/{len(pair_data)} ({sensitivity[-1]['pct_unresolved']:.1f}%)")
    delta = sensitivity[0]['n_unresolved'] - sensitivity[-1]['n_unresolved']
    print(f"    Maximum POSSIBLE change if correlation were perfect: {delta} pairs "
          f"({100*delta/len(pair_data):.1f} pts) -- an upper bound on sensitivity, not an estimate of it.")

    # ---- (C) Required additional-n for a usable rho estimate ----
    print()
    print("-" * 78)
    print("REQUIRED ADDITIONAL LABELS for a usable (non-degenerate) correlation estimate")
    print("-" * 78)
    target_events = 20  # informal rule of thumb for a stable 2x2-style association estimate
    p_assumed = 0.03  # the pooled anchor already used throughout this project
    p_either_wrong_assumed = 2 * p_assumed - p_assumed**2
    required_paired_n = target_events / p_either_wrong_assumed
    ratio_paired_to_raw = n_paired / 69  # this audit's own paired:raw ratio (51 paired from 69 raw)
    required_raw_n = required_paired_n / ratio_paired_to_raw
    print(f"Rule: to fit even a coarse 2x2 (both-wrong vs either-wrong) association, need on the")
    print(f"order of {target_events} either-wrong events (not a formal power target -- a minimum")
    print(f"cell-count convention, stated as such).")
    print(f"At the pooled p~{p_assumed} (implies P(either-wrong)~{p_either_wrong_assumed:.4f}):")
    print(f"  required paired (model-pair, same-item) observations: {required_paired_n:.0f}")
    print(f"  at this audit's own paired:raw ratio ({n_paired}/69 = {ratio_paired_to_raw:.3f}):")
    print(f"  required raw audited rows: ~{required_raw_n:.0f} (vs. 69 actually audited)")
    print(f"  i.e. roughly {required_raw_n/69:.1f}x the current T-C audit size.")

    out = {
        "real_audit_bound": {
            "n_paired": n_paired, "x_either_wrong": x_either_wrong,
            "upper_95_either_wrong": upper_either_wrong,
            "implied_p_upper_rho0": p_upper_indep, "implied_p_upper_rho1": p_upper_shared,
        },
        "sensitivity_to_rho": sensitivity,
        "n_pairs_in_sensitivity": len(pair_data),
        "max_possible_pairs_changed_by_correlation": delta,
        "required_additional_labels": {
            "target_either_wrong_events": target_events,
            "assumed_p": p_assumed,
            "required_paired_n": required_paired_n,
            "required_raw_audit_n": required_raw_n,
            "current_raw_audit_n": 69,
            "multiplier_vs_current": required_raw_n / 69,
        },
    }
    with open("results/flipbudget/tc_correlated_error_bound.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/tc_correlated_error_bound.json")


if __name__ == "__main__":
    main()
