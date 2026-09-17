# Venue and overlap audit: flipbudget vs. P13 ("Benchmark Accuracy Is Not an Identified Quantity," TMLR)

Written 2026-09-17, in response to an explicit directive to determine
whether this manuscript conflicts with the author's own concurrent TMLR
submission before any further venue recommendation is made. Read P13's
actual TMLR source (`D:\Projects\knowledgeshift\paper\tmlr.tex`) directly,
not from memory or from the dossier's summary of it.

## The one fact that settles the classification question

`results/analysis/mathhard_labelling_key.json` exists at the identical
relative path in both repositories. MD5 checksum, both copies:
**`e21cf086392e98b367be04224100e16a`** — byte-identical, 400 human-labeled
items, same file. This is not "the same kind of audit" or "the same
lineage" — it is the literal same dataset, used as a core empirical pillar
in both papers' headline results.

Both papers also share the same base roster: P13's abstract states
"28 published models," "378 pairwise orderings"; flipbudget's
`ea_dominance_canonical.json` gives `n_unique_models_in_human_pair_list=28`,
`total_candidate_pairs=378`. Same MATH-Hard leaderboard snapshot, same
28-model candidate set.

## Classification

**Not the same paper, not merely evolving under one submission — but not
genuinely distinct either. This is a derivative/extension relationship,
and the shared part is the underlying human-audit data specifically, not
just the general research question.**

| | P13 (TMLR) | flipbudget (this manuscript) |
|---|---|---|
| Title | "Benchmark Accuracy Is Not an Identified Quantity" | "Scorer-Induced Partial Identification of Benchmark Comparisons: An Audit-Design Approach" |
| Estimand | $\hat A - \bar\varphi \le A^* \le \hat A + U/n + \psi$ — driven by the scorer's own discarded **parse-failure count** $U$, with $\bar\varphi,\psi$ as measured secondary margins | $A^* = g(a,\alpha,\beta) = (a-\alpha)/(1-\alpha-\beta)$ — a full two-parameter false-credit/false-miss box $(\alpha,\beta)$, not conditioned on parse failure specifically |
| Headline statistic | % of 378 pairwise orderings **not identified** (87.8% zero-error / 94.4% human-audited / 90.2% LLM-adjudicated) | **median identification-to-sampling width ratio** (6.10×/5.74×), % dominant, on 120 of 136 scored pairs |
| Audit measured from the shared 400-item data | $\bar\varphi=6.4\%$, $\psi=0.8\%$ (conditional on the parse-failure/positional-credit mechanism P13 defines) | pooled $\alpha=3.14\%$, $\beta\approx0$ (unconditional false-credit/false-miss over the whole credited/wrong strata) — a different conditioning, a different number, not a relabeling of the same statistic |
| Audit-design / labeling-budget-allocation theory | **Absent** — not in the contributions list, not a section of the paper | **Present** and a named contribution: Neyman-allocation proof + the real-data finding that naive plug-in Neyman is dominated by proportional allocation under sparse audits |
| Scorer-choice dependence (exact_match vs. score_boxed as two live production scorers on the same benchmark, disagreement rate measured directly) | **Absent** — P13's "two independent censuses" measures parse-failure *prevalence* across many harness *task configurations*, a different question from *two named scorers disagreeing on the same items* | **Present**, 3.63% disagreement (817/22,508), independently corroborated by Hugging Face's own math-verify postmortem |
| Cross-framework harness census (lm-evaluation-harness, OpenCompass) | **Present**, a named contribution | Absent — not claimed here |
| Learned/better extractor comparison | Present | Absent |
| Five-field Scorer Card prescription | Present | Absent (cites the concept implicitly through the disclosure framing, does not propose a reporting standard) |

**Verdict: derivative/extension.** flipbudget is not P13 restated, and it is
not unrelated to P13 — it shares P13's core empirical resource (the 400-item
audit) and its general thesis (benchmark comparisons under an imperfect
scorer are not simply identified), while contributing a materially
different formal treatment (general two-parameter misclassification bounds
vs. P13's parse-failure-count-specific bound) and two contributions P13
does not have at all (audit-design/Neyman allocation; scorer-choice
dependence between two named production scorers).

## Policy check — read directly from the venues' own current pages, not assumed

**TMLR** (`jmlr.org/tmlr/editorial-policies.html`, fetched and read in full
this pass): *"There should not be any reuse of written text, figures or
results between the submitted paper and any paper which has been
published, accepted for publication, or submitted in parallel at another
archival, peer-reviewed venue."* NeurIPS (all tracks, including
Evaluations & Datasets) is archival and peer-reviewed. **If flipbudget is
submitted to NeurIPS E&D while P13 is still under review at TMLR (or
shortly after acceptance, before that overlap is disclosed), and a
reviewer or editor at either venue discovers the shared 400-item audit
underlying both papers' results, this reads as exactly the "reuse of...
results" TMLR's own policy prohibits — even though the two papers compute
different statistics from it.** The risk is not hypothetical: both
projects are built around public, reproducible code releases, and the
shared file lives at an identical relative path in both public repo
layouts — a routine reproducibility check on either paper would surface it
directly.

**NeurIPS 2026** (`neurips.cc/Conferences/2026/CallForPapers` and the Main
Track Handbook, searched this pass; the 2027 CFP is not yet published —
see the explicit note below): *"The reviewing process will treat any other
archival submission by an overlapping set of authors as prior work... If
publishing one would render the other too incremental, both may be
rejected."* Also explicitly prohibited: *"thin slicing"* (submitting
multiple very similar papers hoping one is accepted). Sole authorship means
every P13/flipbudget pairing is by definition an "overlapping set of
authors" of exactly one. **A NeurIPS E&D reviewer who finds P13 (whether
still under review, or already accepted/public at TMLR) would be expected
to treat it as prior work and assess whether flipbudget is "too
incremental" relative to it** — which is a real risk unless flipbudget's
own framing foregrounds the two contributions P13 genuinely lacks
(audit-design; scorer-choice dependence) rather than leading with the
shared "benchmark comparisons aren't automatically identified" thesis P13
already established first, in an archival-track submission, on the same
data.

**2027 CFP status**: not yet published as of 2026-09-17 (checked this
pass). The 2026 CFP's dual-submission and prior-work language quoted above
is the most recent official statement available and is used here as the
working assumption; re-check the 2027 CFP specifically before any actual
submission, since page limits and track-specific rules are the parts most
likely to change year over year even when the dual-submission principle
itself does not.

## What does NOT need to wait

Citing and distinguishing from one's own closely related prior/concurrent
work is never prohibited — it is expected, under every policy read above.
**Fixed in this pass, regardless of the timing decision below**: added an
explicit paragraph to flipbudget's Related Work naming P13, the shared
400-item audit, and the precise boundary between the two papers' claims
(see `manuscript/latex/sections/02_related_work.tex` and
`manuscript/MANUSCRIPT_DRAFT.md`, both updated same commit as this file).
This was a real, unforced gap — flipbudget's manuscript did not mention
P13 anywhere before this pass, despite the shared data.

## Recommendation

1. **Do not submit flipbudget to NeurIPS E&D (or any other archival venue)
   while P13 is under review at TMLR, without first disclosing the shared
   audit explicitly in flipbudget's own Related Work** — now done (see
   above), so this specific blocking condition is cleared.
2. **The safer sequencing is still to let P13's TMLR outcome resolve
   first.** P13's own status (per the application dossier, checked
   2026-09-09) is under review with a reported ~91-day median time to
   decision from a 2026-09-08 submission — roughly early December 2026.
   Submitting flipbudget to an archival venue before that resolves is not
   strictly prohibited given the disclosure fix above, but it maximizes
   the chance a NeurIPS reviewer encounters P13 mid-review at TMLR (an
   awkward, avoidable "which one is prior art" situation) rather than
   encountering it as a settled, citable, already-decided paper.
3. **If flipbudget must be submitted before P13's TMLR decision**, the
   manuscript's own framing must lead with the audit-design and
   scorer-choice contributions — the two pieces P13 does not have — rather
   than the shared partial-identification thesis, both to give reviewers
   the clearest true novelty signal and to minimize "too incremental
   relative to overlapping-author prior work" risk under NeurIPS's own
   stated criterion.
4. **Do not, under any timing, let the two papers' headline numbers drift
   into looking like the same result restated.** They already don't (6.10×
   vs. 94.4%-not-identified are different statistics by construction) —
   keep it that way; do not add a "% pairs not identified" statistic to
   flipbudget merely because it would look impressive, since that specific
   framing is P13's.
