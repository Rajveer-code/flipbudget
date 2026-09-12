"""Recompute nondeterminism_flagged on the 454-row audit KEY (not the sheet --
labeling/ifeval_audit_l1.csv has no such column and is untouched) against the
corrected 96-item mechanism set from fb_ifeval_mechanism_rescan.py. The key
file's flags were built from the original, incomplete 33-item scan; this
brings them in line with the source-verified set before the post-labeling
analysis needs them.

Run: python scripts/fb_ifeval_key_reflag.py
"""
import json
from pathlib import Path

KEY_PATH = Path("results/flipbudget/ifeval_audit_key.json")
FLAGGED_PATH = Path("results/flipbudget/ifeval_nondeterminism_flagged_items.json")

if __name__ == "__main__":
    with open(FLAGGED_PATH, encoding="utf-8") as f:
        flagged_keys = set(int(k) for k in json.load(f)["flagged_keys"].keys())

    with open(KEY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # Idempotency: this file records its own before/after once corrected. A
    # second run must not recompute n_before from the ALREADY-corrected
    # nondeterminism_flagged values on disk -- that would silently replace
    # the true historical "29" with "75" (the same self-comparison bug
    # fb_ifeval_mechanism_rescan.py had, caught by fb_reproduce_all.py).
    already_corrected = data.get("reflagged_with_corrected_scan", False)
    n_before = data["n_flagged_before_correction"] if already_corrected else \
        sum(1 for r in data["key"] if r["nondeterminism_flagged"])

    newly_flagged_uids = []
    for r in data["key"]:
        was = r["nondeterminism_flagged"]
        r["nondeterminism_flagged"] = r["key"] in flagged_keys
        if r["nondeterminism_flagged"] and not was:
            newly_flagged_uids.append(r["uid"])
    n_after = sum(1 for r in data["key"] if r["nondeterminism_flagged"])

    print(f"nondeterminism_flagged on the 454-row sample: {n_before} -> {n_after} "
          f"(+{len(newly_flagged_uids)} rows newly flagged vs. original, corrected mechanism scan)")
    if already_corrected:
        print(f"  (n_before={n_before} preserved from the original correction, not "
              f"recomputed from already-corrected data on disk)")

    data["reflagged_with_corrected_scan"] = True
    data["n_flagged_before_correction"] = n_before
    data["n_flagged_after_correction"] = n_after

    with open(KEY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Written to {KEY_PATH}")
