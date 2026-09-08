---
id: DOC-OPUS-CAMPAIGN-INTEGRATION2-SEMANTIC-LIMITATIONS
title: "Semantic limitations of the INTEGRATION2 endpoint ledger"
level: L4
kind: statement
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# What the words in this ledger do and do not mean

Every limitation below is a property of the **cached source and the three components**, not a
stylistic hedge. Each is enforced by a named check.

## 1 · "Not refuted by this component" is not "suitable"

A2's `NOT_REFUTED_BY_THIS_COMPONENT` (491 rows) records that **A2 found no denominator/category
defect**. It is not a finding that the record supports a proportion, and A2 constructed no
numerator. A2's advisory flag is now
`RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER` (101 rows): it is computed from the
**verbatim category title string alone**. It does not say those participants met any objective
response definition, does not classify anyone as a responder, and is neither an eligibility nor a
numerator warrant. That is A2's own wording and it is carried unchanged (`J5`, `J12`).

## 2 · Non-identical encoding is not semantic non-duplication

B2's finding is that **no competing set is identical on every preserved identity field** — the
encodings differ. Whether two competing records are the *same measurement on the same patients* is
`UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED` on **all 4,464** competing cohort keys
corpus-wide, **zero** semantically resolved; 309 of those sets contain a spine row. For **1,744**
of the 4,464 the only separating fields are free-text-derived — exactly the case B2's negative
control shows is not evidence of a distinct measurement; 48 spine rows sit in such a set.

⛔ This ledger therefore never says a competing pair is a distinct outcome, time point or
population, and never says duplicates are absent. `J11` fails if any such token appears.

## 3 · An arm link is source-confirmed on 58 of 552 rows

C2 deleted v1's narrative-token predicate. **58 rows are `SOURCE_CONFIRMED`; 494 (89.5 %) are
not** — 337 `PROPOSED`, 132 `LABEL_MATCH`, 13 `UNKNOWN_IN_THIS_CACHE`, 11 `UNRESOLVED`,
1 `CONTESTED`. `LABEL_MATCH` means a label string corresponded; it is not arm identity, and the
assumption is written in machine state on every row that carries one
(`ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY`, 132 rows;
`ASSUMES_THIS_RESULTS_GROUP_IS_A_SUBSET_OF_THE_REGISTERED_ARM_SET_MEMBERSHIP_UNPROVED`, 333 rows).

## 4 · `NOT_CONTROL` no longer exists, and comparator role is a separate axis from registry type

C2 removed `NOT_CONTROL` as a state. What v1 asserted as not-control is now
`NOT_ESTABLISHED_IN_THIS_CACHE` (166) or `UNKNOWN_IN_THIS_CACHE` (355). A comparator role is
**source-supported on 8 rows only**. The registry's arm *type* is recorded separately from the
comparator *role*, because a registered type of EXPERIMENTAL is not evidence about who served as a
comparator. The single occurrence of the retired vocabulary anywhere in the ledger is inside C2's
own historical change-map token `CHANGED_CLASS:NOT_CONTROL_ASSERTED->…`, carried verbatim in
`c_disposition_vs_v1`; `J12` fails if it appears in any state-bearing column.

## 5 · Two different unknowns, never merged

| | what is unknown | what it limits |
|---|---|---|
| **cross-observation disjointness** | whether two cohorts share patients | **pooling and unique-patient counting across records** |
| **within-record reporting** | whether an individual source observation's own values are present and readable at component scope | what can be said about that one record |

The cache carries **no `participantFlowModule`**, so cross-observation disjointness is
`UNVERIFIABLE_IN_THIS_CACHE__NO_PARTICIPANT_FLOW_MODULE` on all 552 rows.

⚠ **That absence is NOT proof that every conceivable within-record proportion is mathematically
uncomputable.** The two questions are different, and v1's single merged condition invited the
confusion. Within-record reporting is answered from each record's own fields instead:
**458 rows carry `SOURCE_VALUES_PRESENT_AT_B_SCOPE`** (54 of them alongside A2's structural
unsuitability), **94 are `NOT_ASSESSED_BY_B`** because they lie outside B's corpus or title
boundary, and **0 spine rows are unusable at B scope**.

⛔ **No proportion is authorised here regardless.** `proportion_authorisation` reads
`NO_PROPORTION_AUTHORISED_IN_THIS_INTEGRATION` on all 552 rows. Stating that the two unknowns are
distinct is a correction of the reasoning, **not** a licence to compute anything — the authority to
compute is absent for separate reasons (§6, and the HOLD's F1–F3). `J13` and `J13b` enforce both
halves.

## 6 · No selection rule exists, so no record was selected

`selection_status` is `NOT_SELECTED_BY_DESIGN` on every cohort set, corpus-wide. Choosing among
competing records would be a scientific decision the source does not license and no component is
authorised to invent (`J10`).

## 7 · The spine itself rests on an unconfirmed chain

Only **job 1's arithmetic** was independently re-derived. **job 2 and job 3 were never
independently confirmed**, and correcting A, B and C does not confirm them. The 552-key spine, its
four-cell category rules, and its disease and phase attributions are inherited from that chain.
Carried on all 552 rows (`J8`).
