# Independent benchmark search (item 9)

Searched beyond Open LLM Leaderboard, as instructed, rather than re-asserting the prior "blocked" conclusion (which only checked the already-authenticated open-llm-leaderboard details repos specifically).

## Real candidates found

| Source | Response-level data? | Reproducible scorer? | Different benchmark? | Different scoring mechanism? | Multiple models? | License |
|---|---|---|---|---|---|---|
| **HELM** (Stanford CRFM) | **Yes** — "releases all raw model prompts and completions publicly... a Web UI for inspecting individual prompts and responses" | Yes, open-source framework (`stanford-crfm/helm`, GitHub) | Yes — dozens of scenarios, several exact-match/symbolic-scored like MATH-Hard | Yes — HELM includes both exact-match and LLM-judge-scored scenarios in the same public release | Yes, large model roster | Open (Apache-2.0 framework; per-scenario dataset licenses vary, checked at use time) |
| **AlpacaEval** (Tatsu Lab) | Yes — per-item outputs on Hugging Face (`tatsu-lab/alpaca_eval`), includes `alpaca_eval_all_outputs` | Yes — public judge-annotator code, reproducible via API replay | Yes — instruction-following, not math/format | **Yes — judge-scored (LLM-as-judge), the one scoring paradigm this project has not yet tested** | Yes | Apache-2.0 / MIT-style, redistribution permitted |
| **Every Eval Ever** (EvalEval Coalition, arXiv 2606.14516) | Partial — "optionally stores per-instance outputs where source logs provide them" | Depends on underlying source | Aggregates HELM, lm-eval-harness, Inspect AI results under one schema | Multiple, by construction | Yes, 22,235 models across 2,273 benchmarks (as of the paper) | Community/HF-hosted, designed for reuse |

All three are real, licensed, response-level, and satisfy "different benchmark" and (HELM, AlpacaEval) "different scoring mechanism" — the prior session's "blocked" conclusion was correct for the specific source it checked, but too narrow as a statement about independent replication generally.

## Why this is not executed as a full replication in this pass

Actually running E-A/T-C-style analysis on HELM or AlpacaEval requires the same two ingredients T-C needed here: (1) a working, auditable scorer for that benchmark (straightforward for HELM's exact-match scenarios; already-existing for AlpacaEval's judge), and (2) a **new human-labeling round** to audit that scorer's real false-positive/false-negative rate on a sample — exactly the kind of new human-labeling task the standing instruction reserves for you, not for autonomous execution. Starting a partial version (scraping data but never auditing it) would be unfinished work of the kind the instructions explicitly warn against ("do not add work merely to make the paper larger").

## Recommendation

**HELM is the strongest candidate for a genuine independent-replication follow-up**: it already ships both exact-match and judge-scored scenarios from the same public release, meaning a single follow-up project could test the SSM/audit-design framework's generalization across scoring paradigms (item 9 of the original 25-point list) using ONE data source. This is now a properly scoped, named, ready-to-start follow-up — not a dead end — contingent on you allocating a new (smaller, since HELM scenarios are pre-scored) human-audit round.
