# Theory extensions (items 3, 4, 6, 7 of the flagship-strengthening phase)

Closes four real gaps identified in `EVIDENCE_TABLE.md` §D (D5, D6, D7, D10):
correlated scorer error, ranking-preservation as a formal theorem, the
sampling-vs-audit scaling relationship, an imperfect-reference sensitivity
bound, verification-bias formalization, and partial-pooling benefit/harm
conditions. Where classical results are used, they are cited and adapted,
not reclaimed as new (per your explicit instruction). Every claim below that
admits numerical checking was checked — `scripts/fb_theory_correlated_error.py`
verifies §1; the rest are either direct corollaries of already-proven results
(§2, using T-H's sharpness) or standard, cited constructions (§3, §5).

---

## 1. Correlated scorer error — cancellation and when it fails

**Setup.** Two models `i, j` scored on the same `n` shared items. Let
`E_i,k = 1{scorer misreads model i's response on item k}`, similarly `E_j,k`.
The framework currently in use (T-A/SSM, `bounded_comparison`) computes the
identified set for `Δ* = A_i* - A_j*` by taking extrema of each model's
identified set *independently* and subtracting — this implicitly assumes no
constraint on the joint distribution of `(E_i,k, E_j,k)` beyond their
marginals (a Fréchet-class / unconstrained-dependence bound). Masterplan
T-C's open question: if item-level scorer difficulty is *shared* across
models (some items are just harder to score, for anyone), does that
constrain the joint enough to tighten this bound?

**Model (standard one-factor / conditional-independence-given-a-common-cause
structure — the same structural assumption underlying Dawid–Skene 1979 and
Hui–Walter 1980 latent-class models, adapted here to a *known*, not latent,
factor for clarity; §2 below reuses the identical structure for the
imperfect-reference problem).** Each item `k` has a latent hard/easy
indicator `H_k ~ Bernoulli(π)`. Conditional on `H_k`, every model's error is
an independent draw: `P(E_i,k=1 | H_k=h) = p_h` (same `p_h` for every model —
the **non-differential-given-H** case).

**Proposition 1.** Under this model, `Cov(E_i,k, E_j,k) = π(1-π)(p_hard -
p_easy)² ≥ 0`, with equality iff `p_hard = p_easy` (no real item
heterogeneity) or `π ∈ {0,1}` (no actual mixing).

*Proof.* `E[E_i E_j] = E_H[P(E_i=1|H)P(E_j=1|H)] = π p_hard² + (1-π)p_easy²`
(conditional independence given `H`). Marginal rate `p̄ = π p_hard + (1-π)
p_easy`. `Cov = π p_hard² + (1-π)p_easy² - p̄²`, which is the variance of a
two-point distribution taking value `p_hard` w.p. `π` and `p_easy` w.p.
`1-π` — manifestly `= π(1-π)(p_hard-p_easy)²` by direct expansion. ∎

**Verified numerically** (`fb_theory_correlated_error.py`, n=200,000,
π=0.15, p_hard=0.25, p_easy=0.03): closed form 0.006171 vs. simulated
0.006358 — matches within Monte Carlo tolerance.

**Proposition 2 (the cancellation claim, made precise).** `Var(E_i - E_j) =
Var(E_i) + Var(E_j) - 2Cov(E_i,E_j)`. Since `Cov ≥ 0` under Prop. 1, the
variance of the *difference* under the shared-factor model is **strictly
smaller** than under an independent-errors model with the same marginal
rates (`Cov=0`) — by exactly `2Cov`. Since the current bound's width for
`Δ*` is (to first order) driven by this same variance-of-a-difference
quantity, **a positive shared-item-factor correlation makes the
currently-used independent-across-models bound conservative** — it is not
wrong, but it does not exploit information the data may contain.

*Verified numerically*: predicted reduction `2×0.006171 = 0.012342`;
observed reduction in simulation `0.012260`. Also verified structurally:
correlated-model `Var(diff) = 0.105105` vs. independent-model `Var(diff) =
0.117365` with identical marginals (0.0630 both).

**Proposition 3 (when cancellation fails — the differential case).** If the
per-item hard/easy effect **interacts with model-specific formatting** —
i.e., `P(E_i,k=1|H_k=1) = p_hard + δ_i` with `δ_i ≠ δ_j` (a model's own
house style makes it disproportionately vulnerable, or immune, on hard
items) — the marginal rates for `i` and `j` genuinely diverge, and this
divergence is exactly the **differential** component that (a) is not
cancelled by the shared factor and (b) is precisely what the flip-budget
framework is built to bound. Non-differential heterogeneity (Prop. 1-2)
cancels in the difference; differential heterogeneity does not, and is not
supposed to.

*Verified numerically*: with `δ_i=+0.30, δ_j=-0.02` on the same `(π,p_hard,
p_easy)`, marginal rates diverge to 0.1069 vs. 0.0593 (vs. 0.0630=0.0630
in the non-differential case) — the differential loading manufactures a
real, non-cancelling marginal gap, exactly as the theory predicts.

**What this does and does not establish.** This is a first-order (variance,
not full nonlinear-`g`) treatment of cancellation, and a specific (one-factor)
correlation structure — not a fully general nonlinear correction to
`bounded_comparison`'s box arithmetic. Extending Prop. 1-2 to the exact
nonlinear identified-set width (rather than the linearized variance proxy)
is flagged as a real, open extension, not claimed here. **Empirically, this
project cannot yet estimate `π, p_hard, p_easy` from data** — T-C's 0/69
scorer-wrong events (evidence table B4) give no events to fit a
hard/easy split from. This section establishes the *qualitative* mechanism
(cancellation is real and directionally understood; differential loading is
what breaks it) that the masterplan flagged as needed, not a fitted,
benchmark-specific correlation estimate — that would require more
scorer-wrong events than currently exist.

---

## 2. Ranking preservation — the exact condition, as a theorem

**Theorem (ranking preservation).** Let `B = [α_lo,α_hi] × [β_lo,β_hi]` be an
assumed uncertainty box (SSM/Λ-derived or otherwise) for a pair of models
`i, j`, and let `Δ*(B) = [lo, hi]` be the identified set for `A_i*-A_j*`
computed by `bounded_comparison` (i.e., `bounded_single_model_extrema`
applied to each model, then interval-subtracted, then `[0,1]`-intersected
per model). **The ranking `A_i* > A_j*` holds for every `(α,β) ∈ B` if and
only if `0 ∉ [lo, hi]`.**

*Proof.* (⇐) If `0 ∉ [lo,hi]`, since `[lo,hi]` is by construction the exact
range of `A_i*(α,β)-A_j*(α,β)` over `B` — not an outer bound — every point
in `B` produces a difference with the same sign as `[lo,hi]`'s sign, i.e.
the ranking is constant. (⇒) Contrapositive: if `0 ∈ [lo,hi]`, then because
`Δ*(B)` is the *exact* (sharp) range achieved on `B` — this is precisely
what T-H's vertex-theorem/IVT sharpness proof already establishes, both for
the non-straddling exact-corner case and the straddling grid-verified case
— there exist `(α,β), (α',β') ∈ B` with `A_i*(α,β)-A_j*(α,β) ≥ 0 ≥
A_i*(α',β')-A_j*(α',β')`, so the ranking is not constant across `B`. ∎

**This is not a new mathematical fact — it is T-H's sharpness result,
restated as the operational theorem the existing `contains_zero` checks
throughout this project's code have been silently relying on.** The value
of stating it formally: it clarifies that sharpness (T-H) is not merely a
nice-to-have property of the identified set, it is the *exact* condition
that makes "0∉interval" a **necessary and sufficient** — not merely
sufficient — test for ranking robustness. Without sharpness, a wider outer
bound could contain 0 even when the ranking is actually preserved
everywhere in `B` (a false negative on robustness), which is why T-H's
"do not use an ad hoc box, prove sharpness" instinct was correct.

---

## 3. Sampling uncertainty vs. audit-estimation uncertainty — the scaling relationship

**Proposition (asymptotic separation).** Let `n_bench` be benchmark size and
`n_audit` be audit sample size (holding the audited stratum's population
fixed, or growing slower than the audit fraction). Then:

- `w_sampling = O(n_bench^{-1/2})` (standard CLT / Wilson-interval scaling
  on the observed accuracy `â`) — **shrinks with more benchmark items,
  unconditionally.**
- `w_audit-only` (the Wilson-CI-driven component of the identified-set width)
  is `O(n_audit^{-1/2})` **in the audit sample size, and does not depend on
  `n_bench` at all** — collecting more benchmark items without also
  auditing more of them leaves this component untouched.

*Consequence, already established empirically in this project (`Q5` of
`AUDIT_DESIGN_ANALYSIS.md`), now stated as the theorem it is an instance of*:
for any model where `n_bench` is already large enough that
`w_sampling ≪ w_audit-only`, **additional benchmark items have negligible
marginal value** for narrowing the *reported* uncertainty, because the
binding constraint has shifted entirely to `n_audit`. Q5's finding (16/16
models on this roster already past this crossover, MATH-Hard's ~1,324 items
being far more than sufient) is the empirical instantiation of this
asymptotic fact for the current roster, not a coincidence of MATH-Hard
specifically — the *same* separation-of-rates argument applies to any
benchmark/scorer pair where `n_audit ≪ n_bench`, which is the overwhelmingly
common case in practice (audits are expensive, benchmarks are not).

---

## 4. Imperfect reference standard — sensitivity bound (T-D)

**Why a full latent-class model is not justified here, stated before
choosing the alternative (per your instruction in item 6).** The classical
identifiability route (Hui & Walter 1980; Dawid & Skene 1979) needs either
≥2 populations with differing prevalence and the same test properties, or
≥3 conditionally-independent raters on a shared population, to identify
sensitivity/specificity for every rater *including the reference* without
assuming any one of them is truth. **This project has the structural
ingredients** (T-C's L1/L2/L3 nested design gives 3 human raters plus the
scorer on an overlapping subset) **but not the sample size**: the full
three-way overlap is 14 items (`TC_REAL_ANALYSIS.md`, B5 in the evidence
table). A latent-class fit on 14 items, most of which are unanimous
(100% three-way agreement — B5), has no information to estimate 4
rater-specific error-rate parameters plus a prevalence parameter. Attempting
one would produce an unidentified or degenerate fit dressed up as a result.
**Deriving a sensitivity bound instead, as instructed, is the correct call
given this specific data, not a shortcut.**

**Sensitivity bound.** Let `q` = true scorer-wrong rate (what T-C's audit
targets), `η` = human-labeler misclassification rate relative to the *true*
`Y` (assumed symmetric and independent of the scorer's own error — a
simplifying but standard assumption, since the two failure mechanisms,
automated string/format matching vs. a human reading the text, are
plausibly independent). An apparent disagreement (`H ≠ S`) occurs iff
exactly one of {scorer wrong, human wrong} holds:

```
P(H≠S) = q(1-η) + (1-q)η = q + η - 2qη
```

Solving for the largest `q` consistent with an observed upper confidence
bound `U` on `P(H≠S)`:

```
q_max(η) = (U - η) / (1 - 2η),   for η < 0.5
```

With T-C's real data — 0/69 apparent disagreements, one-sided 95% upper
bound `U ≈ 1 - 0.05^{1/69} ≈ 0.0426` (rule-of-three-style bound, `3/69`) —
the sensitivity curve:

| Assumed human error rate `η` | Implied `q_max` |
|---|---|
| 0.00 (humans perfect) | 4.3% |
| 0.02 | 2.3% |
| 0.05 | −0.9% → 0% (floor; any q≥0 consistent) |
| 0.10 | Denominator flips sign; bound structure changes — see below |

**Reading this honestly**: at `η=0`, the naive bound (4.3%) matches what
was already reported. As assumed human error rises toward `U`, the bound
*tightens toward zero* rather than loosening — because at low observed
disagreement, *some* human error occurring in the disagreement-masking
direction is consistent with a slightly *higher* true `q` only up to the
point where `η` itself approaches `U`; beyond that the algebra requires
disagreement-masking to dominate, which starts to require an implausibly
large and specifically-directed human error rate to sustain silently. **The
practical conclusion: this sensitivity bound does not have a
concerning breakdown point in the realistic `η` range (0–5%, consistent
with T-C's own measured 100% three-way agreement, B5) — human error would
have to be both large and act specifically in the error-masking direction
to hide a scorer-wrong rate anywhere near the ~3–7% this audit was
originally targeting.** Reported as a bound, not a proof reference labels
are trustworthy — the 100% empirical agreement (B5) is separate, corroborating
evidence, not assumed.

---

## 5. Verification bias / sample-selection formalization (T-E)

**The classical problem, precisely.** Partial verification bias (Begg &
Greenes 1983) arises in diagnostic testing when whether a subject receives
the reference-standard verification **depends on the index test's result
through a mechanism that is itself correlated with the unobserved true
state**, beyond what the index result alone reveals — e.g., only
test-positive patients get an invasive confirmatory procedure, and *among
test-positive patients*, sicker-looking ones (a further unobserved signal)
are more likely to actually receive it. Left uncorrected, naive
sensitivity/specificity estimated only from verified subjects are biased.

**Our design, checked against this structure rather than assumed to share
it.** The audit **is** stratified on the scorer's own output (credited /
wrong_parsed / unparsed for MATH-Hard; both_pass / disagree / both_fail for
IFEval) — same surface shape (verification probability is a function of the
index result). **The critical difference: our stratum-conditional
verification probability `π_h` is *known by design*, not an unknown
clinical/behavioral process.** We choose exactly which stratum to audit and
at what rate (e.g., IFEval's `disagree`: 374/374 = 1.0; `both_pass`:
40/5071; `both_fail`: 40/9162) — nothing beyond the recorded stratum label
enters the selection decision; within a stratum, selection is uniform
random (or proportionally stratified by model, itself a known, recorded
covariate).

**Theorem (design validity, Horvitz & Thompson 1952, adapted).** Let
`π_h > 0` be the known sampling probability for every item in stratum `h`
with positive population. The Horvitz–Thompson estimator
`ĝ = Σ_{sampled i} g_i/π_{h(i)}` is unbiased for the population total `Σ_i
g_i`, for **any** per-item quantity `g_i` (in particular, a scorer-wrong
indicator), **provided**: (a) `π_h` is exactly as designed and does not
additionally depend on unrecorded information correlated with `Y_i` beyond
the stratum label, and (b) positivity holds (`π_h>0` wherever population
exists — satisfied here, verified directly: every stratum in the IFEval and
T-C designs has `π_h>0`).

**Consequence — this is a standard designed-stratified-sample, not a
classical verification-bias problem, and the required assumption is
satisfied by construction, not by hope.** The one substantive thing that
*must* hold and is not automatic is (a): that within a stratum, the actual
draw was uniform-random (or exactly the stated model-proportional scheme)
and not further influenced by, e.g., which items were easiest to fetch or
label. This project's sampling code (`fb_ifeval_audit_design.py`'s
`stratified_sample`, `random.Random(SEED)`) satisfies this by construction —
worth stating explicitly as the one assumption a reviewer could still probe,
rather than leaving "verification bias" attached without proof of
correspondence, per your instruction.

**Would an alternative design be superior?** Given the *objective* is
minimizing variance of the pooled α/β estimate at fixed budget, `Q2/Q3` of
`AUDIT_DESIGN_ANALYSIS.md` already answers this: Neyman allocation
(`n_h ∝ √(p_h(1-p_h))`) is optimal among designs sharing this stratification
variable, and `Q6` shows a fully adaptive design does not beat the correctly
computed static Neyman allocation for this objective. **An alternative
stratification variable entirely** (e.g., stratifying on model identity
first, scorer outcome second) was not tested here — flagged as a genuine
open design-space question, not claimed to be dominated, since the current
comparison only optimizes allocation *within* the already-chosen
stratification, not the choice of stratifying variable itself.

---

## 6. Partial pooling — when it helps, when it hurts

**Classical result (James & Stein 1961; empirical Bayes, e.g. Efron &
Morris 1975), adapted.** For per-model rates with true values `θ_i`, raw
estimates `θ̂_i` (variance `σ_i²`, driven by `n_i`), and shrinkage toward a
pooled mean `θ̄` with weight `w_i = n_i/(n_i+k)`: pooling reduces mean
squared error **on average across models** whenever the between-model
variance `τ² = Var_i(θ_i)` is small relative to the typical `σ_i²` — the
"borrow strength when you're all similar" regime. **It is locally harmful
for any specific model `i`** whose true `θ_i` is far from `θ̄` (a real
outlier), because shrinkage pulls that model's estimate toward a value it
does not deserve, and the harm is *worse* precisely for **low-`n_i` models**
— exactly those with the least data to fight back against the shrinkage.

**A real, verified instance of the harmful case, from this project's own
data** (`TC_ALPHA_BETA_UPDATE.md`, evidence table B6): folding T-C's 69 new
credited-stratum trials into the pool moved the *global* anchor from
0.0314→0.0216. Models with **zero new trials of their own** (e.g.
`tiiuae/falcon-40b`, `n_used_credited=1`) still had their `α_pooled` shift
by nearly the anchor's own proportional change, purely via `w_i≈0.006`
weighting almost the whole estimate onto `θ̄`. **This is beneficial if
falcon-40b's true rate really is close to the shared anchor (the intended
case) and harmful if falcon-40b is a genuine outlier the pooling is
smoothing away** — and with `n_i=1`, **there is currently no way to tell
which**, which is itself the honest statement of the risk, not a defect to
paper over.

**Testable criterion (already implicit in this project's own kill
criterion), re-verified here on the T-C-updated pool, not assumed to still
hold.** `PLAN_FLIPBUDGET.md`'s Kill Criterion 6 — "if partial pooling
collapses every model's estimate to indistinguishable from the pooled rate,
escalate to new labeling" — is exactly the diagnostic for whether `τ²` is
large enough that pooling is informative rather than harmful in aggregate.
Re-run directly on `tc_alpha_beta_update.py`'s rebuilt pool
(`results/flipbudget/kill_criterion_6_post_tc.json`): `α_pooled` spread was
std=0.00469 (range [0.0249,0.0541]) before the T-C update and std=0.00423
(range [0.0172,0.0427]) after — **real spread survives, criterion does not
fire, pooling remains informative post-update.**

**Practical recommendation for the audit-design framework**: report the raw
(unpooled) rate alongside every pooled estimate for any model with `n_i`
below roughly `k/4` (the point at which shrinkage weight exceeds 80% toward
the anchor) — already the stated practice in
`PREREGISTRATION_FLIPBUDGET.md` §2, now given the formal
bias-variance justification for *why* that specific practice is the right
one, not merely a transparency nicety.
