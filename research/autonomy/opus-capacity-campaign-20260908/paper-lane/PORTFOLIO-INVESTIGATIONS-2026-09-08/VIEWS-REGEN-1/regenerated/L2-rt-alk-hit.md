---
id: DOC-VIEW-RT-ALK-HIT
title: RT-ALK-HIT — Follow-up of the ALK/ROS1-class ex-vivo screen hit
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Which kinase produced the multi-target inhibitor's hit in a patient-derived model of this disease?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ALK-HIT — Follow-up of the ALK/ROS1-class ex-vivo screen hit

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ parked · computed · confidence low · verified 2026-08-29

**Grade** (owned by [`research/modalities/census-route-expression-grading.json`](../../research/modalities/census-route-expression-grading.json)): ⛔ UNATTRIBUTABLE BY EXPRESSION, AND THE RE-READ DEMOTES THE LEAD (2026-08-09). The route's own first step was to re-read the committed screen, and doing it changes what the lead is: the screen returned THREE low-IC50 agents and TWO of them are the same pan-HDAC class, read from this repository's own curated target records rather than recalled. That is a within-screen class replication the one-agent framing could not show — and that class is already on the board, closed on selectivity rather than on activity. ⛔ The expression instrument cannot ATTRIBUTE the hit, and that is an instrument statement and never a biological negative — but it is less blind than this grade said until 2026-08-29. ALK is readable on GPL6244 and not on GPL3290; ROS1 is readable on BOTH. The named target group therefore scores on GPL6244, where it is lower in EMC than in comparator sarcomas, and emits no score on GPL3290 only, where the single missing ALK probe takes coverage below the panel's floor. EGFR is lower in EMC on both platforms. ⚠ The curated record names ALK and EGFR and does NOT name ROS1, though the lead calls this the ALK/ROS1 class. ⭐ AND THE DEPENDENCY PRIOR, RUN 2026-08-09, POINTS THE SAME WAY AS THE HIT LIST. Across the 91 SCREENED sarcoma lines NEITHER named kinase is a dependency in a SINGLE line — mean gene effects of about -0.04 and +0.11, fraction dependent 0.0 for both — while one class I HDAC is a dependency in 82% of them, mean about -0.92. ⚠ This does not prove the hit was not on-target for the named kinase in that particular line: a gene-effect score is a knockout phenotype and an inhibitor's IC50 is not, and the screen ran on a line absent from this panel. But it makes the class attribution the better-supported reading on two independent axes. ⛔ DENOMINATOR CORRECTED 2026-08-27: this grade was written on 2026-08-09 saying 176 sarcoma lines. 176 is the number of sarcoma MODELS in DepMap 24Q4; only 91 of them carry CRISPR gene-effect data, and every per-gene row of research/modalities/depmap-sarcoma-dependency.json reads n_sarcoma: 91 (depmap_sarcoma_dependency.py computes it as len of the non-null sarcoma column, while n_sarcoma_models at the top level is len of the sarcoma model list). The percentages and gene effects are unchanged — they were always computed on the screened subset — but the denominator overstated the evidence base by almost double. The identical error was found and corrected in the MTAP/PRMT5 manuscript's correction register on 2026-08-09/10 (across 176 sarcoma cell lines → across the 91 screened sarcoma cell lines, described there as a real error in the direction that overstated the evidence base), and the fix was never carried back into this graph. ⚠ Other routes' grades and research/modalities/census-route-expression-grading.json still carry the superseded 176; correcting those is a separate item, not this route's. ⭐ RE-GRADED 2026-08-29 AGAINST PMID 42660639 (doi 10.1136/jcp-2026-210760, J Clin Pathol 2026), AND THE ROUTE DOES NOT MOVE. That study scored ALK D5F3 immunohistochemistry across 119 FET-rearranged tumours of 20 types and reports 2 of 4 EMC cases at 2+/3+. ⛔ WHAT IT ESTABLISHES IS PROTEIN ABUNDANCE, AND ITS OWN DESIGN EXCLUDES THE THING THAT WOULD HAVE BEEN A TARGET — its words are that cases with ALK overexpression by IHC were further confirmed to lack ALK gene rearrangements. A stain is not a fusion. It reports no activation, no dependency, no drug response, nothing on ROS1, and nothing about the model the 221-drug screen ran on, so it cannot attribute the hit, which is this route's whole question. ⛔ AND EMC IS NOT SEPARABLE FROM THE FAMILY WITHIN IT: 2/4 carries an exact 95% interval of 6.8% to 93.2%, and against the rest of the cohort (32/115) Fisher's exact test gives two-sided p = 0.32, so the paper's own headline — that ALK overexpression is a property of FET-rearranged tumours generally, 34/119 — is what the EMC number belongs to. Its closing clause about therapeutic opportunity carries no treatment arm, no model and no functional endpoint. Quotations, the exact arithmetic and the full reading: research/literature/alk-ihc-fet-tumours-2026-08-29.json. ⚠ Abstract only — the PubMed record carries no PMCID, checked live on 2026-08-29, so no PubMed Central full text exists to fetch. ⚠ This disease's own CD117/KIT history is the same shape and is owned by research/manuscripts/repurposing/repurposing-hypotheses.md §1.1; the figures are not restated here. ⭐ WHAT THE PAPER DOES ADD is a second MODALITY — protein rather than transcript — on ALK in EMC tissue, at n=4. ⛔ READABILITY CORRECTED 2026-08-29 AND THE ERROR WAS THIS GRADE'S OWN. Until today this grade, the generated route view, the census artifact's prose and the ledger item that commissioned the re-grade all said ALK and ROS1 have no probe on EITHER platform. The artifact that OWNS these reads, research/modalities/emc-expression-panels.json, says ALK is readable on GPL6244 (one probe) and unreadable on GPL3290, that ROS1 is readable on both, and that the brigatinib target group reaches full 3/3 coverage on GPL6244 and emitted a score there. The false sentence was hand-typed prose inside research/modalities/census_route_expression_grading.py, sitting in the same generated file as the per-gene table contradicting it, and it propagated by copy. ⚠ IT DOES NOT TURN A NULL INTO A POSITIVE: where ALK is readable it sits below the array median in EMC and level with the comparators, so the route moves from 'we cannot see it' to 'we can see it on one platform and it is unremarkable there'.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_ALK_HIT["✓ RT-ALK-HIT"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_ALK_HIT
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  BLK_NO_WET_LAB{{"BLK-NO-WET-LAB — No wet lab and no collaborator — an ask…"}}:::blk
  BLK_NO_WET_LAB --> RT_ALK_HIT
  TECH_CLOUD_WET_LAB(["TECH-CLOUD-WET-LAB<br/>expected 2029"]):::tech
  TECH_CLOUD_WET_LAB -.-> BLK_NO_WET_LAB
  TECH_EMC_MODEL_ACCESS(["TECH-EMC-MODEL-ACCESS<br/>expected 2029"]):::tech
  TECH_EMC_MODEL_ACCESS -.-> BLK_NO_WET_LAB
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

An ALK/ROS1-class inhibitor was among the low-IC50 hits of a 221-drug screen run on a patient-derived model of this disease, and nothing here has ever followed it up. The hit does not establish which target produced it, because that agent inhibits several kinases, so the route's first job is to separate the observation from the hypothesis.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CENSUS-ROUTE-GRADING` | the named targets are readable on GPL6244 and the group scores lower in EMC there, ALK alone is unreadable on GPL3290 so the group emits no score on that platform, abundance cannot attribute a screen hit either way, and two of the screen's three hits belong to a single class already assessed on the board | `direct` |
| `ART-DEPMAP-SARCOMA-DEP` | neither named kinase is a dependency in any of the 91 SCREENED sarcoma lines while one class I HDAC is a dependency in the large majority, which points the same way as the screen's own hit list (denominator corrected from 176 on 2026-08-29 — this row was the copy the 2026-08-27 correction did not reach) | `class_inherited` |
| `ART-ALK-IHC-FET-2026` | ALK protein is detectable at D5F3 IHC 2+/3+ in 2 of 4 EMC cases, in tumours confirmed to LACK ALK rearrangement — a protein-level modality the arrays do not supply, at a denominator that does not separate EMC from the FET-rearranged family | `direct` |

## Remaining unknowns

- Which of the agent's targets produced the hit — unanswerable by abundance in principle, since an IC50 reflects dependency and a target at the array floor can still be the one that matters.
- Whether a single-model screen hit transfers, given how few models of this disease exist.
- Whether the class the screen actually favoured has any activity window in this disease, which is the board's existing open question for it and is not reopened by this reading.
- ⭐ NEW 2026-08-29 — whether the ALK protein that stains in EMC tissue is doing anything. PMID 42660639 establishes abundance in 2 of 4 cases and explicitly excludes rearrangement in them; no phospho-ALK, no ALK-inhibitor response and no ALK dependency in any EMC material has ever been reported. The DepMap prior over 91 screened sarcoma lines has ALK and ROS1 dependent in ZERO of them.
- ⭐ NEW 2026-08-29 — what the EMC rate actually is. n=4 is the whole of the EMC evidence in the only study that has ever read ALK protein in this disease.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| ⛔ TAKEN 2026-08-09 — re-read the committed drug-screen artifact for the full hit list and read each agent's curated targets across the expression cohorts | ⛔ none built | yes | — |
| ⛔ TAKEN 2026-08-09 — a sarcoma-class dependency prior for the hit agents' targets, queued in the dependency panel; ⚠ the reason given for queueing it (that the arrays cannot see two of them at all) was corrected on 2026-08-29 and was false for ROS1 on both platforms and for ALK on GPL6244 | ⛔ none built | yes | — |
| An attribution experiment in the line the screen ran on — a knockdown or a target-selective agent, which is the only thing that separates the observation from the hypothesis | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NO-WET-LAB** | `requires_external_collaboration` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |

## Readiness — what this could become today

**`internal_note`**

The expression instrument could only ever have ruled a target out, and for the two it was raised to test it could not even do that.

**Missing:**
- a dependency prior for the named targets, which is queued and $0
- an attribution experiment, which needs the model the screen ran on

## Where this route ends — the paper

**[PUB-KINASE-LEADS](L3-publications.md)** — *Four kinase observations in extraskeletal myxoid chondrosarcoma that nobody followed up* (unwritten)

`contributing` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** One of four kinase observations specific to this disease that exist in the published or curated record and that nobody has followed up.

**The paper would claim:** Four kinase-directed observations specific to this disease exist in the published and curated record — one reported as expressed and activated, one positive across a small series with an internal control, one an interaction curated on the driver protein itself, one an ex-vivo screen hit — and none has been followed up by anyone, in a disease with no targeted agent.

**It is not written because:** ⚠ ITS BLOCKER IS RETIRED — THE CONSOLIDATION IS DONE AND IT INVERTED THE PAPER. All four leads are graded as of 2026-08-09, and reading each one's own primary record demoted THREE of them in ways the leads' prose did not predict: the activation claim behind the strongest lead is a single paywalled abstract sentence with no recoverable denominator, and the approved agents address a molecular state this disease is not reported to be in; the screen hit turns out to sit beside two same-class hits belonging to a class the board already holds, and its named kinases have no probe on either platform so the arrays could never have attributed it; the interaction lead was measured on wild-type protein in a non-sarcoma tissue from one source. The fourth is discordant on the kinase and concordant on its substrate. ⭐ THAT IS THE PAPER NOW, and it is a better one than the consolidation that was planned: four EMC-specific kinase observations that the field has cited or left for one to two decades, each traced to what was actually measured, with the gap between the citation and the measurement stated. ⛔ Superseded, retained: "the consolidation has not been done — three of the four were surfaced two days before this endpoint was registered." ⚠ Two of the four gradings came from records that had been committed since 2026-08-07 and that the routes were registered without reading.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Attribution needs the model, not the arrays. The screen's own weight sits with a class the board has already assessed.

| horizon | effect |
|---|---|
| Cost trend | flat |

**Revisit when:**
- **TECH-EMC-MODEL-ACCESS** — Access to a patient-derived EMC model through a collaborator, or through a solo-affordable cloud or robotic wet-lab service with E *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Best next action

Report it in the kinase paper as a CORRECTED reading of a lead: the screen's dominant signal is a class the board already holds; the arrays can read the named targets on one of two platforms and find them unremarkable there; and the one protein-level read that exists (PMID 42660639) is a stain in tumours confirmed to lack the rearrangement, at a denominator of four.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
