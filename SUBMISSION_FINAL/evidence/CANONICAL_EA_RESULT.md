# Canonical E-A dominance result (item 1 of the final validation phase)

**Scope note, added after the scorer-mismatch audit**: the 6.10×/100% figure below is analysis **A** in `METHODOLOGICAL_AUDIT.md`'s item 6 — the historical *mixed* pairing (`exact_match` accuracy + `score_boxed`-audited α/β). The internally self-consistent `score_boxed` analysis (**B**) gives 5.74×; `exact_match`'s own fully self-consistent analysis (**C**) is not yet established, pending the 458-row human audit. Cite this page's number as "the historical mixed result," not as an unconditional final figure.

Recomputed from the rawest available inputs (`pair_identification_human.json`,
`e1_case_b_TRUE.json`, `e4_mathhard_per_model.json`), not from an intermediate
file. Script: `scripts/fb_ea_dominance_canonical.py`. Output:
`results/flipbudget/ea_dominance_canonical.json`. This supersedes
`ea_dominance_pairwise_corrected_v2.json`/`ea_dominance_corrected_v2.json` as
the citable source for A1/A2 in `EVIDENCE_TABLE.md` — those files were
produced by an untracked interactive calculation during the previous phase
(no script in `scripts/` writes them; grepped directly, confirmed absent).
They are preserved on disk, unmodified, as historical record; this script is
now the reproducible source of truth and its numbers match theirs exactly,
which is itself the verification that the earlier ad-hoc calculation was
correct, not just untracked.

## The full denominator cascade (pairwise)

| Stage | Count | Running total |
|---|---|---|
| Total candidate pairs (all models with a human pair-identification label) | C(28,2) | **378** |
| − pairs where a model has no e1/e4 accuracy-audit data at all (`microsoft/Phi-3-mini-4k-instruct`) | 27 | 351 |
| − pairs where a model has accuracy data but fails the audit-qualification gate (needs audit n>0 on both the credited and wrong strata; 10 of 27 models fail, all on the credited side) | 215 | **136** = C(17,2) |
| **= pairs scored** (both models qualify for a Wilson-CI box) | | **136** |
| − empty identified set (raw Wilson-CI box for ≥1 model's (α,β) does not overlap [0,1] at all — see `RECONCILIATION_EMPTY_SET_BUG.md`) | 16 | **120** |
| **= VALID pairs** (well-defined W_identification vs. W_sampling comparison) | | **120** |

No step in this cascade was previously reported as a single table; `EVIDENCE_TABLE.md` stated "n=120 of 136" but not the 378→136 stage.

## Ratio distribution, valid pairs only (n=120)

| Statistic | Value |
|---|---|
| Median | 6.095 |
| Mean | 7.387 |
| Min | 2.153 |
| Max | 20.300 |
| P5 / P10 | 2.723 / 3.247 |
| P25 / P75 | 4.061 / 9.535 |
| P90 / P95 | 14.759 / 15.677 |

Min = 2.153 > 1 — every single valid pair shows identification width exceeding sampling width by at least a factor of 2; this is not a result carried by a few large outliers pulling the mean up (mean 7.387 > median 6.095 confirms a right skew, but even the smallest ratio in the whole valid set clears the 1× bar by a wide margin).

## "100% dominant" — three denominators, so the claim cannot be misread

| Denominator | Dominant pairs | % |
|---|---|---|
| **Valid pairs (n=120)** — what "100% dominant" refers to | 120/120 | **100.0%** |
| Pairs scored (n=136, empty-set pairs excluded as not-applicable, not counted either way) | 120/136 | 88.2% |
| All candidate pairs (n=378, most conservative — empty-set and non-qualifying pairs both treated as non-dominant) | 120/378 | 31.7% |

**The honest headline is "100% of the 120 pairs where the comparison is well-defined show identification-width dominance," not "100% of all comparisons."** 258 of the 378 raw candidate pairs (68.3%) never enter this statistic at all, for two structural reasons (missing audit data entirely, or an empty identified set) — both reasons are about audit-data availability and consistency, not about the comparison having been checked and found non-dominant.

## Single-model (A2), same cascade

| Stage | Count |
|---|---|
| Total models with accuracy data | 27 |
| Qualifying for Wilson-CI (audit n>0 both strata) | 17 |
| Empty identified set | 1 (`CohereForAI/c4ai-command-r-v01`) |
| **Valid** | **16** |

Ratio distribution (n=16): median 3.220, mean 4.868, min 1.543, max 16.305.

| Denominator | Dominant | % |
|---|---|---|
| Valid models (n=16) | 16/16 | 100.0% |
| Qualifying models (n=17) | 16/17 | 94.1% |
| All models with accuracy data (n=27) | 16/27 | 59.3% |

## What this changes

Nothing about the direction or the point estimate — 6.10× (median, rounds to the previously-reported figure) and min ratio 2.153 both confirm the earlier `_corrected_v2` numbers were correct, not merely uncontradicted. What changes is that the claim is now traceable to a saved, re-runnable script with the full 378→136→120 cascade stated once, in one place, so "100% dominant" cannot be quoted out of context as covering all comparisons attempted.
