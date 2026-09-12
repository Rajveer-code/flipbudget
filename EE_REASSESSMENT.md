# E-E reassessment, post audit-design analysis

Per your instruction: "E-E should only be retained if it adds independent
evidence after accounting for what T-C and the audit-design analysis show."
T-C is out for labeling; the audit-design analysis is done (verdict D). Reassessing now.

## What E-E was for

Predict scorer wrongness from response-format features — originally motivated
as support for a **mechanism** claim: that scorer error is systematic
(format-predictable), not noise, backing a verdict-A-shaped story
(scorer-induced ranking sensitivity as the centerpiece).

## Why that motivation is now weaker

Verdict D centers the project on **B (audit-estimation uncertainty) + C
(audit-design methodology)** — neither needs a format-predictability mechanism
to be true. The reconciliation already showed the scorer-only layer is modest
(11.0%, barely above the 8.8% sampling baseline); E-E succeeding would
strengthen a secondary claim, not the centerpiece.

**Q6 of the audit-design analysis also narrows E-E's remaining practical use.**
E-E's other possible role — a working predictor as the engine for an *adaptive*
audit (label where the model says wrongness is likely) — was directly tested:
Neyman-optimal **static** allocation already coincides with the theoretical
oracle bound for minimizing aggregate variance. A working E-E predictor would
mainly help at the **item level within a stratum** (which specific credited
item to label next, not which model/stratum) — a real but second-order gain,
not the large one Neyman reallocation alone already captures.

## Recommendation

**Do not spend the 6,742-item budget on E-E as previously scoped.** It no
longer supports the paper's centerpiece and its remaining practical value
(item-level adaptive triage) is a second-order refinement on top of a
Neyman-optimal design that already works. If you want a cheap, bounded version
kept as a minor appendix result, the already-computed n=5 finding
(`ee_format_association.json`, honestly reported as underpowered) can stand
as-is — no further labeling needed for that framing. Retire the reduced-feature
worklist unless you see a reason to keep it I haven't accounted for.

## Status of the three open threads

- **T-C**: labeling sheet unchanged, waiting on you.
- **E-B/IFEval**: pipeline built and verified, blocked on gated HF dataset
  access (`EB_IFEVAL_STATUS.md`) — needs your account/token.
- **E-E**: recommend retiring the large-labeling plan per above; nothing
  further from me pending your call.
