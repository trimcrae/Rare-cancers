---
id: DOC-VIEW-RT-SSTR2
title: RT-SSTR2 — SSTR2 / neuroendocrine theranostic
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does EMC express somatostatin receptor 2 well enough for a theranostic pair to work?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-SSTR2 — SSTR2 / neuroendocrine theranostic

**Family:** [ST-RADIOLIGAND](L1-st-radioligand.md) · **state:** ○ blocked · concept · confidence unknown · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#route-7--sstr2--neuroendocrine-theranostic-the-cheapest-possible-confirm-and-the-clearest-case-of-cheapness-not-being-enough)): Tier 3 — demoted; W2 is the smallest imaginable and W1 is the problem

## What has to land for this route to move

```mermaid
flowchart LR
  RT_SSTR2["○ RT-SSTR2"]:::fam
  BLK_CLASS_INHERITANCE{{"BLK-CLASS-INHERITANCE — Class inheritance, not an EMC mea…"}}:::blk
  BLK_CLASS_INHERITANCE --> RT_SSTR2
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_CLASS_INHERITANCE
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_SSTR2
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  BLK_NO_WET_LAB{{"BLK-NO-WET-LAB — No wet lab and no collaborator — an ask…"}}:::blk
  BLK_NO_WET_LAB --> RT_SSTR2
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

✓ Already cleared by this route: `BLK-NOT-FUSION-SELECTIVE`, `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

A theranostic gives imaging and therapy from one vector, and the imaging half is a cheap decisive test: a negative scan kills the route immediately and inexpensively. EMC has neuroendocrine-adjacent features that make the receptor worth checking.

## Remaining unknowns

- Whether EMC expresses the receptor at all — this has never been measured.
- Whether expression is high enough for therapeutic rather than merely diagnostic use.
- SSTR2's normal-tissue window is ALREADY computed as ENHANCED_BROAD (emc-surface-normal-window.json), so a positive EMC scan does not settle the route — tumour-to-normal uptake ratio and dosimetry remain. Crossfire does not make a broadly-expressed normal antigen safer; it widens the irradiated field.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A receptor imaging scan in an EMC patient, or an expression readout on EMC tissue | ⛔ none built | **no** | BLK-NO-EMC-DATA, BLK-NO-WET-LAB |
| Tumour-to-normal uptake ratio and dosimetry on an SSTR2-avid EMC lesion | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-CLASS-INHERITANCE** | `insufficient_data` | `TECH-VIRTUAL-CELL` |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |
| **BLK-NO-WET-LAB** | `requires_external_collaboration` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer
- **BLK-NOT-FUSION-SELECTIVE** — The route also engages the wild-type protein (NR4A3 LBD, or EWSR1's low-complexity half)

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-B7H3](L2-rt-b7h3.md) | which antigen and how it was graded | `BLK-NO-EMC-DATA` | SSTR2 is UNMEASURED in EMC; B7-H3 was MEASURED and came back not selective (BH q = 1.0). 'Surface-target route' names both and they failed differently |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) | which radioligand target | `BLK-NO-EMC-DATA` | SSTR2 follows EMC's own neuroendocrine differentiation and its ask needs a clinician with an EMC patient; FAP targets the myxoid STROMA and its ask is an expression/avidity confirm |

## Readiness — what this could become today

**`experimental_proposal`**

It is a well-formed cheap ask with an unknown answer. There is no computation that would strengthen it — only a measurement.

**Missing:**
- any expression measurement in EMC

**Experiment required:**
- a receptor scan, or an expression readout on EMC tissue

## Where this route ends — the paper

**[PUB-SURFACE-TARGETS](L3-publications.md)** — [How far a lineage-surrogate surface-antigen ranking transfers to the tumour it was built for: extraskeletal myxoid chondrosarcoma as a worked case](../../research/manuscripts/emc-surface-target-landscape.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The theranostic receptor arm, framed as a cheap decisive negative rather than as a lead — there is no computation that strengthens it, only a measurement.

**The paper would claim:** Surface priorities derived from a lineage surrogate did not transfer to EMC tumour tissue, and did not transfer in either direction. A 2,826-gene surfaceome, 2,692 of them present in the expression matrix and scanned, was ranked across a translocation-sarcoma DepMap class of 76 members with 45 carrying expression data, filtered by a normal-tissue prior whose selective-and-restricted intersection holds exactly one member, and then tested in three EMC tumour-tissue cohorts (GSE24369/GPL6244, GSE4303/GPL3290, GSE28866/3SEQ) at alpha 0.05 with Benjamini-Hochberg correction applied within each platform; the third cohort carries 27 normal-organ libraries and supplies the first on-target/off-tumour exposure axis this repository has had. Eighteen of 47 actionable antigens are selective in the surrogate at q < 0.05, 13 have a tumour-tissue reading, none is concordantly elevated on both arrays, and every significant movement among them runs opposite to the direction the surrogate predicted. Three genes on the 100-gene cross-platform board are concordantly elevated (VCAN, BGN, CD44): two are secreted matrix proteoglycans and the third is the antigen the surrogate ranked lowest of all 47 at q = 1.0. B7-H3/CD276 is not selective in the surrogate (q = 1.0); none of the 11 therapeutic addresses named by candidate routes is concordantly elevated; CSPG4, never scanned at stage 1, rose on one array and in the sequencing cohort and is held open. Elevations below about 0.7 SD on the limiting platform are not excluded. Surrogate-built target lists are routine in rare tumours and the outcome when the tumour itself is measured is rarely reported, which is the transferable half. It asserts no protein abundance, no surface localisation, no receptor density, no selectivity, no safety, no therapeutic window and no clinical readiness. ⚠ SUPERSEDED 2026-08-07, RETAINED: the prior claim was that every negative is "bounded by that surrogate basis rather than by an EMC tissue measurement", from "one cell line and a translocation-sarcoma comparison set". ⚠ SUPERSEDED 2026-08-09, RETAINED: "the paper needs rewriting rather than re-verifying" — the rewrite landed that day and the manuscript is now the two-stage study described above, so this field asserted a pending state of a manuscript that had already moved past it. ⛔ The rewrite was a DEMOTION, not a gain: ALCAM, its lead antigen, reads 0.578 in EMC against 0.631 in normal tissue and loses the exposure axis while keeping the lineage half; CSPG4 is the largest row in the deposit and is discordant across cohorts (+0.885 GPL6244, -0.189 GPL3290). ⚠ SUPERSEDED 2026-08-10, RETAINED: "the surrogate's negatives transferred and its positives did not", together with every count built on it — "none of the eight surrogate-selective antigens was concordantly elevated on both arrays and two were concordantly lower", "none of eleven therapeutic addresses", and "ALCAM rose on both arrays yet sat below the normal-organ median". The asymmetry was withdrawn rather than restated when the tissue stage was corrected to the same alpha and Benjamini-Hochberg rule the surrogate stage already used: neither supporting negative survives correction (EGFR is lower on one array only at q = 0.044; CD276 reads p = 0.034, q = 0.088 on the one platform that resolves it), CD44 is a direct counterexample, and ALCAM's second array recomputes to t = 2.214 at df 8.5, p = 0.056, 95% interval [-0.024, +1.531], q = 0.162 — elevated on one array and uninformative on the other. The selective set was also re-derived from a pre-specified rule and is 18 rather than eight.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The cheapest possible negative in the entire portfolio: one scan settles it. A cheap decisive negative is worth having now, because it removes a row from the board permanently at almost no cost.

| horizon | effect |
|---|---|
| Six months | None on our side. |
| Two years | An EMC dataset would answer it without anyone scanning. |
| Cost trend | flat |
| Automation outlook | Not automatable; it is a measurement. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-RADIOLIGAND](L1-st-radioligand.md), which is where these are asserted — a family limitation binds every route inside it.*

- Target expression in EMC is unmeasured; the case is currently inherited from neuroendocrine and stromal biology rather than observed in this disease.
- A radioligand target is not a driver, so nothing here would be evidence about the fusion.

## Closure

`authorization` — Not refuted — a negative scan still kills it cheaply, and it stays on the ask list.

## Best next action

Keep on the ask list. Frame it as a cheap decisive negative rather than as a promising lead — that is the honest framing and the one most likely to get it run.

*Cost:* $0

[← ST-RADIOLIGAND](L1-st-radioligand.md) · [← L0](L0-ecosystem.md)
