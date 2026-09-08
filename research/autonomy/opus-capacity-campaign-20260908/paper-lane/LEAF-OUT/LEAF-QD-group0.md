---
id: DOC-OPUS-CAMPAIGN-LEAF-QD-GROUP0
title: "QUESTION D, group 0 — is the results-group ↔ registered-arm join actually unrecoverable?"
level: L4
kind: memo
status: live
purpose: >
  Test, per trial, whether the 84 results groups of 16 assigned NCTs whose arm_match_quality is
  NONE, CONTAINMENT or AMBIGUOUS_MULTI are genuinely unjoinable to a registered arm, or merely
  unmatched by the one string-matching method Job 3 used.
scope: >
  L4. Source-validation evidence only, for 16 named NCTs. Computes no rate, no response fraction
  and no capacity figure. Asserts nothing about efficacy, safety, selectivity or clinical
  readiness. The endpoint and mortality manuscripts stay PARKED; nothing here corrects a paper.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# QD group 0 — recoverability of the results-group ↔ registered-arm join

## What was read

The delivered immutable cache copy at
`/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
(cache revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`, 12 payloads, 157,268,733 payload bytes).
**`sha256sum -c SHA256-MANIFEST.txt` → all 13 files `OK`, exit code `0`.**
**No network request of any kind was made.** No producer, build, test, gate or preflight was run.
Nothing tracked was edited or committed.

Job 3's `CURATION-endpoint-arm-attribution-map.tsv` was read **only** to select my rows and to quote
each row's own `arm_match_quality`, `registry_arm_label/type` and `control_status`. Job 3's matcher
was not modified and not re-run, and its global counts are not restated as findings here. Disease
attribution is Job 3's and is untouched.

## Coverage — groups reached versus assigned

| | |
|---|---|
| NCTs assigned (`LEAF-ASSIGNMENTS/QD-group0.txt`) | 16 |
| NCTs located in the cache | **16 / 16** |
| Map rows for those NCTs (all qualities) | 88 |
| Rows in scope (`NONE` / `CONTAINMENT` / `AMBIGUOUS_MULTI`) | **84** |
| Rows whose `(om_title, group_title)` was re-located in the cached record | **84 / 84** |
| Rows unreached | 0 |

In-scope rows by Job 3 quality: `NONE` 70, `CONTAINMENT` 14, `AMBIGUOUS_MULTI` 0. Per-row evidence
is in `LEAF-QD-group0.tsv`; every row carries `payload | payload_line | NCT | outcomeMeasures[i] |
group OGnnn`.

## Result

| class | rows | trials |
|---|---|---|
| `JOIN_RECOVERABLE` | **82** | 15 |
| `GENUINELY_UNJOINABLE` | **2** | 1 (NCT00389805) |
| `UNRESOLVED` | 0 | — |

**Job 3's "unreachable by a defensible match" verdict does not survive for 82 of my 84 rows.** The
join failed because the matcher compared the results-group title to the arm **label** only. In this
group of 16 trials the arm identity is carried instead by `armGroups[].description`,
`armGroups[].interventionNames`, or by `armGroups` cardinality.

Two tiers, because they are not equally strong:

- **Tier A — discriminating join inside a multi-arm trial (38 rows, 7 trials).** A specific
  registered arm is named, and the record distinguishes it from the trial's other arms.
  NCT00301067 (1), NCT00600340 (8), NCT00876993 (5), NCT01327612 (7), NCT01648764 (14),
  NCT01790503 (1), NCT01796171 (2).
- **Tier B — single registered arm, arm type determinate by cardinality (44 rows, 8 trials).**
  The trial registers exactly one `armGroup`, so the only `armGroupType` available to any results
  group is that one; six of the eight also carry a positive description/intervention corroboration.
  NCT00654238 (1), NCT00836888 (4), NCT00946153 (4), NCT01124734 (2), NCT01296932 (9),
  NCT01325207 (2), NCT01403948 (20), NCT01562028 (2). Tier B recovers the arm **type**, not a
  dose-level or subgroup identity the registry never registered.

Recovered `armGroupType`: `EXPERIMENTAL` 74 rows, `ACTIVE_COMPARATOR` 8 rows, none 2 rows.

Against Job 3's own control status for the same rows: 33 rows Job 3 left `UNKNOWN` and 14 rows it
left `UNKNOWN_WEAK_MATCH_ONLY` — **47 rows — now have a named registered arm and its type.**

⛔ Recovering an arm type does not manufacture a denominator. Where a row's control status was
`UNKNOWN` it was **not** read as `NOT_CONTROL`; it is replaced only by what the recovered
`armGroupType` itself states, and the two rows that stay unjoinable stay `UNKNOWN`.

## Trial by trial

Source pointers below are `payload file : line | outcomeMeasures[index] | group id`. All lines are
in `ctg_results_bor_1999_2009.txt` or `ctg_results_bor_2010_2013.txt` as named.

### NCT00600340 — the clearest refutation (8 rows)
`ctg_results_bor_1999_2009.txt:638`, `outcomeMeasures[3..6]`, groups `OG000`/`OG001`.

| results-group title | registered arm label | `armGroups[].description` | `armGroupType` |
|---|---|---|---|
| `Bevacizumab Plus Paclitaxel` | `A Bev+Pac` | `Bevacizumab plus Paclitaxel` | `ACTIVE_COMPARATOR` |
| `Bevacizumab Plus Capecitabine` | `B Bev+Cap` | `Bevacizumab plus Capecitabine` | `ACTIVE_COMPARATOR` |

**Field used: `armGroups[i].description`.** The group title is a **case-insensitive exact match** to
the arm description (`"Bevacizumab Plus Paclitaxel".casefold() == "Bevacizumab plus Paclitaxel".casefold()`),
corroborated by `interventionNames` (`Biological: Bevacizumab and Paclitaxel` /
`... and Capecitabine`). The label `A Bev+Pac` is an abbreviation, which is why a title-to-label
matcher returned `NONE`. `JOIN_RECOVERABLE` for all 8 rows.

**Control status implied:** both arms are registered `ACTIVE_COMPARATOR` in a `RANDOMIZED`,
`PARALLEL` trial — i.e. each is the other's *active* comparator. This is a registered comparator
arm type; it is **not** a placebo or untreated control, and it does not license treating either arm
as an untreated denominator. Job 3 had `UNKNOWN` for all 8; this resolves them. These are the only
non-`EXPERIMENTAL` arm types in my 16 trials.

### NCT01648764 — 14 rows, `Arm A` / `Arm B` recovered
`ctg_results_bor_1999_2009.txt:140`, `outcomeMeasures[5]`, `OG000`–`OG013`.
Arms: `LY2334737 - Arm A` (every other day × 21 d, then 7 d off) and `LY2334737 - Arm B`
(daily × 7 d, then 7 d off, repeated), both `EXPERIMENTAL`. Every group title carries the token
`Arm A` or `Arm B` (e.g. `70 mg LY - Arm B Dose Escalation`) **and** each group description
reproduces that arm's schedule sentence verbatim. **Fields: `armGroups[i].label` token +
`armGroups[i].description`.** 8 rows → Arm A, 6 rows → Arm B. All `EXPERIMENTAL` → not a control
arm. Job 3 had `UNKNOWN` for all 14.

### NCT01327612 — 7 rows, parent-protocol prefixes defeated the matcher
`ctg_results_bor_2010_2013.txt:102`, `outcomeMeasures[5]`, `OG000`–`OG006`. Four `EXPERIMENTAL`
arms. Group titles are prefixed with the parent study number, which is why label matching failed.
**Field: `armGroups[i].interventionNames` (drug set) plus the arm description's dosing interval.**

| group | recovered arm | `armGroupType` |
|---|---|---|
| `20050118: Ganitumab 20 mg/kg` (Q4W) | `Ganitumab Monotherapy` (`Q3W or Q4W`) | EXPERIMENTAL |
| `20050171: Conatumumab 0.45 mg/kg` (Q2W) | `Conatumumab Monotherapy` (`Q2W or Q3W`) | EXPERIMENTAL |
| `20060295: Conatumumab 3 mg/kg` (Q3W) | `Conatumumab Monotherapy` | EXPERIMENTAL |
| `20060340: Conatumumab 5 mg/kg` (Q3W) | `Conatumumab Monotherapy` | EXPERIMENTAL |
| `20060464: Conatumumab 10 mg/kg + mFOLFOX6 ± Bevacizumab` | `Conatumumab + mFOLFOX6 ± Bevacizumab` | EXPERIMENTAL |
| `20060464: Conatumumab 2 mg/kg + mFOLFOX6 + Bevacizumab` | `Conatumumab + mFOLFOX6 ± Bevacizumab` | EXPERIMENTAL |
| `20070411: Conatumumab 15 mg/kg + Ganitumab 18 mg/kg` | `Conatumumab + Ganitumab` | EXPERIMENTAL |

Two of these group titles literally contain the whole arm label. Job 3 had `UNKNOWN` for all 7.

### NCT00876993 — 5 rows, dose equality confirms the containment Job 3 rated weak
`ctg_results_bor_1999_2009.txt:38`, `outcomeMeasures[1]`, `OG000`–`OG004`. Five `EXPERIMENTAL` arms
`Dose Level 0`–`Dose Level 4`. Each group title ends in the **verbatim full arm label**, and the
group description's temozolomide dose equals that arm's description dose independently:
`Cohort 2 - Dose Level 0` → 75 mg/m²; `Cohort 1/3/5 - Dose Level 1` → 125 mg/m²;
`Cohort 4 - Dose Level 2` → 175 mg/m². **Fields: `armGroups[i].label` + `armGroups[i].description`.**
Job 3 had `UNKNOWN_WEAK_MATCH_ONLY`; the dose equality is a second, independent field, so the match
is not "substring only". Registered arms `Dose Level 3` and `Dose Level 4` have no results group —
that is an unfilled arm, not a failed join.

### NCT01796171 — 2 rows, resolved by the record's own naming convention
`ctg_results_bor_2010_2013.txt:135`, `outcomeMeasures[1]` (`Part A, Phase IIa`), `OG000`/`OG001`.
13 registered arms, **all `EXPERIMENTAL`**.
- `40/15 With FL` (desc: 15 MBq/kg Betalutin + 40 mg lilotomab) → `Part A, Arm 1: 15 MBq/kg Betalutin with lower dose lilotomab pre-dosing`, `EXPERIMENTAL`.
- `100/20 With FL` (desc: 20 MBq/kg Betalutin + 100 mg/m² lilotomab) → `Part A, Arm 4: 20 MBq/kg Betalutin with higher dose lilotomab pre-dosing`, `EXPERIMENTAL`.

**Fields: `om_title` (`Part A, …`) + `armGroups[i].description` dose pair.** The
`<lilotomab>/<Betalutin>` title convention is asserted by the record itself: `outcomeMeasures[2]`
group `40/12.5 in Part B` corresponds to `armGroups[11]` `Part B, Arm 3: 12.5 MBq/kg Betalutin with
lower dose lilotomab pre-dosing`. Each dose pair is unique within Part A. Even if the Part-A
restriction were rejected, the arm **type** is unchanged, because all 13 registered arms are
`EXPERIMENTAL`. Job 3 had `UNKNOWN` for both.

### NCT00301067 and NCT01790503 — pooled groups, arm type still determinate
- **NCT00301067** (`…1999_2009.txt:192`, `outcomeMeasures[2]`, `OG000`). Group
  `Temozolomide and Calcitriol (Cohort 1-3+Expansion)` enumerates the four registered arm labels
  (`Cohort 1/2/3 - …`, `Expansion - …`) in its own title, and its calcitriol dose set
  {0.2, 0.3, 0.5 mcg/kg} is the union of the four arm descriptions' doses. Many-to-one pooled join;
  all four arms `EXPERIMENTAL`. **Fields: `group_title` + `armGroups[].description`.** Job 3: `UNKNOWN`.
- **NCT01790503** (`…2010_2013.txt:404`, `outcomeMeasures[6]`, `OG000`). Group
  `Combined 800 mg, 5 Days/Week`, description `All participants in Phase 1b or 2 who received
  800 mg/day PLX3397 (5 days/week) during combination therapy` — that names exactly the two arms
  whose descriptions carry 800 mg/day: `Phase 1b dose escalation - 800mg/day PLX3397` and
  `Phase 2 - Recommended phase 2 dose of PLX3397` (`800mg/day`). Both `EXPERIMENTAL`; all four
  registered arms are `EXPERIMENTAL`. **Field: `group_description` + `armGroups[].description`.**
  Job 3: `UNKNOWN`. The `5 days/week` qualifier is *not* in `armGroups`; it does not affect arm
  identity or type.

### Tier B — single-arm trials (44 rows)
In each of these the trial registers exactly one `armGroup`, so the arm type is determinate; the
results groups are dose levels, ethnic strata, treatment periods or biomarker subgroups that the
registry never registered as arms.

| NCT | rows | single registered arm (type) | corroborating field beyond cardinality | pointer |
|---|---|---|---|---|
| NCT00654238 | 1 | `1` (EXPERIMENTAL) | arm description `This is a single arm study.` is the verbatim opening of the group description; `interventionNames` `Drug: sorafenib` = group title `Sorafenib` | `…1999_2009.txt:134` `OM[0]` `OG000` |
| NCT00836888 | 4 | `Cohort` (EXPERIMENTAL) | `interventionNames` `Biological: ONO-4538`; arm description is `null` | `…1999_2009.txt:612` `OM[4]` `OG000`–`OG003` |
| NCT00946153 | 4 | `Lenvatinib` (EXPERIMENTAL) | `interventionNames` `Drug: Lenvatinib`; arm description is `null` | `…1999_2009.txt:256` `OM[2]` `OG000`–`OG003` |
| NCT01124734 | 2 | `Course 1 Cycle 1 and Cycle 2` (EXPERIMENTAL) | the arm description **enumerates both group titles verbatim** as its two labelled sub-cycles, with matching regimens | `…2010_2013.txt:257` `OM[0]` `OG000`/`OG001` |
| NCT01296932 | 9 | `Patients with relapsed CLL` (EXPERIMENTAL) | `interventionNames` `Drug: BI 836826` = every group title's drug | `…2010_2013.txt:174` `OM[4]` `OG000`–`OG008` |
| NCT01325207 | 2 | `intravenous trastuzumab infusions` (EXPERIMENTAL) | **none — see caveat** | `…2010_2013.txt:163` `OM[1]` `OG000`/`OG001` |
| NCT01403948 | 20 | `Patients with relapsed or refractory NHL` (EXPERIMENTAL) | the arm description's population phrase `relapsed or refractory non-Hodgkin lymphoma of B cell origin` recurs verbatim (casefold) in all 10 group descriptions; `interventionNames` `Drug: BI 836826` | `…2010_2013.txt:44` `OM[3]`,`OM[4]` `OG000`–`OG009` |
| NCT01562028 | 2 | `Erlotinib plus bevacizumab` (EXPERIMENTAL) | the arm description's regimen (erlotinib 150 mg p.o. daily; bevacizumab 15 mg/kg i.v. day 1 of each 3-week cycle) is reproduced in both group descriptions; `T790M Positive`/`Negative` are biomarker subgroups, not arms | `…2010_2013.txt:367` `OM[3]` `OG000`/`OG001` |

**Caveat, NCT01325207.** The single registered arm is labelled and described as **intravenous**
trastuzumab, while both results groups describe **intrathecal** administration (`Treatment With
Trastuzumab`, `Cohort 5 + Phase II - Intrathecal Trastuzumab- 80 mg`), and `interventionNames` is
`Radiation: Trastuzumab`. The arm **type** is determinate by cardinality (`EXPERIMENTAL`), but the
arm's own text is internally inconsistent with the trial's results and must not be used as
group-level evidence. Recorded in the TSV `note` column.

### NCT00389805 — `GENUINELY_UNJOINABLE` (2 rows), and one flagged basis
`ctg_results_bor_1999_2009.txt:206`, `outcomeMeasures[6]`, groups `OG000` (`Arm A`) and `OG001`
(`Arm B`).

**What is specifically missing:** `protocolSection.armsInterventionsModule` is the **empty object
`{}`** in this record — there is no `armGroups` array, no arm label, no `armGroupType`. Nothing
exists to join to, by any field. `flowGroups` cannot help either (see limits below). Job 3's verdict
is **confirmed** for these two rows, and their control status stays `UNKNOWN` here.

⚠️ **Flag (basis, not arm type).** Job 3 recorded `control_status = NOT_CONTROL_SINGLE_ARM_TRIAL`
for both rows with `control_basis = "trial registers 0 arm group(s)"`. Zero registered arms is the
**absence** of arm registration, not evidence that the trial had one arm; and this record reports
**two** distinct results groups with different regimens — `Arm A` (pemetrexed d1 + bortezomib
d1, 4, 8, 11 q21d) versus `Arm B` (pemetrexed d1 + bortezomib d1, 8 q21d). The trial's
`designModule` does say `interventionModel: SINGLE_GROUP`, but that trial-level label conflicts with
its own two-group results section. I do not re-assign these rows; I record that the stated basis
does not support the assigned value. This is the parent's to adjudicate.

⚠️ **Second flag (internal inconsistency, NCT01124734).** Job 3 gave the two rows of this one
single-arm trial **different** control statuses — `OG000` got `UNKNOWN_WEAK_MATCH_ONLY` (its title
`Course 1 Cycle 1` is a substring of the arm label) and `OG001` got `NOT_CONTROL_SINGLE_ARM_TRIAL`
(`Course 1 Cycle 2` is not) — although both are periods of the same single registered arm. The
divergence is an artifact of substring matching, not a property of the record.

## Contradictions with Job 3's assigned control status

No row in my group produces a recovered arm type that contradicts a `NOT_CONTROL` assignment: the
74 rows whose type resolves to `EXPERIMENTAL` are consistent with not being a control arm, and the
35 `NOT_CONTROL_SINGLE_ARM_TRIAL` rows I could join all resolve to `EXPERIMENTAL`. The two items
above are flags on the **basis** and on internal consistency, not on the arm type. The one
substantive change is NCT00600340: 8 rows move from `UNKNOWN` to a registered `ACTIVE_COMPARATOR`
arm type.

## Limits of this leaf

- **`flowGroups` was not usable.** The cached payloads were fetched with
  `fields=…,resultsSection.outcomeMeasuresModule` only; `resultsSection.participantFlowModule` is
  absent from all 16 records (verified by listing `resultsSection` keys). Every join above therefore
  rests on `armGroups` and `outcomeMeasuresModule` alone. A record with `flowGroups` might join more,
  or might join NCT00389805 — untestable from this cache, and no network request was made.
- Tier B recovers the registered arm **type**, not a one-to-one identity the registry never
  recorded. A single-arm trial's dose cohorts are not separately registered arms, and this leaf does
  not invent them.
- `armGroupType` is what the sponsor registered. It is a registry attribute, not an adjudication of
  what the group functioned as in analysis.
- Nothing here bears on disease attribution, phase, evaluable counts, response rates, efficacy,
  safety, selectivity or clinical readiness, and nothing here reopens a manuscript.

## Files

- `LEAF-OUT/LEAF-QD-group0.md` — this memo.
- `LEAF-OUT/LEAF-QD-group0.tsv` — 84 rows, one per in-scope group, 21 columns, each with
  `payload | payload_line | outcomeMeasures[i] | group id`, Job 3's own values for the same row, the
  recovered arm, the field that establishes it, the class and the implied control status.
