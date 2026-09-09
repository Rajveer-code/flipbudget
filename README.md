# flipbudget

**Status: early theory + verification stage, not yet a paper.** This repo holds the
formal identification theory, verification scripts, and pre-registration for a
scorer-induced partial-identification framework for benchmark comparisons — a
standalone methodological extension, kept as its own repo and history rather than
folded into the project it builds on.

## The idea, in one paragraph

A benchmark score is produced by a model **and** a scoring function. When the
scorer misreads a response — credits a wrong answer, or fails to credit a right
one — the reported accuracy is not a noisy-but-unbiased read of the true accuracy;
it is *partially identified*: consistent with a range of true values that no
amount of extra sampling narrows. This repo derives that identified set, shows
that *non-differential* scorer error (the same error rate for every model)
preserves pairwise rankings exactly, defines the **flip budget** — how much
*differential* scorer error a published "model A beats model B" claim can absorb
before the ranking is no longer identified — and gives that budget its own
confidence treatment via a paired, item-level bootstrap.

## What's actually here

| File | What it is |
|---|---|
| `PLAN_FLIPBUDGET.md` | The full master plan: theory tasks, experiments, human-validation design, kill criteria, schedule |
| `PREREGISTRATION_FLIPBUDGET.md` | Committed before any new human labelling — held-out design, per-model reporting dimension, bootstrap procedure, execution-paradigm measurement plan |
| `scripts/fb_t1_symbolic.py` | T1 — identified set for a single model's accuracy; symbolic derivation + numeric corner-claim verification |
| `scripts/fb_t2_flipbudget.py` | T2 — the comparison theorem (Case A/B) and the flip-budget bisection |
| `scripts/fb_t3_coverage.py` | T3 — joint uncertainty (paired bootstrap, delta-method cross-check) with a full coverage simulation |
| `scripts/fb_t5_budget_ci.py` | T5 — bootstrap confidence treatment for the flip budget itself, run on real benchmark pairs |
| `scripts/fb_d4_data_sources.py` | Data-source audit — which benchmarks have usable item-level data |
| `results/analysis/*.json` | Snapshot of the underlying MMLU / MATH-Hard scoring and human-audit data these scripts consume |

## Provenance

The underlying benchmark data (`results/analysis/`) — model responses, extractor
outputs, and the human-audited misclassification margins — comes from a companion
project auditing answer-extraction failure in LLM benchmark harnesses, whose own
result is under review at TMLR. That project's own repository, methodology, and
paper are tracked separately; this repo is downstream of it, not a fork or a
duplicate. The snapshot here is frozen at the point this project started and is
tracked independently going forward.

## Running the verification scripts

Each script is self-contained and runnable from the repo root:

```bash
pip install numpy scipy sympy
python scripts/fb_t1_symbolic.py
python scripts/fb_t2_flipbudget.py
python scripts/fb_t3_coverage.py
python scripts/fb_d4_data_sources.py
python scripts/fb_t5_budget_ci.py
```

Every script prints its own verification output — pass/fail checks against
closed-form derivations, Monte-Carlo cross-checks, and coverage simulations. None
of the reported numbers are asserted without a script that reproduces them.

## Honest status

This is theory and verified simulation, not yet an empirical result on the full
benchmark set. T3's coverage simulation found and required fixing a real bug in
its own ground-truth computation before it could be trusted — see the commit
history for the full diagnostic trail, kept rather than squashed, because how a
bug was found matters as much as the fix. The next steps (E1's go/no-go pilot,
per-model differential misclassification with partial pooling, the full empirical
sweep) are specified in `PLAN_FLIPBUDGET.md` and not yet executed.

## License

Apache-2.0 (see `LICENSE`).
