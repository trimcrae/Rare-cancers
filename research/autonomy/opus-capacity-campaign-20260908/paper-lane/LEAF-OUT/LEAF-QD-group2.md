---
id: DOC-OPUS-CAMPAIGN-LEAF-QD-GROUP2
title: "QUESTION D / group 2 — is the results-group ↔ registered-arm join actually unrecoverable?"
level: L4
kind: memo
status: live
purpose: >
  Test, trial by trial for 16 assigned NCTs, whether the results-group to registered-arm join that
  Job 3's string matcher scored NONE / CONTAINMENT / AMBIGUOUS_MULTI is genuinely unrecoverable from
  the cached source record, or merely unmatched by that one method.
scope: >
  L4. Source-validation evidence only. Computes no rate, no response fraction, no effect estimate,
  no capacity figure. Repairs nothing, reopens nothing, authorises no publication act. Does not
  modify, re-run or replace Job 3's matcher or its map.
audience: [maintainers, external reviewers, autonomous research agents]
date: 2026-09-08
last_verified: 2026-09-08
---

# QUESTION D, group 2 — recoverability of the group↔arm join

⛔ The endpoint manuscript stays parked. Nothing here is an efficacy, safety or capacity claim.
⛔ `UNKNOWN` control status is never read as `NOT_CONTROL`. No denominator is constructed anywhere.
⛔ Disease attribution is Job 3's and is not touched here.

## Inputs and integrity

- Cache: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
  (12 payloads + `_manifest.json` + `SHA256-MANIFEST.txt`, cache revision `216bd1b5fb25a56b90ef3cc2373e1fe68322708f`).
- `sha256sum -c SHA256-MANIFEST.txt` → all 13 files `OK`, **exit code 0**.
- **No network request of any kind was made.** No producer, gate, test suite or preflight was run.
  Job 3's `CURATION-endpoint-arm-attribution-derive.py` was **read only** — not executed, not edited.
- Rows read from `CURATION-endpoint-arm-attribution-map.tsv` (Job 3's map), restricted to my 16 NCTs.

## Coverage — groups reached versus assigned

| | count |
|---|---|
| NCTs assigned (`LEAF-ASSIGNMENTS/QD-group2.txt`) | 16 |
| NCTs located in the cache | **16 of 16** |
| Job 3 map rows for those NCTs | 151 |
| Rows in scope (`arm_match_quality` ∈ {NONE, CONTAINMENT, AMBIGUOUS_MULTI}) | **144** |
| Rows examined | **144 of 144** (100%) |
| Distinct `(nct, group_title)` groups behind those rows | 105 |
| Rows out of scope (EXACT/NORMALIZED, left untouched) | 7 |

Per-row output: `LEAF-OUT/LEAF-QD-group2.tsv` (144 data rows, 21 columns). Every row carries
`nct`, `om_index`, `om_title`, `group_id`, `group_title`, `evaluable_n` as its source pointer;
recovered arms are pointed to by index into `protocolSection.armsInterventionsModule.armGroups`.

## Headline

For **my 16 trials only** — these are not global counts and must not be read as such:

| verdict | rows | distinct groups | trials |
|---|---|---|---|
| `JOIN_RECOVERABLE` | **136** | 97 | 14 |
| `UNRESOLVED` | 5 | 5 | 2 (NCT02593786 ×4, NCT03480646 ×1) |
| `GENUINELY_UNJOINABLE` | 3 | 3 | 1 (NCT02825420) |

So for these 16 trials the "registry arm type is unreachable by a defensible match" verdict does
**not** survive per-trial inspection: 136 of 144 in-scope rows have a join that a second field in
the same record establishes. The failures were failures of one label-string method, not of the
records. The one genuinely unjoinable trial fails for a hard reason (no arms registered at all),
and the 5 unresolved rows fail for a reason the record itself cannot fix.

**A vital caveat on what a recovered join buys.** In 128 of the 136 recovered rows the registered
arm type is `EXPERIMENTAL` or `OTHER`, so the join delivers `NOT_CONTROL` and no new control group.
Only 5 rows recover a registry control type (`ACTIVE_COMPARATOR`), across 4 trials. Recovering the
join therefore mostly *removes UNKNOWNs*; it does not manufacture comparators.

Implied control status over the 136 recovered rows: `NOT_CONTROL` 128, `CONTROL_ACTIVE_COMPARATOR` 5,
`UNKNOWN_ARM_TYPE_ABSENT` 2 (NCT02679170 — see below), `CONTESTED` 1 (NCT03409614 — see below).

### Which fields did the recovery work

| field that established the join | rows |
|---|---|
| `armGroups[].description` read against the results-group `description` | 68 |
| `armGroups[].label` after removing dose tokens (group title = arm label + dose) | 32 |
| bijection / complement / shared Part-Cohort prefix asserted by the record itself | 15 |
| only one arm registered in the whole record | 10 |
| `armGroups[].interventionNames` with description corroboration | 7 |
| the record's own statement that a candidate arm "was not opened for enrollment" | 2 |
| `armGroups[].label` alone (whitespace-only difference / unique token) | 2 |

(Counts are over the 136 recovered rows, classified by the leading field named in the TSV's
`join_field` column; most rows carry a second corroborating field named in the same string.)

⛔ **`flowGroups` could not be used and this is a property of the cache, not of the trials.** The
cached payloads were fetched with `fields=…,resultsSection.outcomeMeasuresModule` only. For all 16
of my trials the `resultsSection` in the cache contains **exactly one key, `outcomeMeasuresModule`**;
there is no `participantFlowModule`, hence no `flowGroups`, and no `baselineCharacteristicsModule`.
Any future recovery attempt via flow-group ids needs a re-fetch, which the fence forbids here.

---

## Trial by trial

Legend: `AG[i]` = `protocolSection.armsInterventionsModule.armGroups[i]` in the cached record.
All 16 trials are in payload `ctg_results_bor_2014_2017.txt` except NCT03455829, NCT03451825,
NCT02913430, NCT03409614, NCT03212274, which are in `ctg_results_bor_2018_2021.txt`.

### NCT02593786 — UNRESOLVED (4 rows, 4 groups)

Results groups (`om_index` 3) — 4, none of them joined:
`Cohort A: Nivolumab 3 mg/kg Q2W` (OG000), `Cohort B: Nivolumab 240 mg Q2W` (OG001),
`Cohort C: Nivolumab 360 mg Q3W` (OG002), `Cohort D: Nivolumab 480 mg Q4W` (OG003).

Registered arms — 2, **no pairing to the above is asserted anywhere in the record**:
`AG[0]` `Nivolumab monotherapy` (EXPERIMENTAL) and `AG[1]` `Cohort Expansion` (EXPERIMENTAL).

Both arms carry the **identical** description `Nivolumab specified dose on specified days` and the
identical `interventionNames` `['Drug: Nivolumab']`. Nothing in the record assigns cohort A–D to
`Nivolumab monotherapy` versus `Cohort Expansion`. Verdict `UNRESOLVED` (not "unjoinable": the arms
exist and are described, they are just not distinguishable from each other).
**Note the record still fixes the arm type without the join**: both registered arms are
`EXPERIMENTAL`, so no assignment of these groups to any registered arm could yield a control arm.
That is a statement about arm type, not a resolved join, and it is recorded separately in the TSV
note column — the `implied_control_status` for these rows stays `UNKNOWN`.

### NCT02608268 — JOIN_RECOVERABLE (30 rows, 30 groups)

Job 3: 28 NONE + 2 AMBIGUOUS_MULTI, all `control_status=UNKNOWN`.
The record's own construction: **each results-group title is a registered arm label with the dose
inserted, and each group description is the arm description with the dose inserted.** Example
(`om_index` 7, group OG027): group `Dose Ranging Part: MBG453 1200mg Q4W`, description
`Sabatolimab 1200 mg Q4W in Dose Ranging Part` ↔ `AG[7]` label `Dose Ranging Part: MBG453 Q4W`,
description `Sabatolimab Q4W in Dose Ranging Part` (EXPERIMENTAL). Stripping numeric dose tokens
from the group title yields an **exact** normalized match to exactly one arm label for 28 of 30
groups (arms 0,1,2,3,4,5,7 — mapping in the TSV).

The 2 AMBIGUOUS_MULTI rows (`Phase II: MBG453 + PDR001 NSCLC` OG028, `… Melanoma` OG029) resolve to `AG[8]`
`Phase II: MBG453 + PDR001` (EXPERIMENTAL): it is the longer of the two containment candidates, and
the competing candidate `AG[9]` `Phase II: MBG453` carries the description
**"This arm was not opened for enrollment."** — the record itself excludes it from holding
participants. All 10 registered arms of this trial are EXPERIMENTAL → implied `NOT_CONTROL`.

### NCT02679170 — JOIN_RECOVERABLE, but the arm type is absent (2 rows)

One registered arm only: `AG[0]` `Routine clinical practice group (NSCLC ALK+, ROS1)`,
`interventionNames ['Drug: Crizotinib']`. Both results groups (`ALK Treatment Sub-study` OG000,
`ROS1 Treatment Sub-study` OG001, `om_index` 8) describe crizotinib in routine clinical practice.
The join is unambiguous because there is exactly one arm.
⚠️ **`AG[0]` has no `type` key at all** — the object is exactly
`{label, description, interventionNames}` — so `armGroupType` is absent from the record. The join is
recovered; the arm type is not. `implied_control_status = UNKNOWN_ARM_TYPE_ABSENT`. Job 3's
`NOT_CONTROL_SINGLE_ARM_TRIAL` for these rows rests on the arm *count*, not on any registered type;
my recovery neither confirms nor contradicts it and does not upgrade it.

### NCT02762981 — JOIN_RECOVERABLE (2 rows)

One registered arm: `AG[0]` `Relacorilant with nab-paclitaxel` (EXPERIMENTAL), description covering
the Continuous- and Intermittent-Dosing Regimens. Groups `GR H-score Above the Overall Median`
(OG000) and `Below` (OG001) (`om_index` 7) are biomarker subgroups of Segment I + Segment II and
their descriptions restate the arm's regimens. Implied `NOT_CONTROL` — and this now rests on the
registered `armGroupType=EXPERIMENTAL`, a firmer basis than Job 3's arm-count rule.

### NCT02825420 — GENUINELY_UNJOINABLE (3 rows) ⚠️

`protocolSection.armsInterventionsModule.armGroups` is **empty — 0 registered arms**. Groups
`Prior Use of Antiangiogenics` (`om_index` 5, OG000), `No Prior Use of Antiangiogenics`
(`om_index` 5, OG001) and `Full Analysis Set` (`om_index` 4, OG000) have nothing to join to. What is specifically missing: the
record registers no arm of any kind, therefore no `armGroupType` exists anywhere in it.
Job 3's verdict is confirmed for this trial.

⚠️ **Flagged for the parent, and it is a basis problem rather than a control-status contradiction.**
Job 3 assigns these three rows `control_status = NOT_CONTROL_SINGLE_ARM_TRIAL` with
`control_basis = "trial registers 0 arm group(s)"`. Zero registered arms is *absence of arm
registration*, not evidence of a single-arm design and not evidence that no control arm existed.
Calling it `NOT_CONTROL` converts a missing field into a negative fact. The defensible value for
these rows is `UNKNOWN`. I am not editing Job 3's map; I am recording the disagreement.

### NCT02829723 — JOIN_RECOVERABLE (65 rows, 26 groups)

Exactly two registered arms, and the record states the discriminator itself:
`AG[0]` `BLZ945 single agent` — description **"BLZ945 administered as single agent"**;
`AG[1]` `BLZ945 + PDR001` — description **"BLZ945 administered in combination with PDR001"**.
Both EXPERIMENTAL. Every one of the 26 group titles names BLZ945 and either does or does not name
PDR001 (12 groups with PDR001 → `AG[1]`; 14 without → `AG[0]`). Examples, `om_index` 13:
`Phase I: BLZ945 600 mg Q1W BID` (OG012) → `AG[0]`;
`Phase I: BLZ945 800 mg Q1W BID + PDR001 400 mg Q4W` (OG024) → `AG[1]`.
Dose, schedule and phase (I/II) are sub-splits **within** the chosen arm; the same 26 groups recur
across five outcome measures (`om_index` 13 RECIST v1.1, 14 irRC, 15 RANO, 16 iRANO,
17 lymphoma guidelines), which is why 65 rows collapse to 26 groups. Implied `NOT_CONTROL` for all 65.

### NCT02895360 — JOIN_RECOVERABLE (5 rows) — Job 3's CONTAINMENT arms were right

| results group (`om_index` 6) | recovered arm | type |
|---|---|---|
| `Phase 1- in the FAP` (OG000) | `AG[0]` `Phase 1` — "Fixed 3+3 dose escalation of BAL101553 in patients with advanced solid tumors" | EXPERIMENTAL |
| `Phase 2a - Patients With Ovarian Cancer in the FAP` (OG001) | `AG[1]` `Phase 2a` — "BAL101553 at MTD in patients with…" | EXPERIMENTAL |
| `Phase 2a - Patients With Ovarian Cancer in the EEP` (OG002) | `AG[1]` | EXPERIMENTAL |
| `Phase 2a - Patients With Recurrent Glioblastoma in the FAP` (OG003) | `AG[1]` | EXPERIMENTAL |
| `Phase 2a - Patients With Recurrent Glioblastoma in the EEP` (OG004) | `AG[1]` | EXPERIMENTAL |

The group descriptions reproduce the arm descriptions (dose cohorts / MTD 70 mg/m²). FAP/EEP are
analysis populations and the tumour split is a sub-split, both **inside** the arm. Job 3 recorded
the same arms but downgraded them to `UNKNOWN_WEAK_MATCH_ONLY` on match quality alone; the arm
description corroborates each one. Implied `NOT_CONTROL`.

### NCT02913430 — JOIN_RECOVERABLE (2 rows) — recovers a registry control type

| results group (`om_index` 1) | recovered arm | type |
|---|---|---|
| `Fulvestrant + Palbociclib` (OG000) — "Fulvestrant: 500mg IM Q28 days / Palbociclib: 125mg/day PO 21 on/7 off" | `AG[0]` `Arm A`, `interventionNames ['Drug: Fulvestrant','Drug: Palbociclib']`, same doses | **ACTIVE_COMPARATOR** |
| `Tamoxifen + Palbociclib` (OG001) — "Tamoxifen: 20mg PO Q-daily / Palbociclib: 125mg/day…" | `AG[1]` `Arm B`, `interventionNames ['Drug: Tamoxifen','Drug: Palbociclib']`, same doses | **ACTIVE_COMPARATOR** |

Field: `interventionNames` plus the dose text in `armGroups[].description`, reproduced verbatim in
the group description. Job 3 had both rows `NONE` / `UNKNOWN`. Implied control status:
`CONTROL_ACTIVE_COMPARATOR` for both. Note the registry codes *both* arms ACTIVE_COMPARATOR — that
is what the record says, and it is reported as a registry arm type, not as a claim about design.

### NCT02994953 — JOIN_RECOVERABLE (1 row)

Group `Part B Cohort 1: UC Cohort Stage 1 Combination Therapy (Experimental)` (`om_index` 5, OG000)
↔ `AG[5]` `Part B Cohort 1: UC Cohort Stage 1 combination therapy` (EXPERIMENTAL). The label differs
only in case and the trailing `(Experimental)`; the **group description is the arm description
verbatim**. Implied `NOT_CONTROL`.

### NCT03088540 — JOIN_RECOVERABLE (1 row) — recovers a registry control type

Group `Chemotherapy` (`om_index` 3, OG001), description "Participants received platinum-based
doublet chemotherapy" ↔ `AG[0]` `Standard-of-care chemotherapy`,
`interventionNames ['Drug: Pemetrexed','Drug: Paclitaxel','Drug: Gemcitabine','Drug: Cisplatin','Drug: Carboplatin']`,
description listing exactly those platinum doublets. Type **ACTIVE_COMPARATOR**.
Corroborated by complement: in Job 3's own map the sibling group `Cemiplimab` matched `AG[1]`
`cemiplimab` (NORMALIZED), and the trial registers only 2 arms.
Job 3: `UNKNOWN_WEAK_MATCH_ONLY` → implied `CONTROL_ACTIVE_COMPARATOR`.

### NCT03164616 — JOIN_RECOVERABLE (3 rows) — recovers a registry control type

| results group (`om_index` 5) | recovered arm (by `armGroups[].description`) | type |
|---|---|---|
| `T + D + SoC` (OG000) — "tremelimumab 75 mg + durvalumab 1500 mg + SoC chemotherapy" | `AG[0]` `Treatment Arm 1` — "durvalumab + tremelimumab combination therapy + SoC chemotherapy" | EXPERIMENTAL |
| `D + SoC` (OG001) — "durvalumab 1500 mg monotherapy + SoC chemotherapy" | `AG[1]` `Treatment Arm 2` — "durvalumab monotherapy + SoC chemotherapy" | EXPERIMENTAL |
| `SoC Alone` (OG002) — "SoC chemotherapy alone" | `AG[2]` `Treatment Arm 3` — **"SoC chemotherapy alone"** | **ACTIVE_COMPARATOR** |

Three results groups, three registered arms, and each arm description is a near-verbatim restatement
of one group description — a bijection the record asserts on its own. Job 3 had all three `NONE` /
`UNKNOWN`, i.e. it missed a registered `ACTIVE_COMPARATOR` arm that the record names in plain text.

### NCT03212274 — JOIN_RECOVERABLE (6 rows)

One registered arm: `AG[0]` `Treatment (olaparib)` (EXPERIMENTAL). The six groups (`om_index` 0,
OG000–OG005: `Cohort 1A-Glioma Naïve to IDH I` … `Cohort 3B Other -Pretreated`) are cohort splits
inside it. Implied `NOT_CONTROL`, now on the registered arm type rather than on arm count.
(Cohort→disease attribution is Job 3's and is not touched.)

### NCT03409614 — JOIN_RECOVERABLE (5 rows), with one contradiction and three mis-assigned arms ⚠️

The record partitions **both** its arms and its outcome-measure titles into Part 1 and Part 2:
Part 1 has 3 arms and 3 results groups, Part 2 has 2 arms and 2 results groups.

| results group | recovered arm | type | Job 3's recorded arm |
|---|---|---|---|
| `Part 1: Chemotherapy` (`om_index` 6, OG002) | `AG[0]` `Chemo` — "Part 1: Chemotherapy" | OTHER | `Chemo` ✔ |
| `Part 1: Cemiplimab + Chemotherapy` (OG000) | `AG[1]` `REGN2810+Chemo Part 1` — "Part 1: REGN2810+chemo" | EXPERIMENTAL | `Chemo` ✘ |
| `Part 1: Cemiplimab+AbbrevChemo+Ipilimumab` (OG001) | `AG[2]` `REGN2810+AbbrevChemo+ipi` — "Part 1: REGN2810+abbrev chemo+ipi" | EXPERIMENTAL | `Chemo` ✘ |
| `Part 2: Cemiplimab + Chemotherapy` (`om_index` 7, OG000) | `AG[4]` `REGN2810+Chemo Part 2` — "Part 2: REGN2810+chemo" | EXPERIMENTAL | `Chemo` ✘ |
| `Part 2: Placebo + Chemotherapy` (`om_index` 7, OG001) | `AG[3]` `Placebo+Chemo` — "Part 2: Placebo plus chemo" | **EXPERIMENTAL** | (none) |

The Part-1 assignments do not need the REGN2810 = cemiplimab identity: the abbreviated-chemotherapy
+ ipilimumab tokens make `AG[2]` unique, and `AG[0]`'s description is literally "Part 1: Chemotherapy".

⚠️ **Job 3's CONTAINMENT match put 3 of these 5 groups on the wrong arm** (`Chemo`, because "chemo"
is a substring of the normalized group title). Its `control_status` for those rows is
`UNKNOWN_WEAK_MATCH_ONLY`, so no false control status was published — but the recorded
`registry_arm_label`/`registry_arm_type` for those 3 rows are wrong and anything downstream that
reads those columns instead of `arm_match_quality` would inherit the error.

⚠️ **CONTRADICTION, `Part 2: Placebo + Chemotherapy`.** Job 3 assigned
`CONTROL_PLACEBO_BY_GROUP_TEXT` from the group title, with
`control_flag = PLACEBO_CLAIM_WITHOUT_PLACEBO_ARM_IN_REGISTRY`. The recovered arm shows why the flag
fired and why it is not the whole story: the placebo arm **is** registered (`AG[3]` `Placebo+Chemo`,
description "Part 2: Placebo plus chemo") but its `armGroupType` is **EXPERIMENTAL**, not
`PLACEBO_COMPARATOR`; no arm in this record carries any control type, which is also why
`registry_has_control_arm=False` for a trial whose `AG[0]` even lists `Drug: Placebo` among its
`interventionNames`. Under Job 3's own rule a strong match to an `EXPERIMENTAL` arm yields
`NOT_CONTROL`, which directly opposes the status it assigned from the title.
**I adopt neither.** The row is recorded as `implied_control_status = CONTESTED`: the group text and
the registered arm type disagree, and this is a registry type-coding artefact that the record cannot
adjudicate. It must not be counted as a control group, and equally must not be counted as
`NOT_CONTROL`.

### NCT03451825 — JOIN_RECOVERABLE (1 row)

Group `Avelumab 20 mg/kg` (`om_index` 2, OG001) ↔ `AG[1]` `Avelumab 20mg/kg` (EXPERIMENTAL).
The two strings differ by **one space**; Job 3's normalizer maps them to `avelumab 20 mg kg` vs
`avelumab 20mg kg`, which is neither equal nor a substring, so it scored `NONE`. Corroborated by
complement — in Job 3's own map the sibling group matched `AG[0]` NORMALIZED and the trial registers
2 arms — and by the group description's 20 mg/kg IV q2w dose. Implied `NOT_CONTROL`.

### NCT03455829 — JOIN_RECOVERABLE (5 rows)

Five registered arms `Part 1: Cohort 1…5 G1T38 + Osimertinib` (`AG[0]`–`AG[4]`), all EXPERIMENTAL,
carrying **byte-identical descriptions** — the cohort number appears only in the label; five results groups `Part 1: Cohort 1…5 Lerociclib at
<dose>` (`om_index` 2, OG000–OG004). The join is the shared `Part 1: Cohort N` prefix, corroborated
by each group description naming `G1T38/Lerociclib … + Osimertinib`, matching
`interventionNames ['Drug: G1T38','Drug: Osimertinib']`. The cohort number is the only discriminator
the record offers, and it is sufficient. Implied `NOT_CONTROL`.

### NCT03480646 — 8 JOIN_RECOVERABLE + 1 UNRESOLVED (9 rows)

All rows `om_index` 4 (`Efficacy: Best Responses by Treatment Group`). Four groups (OG000–OG003) match a registered arm label exactly once dose tokens are removed
(`AG[0]`–`AG[3]`, all EXPERIMENTAL). The rest:

| results group | recovered arm | type |
|---|---|---|
| `Phase 1b HPEC …CPI-1205 800mg TID +Enza` (OG004) | `AG[4]` `Phase 1b HPEC: CPI-1205 800 mg TID + Enza` — only arm with the HPEC token | EXPERIMENTAL |
| `Phase 2 Randomized Combination With Enza` (OG006) | `AG[6]` `Phase 2 Randomized at RP2D: CPI-1205 800 mg TID + Enza` — description reproduced in the group description | EXPERIMENTAL |
| `Phase 2 Randomized Enza Contro` (OG005) | `AG[5]` `Phase 2 Randomized Controlled Group: Enza` — description "Drug: Enzalutamide 160mg PO QD (28-day cycles)" reproduced as "Enzalutamide Control … 160mg PO QD" | **ACTIVE_COMPARATOR** |
| `Phase 2 Single Arm CPI-1205 +Abi/Pred` (OG008) | `AG[7]` `Phase 2 Single Arm at RP2D: CPI-1205 800 mg TID + Abi/Pred` | EXPERIMENTAL |
| `Phase 2 Randomized Crossover Period` (OG007) | — | **UNRESOLVED** |

The eight recovered assignments are additionally order-preserving in the record —
OG000→`AG[0]`, OG001→`AG[1]`, … OG006→`AG[6]`, OG008→`AG[7]`, with only the unregistered crossover
group OG007 breaking the run — which corroborates each individually derived join.

`Phase 2 Randomized Enza Contro` **refines** Job 3: it had `CONTROL_UNSPECIFIED_BY_GROUP_TEXT`
(control language, no arm); the record names a registered `ACTIVE_COMPARATOR` arm for it. Same
direction, firmer basis — not a contradiction.

`Phase 2 Randomized Crossover Period` is `UNRESOLVED`, not recoverable: its treatment description
matches `AG[6]`, but a crossover period is a post-randomisation population and the record registers
**no crossover arm** and never states the origin arm. Assigning it to `AG[6]` alone, or to `AG[5]`,
would both be inventions. `implied_control_status` stays `UNKNOWN`.

---

## What the parent should take from this, and what it must not

1. For these 16 trials, "unreachable by a defensible match" is **refuted for 136 of 144 in-scope
   rows** (97 of 105 distinct groups). The blocker was the matcher's reliance on the arm *label*
   string; the recoveries come from `armGroups[].description`, `armGroups[].interventionNames`,
   dose-token removal, and partitions the records assert themselves.
2. **This is a per-trial result for my 16 NCTs and nothing more.** It is not a rate, not an
   extrapolation to Job 3's other trials, and it does not license restating any global count.
3. Recovering joins mostly converts `UNKNOWN` into `NOT_CONTROL` on the strength of a registered
   `EXPERIMENTAL` arm type. It found **5 rows across 4 trials** (NCT02913430 ×2, NCT03088540,
   NCT03164616, NCT03480646) whose registered arm type is `ACTIVE_COMPARATOR` and which Job 3 left
   `UNKNOWN` or weak. No placebo or no-intervention comparator was recovered anywhere in my group.
4. Two items need a decision above me: the `NCT02825420` rows where `NOT_CONTROL_SINGLE_ARM_TRIAL`
   is derived from **zero** registered arms, and the `NCT03409614` `Part 2: Placebo + Chemotherapy`
   row where group text and registered arm type contradict each other. Both are recorded, neither
   is resolved here, and neither may be converted into a denominator.
5. `flowGroups` was never available: the cache holds `outcomeMeasuresModule` only. If the parent
   wants that route it requires a re-fetch, which this leaf is fenced from making.
