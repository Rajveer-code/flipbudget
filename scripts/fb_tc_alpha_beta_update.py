"""T-C's contribution to the requested joint analysis (compare automatic
scorer verdict -> human verdict -> known-bug cases -> unexplained cases, and
quantify effect on alpha, beta, scorer disagreement, benchmark score, model
rankings, identification/uncertainty estimates).

T-C's human labels already exist (returned and analyzed this session --
TC_REAL_ANALYSIS.md: 0/69 scorer-wrong events found). This script is the part
of that request TC_REAL_ANALYSIS.md did not yet do: fold those 69 real,
newly-audited trials into the existing alpha/beta pooling and recompute
identification bounds and pairwise resolution -- reusing every existing
function exactly (fb_e4_mathhard.partial_pool, ea_dominance_study.
build_model_table/wilson_ci, fb_reconcile_layers.bounded_single_model_extrema/
bounded_comparison, fb_ta_ssm.lambda_bounds, fb_ta_compound_interval.
compound_bounds), not reimplemented.

IFEval's half of this same request is blocked pending its own human labels
(labeling/ifeval_audit_l1.csv, untouched) -- not attempted here.

Run: python scripts/fb_tc_alpha_beta_update.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
from fb_e4_mathhard import partial_pool
from ea_dominance_study import load as load_ea, build_model_table, wilson_ci
from fb_ta_ssm import lambda_bounds
from fb_ta_compound_interval import compound_bounds
from fb_reconcile_layers import bounded_single_model_extrema, bounded_comparison, L_REFERENCE
from fb_tc_real_analysis import is_indeterminate, matches_gold, load_l1, load_key

Z = 1.96


def new_tc_counts_by_model(key, l1_answers):
    """Per model: new (n_used_credited, x_alpha) and (n_used_wrong, x_beta)
    contributed by T-C's 69 usable L1 rows. Mirrors fb_e4_mathhard.
    per_model_rates' credited/else-wrong split and false-credit/false-miss
    definitions exactly, just fed from the new sheet instead of the old one."""
    out = {}
    n_indeterminate = 0
    for uid, ans in l1_answers.items():
        if is_indeterminate(ans):
            n_indeterminate += 1
            continue
        k = key[uid]
        model = k["model"]
        d = out.setdefault(model, {"n0_new": 0, "x_alpha_new": 0, "n1_new": 0, "x_beta_new": 0})
        human_correct = matches_gold(ans, k["gold"])
        if k["stratum"] == "credited":
            d["n0_new"] += 1
            if not human_correct:
                d["x_alpha_new"] += 1  # scorer credited it, human says wrong -> false credit
        else:
            d["n1_new"] += 1
            if human_correct:
                d["x_beta_new"] += 1  # scorer marked it wrong/unparsed, human says it's right
    return out, n_indeterminate


def rebuild_e4_with_new_audit(e4_old, new_counts):
    """Updated per-model margins dict, same shape as e4_mathhard_per_model.json's
    'per_model', with T-C's new trials folded into n_used_credited/n_used_wrong
    and the implied false-credit/false-miss counts, then re-pooled via the
    EXACT SAME partial_pool() used to build the original file."""
    updated_raw = {}
    for model, old in e4_old.items():
        new = new_counts.get(model, {"n0_new": 0, "x_alpha_new": 0, "n1_new": 0, "x_beta_new": 0})
        old_n0, old_n1 = old["n_used_credited"], old["n_used_wrong"]
        # reconstruct old integer counts the same way build_model_table does
        old_alpha_raw = old["alpha_raw"] if old["alpha_raw"] is not None else 0.0
        old_beta_raw = old["beta_raw"] if old["beta_raw"] is not None else 0.0
        old_x_alpha = round(old_alpha_raw * old_n0)
        old_x_beta = round(old_beta_raw * old_n1)

        n0 = old_n0 + new["n0_new"]
        n1 = old_n1 + new["n1_new"]
        x_alpha = old_x_alpha + new["x_alpha_new"]
        x_beta = old_x_beta + new["x_beta_new"]

        updated_raw[model] = {
            "alpha_raw": (x_alpha / n0) if n0 > 0 else np.nan,
            "n_credited": old["n_credited"], "n_used_credited": n0,
            "beta_raw": (x_beta / n1) if n1 > 0 else np.nan,
            "n_wrong": old["n_wrong"], "n_used_wrong": n1,
            "n_total_audited": n0 + n1,
        }

    # global anchor: recompute the same way as the published pooled_anchor,
    # aggregating ALL models' updated raw counts (not just T-C-touched ones)
    total_x_alpha = sum(round((d["alpha_raw"] if not np.isnan(d["alpha_raw"]) else 0.0) * d["n_used_credited"])
                        for d in updated_raw.values())
    total_n0 = sum(d["n_used_credited"] for d in updated_raw.values())
    total_x_beta = sum(round((d["beta_raw"] if not np.isnan(d["beta_raw"]) else 0.0) * d["n_used_wrong"])
                       for d in updated_raw.values())
    total_n1 = sum(d["n_used_wrong"] for d in updated_raw.values())
    pooled_alpha_new = total_x_alpha / total_n0
    pooled_beta_new = total_x_beta / total_n1

    updated = partial_pool(updated_raw, pooled_alpha_new, pooled_beta_new)
    return updated, {"pooled_alpha": pooled_alpha_new, "pooled_beta": pooled_beta_new,
                      "n_used_credited_total": total_n0, "n_used_wrong_total": total_n1}


def pair_bounds(a1, a2, r1, r2, m1, m2):
    """Reuse fb_reconcile_layers' exact per-pair computation for the audit-only,
    scorer-only, and combined layers (sampling layer unaffected by an audit
    that only touches alpha/beta, omitted here)."""
    box1_audit = wilson_ci(r1["x_alpha"], r1["n0_audit"], Z) + wilson_ci(r1["x_beta"], r1["n1_audit"], Z)
    box2_audit = wilson_ci(r2["x_alpha"], r2["n0_audit"], Z) + wilson_ci(r2["x_beta"], r2["n1_audit"], Z)
    lo_a, hi_a = bounded_comparison(a1, box1_audit, a2, box2_audit)

    box1_scorer = lambda_bounds(m1["alpha_pooled"], L_REFERENCE) + lambda_bounds(m1["beta_pooled"], L_REFERENCE)
    box2_scorer = lambda_bounds(m2["alpha_pooled"], L_REFERENCE) + lambda_bounds(m2["beta_pooled"], L_REFERENCE)
    lo_s, hi_s = bounded_comparison(a1, box1_scorer, a2, box2_scorer)

    box1_c = compound_bounds(r1["x_alpha"], r1["n0_audit"], L_REFERENCE) + \
        compound_bounds(r1["x_beta"], r1["n1_audit"], L_REFERENCE)
    box2_c = compound_bounds(r2["x_alpha"], r2["n0_audit"], L_REFERENCE) + \
        compound_bounds(r2["x_beta"], r2["n1_audit"], L_REFERENCE)
    lo_c, hi_c = bounded_comparison(a1, box1_c, a2, box2_c)

    return {"audit": (lo_a, hi_a), "scorer": (lo_s, hi_s), "combined": (lo_c, hi_c)}


if __name__ == "__main__":
    print("=" * 70)
    print("T-C alpha/beta update: folding 69 new real audit trials into the pool")
    print("=" * 70)

    key = load_key()
    l1_answers = load_l1()
    new_counts, n_indet = new_tc_counts_by_model(key, l1_answers)
    n_models_touched = len(new_counts)
    n0_new_total = sum(d["n0_new"] for d in new_counts.values())
    n1_new_total = sum(d["n1_new"] for d in new_counts.values())
    x_alpha_new_total = sum(d["x_alpha_new"] for d in new_counts.values())
    x_beta_new_total = sum(d["x_beta_new"] for d in new_counts.values())
    print(f"T-C usable rows: {n0_new_total + n1_new_total} ({n_indet} indeterminate excluded)")
    print(f"  new credited-stratum trials: {n0_new_total}, new false-credit events: {x_alpha_new_total}")
    print(f"  new wrong-stratum trials: {n1_new_total}, new false-miss events: {x_beta_new_total}")
    print(f"  distinct models touched: {n_models_touched}")

    with open("results/flipbudget/e4_mathhard_per_model.json", encoding="utf-8") as f:
        e4_file = json.load(f)
    e4_old = e4_file["per_model"]
    old_anchor = e4_file["pooled_anchor"]

    e4_new, new_anchor = rebuild_e4_with_new_audit(e4_old, new_counts)
    print(f"\nGlobal pooled anchor: alpha {old_anchor['alpha']:.4f} -> {new_anchor['pooled_alpha']:.4f}, "
          f"beta {old_anchor['beta']:.4f} -> {new_anchor['pooled_beta']:.4f}")
    print(f"Total audited n: credited {new_anchor['n_used_credited_total'] - n0_new_total} -> "
          f"{new_anchor['n_used_credited_total']}, wrong "
          f"{new_anchor['n_used_wrong_total'] - n1_new_total} -> {new_anchor['n_used_wrong_total']}")

    accs, _ = load_ea()
    rows_old, excl_old = build_model_table(accs, e4_old)
    rows_new, excl_new = build_model_table(accs, e4_new)
    print(f"\nQualifying models (n_used_credited>0 AND n_used_wrong>0): "
          f"{excl_old['n_qualifying']} -> {excl_new['n_qualifying']} (of {excl_old['n_total_models']})")
    newly_qualifying = sorted(set(rows_new) - set(rows_old))
    print(f"Newly qualifying (T-C's audit gave them their first trial in a "
          f"previously-empty stratum): {len(newly_qualifying)}")
    for m in newly_qualifying:
        print(f"  {m}: n0={rows_new[m]['n0_audit']} n1={rows_new[m]['n1_audit']}")

    print("\n--- Per-model alpha/beta pooled shift (models touched by T-C only) ---")
    per_model_shifts = []
    for m in sorted(new_counts.keys()):
        if m not in e4_old:
            continue
        old_a, new_a = e4_old[m]["alpha_pooled"], e4_new[m]["alpha_pooled"]
        old_b, new_b = e4_old[m]["beta_pooled"], e4_new[m]["beta_pooled"]
        old_ci_a = wilson_ci(rows_old[m]["x_alpha"], rows_old[m]["n0_audit"]) if m in rows_old else (np.nan, np.nan)
        new_ci_a = wilson_ci(rows_new[m]["x_alpha"], rows_new[m]["n0_audit"]) if m in rows_new else (np.nan, np.nan)
        old_w = old_ci_a[1] - old_ci_a[0] if m in rows_old else np.nan
        new_w = new_ci_a[1] - new_ci_a[0] if m in rows_new else np.nan
        per_model_shifts.append({"model": m, "alpha_pooled_old": old_a, "alpha_pooled_new": new_a,
                                  "beta_pooled_old": old_b, "beta_pooled_new": new_b,
                                  "alpha_wilson_width_old": old_w, "alpha_wilson_width_new": new_w})
        print(f"  {m[:40]:<41} alpha {old_a:.4f}->{new_a:.4f}  beta {old_b:.4f}->{new_b:.4f}  "
              f"alpha-CI-width {old_w if np.isfinite(old_w) else float('nan'):.4f}"
              f"->{new_w if np.isfinite(new_w) else float('nan'):.4f}")

    print("\n--- Pairwise identification impact, 136 real pairs ---")
    with open("results/analysis/pair_identification_human.json", encoding="utf-8") as f:
        pi = json.load(f)

    pair_results = []
    n_skipped = 0
    for p in pi["headline"]["pairs"]:
        m_lo, m_hi = p["lo"], p["hi"]
        if m_lo not in rows_new or m_hi not in rows_new or m_lo not in rows_old or m_hi not in rows_old:
            n_skipped += 1
            continue
        a1, a2 = rows_new[m_hi]["a_hat"], rows_new[m_lo]["a_hat"]  # a_hat is audit-independent, same both ways
        old_b = pair_bounds(a1, a2, rows_old[m_hi], rows_old[m_lo], e4_old[m_hi], e4_old[m_lo])
        new_b = pair_bounds(a1, a2, rows_new[m_hi], rows_new[m_lo], e4_new[m_hi], e4_new[m_lo])
        touched = m_hi in new_counts or m_lo in new_counts
        pair_results.append({"hi": m_hi, "lo": m_lo, "touched_by_tc": touched,
                              "old": old_b, "new": new_b})

    def contains_zero(bounds):
        lo, hi = bounds
        return lo <= 0 <= hi

    for layer in ("audit", "scorer", "combined"):
        old_zero = sum(1 for r in pair_results if contains_zero(r["old"][layer]))
        new_zero = sum(1 for r in pair_results if contains_zero(r["new"][layer]))
        old_w = np.median([r["old"][layer][1] - r["old"][layer][0] for r in pair_results])
        new_w = np.median([r["new"][layer][1] - r["new"][layer][0] for r in pair_results])
        n_flipped_to_resolved = sum(1 for r in pair_results
                                     if contains_zero(r["old"][layer]) and not contains_zero(r["new"][layer]))
        n_flipped_to_unresolved = sum(1 for r in pair_results
                                       if not contains_zero(r["old"][layer]) and contains_zero(r["new"][layer]))
        print(f"  [{layer}] median width {old_w:.4f}->{new_w:.4f}  "
              f"unresolved(contains 0) {old_zero}/{len(pair_results)} -> {new_zero}/{len(pair_results)}  "
              f"newly-resolved={n_flipped_to_resolved} newly-unresolved={n_flipped_to_unresolved}")

    n_touched_pairs = sum(1 for r in pair_results if r["touched_by_tc"])
    print(f"\nPairs scored: {len(pair_results)} (skipped {n_skipped}); "
          f"{n_touched_pairs} involve a T-C-audited model")

    out = {
        "n_tc_usable_rows": n0_new_total + n1_new_total, "n_indeterminate": n_indet,
        "n_models_touched": n_models_touched,
        "new_credited_trials": n0_new_total, "new_false_credit_events": x_alpha_new_total,
        "new_wrong_trials": n1_new_total, "new_false_miss_events": x_beta_new_total,
        "global_anchor_old": old_anchor, "global_anchor_new": new_anchor,
        "n_qualifying_old": excl_old["n_qualifying"], "n_qualifying_new": excl_new["n_qualifying"],
        "newly_qualifying_models": newly_qualifying,
        "per_model_shifts": per_model_shifts,
        "n_pairs_scored": len(pair_results), "n_pairs_skipped": n_skipped,
        "n_pairs_touched_by_tc": n_touched_pairs,
        "pair_results": pair_results,
    }
    with open("results/flipbudget/tc_alpha_beta_update.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=lambda o: list(o) if isinstance(o, tuple) else o)
    print("\nWritten to results/flipbudget/tc_alpha_beta_update.json")
