# IFEval returned labels: not usable as-is — found before trusting any result

Scripts: `scripts/fb_ifeval_real_analysis.py` (the naive analysis — ran, do
**not** trust its headline numbers, kept for the record and reproducibility
only), `scripts/fb_ifeval_label_quality_check.py` (the check that caught the
problem). Results: `results/flipbudget/ifeval_real_analysis.json`,
`results/flipbudget/ifeval_label_quality_check.json`.

## Two files were submitted; only one is IFEval

`ifeval_audit_l1_1.csv` (70 rows) — checked against `tc_expansion_key.json`'s
uid set: **exact match**. This is T-C's 70-row sheet, not IFEval, using the
bare 0/1 scheme (67×"1", 3×"0") already established as circular/lossy for
T-C earlier this session. T-C is already fully labeled and analyzed
(`TC_REAL_ANALYSIS.md`, `TC_ALPHA_BETA_UPDATE.md`) — **not used, adds
nothing new, and uses the wrong scheme for that sheet.**

`ifeval_audit_l1_judged.csv` (454 rows) — this one is genuinely IFEval:
uid set, row order, and prompt/response text all verified identical to the
sheet that was sent out. Uses 1/0 instead of YES/NO/PARTIAL, same as the
T-C file. For matching against **strict** specifically (which requires full
compliance) this is actually a lossless, defensible simplification — 1 =
fully compliant, 0 = not fully compliant, correctly collapsing NO and
PARTIAL together (strict doesn't distinguish them either). This part was
not the problem.

## The real problem: the naive result was implausible, and checking it directly confirmed why

Running the intended analysis (`fb_ifeval_real_analysis.py`) gave: β
(false-reject rate — verifier says non-compliant, human says compliant)
= **85.8% on the `disagree` stratum and 92.5% on `both_fail`** — implying
the automated verifier is wrong on strict/loose rejections nearly all the
time. That is an extraordinary claim, especially for `both_fail` (both
strict *and* loose — which already retries 8 lenient formatting variants —
reject it). Extraordinary claims get checked before being trusted, not
reported.

**Checked directly with the real verifier**, not a guess: refetched the
doc + response for all 454 sampled items, called the actual IFEval checker
(`inst_level_strict_acc`, the per-instruction pass/fail list, not just the
aggregate), and cross-referenced against each row's human judgment. Restricted to
rows on a **non-flagged** item key (541-item mechanism scan says these
checkers are fully deterministic — a "failed" verdict there is a fact about
the text, not a maybe).

**Result: of 318 human-marked-"compliant" rows on non-flagged items, 284
(89.3%) are directly contradicted by a concrete, deterministic instruction
failure** — the response provably violates a stated constraint (a comma
present when forbidden, missing required quotation marks, wrong sentence
count, malformed JSON, wrong word count, etc.), and the human still marked
it `1`. Breakdown by which instruction type is most often missed:

| Instruction | Contradicted rows |
|---|---|
| keywords:forbidden_words | 43 |
| punctuation:no_comma | 36 |
| startend:quotation | 36 |
| length_constraints:number_sentences | 30 |
| detectable_format:json_format | 30 |
| length_constraints:nth_paragraph_first_word | 20 |
| length_constraints:number_paragraphs | 18 |
| combination:repeat_prompt / length_constraints:number_words / startend:end_checker | 14 each |
| (9 more types, 1–11 each) | — |

**Two concrete examples, read directly:**
- Prompt: *"Don't contain the letter 'p' in your reply."* Response contains
  "**exp**ert", "to**p**-notch" — the forbidden letter appears 11 times.
  Marked `1` (compliant).
- Prompt: requires choosing exactly one of three fixed phrases verbatim
  ("My answer is yes/no/maybe.") and nothing else. Response is an unrelated
  paragraph that never states any of the three phrases. Marked `1`.

Both are objectively, mechanically wrong calls — not a matter of
interpretation. The pattern across all 19 affected instruction types is
consistent with a single mechanism: **these are the instructions that
require literal, mechanical verification (counting commas, counting
sentences, checking exact JSON/quote structure) rather than a holistic
read of "does this response seem reasonable."** A human skimming for
overall quality will systematically miss these in a way a careless
automated check would not — which is a real, useful, if uncomfortable,
finding about human-auditing IFEval-style benchmarks, not just a labeling
mistake to shrug off.

There is also a small, separate, likely-unrelated issue: 10/454 rows
(2.2%) had a response text mismatch on refetch (the HF dataset's stored
generation didn't match byte-for-byte what was in the sheet) — noted, not
investigated further, too small to explain the 89.3% figure above.

## What this means for the earlier numbers

**Retracted, not just caveated**: the α=2.5%, β=85.8%/92.5%,
human-corrected-accuracy=0.94 figures from `fb_ifeval_real_analysis.py` do
not reflect genuine scorer error at anywhere near that rate. The α figure
(both_pass stratum, 1/40) is plausible and likely fine — it wasn't
contradicted by this check because it's a "0" (non-compliant) mark, and
the check only interrogated "1" marks. The β/corrected-accuracy figures
are not usable.

## What's needed before the requested comparison and verdict can be done

This isn't a "your work was wasted" situation — the *data itself*
(prompt/response pairs, which items) is exactly right; the *judgments*
need to be redone or narrowed. Three options, not chosen here:

1. **Relabel**, with the README made to say explicitly: for prompts with a
   countable/formattable constraint (letter/word/sentence/paragraph counts,
   comma/quote/JSON formatting, forbidden/required keywords), check that
   constraint mechanically (count it) before marking compliant — don't
   judge on overall impression alone.
2. **Narrow the human task** to only the instruction types that are
   genuinely judgment-based (tone, audience-appropriateness, "funny",
   language) and let the deterministic checker's own verdict stand
   unchallenged for the mechanically-checkable types — arguably the more
   defensible design in hindsight, since code counts commas better than a
   human skimming 454 rows.
3. **Flag and exclude** contradicted rows from this batch specifically and
   treat this as a much smaller, already-verified-clean subset going
   forward.

No further analysis or verdict was produced pending a decision — proceeding
past this without saying so would misrepresent the confidence of any
scorer-vs-human conclusion drawn from this batch.

## Update — round 2 and final status

README rewritten per option 1 (relabel with a stricter, example-led README).
Round 2 (`task2_compliance_audit.csv`, YES/NO this time) checked the same
way: **90.5% contradiction rate (335/370)** — worse than round 1's 89.3%,
only 1/454 rows marked NO. No measurable improvement from the rewrite.

Decision: **paused, not attempted a third time.** IFEval's human-audit angle
is set aside; the verifier-bug/reproducibility finding
(`IFEVAL_REPRODUCIBILITY_CHECK.md`) stands on its own and does not depend on
this. The 83.2% of real disagreement unexplained by a known mechanism
remains genuinely unresolved — not assumed to be scorer error. See
`CONSOLIDATED_VERDICT.md` for how this fits the project's overall verdict.
