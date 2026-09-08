---
id: DOC-OPUS-CAMPAIGN-CORRECTED-B-DATA-SUFFICIENCY
title: "Data-sufficiency statement for corrected contract B (identity / selection / overlap)"
level: L4
kind: statement
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Data sufficiency — what the delivered cache can and cannot support

Scope: the 12 cached ClinicalTrials.gov payloads at revision `216bd1b5…` and the delivered leaf
evidence. Nothing was re-fetched. Every statement below is about **those bytes**, not about the
registry.

## Sufficient

1. **Study identity.** `nctId` is a stable key; 6,081 distinct trials, 4,235 with a results section.
   329 trials appear in more than one payload; a canonical copy per trial is chosen deterministically
   and every copy's payload name is retained on the row.
2. **Observation identity.** `(nctId, outcome-measure index, results-group id)` uniquely and
   completely keys all 16,116 response observations (check `C2`).
3. **Separation of the competing quantities.** Endpoint construct, criteria and version, time frame,
   population description, parameter type, unit, result group and class/category identity are all
   present per observation and are kept apart.
4. **Repeated assessment structure.** 4,464 cohort keys carry more than one competing observation
   (max 17), each with machine-readable unresolved states.
5. **Within-measure denominator arithmetic** against `enrollmentInfo.count`, recomputed from the
   ledger with zero mismatches (check `C13`).
6. **Pooled-parent / component and results-group-id-reuse relationships** (63 pooled cohort keys;
   3,813 id-reuse pairs).

## Insufficient — and therefore withheld

1. **Disjointness of any two cohorts cannot be established.** The cache carries **no
   `participantFlowModule`**, no baseline characteristics and no eligibility module (check `C21`).
   No claim that two cohorts are distinct patient sets is made anywhere, and none could be.
2. **Unique patients cannot be counted at any level**, so no unique-patient total is emitted. A sum
   of denominators is a sum of participant-slots with known internal double counting.
3. **"Independent arm" is not recoverable.** Results-group ids are scoped to one outcome measure
   (3,813 reuse pairs), most results-group titles do not match a registered arm label, and arm
   attribution is a **sibling owner's** component, not decided here.
4. **The choice among competing records is not decidable from the source in 4,464 cohort keys.**
   Each set differs on a real field — construct, time point, criteria, population, unit — so a
   preference would be a scientific decision the source does not license. It stays unresolved.
5. **1,282 observations report a denominator of zero** (287 trials; 364 cohort keys have no non-zero
   observation). Those cohorts cannot yield a response proportion at all. They are neither dropped
   nor read as zero-response cohorts.
6. **15 observations in 10 trials carry no `reportingStatus` field.** Whether those results are
   posted cannot be determined from the cache; they are retained and marked unusable.
7. **639 observations carry an explicit non-collection or termination statement.** Whether data exist
   elsewhere cannot be determined from the cache.
8. **`NCT00756509` is internally inconsistent** — one cohort of 41 against `ACTUAL` enrollment 34.
   The cache cannot resolve which field is wrong. The inference stops.
9. **The two accrual payloads are truncated** (1,000 of 16,035 and 1,000 of 2,027 by the API page
   size). They contribute field-set-only duplicate copies here; no accrual-family statement is made.
10. **The inclusion boundary is job2's response-title regex.** Retained deliberately so the change
    map joins 1:1 — not because it is the right boundary. A wider response-word pattern matches
    10,570 measures against the 5,551 in scope, so the boundary is a **choice, and a live limitation**.
    Widening it is a scientific decision this contract does not make.
11. **job2 and job3 were never independently confirmed.** No quantity carried from them is verified.

## Consequence for the parked manuscript

None of the above authorises a response rate, a pooled cohort, a capacity bound or a comparison, and
none of it unparks the endpoint manuscript. The useful product is the **source-bound long-form
evidence ledger** — defensible even where no scientific selection is currently defensible.
