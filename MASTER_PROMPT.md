# Master prompt — flipbudget TMLR resubmission

Paste the **Prompt** section below into a fresh Claude session. Everything after it is the
reference the prompt points at. Written 2026-09-25.

---

## Prompt (paste this)

> Read `MASTER_PROMPT.md` and `TASKS_REMAINING.csv` in the repository root before doing
> anything. They record exactly what is finished and what is not. Do not redo finished work,
> do not regenerate a number that already has a macro, and do not write any number into prose.
> Tell me which task you are starting, state its acceptance criteria in one line each, then
> do it and show me the output that proves it passed.

---

## What this project is, in five lines

A leaderboard reports one accuracy per model and names only half of what produced it. The
other half is a verifier, and on the Open LLM Leaderboard's MATH-Hard results the choice of
verifier moves the ranking. The paper bounds which pairwise orderings survive a human reader,
under a stated assumption about cross-model heterogeneity, and reports a breakdown value per
ordering so the dependence on that assumption is measured rather than hedged.

Target venue: TMLR. Hard deadline pressure: MS applications, mid-December 2026.

---

## FINISHED — do not redo any of this

| Area | State |
|---|---|
| Manuscript body | Sections 1–8 written and building. `manuscript/tmlr/main.pdf`, 26 pages |
| Appendix A | Proofs of Lemma 1, Propositions 1–3, and the paired variance bound |
| Appendix B | The numerical checks, with counts from macros |
| Appendix C | Level allocation, the distribution-free half-width, the coverage simulation design |
| Appendix D | Registered sensitivity table, generated |
| Appendix E | The human reference routine compared three ways |
| Related work | Nine paragraphs, 26 verified references added |
| Bibliography | Every entry fetched by DOI or from the arXiv API. Two carried-over entries corrected |
| Number discipline | 91 macros, all generated. `scripts/fb_check_manuscript.py` passes |
| Tests | 880 passing |
| Figures | `figures/f1..f4.pdf`, all regenerable |

There is **one** unwritten block in the whole paper: Results §5.6, which is marked `PENDING`
and cannot be written until labels exist.

---

## The one thing I got wrong earlier, corrected here

There are **two different 458-row sheets**, and they share **no rows**. I previously told you
the 60-row re-label unblocks §5.6. It does not.

| Sheet | Rows | What it is | What it unblocks |
|---|---|---|---|
| `labeling/tc_expansion2_l1.csv` | 458 | Labelled three times in Sept 2026, excluded each time on a provenance judgement | Nothing in the paper yet. Admitting it is the subject of the 60-row check |
| `labeling/relabel_check_l1.csv` | 60 | A stratified subsample **of tc_expansion2**, for a fresh timed pass | Whether those 458 old labels may be used at all |
| `labeling/audit_v3_l1.csv` | 458 | The K=3 audit **registered for this paper**, drawn, never labelled | **Results §5.6.** This is the one the paper describes in Section 4 |
| `labeling/audit_v3_l2_overlap.csv` | 92 | Second-labeler overlap for reliability | The inter-labeler number |

So: **§5.6 needs `audit_v3_l1.csv` labelled.** The 60-row check is a separate provenance
question with its own preregistered consequences.

---

## Order of work

```
T1  email TMLR ──────────────────────────────► unblocks resubmission
T2  relabel 60 rows ──► T3 measure agreement ─► decides the tc_expansion2 question
T6  fix Sidak defect ─┐
T4  label 458 v3 rows ┴► T7 analyse ──► T8 write §5.6 ──┐
T9  motivation paragraphs ─────────────────────────────┤
T10 voice pass ────────────────────────────────────────┼► T16 submit
T11 self-citation decision ────────────────────────────┤
T12 read the cited papers ─────────────────────────────┤
T14 release + datasheet ───────────────────────────────┘
```

T6 must land **before** T7. The reason is in the next section.

---

## What only you can do

**T2 and T4, the labelling.** No AI tool generates, pre-fills, completes or cleans any label.
Open `labeling/app/label.html`, load the sheet, read each response, type what it commits to.
The app blocks pasting, times every item and hashes the export. That instrumentation is the
whole evidentiary value; defeating it destroys the thing it is protecting.

For T2 specifically, the criteria were fixed on 2026-09-24 in `VALIDATION_RELABEL.md`, before
the sheet was drawn:

- **Gate:** zero paste attempts, median dwell ≥ 15 s, no run of more than 20 items under 3 s.
- **Pass:** Cohen's κ ≥ 0.8 **and** raw agreement ≥ 0.90 on Y\*.
- Either outcome gets reported. The sheet is not re-drawn to obtain a nicer one.

**T9, the motivation paragraphs.** `manuscript/tmlr/MOTIVATION_DRAFT.md` has three blocks
marked `[AUTHOR: ...]`. The technical reasons are drafted; what is missing is why a ranking
being wrong bothers *you*, what you were doing when you hit this, and what made you keep going
after the rejection. Two or three sentences each. If Claude writes them, the paper loses the
only part a reviewer cannot get anywhere else.

**T10, the voice pass.** Three reviewers scored clarity 2, 1 and 1. The rewrite addressed
structure. Only you can confirm it sounds like you.

**T11, the self-citation.** Your earlier manuscript *Benchmark Accuracy Is Not an Identified
Quantity* is not cited. Section 4 says "earlier work" with no pointer. Three things are in
tension and they are laid out in `manuscript/tmlr/TODO_CITATIONS.md`. Only you know whether
that manuscript is a separate work or an ancestor of this one.

---

## Hard rules — these caused rework before

1. **Never type a number into prose.** Every number enters through a macro generated by
   `scripts/fb_macros_aistats.py` from a committed result file. `fb_check_manuscript.py`
   enforces it and will fail the build.
2. **A generated file declares itself.** The guard exempts a `.tex` file only when its first
   line reads `% Generated by scripts/`. Do not add names to an exemption list.
3. **Never write a bibliography entry from memory.** Fetch it by DOI content negotiation or
   from the arXiv API. Two entries carried over from the previous paper had a reversed author
   order and a wrong title; both were caught this way.
4. **Never claim a paper says something you have not read.** `TODO_CITATIONS.md` records a
   verification level per reference. A sentence may not be stronger than the level recorded.
5. **No AI attribution anywhere.** Not in commits, not in the paper, not in code comments.
   Sole author: Rajveer Singh Pall.
6. **Do not use Bash heredocs for anything containing backslashes.** It ate `\boxed`, `\title`
   and several regexes in past sessions. Use the Write or Edit tool for LaTeX and for Python
   containing escapes.
7. **Regenerate, never hand-edit.** `macros.tex`, `tables.tex` and `sensitivity_table.tex` are
   outputs. Editing them makes the ledger lie.
8. **Branch before pushing.** Never push to `main` directly.

---

## The open defect (T6) — read before touching the v3 labels

`Inputs.pair_bounds` in `scripts/fb_certify.py` allocates the audit level with
`sidak(2 + n_audited_disc(j) + n_audited_disc(k))` — a **per-ordering** parameter count — and
`run(..., simultaneous=True)` widens only the sampling term.

Today this is correct. `results/flipbudget/audit_v3_labels.json` does not exist, so
`n_audited_disc` is zero for every model, the only audit parameters are the two pooled
concordant intervals, and those are shared by every pair, which makes the audit side
simultaneous for free.

The moment the v3 labels land, each model's discordant intervals enter every ordering that
model appears in, while the Šidák count stays per-pair. The family-wise level stated in
Proposition 3 and in `THEORY_CERTIFICATION.md` §8 stops holding. Appendix C already states the
correct rule; the code has to catch up. **Fix it before T7, not after**, or every number in the
paper will have been computed at the wrong level and will need regenerating.

---

## Commands

```bash
python scripts/fb_relabel_agreement.py
```

```bash
python scripts/fb_audit_v3_analysis.py
```

Full regeneration, in order:

```bash
python scripts/fb_certify.py && python scripts/fb_figures_aistats.py && python scripts/fb_test_census.py && python scripts/fb_macros_aistats.py && python scripts/fb_tables_tmlr.py && python scripts/fb_check_manuscript.py
```

Build the PDF:

```bash
cd manuscript/tmlr && latexmk -g -pdf -interaction=nonstopmode main.tex
```

Verify before claiming anything is done:

```bash
python -m pytest -q && python scripts/fb_check_manuscript.py
```

---

## What "done" looks like for the paper

- `grep -rn "PENDING\|TO WRITE" manuscript/tmlr/*.tex` returns nothing.
- `python scripts/fb_check_manuscript.py` prints `OK`.
- `python -m pytest -q` is green.
- The LaTeX log contains zero undefined references and zero undefined citations.
- Every row of `TODO_CITATIONS.md` reads `read`, or its sentence has been softened to match.
- `MOTIVATION_DRAFT.md` has no `[AUTHOR: ...]` block left.

---

## Files worth knowing

| File | What it holds |
|---|---|
| `PLAN_TMLR_RESUBMIT.md` | The gates G0–G8 and the open defect |
| `VALIDATION_RELABEL.md` | The preregistered criteria for the 60-row check |
| `TC_EXPANSION_PREREGISTRATION.md` | The registered audit design, Amendments 4 and 5 |
| `THEORY_CERTIFICATION.md` | The derivations Appendix A transcribes |
| `CLAIM_LEDGER_AISTATS.md` | Every macro, its value, and the file it came from |
| `manuscript/tmlr/TODO_CITATIONS.md` | Verification level per reference, plus the self-citation decision |
| `provenance/ai_use_ledger.md` | What tooling was used where |
