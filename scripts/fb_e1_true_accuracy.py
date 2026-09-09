"""E1 Case B, unblocked -- TRUE per-model MATH-Hard accuracy from cache_l1's
raw generations, using the harness's own already-computed `exact_match` field
per item (no re-scoring, no reweighting of a pooled sampling frame -- this is
the actual population-level truth the frame's 400-item audit was sampling
FROM in the first place).

Replaces fb_e1_case_b.py's design-weighted attempt, which a pre-declared
sanity check correctly caught as biased (pooled-frame weights applied to a
per-model subgroup) -- see that script's commit message for the diagnosis.

Run: python scripts/fb_e1_true_accuracy.py
"""
import glob
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "scripts")
from fb_t2_flipbudget import flip_budget

CACHE_ROOT = Path("results/cache_l1")


def model_to_dirname(model: str) -> str:
    return f"open-llm-leaderboard_{model.replace('/', '__')}-details"


def true_accuracy(model: str):
    dirname = CACHE_ROOT / model_to_dirname(model)
    if not dirname.is_dir():
        return None
    files = sorted(glob.glob(str(dirname / "samples_leaderboard_math_*_hard_*.json")))
    if not files:
        return None
    scores = []
    for fp in files:
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if "exact_match" in rec:
                    scores.append(rec["exact_match"])
    if not scores:
        return None
    return float(np.mean(scores)), len(scores)


if __name__ == "__main__":
    print("=" * 70)
    print("E1 Case B unblocked -- true per-model MATH-Hard accuracy from cache_l1")
    print("=" * 70)

    with open("results/analysis/mathhard_labelling_key.json") as f:
        key = json.load(f)
    roster = sorted(set(item["model"] for item in key))
    print(f"Roster: {len(roster)} models (from mathhard_labelling_key.json)")
    print()

    accs = {}
    missing = []
    for m in roster:
        r = true_accuracy(m)
        if r is None:
            missing.append(m)
            continue
        accs[m] = {"a_hat_true": r[0], "n_items_scored": r[1]}

    print(f"Scored {len(accs)} of {len(roster)} models from raw cache; "
          f"{len(missing)} missing (dir not found or no exact_match field)")
    if missing:
        print(f"  missing: {missing}")
    print()

    print("Sanity check against worked_example_human's known roster max, and the")
    print("actual roster min found by direct computation (an earlier version of")
    print("this script assumed dolly-v2-12b was the min without verifying that --")
    print("it is not; CohereForAI/c4ai-command-r-v01 is, exactly, and it is also")
    print("the model E4 independently flagged with a 0.667 raw false-credit rate")
    print("-- a real, coherent cross-validation, not a coincidence worth ignoring):")
    q72 = accs.get("Qwen/Qwen2-72B-Instruct")
    true_min_model = min(accs.items(), key=lambda kv: kv[1]["a_hat_true"])
    if q72 is None:
        print("  [FAIL] Qwen2-72B-Instruct not found in scored set -- stopping")
        raise SystemExit(1)
    print(f"  Qwen/Qwen2-72B-Instruct: a_hat={q72['a_hat_true']:.4f} "
          f"(n={q72['n_items_scored']}) -- roster max reported: 0.3512")
    print(f"  roster min (computed): {true_min_model[0]} = "
          f"{true_min_model[1]['a_hat_true']:.4f} -- roster min reported: 0.0000")
    close = (abs(q72["a_hat_true"] - 0.3512) < 0.001
             and abs(true_min_model[1]["a_hat_true"] - 0.0) < 0.001)
    print(f"  [{'OK' if close else 'FAIL'}] max matches to 4 decimals, computed min "
          f"matches reported min to 4 decimals: {close}")
    if not close:
        print("STOPPING: true accuracy does not reproduce the published anchors --")
        print("do not trust the Case B pilot below.")
        raise SystemExit(1)
    print()

    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4 = json.load(f)
    per_model_margins = e4["per_model"]

    with open("results/analysis/pair_identification_human.json") as f:
        pi = json.load(f)

    n_total = len(pi["headline"]["pairs"])
    n_scored, n_missing, n_degenerate, n_flippable = 0, 0, 0, 0
    results = []
    for p in pi["headline"]["pairs"]:
        m_lo, m_hi = p["lo"], p["hi"]
        if m_lo not in accs or m_hi not in accs:
            n_missing += 1
            continue
        if m_lo not in per_model_margins or m_hi not in per_model_margins:
            n_missing += 1
            continue
        a_lo, a_hi = accs[m_lo]["a_hat_true"], accs[m_hi]["a_hat_true"]
        mlo, mhi = per_model_margins[m_lo], per_model_margins[m_hi]
        alpha0 = (mlo["alpha_pooled"] + mhi["alpha_pooled"]) / 2
        beta0 = (mlo["beta_pooled"] + mhi["beta_pooled"]) / 2
        if alpha0 + beta0 >= 0.95:
            n_missing += 1
            continue

        d_star, degenerate = flip_budget(a_hi, a_lo, alpha0, beta0)
        n_scored += 1
        if degenerate:
            n_degenerate += 1
            results.append({"lo": m_lo, "hi": m_hi, "gap": p["gap"],
                             "true_gap": abs(a_hi - a_lo), "degenerate": True,
                             "flip_budget": None})
        else:
            if d_star is not None:
                n_flippable += 1
            results.append({"lo": m_lo, "hi": m_hi, "gap": p["gap"],
                             "true_gap": abs(a_hi - a_lo), "degenerate": False,
                             "flip_budget": d_star})

    print("=" * 70)
    print(f"REAL Case B result: scored {n_scored} of {n_total} pairs "
          f"({n_missing} skipped, missing accuracy or margin data)")
    print(f"  already degenerate at d=0 (inconclusive before any differential "
          f"error): {n_degenerate}/{n_scored} ({100*n_degenerate/n_scored:.1f}%)")

    finite = [r["flip_budget"] for r in results if not r["degenerate"] and r["flip_budget"] is not None]
    if finite:
        fb = np.array(finite)
        alpha_spread = np.array([d["alpha_pooled"] for d in per_model_margins.values()]).std()
        below = (fb < alpha_spread).sum()
        print(f"  finite flip budgets: n={len(fb)}, median={np.median(fb):.4f}, "
              f"min={fb.min():.4f}, max={fb.max():.4f}")
        print(f"  real observed pooled-alpha spread across models: {alpha_spread:.4f}")
        print(f"  fraction of pairs with flip budget BELOW that spread "
              f"(i.e. plausibly reachable by real differential error already "
              f"observed in this roster): {below}/{len(fb)} ({100*below/len(fb):.1f}%)")
        gate = below / len(fb)
        print()
        print("=" * 70)
        if gate >= 0.05:
            print(f"GO: {100*gate:.1f}% of scored pairs have a flip budget below the "
                  f"real observed alpha spread -- the differential-misclassification "
                  f"correction is practically relevant on this benchmark, not negligible.")
        else:
            print(f"NO-GO (per Kill Criterion 1): only {100*gate:.1f}% of pairs are "
                  f"reachable by the observed alpha spread -- below the 5% threshold. "
                  f"On this benchmark and this roster, non-differential (Case A) "
                  f"dominates in practice.")
        print("=" * 70)

    out = {
        "n_total_pairs": n_total, "n_scored": n_scored, "n_missing": n_missing,
        "n_degenerate": n_degenerate,
        "sanity_check": {"qwen72b_max": q72,
                          "true_min_model": true_min_model[0],
                          "true_min_value": true_min_model[1],
                          "passed": close},
        "true_accuracy_per_model": accs,
        "results": results,
    }
    with open("results/flipbudget/e1_case_b_TRUE.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/e1_case_b_TRUE.json")
