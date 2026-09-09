"""E1 Case B -- the real differential flip-budget pilot on MATH-Hard.

Per-model accuracy a_hat_j via a design-weighted (Horvitz-Thompson) estimator
over the 400-item stratified audit sample, using the EXACT cell-level
population/sample-target counts already committed in mathhard_frame.json
(the same design-weight machinery PREREGISTRATION_AUDIT.md established, not
a re-derivation): weight_i = population_by_cell[stratum_i][subject_i,quartile_i]
/ sample_target_by_cell[stratum_i][subject_i,quartile_i]; a_hat_j = weighted
mean of 1(stratum_i == credited) over model j's audited items.

Sanity check before trusting anything: worked_example_human in
pair_identification_human.json anchors two models -- Qwen/Qwen2-72B-Instruct
should be near the roster's reported max (0.351) and databricks/dolly-v2-12b
near the reported min (0.0). Checked before the real Case B run, not after.

Then: real per-model alpha_pooled, beta_pooled from E4's output, real
design-weighted a_hat per model, and T2's actual flip-budget bisection run
on all 378 real pairs.

Run: python scripts/fb_e1_case_b.py
"""
import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, "scripts")
from fb_t2_flipbudget import flip_budget


def load():
    with open("results/analysis/mathhard_frame.json") as f:
        frame = json.load(f)
    with open("results/analysis/mathhard_labelling_key.json") as f:
        key = json.load(f)
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4 = json.load(f)
    with open("results/analysis/pair_identification_human.json") as f:
        pi = json.load(f)
    return frame, key, e4, pi


def design_weight(frame, stratum, subject, quartile):
    cell = f"{subject}|q{quartile}"
    pop = frame["targets_by_stratum"][stratum]["population_by_cell"].get(cell)
    tgt = frame["targets_by_stratum"][stratum]["sample_target_by_cell"].get(cell)
    if pop is None or tgt is None or tgt == 0:
        return None
    return pop / tgt


def per_model_accuracy(frame, key):
    by_model = defaultdict(list)
    for item in key:
        w = design_weight(frame, item["stratum"], item["subject"], item["quartile"])
        if w is None:
            continue
        is_credited = 1.0 if item["stratum"] == "credited" else 0.0
        by_model[item["model"]].append((w, is_credited))

    out = {}
    for model, pairs in by_model.items():
        weights = np.array([p[0] for p in pairs])
        credited = np.array([p[1] for p in pairs])
        a_hat = np.average(credited, weights=weights)
        out[model] = {"a_hat_design_weighted": float(a_hat), "n_audited": len(pairs)}
    return out


if __name__ == "__main__":
    print("=" * 70)
    print("E1 Case B -- real differential flip-budget pilot, MATH-Hard")
    print("=" * 70)
    frame, key, e4, pi = load()

    accs = per_model_accuracy(frame, key)

    print("Sanity check against worked_example_human's known anchors:")
    q72 = accs.get("Qwen/Qwen2-72B-Instruct")
    dolly = accs.get("databricks/dolly-v2-12b")
    print(f"  Qwen/Qwen2-72B-Instruct: a_hat={q72['a_hat_design_weighted']:.4f} "
          f"(roster max reported: 0.3512)")
    print(f"  databricks/dolly-v2-12b: a_hat={dolly['a_hat_design_weighted']:.4f} "
          f"(roster min reported: 0.0000)")
    plausible = (0.20 < q72["a_hat_design_weighted"] < 0.50
                 and dolly["a_hat_design_weighted"] < q72["a_hat_design_weighted"])
    print(f"  [{'OK' if plausible else 'FAIL'}] Qwen2-72B clearly above dolly-v2-12b, "
          f"in the reported range: {plausible}")
    if not plausible:
        print("STOPPING: design-weighted accuracy estimator does not pass the sanity")
        print("check against the two known anchors -- do not trust the pilot below.")
        raise SystemExit(1)
    print()

    per_model_margins = e4["per_model"]

    results = []
    n_flippable = 0
    n_already_degenerate = 0
    n_missing_data = 0
    for p in pi["headline"]["pairs"]:
        m_lo, m_hi = p["lo"], p["hi"]
        if m_lo not in accs or m_hi not in accs:
            n_missing_data += 1
            continue
        if m_lo not in per_model_margins or m_hi not in per_model_margins:
            n_missing_data += 1
            continue

        a_lo = accs[m_lo]["a_hat_design_weighted"]
        a_hi = accs[m_hi]["a_hat_design_weighted"]
        mlo, mhi = per_model_margins[m_lo], per_model_margins[m_hi]
        alpha0 = (mlo["alpha_pooled"] + mhi["alpha_pooled"]) / 2
        beta0 = (mlo["beta_pooled"] + mhi["beta_pooled"]) / 2
        if alpha0 + beta0 >= 0.95:
            n_missing_data += 1
            continue

        d_star, degenerate = flip_budget(a_hi, a_lo, alpha0, beta0)
        if degenerate:
            n_already_degenerate += 1
            results.append({"lo": m_lo, "hi": m_hi, "gap": p["gap"],
                             "degenerate": True, "flip_budget": None})
            continue
        if d_star is not None:
            n_flippable += 1
        results.append({"lo": m_lo, "hi": m_hi, "gap": p["gap"],
                         "degenerate": False, "flip_budget": d_star})

    n_total = len(pi["headline"]["pairs"])
    n_scored = len(results)
    print(f"Scored {n_scored} of {n_total} real pairs "
          f"({n_missing_data} skipped: missing accuracy or margin data)")
    print(f"  already degenerate (inconclusive at d=0, before any differential "
          f"error argument): {n_already_degenerate} of {n_scored} "
          f"({100*n_already_degenerate/n_scored:.1f}%)")

    finite_budgets = [r["flip_budget"] for r in results
                      if not r["degenerate"] and r["flip_budget"] is not None]
    if finite_budgets:
        fb = np.array(finite_budgets)
        print(f"  finite flip budgets: n={len(fb)}, "
              f"median={np.median(fb):.4f}, min={fb.min():.4f}, max={fb.max():.4f}")
        real_observed_alpha_spread = np.array(
            [d["alpha_pooled"] for d in per_model_margins.values()]).std()
        below_observed_spread = (fb < real_observed_alpha_spread).sum()
        print(f"  real observed alpha spread (pooled, std across models) = "
              f"{real_observed_alpha_spread:.4f}")
        print(f"  fraction of finite-budget pairs with flip budget BELOW that "
              f"observed spread: {below_observed_spread}/{len(fb)} "
              f"({100*below_observed_spread/len(fb):.1f}%)")

    print()
    print("=" * 70)
    print("GO/NO-GO: this is the real Case B pilot number.")
    print("=" * 70)

    out = {
        "n_total_pairs": n_total,
        "n_scored": n_scored,
        "n_missing_data": n_missing_data,
        "n_already_degenerate": n_already_degenerate,
        "sanity_check_passed": plausible,
        "per_model_accuracy_design_weighted": accs,
        "results": results,
    }
    with open("results/flipbudget/e1_case_b_mathhard.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Written to results/flipbudget/e1_case_b_mathhard.json")
