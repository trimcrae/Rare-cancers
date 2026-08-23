---
name: eli5
description: Explain something in plain language, the way you would to a smart person who does not work on this project. Load when the user types /eli5, or asks for it in their own words — "explain it like a normal person", "in plain English", "I don't follow", "assume I know nothing", "what does that actually mean" — or when they push back on an answer that was dense rather than wrong. Covers the rewrite rules (lead with the point, one idea per sentence, jargon gets replaced not glossed, at most one analogy), what plain language must NOT change (a hedge, a null, an unknown or a number stays exactly as strong as it was), and the failure modes that make an eli5 worse than the original — talking down, hollowing out, and the analogy that quietly becomes the argument.
---

# Explain it like a normal person

**The audience is not a child.** It is a smart adult who does not work on this project, has not read
the roadmap, and does not know what `valB_mini` is. They can follow anything if you build it in
order. They cannot follow a sentence that assumes six things they have never heard of.

⚠ **This repository is the reason this skill exists.** Its documents are written for the next agent
session — glyph-dense, identifier-heavy, every clause load-bearing. That register is correct *in the
repo* and wrong *in a reply to a human*, and the two keep getting confused.

---

## The rewrite rules

1. **Lead with the answer.** First sentence says the thing. Setup, caveats and evidence come after.
   If the reader stops reading after one line they should still have the point.
2. **One idea per sentence.** Short declarative sentences. If a sentence has two clauses joined by
   "which" or "and therefore", it is probably two sentences.
3. **Replace jargon, do not gloss it.** Not *"a paralogue-selectivity ΔΔG (that is, a free-energy
   difference)"* — just *"whether the drug can tell two near-identical proteins apart"*. A term
   survives only if the reader genuinely needs to carry it forward.
4. **Concrete beats abstract.** Say what happened, to what, with what result. *"We ran three tests
   designed to prove the method works. All three failed."*
5. **At most one analogy, and label it as one.** Analogies are for building intuition, never for
   carrying an argument. ⛔ The moment a conclusion depends on the analogy rather than on the
   evidence, delete the analogy.
6. **Cut the apparatus.** No glyph tables, no gate names, no file paths, no accession numbers, no
   internal identifiers — unless the reader is being asked to go look at one.
7. **Numbers stay, units get explained.** *"20 samples"* is plain. *"n=20 across three cohorts"* is
   not. Keep the number; drop the notation.
8. **Keep it short.** An eli5 that is longer than what it explains has failed.

---

## ⛔ What plain language must NOT change

**Style changes. Claims do not.** This is the whole risk of the skill and it is the one thing that
would make it harmful in this repository.

- A **hedge stays a hedge.** "Might", "we think", "unvalidated" survive the rewrite. Simplifying
  *"this is an unvalidated prediction"* into *"this works"* is not simplification, it is a false
  claim.
- A **null stays a null**, and an **unknown stays an unknown**. "We don't know" is already plain
  English. It never becomes "probably".
- **Do not round away a failure.** If three controls failed, three controls failed.
- **Do not drop the ceiling.** If the honest limit is "this suggests where to look next", say that,
  in plain words: *"this tells someone where to look; it does not show the drug works."*
- **Never simplify a medical or clinical statement into a stronger one.** Same rule as everywhere
  else here: no efficacy, no safety, no readiness, ever — plain phrasing included.

---

## The three failure modes

- **Talking down.** No "imagine you're five", no "basically", no exclamation marks, no pretending
  the topic is simpler than it is. The reader is not the problem; the writing was.
- **Hollowing out.** An answer so smoothed that nothing specific survives. If the plain version
  could describe any project, it explains nothing. Keep the *specific* facts — the actual number,
  the actual thing that failed — and drop only the *notation*.
- **The runaway analogy.** The metaphor gets extended until it is doing the reasoning. One analogy,
  one sentence, then back to the real thing.

---

## Quick test before you send it

Read it as someone who has never seen this repository. Ask:

- Did I learn what the answer is in the first two lines?
- Is there a word I would have to look up?
- Could I repeat the main point to someone else?
- **Is anything now stated more confidently than the evidence supports?** If yes, that is not a
  style bug — fix it before anything else.
