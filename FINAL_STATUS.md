# FINAL_STATUS.md — autonomous execution log

## Correct framing of the stop condition (corrected mid-run)

The 458 human labels block ONLY the analyses that specifically require them (analysis C, exact_match's own α/β and self-consistent identification). They are not a reason to pause everything else. This file reflects the state after continuing through everything that does NOT require them.

## What's genuinely done, this run

- **Theory**: flip-budget uncertainty computed on current real MATH-Hard data (superseding a stale MMLU placeholder run), added as `THEORY_EXTENSIONS.md` §7. All other theory items in the directive's list (ranking-preservation, correlated-error, imperfect-reference, verification-bias, partial-identification inference) were already complete from prior phases — verified present, not re-derived.
- **Manuscript**: full draft, all 13 requested sections, written as real prose (`manuscript/MANUSCRIPT_DRAFT.md`), not an outline. Every result depending on the pending audit marked `[PENDING — human audit]` with the exact quantity named. Self-corrected one real weakness (abstract citing only one of two established ratios) via a targeted hostile self-review pass.
- **Figures**: 2 of the ~7 listed (`fig1_uncertainty_decomposition.png`, `fig2_audit_budget_curve.png`), both regenerated from disk data, 300dpi, captioned honestly including caveats.
- **Supplementary material**: `manuscript/SUPPLEMENTARY.md` — HT estimator full derivation, sampling design, adversarial-suite taxonomy, a 7-row bug-disclosure table with quantified impact per bug, exact metric definitions, reproducibility instructions.
- **Consistency audit**: grepped for stale 6.51%, unqualified 6.10×, 134.32×/5.24× without superseding context. Fixed 3 real instances (`CANONICAL_EA_RESULT.md` scope note; `TIER1_VERDICT.md` superseding header; abstract's single-ratio citation).
- **Auto-update pipeline**: `scripts/fb_final_evidence_update.py` — one command (behind an explicit confirmation flag), runs quality gate + full recompute + figure regeneration + test suite + dated JSON report. Syntax-verified; not run end-to-end (needs real labels to actually execute past the gate).
- Tests: 24/24 passing throughout this run.

## What's NOT done — honestly, not glossed over

- Manuscript sections beyond the ones drafted are complete in substance but not typeset/polished for actual submission (no LaTeX, no venue template, no reference list with real DOIs — citations are author-year placeholders pointing at real papers, not formatted).
- 5 of the ~7 listed figures not built (conceptual pipeline diagram; identified-set geometry; scorer-choice disagreement chart as its own figure, currently folded into fig1; ranking-preservation/flip-budget visualization).
- Tables requested (dataset description, theorem summary, scorer comparison, robustness/sensitivity summary) not built as standalone table artifacts — the same numbers exist in prose/markdown tables throughout the manuscript and supplementary, not reformatted into dedicated table files.
- The 3-reviewer hostile pass was NOT redone from scratch on the new manuscript — one targeted self-review catch was made and fixed (the abstract issue); a full fresh 3-reviewer pass on the assembled manuscript specifically (as opposed to the underlying science, already covered in `REVIEWER_ATTACK.md`) was not performed this run.
- `fb_final_evidence_update.py` has not been exercised end-to-end against a real labeled file (cannot be, without real labels) — its component pieces (`fb_tc_expansion2_analysis.py`, the two figure scripts, pytest) are each independently verified working.

## Exact human-label-dependent components remaining

Everything in `MANUSCRIPT_DRAFT.md` marked `[PENDING — human audit]`: `exact_match`'s own audited α/β; analysis C's median ratio and % dominant; the fully self-consistent four-layer decomposition for `exact_match`.

## Commands to run after labels arrive

```bash
python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
```
Then manually transfer the resulting numbers into `MANUSCRIPT_DRAFT.md`'s `[PENDING]` markers (deliberately not automated — see that script's docstring).
