# Excluded labeling attempts — provenance only, never used in any result

Per explicit instruction: preserved as an audit log, permanently excluded
from the scientific analysis. Nothing in this directory feeds any result
in `results/flipbudget/`, `EVIDENCE_TABLE.md`, or `CONSOLIDATED_VERDICT.md`.

| File | What it is | Why excluded | Full account |
|---|---|---|---|
| `round1_mislabeled_as_ifeval_actually_tc.csv` | Submitted as IFEval labeling; uid-set matches T-C's key exactly (70/70) | Not IFEval at all — T-C's sheet, resubmitted with a bare 0/1 scheme, already fully labeled and analyzed elsewhere | `IFEVAL_LABEL_QUALITY_ISSUE.md` |
| `round1_ifeval_judged_binary_89pct_contradicted.csv` | First real IFEval labeling attempt (454 rows, bare 1/0) | 89.3% of "compliant" marks contradicted by a concrete, deterministic instruction failure, checked against the real per-instruction verifier | `IFEVAL_LABEL_QUALITY_ISSUE.md` |
| `round2_tc_resubmission_corrupted.csv` | Second T-C submission (70 rows) | Not a fresh independent re-read — systematically corrupted (every `\frac{X}{Y}` → `\frac{X{Y`, lost the cross-verified `CONTRADICTORY` case, `NOT FOUND` on items with a stated answer) | `IFEVAL_LABEL_QUALITY_ISSUE.md` |
| `round2_ifeval_judged_90pct_contradicted.csv` | Second IFEval labeling attempt, after the README was rewritten with the exact prior failure example and a mechanical-checking checklist | 90.5% contradiction rate — no improvement over round 1 | `IFEVAL_LABEL_QUALITY_ISSUE.md` |

The genuine, currently-standing results are elsewhere:
`labeling/tc_expansion_l1_completed.csv` (+ l2/l3) for T-C, analyzed in
`TC_REAL_ANALYSIS.md` / `TC_ALPHA_BETA_UPDATE.md`. IFEval's 454-row sheet
(`labeling/ifeval_audit_l1.csv`) remains unlabeled and paused per your
decision — see `CONSOLIDATED_VERDICT.md`.
