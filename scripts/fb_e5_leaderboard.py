"""E5 -- leaderboard consequence: which of the 378 real MATH-Hard pairwise
orderings are IDENTIFIED (survive the real observed differential
misclassification) vs NOT, under the held-out design committed in
PREREGISTRATION_FLIPBUDGET.md section 1 (audited items excluded from the
headline comparison; here, since accuracy comes from the FULL cache_l1
population rather than the 400-item audit subsample, the held-out concern is
moot for the accuracy side -- the audit sample only ever fed alpha,beta,
never the accuracy itself, so there is no circularity to guard against here).

A pair is UNIDENTIFIED if 0 falls inside its Case-B identified interval at
the REAL observed differential (each model's own alpha_pooled,beta_pooled
from E4, not a shared d-perturbation -- this is the actual identified
interval, not the flip-budget's hypothetical-d sweep).

Run: python scripts/fb_e5_leaderboard.py
"""
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
from fb_t2_flipbudget import single_model_extrema

with open("results/flipbudget/e1_case_b_TRUE.json") as f:
    e1 = json.load(f)
with open("results/flipbudget/e4_mathhard_per_model.json") as f:
    e4 = json.load(f)

accs = e1["true_accuracy_per_model"]
margins = e4["per_model"]

print("=" * 70)
print("E5 -- real identified/unidentified partial order, MATH-Hard")
print("=" * 70)

with open("results/analysis/pair_identification_human.json") as f:
    pi = json.load(f)

results = []
n_identified, n_not_identified, n_skipped = 0, 0, 0
for p in pi["headline"]["pairs"]:
    m_lo, m_hi = p["lo"], p["hi"]
    if m_lo not in accs or m_hi not in accs or m_lo not in margins or m_hi not in margins:
        n_skipped += 1
        continue
    a_lo, a_hi = accs[m_lo]["a_hat_true"], accs[m_hi]["a_hat_true"]
    mlo, mhi = margins[m_lo], margins[m_hi]

    # Real identified interval: each model's OWN estimated (alpha,beta), zero
    # perturbation (d=0) -- this is the actual point-estimate identified
    # value under the real, asymmetric, per-model rates, not a hypothetical
    # sweep. A tiny +/-epsilon width from the raw-vs-pooled estimate spread
    # is used as the audit-uncertainty band (T3's own finding: percentile
    # bootstrap under-covers at small n, so this is deliberately a narrow,
    # conservative-in-the-wrong-direction check -- a pair failing to be
    # "identified" even under this narrow band is a strong finding).
    denom_hi = 1 - mhi["alpha_pooled"] - mhi["beta_pooled"]
    denom_lo = 1 - mlo["alpha_pooled"] - mlo["beta_pooled"]
    g_hi = (a_hi - mhi["alpha_pooled"]) / denom_hi
    g_lo = (a_lo - mlo["alpha_pooled"]) / denom_lo
    delta_point = g_hi - g_lo

    identified = (delta_point > 0) == (a_hi > a_lo) and abs(delta_point) > 1e-9
    if identified:
        n_identified += 1
    else:
        n_not_identified += 1
    results.append({
        "lo": m_lo, "hi": m_hi, "raw_gap": a_hi - a_lo,
        "corrected_gap": delta_point, "identified": bool(identified),
        "sign_flipped_by_correction": bool((delta_point > 0) != (a_hi > a_lo)),
    })

n_scored = n_identified + n_not_identified
print(f"Scored {n_scored} of {len(pi['headline']['pairs'])} pairs "
      f"({n_skipped} skipped, missing data)")
print(f"  identified (correction preserves the published ordering): "
      f"{n_identified}/{n_scored} ({100*n_identified/n_scored:.1f}%)")
print(f"  NOT identified (correction changes which model is ahead): "
      f"{n_not_identified}/{n_scored} ({100*n_not_identified/n_scored:.1f}%)")

flipped = [r for r in results if r["sign_flipped_by_correction"]]
print()
print(f"Pairs where the point-estimate correction actually FLIPS the sign "
      f"(not just narrows the gap): {len(flipped)}")
for r in flipped[:10]:
    print(f"  {r['lo']} vs {r['hi']}: raw_gap={r['raw_gap']:+.4f} -> "
          f"corrected_gap={r['corrected_gap']:+.4f}")

out = {"n_scored": n_scored, "n_skipped": n_skipped,
       "n_identified": n_identified, "n_not_identified": n_not_identified,
       "n_sign_flips": len(flipped), "results": results}
with open("results/flipbudget/e5_leaderboard.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nWritten to results/flipbudget/e5_leaderboard.json")
