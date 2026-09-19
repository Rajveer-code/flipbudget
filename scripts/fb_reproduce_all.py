"""One-command reproducibility pipeline (item 16). Runs the canonical chain
of scripts that produce every number in EVIDENCE_TABLE.md / CONSOLIDATED_
VERDICT.md, in dependency order, in a clean subprocess each (so a failure in
one step doesn't hide a stale import in the next), and reports PASS/FAIL per
step. Does not include every exploratory script ever written in this
project (many are superseded -- see EVIDENCE_TABLE.md for what replaced
what); this is the CURRENT, live chain.

Steps needing network + the local HF token (already-authenticated on this
machine, not a new credential) are marked NETWORK. Steps needing
human-labeled data already committed in labeling/ are marked HUMAN-LABEL-
DEPENDENT (reproducible from files in this repo, not from code alone).
Everything else is pure computation from data already on disk.

Run: python scripts/fb_reproduce_all.py
"""
import subprocess
import sys
import time

STEPS = [
    ("Theory: SSM derivation", "scripts/fb_ta_ssm.py", "pure"),
    ("Theory: design sensitivity", "scripts/fb_tb_design_sensitivity.py", "pure"),
    ("Theory: correlated-error simulation", "scripts/fb_theory_correlated_error.py", "pure"),
    ("E-A: dominance study (original, uncorrected method, provenance)", "scripts/ea_dominance_study.py", "pure"),
    ("T-A: compound interval", "scripts/fb_ta_compound_interval.py", "pure"),
    ("T-A: boundary audit", "scripts/fb_ta_boundary_audit.py", "pure"),
    ("T-B: compound design sensitivity", "scripts/fb_tb_compound_design_sensitivity.py", "pure"),
    ("Reconciliation: four layers", "scripts/fb_reconcile_layers.py", "pure"),
    ("Audit design: six-question analysis", "scripts/fb_audit_design_analysis.py", "pure"),
    ("Audit design: stress test", "scripts/fb_audit_design_stress_test.py", "pure"),
    ("T-C: real analysis (69 human trials)", "scripts/fb_tc_real_analysis.py", "human-label"),
    ("T-C: alpha/beta pooling update", "scripts/fb_tc_alpha_beta_update.py", "human-label"),
    ("Adversarial suite", "scripts/fb_adversarial_suite.py", "pure"),
    ("Comparator bug verification (T-C)", "scripts/fb_verify_is_equiv_bug.py", "human-label"),
    ("Comparator bug verification (original 400-item audit)", "scripts/fb_verify_original_audit_bug.py", "pure"),
    ("Blinding verification", "scripts/fb_blinding_verification.py", "pure"),
    ("IFEval: mechanism rescan", "scripts/fb_ifeval_mechanism_rescan.py", "network"),
    ("IFEval: reproducibility row cache", "scripts/fb_ifeval_repro_cache.py", "network"),
    ("IFEval: reproducibility check (15+5 replicates)", "scripts/fb_ifeval_reproducibility_check.py", "network"),
    ("IFEval: key re-flag", "scripts/fb_ifeval_key_reflag.py", "pure"),
    ("Provenance manifest", "scripts/fb_provenance_manifest.py", "pure"),
    ("E-A: canonical dominance recomputation (final validation phase)", "scripts/fb_ea_dominance_canonical.py", "pure"),
    ("Root-cause: 70 empty scorer-only sets (final validation phase)", "scripts/fb_rootcause_empty_scorer_layer.py", "pure"),
    ("Negative controls (final validation phase)", "scripts/fb_negative_controls.py", "pure"),
    ("T-C: correlated-error bound (final validation phase)", "scripts/fb_tc_correlated_error_bound.py", "human-label"),
    ("Audit design: formal optimization + budget curve (final validation phase)", "scripts/fb_audit_design_optimization.py", "pure"),
    ("Adversarial suite v2: 12-category taxonomy + real-data grounding", "scripts/fb_adversarial_suite_v2.py", "pure"),
    ("Scorer-choice self-consistency + scorer-choice-width layer", "scripts/fb_scorer_choice_sensitivity.py", "pure"),
    ("Worst-case sensitivity bound (exact_match, population-weighted extremes)", "scripts/fb_worst_case_sensitivity.py", "pure"),
    ("Flip-budget uncertainty (real MATH-Hard data)", "scripts/fb_flip_budget_uncertainty_mathhard.py", "pure"),
    ("T-C expansion2 analysis pipeline smoke test", "scripts/fb_tc_expansion2_analysis.py", "pure", ["--self-test"]),
    ("Figure 1: uncertainty decomposition", "scripts/fb_fig1_uncertainty_decomposition.py", "pure"),
    ("Figure 2: audit-budget curve", "scripts/fb_fig2_audit_budget_curve.py", "pure"),
    ("Figure 3: identified-set geometry", "scripts/fb_fig3_identified_set_geometry.py", "pure"),
    ("Figure 4: scorer-choice disagreement", "scripts/fb_fig4_scorer_choice_disagreement.py", "pure"),
    ("Figure 5: worst-case sensitivity", "scripts/fb_fig5_worst_case_sensitivity.py", "pure"),
    ("Figure 6: flip budget / ranking preservation", "scripts/fb_fig6_flip_budget.py", "pure"),
    ("Figure 7: conceptual framework (schematic, no data)", "scripts/fb_fig7_conceptual_framework.py", "pure"),
    # Steps above are the pre-rebuild pipeline, kept as the audit trail
    # (CORE_ESTIMAND_AUDIT.md). The rebuilt paper uses only the steps below.
    ("REBUILD: core estimand audit (algebra, simulation, old-vs-new)", "scripts/fb_core_estimand_audit.py", "pure"),
    ("REBUILD: 458-row allocation under corrected estimands", "scripts/fb_458_redesign.py", "pure"),
    ("REBUILD: paper numbers (C1-C4)", "scripts/fb_rebuild_analysis.py", "pure", ["1000"]),
    ("REAUDIT: budget curves, allocation rules, mechanism diagnostics", "scripts/fb_reaudit.py", "pure"),
    ("REAUDIT: two-verifier identification + targeted-audit projections", "scripts/fb_joint_verifier.py", "pure"),
    ("REBUILD: figures A-D", "scripts/fb_rebuild_figures.py", "pure"),
    ("REBUILD: numbers.tex + generated tables", "scripts/fb_rebuild_numbers.py", "pure"),
]


if __name__ == "__main__":
    print("=" * 70)
    print("Full reproducibility pipeline -- canonical chain, clean subprocess per step")
    print("=" * 70)

    results = []
    for entry in STEPS:
        name, script, kind = entry[0], entry[1], entry[2]
        extra_args = entry[3] if len(entry) > 3 else []
        t0 = time.time()
        proc = subprocess.run([sys.executable, script] + extra_args, capture_output=True, text=True, timeout=2400)
        elapsed = time.time() - t0
        ok = proc.returncode == 0
        results.append({"name": name, "script": script, "kind": kind, "ok": ok, "elapsed_s": round(elapsed, 1)})
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] ({kind:<12}) {name} ({elapsed:.1f}s)")
        if not ok:
            print(f"    stderr (last 500 chars): {proc.stderr[-500:]}")

    n_pass = sum(1 for r in results if r["ok"])
    print(f"\n{'='*70}")
    print(f"{n_pass}/{len(results)} steps passed")
    n_network = sum(1 for r in results if r["kind"] == "network")
    n_human = sum(1 for r in results if r["kind"] == "human-label")
    print(f"({n_network} require network + local HF token, {n_human} require human-labeled "
          f"CSVs already committed under labeling/, {len(results)-n_network-n_human} are pure "
          f"computation from data already on disk)")

    if n_pass < len(results):
        print("\nNOT fully reproducible end-to-end on this run -- see FAIL entries above.")
        sys.exit(1)
    else:
        print("\nFull chain reproduces cleanly end-to-end on this machine.")
