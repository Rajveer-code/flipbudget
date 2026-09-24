# Why this problem matters — draft for the author to make his own

Rajveer: you asked me to write this. Read it as a starting point, not as your voice. Two of
the three things below I can support from the repository record; the third is about what you
personally care about, and only you can write that honestly. Where I have guessed at your
reasons, I have marked it.

Intended home: the opening of the discussion, or a short paragraph at the end of the
introduction. Not the abstract.

---

I started this because a number I had published was wrong, and the reason it was wrong was
not the model, the data, or the statistics. It was a piece of scoring code that nobody, me
included, had ever read carefully.

The specific case is small enough to describe in a sentence. A model answered a currency
conversion question correctly, wrote the answer in a box the way the benchmark's own
reference solutions do, and finished with "Great job!" instead of the exact sentence the
scorer was looking for. The scorer found no answer. A response with no answer found is
recorded the same way as a response with a wrong answer, so the model lost the point. The
leaderboard reports that loss as a fact about the model's mathematics.

Once I started looking, the same pattern was everywhere, and it was not a matter of one badly
written extractor. The leaderboard I was studying had already replaced its own MATH verifier
once, in February 2025, and the published scores moved while the model outputs stayed
identical. So the same responses, the same models, and the same benchmark produced two
different leaderboards depending on which verifier was running. That is not a bug that
someone can fix. It is a design choice that the published output does not record.

[AUTHOR: the paragraph above is the honest technical reason. What is missing is your reason.
Something like: what you were originally trying to do when you hit this, what made you keep
going after the first rejection, and why a ranking being wrong bothers you specifically.
Two or three sentences in your own words will do more for this paper than anything I can
write here.]

What kept me on it was the second half of the problem, which is harder and more interesting
than the first. Showing that a score is uncertain is easy and slightly useless; a reader can
reasonably answer that published accuracies were always a lower bound and that everyone knew
it. The question that actually matters is whether the *ordering* survives, and that question
cannot be answered by reporting a wider error bar. It has to be answered by reading responses,
and there is never enough labeling budget to read enough of them. Everything in this paper
that looks like machinery exists because of that gap: the only way to certify a ranking from a
few hundred labels is to assume that the models behave similarly where the verifiers agree,
and the only honest way to use that assumption is to say exactly how much of the result rests
on it.

I also found a defect in my own code while doing this, and it had silently invalidated my
earlier verifier comparisons. The equivalence check I relied on guards itself with a timer
that does not exist on Windows, fails, and returns "not equivalent" for every call. Every
comparison I had run for months was really a string match. Reporting that is uncomfortable,
and it is also the strongest single piece of evidence for the paper's argument: if the author
of a paper about verifier error can run a broken verifier for months without noticing, a
leaderboard maintainer scoring tens of thousands of responses can too.

---

## What I could not write for you

The one thing missing is why *you* care, which is the part reviewers respond to and the part
that cannot be reconstructed from a repository. Answer these three in your own words, badly
and quickly, and I will edit them into the draft:

1. What were you actually doing when you first hit this? What were you trying to measure?
2. When the first version was rejected, why did you keep working on it instead of moving on?
3. Who do you think is harmed if leaderboard rankings are wrong in this way? Be specific
   about a person or a decision, not "the community."
