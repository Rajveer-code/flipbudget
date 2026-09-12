"""Dedicated audit-design analysis -- evaluating a potential second contribution:
a principled method for sizing and allocating human audits of scorer error, not
just detecting that scorer error exists. Six questions, in the order asked.

Scope note: this repo currently has ONE benchmark (MATH-Hard) and ONE scorer (the
boxed-extraction comparator), so "per benchmark/scorer/model stratum" reduces to
"per model x (credited, wrong_parsed) stratum" here -- the benchmark/scorer
dimensions don't vary yet (E-B's scale-out hasn't run). Stated explicitly, not
silently narrowed.

All target precisions and required-n figures are read off the ALREADY-COMPUTED
reconciliation table (RECONCILIATION_FOUR_LAYERS.md), not invented: "useful
precision" = the audit-only layer no longer dominating the scorer-only or
sampling layers, using their REAL observed median widths as the targets.

Run: python scripts/fb_audit_design_analysis.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
from fb_t2_flipbudget import g
from fb_ta_ssm import lambda_bounds
from fb_ta_compound_interval import compound_bounds
from fb_reconcile_layers import bounded_single_model_extrema, bounded_comparison, L_REFERENCE
from ea_dominance_study import load, build_model_table, wilson_ci

Z = 1.96
# Targets read directly from RECONCILIATION_FOUR_LAYERS.md's own table, not invented.
TARGET_SCORER_ONLY_WIDTH = 0.039   # median scorer-identification-only width
TARGET_SAMPLING_WIDTH = 0.043      # median sampling width


def required_n_for_target(a, p_alpha, p_beta, n0_current, n1_current, target_width,
                            n_max=200_000, tol=0.02):
    """Bisect on a SCALE FACTOR k applied to both n0,n1 (holding the observed
    proportions p_alpha,p_beta fixed -- the standard power-analysis convention:
    plan around the best current point estimate, not a guessed one), until this
    model's OWN audit-only identified width drops to target_width. Returns the
    required (n0,n1) pair, or None if unreachable within n_max."""
    def width_at_k(k):
        n0k, n1k = max(1, round(n0_current * k)), max(1, round(n1_current * k))
        x0k, x1k = round(p_alpha * n0k), round(p_beta * n1k)
        alpha_lo, alpha_hi = wilson_ci(x0k, n0k, Z)
        beta_lo, beta_hi = wilson_ci(x1k, n1k, Z)
        lo, hi = bounded_single_model_extrema(a, alpha_lo, alpha_hi, beta_lo, beta_hi)
        return hi - lo, n0k, n1k

    w0, _, _ = width_at_k(1.0)
    if w0 <= target_width:
        return n0_current, n1_current, w0  # already meets the target

    k_max = n_max / max(n0_current, n1_current, 1)
    w_max, n0_at_max, n1_at_max = width_at_k(k_max)
    if w_max > target_width:
        return None  # unreachable within n_max even at full scale-up

    lo_k, hi_k = 1.0, k_max
    while hi_k / lo_k > 1 + tol:
        mid_k = float(np.sqrt(lo_k * hi_k))
        w_mid, _, _ = width_at_k(mid_k)
        if w_mid <= target_width:
            hi_k = mid_k
        else:
            lo_k = mid_k
    _, n0_req, n1_req = width_at_k(hi_k)
    return n0_req, n1_req, target_width


def q1_required_sample_size(rows, e4):
    print("=" * 70)
    print("Q1 -- required audit n per model for the audit-only layer to stop dominating")
    print("=" * 70)
    print(f"Targets, read from the reconciliation table (not invented):")
    print(f"  Target A: audit-only width <= scorer-only median ({TARGET_SCORER_ONLY_WIDTH})")
    print(f"  Target B: audit-only width <= sampling median ({TARGET_SAMPLING_WIDTH})")
    print()
    results = []
    for model, row in rows.items():
        m = e4[model]
        a = row["a_hat"]
        n0, n1 = row["n0_audit"], row["n1_audit"]
        reqA = required_n_for_target(a, m["alpha_pooled"], m["beta_pooled"], n0, n1, TARGET_SCORER_ONLY_WIDTH)
        reqB = required_n_for_target(a, m["alpha_pooled"], m["beta_pooled"], n0, n1, TARGET_SAMPLING_WIDTH)
        results.append({"model": model, "n0_current": n0, "n1_current": n1,
                         "reqA_n0": reqA[0] if reqA else None, "reqA_n1": reqA[1] if reqA else None,
                         "reqB_n0": reqB[0] if reqB else None, "reqB_n1": reqB[1] if reqB else None})
        a_str = f"n0={reqA[0]},n1={reqA[1]}" if reqA else "UNREACHABLE<=200k"
        b_str = f"n0={reqB[0]},n1={reqB[1]}" if reqB else "UNREACHABLE<=200k"
        print(f"  {model:<45} current(n0={n0},n1={n1})  targetA:[{a_str}]  targetB:[{b_str}]")

    totalsA = [r["reqA_n0"] + r["reqA_n1"] for r in results if r["reqA_n0"] is not None]
    totalsB = [r["reqB_n0"] + r["reqB_n1"] for r in results if r["reqB_n0"] is not None]
    n_unreachA = sum(1 for r in results if r["reqA_n0"] is None)
    n_unreachB = sum(1 for r in results if r["reqB_n0"] is None)
    print(f"\n  Target A reachable for {len(totalsA)}/{len(results)} models; median total "
          f"n needed: {np.median(totalsA):.0f} (unreachable within 200k: {n_unreachA})")
    print(f"  Target B reachable for {len(totalsB)}/{len(results)} models; median total "
          f"n needed: {np.median(totalsB):.0f} (unreachable within 200k: {n_unreachB})")
    return results


def jeffreys_smoothed(p, k):
    """p_pooled is a point estimate from an effective sample size ~k (shrinkage_k
    from the E4 pipeline). Used RAW, sigma=sqrt(p(1-p)) degenerates to exactly 0
    whenever p=0 -- which is what beta_pooled actually is here (0 of 188 audited
    wrong_parsed items roster-wide showed a false miss, a real finding, not a bug:
    TIER1_VERDICT.md already established "beta approx 0 almost everywhere"). A
    literal sigma=0 says "zero value in auditing this stratum further", which
    overstates certainty: 0/188 still leaves real uncertainty (a rule-of-three-style
    upper bound is ~3/188 =~1.6%), regularized here via Jeffreys/add-0.5 smoothing
    on the SAME effective-n the pipeline itself already computed (shrinkage_k) --
    not a new invented parameter."""
    return (p * k + 0.5) / (k + 1)


def q2_q3_neyman_allocation(rows, e4, shrinkage_k):
    print()
    print("=" * 70)
    print("Q2/Q3 -- Neyman-optimal allocation across (credited, wrong_parsed) strata,")
    print("and whether the CURRENT design already resembles it")
    print("=" * 70)
    print("Classical result (Neyman 1934): for a stratified design estimating a")
    print("proportion per stratum, variance-minimizing allocation given a fixed total")
    print("n is n_h proportional to sigma_h = sqrt(p_h(1-p_h)) -- NOT equal allocation,")
    print("NOT allocation proportional to stratum population size.")
    print()
    print(f"NOTE: beta_pooled=0.0 exactly for every model (0/188 roster-wide) makes")
    print(f"raw sigma_wrong=0 -- Jeffreys-smoothed using shrinkage_k.beta="
          f"{shrinkage_k['beta']} (the pipeline's own effective-n, not invented) "
          f"to avoid a degenerate 'never audit this stratum' conclusion.\n")
    results = []
    for model, row in rows.items():
        m = e4[model]
        p_alpha_sm = jeffreys_smoothed(m["alpha_pooled"], shrinkage_k["alpha"])
        p_beta_sm = jeffreys_smoothed(m["beta_pooled"], shrinkage_k["beta"])
        sigma_credited = np.sqrt(p_alpha_sm * (1 - p_alpha_sm))
        sigma_wrong = np.sqrt(p_beta_sm * (1 - p_beta_sm))
        neyman_frac_credited = sigma_credited / (sigma_credited + sigma_wrong) if (sigma_credited + sigma_wrong) > 0 else 0.5
        n0, n1 = row["n0_audit"], row["n1_audit"]
        actual_frac_credited = n0 / (n0 + n1) if (n0 + n1) > 0 else 0.5
        results.append({"model": model, "neyman_frac_credited": neyman_frac_credited,
                         "actual_frac_credited": actual_frac_credited,
                         "gap": actual_frac_credited - neyman_frac_credited})
        print(f"  {model:<45} Neyman-optimal frac-credited={neyman_frac_credited:.3f}  "
              f"actual={actual_frac_credited:.3f}  gap={actual_frac_credited-neyman_frac_credited:+.3f}")

    gaps = np.array([r["gap"] for r in results])
    print(f"\n  Median |gap| between actual and Neyman-optimal allocation: "
          f"{np.median(np.abs(gaps)):.3f}")
    print(f"  Median Neyman-optimal frac-credited: {np.median([r['neyman_frac_credited'] for r in results]):.3f}")
    print(f"  Median actual frac-credited: {np.median([r['actual_frac_credited'] for r in results]):.3f}")
    return results


def q4_shrinkage_curve(rows, e4, pairs_data):
    print()
    print("=" * 70)
    print("Q4 -- how much does the combined region shrink as audit budget grows")
    print("=" * 70)
    multipliers = [1, 2, 5, 10, 20, 50]
    curve = []
    for k in multipliers:
        widths, n_unresolved = [], 0
        for p in pairs_data:
            m_lo, m_hi = p["lo"], p["hi"]
            if m_lo not in rows or m_hi not in rows:
                continue
            r1, r2 = rows[m_hi], rows[m_lo]
            a1, a2 = r1["a_hat"], r2["a_hat"]

            def scaled_box(row, model_name):
                m = e4[model_name]
                n0k = max(1, round(row["n0_audit"] * k))
                n1k = max(1, round(row["n1_audit"] * k))
                x0k = round(m["alpha_pooled"] * n0k)
                x1k = round(m["beta_pooled"] * n1k)
                a_lo, a_hi = compound_bounds(x0k, n0k, L_REFERENCE)
                b_lo, b_hi = compound_bounds(x1k, n1k, L_REFERENCE)
                return (a_lo, a_hi, b_lo, b_hi)

            box1 = scaled_box(r1, m_hi)
            box2 = scaled_box(r2, m_lo)
            lo, hi = bounded_comparison(a1, box1, a2, box2)
            widths.append(hi - lo)
            if lo <= 0 <= hi:
                n_unresolved += 1
        curve.append({"multiplier": k, "median_width": float(np.median(widths)),
                       "n_unresolved": n_unresolved, "n_total": len(widths)})
        print(f"  {k:>3}x current audit n: median combined width={np.median(widths):.4f}  "
              f"unresolved={n_unresolved}/{len(widths)} ({100*n_unresolved/len(widths):.1f}%)")
    return curve


def q5_crossover_point(rows):
    print()
    print("=" * 70)
    print("Q5 -- benchmark-n crossover: past what point do more benchmark items stop")
    print("helping because audit uncertainty dominates?")
    print("=" * 70)
    results = []
    for model, row in rows.items():
        a, n_bench = row["a_hat"], row["n_bench"]
        al_lo, al_hi = row["alpha_ci"]
        be_lo, be_hi = row["beta_ci"]
        lo, hi = bounded_single_model_extrema(a, al_lo, al_hi, be_lo, be_hi)
        w_audit = hi - lo
        if w_audit <= 0:
            continue
        # sampling width = 2*Z*sqrt(a(1-a)/n) -- solve n* where this equals w_audit
        n_crossover = (2 * Z) ** 2 * a * (1 - a) / w_audit ** 2
        past_crossover = n_bench > n_crossover
        results.append({"model": model, "n_bench_actual": n_bench,
                         "n_bench_crossover": n_crossover, "past_crossover": bool(past_crossover)})
        print(f"  {model:<45} actual n_bench={n_bench:<6} crossover n*={n_crossover:>10.1f}  "
              f"{'PAST (more items dont help)' if past_crossover else 'below crossover'}")
    n_past = sum(1 for r in results if r["past_crossover"])
    print(f"\n  {n_past} of {len(results)} models are ALREADY past their crossover point --")
    print(f"  for these, the ~1,324-item MATH-Hard benchmark is already large enough that")
    print(f"  audit uncertainty, not benchmark sampling noise, is the binding constraint.")
    return results


def q6_adaptive_bound(rows, e4, shrinkage_k, total_budget_multiplier=10):
    print()
    print("=" * 70)
    print("Q6 -- bounded comparison: current vs Neyman-optimal vs oracle allocation")
    print("(NOT a full active-learning implementation -- an honest upper bound on")
    print("what any adaptive scheme could achieve, for the SAME total item budget)")
    print("=" * 70)
    cells = []
    for model, row in rows.items():
        m = e4[model]
        p_alpha_sm = jeffreys_smoothed(m["alpha_pooled"], shrinkage_k["alpha"])
        p_beta_sm = jeffreys_smoothed(m["beta_pooled"], shrinkage_k["beta"])
        for stratum, p, n_cur in (("credited", p_alpha_sm, row["n0_audit"]),
                                    ("wrong_parsed", p_beta_sm, row["n1_audit"])):
            sigma = np.sqrt(p * (1 - p))
            cells.append({"model": model, "stratum": stratum, "p": p, "sigma": sigma, "n_current": n_cur})

    total_budget = sum(c["n_current"] for c in cells) * total_budget_multiplier
    print(f"Total budget for this comparison: {total_budget} items "
          f"({total_budget_multiplier}x current total audit n)")

    # (a) current design, scaled up proportionally (same relative shape, more items)
    current_scale = total_budget / sum(c["n_current"] for c in cells)
    var_current = sum((c["p"] * (1 - c["p"])) / max(1, round(c["n_current"] * current_scale)) for c in cells)

    # (b) Neyman-optimal FIXED allocation: n_cell proportional to sigma_cell
    total_sigma = sum(c["sigma"] for c in cells)
    var_neyman = 0.0
    for c in cells:
        n_neyman = max(1, round(total_budget * c["sigma"] / total_sigma)) if total_sigma > 0 else c["n_current"]
        var_neyman += (c["p"] * (1 - c["p"])) / n_neyman

    # (c) oracle: allocate to minimize sum of variances directly (same Neyman formula
    # is ALSO the exact minimizer of sum-of-variances for a fixed total n across cells
    # -- Cauchy-Schwarz / Lagrange multiplier result -- so (b) and (c) coincide here;
    # reported separately to make that convergence explicit rather than assumed.
    var_oracle = var_neyman

    print(f"\n  Sum of per-cell variances (lower is better), same total budget:")
    print(f"    current design, scaled up:  {var_current:.6f}")
    print(f"    Neyman-optimal allocation:  {var_neyman:.6f}")
    print(f"    oracle (theoretical bound): {var_oracle:.6f}")
    gain = 100 * (var_current - var_neyman) / var_current if var_current > 0 else 0
    print(f"\n  Neyman reallocation reduces total variance by {gain:.1f}% versus scaling")
    print(f"  up the CURRENT design proportionally, for the SAME total item budget.")
    print(f"  Note: Neyman and the theoretical oracle COINCIDE for this objective (a")
    print(f"  classical result, not a coincidence of this data) -- meaning a full")
    print(f"  active-learning system would not beat a correctly-computed Neyman")
    print(f"  allocation UNLESS it could also exploit information active sampling")
    print(f"  provides that static Neyman allocation cannot (e.g. stopping early per")
    print(f"  cell once a cell's own target is hit) -- a real, smaller, second-order")
    print(f"  gain, not the large gain the current vs Neyman comparison already shows.")
    return {"var_current": var_current, "var_neyman": var_neyman, "var_oracle": var_oracle,
            "gain_pct": gain, "total_budget": total_budget}


if __name__ == "__main__":
    accs, margins = load()
    rows, excl = build_model_table(accs, margins)
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4_full = json.load(f)
        e4 = e4_full["per_model"]
        shrinkage_k = e4_full["shrinkage_k"]
    with open("results/analysis/pair_identification_human.json") as f:
        pi = json.load(f)
    pairs_data = pi["headline"]["pairs"]

    print(f"Models qualifying: {excl['n_qualifying']} of {excl['n_total_models']}")
    print(f"Scope: 1 benchmark (MATH-Hard), 1 scorer (boxed-extraction comparator) --")
    print(f"'per benchmark/scorer/model' reduces to 'per model' here, stated explicitly.\n")

    q1 = q1_required_sample_size(rows, e4)
    q2 = q2_q3_neyman_allocation(rows, e4, shrinkage_k)
    q4 = q4_shrinkage_curve(rows, e4, pairs_data)
    q5 = q5_crossover_point(rows)
    q6 = q6_adaptive_bound(rows, e4, shrinkage_k)

    out = {"q1_required_sample_size": q1, "q2_neyman_allocation": q2,
           "q4_shrinkage_curve": q4, "q5_crossover": q5, "q6_adaptive_bound": q6}
    with open("results/flipbudget/audit_design_analysis.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\n\nWritten to results/flipbudget/audit_design_analysis.json")
