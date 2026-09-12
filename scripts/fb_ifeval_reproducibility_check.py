"""The reproducibility check requested before any IFEval human labeling starts.

Runs the real verifier multiple times in genuinely FRESH PROCESSES (subprocess.run,
not repeated in-process calls -- so no shared random-module state leaks between
"runs", matching how the harness is actually invoked once per independent
evaluation) over every row whose item-key carries a known nondeterminism
mechanism (see fb_ifeval_mechanism_rescan.py -- corrected to 96/541 items,
not the original 33). Two conditions:

  UNSEEDED : the real, shipping condition. DetectorFactory.seed left at its
             default (None) and the keywords:letter_frequency random.choice
             fallback left unseeded -- exactly what the actual harness run
             experiences.
  SEEDED   : control. random.seed(42) + DetectorFactory.seed=42 fixed before
             each replicate. If this collapses all variance to zero while
             UNSEEDED does not, that is direct causal confirmation (not just
             correlation) that the seed is what's driving the instability.

Quantifies:
  1. item-level verdict volatility (does strict/loose flip across replicates)
  2. benchmark-score impact (overall strict accuracy across replicate universes)
  3. model-ranking impact (per-model rank stability across replicate universes)
  4. the corrected fraction of the 380 real disagreements explained by a known
     mechanism, now using the 96-item corrected set instead of the original 33

Does NOT touch labeling/ifeval_audit_l1.csv or the composition of
ifeval_audit_sample.json -- only reads cached rows and roster data, and writes
its own new output file plus (separately, after this) an updated
nondeterminism_flagged annotation, never the sheet itself.

Run: python scripts/fb_ifeval_reproducibility_check.py
"""
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import kendalltau

N_UNSEEDED_REPLICATES = 15
N_SEEDED_REPLICATES = 5
SEED = 42

ROWCACHE_PATH = Path("results/flipbudget/ifeval_repro_rowcache.json")
ROSTER_PATH = Path("results/analysis/ifeval_full_roster.json")
FLAGGED_PATH = Path("results/flipbudget/ifeval_nondeterminism_flagged_items.json")
OUT_PATH = Path("results/flipbudget/ifeval_reproducibility_check.json")


def run_replicate(cache_path, out_path, seed=None):
    cmd = [sys.executable, "scripts/_ifeval_repro_worker.py", str(cache_path), str(out_path)]
    if seed is not None:
        cmd.append(str(seed))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"worker failed: {result.stderr[-2000:]}")
    with open(out_path, encoding="utf-8") as f:
        return json.load(f)


def kendall_rank_stability(baseline_acc, replicate_accs):
    """baseline_acc, replicate_accs: dict[model] -> accuracy. Returns
    (tau, max_abs_rank_shift, top_model_changed)."""
    models = sorted(baseline_acc.keys())
    base_rank = {m: r for r, m in enumerate(sorted(models, key=lambda m: -baseline_acc[m]))}
    rep_rank = {m: r for r, m in enumerate(sorted(models, key=lambda m: -replicate_accs[m]))}
    base_vec = [base_rank[m] for m in models]
    rep_vec = [rep_rank[m] for m in models]
    tau, _ = kendalltau(base_vec, rep_vec)
    max_shift = max(abs(base_rank[m] - rep_rank[m]) for m in models)
    base_top = min(models, key=lambda m: base_rank[m])
    rep_top = min(models, key=lambda m: rep_rank[m])
    return float(tau), int(max_shift), base_top != rep_top


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval reproducibility check -- fresh-process replicates")
    print("=" * 70)

    with open(ROWCACHE_PATH, encoding="utf-8") as f:
        rowcache = json.load(f)["rows"]
    with open(ROSTER_PATH, encoding="utf-8") as f:
        roster = json.load(f)["population"]
    with open(FLAGGED_PATH, encoding="utf-8") as f:
        flagged_meta = json.load(f)
    flagged_keys = set(int(k) for k in flagged_meta["flagged_keys"].keys())

    print(f"Rowcache: {len(rowcache)} (model,key) rows, {len(flagged_keys)} flagged item-keys")
    print(f"Roster (full population): {len(roster)} rows")

    tmpdir = Path(tempfile.mkdtemp(prefix="ifeval_repro_"))
    print(f"Replicate temp dir: {tmpdir}")

    unseeded_replicates = []
    for i in range(N_UNSEEDED_REPLICATES):
        out_path = tmpdir / f"unseeded_{i}.json"
        rep = run_replicate(ROWCACHE_PATH, out_path, seed=None)
        unseeded_replicates.append(rep)
        print(f"  unseeded replicate {i+1}/{N_UNSEEDED_REPLICATES} done "
              f"(env={rep['env']})")

    seeded_replicates = []
    for i in range(N_SEEDED_REPLICATES):
        out_path = tmpdir / f"seeded_{i}.json"
        rep = run_replicate(ROWCACHE_PATH, out_path, seed=SEED)
        seeded_replicates.append(rep)
        print(f"  seeded replicate {i+1}/{N_SEEDED_REPLICATES} done "
              f"(env={rep['env']})")

    # --- 1. item-level verdict volatility ---
    def verdicts_by_row(replicates):
        d = defaultdict(list)
        for rep in replicates:
            for row in rep["rows"]:
                d[(row["model"], row["key"])].append((row["strict"], row["loose"]))
        return d

    unseeded_by_row = verdicts_by_row(unseeded_replicates)
    seeded_by_row = verdicts_by_row(seeded_replicates)

    n_rows = len(unseeded_by_row)
    n_unstable_unseeded = sum(1 for v in unseeded_by_row.values() if len(set(v)) > 1)
    n_unstable_seeded = sum(1 for v in seeded_by_row.values() if len(set(v)) > 1)

    print(f"\n[Item-level volatility]")
    print(f"  UNSEEDED: {n_unstable_unseeded}/{n_rows} rows "
          f"({100*n_unstable_unseeded/n_rows:.1f}%) show >1 distinct verdict across "
          f"{N_UNSEEDED_REPLICATES} replicates")
    print(f"  SEEDED (control): {n_unstable_seeded}/{n_rows} rows show >1 distinct "
          f"verdict across {N_SEEDED_REPLICATES} replicates (expect 0 -- causal check)")

    # --- 2 & 3. benchmark score + ranking impact ---
    roster_by_mk = {(r["model"], r["key"]): r for r in roster}
    baseline_overall = sum(1 for r in roster if r["strict"]) / len(roster)

    models = sorted(set(r["model"] for r in roster))
    baseline_per_model = {}
    for m in models:
        rows_m = [r for r in roster if r["model"] == m]
        baseline_per_model[m] = sum(1 for r in rows_m if r["strict"]) / len(rows_m)

    alt_overall_accs = []
    alt_per_model_accs = []
    for rep in unseeded_replicates:
        rep_lookup = {(row["model"], row["key"]): row for row in rep["rows"]}
        alt_strict_sum, alt_n = 0, 0
        per_model_sum = defaultdict(int)
        per_model_n = defaultdict(int)
        for r in roster:
            mk = (r["model"], r["key"])
            strict = rep_lookup[mk]["strict"] if mk in rep_lookup else r["strict"]
            alt_strict_sum += int(strict)
            alt_n += 1
            per_model_sum[r["model"]] += int(strict)
            per_model_n[r["model"]] += 1
        alt_overall_accs.append(alt_strict_sum / alt_n)
        alt_per_model_accs.append({m: per_model_sum[m] / per_model_n[m] for m in models})

    print(f"\n[Benchmark-score impact -- overall strict accuracy across "
          f"{N_UNSEEDED_REPLICATES} replicate universes]")
    print(f"  Baseline (roster, one realization): {baseline_overall:.4f}")
    print(f"  Replicate range: [{min(alt_overall_accs):.4f}, {max(alt_overall_accs):.4f}], "
          f"std={np.std(alt_overall_accs):.5f}")

    ranking_results = []
    for i, alt_pm in enumerate(alt_per_model_accs):
        tau, max_shift, top_changed = kendall_rank_stability(baseline_per_model, alt_pm)
        ranking_results.append({"replicate": i, "kendall_tau": tau,
                                 "max_rank_shift": max_shift, "top_model_changed": top_changed})

    print(f"\n[Model-ranking impact across {N_UNSEEDED_REPLICATES} replicate universes]")
    taus = [r["kendall_tau"] for r in ranking_results]
    shifts = [r["max_rank_shift"] for r in ranking_results]
    n_top_changed = sum(1 for r in ranking_results if r["top_model_changed"])
    print(f"  Kendall tau vs baseline ranking: min={min(taus):.4f}, max={max(taus):.4f}")
    print(f"  Max single-model rank displacement: {max(shifts)} (of {len(models)} models)")
    print(f"  Replicates where the #1-ranked model changed: {n_top_changed}/{N_UNSEEDED_REPLICATES}")

    # --- 4. corrected disagreement-explained fraction ---
    disagreements = [r for r in roster if r["strict"] != r["loose"]]
    n_disagree = len(disagreements)
    n_on_flagged = sum(1 for r in disagreements if r["key"] in flagged_keys)
    n_unexplained = n_disagree - n_on_flagged

    print(f"\n[Corrected disagreement decomposition]")
    print(f"  Total disagreements (strict != loose): {n_disagree}/{len(roster)} "
          f"({100*n_disagree/len(roster):.2f}%)")
    print(f"  On a corrected-flagged item-key (96/541, was 33/541): {n_on_flagged} "
          f"({100*n_on_flagged/n_disagree:.1f}%)")
    print(f"  Unexplained by either known mechanism: {n_unexplained} "
          f"({100*n_unexplained/n_disagree:.1f}%)")
    print(f"  [prior claim, incomplete scan: 31/{n_disagree} explained "
          f"({100*31/n_disagree:.1f}%), {100*(n_disagree-31)/n_disagree:.1f}% unexplained]")

    out = {
        "n_unseeded_replicates": N_UNSEEDED_REPLICATES,
        "n_seeded_replicates": N_SEEDED_REPLICATES,
        "seed_value": SEED,
        "environment": {
            "python_version": unseeded_replicates[0]["env"]["python_version"],
            "unseeded_condition": unseeded_replicates[0]["env"],
            "seeded_condition": seeded_replicates[0]["env"],
        },
        "n_flagged_items": len(flagged_keys),
        "n_flagged_rows_checked": n_rows,
        "item_level_volatility": {
            "n_unstable_unseeded": n_unstable_unseeded,
            "n_unstable_unseeded_pct": 100 * n_unstable_unseeded / n_rows,
            "n_unstable_seeded_control": n_unstable_seeded,
        },
        "benchmark_score_impact": {
            "baseline_overall_strict_acc": baseline_overall,
            "replicate_overall_strict_accs": alt_overall_accs,
            "min": min(alt_overall_accs), "max": max(alt_overall_accs),
            "std": float(np.std(alt_overall_accs)),
        },
        "model_ranking_impact": {
            "baseline_per_model_strict_acc": baseline_per_model,
            "per_replicate": ranking_results,
            "kendall_tau_min": min(taus), "kendall_tau_max": max(taus),
            "max_rank_shift_observed": max(shifts),
            "n_replicates_top_model_changed": n_top_changed,
        },
        "disagreement_decomposition_corrected": {
            "n_total_disagreements": n_disagree,
            "n_disagreements_total_rows_denominator": len(roster),
            "n_explained_corrected_96_items": n_on_flagged,
            "pct_explained_corrected": 100 * n_on_flagged / n_disagree,
            "n_unexplained_corrected": n_unexplained,
            "pct_unexplained_corrected": 100 * n_unexplained / n_disagree,
            "prior_incomplete_scan_n_explained_33_items": 31,
            "prior_incomplete_scan_pct_explained": 100 * 31 / n_disagree,
        },
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nWritten to {OUT_PATH}")
