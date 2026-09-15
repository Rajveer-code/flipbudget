# Major finding: two automated scorers, one benchmark, real disagreement (locked in)

This supersedes the informal write-up in `SCORER_MISMATCH_AND_ADVERSARIAL_FINDINGS.md` (kept, not deleted) as the canonical statement of this finding. Scripts: `scripts/fb_adversarial_suite_v2.py` (discovery), `scripts/fb_tc_expansion_population.py` (full-roster measurement), `scripts/fb_scorer_choice_sensitivity.py` (impact test). All figures re-verified while writing this document.

## 1. The finding, precisely

MATH-Hard's real evaluation harness (`vendor/leaderboard_math/utils.py`, byte-identical to the companion project's copy) computes two scores per item from two extraction methods:

- **`exact_match`** — `math_verify`'s `parse`/`verify` (LaTeX-aware). **This is the field `fb_e1_true_accuracy.py` reads for `a_hat` — every accuracy number this project has ever reported.**
- **`score_boxed`** — `last_boxed_only_string` (finds the last `\boxed{...}`). **This is what T-C's human audit has stratified on and measured α/β for**, inherited exactly from the companion project (`fb_pull_roster.py`).

**Measured across the full 17-qualifying-model roster, all 7 MATH-Hard subjects, 22,508 (model, item) rows (`results/analysis/tc_expansion_population.json`):**

| Quantity | Value |
|---|---|
| Overall disagreement rate, FULL population (22,508 rows, 17 models × 7 subjects) | **3.63%** (817/22,508; exact 95% CI [3.39%, 3.88%]) — **the correct headline number**, verified by direct recount from `tc_expansion_population.json` |
| Overall disagreement rate, algebra_hard subject only (5,219 rows) | 6.51% — a real, correct number, but for one subject, not the population; kept earlier without stating the scope clearly enough — corrected here |
| Model-level range, full population | **0.60% (falcon-7b) to 9.59% (Yi-1.5-9B-Chat)** — corrected from an earlier, wrongly-scoped "0.7–18.6%" figure |
| Direction | Bidirectional — neither scorer strictly dominates |
| Per-model accuracy gap (`a_hat_exact_match − a_hat_score_boxed`) | mean +0.76 pts, but ranges from **−6.87 pts** (Yi-1.5-9B-Chat, score_boxed higher) to **+5.66 pts** (zephyr-orpo, exact_match higher) |
| `a_hat_exact_match` vs. the already-published `e1_case_b_TRUE.json` | Matches to within rounding on 16/17 models (one model, falcon-40b, differs by 0.15 pts — a snapshot-version artifact, not a methodology error) — **independent confirmation this project's `a_hat` pipeline is correctly reading `exact_match`** |

**Mechanisms** (from the 12-category adversarial taxonomy, `scripts/fb_adversarial_suite_v2.py`): `score_boxed` false-misses unboxed "Final Answer: X" prose and bracket-delimited answers; both scorers can mis-extract self-corrected multi-`\boxed{}` responses, via different failure modes; `exact_match` (`math_verify`) false-credits at least one unit-mismatch case (`9 meters` vs `9 seconds`) that `score_boxed` correctly rejects.

## 2. Reinterpreting prior claims — explicit, not silent

**Every α/β, every T-C audit result reported before this finding was measuring `score_boxed`, not `exact_match`.** Stated once here, and the label applies retroactively to every prior number:

| Prior claim | Correct reading now |
|---|---|
| T-C's real audit: 0/69 scorer-wrong events (`TC_REAL_ANALYSIS.md`) | 0/69 **`score_boxed`**-wrong events, relative to human transcription |
| Pooled α anchor ≈3.14%, β≈0 (`TC_ALPHA_BETA_UPDATE.md`) | **`score_boxed`'s** pooled α/β — not a property of `exact_match` |
| Reconciliation's scorer-identification-only layer, Λ=2 (`RECONCILIATION_FOUR_LAYERS.md`) | A Λ-band around **`score_boxed`'s** pooled estimate |
| Every `alpha_ci`/`beta_ci` Wilson interval used in `fb_ea_dominance_canonical.py`, `fb_audit_design_optimization.py` | Audited for **`score_boxed`** |

No historical number is corrected or retracted by this — they were always accurate descriptions of `score_boxed`'s behavior. What changes is that they must now be **cited as `score_boxed`-specific**, not as "the scorer's" behavior generically, since a second, real scorer (`exact_match`) exists and behaves measurably differently.

## 3. Does this change any headline result? Tested directly, not assumed.

**Self-consistency test** (`fb_scorer_choice_sensitivity.py`): the E-A dominance pipeline has always paired `exact_match`-based accuracy with `score_boxed`-audited α/β — a real construct mismatch. Re-ran with the **self-consistent** pairing (`score_boxed`'s own accuracy + its own audited α/β):

| Pairing | n valid | Median ratio | % dominant |
|---|---|---|---|
| `exact_match` accuracy + `score_boxed` α/β (used throughout, mismatched) | 120 | 6.095 | 100.0% |
| `score_boxed` accuracy + `score_boxed` α/β (self-consistent) | 120 | **5.735** | **100.0%** |

**The headline survives**: 5.74× vs. 6.10×, both 100% dominant on the same 120 valid pairs. The construct mismatch changes the point estimate by ~6%, not the qualitative finding.

**New, fifth uncertainty layer — scorer-choice width** (fully computable without new human labels, since both accuracies are automated): `|Δ*_exact_match − Δ*_score_boxed|` per pair, holding α/β fixed.

| Layer | Median width |
|---|---|
| Sampling | 0.0431 |
| Scorer-identification-only (Λ=2) | 0.0679 |
| **Scorer-choice (new)** | **0.0091** |
| Audit-estimation-only | 0.2800 |

**Scorer-choice is the smallest of the four measured uncertainty sources at the median** — about a fifth of sampling width, roughly 1/30 of audit-estimation width. Verdict B (audit-estimation dominates) is not threatened by this finding; if anything it is now measured against one more real, quantified competitor and still wins by a wide margin.

**Honest caveat, not smoothed over**: the scorer-choice width has a heavy right tail (mean 0.0377 vs. median 0.0091, max **0.2491** — comparable to the audit-only layer's own median for at least one real pair). For most comparisons scorer choice barely matters; for a specific minority it matters a lot. This is reported as a real, pair-dependent phenomenon, not summarized away by the median alone.

## 4. What this enables for the manuscript (see `NOVELTY_AUDIT.md`, `MANUSCRIPT_ARCHITECTURE.md` for the full integration)

The finding generalizes the paper's claim beyond "one scorer has a measurable error rate" to **"a benchmark's reported accuracy is itself scorer-choice-dependent, and that dependence can be measured and bounded using the same audit-design machinery already built for scorer error"** — a broader claim about evaluation pipelines as measurement systems, not just about MATH-Hard's `is_equiv`. See §10 discussion in `NOVELTY_AUDIT.md`.
