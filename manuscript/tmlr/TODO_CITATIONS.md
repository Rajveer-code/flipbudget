# Citation verification status

Rule, unchanged: **no claim about a cited work enters the paper until the work has been read.**
If a paper turns out to make a claim closer to this one than Section~\ref{sec:related} implies,
the related-work text changes, not the citation.

This file records, for every work cited in the TMLR draft, how far verification has gone. Three
levels are used.

- **metadata** — the bibliographic record was retrieved from an authoritative source on the date
  shown, so authors, title, venue and year are right.
- **abstract** — the abstract was retrieved from the arXiv API or the publisher and the sentence
  the paper writes about the work is supported by that abstract alone.
- **read** — the author has read the paper and confirms the sentence.

Nothing in the draft may rest on a claim stronger than the level recorded here.

## Verified on 2026-09-25 by DOI content negotiation

`https://doi.org/<doi>` with `Accept: application/x-bibtex`. Level: **metadata**.

| Key | Note |
|---|---|
| `hoeffding1963probability` | JASA 58(301), 13--30. Theorem~4 is cited by number in Appendix~A; confirm the numbering in the published paper before submission. |
| `sidak1967rectangular` | JASA 62(318), 626--633. Cited for the allocation formula only, which is used under independence where it is exact. |
| `rosenbaum2004design` | Biometrika 91(1), 153--164. |
| `horowitz1995identification` | Econometrica 63(2), 281--302. **Author order is Horowitz then Manski**; the previous paper's bibliography had it reversed and the key was renamed to match. |
| `molinari2008partial` | J. Econometrics 144(1), 81--117. |
| `begg1983assessment` | Biometrics 39(1), 207--215. |
| `hui1980estimating` | Biometrics 36(1), 167--171. |
| `dawid1979maximum` | Applied Statistics 28(1), 20--28. |
| `lang2014confidence` | Prev. Vet. Med. 113(1), 13--22. |
| `tenenbein1970double` | JASA 65(331), 1350--1361. |
| `neyman1938contribution` | JASA 33(201), 101--116. |
| `neyman1934stratified` | JRSS 97(4), 558--606. |
| `horvitz1952generalization` | JASA 47(260), 663--685. |
| `angelopoulos2023ppi` | Science 382(6671), 669--674. |

## Verified on 2026-09-25 by the arXiv API

Exact-title or id query; the author lists in `references.bib` are the ones the API returned.
Level: **abstract**, except where noted.

| Key | arXiv id | Note |
|---|---|---|
| `chen2026partial` | 2606.15031 | Closest concurrent work. The draft states their setting (prevalence of a latent binary attribute from a panel of model reports, errors arbitrarily dependent given the truth, unidentified without restrictions, bounds under weak stochastic ordering) directly from the abstract. **Read in full before submission** -- if their restriction implies or is implied by $H(\varepsilon)$, that belongs in the paper. |
| `lee2026judge` | 2511.21140 | The draft claims Proposition~\ref{prop:oneverifier} applies when the judge's sensitivity and specificity are common across the compared models. The abstract says the framework corrects bias from the judge's sensitivity and specificity using a calibration set. **Read in full**: confirm the operating characteristics are modelled as common across the evaluated population, and soften the sentence if they are not. This is the sharpest differentiating claim in the section and the one a reviewer is most likely to check. |
| `chatzi2024ranking` | 2402.17826 | Rank sets for LLMs from pairwise comparisons by a strong model calibrated on human comparisons. |
| `fisch2024stratified` | 2406.04291 | Title is *Stratified Prediction-Powered Inference for Hybrid Language Model Evaluation*; the previous paper's bibliography had a different wording, now corrected. |
| `zrnic2024active` | 2403.03208 | |
| `boyeau2025autoeval` | 2403.07008 | Author list corrected to the arXiv one; the previous bibliography listed an author the API does not return. Key retains the `2025` suffix for stability; the entry year is the arXiv year. |
| `li2025verifybench` | 2507.09884 | |
| `liu2025compassverifier` | 2508.03686 | |
| `morikawa2026tsneyman` | 2606.08418 | |
| `lewkowycz2022minerva` | 2206.14858 | The draft says the leaderboard's original extraction pattern *descends from* the Minerva convention. **Confirm against the harness source**, not the paper, since the claim is about lineage of code. |
| `salaudeen2025measurement` | 2505.10573 | Was previously unverified metadata from a reviewer's report. Metadata and abstract now confirmed; the draft's characterisation follows the abstract. |
| `reuel2024betterbench` | 2411.12990 | Same. Full author list recovered (Reuel, Hardy, Smith, Lamparth, Hardy, Kochenderfer); the `and others` placeholder should be replaced before submission. |

## Verified on 2026-09-25 by retrieval

| Key | Note |
|---|---|
| `kydlicek2025fixing` | `https://huggingface.co/blog/math_verify_leaderboard` returns HTTP 200 with the title *Fixing Open LLM Leaderboard with Math-Verify*. Now cited in Section~\ref{sec:data} where the February 2025 rescoring is described, which it previously was not. |
| `fourrier2024openllm` | The v2 leaderboard space returns HTTP 200. Added alongside `openllmleaderboard` in Section~\ref{sec:data}: MATH-Hard is a v2 task, and the pre-existing citation pointed at the v1 space. |

## Carried over from the previous paper's bibliography

`sclar2023quantifying`, `biderman2024lessons`, `yu2024xfinder`, `manski2003partial`,
`cochran1977sampling`, `kish1965survey`, `clopper1934use`, `openllmleaderboard`,
`hendrycksmath2021`, `opencompass2026`, `fourrier2024lighteval`, `openai2024simpleevals`,
`alzahrani2024benchmarks`. The author has used these before. Each placement in the rewritten
Section~\ref{sec:related} must be re-read before submission to confirm the sentence it supports.

## Open decision for the author

`pall2026identified` -- the author's own earlier manuscript, *Benchmark Accuracy Is Not an
Identified Quantity* -- is **not cited** in the current draft. Section~\ref{sec:data} refers to
"the subset of models analysed in earlier work" without a pointer. Three things are in tension
and only the author can resolve them:

1. TMLR review is anonymous, and the entry's own note says the manuscript is under review at
   TMLR and is not posted publicly, so a reviewer could neither read it nor fail to guess who
   wrote it.
2. Leaving the overlap unreferenced invites a reviewer to ask what the relationship is.
3. If that manuscript is an earlier version of *this* paper rather than a separate work, citing
   it would be wrong outright.

Decide before submission. If it is cited, it goes in third person with no self-identifying note.
