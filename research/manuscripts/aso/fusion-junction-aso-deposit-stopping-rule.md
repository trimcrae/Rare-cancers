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

**Deposit when all five hold.** ⚠ *Superseded, retained: "all four" — condition 5 was added 2026-08-17 after conditions 1-4 all held and an outside screen of the built PDF found a wrong-reagent hazard none of them could see.*

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
