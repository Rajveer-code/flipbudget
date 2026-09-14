# Manuscript architecture (item 22)

Not a draft. A structure where every major claim maps to its theorem,
dataset, experiment, uncertainty estimate, falsification test, and the
reviewer objection it answers — so gaps show up before writing, not during
review. Section order follows the argument, not the chronology of when
things were discovered.

| § | Claim | Theorem/result | Dataset | Experiment | Uncertainty estimate | Falsification test | Reviewer objection answered |
|---|---|---|---|---|---|---|---|
| 1. Motivation | Reported benchmark comparisons omit a real, sometimes-dominant uncertainty source | A1/A2 (`EVIDENCE_TABLE.md`) | MATH-Hard, 27-model roster | E-A dominance study | Wilson CI on α,β; bootstrap not yet run on the corrected ratio (flagged below) | Ratio ≤1 in the majority of pairs would kill this | "Second-order correction, sampling dominates" |
| 2. Framework | Scorer Sensitivity Model (Λ-odds-bound), sharp identified sets | D1/D2 (T-A, T-H) | — (pure theory) | Symbolic + numeric verification, `fb_ta_ssm.py` | N/A (deterministic proof) | A counterexample box where the vertex theorem fails | "Ad hoc box parameterization" |
| 3. Impossibility | Design sensitivity Λ̃: some pairs unidentifiable at any benchmark size | D3 (T-B) | Same roster | `fb_tb_compound_design_sensitivity.py` | Saturation boundary derived exactly, not simulated | Λ̃ infinite for all real pairs would kill the headline | "Just collect more benchmark items" |
| 4. Correlated error | Non-differential item heterogeneity cancels in differences; differential loading does not | Props. 1-3 (`THEORY_EXTENSIONS.md` §1) | Synthetic (verified by simulation, not fit to real data — **flagged gap below**) | `fb_theory_correlated_error.py` | Closed-form Cov, matched to simulation within MC tolerance | A regime where Prop. 1's Cov formula fails simulation would kill it (none found) | "α,β constant/independent across items and models is obviously false" |
| 5. Reconciliation | On MATH-Hard, audit-estimation uncertainty dominates scorer-sensitivity uncertainty | A4, verdict B | MATH-Hard, 136 real pairs | `fb_reconcile_layers.py` | Two sanity checks (non-straddle exact match; known-straddle → [0,1]) pass | Scorer-only unresolved >> audit-only would flip the verdict | "Which uncertainty source actually matters?" |
| 6. Fix | Audit-design methodology: required-n, Neyman allocation, adaptive-vs-static bound | A5, verdict D | Same 136 pairs + `audit_design_stress_test.json`'s 6 synthetic scenarios | `fb_audit_design_analysis.py`, `fb_audit_design_stress_test.py` | Bisection for required-n; variance formulas exact, not simulated for the main result | Neyman losing to proportional in >0 stress-test scenarios would weaken this (did not happen: 0/6) | "How would I actually use this?" |
| 7. Imperfect reference | Sensitivity bound on how much human-label error would change the conclusion | §4 T-D (`THEORY_EXTENSIONS.md`) | T-C's 3-labeler 14-item overlap (100% agreement) | Analytic `q_max(η)` curve | Bound reported as a curve across η, not a point | A latent-class fit would supersede this if n were larger — explicitly stated as not yet possible | "Your human labels aren't ground truth either" |
| 8. Verification bias | Stratified-on-scorer-outcome sampling is Horvitz-Thompson-valid by design, not classical verification bias | §5 T-E (`THEORY_EXTENSIONS.md`) | Both audit designs (T-C, IFEval) | Direct check of positivity + known-π_h | N/A (design property, not estimated) | A hidden dependence of π_h on unrecorded info would break this — named as the one assumption that must hold | "Your audit sample is selected on the scorer's own output" |
| 9. T-C empirical | Real 69-trial audit: 0 scorer-wrong events; anchor-propagation effect on un-audited models | B4-B6 | MATH-Hard | `fb_tc_real_analysis.py`, `fb_tc_alpha_beta_update.py` | Binomial P(0\|~3-7%,n=69)≈11-13%; Wilson CIs throughout | Any nonzero event would have re-opened the correlation test — none observed | "Your audit is too small to mean anything" — answered honestly (it is, for the correlation question; not for the anchor-propagation finding) |
| 10. Real comparator bug | A live, platform-specific correctness bug in the standard MATH comparator | B8 (`MATH_COMPARATOR_BUG.md`) | Constructed adversarial cases + real 400+69-item audits | `fb_adversarial_suite.py`, `fb_verify_*_bug.py` | Exact (deterministic verification, not statistical) | Re-running on Linux would show `is_equiv` behaving correctly — not yet done, flagged | "Is your own tooling even correct?" — a real, previously-unasked question, now answered with evidence |
| 11. Generalization | Same discipline on IFEval: real, causally-confirmed verifier nondeterminism; small effect on rankings | C3-C5 | IFEval, same 27-model roster | `fb_ifeval_mechanism_rescan.py`, `fb_ifeval_reproducibility_check.py` | 15+5 fresh-process replicates; seeded control = 0% variance (causal, not correlational) | Large benchmark-score/ranking swings would have undercut "small effect" — none found | "One benchmark, one harness — anecdote" |
| 12. Honest limitation | Human-audit of fine-grained instruction-following failed twice; 83.2% of IFEval disagreement remains unexplained | C6-C8 | IFEval 454-item sample | Two labeling rounds, checked against the real per-instruction verifier | 89.3%, then 90.5% contradiction rate — both reported | A third, differently-scoped attempt could still resolve this — not attempted, reasons stated | "You're hiding your failures" — answered by including this section at all |
| 13. Limitations | What this project does not and cannot yet claim | §"What remains open" (`CONSOLIDATED_VERDICT.md`, `MECHANISM_ANALYSIS.md`) | — | — | — | — | "Are you overclaiming?" |

## Paragraphs where current evidence is insufficient — named directly, not glossed over

1. **§4 (correlated error) has zero real fitted data.** Propositions 1-3 are
   verified by simulation against their own closed forms, not fit to any
   observed (π, p_hard, p_easy) from MATH-Hard or IFEval — there are no
   scorer-wrong events to fit them to (T-C: 0/69; original audit: 6/350).
   **A paragraph claiming "we show correlated error cancels on MATH-Hard"
   would be unsupported — the honest claim is "we show the mechanism and
   its boundary condition; MATH-Hard's current data cannot estimate its
   magnitude."** State it that way or cut the section's empirical framing.
2. **§9/§10's real event counts (0 and 6) are too small for §4's mechanism
   to ever be empirically closed on this benchmark without a much larger,
   differently-targeted audit** (`AUDIT_DESIGN_ANALYSIS.md` Q1: median 415
   required for the audit-only-layer target). A paper draft must not imply
   this is a near-term next step without saying it needs ~6× the current
   total audit size.
3. **§10's comparator bug fix was verified against Windows-specific
   behavior only.** No confirmation yet that the *unpatched* `is_equiv`
   behaves correctly on Linux (where `SIGALRM` exists) — plausible, expected,
   but not independently verified in this pass. A reviewer could reasonably
   ask "have you checked this doesn't also silently fail on Linux for a
   different reason?" — not yet answered.
4. **§11/§12's IFEval section cannot report a human-validated scorer-error
   rate at all** — unlike MATH-Hard's T-C, there is no working human
   ground-truth for the 83.2% unexplained disagreement. Any manuscript
   sentence structured like MATH-Hard's ("we audited X, found Y") must not
   be written the same way for IFEval; it must read as "verifier bugs
   account for 16.8%; the rest is unresolved," full stop.
5. **The `EE_FEATURE_STABILITY_CHECK.md` 4-feature result is now off by one
   event** (`MATH_COMPARATOR_BUG.md`: 6 true events, not 5) and has not
   been refit. Any manuscript figure or table citing that AUC or feature
   list must either refit first or footnote the discrepancy — do not carry
   the stale number forward silently.

## Final validation phase additions — new rows earned by this pass

| § | Claim | Theorem/result | Dataset | Experiment | Uncertainty estimate | Falsification test | Reviewer objection answered |
|---|---|---|---|---|---|---|---|
| 14. Canonical headline | The 6.10× dominance figure, with a full denominator cascade (378→136→120), not just "n=120 of 136" | A1 (revised) | Same 136 pairs | `fb_ea_dominance_canonical.py` | Full percentile distribution reported, not just median/IQR | A different cascade count would mean the prior ad-hoc number was wrong — matched exactly | "State the denominator or the '100%' claim is meaningless" |
| 15. Empty-set diagnostic | Formal definition + full root-cause of the 70 scorer-only empty sets: 5 models, 100% point-estimate-driven, 0% Λ-width-driven | `RECONCILIATION_EMPTY_SET_ROOTCAUSE.md` | Same 17-model roster | `fb_rootcause_empty_scorer_layer.py` | Exact roll-up (70=60+10) independently re-derived, matches | A mixed-cause breakdown would have meant the "one clean mechanism" claim was wrong — it wasn't | "You found a bug — is the story actually this clean?" |
| 16. Platform validation | `is_equiv` fix verified correct on real Linux, not just "should work the same" | `MATH_COMPARATOR_LINUX_VALIDATION.md` | GitHub Actions, ubuntu-latest | CI run 34764225948 | Exact match to Windows result (0/69 both platforms) | A discrepancy would mean the fix itself was platform-dependent — none found | "Verify on the platform your dependency actually assumes" |
| 17. Negative controls | The method concludes "stable" when it should: audit sized to the project's own required-n gives ratio 0.599, not >1 | `NEGATIVE_CONTROLS.md` | Synthetic, parameter-matched to real roster | `fb_negative_controls.py` | 5 scenarios, 3 stable, 2 dominant, matching theory | The method reporting dominance regardless of input would have failed this test — it didn't | "Does this just always say 'more uncertainty'?" |
| 18. Audit-design reality check | Naive Neyman allocation is dominated by proportional allocation on real sparse audit data (74% vs. 22% unresolved at 16× budget) | `AUDIT_DESIGN_OPTIMIZATION.md` | Same 120 pairs | `fb_audit_design_optimization.py` | Full budget sweep (6 levels) + greedy near-oracle comparison | Neyman matching or beating proportional would have undercut this finding — it didn't | "Did you even check the classical formula works here?" |

## What is genuinely blocked, requiring external input (not a paper-writing gap)

- **`is_equiv` non-Windows verification: RESOLVED this phase**, no longer
  blocked — see row 16 above.
- **A genuinely independent third benchmark: candidates now named, not a
  dead end** (`INDEPENDENT_BENCHMARK_SEARCH.md` — HELM, AlpacaEval), but
  executing a full replication still needs a new human-audit round on
  whichever source is chosen — the external-access decision has moved from
  "no data exists" to "which new labeling round to fund," a smaller and
  more concrete ask.
- **E-H (execution-scored control) and any judge-scored paradigm test**:
  the only currently-accessible data source (open-llm-leaderboard details
  repos, already-authenticated) contains no execution-scored or
  judge-scored tasks — confirmed directly by listing every available task
  file for a real model (`leaderboard_arc_challenge` … `leaderboard_musr_*`,
  no HumanEval/MBPP/judge task anywhere). **Needs**: a different public
  per-response dataset (e.g. EvalPlus's HumanEval+/MBPP+ result dumps, or
  bigcode-evaluation-harness's own published outputs) or new model
  inference — either is a real external-access decision, not something to
  proceed on by assumption.
- **A second, fully independent benchmark/model family/scorer** (item 11):
  IFEval reuses the same 27-model roster as MATH-Hard — real generalization
  evidence (different scoring paradigm) but not full independence (same
  models). A genuinely independent replication needs a different roster,
  which needs a different data source than the one already authenticated.
