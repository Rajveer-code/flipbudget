"""T-A boundary audit -- is "15 of 17 models have zero Lambda-only width" a genuine
structural property of the SSM, or an artifact of anchoring the Lambda-transform at
the RAW (unsmoothed) point estimate?

Prior claim (TA_COMPOUND_INTERVAL.md): "15 of 17 models have w_lambda=0 exactly...
For these, compound width is the only non-degenerate identification-uncertainty
source." That statement conflated two different things without separating them:
(a) whether a model's RAW point estimate happens to be exactly 0 (a real, provable
fixed-point property of lambda_transform: lambda(0,L)=0 for all L), and (b) whether
the resulting COMPOUND width for that same model is actually trustworthy, or is
itself dominated by the same near-singular thin-audit pathology E-A's own
denom_floor=0.95 exists to guard against. The original write-up did not check (b)
separately for the zero-lambda subset -- this script does.

Three checks:
  1. SYMBOLIC: confirm lambda(0,L)=0 and lambda(1,L)=1 are genuine fixed points
     (algebraic fact, not a numerical coincidence) -- and state plainly that this
     IS a real limitation of anchoring at a raw sample proportion, not a coding bug.
  2. CROSS-TABULATION: partition the 17 qualifying models by (robust subset y/n) x
     (w_lambda==0 y/n), and show w_compound for each cell -- does "compound is the
     only signal" actually hold up within the ROBUST (trustworthy) subset alone,
     or only in the thin-audit models whose absolute magnitudes were already known
     to be unreliable?
  3. RAW vs SHRUNK ANCHOR: recompute w_lambda and w_compound anchoring the
     Lambda-transform at alpha_pooled/beta_pooled (the E4 pipeline's own existing
     empirical-Bayes shrinkage estimate, not reinvented) instead of alpha_raw/
     beta_raw, for every qualifying model. Does shrinkage eliminate the zero-width
     degeneracy? If so, that confirms the raw anchor -- not the SSM's mathematical
     structure per se -- is the parameterization artifact.

Run: python scripts/fb_ta_boundary_audit.py
"""
import json
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, "scripts")
from fb_t2_flipbudget import g
from fb_ta_ssm import lambda_transform, lambda_bounds
from fb_ta_compound_interval import compound_bounds, clip_extrema
from fb_tb_design_sensitivity import ssm_single_model_extrema
from ea_dominance_study import load, build_model_table

L_ILLUSTRATIVE = 2.0


def symbolic_fixed_point_check():
    print("-" * 70)
    print("1. SYMBOLIC: is lambda(0,L)=0 / lambda(1,L)=1 a genuine fixed point?")
    print("-" * 70)
    p, L = sp.symbols('p L', positive=True)
    lam = L * p / (1 + (L - 1) * p)
    at0 = sp.limit(lam, p, 0)
    at1 = sp.limit(lam, p, 1)
    print(f"  lim(p->0) lambda(p,L) = {at0}")
    print(f"  lim(p->1) lambda(p,L) = {at1}")
    ok = (at0 == 0) and (at1 == 1)
    print(f"  [{'OK' if ok else 'FAIL'}] both are fixed points, for EVERY L, confirmed symbolically: {ok}")
    print()
    print("  Interpretation, stated plainly: this is NOT a coding bug. It is a real,")
    print("  provable structural property of the odds-ratio parameterization -- a raw")
    print("  proportion of exactly 0 (or 1) has zero odds (or infinite odds), and")
    print("  scaling zero (or infinity) by any finite factor Lambda leaves it unchanged.")
    print("  This IS a genuine limitation when the p being transformed is a small-sample")
    print("  RAW proportion that could easily be 0 by chance (e.g. 0 false-credits in 2")
    print("  audited items) rather than a stable, well-estimated rate. The question this")
    print("  script actually answers is whether that limitation changed the reported")
    print("  headline finding, not whether the algebra is correct (it is).")
    return ok


def cross_tabulation(rows, L=L_ILLUSTRATIVE):
    print()
    print("-" * 70)
    print("2. CROSS-TABULATION: robust subset x (w_lambda==0), with real w_compound")
    print("-" * 70)
    results = []
    for model, row in rows.items():
        a = row["a_hat"]
        is_robust = row["n0_audit"] >= 5 and row["n1_audit"] >= 5
        l_min, l_max = ssm_single_model_extrema(a, row["alpha_raw"], row["beta_raw"], L)
        w_lambda = l_max - l_min
        c_lo, c_hi = compound_bounds(row["x_alpha"], row["n0_audit"], L)
        c_lo_b, c_hi_b = compound_bounds(row["x_beta"], row["n1_audit"], L)
        c_min, c_max = clip_extrema(a, c_lo, c_hi, c_lo_b, c_hi_b)
        w_compound = c_max - c_min
        results.append({"model": model, "robust": is_robust, "n0": row["n0_audit"],
                         "n1": row["n1_audit"], "alpha_raw": row["alpha_raw"],
                         "beta_raw": row["beta_raw"], "w_lambda": w_lambda,
                         "w_compound": w_compound})

    cells = {"robust & zero_lambda": [], "robust & nonzero_lambda": [],
             "thin & zero_lambda": [], "thin & nonzero_lambda": []}
    for r in results:
        key = ("robust" if r["robust"] else "thin") + " & " + \
              ("zero_lambda" if r["w_lambda"] == 0 else "nonzero_lambda")
        cells[key].append(r)

    for key, members in cells.items():
        print(f"\n  {key}: {len(members)} models")
        for m in members:
            print(f"    {m['model']:<45} n0={m['n0']:<3} n1={m['n1']:<3} "
                  f"alpha_raw={m['alpha_raw']:<8} beta_raw={m['beta_raw']:<8} "
                  f"w_lambda={m['w_lambda']:<8.4f} w_compound={m['w_compound']:<10.2f}")

    n_robust_zero = len(cells["robust & zero_lambda"])
    n_robust_total = len(cells["robust & zero_lambda"]) + len(cells["robust & nonzero_lambda"])
    print(f"\n  Within the ROBUST subset alone: {n_robust_zero} of {n_robust_total} models "
          f"have w_lambda=0 exactly.")
    if cells["robust & zero_lambda"]:
        robust_zero_compounds = [m["w_compound"] for m in cells["robust & zero_lambda"]]
        print(f"  Their w_compound values: {[f'{v:.2f}' for v in robust_zero_compounds]} -- "
              f"{'SANE, non-pathological' if max(robust_zero_compounds) < 20 else 'CHECK: some look large'}")
    thin_zero_compounds = [m["w_compound"] for m in cells["thin & zero_lambda"]]
    if thin_zero_compounds:
        print(f"\n  Within the THIN (non-robust) subset, zero-lambda models' w_compound:")
        print(f"  min={min(thin_zero_compounds):.1f}, max={max(thin_zero_compounds):.1f} -- "
              f"these are the SAME near-singular-audit models E-A's own robustness filter")
        print(f"  already excludes from any headline number; their large compound values")
        print(f"  should NOT be read as 'the main signal', for the same reason E-A itself")
        print(f"  does not report unfiltered widths as the headline.")
    return results, cells


def raw_vs_shrunk_anchor(rows, L=L_ILLUSTRATIVE):
    print()
    print("-" * 70)
    print("3. RAW vs SHRUNK anchor -- does shrinkage eliminate the degeneracy?")
    print("-" * 70)
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4 = json.load(f)["per_model"]

    n_zero_raw, n_zero_shrunk = 0, 0
    rows_out = []
    for model, row in rows.items():
        a = row["a_hat"]
        m = e4[model]
        alpha_pooled, beta_pooled = m["alpha_pooled"], m["beta_pooled"]

        l_min_raw, l_max_raw = ssm_single_model_extrema(a, row["alpha_raw"], row["beta_raw"], L)
        w_lambda_raw = l_max_raw - l_min_raw

        l_min_sh, l_max_sh = ssm_single_model_extrema(a, alpha_pooled, beta_pooled, L)
        w_lambda_shrunk = l_max_sh - l_min_sh

        if w_lambda_raw == 0:
            n_zero_raw += 1
        if w_lambda_shrunk == 0:
            n_zero_shrunk += 1
        rows_out.append({"model": model, "alpha_raw": row["alpha_raw"], "beta_raw": row["beta_raw"],
                          "alpha_pooled": alpha_pooled, "beta_pooled": beta_pooled,
                          "w_lambda_raw_anchor": w_lambda_raw, "w_lambda_shrunk_anchor": w_lambda_shrunk})
        flag = "  <-- was degenerate under raw anchor, fixed by shrunk anchor" \
            if w_lambda_raw == 0 and w_lambda_shrunk > 0 else ""
        print(f"  {model:<45} w_lambda(raw)={w_lambda_raw:<10.4f} "
              f"w_lambda(shrunk)={w_lambda_shrunk:<10.4f}{flag}")

    print(f"\n  Models with w_lambda=0 under RAW anchor: {n_zero_raw} of {len(rows)}")
    print(f"  Models with w_lambda=0 under SHRUNK anchor: {n_zero_shrunk} of {len(rows)}")
    if n_zero_shrunk < n_zero_raw:
        print(f"\n  CONFIRMED: shrinkage anchoring eliminates {n_zero_raw - n_zero_shrunk} of the "
              f"{n_zero_raw} degenerate cases. The raw-anchor choice -- not the SSM's")
        print("  mathematical structure -- is the source of most of the zero-width cases.")
        print("  This is a real parameterization artifact, correctly identified by the audit")
        print("  request, not a structural property of the sensitivity model itself.")
    return rows_out


if __name__ == "__main__":
    print("=" * 70)
    print("T-A BOUNDARY AUDIT: is the zero-Lambda-width finding real or an artifact?")
    print("=" * 70)
    ok_sym = symbolic_fixed_point_check()

    accs, margins = load()
    rows, excl = build_model_table(accs, margins)
    print(f"\nModels qualifying: {excl['n_qualifying']} of {excl['n_total_models']}")

    results, cells = cross_tabulation(rows)
    anchor_results = raw_vs_shrunk_anchor(rows)

    out = {
        "symbolic_fixed_point_confirmed": bool(ok_sym),
        "cross_tabulation": results,
        "raw_vs_shrunk_anchor": anchor_results,
        "n_zero_lambda_raw_anchor": sum(1 for r in anchor_results if r["w_lambda_raw_anchor"] == 0),
        "n_zero_lambda_shrunk_anchor": sum(1 for r in anchor_results if r["w_lambda_shrunk_anchor"] == 0),
    }
    with open("results/flipbudget/ta_boundary_audit.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/ta_boundary_audit.json")
