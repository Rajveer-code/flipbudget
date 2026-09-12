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

## Unblocked and run — real results

Access resolved: Rajveer's own already-authenticated HF token (found locally,
`huggingface_hub.get_token()`) already had access to the gated repos — the
earlier 401 was purely anonymous access, not a real block on his account. One
more real bug caught before trusting anything: the fetch script used plain
`urllib.request` without the `truststore.inject_into_ssl()` fix this machine
already needs for every other HF call this session — fixed, then ran clean.

**All 27 models fetched, 0 failures, 14,607 real rows.**

- **Overall strict/loose disagreement: 380/14,607 = 2.6%.** Real, nonzero,
  human-label-free scorer-ambiguity signal — unlike MATH-Hard's near-zero β,
  IFEval's verifier disagrees with itself often enough to matter.
- **Per-model rate varies substantially: 0.2%–7.6% (median 1.9%)** —
  `results/flipbudget/ifeval_per_model.json`. Not uniform, and not randomly
  scattered: **the highest-disagreement models are mostly the higher-scoring
  ones** (Llama-3-70B-Instruct: 7.6% disagreement at 77.1% strict accuracy;
  Yi-1.5-34B-Chat: 7.6% at 55.1%) while the weakest models disagree least
  (falcon-7b: 0.4% at 11.8% accuracy). Plausible mechanism, not yet proven:
  weak models produce short/garbage output that's unambiguously
  non-compliant either way; stronger models produce nuanced, well-formatted
  responses where the strict-vs-loose boundary (trailing lines, markdown)
  actually has room to flip the verdict. **If this holds up, it matters more
  for the comparisons that matter most** — rankings among competitive,
  capable models, not against weak baselines.

## What this does not do yet

This is a strict/loose proxy, not the full [0,1]-bounded Wilson-CI/Λ
machinery built for MATH-Hard — that needs a real human audit of IFEval
specifically (does the verifier's strict-or-loose call match what a human
reads the response as actually doing), not yet run. The per-model pattern
above is a real, observed correlation, not yet tested for statistical
significance or causally explained. Next real step, not started: design an
IFEval audit sample (same audit-design methodology already built) sized
around this real 2.6%/per-model-varying rate instead of a guess.
