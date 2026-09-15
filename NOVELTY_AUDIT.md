# Novelty audit refresh (items 12, 24)

`MASTERPLAN_PHASE2_FLAGSHIP.md` §2 already ran an extensive sweep (~9 query
axes, 2026-09-09). This refreshes it against the broader terminology item
24 asks for, 4 days later — a spot-check for drift, not a from-scratch
redo.

## What was checked

Web searches (not exhaustive; the goal is catching anything that would
materially threaten the novelty claim, not a full systematic review):
"scorer uncertainty"/"grader sensitivity"/"audit allocation" + partial
identification; misclassification + LLM verifier + sensitivity analysis,
September 2026.

## Findings — nothing found that threatens the core claim

- **`2608.13326` "Beyond Local Accuracy: A Protocol-Level Identifiability
  Audit"** (Aug 2026) — shares the word "identifiability audit" but solves
  a different problem: whether an *observation protocol* can distinguish
  between different *behavioral policies* a model might be running (a
  model-behavior identification question). This project's identifiability
  question is whether *true accuracy* is identified given *scorer
  misclassification* — a measurement-error structure, not a policy-
  distinguishability one. **Different object, different math — cite as
  adjacent terminology, not overlapping method.**
- **`2602.16039` "How Uncertain Is the Grade?"** and related — LLM-judge
  grading uncertainty. Relevant to `MASTERPLAN_PHASE2_FLAGSHIP.md`'s E-G
  (judge-scored extension, not yet run) but does not touch programmatic/
  deterministic scorer identification, this project's actual object.
- **VerifyBench (`2507.09884`), CompassVerifier (`2508.03686`)** — these
  *benchmark verifiers themselves* (which verifier is more accurate at
  judging correctness). Adjacent but orthogonal: they ask "how good is this
  verifier," this project asks "given a verifier's known error rate, what
  can we still conclude about a benchmark comparison." Worth citing as
  evidence the field cares about verifier quality; does not compete.
- **A fact-verifier misclassification study** (found via search, exact
  arxiv id not resolved in this pass) independently reports that
  rule-based verifiers "frequently misclassify semantically correct but
  non-canonical responses" — **external, independent corroboration of this
  project's own MATH-Hard mechanism finding** (interval/set-notation
  reordering, `\dfrac` — `ADVERSARIAL_SUITE.md`). Worth citing as
  supporting evidence the mechanism is not MATH-Hard-specific.
- Nothing found using the exact framing "scorer sensitivity model" applied
  to benchmark accuracy identification, nor anything computing an
  audit-estimation-vs-scorer-sensitivity decomposition analogous to
  `RECONCILIATION_FOUR_LAYERS.md`, nor an audit-design (Neyman allocation
  for scorer-error auditing) treatment analogous to
  `AUDIT_DESIGN_ANALYSIS.md`.

## Claim-by-claim novelty map

| Claim | Novel? | Basis |
|---|---|---|
| Sharp partial identification of accuracy under scorer misclassification (T-A/T-H) | Method not novel (MSM, cited); **application to benchmark scoring appears open** | Masterplan §2.1, reconfirmed here |
| Design-sensitivity impossibility result for benchmarks (T-B) | Method not novel (Rosenbaum design sensitivity, cited); **application here appears open** | Masterplan §2.1 |
| Audit-estimation-uncertainty-dominates-scorer-uncertainty finding (B) | **The specific empirical comparison appears open** — no paper found making it | Masterplan §2.1, still true after this refresh |
| Neyman-allocation audit-design methodology for scorer-error auditing (C) | Method not novel (Neyman 1934, cited); **application to this problem appears open** | Not found in this refresh either |
| A real, causally-confirmed nondeterminism bug in IFEval's standard verifier | **Novel as a specific finding** (a bug report, not a methodology claim) | This project's own discovery |
| A real, platform-specific bug in the standard MATH comparator | **Novel as a specific finding** | This project's own discovery, this session |

**No claim in this project needs updating or retracting based on this
refresh.** The one adjustment: cite `2608.13326` explicitly in related
work as an example of "identifiability" being used for a different problem
in the same general area, pre-empting a reviewer conflating the two.

## Final refresh (item 13) — a close, serious neighbor found, and the formal A/B/C/D classification

**Chen, Rambachan & Tamer, "Partial Identification from LLM Prompts"
(arXiv:2606.15031, June 2026, Yale/MIT/Harvard).** This is the closest
paper found in any pass of this project and must be cited and explicitly
distinguished in the manuscript, not omitted. Their setup: LLMs used AS
binary classifiers/raters of a latent truth (e.g. toxicity), partially
identifying the *prevalence* θ=P(X*=1) from a panel of LLM reports whose
errors "may be arbitrarily dependent given the truth" because "LLMs share
training corpora, benchmarks, synthetic data, distillation pipelines, and
alignment procedures" — explicitly breaking Dawid-Skene conditional
independence, exactly the mechanism this project's own correlated-error
theory (`THEORY_EXTENSIONS.md` §1) also invokes. Their identifying
restriction — reporter-specific sensitivity/specificity calibration
constants bounding a false-positive/false-negative-style rate — is
**structurally the same object as this project's (alpha,beta)**, and both
projects cite the same classical lineage (Horowitz & Manski 1995, Molinari
2008, Hu 2008).

**Why this is a neighbor, not a collision:** their LLMs are the *raters*
(the thing that might be wrong); this project's LLMs are the *ratees* (the
thing being scored) by a single fixed, non-LLM, deterministic scorer.
Their estimand is a population *prevalence*; this project's is a
*difference in two specific models' accuracies* (a benchmark-comparison/
ranking question), with a flip-budget and an audit-design allocation
question their paper does not address at all (confirmed: no discussion of
benchmark comparison, ranking, or human-labeling-budget allocation found
in their design-taxonomy, calibration, or empirical sections). **Their
headline contributions (a replication-design taxonomy for count/vector/
matrix panels; a truth-sufficient-coarsening theorem for response
matrices; sharpness from the full score law) have no counterpart here**
because this project has exactly one reporter (the scorer) per item, not
a multi-rater panel — the matrix-reduction question they solve does not
arise in this project's setting.

**What this changes:** it sharpens, rather than damages, this project's
own honesty about T-A. Two independent, serious groups adapting the same
classical misclassification-bounds toolkit to adjacent LLM-measurement
problems in the same year is real evidence the *toolkit* is not this
project's contribution (already conceded) — it is modest additional
reason to lean the novelty claim entirely on the combination this project
actually offers (benchmark comparison + audit design), which their paper
does not touch.

### Formal A/B/C/D classification, every theorem/result, as instructed

A = classical, B = direct adaptation, C = nontrivial extension, D = genuinely new. Never call A or B novel.

| Result | Class | Reasoning |
|---|---|---|
| T-A: Scorer Sensitivity Model (Λ-odds-bound) | **B** | Direct adaptation of the marginal-sensitivity-model / misclassification-bounds literature (Horowitz & Manski 1995; Molinari 2008; Hu 2008) — the same family Chen-Rambachan-Tamer (2026) also adapt, independently, to a different problem |
| T-H: sharpness of the identified set | **B** | Standard linear-fractional vertex-theorem argument; a known proof technique applied to this specific box |
| T-B: design-sensitivity impossibility (Λ̃) | **B** | Direct adaptation of Rosenbaum design sensitivity (matched-observational-studies literature) to a benchmark-comparison setting |
| Neyman-optimal audit-stratum allocation | **A** | Classical (Neyman 1934), applied with no modification to the allocation formula itself — see `fb_audit_design_optimization.py`'s explicit proof, cited not claimed |
| Four-layer reconciliation (sampling/audit-only/scorer-only/combined) | **C** | The layers themselves are individually classical, but decomposing a benchmark comparison into exactly these four, comparable, same-methodology layers and reporting per-layer valid/excluded counts is not found elsewhere — a nontrivial organizing contribution, not a new theorem |
| Flip budget (`d*`, minimum perturbation to flip a comparison) | **C** | A genuinely useful reframing of an existing sensitivity bound as a decision-relevant single number; the underlying bound (T-A/T-H) is B, the reframing is a nontrivial, not fully mechanical, extension |
| Ranking-preservation theorem (`THEORY_EXTENSIONS.md` §2) | **B** | An explicit corollary of T-H's sharpness result, stated as a theorem for citability — not new content beyond T-H |
| Correlated-error cancellation (Props. 1–3, `THEORY_EXTENSIONS.md` §1) | **B** | Direct application of a standard one-factor/conditional-independence-given-a-common-cause variance decomposition (the same structural assumption as Dawid-Skene/Hui-Walter) |
| Empty-identified-set diagnostic (this session's central finding) | **C** | Not a new theorem, but a nontrivial, previously-unstated correct treatment of a real degenerate case in the [0,1]-bounded identification methodology — the *absence* of this check in the field's naive box-clipping is the actual finding |
| Audit-design formal optimization + Neyman-vs-proportional-vs-partial-pooling comparison on real sparse data (this session) | **C** | The optimization problem itself is classical (A above); finding that naive plug-in Neyman is *dominated* by proportional allocation on this real, sparse-event data (`AUDIT_DESIGN_OPTIMIZATION.md`) is a nontrivial, data-specific result about when the classical formula's own assumptions (a decent pilot estimate) break down |
| The SIGALRM/Windows bug, the empty-set bug, the T-C hardcoded-path bug | **D**, but as *findings*, not *methodology* | Genuinely new (previously undiscovered), but they are bug reports, not mathematical or methodological contributions — correctly kept out of the theorem inventory |

### The scorer-mismatch finding — does it enable a broader contribution claim?

**Tested honestly: partially, not fully.** The finding (`SCORER_MISMATCH_MAJOR_FINDING.md`) generalizes the paper's object from "a benchmark's automated scorer has a measurable error rate" to "a benchmark's reported accuracy is itself criterion-dependent — which automated scorer you choose is a real, measurable, boundable source of uncertainty, using the same audit-design machinery already built." That is a genuinely broader framing than "MATH-Hard's `is_equiv` has a bug."

**What would be needed to claim the full "evaluation pipelines as measurement systems" framing, and is not yet present:** (1) a second benchmark showing the same phenomenon (two live, disagreeing automated scorers) — not yet checked elsewhere; IFEval's mechanism-bug finding is a different phenomenon (nondeterminism within one scorer, not disagreement between two); (2) a theoretical result stating conditions under which scorer-choice uncertainty is bounded by the SAME Λ-sensitivity framework as within-scorer error, rather than treated as a separately-measured empirical quantity (currently: measured directly since both scorers are automated and available on the full population — a strength for THIS project, but means the "scorer-choice width" layer is an empirical add-on to the framework, not yet a proven extension of T-A/T-H). **Class: C (nontrivial empirical extension of the existing framework), not D (a new theorem)** — consistent with the rest of this project's honestly-scoped novelty claims.

**Recommendation for the manuscript**: state the broader "criterion-dependence is measurable and typically small but occasionally large" claim as a secondary contribution, explicitly scoped to what was tested (one benchmark, two scorers, one model roster) — not as a general theory of evaluation-pipeline measurement, which this evidence does not yet support.

### Re-checked 2026-09-15 (autonomous execution, Phase 6)

No new direct collision found (Chen-Rambachan-Tamer, VerifyBench, CompassVerifier remain the closest neighbors, already accounted for above). Two confirmations worth recording: (1) NeurIPS 2026's Evaluations & Datasets CFP explicitly scopes in "empirical audits... methodological analyses... analysis, critique, redesign, or stress-testing of evaluation practices" — a direct match to this project's shape, reinforcing the venue choice rather than changing the novelty assessment. (2) Independent, general confirmation that "answer format and extraction dependency" is a recognized open problem in the field (not this project's invention) — supports the motivation, doesn't compete with the contribution.

### Is the combination sufficient for NeurIPS 2027?

**Yes, for the Evaluations & Datasets track, on the combination, not on any single piece.** No individual theorem here is D. The manuscript's defensible novelty claim is the *combination* (C-level): applying classical misclassification-sensitivity bounds specifically to benchmark **comparison** (not just single-model accuracy), formalizing the resulting audit-design problem as a budget-allocation optimization with a proven classical solution whose real-data behavior is itself informative (dominated by proportional allocation under sparse events — a genuine, non-obvious finding), and doing all of this with a from-scratch, self-audited reproducibility discipline that caught three real bugs along the way. This is consistent with, and now more precisely stated than, the prior verdict in `FINAL_DECISION.md`.
