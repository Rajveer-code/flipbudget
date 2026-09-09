# PREREGISTRATION — Flip Budget extension

Committed before any **new** labelling occurs, per `PLAN_FLIPBUDGET.md` §4 (H1).
Re-aggregation of already-collected labels (per-model re-slicing of the existing
400-item MATH-Hard key) is not new labelling and is not gated by this document —
only sheets going to a labeller for the first time are.

> **Terminology note, matching the convention already established in this repo's
> `PREREGISTRATION.md` and `PREREGISTRATION_AUDIT.md`**: "pre-registration" here
> means committed to version control before the run, not lodged with an external
> registry (OSF/AsPredicted). This document is signed with a git tag as its
> verifiable timestamp, exactly as the two documents it extends were.

**This document extends, and does not replace, `PREREGISTRATION_AUDIT.md`.** That
document's commitments — the 400-item MATH-Hard frame, its three strata
(`credited`/`wrong_parsed`/`unparsed`), its design weights, its labelling protocol,
its overlap-for-reliability subsets, its "what would make this null" section — stand
unchanged. Everything below is additional, driven by `PLAN_FLIPBUDGET.md`'s four
corrections.

---

## 1. Held-out design for the leaderboard-consequence claim (fix 4)

**Commitment, before E5 is run:** for MATH-Hard, the 400 items already drawn into
the human audit are **excluded** from the benchmark-level `â` computation used for
any "headline" leaderboard verdict in E5. For those 400 items, `Y*` is directly
known from the human label — use it directly, apply no correction. For the
remaining (non-audited) items, apply the correction `A*=(a−α̂)/(1−α̂−β̂)` using
`α̂,β̂` estimated **only** from the 400-item audit.

**The held-out predictive check this enables** (committed now, not decided after
seeing results): compare, on the 400 audited items themselves, the `Δ` the
audit-derived correction *would have predicted* for those items' scorer verdicts
against the `Δ` computed *directly* from their known `Y*` labels. Report both.
Disagreement between them is a genuine finding about the correction's real-world
predictive validity, not an error to explain away.

## 2. Model as an explicit reporting dimension (fix 4)

**Commitment:** re-slice the existing 400-item MATH-Hard key
(`results/analysis/mathhard_labelling_key.json`, confirmed 2026-09-09 to carry a
`model` field per item) by model, using the same design weights already computed
per stratum/subject/length-quartile cell in `mathhard_frame.json`, restricted to
each model's subset. Horvitz–Thompson estimators are valid for any subpopulation
under the same recorded inclusion probabilities — no new sampling theory is needed,
only a new aggregation.

**Real per-model counts, computed 2026-09-09, before any modelling choice was
made:** 27 of 28 roster models have ≥1 audited item; **min 5, median 11, max 48.**
Full distribution logged in `PLAN_FLIPBUDGET.md` §11.

**Commitment on the estimator, decided now because it must not be tuned after
seeing which models look interesting:** the **primary reported per-model estimate
is partial-pooled** (empirical-Bayes shrinkage of each model's raw rate toward the
stratum-pooled rate already in `mathhard_human_margins.json`, shrinkage weight set
by relative precision — a model with n=48 shrinks little; a model with n=5 shrinks
close to the pooled rate). The **raw, unpooled per-model rate is reported alongside
it in every table**, never suppressed, so a reader can see exactly how much
shrinkage moved each number.

**Escalation rule, decided now:** if partial pooling collapses every model's
estimate to within its own Monte-Carlo noise of the pooled rate — i.e., no model is
distinguishable from another after shrinkage — H2 (new labelling) becomes required,
not optional, with target size set by a power calculation against the *observed*
`unparsed_rate` spread already in `e3_roster.json` (0.0 to 1.0 on one MMLU variant),
not guessed in advance. This is Kill Criterion 6 in `PLAN_FLIPBUDGET.md` §10.

## 3. T3/T5 joint uncertainty procedure (fixes 2, 3)

**Commitment on method, before any coverage number is computed:** the paired
item-level bootstrap (resample benchmark items with replacement for `â₁,â₂`;
independently resample the held-out audit fold, respecting design weights, for
`α̂,β̂`) is the **primary** procedure. The delta-method variance is a **cross-check
only** — reported alongside, never substituted if the two disagree. A disagreement
between delta-method and bootstrap variance is reported as a finding, not silently
resolved in favor of whichever is smaller.

**Commitment on the flip-budget CI:** the **one-sided lower 5th-percentile bound**
from the bootstrap distribution of the flip-budget statistic (T5) is the number
used in every E1/E4/E5 go/no-go judgment. Not the point estimate, not a two-sided
interval — the conservative lower bound, because the decision-relevant question is
"how small could the true flip budget be," and a two-sided interval would
understate that risk in the direction that matters.

**Degenerate-case rule, decided now:** if the raw comparison is already statistically
inconclusive at `δ_α=δ_β=0` (ordinary sampling noise alone), report
"already inconclusive absent differential error," never a flip-budget number for
that pair. Deciding this rule now, rather than when the first degenerate pair is
actually encountered, is what keeps it from becoming a discretionary call made
under the influence of a specific result.

## 4. Criterion-alignment control on execution-scored tasks (fix 1)

**Commitment:** `α,β` on execution-scored tasks are measured via the identical
human-audit procedure used for extraction-scored tasks (same blind protocol: the
labeller sees the question and response, not the gold answer or which paradigm
condition it belongs to). **No value is assumed to be zero before labelling.** The
two-part falsifiable prediction — stated now, not adjusted afterward:

1. `α,β` on execution-scored tasks are small relative to extraction-scored tasks
   (paradigm main effect).
2. `α,β` on execution-scored tasks are **approximately non-differential across
   models** with different output verbosity (the model-interaction term that Case A
   vs. Case B actually turns on).

If (1) holds but (2) fails — execution scoring is low-error but still differential —
the mechanism story (extraction specifically, as opposed to scoring in general, is
what breaks rankings) is wrong, and `PLAN_FLIPBUDGET.md` Kill Criterion 2 applies.

## 5. What would make each of these null, stated now

Following the convention of `PREREGISTRATION_AUDIT.md`'s own closing section:

- If per-model shrinkage still separates models cleanly (informative differential
  misclassification, real spread survives pooling) — strengthens the program.
- If shrinkage collapses everything to the pooled rate — Kill Criterion 6, escalate
  to H2, not a failure of the design, a real finding that current audit density is
  insufficient.
- If the held-out predictive check (§1) shows the audit-derived correction
  mispredicts the directly-known `Δ` on its own held-out items — a real finding
  about the correction's practical validity, reported honestly, not suppressed.
- If execution-scored `α,β` turn out differential (§4) — the mechanism claim
  narrows or breaks; report which.

---

*Committed 2026-09-09, alongside `PLAN_FLIPBUDGET.md` v1.1, before
`scripts/fb_t1_symbolic.py` or any new labelling sheet exists. The per-model count
computation in §2 is descriptive bookkeeping over data already on disk (the 400
items and their labels were drawn and labelled under `PREREGISTRATION_AUDIT.md`
before this document existed) — it draws no new sample and shows no new item to
anyone.*
