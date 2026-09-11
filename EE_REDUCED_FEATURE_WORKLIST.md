# E-E reduced-feature worklist — real, achievable, and large

Per your choice: cut E-E from 9 to 5 features. Script:
`scripts/fb_ee_reduced_feature_worklist.py`. Output:
`results/flipbudget/ee_reduced_feature_worklist.json`.

## Feature selection — caveat stated up front

Top 5 by |standardized coefficient| from the existing fit: `n_newlines` (-3.92),
`ends_with_period` (-1.80), `has_therefore` (+1.62), `n_frac` (-1.26),
`char_length` (+1.23). **That fit was built on 5 events — the same fit Tier 1
found has a bootstrap CI touching chance.** This ranking is a reasonable,
data-driven starting point, not a stable one. Worth re-checking once labelling
produces more events, not treated as final.

## Target and real result

5 features × EPV≥10 (Peduzzi et al. 1996) = 50 events. Currently 5 → 45 more needed.

**Walked real per-pool availability this time — no capacity assumed, each pool
checked and dropped once actually exhausted** (the bug in the first-pass 9-feature
worklist). Result: **11 rounds, 6,742 real items, reaching 50.1 expected events —
target met, using essentially the whole remaining roster.** Active pool count falls
from 53 (round 1) to 1 (round 11) as pools exhaust in priority order.

## Say this plainly: 6,742 items is a large ask

This is not the 540-item interim round from the earlier pass — reaching even the
*reduced*-feature target requires labelling most of what remains. The real ceiling
(52.7 events, all 18,482 available items) and the 50-event target are close, which
is why nearly the full pool gets consumed. If 6,742 items is more than you want to
commit to, the interim-round option (540 items, ~22 events, reported with an
explicit small-n caveat) from `AUDIT_EXPANSION_DESIGN.md` remains available as a
smaller, honestly-underpowered alternative — your call, not assumed here.

## What this does not do

Zero new human labels. Does not refit E-E on the reduced feature set (no new events
exist yet to refit with — that only becomes possible once labelling happens).
