# MASTER PLAN v1.1 — Scorer-Induced Partial Identification of Benchmark Comparisons
## ("The Flip Budget")

**v1.1 · 2026-09-09.** Supersedes `_MASTERPLAN_FLIPBUDGET.md` v1.0 (in
`masters\LATEST_MANUSCRIPTS_FINAL\`). This is now the canonical copy — it lives in
the repo it governs. **Frozen after this revision**: do not add new research
directions unless an experiment in §3 forces a pivot (§10 states exactly which
outcomes count as forcing one).

---

## CHANGELOG v1.0 → v1.1

Four corrections, all user-directed, all real statistical defects in v1.0:

1. **E3's execution-scoring claim was overclaimed.** v1.0 said execution-based
   scoring has `α=β=0` and called it a "negative control." That is an unmeasured
   assertion — exactly what `D:\CLAUDE.md` §2.2 forbids. **Fixed**: reframed as a
   *criterion-alignment control* (§3, E3). `α, β` on execution-scored tasks are
   **measured** via the same human-audit procedure as everything else, never
   assumed. The falsifiable prediction is narrowed to what T2 actually needs: small
   **and non-differential** across models, not zero.
2. **T3 treated audit-estimated `α, β` as known constants.** They are themselves
   binomial proportions estimated from a finite human-audit sample and carry their
   own sampling error — often the *dominant* source of uncertainty, since audit
   samples (hundreds) are far smaller than benchmark samples (thousands). **Fixed**:
   T3 rewritten to jointly propagate benchmark-sampling uncertainty and
   audit-sampling uncertainty via delta method (closed form) and a paired
   item-level bootstrap (primary), matching the DeLong/paired-resampling convention
   already used for AUC comparisons in P1.
3. **The flip budget had no uncertainty treatment of its own.** It was computed
   from point estimates of `Δ*`, making it a plug-in statistic dressed as a fixed
   quantity. **Fixed**: new task **T5** — bootstrap the flip budget itself from the
   same replicates T3 produces, report a conservative one-sided lower confidence
   bound (the decision-relevant direction: how small could the true flip budget be),
   and an explicit rule for the degenerate case where the raw comparison is already
   statistically inconclusive before any differential-error argument.
4. **Circularity risk between the audit sample and the "headline" claim it feeds.**
   If the same human-labelled items are used both to estimate `α, β` and to compute
   the corrected leaderboard verdict for those same items, the result is
   self-referential — structurally the same problem cross-fitting solves in double
   machine learning, which this portfolio already uses (P1's `CausalForestDML`,
   5-fold). **Fixed**: new methodology section (§3.5) — audited items are excluded
   from the "headline" `â` computation (their `Y*` is directly known, no correction
   needed) and non-audited items are corrected using **held-out** `α̂, β̂` estimated
   only from audit data, extending the existing pre-registration design already in
   this repo (`PREREGISTRATION_AUDIT.md`) rather than inventing a parallel one.

**Discovered while implementing fix 4, not scope creep — a direct consequence of
checking real data before writing the fix (verified 2026-09-09):**

- The existing MMLU human audit (`results/analysis/human_labels.json`) has **48
  labelled items across 3 models** — mean ≈16 items per model.
- The existing MATH-Hard human audit (`PREREGISTRATION_AUDIT.md`, 400 items,
  executed — `results/analysis/mathhard_human_margins.json` has real bootstrap
  bounds) **does** carry a `model` field per labelled item
  (`mathhard_labelling_key.json`, checked directly) — re-slicing by model is
  possible with zero new labelling. Real distribution across the 400 items,
  computed 2026-09-09: **27 of 28 roster models have ≥1 audited item; min 5,
  median 11, max 48 per model.** `mathhard_human_margins.json` itself reports only
  stratum-pooled rates — it has never been re-sliced this way before.
- **Raw per-model `α̂_j, β̂_j` from either audit would have unusably wide CIs** —
  median n=11 is barely a handful of Bernoulli trials.
  Default fix, stated now rather than discovered mid-sprint: **partial pooling**
  (empirical-Bayes shrinkage) of each model's estimate toward the benchmark-level
  pooled margin, shrinkage weight set by relative precision (James–Stein-style).
  This is a *proposed default, not a blocking question* — reversible, stated
  explicitly per `D:\CLAUDE.md` §3 ("propose them and proceed — don't block on
  approval for reversible work"). Override by saying so.
- **Independent, real evidence that differential misclassification is not
  hypothetical**, from `results/analysis/e3_roster.json` (14 models, both MMLU
  variants, already computed): per-model `unparsed_rate` on
  `mmlu_flan_n_shot_generative` ranges from **0.0** (`gemini-3.1-flash-lite`) to
  **1.0** (`groq/qwen3.6-27b`); on `mmlu_flan_cot_zeroshot`, from **0.0**
  (`gemini-3.6-flash`, `gemma-4-31b-it`) to **0.91** (`groq/qwen3.6-27b`). Already
  counted: **13 and 15 pairwise rank inversions out of 91 pairs** across the two
  variants when comparing `strict` vs `robust` scoring, with a permutation test
  already run on one (`τ=0.133, p=0.554` — strict-vs-robust ordering statistically
  indistinguishable from random). **E1's pilot does not start from zero — this is
  already most of a pilot on two benchmarks.** Use it; do not recompute it.

---

## §0 — How to use this document

Same rules as v1.0, restated because this is the frozen copy:

1. Follow `D:\CLAUDE.md`. Especially §2.2 (never invent numbers), §2.4 (verify
   before claiming done), §6 (code quality bar), §12 ("if you are a smaller model:
   do not improvise, one task at a time, verify after every step").
2. Every task has an ID, a **Do**, and a **Verify**. Done only when Verify has
   actually run and its output is shown.
3. Unknown numbers get `[PLACEHOLDER: what is needed + how to get it]`. Never a
   plausible guess.
4. Results to disk as JSON before prose.
5. Check the box in §9 when a task's Verify passes.
6. **E1 is a go/no-go gate.** Do not proceed past it to the large-scale
   experiments without reporting the result. See §10.

**State**

| What | Path |
|---|---|
| This plan (canonical) | `D:\Projects\knowledgeshift\PLAN_FLIPBUDGET.md` |
| Superseded copy | `C:\Users\Asus\Downloads\masters\LATEST_MANUSCRIPTS_FINAL\_MASTERPLAN_FLIPBUDGET.md` — leave a one-line pointer there, do not maintain two live copies |
| New scripts | `D:\Projects\knowledgeshift\scripts\fb_*.py` |
| New results | `D:\Projects\knowledgeshift\results\flipbudget\*.json` |
| Pre-registration | `D:\Projects\knowledgeshift\PREREGISTRATION_FLIPBUDGET.md` (new, extends `PREREGISTRATION_AUDIT.md`'s conventions — do not duplicate its design-weight machinery, reference it) |
| Paper | `D:\Projects\knowledgeshift\paper\agentevalsci2026.tex` |
| Package | `D:\Projects\knowledgeshift\scoretrace\` |

**Existing assets — verified present 2026-09-09, do not rebuild:**
`results/analysis/human_labels{,_l2,_l3,_majority}.json` (48 MMLU items, 3 models),
`adjudicator_three_way.json`, `mathhard_human_margins.json` (400-item bootstrap
bounds, stratum-pooled, **not** per-model), `mathhard_frame.json`,
`PREREGISTRATION_AUDIT.md` (the existing 400-item design — extend it, do not
duplicate), `b0_scores.json` / `e3_roster.json` (14-model roster, per-model
`unparsed_rate` and rank-inversion counts already computed), `e4_candidates.json`,
`extractor_zoo.json`, `census_lighteval.json`, `census_version_drift.json`,
`paradigm_breakdown.json`.

**Hardware:** i7-13650HX, RTX 4060 8 GB, Windows. Python 3.13.12, sympy 1.13.1,
numpy 2.4.4 confirmed installed. No experiment here needs a GPU.

---

## §1 — The measurement model (unchanged from v1.0 — this math was already correct)

`n` items, model `M`, scorer `s`. `Y*_i ∈{0,1}` latent semantic correctness;
`Ŷ_i∈{0,1}` scorer verdict; unparseable is recorded as `Ŷ=0`.
`A*=(1/n)ΣY*_i` (target), `Â=(1/n)ΣŶ_i` (published).

`α = P(Ŷ=1|Y*=0)` false credit. `β = P(Ŷ=0|Y*=1)` false miss (absorbs unparsed).

`E[Â] = A*(1−β)+(1−A*)α ⟹ A* = (a−α)/(1−α−β)` for `α+β<1`, `a=E[Â]`.

Classical binary-misclassification correction — cite **Bollinger (1996)**,
**Molinari (2008, *J. Econometrics*)**, **Imbens & Manski (2004)**,
**Stoye (2009)** in the first two pages. Not new. What follows is.

**Two-model comparison, same scorer.**

*Case A — non-differential* (`α₁=α₂=α, β₁=β₂=β`):
`Δ*=A*₁−A*₂=(a₁−a₂)/(1−α−β)`. Attenuated but **sign-preserved**:
`sign(Δ*)=sign(a₁−a₂)`. Under shared scorer error, rankings survive; only the gap's
magnitude is wrong.

*Case B — differential* (`α₁≠α₂` or `β₁≠β₂`): rankings can invert. Define
`δ_α=α₁−α₂`, `δ_β=β₁−β₂`.

**Flip budget**: the smallest differential misclassification `(d_α,d_β)` (report
along a declared path, e.g. `d_α=d_β=d`) that puts `0` inside the identified set for
`Δ*`. Same family as Oster's δ and the epidemiological E-value — both cited widely
because they convert "could this be confounded?" into one interpretable number.
Rajveer has already used Oster bounds (P1) — this is continuous with his own prior
work, not a new vocabulary.

**Novelty positioning, comparison table, kill criteria, venue analysis (§8 of
v1.0)** — **unchanged, carried forward without modification.** Reload from
`_MASTERPLAN_FLIPBUDGET.md` §1.5, §8, §10 if this file is read standalone; not
reproduced here to keep this document to its actual deltas plus the parts that
changed.

---

## §2 — Theory tasks

**T1 — Identified set for a single model.** *Unchanged from v1.0.* Prove the
monotonicity lemma and the interval-at-corners result for `A*` given `α∈[0,ᾱ]`,
`β∈[0,β̄]`. **This task treats `α,β` as known bounds — the pure identification
exercise.** Where they come from (a priori bounds vs. audit estimates) and how
their own uncertainty propagates is T3/T5, not T1. State this distinction
explicitly in the write-up so a reader does not conflate the two layers.
Verify: `scripts/fb_t1_symbolic.py` — sympy derivation + numerical grid check to
1e-9.

**T2 — The comparison theorem.** *Unchanged.* Case A/B as in §1. Closed form or
one-dimensional root-find for the flip budget.
Verify: `scripts/fb_t2_flipbudget.py` — 10,000 simulated draws confirm the flip
threshold empirically.

**T3 — Inference for the identified set. REWRITTEN (fix 2).**

The naive approach — plug in point estimates `α̂,β̂` and treat them as exact — is
wrong. `α̂,β̂` come from a finite human-audit sample and carry their own binomial
sampling variance, typically **larger** than the benchmark-level sampling variance
of `â` because audit samples (tens to low hundreds per model, per the Changelog) are
far smaller than benchmark samples (thousands).

Do:
1. **Delta method (closed form).** For `g(a,α,β)=(a−α)/(1−α−β)`:
   `∂g/∂a=1/(1−α−β)`, `∂g/∂α=(a−1+β)/(1−α−β)²`, `∂g/∂β=(a−α)/(1−α−β)²`
   (the `∂g/∂α` sign matches T1's Lemma 1 — cross-check, do not re-derive
   independently and let it disagree).
   `Var(ĝ) ≈ (∂g/∂a)²Var(â) + (∂g/∂α)²Var(α̂) + (∂g/∂β)²Var(β̂)`, cross-covariance
   terms **zero by construction** if the held-out design in §3.5 is followed
   (benchmark data and audit data for the correction applied to it come from
   disjoint items). For `Δ*=g₁−g₂`: `Var(Δ̂*)=Var(ĝ₁)+Var(ĝ₂)` **only if** items are
   not shared between the two models' variance terms — they usually are (same
   benchmark items scored by both models), which makes this a **paired** comparison.
   Do not use the independent-sum formula without checking; use the paired
   bootstrap below as primary and the delta method as a cross-check.
2. **Paired item-level bootstrap (primary).** Resample **items with replacement**
   (not each model's responses independently) to get bootstrap replicates of
   `â₁,â₂` — this is the same paired-resampling logic already used for AUC
   comparisons in this portfolio (DeLong-style, P1/P9). **Separately and
   independently**, resample the held-out audit fold(s) (§3.5) with replacement,
   respecting strata and IPW weights, to get bootstrap replicates of `α̂,β̂` per
   model. Recombine via `g()` for each replicate to build the bootstrap
   distribution of `Δ̂*`. Percentile CI.
3. Report the **ratio** of this correctly-propagated interval's width to the
   naive sampling-only width the field currently reports — derive it, do not
   assert it as in v1.0's rejected additivity claim.
Verify: `scripts/fb_t3_coverage.py` — 2,000 replications, nominal 95%, empirical
coverage ≥ nominal, reported with its own Monte-Carlo CI. Cross-check delta-method
variance against the bootstrap's empirical variance; they should approximately
agree — if they do not, that disagreement is itself a diagnostic to report, not to
suppress.

**T4 — Sharpness.** *Unchanged in substance.* Note explicitly: sharpness here
concerns T1's pure identified set (known `α,β`). Once `α,β` are estimated, T3's
confidence set is the object with actual coverage guarantees; T4 does not need to
re-derive sharpness for that layer.

**T5 — Flip-budget inference. NEW (fix 3).**

The flip budget computed from a point estimate of `Δ̂*` is itself a plug-in
statistic with its own sampling distribution once `α̂,β̂` carry uncertainty.

Do: for **each** bootstrap replicate produced in T3.2, recompute the flip budget
(given that replicate's `â₁,α̂₁,β̂₁,â₂,α̂₂,β̂₂`, find the smallest `d` putting `0` in
the identified set for `Δ*`). This yields an empirical distribution of the
flip-budget statistic. Report:
- point estimate (median across replicates),
- a **one-sided lower confidence bound** (e.g. 5th percentile) as the primary,
  decision-relevant number — "with 95% confidence the true flip budget is at least
  X" is the conservative framing; a small flip budget means fragile,
- explicit degenerate-case rule: if the raw comparison `a₁` vs `a₂` is already not
  statistically distinguishable under ordinary sampling noise **before** any
  differential-error argument (i.e., 0 is already inside the T3 interval at
  `δ_α=δ_β=0`), report **"already inconclusive absent differential error"**, not a
  flip-budget number — avoids a divide-by-zero/degenerate output and avoids
  implying precision that is not there.
Verify: `scripts/fb_t5_budget_ci.py` — bootstrap distribution of the flip budget on
at least one real pair from the MMLU roster data already on disk (`e3_roster.json`)
where a rank inversion is already documented, plus one pair with no documented
inversion, as a positive/negative sanity pair.

---

## §3 — Experiments

**E1 — The pilot. GO/NO-GO.**

**Already substantially pre-computed — verified 2026-09-09.** `e3_roster.json`
already gives, for 14 models on both MMLU variants: per-model `unparsed_rate`
(0.0–1.0 spread on one variant, 0.0–0.91 on the other), 13 and 15 pairwise rank
inversions out of 91 pairs, and one permutation test already run
(`τ=0.133, p=0.554`). **This is not a fresh pilot — it is most of one, already on
disk.** E1's job is now: (a) apply T1/T2's actual flip-budget formula (not just
raw inversion counts) to these same 91 pairs per variant, using the audit-estimated
`α̂_j,β̂_j` (partial-pooled per the Changelog default) rather than `unparsed_rate`
alone as a proxy for `β`, and (b) add a third benchmark beyond the two MMLU
variants once D4 (§3.4-adjacent, below) confirms what else has usable response-level
data.
Verify: `results/flipbudget/e1_pilot.json` — per-pair flip budgets and T5 lower
bounds for all 91×2 pairs, plus the third benchmark once identified.
**Gate: if the fraction of pairs whose T5 lower-confidence-bound flip budget is
below the observed differential misclassification spread is < 5% on all
benchmarks, STOP** — the correction is real but negligible in practice; see §10.

**E2 — Synthetic ground-truth validation.** Unchanged from v1.0. Plant responses
with known `Y*`, sweep planted `(α,β)`, check T3's interval covers truth at nominal
rate. Costs no API spend, fully controlled — do this early, it is the cheapest
strong evidence available.

**E3 — Multi-paradigm sweep, execution as CRITERION-ALIGNMENT CONTROL. REWRITTEN
(fix 1).**

v1.0 claimed execution-based scoring has `α=β=0` and called it a negative control.
**That is an unmeasured assertion and is dropped.** Execution scoring (unit tests,
exact/numeric equality, code execution) removes the specific mechanism under
study — free-text answer extraction — because the verdict does not depend on
locating a substring in unstructured output. **This does not guarantee `α=β=0`**: an
incomplete test suite can pass a semantically wrong solution (false credit,
contributes to `α`) or a correct solution can fail on a harness/formatting
technicality (false miss, contributes to `β`) — exactly the defect class Auto
Benchmark Audit (`2605.26079`) catalogues in 25.7% of tasks it audited.

Do: apply the **same** human-audit procedure to execution-scored tasks as to
extraction-scored ones — measure `α,β` for real, do not assume. The falsifiable
prediction, narrowed to what T2 actually needs: on execution-scored tasks, `α,β`
should be (i) small in absolute terms relative to extraction-scored tasks, and,
decisively, (ii) **approximately non-differential across models** regardless of
output verbosity — a compiler does not care how long the reasoning was. Condition
(ii), not a zero-error claim, is what Case A needs for rankings to survive.
Existing input: `paradigm_breakdown.json` already reports 924 BLEU/chrF/ROUGE/
execution tasks at 0% *extraction*-vulnerability (a different, narrower measurement
than the full audited `α,β` this task now requires — do not conflate the two;
`paradigm_breakdown.json`'s 0% is a necessary input to this task, not a substitute
for it).
Verify: `results/flipbudget/e3_paradigms.json` — measured `α,β` per paradigm
including execution, with the differential-across-models check explicit.
**If execution-scored tasks show differential misclassification comparable to
extraction-scored ones, the mechanism story is wrong and must be rewritten — a
real risk, and finding it is a success, not a failure.**

**E4 — Differential misclassification, measured.** Do: per-model `α̂_j,β̂_j` from
the (partial-pooled, per Changelog) audit estimates. Report the spread — that
spread is `d`, what the flip budget is compared against. Break down by output-format
covariates (response length, chain-of-thought presence, boxed-answer usage) — the
`unparsed_rate` numbers already in `e3_roster.json` are a documented, real starting
correlate.
Verify: `results/flipbudget/e4_differential.json` — per-model `(α̂_j,β̂_j)` with T3
CIs (partial-pooled and raw, both reported so the shrinkage's effect is visible, not
hidden), figure of `α̂_j` vs. mean response length.

**E5 — Consequence on a public leaderboard.** Do: for MATH-Hard (400-item audit
already exists, 28-model roster already exists), apply the **held-out** design of
§3.5 — audited items excluded from the headline `â`; non-audited items corrected
using audit-only `α̂,β̂`. Report identified/unidentified per published pairwise
ordering.
Verify: `results/flipbudget/e5_leaderboard.json`, Hasse diagram of the resulting
partial order.

**E6 — Version/temporal drift.** Unchanged. Input: `census_version_drift.json`.

**E7 — Re-analysis of published rank-interval methods.** Unchanged, still demoted
below E1–E5 as advised. Reproduce `2606.08679` / `2607.16259` exactly first; extend
respectfully or drop if not reproducible.

**Rejected, unchanged from v1.0:** another judge-agreement study, a contamination
study, an IRT treatment, a new task benchmark, a construct-validity position paper.

### §3.5 — Sample-splitting and reweighting design (fix 4, new)

**Extends `PREREGISTRATION_AUDIT.md`'s existing design — do not build a parallel
system.** That document already establishes, for the 400-item MATH-Hard audit,
**design weights** (`population_in_cell / sample_target_in_cell`, a
Horvitz–Thompson-style inverse-inclusion-probability weight, i.e. the same idea as
IPW under a different name already committed to in this repo) and a
Clopper–Pearson/weighted-bootstrap estimator. **Use that machinery. Add exactly two
things it does not yet have:**

1. **A held-out split, orthogonal to the existing reliability-overlap split.**
   The existing 150/75 overlap subsets are for **inter-rater reliability**, not for
   avoiding circularity — a different purpose. New requirement: for any benchmark
   where audited items are a literal subset of the benchmark items feeding a
   "headline" leaderboard claim (true for MATH-Hard), **exclude audited items from
   the `â` computation entirely** (their `Y*` is directly known — use it directly,
   no correction needed for those items) and compute the correction applied to
   **non-audited** items using `α̂,β̂` estimated **only** from the audit sample. This
   is simpler than K-fold cross-fitting, fully closes the circularity gap, and adds
   a genuine **held-out predictive check** as a byproduct: compare what the
   audit-derived correction *would have predicted* for the audited items' own `Δ`
   against their *directly known* `Δ` (since `Y*` is known there) — a real-data
   analogue of E2's synthetic check.
2. **Model as an explicit stratification/reporting dimension**, for the purpose of
   E4's per-model `α_j,β_j`. The existing design's cells are `(subject ×
   length-quartile)`, pooled over models. Re-slice the **already-labelled** items by
   the model field each labelled item already carries (confirm this field exists
   before assuming it — check `mathhard_labelling_key.json` structure as the first
   sub-task) and apply the existing design weights restricted to each model's
   subset — Horvitz–Thompson estimators remain valid for any subpopulation using the
   same recorded inclusion probabilities. **Given the resulting per-model n is thin
   (≈14–16), use partial pooling (empirical-Bayes shrinkage toward the
   benchmark-pooled rate, precision-weighted) as the default reported estimator,
   with the raw unpooled per-model rate reported alongside for transparency.**

**If per-model n is too thin even for shrinkage to produce informative separation
between models** (e.g. shrinkage collapses every model to the pooled rate,
`Var(α̂_j)` too large relative to `Var(δ_α)` to detect any real difference) — this is
now a named entry in the kill/escalation criteria, §10.

---

## §4 — Human validation

**H1 — Pre-register before labelling. THIS TASK, PARTIALLY EXECUTED TODAY.**
New file `PREREGISTRATION_FLIPBUDGET.md` (§4 of this plan's own execution log,
below) covers: the §3.5 held-out design, model as a reporting dimension, the
partial-pooling default and its threshold, the T3/T5 bootstrap procedure, and E3's
measured (not assumed) execution-paradigm `α,β`. It explicitly **extends**
`PREREGISTRATION_AUDIT.md` rather than replacing it — the original document's
commitments (strata, sample sizes, labelling protocol, "what would make this null")
stand unchanged.
Verify: committed to git with a signed tag before any *new* labelling occurs. Any
re-aggregation of **already-collected** labels (e.g., per-model re-slicing of the
existing 400) is not new labelling and is not gated by this — only new sheets going
to a labeller are.

**H2 — Expand the adjudicated sample where the thinness diagnosis (§3.5.2) shows
it is actually needed** — i.e., only after seeing whether partial pooling already
produces informative per-model separation. Do not commit to a fixed expansion size
before that check; state it as `[PLACEHOLDER: target n per model, decided after
E4's first partial-pooled pass shows whether more data would actually change the
answer]`.

**H3 — Cross-vendor adjudication.** Unchanged; already exists for the current
sample (`adjudicator_three_way.json`).

---

## §5 / §6 / §7 / §8 — Datasets, software, paper, venues

**Unchanged from v1.0.** D1/D2 datasets, S1/S2 software, paper structure, venue
table (AgentEvalSci primary — abstract 20 Oct, full 25 Oct, symposium 20 Nov;
NeurIPS 2027 E&D stage 2; SIGMETRICS rejected as a fit). Reload from
`_MASTERPLAN_FLIPBUDGET.md` §5–§9 if needed; the four corrections do not change any
of these decisions, only the theory (§2) and the audit design (§3.5) that feeds
the experiments.

---

## §9 — Schedule (16 → ~18 days, and why)

The four corrections add real work: T3 grows from a one-day task to closer to
1.5–2 days (joint delta-method + paired-bootstrap implementation, not a single
formula); T5 is new (~0.5–1 day); E3 needs an actual audit pass on execution tasks
instead of an assumption; §3.5's held-out design and per-model re-slicing add
roughly a day to the H1/H2/E1 chain. **Given explicit "substantially more time"
approval, absorbing ~2 extra days for correct statistics is the right trade and I
am not going to compress it back to 16 to hit a round number.**

- [x] **Pre-flight (2026-09-09, this session)** — real-data audit of existing
      assets (§ Changelog); confirmed python/sympy/numpy on PATH; confirmed
      `PREREGISTRATION_AUDIT.md`'s design-weight convention to extend rather than
      reinvent; confirmed per-model thinness numerically (≈16/model MMLU;
      MATH-Hard: 27/28 models represented, min 5 / median 11 / max 48 per model)
      — this is why §3.5's partial-pooling default exists rather than being
      discovered mid-sprint.
- [ ] **D1 — H1 pre-registration**, extending `PREREGISTRATION_AUDIT.md`. Commit +
      signed tag before any new labelling.
- [ ] **D2 — T1** symbolic + grid verification.
- [ ] **D3–D4 — T2** Case A/B proofs + flip-budget simulation.
- [ ] **D5 — Data source audit**, formalized: which benchmarks beyond MMLU/
      MATH-Hard have usable response-level data on disk (GSM8K's `gsm8k_items_400`
      is an item bank only — question/gold, no responses — confirmed 2026-09-09;
      needs a separate scoring run or a different third benchmark).
- [ ] **D6–D7 — T3** delta method + paired bootstrap + coverage simulation.
- [ ] **D8 — T5** flip-budget bootstrap + coverage sanity pair.
- [ ] **D9–D10 — E1 pilot**: apply T1/T2/T3/T5 to the already-computed MMLU
      roster data plus the third benchmark from D5. **GO/NO-GO checkpoint — report
      before continuing.**
- [ ] **D11 — E2** synthetic validation.
- [ ] **D12–D13 — E3** criterion-alignment audit on execution-scored tasks (real
      human labelling, not assumption).
- [ ] **D14 — E4** per-model differential misclassification, partial-pooled.
- [ ] **D15 — E5** MATH-Hard leaderboard consequence under the held-out design.
- [ ] **D16 — S1/D1/D2** package + dataset release.
- [ ] **D17–D18** — write the 6-page paper.

Then: strengthen (E6, E7 if reproducible) → **20 Oct abstract → 25 Oct submission →
20 Nov symposium.**

---

## §10 — Kill criteria (extended)

Unchanged 1–5 from v1.0 (E1 negligible-budget result; E3 execution just as unstable
as extraction; T3 coverage failure; Case A dominates in practice; IELTS/LORs/SOP
always win). **New, from the real-data check today:**

6. **Per-model audit `n` is too thin for partial pooling to separate models even
   after shrinkage** — i.e., `Var(α̂_j)` after shrinkage is still large relative to
   the observed `unparsed_rate` spread (0.0 to 1.0 on MMLU, per `e3_roster.json`),
   so E4 cannot report a differential-misclassification estimate with any real
   precision. This does not kill the program — it converts H2 from optional to
   required, with a size decided by the actual shrinkage diagnostics, not guessed
   now. Report the diagnostic plainly rather than publishing an overconfident
   per-model number.

---

## §11 — Execution log (this session, 2026-09-09)

Real, verified facts established while writing this revision — not claims, results
of commands actually run:

- `git log --oneline -5` in `D:\Projects\knowledgeshift`: clean history, 4 commits
  ahead of `origin/master`, one unstaged modification
  (`results/analysis/iclr_tables.json`) unrelated to this work.
- `python --version` → `3.13.12`; `python -c "import sympy, numpy"` →
  `sympy 1.13.1 numpy 2.4.4`. Both available; T1/T2/T3/T5 scripts can run without
  new installs.
- `results/analysis/human_labels.json`: 48 keys, format
  `{benchmark}|{model}|{task}:{index}` → single-letter verdict. Benchmarks:
  `mmlu_flan_cot_zeroshot`, `mmlu_flan_n_shot_generative`. Models: `openai/gpt-5-mini`,
  `deepseek/deepseek-v4-flash`, `openai/gpt-5.6-luna`.
- `results/analysis/mathhard_human_margins.json`: real bootstrap bounds exist
  (`credited` stratum: rate 0.0314, upper-95 0.0638, n=162 of 175;
  `wrong_parsed` stratum: rate 0.0, upper-95 ≈0.0178, n=167 of 175) — **pooled by
  stratum, not by model.** Confirms the Changelog's claim exactly; not asserted from
  memory.
- `results/analysis/e3_roster.json`: 14 models, 2 MMLU task variants, per-model
  `unparsed_rate`, `robust_minus_strict_pp`, `robust_minus_flexible_pp` already
  computed; `n_pairwise_inversions: 13` (mmlu_flan_cot_zeroshot) and `15`
  (mmlu_flan_n_shot_generative) out of `n_pairs: 91`; one permutation test already
  run (`kendall_tau_strict_vs_robust: 0.133, p_value: 0.554`).
- `results/analysis/gsm8k_items_400.json`: list of 400, keys
  `item_id, question, gold` only — **no response or model field.** Not usable as an
  E1 pilot benchmark without a new scoring run. Corrects an implicit assumption in
  v1.0 that this would be trivially available.
- `results/analysis/b0_scores.json`: top-level keys `design, results, per_item` —
  not yet inspected below the second level; **flagged for D5, not yet a confirmed
  E1 source.**

---

*End of v1.1. Next action: write `PREREGISTRATION_FLIPBUDGET.md` (H1), commit +
tag, then T1.*
