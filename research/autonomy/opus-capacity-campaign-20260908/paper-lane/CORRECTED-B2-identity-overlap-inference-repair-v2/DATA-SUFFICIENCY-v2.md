---
id: DOC-OPUS-CAMPAIGN-CORRECTED-B2-DATA-SUFFICIENCY-V2
title: "Data-sufficiency statement v2 — identity / selection / overlap, inference strength repaired"
level: L4
kind: statement
status: live
version: v2
sibling_of: research/autonomy/opus-capacity-campaign-20260908/paper-lane/CORRECTED-B-identity-selection-overlap/DATA-SUFFICIENCY.md
date: 2026-09-08
last_verified: 2026-09-08
---

# Data sufficiency v2 — what the delivered bytes support, at the right strength

Scope: v1's emitted artifacts only. Nothing was re-fetched, no job or leaf analysis was re-run,
and every v1 byte is unchanged (checks V1, V12). The v1 statement stands as the historical record;
the items below replace only the readings this repair corrects.

## Sufficient

1. **Observation identity.** `(nctId, outcome-measure index, results-group id)` keys all 16,116
   observations (v1 output, carried).
2. **Encoding comparison.** Whether two competing records are identical on every preserved
   identity field is decidable from the delivered bytes, and was decided: 0 of 4,464 sets are
   identical.
3. **Field-class attribution of a difference.** Which class of field separates a competing set —
   free-text-derived, or structured — is decidable and is recorded per set.
4. **Presence of an explicit parent/component statement.** Whether a parent group's own title or
   description enumerates its components or states the pooling arithmetic is decidable from the
   record and is recorded with the field name and its verbatim text (11 of 47).
5. **The excess-category partition.** The three exact conflict labels are disjoint and their union
   is the membership view; both are computable and both are stated (70 / 35 / 1; union 106).

## Insufficient — and therefore withheld

1. **Semantic duplication is NOT decidable here, in any of the 4,464 competing sets.** A
   difference in preserved strings establishes non-identical encodings only. **1,744 sets are
   separated by free-text-derived fields alone.** Whether any set is one measurement recorded twice
   or several genuinely different measurements is UNRESOLVED, and is left so.
2. **Overlap between cohorts is NOT decidable.** v1's finding stands: the cache carries no
   `participantFlowModule`, no baseline characteristics and no eligibility module, so no claim that
   two cohorts are disjoint — or that they share patients — is made anywhere.
3. **Parent and component identity of patients is NOT decidable from a name.** For the 26 name-only
   relations, `same_patients_claim` is NOT ESTABLISHED. For the 10 superset-language relations, the
   record describes a superset but names no component, so *which* cohorts are its components is not
   established either. Only the 11 enumerated relations are source-stated, and only for the
   components the record actually names.
4. **The choice among competing records is not decidable**, and — the correction to v1 item 4 — nor
   is the prior question of whether they measure the same thing. Both stay open.
5. **"Denominator usable" is a scope-limited flag**, meaning a positive reported Participants
   denominator at this component's scope. It establishes nothing about eligibility, about
   analysis-population membership, or about fitness for any downstream estimand.
6. **Source non-collection (639 observations) and an absent `reportingStatus` field (15
   observations, 10 trials) are separate metadata states.** Neither is evidence for the other and
   neither is a missing value.
7. **v1, job2 and job3 remain independently unconfirmed.** No quantity carried from them is
   verified by this repair; carried counts are labelled as v1 outputs.

## UNKNOWN, with locator and boundary

* **Semantic correspondence for all 4,464 competing sets** — UNKNOWN. Locator:
  `artifacts/RELATED-SETS-encoding-vs-semantics-v2.tsv`, column `semantic_duplication_status`.
  Boundary: resolving it would need per-record clinical adjudication or source content
  (participant flow, protocol endpoint definitions) that this cache does not contain; the scope of
  this repair forbids any source query, so it is recorded as unknown rather than pursued.
* **Component membership for the 10 superset-language relations** — UNKNOWN. Locator:
  `artifacts/GROUP-RELATIONS-candidate-parent-component-v2.tsv`, `relation_status` /
  `same_patients_claim`. Boundary: the record names no component group; nothing in the delivered
  bytes closes the gap.
* **Which of NCT00756509's two conflicting fields is wrong** — UNKNOWN, as in v1. Locator:
  `artifacts/ENROLLMENT-EXCESS-CATEGORIES-v2.tsv`, row 3. Boundary: the source states both 34 and
  41 and does not adjudicate; the inference stops.

## Consequence for the parked manuscript

Unchanged and, if anything, stricter: none of this authorises a response rate, a pooled cohort, a
capacity bound or a comparison, and none of it unparks the endpoint manuscript. The useful product
remains the source-bound ledger — now with its identity and relation labels stating only what the
delivered bytes actually show.
