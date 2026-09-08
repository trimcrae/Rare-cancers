---
id: DOC-OPUS-CAMPAIGN-CORRECTED-A-V2-FLAG-SEMANTICS
title: "CORRECTED-A v2 — dropped-category flag semantics repair"
level: L4
kind: curation
status: live
purpose: >
  An explicitly versioned sibling of CORRECTED-A (v1). It repairs ONE interpretive defect: v1 named
  an advisory flag RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER and described the 101 rows carrying
  it as rows that "lost responders". The flag is computed from the verbatim category title alone, and
  a verbatim title such as `Non-CR/Non-PD` does not establish that those participants meet an
  objective response definition. The identifier and its wording are replaced with a descriptive
  dropped-response-assessment-category flag; every title, every count and every value is preserved
  exactly, and v1 is left byte-for-byte intact.
scope: >
  L4. Contract / schema / flag identifiers over the existing v1 outputs. No source audit, no re-run
  of job 1, no leaf re-audit, no source query, no manuscript edit, no rate, no numerator, no
  unique-patient total, no capacity bound, no control analysis.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CORRECTED-A-DENOMINATOR-CATEGORY, DOC-OPUS-CAMPAIGN-CORRECTED-A-V2-NON-WARRANT-DEMONSTRATION]
---

# CORRECTED-A v2 — dropped-category flag semantics

⛔ The response-endpoint manuscript stays **parked**. Nothing here recomputes a manuscript quantity
or lifts a hold.

## 0 · What v1 got right, and is carried unchanged

The **literal source-participant denominator** and **full category preservation** direction is
correct and is carried forward without modification:

- raw denominator values and their hierarchical `denominator_provenance` — **unchanged**;
- the **column-26** treatment (label corrected, value byte-identical, old shard files untouched,
  the implied full-vector diagnostic emitted separately) — **unchanged**;
- 3,123 category records, 123 verbatim titles, `folded = NO` — **unchanged**
  (`corrected-a-v2-categories.tsv` is byte-identical to v1's file);
- every blocking reason code, every suitability state, every count — **unchanged**.

⛔ v1 and the original job-1 shard TSVs, leaf outputs and payload cache are **not modified**. v1's
outputs and their historical claims stand as the record of what was delivered
(check `D9`: 13 v1 files + 12 original job-1/leaf evidence files re-hashed, **0 changed**).

## 1 · The defect repaired

v1 filed `Non-CR/Non-PD` and eleven other verbatim titles under an advisory flag named
`RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER`, described it as "a category that reports
**responders** under its own criteria set", and said in prose that **101 rows lost responders**.

⚠ The flag is computed from the **verbatim title string alone**. A verbatim title such as
`Non-CR/Non-PD` **does not itself establish that those patients meet an objective response
definition**, and **no cross-criteria numerator has been adjudicated**. The name and the wording
asserted a conclusion the evidence does not carry.

## 2 · The rename (the whole change)

| | v1 | v2 |
|---|---|---|
| advisory flag code | `RESPONSE_BEARING_CATEGORY_DROPPED_BY_PRODUCER` | **`RESPONSE_ASSESSMENT_CATEGORY_TITLE_DROPPED_BY_PRODUCER`** |
| row column | `dropped_response_bearing_categories_with_values` | **`dropped_response_assessment_category_titles_with_values`** |
| inventory column | `response_bearing_title_flag` | **`response_assessment_category_title_flag`** |
| flag description | "dropped a category that reports **responders** under its own criteria set" | "dropped a category whose **verbatim title** matches a response-assessment vocabulary … computed from the title string alone … does NOT state that those participants met any objective response definition, is NOT an eligibility warrant and is NOT a numerator warrant" |
| rows carrying the flag | **101** | **101** (the same 101 rows) |

The three v1 identifiers survive only under `corrected-a-v2-schema.json → superseded_identifiers`,
labelled as superseded with the reason. They appear in no v2 data table, no v2 count and no live
schema slot (`D1`).

⛔ **Nothing is called a responder.** ⛔ **Nothing is folded into `CR` or `PR`.**
⛔ **No narrower responder class is retained** — `schema.warrants.responder_class_retained.retained
= false` — so no responder definition is asserted, and none is inferred from a title or a token.

## 3 · Did any row change? **No.**

`D8`, the proof: reversing **only** the identifier rename on the v2 tables reproduces the v1 files'
sha256 **exactly**.

```
corrected-a-v2-rows.tsv              reverse-renamed -> 0f1001e51e9244d7849c6b72e0d4668c858e842a3b5231c11ddb96e11cc0080a
corrected-a-rows.tsv (v1)                               0f1001e51e9244d7849c6b72e0d4668c858e842a3b5231c11ddb96e11cc0080a   equal
corrected-a-v2-category-inventory.tsv reverse-renamed -> eb6f3a2f8c4c5b6b5369536265949b73b73a729643d3549064389faf9a0355a6
corrected-a-category-inventory.tsv (v1)                  eb6f3a2f8c4c5b6b5369536265949b73b73a729643d3549064389faf9a0355a6   equal
corrected-a-v2-categories.tsv                         -> c8434d7d9d75d9e42ab881c98eef449257a15f0d80a35abe664cadd447e1a2e7  (byte-identical copy of v1)
```

**No row datum changed. 101 advisory-code strings were renamed in place and nothing else was
touched.** That is the correct outcome here; no change was manufactured to look productive.

## 4 · The 101 rows, restated without the claim

The 12 verbatim titles the old extraction dropped, with **every count preserved** — v1's list was at
the **category-record** grain, so the row grain is stated alongside it rather than replacing it:

| verbatim title | category records (v1 grain) | rows carrying it |
|---|---|---|
| `Non-CR/Non-PD (NCRNPD)` | 54 | 54 |
| `Non-CR/Non-PD` | 26 | 26 |
| `Very Good Partial Response (VGPR)` | 15 | 7 |
| `Stringent Complete Response (sCR)` | 13 | 5 |
| `CRh` | 8 | 8 |
| `CRi` | 8 | 8 |
| `CRmrd-` | 8 | 8 |
| `Minimal Response (MR)` | 3 | 3 |
| `Non-CR / Non-PD` | 3 | 3 |
| `Non-CR/Non-PD (NN)` | 2 | 2 |
| `MR` | 1 | 1 |
| `Near Complete Response (nCR)` | 1 | 1 |
| **total** | **142 records** | **101 distinct rows** |

The correct statement is: **on 101 rows the old extraction dropped a response-assessment category
that its four-label regex did not match.** ⛔ Not "101 rows lost responders."

## 5 · The positive-denominator constraint, checked explicitly

`D7` checks the **values**, not the state token. `denominator_state == READ_FROM_SOURCE` on 552/552
would not by itself have excluded a zero, an empty cell or a non-`Participants` denominator, so the
constraint is now checked on its own, keeping the distinctions separate:

| | rows |
|---|---|
| present, integer, **> 0** | **552** |
| reported **zero** (`== 0`) | 0 |
| negative | 0 |
| non-integer | 0 |
| **missing / empty** (no denominator read) | 0 |
| available units lack `Participants` (**non-participant denominator**) | 0 |

All 552 denominators are strictly positive participant counts. Zero, missing and nonparticipant
remain **distinct enumerated outcomes** of the check, not a single "not positive" bucket — had any
row hit one, it would have been reported under its own heading rather than folded into the others.

## 6 · Checks actually run, with real exit codes

`CHECK-RUN-RECORD-v2.txt` holds the commands and captured exits. No pipes were used, so `$?` is the
real exit code. **Both check attempts are preserved, including the failing one.**

| attempt | command | exit |
|---|---|---|
| build | `python3 build_corrected_a_v2.py` | **0** |
| check attempt 01 | `python3 check_corrected_a_v2.py` | **1** — 6/9, `D2`/`D5`/`D6` FAILED |
| check attempt 02 | `python3 check_corrected_a_v2.py` (harness fixed) | **0** — 9/9 |

⚠ Attempt 01's three failures were **defects in the checking harness, not in the data**: the checker
split the code cells on `;` when the tables use `|`, treated the `NONE` sentinel as a present code,
and its column-name regex flagged `rate_derived` — the column that *declares* no rate was derived.
`D8` passed in **both** attempts, so the data was never in question. Attempt 01's stdout/stderr are
retained verbatim in `CHECK-ATTEMPT-01-stdout.txt` / `-stderr.txt`; nothing was overwritten.

| id | check | result |
|---|---|---|
| D1 | the three v1 identifiers are absent from every v2 data table, count and live schema slot, and survive only as labelled superseded identifiers | PASS |
| D2 | every count preserved: advisory-code counts, blocking-code counts and the suitability partition identical to v1 under the rename (flag = 101) | PASS |
| D3 | every verbatim title preserved: 123 inventory titles in order, the same 12 flagged titles, the category ledger byte-identical, `folded = NO` | PASS |
| D4 | the flag is exactly the title-derived predicate: flag ⇔ non-empty dropped-title column, 0 mismatches / 552 | PASS |
| D5 | **not an eligibility warrant** — suitability is a function of the blocking codes alone (552/552); the flag is in no blocking cell and no blocking enumeration; flagged rows occur in both suitability states (97 / 4) | PASS |
| D6 | **not a numerator warrant** — no numerator/rate/percent column; `rate_derived = NOT_DERIVED` 552/552; the would-be numerator (per-row sum of the flagged categories, range 0..19) equals **no** emitted column | PASS |
| D7 | positive-denominator constraint checked on the values, zero / missing / non-participant kept distinct | PASS |
| D8 | no row datum changed — reverse-rename reproduces the v1 sha256 exactly | PASS |
| D9 | 13 v1 component files and 12 original job-1 / leaf evidence files re-hashed, 0 changed | PASS |

## 7 · Limitations, unchanged and restated

- **The cross-criteria numerator question stays open.** Whether `Non-CR/Non-PD`, `VGPR`, `sCR`,
  `CRh`, `CRi`, `CRmrd-`, `MR` or `nCR` counts belong in any objective-response numerator is a
  criteria decision that has **not** been adjudicated. This component does not decide it, and its
  flag must not be read as having decided it.
- **`NOT_REFUTED_BY_THIS_COMPONENT` (491 rows) is still not eligibility.** Job 2 (identity /
  selection / overlap) and job 3 (arm attribution) remain **independently unconfirmed**;
  `job2_job3_independently_confirmed` is `false` in the v2 summary as in v1.
- **61 rows remain `UNSUITABLE_FOR_PROPORTION`** on denominator/category grounds; v2 changes none
  of that adjudication.
- **The rename is not new evidence.** No source content was re-read, no payload re-fetched, no leaf
  re-audited. If the title-matching vocabulary itself is wrong for some record, this component does
  not detect it — it only stops the flag from asserting a responder conclusion.
- **UNKNOWN — the criteria set behind each verbatim title.** The delivered payload cache records
  category titles, not the criteria document that defines them. Locator: the categories carry
  `class_title` and `om_title` only; a criteria-bound definition would require source content
  outside `ctg-cache-216bd1b5`. Boundary: this component therefore binds **no** responder
  definition and retains **no** responder class, rather than guessing one from a title.

⛔ No response rate, unique-patient total, cross-disease capacity bound, control comparison or
manuscript edit appears anywhere in this component.
