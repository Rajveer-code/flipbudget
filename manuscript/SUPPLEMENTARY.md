# Supplementary material

Consolidated pointers + the technical details not fully spelled out in the main text, per Phase 5 of the latest directive. Full derivations live in their own dedicated files (linked below), not duplicated here — this file is the index plus the pieces that don't have a natural home elsewhere.

## S1. Proofs and derivations

| Result | File |
|---|---|
| T-A (Scorer Sensitivity Model), symbolic + numeric verification | `TA_SSM_DERIVATION.md`, `scripts/fb_ta_ssm.py` |
| T-H (sharpness) | Embedded in `TA_SSM_DERIVATION.md`; boundary-case audit `scripts/fb_ta_boundary_audit.py` |
| T-B (design sensitivity) | `TB_DESIGN_SENSITIVITY.md` (pure-Λ), `TB_COMPOUND.md` (compound, saturation-corrected) |
| Ranking-preservation theorem | `THEORY_EXTENSIONS.md` §2 |
| Correlated-error Propositions 1–3, Monte Carlo verification | `THEORY_EXTENSIONS.md` §1, `scripts/fb_theory_correlated_error.py` |
| T-D (imperfect reference, `q_max(η)` bound) | `THEORY_EXTENSIONS.md` §4 |
| T-E (verification bias / Horvitz-Thompson validity) | `THEORY_EXTENSIONS.md` §5 |
| Neyman allocation proof | `scripts/fb_audit_design_optimization.py` docstring (3-line Lagrangian) |
| Flip-budget bootstrap | `THEORY_EXTENSIONS.md` §7, `src/flipbudget/inference.py::paired_bootstrap_delta` |

## S2. The Horvitz-Thompson / post-stratified estimator, full detail

For a scorer's credited (or wrong) stratum composed of cells `S = {h}` with population size `N_h` and sample `(n_h, x_h)` (scored rows, events):

```
p_hat_HT = sum_{h in S} N_h * (x_h/n_h)  /  sum_{h in S} N_h
Var(p_hat_HT) = [1 / (sum_h N_h)^2] * sum_h N_h^2 * (1 - n_h/N_h) * p_h(1-p_h) / max(n_h-1, 1)
```

`(1 - n_h/N_h)` is the finite-population correction. Implementation: `scripts/fb_tc_expansion2_analysis.py::_ht_pool`. Regression tests, including the bias-if-naively-pooled demonstration: `tests/test_tc_expansion2_estimator.py`. Cell-to-scorer unions (which cells feed which scorer's credited/wrong stratum — NOT the same two cells for both scorers): `SCORER_CELLS` in the same file, cross-checked against `scripts/fb_tc_expansion_sample.py::cell_of`.

## S3. Sampling design, full detail

Population: 22,508 (model, item) rows, 17 qualifying models × 7 MATH-Hard subjects (`results/analysis/tc_expansion_population.json`). Four joint-scorer cells, exact population sizes: `both_credited`=1,531, `both_not_credited`=19,873, `disagree_sb_credited_em_not`=291, `disagree_em_credited_sb_not`=493. Sample targets: 200/198/30/30 = 458, seed 42, blinded (`labeling/tc_expansion2_l1.csv`), excludes 320 items already in the original 400-item T-C population. Full preregistration, including the three separate power calculations behind each target-n: `TC_EXPANSION_PREREGISTRATION.md`.

## S4. Adversarial suite — full taxonomy and results

12 categories (formatting, LaTeX, whitespace, delimiters, answer-position, verbosity, multiple-answers, self-correction, numerical-formatting, case, units, other-scorer-specific), 24 constructed cases with known ground truth, run against both live scorers via the real harness function (`math_verify`'s `parse`/`verify` with `parsing_timeout=None`/`timeout_seconds=None` — its own multiprocessing-based timeout is unreliable when called repeatedly from a dynamically-loaded module on this platform, a second, distinct Windows-fragility finding alongside `is_equiv`'s `SIGALRM` issue). 5 of 12 categories are null results, reported as such. Full table: `SCORER_MISMATCH_AND_ADVERSARIAL_FINDINGS.md`.

## S5. Bug disclosures (full account, each with root cause and quantified impact)

| Bug | Root cause | Impact quantified |
|---|---|---|
| `is_equiv` always `False` on Windows | `signal.SIGALRM` doesn't exist; existing `ThreadPoolExecutor` patch didn't actually fix it | 0/69 T-C rows change; 1/400 original-audit rows change; verified correct on real Linux CI |
| Empty-identified-set silently inverted | Independent `max(lo,0)`/`min(hi,1)` clipping when the raw range misses `[0,1]` entirely | 16–70 of 136 real pairs depending on layer; fixed in package + research code, 3 new tests |
| Mutable self-comparison in 2 IFEval scripts | Compared against the file about to be overwritten, corrupting historical baselines on re-run | Caught by the reproducibility pipeline's own second run; fixed |
| Hardcoded absolute Downloads paths | `fb_tc_real_analysis.py`'s `load_l1/l2/l3` | Caught building the Linux CI validation; fixed, re-verified identical output before/after |
| `score_boxed`/`exact_match` scope confusion in an early draft of this session's own scorer-mismatch note | 6.51% (algebra_hard-only) presented next to full-population language | Corrected to 3.63% everywhere; `METHODOLOGICAL_AUDIT.md` item 1 |
| Naive pooling across disproportionate sampling-fraction cells | `fb_tc_expansion2_analysis.py`'s original `recompute_alpha_beta` | +444% relative bias demonstrated in a realistic scenario; fixed with HT estimator before any real label was processed |
| `math_verify`'s multiprocessing timeout crash | Windows `multiprocessing.spawn` fragility when called repeatedly from a dynamically-loaded module | Fixed via `parsing_timeout=None` — safe for short constructed inputs, not a scoring-behavior change |

## S6. Exact metric definitions

- **α (false-credit rate)**: `P(scorer says correct | true label incorrect)`, estimated within the audited credited stratum.
- **β (false-miss rate)**: `P(scorer says incorrect | true label correct)`, estimated within the audited wrong/unparsed stratum.
- **Identified-set width**: `hi - lo` of the sharp interval for `A*` (single-model) or `Δ*` (pairwise), per T-A/T-H.
- **Dominant**: `W_identification / W_sampling > 1` for a given pair.
- **Unresolved**: the identified interval for `Δ*` contains 0.
- **Flip budget `d*`**: the minimum differential-error perturbation (beyond the audited margins) required to make an otherwise-resolved comparison's sign ambiguous; `None`/degenerate if the pair is already unresolved at `d=0`.
- **Scorer-disagreement rate**: fraction of (model, item) rows where `score_boxed` and `exact_match` give different binary verdicts on the identical raw response.

## S7. Reproducibility

`scripts/fb_reproduce_all.py` — one-command canonical chain, 21 steps (now includes this phase's estimator/analysis scripts where they don't require new human labels), clean-subprocess-per-step, tagged pure/human-label/network. Last full clean run: 21/21 passed (this session). Package tests: `pytest tests/` — 24/24 passed as of this phase. Environment: Python 3.13.12, Windows; pinned dependencies in `pyproject.toml`; fixed seeds throughout (42 is the standing convention).
