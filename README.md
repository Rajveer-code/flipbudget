# flipbudget

**Status: manuscript content-complete and typeset, one external dependency
remaining.** A full 15-page LaTeX manuscript ("Scorer-Induced Partial
Identification of Benchmark Comparisons: An Audit-Design Approach") is
drafted, compiled, hostile-reviewed, and compressed to a 9-page main-content
budget against NeurIPS Evaluations & Datasets formatting rules —
`manuscript/latex/main.pdf`. Every established result is real, on real
data, traced to a script (`CLAIM_LEDGER.md`). The one piece still open is
a preregistered 458-row human audit, in progress, explicitly marked
`[PENDING]` everywhere it affects a number — never invented, never
substituted.

## The idea, in one paragraph

A benchmark score is produced by a model **and** a scoring function. When the
scorer misreads a response — credits a wrong answer, or fails to credit a right
one — the reported accuracy is not a noisy-but-unbiased read of the true accuracy;
it is *partially identified*: consistent with a range of true values that no
amount of extra sampling narrows. This repo derives that identified set on real
MATH-Hard data, shows that **audit-estimation uncertainty (how little the
scorer's own error rate is pinned down) exceeds sampling uncertainty for
most identifiable comparisons** (median ratio 6.10×, 100% dominant among
120 pairs), formalizes the resulting audit-budget allocation problem and
finds naive Neyman allocation is **dominated by simple proportional
allocation** on real sparse audit data, and shows that *which* automated
scorer grades a benchmark (`exact_match` vs `score_boxed`) is itself a
measurable, independently-corroborated source of uncertainty.

## What's here

| Path | What it is |
|---|---|
| `manuscript/latex/main.pdf` | The compiled manuscript. `manuscript/latex/sections/*.tex` is the source; `manuscript/MANUSCRIPT_DRAFT.md` is the prose source it was translated from |
| `manuscript/SUPPLEMENTARY.md`, `manuscript/latex/sections/appendix.tex` | Full derivations, estimator details, bug disclosures, metric definitions |
| `CLAIM_LEDGER.md` | Every quantitative claim in the paper, traced to its script and raw data |
| `NOVELTY_AUDIT.md`, `THEORY_AUDIT.md` | Novelty classification (A/B/C/D) and theoretical rigor checks against real test coverage |
| `REVIEWER_ATTACK_FINAL.md` | Four written hostile reviews (statistics, ML evaluation, skeptical reviewer, area chair) against the typeset manuscript, with fixes applied and reverified |
| `VENUE_AND_OVERLAP_AUDIT.md` | Disclosed, precisely bounded relationship to a concurrent related submission by the same author (TMLR) sharing the same underlying human audit |
| `PAGE_BUDGET.md` | Per-section page accounting against the 9-page main-content limit |
| `FINAL_STATUS.md` | Living status log |
| `scripts/fb_reproduce_all.py` | One command, 38 steps, regenerates every figure/table/number not gated behind the pending human audit |
| `scripts/fb_final_evidence_update.py` | The pipeline that runs once the 458 real labels exist — see `MANUSCRIPT_VERSIONS.md` |
| `labeling/`, `TC_EXPANSION_PREREGISTRATION.md` | The blinded sheet awaiting genuine human labeling, and its preregistered design, sample size, and power calculation |
| `provenance/excluded_labeling_attempts/` | Three AI-generated label submissions detected and excluded before use, preserved as an audit trail |
| `src/flipbudget/` | The installable package (identification math + paired bootstrap) |

## Provenance

The original human audit (`results/analysis/mathhard_labelling_key.json`,
400 items, 350 usable) is shared with a companion, concurrent manuscript by
the same author (under review at TMLR) — verified byte-identical (MD5
`e21cf086392e98b367be04224100e16a`) rather than assumed similar. The
relationship between the two papers — shared data, distinct estimand,
distinct headline statistic, two contributions present here and absent
there — is disclosed explicitly in this paper's own Related Work and
detailed fully in `VENUE_AND_OVERLAP_AUDIT.md`.

## Install and use the package

```bash
pip install -e ".[dev]"
pytest tests/          # 24 tests, real regression suite, not just scripts
```

Library:

```python
from flipbudget import corrected_interval, paired_bootstrap_delta

# One model: correct a reported accuracy for scorer misclassification.
result = corrected_interval(benchmark_verdicts, audit_ystar, audit_yhat)
print(result["corrected_point_estimate"], result["interval"])

# Two models: correct a pairwise comparison, including the flip budget.
cmp = paired_bootstrap_delta(bench1, bench2, ystar1, yhat1, ystar2, yhat2)
print(cmp["corrected_delta_point"], cmp["flip_budget_point"])
```

CLI:

```bash
flipbudget correct records.json audit.json
```

`records.json` is a list of 0/1 scorer verdicts on the benchmark run you want
corrected. `audit.json` is `{"ystar": [...], "yhat": [...]}`, a small paired
human-audit sample (the scorer's verdict and a human's true-label judgment on
the same items). Every returned interval carries an explicit coverage caveat
rather than an unearned "95% CI" label — see `inference.py`'s `COVERAGE_CAVEAT`.

## Reproducing everything except the pending audit

```bash
python scripts/fb_reproduce_all.py
```

One command, 38 steps, clean subprocess per step. Most recent isolated
clean run: **38/38 passed**, ~865s (dominated by one live network step
against the Hugging Face API), full per-step log in
`results/flipbudget/reproducibility_run_2026-09-17.log`.

## The one remaining dependency

458 rows of genuine, independent human labeling
(`labeling/tc_expansion2_l1.csv`, instructions in
`labeling/HUMAN_LABELING_INSTRUCTIONS_tc_expansion2.md`). Three prior
submissions were detected as AI-generated and excluded — see
`TC_EXPANSION2_LABELING_QUALITY_ISSUE.md` — none used in any result. Once
genuine labels exist:
```bash
python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
```
See `MANUSCRIPT_VERSIONS.md` for the exact, deterministic procedure from
there to a final, fully-resolved manuscript.

## License

Apache-2.0 (see `LICENSE`).
