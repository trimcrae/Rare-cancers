---
id: DOC-OPUS-CAMPAIGN-C2-V3-RESIDUAL-ITEM5-APPLIED
title: "C2 v3 finite residual — item 5 applied, 2026-09-08"
level: L4
kind: applied-record
status: live
date: 2026-09-08
last_verified: 2026-09-08
---

# C2 v3 finite residual — item 5, APPLIED

Applied by the **sole integrating parent**, not a duplicate owner. Capsule verified first at pin
`0985321e8836ebf7aa24ee40b5d161493b6a4a0f`: **9/9 ZIP members CRC-clean and byte-exact** against the
manifest, zero unsafe paths; root memo 5,346 B `aa389db7…`; `INTAKE-REPORT.md` 14,285 B `135b4673…`;
`DELIVERABLE-HASHES.json` 1,445 B `c7866391…` — all exact.

## The error, and what actually caused it

`decide_comparator` selected the identity assumption from the **arm_link_state**:

```python
"ASSUMES_LABEL_FIELD_CORRESPONDENCE_..." if link["arm_link_state"] == "LABEL_MATCH"
else "ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES_..."
```

But `SOURCE_FIELD_MATCH` is reached by **two different relations**, and they do not share a premise.
Measured from the delivered map, exactly as root states:

| relation | rows | assumption it actually rests on |
|---|---|---|
| `TWO_AGREEING_FIELD_MATCHES:*` | **57** | two agreeing source fields |
| `DESCRIPTION_FIELD_MATCH_ONLY:DESC_BYTE_EXACT` | **1** | a unique description field alone |
| `LABEL_FIELD_MATCH_ONLY:*` | **132** | label correspondence |

The single description-only row therefore carried a two-agreeing premise it does not have.

**The fix is to select on the relation, because the relation is the thing that knows.** A cleared
contrary-description binding prefixes the relation, so the prefix is stripped before reading it. A
fourth catch-all token names an unclassified relation form rather than defaulting to the strongest
premise — and check `V8` asserts it is **unused (0 rows)**, so a future producer change cannot hide
there.

## The one changed cell

`NCT02994953`, outcome *"Part B: Number of Participants With Confirmed Best Overall Response (BOR)
Assessed by Investigator Using RECIST Version 1.1"*, group *"Part B Cohort 1: UC Cohort Stage 1
Combination Therapy (Experimental)"*, bound arm index **5**:

```
registry_type_statement_assumption
  before  ASSUMES_TWO_AGREEING_SOURCE_FIELD_MATCHES_ARE_ARM_IDENTITY_UNPROVED
  after   ASSUMES_DESCRIPTION_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED
```

Its `comparator_role` stays `NOT_ESTABLISHED_IN_THIS_CACHE`; the eight inferred-comparator count is
unchanged. **No row's state, role, binding, count or numeric value was changed to meet a partition.**

## Invariance — measured, 13 checks, exit 0

`RESIDUAL-2026-09-08/verify_item5.py`, run RUN-R03, all 13 PASS:

552 rows and 53 columns unchanged in count and order · **all 552 keys identical** · **exactly one
changed cell in exactly one row, in exactly one column** · that row is the description-only
NCT02994953 row · its comparator role unchanged · partition now **57 / 1 / 132** · catch-all token
**unused** · every `arm_link_state` count unchanged (`SOURCE_FIELD_MATCH` still 58) · every
`comparator_role` count unchanged (8 inferred) · `bound_arm_index` identical on all 552 rows ·
every numeric field unchanged · every flag unchanged (8 contested tokens, 83 sole-arm YES).

## Documentation residues, also corrected

* **Producer comments 327 / 334** — "two independent exact field identities" and "an explicit
  within-record identity" now say *field correspondences*, not proven identities, and name the
  premise each carries.
* **The v2 rules docstring** — marked `[HISTORICAL — written for v2]` with a dated CURRENT note
  naming the two assertions no longer true of this producer (narrative is a labelled transformed
  excerpt, not verbatim; label+description are two fields of the **same** record and their agreement
  is not independent confirmation). **The v2 text is left exactly as written** — not retokenised.
* **Schema** — the assumption field now documents **three** alternatives selected by relation, plus
  the unused catch-all; and the retired v2 token
  `LABEL_AND_DESCRIPTION_SOURCE_IDENTITIES_NAME_DIFFERENT_ARMS` is replaced by the current
  `…_FIELD_MATCHES_…`.
* **Fixture T5b** — it stopped at `decide_link` and so **never exercised the propagation**, which is
  exactly how the wrong token survived. It now calls `decide_comparator`, asserts the
  relation-specific assumption, asserts it is *not* the two-agreeing one, and requires any propagated
  `role_assume` to match. Renamed to `T5b_description_only_relation_carries_its_OWN_relation_specific_assumption`.
* **Report** — "one settled curation derivation" corrected to "one settled correction **batch**",
  naming the **two actual derivations RUN-01 and RUN-05** with delta and test runs separate, and
  recording that **RUN-02's exit 1 is original and the later 21-pass does not overwrite it**. The
  336 / 158 / 58 counts are now explicitly scoped to the **carried** columns, with the two excluded
  prose columns (378 changed comparator-basis strings) and the **14 added** columns named as outside
  the classification and **not** proof of complete per-row semantic identity.

**The other four accepted repairs were not repeated**, and no v2 or v3 original was erased.

## Executions — real commands, measured exits

| run | command | exit |
|---|---|---|
| RUN-R01-tests | `python3 CORRECTED-C-arm-attribution-v3-tests.py` | **0** — 21 tests, 21 PASS |
| RUN-R02-derive | `python3 CORRECTED-C-arm-attribution-v3-derive.py <map> <checks>` | **0** — the one admitted metadata derivation |
| RUN-R03-invariance | `python3 RESIDUAL-2026-09-08/verify_item5.py` | **0** — 13/13 |

The original v3 runs `RUN-01 … RUN-07` are untouched, `RUN-02`'s **exit 1** included.

## Dependent propagation — Integration3

Re-derived and re-checked: `RUN-09-c2residual-build` **exit 0**, `RUN-10-c2residual-checks`
**exit 0, 31/31 passed**. Exactly **one row** moved, `NCT02994953|OM5|OG000`, in exactly the two
fields that consume the assumption:

* `c_registry_type_statement_assumption` → `ASSUMES_DESCRIPTION_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED`
* `blocking_conditions` → `AXIS_ARM_IDENTITY_ASSUMPTION:C_ASSUMES_DESCRIPTION_FIELD_CORRESPONDENCE_IS_ARM_IDENTITY_UNPROVED`

Nothing else in the 552-row ledger changed. No job 2/3 re-run, no source-leaf curation, no joined-row
census, no clinical calculation, no broad suite, no new model audit.

⚠ Integration3's separate **83-granularity / 8-uncertainty demotion** repair is a **different**
matter and still requires its own committed return; it is complete on disk and blocked only by the
commit gate recorded in `PARENT-GATE-RECORD/`. No global absence or acceptance is inferred from any
sampled delta.
