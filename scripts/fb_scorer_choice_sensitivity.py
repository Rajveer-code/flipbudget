"""Item 7/9 of the latest directive: does the 6.51% exact_match/score_boxed
mismatch change any headline result? Tests the SELF-CONSISTENT pairing
(score_boxed's own accuracy + score_boxed's own audited alpha/beta) against
the pairing used throughout this project so far (exact_match's accuracy +
score_boxed's audited alpha/beta -- a real construct mismatch, since alpha/
beta were audited relative to score_boxed specifically, not exact_match).

Also computes a NEW, fifth uncertainty layer -- "scorer-choice width": for
each real pair, the gap between Delta* computed under exact_match-accuracy
vs score_boxed-accuracy (holding the SAME audited alpha/beta box), which is
fully computable from data already on disk -- no new human labels needed,
since both accuracies are automated, deterministic quantities.

Run: python scripts/fb_scorer_choice_sensitivity.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
from ea_dominance_study import build_model_table, wilson_ci
from fb_reconcile_layers import bounded_single_model_extrema, bounded_comparison

Z = 1.96


def main():
    with open("results/flipbudget/scorer_accuracy_comparison.json") as f:
        acc_cmp = {r["model"]: r for r in json.load(f)["per_model"]}
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        margins = json.load(f)["per_model"]
    with open("results/analysis/pair_identification_human.json") as f:
        pi = json.load(f)

    # Build the SAME qualifying-model rows as ea_dominance_study, but with
    # TWO accuracy values (exact_match, score_boxed) per model instead of one.
    accs_em = {m: {"a_hat_true": r["a_hat_exact_match"], "n_items_scored": r["n"]}
               for m, r in acc_cmp.items()}
    accs_sb = {m: {"a_hat_true": r["a_hat_score_boxed"], "n_items_scored": r["n"]}
               for m, r in acc_cmp.items()}
    rows_em, excl = build_model_table(accs_em, margins)
    rows_sb, _ = build_model_table(accs_sb, margins)
    print(f"Qualifying models: {excl['n_qualifying']} of {excl['n_total_models']}")

    pairs = [(p["lo"], p["hi"]) for p in pi["headline"]["pairs"]]

    def score(rows):
        n_valid, ratios = 0, []
        for lo, hi in pairs:
            if lo not in rows or hi not in rows:
                continue
            r1, r2 = rows[hi], rows[lo]
            a1, a2 = r1["a_hat"], r2["a_hat"]
            w_sampling = 2 * Z * np.sqrt(a1 * (1 - a1) / r1["n_bench"] + a2 * (1 - a2) / r2["n_bench"])
            box1 = r1["alpha_ci"] + r1["beta_ci"]
            box2 = r2["alpha_ci"] + r2["beta_ci"]
            lo_c, hi_c = bounded_comparison(a1, box1, a2, box2)
            if np.isnan(lo_c):
                continue
            w_id = hi_c - lo_c
            n_valid += 1
            ratios.append(w_id / w_sampling if w_sampling > 0 else np.nan)
        ratios = np.array([r for r in ratios if np.isfinite(r)])
        return n_valid, ratios

    print("\n" + "=" * 78)
    print("SELF-CONSISTENT PAIRING TEST: exact_match-accuracy vs score_boxed-accuracy,")
    print("BOTH using score_boxed's own audited alpha/beta (the only audited box we have)")
    print("=" * 78)
    n_em, ratios_em = score(rows_em)
    n_sb, ratios_sb = score(rows_sb)
    print(f"exact_match-accuracy pairing (used throughout this project so far):")
    print(f"  n_valid={n_em}  median={np.median(ratios_em):.3f}  "
          f"dominant={100*(ratios_em>1).mean():.1f}% of valid")
    print(f"score_boxed-accuracy pairing (self-consistent with the audited alpha/beta):")
    print(f"  n_valid={n_sb}  median={np.median(ratios_sb):.3f}  "
          f"dominant={100*(ratios_sb>1).mean():.1f}% of valid")

    # ---- The new, fifth layer: scorer-choice width (fully automated, no new labels) ----
    print("\n" + "=" * 78)
    print("SCORER-CHOICE WIDTH: |Delta*_exact_match - Delta*_score_boxed| per pair,")
    print("holding alpha/beta fixed -- a real, computable uncertainty source,")
    print("independent of sampling/audit-estimation/scorer-sensitivity")
    print("=" * 78)
    choice_widths = []
    per_pair = []
    for lo, hi in pairs:
        if lo not in rows_em or hi not in rows_em or lo not in rows_sb or hi not in rows_sb:
            continue
        r1e, r2e = rows_em[hi], rows_em[lo]
        r1s, r2s = rows_sb[hi], rows_sb[lo]
        box1 = r1e["alpha_ci"] + r1e["beta_ci"]  # same audited box either way
        box2 = r2e["alpha_ci"] + r2e["beta_ci"]
        pt_em = None
        pt_sb = None
        lo1, hi1 = bounded_single_model_extrema(r1e["a_hat"], *box1)
        lo2, hi2 = bounded_single_model_extrema(r2e["a_hat"], *box2)
        if not np.isnan(lo1) and not np.isnan(lo2):
            pt_em = ((lo1 + hi1) / 2) - ((lo2 + hi2) / 2)
        lo1s, hi1s = bounded_single_model_extrema(r1s["a_hat"], *box1)
        lo2s, hi2s = bounded_single_model_extrema(r2s["a_hat"], *box2)
        if not np.isnan(lo1s) and not np.isnan(lo2s):
            pt_sb = ((lo1s + hi1s) / 2) - ((lo2s + hi2s) / 2)
        if pt_em is None or pt_sb is None:
            continue
        w = abs(pt_em - pt_sb)
        choice_widths.append(w)
        per_pair.append({"hi": hi, "lo": lo, "point_exact_match": pt_em,
                          "point_score_boxed": pt_sb, "scorer_choice_width": w})

    choice_widths = np.array(choice_widths)
    print(f"n pairs with both accuracies valid: {len(choice_widths)}")
    print(f"median scorer-choice width: {np.median(choice_widths):.4f}")
    print(f"mean: {np.mean(choice_widths):.4f}  max: {choice_widths.max():.4f}")

    # Compare directly against the other three layers' median widths (already established)
    with open("results/flipbudget/reconciliation_four_layers_corrected.json") as f:
        recon = json.load(f)
    print(f"\nFor comparison, already-established median widths (same pairs, different object):")
    print(f"  sampling:               {recon['layer_stats']['w_sampling']['median_width']:.4f}")
    print(f"  audit-estimation-only:  {recon['layer_stats']['w_audit_only']['median_width']:.4f}")
    print(f"  scorer-identification-only (Lambda=2): {recon['layer_stats']['w_scorer_only']['median_width']:.4f}")
    print(f"  scorer-CHOICE (this analysis, exact_match vs score_boxed accuracy): "
          f"{np.median(choice_widths):.4f}")

    out = {
        "self_consistent_test": {
            "exact_match_pairing": {"n_valid": n_em, "median_ratio": float(np.median(ratios_em)),
                                     "pct_dominant": float(100 * (ratios_em > 1).mean())},
            "score_boxed_pairing": {"n_valid": n_sb, "median_ratio": float(np.median(ratios_sb)),
                                     "pct_dominant": float(100 * (ratios_sb > 1).mean())},
        },
        "scorer_choice_width": {
            "n_pairs": len(choice_widths), "median": float(np.median(choice_widths)),
            "mean": float(np.mean(choice_widths)), "max": float(choice_widths.max()),
            "per_pair": per_pair,
        },
        "comparison_to_other_layers": {
            "sampling_median": recon["layer_stats"]["w_sampling"]["median_width"],
            "audit_only_median": recon["layer_stats"]["w_audit_only"]["median_width"],
            "scorer_only_median": recon["layer_stats"]["w_scorer_only"]["median_width"],
            "scorer_choice_median": float(np.median(choice_widths)),
        },
    }
    with open("results/flipbudget/scorer_choice_sensitivity.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/scorer_choice_sensitivity.json")


if __name__ == "__main__":
    main()
