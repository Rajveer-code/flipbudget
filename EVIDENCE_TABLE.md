# Canonical evidence table

Every quantitative/qualitative claim currently standing anywhere in this
repo, re-verified against its live source JSON today, not recalled from the
markdown prose that first reported it. Status categories: **SUPPORTED**
(verified, stands as reported), **REVISED** (real finding, but the original
number was wrong and is corrected here — both kept, superseded flagged),
**WEAK** (real but underpowered / small effect, don't lean on it alone),
**UNSUPPORTED** (attempted, no usable evidence either way), **EXCLUDED**
(data quality failure, never entered analysis), **NOT YET DERIVED** (a real
gap this phase should close).

## A. The headline claims

| # | Claim | Status | Current number | Source | Note |
|---|---|---|---|---|---|
| A1 | Audit-estimation identification width exceeds sampling width, pairwise | **REVISED** | median **5.24×**, 89.7% dominant, 21.3% >10× | `ea_dominance_pairwise_corrected.json` | Was reported as median 134.32×, 100% dominant (`ea_dominance_study.json`, `TIER1_VERDICT.md`) — that number used a pre-fix corner-drop method (0.95 floor) later shown wrong; recomputed here with the corrected `[0,1]`-bounded method. Direction unchanged, magnitude was ~26× overstated. |
| A2 | Same, single-model | **REVISED** | median **3.22×**, 100% dominant (n=16) | `ea_dominance_corrected.json` | Was 74.99×, 100% dominant. Same correction, same direction held, magnitude ~23× overstated. |
| A3 | Original compound Λ-bounded flip rate | **SUPERSEDED, preserved as historical** | 73.5% saturated-at-Λ=1 | `TB_COMPOUND.md` | Explicitly preserved per your instruction, not deleted. Superseded as *the* headline by A4. |
| A4 | Four-layer reconciliation of A3 | **SUPPORTED** | audit-only unresolved 91/136 (66.9%) vs. scorer-only 15/136 (11.0%) vs. sampling 12/136 (8.8%) vs. combined 110/136 (80.9%). Verdict **B**. | `reconciliation_four_layers.json` | Corrected `[0,1]`-bounded methodology throughout (`bounded_single_model_extrema`), two sanity checks pass. This is the current, trusted decomposition of A3. |
| A5 | Audit-design six-question analysis | **SUPPORTED** | required-n median 415/362; Neyman gap median 0.482 (77% variance cut available for free); 16/16 models past benchmark-crossover; adaptive ≈ static Neyman (oracle-coincident) | `audit_design_analysis.json`, `AUDIT_DESIGN_ANALYSIS.md` | Verdict **D** (B+C) first given here. |
| A6 | Consolidated verdict | **SUPPORTED, current** | D confirmed | `CONSOLIDATED_VERDICT.md` | Incorporates A7–A11 below. This phase re-examines whether it still holds after A1/A2's correction — it does (§ Core thesis, below). |

## B. T-C (MATH-Hard human audit)

| # | Claim | Status | Current number | Source | Note |
|---|---|---|---|---|---|
| B1 | Original companion-project correlation test | **UNSUPPORTED (underpowered)** | 1/41 paired observations with any wrongness event | `TIER1_VERDICT.md` | Neither confirms nor refutes correlated error. |
| B2 | Original E-E format-association | **UNSUPPORTED (underpowered)** | AUC=0.830, bootstrap 95% CI [0.492, 0.991] | `TIER1_VERDICT.md`, `ee_format_association.json` | CI crosses chance; 5 positive events on 350 records. |
| B3 | E-E feature stability re-check | **WEAK, partial** | 4 of 5 features robust (`n_newlines`, `ends_with_period`, `has_therefore`, `n_frac`; `char_length` fails); 5 events total, need ≥40 | `EE_FEATURE_STABILITY_CHECK.md` | Retired as a large-labeling plan (`EE_REASSESSMENT.md`) — correctly, since verdict D doesn't need this mechanism. |
| B4 | T-C real audit expansion (this session) | **UNSUPPORTED (underpowered), but real** | 0/69 scorer-wrong events, 51 valid paired observations, 0 either-wrong | `TC_REAL_ANALYSIS.md` | P(0 events \| true rate ≈3%, n=69) ≈ 11% — consistent with the targeted rate, not evidence against it. Still underpowered after two independent audit rounds (B1, B4). |
| B5 | T-C inter-rater agreement | **SUPPORTED** | 100% derived agreement, all pairs and 3-way (14/14) | `TC_REAL_ANALYSIS.md` | Genuine, strong, reportable. |
| B6 | T-C alpha/beta pooling update | **SUPPORTED** | global α anchor 0.0314→0.0216; 8/27 models newly qualify (17→25); scorer-only-layer unresolved count *worsened* 15→22 via anchor propagation to untouched models | `TC_ALPHA_BETA_UPDATE.md` | Real, verified secondary finding: EB pooling propagates a local audit's effect to un-audited models. |
| B7 | T-C resubmission (`task1_math_answers.csv`) | **EXCLUDED — corrupted** | every `\frac{X}{Y}` → `\frac{X{Y`; lost `CONTRADICTORY` flag; `NOT FOUND` on items with a stated answer | `IFEVAL_LABEL_QUALITY_ISSUE.md` §T-C | Preserved as provenance only, per your instruction. Never entered any result. |

## C. IFEval (E-B scale-out)

| # | Claim | Status | Current number | Source | Note |
|---|---|---|---|---|---|
| C1 | IFEval is the right E-B choice, not GPQA | **SUPPORTED** | GPQA/MMLU-PRO/MuSR are `multiple_choice`, no scorer-error mechanism possible | `EB_IFEVAL_STATUS.md` | Self-corrected before building anything. |
| C2 | Strict/loose disagreement, full population | **SUPPORTED** | 380/14,607 (2.60%) | `ifeval_full_roster.json`, verified directly | |
| C3 | Nondeterminism mechanism scan | **REVISED** | 96/541 items (17.7%) carry a real, source-verified mechanism | `ifeval_nondeterminism_flagged_items.json` | Originally scanned as 33/541 (6.1%, only 2 of 3 real mechanisms checked). Old count preserved in the same file for the record. |
| C4 | Reproducibility of the mechanism (fresh-process replicates) | **SUPPORTED** | unseeded: 1.9% item flip rate; seeded control: 0%; benchmark-score spread 0.0004; max rank shift 2/27; #1 model never changes across 15 replicates | `ifeval_reproducibility_check.json` | Causal, not correlational — same rows, only the seed differs. |
| C5 | Corrected disagreement decomposition | **SUPPORTED** | 64/380 (16.8%) explained by a known mechanism, 316/380 (83.2%) unexplained | `ifeval_reproducibility_check.json` | Was 31/380 (8.2%) explained under the incomplete C3 scan — corrected upward, qualitative conclusion (majority unexplained) unchanged and now more firmly grounded. |
| C6 | IFEval human-audit round 1 | **EXCLUDED — labeling failure** | 89.3% contradiction rate (284/318) against real per-instruction verifier | `IFEVAL_LABEL_QUALITY_ISSUE.md` | Concentrated in mechanically-checkable constraint types (19 ids). |
| C7 | IFEval human-audit round 2 (rewritten README) | **EXCLUDED — labeling failure, no improvement** | 90.5% contradiction rate (335/370) | `IFEVAL_LABEL_QUALITY_ISSUE.md` | No measurable change from the rewrite. Paused per your decision, not attempted a third time. |
| C8 | IFEval's 83.2% unexplained disagreement, nature | **NOT YET DERIVED** | — | — | Genuinely open. No human-validated answer exists. Not assumed to be scorer error in either direction. |

## D. Theory (T-A through T-H, masterplan numbering)

| # | Object | Status | Note |
|---|---|---|---|
| D1 | T-A: Scorer Sensitivity Model (Λ-odds-bound) | **SUPPORTED** | `TA_SSM_DERIVATION.md`, `fb_ta_ssm.py`. Symbolic + numeric verification. |
| D2 | T-H: sharpness under SSM | **SUPPORTED** | IVT/vertex-theorem argument, verified on a non-rectangular case too. |
| D3 | T-B: design sensitivity Λ̃ | **SUPPORTED** | `TB_DESIGN_SENSITIVITY.md` (pure-Λ) + `TB_COMPOUND.md` (compound, saturation-corrected). |
| D4 | `[0,1]`-boundedness correction | **SUPPORTED** | `RECONCILIATION_FOUR_LAYERS.md` — the fix that produced A1/A2/A4's corrections above. |
| D5 | T-C (masterplan): item-heterogeneous, **correlated** scorer error, formal cancellation bound | **NOT YET DERIVED** | Empirically attempted twice (B1, B4), both underpowered. No formal theorem exists yet for *how much* correlated error cancels in a difference. This phase derives it (§ Theory, below). |
| D6 | T-D: imperfect reference / latent-class | **NOT YET DERIVED** | No latent-class model or sensitivity bound exists yet. This phase derives one. |
| D7 | T-E: verification-bias formalization | **NOT YET DERIVED** | The stratified-on-scorer-outcome design has never been formally checked against the verification-bias/MAR literature. This phase does it. |
| D8 | T-F: probability reporting | **NOT STARTED** | Lower priority per `MASTERPLAN_PHASE2_FLAGSHIP.md` §14 Tier 4. |
| D9 | T-G: studentized inference | **NOT STARTED** | Same. |
| D10 | Ranking-preservation exact conditions | **NOT YET DERIVED, implicit only** | `bounded_comparison`'s `contains_zero` check is the operational version; no closed-form necessary-and-sufficient condition has been stated as a theorem. This phase states one. |

## E. What this table changes about prior claims

- **A1/A2 (E-A dominance) are the single biggest correction from this pass.**
  The direction of the finding is unchanged and still real; the magnitude was
  overstated by roughly an order of magnitude due to a since-identified
  corner-drop artifact in the *original* E-A script, never previously
  re-run under the corrected method it itself motivated elsewhere in this
  project. Every future citation of "134×"/"75×"/"100% dominant" must use
  5.24×/3.22×/89.7%–100% instead. `ea_dominance_study.json` is left on disk
  unmodified (provenance); the two `*_corrected.json` files are the ones to
  cite going forward.
- **Nothing else required a numeric correction of this kind** — B and C's
  claims were already internally corrected in real time as the issues were
  found this session (C3, B7, C6/C7 in particular).
