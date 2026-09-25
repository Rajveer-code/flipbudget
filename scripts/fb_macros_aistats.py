"""G4.4 -- LaTeX macros for every number the manuscript may state, plus the claim ledger.

Each macro is read from a committed result file; none is typed here. The ledger records, for
every macro, its value and the exact file and key it came from, so a reviewer (or the author)
can trace any number in the paper back to the artifact that produced it.

Run: python scripts/fb_macros_aistats.py
Out: manuscript/aistats2027/macros.tex, CLAIM_LEDGER_AISTATS.md
"""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "flipbudget"
TEX = ROOT / "manuscript" / "aistats2027" / "macros.tex"
TMLR_TEX = ROOT / "manuscript" / "tmlr" / "macros.tex"
LEDGER = ROOT / "CLAIM_LEDGER_AISTATS.md"


def fmt(v):
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}".replace(",", "{,}")
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def main():
    cert = json.load(open(RES / "certify_results.json", encoding="utf-8"))
    prov = json.load(open(RES / "verifier_provenance.json", encoding="utf-8"))
    cov = json.load(open(RES / "coverage_table.json", encoding="utf-8"))
    amap = json.load(open(RES / "audit_k3_map.json", encoding="utf-8"))
    sim = json.load(open(RES / "certify_coverage_sim.json", encoding="utf-8"))
    front = json.load(open(RES / "g3_frontier.json", encoding="utf-8"))
    op = json.load(open(RES / "g3_operating_point.json", encoding="utf-8"))
    imp = json.load(open(RES / "g1_semantics_impact.json", encoding="utf-8"))
    tests = json.load(open(RES / "test_census.json", encoding="utf-8"))
    sens = cert["K3"]["sensitivity"]
    m17 = amap["models17"]
    HC = ROOT / "results" / "harness_census"
    prev = {r[0]: r for r in json.load(open(HC / "prevalence.json", encoding="utf-8"))["rows"]}
    light = json.load(open(HC / "census_lighteval.json", encoding="utf-8"))
    simple = json.load(open(HC / "simple_evals_census.json", encoding="utf-8"))
    valid = json.load(open(HC / "census_validation.json", encoding="utf-8"))["summary"]
    census = json.load(gzip.open(RES / "census_k3.json.gz", "rt", encoding="utf-8"))
    K3, eps0 = cert["K3"], cert["config"]["eps0_preregistered"]
    grid = {p["eps"]: p for p in K3["eps_curve"]}
    cells3 = amap["census_cells"]["k3_sympy"]["27"]
    rows = census["rows"]
    opt = next(p for p in front["points"] if p.get("is_operating_point"))
    worst_sim = max(s["audit"]["familywise_error"] for s in sim["scenarios"]
                    if s["eps_true"] >= 0 and s["eps_true"] == s["eps_analysis"])

    M = [  # (macro, value, source)
        ("NumModels", len(cov["models_kept"]), "coverage_table.json: models_kept"),
        ("NumItems", cert["config"]["n_items"], "certify_results.json: config.n_items"),
        ("NumOrderings", len(K3["eps0_pairs"]), "certify_results.json: K3.eps0_pairs"),
        ("NumVerifiers", len(K3["inputs"]["cells"][0]), "certify_results.json: K3.inputs.cells (cell width)"),
        ("NumCells", len(K3["inputs"]["cells"]), "certify_results.json: K3.inputs.cells"),
        ("NumRows", len(rows), "census_k3.json.gz: rows"),
        ("MissingRows", sum(v["n_missing"] for v in cov["per_model"].values()), "coverage_table.json: per_model"),
        ("CommonItems", cov["n_common_items"], "coverage_table.json: n_common_items"),
        # provenance
        ("EmReexecDisagree", prov["summary"]["items_em_vs_em_rec_disagree"], "verifier_provenance.json: summary"),
        ("EmReexecItems", prov["summary"]["items"], "verifier_provenance.json: summary.items"),
        ("EmAggregateMatch", prov["summary"]["subjects_em_equals_original_aggregate"], "verifier_provenance.json"),
        # only models whose results file was rescored in Feb 2025 can test the Math-Verify match
        ("MvAggregateMatch", sum(v["mv_matches_current_aggregate"] for m in prov["per_model"].values()
                                 if m["results_original_revision"] for v in m["per_subject"].values()),
         "verifier_provenance.json: per_model (rescored models only)"),
        ("NumSubjectsRescored", prov["summary"]["subjects"]
         - 7 * prov["summary"]["models_without_pre_rescoring_results"], "verifier_provenance.json: summary"),
        # cells and audit
        ("CellAgreeAll", cells3["111"], "audit_k3_map.json: census_cells.k3_sympy.27"),
        ("CellRejectAll", cells3["000"], "audit_k3_map.json: census_cells.k3_sympy.27"),
        ("RowsAnyDisagree", sum(len({r["em"], r["sb_sympy"], r["mv"]}) > 1 for r in rows), "census_k3.json.gz"),
        ("DisagreeSbEmSeventeen", amap["disagreements_17_sb_sympy_vs_em"], "audit_k3_map.json"),
        ("DisagreeSbEmSeventeenString", amap["disagreements_17_sb_string_vs_em"], "audit_k3_map.json"),
        ("AuditCorrectAgreeAll", K3["inputs"]["audit_pooled"]["111"]["x_correct"], "certify_results.json: K3.inputs"),
        ("AuditNAgreeAll", K3["inputs"]["audit_pooled"]["111"]["n"], "certify_results.json: K3.inputs"),
        ("AuditCorrectRejectAll", K3["inputs"]["audit_pooled"]["000"]["x_correct"], "certify_results.json: K3.inputs"),
        ("AuditNRejectAll", K3["inputs"]["audit_pooled"]["000"]["n"], "certify_results.json: K3.inputs"),
        # certification
        ("CertEpsZero", grid[0.0]["combined"], "certify_results.json: K3.eps_curve[eps=0]"),
        ("CertEpsZeroSim", grid[0.0]["combined_simultaneous"], "certify_results.json: K3.eps_curve[eps=0]"),
        ("CertEpsZeroAudit", grid[0.0]["audit_only"], "certify_results.json: K3.eps_curve[eps=0]"),
        ("CertPrereg", grid[eps0]["combined"], f"certify_results.json: K3.eps_curve[eps={eps0}]"),
        ("CertPreregSim", grid[eps0]["combined_simultaneous"], f"certify_results.json: K3.eps_curve[eps={eps0}]"),
        ("CertNoPooling", K3["no_pooling"]["combined_resolved"], "certify_results.json: K3.no_pooling"),
        ("CeilingEm", K3["ceiling"]["em"], "certify_results.json: K3.ceiling.em"),
        ("CeilingMv", K3["ceiling"]["mv"], "certify_results.json: K3.ceiling.mv"),
        ("CertKTwoEpsZero", cert["K2"]["eps_curve"][0]["combined"], "certify_results.json: K2.eps_curve"),
        ("CertKTwoPrereg", {p["eps"]: p for p in cert["K2"]["eps_curve"]}[eps0]["combined"],
         "certify_results.json: K2.eps_curve"),
        ("EpsPrereg", eps0, "certify_results.json: config.eps0_preregistered"),
        ("EpsRefDerived", K3["eps_reference_a"]["eps_ref_a"], "certify_results.json: K3.eps_reference_a"),
        ("BreakdownMedian", sorted(K3["breakdown_eps"].values())[len(K3["breakdown_eps"]) // 2],
         "certify_results.json: K3.breakdown_eps (median)"),
        # the Windows defect, measured
        ("AnchorStringCombined", imp["string"]["as_incorrect"]["combined_resolved"], "g1_semantics_impact.json"),
        ("AnchorSympyCombined", imp["sympy"]["as_incorrect"]["combined_resolved"], "g1_semantics_impact.json"),
        ("AnchorStringAudit", imp["string"]["as_incorrect"]["audit_resolved"], "g1_semantics_impact.json"),
        ("AnchorSympyAudit", imp["sympy"]["as_incorrect"]["audit_resolved"], "g1_semantics_impact.json"),
        # coverage simulation
        ("SimReplicates", sim["n_rep"], "certify_coverage_sim.json: n_rep"),
        ("SimWorstFwerUnderH", worst_sim, "certify_coverage_sim.json: scenarios where H holds"),
        ("SimFwerMisspecified", next(s["audit"]["familywise_error"] for s in sim["scenarios"]
                                     if s["eps_true"] == 0.02), "certify_coverage_sim.json"),
        ("SimFwerPropensityKTwo", next(s["audit"]["familywise_error"] for s in sim["scenarios"]
                                       if s["K"] == 2 and s["eps_true"] < 0 and s["eps_analysis"] == 0),
         "certify_coverage_sim.json"),
        ("SimScenarios", len(sim["scenarios"]), "certify_coverage_sim.json: scenarios"),
        ("SimMcSeAudit", sim["scenarios"][0]["audit"]["mc_se_at_nominal"],
         "certify_coverage_sim.json: audit.mc_se_at_nominal"),
        # levels, and the distribution-free sampling alternative (appendix C)
        ("AlphaAudit", cert["config"]["alpha_audit"], "certify_results.json: config.alpha_audit"),
        ("AlphaSample", cert["config"]["alpha_sampling"], "certify_results.json: config.alpha_sampling"),
        ("SidakTwoLevel", cert["K3"]["inputs"]["interval_level"],
         "certify_results.json: K3.inputs.interval_level"),
        ("CertHoeffding", cert["K3"]["sensitivity"]["sampling_hoeffding"]["combined"],
         "certify_results.json: K3.sensitivity.sampling_hoeffding.combined"),
        ("CertSamplingLegacy", cert["K3"]["sensitivity"]["sampling_legacy"]["combined"],
         "certify_results.json: K3.sensitivity.sampling_legacy.combined"),
        # numerical checks (appendix B)
        ("TestsTotal", tests["total_cases"], "test_census.json: total_cases"),
        ("TestsFunctions", tests["total_functions"], "test_census.json: total_functions"),
        ("TestsCertification", tests["named"]["certification"], "test_census.json: named.certification"),
        ("TestsManuscriptClaims", tests["named"]["manuscript_claims"],
         "test_census.json: named.manuscript_claims"),
        ("TestsAnchor", tests["named"]["regression_anchor"], "test_census.json: named.regression_anchor"),
        # registered sensitivity analyses (appendices D and E)
        ("SensMvCombined", sens["mv_reference"]["combined"],
         "certify_results.json: K3.sensitivity.mv_reference.combined"),
        ("SensMvCorrectRejectAll", sens["mv_reference"]["audit_pooled"]["000"]["x_correct"],
         "certify_results.json: K3.sensitivity.mv_reference.audit_pooled.000"),
        ("SensMvCorrectAgreeAll", sens["mv_reference"]["audit_pooled"]["111"]["x_correct"],
         "certify_results.json: K3.sensitivity.mv_reference.audit_pooled.111"),
        ("SensDropCombined", sens["indeterminate_dropped"]["combined"],
         "certify_results.json: K3.sensitivity.indeterminate_dropped.combined"),
        ("SensDropNRejectAll", sens["indeterminate_dropped"]["audit_pooled"]["000"]["n"],
         "certify_results.json: K3.sensitivity.indeterminate_dropped.audit_pooled.000"),
        ("SensStringCombined", sens["string_semantics"]["combined"],
         "certify_results.json: K3.sensitivity.string_semantics.combined"),
        ("SensStringNAgreeAll", sens["string_semantics"]["audit_pooled"]["111"]["n"],
         "certify_results.json: K3.sensitivity.string_semantics.audit_pooled.111"),
        ("SensCpCombined", sens["clopper_pearson"]["combined"],
         "certify_results.json: K3.sensitivity.clopper_pearson.combined"),
        ("SensCpPrereg", sens["clopper_pearson"]["combined_eps0"][1],
         "certify_results.json: K3.sensitivity.clopper_pearson.combined_eps0"),
        ("SensSeventeenCombined", sens["models17"]["combined"],
         "certify_results.json: K3.sensitivity.models17.combined"),
        ("NumOrderingsSeventeen", len(m17) * (len(m17) - 1) // 2, "audit_k3_map.json: models17"),
        # audit design
        ("AuditBudget", op["budget"], "g3_operating_point.json: budget"),
        ("ScreenedModels", op["F"], "g3_operating_point.json: F"),
        ("ScreenNRejectAll", op["n0_by_cell"]["000"], "g3_operating_point.json: n0_by_cell"),
        ("ScreenNAgreeAll", op["n0_by_cell"]["111"], "g3_operating_point.json: n0_by_cell"),
        ("ScreenRho", op["rho"], "g3_operating_point.json: rho"),
        ("ScreenPowerPct", round(op["power"] * 100), "g3_operating_point.json: power"),
        ("ScreenPowerRejectAll", opt["falsification"]["000"]["power_rho20"], "g3_frontier.json: operating point"),
        ("ScreenPowerAgreeAll", opt["falsification"]["111"]["power_rho20"], "g3_frontier.json: operating point"),
        ("LabelsFalsification", op["labels_falsification"], "g3_operating_point.json"),
        ("LabelsCertification", op["labels_certification"], "g3_operating_point.json"),
        ("ProjectedCertPrereg", opt["certified_uniform_eps0.01"]["median"],
         "g3_frontier.json: operating point (PROJECTED)"),
        # how widely the same design choice is made (harness census)
        ("LmEvalGenerative", prev["lm-evaluation-harness"][1], "harness_census/prevalence.json"),
        ("LmEvalCoerce", prev["lm-evaluation-harness"][2], "harness_census/prevalence.json"),
        ("LmEvalCoercePct", prev["lm-evaluation-harness"][3], "harness_census/prevalence.json"),
        ("OpenCompassGenerative", prev["OpenCompass"][1], "harness_census/prevalence.json"),
        ("OpenCompassCoerce", prev["OpenCompass"][2], "harness_census/prevalence.json"),
        ("OpenCompassCoercePct", prev["OpenCompass"][3], "harness_census/prevalence.json"),
        ("LightevalGenerative", light["n_generative"], "harness_census/census_lighteval.json"),
        ("LightevalCoerce", light["n_vulnerable"], "harness_census/census_lighteval.json"),
        ("SimpleEvalsStringMatch", simple["n_string_match_modules"], "harness_census/simple_evals_census.json"),
        ("SimpleEvalsCoerce", simple["n_vulnerable"], "harness_census/simple_evals_census.json"),
        ("CensusValidTestable", valid["vulnerable"]["n_testable"], "harness_census/census_validation.json"),
        ("CensusValidConfirmed", valid["vulnerable"]["n_agreeing_with_census"], "harness_census/census_validation.json"),
        ("CensusControlN", valid["control"]["n_sampled"], "harness_census/census_validation.json"),
        ("CensusControlClean", valid["control"]["not_vulnerable"], "harness_census/census_validation.json"),
    ]
    body = ("% Generated by scripts/fb_macros_aistats.py -- do not edit by hand.\n"
            "% Every value is read from a committed result file; see CLAIM_LEDGER_AISTATS.md.\n"
            + "".join(f"\\newcommand{{\\{name}}}{{{fmt(value)}}}\n" for name, value, _ in M))
    for out in (TEX, TMLR_TEX):  # the guard reads TEX; the TMLR build inputs TMLR_TEX
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
    with open(LEDGER, "w", encoding="utf-8") as f:
        f.write("# Claim ledger (AISTATS submission)\n\n")
        f.write("Every number the manuscript states is a macro from `manuscript/aistats2027/macros.tex`,\n"
                "generated by `scripts/fb_macros_aistats.py`. Projections are marked.\n\n")
        f.write("| macro | value | source |\n|---|---|---|\n")
        for name, value, src in M:
            tag = " **(PROJECTED)**" if "PROJECTED" in src else ""
            f.write(f"| `\\{name}` | {fmt(value)} | `{src}`{tag} |\n")
    print(f"wrote {TEX} ({len(M)} macros) and {LEDGER}")


if __name__ == "__main__":
    main()
