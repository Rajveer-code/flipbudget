"""Audit-expansion design -- computation only, no new labels. Per TIER1_VERDICT.md
point 3: the concrete next step is a targeted audit expansion, stratified to be
wrongness-event-rich (oversample low-accuracy / any-alpha>0 models), sized to
actually power T-C and E-E before either is re-attempted. This script computes the
worklist; it does NOT and cannot perform the labelling itself -- that is the user's
own manual work (a genuine human-labelling-only blocker, per standing instructions).

Uses the EXISTING empirical-Bayes shrinkage estimates already computed by the E4
pipeline (alpha_pooled, beta_pooled, shrinkage_weight_*) rather than inventing a new
smoothing rule -- these are the project's own established, already-verified per-model
rate estimates, and are a better predictor of a NEW item's expected yield than either
the raw (noisy, sometimes zero-n) rate or the pooled-only rate alone.

Targets used, both real and citable, not invented:
  E-E (format-association AUC): >=10 events per predictor variable (Peduzzi, Concato,
  Kemper, Holford & Feinstein 1996, "A simulation study of the number of events per
  variable in logistic regression analysis") -- 9 features -> >=90 events.
  T-C (item-overlap correlation): no analogous named rule for a paired-binary
  correlation test at this scale; uses this project's own established minimum-count
  convention (n>=5, already used by E-A's robustness filter and T-C's own cell-level
  test's n>=3 cell floor) applied to the number of EITHER-wrong paired observations
  needed for a Pearson correlation estimate to be minimally trustworthy, scaled up by
  an order of magnitude (>=20) since a single-digit count produced exactly the
  degenerate 1/41 result Tier 1 hit. Labelled explicitly as a planning-level target,
  not a formal power calculation, because no effect size exists yet to power against
  -- that absence is what T-C is trying to resolve.

Run: python scripts/fb_audit_expansion_design.py
"""
import json


PEDUZZI_EPV = 10  # events per variable, Peduzzi et al. 1996
N_EE_FEATURES = 9  # from scripts/ee_format_association.py's feature_names
TC_TARGET_EITHER_WRONG = 20  # planning-level, see module docstring
BATCH_SIZE = 20  # items per worklist row, a practical labelling-session unit


def shrunk_rate(raw, pooled, weight):
    if raw is None:
        return pooled
    return weight * raw + (1 - weight) * pooled


def load_per_model():
    with open("results/flipbudget/e4_mathhard_per_model.json") as f:
        e4 = json.load(f)
    return e4["per_model"]


def build_pools(per_model):
    """One row per (model, stratum): current audit n, shrunk expected-yield rate."""
    pools = []
    for model, m in per_model.items():
        pools.append({
            "model": model, "stratum": "credited",
            "n_audited": m["n_used_credited"],
            "raw": m["alpha_raw"], "pooled": m["alpha_pooled"],
            "weight": m["shrinkage_weight_alpha"],
            "rate": shrunk_rate(m["alpha_raw"], m["alpha_pooled"], m["shrinkage_weight_alpha"]),
        })
        pools.append({
            "model": model, "stratum": "wrong_parsed",
            "n_audited": m["n_used_wrong"],
            "raw": m["beta_raw"], "pooled": m["beta_pooled"],
            "weight": m["shrinkage_weight_beta"],
            "rate": shrunk_rate(m["beta_raw"], m["beta_pooled"], m["shrinkage_weight_beta"]),
        })
    return sorted(pools, key=lambda p: -p["rate"])


def greedy_worklist(pools, target_additional_events, batch_size=BATCH_SIZE, max_rounds=10):
    """Multiple DIVERSIFIED rounds: round 1 draws one batch from every positive-rate
    pool in priority order (not just the single best pool), round 2 repeats the same
    pass if target is not yet met, and so on up to max_rounds.

    Deliberate design choice, not a simplification: for E-E specifically, concentrating
    the whole expansion in one or two models would reintroduce the exact confound E-E
    exists to rule out -- whether an association is with FORMAT or merely with being a
    PARTICULAR model, since format is partly a house-style property of the model. Model
    diversity in the new audit sample is a requirement, not a nicety, so each round
    spreads batches across every positive-rate pool before any pool gets a second one.
    This is a planning projection (expected value), not a guarantee -- flagged as such
    in the report."""
    positive_pools = [p for p in pools if p["rate"] > 0]
    worklist = []
    cumulative = 0.0
    for round_num in range(1, max_rounds + 1):
        if cumulative >= target_additional_events:
            break
        for pool in positive_pools:
            if cumulative >= target_additional_events:
                break
            gained = pool["rate"] * batch_size
            cumulative += gained
            worklist.append({
                "round": round_num,
                "model": pool["model"], "stratum": pool["stratum"],
                "current_n_audited": pool["n_audited"],
                "shrunk_rate": pool["rate"],
                "additional_items_recommended": batch_size,
                "expected_additional_events": gained,
                "cumulative_expected_events_after_this_row": cumulative,
            })
    return worklist, cumulative


if __name__ == "__main__":
    print("=" * 70)
    print("AUDIT-EXPANSION DESIGN -- computation only, no new labels performed")
    print("=" * 70)

    per_model = load_per_model()
    pools = build_pools(per_model)
    print(f"Models: {len(per_model)}, pools (model x stratum): {len(pools)}")
    print()
    print("Top 8 pools by shrunk expected-yield rate (oversampling priority order):")
    for p in pools[:8]:
        raw_str = f"{p['raw']:.4f}" if p['raw'] is not None else "None"
        print(f"  {p['model']:<45} {p['stratum']:<13} n_audited={p['n_audited']:<4} "
              f"raw={raw_str:<8} pooled={p['pooled']:.4f} weight={p['weight']:.3f} "
              f"-> shrunk_rate={p['rate']:.4f}")

    with open("results/flipbudget/ee_format_association.json") as f:
        ee = json.load(f)
    with open("results/flipbudget/tc_correlated_error.json") as f:
        tc = json.load(f)
    current_ee_events = ee["n_wrong"]
    current_ee_n = ee["n_records"]
    current_tc_events = tc["item_level"]["n_either_wrong"]
    current_tc_n = tc["item_level"]["n_valid_pairs"]

    print()
    print("-" * 70)
    print("E-E TARGET (Peduzzi et al. 1996, EPV >= 10, 9 features -> >=90 events)")
    print("-" * 70)
    ee_target_total = PEDUZZI_EPV * N_EE_FEATURES
    ee_additional_needed = max(0, ee_target_total - current_ee_events)
    print(f"  current: {current_ee_events} wrongness events in {current_ee_n} records")
    print(f"  target: {ee_target_total} events total -> {ee_additional_needed} MORE needed")

    ee_worklist, ee_cumulative = greedy_worklist(pools, ee_additional_needed)
    n_rounds = max(row["round"] for row in ee_worklist) if ee_worklist else 0
    total_items = len(ee_worklist) * BATCH_SIZE
    print(f"\n  DESIGN: each round spreads one {BATCH_SIZE}-item batch across every")
    print("  positive-rate pool (model diversity is required, not optional -- see")
    print("  module docstring: concentrating on 1-2 models would reintroduce exactly")
    print("  the model-vs-format confound E-E exists to rule out).")
    print(f"\n  Round 1 detail ({sum(1 for r in ee_worklist if r['round']==1)} pools, "
          f"illustrative -- later rounds repeat the same pool order):")
    for row in ee_worklist:
        if row["round"] != 1:
            continue
        print(f"    +{row['additional_items_recommended']} items from "
              f"{row['model']} / {row['stratum']}  (current n_audited="
              f"{row['current_n_audited']}, rate={row['shrunk_rate']:.4f}) "
              f"-> expected +{row['expected_additional_events']:.2f} events")
    print(f"\n  Round-by-round summary:")
    for rnd in range(1, n_rounds + 1):
        rows = [r for r in ee_worklist if r["round"] == rnd]
        rnd_gain = sum(r["expected_additional_events"] for r in rows)
        cum_after = rows[-1]["cumulative_expected_events_after_this_row"] if rows else 0.0
        print(f"    round {rnd}: {len(rows)} pools x {BATCH_SIZE} items = "
              f"{len(rows)*BATCH_SIZE} items, +{rnd_gain:.1f} expected events, "
              f"cumulative {cum_after:.1f}")
    print(f"\n  Total: {len(ee_worklist)} batches, {total_items} items across "
          f"{n_rounds} round(s).")
    print(f"  Projected cumulative expected events: {current_ee_events + ee_cumulative:.1f} "
          f"(target {ee_target_total})")
    if current_ee_events + ee_cumulative < ee_target_total:
        print(f"  SHORTFALL: even after {n_rounds} rounds ({total_items} items), the "
              f"full-roster ceiling at these rates is not enough to reach {ee_target_total}.")
        print("  This is a real finding, not a script limitation: at the observed/pooled")
        print("  rates (~1.6-7.6% per item), reaching a clean EPV>=10 target requires")
        print("  either far more items than 1-2 focused rounds, or accepting a lower")
        print("  interim target for a first, still-informative expansion.")
    print("  NOTE: this is an EXPECTED VALUE projection from shrunk point estimates,")
    print("  not a guarantee -- actual yield will vary, and some pools may not have")
    print("  this many un-audited items available (pool availability is NOT verified")
    print("  in this pass; see caveat below).")

    print()
    print("-" * 70)
    print(f"T-C TARGET (planning-level: >={TC_TARGET_EITHER_WRONG} either-wrong paired "
          f"observations)")
    print("-" * 70)
    print(f"  current: {current_tc_events} of {current_tc_n} valid paired observations "
          f"have any wrongness event")
    print("  T-C's test needs NEW shared items (audited on >=2 models each), not just")
    print("  more items on one model -- the exact candidate item list requires the raw")
    print("  per-model generation cache (which items each model was evaluated on),")
    print("  which is NOT available in this repo's results/analysis/ snapshot (checked:")
    print("  e3_roster.json is sampling-design metadata, not a per-item roster).")
    print("  FLAGGED, not fabricated: the mechanical next step before labelling T-C's")
    print("  expansion is to pull that roster from the companion project's raw cache.")
    print("  Stratification RULE (usable once that roster is available): prioritize")
    print("  items scored by model PAIRS where at least one model is in the top-8 pools")
    print("  above (nonzero shrunk alpha or beta), since those are the pairs most likely")
    print("  to produce a wrongness event on at least one side of the pair.")
    avg_rate = sum(p["rate"] for p in pools) / len(pools)
    rough_items_scale = TC_TARGET_EITHER_WRONG / avg_rate if avg_rate > 0 else None
    print(f"  Rough planning scale (roster-average shrunk rate={avg_rate:.4f}, NOT the")
    print(f"  priority-weighted rate the real worklist would use): order-of-magnitude "
          f"~{rough_items_scale:.0f} shared items would be needed if drawn at the")
    print("  roster-average rate; the real number is lower if drawn preferentially from")
    print("  the high-rate pools above, exactly as E-E's worklist does.")

    print()
    print("=" * 70)
    print("WHAT THIS SCRIPT DOES NOT DO")
    print("=" * 70)
    print("- Does not select or label any actual item. Zero new human labels produced.")
    print("- Does not verify how many un-audited items actually remain available in")
    print("  each high-priority pool (would require the raw per-model results file).")
    print("- T-C's worklist is a planning-level scale estimate, not an item-level")
    print("  worklist like E-E's, for the roster-data reason stated above.")
    print("Executing either worklist is the user's own manual labelling work.")
    print("=" * 70)

    out = {
        "peduzzi_epv_rule": PEDUZZI_EPV,
        "ee_n_features": N_EE_FEATURES,
        "ee_target_total_events": ee_target_total,
        "ee_current_events": current_ee_events,
        "ee_additional_needed": ee_additional_needed,
        "ee_worklist": ee_worklist,
        "ee_projected_cumulative_events": current_ee_events + ee_cumulative,
        "tc_target_either_wrong_planning_level": TC_TARGET_EITHER_WRONG,
        "tc_current_either_wrong": current_tc_events,
        "tc_current_valid_pairs": current_tc_n,
        "tc_roster_average_shrunk_rate": avg_rate,
        "tc_rough_item_scale_estimate": rough_items_scale,
        "tc_note": "item-level worklist blocked on raw per-model roster data, not "
                   "available in results/analysis/ snapshot -- flagged, not fabricated",
        "all_pools_ranked": pools,
    }
    with open("results/flipbudget/audit_expansion_design.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/audit_expansion_design.json")
