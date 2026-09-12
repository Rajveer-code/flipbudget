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
| A1 | Audit-estimation identification width exceeds sampling width, pairwise | **REVISED (twice — see `RECONCILIATION_EMPTY_SET_BUG.md`)** | median **6.10×**, **100%** dominant (n=120 of 136), 24.2% >10× | `ea_dominance_pairwise_corrected_v2.json` | Original: 134.32×/100% (pre-fix corner-drop method). First revision this phase: 5.24×/89.7% ([0,1]-clip fix, but still counted 16 pairs with nonsensical negative widths). This (third, current) revision: those 16 empty-identified-set pairs properly excluded rather than included — result is *cleaner* than the first revision, not just smaller. |
| A2 | Same, single-model | **REVISED (twice)** | median **3.22×**, 100% dominant (n=16 of 17) | `ea_dominance_corrected_v2.json` | Unchanged from the first revision (only 1 model was ever affected by the empty-set issue on this side). |
| A3 | Original compound Λ-bounded flip rate | **SUPERSEDED, preserved as historical** | 73.5% saturated-at-Λ=1 | `TB_COMPOUND.md` | Explicitly preserved per your instruction, not deleted. Superseded as *the* headline by A4. |
| A4 | Four-layer reconciliation of A3 | **SUPPORTED, corrected** | audit-only unresolved 91/**120 valid** (75.8%) vs. scorer-only 15/**66 valid** (22.7%) vs. sampling 12/136 (8.8%) vs. combined 110/**120 valid** (91.7%). Verdict **B**. | `reconciliation_four_layers_corrected.json` | Original `reconciliation_four_layers.json` (91/136=66.9% audit-only, no exclusions) preserved as historical — it silently included 16 pairs with impossible negative widths. Corrected version excludes empty-identified-set pairs **per layer** (16 for audit-only, **70 — over half — for scorer-only**, flagged as a large, not-yet-root-caused open question in `RECONCILIATION_EMPTY_SET_BUG.md`). |
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
| B8 | MATH-Hard comparator (`is_equiv`) is silently broken on Windows (`SIGALRM` missing) | **REVISED, fixed** | T-C's 69-row result: **0 rows change, unaffected.** Original 400-item companion audit: **1 row changes (5→6 true scorer-wrong events)**. | `MATH_COMPARATOR_BUG.md` | Found via the adversarial suite (item 13), root-caused, fixed in `fb_math_comparator_fixed.py`. E-E's AUC=0.830 not re-derived with the corrected 6th event — flagged as a small, real, not-yet-done follow-up, not silently left stale. |

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
| D4 | `[0,1]`-boundedness correction | **REVISED — the fix itself had a bug** | `RECONCILIATION_FOUR_LAYERS.md` for the original fix; `RECONCILIATION_EMPTY_SET_BUG.md` for a second, deeper correction found auditing the published package (item 18): independently clipping `min(lo,0)`/`max(hi,1)` silently inverts the interval when the raw range misses `[0,1]` entirely (real on 16-70 of 136 pairs depending on layer). Fixed in both the package and the research script; the identified set is now explicitly empty (NaN) in that case, not a fabricated bounded interval. |
| D5 | T-C (masterplan): item-heterogeneous, **correlated** scorer error, formal cancellation bound | **NOT YET DERIVED** | Empirically attempted twice (B1, B4), both underpowered. No formal theorem exists yet for *how much* correlated error cancels in a difference. This phase derives it (§ Theory, below). |
| D6 | T-D: imperfect reference / latent-class | **NOT YET DERIVED** | No latent-class model or sensitivity bound exists yet. This phase derives one. |
| D7 | T-E: verification-bias formalization | **NOT YET DERIVED** | The stratified-on-scorer-outcome design has never been formally checked against the verification-bias/MAR literature. This phase does it. |
| D8 | T-F: probability reporting | **NOT STARTED** | Lower priority per `MASTERPLAN_PHASE2_FLAGSHIP.md` §14 Tier 4. |
| D9 | T-G: studentized inference | **NOT STARTED** | Same. |
| D10 | Ranking-preservation exact conditions | **NOT YET DERIVED, implicit only** | `bounded_comparison`'s `contains_zero` check is the operational version; no closed-form necessary-and-sufficient condition has been stated as a theorem. This phase states one. |

## E. What this table changes about prior claims

- **A1/A2 (E-A dominance) and A4 (the reconciliation itself) were corrected
  twice in this same phase — not because the first fix was wrong in
  direction, but because auditing the published package (item 18) found
  the first fix's own clipping logic had an edge case.** Net result across
  both corrections: 134.32×/100% (original) → 5.24×/89.7% (first fix,
  [0,1]-bounding) → **6.10×/100% (second fix, proper empty-set exclusion)**.
  The final number is *cleaner* than either predecessor, not just smaller —
  finding and fixing your own fix's bug before reporting it as final is the
  point of this exercise. `ea_dominance_study.json` and
  `reconciliation_four_layers.json` are left on disk unmodified
  (provenance); `*_corrected_v2.json` and `*_corrected.json` (reconciliation)
  are current.
- **One number got MORE uncertain, honestly, not less**: the
  scorer-identification-only layer now excludes 70/136 pairs (51.5%) as
  empty-identified-set — a large, real, not-yet-root-caused finding
  (`RECONCILIATION_EMPTY_SET_BUG.md`), not swept under the 22.7% headline.
- **Nothing else required a numeric correction of this kind** — B and C's
  claims were already internally corrected in real time as the issues were
  found this session (C3, B7, C6/C7 in particular).
