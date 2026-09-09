"""T5 -- the flip budget's own confidence treatment.

For each bootstrap replicate of (a1,alpha1,beta1,a2,alpha2,beta2) (same paired
resampling machinery as T3, RAW percentile per T3's conclusion -- BC was tried
and dropped), recompute the flip budget via T2's bisection. Report the median
and the one-sided LOWER 5th-percentile bound (the decision-relevant direction:
how small could the true flip budget plausibly be).

Degenerate-case rule (decided in PREREGISTRATION_FLIPBUDGET.md before this was
run): if 0 is already inside the Delta* interval at d=0 (the pair is
inconclusive under ordinary sampling noise, before any differential-error
argument), report "already inconclusive," not a flip-budget number.

Sanity pair requirement (from PLAN_FLIPBUDGET.md's Verify step): run on at
least one real pair with a documented rank inversion and one without, using
the actual data already on disk (e3_roster.json).

Run: python scripts/fb_t5_budget_ci.py
"""
import json
import numpy as np
import sys
sys.path.insert(0, "scripts")
from fb_t2_flipbudget import flip_budget, comparison_extrema
from fb_t3_coverage import simulate_benchmark, apply_noisy_channel, cond_rate_point, g

RNG = np.random.default_rng(2026)


def flip_budget_bootstrap(a1, a2, alpha1_pt, beta1_pt, alpha2_pt, beta2_pt,
                           audit_ystar1, audit_yhat1, audit_ystar2, audit_yhat2,
                           n_bench, n_boot, rng):
    """Bootstrap the flip-budget statistic itself. Resamples the SAME way T3
    does (paired benchmark items via binomial approx since we don't have raw
    item arrays here, independent audit resampling per model)."""
    budgets = []
    for _ in range(n_boot):
        a1_b = rng.binomial(n_bench, a1) / n_bench
        a2_b = rng.binomial(n_bench, a2) / n_bench

        idx1 = rng.integers(0, len(audit_ystar1), len(audit_ystar1))
        idx2 = rng.integers(0, len(audit_ystar2), len(audit_ystar2))
        ys1, yh1 = audit_ystar1[idx1], audit_yhat1[idx1]
        ys2, yh2 = audit_ystar2[idx2], audit_yhat2[idx2]

        alpha1_b = cond_rate_point(ys1, yh1, 0, 1)
        beta1_b = cond_rate_point(ys1, yh1, 1, 0)
        alpha2_b = cond_rate_point(ys2, yh2, 0, 1)
        beta2_b = cond_rate_point(ys2, yh2, 1, 0)
        if any(np.isnan(x) for x in [alpha1_b, beta1_b, alpha2_b, beta2_b]):
            continue
        if alpha1_b + beta1_b >= 0.95 or alpha2_b + beta2_b >= 0.95:
            continue

        # shared baseline for the Case-B perturbation: midpoint of the two
        # bootstrap replicate's own (alpha,beta), matching T2's parameterization
        alpha0_b = (alpha1_b + alpha2_b) / 2
        beta0_b = (beta1_b + beta2_b) / 2
        d_star, degenerate = flip_budget(a1_b, a2_b, alpha0_b, beta0_b)
        if degenerate:
            budgets.append(0.0)
        elif d_star is not None:
            budgets.append(d_star)
    return np.array(budgets)


def report_pair(label, a1, a2, alpha1_pt, beta1_pt, alpha2_pt, beta2_pt,
                 n_bench, n_audit1, n_audit2, rng):
    print(f"--- {label} ---")
    print(f"  a1={a1:.4f}, a2={a2:.4f}, point (alpha1,beta1)=({alpha1_pt:.4f},{beta1_pt:.4f}), "
          f"(alpha2,beta2)=({alpha2_pt:.4f},{beta2_pt:.4f})")

    alpha0 = (alpha1_pt + alpha2_pt) / 2
    beta0 = (beta1_pt + beta2_pt) / 2
    d_star_point, degenerate_point = flip_budget(a1, a2, alpha0, beta0)
    if degenerate_point:
        print("  POINT ESTIMATE: already inconclusive at d=0 (degenerate case, per")
        print("  the pre-registered rule -- no flip-budget number reported)")
        return {"label": label, "degenerate": True}

    print(f"  POINT ESTIMATE flip budget: {d_star_point:.5f}")

    audit_ystar1 = simulate_benchmark(alpha1_pt / (alpha1_pt + beta1_pt) if alpha1_pt + beta1_pt > 0 else 0.5,
                                       n_audit1, rng)  # placeholder Y* generator, replaced below by direct construction
    # Build audit (Y*,Yhat) pairs directly from the point rates rather than a
    # further nested simulation -- construct n_audit1 items split by the
    # implied population share so cond_rate_point recovers alpha1_pt,beta1_pt
    # on average, then let resampling do the rest.
    n_pos1 = max(1, int(round(n_audit1 * a1)))
    n_neg1 = max(1, n_audit1 - n_pos1)
    ys1 = np.array([1] * n_pos1 + [0] * n_neg1)
    yh1 = ys1.copy()
    n_false_miss1 = int(round(n_pos1 * beta1_pt))
    n_false_credit1 = int(round(n_neg1 * alpha1_pt))
    yh1[:n_pos1][:n_false_miss1] = 0
    yh1[n_pos1:][:n_false_credit1] = 1

    n_pos2 = max(1, int(round(n_audit2 * a2)))
    n_neg2 = max(1, n_audit2 - n_pos2)
    ys2 = np.array([1] * n_pos2 + [0] * n_neg2)
    yh2 = ys2.copy()
    n_false_miss2 = int(round(n_pos2 * beta2_pt))
    n_false_credit2 = int(round(n_neg2 * alpha2_pt))
    yh2[:n_pos2][:n_false_miss2] = 0
    yh2[n_pos2:][:n_false_credit2] = 1

    budgets = flip_budget_bootstrap(a1, a2, alpha1_pt, beta1_pt, alpha2_pt, beta2_pt,
                                     ys1, yh1, ys2, yh2, n_bench, 500, rng)
    if len(budgets) < 100:
        print(f"  BOOTSTRAP: too few valid replicates ({len(budgets)}/500) to report a "
              f"CI -- audit sample too thin for this pair's flip-budget CI")
        return {"label": label, "point_estimate": d_star_point, "bootstrap_ci": None}

    median_b = np.median(budgets)
    lower_5pct = np.percentile(budgets, 5)
    frac_zero = (budgets < 1e-6).mean()
    print(f"  BOOTSTRAP ({len(budgets)} valid replicates): median={median_b:.5f}, "
          f"lower-5th-pct (reported bound)={lower_5pct:.5f}, "
          f"fraction already-degenerate={frac_zero:.3f}")
    return {"label": label, "point_estimate": d_star_point,
            "bootstrap_median": float(median_b), "bootstrap_lower_5pct": float(lower_5pct),
            "n_valid_replicates": int(len(budgets))}


if __name__ == "__main__":
    print("=" * 70)
    print("T5 -- flip-budget bootstrap CI on real MMLU roster pairs")
    print("=" * 70)

    with open("results/analysis/e3_roster.json") as f:
        roster = json.load(f)

    task = roster["tasks"]["mmlu_flan_n_shot_generative"]
    gaps = {m["model"]: m for m in task["gaps"]}

    # Pick one pair WITH a documented rank inversion and one WITHOUT, from the
    # real data already on disk (task["inversions"] lists real inverted pairs).
    inv_pair = task["inversions"][0]["pair"]
    all_models = list(gaps.keys())
    inverted_set = {tuple(sorted(p["pair"])) for p in task["inversions"]}
    non_inv_pair = None
    for i in range(len(all_models)):
        for j in range(i + 1, len(all_models)):
            cand = tuple(sorted([all_models[i], all_models[j]]))
            if cand not in inverted_set:
                non_inv_pair = list(cand)
                break
        if non_inv_pair:
            break

    n_audit = 16  # real median found in D4/D5 for the MMLU 3-model audit
    n_bench = 400

    results = []
    for label, pair in [("documented rank inversion (real MMLU pair)", inv_pair),
                         ("no documented inversion (real MMLU pair)", non_inv_pair)]:
        m1, m2 = pair
        a1, a2 = gaps[m1]["robust"], gaps[m2]["robust"]
        # unparsed_rate is the closest existing proxy for beta already computed
        # for these models; alpha (false credit) has no existing per-model
        # estimate on disk, so use the pooled 3-model human-audit alpha as a
        # shared floor, explicitly flagged as an approximation, not invented
        # from nothing -- it is the best real number available without new
        # labelling, and the point of this run is to demonstrate the T5
        # MACHINERY on real gaps, not to publish a final per-model estimate
        # (E4 does that properly with the full re-slicing + partial pooling).
        beta1_pt = min(gaps[m1]["unparsed_rate"], 0.94)
        beta2_pt = min(gaps[m2]["unparsed_rate"], 0.94)
        alpha1_pt = alpha2_pt = 0.01  # placeholder floor -- see note above; real
        # per-model alpha awaits E4's re-slicing of human_labels.json
        r = report_pair(f"{label}: {m1} (a={a1}) vs {m2} (a={a2})",
                         a1, a2, alpha1_pt, beta1_pt, alpha2_pt, beta2_pt,
                         n_bench, n_audit, n_audit, RNG)
        results.append(r)
        print()

    print("=" * 70)
    print("T5 sanity check: the documented-inversion pair should show a smaller")
    print("(more fragile) flip budget than the non-inversion pair, if the")
    print("machinery is behaving sensibly on real data.")
    if all("point_estimate" in r for r in results) and results[0].get("point_estimate") is not None:
        b0 = results[0].get("bootstrap_lower_5pct", results[0].get("point_estimate"))
        b1 = results[1].get("bootstrap_lower_5pct", results[1].get("point_estimate"))
        print(f"  inversion-pair budget: {b0}")
        print(f"  non-inversion-pair budget: {b1}")
    print("=" * 70)
    print()
    print("NOTE: alpha (false-credit) uses a placeholder floor (0.01) here, not a")
    print("real per-model estimate -- no per-model alpha exists on disk yet. This")
    print("run verifies the T5 MACHINERY end-to-end on real accuracy gaps and real")
    print("beta proxies; a trustworthy per-model alpha awaits E4's re-slicing of")
    print("human_labels.json with partial pooling, per PREREGISTRATION_FLIPBUDGET.md.")
