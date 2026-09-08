---
id: DOC-OPUS-CAMPAIGN-INTEGRATION2-CONTRACT
title: "Contract — INTEGRATION2 endpoint curation ledger over the corrected v2 components"
level: L4
kind: contract
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# Contract — INTEGRATION2

## What this is

A **new explicitly versioned sibling** of `INTEGRATION-endpoint-ledger/` (v1), built over the
settled corrected components **A2**, **B2** and **C2**. It supersedes nothing: every v1 byte,
including v1's original failing check log and its negative-control log, stays exactly as delivered
and is hashed here so its preservation is checkable (`J16`, `J16b`).

## Fences — what this integration does NOT do

⛔ No response rate, proportion or percentage of any kind.
⛔ No cross-disease capacity bound. No agent-independent effect. No control comparison.
⛔ No unique-patient total, no pooled cohort, no de-duplicated denominator.
⛔ No scientific eligibility subset is constructed, named as eligible, or emitted as a file.
⛔ No revised endpoint manuscript. The endpoint paper was not read or edited and stays **PARKED**.
⛔ No source query, no network, no re-run of any job or leaf, no re-harmonisation of the 8 leaf
TSVs, no independent pre-audit, no batch planner, no broad test suite.
⛔ No component state is strengthened, resolved, merged, normalised or overwritten by another
component.

## Inputs (read-only; hashed in `INPUT-MANIFEST2.json`)

| component | file | grain |
|---|---|---|
| A2 | `CORRECTED-A-denominator-category-v2/corrected-a-v2-rows.tsv` | `(nct_id, om_index, group_id)`, 552 |
| C2 | `CORRECTED-C-arm-attribution-v2/CORRECTED-C-arm-attribution-v2-map.tsv` | `(nct, om_title, group_title, evaluable_n)`, 552 |
| B (v1) | `CORRECTED-B-identity-selection-overlap/artifacts/LEDGER-response-observations.tsv` | `obs_id`, 16,116 |
| B2 | `CORRECTED-B2-.../artifacts/RELATED-SETS-encoding-vs-semantics-v2.tsv` | `cohort_key`, 8,740 |
| v1 | `INTEGRATION-endpoint-ledger/*` | comparison only |

**Why the observation ledger is B v1's.** B2 repaired inference strength, not observation-level
source facts, and did **not** re-emit `LEDGER-response-observations.tsv`. Its cohort-key set and
`observation_ids` are byte-identical to v1's related-sets file (verified before use: 8,740 keys,
0 differing membership strings). Using v1's observation rows with B2's set semantics is therefore
the correct pairing, and it is stated rather than implied.

## Obligations

1. **Grains are preserved**: 552 spine rows, 458 joined, 94 never assessed by B, 15,658 B-only
   observations. `J3b` fails on any change. Changes that corrected component logic genuinely
   forces are shown in `CHANGE-MAP-v1-to-v2.md` with their cause, not absorbed silently.
2. **Uncertainty arrives no firmer than it left.** A2's renamed advisory flag, B2's unresolved
   semantics and C2's `PROPOSED` / `LABEL_MATCH` / `CONTESTED` states are carried verbatim
   (`J5`), and no retired stronger vocabulary may appear (`J12`).
3. **"Contradiction" is reserved for genuinely incompatible claims** (`J14`, `J14b`). Compatible
   statements about different axes are **cross-component status / constraints**.
4. **The two unknowns stay apart** (`J13`): cross-observation disjointness is not within-record
   reportability, and the absent `participantFlowModule` is never cited as a within-record bar.
5. **Checks must be able to fail.** Every attempt is preserved in its own directory under
   `CHECK-RUNS/` with the real exit code; a negative control must be rejected with exit 1.
6. **The endpoint HOLD and its ten findings F1–F10 stand** and are not satisfied by this ledger
   (`J17`).
