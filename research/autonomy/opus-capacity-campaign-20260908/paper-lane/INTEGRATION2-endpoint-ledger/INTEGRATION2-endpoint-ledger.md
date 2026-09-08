---
id: DOC-OPUS-CAMPAIGN-INTEGRATION2-ENDPOINT-LEDGER
title: "INTEGRATION2 — integrated endpoint curation ledger over the corrected v2 components"
level: L4
kind: ledger
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# INTEGRATION2 — integrated endpoint ledger

⛔ **A proposed ledger and a transparent accounting. NOT scientific acceptance of anything.**
⛔ **No response rate, no cross-disease capacity bound, no agent-independent effect, no control
comparison, no unique-patient total, no revised manuscript.** The endpoint manuscript stays
**PARKED** and was not read or edited.

> **job 2 and job 3 were NEVER independently confirmed.** Only job 1's arithmetic was
> (`VERIFY-job1-arithmetic.md`). The 552-key spine, its four-cell category rules, and its disease
> and phase attributions are inherited from that unconfirmed chain. Correcting components A, B and
> C does not confirm it. This carries on all 552 rows.

This is a **new versioned sibling** of `INTEGRATION-endpoint-ledger/` (v1). v1 is untouched,
including its original failing check log and its negative-control log; both are hashed in
`INPUT-MANIFEST2.json` and their preservation is checked (`J16`, `J16b`).

## 1 · Coverage — the grains root required, preserved

| | count |
|---|---|
| spine rows (A2's 552, bijective, `J1`) | 552 |
| distinct trials in the spine | 138 |
| spine rows joined to a B observation | 458 |
| spine rows B never assessed (48 trial-outside / 46 measure-outside) | 94 |
| B observations with no A or C counterpart, emitted not dropped | 15,658 |
| disposition-map rows (A 552 + C 552 + B 16,116 + 94) | 17,314 |

`J3b` fails if any of 552 / 458 / 94 / 15,658 moves. The row-key set is identical to v1's (`J1b`).
Corrected component logic changed **no grain**; what it changed are the states written on those
rows, itemised in `CHANGE-MAP-v1-to-v2.md`.

## 2 · The states that arrived, at their delivered strength

| component | what arrives | check |
|---|---|---|
| **A2** | 61 `UNSUITABLE_FOR_PROPORTION`, 491 `NOT_REFUTED_BY_THIS_COMPONENT`; the renamed advisory flag `RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER` on 101 rows; no responder class, no numerator | `J5`, `J12` |
| **B2** | `NON_IDENTICAL_ENCODING_ON_PRESERVED_FIELDS` with `semantic_duplication_status = UNRESOLVED__SEMANTIC_CORRESPONDENCE_NOT_ESTABLISHED` on all 4,464 competing sets (309 spine rows), **zero** semantically resolved; `distinction_basis = TEXT_DERIVED_ONLY` on 1,744 sets (48 spine rows) | `J10`, `J11` |
| **C2** | 58 `SOURCE_CONFIRMED`, 337 `PROPOSED`, 132 `LABEL_MATCH`, 13 `UNKNOWN_IN_THIS_CACHE`, 11 `UNRESOLVED`, 1 `CONTESTED`; comparator role separate from registry type; 333 conditional type statements carrying their membership assumption | `J5`, `J12` |

Nothing is promoted. `J12` fails if any retired or stronger token (`NOT_CONTROL*`,
`CONFIRMED_TYPE_ONLY`, `RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER`,
`DUPLICATE_ENCODING_CANDIDATE`) appears in a state-bearing column.

## 3 · The accounting, by axis

| axis | blocking condition | rows |
|---|---|---|
| cross-observation disjointness | `NO_PARTICIPANT_FLOW_MODULE_IN_THIS_CACHE` (**universal**) | 552 |
| arm attribution | `C_ARM_LINK_NOT_SOURCE_CONFIRMED` (PROPOSED 337 / LABEL_MATCH 132 / UNKNOWN 13 / UNRESOLVED 11 / CONTESTED 1) | 494 |
| comparator role | not source-supported (UNKNOWN 355 / NOT_ESTABLISHED 166 / proposed 19 / contested 4) | 544 |
| record identity | `B_COMPETING_RECORDS_SEMANTIC_CORRESPONDENCE_UNRESOLVED` | 309 |
| record identity | `B_DISTINCTION_TEXT_DERIVED_ONLY` | 48 |
| denominator/category | `A_UNSUITABLE_FOR_PROPORTION` | 61 |
| coverage | `B_NOT_ASSESSED` | 94 |
| observation usability | `B_NOT_USABLE_AT_B_SCOPE` | 0 |

**BLOCKED 550 · no component-specific block 2.** The 2 are
`NCT02394795|OM4|OG001` and `NCT02472964|OM0|OG000`. ⛔ **Not an eligible subset** — they still
carry the universal disjointness condition and the unconfirmed chain, and no eligibility subset is
constructed or emitted anywhere (`J18`).

## 4 · ⭐ The false "contradiction", renamed

v1 called an A-unsuitable + C-arm-confirmed pair a **contradiction** and then conceded in the same
paragraph that both statements are true about **different axes**. That is a **constraint**, not an
incompatibility. INTEGRATION2 splits the register:

* **`CROSS-COMPONENT-STATUS.tsv`** — 807 entries on 488 rows: compatible statements about different
  axes, plus the 94 coverage gaps. Every entry keeps both component states and the row stays
  `BLOCKED` (`J6`).
* **`CONTRADICTIONS-genuine.tsv`** — **91 entries on 91 rows**, reserved for claims that cannot both
  be true: 83 sole-registered-arm-vs-multiple-results-groups, 8 contested-flag entries. The
  A↔B denominator disagreement test is live and reads **0**.

All 562 v1 labels are re-derived in `CONTRADICTION-REDERIVATION.tsv`: **472 of 562 were not
incompatibilities**; 90 v1 rows were. `J14b` recomputes the genuine register from the components
and fails on any disagreement.

## 5 · ⚠ Two unknowns v1 merged, now separate

**Unknown cross-observation disjointness** (no `participantFlowModule`) limits **pooling and
unique-patient counting across records**. It is **not** the same as an inability to report an
individual source observation, and **absence of `participantFlowModule` is NOT proof that every
conceivable within-record proportion is mathematically uncomputable.**

Within-record reporting is answered from each record's own fields: 458 `SOURCE_VALUES_PRESENT_AT_B_SCOPE`,
94 `NOT_ASSESSED_BY_B`, 0 unusable at B scope.

⛔ **No proportion is authorised here regardless.** `proportion_authorisation` reads
`NO_PROPORTION_AUTHORISED_IN_THIS_INTEGRATION` on all 552 rows; the five sentinel columns read
`NOT_DERIVED` on all 552. Correcting the reasoning is not a licence to compute (`J13`, `J13b`, `J7`).

## 6 · Checks

**25 deterministic checks**, `check_integration2.py`, **exit 1 if any fails**. Real exit codes and
every attempt are preserved under `CHECK-RUNS/`; the machine record is `INTEGRATION2-CHECKS.json`.

The checks are demonstrably able to fail:

* the **first real check run exited 1** with **3 genuine defects** in the checks themselves
  (`CHECK-RUNS/RUN-02-checks-*`, 21/24): `J7` matched `orr` as a substring inside
  `correspondence`; `J12` scanned the whole file and so tripped on C2's own historical change-map
  token carried verbatim in `c_disposition_vs_v1`; `J17` looked for `**F1**` while the HOLD writes
  `**F1 ·`. All three were repaired by making the check **more precise, and J7 and J12 stricter** —
  `J7` now also fails on any proportion-shaped cell value anywhere in the ledger, and `J12` now
  additionally fails if the retired `NOT_CONTROL` vocabulary appears in the change-map column in
  any form but C2's `CHANGED_CLASS:NOT_CONTROL_ASSERTED->…`. No ledger value was changed to make a
  check pass.
* a **negative control** with six planted defects is **rejected with exit 1 and 8 failures**
  (`CHECK-RUNS/RUN-04-negcontrol-*`, `NEG-CONTROL/`): A's doubt overwritten by C's confidence, the
  15,658 B-only rows inner-joined away, a `LABEL_MATCH` promoted to `SOURCE_CONFIRMED`, the two
  unknowns merged, a compatible status moved into the genuine-contradiction register, and B2's
  unresolved semantics strengthened to a not-a-duplicate claim.

`scripts/preflight.sh` was **not** run: it is the commit gate, and nothing is committed here.
No component was re-run; no job original, leaf file or v1 byte was written (`J16`).

## 7 · Verdict

`DATA-SUFFICIENCY2.md` states it in full. In one line: **the ledger is complete and the analysis is
not supportable.** Three source distinctions remain unresolved — (a) job 2 and job 3 unconfirmed,
(b) no cohort-disjointness evidence in this cache, (c) semantic correspondence among competing
records not established and no pre-registered selection rule. **Because those are unresolved, the
endpoint paper stays PARKED.** A complete curation ledger is not automatic scientific eligibility.

⚠ A repaired ledger **does not** satisfy the earlier paper's clinical or causal claims, **does not**
answer the HOLD's findings **F1–F10**, and **does not authorise any new endpoint selection**
(`J17`).

## Files

| file | what it is |
|---|---|
| `CONTRACT-INTEGRATION2-endpoint-ledger.md` | the contract and its fences |
| `INTEGRATION2-SCHEMA.json` | grains, joins, enumerations, sentinels |
| `LEDGER2-integrated-552.tsv` | the joined ledger, 552 rows |
| `COVERAGE2-b-observations.tsv` | all 16,116 B observations with their coverage state |
| `DISPOSITION-MAP2.tsv` | 17,314 rows: every component record's disposition |
| `CROSS-COMPONENT-STATUS.tsv` | 807 compatible cross-component combinations and coverage gaps |
| `CONTRADICTIONS-genuine.tsv` | 91 genuinely incompatible claims, retained unresolved |
| `CONTRADICTION-REDERIVATION.tsv` | every v1 contradiction code re-derived to its register |
| `CHANGE-MAP-v1-to-v2.md` | the exact change map |
| `SEMANTIC-LIMITATIONS.md` | what the words do and do not mean |
| `DATA-SUFFICIENCY2.md` | the coherent data-sufficiency statement |
| `INTEGRATION2-CENSUS.json` | census, recomputed by `J15` |
| `INTEGRATION2-CHECKS.json` | check results |
| `CHECK-RUNS/` | every attempt, its command and its real exit code |
| `NEG-CONTROL/` | the rejected negative control and its planted defects |
| `INPUT-MANIFEST2.json` | sha256 of every input, including all of v1 |
| `build_integration2.py`, `check_integration2.py`, `neg_control2.py` | the code |
