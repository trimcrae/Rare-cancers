---
id: DOC-OPUS-CAMPAIGN-CORRECTED-C-ARM-ATTRIBUTION-V2-CHANGEMAP
title: "CORRECTED-C v2 — exact change map against v1, with the unresolved counts"
level: L4
kind: evidence
status: live
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CORRECTED-C-ARM-ATTRIBUTION]
---

# Change map — CORRECTED-C v1 → CORRECTED-C v2

Row-level map: `CHANGE-MAP-v1-to-v2.tsv` (552 rows, one per included results group, same key set as
v1 and Job 3). Nothing in v1, Job 3 or the 16 leaves was edited, re-run or re-graded in place.
**v1's map, its checks JSON and its contract remain exactly as they were written, and the claims
they made stand on the record as claims that were made.** This file states where v2 disagrees.

## 1 · Why the counts fall

v1 confirmed **314** of 552 rows by testing whether a leaf's free-text narrative contained any of
ten tokens (`description`, `interventionnames`, `bijection`, `complement`, `partition`, `enumerat`,
`verbatim`, `reproduced`, `drug set`, `elimination`). That predicate reports **what a narrative
mentioned**, not that a source relation was verified — a narrative reading "the description is
absent … so no verbatim field supports elimination of either arm" satisfies all of it.

v2 deletes the predicate. Of those **314** rows, **313 are now PROPOSED / UNVERIFIED** and **1**
survives as `SOURCE_CONFIRMED`. There was no confirmation quota; 503 / 521 / 41 were never targets.
A large fall is the correct consequence of removing a token test.

## 2 · Arm-link state transition (exact, all 552 rows)

| v1 state (evidence code) | v2 state | rows |
|---|---|---|
| CONFIRMED (LEAF_WITHIN_RECORD_RELATION — the token test) | PROPOSED | **313** |
| CONFIRMED (LEAF_WITHIN_RECORD_RELATION) | SOURCE_CONFIRMED | 1 |
| CONFIRMED (LABEL_BYTE_EXACT) | SOURCE_CONFIRMED | 41 |
| CONFIRMED (LABEL_BYTE_EXACT) | LABEL_MATCH | 96 |
| CONFIRMED (LABEL_CASE_AND_WHITESPACE_ONLY) | SOURCE_CONFIRMED | 16 |
| CONFIRMED (LABEL_CASE_AND_WHITESPACE_ONLY) | LABEL_MATCH | 36 |
| CONFIRMED_TYPE_ONLY (LEAF_SOLE_REGISTERED_ARM_TYPE_ONLY) | PROPOSED | 13 |
| CONFIRMED_TYPE_ONLY (LEAF_ARM_SET_TYPE_INVARIANT) | PROPOSED / UNRESOLVED | 2 / 1 |
| CONFIRMED_TYPE_ONLY (LEAF_ARM_IDENTITY_NOT_BOUND_ARM_SET_TYPE_INVARIANT) | UNRESOLVED | 10 |
| CANDIDATE (LEAF_LABEL_STRING_ONLY_NOT_CONFIRMED) | PROPOSED | 9 |
| CANDIDATE (LEAF_ARM_IDENTITY_NOT_BOUND_TO_A_SINGLE_ARM) | CONTESTED | 1 |
| UNRESOLVED (LEAF_ARMS_MUTUALLY_INDISTINGUISHABLE) | UNKNOWN_IN_THIS_CACHE | 5 |
| UNKNOWN_IN_THIS_CACHE (3 codes) | UNKNOWN_IN_THIS_CACHE | 8 |

**No row moved upward.** Every transition is a demotion, a split, or unchanged.

## 3 · Unresolved counts (v2, of 552)

| v2 arm-link state | rows | meaning |
|---|---|---|
| SOURCE_CONFIRMED | **58** | two independent exact field identities agree on one arm (57), or a unique description-field identity (1) |
| LABEL_MATCH | **132** | unique exact (96) or case/whitespace-only (36) label correspondence, and nothing else |
| PROPOSED | **337** | a leaf named exactly one real registered arm, but **no exact source field relation exists in this cache**; the claim and its locator are retained, unpromoted |
| UNRESOLVED | **11** | the leaf claimed several registered arms (an aggregation, not an identity); all candidates preserved |
| CONTESTED | **1** | the leaf's claimed label is not a registered arm label in the record |
| UNKNOWN_IN_THIS_CACHE | **13** | zero registered arms (6), leaf recovered no arm (6), no relation at all (1) |

**Not source-confirmed: 494 of 552 (89.5%).**

| v2 comparator role (clinical) | rows |
|---|---|
| COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE | **8** |
| COMPARATOR_PROPOSED (label-matched arm type 13, group text 6) | **19** |
| CONTESTED | **4** |
| NOT_ESTABLISHED_IN_THIS_CACHE | **166** |
| UNKNOWN_IN_THIS_CACHE | **355** |

v1 asserted `NOT_CONTROL_*` for **480** rows (454 confirmed + 26 by arm-set type invariant). v2
asserts `NOT_CONTROL` for **none**. Those 480 rows split exactly: **166** →
`NOT_ESTABLISHED_IN_THIS_CACHE` (an arm is bound and its registered type is EXPERIMENTAL/OTHER —
*absence of comparator evidence, not evidence of absence*) and **314** → `UNKNOWN_IN_THIS_CACHE`
(no arm is bound at all).

## 4 · The five separations v2 keeps distinct in machine state

1. **LABEL_MATCH ≠ SOURCE_CONFIRMED.** A unique identical label is preserved as useful evidence
   with its exact field path (`armGroups[i].label`), and where it carries a registered comparator
   type the role is `COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE`, never supported — with
   `registry_type_statement_assumption = ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY`. Where other
   source fields conflict it is downgraded, not preserved (§5).
2. **Explicit within-record identity** is recorded only with an exact field path and the relation
   that holds: `TWO_INDEPENDENT_FIELD_IDENTITIES:LABEL_BYTE_EXACT+DESC_BYTE_EXACT` (38),
   `…+DESC_CASE_WS_FOLD` (3), `LABEL_CASE_WS_FOLD+DESC_BYTE_EXACT` (16),
   `DESCRIPTION_FIELD_IDENTITY:DESC_BYTE_EXACT` (1).
3. **Cardinality and uniform arm type are CONDITIONAL statements.** 320 rows carry
   `ALL_REGISTERED_ARMS_NON_COMPARATOR_TYPED_CONDITIONAL` and 13
   `ALL_REGISTERED_ARMS_COMPARATOR_TYPED_CONDITIONAL`, each with the machine-readable assumption
   `ASSUMES_THIS_RESULTS_GROUP_IS_A_SUBSET_OF_THE_REGISTERED_ARM_SET_MEMBERSHIP_UNPROVED`. v1's
   `NOT_CONTROL_BY_ARM_SET_TYPE_INVARIANT` (26 rows) asserted this unconditionally; it is gone.
4. **Four distinct unknowns.** zero arms → `NO_ARMS_REGISTERED_IN_THIS_CACHE` (6); absent type →
   `ARM_TYPE_ABSENT_IN_THIS_CACHE` (3) / `BOUND_ARM_TYPE_ABSENT_IN_THIS_CACHE`; placebo-vs-type →
   `CONTESTED` (3 flagged); candidate fields → `candidate_arm_indices` / `_labels` / `_types`.
5. **Comparator role and registry type are separate columns.** `bound_arm_registered_type_verbatim`
   and `registry_arm_types_in_record_verbatim` reproduce the registered types verbatim; no
   EXPERIMENTAL/OTHER value is read as proof that a group had no comparator role.

## 5 · The two withdrawn rules

- **Monotonicity withdrawn.** v1: "a leaf may only strengthen; never downgrade an exact match."
  v2 downgrades on contrary source evidence — a unique description identity naming a different arm
  (`LABEL_IDENTITY_AND_DESCRIPTION_IDENTITY_DISAGREE`), a bound arm whose registered description
  says it never enrolled (`CONTRARY_DESCRIPTION:…`), and placebo/control wording against the bound
  arm's registered type (3 + 0 rows flagged). Contested rows resolve to neither side.
- **First-candidate binding withdrawn.** v1 bound with `next((a for a in ai if …), arm)`. v2
  records the exact candidate count in `n_candidate_arms` and binds only when it is 1; 11 rows with
  2+ compatible arms bind nothing and keep every candidate.

## 6 · Semantic limitations (unchanged by this repair)

- **The registry's own explicit join fields are absent from this cache by established fact**:
  `resultsSection.participantFlowModule` and
  `armsInterventionsModule.interventions[].armGroupLabels` were never fetched (0 occurrences across
  all 12 payloads, checked). They were not fetched here either. **This is why 337 rows can only be
  PROPOSED: the evidence that would settle them is not in this cache.** Recorded as UNKNOWN with a
  locator, not hunted for.
- `SOURCE_CONFIRMED` means two exact fields of one cached record agree. It is **not** a registry
  assertion that the results group *is* that arm, and it is not clinical validation.
- The 552-key set, the disease attributions and the phase attributions are **inherited from the
  unconfirmed job2/job3 chain** and are not re-derived or endorsed here.
- No response rate, no unique-patient total, no control comparison, no effect estimate and no
  clinical comparison is computed. **The endpoint manuscript stays parked.**
