"""Data-quality check on the returned IFEval human labels, triggered by an
extreme, implausible result: the naive analysis found 92.5%/85.8% "false-reject"
rates in the both_fail/disagree strata (human says compliant on items the
verifier -- both strict AND loose -- says are not), which would mean the
verifier is wrong almost every time it confidently rejects a response. Spot
inspection of 3 both_fail-marked-compliant rows found 2 with clear,
mechanically-verifiable constraint violations the label missed (a forbidden
letter appearing 11x; a required exact-phrase response replaced by a
paragraph). This script checks ALL 454 rows systematically, using the REAL
verifier's own per-instruction breakdown (inst_level_strict_acc), not a
regex approximation, before trusting any of the naive analysis's numbers.

Refetches doc+response for the exact 454 sampled (model,key) pairs (kwargs
weren't cached when the sheet was built, only instruction_id_list) and
verifies the refetched response text matches the judged CSV exactly before
using anything.

Run: python scripts/fb_ifeval_label_quality_check.py
"""
import csv
import json
import sys
from collections import defaultdict

sys.path.insert(0, "scripts")
from fb_eb_ifeval_pull import fetch_model_ifeval, load_ifeval_verifier
from huggingface_hub import get_token
import truststore
truststore.inject_into_ssl()


def load_judged():
    with open("C:/Users/Asus/Downloads/ifeval_audit_l1_judged.csv", newline="", encoding="utf-8") as f:
        return {r["uid"]: r for r in csv.DictReader(f)}


def load_key():
    with open("results/flipbudget/ifeval_audit_key.json", encoding="utf-8") as f:
        return {r["uid"]: r for r in json.load(f)["key"]}


def load_flagged_keys():
    with open("results/flipbudget/ifeval_nondeterminism_flagged_items.json", encoding="utf-8") as f:
        return set(int(k) for k in json.load(f)["flagged_keys"].keys())


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval label quality check -- per-instruction ground truth")
    print("=" * 70)

    judged = load_judged()
    key = load_key()
    flagged_keys = load_flagged_keys()
    process_results = load_ifeval_verifier()

    token = get_token()
    if not token:
        raise SystemExit("No local HF token found.")

    by_model = defaultdict(list)
    for uid, k in key.items():
        by_model[k["model"]].append((uid, k["key"]))

    n_text_mismatch = 0
    rows = []
    for i, (model, pairs) in enumerate(sorted(by_model.items()), 1):
        wanted_keys = {k for _, k in pairs}
        raw = fetch_model_ifeval(model, token)
        found = {r["doc"]["key"]: r for r in raw if r["doc"]["key"] in wanted_keys}
        print(f"  [{i}/{len(by_model)}] {model}: {len(found)}/{len(wanted_keys)} items refetched")
        for uid, k_key in pairs:
            row = found.get(k_key)
            if row is None:
                continue
            doc = row["doc"]
            resps = row.get("resps") or row.get("filtered_resps") or []
            response = resps[0][0] if isinstance(resps[0], list) else resps[0]
            if response != judged[uid]["response"]:
                n_text_mismatch += 1
                continue
            out = process_results(doc, [response])
            rows.append({
                "uid": uid, "model": model, "key": k_key,
                "instruction_id_list": doc["instruction_id_list"],
                "inst_level_strict": out["inst_level_strict_acc"],
                "human_marked_compliant": judged[uid]["your_judgment"].strip() == "1",
            })

    print(f"\nText mismatches on refetch (should be 0): {n_text_mismatch}")
    print(f"Rows checked: {len(rows)}")

    # For every row the human marked fully compliant (1), find any FAILED
    # instruction under strict that is NOT on the nondeterminism-flagged list
    # -- a deterministic checker saying "failed" on a non-flagged instruction
    # is ground truth, not a maybe.
    contradicted = []
    for r in rows:
        if not r["human_marked_compliant"]:
            continue
        if r["key"] in flagged_keys:
            continue  # can't use this row as clean ground truth either way
        failed_instructions = [iid for iid, ok in zip(r["instruction_id_list"], r["inst_level_strict"]) if not ok]
        if failed_instructions:
            contradicted.append({**r, "failed_instructions": failed_instructions})

    print(f"\nRows human-marked COMPLIANT (1), on a non-flagged item, where the real "
          f"verifier found a concrete failed instruction: {len(contradicted)}")

    by_instruction_type = defaultdict(int)
    for c in contradicted:
        for iid in c["failed_instructions"]:
            by_instruction_type[iid] += 1
    print("\nWhich instruction types are being missed (contradicted rows, count by failed id):")
    for iid, n in sorted(by_instruction_type.items(), key=lambda x: -x[1]):
        print(f"  {iid}: {n}")

    n_human_compliant_nonflagged = sum(1 for r in rows if r["human_marked_compliant"] and r["key"] not in flagged_keys)
    print(f"\nOf {n_human_compliant_nonflagged} human-marked-compliant, non-flagged rows: "
          f"{len(contradicted)} ({100*len(contradicted)/n_human_compliant_nonflagged:.1f}%) "
          f"are contradicted by a concrete, deterministic, non-flagged instruction failure.")

    with open("results/flipbudget/ifeval_label_quality_check.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_rows_checked": len(rows), "n_text_mismatch": n_text_mismatch,
            "n_human_compliant_nonflagged": n_human_compliant_nonflagged,
            "n_contradicted": len(contradicted),
            "pct_contradicted": 100 * len(contradicted) / n_human_compliant_nonflagged if n_human_compliant_nonflagged else None,
            "by_instruction_type": dict(by_instruction_type),
            "contradicted_rows": contradicted,
        }, f, indent=2)
    print("\nWritten to results/flipbudget/ifeval_label_quality_check.json")
