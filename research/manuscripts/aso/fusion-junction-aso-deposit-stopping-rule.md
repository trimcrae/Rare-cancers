---
id: DOC-FUSION-JUNCTION-ASO-STOPPING-RULE
title: "The pre-registered stopping rule for the fusion-junction ASO deposit — written before the final round, so the result cannot be rationalised into it"
level: L3
kind: manuscript
status: live
canonical_for:
  - the termination condition for adversarial review of the fusion-junction ASO submission
purpose: >
  Fix, IN ADVANCE, the condition under which review of fusion-junction-aso-research-article.md stops
  and the preprint is deposited. It exists because the alternative — deciding after the fact whether
  a round's findings were "serious enough" to warrant another — has no stopping point, and seven
  rounds have demonstrated that this method finds something every time.
scope: >
  The termination condition for adversarial review of the three fusion-junction ASO submission
  documents — the research article, its supplementary information and the generated submission
  tables — for a bioRxiv deposit specifically. ⛔ It governs WHEN REVIEW STOPS and nothing else: it
  is not a quality claim about the manuscript, not a checklist of deposit steps (that is
  fusion-junction-aso-preprint-checklist.md), and it says nothing about any other paper in the
  portfolio. Its five conditions and its one headline-falsifying exception are binding; everything
  else here is the reasoning that produced them.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-08-16
last_verified: unverified
---
# The stopping rule, pre-registered

> ⛔ **WRITTEN AND COMMITTED BEFORE THE FINAL ROUND RUNS.** That ordering is the whole point. A
> stopping rule written after the results are known is not a stopping rule, it is a justification.

## 1 · Why a rule is needed at all

Seven adversarial rounds have run on this manuscript. Round 7 pre-registered the prediction that no
coverage gap remained in text six prior rounds and eighteen reviewers had walked past, and **that
prediction was falsified** — B5-F1 found one, in text no prior round had touched.

The honest reading of that is **not** "run round 8". It is that this method has a floor above zero:
the same model family, reviewing the same document, with the same blind spots, will keep returning
findings for as long as it is asked to, and the marginal finding gets smaller while the marginal cost
does not. "No problems left" is not a reachable state and is not the target.

What *is* reachable is a **defined done-state**: every known finding dispositioned, the recurring
defect classes converted into gates that make them structurally impossible, and the stopping
condition fixed in advance.

## 2 · The rule

### ⭐ CONDITION 6 — TWO READERS, AND ONLY THE OVERLAP COUNTS (added 2026-08-19, trimcrae)

#### Round 12 — the first round run under this condition, and what it filtered

Two readers, same build, different briefs (one a bioRxiv screener working a scope list, one a
copy-editor reading for sense), neither seeing the other. Between them they raised **two majors and
five distinct minors. Exactly one minor was raised by both.**

| finding | reader A | reader B | action |
|---|---|---|---|
| "clean" carries four senses in §2.6 | MAJOR | — | FIXED — a major stands on one reader |
| Methods says the longer geometries went through "the same screens" | — | MAJOR | FIXED — a major stands on one reader |
| "Two of those three sources" followed by a three-item list | MINOR | MINOR | **FIXED — the overlap** |
| Figure 2 not standalone-readable without §2.2's correction | MINOR | — | FIXED |
| "shown to be sufficient and not to be necessary" | — | MINOR | FIXED |
| Declarations enumeration misses the five non-panel designs | — | MINOR | FIXED |

⚠ **ALL THREE SINGLE-READER MINORS WERE SUBSEQUENTLY FIXED**, under the corrected reading of this
condition. They are listed as "held" above only because that was their status for the hour between
the round landing and the correction. Nothing from round 12 is unrepaired.

★ **THE FILTER DID WHAT IT WAS ADDED TO DO.** Under the old rule all five minors would have been
fixed, and on the measured rate of this loop roughly one of those five repairs would have seeded the
next round's finding. ⛔ And the one that survived was itself a repair: the "two of those three
sources" sentence was written in round 11 to fix a DIFFERENT antecedent defect in the same sentence,
and both readers independently found the replacement worse than what it replaced. That is the
clearest evidence in this ledger for why single-reader minors are not worth chasing — and for why
the overlap is worth fixing.


**Every minor raised is fixed. The two-reader test is the STOPPING condition, not a filter on what
gets repaired:** the loop ends when a two-reader round returns no minor that BOTH readers raise.
A minor only one reader sees is still fixed; it simply does not, on its own, keep the loop open.

⚠ *Superseded, retained: this condition was first written as "a minor one reader raises and the
other does not is recorded and NOT fixed" — a filter on repairs. trimcrae corrected it the same
day: "You should still try to fix every minor that is raised. Just don't let a minor that isn't
shared by both agents block you." The distinction matters — under the first reading three real
observations would have been left in the deposit because only one reader happened to see each.*

⛔ **WHY, AND IT IS MEASURED RATHER THAN ARGUED.** Across nine screened rounds of both built formats:

| round | blockers | majors | minors |
|---|---|---|---|
| 3 | 1 | 3 | 8 |
| 4 | 0 | 0 | 11 |
| 5 | 0 | 1 | 8 |
| 6 | 2 | 1 | 5 |
| 7 | 0 | 0 | 7 |
| 8 | 0 | 0 | 5 |
| 9 | 0 | 2 | 6 |
| 10 | 0 | 0 | 5 |
| 11 | 0 | 0 | 4 |

Blockers and majors CONVERGED — zero of both in six of the last seven format-rounds. **Minors did
not.** They oscillate between 4 and 7 with no trend that survives the noise, and the mechanism is
visible in the ledger: **roughly one finding per round was created by the previous round's fix**
(round 6's blocker, round 7's fragment, round 8's all-caps emphasis, round 9's precedent major,
round 11's "the two reagents"). The screener finds ~4, the repair introduces ~1, and the count sits
at a fixed point. That is a sampling rate, not a defect count.

★ **THIS IS WHAT §1 ALREADY PREDICTED**, and the prediction is now quantified rather than asserted:
"the same model family, reviewing the same document, with the same blind spots, will keep returning
findings for as long as it is asked to." Chasing single-reader minors is an indefinite loop whose
marginal finding was, by the end, a gene abbreviation left unexpanded and a source set not announced
as three.

⚠ **THE CRITERION WAS FIXED BEFORE THE ROUND THAT TESTS IT.** Written while round 12's two readers
were still reading and their findings were unknown — a stopping rule chosen after seeing the data is
not a stopping rule. Both readers get the same build and neither sees the other.

⚠ **THIS RELAXES NOTHING ABOVE MINOR.** A blocker or a major from EITHER reader is actionable on its
own; the two-reader test applies to minors only, which is exactly the class that stopped converging.


**Deposit when all six hold.** ⚠ *Superseded, retained: "all five", and before it "all four" — condition 6 was added 2026-08-19 after the minor count was measured across nine rounds and found not to converge; condition 5 was added 2026-08-17 after conditions 1-4 all held and an outside screen of the built PDF found a wrong-reagent hazard none of them could see.*

1. **Every P0 and P1 item has a recorded disposition** — applied, declined with a stated reason, or
   refuted with evidence. **Zero OPEN.** A deferred item is only permissible where its trigger is
   named and outside this repository's control (see §4).
2. **Every gate is green**, including `PREFLIGHT_FULL=1` and all four generated-artifact `--check`
   modes (`submission_tables.py`, `submission_citations.py`, `submission_metrics.py`,
   `aso_archive_manifest.py`).
3. **One firewalled cold reader** — given the three documents and nothing else, no history, no diff,
   no plan — **returns nothing above `minor`.**
4. **One adversarial reviewer with artifact access**, explicitly permitted to report that it found
   nothing, returns findings that are all either refuted or already in the ledger.
5. **⭐ ONE BLIND SCREEN OF THE BUILT PDF** — the artifact a depositor actually uploads — returns
   nothing above `minor`. **Added 2026-08-17, and it was earned the expensive way.** Conditions 1–4
   were all met, this rule declared the paper deposit-ready, and an outside screen of the PDF then
   found a **wrong-reagent hazard**: table sequences printed with no `5′-`/`-3′` delimiters against a
   numeric cell, so one extractor returned a 16-mer carrying a trailing digit. Nothing in conditions
   1–4 could have seen it, because **every seat read the Markdown** and the defect is created by
   typesetting.
   ⛔ **The lesson is not "add a reader", it is that VERIFYING A SOURCE AND INFERRING THE DELIVERABLE
   IS FINE is the inference this repository forbids everywhere else.** A PDF is derived, and a
   derivation can change what a sequence *is*.
   ⚠ The screen must cover, at minimum: the text layer as a reader copy-pastes it; display-item
   numbering against citation order; what the front matter looks like to a screener skimming it; and
   whether anything a laboratory would order from survives extraction intact. The standing instrument
   is `tests/test_pdf_text_layer_is_orderable.py`, which asserts the document's property rather than
   one extractor's behaviour — ⛔ because the fusion is **extractor-dependent**, and a guard written
   against the tool that happened to be at hand would have gone green on a corrupting document.
   ⛔⛔ **BOTH BUILT FORMATS, SCREENED SEPARATELY, AND THE SCREEN RE-RUN AFTER EVERY FIX ROUND**
   (added 2026-08-17, second revision). Two things were learned the same way the condition itself
   was. **First, one format is not the other document.** The build emits a journal typesetting and a
   submission-format manuscript from the same sources; page geometry differs, so float placement,
   page breaks and what a caption sits beside all differ. A round that screened only one returned six
   minors the other did not have, and a later round's blocker — a caption misstating the architecture
   of a named oligonucleotide — was visible in the manuscript format and not the journal one.
   **Second, a fix round is a new document and needs its own screen.** The blocker just described
   was CREATED by the previous round's remedy for a different finding: a chemistry clause written
   for the all-5-6-5 tables, pasted onto two tables whose subject is that the geometry varies. A
   screen that ran before the fixes cannot see the fixes' own defects, and "we already screened it"
   is the inference that let it through.

### Why those seats specifically

- **The cold reader was the highest-yield seat in round 7.** It found that `gap-level margin` — the
  statistic the entire ranking rests on — is first used at character 9,605 and defined at 92,817, and
  that "EMC" is never defined at all. Every reviewer carrying memory of the older draft read straight
  past both. A reader with no context is the only instrument that can see this class.
- **The permission to find nothing is load-bearing.** It produced a real result twice. Without it the
  seat manufactures an objection, because a reviewer asked for findings supplies findings.

## 3 · ⚠ The corollary, which must not be flinched from

**If the final round returns a class-B finding — a real defect in text no prior round touched — that
is NOT a reason to run another round.**

It is evidence that this method has a floor above zero, which is already known. The correct response
is: record the finding, fix it, and **deposit anyway.**

A preprint is revisable. That is what preprints are for, and it is the reason the author chose a
preprint over journal submission. Treating a bioRxiv deposit as though it were irreversible imports
exactly the cost model the venue exists to avoid.

⛔ **The one exception, stated so it cannot be stretched:** a finding that would make the paper's
*headline* false — 87 of 190, 61 against wild-type *NR4A3*, or the claim that a longer catalytic gap
cannot separate them — stops the deposit regardless of what this rule says. Nothing else does.
Round 7's B5-F1 is the worked example of the boundary: it invalidated an *apportionment label* and
left the headline untouched, so it was a fix, not a stop.

## 4 · What will still be open at deposit, and is stated rather than hidden

- **No reviewer in seven rounds has been a wet-lab scientist who has run one of these experiments.**
  Every bench perspective is simulated. This is the largest gap in the review history and **no amount
  of further simulated review closes it.**
- **Same method, same model family, same blind spots.** A quiet round is weak evidence that the paper
  is good and strong evidence only about what this method can see.
- **Four venue-triggered P3 items stay deferred** by the author's decision to target bioRxiv, which
  has no length cap and no IMRaD template. Each names the trigger that reopens it.
- **Anything the CI fetches could not reach** is marked UNVERIFIED. Never guessed.

## 5 · The three things only the author can supply

These are not review findings and no round can close them.

1. An **ORCID** — the manuscript carries `ORCID: [to be inserted]`.
2. A **reserved archive DOI**. The checklist requires reserving it *before* publishing the deposit, so
   the manuscript cites the DOI it will have. Two `[ARCHIVE DOI]` placeholders await it.
3. **The go-ahead to post.** Outward-facing and irreversible, and therefore a human's call.
