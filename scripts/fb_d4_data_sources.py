"""D4/D5 -- data source audit for the E1 pilot.

Answers, from files already on disk (no new API spend): which benchmarks have
usable item-level or pair-level data for the flip-budget pilot, and what exactly
each one provides. Writes results/flipbudget/d4_data_sources.json.

Run: python scripts/fb_d4_data_sources.py
"""
import json
import os

OUT = "results/flipbudget/d4_data_sources.json"


def check_mmlu():
    with open("results/analysis/b0_scores.json") as f:
        d = json.load(f)
    n_model_task_rows = len(d["per_item"])
    n_items_per_row = len(d["per_item"][0]["rows"])
    with open("results/analysis/human_labels.json") as f:
        hl = json.load(f)
    benches = sorted(set(k.split("|")[0] for k in hl.keys()))
    models = sorted(set(k.split("|")[1] for k in hl.keys()))
    return {
        "usable_for_e1": True,
        "raw_item_level_data": "results/analysis/b0_scores.json",
        "n_model_task_combinations": n_model_task_rows,
        "n_items_per_combination": n_items_per_row,
        "total_responses": n_model_task_rows * n_items_per_row,
        "extractors_per_item": ["strict_match_extracted", "flexible_extracted", "robust_letter"],
        "human_audit_file": "results/analysis/human_labels.json",
        "human_audit_n_items": len(hl),
        "human_audit_benchmarks": benches,
        "human_audit_models_covered": models,
        "human_audit_n_models": len(models),
        "note": "audit covers only 3 of the roster's models -- per-model estimates "
                "for the other 11 models in e3_roster.json have no direct human "
                "audit and must rely entirely on partial pooling toward the "
                "3-model pooled rate, or be flagged as unaudited.",
    }


def check_mathhard():
    with open("results/analysis/mathhard_human_margins.json") as f:
        mm = json.load(f)
    with open("results/analysis/mathhard_labelling_key.json") as f:
        key = json.load(f)
    with open("results/analysis/pair_identification_human.json") as f:
        pairs = json.load(f)
    from collections import Counter
    per_model = Counter(item["model"] for item in key)
    counts = sorted(per_model.values())
    return {
        "usable_for_e1": "partial",
        "raw_item_level_data": "results/cache_l1/ (Open LLM Leaderboard generations, "
                                "per PREREGISTRATION_AUDIT.md -- not directly re-read here, "
                                "already processed into the files below)",
        "pooled_margins_file": "results/analysis/mathhard_human_margins.json",
        "pooled_margins_are": "stratum-pooled across all 28 models -- NOT per-model",
        "pair_level_gaps_file": "results/analysis/pair_identification_human.json",
        "n_pairs_with_real_gap": pairs["headline"]["n_pairs"],
        "n_roster_models": pairs["n_models"],
        "phibar_used_pooled": pairs["phibar_used"],
        "labelling_key_has_model_field": True,
        "per_model_audit_counts": {
            "n_models_with_any_audit": len(per_model),
            "n_roster_models": 28,
            "min": counts[0],
            "median": counts[len(counts) // 2],
            "max": counts[-1],
        },
        "note": "per-model gap and margin are both available in principle (gap "
                "directly from pair_identification_human.json, margin re-sliceable "
                "from mathhard_labelling_key.json), but per-model differential "
                "flip-budget computation is deferred to E4/E5 pending the "
                "re-slicing + partial-pooling script. This E1 pass uses MATH-Hard "
                "ONLY as a Case-A (pooled, non-differential) check using the real "
                "378 pair gaps against the real pooled phibar -- not yet the full "
                "differential Case-B treatment.",
    }


def check_gsm8k():
    with open("results/analysis/gsm8k_scores.json") as f:
        d = json.load(f)
    return {
        "usable_for_e1": False,
        "reason": f"design requested {d['design']['n_items_requested']} items but "
                  f"scores file has n_scored={d['scores'][0]['n_scored']} for the "
                  f"one model checked -- a partial/interrupted run, not item-level "
                  f"(no per-item rows, only aggregate strict/flexible rate per "
                  f"model). Generation logs exist (results/runs/gsm8k_generate_*.json, "
                  f"dated 2026-09-05) but were not re-read here to control cost; "
                  f"a full item-level GSM8K pilot needs a fresh scoring pass over "
                  f"the existing generations, which is free (no new API calls, "
                  f"already-generated responses just need re-scoring) -- flagged "
                  f"as a candidate task, not done in this pass.",
    }


if __name__ == "__main__":
    result = {
        "generated": "2026-09-09, this session",
        "purpose": "settle which benchmarks are usable for the E1 pilot before "
                   "promising a benchmark count, per PLAN_FLIPBUDGET.md D5",
        "mmlu": check_mmlu(),
        "math_hard": check_mathhard(),
        "gsm8k": check_gsm8k(),
    }
    os.makedirs("results/flipbudget", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    print(f"\nWritten to {OUT}")
