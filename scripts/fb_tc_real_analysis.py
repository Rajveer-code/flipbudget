"""T-C real analysis on the returned human labels.

Data status at time of this run (stated explicitly, not assumed later):
  - L1 (primary, 70 rows / 30 items): valid, verified. A handful of rows have
    your_answer literally "0" or "1" -- checked individually against their
    response text, confirmed these are genuine boxed answers of 0 or 1 (e.g.
    "a+b=\\boxed{1}"), not leftover broken labels, before trusting them.
  - L2 (overlap, 26 rows / 11 items): valid, delivered as a separate
    entry/uid/your_answer file; uid set cross-checked against the committed
    l2 sheet, exact match, 26/26.
  - L3 (overlap, 14 rows / 6 items): STILL the broken binary 0/1 scheme
    (verified: uid 22f02e1657e860a9's answer should be -35/9, matching L1 and
    L2's own transcription for the same item, but L3 shows "1"). NOT used
    here. Three-way agreement waits for a corrected L3.

Reuses the exact matches_gold/is_indeterminate logic already established and
validated in this project (ee_format_association.py / tc_correlated_error.py)
-- not reimplemented.

Run: python scripts/fb_tc_real_analysis.py
"""
import csv
import json
import sys
import types
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr

if "datasets" not in sys.modules:
    _stub = types.ModuleType("datasets")
    _stub.Dataset = object
    sys.modules["datasets"] = _stub

_spec_source = Path("vendor/leaderboard_math/utils.py")
import importlib.util
_spec = importlib.util.spec_from_file_location("leaderboard_math_utils", _spec_source)
mathutils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mathutils)

if not hasattr(__import__("signal"), "SIGALRM"):
    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import TimeoutError as FutureTimeout
    _orig = mathutils.is_equiv
    _pool = ThreadPoolExecutor(max_workers=4)

    def _is_equiv_deadline(x1, x2, seconds=1.0):
        fut = _pool.submit(_orig, x1, x2)
        try:
            return fut.result(timeout=seconds)
        except FutureTimeout:
            return False
    mathutils.is_equiv = _is_equiv_deadline


def is_indeterminate(answer):
    if answer is None or answer.strip() == "":
        return True
    return answer.strip().upper() in ("NONE", "CONTRADICTORY")


def matches_gold(answer, gold):
    a = mathutils.normalize_final_answer(answer)
    g = mathutils.normalize_final_answer(gold)
    return a.strip() == g.strip() or mathutils.is_equiv(a, g)


def load_l1():
    with open(r"C:\Users\Asus\Downloads\tc_expansion_l1 (2).csv", newline="", encoding="utf-8") as f:
        return {r["uid"]: r["your_answer"] for r in csv.DictReader(f)}


def load_l2():
    with open(r"C:\Users\Asus\Downloads\tc_expansion_l2_answers.csv", newline="", encoding="utf-8") as f:
        return {r["uid"]: r["your_answer"] for r in csv.DictReader(f)}


def load_key():
    with open("results/flipbudget/tc_expansion_key.json", encoding="utf-8") as f:
        d = json.load(f)
    return {r["uid"]: r for r in d["key"]}


if __name__ == "__main__":
    print("=" * 70)
    print("T-C real analysis -- L1 full set + L1xL2 agreement (L3 pending)")
    print("=" * 70)

    l1_answers = load_l1()
    l2_answers = load_l2()
    key = load_key()
    print(f"L1: {len(l1_answers)} rows, L2: {len(l2_answers)} rows, key: {len(key)} rows")

    # ---- Build per-row (human_correct, scorer_correct, wrong) using L1 ----
    records = []
    n_indeterminate = 0
    for uid, your_answer in l1_answers.items():
        k = key[uid]
        if is_indeterminate(your_answer):
            n_indeterminate += 1
            continue
        human_correct = matches_gold(your_answer, k["gold"])
        scorer_correct = (k["stratum"] == "credited")
        wrong = scorer_correct != human_correct
        records.append({"uid": uid, "model": k["model"], "item_id": k["item_id"],
                         "stratum": k["stratum"], "subject": k["subject"],
                         "your_answer": your_answer, "gold": k["gold"],
                         "human_correct": human_correct, "scorer_correct": scorer_correct,
                         "scorer_wrong": wrong})

    print(f"\nL1 usable records (indeterminate excluded): {len(records)} of {len(l1_answers)} "
          f"({n_indeterminate} indeterminate)")
    n_wrong = sum(1 for r in records if r["scorer_wrong"])
    print(f"Scorer-wrong events found in this NEW audit: {n_wrong} of {len(records)} "
          f"({100*n_wrong/len(records):.1f}%)")
    for r in records:
        if r["scorer_wrong"]:
            print(f"  WRONG: uid={r['uid'][:12]} model={r['model']} stratum={r['stratum']} "
                  f"your_answer={r['your_answer'][:40]!r} gold={r['gold']!r}")

    # ---- Item-level paired test (T-C's core question), mirroring
    # tc_correlated_error.py's methodology exactly, on this NEW real data ----
    print()
    print("-" * 70)
    print("Item-level paired test (same item, >=2 models)")
    print("-" * 70)
    by_item = defaultdict(list)
    for r in records:
        by_item[r["item_id"]].append(r)

    marginal_rate = defaultdict(list)
    for r in records:
        marginal_rate[r["model"]].append(r["scorer_wrong"])
    marginal_rate = {m: np.mean(v) for m, v in marginal_rate.items()}

    pairs = []
    for item_id, recs in by_item.items():
        if len(recs) < 2:
            continue
        for r1, r2 in combinations(recs, 2):
            pairs.append({"item_id": item_id, "model1": r1["model"], "model2": r2["model"],
                          "wrong1": r1["scorer_wrong"], "wrong2": r2["scorer_wrong"],
                          "expected1": marginal_rate[r1["model"]], "expected2": marginal_rate[r2["model"]]})

    print(f"Paired (model_i, model_j, same item) observations: {len(pairs)}")
    if len(pairs) < 10:
        print("STOPPING (item-level): fewer than 10 valid paired observations -- reporting")
        print("as an honest null result on sample-size grounds, not evidence of no correlation.")
        item_result = {"n_valid_pairs": len(pairs), "conclusion": "insufficient_data"}
    else:
        w1 = np.array([1 if p["wrong1"] else 0 for p in pairs])
        w2 = np.array([1 if p["wrong2"] else 0 for p in pairs])
        exp1 = np.array([p["expected1"] for p in pairs])
        exp2 = np.array([p["expected2"] for p in pairs])
        observed_both = np.mean(w1 & w2)
        expected_both = np.mean(exp1 * exp2)
        ratio = observed_both / expected_both if expected_both > 0 else np.nan
        n_either = int(np.sum(w1 | w2))
        n_both = int(np.sum(w1 & w2))
        print(f"Observed P(both wrong): {observed_both:.4f}  Expected under independence: {expected_both:.4f}")
        print(f"Either-wrong: {n_either}/{len(pairs)}  Both-wrong: {n_both}/{len(pairs)}")
        if len(set(w1)) > 1 and len(set(w2)) > 1:
            r_corr, pval = pearsonr(w1, w2)
            print(f"Pearson r={r_corr:.3f}, p={pval:.4f}")
        else:
            r_corr, pval = None, None
            print("Pearson not computable (no variance in one arm)")

        if n_either < 5:
            verdict = "UNDERPOWERED"
        elif ratio is not None and np.isfinite(ratio) and ratio > 1.2 and (pval is None or pval < 0.10):
            verdict = "POSITIVE_CORRELATION"
        elif ratio is not None and np.isfinite(ratio) and ratio < 0.8:
            verdict = "NEGATIVE_CORRELATION"
        else:
            verdict = "NO_CLEAR_CORRELATION"
        print(f"VERDICT: {verdict}")
        item_result = {"n_valid_pairs": len(pairs), "n_either_wrong": n_either, "n_both_wrong": n_both,
                        "observed_both": float(observed_both), "expected_both": float(expected_both),
                        "ratio": float(ratio) if np.isfinite(ratio) else None,
                        "pearson_r": float(r_corr) if r_corr is not None else None,
                        "pearson_p": float(pval) if pval is not None else None, "verdict": verdict}

    # ---- L1 x L2 inter-rater agreement on the 26-row overlap ----
    print()
    print("-" * 70)
    print("L1 x L2 inter-rater agreement (26-row overlap; L3 pending)")
    print("-" * 70)
    overlap_uids = set(l1_answers.keys()) & set(l2_answers.keys())
    print(f"Overlap rows: {len(overlap_uids)}")
    n_raw_match, n_derived_match, n_checked = 0, 0, 0
    disagreements = []
    for uid in sorted(overlap_uids):
        a1, a2 = l1_answers[uid].strip(), l2_answers[uid].strip()
        raw_match = a1 == a2
        gold = key[uid]["gold"]
        i1, i2 = is_indeterminate(a1), is_indeterminate(a2)
        if i1 or i2:
            derived_match = (i1 == i2) and (a1.upper() == a2.upper() if i1 and i2 else False)
        else:
            derived_match = matches_gold(a1, gold) == matches_gold(a2, gold)
        n_checked += 1
        n_raw_match += raw_match
        n_derived_match += derived_match
        if not derived_match:
            disagreements.append({"uid": uid, "l1": a1, "l2": a2, "gold": gold})

    print(f"Raw string agreement: {n_raw_match}/{n_checked} ({100*n_raw_match/n_checked:.1f}%)")
    print(f"Derived (matches_gold) agreement: {n_derived_match}/{n_checked} "
          f"({100*n_derived_match/n_checked:.1f}%)")
    if disagreements:
        print("Disagreements (derived-correctness level):")
        for d in disagreements:
            print(f"  uid={d['uid'][:12]} L1={d['l1']!r} L2={d['l2']!r} gold={d['gold']!r}")

    out = {
        "l1_n_rows": len(l1_answers), "l1_n_usable": len(records), "l1_n_indeterminate": n_indeterminate,
        "l1_n_scorer_wrong": n_wrong,
        "item_level_test": item_result,
        "l1_records": records,
        "agreement_l1_l2": {
            "n_overlap": n_checked, "n_raw_match": int(n_raw_match), "n_derived_match": int(n_derived_match),
            "raw_agreement_rate": n_raw_match / n_checked, "derived_agreement_rate": n_derived_match / n_checked,
            "disagreements": disagreements,
        },
        "l3_status": "still using the broken binary 0/1 scheme, not included in this run",
    }
    with open("results/flipbudget/tc_real_analysis.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/tc_real_analysis.json")
