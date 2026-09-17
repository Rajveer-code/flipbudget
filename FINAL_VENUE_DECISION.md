# Final venue decision (2026-09-17, post-compression, post-hostile-review)

Assessed on evidence fit, contribution fit, policy compatibility, format
requirements, and likely reviewer expectations — not ranked by prestige.

## NeurIPS Evaluations & Datasets — primary recommendation

- **Evidence fit**: strong. The track's own scope (fetched and read
  directly from the 2026 CFP) explicitly welcomes "rigorous reproduction,
  auditing, and stress-testing of prior evaluations" and "compar[ing]
  evaluation designs and demonstrat[ing] how different assumptions lead to
  different results" — this paper is close to a textbook match, not a
  stretch fit.
- **Contribution fit**: strong for the combination (partial identification
  + audit design + scorer-choice dependence), honestly scoped as
  class-C-or-below on any individual piece.
- **Policy compatibility**: conditional, not automatic. The E&D track
  explicitly inherits Main Track dual-submission/prior-work rules
  (confirmed, not assumed, this pass). Given the P13/TMLR data overlap,
  submission is policy-safe **only with the Related Work disclosure this
  pass added** — already done — and the timing caveat in
  `VENUE_AND_OVERLAP_AUDIT.md` still applies.
- **Format**: 9-page main-content budget, confirmed inherited from Main
  Track; this manuscript fits (8.5/9 pages, verified by direct inspection
  of the compiled PDF, not by page-counter trust alone).
- **Reviewer expectations**: rigor- and reproducibility-focused reviewers,
  per the track's own stated emphasis — this paper's unusually candid bug
  disclosure and three-submissions-caught labeling-integrity story play to
  exactly this audience's values.
- **Missing evidence**: `exact_match`'s own audited $(\alpha,\beta)$ and
  analysis C (the 458-row human audit).

## ICML / ICLR evaluation-and-benchmarks-type tracks — viable alternative, not preferred

- **Evidence/contribution fit**: comparable to NeurIPS E&D in substance;
  these tracks exist for similar reasons.
- **Policy compatibility**: same P13-overlap analysis applies regardless
  of which archival venue is chosen — the disclosure and timing
  consideration are venue-agnostic, not specific to NeurIPS.
- **Why not preferred**: no venue-specific advantage identified over
  NeurIPS E&D for this paper's specific shape; picking a second archival
  venue to evaluate does not reduce the P13-overlap consideration, and
  NeurIPS E&D's stated scope is the closest textual match found.

## TMLR — viable, notably different tradeoffs

- **Evidence/contribution fit**: TMLR has no formal page limit
  ("submissions may be any length ... justified by its content" — the
  same policy page P13 itself cites) — this paper's uncompressed 17-page
  version could go to TMLR without the compression this pass performed,
  which is a genuine option worth naming, not just a formatting footnote.
- **Policy compatibility**: this is **the same venue as P13**. TMLR's own
  policy ("no reuse of results... between the submitted paper and any
  paper... submitted in parallel at another archival, peer-reviewed
  venue") does not obviously prohibit two papers by the same author at
  the *same* venue if both are disclosed and distinct — but submitting a
  second, closely related, same-audit-data paper to the identical venue
  while the first is still under review is a heavier disclosure burden
  than a different venue, and was not the working assumption anywhere
  else in this project's planning. **Not recommended without first asking
  TMLR's own action editors directly** — genuinely outside what a
  literature/policy-page read alone can resolve.
- **Missing evidence**: same as above.

## A strong evaluation/benchmark workshop — recommended as a parallel, non-competing action

- **Policy compatibility**: explicitly the safest option — both TMLR's and
  NeurIPS's dual-submission rules exempt non-archival workshops. A
  workshop submission (before or in parallel with the archival decision)
  carries none of the overlap risk analyzed above.
- **Recommendation**: pursue a workshop presentation of this work
  independent of, and not gated by, the archival-venue timing question —
  this is the one action in this whole decision that has no downside and
  was not previously flagged as available.

## Recommendation

**Submit to NeurIPS 2027 Evaluations & Datasets**, timed per
`VENUE_AND_OVERLAP_AUDIT.md` (after P13's TMLR decision resolves, or with
the audit-design/scorer-choice contributions foregrounded if it must go
out sooner), with a workshop submission pursued in parallel at no
additional risk. Re-verify the 2027 E&D CFP specifically once published —
this decision is built on the 2026 CFP as the best available proxy,
explicitly flagged as such throughout this pass's documents, not
presented as a confirmed 2027 rule.

---

# Final quality-bar checklist

| Bar | Status | Evidence |
|---|---|---|
| **Scientific** — estimand correct | ✓ | `THEORY_AUDIT.md` |
| — theory correct | ✓ | `THEORY_AUDIT.md`, 5 targeted tests, 24/24 suite |
| — empirical claims traceable | ✓ | `CLAIM_LEDGER.md`, no untraceable claim found |
| — limitations explicit | ✓ | 10 items, Section 8, none removed under compression |
| — novelty accurately scoped | ✓ | `NOVELTY_AUDIT.md`, no claim above class C |
| **Statistical** — sampling weights correct | ✓ | Horvitz–Thompson estimator, 7 regression tests |
| — uncertainty correct | ✓ (with a stated caveat) | R1.1 fix: compounding-coverage caveat now explicit |
| — identified sets correctly bounded | ✓ | `THEORY_AUDIT.md` empty-set/straddle tests |
| — empty sets correctly treated | ✓ | dedicated regression test, real bug fixed earlier in this project |
| — no accidental construct mixing | ✓ | `exact_match`/`score_boxed` kept structurally separate throughout, verified by an earlier hostile-review pass this session |
| **Reproducible** — clean build | ✓ | 0 Overfull/Undefined, verified this pass |
| — clean package | ✓ | `SUBMISSION_FINAL/`, standalone-rebuilt, verified |
| — deterministic outputs | ✓ | byte-identical JSON across repeated runs, checked this pass |
| — no machine-specific paths | ✓ | scanned by the packaging script, none found |
| **Presentation** — official format | ✓ | NeurIPS 2026 `[eandd]` template |
| — page limit satisfied | ✓ | 8.5/9 main-content pages, verified by direct page inspection |
| — figures readable | ✓ | visually inspected, all 15 pages |
| — references complete | ✓ | 13 entries, all cited, all verified against publisher/arXiv records |
| — no overfull boxes | ✓ | 0, confirmed on the final compile |
| — no ambiguous terminology | ✓ | scorer-identification vs. audit-estimation distinguished explicitly (this pass); `exact_match`/`score_boxed` distinguished throughout |
| **Review-resistant** — hostile reviews completed | ✓ | `REVIEWER_ATTACK_FINAL.md`, 4 personas, written in full |
| — major criticisms addressed | ✓ | 5 of 8 findings fixed; 3 correctly left as disclosed-not-fixable |
| — remaining weaknesses explicitly disclosed | ✓ | R2.2, R3.1 (resolved by disclosure), R3.3 named plainly |

**All bars met except the one this paper cannot meet without the pending
data**: `exact_match`'s own audit. That is not a quality-bar failure — it
is the one named, disclosed, honestly-marked external dependency the
entire pass was built around.
