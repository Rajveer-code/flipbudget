"""Final blinding verification, both labeling packages, before handoff.
Checks: no model-name substring, no stratum word, no scorer-verdict field,
anywhere in the header or cell content of either blinded CSV. Confirms row
counts and uid uniqueness. Does not modify either CSV.

Run: python scripts/fb_blinding_verification.py
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from fb_eb_ifeval_pull import load_roster_models

FORBIDDEN_COLUMNS = {"model", "stratum", "strict", "loose", "verdict", "key",
                      "gold", "correct", "disagree", "nondeterminism_flagged"}
STRATUM_WORDS = ["both_pass", "both_fail", "disagree", "credited", "wrong_parsed", "unparsed"]

SHEETS = [
    ("T-C L1 (70-row)", "labeling/tc_expansion_l1.csv"),
    ("T-C L2 (26-row)", "labeling/tc_expansion_l2.csv"),
    ("T-C L3 (14-row)", "labeling/tc_expansion_l3.csv"),
    ("IFEval L1 (454-row)", "labeling/ifeval_audit_l1.csv"),
]


def check_sheet(name, path):
    print(f"\n--- {name}: {path} ---")
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    header = set(rows[0].keys()) if rows else set()
    print(f"  rows: {len(rows)}")
    print(f"  columns: {sorted(header)}")

    bad_cols = header & FORBIDDEN_COLUMNS
    print(f"  [{'FAIL' if bad_cols else 'OK'}] forbidden columns present: {bad_cols or 'none'}")

    uids = [r.get("uid") for r in rows]
    dup = len(uids) != len(set(uids))
    print(f"  [{'FAIL' if dup else 'OK'}] uid uniqueness: "
          f"{len(set(uids))}/{len(uids)} unique")

    full_text = "\n".join(",".join(str(v) for v in r.values()) for r in rows)
    model_hits = [m for m in models if m.lower() in full_text.lower()]
    print(f"  [{'REVIEW' if model_hits else 'OK'}] model-name substring hits: "
          f"{model_hits or 'none'}")

    stratum_hits = [w for w in STRATUM_WORDS if w in full_text]
    print(f"  [{'REVIEW' if stratum_hits else 'OK'}] stratum-word hits: "
          f"{stratum_hits or 'none'}")

    return {"name": name, "path": path, "n_rows": len(rows), "columns": sorted(header),
            "forbidden_columns_present": sorted(bad_cols), "uid_unique": not dup,
            "model_name_hits": model_hits, "stratum_word_hits": stratum_hits}


if __name__ == "__main__":
    print("=" * 70)
    print("Final blinding verification -- T-C and IFEval labeling packages")
    print("=" * 70)
    models = load_roster_models()
    print(f"Checking against {len(models)}-model roster")

    results = [check_sheet(name, path) for name, path in SHEETS]

    all_clean = all(
        not r["forbidden_columns_present"] and r["uid_unique"]
        and not r["model_name_hits"] and not r["stratum_word_hits"]
        for r in results
    )
    print(f"\n{'='*70}")
    print(f"[{'ALL CLEAN' if all_clean else 'REVIEW NEEDED'}]")

    with open("results/flipbudget/blinding_verification.json", "w", encoding="utf-8") as f:
        json.dump({"all_clean": all_clean, "sheets": results}, f, indent=2)
    print("Written to results/flipbudget/blinding_verification.json")
