---
id: DOC-OPUS-CAMPAIGN-INTEGRATION2-DATA-SUFFICIENCY
title: "Data-sufficiency statement — INTEGRATION2 over the corrected v2 components"
level: L4
kind: statement
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Data sufficiency — one coherent statement across A2, B2 and C2

Scope: the 12 cached ClinicalTrials.gov payloads at revision `216bd1b5…`, the delivered leaf
evidence, and the three corrected v2 components built over them. Nothing was re-fetched, re-run or
re-harmonised. Every statement is about **those bytes**.

## The bottom line, first

**The integrated ledger is complete, and the endpoint analysis is not supportable. The endpoint
manuscript stays PARKED.** A complete curation ledger is **not** scientific eligibility. The ledger
is still a useful result: it says, per record and with a checkable reason, exactly what the source
can and cannot carry — and after the v2 repairs it says so with **less** confidence than v1 did,
not more.

## What INTEGRATION2 establishes (sufficient)

1. **A stated, verified join.** `(nct, om_title, group_title)` is a bijection between A2 and C2
   over all 552 records (`J2`), and C2's `evaluable_n` key component equals A2's carried job-1
   value on 552/552 (`J2b`). It is a *string* bridge and is recorded as a hazard: any repeated
   title triple would break it, and the check fails rather than silently picking one.
2. **An exhaustive account of the A↔B grain mismatch**, recomputed independently (`J3`): 458
   joined, 48 rows in 21 trials outside B's corpus, 46 rows in 17 trials outside job 2's
   response-title boundary, 0 group-absent. The 15,658 B observations with no A or C counterpart
   are emitted, not dropped (`J4`).
3. **A machine-readable disposition for every component record** — 552 A2, 552 C2, 16,116 B
   observations and the 94 spine rows B never assessed, each exactly once (`J9`).
4. **Two registers in which no component overwrites another** (`J5`, `J6`), with "contradiction"
   reserved for genuinely incompatible claims (`J14`, `J14b`).
5. **Independent agreement on the one quantity both A2 and B read from source**: the participant
   denominator matches on all 458 jointly covered rows, 0 disagreements. Agreement between two
   readings of the same cache — **not** confirmation of job 2.

## What remains insufficient — and is therefore withheld

1. **The spine rests on an unconfirmed chain.** Only job 1's *arithmetic* was ever independently
   re-derived. **job 2 and job 3 were never independently confirmed.** Correcting A, B and C does
   not confirm them.
2. **Cross-observation disjointness cannot be established for any pair of cohorts, anywhere.** The
   cache carries no `participantFlowModule`. This condition sits on all 552 rows. Consequently:
   **no unique-patient total, no pooled cohort, no capacity bound.** It is a bar on *pooling and
   unique-patient counting*, and it is **not** a proof that every within-record proportion is
   mathematically uncomputable — a distinction v1 merged and this ledger keeps apart
   (`SEMANTIC-LIMITATIONS.md` §5). ⛔ No proportion is authorised here regardless.
3. **Semantic correspondence among competing records is unresolved everywhere it arises**: all
   **4,464** competing cohort keys, **zero** semantically resolved; 1,744 of them separated only by
   free-text-derived fields. 309 spine rows sit in such a set. There is no approved rule for
   choosing among competing records, and `selection_status` is `NOT_SELECTED_BY_DESIGN` corpus-wide.
4. **Arm attribution is source-confirmed on 58 of 552 rows; 494 (89.5 %) are not.** 333 rows carry
   a conditional registry-type statement whose membership assumption is unproved, and 132 rest on
   label correspondence alone.
5. **Comparator role is source-supported on 8 rows.** `NOT_CONTROL` does not exist as a state:
   166 rows are `NOT_ESTABLISHED_IN_THIS_CACHE` and 355 `UNKNOWN_IN_THIS_CACHE`. This is far too
   little, and far too entangled with the conditions above, to support any control comparison;
   none is attempted.
6. **61 rows are structurally unsuitable for any proportion** (A2): overlapping strata, category
   sums exceeding or a multiple of the reported denominator, or producer label collisions. 5 of
   them also carry a source-confirmed arm link — a constraint, not a contradiction, and still
   uncomputable.
7. **94 spine rows were never assessed for identity, repetition or overlap at all.** Their silence
   is a coverage gap, never agreement.
8. **83 rows contradict a one-arm reading of their own trial**, and 8 contested-flag entries record
   incompatible source statements about the same arm or comparator. Retained, unresolved; no field
   is declared wrong.
9. **B's inclusion boundary is job 2's response-title regex, retained deliberately** so the change
   map joins 1:1 — not because it is the right boundary. A wider response-word probe matches 10,570
   measures against the 5,551 in scope. Widening it is a scientific decision no component made.
10. **1,282 B observations report a denominator of zero, 15 carry no `reportingStatus` field, and
    639 carry a verbatim non-collection or termination statement.** These are three separate
    metadata states, never collapsed into one another or into a missing value, and never read as
    observed zero-response cohorts.
11. **`NCT00756509` is internally inconsistent** (one cohort of 41 against `ACTUAL` enrollment 34).
    Its measure holds exactly one group, so its within-measure "sum" *is* that cohort. The cache
    cannot say which field is wrong; the inference stops there.

## The 2 rows with no component-specific block

`NCT02394795|OM4|OG001` and `NCT02472964|OM0|OG000` carry no block from A2, B2 or C2 — down from
105 in v1, because C2's arm-attribution repair blocks every row whose link is not
`SOURCE_CONFIRMED`. **This is not an eligible subset.** It is the absence of a *found* defect in
three components, on two records that still carry the universal cross-observation disjointness
condition and still rest on the unconfirmed job2/job3 chain. Nothing may be computed from them, and
no eligibility subset is constructed or emitted anywhere (`J18`).

## The exact unresolved condition, and what follows from it

Three source distinctions remain unresolved, and each is a scientific blocker, not a tooling gap:

* **(a)** job 2 and job 3 are unconfirmed, so the 552-key spine, its category rules and its disease
  and phase attributions are inherited rather than established;
* **(b)** the cache contains no evidence of cohort disjointness, so records cannot be pooled or
  counted as unique patients;
* **(c)** semantic correspondence among competing records is not established by the source, and no
  pre-registered selection rule exists that any component is authorised to invent.

**Because (a), (b) and (c) are unresolved, the endpoint paper stays PARKED.** A repaired ledger
does not satisfy the earlier paper's clinical or causal claims, does not answer the HOLD's findings
F1–F10, and **does not authorise any new endpoint selection**. The reopening condition remains the
one the HOLD states — validated original evidence with a reviewed selection rule and recomputed
outputs, or a root-adjudicated descriptive extraction-record manuscript that withdraws the
unverified claims — and neither route is met by more curation.
