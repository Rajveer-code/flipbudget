"""IFEval audit design -- stratified sample, mirroring the exact 3-stratum logic
already used for MATH-Hard's frame (62_mathhard_frame.py: credited/wrong_parsed/
unparsed), adapted to IFEval's real strata:

  both_pass   (strict=True, loose=True)  -- scorer confidently credits
  disagree    (strict=False, loose=True) -- the ambiguous case, 380/14607 (2.6%),
                                             the entire reason for this audit
  both_fail   (strict=False, loose=False) -- scorer confidently rejects

(strict=True,loose=False is logically impossible: loose's 8 variants include
the untouched response itself, so strict passing implies loose passes too --
verified directly on the real data below, not assumed.)

Design: FULL CENSUS of "disagree" (it's the stratum this whole audit exists to
characterize, and at 380 items auditing all of it removes sampling error on
the one number that matters most) plus a smaller stratified comparison sample
of both_pass/both_fail (sanity-checking that the "unambiguous" strata really
are, an idea directly informed by TA_BOUNDARY_AUDIT.md's lesson: don't assume
a stratum is uninformative just because its label suggests so).

Run: python scripts/fb_ifeval_audit_design.py
"""
import json
import random
from collections import defaultdict

SEED = 42
N_COMPARISON_PER_STRATUM = 40  # both_pass and both_fail each get this many, sanity-check only


def load_roster():
    with open("results/analysis/ifeval_full_roster.json", encoding="utf-8") as f:
        return json.load(f)["population"]


def load_flagged_keys():
    """Items using a checker with a known non-determinism mechanism (found and
    root-caused this session, not assumed): keywords:letter_frequency falls
    back to random.choice(ascii_letters) whenever its 'letter' kwarg isn't a
    single a-z character (e.g. '!' or '#'), and language:response_language
    uses langdetect, whose algorithm is unseeded and not guaranteed
    deterministic. 33 of 541 items (6.1%) are affected; they explain 8.2% of
    observed disagreements -- real, but not most of the signal. Flagged in
    the sample so the labeler/analysis can treat them as a distinct category,
    not silently pooled with genuine strict-vs-loose ambiguity."""
    with open("results/flipbudget/ifeval_nondeterminism_flagged_items.json", encoding="utf-8") as f:
        return set(int(k) for k in json.load(f)["flagged_keys"].keys())


def stratum_of(row):
    if row["strict"]:
        return "both_pass"
    return "disagree" if row["loose"] else "both_fail"


def verify_impossible_combo(pop, flagged_keys):
    """strict=True,loose=False should be logically impossible (loose's 8 variants
    include the untouched response, so anything strict credits, loose should too)
    -- UNLESS the verifier itself is non-deterministic, which it is for 33 known
    items (see load_flagged_keys). Root-caused, not assumed: reproduced directly
    by calling keywords:letter_frequency's check_following twice on identical
    input and getting different answers, traced to build_description falling
    back to random.choice(ascii_letters) whenever 'letter' isn't a single a-z
    char. Real anomalies found: 6, all 6 on a flagged key -- confirmed here,
    not just assumed, before downgrading this from a hard stop to a known,
    accounted-for exception."""
    bad = [r for r in pop if r["strict"] and not r["loose"]]
    bad_unexplained = [r for r in bad if r["key"] not in flagged_keys]
    print(f"strict=True,loose=False rows (should be impossible): {len(bad)}")
    print(f"  of which on a KNOWN non-deterministic key: {len(bad) - len(bad_unexplained)}")
    print(f"  UNEXPLAINED (not on a flagged key): {len(bad_unexplained)}")
    return len(bad_unexplained) == 0


def stratified_sample(pop, stratum, n, rng):
    candidates = [r for r in pop if stratum_of(r) == stratum]
    if n >= len(candidates):
        return candidates
    # stratify the comparison sample across models proportionally, not pure
    # random, so no single model dominates the sanity-check subset
    by_model = defaultdict(list)
    for r in candidates:
        by_model[r["model"]].append(r)
    models = sorted(by_model.keys())
    per_model_target = max(1, n // len(models))
    picked = []
    for m in models:
        picked.extend(rng.sample(by_model[m], min(per_model_target, len(by_model[m]))))
    # top up / trim to exactly n
    rng.shuffle(picked)
    if len(picked) > n:
        picked = picked[:n]
    elif len(picked) < n:
        remaining = [r for r in candidates if r not in picked]
        rng.shuffle(remaining)
        picked.extend(remaining[: n - len(picked)])
    return picked


if __name__ == "__main__":
    print("=" * 70)
    print("IFEval audit design -- stratified sample")
    print("=" * 70)
    pop = load_roster()
    flagged_keys = load_flagged_keys()
    print(f"Population: {len(pop)} rows")
    print(f"Non-determinism-flagged item keys: {len(flagged_keys)} of 541 items")
    ok = verify_impossible_combo(pop, flagged_keys)
    print(f"[{'OK' if ok else 'FAIL'}] every strict=>loose violation is explained by a "
          f"known-flagged non-deterministic item: {ok}")
    if not ok:
        raise SystemExit("Found an UNEXPLAINED strict/loose violation -- stop, "
                          "investigate before sampling (do not assume it's the same bug).")

    by_stratum = defaultdict(list)
    for r in pop:
        by_stratum[stratum_of(r)].append(r)
    for s in ("both_pass", "disagree", "both_fail"):
        print(f"  {s}: {len(by_stratum[s])} ({100*len(by_stratum[s])/len(pop):.1f}%)")

    rng = random.Random(SEED)
    sample = list(by_stratum["disagree"])  # full census
    sample += stratified_sample(pop, "both_pass", N_COMPARISON_PER_STRATUM, rng)
    sample += stratified_sample(pop, "both_fail", N_COMPARISON_PER_STRATUM, rng)

    print(f"\nFinal audit sample: {len(sample)} items")
    print(f"  disagree (full census): {len(by_stratum['disagree'])}")
    print(f"  both_pass (comparison): {sum(1 for r in sample if stratum_of(r)=='both_pass')}")
    print(f"  both_fail (comparison): {sum(1 for r in sample if stratum_of(r)=='both_fail')}")

    models_covered = sorted(set(r["model"] for r in sample))
    print(f"  models represented: {len(models_covered)} of {len(set(r['model'] for r in pop))}")

    n_sample_flagged = sum(1 for r in sample if r["key"] in flagged_keys)
    print(f"  sampled items on a non-determinism-flagged key: {n_sample_flagged} of {len(sample)}")

    out = [{"model": r["model"], "key": r["key"], "stratum": stratum_of(r),
            "strict": r["strict"], "loose": r["loose"],
            "nondeterminism_flagged": r["key"] in flagged_keys} for r in sample]
    with open("results/flipbudget/ifeval_audit_sample.json", "w", encoding="utf-8") as f:
        json.dump({"seed": SEED, "n_comparison_per_stratum": N_COMPARISON_PER_STRATUM,
                    "n_total": len(out), "sample": out}, f, indent=2)
    print("\nWritten to results/flipbudget/ifeval_audit_sample.json")
