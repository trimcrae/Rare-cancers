---
name: scientific-writing
description: Write and revise this repository's submission texts so a working scientist can read them once and follow them. Load BEFORE drafting or revising any manuscript, SI, cover letter or abstract that will go to a preprint server, a journal or aiXiv, and before applying a hardening round's findings to prose. Covers the four moves that carry almost all the gain (topic and stress positions, characters as subjects, actions as verbs, one sentence one idea), the revision pass that finds the damage, and the two failure modes that make a "clearer" paper worse — a hedge quietly dropped to shorten a sentence, and a readability score chased as a target. Metrics are a SCREEN that says where to look, never a measure of whether the prose is good; `lint_readability.py` reports, this file decides.
---

# Writing a paper somebody can actually read

⚠ **WHY THIS EXISTS, WITH THE MEASUREMENT THAT PROMPTED IT.** trimcrae, 2026-08-27, on the ASO
preprint's v1 (doi 10.32388/VL3LJR): *"A big issue with the preprint v1 is readability. It's written
in a very difficult to understand style, which is characteristic of Opus 5."* Measured on the
published text: **mean sentence 28.8 words, 22 % of sentences over 40 words, a 101-word sentence in
the methods, Flesch–Kincaid grade 15.3.** The same repository's MTAP hypothesis runs **23.2 words and
grade 13.0**, so the subject matter is not what forced it. ⛔ **The science was not the problem and
neither was the honesty — the prose was.**

⛔⛔ **THE ONE RULE EVERYTHING HERE IS SUBORDINATE TO: PLAIN NEVER MEANS WEAKER.** A hedge, a null,
an UNKNOWN, a negative, a limitation and a number keep exactly the strength they had. This is
CLAUDE.md §1's eli5 rule, and it binds harder in a manuscript than in a chat reply, because a
manuscript is the thing an outside reader acts on. **A sentence that got shorter by losing a
qualification has not been improved; it has been falsified.** Every technique below is a way to move
words around, not a licence to drop them — and §4 is the check that you did not.

---

## 1 · The four moves, in the order that pays

Almost all the gain is in four moves. They come from the two works that established them for science
prose — Gopen & Swan's reader-expectation analysis (*American Scientist* 78:550, 1990) and Williams's
*Style* — and they are mechanical enough to apply without taste.

### 1.1 · ★★ Put old information first and new information last

A reader arrives at a sentence holding what the last sentence gave them. Start there, and end on the
thing you want them to carry forward. Gopen & Swan call these the **topic position** and the **stress
position**, and violating them is the single most common reason a technically correct sentence reads
as hard.

> ⛔ *Selectivity is the wild-type NR4A3 half-maximal knockdown concentration divided by the fusion's,
> from a matched dose-response in the same wells, at a cut of 5.0 adopted as a convention — a
> comparison of the two half-maximal concentrations is the margin assessment the recommendations
> specify at this stage.* (101 words, and the point lands in the middle)

> ✅ *Selectivity is the ratio of two half-maximal knockdown concentrations: wild-type NR4A3 over the
> fusion, measured in the same wells. We adopt a cut of 5.0. That ratio is the margin assessment the
> field's recommendations specify at this stage — it is a convention, not a measurement.*

Same claims, same hedge ("a convention, not a measurement"), same number. Three sentences, each
ending on what matters.

### 1.2 · ★ Make the subject the thing the sentence is about

If the sentence is about a gapmer, the gapmer should be its grammatical subject. When the subject is
an abstraction and the real actor is buried in a prepositional phrase, the reader does the assembly.

> ⛔ *Assessment of the parent-pairing liability was performed across the panel.*
> ✅ *We assessed every design in the panel for parent pairing.* — or, if the agent is irrelevant:
> ✅ *Every design in the panel carries a parent-pairing liability.*

⚠ **Passive voice is not the enemy and a blanket ban is wrong.** Passive is correct when the actor is
genuinely unimportant or unknown (*the samples were sequenced*). The defect is a **missing character**,
not a passive verb.

### 1.3 · ★ Put the action in the verb

Nominalisation — an action frozen into a noun — is what makes methods sections feel like treacle.
Find the action; make it the verb.

| ⛔ nominalised | ✅ verb |
|---|---|
| performed an evaluation of | evaluated |
| provides confirmation that | confirms |
| is in agreement with | agrees with |
| conducted a comparison between | compared |
| the determination of selectivity was made | we determined selectivity |

### 1.4 · ★★ One sentence, one idea

The 101-word sentence above is not one idea. Long sentences in this repository are almost never long
because the thought is complex; they are long because **three thoughts were joined with dashes and
semicolons rather than full stops**. Splitting costs nothing and drops no content.
⚠ **This is the move most likely to be done badly.** Splitting is safe; *deleting a clause to hit a
length* is the §4 failure. If a sentence will not split, it is usually because a subordinate clause
carries a qualification — **keep the qualification and give it its own sentence.**

---

## 2 · Above the sentence: say what the section is for

Sentence-level work cannot rescue a paragraph the reader cannot place. Schimel's *Writing Science*
frames a paper as **opening → challenge → action → resolution**, and the same shape works per section
and per paragraph.

- **Lead each paragraph with its point.** A paragraph whose first sentence is context and whose last
  sentence is the finding makes the reader hold everything in the middle. Put the finding first, then
  support it.
- **One paragraph, one claim.** If you cannot write the paragraph's claim in the margin in six words,
  it is two paragraphs.
- **Name the thing the same way every time.** Synonym variation is a literary virtue and a scientific
  defect: *the gapmer*, *the reagent*, *the oligo* and *the construct* read as four objects. Pick one
  and repeat it. ⚠ This repository already enforces the identifier half of this
  (`test_the_manuscripts_gene_identifiers_are_ones_an_artifact_names.py`); the prose half is yours.

---

## 3 · The revision pass — what to actually do

⛔ **Do not revise while drafting.** Draft, then run this pass. It is mechanical and it is fast.

1. **Screen, don't judge.** `python3 research/manuscripts/lint_readability.py --report <file>` prints
   the sentence-length distribution and the worst offenders **with their line numbers**. That list is
   *where to look*, nothing more (§5).
2. **Take the longest ten sentences and split them.** This alone moves the mean further than any
   other single action.
3. **Read the first sentence of every paragraph, in order, and nothing else.** If that sequence does
   not tell the paper's story, the problem is structure, not wording (§2).
4. **Grep your own nominalisations** — `\b(?:performance|evaluation|determination|assessment|
   utilisation|implementation)\s+of\b` — and convert each to its verb (§1.3).
5. **Re-run the screen and the content gates together.** Readability without `lint_claims`,
   `lint_citations` and the pinned-figure guards green is meaningless: the fastest way to a beautiful
   score is to delete the difficult truth.

---

## 4 · ⛔⛔ The check that readability did not cost you honesty

**This is the section that matters most, and it is the one a rewrite pass will be tempted to skip.**

A revision that improves readability *by removing caution* is the worst outcome available here —
worse than the dense original, because it is now both readable and overstated, and it is going out
under a DOI. The failure does not announce itself: every individual edit looks like tightening.

**Before and after any readability pass on a submission text, count the caution.** Hedges (*may*,
*could*, *appears*), explicit nulls (*no difference*, *not established*, *unverified*), UNKNOWNs,
limitation sentences, and every number with its interval. ⛔ **If the count fell, name which
qualification left and why.** `lint_readability.py --caution <file>` prints the count and the
markers it found, so this is a measurement rather than a memory.

⚠ **The specific sentences to guard hardest** are the ones this repository has already paid to get
right: the strongest null, the delivery gate, *nothing here has been synthesised or tested*, and any
sentence whose whole job is to stop a reader over-reading a result. **Those are allowed to be the
longest sentences in the paper.** A limitation that survives only as a subordinate clause in a
32-word sentence is worth more than a crisp 12-word sentence that lost it.

---

## 5 · ⛔ The metric is a screen, and it must never become the target

trimcrae, 2026-08-27: *"Good prose is going to come from better writing style rather than metrics.
Though the metrics could be a decent screening layer."* That is the whole relationship, and this
section exists so a later cycle cannot quietly invert it.

- **What a score can do:** point at the ten sentences most likely to be unreadable. That is genuinely
  useful and it is cheap.
- **What a score cannot do:** tell you whether the prose is good. Flesch–Kincaid counts syllables and
  words per sentence. It cannot see a missing character, a buried stress position, a paragraph that
  leads with context, or an argument that does not follow. **A paper can hit any target and still be
  unreadable**, and a technical paper's unavoidable vocabulary — *oligonucleotide*,
  *extraskeletal myxoid chondrosarcoma* — drags every syllable-based score down without costing a
  reader anything.
- ⛔ **So the gate reports, and the gate never fails a paper for a score alone.** Goodhart's law is
  not a theoretical concern here: this loop optimises what it is measured on, and a readability
  threshold as a hard gate is an instruction to write shorter sentences by any means available —
  including §4's.

★ **The honest shape, and the one implemented:** the screen is **advisory on the number** and **hard
on the two things that are unambiguous** — a sentence over the ceiling is always worth splitting, and
a *fall* in caution markers is always worth explaining. Neither of those can be satisfied by making
the paper say less.

---

## 6 · Where the rest lives

- **Mechanical tics, journal register, the glyph and bold discipline:** `lint_style.py` and its
  TARGETS list, which is the one home of "is this a submission text". This file does not restate it.
- **Plain language for trimcrae specifically, in replies and nowhere else:** `eli5`.
- **Applying a review round's findings without inflating the paper:** `paper-hardening` §1 —
  a correction REPLACES text, it does not append. That rule and §1.4 here are the same rule seen from
  two sides.
- **Gates, preflight tiers and anything outward-facing:** `repo-gates`.
