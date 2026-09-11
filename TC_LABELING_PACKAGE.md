# T-C labeling package — ready to label

Script: `scripts/fb_tc_labeling_package.py`. Files:
[labeling/tc_expansion_l1.csv](labeling/tc_expansion_l1.csv) (70 rows, **open this
to label**) and `results/flipbudget/tc_expansion_key.json` (scoring key —
**do not open while labeling**).

## Blinding — reused, not reinvented

`HUMAN_LABELING_GUIDE.md` in the companion project documents a real prior
regression: an earlier sheet put `stratum|model|item_id` straight into the HTML
source. Never rendered, but visible to anyone who viewed source — defeats
blinding as surely as showing it outright. Reused that fix exactly:
`uid = sha256(f"{stratum}|{model}|{item_id}")[:16]`, same construction, same
truncation (response capped at 6,000 chars). The CSV has only `uid, problem,
response, your_answer` — no model name, no item_id, no stratum anywhere in the
file (checked directly: grepped for every model name in the roster against the
full CSV text, zero matches).

## What's in it

70 rows from the top 40 candidate pairs (30 distinct items, some shared across
multiple pairs — one item has 4 models represented, yielding several pairs at
once). Distribution: 22 items → exactly 2 models (one pair each), 6 items → 3
models, 2 items → 4 models. Every item yields at least one real new paired
observation toward T-C's ≥20 target; several yield more.

## How to label it

Same rules as the existing audit — `HUMAN_LABELING_GUIDE.md`'s MATH-Hard
protocol: type the transcribed final answer exactly as written (no
normalizing), `NONE` for no commitment, `CONTRADICTORY` for two unresolved final
answers, self-correction resolves to the last stated value. Fill only
`your_answer`; leave `uid` untouched. Save as CSV.

## After labeling

`tc_expansion_key.json` maps each `uid` back to (model, item_id, stratum,
subject, gold) and lists which `uid`s pair together (shared `item_id`) —
everything needed to extend `tc_correlated_error.py`'s item-level test with real
new paired observations. Not run yet — that's the next step once you've labeled.

## What this does not do

Zero labels filled in. Does not re-run T-C's test (nothing to test until the CSV
comes back filled). Selection rule (top-40 by joint expected-yield score) was
already committed in `results/flipbudget/tc_ee_real_worklist.json` before this
package was built — the item selection isn't influenced by anything in the
responses themselves, only by the priors (which pools are high-α/β) already on
record.
