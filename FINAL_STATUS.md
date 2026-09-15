# FINAL_STATUS.md — autonomous execution log

## Correct framing of the stop condition

The 458 human labels block ONLY the analyses that specifically require them (analysis C, `exact_match`'s own α/β and self-consistent identification). They are not a reason to pause everything else. This file reflects the state after two consecutive autonomous passes continuing through everything that does NOT require them.

## Paper readiness audit

| Component | Status | Remaining action |
|---|---|---|
| Theory | Done | None — T-A/T-H/T-B/T-D/T-E, ranking-preservation, correlated-error, flip-budget all derived, A/B/C-classified, cross-checked against literature |
| Empirical evidence (analyses A, B) | Done | None — 6.10×/5.74×, 100% dominant, real data, reproducible |
| Empirical evidence (analysis C) | **Blocked** | 458 real human labels (the one true external dependency) |
| Scorer-mismatch finding | Done | None — 3.63% full-population rate, worst-case bound, one genuine external corroboration (HF's math-verify postmortem) |
| Human audit pipeline hygiene | Done | None — two AI-generated submissions caught and excluded; quality gate hardened this pass with duplicate/corruption/row-count/provenance checks, tested against a synthetic bad file |
| Figures | Done | All 7 built, each viewed and two real rendering defects (fig6 legend collision, fig7 crossing arrows) caught and fixed before commit |
| Tables | Done | All 8 standalone artifacts built; two real bugs (unformatted placeholder, wrong per-model range from a bad field comparison) caught and fixed before commit |
| Manuscript assembly | Done | All 13 sections real prose; every figure/table referenced exactly once (grep-verified) |
| Manuscript accuracy (hostile review) | Done | One substantial finding — two separate human audits (400-item original vs. T-C's 69-item round) were conflated in the abstract and §6 as if one continuous result — traced, root-caused, and corrected; Limitations item 7 added disclosing the unmerged-pooling gap this exposed |
| Related work / novelty | Done | Chen-Rambachan-Tamer distinguished; one genuine external validation added (HF's math-verify postmortem); no claim rises above novelty class C |
| Reproducibility | **Not fully verified this pass** | `fb_reproduce_all.py` extended to 33 steps and launched as a full clean run; each new step individually re-verified to exit 0, but the single unbroken 33-step pass had not finished by the time this file was last written (network/IFEval steps are slow) — check its output before citing "N/33 passed" anywhere |
| Supplementary material | Done | HT estimator derivation, sampling design, adversarial-suite taxonomy, 7-row bug table, metric definitions, reproducibility instructions |
| Formatting / submission package | **Not started** | No LaTeX, no venue template, no formatted reference list — explicitly out of scope for content-readiness, in scope for actual submission |

## Positioning decision (made, not deferred)

**Option C — a combination with one clearly dominant thesis.** The dominant thesis is partial identification: reported benchmark accuracy is not automatically identified because the scorer that produces it is an imperfect, only-partially-audited measurement procedure. Audit design is the concrete mechanism this creates (§5) and scorer-choice dependence is an explicitly secondary, bounded-not-resolved finding (§7.4) — this is already how the title, abstract, and every section transition are written; nothing needed to change to reach this framing, it fell out of how the manuscript was drafted and held up under the hostile-review pass.

## Venue re-evaluation

Unchanged from `NOVELTY_AUDIT.md`'s prior verdict: **NeurIPS 2027 Evaluations & Datasets track** (or equivalent — ICML/ICLR datasets-and-benchmarks tracks, or a workshop as a fast-decision parallel per the user's global venue-strategy preference). Re-checked against the now-fully-assembled paper, not upgraded merely because the paper reads stronger post-polish: no individual result exceeds novelty class C, the contribution is the combination, and the CFP fit noted in `NOVELTY_AUDIT.md` ("empirical audits... methodological analyses... redesign or stress-testing of evaluation practices") still matches exactly.

## What's genuinely done, this pass (second autonomous continuation)

- **Worst-case sensitivity given a real script**: the 2.38%/26.73%/0.166 figures from `METHODOLOGICAL_AUDIT.md` item 7 existed only as an inline, unsaved calculation — built `scripts/fb_worst_case_sensitivity.py`, verified it reproduces the published numbers exactly.
- **5 remaining figures** built (`fig3`–`fig7`): identified-set geometry, scorer-choice disagreement, worst-case sensitivity, flip-budget/ranking-preservation, conceptual framework. Each viewed after generation; two real defects found and fixed (fig6's legend overlapped the data and used an unverified geometric relationship for a threshold line — dropped; fig7's title was clipped and an earlier grid layout produced crossing arrows — replaced with a staircase layout).
- **8 standalone tables** built (`scripts/fb_build_tables.py` → `tables/*.md`). Two real bugs caught reviewing the script's own output before committing: a literal unformatted `{n_valid}` placeholder, and a per-model disagreement-range computation that produced 69%–100% garbage on the first attempt because it compared stratum labels (which include a third "unparsed" value) instead of the data's own authoritative `disagree` boolean.
- **Every figure and table wired into the manuscript body** — was fig1-only before this pass; grep-verified each of fig1–7/table1–8 now has exactly one reference.
- **Fresh hostile-review pass on the assembled manuscript** (not just the underlying science, already covered by `REVIEWER_ATTACK.md`). Found and fixed the two-audits-conflated issue above (the pass's single most consequential catch), plus two smaller clarity fixes (a forward-pointer for "historical, mixed" in §7.1; adding Figure 7 to the Introduction).
- **One genuine external validation, not forced**: Hugging Face's own "Fixing Open LLM Leaderboard with Math-Verify" postmortem independently documents the same comparator failure family this project's adversarial suite found, and confirms `exact_match` (this project's field) is the platform's own current endorsed scorer. Added to Related Work with careful hedging; logged in `NOVELTY_AUDIT.md`.
- **Quality-gate hardened** against a third bad label submission: duplicate-uid, unmatched-uid, wrong-row-count, and answer-corruption checks added to `fb_tc_expansion2_analysis.py`'s `quality_gate`, verified against a synthetic bad file built for the purpose.
- **`fb_reproduce_all.py` extended** from 21 to 33 steps (new figures/tables/analyses added); a full clean run was launched but had not finished at last check.
- Tests: 24/24 passing throughout this pass.

## What's NOT done — honestly, not glossed over

- The 33-step reproducibility pipeline's single unbroken pass had not finished/been confirmed at the time this file was last written — see the reproducibility row above.
- Manuscript not typeset for actual submission (no LaTeX, no venue template, no formatted reference list with real DOIs).
- The T-C round's 69 additional audited items were never merged into `e4_mathhard_per_model.json`'s pooling (Limitations item 7) — mechanical but undone.
- No second independent benchmark with two genuinely independent scoring libraries was found (searched honestly, reported as a named limitation, not glossed over).

## Exact human-label-dependent components remaining

Everything in `MANUSCRIPT_DRAFT.md` marked `[PENDING — human audit]`: `exact_match`'s own audited α/β; analysis C's median ratio and % dominant; the fully self-consistent four-layer decomposition for `exact_match`.

## Commands to run after labels arrive

```bash
python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
```
Then manually transfer the resulting numbers into `MANUSCRIPT_DRAFT.md`'s `[PENDING]` markers (deliberately not automated — see that script's docstring).
