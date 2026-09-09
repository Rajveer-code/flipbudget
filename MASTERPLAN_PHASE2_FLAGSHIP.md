# MASTERPLAN — PHASE 2: FLAGSHIP ESCALATION

**Written 2026-09-09, after a fresh literature sweep (arXiv API, ~9 query axes across
econometrics, diagnostic-testing statistics, sensitivity analysis, and LLM evaluation).
Phase 1 — `PLAN_FLIPBUDGET.md` — is now the foundation, not the deliverable.**

Phase 1 built: T1–T5 theory, E1/E2/E4/E5/E6, a tested package, a public dataset and
audit page, 20 commits. It produced one real empirical result (16.1% of 351 MATH-Hard
pairs have a flip budget below the roster's observed differential error) and two real
mechanism findings (a false-credit outlier model; a `dfrac` false-miss in the live
comparator).

**That is a competent audit paper. It is not yet a field-level contribution.** This
document is the plan to make it one.

---

## §1 — CORE THESIS

### 1.1 The reframe that changes what this is

Phase 1's thesis: *benchmark accuracy is partially identified under scorer error; here
is a diagnostic statistic.*

Phase 2's thesis:

> **Observational causal inference solved "how much hidden bias would overturn this
> conclusion?" — Cornfield's inequality, Rosenbaum's Γ, the E-value, the marginal
> sensitivity model, design sensitivity. Machine-learning evaluation has the identical
> problem, with the scorer as the source of hidden bias, and has no such apparatus at
> all. We build it.**

Under that framing the flip budget stops being a statistic we invented and becomes the
scorer-error analogue of Γ — an instance of a mature, respected methodology being
imported into a field that needs it and does not have it. That is a field-level
methodological contribution. A diagnostic statistic is not.

Everything in this plan is downstream of that reframe.

### 1.2 The one-sentence claim we are trying to earn

> Reported benchmark comparisons carry a second, unreported uncertainty component that
> does not shrink with more data, is frequently larger than the sampling uncertainty
> that *is* reported, is predictable from observable response properties, and is large
> enough that a nontrivial fraction of published leaderboard orderings cannot be
> distinguished from their reverse.

Every clause of that sentence is a separate empirical obligation. §5 assigns each one
an experiment. **We have currently earned none of them at scale, and the "larger than
sampling uncertainty" clause — the one that makes the paper matter — has never been
tested at all.**

---

## §2 — NOVELTY GAP (verified 2026-09-09, not asserted from memory)

### 2.1 Verified absences — these are the openings

| Gap | Evidence it is open |
|---|---|
| **No sensitivity-analysis apparatus for scorer error in ML evaluation** | Queried `E-value`+`sensitivity`, `marginal sensitivity model`, `design sensitivity`, and `scorer`+`error`+`language model` — the causal-inference apparatus is mature and entirely absent from the eval literature. Zero overlap. |
| **No treatment of the human reference as imperfect in benchmark auditing** | `imperfect gold standard`, latent-class/Hui-Walter test-accuracy literature exists (`1608.06677`, `2509.18489`) and is used nowhere in LLM-eval auditing. Every audit implicitly assumes human labels are truth. |
| **No verification-bias correction in benchmark audits** | `verification bias` literature is mature in diagnostics (`2509.12217` tutorial, `2601.12167` DAGs). Every benchmark audit I have seen — **including Phase 1's own** — stratifies the audit sample on the scorer's own output. That is textbook partial verification bias and nobody names it. |
| **Nobody has established whether scorer-induced uncertainty exceeds sampling uncertainty** | No paper found making this comparison. This is the headline nobody has claimed. |

### 2.2 Adjacent work — cite prominently, do not overclaim against

| Work | What it does | Our relation |
|---|---|---|
| **`2607.02104`** *When Can You Debias an LLM Judge? Identifiability Limits…* (Jul 2026) | Proves the quality/bias split in Bradley–Terry judge models is **not identified**; profile likelihood flat to 0.0000 nats across 48 judge pools; scaling comparisons 26× buys nothing. Characterizes when prior-based correction is justified, plus **designs that supply the missing information**. | **Nearest theoretical neighbour, and a gift.** Same structural insight (identification, not estimation, is binding) in a different setting: they treat *LLM judges* and *pairwise BT models*; we treat *deterministic/programmatic scorers* (extraction, string-match, execution) and *accuracy + its differences*. Crucially, they say the missing information must come from **designs** — our human-audit validation sample *is* such a design, for their sibling problem. Cite as independent confirmation; position as complementary, never competing. |
| **Chen, Rambachan & Tamer `2606.15031`** | Partial identification of prevalence from LLM reports | Roles inverted: LLM is their instrument, our object. They lack a validation sample (bounds → [0,1]); we have one. |
| Rollout Cards `2605.12131`, ABA `2605.26079`, `2510.14773`, `2606.10904` | Audits and reporting standards | They document; we supply the inferential object. |
| `2606.12639` (drug-response), `2607.08203` (polyp segmentation) | "Evaluation choice flips rankings", independently, in **other domains** | **Strong support for generality.** The phenomenon is not an LLM quirk. It is a measurement problem across ML, and each of these is a one-off audit with no methodology. A domain-general method has an audience beyond NLP. |
| Rank-interval cluster (`2607.16259`, `2606.08679`, `2603.03336`, `2604.05460`) | Sampling-uncertainty intervals for ranks | Complementary; we attack the conditioning assumption they all share. |

### 2.3 The novelty claim, in the exact words to defend

> We import sensitivity analysis — the apparatus developed for unmeasured confounding in
> observational studies — into benchmark evaluation, with the scoring function as the
> source of hidden bias. We define a scorer sensitivity model, derive sharp bounds and a
> design-sensitivity limit under it, correct for the verification bias and imperfect
> reference standard that benchmark audits structurally incur, and show empirically that
> the resulting uncertainty component is frequently larger than the sampling uncertainty
> the field currently reports.

Not novel and must be said so: partial identification, misclassification correction,
sensitivity analysis, Rosenbaum bounds, the E-value, latent-class reference-standard
models, verification-bias correction. **We are importing, extending, and validating —
not inventing the mathematics.** Reviewers punish the opposite claim.

---

## §3 — THEORETICAL PROGRAM

Ranked by scientific value. Each states the reviewer objection it kills.

### T-A. The Scorer Sensitivity Model (SSM) — **highest value**
*Objection killed: "Why a symmetric box on (α,β)? That parameterization is arbitrary."*

Phase 1 perturbs (α,β) inside a box of radius `d`. That is ad hoc, not
reparameterization-invariant, and a reviewer from the sensitivity-analysis world will
say so immediately.

**Replace it with an odds-ratio-bounded family, the marginal-sensitivity-model analogue:**
for every item `i`, the odds that the scorer misreads it deviate from a baseline by at
most Λ:

```
1/Λ  ≤  [ oddsᵢ(misread | model j) / oddsᵢ(misread | baseline) ]  ≤  Λ
```

Deliverables: the identified set for `A*` and for `Δ*` under Λ-boundedness; proof of
sharpness (extends T4's IVT argument to the new family); the map from Λ back to
interpretable (α,β) so practitioners can reason about it.

**Expected information gain:** high. Converts the central object from "a number we
defined" to "an instance of a standard, respected family." Also strictly generalizes
Phase 1 (the box is a special case).
**Could it change the conclusion?** Yes — Λ-bounded sets are generally *tighter* than
box sets, so the 16.1% could move in either direction. That is a feature: it is the
honest number.

### T-B. Design sensitivity for benchmarks — **the quotable theorem**
*Objection killed: "Just collect more benchmark items."*

Rosenbaum's design sensitivity Γ̃ is the limiting Γ at which power → 0 as n → ∞.
The analogue: **Λ̃**, the limiting scorer-sensitivity at which a comparison becomes
unidentifiable *no matter how many benchmark items are added*.

**Theorem candidate:** for a fixed scorer with margins (α,β) and true gap Δ*, Λ̃ is
finite and computable in closed form — hence **there exist model pairs that no amount
of benchmark data can separate.**

**Expected information gain:** very high. This is an impossibility result, it is short,
it is quotable, and it directly answers the field's reflex ("add more items"). It is the
single most likely thing in this plan to be cited by people who disagree with us.
**Could it change the conclusion?** If Λ̃ is infinite for realistic parameters, the
impossibility claim dies and we keep only the finite-sample story. Test early.

### T-C. Item-heterogeneous and correlated scorer error — **kills the biggest objection**
*Objection killed: "α and β constant across items and independent across models is
obviously false, so your bound is wrong."*

Upgrade the model to item-specific `(αᵢ, βᵢ)` with a shared latent "scorer difficulty"
factor per item inducing **correlation across models on the same item**.

Two results to derive:
1. **Correlated error partially cancels in differences** — shared per-item scorer
   difficulty affects both models, so the naive bound is *conservative*. Quantify how
   conservative.
2. **Format-dependent heterogeneity does not cancel** — it is exactly the differential
   component, and it is what breaks rankings.

**Expected information gain:** very high. This is the objection that would otherwise
sink the paper, and answering it *tightens* our own bound rather than widening it —
which is the strongest possible way to answer an objection.
**Could it change the conclusion?** Yes. If cancellation dominates, the effective
differential is much smaller than Phase 1 assumed and the 16.1% shrinks. Must be run.

### T-D. Imperfect reference standard
*Objection killed: "Your human labels are not ground truth either."*

Phase 1 treats human adjudication as truth (κ = 0.98, not 1.0). Use the latent-class /
Hui-Walter apparatus: with ≥2 conditionally-independent imperfect raters plus the
scorer, all three accuracies are identifiable without a gold standard. Report bounds
robust to reference error; report how much reference error would have to exist to
explain away our finding (an E-value for the *reference*, not the scorer).

**Expected information gain:** high, and it is *insurance* — this objection is certain
to be raised and currently has no answer.
**Could it change the conclusion?** Yes, in the bad direction: if reference error is
comparable to scorer error, the measurement chain is unreliable end-to-end. That would
be a different — still publishable, arguably more important — paper. See §12 kill
criteria.

### T-E. Verification-bias-corrected estimation
*Objection killed: "Your audit sample is selected on the scorer's own output."*

Phase 1's audit stratifies on `credited` / `wrong_parsed` / `unparsed` — the scorer's
verdict. That is partial verification bias. The existing design weights are, I believe,
the correct correction, but Phase 1 never *named* the bias or *proved* the estimator is
consistent under a stated assumption.

Deliverable: formalize with the diagnostic-testing apparatus (Begg–Greenes lineage;
`2509.12217`), state the MAR-given-stratum assumption explicitly, prove consistency,
and give a sensitivity analysis for violations of it.

**Expected information gain:** moderate-high. It converts a latent vulnerability into a
stated, defended design choice.

### T-F. From threshold to probability
*Objection killed: "A threshold is not a probability; what do I do with Λ = 1.8?"*

Following `2603.18928` (Bayesian reinterpretation of Cornfield-type analysis, Mar 2026):
replace "the flip budget is 0.02" with **"given the empirically observed distribution of
scorer errors across this roster, P(this published ordering is wrong) = p."**

**Expected information gain:** high for adoption. A probability is directly usable by a
leaderboard maintainer; a threshold requires interpretation. This is the difference
between a statistic people cite and a statistic people *run*.

### T-G. Studentized sensitivity inference
*Objection killed: "Your bootstrap under-covers and you just wrote a caveat about it."*

Phase 1's T3 found raw percentile bootstrap achieving ~0.90–0.92 against 0.95 nominal
and honestly labelled it. Honest, but not good enough for a flagship. Adopt Rosenbaum's
studentized sensitivity analysis so the procedure is valid without knowing true (α,β).

**Expected information gain:** moderate. Fixes a known defect properly instead of
disclosing it.

### T-H. Sharpness under the SSM
Extend T4's constructive IVT sharpness proof to the Λ-bounded family. Required for T-A
to be a real contribution rather than a re-parameterization.

---

## §4 — EMPIRICAL PROGRAM

Ranked by scientific value. **E-A runs first and gates the rest.**

### E-A. The dominance study — **run this before anything else**
**Question:** Is scorer-induced identification width larger than sampling width?
**Objection answered:** "This is a second-order correction; sampling noise dominates."
**Information gain:** Maximal. This single ratio determines whether the paper matters.
If identification width routinely exceeds sampling width, then every rank-interval paper
in §2.2's cluster is understating uncertainty, and they must cite us.
**Could it change the conclusion?** It *is* the conclusion. If the ratio is < 1
everywhere, §12's kill criterion 1 fires.
**Design:** across every (benchmark × harness × model-pair) cell reachable, compute both
widths and report the ratio's distribution. Target ≥8 benchmark families, ≥4 harnesses,
≥100 models.

### E-B. Scale-out: benchmark families × harnesses × paradigms
**Question:** Does the phenomenon generalize beyond MATH-Hard?
**Objection answered:** "One benchmark, one harness, one paradigm — this is anecdote."
**Information gain:** High. Generality is the difference between a case study and a
method.
**Design:** MATH-Hard, GSM8K, MMLU (both variants), IFEval, GPQA, plus execution-scored
(HumanEval/MBPP) and judge-scored tasks. Harnesses: lm-eval, lighteval, OpenCompass,
HELM, simple-evals. The Open LLM Leaderboard details datasets supply models at scale.
**Could it change the conclusion?** Yes — if the effect is MATH-Hard-specific, the claim
narrows to "extraction-heavy math benchmarks," which is a real but much smaller paper.

### E-C. Predicting scorer failure from observable response features — **highest value-per-hour**
**Question:** Can `P(scorer misreads response)` be predicted from response length, boxed
presence, CoT markers, delimiter counts, format entropy — *before* human adjudication?
**Objection answered:** "Your audit is tiny and cannot scale; α,β for unaudited models
are guesses."
**Information gain:** Very high, three ways at once:
1. **Practical** — a high-AUC predictor lets anyone triage a human audit to the items
   most likely to be misread, cutting audit cost by an order of magnitude.
2. **Mechanistic** — if format features predict failure, format-dependence is
   *systematic*, not noise. That is the causal story the whole paper needs.
3. **Statistical** — it supplies a cheap proxy for `αᵢ, βᵢ` at scale, feeding T-C's
   item-heterogeneous model without labelling everything.
**Could it change the conclusion?** Yes. AUC ≈ 0.5 kills the triage claim and weakens
the mechanism story considerably.

### E-D. Adversarial scorer stress test (at scale, with a taxonomy)
**Question:** What is the worst-case α,β a legitimate response style can induce?
**Objection answered:** "Your synthetic set was 14 hand-written cases."
**Information gain:** High. Phase 1's E2 already found a real `dfrac` false-miss from 8
constructed cases — a systematic, taxonomized version at scale will find more, and
establishes the worst case rather than the average.
**Design:** a generated taxonomy of semantically-invariant transformations (LaTeX
variants, unit placement, verbosity, delimiter style, multi-answer, self-correction) ×
semantically-wrong-but-surface-similar constructions. Per-scorer α,β per transformation.
**Could it change the conclusion?** It cannot lower the effect, only raise it —
so it strengthens rather than tests. Weight accordingly (it is evidence, not a gate).

### E-E. Format-conditional differential error
**Question:** Does differential scorer error track *model house style* — reasoning vs
terse, verbose vs boxed?
**Objection answered:** "So what if scorers err — why would it favour anyone?"
**Information gain:** Very high. This is the "so what." If model families with different
output conventions are systematically mis-compared, the finding is directly actionable
for anyone reading a leaderboard.
**Could it change the conclusion?** Yes — if error is format-independent, it is largely
non-differential, Case A applies, and rankings are mostly safe. That would substantially
deflate the paper. **Must run.**

### E-F. Version/temporal drift at scale
**Question:** How much do rankings move across defensible harness versions, holding
responses fixed?
**Objection answered:** "Pick a version and move on."
**Information gain:** Moderate-high. Phase 1's E6 found two real cases by hand,
including in the very comparator this project uses. Scaling it converts an anecdote into
a distribution.
**Could it change the conclusion?** No — it extends scope rather than testing the core.

### E-G. Judge-scored paradigm
**Question:** Does the framework extend to LLM-judge scoring?
**Objection answered:** "String-match scorers are legacy; everyone uses judges now."
**Information gain:** High for relevance and reach, and it is the natural bridge to
`2607.02104`. **Do not enter the judge-agreement literature** — enter with the
identification framing only, which is unoccupied.
**Could it change the conclusion?** It extends rather than tests.

### E-H. Execution-scored criterion-alignment control
**Question:** Is error small **and approximately non-differential** where no extraction
step exists?
**Objection answered:** "Is the mechanism really extraction, or just 'scoring is hard'?"
**Information gain:** High — this is the experiment that isolates the mechanism.
Measured, never assumed (Phase 1 already corrected this once).
**Could it change the conclusion?** Yes, decisively. If execution-scored tasks show
comparable differential error, the extraction mechanism story is wrong.

### E-I. Replication of published rank-interval methods — **only after ours stands**
**Question:** What happens to `2606.08679` / `2607.16259`'s intervals with identification
width added?
**Objection answered:** "This is orthogonal to real uncertainty-quantification work."
**Information gain:** High but *contingent*: it is only credible once our own result is
independently established. Reproduce their published numbers **exactly** before changing
anything; drop the experiment if they cannot be reproduced. Frame as extension, never
as attack.

**Deliberately excluded** (would enlarge the paper without adding evidence): another
judge-agreement study; a contamination study (`2609.02899` largely settled it); an IRT
treatment; a new task benchmark; a construct-validity position paper.

---

## §5 — CLAIM-TO-EXPERIMENT MAP

Every clause of §1.2's headline sentence, and what earns it:

| Clause | Earned by | Status |
|---|---|---|
| "a second, unreported uncertainty component" | T-A, T-C | Phase 1 partial |
| "does not shrink with more data" | **T-B** | Not started |
| "frequently larger than the sampling uncertainty that is reported" | **E-A** | **Never tested** |
| "predictable from observable response properties" | **E-C** | Not started |
| "a nontrivial fraction of published orderings cannot be distinguished from their reverse" | E-A, E-B, E-I | Phase 1 single-benchmark only |

---

## §6 — HUMAN VALIDATION

- **H-A.** Preregistered stratified expansion, size set by a **real power calculation**
  against the effect observed in Phase 1 — not a guessed n. Register before drawing.
- **H-B.** ≥3 blind labellers; per-stratum agreement (not pooled — pooled κ = 0.98 is
  flattering and per-stratum will be lower and more honest); cross-vendor adjudication.
- **H-C.** Held-out fold reserved for a **predictive check**: does the calibration-fold
  correction predict the held-out fold's directly-known Δ? This is stronger than merely
  avoiding circularity.
- **H-D.** **Uncertainty in the reference itself** (T-D): deliberate hard-case
  oversample, latent-class treatment, and an explicit "how wrong would the humans have
  to be to explain this away" number.
- **H-E.** Documented adjudication protocol for disagreements, frozen before labelling.
- **H-F.** Audit triage informed by E-C's predictor — label where information is, and
  report the design weights that keep the estimator unbiased under that choice.

---

## §7 — DATASETS

- **D1** `flipbudget-responses` — response × scorer verdict × human verdict ×
  parseability × extracted format features, across all benchmark families in E-B. The
  first public corpus whose subject is the **scorer**.
- **D2** `flipbudget-margins` — per (harness, extractor, benchmark, model): α, β with
  CIs, audit n, design weights. **This is the file that generates citations by use** —
  anyone applying the correction needs it.
- **D3** `flipbudget-adversarial` — E-D's taxonomy with per-scorer outcomes.
- **D4** `flipbudget-adjudicated` — the frozen human set including *disagreements*, not
  just majority labels.

Licensing per upstream source; ship IDs + labels where redistribution is restricted.

---

## §8 — SOFTWARE

- **S1** (exists, Phase 1) — `flipbudget` package. Extend with the SSM (T-A), the
  probability output (T-F), studentized inference (T-G).
- **S2** — harness plugins (lm-eval entry points first, then lighteval, OpenCompass) so
  the correction runs inside someone's existing pipeline with one config line.
- **S3** — `flipbudget audit-triage`: E-C's predictor as a CLI that ranks unlabelled
  responses by P(scorer misread), so a practitioner can spend a fixed labelling budget
  where it matters.
- **S4** — a reproducibility package: one command regenerates every number in the paper
  from released data.

---

## §9 — PUBLIC INFRASTRUCTURE

- **B1** (exists) — the shadow leaderboard Space. Extend to all E-B benchmarks, add the
  T-F probability column and the Λ slider so a reader can move the sensitivity parameter
  and watch orderings dissolve. **That interaction is the single most persuasive artifact
  available** — it turns an abstract bound into something a person operates.
- **B2** — a public **Scorer Card** registry: submit an extractor, get back its measured
  α, β on the adversarial suite. The benchmark whose subject is the grader.
- **B3** — a reporting standard, proposed **only after** B1/B2 are used by someone other
  than us. A standard nobody has adopted is a blog post.

---

## §10 — PAPER STRUCTURE

1. Motivating example: a real published ordering that reverses under a defensible scorer
   change (from E-B, not hypothetical).
2. Measurement model and estimand; the scorer as hidden bias.
3. **T-A** the Scorer Sensitivity Model; identified sets; **T-H** sharpness.
4. **T-B** design sensitivity — the impossibility result.
5. **T-C** heterogeneity and correlation; when error cancels and when it does not.
6. **T-D/T-E** imperfect reference, verification bias.
7. **T-F/T-G** probability reporting and studentized inference.
8. **E-A** dominance — the headline table.
9. **E-C/E-E** mechanism: prediction and format-dependence.
10. **E-H** execution control; **E-D** adversarial worst case.
11. **E-B** scale; **E-I** replication.
12. Limitations, explicit non-claims, and what would falsify us.

---

## §11 — VENUE STRATEGY

| Venue | Fit | Timing |
|---|---|---|
| **NeurIPS 2027 Evaluations & Datasets** | Primary. Track exists precisely for evaluation-as-object-of-study. | ~May 2027 |
| **JMLR / TMLR** | The full methodological treatment, no page limit, for T-A→T-H plus E-A/E-B. | Rolling |
| **ICML 2027** | If the theory (T-A/T-B/T-C) grows enough to stand alone. | ~Jan 2027 |
| **AgentEvalSci 2026** | Early visibility for the Phase-1 result only. Non-archival, does not block the above. | Oct 2026 |
| **FAccT / AIES** | Fallback if framing drifts toward audit and accountability. | — |

---

## §12 — KILL CRITERIA

Written before investment, as always.

1. **E-A shows scorer width ≪ sampling width across benchmarks.** The correction is real
   but negligible. Publish a short honest negative result; stop the program.
2. **T-B's Λ̃ is infinite for realistic parameters.** No impossibility theorem. Keep the
   finite-sample story, drop the headline claim.
3. **T-C shows correlated error cancels almost entirely.** The differential component is
   small, Case A dominates, published rankings are largely safe. Report it — it is a
   genuine, citable, field-correcting negative result and more useful than a manufactured
   positive one.
4. **T-D shows reference error is comparable to scorer error.** The measurement chain is
   unreliable end to end. Pivot to that paper; it is bigger, not smaller.
5. **E-H shows execution-scored tasks are equally unstable.** The extraction mechanism
   story is wrong. Stop and re-diagnose before writing.
6. **E-C's predictor achieves AUC ≈ 0.5.** Drop the triage claim and the mechanism story
   weakens; the paper survives but is smaller.
7. **Someone publishes the SSM-for-scorers result first.** Set an alert on citations to
   `2607.02104` and `2606.15031`. Pivot to the empirical corpus, which retains value
   regardless.

---

## §13 — APPLICATION-FACING DELIVERABLES

The research program runs past the Nov–Dec 2026 application deadlines. The two must be
separated cleanly and honestly.

**Listable by 1 Dec 2026 (Phase 1 + first Phase 2 results):**
- arXiv preprint of the Phase-1 result (real, done, defensible)
- `github.com/Rajveer-code/flipbudget` — 20 commits, tested package
- `huggingface.co/datasets/Rajveer-code/flipbudget-results` — live
- `huggingface.co/spaces/Rajveer-code/flipbudget-leaderboard` — live
- AgentEvalSci submission (if remote presentation is approved)
- **E-A's dominance result if it lands by mid-November** — the single highest-value
  addition to the application, because it is one sentence a professor remembers

**Not listable by then, and should not be implied to be:** the full theory program,
NeurIPS/JMLR submission, the large human audit.

The honest CV line in December is *"first author, preprint + released dataset, package,
and public audit tool; extended methodological version in preparation."* That is
accurate and strong. Claiming the flagship exists in December would not be.

---

## §14 — EXECUTION ORDER

Strictly by information gain per unit time, not by paper order.

**Tier 1 — do first, they gate everything**
1. **E-A** dominance study (decides whether the program is worth running)
2. **T-C** heterogeneity/correlation (decides whether the effect survives a correct model)
3. **E-E** format-conditional differential error (decides whether there is a mechanism)

**Tier 2 — the contribution**
4. **T-A** Scorer Sensitivity Model + **T-H** sharpness
5. **T-B** design sensitivity theorem
6. **E-C** scorer-failure prediction
7. **E-H** execution control

**Tier 3 — the defence**
8. **T-D** imperfect reference · **T-E** verification bias · **T-G** studentized inference
9. **E-D** adversarial suite · **E-B** scale-out
10. **H-A–H-F** the large human audit

**Tier 4 — extension**
11. **T-F** probability reporting · **E-F** drift · **E-G** judges · **E-I** replication
12. **S2–S4**, **B1–B3**, **D1–D4**

---

## §15 — HONEST ASSESSMENT

**What Phase 1 actually is:** a competent, unusually well-verified audit with one real
empirical result and two real mechanism findings. Publishable at a workshop. Not
exceptional.

**What would make it exceptional, in order:**
1. **E-A** — if scorer-induced uncertainty is routinely larger than the sampling
   uncertainty the field reports, that is a finding the rank-interval literature must
   respond to. One number. Highest leverage in this document.
2. **T-B** — a short impossibility theorem is the most citable object available here.
3. **E-C** — a working predictor turns the paper from a critique into a tool.

**The honest risk:** three of the seven kill criteria (1, 3, 5) would each substantially
deflate the contribution, and all three are live. Phase 1 has not tested any of them.
Tier 1 exists to find that out in weeks, not months.

**What I would not do:** add experiments to make the paper look larger. §4 already
excludes five tempting-but-low-value directions. Every item above has a stated objection
it kills and a stated way it could change the conclusion. Anything that cannot state
both should be cut.
