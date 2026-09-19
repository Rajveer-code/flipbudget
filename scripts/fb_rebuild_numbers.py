"""Write manuscript/latex/numbers.tex (every reported number as a macro) and the
generated appendix tables, from results/flipbudget/rebuild_results.json and
results/flipbudget/core_estimand_audit.json. No hand-typed numbers."""
import json

BS = chr(92)  # backslash, kept out of string literals on purpose
NL = chr(10)

R = json.load(open("results/flipbudget/rebuild_results.json"))
c1, pw = R["C1_census"], R["pairwise"]
mm, loo = R["C2_common_mechanism"], R["C2_common_mechanism_without_command_r"]
pm = R["per_model"]
curve = {c["n_per_stratum"]: c for c in R["C3_sizing"]["curve"]}
law = {round(x["a"], 2): x for x in R["C3_sizing"]["crossover_law"]}
pp, jt, ie = pw["per_parameter_95"], pw["joint_95_sidak"], pw["joint_95_indeterminate_as_error"]


def pct(x, d=2):
    return f"{100 * x:.{d}f}" + BS + "%"


def thousands(n):
    return f"{n:,}".replace(",", "{,}")


def p(x):
    return "<0.001" if x < 0.001 else f"{x:.3f}"


yi9 = next(x for x in pm if x["model"].endswith("Yi-1.5-9B-Chat"))
M = {
    "NRows": thousands(c1["n_rows"]), "NDisagree": str(c1["n_disagree"]),
    "DisRate": pct(c1["rate"]), "DisLo": pct(c1["wilson95"][0]), "DisHi": pct(c1["wilson95"][1]),
    "DisMin": pct(c1["model_rate_min"]), "DisMax": pct(c1["model_rate_max"]),
    "SbOnly": str(c1["sb_credited_em_not"]), "EmOnly": str(c1["em_credited_sb_not"]),
    "NModels": str(pp["n_models"]), "NPairs": str(pp["n_pairs"]),
    "ResPP": str(pp["n_resolved"]), "ResJoint": str(jt["n_resolved"]), "ResIndet": str(ie["n_resolved"]),
    "ResSampling": str(pp["n_resolved_by_sampling_alone"]),
    "WAuditJoint": f"{jt['median_w_audit']:.2f}", "WAuditPP": f"{pp['median_w_audit']:.2f}",
    "WSampling": f"{pp['median_w_sampling']:.3f}",
    "RatioPP": f"{pp['median_ratio']:.1f}", "RatioJoint": f"{jt['median_ratio']:.1f}",
    "FalseCredits": str(R["C2_heterogeneity_q"]["false_credits"]),
    "NCredAud": str(R["C2_heterogeneity_q"]["n_credited_audited"]),
    "FalseMiss": str(R["C2_heterogeneity_q"]["false_miss_total"]),
    "NWrongAud": str(R["C2_heterogeneity_q"]["n_wrong_audited"]),
    "AlphaHat": f"{mm['alpha_hat']:.4f}", "AlphaLo": f"{mm['alpha_95_profile'][0]:.4f}",
    "AlphaHi": f"{mm['alpha_95_profile'][1]:.4f}", "AlphaFeas": f"{mm['alpha_feasible_max']:.4f}",
    "LR": f"{mm['LR_vs_saturated']:.1f}", "LRp": p(mm["bootstrap_p"]),
    "LRlooStat": f"{loo['LR_vs_saturated']:.1f}", "LRloop": p(loo["bootstrap_p"]),
    "IndetCred": str(sum(x["indet_cred"] for x in pm)), "IndetWrong": str(sum(x["indet_wrong"] for x in pm)),
    "YiNineIndet": str(yi9["indet_cred"]), "YiNineCred": str(yi9["n_q"] + yi9["indet_cred"]),
    "NstarLow": str(law[0.35]["n_star_exact"]), "NstarMid": str(law[0.2]["n_star_exact"]),
    "NstarHigh": str(law[0.05]["n_star_exact"]),
    "CurveFifty": f"{curve[50]['pct_resolved']:.0f}" + BS + "%",
    "CurveHundred": f"{curve[100]['pct_resolved']:.0f}" + BS + "%",
    "CurveTwoHundred": f"{curve[200]['pct_resolved']:.0f}" + BS + "%",
    "LabelsFifty": thousands(curve[50]["labels_total"]),
    "LabelsHundred": thousands(curve[100]["labels_total"]),
    "LabelsTwoHundred": thousands(curve[200]["labels_total"]),
    "SamplingCeiling": f"{curve[50]['pct_resolved_by_sampling_alone']:.1f}" + BS + "%",
    "NBoot": str(R["n_boot"]),
}
J = json.load(open("results/flipbudget/joint_verifier_results.json"))
JI, JD = J["as_incorrect"], J["drop"]
A = json.load(open("results/flipbudget/reaudit_results.json"))
cells = JI["audit_cells"]
from scipy.stats import beta as _Beta  # noqa: E402

H = {h["L"]: h for h in JI["hetero"]}
DES = {d["design"]: d for d in JI["designs"]["p10~Beta(audit),p01~U(0,1)"]}
DES_ALL = [d for v in JI["designs"].values() for d in v]
NP = {x["labels_total"]: x for x in JI["nonparametric_projection"]}
np_full = next(x for x in JI["nonparametric_projection"] if x["combined"] >= JI["shared"]["combined_resolved"])
cen_miss = JI["census_projection"]["not_resolved"]
cur_curve = {c["mult"]: c for c in A["budget"]["curves"]["heterogeneous_posterior|width_optimal"]}
plus = A["budget"]["plus_458"]
plus_vals = [100 * v[r]["median"] for v in plus.values() for r in v]
loo = A["mechanism"]["leave_one_out"]
loo_other = [v for k, v in loo.items() if "command-r-v01" not in k]
conc_err = cells["11"]["n"] - cells["11"]["x_correct"] + cells["00"]["x_correct"]
conc_n = cells["11"]["n"] + cells["00"]["n"]


def pct0(x):
    return f"{100 * x:.0f}" + BS + "%"


def design_range(name, key):
    vals = [d[key] for d in DES_ALL if d["design"] == name]
    return f"{min(vals):.0f}", f"{max(vals):.0f}"


M.update({
    "SingleComb": str(J["single_verifier_combined"]), "Ceiling": str(J["sampling_ceiling"]),
    "CeilingSim": str(J["sampling_ceiling_simultaneous"]),
    "JointAudit": str(JI["shared"]["audit_resolved"]), "JointComb": str(JI["shared"]["combined_resolved"]),
    "JointSim": str(JI["shared_simultaneous"]["combined_resolved"]),
    "JointCombDrop": str(JD["shared"]["combined_resolved"]),
    "HetOne": str(H[1]["combined"]), "HetTwo": str(H[2]["combined"]), "HetThree": str(H[3]["combined"]),
    "HetFive": str(H[5]["combined"]), "HetTen": str(H[10]["combined"]),
    "NoPool": str(JI["per_model_concordant"]["combined_resolved"]),
    "PooledDisComb": str(JI["pooled_dis"]["combined_resolved"]),
    "CensusComb": str(JI["census_projection"]["combined_resolved"]),
    "CensusGapShrink": str(sum(x["sampling_alone_resolves"] for x in cen_miss)),
    "CensusGapShrinkCmdr": str(sum(x["sampling_alone_resolves"] and "c4ai-command-r-v01" in x["pair"] for x in cen_miss)),
    "JointWidth": f"{JI['shared']['median_width']:.3f}",
    "NPThreeK": str(NP[3400]["combined"]), "NPLabelsFull": thousands(np_full["labels_total"]),
    "DesUniform": f"{DES['uniform']['median']:.0f}", "DesOneVer": f"{DES['one_verifier']['median']:.0f}",
    "DesConcOnly": f"{DES['concordant_only']['median']:.0f}",
    "DesBalanced": f"{DES['balanced_check']['median']:.0f}",
    "DesBalancedLo": f"{DES['balanced_check']['p10']:.0f}", "DesBalancedHi": f"{DES['balanced_check']['p90']:.0f}",
    "DesBalancedMin": design_range("balanced_check", "median")[0], "DesBalancedMax": design_range("balanced_check", "median")[1],
    "DesProp": f"{DES['prop_disagreement_plus_check']['median']:.0f}",
    "DesFull": f"{DES['full_disagreement']['median']:.0f}",
    "DesFullMin": design_range("full_disagreement", "median")[0], "DesFullMax": design_range("full_disagreement", "median")[1],
    "PowBalanced": pct0(DES["balanced_check"]["falsification_power_rho10_median"]),
    "PowBalancedMin": pct0(DES["balanced_check"]["falsification_power_rho10_min"]),
    "PowProp": pct0(DES["prop_disagreement_plus_check"]["falsification_power_rho10_median"]),
    "PowPropMin": pct0(DES["prop_disagreement_plus_check"]["falsification_power_rho10_min"]),
    "PowFull": pct0(DES["full_disagreement"]["falsification_power_rho10_median"]),
    "PowFullMin": pct0(DES["full_disagreement"]["falsification_power_rho10_min"]),
    "NRep": str(J["n_rep"]),
    "ConcUpper": f"{100 * _Beta.ppf(0.975, conc_err + 1, conc_n - conc_err):.1f}" + BS + "%",
    "ElevenUpper": f"{100 * _Beta.ppf(0.975, 2, cells['11']['n'] - 1):.1f}" + BS + "%",
    "ZeroUpper": f"{100 * _Beta.ppf(0.975, 1, cells['00']['n']):.1f}" + BS + "%",
    "LOOCmdrP": f"{loo['CohereForAI/c4ai-command-r-v01']['bootstrap_p']:.2f}",
    "LOOOtherPLo": f"{min(v['bootstrap_p'] for v in loo_other):.3f}",
    "LOOOtherPHi": f"{max(v['bootstrap_p'] for v in loo_other):.3f}",
    "CellElevenX": str(cells["11"]["x_correct"]), "CellElevenN": str(cells["11"]["n"]),
    "CellTenX": str(cells["10"]["x_correct"]), "CellTenN": str(cells["10"]["n"]),
    "CellTenDet": str(JD["audit_cells"]["10"]["n"]),
    "CellZeroOneX": str(cells["01"]["x_correct"]), "CellZeroOneN": str(cells["01"]["n"]),
    "CellZeroX": str(cells["00"]["x_correct"]), "CellZeroN": str(cells["00"]["n"]),
    "ConcErr": str(conc_err), "ConcN": str(conc_n),
    "ScorerFlips": str(A["why"]["scorer_choice_order_flips"]),
    "ScorerFlipsSig": str(A["why"]["scorer_choice_flips_both_sampling_significant"]),
    "ScorerFlipsCmdr": str(sum("command-r-v01" in " ".join(p) for p in A["why"]["scorer_choice_flip_pairs_significant"])),
    "PointFlips": str(A["why"]["point_estimate_order_flips_vs_a_sb"]),
    "RShare": f"{100 * A['why']['share_width_from_r']:.0f}" + BS + "%",
    "CurTotal": str(A["budget"]["current_total_labels"]),
    "CurveEight": f"{100 * cur_curve[8]['median']:.0f}" + BS + "%", "LabelsEight": thousands(cur_curve[8]["labels"]),
    "CurveSixteen": f"{100 * cur_curve[16]['median']:.0f}" + BS + "%", "LabelsSixteen": thousands(cur_curve[16]["labels"]),
    "PlusLo": f"{min(plus_vals):.0f}" + BS + "%", "PlusHi": f"{max(plus_vals):.0f}" + BS + "%",
    "CmdrLR": f"{A['mechanism']['per_model_LR_contribution']['CohereForAI/c4ai-command-r-v01']:.1f}",
    "LOOLo": f"{min(v['LR'] for v in loo_other):.1f}", "LOOHi": f"{max(v['LR'] for v in loo_other):.1f}",
})

# reversal table: the orderings that flip between the two verifiers
pmc = JI["per_model_cells"]


def disagree_evidence(m):
    c = pmc.get(m, {})
    x10, n10 = c.get("10", [0, 0])
    return f"{x10}/{n10}"


def _s(m):
    return m.split('/')[-1].replace('_', BS + '_')


rev_rows = []
for d in A["why"]["scorer_choice_flip_detail"]:
    m1, m2 = d["pair"]
    hi_sb = m1 if d["a_sb"][0] > d["a_sb"][1] else m2
    hi_em = m1 if d["a_em"][0] > d["a_em"][1] else m2
    sig = ("both" if d["sig_sb"] and d["sig_em"] else ("em only" if d["sig_em"] else ("sb only" if d["sig_sb"] else "neither")))
    rev_rows.append(f"{_s(m1)} vs {_s(m2)} & {_s(hi_sb)} & {_s(hi_em)} & {sig} & "
                    f"{disagree_evidence(m1)} ; {disagree_evidence(m2)}")
with open("manuscript/latex/numbers.tex", "w", encoding="utf-8") as f:
    f.write("% GENERATED by scripts/fb_rebuild_numbers.py -- do not edit by hand." + NL)
    for k, v in M.items():
        f.write(BS + "newcommand{" + BS + "n" + k + "}{" + v + "}" + NL)


def short(m):
    return m.split("/")[-1].replace("_", BS + "_")


def tex(rows, cols, header):
    out = [BS + "begin{tabular}{@{}" + cols + "@{}}", BS + "toprule", header + " " + BS * 2, BS + "midrule"]
    out += [r + " " + BS * 2 for r in rows]
    return NL.join(out + [BS + "bottomrule", BS + "end{tabular}"]) + NL


hdr = ("Model & $a_m$ & false cr./aud. & false rej./aud. & indet. (cr./rej.) & $" + BS + "hat A^"
       + BS + "ast_m$ & 95" + BS + "% set")
rows = [f"{short(x['model'])} & {x['a_sb']:.3f} & {x['x_q']}/{x['n_q']} & {x['x_r']}/{x['n_r']} & "
        f"{x['indet_cred']}/{x['indet_wrong']} & {x['A_point']:.3f} & [{x['A_lo']:.2f}, {x['A_hi']:.2f}]" for x in pm]
open("manuscript/latex/tab_models.tex", "w", encoding="utf-8").write(tex(rows, "lrrrrrc", hdr))

S = json.load(open("results/flipbudget/core_estimand_audit.json"))["simulation"]
names = {"typical": "typical", "low_acc": "low accuracy", "zero_acc_model": "zero accuracy",
         "high_error": "high error", "perfect_scorer": "perfect verifier"}
eq = "Eq.~(" + BS + "ref{eq:identity})"
hdr = ("Scenario ($A^" + BS + "ast," + BS + "alpha," + BS + "beta$) & bias, " + eq
       + " & bias, plug-in & cover, " + eq + " & cover, plug-in & empty, plug-in")
rows = []
for k, v in S.items():
    ob = "---" if v["old_bias"] is None else f"{v['old_bias']:+.3f}"
    oc = "---" if v["old_coverage_among_nonempty"] is None else f"{v['old_coverage_among_nonempty']:.3f}"
    rows.append(f"{names[k]} ({v['A']}, {v['alpha']}, {v['beta']}) & {v['pv_bias']:+.4f} & {ob} & "
                f"{v['pv_coverage']:.3f} & {oc} & {v['old_empty_rate']:.2f}")
open("manuscript/latex/tab_sim.tex", "w", encoding="utf-8").write(tex(rows, "lccccc", hdr))
SOURCE = {  # macro prefix -> JSON block in rebuild_results.json
    "NRows": "C1_census", "NDisagree": "C1_census", "Dis": "C1_census", "SbOnly": "C1_census",
    "EmOnly": "C1_census", "NModels": "pairwise.per_parameter_95", "NPairs": "pairwise.per_parameter_95",
    "ResPP": "pairwise.per_parameter_95", "ResSampling": "pairwise.per_parameter_95",
    "WAuditPP": "pairwise.per_parameter_95", "WSampling": "pairwise.per_parameter_95",
    "RatioPP": "pairwise.per_parameter_95", "ResJoint": "pairwise.joint_95_sidak",
    "WAuditJoint": "pairwise.joint_95_sidak", "RatioJoint": "pairwise.joint_95_sidak",
    "ResIndet": "pairwise.joint_95_indeterminate_as_error", "FalseCredits": "C2_heterogeneity_q",
    "NCredAud": "C2_heterogeneity_q", "FalseMiss": "C2_heterogeneity_q", "NWrongAud": "C2_heterogeneity_q",
    "Alpha": "C2_common_mechanism", "LRloo": "C2_common_mechanism_without_command_r",
    "LR": "C2_common_mechanism", "Indet": "per_model (sum)", "YiNine": "per_model (Yi-1.5-9B-Chat)",
    "Nstar": "C3_sizing.crossover_law", "Curve": "C3_sizing.curve", "Labels": "C3_sizing.curve",
    "SamplingCeiling": "C3_sizing.curve", "NBoot": "n_boot",
    "Single": "joint_verifier_results.json", "Ceiling": "joint_verifier_results.json",
    "Joint": "joint_verifier_results.json", "Census": "joint_verifier_results.json",
    "Tgt": "joint_verifier_results.json (disagreement_targeted)", "Cell": "joint_verifier_results.json (audit_cells)",
    "Conc": "joint_verifier_results.json (audit_cells)", "Scorer": "reaudit_results.json (why)",
    "Point": "reaudit_results.json (why)", "RShare": "reaudit_results.json (why)",
    "CurTotal": "reaudit_results.json (budget)", "CurveEight": "reaudit_results.json (budget)",
    "CurveSixteen": "reaudit_results.json (budget)", "LabelsEight": "reaudit_results.json (budget)",
    "LabelsSixteen": "reaudit_results.json (budget)", "Plus": "reaudit_results.json (budget.plus_458)",
    "Cmdr": "reaudit_results.json (mechanism)", "LOO": "reaudit_results.json (mechanism)",
    "Het": "joint_verifier_results.json (hetero)", "NoPool": "joint_verifier_results.json (per_model_concordant)",
    "PooledDis": "joint_verifier_results.json (pooled_dis)", "NP": "joint_verifier_results.json (nonparametric_projection)",
    "Des": "joint_verifier_results.json (designs; simulated)", "Pow": "joint_verifier_results.json (designs; falsification power)",
    "NRep": "joint_verifier_results.json", "Eleven": "joint_verifier_results.json (audit_cells; exact CP bound)",
    "Zero": "joint_verifier_results.json (audit_cells; exact CP bound)",
}


def source(k):
    return next(v for pre, v in sorted(SOURCE.items(), key=lambda kv: -len(kv[0])) if k.startswith(pre))


ledger = ["# Claim ledger (GENERATED by scripts/fb_rebuild_numbers.py -- do not edit)", "",
          "Every number in the rebuilt manuscript is a macro in `manuscript/latex/numbers.tex`.",
          "Sources under `results/flipbudget/`: `rebuild_results.json` (`scripts/fb_rebuild_analysis.py`), `joint_verifier_results.json` (`scripts/fb_joint_verifier.py`), `reaudit_results.json` (`scripts/fb_reaudit.py`).",
          "Appendix tables: `tab_models.tex` (key `per_model`), `tab_sim.tex`",
          "(`results/flipbudget/core_estimand_audit.json`, key `simulation`, from `scripts/fb_core_estimand_audit.py`).",
          "Inter-rater kappas in Section 4: `results/analysis/mathhard_human_margins.json`, key `inter_rater`.",
          "", "| Macro | Value | JSON block |", "|---|---|---|"]
ledger += [f"| `{BS}n{k}` | {v} | `{source(k)}` |" for k, v in M.items()]
open("CLAIM_LEDGER.md", "w", encoding="utf-8").write(NL.join(ledger) + NL)
print(f"wrote {len(M)} macros, tab_models.tex, tab_sim.tex, CLAIM_LEDGER.md")

rev_hdr = "Pair & higher by score" + BS + "_boxed & higher by exact" + BS + "_match & sampling-clear & audited sb-only correct/n"
open("manuscript/latex/tab_reversals.tex", "w", encoding="utf-8").write(tex(rev_rows, "lllcc", rev_hdr))
print("wrote tab_reversals.tex")
