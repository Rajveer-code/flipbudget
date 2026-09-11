# T-C roster pull — real item-level worklists, one finding corrected

Per your instruction: pulled the per-model item roster from knowledgeshift's raw
`results/cache_l1` to unblock T-C's exact worklist. Scripts:
`scripts/fb_pull_roster.py`, `scripts/fb_tc_ee_real_worklist.py`. Output:
`results/analysis/mathhard_full_roster.json` (35,613 rows, metadata only — model,
item_id, subject, stratum; no response text, matching the existing snapshot
convention), `results/flipbudget/tc_ee_real_worklist.json`.

## How this was done, and why it can be trusted

Not reimplemented: imported knowledgeshift's own `19_l1_rescore_leaderboard.py`
directly (`score_boxed`, `latest_math_files`, `rows_of`, the real comparator) — the
exact same logic `scripts/62_mathhard_frame.py` uses to build the original sampling
frame. Read-only: nothing written to knowledgeshift; this repo's provenance-snapshot
convention (already used for every file in `results/analysis/`) is unchanged.

**Validation, not assumed:** re-derived stratum for all 400 currently-audited
(model, item_id) records and compared against the audit key's own recorded stratum.
**0 of 400 mismatches.** Full confidence to trust the same derivation on the
35,213 not-yet-audited rows.

**Item-sharing, measured not assumed:** MATH-Hard's 1,324 items are the *same* fixed
set for every model — 89.8% scored by all 27 roster models, worst case 26/27. This
overturns last pass's premise that finding overlapping items was the hard part —
it isn't; nearly everything is shared. The real constraint is which (model, item)
cells to prioritize for labelling, not finding candidates.

## T-C: solved, not just designed

**90 real (item_id, model_A, model_B) candidate pairs** found among the top-12
priority pools, all not-yet-audited on both named models. Top 40 candidates span
30 distinct items — labelling those 30 items on their two named models each gives
**40 real new paired observations**, comfortably past the ≥20 planning-level target
from the previous pass. Full ranked list (top 100) in
`results/flipbudget/tc_ee_real_worklist.json`. This is genuinely actionable: pick an
item from the list, its subject, and its two named models, find that (item, model)
response pair, label it.

## E-E: a real finding that corrects the previous projection, reported honestly

Previous pass projected 2,700 items / 5 rounds would reach 90.2 expected events
(the Peduzzi EPV≥10 target for 9 features), explicitly caveated as unverified pool
availability. **Now measured directly, and it does not hold:**

- Several top pools are far thinner than assumed: `CohereForAI/c4ai-command-r-v01`
  (the single highest-rate pool) has only **27** not-yet-audited credited items
  available, not the 100 (5 rounds × 20) the projection assumed.
  `EleutherAI/pythia-160m`/credited has **zero** available.
- **Real ceiling: using every one of the 18,482 available not-yet-audited items
  across all 54 pools — not a sample, the entire remaining roster — the expected
  total is 52.7 events, not 90.** The clean EPV≥10 target for a 9-feature model is
  **structurally unreachable on this benchmark's current 27-model roster**, no
  matter how much of it gets audited.

This is a genuine, sobering result, not a script bug — cross-checked: `wrong_parsed`
pools hold the bulk of available items (weak models get many items marked wrong)
but their β is close to 0 almost everywhere (E4's own earlier finding), so huge
item counts there buy very few events. `credited` pools have real yield but are
small in absolute population for most models on a benchmark this hard.

**What this means, stated plainly:**
1. A **reduced-feature E-E model** (top ~5 of the 9 features, by the existing fit's
   coefficient magnitude) needs only 50 events (EPV≥10×5) — the 52.7 ceiling clears
   this, barely. A defensible fallback if full labelling is pursued.
2. **MATH-Hard alone may not be able to support a clean, fully-powered E-E**, full
   stop — this is a property of the benchmark (extraction failures are genuinely
   rare here), not of the audit design. E-B's multi-benchmark scale-out (other
   benchmarks, likely with higher scorer-error rates than MATH-Hard's boxed-answer
   extraction) is the more promising path to a properly-powered E-E, not more
   MATH-Hard auditing.
3. The cheaper interim option from last pass still stands as the practical choice
   if you want to improve E-E on MATH-Hard specifically without chasing an
   unreachable target: round 1 alone (540 items, real availability confirmed
   sufficient) raises the event count from 5 to ~22 — informative, reported with
   an explicit small-n caveat, same honest framing Tier 1 already used.

## What this does not do

Zero new human labels. Does not pick a path forward (reduced-feature E-E vs.
E-B scale-out vs. accept the interim round) — that is your call, not mine to make
silently.
