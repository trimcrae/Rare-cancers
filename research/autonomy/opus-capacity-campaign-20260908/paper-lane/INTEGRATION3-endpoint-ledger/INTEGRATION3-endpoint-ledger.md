---
id: DOC-OPUS-CAMPAIGN-INTEGRATION3-ENDPOINT-LEDGER
title: "INTEGRATION3 — the endpoint curation ledger rebound to the corrected C2 v3 map"
level: L4
kind: ledger
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# INTEGRATION3 — the C2 v3 propagation

⛔ **A propagation of a corrected component, and a transparent accounting. NOT scientific
acceptance of anything.**
⛔ **No response rate, no cross-disease capacity bound, no agent-independent effect, no control
comparison, no unique-patient total, no revised manuscript.** The endpoint manuscript stays
**PARKED** and was not read or edited.

> **job 2 and job 3 were NEVER independently confirmed.** Only job 1's arithmetic was
> (`VERIFY-job1-arithmetic.md`). The 552-key spine, its four-cell category rules, and its disease
> and phase attributions are inherited from that unconfirmed chain. Correcting components A, B and
> C does not confirm it. This carries on all 552 rows, unchanged from v1 and v2.

This is a **new versioned sibling** of `INTEGRATION-endpoint-ledger/` (v1) and
`INTEGRATION2-endpoint-ledger/` (v2). **Both are untouched**, including v1's original failing check
log and negative-control log, and including v2's genuine-contradiction register whose counts this
document withdraws. All of it is hashed in `INPUT-MANIFEST3.json` and its preservation is checked
(`J16`, `J16b`, `J16c`).

## 1 · Why this exists

INTEGRATION2 was built against **C2 v2**. C2 then corrected itself to **v3**, and three of those
corrections reach into the integration. Nothing else about the integration was reopened: no
component was re-run, no job or leaf file was read or written, and no grain moved.

## 2 · What propagated

### (a) Vocabulary

| C2 v2 token (retired) | C2 v3 token | ledger rows |
|---|---|---|
| `SOURCE_CONFIRMED` | `SOURCE_FIELD_MATCH` | 58 |
| `COMPARATOR_SUPPORTED_BY_SOURCE_CONFIRMED_ARM_TYPE` | `COMPARATOR_TYPE_INFERRED_VIA_SOURCE_FIELD_MATCH` | 8 |
| `COMPARATOR_PROPOSED_BY_LABEL_MATCHED_ARM_TYPE` | `COMPARATOR_PROPOSED_BY_LABEL_FIELD_MATCHED_ARM_TYPE` | 13 |
| `ASSUMES_LABEL_CORRESPONDENCE_IS_ARM_IDENTITY` | `ASSUMES_LABEL_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED` | 132 |

`J12` fails if any retired token survives anywhere in a state-bearing column. It reads **0**. The
integration's own derived code names were changed with them, so that
`AXIS_ARM_ATTRIBUTION:C_ARM_LINK_NOT_SOURCE_CONFIRMED:*` is now
`…:C_ARM_LINK_NOT_SOURCE_FIELD_MATCHED:*`, and the constraint code
`CROSS_COMPONENT_CONSTRAINT:A_UNSUITABLE_WITH_C_ARM_SOURCE_CONFIRMED` (5 rows) is now
`…_WITH_C_ARM_SOURCE_FIELD_MATCH`.

### (b) ⭐ The count complement is gone

This is the substantive change, not a rename. C2 v3 records
`source_join_verification = NOT_ESTABLISHED_REGISTRY_JOIN_FIELDS_ABSENT_FROM_THIS_CACHE` on **all
552 rows**, and attaches an explicit `…_UNPROVED` identity assumption to every non-empty arm-link
state — **including** the 58 rows v2 called `SOURCE_CONFIRMED`.

So v2's arithmetic of "494 blocked on arm attribution, 58 not" no longer has a complement to
name. v3 blocks the arm-attribution axis **universally**:

| blocking condition | rows |
|---|---|
| `AXIS_ARM_ATTRIBUTION:C_REGISTRY_SOURCE_JOIN_NOT_ESTABLISHED` | **552** |
| `AXIS_ARM_ATTRIBUTION:C_ARM_LINK_NOT_SOURCE_FIELD_MATCHED:*` (PROPOSED 337 / LABEL_MATCH 132 / UNKNOWN 13 / UNRESOLVED 11 / CONTESTED 1) | 494 |
| `AXIS_ARM_IDENTITY_ASSUMPTION:C_*_UNPROVED` (subset 333 / label-field 132 / two-field 58) | 523 |

`K21` fails if any row is left without the universal join block. Consequently
`integration_state` is **BLOCKED on 552 of 552**; v2's two `NO_COMPONENT_BLOCK_FOUND` rows
(`NCT02394795|OM4|OG001`, `NCT02472964|OM0|OG000`) are now blocked like the rest. That was never
an eligibility grant in v2 and is not one now (`J18`).

### (c) Identity assumptions, carried onto every row

`c_registry_type_statement_assumption` moved on 190 rows, and two v3 columns are now carried that
v2 had no counterpart for: `c_source_join_verification` and `c_comparator_role_identity_assumption`
(8 two-field-match rows, 13 label-field rows). Also carried:
`c_group_text_comparator_wording_unverified` and `c_leaf_claim_verification_before_downgrade`, so a
reader can see what the leaf claims said before C2 v3 downgraded them.

## 3 · ⭐ The two demoted contradiction families

v2's `CONTRADICTIONS-genuine.tsv` held **91 entries on 91 rows**. Both of its families fail the
admission test this ledger applies:

> **A genuine contradiction is two demonstrably mutually exclusive assertions about the same
> object at the same scope.** A candidate that needs an unproved mapping, or that opposes an
> inference to a source field, is not one. **Zero is a permissible result, not a failed quota.**

**83 · sole registered arm vs multiple results groups → `UNRESOLVED_MAPPING_TENSION`.**
One registered arm in the arms module; several results groups in one outcome measure. These are two
modules at two different grains. They are mutually exclusive *only if* each results group must be a
registered arm — precisely the correspondence C2 v3 marks `…_UNPROVED`, over a registry join it
marks `NOT_ESTABLISHED` on all 552 rows. Under a reporting-group reading both statements stand.

**8 · contested flags → `UNRESOLVED_EVIDENCE_TENSION`.**
Each contested flag opposes a token- or text-derived reading (group-title wording, a leaf claim) to
a registry field: an inference against a source statement, not two source assertions about one
object. v3 additionally downgrades the leaf claims, records the group description as a transformed
excerpt rather than verbatim, and marks group-text comparator wording unverified. The **blanket
promotion** of any contested flag to a contradiction is withdrawn.

Both families keep every flag, every row and every reason, in `UNRESOLVED-TENSIONS3.tsv` (91
entries on 91 rows, MAPPING 83 / EVIDENCE 8), each with a `what_would_settle_it` column. `K20`
fails if the flag counts move: C2 v3 and the ledger both carry 83 `sole_arm…=YES` rows and 8 rows
with contested flags. **Demotion changes the register a flag is counted in. It must not change how
many flags exist.**

`CONTRADICTIONS-genuine3.tsv` is therefore **empty, with its full header**. Its one remaining
family — `A_B_DENOMINATOR_VALUE_DISAGREE`, two components reading one cached denominator field —
passes the admission test, is re-tested here, and reads **0**, as it did in v1 and v2. The test
stays live.

## 4 · ⚠ What is withdrawn, and what is not erased

**Withdrawn as assertions**: v2's "**91 genuinely incompatible claims**" and its "**90 of 562 v1
rows were** [incompatibilities]". Those counts are no longer asserted by this lane.

**Not erased**: `INTEGRATION2-endpoint-ledger/` is intact, byte for byte, and remains the record of
what v2 claimed; `J16c` re-hashes it and fails on any modification. `K19` proves the demotion lost
nothing — every one of v2's 91 entries is present here, in one register or the other, on the same
row. `CONTRADICTION-REDERIVATION3.tsv` carries a `v2_verdict_now_withdrawn` column beside each v3
verdict rather than overwriting the v2 one.

I am withdrawing my own lane's earlier count, not correcting an external source.

## 5 · Grains: unchanged, and required to be

| | v1 | v2 | v3 |
|---|---|---|---|
| spine rows | 552 | 552 | 552 |
| joined to a B observation | 458 | 458 | 458 |
| B never assessed | 94 | 94 | 94 |
| B observations not in the spine, emitted not dropped | 15,658 | 15,658 | 15,658 |
| B observation rows | 16,116 | 16,116 | 16,116 |
| disposition-map rows | 17,314 | 17,314 | 17,314 |

Row-key set identical to both v1 and v2. `J3b` fails if any of these moves. **The propagation
changes states and registers, never grains.**

## 6 · Checks

**31 deterministic checks**, `check_integration3.py`, **exit 1 if any fails** — v2's 25, retargeted,
plus `J14c` (the demoted register recomputed from the components) and `K19`–`K22`, which exist only
because of this propagation. Real exit codes and every attempt are preserved under `CHECK-RUNS/`;
the machine record is `INTEGRATION3-CHECKS.json`.

The checks are demonstrably able to fail. Two real failures are preserved:

* `RUN-03` **exited 1 on a traceback** — `J11`'s hard-coded file list still named v2's outputs.
* `RUN-04` **exited 1 with 1 failure** — `J9` counted a disposition component label the builder had
  renamed `CORRECTED-C-v3`. The check was right and the label had moved; the check was retargeted,
  not relaxed.
* One check name embedded a retired token in a code **of my own making**
  (`AXIS_COMPARATOR_ROLE:C_TYPE_INFERRED_NOT_SOURCE_CONFIRMED`, 8 rows), which the strict
  retired-vocabulary scan correctly flagged. I renamed my code to `…NOT_SOURCE_ESTABLISHED` rather
  than loosen the matcher. `RUN-01` (exit 0) preserves the census as it stood before that rename.

A **negative control with nine planted defects** is **rejected with exit 1 and 14 failures**
(`CHECK-RUNS/RUN-06-negcontrol-*`, `NEG-CONTROL/`). Six are v2's. Three target this propagation
exactly: the retired `SOURCE_CONFIRMED` restored on an arm link (`J12`), a contested flag silently
**dropped** while being demoted (`J14c`, `K19`, `K20`), and a row left unblocked on arm attribution
(`K21`). A demoted tension re-promoted into the genuine register is also rejected (`J14`, `J14b`).

`scripts/preflight.sh` is the repository commit gate and is run at commit time, not here.
No component was re-run; no job original, leaf file, v1 byte or v2 byte was written.

## 7 · Verdict — unchanged

`DATA-SUFFICIENCY3.md` states it in full. In one line: **the ledger is complete and the analysis is
not supportable.** The propagation makes the ledger *more* blocked, not less: the arm-attribution
axis now blocks universally, and zero established contradictions is a statement about the strength
of the evidence for incompatibility, **not** a statement that the records agree. **The endpoint
paper stays PARKED**, findings **F1–F10** of `HOLD-endpoint-extraction-validity.md` are untouched
and unsatisfied, and no endpoint selection is authorised (`J17`, `J18`).

## Files

| file | what it is |
|---|---|
| `CONTRACT-INTEGRATION3-propagation.md` | the contract and its fences |
| `LEDGER3-integrated-552.tsv` | the joined ledger, 552 rows, 90 columns |
| `COVERAGE3-b-observations.tsv` | all 16,116 B observations with their coverage state |
| `DISPOSITION-MAP3.tsv` | 17,314 rows: every component record's disposition |
| `CROSS-COMPONENT-STATUS3.tsv` | 807 compatible cross-component combinations and coverage gaps |
| `CONTRADICTIONS-genuine3.tsv` | **empty, with header** — the admission test's surviving family reads 0 |
| `UNRESOLVED-TENSIONS3.tsv` | 91 demoted entries, every flag retained, with what would settle each |
| `CONTRADICTION-REDERIVATION3.tsv` | v1's codes re-derived, beside the v2 verdict now withdrawn |
| `CHANGE-MAP-v2-to-v3.md` | the exact v2 → v3 change map, per column |
| `DATA-SUFFICIENCY3.md` | the coherent data-sufficiency statement |
| `INTEGRATION3-CENSUS.json` | census, recomputed by `J15` |
| `INTEGRATION3-CHECKS.json` | check results |
| `CHECK-RUNS/` | every attempt, its command and its real exit code, including two failures |
| `NEG-CONTROL/` | the rejected negative control and its nine planted defects |
| `INPUT-MANIFEST3.json` | sha256 of every input, including all of v1 and all of v2 |
| `SHA256-INTEGRATION3-OUTPUTS.txt` | sha256 of everything this component emitted |
| `build_integration3.py`, `check_integration3.py`, `neg_control3.py` | the code |
