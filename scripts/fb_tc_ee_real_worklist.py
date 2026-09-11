"""Real, item-level audit-expansion worklists for E-E and T-C, built from the full
roster pulled by fb_pull_roster.py (results/analysis/mathhard_full_roster.json,
cross-validated 0 mismatches against the existing audit key -- see that script's
output). Replaces the RATE-PROJECTION worklist in audit_expansion_design.json with
REAL item_ids and REAL pool-availability counts (resolving that file's stated
caveat: "pool availability is NOT verified in this pass").

E-E: real not-yet-audited item_ids per (model,stratum) pool, in the SAME priority
order as audit_expansion_design.json's pool ranking (recomputed nowhere -- reused
directly from that file so the two stay consistent).

T-C: since 89.8% of items are scored by ALL 27 models (fb_pull_roster.py), and the
current audit covers only ~400 of 35,613 (model,item) rows, most not-yet-audited
items are simultaneously available across MANY models at once. Finds items where
>=2 HIGH-PRIORITY pools (by the same ranking) both have a not-yet-audited record for
the SAME item_id -- real (item_id, model_A, model_B) candidates for new paired
observations, which is what T-C's test structurally needs and what was blocked last
pass.

Zero new human labels produced. Run: python scripts/fb_tc_ee_real_worklist.py
"""
import json
from collections import defaultdict
from itertools import combinations

BATCH_SIZE = 20
N_ROUNDS = 5
TOP_N_POOLS_FOR_TC = 12  # how many top pools count as "high-priority" for T-C pairing


def load():
    with open("results/analysis/mathhard_full_roster.json", encoding="utf-8") as f:
        roster = json.load(f)
    with open("results/analysis/mathhard_labelling_key.json", encoding="utf-8") as f:
        key = json.load(f)
    with open("results/flipbudget/audit_expansion_design.json", encoding="utf-8") as f:
        design = json.load(f)
    audited = {(r["model"], r["item_id"]) for r in key}
    return roster["population"], audited, design["all_pools_ranked"]


def build_ee_worklist(population, audited, pools):
    # index: (model,stratum) -> list of not-yet-audited item_ids, subject attached
    by_pool = defaultdict(list)
    for row in population:
        key = (row["model"], row["stratum"])
        if (row["model"], row["item_id"]) in audited:
            continue
        by_pool[key].append({"item_id": row["item_id"], "subject": row["subject"]})

    worklist = []
    cumulative_capacity_used = 0
    for round_num in range(1, N_ROUNDS + 1):
        for pool in pools:
            key = (pool["model"], "credited" if pool["stratum"] == "credited" else "wrong_parsed")
            available = by_pool.get(key, [])
            start = (round_num - 1) * BATCH_SIZE
            batch = available[start:start + BATCH_SIZE]
            if not batch:
                continue
            worklist.append({
                "round": round_num, "model": pool["model"], "stratum": pool["stratum"],
                "shrunk_rate": pool["rate"],
                "n_available_total_not_yet_audited": len(available),
                "items_this_batch": batch,
            })
    return worklist, by_pool


def build_tc_worklist(population, audited, pools):
    top_pools = {(p["model"], p["stratum"]): p["rate"] for p in pools[:TOP_N_POOLS_FOR_TC]}
    # for each item_id, which (model,stratum) TOP pools have a not-yet-audited record
    by_item = defaultdict(list)
    for row in population:
        pool_key = (row["model"], row["stratum"])
        if pool_key not in top_pools:
            continue
        if (row["model"], row["item_id"]) in audited:
            continue
        by_item[row["item_id"]].append({
            "model": row["model"], "stratum": row["stratum"],
            "subject": row["subject"], "rate": top_pools[pool_key],
        })

    candidates = []
    for item_id, records in by_item.items():
        if len(records) < 2:
            continue
        models_here = {r["model"] for r in records}
        if len(models_here) < 2:
            continue  # same model in both strata isn't a cross-model pair
        for r1, r2 in combinations(records, 2):
            if r1["model"] == r2["model"]:
                continue
            score = r1["rate"] * r2["rate"]  # joint expected-yield proxy
            candidates.append({
                "item_id": item_id, "subject": r1["subject"],
                "model_a": r1["model"], "stratum_a": r1["stratum"], "rate_a": r1["rate"],
                "model_b": r2["model"], "stratum_b": r2["stratum"], "rate_b": r2["rate"],
                "joint_score": score,
            })
    candidates.sort(key=lambda c: -c["joint_score"])
    return candidates


if __name__ == "__main__":
    print("=" * 70)
    print("Real item-level worklists: E-E and T-C")
    print("=" * 70)
    population, audited, pools = load()
    print(f"Population rows: {len(population)}, already-audited: {len(audited)}, "
          f"pools ranked: {len(pools)}")

    print()
    print("-" * 70)
    print("E-E: real not-yet-audited item_ids per pool")
    print("-" * 70)
    ee_worklist, by_pool = build_ee_worklist(population, audited, pools)
    n_rounds_actual = max((r["round"] for r in ee_worklist), default=0)
    total_items = sum(len(r["items_this_batch"]) for r in ee_worklist)
    print(f"Rounds produced: {n_rounds_actual} (target {N_ROUNDS}), "
          f"total real items listed: {total_items}")
    print(f"\nPer-pool availability (top 10 pools, capacity check):")
    for pool in pools[:10]:
        key = (pool["model"], pool["stratum"])
        avail = len(by_pool.get(key, []))
        needed = N_ROUNDS * BATCH_SIZE
        status = "OK" if avail >= needed else f"SHORT by {needed - avail}"
        print(f"  {pool['model']:<45} {pool['stratum']:<13} available={avail:<6} "
              f"needed_for_{N_ROUNDS}_rounds={needed:<5} [{status}]")
    short_pools = [p for p in pools if len((by_pool.get((p["model"], p["stratum"]), []))) < N_ROUNDS * BATCH_SIZE
                   and len(by_pool.get((p["model"], p["stratum"]), [])) > 0]
    print(f"\nPools with SOME availability but short of {N_ROUNDS} full rounds: {len(short_pools)}")
    zero_pools = [p for p in pools if len(by_pool.get((p["model"], p["stratum"]), [])) == 0]
    print(f"Pools with ZERO not-yet-audited items available: {len(zero_pools)}")
    if zero_pools:
        for p in zero_pools[:5]:
            print(f"  {p['model']} / {p['stratum']}")

    # Real ceiling: use ALL available items in every positive-rate pool (not capped
    # at 5 rounds x 20/pool), and report the true achievable expected-event total --
    # this is what the round-capped worklist above was silently short of.
    real_ceiling_events = 0.0
    real_ceiling_items = 0
    for pool in pools:
        avail = by_pool.get((pool["model"], pool["stratum"]), [])
        real_ceiling_items += len(avail)
        real_ceiling_events += pool["rate"] * len(avail)
    print(f"\nREAL CEILING (every available not-yet-audited item in every positive-rate")
    print(f"pool, no round cap): {real_ceiling_items} items available, "
          f"{real_ceiling_events:.1f} expected events.")
    print(f"vs. previous pass's rate-projection ceiling of 90.2 events from 2700 items:")
    if real_ceiling_events >= 90:
        print(f"  [OK] real available population CAN reach the 90-event EPV target "
              f"(using {real_ceiling_items} real items, not a projection).")
    else:
        print(f"  [SHORTFALL] even using EVERY available not-yet-audited item across "
              f"all {len(pools)} pools, only {real_ceiling_events:.1f} expected events are")
        print(f"  reachable -- the previous pass's projection assumed more per-pool")
        print(f"  capacity than actually exists. This is the honest real number.")

    print()
    print("-" * 70)
    print(f"T-C: real (item, model_A, model_B) candidates, top-{TOP_N_POOLS_FOR_TC} pools")
    print("-" * 70)
    tc_candidates = build_tc_worklist(population, audited, pools)
    print(f"Total real cross-model candidate pairs found: {len(tc_candidates)}")
    print(f"\nTop 15 by joint expected-yield score:")
    for c in tc_candidates[:15]:
        print(f"  item={c['item_id'][:16]}... subject={c['subject']:<20} "
              f"{c['model_a']} ({c['stratum_a']}, r={c['rate_a']:.3f}) x "
              f"{c['model_b']} ({c['stratum_b']}, r={c['rate_b']:.3f}) "
              f"joint={c['joint_score']:.4f}")

    n_target = 20  # T-C's planning-level target from AUDIT_EXPANSION_DESIGN.md
    top_n_items = {c["item_id"] for c in tc_candidates[:n_target * 2]}
    print(f"\nDistinct items in top {n_target*2} candidate pairs: {len(top_n_items)}")
    print(f"(labelling these items on BOTH named models gives {min(len(tc_candidates), n_target*2)} "
          f"real new paired observations toward T-C's >=20 either-wrong-observation target)")

    out = {
        "ee_worklist": ee_worklist,
        "ee_pool_availability": {
            f"{p['model']}|{p['stratum']}": len(by_pool.get((p["model"], p["stratum"]), []))
            for p in pools
        },
        "ee_zero_availability_pools": [{"model": p["model"], "stratum": p["stratum"]} for p in zero_pools],
        "ee_real_ceiling_items": real_ceiling_items,
        "ee_real_ceiling_expected_events": real_ceiling_events,
        "tc_top_pools_used": TOP_N_POOLS_FOR_TC,
        "tc_n_candidates": len(tc_candidates),
        "tc_top_candidates": tc_candidates[:100],
    }
    with open("results/flipbudget/tc_ee_real_worklist.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/tc_ee_real_worklist.json")
