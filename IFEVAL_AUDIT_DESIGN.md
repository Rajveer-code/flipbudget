# IFEval audit design — a real verifier bug found, then the sample built around it

Scripts: `scripts/fb_ifeval_audit_design.py`, `scripts/fb_ifeval_labeling_package.py`.
Sheet ready to label: [labeling/ifeval_audit_l1.csv](labeling/ifeval_audit_l1.csv)
(454 rows). Key: `results/flipbudget/ifeval_audit_key.json` (not for the labeler).

## A real, root-caused bug in IFEval's own verifier

Building the sample, a sanity check (strict compliance must imply loose
compliance — loose's 8 response variants include the untouched response
itself) failed on 6 real rows. Investigated rather than dismissed:
reproduced directly — calling the same instruction checker twice on
identical input gave different answers. Traced to source:
`keywords:letter_frequency`'s `build_description` validates its `letter`
kwarg as a single a–z character; when the prompt actually asks for a
**punctuation** frequency (`"!"`, `"#"`), that validation fails and the code
silently falls back to `random.choice(string.ascii_letters)` — checking a
**random, unrelated letter** instead of the one the prompt asked about, with
no fixed seed. Separately, `language:response_language` uses `langdetect`,
whose algorithm is not seeded here and is not guaranteed deterministic.

**Scanned all 541 items directly: 33 (6.1%) use one of these two mechanisms.**
Cross-referenced against the real 380-disagreement data: **31 of 380
disagreements (8.2%) sit on a flagged item — real, but not most of the
signal.** The other 91.8% of disagreements are unexplained by this
mechanism and are the genuine target of this audit.

## Sample design

Three strata, exactly the scorer's own logic (both_pass: strict=T;
disagree: strict=F,loose=T; both_fail: strict=F,loose=F):

| Stratum | Population | Sampled |
|---|---|---|
| both_pass | 5,071 (34.7%) | 40 (comparison) |
| **disagree** | 374 (2.6%) | **374 (full census)** |
| both_fail | 9,162 (62.7%) | 40 (comparison) |

Full census on `disagree` — it's the entire reason for this audit, and at
374 items removes sampling error on the one number that matters most.
Comparison samples on the other two strata (proportional across models, not
pure random) sanity-check that "unambiguous" really is — direct lesson from
`TA_BOUNDARY_AUDIT.md`: don't assume a stratum is uninformative just because
its label suggests so. **454 total items, all 27 models represented.**

Every sampled item is tagged `nondeterminism_flagged` in the key (29 of 454)
— not shown to the labeler, but the analysis must treat these as a distinct
category, not pool them with genuine strict/loose ambiguity.

## Blinding

Same construction as T-C (`sha256(stratum|model|key)[:16]`), same reason
(`HUMAN_LABELING_GUIDE.md`): no model name, key, or stratum in the sheet.
Verified directly against every roster model-name substring — one
false-positive match (`zephyr`, the English word for a breeze, inside a
model's own prose) confirmed by inspection, not a real leak.

## Labeling question

IFEval has no separate gold-answer transcription step — the question is
"does this response comply with the instruction(s) stated in the prompt?"
`your_judgment`: YES / NO / PARTIAL (multi-instruction prompts where some but
not all are followed).

## What this does not do

No labeling started. Does not build the multi-labeler (l2/l3) overlap split
T-C used — not done this round, a natural next addition if wanted. Does not
yet compute IFEval's own Wilson-CI/Λ apparatus — that needs these labels
first.
