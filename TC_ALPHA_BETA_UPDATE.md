# T-C's contribution to the joint scorer-verdict-vs-human-verdict analysis

Script: `scripts/fb_tc_alpha_beta_update.py`. Result:
`results/flipbudget/tc_alpha_beta_update.json`. Reuses every existing
function exactly (`fb_e4_mathhard.partial_pool`, `ea_dominance_study.
build_model_table`/`wilson_ci`, `fb_reconcile_layers.
bounded_single_model_extrema`/`bounded_comparison`, `fb_ta_ssm.lambda_bounds`,
`fb_ta_compound_interval.compound_bounds`) — nothing here is a new formula.

This is T-C's half of the requested comparison (scorer verdict → human
verdict → known-bug cases → unexplained cases, quantified against α, β,
benchmark score, rankings, identification/uncertainty). **IFEval's half is
blocked pending its own human labels** — `labeling/ifeval_audit_l1.csv` is
untouched, as instructed, and nothing below reflects it.

## Scorer verdict vs. human verdict, T-C

69 usable audited trials (1 of 70 indeterminate, excluded), 10 models
touched, **0 disagreements between the automated scorer's credited/wrong
verdict and the human transcription** (`TC_REAL_ANALYSIS.md`'s finding,
carried forward here). There is no "known verifier-bug" category for
MATH-Hard's scorer analogous to IFEval's langdetect/letter-frequency
mechanisms — no such mechanism has been identified or catalogued for this
scorer in this project. With 0 disagreements to begin with, both the
known-bug and unexplained buckets are empty for this batch: **69/69 scorer
verdicts confirmed by direct human read.** A clean result, not a strong one —
0 events remains statistically consistent with the ~3–7% error rate this
audit was targeted at (P(0 | rate≈3%, n=69) ≈ 11%), not evidence the
targeting or the rate itself was wrong.

All 69 trials landed in the **credited** stratum by design (T-C/E-E's
audit-expansion targeted false-credit risk specifically) — the **wrong**
stratum received zero new trials from this round, confirmed directly: the
global β anchor is unchanged to the shown precision (0.0000 → 0.0000).

## Effect on α, β

Folding 69 new trials (0 new false-credit events) into the existing 162-item
pooled credited-stratum audit:

| | Before | After |
|---|---|---|
| Global pooled α anchor | 0.0314 | **0.0216** |
| Global pooled β anchor | 0.0000 | 0.0000 (unchanged — no new β trials) |
| Total credited-stratum n audited | 162 | 231 |
| Total wrong-stratum n audited | 188 | 188 (unchanged) |

A 31% relative drop in the shared α anchor, from real zero-error evidence,
not from a parameter change.

**Qualifying models (both strata have ≥1 audited trial) went from 17/27 to
25/27** — 8 models that previously had zero credited-stratum audit coverage
now qualify for the identification apparatus for the first time, because
T-C's new trials happened to be their first:

| Model | New n (credited / wrong) |
|---|---|
| 01-ai/Yi-34B-Chat | 4 / 9 |
| Deci/DeciLM-7B | 6 / 5 |
| EleutherAI/gpt-neox-20b | 1 / 4 |
| HuggingFaceH4/zephyr-7b-alpha | 3 / 7 |
| HuggingFaceH4/zephyr-7b-beta | 3 / 12 |
| ibm/merlinite-7b | 7 / 7 |
| microsoft/phi-1_5 | 2 / 6 |
| mistralai/Mistral-7B-Instruct-v0.3 | 10 / 7 |

(Wrong-stratum n above is the *pre-existing* count from the original Tier-1
audit — T-C didn't add to it. These models qualify now only because T-C gave
them their first credited-stratum trial.)

**An important, verified, non-obvious propagation effect**: models never
touched by T-C's new audit still shift, because empirical-Bayes pooling
shares one anchor across all models. A low-audit-n model (e.g.
`tiiuae/falcon-40b`, n_used_credited=1) gets ~99% of its α estimate from the
anchor — when the anchor moves, so does every thinly-audited model's
α_pooled, regardless of whether that specific model was re-audited. Verified
directly, not assumed: `01-ai/Yi-34B` and `tiiuae/falcon-40b` (neither in
T-C's touched set) both show their α_pooled shift by the same proportion as
the anchor itself.

## Effect on identification bounds and pairwise resolution (136 real pairs)

Benchmark score itself (raw accuracy â) is **unaffected** — this audit
revises the scorer-error estimate, not the model responses or the automated
scores. What moves is the *corrected* accuracy A* = g(â, α, β) and its
identified range.

| Layer | Median width, before → after | Unresolved (contains 0), before → after |
|---|---|---|
| Audit-estimation-only (Wilson CI, Λ=1) | 0.2636 → 0.2321 | 91/136 → 89/136 |
| Scorer-identification-only (Λ=2, shrunk anchor) | 0.0390 → 0.0330 | 15/136 → **22/136** |
| Combined | 0.4227 → 0.4020 | 110/136 → 105/136 |

Audit and combined layers move the expected direction (more real data →
narrower bands, net 2 and 5 more pairs resolved respectively). The
**scorer-only layer's unresolved count rose (15→22: 3 newly resolved, 10
newly unresolved)** — checked directly rather than assumed to be an error:
this layer's width depends only on the point estimate of α_pooled/β_pooled
(Λ-bands shrink toward 0 as the point estimate itself shrinks toward 0), not
on audit n. All 10 newly-unresolved pairs checked involve models whose
α_pooled *point estimate* moved (via the anchor-propagation effect above),
shifting their corrected-accuracy center closer to a competitor's —
previously-clear comparisons becoming ambiguous because the *correction
itself moved*, not because uncertainty grew. A real, reportable finding: a
small, targeted human audit can destabilize conclusions about models it
never directly touched, purely through a shared statistical prior.

31 of the 136 real pairs involve at least one T-C-audited model.

## What this does not do

Does not resolve T-C's central correlation question (still underpowered, 0
events — unchanged from `TC_REAL_ANALYSIS.md`). Does not include IFEval —
blocked pending its own labels. Does not yet give the consolidated verdict
requested (A/B/C/D-style, or the strongest defensible contribution) — that
requires IFEval's matching analysis, not run here.
