# Plan: TMLR resubmission of the flagship paper

Written 2026-09-24. Supersedes the AISTATS 2027 target in `PLAN_AISTATS2027.md` (that
deadline, 6 October, cannot be met without rushing exactly the thing that got the paper
rejected twice). Everything technical in that plan stands; only the venue and the ordering
change.

## Where this stands

The same work has now been turned away twice, and neither was about the evidence:

- **TMLR, 2026-09-10.** Desk screen, ~46 hours, no reason given, no action editor. Cause
  unknown — G0 below.
- **TAE @ NeurIPS 2026, 2026-09-17.** Three reviews. Ratings 4 / 2 / 1; clarity 2 / 1 / 1.
  Every reviewer named the writing. One called it "AI-slop" and pointed at code-line and
  git-commit references in the prose. One rejected on the benchmark choice: MMLU is multiple
  choice, so the extraction problem looks manufactured there. One asked, fairly, why an
  extraction-failure rate is worth reporting when accuracy is already a lower bound.

The science was never the problem. The framing, the writing, and the benchmark choice were.

## The target

**TMLR**, resubmitted mid-October. Rolling deadlines, no page limit, and an explicit standard
of correctness over novelty — which is what this paper actually offers. A decision can
plausibly land in December or January, so the application-season artifact is either "accepted
at TMLR" or "under review at TMLR" alongside a strong arXiv v2.

## The paper

One paper, not three. MATH-Hard leads; the harness-wide audit supplies generality; the human
labels are the released resource. The arXiv preprint becomes v2 of the same work rather than a
fourth overlapping artifact.

**Claim:** a leaderboard's ranking is not identified by its published scores, because the
scorer that decides what answer a response contains is itself a design choice; and a small
human audit can certify part of that ranking only under an assumption about how verifier
agreement relates to cross-model correctness, which we state, quantify, and test.

## Gates

- [ ] **G0 — Why was it desk-rejected?** Send `provenance/tmlr_email_draft.md`. Blocking: do
  not resubmit until the cause is known and fixed. If no reply within a week, resubmit having
  independently re-checked anonymity, formatting, and the TMLR style file.
- [ ] **G1 — Label provenance.** Re-label the 60-row check sheet in the instrumented app and
  run `scripts/fb_relabel_agreement.py`. Criteria and consequences are fixed in
  `VALIDATION_RELABEL.md`. A pass adds 458 labels to the 400 already accepted.
- [ ] **G2 — Rewrite for a reader.** The binding constraint. No file paths, line numbers or
  commit hashes in prose; every term defined at first use; open on one real response and what
  the scorer did to it; the author's own voice throughout. Heavy machinery moves to the
  appendix — the main text carries the result and one theorem statement.
- [ ] **G3 — Answer the three reviewers in the text.**
  - Lower bounds do not order models: ranking is the claim, and reversals are exhibited.
  - A taxonomy of extraction failures with real examples, not a single rate.
  - Output-format adherence depends on instruction tuning, decoding and prompting; the
    leaderboard's generations are fixed, and the design choice under study is the harness's.
- [ ] **G4 — Related work.** Engage BetterBench (Reuel et al., NeurIPS 2024) and M2M
  (Salaudeen et al., arXiv 2505.10573), plus the benchmark-validity, prediction-powered
  inference and rank-interval lines. Verify every claim attributed to a cited work by reading
  it.
- [ ] **G5 — Generality.** The harness-wide audit (64.9% of 4,524 generative tasks) becomes a
  section that answers "this is one leaderboard", not a footnote.
- [ ] **G6 — MMLU.** Demoted to an appendix robustness check, with the multiple-choice caveat
  stated in the author's own words before a reviewer states it for us.
- [ ] **G7 — The resource.** Release the labels, the per-cell census, the scorer cards and the
  code, with a datasheet. This is what makes it a resource paper.
- [ ] **G8 — Hostile read and submit.** Re-run the pipeline clean, check every number against
  its macro, then submit.

## What does not change

The certification machinery, the coverage simulation, the preregistrations, the quality gate
and the 27-model census all stand as built. They move to the appendix, they do not get
diluted, and no number enters the paper except through a generated macro.
