# Audit-expansion design — computation only, zero new labels

Per TIER1_VERDICT.md point 3. Full script: `scripts/fb_audit_expansion_design.py`.
Results: `results/flipbudget/audit_expansion_design.json`. **This designs the
expansion; it does not execute it. Labelling is the user's own manual work.**

## Estimator used

Reuses the E4 pipeline's own empirical-Bayes shrinkage (`alpha_pooled`, `beta_pooled`,
`shrinkage_weight_*`, already computed and verified, not reinvented here) as the
expected-yield predictor for a new item in each (model, stratum) pool — better than a
raw per-model rate (many pools have 0-1 audited items) or a flat pooled rate (ignores
what's already been observed for well-audited models).

## E-E target: real, citable, and larger than expected

Target: **≥10 events per predictor variable** (Peduzzi, Concato, Kemper, Holford &
Feinstein, 1996 — the standard minimum-events-per-variable rule for logistic
regression). 9 features → **≥90 total wrongness events**. Currently 5.

**Design requirement, not a simplification:** new items must be spread across many
models, not concentrated in 1-2. Concentrating would reintroduce exactly the
model-vs-format confound E-E exists to rule out — an association could then be "this
is GPT-style formatting" dressed up as "this is a format effect." Each round therefore
draws one 20-item batch from **every** positive-rate pool before any pool gets a
second batch.

**Real result: 5 rounds (2700 items total) are needed to reach the clean 90-event
target**, projected cumulative 90.2. This is the honest number at the roster's
observed/pooled rates (1.6%–7.6% per item) — not shrunk to look smaller.

**A cheaper interim option, stated explicitly since 2700 items is a large ask:** round
1 alone (540 items) is projected to raise the event count from 5 to ~22 — a 4.4×
improvement, not fully EPV-clean but a large step, and a reasonable first tranche if
the full 2700-item round is more than is wanted right now.

## T-C target: scale estimate only, item-level worklist blocked

T-C's item-overlap test needs **new items scored by ≥2 models each** (not just more
items on one model). Producing an exact candidate list requires the raw per-model
roster of which items each model was evaluated on — checked this repo's
`results/analysis/` snapshot for it (`e3_roster.json` is sampling-design metadata, not
a per-item roster) and it is not here. **Flagged, not fabricated**: pulling that
roster from the companion project's raw generation cache is the concrete next
mechanical step before an item-level T-C worklist can be produced.

What is given here: the stratification *rule* (prioritize item-pairs where at least
one model is in the top-8 high-rate pool list) and an order-of-magnitude planning
number — roughly 1,268 shared items at the roster-average rate, fewer if drawn
preferentially from high-rate pools as E-E's worklist does — for reaching a
planning-level target of ≥20 either-wrong paired observations (current: 1 of 41; this
target is not a formal power calculation, since no effect size exists yet to power
against — that is what T-C is trying to establish).

## Explicit caveat, not hidden

Pool *availability* — how many un-audited items actually remain in each high-priority
(model, stratum) pool — is not verified here; that requires the same raw per-model
results file T-C's exact worklist needs. The numbers above are expected-value
projections from shrunk rates, not guarantees, and the real next step before
labelling begins is a quick check of that availability.
