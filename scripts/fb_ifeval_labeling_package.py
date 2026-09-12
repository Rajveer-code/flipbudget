"""Build the blinded IFEval labeling sheet from the 454-item audit sample.
Same blinding scheme as T-C (sha256(stratum|model|key)[:16]), same reasons
(HUMAN_LABELING_GUIDE.md's rationale applies identically: never show the
labeler the model, the automated verdict, or which stratum an item is in).

Labeling question, since IFEval has no separate gold-answer transcription
step: does the response comply with the instruction(s) stated in the prompt?
your_judgment: YES / NO / PARTIAL (some but not all instructions followed,
for multi-instruction prompts).

Run: python scripts/fb_ifeval_labeling_package.py
"""
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from fb_eb_ifeval_pull import fetch_model_ifeval

RESPONSE_TRUNCATE = 6000


def load_sample():
    with open("results/flipbudget/ifeval_audit_sample.json", encoding="utf-8") as f:
        return json.load(f)["sample"]


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval labeling package: blinded CSV + separate key")
    print("=" * 70)
    sample = load_sample()
    by_model = {}
    for r in sample:
        by_model.setdefault(r["model"], set()).add(r["key"])

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN not set in this shell.")

    rows_csv, rows_key = [], []
    for i, (model, keys) in enumerate(by_model.items(), 1):
        raw_rows = fetch_model_ifeval(model, token)
        found = {r["doc"]["key"]: r for r in raw_rows if r["doc"]["key"] in keys}
        print(f"  [{i}/{len(by_model)}] {model}: {len(found)} of {len(keys)} needed items found")
        for k in keys:
            row = found.get(k)
            if row is None:
                continue
            doc = row["doc"]
            resps = row.get("resps") or row.get("filtered_resps") or []
            if not resps:
                continue
            response = resps[0][0] if isinstance(resps[0], list) else resps[0]
            if not isinstance(response, str):
                continue
            sample_row = next(r for r in sample if r["model"] == model and r["key"] == k)
            raw_id = f"{sample_row['stratum']}|{model}|{k}"
            uid = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:16]
            rows_csv.append({"uid": uid, "prompt": doc["prompt"],
                              "response": response[:RESPONSE_TRUNCATE], "your_judgment": ""})
            rows_key.append({"uid": uid, "model": model, "key": k,
                              "stratum": sample_row["stratum"], "strict": sample_row["strict"],
                              "loose": sample_row["loose"],
                              "nondeterminism_flagged": sample_row["nondeterminism_flagged"],
                              "instruction_id_list": doc["instruction_id_list"]})

    print(f"\nTotal blinded rows: {len(rows_csv)} of {len(sample)} sample items")

    out_dir = Path("labeling")
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "ifeval_audit_l1.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["uid", "prompt", "response", "your_judgment"])
        w.writeheader()
        w.writerows(rows_csv)
    print(f"BLINDED CSV: {csv_path} ({len(rows_csv)} rows)")

    key_path = Path("results/flipbudget/ifeval_audit_key.json")
    with open(key_path, "w", encoding="utf-8") as f:
        json.dump({"n_rows": len(rows_key), "key": rows_key}, f, indent=2)
    print(f"KEY (do not open while labeling): {key_path}")

    csv_uids = {r["uid"] for r in rows_csv}
    key_uids = {r["uid"] for r in rows_key}
    print(f"\n[{'OK' if csv_uids == key_uids and len(csv_uids) == len(rows_csv) else 'FAIL'}] "
          f"uid sets match, no duplicates: {csv_uids == key_uids and len(csv_uids) == len(rows_csv)}")
