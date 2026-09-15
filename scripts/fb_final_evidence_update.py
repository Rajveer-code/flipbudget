"""ONE-COMMAND pipeline for when the 458-row human labels return (item 11 of
the latest directive). Runs the preregistered analysis, regenerates the
affected figures, and writes a dated validation report -- so analysis C's
numbers drop into the manuscript without hand-editing.

Deliberately does NOT overwrite any existing "PENDING" text in the
manuscript automatically (a hand-edit of manuscript/MANUSCRIPT_DRAFT.md's
[PENDING] markers, guided by this script's own printed output, is the
intended final step -- an automatic text-replace into prose risks a
silent, unreviewed wording change, which is a worse failure mode than one
extra manual copy-paste).

Run: python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
"""
import argparse
import datetime
import json
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="labeling/tc_expansion2_l1.csv")
    ap.add_argument("--i-confirm-human-labeled", action="store_true")
    args = ap.parse_args()

    if not args.i_confirm_human_labeled:
        print("Refusing to run without --i-confirm-human-labeled.")
        print("This flag exists so a human consciously confirms the CSV was")
        print("independently, manually labeled -- not to be passed by habit.")
        sys.exit(1)

    steps = []

    print("=" * 78)
    print("STEP 1: quality gate + alpha/beta/reconciliation recompute")
    print("=" * 78)
    r1 = subprocess.run([sys.executable, "scripts/fb_tc_expansion2_analysis.py",
                          "--csv", args.csv, "--i-confirm-human-labeled"],
                         capture_output=True, text=True)
    print(r1.stdout[-3000:])
    if r1.returncode != 0:
        print("STOPPED: quality gate or analysis failed. See output above.")
        print(r1.stderr[-2000:])
        sys.exit(1)
    steps.append({"step": "fb_tc_expansion2_analysis.py", "ok": True})

    print("\n" + "=" * 78)
    print("STEP 2: regenerate figures that depend on this data")
    print("=" * 78)
    for fig_script in ["scripts/fb_fig1_uncertainty_decomposition.py",
                        "scripts/fb_fig2_audit_budget_curve.py"]:
        r = subprocess.run([sys.executable, fig_script], capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"  [{'OK' if ok else 'FAILED'}] {fig_script}")
        steps.append({"step": fig_script, "ok": ok})
        # Note: neither figure currently reads analysis-C-specific output;
        # this step is a placeholder wired for when a fig3 (exact_match's own
        # decomposition) is added -- listed explicitly rather than silently
        # skipped, so the gap is visible, not hidden.

    print("\n" + "=" * 78)
    print("STEP 3: package tests (confirm nothing broke)")
    print("=" * 78)
    r3 = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], capture_output=True, text=True)
    print(r3.stdout[-1500:])
    steps.append({"step": "pytest tests/", "ok": r3.returncode == 0})

    with open("results/flipbudget/tc_expansion2_analysis.json") as f:
        analysis = json.load(f)

    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "input_csv": args.csv,
        "steps": steps,
        "quality_gate_passed": analysis["gate_passed"],
        "quality_gate_red_flags": analysis["quality_gate"]["red_flags"],
        "score_boxed_alpha_beta": analysis["score_boxed_alpha_beta"],
        "exact_match_alpha_beta": analysis["exact_match_alpha_beta"],
        "reconciliation_by_scorer": analysis["reconciliation_by_scorer"],
        "manual_step_still_required": (
            "Replace every [PENDING -- human audit] marker in "
            "manuscript/MANUSCRIPT_DRAFT.md's Section 7 (Results) with the "
            "numbers in this report -- deliberately not automated, see "
            "this script's own docstring."
        ),
    }
    out_path = f"results/flipbudget/final_validation_report_{datetime.date.today().isoformat()}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 78)
    print(f"DONE. Report: {out_path}")
    print("=" * 78)
    print(f"Quality gate passed: {report['quality_gate_passed']}")
    if not report["quality_gate_passed"]:
        print("Red flags:", report["quality_gate_red_flags"])
    print(f"\nManual step still required: {report['manual_step_still_required']}")


if __name__ == "__main__":
    main()
