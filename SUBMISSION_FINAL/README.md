# Submission package -- Scorer-Induced Partial Identification of Benchmark Comparisons

Built from commit `8a6af08959538bc7110219c5ae72d601201ab071` of the code repository
(https://github.com/Rajveer-code/flipbudget.git).

## Contents

- `paper.pdf` -- the compiled manuscript (17 pages).
- `latex_source/` -- complete LaTeX source, self-contained (figures copied
  locally, `\graphicspath` rewritten). Rebuild with:
  ```
  cd latex_source
  pdflatex -interaction=nonstopmode main.tex
  bibtex main
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
  ```
  Requires only a standard LaTeX2e install (tested with MiKTeX; TeX Live
  works identically) -- no repo-specific paths, no non-standard packages
  beyond what `main.tex`'s preamble lists explicitly.
- `manuscript_markdown/` -- the human-readable prose source the LaTeX was
  translated from, kept for cross-checking.
- `tables/`, `figures/` -- every standalone table (8) and figure (7) as
  committed, each independently regenerable from the code repository's own
  `scripts/fb_build_tables.py` and `scripts/fb_fig*.py`.
- `evidence/` -- the paper's own audit trail: a claim ledger tracing every
  quantitative claim to its script and raw data, the novelty classification,
  the methodological audit that found and fixed two real estimator bugs
  before any human label was processed, the final status log, and the most
  recent full reproducibility run's log (38/38 steps, isolated, timed).
- `LICENSE` (Apache-2.0), `CITATION.cff`.

## Reproducing the results from scratch

This package intentionally does not bundle the full code repository (that
would duplicate the git history for no benefit). To regenerate every number,
figure, and table in this paper that does not depend on the pending human
audit:

1. Clone the code repository at the commit named above.
2. `pip install -e .` (repository root; pinned dependencies in
   `pyproject.toml`).
3. `python scripts/fb_reproduce_all.py` -- one command, 38 steps, ~15
   minutes (dominated by one live network step against the Hugging Face
   API using your own token; everything else is pure computation from data
   already committed in the repository).
4. `pytest tests/` -- 24 tests, all passing as of this package's build.

## Data access

All benchmark data (MATH-Hard model generations, per-item scoring) is
already committed inside the code repository under `results/` and
`results/analysis/`, sourced from the public Open LLM Leaderboard v2. No
external data download is required to reproduce the results above.

## The one genuine external dependency

458 rows of real, independently human-labeled data
(`labeling/tc_expansion2_l1.csv` in the code repository) are the only piece
of this paper's empirical core still outstanding -- preregistered, in
progress, not invented, not substituted. Every place this affects a number
in the paper is marked in red (`[PENDING -- human audit: ...]`) rather than
filled with a placeholder that looks like a result. Once those labels exist:
```
python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
```
produces `results_to_insert.json` (exact replacement numbers, keyed by
manuscript location) and a printed checklist of exactly which lines in the
manuscript need a manual edit -- deliberately not automated, so a wording
change is always human-reviewed before it enters the paper.

## Dataset-restrictions checklist

- [x] MATH-Hard / Open LLM Leaderboard v2 data: public, no restriction.
- [x] IFEval data (used for the secondary generalization check): public,
      no restriction.
- [ ] The pending 458-row human audit: to be collected by the paper's sole
      author under the preregistered protocol in the code repository's
      `TC_EXPANSION_PREREGISTRATION.md`; not yet collected, no restriction
      anticipated once it is (same blinded-annotator protocol as the
      already-completed rounds).
- [x] No personally identifiable information, credentials, or private data
      appears anywhere in this package -- verified by grep across every
      file included here before packaging.
