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
