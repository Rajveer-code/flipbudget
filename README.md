> [!NOTE]
> **Moved.** This was the working repository for the paper. The current code, data and manuscript
> (submitted to DMLR) live in [`leaderboard-orderings`](https://github.com/Rajveer-code/leaderboard-orderings).
> This repository is archived and is not updated.

# flipbudget

**Which leaderboard orderings survive a human reader?**

A leaderboard reports one accuracy per model and names only half of what produced it. The
other half is a verifier — the code that reads a free-text response and decides whether it
answered the question. On the Open LLM Leaderboard v2's MATH-Hard results, the choice of
verifier moves the ranking, and a published score gives a reader no way to detect it.

This repository bounds which pairwise orderings survive when no verifier is taken as truth,
using a small human audit and a stated assumption about how models differ where the verifiers
agree. Every ordering carries a breakdown value: the amount of cross-model heterogeneity it
would take to overturn it.

**Status (2026-09-25):** TMLR resubmission draft complete except for one results subsection
that is waiting on human labels. See `PLAN_TMLR_RESUBMIT.md` for the gates and
`TASKS_REMAINING.csv` for what is open.

## What the data say

- 27 models, 1,324 Level-5 MATH items, 35,748 published responses, read by three verifiers.
  No model dropped, no response regenerated.
- The three verifiers disagree on 1,159 responses. That small fraction is the part that
  decides the ranking.
- Verifier provenance is established from the leaderboard's own records rather than inferred:
  re-executing the scoring function recorded in the result files reproduces the published
  verdict on 35,748 of 35,748 responses.
- The leaderboard re-scored its MATH results with a different verifier in February 2025 and
  left the per-item verdict files untouched, so it currently displays scores from one verifier
  and publishes item-level verdicts from another.
- Of 351 pairwise orderings, the audit certifies 153 at exact homogeneity and 131 at the
  tolerance registered before any result was seen. Without the pooling assumption it certifies
  0. The useful output is the curve between them.

## The argument

Accuracy under a human reference is a sum over verifier-agreement cells of a known share times
an unknown correctness rate. A few hundred labels cannot identify those rates, so the paper
bounds them instead, and reports what the bounds do to the ranking rather than to the score.

The one assumption that does real work is stated as a single parameter: within a cell where
the verifiers agree, models' correctness rates lie in an interval of width at most ε. Results
are reported as a function of ε, with ε = 0 treated as the end of a curve rather than an
estimate, because a simulation at full board scale shows exact homogeneity is unattainable —
finite sub-populations differ by chance alone.

## What's here

| Path | What it is |
|---|---|
| `manuscript/tmlr/` | The paper. `macros.tex`, `tables.tex` and `sensitivity_table.tex` are generated, never hand-edited |
| `src/flipbudget/certify.py` | The certification machinery: KL intervals, identified ranges, breakdown values, rank intervals |
| `src/flipbudget/verifiers.py` | The three verifiers and the human-reference routine |
| `THEORY_CERTIFICATION.md` | The derivations the paper's appendix transcribes |
| `CLAIM_LEDGER_AISTATS.md` | Every macro in the paper traced to the result file and key it came from |
| `PLAN_TMLR_RESUBMIT.md` | Gates, and an open defect found while proving the coverage result |
| `TASKS_REMAINING.csv`, `MASTER_PROMPT.md` | What is finished, what is not, and what not to redo |
| `TC_EXPANSION_PREREGISTRATION.md` | The registered audit design, with Amendments 4 and 5 |
| `VALIDATION_RELABEL.md` | Preregistered criteria for the label-provenance check |
| `labeling/` | The sheets, the instrumented labelling app, and `LABELING_MASTER_PROMPT.md` |
| `provenance/excluded_labeling_attempts/` | Label submissions that failed the quality gate, and the checks that excluded them |

## Two findings about this repository's own code

A verifier here was silently degraded for the whole of its earlier life: its symbolic
equivalence check guarded itself with a timer available only on Unix, the guard raised on
Windows, a broad handler swallowed it, and the function returned "not equivalent" for every
call. Every verdict it had produced was a string comparison. The paper reports this, because
it is the paper's own argument turned on its author — a verifier that fails silently produces
a plausible number and nothing in the output says otherwise.

Separately, a preregistered falsification rule turned out to be self-defeating: a model's own
labels inflated the pooled bound it was tested against, so a model with a 40% error rate would
not have been rejected. Amendment 5 replaced it with a leave-one-out pool, written before any
label for it existed.

## Reproduce

```bash
pip install -e ".[dev]"
```

```bash
pytest -q
```

Full regeneration, in order:

```bash
python scripts/fb_certify.py && python scripts/fb_figures_aistats.py && python scripts/fb_test_census.py && python scripts/fb_macros_aistats.py && python scripts/fb_tables_tmlr.py && python scripts/fb_check_manuscript.py
```

Build the paper:

```bash
cd manuscript/tmlr && latexmk -g -pdf -interaction=nonstopmode main.tex
```

## How numbers get into the paper

No number is typed into prose. Each one enters as a LaTeX macro generated by
`scripts/fb_macros_aistats.py` from a committed result file, and
`scripts/fb_check_manuscript.py` fails the build if a number is typed directly or a macro is
undefined. A `.tex` file is exempt from that check only if its first line declares it
generated. `CLAIM_LEDGER_AISTATS.md` lists every macro with its value and its source.

The test suite holds 880 checks. They compare the implementation against independent
computation, compare the formulas as printed in the manuscript against the implementation, and
hold a regression anchor that reproduces previously published counts from the current data
pipeline.

## Human labels

No automated tool generates, pre-fills, completes or cleans any label. Labelling happens in an
offline app that blocks pasting, times every item, and hashes its export; each batch passes an
automated quality gate before it is used, and batches that fail are excluded and kept in the
record. `labeling/LABELING_MASTER_PROMPT.md` is the instruction sheet.

## Author

Rajveer Singh Pall — rajveerpall04@gmail.com
