"""E1 -- the GO/NO-GO pilot, run on real data.

Case A (pooled, non-differential) on all 378 real MATH-Hard pairs from
pair_identification_human.json, using the real pooled alpha=0.0314, beta=0.0
from E4/mathhard_human_margins.json. This needs only the real `gap` field --
not per-model absolute accuracy, which is not yet located/verified for
MATH-Hard (flagged honestly, not guessed at).

Case A's own theorem (T2) says this analysis CANNOT change any ranking --
sign is preserved by construction. Its purpose here is different: it
reports the ATTENUATION factor 1/(1-alpha-beta), i.e. how much the
published gaps understate the true gaps under the pooled misclassification
rate, and flags which pairs have a gap small enough that this attenuation
could plausibly matter for a differential (Case B) analysis once absolute
accuracies are available.

The genuine differential (Case B) flip-budget pilot -- the one that COULD
change conclusions, and the one E1 is really asking about -- needs the
per-model absolute accuracies not yet in hand. Reported honestly as the
concrete next step, not run on an assumed baseline.

Run: python scripts/fb_e1_pilot.py
"""
import json

with open("results/analysis/pair_identification_human.json") as f:
    pi = json.load(f)
with open("results/analysis/mathhard_human_margins.json") as f:
    mm = json.load(f)

pooled_alpha = mm["strata"]["credited"]["primary"]["rate_within_stratum"]
pooled_beta = mm["strata"]["wrong_parsed"]["primary"]["rate_within_stratum"]
attenuation = 1 - pooled_alpha - pooled_beta

pairs = pi["headline"]["pairs"]
n_pairs = len(pairs)

print("=" * 70)
print("E1 -- Case A (pooled, non-differential) on all real MATH-Hard pairs")
print("=" * 70)
print(f"n_pairs = {n_pairs} (real, from pair_identification_human.json)")
print(f"pooled alpha (false-credit) = {pooled_alpha:.4f}")
print(f"pooled beta (false-miss)    = {pooled_beta:.4f}")
print(f"attenuation factor 1/(1-alpha-beta) = {1/attenuation:.4f}")
print(f"  (every published gap understates the corrected Case-A gap by this factor")
print(f"  -- Case A CANNOT change sign by T2's own theorem; this is a magnitude")
print(f"  correction only, not a ranking-changing result)")
print()

gaps = [p["gap"] for p in pairs]
zero_gap = sum(1 for g in gaps if g == 0)
small_gap = sum(1 for g in gaps if 0 < g < 0.03)
print(f"gap == 0 exactly: {zero_gap} of {n_pairs} ({100*zero_gap/n_pairs:.1f}%) "
      f"-- these pairs are ALREADY tied under the scorer's own accuracy, before")
print(f"  any misclassification correction is applied at all")
print(f"0 < gap < 0.03 (smaller than the pooled alpha itself): {small_gap} of {n_pairs} "
      f"({100*small_gap/n_pairs:.1f}%)")
print()

print("=" * 70)
print("GO/NO-GO (Case A component): the pooled attenuation factor is "
      f"{1/attenuation:.3f}x -- a real, non-negligible correction to reported")
print("gap magnitude, but by T2's own theorem it cannot overturn a single")
print("published ranking on its own (non-differential error preserves sign).")
print()
print("The differential (Case B) component -- the one that CAN overturn")
print("rankings, and the one this gate is really asking about -- is NOT YET")
print("RUN on MATH-Hard: it needs per-model absolute accuracy, which is not")
print("located/verified in this data snapshot. E4 already found real")
print("differential signal in alpha (CohereForAI/c4ai-command-r-v01 at raw")
print("0.667 vs pooled 0.031) -- that is the concrete lead a real Case-B")
print("pilot should chase next, once the accuracy file is found or computed.")
print("=" * 70)

out = {
    "n_pairs": n_pairs,
    "pooled_alpha": pooled_alpha,
    "pooled_beta": pooled_beta,
    "attenuation_factor": 1 / attenuation,
    "n_pairs_gap_zero": zero_gap,
    "n_pairs_gap_below_pooled_alpha": small_gap,
    "case_b_status": "NOT RUN -- needs per-model absolute MATH-Hard accuracy, "
                     "not located in this data snapshot. E4's raw per-model alpha "
                     "already shows real differential signal (one outlier model) "
                     "that a Case-B pass should investigate once unblocked.",
}
import os
os.makedirs("results/flipbudget", exist_ok=True)
with open("results/flipbudget/e1_pilot_case_a.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nWritten to results/flipbudget/e1_pilot_case_a.json")
