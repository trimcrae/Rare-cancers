---
id: DOC-VIEW-RT-CHAPERONE
title: RT-CHAPERONE — Chaperone dependency of the chimera (HSP90 and co-chaperones)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is the chimeric protein more dependent on the chaperone system than the wild-type proteins it is assembled from?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-CHAPERONE — Chaperone dependency of the chimera (HSP90 and co-chaperones)

**Family:** [ST-DEPENDENCY](L1-st-dependency.md) · **state:** ○ blocked · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/cancer-modality-census.md`](../../research/manuscripts/cancer-modality-census.md#31--transcriptional-and-proteostatic-dependency)): ⭑ Registered 2026-08-09 from the modality census; concept maturity, nothing run. The class's toxicity record is a stated liability rather than a footnote.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_CHAPERONE["○ RT-CHAPERONE"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_CHAPERONE
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

A structural argument nobody here had made. Chimeric proteins are disproportionately chaperone-dependent for folding and stability, which offers a way to lower fusion protein levels that needs no pocket ligand, no assembled ternary complex and no paralogue discrimination — the three blockers holding this portfolio's largest family down.

## Remaining unknowns

- Whether the chimera is in fact more chaperone-dependent than wild-type NR4A3 and wild-type EWSR1, which is the premise and has never been tested for this fusion.
- Nothing here assumes a therapeutic window exists for a class whose clinical record is dominated by toxicity; whether one could is a question about the class rather than about this disease, and it is not settled anywhere.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A literature assessment of chaperone clientship across FET-family fusion proteins | ⛔ none built | yes | — |
| A structural assessment of whether the junction region is predicted to be unstable or disordered, using the structural work already committed here | ⛔ none built | yes | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

Nothing has been run. This route was registered on 2026-08-09 from the modality census and is at concept maturity, so the only honest output today is the question and its cheapest next observation.

**Missing:**
- the chaperone-clientship literature assessment, which is $0

## Where this route ends — the paper

**[PUB-TXN-DEPENDENCY](L3-publications.md)** — *Transcriptional and proteostatic dependency of a fusion transcription factor: what a no-wet-lab program can and cannot establish* (unwritten)

`primary` · ○ `unwritten` · aimed at `preprint`

**This route contributes:** The half of the paper that argues from what the driver IS STRUCTURALLY: a chimera of two domains that never evolved together is a folding problem before it is a signalling one.

**The paper would claim:** A fusion oncoprotein whose entire mechanism is transactivation, and whose structure is a chimera of two domains that never evolved together, predicts dependencies on the transcriptional machinery and on the chaperone system — and neither had ever been assessed in this disease despite both being standard vulnerabilities of its tumour class.

**It is not written because:** The two classes it would cover were identified on 2026-08-09 and neither has had its cheapest observation yet, so there is no result to write up — only a stated gap and a protocol for closing it.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The next step costs nothing and needs nobody's cooperation, so there is no reason to defer it; what it returns decides whether this route is worth more than a row.

| horizon | effect |
|---|---|
| Cost trend | flat |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DEPENDENCY](L1-st-dependency.md), which is where these are asserted — a family limitation binds every route inside it.*

- The dependency transfer prior came back negative on the available data — a measured premise, revivable only by EMC-specific data.
- One route rests on class inheritance: no NR4A3 fusion has been tested for the phenotype it assumes.
- There is one EMC model in public dependency data, with no CRISPR data, so this family's in-silico half is bounded by a sample size of one.

## Best next action

Assess chaperone clientship for FET-family fusion proteins in the literature, and check whether this repository's own structural work predicts an unstable junction interface.

*Cost:* $0

[← ST-DEPENDENCY](L1-st-dependency.md) · [← L0](L0-ecosystem.md)
