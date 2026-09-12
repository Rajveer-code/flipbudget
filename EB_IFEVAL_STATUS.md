# E-B scale-out: IFEval — corrected choice, verified pipeline, blocked on access

## Correction to the prior recommendation

Recommended GPQA last turn. Checked the actual task configs before building
anything (per the "verify before proceeding" discipline this whole project
runs on) and that recommendation was wrong: GPQA, MMLU-PRO, and MuSR are all
`output_type: multiple_choice` in the vendored harness — loglikelihood-scored
over the literal strings `"(A)"`–`"(D)"`, with no free-text generation and no
parsing/extraction step. **No analogous scorer-error mechanism can exist
there at all** — there's nothing to misparse.

**IFEval is the right choice**: `output_type: generate_until` — the model
free-text generates, and a programmatic verifier checks compliance. The
harness's own **strict vs. loose** scoring split is a direct, human-label-free
proxy for verifier ambiguity (loose retries 8 response-formatting variants
before crediting compliance) — this project's exact object of study, visible
without needing new labels to detect it.

## What's verified and ready

`scripts/fb_eb_ifeval_pull.py` — code-complete, syntax-checked, fails at
exactly the right point (missing credentials) when run now.

**The real verifier was pulled in and tested**, not assumed: loading
`lm_eval.tasks.leaderboard.ifeval.utils.process_results` directly triggered
the full harness's dependency chain (`TaskManager → sacrebleu`, irrelevant to
reusing two scoring files) — worked around with the same package-stubbing
technique already used for the MATH-Hard comparator, extended one level
deeper. Two more real, legitimate runtime dependencies of the verifier itself
surfaced and were installed (`langdetect`, `immutabledict`, `nltk`) — not
artifacts of the loading trick. **Confirmed working** on a synthetic
compliant/non-compliant pair against the real 25-entry instruction registry:
correctly scored a comma-free sentence as compliant and a comma-containing one
as not, under the real `punctuation:no_comma` checker.

## Blocked, confirmed not merely a missing token

`open-llm-leaderboard/<model>-details` on HuggingFace is a **gated dataset**.
Tried anonymous access (401) and `huggingface_hub.hf_hub_download` (raises
`GatedRepoError` explicitly, not a generic auth error) — confirmed via the
library's own error, not guessed. This needs an **authenticated HF account
with granted access to this specific gated dataset**, not just any
`HF_TOKEN` — `HF_TOKEN` alone will fail the same way if the account behind it
hasn't been granted access.

## Concrete next step

Once you (a) confirm your HF account already has access (the original
`cache_l1` MATH-Hard pull had to have gone through this same gate at some
point) and (b) set `HF_TOKEN` in the environment, `fb_eb_ifeval_pull.py` runs
immediately — no further code changes needed. It will pull real per-model
IFEval generations, score them with the verified real verifier, and report the
strict/loose disagreement rate per model directly (the human-label-free
ambiguity signal) — the first real number toward answering whether E-A/the
reconciliation's verdict generalizes to a second, differently-scored
benchmark.

## What this does not do

No data fetched, no numbers computed, nothing fabricated in its place. Does
not start a human audit for IFEval (that decision, and its own audit-design
sizing, comes after real strict/loose disagreement data exists to plan
around).
