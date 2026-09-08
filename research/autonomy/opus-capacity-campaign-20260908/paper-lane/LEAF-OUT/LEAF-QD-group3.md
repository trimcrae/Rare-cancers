# LEAF QD / group 3 — is the results-group ↔ registered-arm join actually recoverable?

Leaf worker, wave of 2026-09-08 ~18:55Z. Question D, NCT group 3 (13 trials), plus the corpus-wide
`AMBIGUOUS_MULTI` triage requested as a separate section.

## 0 · Provenance and integrity

- Cache read: `/tmp/claude-0/-home-user-Rare-cancers/8ecd0f49-96ba-5dcf-b11a-af5e48bdec71/scratchpad/ctg-cache-216bd1b5/`
- `sha256sum -c SHA256-MANIFEST.txt` → all 13 entries `OK`, **exit code 0**.
- No network request of any kind was made. Nothing was re-fetched, re-copied or re-derived from a
  producer. Job 3's matcher was not modified and was not re-run.
- Job 3's outputs (`CURATION-endpoint-arm-attribution-map.tsv`, 552 rows) were read as the *input
  index only* — to select my rows and to record what Job 3 concluded for each. Job 3's global
  counts are not restated as findings here.
- Companion table: `LEAF-OUT/LEAF-QD-group3.tsv` (82 data rows, 17 columns). Every row carries a
  `source_pointer` of the form `<payload>.txt | <NCT> | armGroups[i] | outcomeMeasures[j] group <OGid>`
  so the parent can re-derive each verdict from the cache directly.

## 1 · Coverage: groups reached vs assigned

| | count |
|---|---|
| NCTs assigned (`LEAF-ASSIGNMENTS/QD-group3.txt`) | 13 |
| NCTs located in the cache | 13 |
| Map rows for my 13 NCTs with `arm_match_quality` ∈ {NONE, CONTAINMENT, AMBIGUOUS_MULTI} | **79** |
| Rows adjudicated | **79 / 79 (100 %)** |
| Rows not reached | 0 |

All 79 of my rows are `NONE` (70) or `CONTAINMENT` (9); my group contains no `AMBIGUOUS_MULTI` row.
Section 5 covers the 3 corpus-wide `AMBIGUOUS_MULTI` rows separately (2 NCTs, both outside my group),
bringing the TSV to 82 rows.

## 2 · A structural limit that applies to every verdict below

The cached payloads were fetched with a `fields=` restriction (visible in the SOURCE URL header of
each payload file): `protocolSection.identificationModule`, `.conditionsModule`, `.designModule`,
`.armsInterventionsModule.armGroups`, and `resultsSection.outcomeMeasuresModule` — **and nothing
else**. I confirmed this for all 13 records: every one has exactly
`protocolSection ∈ {identification, conditions, design, armsInterventions}` and
`resultsSection ∈ {outcomeMeasuresModule}`.

Consequence for my task: **`flowGroups` (`resultsSection.participantFlowModule`) is not present in
this cache and could not be used.** Neither is `baselineCharacteristicsModule`, nor the
`armsInterventionsModule.interventions` list with its `armGroupLabels` back-pointers — which on
ClinicalTrials.gov is the *explicit* intervention→arm join. So the joins established below use only
what is actually in the cache: per-arm `label`, `type`, `interventionNames` and `description`, and
the results groups' `title` and `description`. A parent that wants the strongest possible join for
these trials should note that two further registry-asserted join fields exist upstream and were
simply not requested at fetch time. That is a **cache-scope** gap, not a registry gap.

## 3 · Headline result

Job 3's verdict — that for these groups "the registry arm type is unreachable by a defensible
match" — **does not hold for my group.** It is an artefact of one string-matching method, not a
property of the source records.

| verdict | rows | trials |
|---|---|---|
| `JOIN_RECOVERABLE` | **78 / 79** | 12 / 13 |
| `GENUINELY_UNJOINABLE` | **1 / 79** | 1 / 13 (NCT04539327) |
| `UNRESOLVED` | 0 | – |

Recovered control status implied by the recovered arm type:

| implied control status | rows |
|---|---|
| `NOT_CONTROL` (recovered `armGroupType = EXPERIMENTAL`) | 77 |
| `UNKNOWN` — join recovered but the registry states **no** arm type (NCT04753658) | 1 |
| `UNKNOWN` — no registered arm exists at all (NCT04539327) | 1 |

⛔ Note on direction: nothing here converts an `UNKNOWN` into a `NOT_CONTROL` by assumption. The 77
`NOT_CONTROL` rows are each backed by a named `armGroups[i]` whose `type` field literally reads
`EXPERIMENTAL` in the cached record. Where the record carries no type (NCT04753658) or no arms
(NCT04539327), the answer stays `UNKNOWN`. No denominator was manufactured.

A second, weaker but very robust observation supports most of the above independently of arm
identity: **in 11 of my 13 trials every registered arm is typed `EXPERIMENTAL`.** For those trials
the arm *type* — the only thing control status actually needs — is determined even if the exact arm
were disputed. The TSV records this as `join_level = ARM_SET_TYPE_INVARIANT` for the two trials
(NCT04020185, NCT04387071) where I could not pin a single arm; the other 10 are `ARM_EXACT`.

## 4 · Per-trial findings

Arm indices are 0-based into `protocolSection.armsInterventionsModule.armGroups` of the payload named
in each heading. All 13 records live in `ctg_results_bor_2018_2021.txt` except where noted.

### NCT03711188 — 2 rows, Job 3 `NONE` / `NOT_CONTROL_SINGLE_ARM_TRIAL`
Results groups `Cohort A`, `Cohort B`. One registered arm, `armGroups[0]` =
`'IMM-101 (and nivolumab or ipilimumab)'`, `type=EXPERIMENTAL`.
**Field that establishes the join:** `armGroups[0].description`, which names the results cohorts
verbatim — *"Patients in **cohort A** were given IMM-101 in combination with nivolumab. Patients in
**cohort B** who fail to respond … have the option to change treatment … to IMM-101 and ipilimumab."*
The registry document itself asserts the mapping in prose; Job 3's matcher never read `description`.
→ `JOIN_RECOVERABLE`, both groups → `armGroups[0]`, `EXPERIMENTAL`, control `NOT_CONTROL`.
Job 3 reached the same *label* by a different route (arm count ≤ 1). No contradiction; the basis is
now the registry's own arm type rather than an arithmetic fallback.

### NCT03724890 — 11 rows, Job 3 `NONE` / `UNKNOWN`
3 arms, all `EXPERIMENTAL`: `[0] Part A: M3814 + Avelumab`, `[1] Part B: … + Radiotherapy (RT)`,
`[2] Part FE: … (fasted/fed state)`. Results groups are **dose levels inside those parts**:
`Part A: M3814 {100,200,250,300,400} mg BID + Avelumab 800 mg Q2W` (5),
`Part B: … {100,150,200,250} mg … + RT` (4), `Part Food Effect: … {100,200} mg …` (2).
**Fields:** the `Part A/Part B` token shared by arm `label` and group `title`; for Part B the group
descriptions state radiotherapy at 3 Gy, and `Radiation: Radiotherapy` appears **only** in
`armGroups[1].interventionNames`; for Part FE the group descriptions state the fasted/fed condition
named in `armGroups[2].label`.
→ 11 × `JOIN_RECOVERABLE`, all `EXPERIMENTAL`, control `NOT_CONTROL`. **This flips 11 rows from
Job 3's `UNKNOWN`.** Job 3's matcher failed only because the results labels carry a dose the arm
label does not.

### NCT03829501 — 23 rows, Job 3 `NONE` / `UNKNOWN`
4 arms, all `EXPERIMENTAL`: `[0] Phase 1: Alomfilimab Monotherapy`,
`[1] Phase 1: Alomfilimab + Atezolizumab Combination Therapy`,
`[2] Phase 2: … in Anti-PD-(L)1 Naïve Participants`, `[3] Phase 2: … in Pre-treated Participants`.
**Fields:** `armGroups[0].description` — *"alomfilimab 0.8 to 240 mg as a single agent"* — covers the
six monotherapy dose groups by explicit range; `armGroups[1].interventionNames`
`['Drug: Alomfilimab','Drug: Atezolizumab']` is the only Phase 1 combination; `armGroups[2]` and
`[3]` descriptions carry the literal tokens *"Anti-PD-(L)1 naïve"* / *"Pre-treated"* **and** the three
tumour types (pancreatic, triple-negative BC, HNSCC) that the twelve Phase 2 group titles use.
→ 23 × `JOIN_RECOVERABLE`, all `EXPERIMENTAL`, control `NOT_CONTROL`.
**Registry imprecision recorded, not resolved away:** the group `Alomfilimab 0.8 mg + Atezolizumab`
sits *below* the "2.4 to 80 mg" range stated in `armGroups[1].description`. Since `armGroups[1]` is
the only Phase 1 combination arm and all four arms are `EXPERIMENTAL`, the arm type is unaffected;
the range statement in the registry is simply narrower than what the results report.

### NCT03854227 — 3 rows (1 `NONE`, 2 `CONTAINMENT`), Job 3 `UNKNOWN` / `UNKNOWN_WEAK_MATCH_ONLY`
6 arms, all `EXPERIMENTAL`. `Part 2B (2L+ Urothelial Carcinoma)` → `armGroups[2] 'Urothelial
carcinoma'`; `Part 2C (HNSCC)` → `armGroups[3] 'Head and neck squamous cell carcinoma'` — Job 3's
own containment hit was correct, it was merely graded "weak". `Part 2A (2L+ NSCLC)` →
`armGroups[1] 'Non small cell lung cancer monotherapy'`: the group description states
*PF-06939999 6 mg QD* with **no docetaxel**, which excludes `armGroups[4]`/`[5]`
(`'…PF-06939999 plus docetaxel'`, `'…dose finding'`, both `Drug: PF-06939999 in combination with
docetaxel`).
→ 3 × `JOIN_RECOVERABLE`, `EXPERIMENTAL`, control `NOT_CONTROL`.

### NCT03894540 — 6 rows, Job 3 `CONTAINMENT` / `UNKNOWN_WEAK_MATCH_ONLY`
4 arms, all `EXPERIMENTAL`. Groups `IPN60090 {20,40,80,120,180,240} mg`, each described as
*"capsules orally BID up to Cycle N in Part A"*. → `armGroups[0] 'IPN60090'`, whose description reads
*"Part 1: Dose escalation of IPN60090 … given as a BID oral dose"*. The group descriptions name no
pembrolizumab and no paclitaxel (excluding `armGroups[1]`/`[2]`) and describe repeated multi-cycle
BID dosing rather than a single fasted/fed administration (excluding `armGroups[3]`, food effect).
→ 6 × `JOIN_RECOVERABLE`, `EXPERIMENTAL`, control `NOT_CONTROL`. Job 3's containment hit was right;
the description text is what upgrades it from "weak substring" to a defensible join.

### NCT04020185 — 8 rows, Job 3 `NONE` / `UNKNOWN`
5 arms, all `EXPERIMENTAL`: Ph I Monotherapy, Ph I Combination, Ph II Mono (Arm A), Ph II Combo
(Arm B), Ph II Combo (Arm C). Groups are `Monotherapy {100,200,400,800,1200} μg` and
`Combination Therapy {800,1200,2400} μg`.
**Field:** the group descriptions for the combination groups end *"Plus an ICI administered as per
product label"*, which matches `interventionNames` `'Drug: Immune checkpoint inhibitor (ICI)'` /
`'Drug: Immuno-oncology (IO) therapy'` on `armGroups[1]/[3]/[4]` and excludes the two monotherapy
arms; the monotherapy group descriptions name IMSA101 alone.
**Honest limit:** the record does not let me separate the Phase I dose-escalation arm from its
Phase II dose-expansion counterpart (`armGroups[0]` vs `[2]`; `[1]` vs `[3]`/`[4]`), because the
results groups are labelled by dose only. I therefore record `join_level = ARM_SET_TYPE_INVARIANT`:
the arm is resolved to a **set**, and every member of that set is `EXPERIMENTAL`, so the arm type —
and hence control status — is determined. → 8 × `JOIN_RECOVERABLE` (type level), `NOT_CONTROL`.

### NCT04044768 — 2 rows, Job 3 `NONE` / `NOT_CONTROL_SINGLE_ARM_TRIAL`
One arm, `armGroups[0]` = afamitresgene autoleucel SPEAR T cells, `EXPERIMENTAL`. Groups
`Synovial Sarcoma`, `MRCLS` are disease strata; both group descriptions state *"received
afamitresgene autoleucel as a single infusion in Cohort 1"*, matching
`armGroups[0].interventionNames`. → `JOIN_RECOVERABLE`, `EXPERIMENTAL`, `NOT_CONTROL`.

### NCT04099641 — 2 rows, Job 3 `NONE` / `NOT_CONTROL_SINGLE_ARM_TRIAL`
One arm, `armGroups[0] 'bavituximab and pembrolizumab'`, `EXPERIMENTAL`, description
*"Bavituximab 3mg/kg IV weekly in combination with pembrolizumab 200mg IV given once every 3 weeks"*.
Groups `Group 1 (CPI Naïve)` / `Group 2 (CPI Relapse)` are prior-therapy strata whose descriptions
restate that same regimen. → `JOIN_RECOVERABLE`, `EXPERIMENTAL`, `NOT_CONTROL`.

### NCT04306900 — 11 rows, Job 3 `NONE` / `UNKNOWN` — the clearest refutation
8 arms named only `Combo 1` … `Combo 8`, all `EXPERIMENTAL`, each carrying a full regimen in
`interventionNames` and `description`. The 11 results groups are named
`Cohort N - <disease> (<regimen>)`. Job 3's matcher could not match `Cohort 6 - HNSCC (TTX-030 +
Budigalimab)` to `Combo 5` because the two strings share no token. **Regimen composition joins all
11 uniquely:**

| results group | → arm | registered regimen |
|---|---|---|
| Cohort 1 – Safety Lead-in (TTX-030 + Budigalimab + mFOLFOX6) | `armGroups[0]` Combo 1 | TTX-030, budigalimab and mFOLFOX6 |
| Cohort 3B – Gastric (TTX-030 + Budigalimab + mFOLFOX6) | `armGroups[0]` Combo 1 | same regimen (many-to-one) |
| Cohort 2 – mCRPC (TTX-030 + Budigalimab + Docetaxel) | `armGroups[1]` Combo 2 | TTX-030, budigalimab and docetaxel |
| Cohort 3A – Gastric (TTX-030 + mFOLFOX6) | `armGroups[2]` Combo 3 | TTX-030 and mFOLFOX6 |
| Cohort 10 – UCC (TTX-030 + Pembrolizumab) | `armGroups[3]` Combo 4 | TTX-030 and pembrolizumab |
| Cohort 4 – CRC (TTX-030 + Budigalimab) | `armGroups[4]` Combo 5 | TTX-030 and budigalimab |
| Cohort 6 – HNSCC (TTX-030 + Budigalimab) | `armGroups[4]` Combo 5 | idem |
| Cohort 8 – GEC (TTX-030 + Budigalimab) | `armGroups[4]` Combo 5 | idem |
| Cohort 9 – Pancreatic (TTX-030 + Budigalimab + Gem + Nab-P) | `armGroups[5]` Combo 6 | TTX-030, budigalimab, nab-paclitaxel and gemcitabine |
| Cohort 11 – Pancreatic (TTX-030 + Gem + Nab-P) | `armGroups[6]` Combo 7 | TTX-030, nab-paclitaxel and gemcitabine |
| Cohort 12 – Gastric (Budigalimab + mFOLFOX6) | `armGroups[7]` Combo 8 | Budigalimab and mFOLFOX6 |

→ 11 × `JOIN_RECOVERABLE`, all `EXPERIMENTAL`, control `NOT_CONTROL`. **Flips 11 rows from `UNKNOWN`.**
Recorded for the parent: Cohort 12 is the only cohort that omits the investigational agent TTX-030
and is the natural comparator for Cohort 3B, but the sponsor typed `Combo 8` as `EXPERIMENTAL`, so
**the record designates no control arm anywhere in this trial.** The recovered status is
`NOT_CONTROL`, not "control by design intuition".

### NCT04387071 — 1 row, Job 3 `NONE` / `UNKNOWN`
7 registered arms (`Dose Level -1` … `Dose Level 6`), all `EXPERIMENTAL`. The single results group
`Treatment (CMP-001, INCAGN01949)` **pools every dose level** — its description omits any dose,
where all seven arm descriptions differ only by the INCAGN01949 dose (250 / 500 / 1000 / 1670 /
2505 / 3507 / 4559 mcg/m²). There is therefore no one-to-one arm identity to recover, and I do not
invent one. But `armGroups[*].type` is `EXPERIMENTAL` for all 7, so the arm type the control
determination needs **is** established. → `JOIN_RECOVERABLE` at `join_level =
ARM_SET_TYPE_INVARIANT`, control `NOT_CONTROL`.

### NCT04539327 — 1 row — **`GENUINELY_UNJOINABLE`**, and a Job 3 contradiction
Group `Rucaparib - Treatment`. `protocolSection.armsInterventionsModule` is the **empty object `{}`**:
zero `armGroups`. The record is `studyType: OBSERVATIONAL`, `observationalModel: CASE_ONLY`,
`timePerspective: RETROSPECTIVE`, enrolment 51 actual. Nothing exists to join to; no `armGroupType`
appears anywhere in the record. **What specifically is missing: the `armGroups` array itself.**
Job 3's verdict "unreachable" is **confirmed** for this row.

⛔ **Contradiction to flag.** Job 3 recorded `control_status = NOT_CONTROL_SINGLE_ARM_TRIAL` with
`n_arms_registered = 0`, via the rule `n_arms_registered <= 1 → NOT_CONTROL_SINGLE_ARM_TRIAL`. Zero
registered arms is *absence of information*, not evidence of a single-arm design — and this study is
not an arm-based design at all. The source supports `UNKNOWN` here. This is exactly the failure mode
the brief warns about, in the reverse direction: a `NOT_CONTROL` produced where the registry says
nothing. The parent should treat any `NOT_CONTROL_SINGLE_ARM_TRIAL` row with `n_arms_registered = 0`
as suspect. (Whether other such rows exist across the corpus is outside my group and I did not check.)

### NCT04753658 — 1 row, Job 3 `CONTAINMENT` / `UNKNOWN_WEAK_MATCH_ONLY`
One arm, `armGroups[0] 'Pediatric Neuroblastoma Patients Treated with Lorlatinib'`, whose
`interventionNames` `['Drug: lorlatinib']` matches the results group `Lorlatinib` and its
description. The **join is recoverable** (`ARM_EXACT`). But I verified the object literally has no
`type` key at all (`"type" in armGroups[0]` → `False`), which is what Job 3 encoded as
`NOT_STATED_IN_REGISTRY`. **Recovering the join does not recover a type.** → `JOIN_RECOVERABLE`,
recovered arm type `ABSENT_NO_TYPE_KEY`, implied control status **`UNKNOWN`**. Same endpoint as
Job 3, reached honestly: the limit here is the registry's, not the matcher's.

### NCT04764474 — 8 rows, Job 3 `NONE` / `NOT_CONTROL_SINGLE_ARM_TRIAL`
One arm, `armGroups[0] 'Treatment'`, `EXPERIMENTAL`, description *"All patients will be administered
HMPL-306 orally QD"* — which by its own wording covers all eight dose-escalation cohorts
(`Cohort 1..8: HMPL-306 Dose Level 1..8`). → 8 × `JOIN_RECOVERABLE`, `EXPERIMENTAL`, `NOT_CONTROL`,
now type-supported rather than count-supported.

## 5 · Separate section — the 3 corpus-wide `AMBIGUOUS_MULTI` rows (OUTSIDE my NCT group)

These 3 rows fall on **NCT02608268 (2 rows)** and **NCT03409614 (1 row)**. Neither NCT is in
`QD-group3.txt`; I examined them only because the task assigned this triage explicitly, and I make
no claim about anything else in those two trials.

Both cases are produced by the **same mechanism**: Job 3's fallback is an *unanchored substring
containment* test on whitespace-normalised text (`k in gt or gt in k`), and when two registered arm
labels both satisfy it the matcher returns `AMBIGUOUS_MULTI` and discards the arm. The ambiguity is
in the test, not in the record — in both cases the record disambiguates cleanly.

**(a) NCT02608268** — payload `ctg_results_bor_2014_2017.txt`, 10 registered arms, all `EXPERIMENTAL`.
Rows: `Phase II: MBG453 + PDR001 NSCLC` and `Phase II: MBG453 + PDR001 Melanoma`.
*What makes it ambiguous:* `armGroups[9]` is labelled `'Phase II: MBG453'`, whose normalised form
`phase ii mbg453` is a **strict prefix** of `armGroups[8]`'s `'Phase II: MBG453 + PDR001'`
(`phase ii mbg453 pdr001`), and both are substrings of the normalised group title. Two containment
hits → `AMBIGUOUS_MULTI`.
*Resolution:* `armGroups[8]`. Two independent fields settle it — `armGroups[8].interventionNames`
includes `'Drug: PDR001'` (the group titles say `+ PDR001`; `armGroups[9]` has only `Drug: MBG453`),
and `armGroups[8].description` names *"non-small cell lung carcinoma (NSCLC) and melanoma"*, i.e. the
two disease strata that are exactly these two results groups. A third field kills `armGroups[9]`
outright: its description states *"This arm was not opened for enrollment."*
→ `JOIN_RECOVERABLE`, `armGroups[8]`, `EXPERIMENTAL`, implied control `NOT_CONTROL` (Job 3: `UNKNOWN`).

**(b) NCT03409614** — payload `ctg_results_bor_2018_2021.txt`, 5 registered arms.
Row: `Part 2: Placebo + Chemotherapy`.
*What makes it ambiguous:* `armGroups[0]` is labelled `'Chemo'`; normalised `chemo` is a substring of
`chemotherapy` inside the normalised group title `part 2 placebo chemotherapy`. `armGroups[3]`
`'Placebo+Chemo'` normalises to `placebo chemo`, also a substring. Two hits → `AMBIGUOUS_MULTI`. The
culprit is an abbreviation (`Chemo`) that is a prefix of a full word (`Chemotherapy`) — a pure
artefact of substring matching.
*Resolution:* `armGroups[3] 'Placebo+Chemo'`, whose description is *"Part 2: Placebo plus chemo"*.
The `Part 2` token appears in both the group title and the arm description, and `armGroups[0]`'s
description is *"Part 1: Chemotherapy"*, so the trial's own Part labelling separates them.

⛔ **This is the one case where the recovered arm type CONTRADICTS the control status Job 3 assigned.**
Job 3 recorded `CONTROL_PLACEBO_BY_GROUP_TEXT` from the group text (*"Placebo matching cemiplimab plus
platinum-based doublet chemotherapy"*). The recovered `armGroups[3].type` is **`EXPERIMENTAL`**, not
`PLACEBO_COMPARATOR`. Under Job 3's own precedence rule (a strong arm match with type `EXPERIMENTAL`
→ `NOT_CONTROL`), recovering this join would *overturn* a correct placebo determination.

My reading, stated as a judgement and not as a fact of the record: **the registry `type` field is the
unreliable side here, and Job 3's group-text answer is substantively right.** Supporting evidence in
the same record: `armGroups[0] 'Chemo'` is typed `OTHER` yet its `interventionNames` are
`['Other: Chemotherapy', 'Drug: Placebo']` — a placebo intervention attached to a non-placebo-typed
arm. This trial's arm typing is internally inconsistent. The parent should therefore **not** apply a
blanket "recovered `armGroupType` beats group text" precedence: for this row I recommend the control
status remain `CONTROL_PLACEBO_BY_GROUP_TEXT` with a recorded registry-type conflict, and I flag the
row rather than silently flipping it. The TSV records `implied_control_status =
"NOT_CONTROL (by recovered armGroupType=EXPERIMENTAL)"` with `contradicts_job3 = YES …` so the
conflict is visible rather than resolved by me.

## 6 · What this does and does not establish

- It establishes that, for 12 of my 13 trials, **a defensible results-group → registered-arm join
  exists in the cached record** and was missed because Job 3's matcher reads only `label`, and only
  by exact / normalised-equality / substring containment. The fields that carry the join in practice
  are `armGroups[].description`, `armGroups[].interventionNames`, and the results groups' own
  `description` — none of which the matcher consults.
- It does **not** revise Job 3's map. I changed nothing, re-ran nothing, and rebuilt nothing. These
  are per-row adjudications for the parent to act on or not.
- It says nothing about disease attribution (Job 3's), nothing about any NCT outside my group beyond
  the two named in section 5, and nothing about efficacy, safety, selectivity or clinical readiness.
- One row of mine is genuinely unjoinable, and two rows end at `UNKNOWN` control status. Those stay
  `UNKNOWN`. No `UNKNOWN` was read as `NOT_CONTROL`.
