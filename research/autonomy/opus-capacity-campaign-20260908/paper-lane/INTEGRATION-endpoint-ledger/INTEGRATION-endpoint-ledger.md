---
id: DOC-OPUS-CAMPAIGN-INTEGRATION-ENDPOINT-LEDGER
title: "Integrated endpoint curation ledger — proposed, source-bound, not scientific acceptance"
level: L4
kind: ledger
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Integrated endpoint ledger

⛔ **A proposed ledger and a transparent accounting. NOT scientific acceptance of anything.**
⛔ **No response rate, no capacity bound, no agent-independent effect, no control comparison, no
unique-patient total, no revised manuscript.** The endpoint manuscript stays **PARKED** and was not
read or edited.

> **job 2 and job 3 were NEVER independently confirmed.** Only job 1's arithmetic was
> (`VERIFY-job1-arithmetic.md`). The 552-key spine, its four-cell category rules, and its disease
> and phase attributions are inherited from that unconfirmed chain. This carries on all 552 rows,
> not only here.

## 1. The three grains, and the join

The components **do not share one grain**. The join is stated, verified, and never implicit.

```
CORRECTED-A   552 rows   key (nct_id, om_index, group_id)              job-1 contract rows
CORRECTED-C   552 rows   key (nct, om_title, group_title, evaluable_n) same records, TITLE-keyed,
                                                                       no om_index, no group_id
CORRECTED-B 16,116 obs   key nct#om<i>#<group_id>                      a much larger corpus:
             8,740 cohort keys (nct, group-title-norm)                 4,235 results trials
```

**A ↔ C.** No shared machine key exists; the only bridge is `(nct, om_title, group_title)`. Check
`I2` verifies it is unique on both sides with symmetric difference 0 — a bijection over all 552
rows — and `I2b` verifies C's `evaluable_n` equals A's carried job-1 value on 552/552. It is a
*string* bridge and is recorded as a hazard: any repeated title triple would break it, and the
check fails rather than silently picking one.

**A ↔ B.** Partial by construction, and recomputed independently by check `I3`:

| state | rows | trials |
|---|---|---|
| `JOINED_UNIQUE` | 458 | — |
| `TRIAL_OUTSIDE_B_CORPUS_SCOPE` | 48 | 21 |
| `MEASURE_OUTSIDE_B_TITLE_BOUNDARY` (job 2's response-title regex) | 46 | 17 |
| `GROUP_ABSENT_IN_B_MEASURE` | 0 | — |

The 94 non-joining rows stay in the spine carrying `B_NOT_ASSESSED`. In the other direction,
**15,658 B observations have no A or C counterpart at all** and are emitted in
`COVERAGE-b-observations.tsv` as `B_ONLY__NO_DENOMINATOR_CATEGORY_OR_ARM_COMPONENT`. Nothing is
inner-joined away (check `I4`).

**Known hazard, carried:** the 8 delivered leaf TSVs are schema-incompatible as delivered (4 headers
in QB, 4 in QC). B harmonised them under a recorded mapping; this integration consumes that output
and does not re-harmonise.

## 2. Actual row coverage

| | count |
|---|---|
| spine rows (= A's 552, bijective, check `I1`) | 552 |
| distinct trials in the spine | 138 |
| spine rows joined to a B observation | 458 |
| spine rows B never assessed | 94 |
| B observations outside the spine | 15,658 |
| disposition-map rows (A 552 + C 552 + B 16,116 + 94) | 17,314 |
| contradiction rows | 562 |
| rows with at least one contradiction | 459 |

## 3. The accounting

### Blocked — 447 rows

| blocking condition | rows |
|---|---|
| `B_DISJOINTNESS_UNVERIFIABLE_NO_PARTICIPANT_FLOW` (**universal**) | 552 |
| `B_COMPETING_RECORDS_UNRESOLVED` | 309 |
| `B_NOT_ASSESSED:*` | 94 |
| `A_DENOMINATOR_OR_CATEGORY_UNSUITABLE` | 61 |
| `C_ARM_LINK_NOT_CONFIRMED:*` (TYPE_ONLY 26 / CANDIDATE 10 / UNKNOWN 8 / UNRESOLVED 5) | 49 |
| `C_CONTROL_STATUS_UNKNOWN_IN_THIS_CACHE` | 25 |
| `C_CONTROL_STATUS_CONTESTED` | 5 |
| `C_CONTROL_STATUS_CANDIDATE_ONLY` | 1 |
| `B_OBSERVATION_NOT_USABLE_FOR_PROPORTION` | 0 |

### No component-specific block found — 105 rows

**Not an eligible subset.** These 105 (44 trials) still carry the universal disjointness condition,
still rest on the unconfirmed job2/job3 chain, and 11 of them sit in trials whose own record
contradicts a one-arm reading. Nothing may be computed from them. The state is named
`NO_COMPONENT_BLOCK_FOUND__NOT_AN_ELIGIBILITY_GRANT` for that reason.

### Repeated

309 spine rows lie in a B cohort key holding more than one competing observation; every one retains
its sibling observation ids, its unresolved-state tokens and `selection_status =
NOT_SELECTED_BY_DESIGN` (check `I10`). Corpus-wide B holds 4,464 such cohort keys of 8,740.
`DUPLICATE_ENCODING_CANDIDATE` is 0: no competing pair is identical on every identity field, so
none of this repetition is a mere duplicate encoding.

### Contested and contradictory — retained, never reconciled

| contradiction | rows |
|---|---|
| `C_SOLE_ARM_BUT_MULTIPLE_RESULTS_GROUPS` | 83 |
| `A_UNSUITABLE_WHILE_C_ARM_CONFIRMED` | 60 |
| `A_NOT_REFUTED_WHILE_C_ARM_*` (TYPE_ONLY 25 / CANDIDATE 10 / UNKNOWN 8 / UNRESOLVED 5) | 48 |
| `A_NOT_REFUTED_WHILE_B_SET_UNRESOLVED` | 270 |
| `ROW_NOT_ASSESSED_BY_B` | 94 |
| `C_CONTESTED_FLAG_PRESENT` | 7 |
| `A_B_DENOMINATOR_VALUE_DISAGREE` | **0** |

The load-bearing case is the 60 rows where **A says the denominator/category structure is unusable
and C says the arm link is confirmed**. Both are true statements about different things. A confirmed
arm on an uncomputable denominator is still uncomputable: both states are written on the row, the
row stays `BLOCKED`, and check `I6` fails if either is dropped.

The 0 denominator disagreements are worth naming precisely: A and B read the same participant
denominator from the same cache on all 458 jointly covered rows. That is agreement between two
independent readings — **not** confirmation of job 2.

### Uncomputable

Everything above the line of "a proportion could be formed at all": the 61 structurally unsuitable
rows, the 1,282 zero-denominator observations B retains as unusable, the 15 observations with no
`reportingStatus`, the 639 with an explicit non-collection statement, and — for every row without
exception — cohort disjointness, because the cache contains no `participantFlowModule`.

## 4. Checks

16 deterministic checks, `check_integration.py`, **exit 1 if any fails**. Real exit codes and the
full command log are in `CHECK-RUN-RECORD.txt`; the machine record is `INTEGRATION-CHECKS.json`.

The checks are demonstrably able to fail:

* the **first real run exited 1** (`RUN1-FAILING-checks.log`, 15/16) on a genuine defect in check
  `I7`, which was a name-only test. `I7` was made **stricter** — it now tests the values of every
  forbidden-named column and fails if one ever holds anything but the literal `NOT_DERIVED`;
* a **negative control** — a copy with one A `UNSUITABLE` state overwritten by C's confidence, and
  the 15,658 B-only rows inner-joined away — is **rejected with exit 1 and 4 failures** (`I4`, `I5`,
  `I6b`, `I13`): `NEG-CONTROL-checks.log`.

`scripts/preflight.sh` was **not** run: it is the commit gate and nothing is committed here.
No component was re-run; no job original or leaf file was touched (`CHECK-RUN-RECORD.txt` §R6–R7).

## 5. Verdict

`DATA-SUFFICIENCY.md` states it in full. In one line: **the ledger is complete and the analysis is
not supportable.** The endpoint manuscript stays **PARKED**, and unparking it needs (a) independent
confirmation of job 2 and job 3 or a spine rebuilt without them, (b) source evidence of cohort
disjointness this cache does not contain, and (c) a pre-registered rule for choosing among competing
records that no component is authorised to invent.

## Files

| file | what it is |
|---|---|
| `CONTRACT-INTEGRATION-endpoint-ledger.md` | the contract and its fences |
| `INTEGRATION-SCHEMA.json` | exact schema, grains, join, enumerations |
| `LEDGER-integrated-552.tsv` | the joined ledger, 552 rows |
| `COVERAGE-b-observations.tsv` | all 16,116 B observations with their coverage state |
| `DISPOSITION-MAP.tsv` | 17,314 rows: every component record's disposition |
| `CONTRADICTIONS.tsv` | 562 retained contradictions |
| `INTEGRATION-CENSUS.json` | census, recomputed by check `I13` |
| `INTEGRATION-CHECKS.json`, `checks.log` | check results |
| `CHECK-RUN-RECORD.txt` | command log with real exit codes |
| `RUN1-FAILING-checks.log`, `NEG-CONTROL-checks.log` | evidence the checks can fail |
| `INPUT-MANIFEST.json` | sha256 of every component file read |
| `DATA-SUFFICIENCY.md` | the coherent data-sufficiency statement |
