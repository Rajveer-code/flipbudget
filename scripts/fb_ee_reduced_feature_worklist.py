"""Real, capacity-respecting worklist for the REDUCED-FEATURE E-E model.

Full 9-feature EPV>=10 target (90 events) is unreachable on this roster (real
ceiling 52.7, see TC_ROSTER_PULL.md -- fb_tc_ee_real_worklist.py). User chose the
reduced-feature path: cut to the top-5 features by |standardized coefficient| from
the existing (underpowered, n=5) fit in ee_format_association.json. Explicit
caveat, not hidden: that coefficient ranking itself comes from a 5-event fit and is
therefore an unstable basis for feature selection -- it is a reasonable, data-driven
starting point, not a guaranteed-optimal one. Restated once labelling actually
starts producing more events, this ranking should be re-checked, not assumed final.

5 features x Peduzzi EPV>=10 = 50 events. Currently 5 -> 45 more needed. Unlike the
first-pass worklist (which assumed 100/pool and was wrong), this one walks REAL
per-pool availability from mathhard_full_roster.json directly and stops a pool when
it is actually exhausted, never assuming capacity that was not checked.

Zero new human labels produced. Run: python scripts/fb_ee_reduced_feature_worklist.py
"""
import json
from collections import defaultdict

BATCH_SIZE = 20
TARGET_ADDITIONAL_EVENTS = 45  # 50 total - 5 current
N_REDUCED_FEATURES = 5


def load():
    with open("results/analysis/mathhard_full_roster.json", encoding="utf-8") as f:
        population = json.load(f)["population"]
    with open("results/analysis/mathhard_labelling_key.json", encoding="utf-8") as f:
        audited = {(r["model"], r["item_id"]) for r in json.load(f)}
    with open("results/flipbudget/audit_expansion_design.json", encoding="utf-8") as f:
        pools = json.load(f)["all_pools_ranked"]
    with open("results/flipbudget/ee_format_association.json", encoding="utf-8") as f:
        coefs = json.load(f)["coefficients"]
    return population, audited, pools, coefs


def build_diversified_worklist(population, audited, pools, target_events, batch_size):
    """Walk pools in priority order, one batch at a time, ACTUALLY checking remaining
    capacity each round (not assumed). A pool drops out once its real supply of
    not-yet-audited items is exhausted. Loops rounds until target met or every pool
    is exhausted (the real ceiling, 52.7 events, is the hard cap -- verified >45)."""
    by_pool = defaultdict(list)
    for row in population:
        if (row["model"], row["item_id"]) in audited:
            continue
        by_pool[(row["model"], row["stratum"])].append(
            {"item_id": row["item_id"], "subject": row["subject"]})

    offsets = defaultdict(int)  # how many items already claimed from each pool
    worklist = []
    cumulative = 0.0
    round_num = 0
    while cumulative < target_events:
        round_num += 1
        made_progress = False
        for pool in pools:
            if cumulative >= target_events:
                break
            key = (pool["model"], pool["stratum"])
            available = by_pool.get(key, [])
            start = offsets[key]
            batch = available[start:start + batch_size]
            if not batch:
                continue  # this pool is exhausted, real capacity checked, not assumed
            offsets[key] += len(batch)
            gained = pool["rate"] * len(batch)
            cumulative += gained
            made_progress = True
            worklist.append({
                "round": round_num, "model": pool["model"], "stratum": pool["stratum"],
                "shrunk_rate": pool["rate"], "n_items_this_batch": len(batch),
                "item_ids": [b["item_id"] for b in batch],
                "subjects": [b["subject"] for b in batch],
                "expected_additional_events": gained,
                "cumulative_expected_events_after_this_row": cumulative,
            })
        if not made_progress:
            break  # every pool exhausted -- true ceiling reached, stop, report honestly
    return worklist, cumulative


if __name__ == "__main__":
    print("=" * 70)
    print("Reduced-feature E-E worklist (user-selected path)")
    print("=" * 70)
    population, audited, pools, coefs = load()

    ranked_features = sorted(coefs.items(), key=lambda x: -abs(x[1]))
    reduced = [name for name, _ in ranked_features[:N_REDUCED_FEATURES]]
    print(f"Top {N_REDUCED_FEATURES} features by |standardized coefficient| "
          f"(from the existing n=5-event fit -- unstable basis, stated explicitly):")
    for name, c in ranked_features[:N_REDUCED_FEATURES]:
        print(f"  {name:<18} {c:+.4f}")
    print(f"\nTarget: {N_REDUCED_FEATURES} features x EPV>=10 = "
          f"{N_REDUCED_FEATURES*10} events total. Currently 5 -> "
          f"{TARGET_ADDITIONAL_EVENTS} more needed.")

    worklist, cumulative = build_diversified_worklist(
        population, audited, pools, TARGET_ADDITIONAL_EVENTS, BATCH_SIZE)

    n_rounds = max((r["round"] for r in worklist), default=0)
    total_items = sum(r["n_items_this_batch"] for r in worklist)
    print(f"\nRounds used: {n_rounds}, total real items in worklist: {total_items}")
    print(f"Projected cumulative expected events: {5 + cumulative:.1f} "
          f"(target {N_REDUCED_FEATURES*10})")
    if 5 + cumulative >= N_REDUCED_FEATURES * 10:
        print("[OK] target reached with REAL, capacity-checked items -- not a projection.")
    else:
        print("[SHORTFALL] every available pool exhausted before reaching target -- "
              "this is the true ceiling, reported as such.")

    print(f"\nPer-round summary:")
    for rnd in range(1, n_rounds + 1):
        rows = [r for r in worklist if r["round"] == rnd]
        rnd_items = sum(r["n_items_this_batch"] for r in rows)
        rnd_gain = sum(r["expected_additional_events"] for r in rows)
        cum_after = rows[-1]["cumulative_expected_events_after_this_row"] if rows else 0.0
        print(f"  round {rnd}: {len(rows)} pools, {rnd_items} items, "
              f"+{rnd_gain:.1f} expected events, cumulative {cum_after:.1f}")

    out = {
        "reduced_features": reduced,
        "reduced_feature_coefficients": dict(ranked_features[:N_REDUCED_FEATURES]),
        "target_total_events": N_REDUCED_FEATURES * 10,
        "current_events": 5,
        "target_additional_events": TARGET_ADDITIONAL_EVENTS,
        "n_rounds": n_rounds,
        "total_items": total_items,
        "projected_cumulative_events": 5 + cumulative,
        "target_reached": (5 + cumulative) >= N_REDUCED_FEATURES * 10,
        "worklist": worklist,
    }
    with open("results/flipbudget/ee_reduced_feature_worklist.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/ee_reduced_feature_worklist.json")
