"""Split the T-C 70-row blinded sheet into l1/l2/l3 for 3 independent labelers,
mirroring the exact overlap convention this project's OWN human-labeling
protocol already uses for the main MATH-Hard audit (mathhard_l1/l2/l3.csv:
400/151/75, ~37.75%/18.75% of the full set, l3 nested inside l2) and the
masterplan's own H-B item ("...=3 blind labellers; per-stratum agreement...
cross-vendor adjudication").

Overlap is stratified by ITEM, not row: an item's rows (the paired
observations T-C needs) always travel together into an overlap subset, so
agreement can be checked on genuinely paired items rather than fragments of a
pair landing in different labelers' sheets. l2/l3 are NESTED (l3 subset of
l2 subset of l1), matching the original protocol exactly, enabling pairwise
(l1xl2, l1xl3, l2xl3) and three-way agreement checks once all three come back.

Does NOT redraw the sample -- reuses the ALREADY-COMMITTED 70-row/30-item
selection from fb_tc_labeling_package.py exactly. Only splits it.

Run: python scripts/fb_tc_multi_labeler_split.py
"""
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
L2_ITEM_FRACTION = 151 / 400  # exact ratio the original mathhard_l2.csv used
L3_ITEM_FRACTION = 75 / 400   # exact ratio the original mathhard_l3.csv used


def load():
    with open("labeling/tc_expansion_l1.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open("results/flipbudget/tc_expansion_key.json", encoding="utf-8") as f:
        key_data = json.load(f)
    uid_to_item = {r["uid"]: r["item_id"] for r in key_data["key"]}
    return rows, uid_to_item


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["uid", "problem", "response", "your_answer"])
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    print("=" * 70)
    print("T-C multi-labeler split (l1 full / l2 nested overlap / l3 nested overlap)")
    print("=" * 70)
    rows, uid_to_item = load()
    by_item = defaultdict(list)
    for r in rows:
        by_item[uid_to_item[r["uid"]]].append(r)

    items = sorted(by_item.keys())
    n_items = len(items)
    n_l2 = round(n_items * L2_ITEM_FRACTION)
    n_l3 = round(n_items * L3_ITEM_FRACTION)
    print(f"Full set (l1): {len(rows)} rows, {n_items} items")

    rng = random.Random(SEED)
    l2_items = set(rng.sample(items, n_l2))
    l3_items = set(rng.sample(sorted(l2_items), n_l3))  # nested inside l2, matching original protocol

    l2_rows = [r for r in rows if uid_to_item[r["uid"]] in l2_items]
    l3_rows = [r for r in rows if uid_to_item[r["uid"]] in l3_items]

    print(f"l2 (2nd labeler): {len(l2_items)} items, {len(l2_rows)} rows "
          f"({100*len(l2_items)/n_items:.1f}% of items)")
    print(f"l3 (3rd labeler): {len(l3_items)} items, {len(l3_rows)} rows "
          f"({100*len(l3_items)/n_items:.1f}% of items, nested inside l2)")

    ok_nested = l3_items.issubset(l2_items)
    print(f"[{'OK' if ok_nested else 'FAIL'}] l3 items are a subset of l2 items: {ok_nested}")

    out_dir = Path("labeling")
    write_csv(out_dir / "tc_expansion_l2.csv", l2_rows)
    write_csv(out_dir / "tc_expansion_l3.csv", l3_rows)
    print(f"\nWritten: labeling/tc_expansion_l2.csv ({len(l2_rows)} rows)")
    print(f"Written: labeling/tc_expansion_l3.csv ({len(l3_rows)} rows)")

    meta = {
        "seed": SEED, "n_items_total": n_items, "l2_item_fraction_target": L2_ITEM_FRACTION,
        "l3_item_fraction_target": L3_ITEM_FRACTION,
        "l2_items": sorted(l2_items), "l3_items": sorted(l3_items),
        "l2_n_rows": len(l2_rows), "l3_n_rows": len(l3_rows),
        "l3_nested_in_l2": ok_nested,
    }
    with open("results/flipbudget/tc_multi_labeler_split.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Written: results/flipbudget/tc_multi_labeler_split.json")
