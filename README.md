# flipbudget

**What can a small human audit establish about a leaderboard ranking?**
Verifier agreement, a breakdown analysis, and audit design (MATH-Hard, Open LLM Leaderboard v2).

**Status (2026-09-19): re-founded twice, on the evidence.** (1) A core
estimand error was found and corrected (`CORE_ESTIMAND_AUDIT.md`): a
verifier-stratified audit identifies q = P(wrong | credited) and
r = P(right | rejected), not error rates. (2) A final re-audit (`REAUDIT.md`)
found that the corrected single-verifier result (the audit certifies almost
no ranking) reflects audit size, and that the data support a stronger,
different thesis. All earlier headline numbers are withdrawn; their scripts
stay as an audit trail. No new human labels are needed for the paper's
claims.

## Findings

- The harness's two verifiers (`exact_match`, `score_boxed`) disagree on
  3.63% of 22,508 responses and reverse 7 orderings that each reports as
  statistically clear.
- A 400-item human audit used per model with one verifier certifies 0 of 136
  orderings once sampling error is included.
- Where both verifiers agree, the human reference disagrees with them on 1 of
  287 audited responses; the remaining error, including all model-specific
  error, is in the disagreements.
- Stratifying on the joint verifier outcome, the same audit certifies 84 of
  the 118 orderings sampling error permits, but only if verifier agreement is
  equally reliable across models. That assumption carries the result:
  allowing per-model concordant error up to 2x the pooled bound leaves 43, 5x
  leaves 7, no pooling leaves 0 (STRESS_TEST.md). Next: AISTATS 2027 plan in
  PLAN_AISTATS2027.md (local, gitignored).

## What's here

| Path | What it is |
|---|---|
| `manuscript/latex/` | Paper source; `numbers.tex` and `tab_*.tex` are generated, never hand-edited |
| `CORE_ESTIMAND_AUDIT.md` | Derivation, simulation, real-data re-analysis, theorem-by-theorem consequences of the estimand correction |
| `CLAIM_LEDGER.md` | Every number in the paper traced to its JSON key and script |
| `REAUDIT.md` | Final re-audit: construct validity, why the single-verifier result is weak, joint-verifier design, 458 decision, prior-art matrix, venue verdict |
| `PLAN_REBUILD.md` | Rebuild plan and progress |
| `src/flipbudget/pv.py` | The estimator for verifier-stratified audits (tested) |
| `scripts/fb_rebuild_analysis.py` | Single entry point for the paper's numbers |
| `TC_EXPANSION_PREREGISTRATION.md` | Audit designs; Amendment 1 (estimand error), Amendment 2 (disagreement-targeted redesign, sheet `labeling/audit_v2_l1.csv`) |
| `provenance/excluded_labeling_attempts/` | Excluded label submissions and the checks that excluded them |

## Reproduce

```bash
pip install -e ".[dev]"
pytest tests/
python scripts/fb_rebuild_analysis.py 1000   # results/flipbudget/rebuild_results.json
python scripts/fb_core_estimand_audit.py     # simulation + estimand audit
python scripts/fb_rebuild_figures.py
python scripts/fb_rebuild_numbers.py         # manuscript/latex/numbers.tex, tab_*.tex
```

`python scripts/fb_reproduce_all.py` runs the full pipeline, including the
historical scripts kept for the audit trail.

## Library

```python
from flipbudget import pv
lo, hi = pv.accuracy_interval(a, pv.wilson(x_q, n_q) + pv.wilson(x_r, n_r))
```

`flipbudget.corrected_interval` estimates error rates conditional on truth
and is valid only for a simple random audit; for audits drawn within the
verifier's strata use `flipbudget.pv`.

## Provenance

The 400-item human audit (`results/analysis/mathhard_labelling_key.json`) is
shared with a concurrent manuscript by the same author under review at TMLR;
the overlap is disclosed in the paper's Related Work.

## License

See `LICENSE`.
