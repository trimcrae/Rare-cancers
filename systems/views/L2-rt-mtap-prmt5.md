---
id: DOC-VIEW-RT-MTAP-PRMT5
title: RT-MTAP-PRMT5 — PRMT5 / MAT2A synthetic lethality (MTAP co-deletion)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does this tumour carry the copy-number state that selects the PRMT5 axis?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-MTAP-PRMT5 — PRMT5 / MAT2A synthetic lethality (MTAP co-deletion)

**Family:** [ST-DEPENDENCY](L1-st-dependency.md) · **state:** ✓ ready · computed · confidence moderate · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/emc-mtap-prmt5-hypothesis.md`](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md#3--the-reading)): ◐ ROUTE 1'S CLAIM IS SHARPER AND ITS TRANSCRIPT HALF IS NOW IN DOUBT ON ONE PLATFORM; ROUTE 2 REMAINS CLOSED (2026-08-09, after a full panel re-fetch). ⭐ PRMT5 itself reads t = 6.24 and 6.67, EXACT permutation p = 0.000142 and 0.000125 over all 1,623,160 and 8,008 labelings, and it sits in the top 1.9% and top 1.0% of every gene on its own array (18,474 and 14,402 symbols scored). It ranks FIRST of the readable PRMT family on both platforms, so the elevation is not simply family-wide. ⭐ THE FUSION-CLASS TRANSFER IS ARGUED RATHER THAN ASSUMED: a peer-reviewed Ewing result shows PRMT5 inhibition acting in an EWSR1::FLI1-DEPENDENT way (PMC12354397), and PRMT5's measured GRG motif is absent from EWSR1's first 300 residues -- the segment every fusion retains -- with the commonest EMC fusion and the commonest clear cell fusion each keeping 4 of 11 sites. ⚠ The same data refuses the obvious prediction: EWSR1::FLI1 keeps ZERO and PRMT5 still matters there. ⛔ AND THE PROLIFERATION CONTROL BITES ON ONE PLATFORM: adjusting for a twelve-gene score leaves PRMT5 at 5.23 on GPL6244 (35 tumours, score flat) but takes it to 2.71 on GPL3290 (16 tumours, score itself elevated in EMC, r = 0.60). The platforms disagree and nothing here settles which to believe -- this is now the likeliest way route 1's transcript half is wrong. ⛔ ROUTE 2 CLOSED AT TRANSCRIPT LEVEL, and the re-fetch sharpened it: MTAP reads +0.05 SD (t = +0.69) where the read is powered, -0.61 on the other platform -- opposite signs -- and is unremarkable genome-wide on both (top 74% and top 26%). The powered locus signal is CDKN2A (-0.48 SD), which itself reverses (+0.17). Only an MTAP stain can reopen it. Superseded, retained: PRMT5 +0.27/+0.74 SD; MTAP -0.023/-0.389; CDKN2A -0.399/+0.173; CDKN2B -0.096 -- pre-re-fetch values, registered in the manuscript SI's corrections table.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_MTAP_PRMT5["✓ RT-MTAP-PRMT5"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_MTAP_PRMT5
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

## Scientific rationale

One of the few genuinely biomarker-selected synthetic-lethal classes in oncology, and its selecting feature is a copy state nobody here has ever read in this disease. The question is cheap and close to binary, and it has simply never been asked.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CENSUS-ROUTE-GRADING` | the PRMT5 methylosome reads higher in EMC than in comparator sarcomas on both readable platforms, and the MTAP locus group reads lower on the platform where all three genes are readable | `direct` |

## Remaining unknowns

- ⛔ ANSWERED AGAINST ROUTE 2 and kept so it is not re-asked: the low locus reading IS CDKN2A alone at transcript level. Whether MTAP PROTEIN is lost in any EMC case is untouched by that and is the only thing that could reopen the route.
- Whether PRMT5's contribution in the sibling sarcoma runs through the shared 5′ partner or through fusion-driven transcription generally — the question route 1 rests on, and one no public data answers.
- Whether the methylosome elevation is specific or generic, since elevated PRMT5 is reported across many malignancies and abundance is not dependency.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A clinical-stage PRMT5 inhibitor added to the functional screen already running on the two published patient-derived EMC models — the decisive test for the stronger route | ⛔ none built | **no** | BLK-NO-WET-LAB |
| MTAP immunohistochemistry on archival EMC tissue — routine, no fresh tissue, no cell line | ⛔ none built | **no** | BLK-NO-WET-LAB |
| A gene-level copy-number read of the locus in any EMC cohort | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`preprint`**

The decisive observation is a stain on tissue this programme cannot obtain, so the deliverable is the hypothesis and its falsifier rather than the answer.

**Missing:**
- nothing for the preprint — it is written and every figure resolves to a committed artifact

## Where this route ends — the paper

**[PUB-MTAP-PRMT5](L3-publications.md)** — [PRMT5 in extraskeletal myxoid chondrosarcoma — one route in, one route closed, and the cheap test that would settle each](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The route IS the paper: two independent routes into the same class, the confounds that could produce each reading without the underlying biology, and the two different cheap experiments that separate them.

**The paper would claim:** Two independent lines point at the PRMT5 methylosome in extraskeletal myxoid chondrosarcoma and neither has ever been examined in it. One of them closes on the paper's own data and is reported as the negative it is; the other survives and is argued rather than assumed — a peer-reviewed result in a second EWSR1-fusion sarcoma where PRMT5 inhibition acts in a fusion-DEPENDENT way, plus a sequence finding that PRMT5's measured substrate motif is absent from the half of EWSR1 every fusion retains and that the commonest EMC and clear cell fusions keep the same number of sites. The same analysis refuses the response prediction it looks like it licenses. Each route ends at a different inexpensive experiment, and the negative branch of each is worth publishing.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The preprint is complete and needs nobody's cooperation, and the experiment it specifies is the cheapest decisive one anywhere in this portfolio — a routine stain on archival blocks that already exist.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DEPENDENCY](L1-st-dependency.md), which is where these are asserted — a family limitation binds every route inside it.*

- The dependency transfer prior came back negative on the available data — a measured premise, revivable only by EMC-specific data.
- One route rests on class inheritance: no NR4A3 fusion has been tested for the phenotype it assumes.
- There is one EMC model in public dependency data, with no CRISPR data, so this family's in-silico half is bounded by a sample size of one.

## Best next action

Post the preprint and put the MTAP stain in front of a group holding EMC archival material.

*Cost:* $0

[← ST-DEPENDENCY](L1-st-dependency.md) · [← L0](L0-ecosystem.md)
