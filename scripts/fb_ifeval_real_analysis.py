"""IFEval real analysis on the returned human labels (454 rows, 1=fully
compliant / 0=not fully compliant). Compares automatic scorer verdict (strict)
-> human verdict -> known verifier-bug cases (the 96-item corrected
nondeterminism scan) -> unexplained cases, and quantifies alpha, beta,
benchmark-score, and identification-uncertainty impact.

Convention used for the 1/0 labels (stated explicitly, not hidden): 1 = fully
compliant (matches YES), 0 = not fully compliant (collapses NO and PARTIAL).
This is exact and lossless for comparison against STRICT specifically, since
strict's own definition requires full compliance -- anything less (NO or
PARTIAL) is correctly "not strict-compliant" either way. It loses the
NO-vs-PARTIAL distinction as a separate descriptive statistic; 22 of 454 rows
(multi-instruction prompts marked 0) are flagged as unresolvable on that
narrower question alone, not on the alpha/beta/accuracy analysis below.

Stratified design (not a simple random sample): both_pass full population
5,071 (40 sampled), disagree full population 374 (374 sampled = full
census), both_fail full population 9,162 (40 sampled). Population-weighted
(Horvitz-Thompson) estimates used wherever an overall (not per-stratum)
number is reported, so the oversampled "disagree" stratum doesn't bias the
combined estimate.

Run: python scripts/fb_ifeval_real_analysis.py
"""
import csv
import json
import sys
from collections import defaultdict

import numpy as np

Z = 1.96
POP_SIZES = {"both_pass": 5071, "disagree": 374, "both_fail": 9162}
N_TOTAL_POP = sum(POP_SIZES.values())


def wilson_ci(x, n, z=Z):
    if n == 0:
        return (np.nan, np.nan)
    p = x / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def load_judged():
    with open("C:/Users/Asus/Downloads/ifeval_audit_l1_judged.csv", newline="", encoding="utf-8") as f:
        return {r["uid"]: r["your_judgment"].strip() for r in csv.DictReader(f)}


def load_key():
    with open("results/flipbudget/ifeval_audit_key.json", encoding="utf-8") as f:
        return {r["uid"]: r for r in json.load(f)["key"]}


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval real analysis -- 454 human judgments")
    print("=" * 70)

    judged = load_judged()
    key = load_key()
    assert set(judged) == set(key), "uid set mismatch -- stop"
    print(f"Rows: {len(judged)}, all uids matched to key")

    vals = set(judged.values())
    print(f"Distinct your_judgment values: {vals}")
    if vals - {"0", "1"}:
        raise SystemExit(f"Unexpected judgment values {vals - {'0','1'}} -- stop, do not guess.")

    records = []
    for uid, v in judged.items():
        k = key[uid]
        human_correct = (v == "1")
        scorer_correct = k["strict"]
        records.append({
            "uid": uid, "model": k["model"], "key": k["key"],
            "stratum": k["stratum"], "strict": k["strict"], "loose": k["loose"],
            "nondeterminism_flagged": k["nondeterminism_flagged"],
            "n_instructions": len(k["instruction_id_list"]),
            "human_correct": human_correct, "scorer_correct": scorer_correct,
            "scorer_wrong": human_correct != scorer_correct,
        })

    n_ambiguous = sum(1 for r in records if r["human_correct"] is False and r["n_instructions"] > 1)
    print(f"\n[LIMITATION, flagged not hidden] {n_ambiguous}/{len(records)} rows are marked "
          f"'0' on a multi-instruction prompt -- could be NO or a collapsed PARTIAL, not "
          f"separately distinguishable from this file. Does not affect the alpha/beta/"
          f"accuracy analysis below (both correctly count as 'not strict-compliant'); only "
          f"blocks a separate NO-vs-PARTIAL breakdown, not attempted here.")

    # ---- scorer verdict vs human verdict: known-bug vs unexplained ----
    print()
    print("-" * 70)
    print("Scorer-wrong events: known-bug (nondeterminism-flagged) vs unexplained")
    print("-" * 70)
    n_wrong = sum(1 for r in records if r["scorer_wrong"])
    n_wrong_flagged = sum(1 for r in records if r["scorer_wrong"] and r["nondeterminism_flagged"])
    n_wrong_unexplained = n_wrong - n_wrong_flagged
    print(f"Total scorer-wrong events (human disagrees with strict verdict): "
          f"{n_wrong}/{len(records)} ({100*n_wrong/len(records):.1f}%)")
    print(f"  on a known-verifier-bug item: {n_wrong_flagged} ({100*n_wrong_flagged/n_wrong:.1f}% of wrong events)"
          if n_wrong else "  (no wrong events)")
    print(f"  unexplained by either known mechanism: {n_wrong_unexplained} "
          f"({100*n_wrong_unexplained/n_wrong:.1f}% of wrong events)" if n_wrong else "")

    by_stratum = defaultdict(list)
    for r in records:
        by_stratum[r["stratum"]].append(r)
    print("\nPer-stratum breakdown:")
    for s in ("both_pass", "disagree", "both_fail"):
        rs = by_stratum[s]
        wrong = sum(1 for r in rs if r["scorer_wrong"])
        print(f"  {s}: n_sampled={len(rs)} (of {POP_SIZES[s]} population), "
              f"scorer_wrong={wrong}/{len(rs)} ({100*wrong/len(rs):.1f}%)")

    # ---- alpha: false-credit rate, both_pass stratum ----
    print()
    print("-" * 70)
    print("Alpha (false-credit: strict says compliant, human says not)")
    print("-" * 70)
    bp = by_stratum["both_pass"]
    x_alpha = sum(1 for r in bp if r["scorer_wrong"])
    n_alpha = len(bp)
    alpha_hat = x_alpha / n_alpha
    alpha_lo, alpha_hi = wilson_ci(x_alpha, n_alpha)
    print(f"both_pass sample: {x_alpha}/{n_alpha} false-credits, "
          f"alpha_hat={alpha_hat:.4f}, 95% Wilson CI=[{alpha_lo:.4f},{alpha_hi:.4f}]")

    # ---- beta: false-reject rate, disagree + both_fail (strict=False) ----
    print()
    print("-" * 70)
    print("Beta (false-reject: strict says non-compliant, human says fully compliant)")
    print("-" * 70)
    dis, bf = by_stratum["disagree"], by_stratum["both_fail"]
    x_beta_dis, n_beta_dis = sum(1 for r in dis if r["scorer_wrong"]), len(dis)
    x_beta_bf, n_beta_bf = sum(1 for r in bf if r["scorer_wrong"]), len(bf)
    beta_dis_hat = x_beta_dis / n_beta_dis
    beta_bf_hat = x_beta_bf / n_beta_bf
    beta_dis_ci = wilson_ci(x_beta_dis, n_beta_dis)  # full census -- no extrapolation, but CI still reflects finite-n human-labeling noise
    beta_bf_ci = wilson_ci(x_beta_bf, n_beta_bf)
    print(f"disagree (FULL CENSUS, no sampling error on which items, only on the human read): "
          f"{x_beta_dis}/{n_beta_dis} false-rejects among strict=False items that ARE actually "
          f"loose=True, beta_hat={beta_dis_hat:.4f}, CI=[{beta_dis_ci[0]:.4f},{beta_dis_ci[1]:.4f}]")
    print(f"both_fail (comparison sample, 40 of {POP_SIZES['both_fail']}): "
          f"{x_beta_bf}/{n_beta_bf}, beta_hat={beta_bf_hat:.4f}, "
          f"CI=[{beta_bf_ci[0]:.4f},{beta_bf_ci[1]:.4f}]")

    # population-weighted (Horvitz-Thompson) overall beta across both strict=False strata
    n_beta_pop = POP_SIZES["disagree"] + POP_SIZES["both_fail"]
    beta_overall = (POP_SIZES["disagree"] * beta_dis_hat + POP_SIZES["both_fail"] * beta_bf_hat) / n_beta_pop
    # variance of a population-weighted mean of two independent sample proportions
    var_dis = beta_dis_hat * (1 - beta_dis_hat) / n_beta_dis if n_beta_dis > 0 else 0
    var_bf = beta_bf_hat * (1 - beta_bf_hat) / n_beta_bf if n_beta_bf > 0 else 0
    w_dis, w_bf = POP_SIZES["disagree"] / n_beta_pop, POP_SIZES["both_fail"] / n_beta_pop
    se_overall = np.sqrt((w_dis**2) * var_dis + (w_bf**2) * var_bf)
    print(f"Population-weighted overall beta (Horvitz-Thompson, weights "
          f"{POP_SIZES['disagree']}/{n_beta_pop} disagree + {POP_SIZES['both_fail']}/{n_beta_pop} both_fail): "
          f"{beta_overall:.4f} +/- {Z*se_overall:.4f} (95%)")

    # ---- benchmark score impact: population-weighted human-corrected strict accuracy ----
    print()
    print("-" * 70)
    print("Benchmark-score impact: naive vs human-corrected overall strict accuracy")
    print("-" * 70)
    naive_strict_acc = POP_SIZES["both_pass"] / N_TOTAL_POP  # strict=True fraction, exact from full roster
    # human-corrected: both_pass items are credited unless alpha says otherwise;
    # strict=False items are rejected unless beta says otherwise
    corrected_true_positives = POP_SIZES["both_pass"] * (1 - alpha_hat) + n_beta_pop * beta_overall
    corrected_strict_acc = corrected_true_positives / N_TOTAL_POP
    print(f"Naive overall strict accuracy (raw, uncorrected): {naive_strict_acc:.4f}")
    print(f"Human-corrected overall strict accuracy estimate: {corrected_strict_acc:.4f} "
          f"(shift: {corrected_strict_acc - naive_strict_acc:+.4f})")

    # ---- per-model: only where sample size gives any real signal ----
    print()
    print("-" * 70)
    print("Per-model scorer_wrong rate (descriptive only -- ~17 rows/model average, "
          "NOT a corrected per-model accuracy estimate -- too thin for that)")
    print("-" * 70)
    by_model = defaultdict(list)
    for r in records:
        by_model[r["model"]].append(r)
    model_rates = []
    for m, rs in sorted(by_model.items()):
        n_wrong_m = sum(1 for r in rs if r["scorer_wrong"])
        model_rates.append({"model": m, "n_sampled": len(rs), "n_scorer_wrong": n_wrong_m,
                             "rate": n_wrong_m / len(rs)})
    for r in sorted(model_rates, key=lambda x: -x["rate"])[:5]:
        print(f"  {r['model'][:40]:<41} {r['n_scorer_wrong']}/{r['n_sampled']} ({100*r['rate']:.1f}%)")
    print(f"  ... ({len(model_rates)} models total, min n_sampled="
          f"{min(r['n_sampled'] for r in model_rates)}, max={max(r['n_sampled'] for r in model_rates)})")
    print("  Model-ranking conclusion: sample too thin per model (avg "
          f"{454/len(model_rates):.1f} rows/model) to support any per-model corrected ranking "
          "-- reporting descriptively, not treating as a ranking result.")

    out = {
        "n_rows": len(records), "n_ambiguous_partial_ineligible": n_ambiguous,
        "n_scorer_wrong": n_wrong, "n_scorer_wrong_known_bug": n_wrong_flagged,
        "n_scorer_wrong_unexplained": n_wrong_unexplained,
        "alpha": {"x": x_alpha, "n": n_alpha, "hat": alpha_hat, "ci": [alpha_lo, alpha_hi]},
        "beta_disagree": {"x": x_beta_dis, "n": n_beta_dis, "hat": beta_dis_hat, "ci": list(beta_dis_ci)},
        "beta_both_fail": {"x": x_beta_bf, "n": n_beta_bf, "hat": beta_bf_hat, "ci": list(beta_bf_ci)},
        "beta_overall_population_weighted": {"hat": beta_overall, "se": se_overall, "ci95": [beta_overall - Z*se_overall, beta_overall + Z*se_overall]},
        "naive_strict_accuracy": naive_strict_acc,
        "human_corrected_strict_accuracy": corrected_strict_acc,
        "per_model_rates": model_rates,
        "per_stratum": {s: {"n_sampled": len(by_stratum[s]), "n_population": POP_SIZES[s],
                             "n_scorer_wrong": sum(1 for r in by_stratum[s] if r["scorer_wrong"])}
                        for s in POP_SIZES},
        "records": records,
    }
    with open("results/flipbudget/ifeval_real_analysis.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/ifeval_real_analysis.json")
