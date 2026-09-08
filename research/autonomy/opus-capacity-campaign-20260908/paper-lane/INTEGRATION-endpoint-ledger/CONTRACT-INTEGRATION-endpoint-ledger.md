---
id: DOC-OPUS-CAMPAIGN-INTEGRATION-ENDPOINT-LEDGER-CONTRACT
title: "Contract — integration of CORRECTED-A / -B / -C into one proposed source-bound ledger"
level: L4
kind: contract
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Contract

## What this is

A **proposed source-bound curation ledger** and a **transparent accounting** of which records are
resolved, excluded, contested, repeated and uncomputable, built by joining three corrected
components that do not share a grain.

⛔ **This is not scientific acceptance of anything.** Not of the components, not of any row, not of
any endpoint claim. A complete curation ledger is not scientific eligibility.

## Inputs — read-only, byte-verified, never re-run

| component | grain | rows | own checks |
|---|---|---|---|
| `CORRECTED-A-denominator-category` | `(nct_id, om_index, group_id)` | 552 | 12/12, 0 failed |
| `CORRECTED-B-identity-selection-overlap` | `obs_id = nct#om<i>#<group_id>`; cohort sets `(nct, group-title-norm)` | 16,116 observations / 8,740 cohort keys | 22/22, 0 failed |
| `CORRECTED-C-arm-attribution` | `(nct, om_title, group_title, evaluable_n)` | 552 | 13, 0 failed |

`INPUT-MANIFEST.json` pins the sha256 of every file read. `CHECK-RUN-RECORD.txt` §R6 re-hashes them
after the build: 8/8 unchanged. §R7 re-hashes the job-3 originals: unchanged, and byte-identical to
the hashes CORRECTED-C recorded. No component, no job1/job2/job3 original and none of the 16 leaf
files was modified, overwritten or re-executed. No network call was made. Nothing was committed.

## What this integration is permitted to produce

A joined ledger, a disposition map, a contradiction register, a coverage accounting, original check
records with real exit codes, and a data-sufficiency statement. **That is all.**

## What it must not produce — and does not

No response rate. No cross-disease capacity bound. No agent-independent effect. No control
comparison. No unique-patient total. No revised endpoint manuscript — the endpoint manuscript stays
**PARKED** and was neither read nor edited. `rate_derived`, `unique_patient_total_derived` and
`control_comparison_derived` are the literal `NOT_DERIVED` on 552/552 rows, and check `I7` fails if
any forbidden-named column ever holds anything else.

## Rules this integration binds itself to

1. **The join is stated, never implicit.** See `INTEGRATION-SCHEMA.json` → `grains_and_the_join`.
2. **No silent inner join.** Records present in one component and absent from another are emitted
   with an explicit non-join state on both sides (checks `I3`, `I4`, `I9`).
3. **Contradictions survive as contradictions.** Where CORRECTED-A marks a row unsuitable and
   CORRECTED-C confirms its arm, both states stand and the row stays blocked (check `I6`).
4. **No component value is rewritten by another component** (check `I5`).
5. **Duplicate, repeated and unresolved-alternative relationships are first-class states**, not
   collapsed to one row per cohort or one arm per record (checks `I10`, `I11`).
6. **job 2 and job 3 were NEVER independently confirmed.** Only job 1's arithmetic was. This is
   carried on every one of the 552 rows and in the census, not only in prose (check `I8`).
7. **Checks must be able to fail.** They did: the first real run exited 1 (`RUN1-FAILING-checks.log`),
   and a deliberately corrupted copy is rejected with exit 1 and 4 failures
   (`NEG-CONTROL-checks.log`). Real exit codes only; no pipes; nothing declared `EXIT=0` unemitted.

## Reproduce

```
python3 build_integration.py     # writes only this directory
python3 check_integration.py     # exits 1 if any check fails
```
