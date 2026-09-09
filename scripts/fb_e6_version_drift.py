"""E6 -- legitimate-variation robustness: does alpha,beta drift across
defensible harness versions, and does the drift land in exactly the
dimension this program studies?

Uses git-history evidence already committed in census_version_drift.json
(specific PRs, specific commits, real diffs against the vendored harness
clone, each independently verifiable via the recorded verify_command) rather
than re-deriving anything. E6's job here is to connect that evidence to the
program's own (alpha, beta) vocabulary and state what it implies for the
flip budget, not to recompute the underlying git facts.

Run: python scripts/fb_e6_version_drift.py
"""
import json

with open("results/analysis/census_version_drift.json") as f:
    d = json.load(f)

print("=" * 70)
print("E6 -- version drift, real git-history evidence")
print("=" * 70)
print(f"Pinned commit: {d['design']['pinned_commit']}")
print(f"Tags compared: {d['design']['tags_compared']}")
print(f"Null-result check: {d['null_result_check']['result']}")
print()

for i, finding in enumerate(d["findings"], 1):
    print(f"--- Finding {i}: {finding['id']} ---")
    print(f"  file: {finding['file']}")
    print(f"  affects: {finding['affects']}")
    print(f"  version window: {finding['version_window']}")
    print(f"  verify yourself: {finding.get('verify_command', '(see PR list)')}")
    print()

print("=" * 70)
print("Interpretation in this program's own (alpha, beta) vocabulary")
print("=" * 70)
print("""
Finding 1 (extraction.py, v0.4.4 -> pinned): an uncaught IndexError on a
degenerate empty-capture-group match became a caught, silent fallback to
the sentinel. Before: a malformed response CRASHED the harness (visible,
loud, forces a human to look). After: the SAME response is silently scored
wrong. This is a direct, verifiable beta-side event -- the harness's own
maintainers changed WHICH responses get silently mis-scored, in a released
version bump, for reasons unrelated to model quality.

Finding 2 (leaderboard/math/utils.py, v0.4.5 -> pinned) is the more
striking one FOR THIS SPECIFIC PROJECT: it is the exact comparator vendored
into this repo's own vendor/leaderboard_math/utils.py (E2, E4's real
per-model margins). Two independently verifiable changes:
  - the equivalence-check timeout tightened 5s -> 1s, meaning MORE
    boundary-case comparisons get marked "not equivalent" (a real,
    version-induced beta increase) purely because verification took too
    long, independent of whether the answer was actually right;
  - the backend itself changed from plain sympy to a NEW dependency,
    math_verify. E2 already found (independently, before this file was
    read) that the CURRENT (pinned) version does not recognize \\dfrac as
    equivalent to \\frac. Whether the OLDER, plain-sympy backend handled
    that case differently is a real, concretely answerable question this
    evidence sets up but does not itself answer -- flagged as a specific,
    bounded next check, not run here to control cost.

What this means for the flip budget: T2's Case B is not a hypothetical
abstraction. "Differential misclassification" includes differences ACROSS
TIME on the identical benchmark, not just across models at one instant --
two labs scoring the "same" benchmark six months apart, on different
harness commits, are running a real Case-B perturbation on themselves,
whether they know it or not. This is exactly the legitimate-variation
robustness check E6 was scoped to establish, and the evidence for it was
already sitting in this project's own git-history audit before this
session started.
""")

out = {
    "n_findings": len(d["findings"]),
    "null_result": False,
    "connects_to_e2": (
        "Finding 2's comparator IS the one vendored for E2/E4 in this repo; "
        "E2 independently found a real dfrac-vs-frac false-miss in the "
        "PINNED (current) version. Whether the pre-drift version handled it "
        "differently is a flagged, unresolved, concretely bounded follow-up."
    ),
}
with open("results/flipbudget/e6_version_drift_summary.json", "w") as f:
    json.dump(out, f, indent=2)
print("Written to results/flipbudget/e6_version_drift_summary.json")
