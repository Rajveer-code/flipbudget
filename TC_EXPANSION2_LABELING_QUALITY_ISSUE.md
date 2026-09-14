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

## Why this specific thing matters here, not as a compliance point

The entire purpose of the T-C audit is to measure how often a human's independent reading of a response diverges from what an automated scorer already concluded. If the labels come from another automated process, the resulting "α/β" describe agreement between two machines, not the scorer-vs-human-judgment gap this project's whole framework is built to bound. Using this would not just be a data-quality problem — it would silently answer a different scientific question while looking like it answered the preregistered one.

## Status

Both submissions excluded, preserved as provenance only. `labeling/tc_expansion2_l1.csv` (the original, unlabeled sheet) and `TC_EXPANSION_PREREGISTRATION.md` (the design) still stand — genuine human labeling of this sheet is still needed before the recompute in the preregistration's analysis plan can run.
