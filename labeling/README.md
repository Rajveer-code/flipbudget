# Labeling instructions

Two spreadsheets, two different tasks. Read the section for the one you were
given. Don't look anything up, don't try to guess who wrote a response —
judge only from the text in front of you.

Only ever type in the last column. Leave every other column exactly as it
is — `uid` in particular is how your row gets matched back to the right
item; if it gets edited, duplicated, or deleted, that row can't be used.
Don't reorder, sort, or filter rows. Save as CSV when done (not .xlsx) and
send it back with the same filename it came with.

---

## `tc_expansion_l1.csv` — math problems

Each row has a math problem and a model's response to it. Your column is
`your_answer`.

**What to do:** find the final answer the response commits to, and type it
exactly as written — same notation, same form. `\frac{1}{2}` stays
`\frac{1}{2}`, not `0.5`. `x=2` stays `x=2`, not `2`. You're transcribing what
the text says, not solving the problem yourself and not simplifying it.

- **Response never gives a final answer** (cut off, refuses, never
  concludes) → type `NONE`.
- **Response states two different final answers with no resolution between
  them** (not a correction, just two contradicting claims both presented as
  final) → type `CONTRADICTORY`.
- **Response corrects itself** ("wait, that's wrong, actually it's X") → type
  the final, corrected value. That's one commitment, not a contradiction.
- **Response hedges between options and never picks one** ("it could be
  1/2 or 1/3") → `NONE`. If it hedges and then picks one, type the pick.
- **Response is cut off mid-way** → use whatever answer was already stated
  before the cutoff. If nothing was stated yet, `NONE`.
- **You genuinely can't tell** what it commits to → `NONE`. Don't force a
  guess.

Long response cells look intimidating in a spreadsheet — widen the column or
turn on wrap-text rather than skimming.

---

## `ifeval_audit_l1.csv` — instruction-following

Each row has a prompt (which may contain one or more specific instructions —
e.g. "write X, and don't use commas") and a model's response to it. Your
column is `your_judgment`.

**What to do:** decide whether the response actually does what the prompt's
instructions ask for.

- **Response follows every instruction in the prompt** → type `YES`.
- **Response fails at least one instruction** (if there's only one
  instruction, this means it fails it) → type `NO`.
- **Prompt has multiple instructions and the response follows some but not
  all of them** → type `PARTIAL`.

Judge only against what the prompt actually asked for — not whether the
response is well-written, correct on facts, or something you'd personally
prefer.
