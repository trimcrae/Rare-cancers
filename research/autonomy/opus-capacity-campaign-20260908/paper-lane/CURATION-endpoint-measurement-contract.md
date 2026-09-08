---
id: DOC-OPUS-CAMPAIGN-CURATION-ENDPOINT-MEASUREMENT-CONTRACT
title: "Source validation — measurement and denominator contract for the endpoint cache"
level: L4
kind: curation
status: live
purpose: >
  Map every derived endpoint-corpus count back to the study, outcome measure, group, class,
  time frame, unit and REPORTED DENOMINATOR in the source ClinicalTrials.gov records, classify each
  mapping valid / ambiguous / unsupported, and state the minimal contract a correct extraction must
  bind. Evidence against the parked paper's reopening condition (route 1).
scope: >
  L4. Source validation only. It repairs nothing, recomputes no manuscript quantity, proposes no
  replacement rate, edits no manuscript or producer, and lifts no hold. It makes no claim about
  causal ceilings, cause fractions, patient capacity or treatment efficacy.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-HOLD-ENDPOINT]
---

# Measurement and denominator contract — source validation of the derived endpoint cache

⛔ The response-endpoint manuscript stays parked. Nothing here reinstates a withdrawn claim.

## 1 · What was read, and what was not

Sole input: the already-delivered immutable copy of the ClinicalTrials.gov payload cache at
revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f` (branch `literature-cache`), 12 payloads plus
`_manifest.json`, 157,268,733 payload bytes. **No network request of any kind was made**, no payload
was re-fetched, no source was substituted, and no second copy of the cache was created.

Integrity of the delivered bytes was verified against the shipped digest list:
`sha256sum -c SHA256-MANIFEST.txt` → 13/13 `OK`, **exit 0**.

Derived artifact compared against: `research/manuscripts/endpoint/endpoint-corpus-inputs.json`
(552 arm rows), produced by `research/manuscripts/endpoint_corpus.py --extract`.

## 2 · Method

A read-only replay reproduced the producer's extraction from the raw payloads in the producer's own
order (BOR eras, then placebo eras), with the producer's category regexes, integer test, four-cell
requirement and `(nct, outcome title, group title, n)` de-duplication — but recording, for every
emitted row, the full source pointer rather than only the sum.

**Fidelity check.** The replay emitted **552 rows**, positionally identical to the 552 rows of the
committed `endpoint-corpus-inputs.json` on `(nct_id, outcome_measure_title, arm_title, evaluable_n,
cells)`: **0 mismatches**. Every statement below is therefore about the rows the paper actually used.

Sharding: the work divides naturally by payload era, and the per-era row tables are published as
separate shard files (section 6). The inspection itself is a deterministic pass over the one
delivered cache copy — 552 rows over 138 trials did not merit farming the same question out to
parallel reviewers, and no unit was reviewed twice.

## 3 · What the source records actually carry

Each ClinicalTrials.gov v2 outcome measure carries, alongside `classes[].categories[].measurements`,
an explicit **`denoms`** block: the denominator the trial reported, per group, with its units.

- **552 / 552 rows have exactly one reported participant denominator** (`denoms.units ==
  "Participants"`) for their group in the same record. It was available in every case and the
  producer reads none of it — `evaluable_n` is `sum(cells.values())`, full stop.
- **548 / 552 rows**: the sum of **all** integer categories in the contributing class(es) equals the
  reported denominator exactly. The record is internally consistent and the denominator is
  recoverable. (The 4 exceptions are rows whose classes are overlapping subgroups or repeated
  timepoints, so the categories sum to a multiple of the denominator: `NCT01790503` 197 vs 53,
  `NCT02150967` 118 vs 59, `NCT02440464` OG000 42 vs 21 and OG001 44 vs 22.)
- **299 / 552 rows**: the derived `evaluable_n` is **strictly smaller** than the denominator the
  trial reported. Median shortfall 3 participants, maximum 112. **0 rows exceed it.**
- 253 / 552 rows: the sum coincides with the reported denominator — because those records carry only
  the four matched categories, not because the producer read a denominator.

The shortfall is the categories the four-label regex drops. Most frequent dropped category titles
across the corpus: `Unknown` (155), `Not Evaluable` (77), `NE` (70), `Missing` (57),
`Non-CR/Non-PD (NCRNPD)` (54), `Not evaluable` (50), `Not Evaluable (NE)` (26), `Non-CR/Non-PD` (26),
`Very Good Partial Response (VGPR)` (15), `UE` (15), `Not Done` (14),
`Stringent Complete Response (sCR)` (13), `Died Before Evaluation` (8), `CRh` (8).

Two of those are not "non-evaluable" at all: `VGPR`, `sCR`, `CRh` and `CRmrd-` are **response**
categories in myeloma and leukaemia reporting. Dropping them removes responders from both the
numerator and the denominator of the derived row.

All 552 rows have `unitOfMeasure` = `Participants` and `paramType` = `COUNT_OF_PARTICIPANTS`; every
row carries a non-empty `timeFrame`; 451 carry a `populationDescription` (ITT / FAS / per-protocol /
response-evaluable), and **none of `timeFrame`, `populationDescription` or `denoms` is stored in the
derived cache**.

## 4 · Classification of all 552 mappings

The mapping under test is the manuscript's own statement: that a row's denominator is the one the
trial **reported** (§2.1 "alongside an evaluable denominator"; §2.3 "an arm whose categories came
from different denominators fails the build"). Rules applied to each row:

| Label | Rule |
|---|---|
| **valid** | Cells come from a single class with no repeated assignment, unit is `Participants`, and the record's own reported participant denominator **equals** the stored `evaluable_n`. The derived number is independently confirmed by the record. |
| **ambiguous** | Denominator matches, but two or more source categories collided onto one stored label (last write wins), so the stored category value does not identify which reported category it is. Here the collided values happened to agree. |
| **unsupported** | The record contradicts the mapping: reported denominator ≠ stored `evaluable_n`, or a category value was overwritten by a **conflicting** value from another class. |

| Classification | Rows |
|---|---|
| valid | **233** |
| ambiguous | **19** |
| unsupported | **300** |
| total | **552** |

Overwrite scope, independent of the above: **10 rows** have a value overwritten **across classes**,
**51 rows** have a value overwritten **within** one class by a second colliding category title, 491
rows have no repeated assignment. **22 rows** had the overwritten values actually differ.

⛔ No row was called `valid` by summing categories and finding the total plausible. `valid` requires
a separately reported denominator in the record that the sum matches.

## 5 · Evidence for the two named defects

### 5.1 The denominator is inferred from cells, not read (299 rows)

`endpoint_corpus.py` computes `n = sum(cells.values())` and stores it as `evaluable_n`; the
manuscript's build assertion "the four categories sum to the denominator" is then true by
construction and can fail for no row. The record disagrees with the derived number in 299 of 552
rows. Largest instances, each a single-class outcome measure whose reported denominator is stated
outright in the record:

| NCT | group | reported denominator | derived `evaluable_n` | populationDescription |
|---|---|---|---|---|
| NCT02395172 | Docetaxel | 396 | 284 | "Full analysis set (FAS) included all participants who were randomized to study." |
| NCT02263508 | Phase 3: Placebo + Pembrolizumab | 346 | 251 | "All participants randomized in Phase 3" |
| NCT02395172 | Docetaxel (PD-L1+) | 265 | 192 | "PD-L1+ FAS included all PD-L1+ tumor participants…" |
| NCT03445533 | Arm A: Ipilimumab | 243 | 176 | "All percentages were based on the number of participants in the Intent-to-Treat (ITT) analysis…" |
| NCT03445533 | Arm B: IMO-2125 + Ipilimumab | 238 | 171 | same |

Every rate the paper computes on `evaluable_n` for these rows is a rate on a response-evaluable
subset that the record does not define as the denominator, presented as the trial's reported one.

### 5.2 A category value overwritten across source classes (10 rows)

`_cells_for_groups` iterates `for cl in om["classes"]` and assigns `per[gid][label] = int(f)` with no
guard, so when the same group appears in several classes the **last class silently wins**.

**Exhibit A — NCT00654238 (`ctg_results_bor_1999_2009.txt`, outcome "To Determine the Efficacy (Best
Response) of BAY 43-9006 …", group OG000 "Sorafenib").** The four classes are histology strata:
`Differentiated`, `Poorly Differenitated` [sic], `Medullary`, `Anaplastic`. Reported participant
denominator: **55** (all four strata sum to 55). Source values for OG000:

| label | Differentiated | Poorly diff. | Medullary | Anaplastic | stored |
|---|---|---|---|---|---|
| CR | 0 | 0 | 0 | 0 | 0 |
| PR | 16 | 2 | 1 | 0 | **0** |
| SD | 22 | 1 | 2 | 0 | **0** |
| PD | 1 | 1 | 0 | 1 | **1** |

The committed corpus row is `{"CR":0,"PR":0,"SD":0,"PD":1}`, `evaluable_n: 1` — the Anaplastic
stratum alone, labelled with the whole trial's four conditions. A trial reporting 19 responses in 55
patients enters the analysis as **0 responses in 1 patient**. This row also passes the manuscript's
"categories came from different denominators fails the build" assertion, because that assertion is
checked against the sum of the same cells.

**Exhibit B — NCT01790503 ("Summary of Best Overall Response by Subgroups in the Modified
Intent-To-Treat Population…", group OG000).** The eight classes are overlapping subgroups (age
18–64 / 65+, complete / partial resection, KPS 70–89 / 90–100, MGMT methylated / unmethylated).
Reported denominator **53**; stored row is the last subgroup (MGMT unmethylated), `evaluable_n: 26`.
The same outcome measure also shows the **within-class** collision: the category `CR+PR` matches the
`CR` regex (`^CR\b`), so a combined-response cell overwrites the complete-response cell.

**The remaining eight cross-class rows**, all `unsupported`: NCT02150967 OG000 (line-of-therapy
classes; 55 vs 59), NCT02440464 OG000 and OG001 twice each (baseline-response classes 5 vs 21 and
3 vs 22; repeated 18-month / 24-month timepoint classes 2 vs 21 and 2 vs 22), NCT02212015 OG000
twice (cutaneous/visceral 7 vs 26; primary/secondary 12 vs 26), NCT04208958 OG000 (tumour-type
classes CRC / Melanoma / Gastric, 19 vs 54).

### 5.3 Within-class collisions (51 rows, 19 of them the `ambiguous` set)

Distinct reported categories collapse onto one stored label: `Complete remission` vs
`Complete remission unconfirmed` (NCT01403948), `Complete remission` vs `Complete remission with
incomplete count recovery` (NCT01296932), `SD` vs `SD/ PR` (NCT00942162), `Stable disease ≥ 6 months`
vs `< 6 months` (NCT02431260), `PD as per tumour assessment` vs `PD as per clinical criteria`
(NCT02829723), `CR` vs `CR with partial / incomplete haematological recovery` (NCT03671564). A stored
`cells.CR` therefore does not identify which reported category it is.

## 6 · Row tables (the mapping table)

Per-era shard tables, one row per derived count, 30 columns carrying study, outcome measure and
index, outcome type, param type, unit, time frame, population description, group id and title,
class count, contributing class indices and titles, the four cells, `evaluable_n`, the **reported
denominator**, the all-category class total, the signed difference, the matched and dropped category
titles, the classification with its reason, and an exact source pointer
(`<payload>.txt :: studies[nct=…] :: outcomeMeasures[i] :: groups[OGxxx]`).

| shard file (prefix `CURATION-endpoint-measurement-contract-rows-`) | rows | bytes |
|---|---|---|
| `ctg_results_bor_1999_2009.tsv` | 49 | 31,043 |
| `ctg_results_bor_2010_2013.tsv` | 81 | 55,374 |
| `ctg_results_bor_2014_2017.tsv` | 283 | 221,163 |
| `ctg_results_bor_2018_2021.tsv` | 130 | 85,431 |
| `ctg_results_bor_2022_2026.tsv` | 3 | 2,097 |
| `ctg_placebo_onc_2010_2013.tsv` | 4 | 3,415 |
| `ctg_placebo_onc_2014_2017.tsv` | 2 | 1,544 |
| **total** | **552** | **400,067** |

Counts and shard sizes are also machine-readable in
`CURATION-endpoint-measurement-contract-summary.json`.

## 7 · Minimal proposed extraction contract

What a correct extraction must **bind** — proposed, not adopted; adopting it is a separate authorised
act, and it does not by itself satisfy the reopening condition.

1. **The denominator is read, never computed.** A row's denominator is `denoms[units ==
   "Participants"].counts[groupId].value` from the same outcome measure, stored verbatim with its
   units. `sum(cells)` may be stored **only** as a separate field with a separate name, and a row
   whose cells sum to something other than the reported denominator is a **recorded discrepancy**,
   never a denominator.
2. **Every stored count binds a six-tuple**: `(nctId, outcomeMeasure index + title, groupId + group
   title, class index + class title, category title, timeFrame)`. A count that cannot name all six is
   not stored.
3. **No key may be written twice.** Assignment to an existing `(group, class, category)` slot is an
   error that fails the row, not a silent overwrite. Category-title matching must be exact against a
   declared vocabulary, not a prefix regex: `CR+PR`, `CRi`, `CRh`, `sCR`, `VGPR`, `SD/ PR`,
   `SD ≥ 6 months` are distinct reported categories and must map to distinct stored fields or to
   nothing.
4. **One class per row.** A row's cells come from exactly one class. Multi-class outcome measures are
   either emitted as one row per class, each carrying its class title and its own denominator, or
   refused — never merged, and never reduced to the last class.
5. **The residual is retained.** All non-matched categories of the contributing class are stored with
   their titles and values, so `reported denominator − matched cells` is explicit rather than
   invisible.
6. **The analysis population is carried, not inferred**: `populationDescription`, `timeFrame`,
   outcome `type` and `paramType` travel with the row; a rate must name which of them its denominator
   belongs to.
7. **Unresolved stays unresolved.** No absent reading may be stored as a reading of absence — the
   existing `UNRESOLVED` / `NOT_STATED_IN_REGISTRY` discipline extended to denominators and classes.
8. **A selection rule, reviewed before extraction**, states which outcome measure and which class of
   a trial is eligible, so that an arm reported several times is selected rather than de-duplicated
   by an incidental key. (Identity and repeated assessment are Job 2's question; this contract only
   requires that the rule exist and be applied at extraction.)

## 8 · What this establishes, and what it does not

**Establishes**, from the raw records only:

- The reported denominator exists in **all 552** source records and was **not** read by the producer.
- In **299** rows the derived `evaluable_n` is **not** the reported denominator, always smaller
  (median 3, max 112) — root's F1 first part is confirmed on the raw source, not merely in the code.
- In **10** rows a category value was **overwritten across source classes** and the stored row is one
  stratum, subgroup, therapy line, timepoint or tumour type of the arm; in **51** rows a value was
  overwritten within a class by a colliding category title; **22** of these overwrites changed the
  value. F1's second part is confirmed with named exhibits.
- **233** mappings are confirmed by an independently reported denominator in the same record.

**Does not establish:**

- It does **not** validate the 233 `valid` rows as units of analysis. A matching denominator says
  nothing about arm identity, repeated or duplicated assessments, or overlap (Job 2), nor about
  arm-level disease, phase or control status (Job 3).
- It does **not** recompute any manuscript quantity, propose a corrected rate, or estimate how the
  paper's numbers would change. No such recomputation is authorised here and none was performed.
- It does **not** satisfy the reopening condition. Route 1 additionally requires a **reviewed
  selection rule** and outputs recomputed on validated evidence; this document supplies only the
  source-validation half, for group / class / reported denominator / time frame / unit.
- It asserts nothing about EMC efficacy, safety, selectivity or clinical readiness, and no causal,
  cause-fraction, capacity or treatment-efficacy claim follows from it.
- It is a reading of what trials **reported**. It is not patient-level data and re-analyses no
  patient.

## 9 · Reproduction

The replay and emit scripts are working files, not committed producers; they read only the delivered
cache copy and write only files under this document's own prefix. Nothing was committed or pushed,
no manuscript, producer or frozen artifact was edited, and no test suite was run. The only commands
whose exit codes are claimed here are `sha256sum -c` (exit 0) and the two read-only Python passes
(exit 0 each).
