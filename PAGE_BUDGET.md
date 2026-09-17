# Page budget

Measured by direct visual inspection of the compiled PDF (`manuscript/latex/main.pdf`,
compiled 2026-09-17: `pdflatex` + `bibtex` + `pdflatex` x2, zero Overfull/Undefined
warnings), locating each section's start position on its page. Fractional-page
figures are read off the rendered layout, not an automated box measurement —
precise to roughly ±0.05 pages, sufficient to verify the budget, not a
typesetting-internals claim.

**Main content (Abstract through Conclusion): ≈8.5 of 9 pages allowed.
References begin on page 9. Total document: 14 pages** (main content + 1
page of references + ~4.5 pages of appendix, which NeurIPS's own rules do
not count against the main-content limit).

| Section | Pages | Cumulative | Note |
|---|---|---:|---|
| Title / author / abstract | 0.55 | 0.55 | |
| 1. Introduction | 1.10 | 1.65 | fig7 (conceptual framework) moved to appendix this pass |
| 2. Related Work | 0.95 | 2.60 | includes the new P13/TMLR overlap disclosure paragraph — grew, not shrank, this pass; compensated elsewhere |
| 3. Problem Formulation | 0.35 | 2.95 | |
| 4. Theory | 1.30 | 4.25 | includes Table 1 (kept — compact, higher information density per line than the equivalent prose); fig3 moved to appendix |
| 5. Audit Design | 1.10 | 5.35 | fig2 + the compressed 3-row allocation table (was 6 rows) |
| 6. Empirical Setup | 0.37 | 5.72 | dataset table condensed from 12 rows to 5 |
| 7. Results | 1.68 | 7.40 | fig1 + 2 tables kept; fig4/5/6 and 2 tables (scorer-comparison, worst-case detail) moved to appendix |
| 8. Limitations | 0.75 | 8.15 | all 10 items preserved, none deleted, wording tightened |
| 9. Discussion | 0.20 | 8.35 | |
| 10. Conclusion | 0.13 | 8.48 | |
| **References** | ~1.0 | ~9.5 | not counted against the 9-page main-content limit per NeurIPS's own rule |
| **Appendix** | ~3.5 | ~13.0 | not counted against the limit; holds the 5 relocated figures, 2 relocated tables, and the original 9 supplementary subsections |

## What moved, and why each piece is safe to have moved

Everything relocated to the appendix supports a claim already stated in
full, with its number, in the main text — nothing was cut, only relocated
with a pointer left behind:

- **Figure 7** (conceptual framework, schematic, no data) — the least
  evidentiary of the seven figures; the pipeline it illustrates is also
  described in one Introduction sentence.
- **Figure 3** (identified-set geometry) — a pedagogical illustration of
  T-H's already-stated corner-envelope argument, not new evidence.
- **Figures 4, 5, 6** (scorer-choice scatter, worst-case bars, flip-budget) —
  each supports a *secondary* claim (Sections 7.3–7.4) whose headline
  numbers are already stated in the main-text prose; the figure adds visual
  confirmation, not new information a reviewer needs to follow the argument.
- **Table 1 (theory summary)** — kept in the main body on reflection: at 9
  lines it is more space-efficient than the equivalent prose would be, and
  gives a reviewer a one-glance scan of the novelty classification the
  directive explicitly asked to keep auditable.
- **Negative-controls table, scorer-comparison detail table, worst-case
  detail table** — each is a full-detail expansion of numbers already
  stated in the main-text prose (e.g. Section 7.4 states the worst-case
  $\alpha$ range and median width directly; the appendix table adds the
  best-case row and the established-median comparison already implied).

## What was NOT cut

Per the directive's explicit preservation list: the central theorem (T-H /
ranking-preservation, Section 4, full statement retained), all key
empirical evidence (Table 4, the A/B/C pairwise table; Table 5, the
four-layer decomposition; Figure 1 and Figure 2 both stay in the main
body), the strongest audit-design result (Section 5's Neyman-vs-proportional
finding, Figure 2, and its table, all retained in full in the main body),
and all ten Limitations items (tightened in wording, none removed,
none merged into a weaker combined statement that would lose a distinct
caveat).
