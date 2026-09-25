# How to label — read this once, fully, before opening the app

Written 2026-09-25. This is the instruction sheet for the two outstanding labelling jobs.
Follow it exactly and the batches will pass the gate. The three excluded attempts failed on
process, not on effort, so the process is what this document is about.

---

## 0. The single most important thing

**You do not type into the sheet CSV.**

The CSV is the *input*. You load it into `labeling/app/label.html`, which shows you one
response at a time and writes a *different* CSV when the batch is finished.

| | Input (you load this) | Output (the app writes this) |
|---|---|---|
| Columns | `uid, problem, response, your_answer` | `uid, your_answer, start, end, batch_id, paste_attempts` |
| Who fills it | Nobody. `your_answer` stays empty | The app, from what you type |
| Where it lives | `labeling/audit_v3_l1.csv` | `labeling/exports/` |

The output carries the per-item timestamps, the immutable batch id and the paste counter.
Those three things are the entire evidentiary value of the audit. A CSV filled in Excel has
none of them, and `scripts/fb_audit_v3_gate.py` rejects it before it looks at a single answer.

If the app will not open or the sheet will not load, stop and tell me. Do not fall back to
editing the CSV by hand.

---

## 1. The two jobs

### Job A — the provenance check, 60 rows

- **Sheet:** `labeling/relabel_check_l1.csv`
- **Export to:** `labeling/exports/relabel/`
- **Batches:** 2 (50 rows, then 10)
- **Why:** a stratified subsample of the 458-row sheet you labelled in September. A fresh
  timed pass measures agreement with those labels instead of arguing about them. Pass and all
  458 are admitted; fail and they stay out. The criteria were fixed on 2026-09-24 in
  `VALIDATION_RELABEL.md`, before the sheet was drawn, and they do not move.
- **Do not** open `provenance/excluded_labeling_attempts/` at any point while doing this. If
  you look at what you answered last time, the measurement is worthless and we cannot redo it.

### Job B — the registered audit, 458 rows

- **Sheet:** `labeling/audit_v3_l1.csv`
- **Export to:** `labeling/exports/`
- **Batches:** 10 (9 × 50, then 8)
- **Why:** this is the audit Section 4 of the paper describes and Results §5.6 is waiting on.
  It shares no rows with the September sheet. It is the bigger job and the one that finishes
  the paper.

Job A is two sittings. Job B is ten. Do A first — it is short, and its outcome changes how
much of the old work survives.

---

## 2. Running the app

1. Open `labeling/app/label.html` in a browser. It is offline; nothing leaves the page.
2. Choose the sheet file.
3. Pick a batch from the dropdown. Batches are fixed at 50 rows and are numbered; finished
   ones are marked `(done)`.
4. Click **Start batch**.
5. For each item: read the problem, read the response, type the final answer, press Enter.
   Or click **NONE** / **CONTRADICTORY**.
6. At the end of the batch the app shows a SHA-256 and a **Download CSV** button. Download it
   and put it in the export folder for that job. Do not rename it.
7. Tell me the batch is done and I will run the gate on it.

Progress within a batch is saved, so closing the tab mid-batch does not lose work. The batch
id is created when you first start it and never changes — that is deliberate, and it is why a
batch cannot be quietly restarted to get a cleaner-looking one.

---

## 3. What you are actually deciding

The task has two halves and only the first one needs a human.

**The judgement:** what final answer does this response commit to? A regular expression cannot
do this. It cannot tell that a response worked to `x = 3`, then said "but wait, that violates
the constraint, so `x = 5`". It cannot tell that a box appears mid-derivation and is not the
conclusion. It cannot tell that a response trails off without ever committing.

**The transcription:** once you have decided which statement is the final answer, write that
statement exactly as the response wrote it.

So: read to decide *which*, then copy *that* faithfully.

This matters because of a confound we already hit. The September instructions said "copy
exactly what is inside the box", which turns the job into optical character recognition and
mechanically raises agreement with the automated extractors. That is one of the three
explanations we cannot currently rule out for those labels. The rule above is different in a
way that matters: the box is usually the commitment, but you decide that it is, rather than
assuming it.

### The three answers

| You type | When |
|---|---|
| the answer | The response commits to exactly one final answer |
| `NONE` | The response never commits to a final answer |
| `CONTRADICTORY` | The response presents two different answers, both as final |

`NONE` is for a response that stops mid-working, loops, refuses, or produces prose with no
answer in it. It is **not** for a response whose answer looks wrong to you. A confidently
wrong answer is still an answer — transcribe it. Whether it is correct is decided later, by
the benchmark's own equivalence routine, against a reference answer you are never shown.

`CONTRADICTORY` is for two competing *final* answers, not for a correction. "I get 7 — no
wait, 9" is a commitment to 9. "The answer is 7. The answer is 9." with neither withdrawn is
contradictory.

### Formatting

Write the answer and nothing else.

- Do not wrap it in `\boxed{}`. Type `3/4`, not `\boxed{3/4}`.
- Do not add "Final Answer" or "I hope it is correct".
- Do not add units or words the response did not use.
- Keep the response's own form: if it wrote `\frac{1}{2}`, write `\frac{1}{2}`; if it wrote
  `0.5`, write `0.5`. Do not normalise, simplify or convert. The equivalence routine handles
  that, and it is one of the things the paper measures.
- No line breaks. One line per answer.

The gate fails a batch with three or more answers containing `\boxed`, "Final Answer", "I hope
it is correct", a newline, or more than 200 characters.

---

## 4. What the gate checks, so nothing surprises you

`scripts/fb_audit_v3_gate.py` runs on each exported batch. Any one of these fails it:

| Check | Threshold |
|---|---|
| Structure | Every uid on the sheet, no duplicates, one batch id, ≤ 50 rows, start before end |
| Paste | **Zero** blocked paste or drop attempts |
| Dwell | Median **≥ 15 seconds** per item |
| Burst | No run of more than **20 consecutive** items under 3 seconds each |
| Artifacts | Fewer than **3** answers containing generation artifacts |
| Extraction | Exact-match-with-a-regex rate not implausibly high, Poisson-binomial p ≥ 0.001 |

Three of those deserve a sentence each.

**Paste.** The box refuses paste and counts the attempt. One attempt fails the batch. If you
reflexively hit Ctrl+V, you have burned that batch — tell me and we redraw that batch's id
honestly rather than hiding it.

**Dwell.** Median, not mean, so a few fast obvious ones are fine. Fifteen seconds is not a
target to hit; it is a floor that reading actually clears. If you are consistently under it,
you are skimming rather than reading, and the label quality is the thing at stake, not the
number.

**Extraction.** This is the automation detector. It asks whether you typed exactly what a
regex would have extracted more often than a genuine human reader does. The comparison is
against your own accepted 400-item audit: on rows with a boxed answer, 287 of 350, about 82%.
So typing the box contents most of the time is *expected and fine*. Do not try to manage this
number. Do not deliberately introduce variation to look human — that is falsifying data, it
would corrupt the measurement the paper reports, and it would be far worse than a failed
batch. Read honestly and the rate lands where it lands.

---

## 5. Pace

Ten batches of 50 for Job B. At a genuine reading pace that is roughly 20–30 minutes a batch,
so about four to five hours total, and it does not have to be one day.

Do not do more than two or three batches in a sitting. Attention drops, dwell drops with it,
and a tired batch is more likely to fail the gate than a batch you did tomorrow. There is no
deadline inside the audit itself — the deadline is the paper, and a redone batch costs more
than a rested one.

---

## 6. What I cannot do, and why

I cannot label any of these rows, cannot pre-fill `your_answer`, cannot suggest an answer for
a specific uid, and cannot "clean up" an export. Not a policy I am applying to be difficult:
the paper's central claim is about what a *human reader* credits, measured against what
automated extractors credit. A label produced by an AI tool is an extractor label wearing a
human label's clothes, and it would silently destroy the quantity being measured.

The examples in section 3 are invented for this document. None of them is from either sheet.

What I can do: run the gate, run the agreement measurement, tell you which batches passed,
and write up whatever the numbers say — including if they say the September labels stay
excluded.

---

## 7. When a batch is done

Tell me, and I will run:

```bash
python scripts/fb_audit_v3_gate.py labeling/exports/<the file you downloaded>
```

For Job A, once both batches are in:

```bash
python scripts/fb_relabel_agreement.py
```

The verdict is whatever comes out. It was fixed in advance for exactly this reason, and we
report it either way.
