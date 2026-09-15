# T-C expansion: preregistered design (~458 rows, approved this phase)

Written and committed **before** any new label is seen — this is the preregistration itself, not a post-hoc description. Scripts: `scripts/fb_tc_expansion_population.py` (population), `scripts/fb_tc_expansion_sample.py` (sampling + CSV). Sampling seed fixed at 42 (this project's standing convention) before drawing.

## Why ~458, precisely (not reused as a round number)

Three distinct sub-goals, each with its own target-n, computed via this project's own Wilson-CI machinery (not a generic formula):

1. **exact_match's own false-credit rate (α) — never measured before this phase.** Working prior for planning: 3.14% (score_boxed's pooled α, the closest available estimate — standard practice: plan around the best current estimate, revise after data returns). Target: Wilson-CI half-width ≤0.02 on the credited-stratum estimate. Computed directly (not approximated): **n≈300 achieves half-width 0.0201.**
2. **The scorer-disagreement resolution question — new this phase.** Of the cases where `exact_match` and `score_boxed` disagree, does one tend to be right more often, or is it close to a coin flip? Power calculation (one-sample proportion test, H0: p=0.5): **n=60 gives 89% power to detect a 70/30 split, 65% power for a more modest 65/35 split** — adequate for an exploratory-but-real answer, not overpowered for a secondary question.
3. **score_boxed's own α/β — the established target, continuity with the existing 69-row result.** Folded into the "both agree" cells below rather than budgeted separately (see design).

## The sampling design (4 cells, joint on both scorers)

| Cell | Definition | Target n | What it powers |
|---|---|---|---|
| `both_credited` | score_boxed=credited AND exact_match=credited | 200 | α for BOTH scorers simultaneously (the credited-stratum question that matters most for the reconciliation, since a_hat's correctness rests here) |
| `both_not_credited` | score_boxed≠credited AND exact_match≠credited | 198 | β for BOTH scorers simultaneously |
| `disagree_sb_credited_em_not` | score_boxed=credited, exact_match=not | 30 | Disagreement resolution (direction 1) |
| `disagree_em_credited_sb_not` | exact_match=credited, score_boxed=not | 30 | Disagreement resolution (direction 2) |
| **Total** | | **458** | |

**Why disagreement is split into two directional cells of 30 each, not one pooled cell of 60**: the two directions could have different true rates (e.g., `exact_match`'s unit-stripping false-credit found in the adversarial suite is a different failure mode than `score_boxed`'s missed-unboxed-answer false-miss) — collapsing them would average over two potentially different phenomena. Reported separately, optionally pooled at analysis time if they turn out similar.

## Population, exclusions, blinding

- Population: all (model, item) pairs for the **17 qualifying models** (the ones already in the reconciliation) across **all 7 MATH-Hard subjects**, freshly fetched (22,508 rows, `results/analysis/tc_expansion_population.json`).
- **Excluded**: any (model, item_id) already in the existing 400-item T-C population (`mathhard_labelling_key.json`) — 320 of those 400 belong to these 17 models and are excluded from the new sample, avoiding overlap where avoidable, per instruction. (The other 80 belong to non-qualifying models, not part of this population at all.)
- **Blinding**: identical to the existing, verified T-C protocol (`fb_tc_labeling_package.py`'s exact CSV format: `uid, problem, response, your_answer`) — no model name, no scorer stratum, no cell label, no gold answer in the distributed file. Row order shuffled (seed 43) so cell membership isn't inferable from position. Provenance (model/item/cell/gold) kept in a **separate, non-distributed** file (`results/analysis/tc_expansion2_provenance.json`), matched back to labels by `uid` only after they return, exactly as the existing protocol already does.
- **Labeling task unchanged**: the labeler transcribes the response's final answer (or writes NONE/CONTRADICTORY per the existing rules) — the SAME task as the original 69/70-row round. The comparison against gold, and against each of the two automated scorers, all happens at analysis time, after labels return. Nothing about the labeling task itself needed to change to resolve the scorer-mismatch question — only which items get shown.

## What this audit is intended to determine, exactly

1. **Does `exact_match`'s own α (never measured) resemble `score_boxed`'s (~3.1%), or differ meaningfully?** Directly tests whether the audit-estimation-uncertainty finding, built on `score_boxed`'s audited rate, would look different if built on the scorer that actually produces `a_hat`.
2. **When the two scorers disagree, which one tends to track human judgment?** Directly informs whether `a_hat` (exact_match-based) or the historically-audited number (score_boxed-based) is the more trustworthy accuracy signal going forward.
3. **Does more audit power (458 new + up to 320 excludable-overlap-avoided from the old 400) shrink the audit-estimation-uncertainty width, and does the "even a perfect scorer at n=11 shows 5.6x dominance" finding (`NEGATIVE_CONTROLS.md`) actually resolve at this larger n, as the theory predicts?** The direct test of whether the current central conclusion survives adequate power — not assumed to survive, per instruction.

## Efficient human-labeling protocol (added after two AI-generated submissions were excluded)

The task and blinding are unchanged (see above). Given 458 rows is a real time commitment and the failure mode just observed (an AI tool substituted for reading), the protocol going forward:

1. **Batch it.** Split the 458-row sheet into ~8 sessions of ~55-60 rows each (a sitting of well under an hour at a sustainable pace), not one continuous pass — the two excluded submissions arrived 6-7 minutes apart for 458 rows each, which is itself the tell; a real pace is closer to 5-15 seconds per row for the ~369 template-following rows and 1-3 minutes for the ~77-90 that need actual reading, i.e. several hours total, not several minutes.
2. **Submit in the same batches**, not all at once — makes a quality-gate check on each batch (`fb_tc_expansion2_analysis.py`'s gate) meaningful before the whole 458 rows are sunk into one submission.
3. **No AI tool in the loop for this specific task** — not a compliance rule for its own sake: the whole point of T-C is a judgment independent of automated extraction, so running the response text through any LLM/extraction tool first (even "just to help transcribe") reintroduces exactly the dependency the audit exists to check against. Reading the raw text and typing what it says is the entire task.
4. **The self-correction and NONE/CONTRADICTORY rules already in the README are the hard part** — those are also exactly what the 12-category adversarial suite targeted, so getting them right here is directly informative for the paper, not busywork.

## Analysis plan, fixed now, before any label is seen

Once labels return: (1) recompute α, β separately for `exact_match` and `score_boxed` from the `both_credited`/`both_not_credited` cells; (2) recompute the disagreement-resolution rate from the two disagreement cells; (3) recompute scorer-identification, audit-estimation, and combined uncertainty for BOTH scorer targets using the existing, unmodified `fb_reconcile_layers.py` machinery; (4) recompute pairwise identification and compare directly against the 69-row result; (5) report the A/B/C/D interpretation (scorer-error-dominant / audit-uncertainty-dominant / both / small-audit-artifact) strictly from what the numbers show — not decided in advance.
