---
id: DOC-OPUS-CAMPAIGN-LEAF-QD-GROUP1
title: "QUESTION D / group 1 — is the results-group ↔ registered-arm join actually unrecoverable?"
level: L4
kind: memo
status: live
purpose: >
  Test, per trial and per group, whether Job 3's `arm_match_quality = NONE / CONTAINMENT /
  AMBIGUOUS_MULTI` verdicts mean the registry arm is genuinely unreachable, or only that one
  string-matching method did not reach it.
scope: >
  L4. Leaf worker output for the 16 NCTs in `LEAF-ASSIGNMENTS/QD-group1.txt` only. It computes no
  response rate, no effect estimate and no capacity figure; it repairs no manuscript and authorises
  no publication act. The endpoint manuscript stays parked.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
related: [DOC-OPUS-CAMPAIGN-CURATION-ARM-ATTRIBUTION]
---

# QUESTION D, group 1 — the join is recoverable for 51 of 52 groups

## What was read

Only the delivered immutable cache copy at
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
(cache revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`), plus the existing
`CURATION-endpoint-arm-attribution-map.tsv` for the rows already assigned to my 16 NCTs.

- `sha256sum -c SHA256-MANIFEST.txt` → all 13 entries `OK`, **exit code 0**.
- **No network request of any kind was made.** No producer, gate, preflight or test suite was run.
  Job 3's matcher was not modified and not re-run; its global counts are not restated as findings.

## Coverage — reached versus assigned

| | count |
|---|---|
| NCTs assigned (`LEAF-ASSIGNMENTS/QD-group1.txt`) | 16 |
| NCTs located in the cache | **16** (100%) |
| Map rows for my NCTs with `arm_match_quality` in {NONE, CONTAINMENT, AMBIGUOUS_MULTI} | **60** |
| Rows adjudicated | **60** (100%) |
| Distinct `(NCT, results-group title)` groups behind those rows | **52** |

The 60 rows collapse to 52 distinct groups because three trials report the same groups under more
than one outcome measure (`NCT02421588` 2 groups × 3 outcome measures; `NCT02475213` 4 groups × 2;
`NCT02259582` counted once — its record appears in two payloads, verified byte-identical after JSON
normalisation, see "Duplicate payload" below).

Every trial in my group is in `ctg_results_bor_2010_2013.txt` or `ctg_results_bor_2014_2017.txt`;
the exact payload file and line number for each is in column `source_payload` / `source_line` of
`LEAF-QD-group1.tsv`, and `om_index` / `group_index` / `group_id` give the position inside
`resultsSection.outcomeMeasuresModule.outcomeMeasures[]`.

## Headline result

**Job 3's "the registry arm type is unreachable by a defensible match" does not hold for my group.**

| verdict | groups | rows |
|---|---|---|
| `JOIN_RECOVERABLE` | **51 / 52** | 59 / 60 |
| `GENUINELY_UNJOINABLE` | **1 / 52** | 1 / 60 |
| `UNRESOLVED` | 0 | 0 |

This is a statement about **these 16 trials only**. It is not a projection onto the rest of the
corpus, and it does not license re-deriving any other lane's rows.

## Why the matcher missed them — five recovery fields, none of them a title match

Job 3's matcher compared the results-group **title** with the registered arm **label**. Every
recovery below uses a field that matcher did not consult. The field actually used for each group is
in column `field_used`; the counts are groups, not rows.

| # | recovery field | groups | why the title match failed |
|---|---|---|---|
| 1 | **cardinality** — `n_arms_registered = 1`, so every results group is necessarily inside the sole registered arm; corroborated in each case by `interventionNames` or the arm `description` | 18 | the sole arm is named for the drug ("Single-arm", "Treatment (pegylated irinotecan NKTR 102)") while the groups are named for dose levels, disease cohorts or trial parts |
| 2 | **per-arm `interventionNames`** | 15 | the arm label is contentless ("Arm A", "Arm B", "Experimental Arm", "Control Arm 1/2") and carries no drug name at all |
| 3 | **arm `label` / `description` matched against the group `description` or a drug token in the group title**, sometimes verbatim | 11 | the group description embeds the arm text but the titles are respelled ("MYL-1401O Trastuzumab + Taxane" vs registered "MYL- 1401O + Taxane") |
| 4 | **an ordinal arm token the record itself asserts** — group titles ending "(Arm 1)", "(Arm 2)", "(Arm 3)" against arm labels beginning "Arm 1", "Arm 2", "Arm 3" | 3 | the rest of each label is a regimen abbreviation the group title does not repeat |
| 5 | **the registered label spelled out where the group uses an acronym** ("Non-small Cell Cancer (NSCLC) Cohort" ↔ "NSCLC Cohort: …") | 4 | the group appends a prior-therapy split ("PD1/PDL1 Naïve" / "Experienced") that no registered arm carries |
| — | not recoverable | 1 | — |

Two extra observations that make the arm **type** reachable even where arm identity is one-to-many:

- **Uniform-type trials.** In `NCT02475213` all 8 registered arms are `EXPERIMENTAL`, and in
  `NCT02383927`, `NCT02509507` and `NCT01859741` all registered arms are `EXPERIMENTAL`. For any
  group that belongs to *some* registered arm of such a trial, `armGroupType` is determined without
  resolving which arm it is.
- **Pooled-arm groups.** `NCT02566993` reports one control results group against **two** registered
  arms (`Control Arm 1` = CAV, `Control Arm 2` = topotecan). The identity is 1:N, but both arms are
  `ACTIVE_COMPARATOR`, so the type is still unambiguous.

## ⛔ `flowGroups` was not available and was not used

The cache payloads were fetched with an explicit `fields=` list —
`protocolSection.identificationModule.nctId,protocolSection.conditionsModule,protocolSection.designModule,protocolSection.armsInterventionsModule.armGroups,resultsSection.outcomeMeasuresModule`
(SOURCE URL header line 1 of each `ctg_results_bor_*.txt`). `resultsSection.participantFlowModule`
is therefore **absent from every cached record**, confirmed by inspection: the only key under
`resultsSection` in all 16 records is `outcomeMeasuresModule`. **No finding here rests on
`flowGroups`, and none could.** A future re-fetch that includes `participantFlowModule` could only
add joins, not remove any established below.

## The one genuinely unjoinable group

**`NCT02383927` — results group `Cohort 3`**
(`ctg_results_bor_2014_2017.txt` line 506; outcome measure index 5, group index 3, `id=OG003`).

The registry registers exactly **two** arm groups: `Cohort 1` (description "Thyroid Cancer") and
`Cohort 2` (description "Squamous Head and Neck Cancer"), both `EXPERIMENTAL`. The results section
reports a **Cohort 3** — group description "Subjects with any SCC (excluding HNSCC) with HRAS
mutation" — that has **no counterpart in `armGroupType`, `armGroups[].label`,
`armGroups[].description` or `armGroups[].interventionNames`**, and no ordinal, flow or descriptive
field in the cached record asserts a mapping for it. What is specifically missing: the arms module
was never updated to register the third cohort. Job 3's `NONE` verdict is **confirmed** for this
group.

Its control status stays **`UNKNOWN`**. ⛔ That `UNKNOWN` is not `NOT_CONTROL` and must not be used
as, or counted into, a denominator.

## Control status implied by the recovered joins

Reading the recovered `armGroupType` back onto the 60 rows:

| recovered `armGroupType` | Job 3 `control_status` on the same row | rows |
|---|---|---|
| `EXPERIMENTAL` | `NOT_CONTROL_SINGLE_ARM_TRIAL` | 18 |
| `EXPERIMENTAL` | `UNKNOWN` | 30 |
| `EXPERIMENTAL` | `UNKNOWN_WEAK_MATCH_ONLY` | 2 |
| `EXPERIMENTAL` | `CONTROL_PLACEBO_BY_GROUP_TEXT` | 1 |
| `ACTIVE_COMPARATOR` | `CONTROL_UNSPECIFIED_BY_GROUP_TEXT` | 4 |
| `ACTIVE_COMPARATOR` | `UNKNOWN` | 2 |
| `ACTIVE_COMPARATOR` | `UNKNOWN_AMBIGUOUS_SEQUENCE_LABEL` | 1 |
| `PLACEBO_COMPARATOR` | `UNKNOWN_AMBIGUOUS_SEQUENCE_LABEL` | 1 |
| — (unjoinable) | `UNKNOWN` | 1 |

Of the **37 rows** Job 3 left in the UNKNOWN family (`UNKNOWN`, `UNKNOWN_WEAK_MATCH_ONLY`,
`UNKNOWN_AMBIGUOUS_SEQUENCE_LABEL`), **36 now carry a registered `armGroupType`** taken from a named
field of the record. That is a change in what the source supports, and it is reported here for the
parent to adjudicate — **this leaf does not rewrite the map.**

### The one previously unidentified control arm

**`NCT02578641`, group `Chemo Only`** (`ctg_results_bor_2014_2017.txt` line 119; OM index 4, group
index 1, `id=OG001`) joins to `armGroups[1]` = `Arm B`, **`armGroupType = ACTIVE_COMPARATOR`**, via
`interventionNames = ["Drug: combination IV gemcitabine and IV carboplatin (AUC2)"]` and
`description` "6 cycles of combination IV gemcitabine (1000 mg/m2) and IV carboplatin (AUC2)". The
group description is exactly "gemcitabine+carboplatin", with no EBV-CTL — which is precisely what
separates it from `Arm A`. Job 3 recorded `control_status = UNKNOWN` for this row. **This is a
registered active-comparator control group that Job 3 did not identify.**

### Contradictions and cautions to flag to the parent

1. **`NCT01859741`, group `P2: Placebo + CIS or CARB`** (line 162; OM 3, group 0, `OG000`) — Job 3
   assigned `CONTROL_PLACEBO_BY_GROUP_TEXT`. The join recovers `armGroups[1]` = "Etoposide and
   Cisplatin plus Placebo", whose **`armGroupType` is `EXPERIMENTAL`, not `PLACEBO_COMPARATOR`**,
   and the map's `registry_has_control_arm` for this trial is `False`. Job 3's control call is
   supported by the group text and by the recovered arm *label*, but the registry's **arm typing
   does not corroborate it**. Anyone deriving control status from `armGroupType` alone would flip
   this row; anyone deriving it from group text alone would keep it. Both facts belong on the row.

2. **`NCT02259582`, group `Demcizumab/Placebo Arm (Arm 2)`** (`ctg_placebo_onc_2014_2017.txt`
   line 62 / `ctg_results_bor_2014_2017.txt` line 108; OM 0, group 1, `OG001`) — the join to
   `armGroups[1]` = "Arm 2 Pem, carbo x 4 cycles, one course of dem" (`ACTIVE_COMPARATOR`)
   **vindicates Job 3's refusal** to read the trailing "/Placebo" as a placebo control: the
   "/Placebo" denotes the maintenance phase. The registered placebo control of this trial is
   `armGroups[0]` = "Arm 1 Pem, carbo, placebo x 4 cycles", `PLACEBO_COMPARATOR`, which the join
   assigns to group `Placebo/Placebo Arm (Arm 1)`.

3. **`NCT02259582`, group `Demcizumab/Demcizumab Arm (Arm 3)`** — registry-typing caveat, not a
   contradiction: `armGroups[2]` is typed **`ACTIVE_COMPARATOR`** even though that arm receives the
   investigational agent demcizumab in both phases. `armGroupType = ACTIVE_COMPARATOR` therefore
   cannot be read as "this group is the trial's control" without checking the arm content.

## Duplicate payload

`NCT02259582` appears twice in the cache — `ctg_placebo_onc_2014_2017.txt` line 62 and
`ctg_results_bor_2014_2017.txt` line 108. The two study objects are **byte-identical after
key-sorted JSON normalisation** (verified). The TSV cites the `ctg_placebo_onc_2014_2017.txt`
occurrence. No other NCT in my group is duplicated. Cross-shard duplicate reconciliation is the
parent's and was not attempted.

## Limits of this leaf

- These findings are about the **join**, not about disease attribution — no disease inference was
  made (that is Job 3's).
- "Not a registered comparator" is a statement that the **matched arm's `armGroupType` is
  `EXPERIMENTAL`**. It is a positive registry fact, not a re-reading of an `UNKNOWN`. Where no arm
  was matched (`NCT02383927 Cohort 3`), the status stays `UNKNOWN` and nothing was substituted for
  it.
- Where a results group is a *subgroup* of a registered arm (dose level, disease cohort, trial part,
  prior-therapy split), the join carries the **arm's** type to the group. It does **not** make the
  subgroup a registered arm, and it does not license treating those subgroups as independent
  randomised units. Column `join_cardinality` records this for every row.
- No claim about efficacy, safety, selectivity, therapeutic window or clinical readiness is made or
  implied anywhere in this file.

## Machine-readable output

`LEAF-OUT/LEAF-QD-group1.tsv` — 60 data rows, 22 columns:
`nct`, `source_payload`, `source_line`, `om_index`, `group_index`, `group_id`, `om_title`,
`group_title`, `job3_arm_match_quality`, `job3_registry_arm_label`, `job3_registry_arm_type`,
`job3_control_status`, `n_arms_registered`, `recovered_arm_index`, `recovered_arm_label`,
`recovered_armGroupType`, `join_cardinality`, `field_used`, `evidence`, `verdict`,
`control_status_implied`, `contradiction_or_note`.
