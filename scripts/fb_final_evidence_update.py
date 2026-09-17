"""ONE-COMMAND pipeline for when the 458-row human labels return. Runs the
preregistered analysis, regenerates every figure/table that depends on it,
and writes two machine-readable artifacts plus a dated validation report --
so analysis C's numbers can be dropped into the manuscript by hand, guided
by an exact checklist, rather than by re-deriving where they go.

Deliberately does NOT overwrite any existing "PENDING" text in the
manuscript automatically -- a hand-edit of manuscript/MANUSCRIPT_DRAFT.md's
[PENDING] markers, guided by results_to_insert.json and the printed
checklist, is the intended final step. An automatic text-replace into prose
risks a silent, unreviewed wording change, which is a worse failure mode
than one extra manual copy-paste per location.

Outputs (all under results/flipbudget/):
  - tc_expansion2_analysis.json          (unchanged name, the raw recompute)
  - results_to_insert.json               (NEW: exact replacement text per
                                           manuscript location, keyed by a
                                           short id, both the current
                                           [PENDING] snippet and the
                                           computed replacement)
  - final_validation_report_<date>.json  (dated run record: steps, quality
                                           gate, environment, commit hash)

Run: python scripts/fb_final_evidence_update.py --csv labeling/tc_expansion2_l1.csv --i-confirm-human-labeled
"""
import argparse
import datetime
import json
import subprocess
import sys


def git_commit_hash():
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def build_results_to_insert(analysis):
    """One entry per [PENDING] location in manuscript/MANUSCRIPT_DRAFT.md
    (enumerated by `grep -n PENDING manuscript/MANUSCRIPT_DRAFT.md` on
    2026-09-17 -- re-check that list if the manuscript has been restructured
    since). Each entry names the exact current snippet to find and the
    exact replacement text to substitute by hand, built from real computed
    numbers -- never a template with blanks."""
    em = analysis["exact_match_alpha_beta"]
    c = analysis.get("analysis_c_ratio")
    entries = []

    def fmt_pct(x):
        return f"{100*x:.2f}%" if x is not None else "[unavailable -- see quality_gate red_flags]"

    alpha_txt = fmt_pct(em.get("alpha"))
    beta_txt = fmt_pct(em.get("beta"))

    entries.append({
        "id": "abstract_pending_clause",
        "manuscript_line_anchor": "`[PENDING — human audit]`: the verifier's *other* live scorer",
        "instruction": "Extend the abstract's final sentence with the now-available numbers, or "
                       "replace it if analysis C changes the headline framing.",
        "replacement_data": {"exact_match_alpha": alpha_txt, "exact_match_beta": beta_txt,
                              "analysis_c_ratio_median": c["ratio_median"] if c else None,
                              "analysis_c_pct_dominant": c["pct_dominant"] if c else None},
    })
    entries.append({
        "id": "section6_second_audit_pending",
        "manuscript_line_anchor": "power-justified (n=300 for a first `exact_match`-α estimate; "
                                   "n=60, 65–89% power, for a scorer-disagreement-resolution "
                                   "comparison). `[PENDING — human audit]`.",
        "instruction": "Replace the trailing `[PENDING — human audit]` with the actual outcome: "
                       "report n_credited/n_false_credit and n_wrong/n_false_miss actually observed.",
        "replacement_data": {"n_credited": em.get("n_credited"), "n_false_credit": em.get("n_false_credit"),
                              "n_wrong": em.get("n_wrong"), "n_false_miss": em.get("n_false_miss")},
    })
    entries.append({
        "id": "table_7_1_analysis_c_row",
        "manuscript_line_anchor": "| **C** (`exact_match`'s own) | `exact_match` accuracy + "
                                   "`exact_match`-audited (α,β) | `[PENDING — human audit]` | "
                                   "`[PENDING]` | `[PENDING]` |",
        "instruction": "Replace the three [PENDING] cells with ratio / % dominant / n valid.",
        "replacement_data": c if c else "analysis_c_ratio is null -- see quality_gate red_flags "
                                         "or the printed 'genuinely undetermined' note",
    })
    entries.append({
        "id": "section7_4_heading",
        "manuscript_line_anchor": "worst-case bound established, `exact_match`'s own audit `[PENDING]`",
        "instruction": "Update the section heading to state the audit is now established, not pending.",
        "replacement_data": None,
    })
    entries.append({
        "id": "section7_4_body_pending_clause",
        "manuscript_line_anchor": "`[PENDING — human audit]`: `exact_match`'s actual (not "
                                   "worst-case-bounded) audited α, β, and its own fully "
                                   "self-consistent identification result (analysis C, §7.1).",
        "instruction": "Replace with the actual alpha/beta and a one-sentence comparison against "
                       "the worst-case bound (0.166) already reported -- does the real value land "
                       "inside [2.38%,26.73%] as assumed, or outside it? State plainly either way.",
        "replacement_data": {"exact_match_alpha": alpha_txt, "exact_match_beta": beta_txt,
                              "worst_case_bound_was": "[2.38%, 26.73%]",
                              "actual_within_worst_case_bound":
                                  (em.get("alpha") is not None and 0.0238 <= em["alpha"] <= 0.2673)},
    })
    entries.append({
        "id": "limitations_item_1",
        "manuscript_line_anchor": "`exact_match`'s own audited α/β do not yet exist — analysis C "
                                   "is the single largest open piece of this paper, "
                                   "`[PENDING — human audit]`, 458 rows, preregistered and in progress.",
        "instruction": "This limitation is now resolved -- either delete the item and renumber "
                       "items 2-10, or rewrite it to state what WAS found (do not just delete "
                       "silently; a paper that once disclosed a gap and quietly removes the "
                       "disclosure without saying what filled it reads worse than one that updates "
                       "it explicitly).",
        "replacement_data": None,
    })
    return entries


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
    print("STEP 1: quality gate + alpha/beta/reconciliation/analysis-C recompute")
    print("=" * 78)
    r1 = subprocess.run([sys.executable, "scripts/fb_tc_expansion2_analysis.py",
                          "--csv", args.csv, "--i-confirm-human-labeled"],
                         capture_output=True, text=True)
    print(r1.stdout[-4000:])
    if r1.returncode != 0:
        print("STOPPED: quality gate or analysis failed. See output above.")
        print(r1.stderr[-2000:])
        sys.exit(1)
    steps.append({"step": "fb_tc_expansion2_analysis.py", "ok": True})

    with open("results/flipbudget/tc_expansion2_analysis.json") as f:
        analysis = json.load(f)

    if not analysis["gate_passed"]:
        print("\nSTOPPED: quality gate did not pass. Not proceeding to figures/tables/report.")
        print("Red flags:", analysis["quality_gate"]["red_flags"])
        print("This mirrors the two prior AI-generated-label incidents (see")
        print("TC_EXPANSION2_LABELING_QUALITY_ISSUE.md) -- do not override without manually")
        print("confirming independent human authorship of every flagged row.")
        sys.exit(1)

    print("\n" + "=" * 78)
    print("STEP 2: regenerate figures")
    print("=" * 78)
    for fig_script in [f"scripts/fb_fig{i}_{name}.py" for i, name in [
            (1, "uncertainty_decomposition"), (2, "audit_budget_curve"),
            (3, "identified_set_geometry"), (4, "scorer_choice_disagreement"),
            (5, "worst_case_sensitivity"), (6, "flip_budget"), (7, "conceptual_framework")]]:
        r = subprocess.run([sys.executable, fig_script], capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"  [{'OK' if ok else 'FAILED'}] {fig_script}")
        steps.append({"step": fig_script, "ok": ok})

    print("\n" + "=" * 78)
    print("STEP 3: regenerate tables")
    print("=" * 78)
    r_tab = subprocess.run([sys.executable, "scripts/fb_build_tables.py"], capture_output=True, text=True)
    print(r_tab.stdout[-1500:])
    steps.append({"step": "fb_build_tables.py", "ok": r_tab.returncode == 0})

    print("\n" + "=" * 78)
    print("STEP 4: package tests (confirm nothing broke)")
    print("=" * 78)
    r3 = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"], capture_output=True, text=True)
    print(r3.stdout[-1500:])
    steps.append({"step": "pytest tests/", "ok": r3.returncode == 0})

    print("\n" + "=" * 78)
    print("STEP 5: build results_to_insert.json + manuscript-location checklist")
    print("=" * 78)
    entries = build_results_to_insert(analysis)
    with open("results/flipbudget/results_to_insert.json", "w") as f:
        json.dump({"generated_at": datetime.datetime.now().isoformat(), "entries": entries}, f, indent=2)
    print("Written to results/flipbudget/results_to_insert.json")
    print("\nMANUSCRIPT LOCATIONS REQUIRING A MANUAL EDIT (manuscript/MANUSCRIPT_DRAFT.md):")
    for e in entries:
        print(f"  [{e['id']}] find: \"{e['manuscript_line_anchor'][:80]}...\"")
        print(f"      -> {e['instruction']}")

    report = {
        "generated_at": datetime.datetime.now().isoformat(),
        "input_csv": args.csv,
        "git_commit": git_commit_hash(),
        "python_version": sys.version,
        "steps": steps,
        "all_steps_ok": all(s["ok"] for s in steps),
        "quality_gate_passed": analysis["gate_passed"],
        "quality_gate_red_flags": analysis["quality_gate"]["red_flags"],
        "score_boxed_alpha_beta": analysis["score_boxed_alpha_beta"],
        "exact_match_alpha_beta": analysis["exact_match_alpha_beta"],
        "reconciliation_by_scorer": analysis["reconciliation_by_scorer"],
        "analysis_c_ratio": analysis.get("analysis_c_ratio"),
        "results_to_insert_path": "results/flipbudget/results_to_insert.json",
        "manual_step_still_required": (
            "Open results_to_insert.json and, for each entry, find manuscript_line_anchor in "
            "manuscript/MANUSCRIPT_DRAFT.md and apply the change per its instruction -- "
            "deliberately not automated, see this script's own docstring."
        ),
    }
    out_path = f"results/flipbudget/final_validation_report_{datetime.date.today().isoformat()}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 78)
    print(f"DONE. Report: {out_path}")
    print("=" * 78)
    print(f"All steps OK: {report['all_steps_ok']}")
    print(f"Quality gate passed: {report['quality_gate_passed']}")
    if not report["quality_gate_passed"]:
        print("Red flags:", report["quality_gate_red_flags"])
    print(f"\nManual step still required: {report['manual_step_still_required']}")


if __name__ == "__main__":
    main()
