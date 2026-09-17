# T-C expansion round 2: labeling quality issue — excluded, not used

Two submissions of the preregistered 458-row sheet (`labeling/tc_expansion2_l1.csv`) were received. Both show a pattern inconsistent with independent human reading. Preserved as provenance only in `provenance/excluded_labeling_attempts/` (`tc_expansion2_round1_submission.csv`, `tc_expansion2_round2_submission.csv`), per this project's standing rule — neither feeds any result.

## Submission 1

Returned ~6 minutes after the sheet was sent, accompanied by a chat message narrating a process ("Now let's validate the 368 auto-extracted rows...", "That looks legitimate...", "All extractions look accurate. Now finalize the CSV...") — phrasing that describes a tool's own workflow, not a person's account of reading 458 math responses.

Cross-referencing `your_answer` against gold, by the preregistered cell:

| Cell | n | Matches gold |
|---|---|---|
| `both_credited` | 200 | 200/200 — 100.0% |
| `disagree_em_credited_sb_not` | 30 | 30/30 — 100.0% |
| `disagree_sb_credited_em_not` | 30 | 29/30 — 96.7% |
| `both_not_credited` | 198 | 1/198 — 0.5% |
| CONTRADICTORY used | 458 | 0 |

This tracks the two existing automated scorers almost exactly, including reproducing the earlier near-zero-β result (1/198 here vs. 0/69 and 0/51 in the two prior audit rounds) on a completely fresh sample. Zero contradictions across 458 responses from a roster that includes models known from this project's own data to produce a lot of incoherent, repetitive text is a hard pattern to get from careful manual reading.

## Submission 2

Returned ~7 minutes after submission 1, accompanied by the message "is this fine done by me." 318 of 458 rows changed from submission 1. Diffing the two:

- **The overwhelming majority (~310) are a single, uniform, mechanical edit**: stripping the surrounding `$...$` LaTeX delimiter from the answer (e.g. `'$46$'` → `'46'`, `'$\frac{35\sqrt{42}}{189}$'` → `'\frac{35\sqrt{42}}{189}'`), applied identically across hundreds of unrelated rows. Not plausible as 458 independent manual re-reads completed in 7 minutes; consistent with one bulk find-and-replace or a "clean up formatting" instruction to a tool.
- **At least two rows got measurably worse**, not better: `f48e1a40a0` gained trailing junk (`'\frac{1}{5}'` → `'$\frac{1}{5}$. I'`); `187777fe83` had an entire irrelevant sentence fragment appended (`'4848'` → `'4848 natural numbers less than 1000 have exactly three distinct positive integer divisors'`). A third (`6940126476`) silently lost an escaped backslash inside a matrix (`\\0` → `\0`) — a corruption, not a correction. These are signatures of automated reprocessing errors, not careful proofreading.
- **One row's classification reversed inconsistently with the README's own rule**: `2cf973fd1c` went from `NONE` to the literal transcribed phrase `'There is no solution to this problem'` — the opposite of what the accompanying submission-1 narration itself said it had decided for this exact case ("[the response] explicitly concluded 'there is no solution to this problem'... treated as not committing to an answer → NONE").

## Submission 3 (2026-09-17)

Submitted as `C:\Users\Asus\Downloads\tc_expansion2_l1_labeled.csv`, alongside a detailed, example-rich labeling instruction document (`labeling/HUMAN_LABELING_INSTRUCTIONS_tc_expansion2.md`) written and delivered earlier in the same session — i.e., this submission arrived with the most explicit guidance of any of the three attempts, including an explicit worked-out example of the exact turnaround-time red flag this project checks for ("several hours, not several minutes... the two rejected attempts each claimed to finish all 458 in under ten minutes").

**Timestamp, not inference this time — filesystem fact.** File `mtime`/`ctime`: 2026-09-17 16:21:40. Checked against the current time at review (16:23:11), roughly 90 seconds later. The entire 458-row file did not exist, in any form, more than about two minutes before it was submitted — faster than either of the two prior rejected submissions, and squarely inside the exact window the delivered instructions had just named as the tell to avoid.

**Statistical signature, reproduced a third time, structurally identical to submission 1's pattern:**

```
both_credited:                  match_rate = 100.0%  (200/200)
disagree_em_credited_sb_not:    match_rate = 100.0%  (30/30)
disagree_sb_credited_em_not:    match_rate = 96.7%   (29/30)
both_not_credited:              match_rate = 0.7%    (1/149 scored; 49 marked NONE)
n_contradictory = 0 (of 458)
```

The pattern is not "close to the automated scorers" in general — it is "matches whichever scorer already credited that specific cell, almost exactly." `both_credited` and `disagree_em_credited_sb_not` (`exact_match` credits) both hit 100%; `disagree_sb_credited_em_not` (`score_boxed` credits) hits 96.7%; the one cell where both scorers agree the answer is wrong lands at 0.7% — reproducing, on a third independent attempt, the specific near-zero result the first exclusion already flagged as implausible on fresh data. Zero `CONTRADICTORY` uses across 458 rows, again.

**Content check consistent with automated extraction, not a slower tell but a consistent one:** sampled answer values are well-formed, correctly-escaped LaTeX (`'$18+2\pi$'`, `'$\frac{...}{...}$'`-style strings), the kind of output a parser produces reliably, not the kind of output a two-minute skim produces reliably across 458 distinct problems.

Excluded, preserved as provenance only: `provenance/excluded_labeling_attempts/tc_expansion2_round3_submission.csv`.

## Why this specific thing matters here, not as a compliance point

The entire purpose of the T-C audit is to measure how often a human's independent reading of a response diverges from what an automated scorer already concluded. If the labels come from another automated process, the resulting "α/β" describe agreement between two machines, not the scorer-vs-human-judgment gap this project's whole framework is built to bound. Using this would not just be a data-quality problem — it would silently answer a different scientific question while looking like it answered the preregistered one.

## Status

Three submissions excluded, all preserved as provenance only, none used in any result. `labeling/tc_expansion2_l1.csv` (the original, unlabeled sheet), `labeling/HUMAN_LABELING_INSTRUCTIONS_tc_expansion2.md` (the instructions), and `TC_EXPANSION_PREREGISTRATION.md` (the design) still stand — genuine human labeling of this sheet is still needed before the recompute in the preregistration's analysis plan can run. The quality gate has now correctly caught three attempts in a row; it is doing its job.
