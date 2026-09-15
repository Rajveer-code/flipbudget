"""Methodological-audit item 7 (METHODOLOGICAL_AUDIT.md S7), made reproducible.

The 26.73%/2.38% worst/best-case bound on exact_match's own alpha (and the
0.166 median identified-set width run through it) was computed inline while
writing that audit and never saved as a script+JSON -- a real gap flagged
during this pass (every number must trace to a script per the project's own
reproducibility rule). This script closes it: same formula, verified to
reproduce the published figures exactly, now with a checkable output file.

Logic: exact_match's credited stratum = both_credited U disagree_em_credited
_sb_not (SCORER_CELLS in fb_tc_expansion2_analysis.py). both_credited's false
-credit rate is held at score_boxed's own known global anchor (tc_alpha_beta_
update.json global_anchor_old.alpha = 3.137%); the disagreement cell's true
rate for exact_match is UNKNOWN without the pending human audit, so the two
extremes (all-false-credit / none-false-credit) bound it. Same construction
for beta using both_not_credited + disagree_sb_credited_em_not, anchored at
score_boxed's beta=0. This is a population-weighted average of a known rate
and an extreme assumption, not a sampled estimate -- no standard error.

The worst-case point is then run through the SAME Lambda=2 sensitivity
methodology already used for the scorer-identification-only layer
(fb_reconcile_layers.py), on exact_match's OWN accuracy values (not
score_boxed's) -- the one apples-to-apples self-consistent worst-case check.

Run: python scripts/fb_worst_case_sensitivity.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
from ea_dominance_study import build_model_table
from fb_reconcile_layers import bounded_comparison
from fb_ta_ssm import lambda_bounds
from fb_tc_expansion2_analysis import CELL_POPULATION

L_REFERENCE = 2.0


def worst_best_case_alpha_beta():
    with open("results/flipbudget/tc_alpha_beta_update.json") as f:
        anchor = json.load(f)["global_anchor_old"]
    sb_alpha, sb_beta = anchor["alpha"], anchor["beta"]

    n_bc = CELL_POPULATION["both_credited"]
    n_disagree_em = CELL_POPULATION["disagree_em_credited_sb_not"]  # exact_match credits, score_boxed doesn't
    n_bnc = CELL_POPULATION["both_not_credited"]
    n_disagree_sb = CELL_POPULATION["disagree_sb_credited_em_not"]  # score_boxed credits, exact_match doesn't

    alpha_best = (n_bc * sb_alpha + n_disagree_em * 0) / (n_bc + n_disagree_em)
    alpha_worst = (n_bc * sb_alpha + n_disagree_em * 1) / (n_bc + n_disagree_em)
    beta_best = (n_bnc * sb_beta + n_disagree_sb * 0) / (n_bnc + n_disagree_sb)
    beta_worst = (n_bnc * sb_beta + n_disagree_sb * 1) / (n_bnc + n_disagree_sb)

    return {"score_boxed_anchor_alpha": sb_alpha, "score_boxed_anchor_beta": sb_beta,
            "exact_match_alpha_best": alpha_best, "exact_match_alpha_worst": alpha_worst,
            "exact_match_beta_best": beta_best, "exact_match_beta_worst": beta_worst}


def run_scenario(alpha, beta, rows_em, pairs):
    box = lambda_bounds(alpha, L_REFERENCE) + lambda_bounds(beta, L_REFERENCE)
    n_valid, n_unresolved, widths = 0, 0, []
    for lo_m, hi_m in pairs:
        if lo_m not in rows_em or hi_m not in rows_em:
            continue
        r1, r2 = rows_em[hi_m], rows_em[lo_m]
        lo_c, hi_c = bounded_comparison(r1["a_hat"], box, r2["a_hat"], box)
        if np.isnan(lo_c):
            continue
        n_valid += 1
        widths.append(hi_c - lo_c)
        if lo_c <= 0 <= hi_c:
            n_unresolved += 1
    return {"alpha": alpha, "beta": beta, "lambda": L_REFERENCE,
            "n_valid": n_valid, "n_unresolved": n_unresolved,
            "pct_unresolved": 100 * n_unresolved / n_valid if n_valid else None,
            "median_width": float(np.median(widths)) if widths else None}


def main():
    bounds = worst_best_case_alpha_beta()
    print("=" * 78)
    print("Worst/best-case exact_match alpha,beta (population-weighted extremes)")
    print("=" * 78)
    for k, v in bounds.items():
        print(f"  {k}: {v:.6f}  ({100*v:.2f}%)")

    with open("results/flipbudget/scorer_accuracy_comparison.json") as f:
        acc_cmp = {r["model"]: r for r in json.load(f)["per_model"]}
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        margins = json.load(f)["per_model"]
    with open("results/analysis/pair_identification_human.json") as f:
        pairs = [(p["lo"], p["hi"]) for p in json.load(f)["headline"]["pairs"]]

    accs_em = {m: {"a_hat_true": r["a_hat_exact_match"], "n_items_scored": r["n"]}
               for m, r in acc_cmp.items()}
    rows_em, _ = build_model_table(accs_em, margins)

    worst = run_scenario(bounds["exact_match_alpha_worst"], bounds["exact_match_beta_worst"], rows_em, pairs)
    best = run_scenario(bounds["exact_match_alpha_best"], bounds["exact_match_beta_best"], rows_em, pairs)

    with open("results/flipbudget/reconciliation_four_layers_corrected.json") as f:
        established_audit_only = json.load(f)["layer_stats"]["w_audit_only"]["median_width"]

    print("\n" + "=" * 78)
    print(f"WORST CASE  (Lambda={L_REFERENCE}): n_valid={worst['n_valid']}  "
          f"unresolved={worst['n_unresolved']}/{worst['n_valid']}  median_width={worst['median_width']:.4f}")
    print(f"BEST CASE   (Lambda={L_REFERENCE}): n_valid={best['n_valid']}  "
          f"unresolved={best['n_unresolved']}/{best['n_valid']}  median_width={best['median_width']:.4f}")
    print(f"Established audit-estimation-only median (score_boxed, reconciliation_four_layers_corrected.json): "
          f"{established_audit_only:.4f}")
    survives = worst["median_width"] < established_audit_only
    print(f"\nVerdict B survives even the worst case: {survives}  "
          f"({worst['median_width']:.4f} < {established_audit_only:.4f})")

    out = {"bounds": bounds, "worst_case": worst, "best_case": best,
           "established_audit_only_median_width": established_audit_only,
           "verdict_b_survives_worst_case": survives}
    with open("results/flipbudget/worst_case_sensitivity.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/worst_case_sensitivity.json")


if __name__ == "__main__":
    main()
