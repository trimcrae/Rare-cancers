---
id: DOC-OPUS-CAMPAIGN-INTEGRATION3-ADDENDUM
title: "INTEGRATION3 — dated current identity and scope record"
level: L4
kind: addendum
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# INTEGRATION3 — current identity and scope, dated

**Additive.** `SHA256-INTEGRATION3-OUTPUTS.txt` (the original 18-entry list) and every failed run
under `CHECK-RUNS/` are **historical originals and are left byte-unchanged.** This record states the
current identities beside them; it replaces nothing.

## Current identities of the three outputs the C2 item-5 propagation moved

Measured here with `sha256sum`, and agreeing with the intake report
(`C2-INTEGRATION3-INTAKE-REPORT.md`, 13,525 B, sha256
`a7bf3559ab0707222e9ed0c63c9cb81a7105cf715024988658516fab9a45b6db`) entry for entry:

| file | sha256 in the original 18-entry list | **current** sha256 | current bytes |
|---|---|---|---|
| `INPUT-MANIFEST3.json` | `b18e4aef38359a31e1396d8c14630123b4d78382c522f3db56d98ddc3704f46c` | **`845ee852106d6435b1fb9efe1c37769838778f86e181c8de2ff35175a355c2a8`** | 5,375 |
| `INTEGRATION3-CENSUS.json` | `6300961fad5b57fa2a3fcdcd894c5a75502a36aa9f9f7de60181cb94bf3b54bc` | **`a213a472edfa66dca8036a85284e9699c9b08e60d52de21acaa30c0c9cfa5694`** | 11,414 |
| `LEDGER3-integrated-552.tsv` | `d048335bede7104e86136458318db5420ede968be5929caaad2d496dfe29c4ce` | **`098f855a3b5344ca4e8700241757fd3fa6f4302aefae15c29903035ed7fffd27`** | 1,737,655 |

The other 15 entries of the original list are unchanged.

## Execution summary, extended — RUN-09 and RUN-10 are real and follow RUN-08

| run | command | exit | note |
|---|---|---|---|
| RUN-01 build | `build_integration3.py` | 0 | census then reported 8 retired-token hits, from a blocking code of my own making |
| RUN-02 build | `build_integration3.py` | 0 | after renaming that code; retired-token count 0 |
| RUN-03 checks | `check_integration3.py` | **1** | **preserved failure** — traceback, `J11` still named v2 filenames |
| RUN-04 checks | `check_integration3.py` | **1** | **preserved failure** — `J9` counted a disposition label the builder had renamed |
| RUN-05 checks | `check_integration3.py` | 0 | 31/31 |
| RUN-06 negcontrol | `neg_control3.py` then `check_integration3.py --dir NEG-CONTROL` | 0 then **1** | **required failure** — 9 planted defects rejected, 14 checks failed |
| RUN-07 settled build | `build_integration3.py` | 0 | re-derivation byte-identical across 19 artifacts |
| RUN-08 settled checks | `check_integration3.py` | 0 | 31/31 |
| **RUN-09 c2residual build** | `build_integration3.py` | **0** | the C2 item-5 propagation |
| **RUN-10 c2residual checks** | `check_integration3.py` | **0** | 31/31 after the propagation |

**Honest history: four builds (01, 02, 07, 09), five direct check runs (03, 04, 05, 08, 10), and one
compound negative control (06).** ⛔ Missing per-attempt `cwd`, runtime and environment snapshots are
**not reconstructed** and are named as missing.

## ⛔ What this record does NOT claim

**There is no authentic pre-RUN-09 INTEGRATION3 ledger among the inspected outputs.** RUN-07 and
RUN-09 both wrote `LEDGER3-integrated-552.tsv` in place, so the pre-propagation bytes survive only as
the hash in the original 18-entry list, not as a retained file.

⛔ **I therefore do NOT claim an independently proven complete two-fields-only final-step diff.** The
one-row / two-field result I reported was computed against a copy taken in-session immediately before
RUN-09, and that copy is not itself a preserved original. The claim it supports is that the
propagation *as executed* moved one row in two consumed fields; it is **not** a proof reconstructed
from retained artifacts, and it should not be read as one.

## Mechanical state, reported as mechanical state

552-row spine, all A-side and B-side values, the 83 sole-arm plus 8 contested flags, and **zero**
genuine-contradiction entries stand as **reported mechanical state of this ledger**. ⛔ They are
**not** clinical validation and **not** source validation. **The endpoint paper stays PARKED** under
its existing ten findings.

## Corrected in this pass

* `build_integration3.py`'s vocabulary comment said the `SOURCE_FIELD_MATCH` state carries
  `ASSUMES_TWO_AGREEING…`, as if all 58 rows did. **They do not** — 57 by two agreeing field matches,
  1 by a unique description-field match. Corrected in place with the correction dated.
* `CHANGE-MAP-v2-to-v3.md`'s assumption row read `58 → …TWO_AGREEING…`. Corrected to **57 + 1**, with
  the superseded wording quoted inside the correction. The 190 total is unchanged.

⛔ No table, data or branch changed; no producer or test was run for this addendum; nothing was
regenerated. Root's acceptance of the finite C2 defect fix implies **no** clinical, source or gate
clearance.
