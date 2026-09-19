# PLAN_REBUILD (approved "rebuild", 2026-09-19)

Rebuild the paper on the corrected (predictive-value) estimand, per
CORE_ESTIMAND_AUDIT.md §10. No new labels. Surviving claims:
C1 census scorer disagreement 3.63%; C2 differential scorer error (common-
mechanism test); C3 audit-sizing law for per-model ranking identification;
C4 indeterminate-label (Manski) bounds. Obsolete results stay in repo as
audit trail, leave the paper.

- [x] 1. Library: `src/flipbudget/identification.py` on PV map (+ Bayes
      conversion to alpha/beta), Sidak projection; tests first. Verify: pytest.
- [x] 2. Analysis entry point `scripts/fb_rebuild_analysis.py` ->
      `results/flipbudget/rebuild_results.json` (C1-C4 + pairwise table).
      Verify: runs clean, numbers match CORE_ESTIMAND_AUDIT where overlapping.
- [x] 3. Figures (new fig1 teaser intervals, fig2 sizing curve, fig3
      differential error) + tables from JSON. Verify: view each PNG.
- [x] 4. Bibliography: add verified refs (two-phase / verification bias /
      PPI line / benchmark sources). Verify: each checked by search.
- [x] 5. Manuscript rewrite (all sections, appendix). Verify: compiles,
      0 overfull/undefined, <=9 pages, grep old numbers = 0 hits.
- [x] 6. Docs: preregistration amendment, CLAIM_LEDGER, FINAL_STATUS,
      README. Verify: grep old headline numbers outside audit-trail files.
- [ ] 7. Reproducibility: add new steps to `fb_reproduce_all.py`, full clean
      run. Verify: all steps pass, log saved.
- [ ] 8. Hostile re-review of rebuilt PDF; fix; rebuild SUBMISSION_FINAL.
