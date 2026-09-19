---
id: DOC-VIEW-RT-NR2F1
title: RT-NR2F1 — Orphan nuclear-receptor agonism against dormancy escape
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a nuclear receptor other than the driver's be engaged to hold disseminated cells dormant?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-NR2F1 — Orphan nuclear-receptor agonism against dormancy escape

**Family:** [ST-OCCUPANCY](L1-st-occupancy.md) · **state:** ○ blocked · scoped · confidence unknown · verified 2026-09-19

**Grade** (owned by [`research/autonomy/nr2f1-retained-tpm-20260919/RESULT.json`](../../research/autonomy/nr2f1-retained-tpm-20260919/RESULT.json)): Bulk NR2F1 TPM is reported in all nine retained primary EMC specimens: median 0.96, range 0.28–17.86. Cell source, protein and dormancy function remain unestablished. Two array mappings and the fourth assigned-gene panel remain uninformative for NR2F1. The retained C26 assessment is not an experimental pose or affinity known-answer control.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_NR2F1["○ RT-NR2F1"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_NR2F1
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

Whether NR2F1-mediated dormancy is relevant to EMC remains a biological question. The retained C26 assessment supports considering that question separately from computational calibration: its modeled pose and cellular evidence do not supply an experimental receptor-ligand pose or measured binding affinity against which this pipeline can be validated.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CENSUS-ROUTE-GRADING` | a curated dormancy-associated context set scores higher in EMC than in comparator sarcomas on both platforms, while the receptor itself is unreadable on both | `surrogate` |

## Remaining unknowns

- Which cells contribute the reported bulk NR2F1 transcript, and whether the relevant EMC cells express functional NR2F1 protein.
- Whether NR2F1 has a functional role in EMC dormancy and whether modulation changes a relevant outcome.
- Whether an independent experimental receptor-ligand reference appropriate to a proposed NR2F1 pose or affinity calibration is available; the retained assessment supplies none.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Cell-source/protein and functional evidence appropriate to a specific EMC dormancy or modulation claim; the nine-specimen bulk transcript lookup is complete | ⛔ none built | **no** | — |
| An experimental receptor-ligand pose or measured affinity appropriate to the proposed calibration; reproducing the retained docking model is insufficient | ⛔ none built | **no** | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

The fixed nine-specimen transcript lookup answers a descriptive question. It does not test dormancy, drug response or computational calibration, and does not establish a standalone contribution.

**Missing:**
- Evidence resolving relevant cell source, protein and functional dormancy/modulation claims
- An independent experimental reference appropriate to the intended calibration

## Where this route ends — the paper

**[PUB-NR-OUTSIDE-NR4A3](L3-publications.md)** — *Nuclear-receptor pharmacology outside NR4A3 in a NR4A3-driven sarcoma* (unwritten)

`primary` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** An internal record separating the unresolved EMC dormancy hypothesis from the unsupported use of NR2F1/C26 as a computational known-answer control. These retained findings do not establish a standalone paper.

**The paper would claim:** Two nuclear-receptor routes exist in this disease that do not act on its own receptor — one where a 5′ fusion partner imports a druggable transcriptional input, and one targeting dormancy through a receptor that has the published tool compound this program's own receptor never had.

**It is not written because:** ⚠ ITS BLOCKER IS RETIRED AND BOTH ROUTES ARE GRADED, BOTH NEGATIVELY, FOR DIFFERENT REASONS. The dormancy route is UNREAD — its receptor has no probe on either readable platform, an instrument limit that no further expression work can close. The partner route is graded on REACH: a hormone-responsive 5′ partner is reported in one EMC patient in the world literature and in none of the partner-genotyped cases the cited cohorts cover, and the dominant partner has no retrieved druggable input. ⭐ The general mechanism survives and was strengthened by that sweep — the regulatory input a fusion imports is the PARTNER's, never NR4A3's own — which is the claim worth publishing and is a statement about fusion architecture rather than about a drug. ⛔ Superseded, retained: "neither has had its expression lookup run." One has; the other never needed one; and the arithmetic the partner route was waiting on had already been on disk since 2026-08-07.

## Strategic timing — the wait equation

**Recommendation: `wait`**

The retained bulk-expression lookup is complete. Reopen for a distinct source-grounded functional question or relevant cell-resolved/experimental evidence, not another summary of these values.

| horizon | effect |
|---|---|
| Cost trend | falling |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-OCCUPANCY](L1-st-occupancy.md), which is where these are asserted — a family limitation binds every route inside it.*

- Whether the ligand-binding domain is a functional handle in the fusion — whose other end is a strong independent activator — has never been tested by anyone.
- Nobody has stated how much paralogue selectivity this family would need, so 'the requirement is smaller here' is not a claim this repository can make.
- The covalent sub-form's negative result rests on an exposure criterion that fails its own positive control, so it is a rank and not a verdict.

## Best next action

Preserve the nine-specimen descriptive result. Consider new evidence or a specific source-grounded functional question before further route work; do not repeat the completed lookup or use a predicted C26 pose as an experimental known answer.

*Cost:* $0 for evidence intake; no compute dispatch follows from this expression result

[← ST-OCCUPANCY](L1-st-occupancy.md) · [← L0](L0-ecosystem.md)
