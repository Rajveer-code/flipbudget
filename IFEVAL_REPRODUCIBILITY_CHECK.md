# IFEval reproducibility check — run before any human labeling

Scripts: `scripts/fb_ifeval_mechanism_rescan.py`, `scripts/fb_ifeval_repro_cache.py`,
`scripts/_ifeval_repro_worker.py`, `scripts/fb_ifeval_reproducibility_check.py`.
Result: `results/flipbudget/ifeval_reproducibility_check.json`.

**The 454-row labeling sheet (`labeling/ifeval_audit_l1.csv`) was not touched.**
It has no mechanism-flag column at all (`uid,prompt,response,your_judgment`
only), so nothing here required editing it. Ready to label, unchanged.

## Correction found before the check could even run: 33 flagged items was wrong

The prior scan (`IFEVAL_AUDIT_DESIGN.md`) checked only two named mechanisms:
`language:response_language` and `keywords:letter_frequency`. Re-reading
IFEval's own source (`instructions.py`) before trusting that scan further:
two more checker classes call the same unseeded `langdetect.detect()` —
`change_case:english_capital` (line ~1469) and `change_case:english_lowercase`
(line ~1501). Rather than hand-map every checker's optional kwargs for a
similar random-fallback risk, the rescan is empirical: monkeypatch
`random.choice`/`random.randint`, run the real verifier on all 541 items with
a placeholder response, and record whether either was actually invoked.

**Corrected count: 96/541 items (17.7%), not 33/541 (6.1%).** Breakdown: 94
langdetect-only, 1 letter_frequency-only, 1 both. The old 33 are a strict
subset — no keys lost, the original scan just stopped looking too early.

Updated in place (derived annotation files, not the sheet or the sample
composition): `results/flipbudget/ifeval_nondeterminism_flagged_items.json`
(old count preserved in the file for the record) and
`results/flipbudget/ifeval_audit_key.json` (`nondeterminism_flagged`: 29→75 of
the 454 sampled rows — the key file the labeler never sees, not the sheet).

## Method: fresh-process replicates, not repeated in-process calls

Genuinely separate `subprocess.run` calls (`scripts/_ifeval_repro_worker.py`),
each one independent pass over all 2,592 rows (96 flagged items × 27 models)
whose key carries a known mechanism. This is the right unit of reproduction:
the real harness runs once per model evaluation in one process sharing one
random stream across items, not once per item in isolation — a per-row-fresh-
process design would have been a less realistic, artificially-independent
assumption.

Two conditions, 15 + 5 replicates:

- **UNSEEDED** — the real, shipping condition. `DetectorFactory.seed` at its
  default `None`, `random` module never seeded.
- **SEEDED (control)** — `random.seed(42)` fixes `keywords:letter_frequency`'s
  fallback (confirmed from source: it calls the global `random.choice`, so the
  module seed applies directly). `langdetect.detector_factory.DetectorFactory.seed
  = 42` separately fixes langdetect's own `Detector`, which seeds its *own*
  `random.Random()` instance from `self.seed` (confirmed from
  `langdetect/detector.py` line 154: `self.random.seed(self.seed)`) — the
  global module seed alone does **not** reach it, which is why both knobs are
  set, not just one.

## Results

**1. Item-level verdict volatility.** UNSEEDED: 49/2,592 rows (1.9%) show more
than one distinct (strict, loose) outcome across 15 replicates. SEEDED
control: 0/2,592 — zero variance once both knobs are fixed. This is the causal
confirmation, not just a correlation: same rows, same code, only the seed
state differs, and only the unseeded condition is unstable.

**2. Benchmark-score impact.** Overall strict accuracy: baseline (the one
realization already on record) 0.3472; across the 15 unseeded replicate
universes, range [0.3469, 0.3473], std 0.00012. **Negligible** — under 0.05
percentage points of spread on the headline number.

**3. Model-ranking impact.** Kendall's τ against the baseline ranking: 0.977–
0.989 across all 15 replicates (near-perfect concordance). Max single-model
rank displacement: **2 positions**, consistently, in every one of the 15
replicates (the same pair of adjacently-ranked models trading places, not
random noise). **The #1-ranked model never changes in any replicate.**
Nondeterminism from this mechanism does not reach the comparisons that would
change a headline claim about which model is best, but it is not exactly zero
either — a claim about a specific model being, say, 3rd vs 5th on this
benchmark should be read with 2 positions of play from this source alone.

**4. Corrected disagreement decomposition.** Of the 380 real strict/loose
disagreements (380/14,607 = 2.60%, unchanged — this is measured directly from
the roster, not affected by the mechanism-count correction):

| | Prior (incomplete, 33-item scan) | Corrected (96-item scan) |
|---|---|---|
| Explained by a known mechanism | 31/380 (8.2%) | **64/380 (16.8%)** |
| Unexplained | 349/380 (91.8%) | **316/380 (83.2%)** |

The headline qualitative conclusion is unchanged and, if anything, more
firmly established by doing the scan properly: **the large majority of
strict/loose disagreement (83.2%) is not explained by either known verifier
mechanism** and remains the genuine target of human audit. But the earlier
91.8% figure overstated how "clean" the unexplained bucket was — roughly twice
as much of the disagreement signal traces to a known bug as originally
credited. Reported here rather than left standing uncorrected, per the
standing rule that a wrong number doesn't get to survive because the
qualitative story still holds.

## What this does and does not settle

Settled: the mechanism is real, is fully explained by a missing/absent seed
(not some other latent instability), and its effect on the benchmark-level
conclusions that matter most (overall score, model ranking, which model is
best) is small. Not settled: the other 83.2% of disagreements — that is
exactly what the 454-row human audit is for, unchanged from
`IFEVAL_AUDIT_DESIGN.md`.

## Next step

None until the labels come back. `labeling/ifeval_audit_l1.csv` is unchanged
and ready. After labeling: compare known verifier bugs (this file) vs.
unexplained scorer disagreement vs. human-validated scorer error, per the
three-way breakdown requested.
