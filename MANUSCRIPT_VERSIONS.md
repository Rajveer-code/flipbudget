# Two manuscript states

## A. CURRENT_EVIDENCE_VERSION

**This is `manuscript/latex/main.pdf` as committed right now** (15 pages,
9-page main content, compiled 2026-09-17, zero Overfull/Undefined
warnings, hostile-reviewed with 5 fixes applied and reverified). It is
scientifically complete using only evidence already in hand: every
established result (analyses A and B, the audit-design finding, the
scorer-mismatch finding and its worst-case bound) is stated in full, with
real numbers, traced to a script and a result file
(`CLAIM_LEDGER.md`/Appendix A.9). Every place a result depends on the
pending 458-row audit is marked `\pending{...}` (renders as red text,
e.g. the abstract's final sentence, Table 4's row C, Section 7.4's closing
sentence, Limitations item 1) — six locations total, enumerated exactly in
`results/flipbudget/results_to_insert.json`'s structure. Nothing in this
version is invented; every `[PENDING]` is a named, specific, missing
quantity, not a placeholder standing in for an unstated one.

This is the version to submit if the submission-timing decision
(`VENUE_AND_OVERLAP_AUDIT.md`) concludes the paper should go out before the
458 labels arrive.

## B. FINAL_POST_AUDIT_VERSION

**Not a separately-drafted document — a deterministic procedure applied to
version A**, so that no number in it is invented ahead of the real
labels existing. The procedure, already built and independently tested
this pass (`scripts/fb_final_evidence_update.py`, `THEORY_AUDIT.md`'s
verification of the underlying estimator, `tests/test_tc_expansion2_estimator.py`):

1. `python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled`
   — runs the quality gate (refuses to proceed on a failed gate, exactly as
   it did on the three prior submissions), recomputes `exact_match`'s own
   $\alpha,\beta$ and the analysis-C dominance ratio, regenerates all 7
   figures and all 8 standalone tables, reruns the test suite, and writes
   `results/flipbudget/results_to_insert.json` — the exact replacement
   text for each of the six `\pending{...}` locations, keyed by a short id,
   built from the real computed numbers, never a template with blanks.
2. Open `results_to_insert.json` and, for each of the six entries, find its
   `manuscript_line_anchor` in the six `.tex` files
   (`00_abstract.tex`, `06_empirical_setup.tex`, `07_results.tex` [two
   locations], `08_limitations.tex`) and apply the change per its
   `instruction` field — a human edit, deliberately not automated (an
   automatic text-replace into prose risks a silent, unreviewed wording
   change, a worse failure mode than one extra manual copy-paste per
   location).
3. Recompile (`pdflatex` + `bibtex` + `pdflatex` x2), re-verify zero
   Overfull/Undefined warnings and the page budget still holds (Table 4's
   row C will likely need slightly more horizontal room once filled with
   real numbers instead of the word "pending" — check first, per
   `PAGE_BUDGET.md`'s own margin, currently 0.5 pages of headroom against
   the 9-page limit).
4. Rebuild the submission package
   (`python scripts/fb_build_submission_package.py`) and re-run the
   standalone-compile check this pass performed on `SUBMISSION_FINAL/`.

No number for version B is fabricated here or anywhere else in this
project in anticipation of the real labels. The procedure above is the
entire content of "version B" until it is actually run against real data.
