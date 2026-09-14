# Adversarial suite v2 + a major finding it surfaced: two different real scorers

Scripts: `scripts/fb_adversarial_suite_v2.py` (both parts below).
Output: `results/flipbudget/adversarial_suite_v2.json`.

## The finding, stated precisely

MATH-Hard's real evaluation harness (`vendor/leaderboard_math/utils.py`, unmodified, identical to the companion project's copy — byte-diffed to confirm) computes **two different scores per item**, from **two different answer-extraction methods**:

| Field | Extraction method | What this project has used it for |
|---|---|---|
| `exact_match` | `math_verify` library's `parse`/`verify` (LaTeX-aware, robust to several answer formats) | **This is the field `fb_e1_true_accuracy.py` reads for `a_hat`** — every accuracy number in this entire project |
| (T-C's own target, via `score_boxed`) | `last_boxed_only_string` — finds the LAST `\boxed{...}` in the response, nothing else | **This is what T-C's human audit has stratified on and measured α/β for**, inherited exactly from the companion project (`fb_pull_roster.py`, byte-identical logic) |

**These two methods disagree on 6.51% of real responses, aggregated across all 17 qualifying models (n=5,219, algebra_hard subject)** — more than double the ~3.1% pooled α this project has treated as "the" scorer error rate throughout. Disagreement is **bidirectional** (161 cases where `exact_match` credits but `score_boxed` doesn't; 179 the other way) and **varies enormously by model** (near-zero for models that rarely produce any parseable answer at all, up to 16–19% for capable instruction-tuned models like Qwen2-72B-Instruct and Yi-1.5-9B-Chat — see per-model table in the JSON).

**What this means, precisely:** `a_hat` (the accuracy this project corrects via `g(a,alpha,beta)`) is produced by `exact_match`. T-C's audited `alpha`/`beta` describe `score_boxed`'s disagreement with human judgment — a different comparator. Applying `score_boxed`'s audited error rates to correct `exact_match`-derived accuracy is not automatically valid; the correction formula assumes `alpha`/`beta` describe errors in the same measurement process that produced `a`.

**A previously-known limitation (`get_unnormalized_answer`, the regex-based "Final Answer: X. I hope it is correct." extractor used by `process_result_v1`/`exact_match_original`) is a THIRD, separate extraction method, not equivalent to either of the above — confirmed by reading its source directly, and it is not the field this project's `a_hat` or T-C's stratification actually use. An earlier draft of this script conflated it with `score_boxed`; caught and fixed before being reported (see script history).**

## Part A: the 12-category constructed taxonomy (pre-declared, not tuned for drama)

24 cases, 2 per category, known ground truth, run through both real scorers (`exact_match` via `math_verify` with its multiprocessing timeout disabled — a second, distinct Windows-fragility in a safety-timeout mechanism, analogous to `is_equiv`'s `SIGALRM` issue, `MATH_COMPARATOR_BUG.md` — and `score_boxed`, T-C's real target):

| Category | Result |
|---|---|
| formatting, latex, whitespace, verbosity, numerical_formatting | **NULL** — both scorers correctly handle these equivalences |
| delimiters (`\[7\]` vs `7`) | **score_boxed-specific false miss** |
| answer_position (unboxed "Final Answer: X" prose) | **score_boxed-specific false miss** — the exact mechanism behind the real-data finding above |
| case (`\text{even}` vs `\text{EVEN}`) | **score_boxed-specific false miss** |
| units (`9 meters` vs `9 seconds`, should NOT match) | **exact_match-specific false credit** — `math_verify` strips units and wrongly credits a unit mismatch |
| multiple_answers (two boxed values, self-correction) | **GENERAL false miss on both scorers** — different failure modes (`score_boxed` takes the literal last box; `math_verify`'s extraction can also pick the wrong one) |
| self_correction | **exact_match-specific false miss** in one direction, general in another — genuinely mixed, not cherry-picked |
| other_scorer_specific (interval/set reordering) | **GENERAL false miss on both** — replicates the already-known limitation, a useful consistency check |

No category was dropped for being boring; five of twelve are null results, reported as such.

## Part B: real-data grounding (the table behind the headline number)

Per-model agreement/disagreement table for all 17 qualifying models is in `results/flipbudget/adversarial_suite_v2.json`'s `part_b_real_data_grounding`. Range: 81.4% (Yi-1.5-9B-Chat) to 99.3% (gpt-j-6b) agreement between the two real scorers.

## What this changes, and what it does not

- **Does not invalidate** the audit-estimation-uncertainty finding itself, the empty-set fix, the audit-design work, or the Neyman-degeneracy finding — those concern the *width* of estimates and allocation efficiency, structurally independent of which specific scorer is being audited.
- **Does directly bear on which scorer T-C's expanded audit should target.** Continuing to audit `score_boxed` specifically would produce a more precise estimate of the wrong thing (a comparator that isn't what produced `a_hat`). This needs a decision before the ~458-row labeling sheet is generated — see the question below.
