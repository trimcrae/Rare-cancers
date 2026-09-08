---
id: DOC-OPUS-CAMPAIGN-INTEGRATION3-CHANGE-MAP
title: "INTEGRATION2 → INTEGRATION3: the exact change map"
level: L4
kind: change-map
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# INTEGRATION2 → INTEGRATION3 — exact change map

Both ledgers hold the same 552 rows under the same row keys. v2 has 85 columns, v3 has 90. **No
column was removed.** Measured by re-reading both emitted ledgers, column by column.

## Columns added (5)

| column | source | why |
|---|---|---|
| `c_source_join_verification` | C2 v3, verbatim | `NOT_ESTABLISHED_REGISTRY_JOIN_FIELDS_ABSENT_FROM_THIS_CACHE` × 552 |
| `c_comparator_role_identity_assumption` | C2 v3, verbatim | 8 two-field-match rows, 13 label-field rows, 531 empty |
| `c_group_text_comparator_wording_unverified` | C2 v3, verbatim | so a comparator read from group text is visibly unverified |
| `c_leaf_claim_verification_before_downgrade` | C2 v3, verbatim | so v3's leaf-claim downgrade is visible, not silent |
| `unresolved_tensions` | derived here | the demoted register's per-row codes; `NONE` on 461 rows |

## Shared columns whose values changed

All 552 rows changed in at least one shared column. Per column:

| column | rows changed | what changed |
|---|---|---|
| `c_component` | 552 | provenance string now names `C2-correction/CORRECTED-C-arm-attribution-v3` |
| `blocking_conditions` | 552 | the universal `C_REGISTRY_SOURCE_JOIN_NOT_ESTABLISHED`, the new identity-assumption axis, and the renamed arm/comparator codes |
| `c_comparator_role_basis` | 378 | C2 v3's own rewritten basis text, carried verbatim |
| `c_arm_link_relation` | 190 | C2 v3, verbatim |
| `c_registry_type_statement_assumption` | 190 | 58 → `ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES…_UNPROVED`; 132 → `ASSUMES_LABEL_FIELD_CORRESPONDENCE…_UNPROVED` |
| `contradictions_genuine` | 91 | 91 rows go from a genuine code to `NONE`; the same 91 rows gain `unresolved_tensions` |
| `c_arm_link_state` | 58 | `SOURCE_CONFIRMED` → `SOURCE_FIELD_MATCH` |
| `c_disposition_vs_v1` | 41 | C2 v3's own change-map column, carried verbatim |
| `c_comparator_role` | 21 | 13 `…LABEL_MATCHED…` → `…LABEL_FIELD_MATCHED…`; 8 `COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE` → `COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH` |
| `c_registry_type_statement` | 6 | C2 v3, verbatim |
| `cross_component_status` | 5 | `CROSS_COMPONENT_CONSTRAINT:A_UNSUITABLE_WITH_C_ARM_SOURCE_CONFIRMED` → `…_WITH_C_ARM_SOURCE_FIELD_MATCH` |
| `integration_state` | 2 | `NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT` → `BLOCKED` (the universal join block now reaches them) |

**Zero rows changed** in every A-side and B-side column, in the join states, in the two
cross-observation/within-record unknown columns, in the sentinels, or in `source_pointer`. The
propagation touched the C axis and what the integration derives from it — nothing else.

## Registers

| register | v2 | v3 |
|---|---|---|
| `CROSS-COMPONENT-STATUS*.tsv` | 807 entries / 488 rows | 807 entries / 488 rows (5 codes renamed) |
| `CONTRADICTIONS-genuine*.tsv` | 91 entries / 91 rows | **0 entries**, header retained |
| `UNRESOLVED-TENSIONS3.tsv` | — | 91 entries / 91 rows (MAPPING 83, EVIDENCE 8) |

`K19` proves the move is lossless: v2's 91 entries and v3's 91 entries agree row by row.

## Counts withdrawn as assertions, preserved as history

* v2: "**91 genuinely incompatible claims**, retained unresolved" — **withdrawn**.
* v2: "**472 of 562 were not incompatibilities**; **90 v1 rows were**" — the 90 is **withdrawn**;
  the 562 re-derivation itself stands and is reproduced in `CONTRADICTION-REDERIVATION3.tsv` with
  a `v2_verdict_now_withdrawn` column beside each v3 verdict.

`INTEGRATION2-endpoint-ledger/` is unmodified. `J16c` re-hashes it and fails on any change.

## Grains

Unmoved: 552 / 458 / 94 / 15,658 / 16,116 / 17,314, and the row-key set is identical to both v1 and
v2 (`J1b`, `J3b`, `J4`, `J9`).
