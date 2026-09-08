---
id: DOC-OPUS-CAMPAIGN-INTEGRATION-DATA-SUFFICIENCY
title: "Data-sufficiency statement for the integrated endpoint ledger"
level: L4
kind: statement
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Data sufficiency — coherent statement across all three components

Scope: the 12 cached ClinicalTrials.gov payloads at revision `216bd1b5…`, the delivered leaf
evidence, and the three corrected components built over them. Nothing was re-fetched. Every
statement is about **those bytes**.

## The bottom line, first

**The integrated ledger does not support an endpoint analysis, and the endpoint manuscript stays
PARKED.** The ledger is nonetheless a correct and useful result: it says, per record and with a
checkable reason, exactly what the source can and cannot carry.

## What the integration establishes (sufficient)

1. **A stated, verified join between A and C.** `(nct, om_title, group_title)` is a bijection over
   all 552 records (check `I2`), and C's `evaluable_n` key component agrees with A's carried job-1
   value on 552/552 (`I2b`). The two components describe the same 552 records.
2. **A precise, exhaustive account of the A↔B grain mismatch.** 458 of 552 spine rows exist as B
   observations; 48 rows (21 trials) are in trials outside B's corpus; 46 rows (17 trials) are in
   measures outside job 2's response-title boundary; 0 rows are group-absent (`I3`). The 15,658 B
   observations with no A or C counterpart are emitted, not dropped (`I4`).
3. **Independent agreement on the one quantity both A and B read from source.** A's read
   participant denominator equals B's on all 458 jointly covered rows — 0 disagreements. This is
   agreement between two independent readings of the same cache, not confirmation of job 2.
4. **A machine-readable disposition for every component record**: 552 A rows, 552 C rows and
   16,116 B observations each appear exactly once in `DISPOSITION-MAP.tsv` (`I9`).
5. **A contradiction register in which no component overwrites another** (`I5`, `I6`).

## What remains insufficient — and is therefore withheld

1. **The spine itself is inherited from an unconfirmed chain.** Only job 1's *arithmetic* was ever
   independently re-derived. **job 2 and job 3 were never independently confirmed.** The 552-key
   set, the four-cell category rules behind it, and the disease and phase attributions attached to
   it come from that chain. Correcting job 3's arm logic (component C) does not confirm job 3.
2. **Disjointness cannot be established for any pair of cohorts, anywhere.** The cache carries no
   `participantFlowModule`, no baseline characteristics and no eligibility module (B check `C21`,
   C check `absent_modules_stay_absent_in_this_cache`). This condition sits on **all 552 rows**,
   including the 105 with no component-specific block. Consequently: **no unique-patient total, no
   pooled cohort, no capacity bound.**
3. **No approved rule exists for choosing among competing records.** 309 spine rows sit in a B
   cohort key holding more than one competing observation, differing on a real field — endpoint
   construct, criteria version, time frame, population, unit. Corpus-wide, 4,464 of 8,740 cohort
   keys are in this state. `selection_status` is `NOT_SELECTED_BY_DESIGN` everywhere; a preference
   would be a scientific decision the source does not license.
4. **94 spine rows were never assessed for identity, repetition or overlap at all** — they lie
   outside B's corpus or title boundary. Their silence is a coverage gap, recorded as
   `ROW_NOT_ASSESSED_BY_B`, never as agreement.
5. **61 rows are structurally unsuitable for any proportion** (A): overlapping strata, category
   sums exceeding or a multiple of the reported denominator, or producer label collisions. 60 of
   those 61 have a *confirmed* arm link in C — a confirmed arm on an uncomputable denominator is
   still uncomputable, and the ledger keeps both states.
6. **Arm attribution is unconfirmed on 49 rows** (26 `CONFIRMED_TYPE_ONLY`, 10 `CANDIDATE`,
   8 `UNKNOWN_IN_THIS_CACHE`, 5 `UNRESOLVED`), and control status is contested on 5, unknown on 25
   and candidate-only on 1. `UNKNOWN_IN_THIS_CACHE` is never read as not-control.
7. **83 rows contradict a one-arm reading of their own trial** (one registered arm, several results
   groups in the measure). The contradiction is retained; no row is forced into a one-arm model.
8. **Confirmed untreated controls are 9 rows in 6 trials** across the whole spine (8 placebo, 1
   no-intervention). 32 further rows are *active* comparators — treated, and not an untreated
   control. This is far too little, and far too entangled with the conditions above, to support any
   control comparison; none is attempted.
9. **B's inclusion boundary is job 2's response-title regex, retained deliberately** so the change
   map joins 1:1 — not because it is the right boundary. A wider response-word pattern matches
   10,570 measures against the 5,551 in scope. Widening it is a scientific decision no component
   made.
10. **1,282 B observations report a denominator of zero** and 15 carry no `reportingStatus` field.
    They are retained as source facts, marked unusable, and never read as observed zero-response
    cohorts.
11. **`NCT00756509` is internally inconsistent** (one cohort of 41 against `ACTUAL` enrollment 34).
    The cache cannot say which field is wrong; the inference stops there.

## The 105 rows with no component-specific block

105 of 552 rows carry no block from A, B or C. **This is not an eligible subset.** It is the absence
of a *found* defect in three components, on records that still carry the universal disjointness
condition (item 2), still rest on the unconfirmed job2/job3 chain (item 1), span 44 trials, and
include 11 rows whose own trial contradicts a one-arm reading. Nothing may be computed from them.

## Condition under which the paper could stop being parked

Not met, and not met by more curation. It would require, at minimum: (a) an independent confirmation
of job 2 and job 3, or a spine rebuilt from source without them; (b) source evidence of cohort
disjointness — a `participantFlowModule` or equivalent — which this cache does not contain; and
(c) a scientifically justified, pre-registered rule for choosing among competing records, which no
component is authorised to invent. Until all three exist, **the endpoint manuscript stays PARKED.**
