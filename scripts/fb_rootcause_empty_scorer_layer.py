"""Item 2 of the final validation phase: root-cause the 70/136 empty identified
sets in the SCORER-IDENTIFICATION-ONLY layer (Lambda=2, anchored at the
pooled/shrunk alpha,beta point estimate -- fb_reconcile_layers.py's third
layer). Emptiness there is fundamentally a PER-MODEL property (a pair is
empty iff at least one of its two models has an empty box), so this script
first classifies each of the 17 qualifying models, then rolls that up to the
136 pairs.

For each qualifying model, decompose why its box is empty (if it is) into:
  - whether the RAW POOLED POINT ESTIMATE alone (alpha_pooled, beta_pooled,
    Lambda=1, no sensitivity widening at all) is already inconsistent with
    a_hat -- this isolates "empirical-Bayes shrinkage / pooling" as the cause,
    independent of the Lambda=2 sensitivity band.
  - which corner of the Lambda=2 box is the binding constraint (alpha_lo,
    alpha_hi, beta_lo, beta_hi), via the same 4-corner evaluation
    bounded_single_model_extrema uses internally, to attribute emptiness to
    the alpha channel, the beta channel, or their joint interaction with the
    denominator (1-alpha-beta) -- not asserted, computed.
  - the numeric margin: by how much does the best-case corner miss [0,1].

Run: python scripts/fb_rootcause_empty_scorer_layer.py
"""
import json
import sys
from itertools import combinations

import numpy as np

sys.path.insert(0, "scripts")
from ea_dominance_study import load, build_model_table
from fb_ta_ssm import lambda_bounds
from fb_reconcile_layers import bounded_single_model_extrema
from fb_t2_flipbudget import g

L_REFERENCE = 2.0


def classify_model(model, a_hat, alpha_pooled, beta_pooled):
    # Lambda=1 (no widening at all) -- pure point-estimate/pooling check.
    point_only_negative = (a_hat - alpha_pooled) < 0  # g's numerator sign at the point estimate

    alpha_lo, alpha_hi = lambda_bounds(alpha_pooled, L_REFERENCE)
    beta_lo, beta_hi = lambda_bounds(beta_pooled, L_REFERENCE)
    lo, hi = bounded_single_model_extrema(a_hat, alpha_lo, alpha_hi, beta_lo, beta_hi)
    is_empty = np.isnan(lo)

    corners = {}
    for al, al_name in ((alpha_lo, "alpha_lo"), (alpha_hi, "alpha_hi")):
        for be, be_name in ((beta_lo, "beta_lo"), (beta_hi, "beta_hi")):
            if al + be < 0.999:
                corners[f"{al_name},{be_name}"] = g(a_hat, al, be)
    best_corner = max(corners, key=corners.get) if corners else None
    best_val = corners[best_corner] if best_corner else None

    return {
        "model": model, "a_hat": a_hat,
        "alpha_pooled": alpha_pooled, "beta_pooled": beta_pooled,
        "alpha_band_L2": [alpha_lo, alpha_hi], "beta_band_L2": [beta_lo, beta_hi],
        "point_estimate_alone_inconsistent": bool(point_only_negative),
        "is_empty_at_L2": bool(is_empty),
        "best_corner": best_corner, "best_corner_g_value": best_val,
        "margin_below_zero": (0.0 - best_val) if (best_val is not None and best_val < 0) else None,
    }


def main():
    accs, margins = load()
    rows, excl = build_model_table(accs, margins)
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4 = json.load(f)["per_model"]

    classified = []
    for model, r in rows.items():
        m = e4[model]
        classified.append(classify_model(model, r["a_hat"], m["alpha_pooled"], m["beta_pooled"]))

    empty_models = [c for c in classified if c["is_empty_at_L2"]]
    valid_models = [c for c in classified if not c["is_empty_at_L2"]]

    print("=" * 78)
    print("ROOT-CAUSE: scorer-identification-only layer (Lambda=2), per-model")
    print("=" * 78)
    print(f"Qualifying models: {len(classified)}")
    print(f"Empty at Lambda=2: {len(empty_models)}")
    print(f"Valid at Lambda=2: {len(valid_models)}")
    print()
    print(f"{'model':<45}{'a_hat':<8}{'alpha_pooled':<14}{'empty?':<8}{'point-only bad?':<16}{'margin':<10}")
    for c in sorted(classified, key=lambda x: x["a_hat"]):
        margin_str = f"{c['margin_below_zero']:.4f}" if c["margin_below_zero"] is not None else "-"
        print(f"{c['model']:<45}{c['a_hat']:<8.3f}{c['alpha_pooled']:<14.4f}"
              f"{'YES' if c['is_empty_at_L2'] else 'no':<8}"
              f"{'YES' if c['point_estimate_alone_inconsistent'] else 'no':<16}"
              f"{margin_str:<10}")

    n_point_driven = sum(1 for c in empty_models if c["point_estimate_alone_inconsistent"])
    n_lambda_only = len(empty_models) - n_point_driven
    print()
    print("-" * 78)
    print("ROOT-CAUSE BREAKDOWN of empty models")
    print("-" * 78)
    print(f"  point-estimate-alone already inconsistent (a_hat < alpha_pooled, "
          f"i.e. pooling/shrinkage puts the point estimate itself above accuracy): "
          f"{n_point_driven}/{len(empty_models)}")
    print(f"  point estimate consistent but Lambda=2 widening pushes it empty "
          f"(sensitivity-band effect, not pooling per se): {n_lambda_only}/{len(empty_models)}")

    corner_counts = {}
    for c in empty_models:
        corner_counts[c["best_corner"]] = corner_counts.get(c["best_corner"], 0) + 1
    print(f"  binding corner distribution (which channel is closest to [0,1]): {corner_counts}")

    # ---- Roll up to the 136 pairs ----
    empty_set_model_names = {c["model"] for c in empty_models}
    qualifying = sorted(rows.keys())
    pairs = list(combinations(qualifying, 2))
    n_pairs_empty = sum(1 for (m1, m2) in pairs if m1 in empty_set_model_names or m2 in empty_set_model_names)
    n_pairs_empty_both = sum(1 for (m1, m2) in pairs if m1 in empty_set_model_names and m2 in empty_set_model_names)
    n_pairs_empty_one = n_pairs_empty - n_pairs_empty_both

    print()
    print("-" * 78)
    print("ROLL-UP TO 136 PAIRS")
    print("-" * 78)
    print(f"  total pairs: {len(pairs)}")
    print(f"  pairs with >=1 empty-model side: {n_pairs_empty}  "
          f"(one side empty: {n_pairs_empty_one}, both sides empty: {n_pairs_empty_both})")
    print(f"  [expected from RECONCILIATION_EMPTY_SET_BUG.md: 70]")

    print()
    print("-" * 78)
    print("IS 'EMPTY IDENTIFIED SET' A FORMAL DIAGNOSTIC OF MODEL/DATA INCOMPATIBILITY?")
    print("-" * 78)
    print("Yes, under the following precise statement: an empty identified set at")
    print("sensitivity level Lambda means NO (alpha,beta) pair within odds-ratio Lambda")
    print("of the pooled point estimate can reproduce the model's observed accuracy a_hat")
    print("via the measurement identity a = A*(1-beta) + (1-A*)*alpha for ANY A* in [0,1].")
    print("This is a real falsifiable statement about the (Lambda, pooled-estimate, a_hat)")
    print("triple, not an estimation artifact -- it says the assumed scorer-error model is")
    print("too narrow (Lambda too small) or the pooled estimate itself is a poor anchor for")
    print("this specific model, GIVEN its observed accuracy.")

    out = {
        "reference_lambda": L_REFERENCE,
        "n_qualifying_models": len(classified),
        "n_empty_models": len(empty_models),
        "n_valid_models": len(valid_models),
        "empty_models_detail": empty_models,
        "n_point_estimate_driven": n_point_driven,
        "n_lambda_widening_driven": n_lambda_only,
        "binding_corner_distribution": corner_counts,
        "n_pairs_total": len(pairs),
        "n_pairs_with_empty_side": n_pairs_empty,
        "n_pairs_both_sides_empty": n_pairs_empty_both,
        "n_pairs_one_side_empty": n_pairs_empty_one,
        "all_models_classified": classified,
    }
    with open("results/flipbudget/rootcause_empty_scorer_layer.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/rootcause_empty_scorer_layer.json")


if __name__ == "__main__":
    main()
