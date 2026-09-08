---
id: DOC-OPUS-CAMPAIGN-INTEGRATION2-CHANGE-MAP
title: "Exact change map — INTEGRATION-endpoint-ledger (v1) to INTEGRATION2"
level: L4
kind: change-map
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Change map, v1 → INTEGRATION2

Machine forms: `CONTRADICTION-REDERIVATION.tsv` (per v1 contradiction code),
`INTEGRATION2-CENSUS.json → grain_preservation_vs_v1`, `INTEGRATION2-CHECKS.json`.
v1 is untouched; its own numbers below are read from its emitted tables, not restated from memory.

## A · Grains — preserved exactly

| grain | v1 | INTEGRATION2 | disposition |
|---|---|---|---|
| spine rows | 552 | 552 | UNCHANGED (row-key sets identical, `J1b`) |
| distinct trials in spine | 138 | 138 | UNCHANGED |
| joined to a B observation | 458 | 458 | UNCHANGED |
| B never assessed | 94 (48 + 46) | 94 (48 + 46) | UNCHANGED |
| B observations | 16,116 | 16,116 | UNCHANGED |
| B-only observations | 15,658 | 15,658 | UNCHANGED |
| disposition-map rows | 17,314 | 17,314 | UNCHANGED |
| corpus cohort keys | 8,740 | 8,740 | UNCHANGED |

## B · Values that changed, and the corrected component logic that forced each

| item | v1 | INTEGRATION2 | why |
|---|---|---|---|
| arm link treated as confirmed | `CONFIRMED` 503 rows | `SOURCE_CONFIRMED` **58** rows | C2 deleted v1's narrative-token corroboration predicate. 313 of v1's token-confirmed rows are now `PROPOSED`. Not a new judgement by this integration: C2's own state is carried. |
| `A_UNSUITABLE_WHILE_C_ARM_CONFIRMED` population | 60 rows | **5 rows** (`CROSS_COMPONENT_CONSTRAINT:A_UNSUITABLE_WITH_C_ARM_SOURCE_CONFIRMED`) | Same A2 rows (61 unsuitable, unchanged); the *confirmed* side shrank with C2. |
| control status | 8 states incl. `NOT_CONTROL_CONFIRMED` 454, `NOT_CONTROL_BY_ARM_SET_TYPE_INVARIANT` 26 | `comparator_role`: `UNKNOWN_IN_THIS_CACHE` 355, `NOT_ESTABLISHED_IN_THIS_CACHE` 166, source-supported **8**, proposed 19, contested 4 | `NOT_CONTROL` no longer exists as a C2 state. |
| registry arm type | folded into control status | separate `registry_type_statement` + `registry_type_statement_assumption` (333 conditional statements carry their membership assumption) | C2 separates the comparator role from the registry type. |
| B set semantics | `duplicate_encoding_candidate = 0`, read as "no competing pair is a mere duplicate encoding" | `encoding_identity_status` + `semantic_duplication_status` = `UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED` on all 4,464 competing sets, plus `distinction_basis` | B2 withdrew the semantic reading of a field-string comparison. |
| A advisory flag | `RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER` | `RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER` (same 101 rows) | A2 rename; **no row data value changed** (A2 check D8). |
| `integration_state` | BLOCKED 447 / no-block 105 | BLOCKED **550** / no-block **2** | Direct consequence of the two C2 changes above: rows whose arm link is not `SOURCE_CONFIRMED`, or whose comparator role is not source-supported, now carry a block. The 2 residual rows are `NCT02394795\|OM4\|OG001` and `NCT02472964\|OM0\|OG000`. Still **not** an eligibility grant. |
| disjointness condition | one universal code merging two unknowns | `AXIS_CROSS_OBSERVATION_DISJOINTNESS:…` (552) **plus** a separate `within_record_reporting_state` | see `SEMANTIC-LIMITATIONS.md` §5. |
| blocking codes | flat strings | axis-prefixed (`AXIS_DENOMINATOR_CATEGORY:`, `AXIS_ARM_ATTRIBUTION:`, `AXIS_COMPARATOR_ROLE:`, `AXIS_RECORD_IDENTITY:`, `AXIS_COVERAGE:`, `AXIS_OBSERVATION_USABILITY:`, `AXIS_CROSS_OBSERVATION_DISJOINTNESS:`) | the axis is what makes a combination a constraint rather than a contradiction. |

## C · The false "contradiction", renamed — and the re-derivation of all 562

v1 labelled **562 combinations across 459 rows** "contradictions", while conceding in the same
paragraph that the load-bearing case (A unsuitable + C arm confirmed) consists of **compatible
statements about different axes**. That is a constraint, not an incompatibility.

INTEGRATION2 splits the register in two and re-derives every v1 code
(`CONTRADICTION-REDERIVATION.tsv`):

| v1 code | v1 rows | verdict | v2 register |
|---|---|---|---|
| `A_UNSUITABLE_WHILE_C_ARM_CONFIRMED` | 60 | **not a contradiction** — cross-component *constraint* | `CROSS-COMPONENT-STATUS.tsv` |
| `A_NOT_REFUTED_WHILE_C_ARM_CONFIRMED_TYPE_ONLY` | 25 | not a contradiction (and the state itself is retired) | `CROSS-COMPONENT-STATUS.tsv` |
| `A_NOT_REFUTED_WHILE_C_ARM_CANDIDATE` | 10 | not a contradiction | `CROSS-COMPONENT-STATUS.tsv` |
| `A_NOT_REFUTED_WHILE_C_ARM_UNKNOWN_IN_THIS_CACHE` | 8 | not a contradiction — an unknown is not a claim | `CROSS-COMPONENT-STATUS.tsv` |
| `A_NOT_REFUTED_WHILE_C_ARM_UNRESOLVED` | 5 | not a contradiction | `CROSS-COMPONENT-STATUS.tsv` |
| `A_NOT_REFUTED_WHILE_B_SET_UNRESOLVED` | 270 | not a contradiction — different axes | `CROSS-COMPONENT-STATUS.tsv` |
| `ROW_NOT_ASSESSED_BY_B` | 94 | not a contradiction — a **coverage gap** | `CROSS-COMPONENT-STATUS.tsv`, kind `COVERAGE_GAP` |
| `C_SOLE_ARM_BUT_MULTIPLE_RESULTS_GROUPS` | 83 | **genuine contradiction**, retained | `CONTRADICTIONS-genuine.tsv` |
| `C_CONTESTED_FLAG_PRESENT` | 7 | **genuine contradiction**, retained | `CONTRADICTIONS-genuine.tsv` |
| `A_B_DENOMINATOR_VALUE_DISAGREE` | 0 | genuine if it ever occurs; test stays live | `CONTRADICTIONS-genuine.tsv` |

**472 of the 562 are not incompatibilities. 90 v1 rows were.**

In INTEGRATION2 the genuine register holds **91 entries on 91 rows**: 83 sole-registered-arm vs
multiple-results-groups, and **8** contested-flag entries — up from v1's 7 because C2 re-derives the
contested flags and itemises them (`PLACEBO_OR_NOINT_GROUP_TEXT_VS_NON_COMPARATOR_BOUND_TYPE` 3,
`PLACEBO_CLAIM_WITHOUT_ANY_PLACEBO_TYPED_ARM_IN_THIS_CACHE` 2,
`GROUP_TITLE_IS_A_TREATMENT_SEQUENCE_CONTAINING_A_PLACEBO_TOKEN` 2,
`LEAF_CLAIMED_ARM_LABEL_NOT_PRESENT_IN_REGISTERED_ARMS` 1) rather than collapsing them into one
code. `A_B_DENOMINATOR_VALUE_DISAGREE` is **0** again: A2 and B read the same participant
denominator on all 458 jointly covered rows. That is agreement between two independent readings of
one cache — **not** confirmation of job 2.

The cross-component register holds **807 entries on 488 rows**. Every one of them keeps both
component states, and every affected row stays `BLOCKED` (`J6`).

## D · What did not change

The endpoint manuscript status (**PARKED**), the HOLD's ten findings F1–F10, the unconfirmed
job2/job3 chain on all 552 rows, `selection_status = NOT_SELECTED_BY_DESIGN` everywhere, the
retained leaf-harmonisation hazard (8 leaf TSVs schema-incompatible as delivered, harmonised by B
under a recorded mapping and consumed here unchanged), and B's inclusion boundary — job 2's
response-title regex, retained deliberately so the change map joins 1:1, against a wider probe of
10,570 measures.
