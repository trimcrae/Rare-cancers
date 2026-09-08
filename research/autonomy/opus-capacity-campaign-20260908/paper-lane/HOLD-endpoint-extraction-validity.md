---
id: DOC-OPUS-CAMPAIGN-HOLD-ENDPOINT
title: "Paper-specific hold — response endpoint in indolent tumours"
level: L4
kind: memo
status: live
purpose: >
  Record the adverse outcome of the completed independent final review of the response-endpoint
  manuscript, the findings root accepts as requiring major scientific revision, and the exact
  condition under which the paper may reopen.
scope: >
  L4. A hold and its evidence. It repairs nothing, proposes no replacement number, authorises no
  publication act, and asserts no green gate.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# ⛔ HOLD — `research/manuscripts/endpoint/response-endpoint-indolent-tumours.md`

**The independent final review is COMPLETE, and its outcome is ADVERSE.** Root accepts it:
**MAJOR SCIENTIFIC REVISION IS REQUIRED** before this paper can be a publication candidate.

This supersedes the promotion lane's earlier "ALREADY COHERENT — freeze, zero edits" disposition and
supersedes the PRELIMINARY-findings section of
[`FROZEN-HANDOFF-endpoint-response.md`](FROZEN-HANDOFF-endpoint-response.md), which recorded two of
these findings while the review was still running. The handoff's revision identity, package identity
and check table remain accurate as written and are not restated here.

- **Held revision:** `9c6f4a80fc2fd69ee71ad6124c8de03e6e1af395`, branch `claude/confident-bardeen-ji76cd`.
- **Frozen evidence:** all **21** package inputs and the manuscript stay frozen exactly as reviewed.
  They are the evidence the review read; they are not to be edited, substituted, regenerated or
  deleted while this hold stands.

## Core findings — the reason for the hold (F1–F3)

These three are what make the revision major. They are not wording problems.

**F1 · `evaluable_n` is a derived sum, not a reported denominator.** The producer computes
`evaluable_n` as the **sum of the outcome cells**. The manuscript describes it as the denominator the
trial **reported**. Those are two different quantities, and every rate the paper computes on
`evaluable_n` inherits the difference. Nothing here establishes what the reported denominators are;
this finding says the manuscript's stated definition is not the one the code implements.

**F2 · Extraction can overwrite category values across source classes.** The extraction path permits
a value drawn from one source class to overwrite the value held for another, so a stored category
value does not reliably identify which class it came from. This is a defect in how the cache was
built, not a presentation choice.

**F3 · The 552 records are not 552 independent units.** The record set includes **repeated arms**,
**ITT and per-protocol measures of the same arm**, and **confirmed and unconfirmed measures of the
same arm**. Beyond that, whole-trial attributes are assigned to each record: the trial-level
**condition** and **phase** are stamped onto every record from that trial, so, for example, the
**23 cervical records are all one mixed phase I/II trial**, not 23 cervical units at a single phase.

⚠ **465 distinct NCT/title strings is diagnostic only.** It tells you the record set is not 552
distinct trials. It is **not** a corrected unique-arm count and must never be used as one, in this
paper or downstream.

⛔ **Do NOT invent percentage-row contamination.** Root checked the frozen rows and **every one has
unit `Participants`**. There is no actual percentage-row contamination to report, and asserting one
would be a fabricated finding.

## Reopening condition

The paper reopens on **one** of two routes, and on nothing else:

1. **Validated original evidence.** Original, validated **group / class / reported-denominator /
   assessment / arm-disease / phase** evidence, carrying a **reviewed selection rule**, with the
   paper's outputs **recomputed** on it and coherent with the recomputed inputs; or
2. **A different manuscript.** A **root-adjudicated descriptive EXTRACTION-RECORD manuscript** that
   **withdraws** the unverified claims and reports only what the cache can support as a record of
   extraction.

⛔ **Wording alone cannot make the cache satisfy its original methods.** Re-describing
`evaluable_n`, relabelling the records, or hedging the rates does not close F1–F3 and does not
satisfy either route.

⛔ **No blind full producer chain re-run and no source reconstruction.** Regenerating the artifacts
would replace the reviewed evidence without answering the findings.

⛔ The sole collector's one authorised existing-cache lookup is **already done**. Do **not** duplicate
it and do **not** fetch ClinicalTrials.gov.

## Accepted and retained for later authorised repair (F4–F10)

These are accepted as real. They are **not** repaired here — F1–F3 govern, and repairing presentation
on top of an unvalidated extraction would be work done twice.

- **F4** · 31.8–73.9 is a range across the observed values; it is **not** population bounds.
- **F5** · Zero responses is informative but **imprecise**, and it is **not** an agent-independent
  cause.
- **F6** · The figure **clamps 77.8 and 80 to 60**, and its gray **mislabels the 16 undefined**.
- **F7** · **PMID 25317882** is a **Letter/Comment**, not a trial.
- **F8** · 4/25 controls is **not** a natural-history confound magnitude.
- **F9** · The interval is **Wilson SCORE**, not exact.
- **F10** · The linked EMC JSON narrative must be brought into agreement with **§8**.

## Packaging correction — eventual, and the old range is wrong

Packaging is a deposit-time step and is **eventual**: it does not happen under this hold.

⛔ **The earlier "lines 44–56" range in the frozen handoff is WRONG and must not be used to strip
anything.** Measured on the held revision: the **actual HTML editorial comment is lines 38–51**.
**Lines 53–56 are REAL ethics / funding / data declarations** and are part of the paper. Stripping
the old 44–56 range would delete four lines of genuine declarations along with the editorial block.

## No data-loss claim

The four producer files, the four inputs and the protocol referred to in review discussion **already
exist at `9c`** (`9c6f4a80fc2fd69ee71ad6124c8de03e6e1af395`). There is **no** data-loss finding here,
and none should be inferred from this hold.

## What this hold is not

⛔ It is not a retraction, not a publication act, and not a claim that any gate is green or red beyond
the checks the frozen handoff already recorded with their exit codes. It asserts no EMC efficacy,
safety, selectivity or clinical readiness. It binds **this paper only**: other papers continue on
their own scopes, and no programme-wide pause follows from it.
