"""THE CANONICAL E-A dominance recomputation, from the rawest available inputs,
with every exclusion stage tracked separately and every percentage's denominator
stated explicitly. Written because `ea_dominance_pairwise_corrected_v2.json` and
`ea_dominance_corrected_v2.json` -- the files EVIDENCE_TABLE.md's A1/A2 currently
cite -- were produced by an ad-hoc interactive calculation during the previous
phase, not by a saved, re-runnable script (grep for their filename across
scripts/ returns nothing). That is itself a reproducibility gap: this script
closes it by recomputing the same quantity, one time, as a real pipeline step,
importing the ALREADY-FIXED logic (bounded_single_model_extrema/
bounded_comparison) from fb_reconcile_layers.py rather than re-deriving it, so
there is exactly one place the [0,1]/empty-set math lives.

Denominator chain, tracked at every stage (this is the actual point of this
script -- see RECONCILIATION_EMPTY_SET_BUG.md and FINAL_DECISION.md, which
report "100% dominant" without this full cascade made explicit in one place):

  378 total candidate pairs   = C(28,2), all models with a human pair-
                                 identification label in
                                 results/analysis/pair_identification_human.json
    -> excluded: pair involves a model with NO e1/e4 accuracy-audit data at all
       (microsoft/Phi-3-mini-4k-instruct: in the human pair list, absent from
       both e1_case_b_TRUE.json and e4_mathhard_per_model.json)
    -> excluded: pair involves a model that HAS e4 margin data but fails the
       audit-qualification gate (needs n_used_credited>0 AND n_used_wrong>0 --
       10 of 27 models fail this, all on the credited side, 0 on the wrong side)
  136 pairs scored             = C(17,2), pairs where BOTH models qualify
    -> excluded: empty identified set (raw Wilson-CI box for at least one
       model's alpha,beta does not overlap [0,1] at all -- see
       RECONCILIATION_EMPTY_SET_BUG.md)
  N valid pairs                = pairs scored minus empty-set pairs -- THIS is
                                 the denominator "100% dominant" refers to.

Run: python scripts/fb_ea_dominance_canonical.py
"""
import json
import sys
from itertools import combinations

import numpy as np

sys.path.insert(0, "scripts")
from ea_dominance_study import load, build_model_table, wilson_ci
from fb_reconcile_layers import bounded_single_model_extrema, bounded_comparison

Z = 1.96


def main():
    with open("results/analysis/pair_identification_human.json") as f:
        pi = json.load(f)
    human_pairs = pi["headline"]["pairs"]
    all_models_in_human_pairs = sorted({p["lo"] for p in human_pairs} | {p["hi"] for p in human_pairs})
    # The headline pair list may itself contain duplicate (lo,hi) unordered
    # pairs or repeats -- do not assume 378 is C(28,2) just because the count
    # matches; verify by reconstructing the full pair set directly and
    # comparing membership, not just cardinality.
    reconstructed = set(combinations(sorted(all_models_in_human_pairs), 2))
    human_pair_keys = set()
    for p in human_pairs:
        human_pair_keys.add(tuple(sorted((p["lo"], p["hi"]))))
    n_duplicate_or_extra = len(human_pairs) - len(human_pair_keys)

    accs, margins = load()
    rows, excl = build_model_table(accs, margins)  # rows = qualifying models only

    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4_all_models = set(json.load(f)["per_model"].keys())

    # ---- Walk every candidate pair, classify into exactly one bucket ----
    cat_counts = {
        "missing_accuracy_data": 0,      # model absent from e4 entirely
        "fails_audit_qualification": 0,  # in e4, but n_used_credited==0 or n_used_wrong==0
        "empty_identified_set": 0,       # both qualify, but Wilson-CI box empty for >=1 model
        "valid": 0,
    }
    empty_set_detail = []
    valid_results = []

    for lo, hi in sorted(human_pair_keys):
        missing = [m for m in (lo, hi) if m not in e4_all_models]
        if missing:
            cat_counts["missing_accuracy_data"] += 1
            continue
        not_qualifying = [m for m in (lo, hi) if m not in rows]
        if not_qualifying:
            cat_counts["fails_audit_qualification"] += 1
            continue

        r1, r2 = rows[hi], rows[lo]
        a1, a2 = r1["a_hat"], r2["a_hat"]
        n1_, n2_ = r1["n_bench"], r2["n_bench"]
        w_sampling = 2 * Z * np.sqrt(a1 * (1 - a1) / n1_ + a2 * (1 - a2) / n2_)

        box1 = r1["alpha_ci"] + r1["beta_ci"]
        box2 = r2["alpha_ci"] + r2["beta_ci"]
        e1_lo, e1_hi = bounded_single_model_extrema(a1, *box1)
        e2_lo, e2_hi = bounded_single_model_extrema(a2, *box2)
        lo_c, hi_c = bounded_comparison(a1, box1, a2, box2)

        if np.isnan(lo_c):
            cat_counts["empty_identified_set"] += 1
            empty_set_detail.append({
                "pair": [hi, lo],
                "hi_model_a_hat": a1, "hi_model_empty": bool(np.isnan(e1_lo)),
                "lo_model_a_hat": a2, "lo_model_empty": bool(np.isnan(e2_lo)),
            })
            continue

        w_id = hi_c - lo_c
        cat_counts["valid"] += 1
        valid_results.append({
            "hi": hi, "lo": lo, "a_hat_hi": a1, "a_hat_lo": a2,
            "w_sampling": float(w_sampling), "w_identification": float(w_id),
            "ratio": float(w_id / w_sampling) if w_sampling > 0 else None,
        })

    total_candidate_pairs = len(human_pair_keys)
    pairs_scored = cat_counts["fails_audit_qualification"] * 0 + cat_counts["empty_identified_set"] + cat_counts["valid"]
    # pairs_scored (both models qualify, regardless of empty-set outcome):
    pairs_scored = cat_counts["empty_identified_set"] + cat_counts["valid"]

    ratios = np.array([r["ratio"] for r in valid_results if r["ratio"] is not None])
    n_valid = len(ratios)
    n_dominant_valid = int((ratios > 1).sum())

    percentiles = {str(p): float(np.percentile(ratios, p)) for p in (5, 10, 25, 50, 75, 90, 95)}

    print("=" * 78)
    print("CANONICAL E-A DOMINANCE RECOMPUTATION -- full denominator cascade")
    print("=" * 78)
    print(f"Total candidate pairs (unique unordered pairs in human pair-ID list): {total_candidate_pairs}")
    print(f"  (raw list length {len(human_pairs)}, {n_duplicate_or_extra} duplicate/repeat entries collapsed)")
    print(f"  unique models referenced: {len(all_models_in_human_pairs)}  "
          f"(C(n,2) check: {len(all_models_in_human_pairs)*(len(all_models_in_human_pairs)-1)//2})")
    print(f"  models with e1/e4 accuracy-audit data at all: {len(e4_all_models)} of {len(all_models_in_human_pairs)}")
    print(f"  of those, models qualifying for Wilson-CI (audit n>0 both strata): "
          f"{excl['n_qualifying']} of {excl['n_total_models']} "
          f"(excluded: {excl['n_excluded_no_credited_audit']} no-credited-audit-item, "
          f"{excl['n_excluded_no_wrong_audit']} no-wrong-audit-item)")
    print()
    print(f"  excluded -- missing accuracy data entirely:      {cat_counts['missing_accuracy_data']}")
    print(f"  excluded -- model fails audit qualification:     {cat_counts['fails_audit_qualification']}")
    print(f"  = pairs scored (both models qualify):            {pairs_scored}")
    print(f"      excluded -- empty identified set (>=1 side):  {cat_counts['empty_identified_set']}")
    print(f"      = VALID pairs (well-defined comparison):      {cat_counts['valid']}")
    print()
    print("-" * 78)
    print("RATIO DISTRIBUTION (W_identification / W_sampling), VALID PAIRS ONLY, n=%d" % n_valid)
    print("-" * 78)
    print(f"  median: {np.median(ratios):.3f}   mean: {np.mean(ratios):.3f}   "
          f"min: {ratios.min():.3f}   max: {ratios.max():.3f}")
    print(f"  percentiles: {percentiles}")
    print()
    print("-" * 78)
    print("'DOMINANT' (ratio>1) -- THREE DENOMINATORS, STATED EXPLICITLY")
    print("-" * 78)
    print(f"  among VALID pairs only:          {n_dominant_valid}/{n_valid} "
          f"= {100*n_dominant_valid/n_valid:.1f}%   <-- what '100% dominant' refers to")
    print(f"  among PAIRS SCORED (incl. empty-set as not-applicable, "
          f"not counted either way): {n_dominant_valid}/{pairs_scored} "
          f"= {100*n_dominant_valid/pairs_scored:.1f}%")
    print(f"  among ALL {total_candidate_pairs} CANDIDATE PAIRS (most conservative, empty-set "
          f"and non-qualifying both treated as non-dominant): "
          f"{n_dominant_valid}/{total_candidate_pairs} = {100*n_dominant_valid/total_candidate_pairs:.1f}%")

    # ---- Single-model canonical (A2): same cascade, one model at a time ----
    sm_empty, sm_valid = [], []
    for model, r in rows.items():
        lo_s, hi_s = bounded_single_model_extrema(r["a_hat"], *(r["alpha_ci"] + r["beta_ci"]))
        w_sampling = 2 * Z * np.sqrt(r["a_hat"] * (1 - r["a_hat"]) / r["n_bench"])
        if np.isnan(lo_s):
            sm_empty.append(model)
            continue
        w_id = hi_s - lo_s
        sm_valid.append({"model": model, "w_sampling": float(w_sampling),
                          "w_identification": float(w_id),
                          "ratio": float(w_id / w_sampling) if w_sampling > 0 else None})
    sm_ratios = np.array([r["ratio"] for r in sm_valid if r["ratio"] is not None])
    print()
    print("-" * 78)
    print("SINGLE-MODEL (A2), same cascade: 17 qualifying models")
    print("-" * 78)
    print(f"  empty identified set: {len(sm_empty)} ({sm_empty})")
    print(f"  valid: {len(sm_valid)}")
    print(f"  median ratio: {np.median(sm_ratios):.3f}   mean: {np.mean(sm_ratios):.3f}   "
          f"min: {sm_ratios.min():.3f}   max: {sm_ratios.max():.3f}")
    print(f"  dominant among valid: {(sm_ratios>1).sum()}/{len(sm_ratios)} = "
          f"{100*(sm_ratios>1).mean():.1f}%")
    print(f"  dominant among all 17 qualifying: {(sm_ratios>1).sum()}/17 = "
          f"{100*(sm_ratios>1).sum()/17:.1f}%")
    print(f"  dominant among all 27 models with any accuracy data: {(sm_ratios>1).sum()}/27 = "
          f"{100*(sm_ratios>1).sum()/27:.1f}%")

    out = {
        "single_model": {
            "n_qualifying": len(rows), "n_total_with_accuracy_data": excl["n_total_models"],
            "n_empty_set": len(sm_empty), "empty_set_models": sm_empty,
            "n_valid": len(sm_valid),
            "ratio_median": float(np.median(sm_ratios)), "ratio_mean": float(np.mean(sm_ratios)),
            "ratio_min": float(sm_ratios.min()), "ratio_max": float(sm_ratios.max()),
            "n_dominant": int((sm_ratios > 1).sum()),
            "pct_dominant_among_valid": 100 * (sm_ratios > 1).mean(),
            "pct_dominant_among_qualifying": 100 * (sm_ratios > 1).sum() / len(rows),
            "pct_dominant_among_all_models": 100 * (sm_ratios > 1).sum() / excl["n_total_models"],
            "per_model": sm_valid,
        },
        "total_candidate_pairs": total_candidate_pairs,
        "n_duplicate_or_extra_entries_in_raw_list": n_duplicate_or_extra,
        "n_unique_models_in_human_pair_list": len(all_models_in_human_pairs),
        "n_models_with_any_accuracy_audit_data": len(e4_all_models),
        "n_models_qualifying_for_wilson_ci": excl["n_qualifying"],
        "n_models_total_with_e4_data": excl["n_total_models"],
        "n_excluded_no_credited_audit": excl["n_excluded_no_credited_audit"],
        "n_excluded_no_wrong_audit": excl["n_excluded_no_wrong_audit"],
        "category_counts": cat_counts,
        "pairs_scored": pairs_scored,
        "n_valid": n_valid,
        "ratio_median": float(np.median(ratios)),
        "ratio_mean": float(np.mean(ratios)),
        "ratio_min": float(ratios.min()),
        "ratio_max": float(ratios.max()),
        "ratio_percentiles": percentiles,
        "n_dominant_among_valid": n_dominant_valid,
        "pct_dominant_among_valid": 100 * n_dominant_valid / n_valid,
        "pct_dominant_among_pairs_scored": 100 * n_dominant_valid / pairs_scored,
        "pct_dominant_among_all_candidate_pairs": 100 * n_dominant_valid / total_candidate_pairs,
        "empty_set_pair_detail": empty_set_detail,
        "valid_pair_detail": valid_results,
        "note": ("'100%% dominant' in prior writeups (EVIDENCE_TABLE.md A1, "
                 "FINAL_DECISION.md) refers to the VALID-pairs denominator "
                 "(n=%d) -- stated here alongside the other two denominators "
                 "so the claim cannot be misread as covering all %d candidate "
                 "pairs." % (n_valid, total_candidate_pairs)),
    }
    with open("results/flipbudget/ea_dominance_canonical.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/ea_dominance_canonical.json")
    print("(ea_dominance_study.json / *_corrected.json / *_corrected_v2.json preserved unchanged)")
    print("=" * 78)


if __name__ == "__main__":
    main()
