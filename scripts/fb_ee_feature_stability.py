"""E-E feature-selection design check -- run BEFORE committing to any reduced-feature
labeling. Direct response to the objection: the 5-feature set in
fb_ee_reduced_feature_worklist.py was picked by |coefficient| from a fit on 5 events --
selecting features FROM the outcome you're trying to detect, on a sample too small to
estimate 9 coefficients reliably. That is the textbook overfitting-by-selection failure
mode, and 6,742 labels is too large an investment to spend confirming it.

Five checks, in the order requested:
  1. Reconstruct exactly how the 5 features were chosen (mechanical, not new).
  2. Leave-one-positive-out AND full leave-one-out stability of the top-5 set/signs.
  3. Bootstrap stability selection (Meinshausen & Buhlmann 2010 framing): selection
     frequency and sign-consistency per feature across resamples.
  4. Compare: full 9-feature spec vs data-driven top-5 vs a PRE-SPECIFIED alternative
     chosen from the scorer's known extraction mechanism (has_boxed, n_frac,
     n_dollar_signs -- tied to the ACTUAL boxed-extraction/LaTeX-normalization
     algorithm and Phase 1's own E2 finding of a real dfrac false-miss bug, not to
     any fit against wrongness labels).
  5. Verdict: is the reduced spec stable enough to justify 6,742 labels, or does E-E
     move to a later stage. Decided by the numbers below, not pre-judged either way --
     "never choose a specification because it produces a stronger result" cuts against
     assuming instability in advance just as much as against assuming stability.

Run: python scripts/fb_ee_feature_stability.py
"""
import json
import sys
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, "scripts")
import ee_format_association as ee  # reuses its exact loading/matching/feature code

TOP_K = 5
N_BOOTSTRAP = 2000
# Pre-specified alternative, chosen from the scorer's extraction mechanism, NOT from
# any fit against wrongness -- has_boxed anchors the extraction regex itself; n_frac
# is the exact feature implicated in Phase 1's E2 dfrac false-miss finding; n_dollar_signs
# is a general LaTeX-markup-density proxy the normalizer has to parse through.
MECHANISM_FEATURES = ["has_boxed", "n_frac", "n_dollar_signs"]

warnings.filterwarnings("ignore", category=ConvergenceWarning)


def load_records():
    with open("results/analysis/mathhard_labelling_key.json") as f:
        key = json.load(f)
    import csv
    with open("results/analysis/mathhard_l1.csv", newline="", encoding="utf-8") as f:
        rows_by_uid = {r["uid"]: r for r in csv.DictReader(f)}
    records = []
    for item in key:
        row = rows_by_uid.get(item["uid"])
        if row is None:
            continue
        ans = row["your_answer"]
        if ee.is_indeterminate(ans):
            continue
        human_correct = ee.matches_gold(ans, item["gold"])
        scorer_correct = (item["stratum"] == "credited")
        wrong = int(scorer_correct != human_correct)
        feats = ee.extract_features(row["response"])
        records.append({"wrong": wrong, **feats})
    return records


FEATURE_NAMES = ["char_length", "word_count", "has_boxed", "n_dollar_signs",
                  "n_newlines", "n_equals", "has_therefore", "n_frac", "ends_with_period"]


def build_xy(records):
    X = np.array([[r[f] for f in FEATURE_NAMES] for r in records], dtype=float)
    y = np.array([r["wrong"] for r in records])
    return X, y


def standardize(X):
    mean, std = X.mean(axis=0), X.std(axis=0)
    std[std == 0] = 1.0
    return (X - mean) / std


def fit_rank(X, y):
    Xs = standardize(X)
    clf = LogisticRegression(max_iter=1000, class_weight="balanced")
    clf.fit(Xs, y)
    coefs = clf.coef_[0]
    return sorted(zip(FEATURE_NAMES, coefs), key=lambda x: -abs(x[1]))


def epv_target(n_features):
    return 10 * n_features


if __name__ == "__main__":
    print("=" * 70)
    print("E-E FEATURE-SELECTION DESIGN CHECK -- run before any new labeling")
    print("=" * 70)

    records = load_records()
    X, y = build_xy(records)
    n, n_wrong = len(y), int(y.sum())
    print(f"Records: {n}, wrongness events: {n_wrong}")

    # ---- 1. Reconstruct the original selection exactly ----
    print()
    print("-" * 70)
    print("1. RECONSTRUCTION: how the 5 features were originally selected")
    print("-" * 70)
    original_ranked = fit_rank(X, y)
    original_top5 = [f for f, _ in original_ranked[:TOP_K]]
    print("Full-sample fit (n=350, 5 events, class_weight=balanced), ranked by |coef|:")
    for f, c in original_ranked:
        flag = " <-- in reduced set" if f in original_top5 else ""
        print(f"  {f:<18} {c:+.4f}{flag}")
    print(f"\nSelected as reduced set: {original_top5}")
    print("This ranking comes directly from fitting against the wrongness outcome on")
    print("only 5 positive events -- selection is NOT independent of the outcome it")
    print("will be used to detect. That is the concern being tested below, not assumed.")

    # ---- 2a. Leave-one-positive-out ----
    print()
    print("-" * 70)
    print("2a. LEAVE-ONE-POSITIVE-OUT (drop each of the 5 wrongness events, one at a time)")
    print("-" * 70)
    pos_idx = np.where(y == 1)[0]
    loo_pos_top5_sets = []
    for drop in pos_idx:
        mask = np.ones(n, dtype=bool)
        mask[drop] = False
        ranked = fit_rank(X[mask], y[mask])
        top5 = [f for f, _ in ranked[:TOP_K]]
        loo_pos_top5_sets.append(set(top5))
        match = "SAME SET" if set(top5) == set(original_top5) else "DIFFERENT"
        print(f"  drop event #{drop}: top5={top5}  [{match}]")
    n_loo_pos_match = sum(1 for s in loo_pos_top5_sets if s == set(original_top5))
    print(f"\n{n_loo_pos_match} of {len(pos_idx)} leave-one-positive-out refits reproduce "
          f"the exact same top-5 set.")

    # ---- 2b. Full leave-one-out (all 350), summarized ----
    print()
    print("-" * 70)
    print("2b. FULL LEAVE-ONE-OUT (all 350 records, summarized)")
    print("-" * 70)
    loo_top5_match = 0
    loo_sign_flip_any = 0
    original_signs = {f: np.sign(c) for f, c in original_ranked}
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        ranked = fit_rank(X[mask], y[mask])
        top5 = set(f for f, _ in ranked[:TOP_K])
        if top5 == set(original_top5):
            loo_top5_match += 1
        signs = {f: np.sign(c) for f, c in ranked}
        if any(signs[f] != original_signs[f] for f in FEATURE_NAMES):
            loo_sign_flip_any += 1
    print(f"Top-5 set reproduced exactly: {loo_top5_match} of {n} single-record removals "
          f"({100*loo_top5_match/n:.1f}%)")
    print(f"At least one feature's sign flips: {loo_sign_flip_any} of {n} removals "
          f"({100*loo_sign_flip_any/n:.1f}%)")
    print("(Removing one of 345 NEGATIVE records should barely matter -- most of this")
    print("350-count is uninformative by construction. The positive-only check above is")
    print("the real stress test; this one is the complementary sanity bound.)")

    # ---- 3. Bootstrap stability selection ----
    print()
    print("-" * 70)
    print(f"3. BOOTSTRAP STABILITY SELECTION ({N_BOOTSTRAP} resamples)")
    print("-" * 70)
    rng = np.random.default_rng(0)
    selection_count = {f: 0 for f in FEATURE_NAMES}
    sign_matches_original = {f: 0 for f in FEATURE_NAMES}
    sign_observations = {f: 0 for f in FEATURE_NAMES}
    top5_exact_match = 0
    n_degenerate = 0
    n_usable = 0
    for b in range(N_BOOTSTRAP):
        idx = rng.integers(0, n, n)
        yb = y[idx]
        if len(set(yb)) < 2:
            n_degenerate += 1
            continue
        Xb = X[idx]
        ranked = fit_rank(Xb, yb)
        n_usable += 1
        top5 = set(f for f, _ in ranked[:TOP_K])
        if top5 == set(original_top5):
            top5_exact_match += 1
        for f in top5:
            selection_count[f] += 1
        for f, c in ranked:
            sign_observations[f] += 1
            if np.sign(c) == original_signs[f]:
                sign_matches_original[f] += 1

    print(f"Usable resamples: {n_usable} of {N_BOOTSTRAP} "
          f"({100*n_usable/N_BOOTSTRAP:.1f}%); degenerate (only one class present, "
          f"could not fit): {n_degenerate} ({100*n_degenerate/N_BOOTSTRAP:.1f}%)")
    print(f"\nExact top-5 set reproduced: {top5_exact_match} of {n_usable} usable "
          f"resamples ({100*top5_exact_match/n_usable:.1f}%)" if n_usable else "n/a")
    print(f"\nPer-feature selection frequency (fraction of usable bootstraps where the")
    print(f"feature lands in the top-5) and sign consistency vs. the original fit:")
    for f in FEATURE_NAMES:
        sel_freq = selection_count[f] / n_usable if n_usable else float("nan")
        sign_freq = (sign_matches_original[f] / sign_observations[f]
                     if sign_observations[f] else float("nan"))
        marker = " <-- original top-5" if f in original_top5 else ""
        print(f"  {f:<18} selected in top5: {sel_freq:.3f}   sign matches original: "
              f"{sign_freq:.3f}{marker}")

    # ---- 4. Comparison: 9-feature vs data-driven 5 vs pre-specified mechanism set ----
    print()
    print("-" * 70)
    print("4. COMPARISON: full spec vs data-driven reduced spec vs pre-specified spec")
    print("-" * 70)
    print(f"Full 9-feature spec: EPV>=10 needs {epv_target(9)} events (ceiling 52.7 -- "
          f"UNREACHABLE, established last pass)")
    print(f"Data-driven top-5 ({original_top5}): EPV>=10 needs {epv_target(TOP_K)} "
          f"events (reachable, 6,742-item worklist already built)")
    print(f"Pre-specified mechanism set {MECHANISM_FEATURES}: EPV>=10 needs "
          f"{epv_target(len(MECHANISM_FEATURES))} events")
    mech_sel_freq = {f: selection_count.get(f, 0) / n_usable if n_usable else float("nan")
                     for f in MECHANISM_FEATURES}
    print(f"\nMechanism-set features' bootstrap top-5 selection frequency (how often the")
    print(f"DATA-DRIVEN procedure would have picked them anyway, for comparison):")
    for f in MECHANISM_FEATURES:
        print(f"  {f:<18} {mech_sel_freq[f]:.3f}")

    # ---- 5. Verdict ----
    print()
    print("=" * 70)
    print("5. VERDICT")
    print("=" * 70)
    stability_threshold = 0.5  # a feature "reliably" selected should beat a coin flip
    reliably_selected = [f for f in original_top5
                         if (selection_count[f] / n_usable if n_usable else 0) >= stability_threshold]
    print(f"Of the original top-5 {original_top5},")
    print(f"{len(reliably_selected)} are selected in >={stability_threshold:.0%} of "
          f"bootstrap resamples: {reliably_selected}")
    print(f"Leave-one-positive-out: {n_loo_pos_match} of {len(pos_idx)} single-event "
          f"removals reproduce the exact same top-5 set.")

    data_driven_stable = (len(reliably_selected) >= 3) and (n_loo_pos_match >= 3)
    if data_driven_stable:
        verdict = "DATA_DRIVEN_SET_DEFENSIBLE"
        print("\nVERDICT: the data-driven 5-feature set clears a reasonable stability bar.")
        print("Proceeding with it for a large labeling investment is defensible.")
    else:
        verdict = "DATA_DRIVEN_SET_NOT_STABLE"
        print("\nVERDICT: the data-driven 5-feature set does NOT clear a reasonable")
        print("stability bar -- selecting features by |coefficient| from a 5-event fit")
        print("is not a reliable procedure at this sample size, confirmed empirically,")
        print("not merely asserted. DO NOT commit 6,742 labels to this specification.")
        print(f"\nRECOMMENDATION: use the pre-specified mechanism set {MECHANISM_FEATURES}")
        print(f"instead -- chosen from the scorer's known extraction algorithm and Phase")
        print(f"1's own E2 dfrac finding, not from fitting against wrongness. It needs")
        print(f"only {epv_target(len(MECHANISM_FEATURES))} events (vs {epv_target(TOP_K)}")
        print(f"for the unstable data-driven set), a smaller and more defensible ask.")

    out = {
        "n_records": n, "n_wrong": n_wrong,
        "original_top5_ranked": [{"feature": f, "coef": float(c)} for f, c in original_ranked],
        "loo_positive_out": {
            "n_matches": int(n_loo_pos_match), "n_total": len(pos_idx),
            "per_drop_top5": [sorted(s) for s in loo_pos_top5_sets],
        },
        "full_loo": {
            "top5_match_count": int(loo_top5_match), "n_total": n,
            "sign_flip_count": int(loo_sign_flip_any),
        },
        "bootstrap": {
            "n_bootstrap": N_BOOTSTRAP, "n_usable": n_usable, "n_degenerate": n_degenerate,
            "top5_exact_match_count": top5_exact_match,
            "per_feature_selection_frequency": {f: selection_count[f] / n_usable if n_usable else None
                                                  for f in FEATURE_NAMES},
            "per_feature_sign_consistency": {f: (sign_matches_original[f] / sign_observations[f]
                                                   if sign_observations[f] else None)
                                               for f in FEATURE_NAMES},
        },
        "mechanism_alternative": {
            "features": MECHANISM_FEATURES,
            "epv10_events_needed": epv_target(len(MECHANISM_FEATURES)),
            "bootstrap_selection_frequency": mech_sel_freq,
        },
        "reliably_selected_at_threshold": reliably_selected,
        "stability_threshold": stability_threshold,
        "verdict": verdict,
    }
    with open("results/flipbudget/ee_feature_stability.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWritten to results/flipbudget/ee_feature_stability.json")
