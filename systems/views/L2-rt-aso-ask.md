---
id: DOC-VIEW-RT-ASO-ASK
title: RT-ASO-ASK — Junction knockdown + parental sparing in EMC lines (the ask behind the ASO)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can junction knockdown be shown to spare the wild-type parents, and does losing the fusion kill EMC cells? ⚠ The sparing half CANNOT be shown in an EMC line alone — EMC cells may express little wild-type NR4A3, so 'sparing' is unmeasurable where the wild-type transcript is near-absent.
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-ASO-ASK — Junction knockdown + parental sparing in EMC lines (the ask behind the ASO)

**Family:** [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · **state:** ○ blocked · scoped · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/program/emc-post-degrader-options.md`](../../research/manuscripts/program/emc-post-degrader-options.md)): Tier 2, rank 6 — ASK

## What has to land for this route to move

```mermaid
flowchart LR
  RT_ASO_ASK["○ RT-ASO-ASK"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_ASO_ASK
  TECH_EMC_EXPRESSION_DATA(["TECH-EMC-EXPRESSION-DATA<br/>expected 2029"]):::tech
  TECH_EMC_EXPRESSION_DATA -.-> BLK_NO_EMC_DATA
  TECH_VIRTUAL_CELL(["TECH-VIRTUAL-CELL<br/>expected 2028"]):::tech
  TECH_VIRTUAL_CELL -.-> BLK_NO_EMC_DATA
  BLK_NO_WET_LAB{{"BLK-NO-WET-LAB — No wet lab and no collaborator — an ask…"}}:::blk
  BLK_NO_WET_LAB --> RT_ASO_ASK
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

This is the single experiment that would convert the oligonucleotide route from a design into a result. It is small, cheap for anyone who already has the cells, and its outcome is informative in both directions. It is registered as a route because an ask with no owner is not a plan.

## Remaining unknowns

- Whether anyone with an EMC or FET-fusion line is interested enough to run it.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| Junction knockdown and the phenotype arm, in an EMC line — with a fusion-negative line as control (fusion-junction-aso-working-record.md §4) | ⛔ none built | **no** | BLK-NO-WET-LAB |
| PARENTAL SPARING, in an engineered or isogenic fusion-positive model carrying abundant wild-type NR4A3 AND EWSR1, with single-parent-targeting ASOs as positive controls. A scrambled control tests sequence-independent toxicity, not discrimination (red-team F7) | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-WET-LAB** | `requires_external_collaboration` | `TECH-CLOUD-WET-LAB`, `TECH-EMC-MODEL-ACCESS` |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-ASO](L2-rt-aso.md) | deliverable vs ask | `BLK-DELIVERY` | the paper is unaffected by this ask failing — the one ask in the portfolio whose failure costs its route nothing |
| [RT-ATR-PANEL](L2-rt-atr-panel.md) | which ask spends the one relationship | `BLK-NO-WET-LAB` | ⚠ THIS ASK AND RT-ASO-ASK SPEND THE SAME SCARCE INPUT. Both address the same two model-holding groups (USZ Zurich and NCC Japan), both are `pursue_now` at `$0`, and BLK-NO-WET-LAB is `requires_external_collaboration` — the scarce resource is a RELATIONSHIP, not money. Two $0 asks to one relationship are not independent: a declined first ask prices the second. Eleven routes sit behind TR-EMC-MODEL-ACCESS. The ordering is trimcrae's outward-facing call and is recorded nowhere. |

## Readiness — what this could become today

**`experimental_proposal`**

It is a specified but UNCOSTED experimental proposal (fusion-junction-aso-working-record.md §4). What it lacks is a taker, and no amount of further specification produces one.

**Missing:**
- a collaborator with an EMC or FET-fusion line
- an engineered or isogenic fusion-positive model expressing abundant wild-type NR4A3 and EWSR1 — an EMC line alone cannot carry the sparing claim
- single-parent-targeting positive-control oligos

**Experiment required:**
- junction-spanning qPCR/RNA-seq plus fusion protein readout
- allele- or exon-resolved wild-type EWSR1 and NR4A3 quantitation
- viability/apoptosis for the phenotype arm
- an engineered/isogenic fusion-positive model with abundant wild-type parents, plus single-parent-targeting positive-control oligos (red-team F7)

## Where this route ends — the paper

**[PUB-ASO](L3-publications.md)** — [NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment](../../research/manuscripts/aso/fusion-junction-aso-journal-article.md)

`contributing` · ◉ `posted_preprint` · aimed at `journal_submission`

**This route contributes:** The decisive experiment, specified inside the paper and sent with it: junction knockdown with wild-type sparing in an EMC line. Without it the paper states a specificity result with no named way to falsify it at a bench.

**The paper would claim:** The NR4A3 fusion junction is the one tumour-exclusive feature of this disease at the RNA level, and two junction-spanning gapmers are named for synthesis against it: 5'-GGGCATATCATCAAAC-3' at EWSR1 exon 12 and 5'-GGGCATATCTTGTGTG-3' at TAF15 exon 6, the best available designs at the two most frequently reported breakpoints. They are what survives a screen that condemns most of the panel: 87 of 190 junction-spanning designs let a mature wild-type parent transcript pair their whole catalytic gap over at least ten contiguous base pairs, 61 of them against wild-type NR4A3 itself, and lengthening the catalytic gap raises the margin available only by conceding parent-paired gap DNA, for an arithmetic rather than an empirical reason. Two fusion-positive patient-derived EMC models and two engineered constructs carrying these junctions are named as test articles, the controls and pre-registrable decision threshold for the falsifying experiment are stated, and the design pipeline is released for breakpoints outside the panel. Delivery is named as an outstanding gate rather than assumed away, the named reagents carry stated parent-duplex and off-target loads, and nothing here has been synthesised or tested.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The proposal is written and the cost to ask is zero. An ask that is never made has the same outcome as one that is refused, at the same price.

| horizon | effect |
|---|---|
| Six months | Only through whoever reads the preprint. |
| Two years | A solo-affordable cloud lab with the right assay scope would remove the need for a taker entirely — though not the need for the cell line. |
| Cost trend | falling |
| Automation outlook | Not automatable today; this is precisely what a cloud lab would change. |

**Revisit when:**
- **TECH-EMC-MODEL-ACCESS** — Access to a patient-derived EMC model through a collaborator, or through a solo-affordable cloud or robotic wet-lab service with E *(expected 2029, basis `speculative`)*
- **TECH-CLOUD-WET-LAB** — A remote robotic or cloud wet lab, rentable per experiment by an unaffiliated researcher, at a price and assay scope that covers E *(expected 2029, basis `extrapolated`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-NUCLEIC-ACID](L1-st-nucleic-acid.md), which is where these are asserted — a family limitation binds every route inside it.*

- Delivery of an oligonucleotide to a non-hepatic solid tumour has no validated solution, and this is not solvable in silico today.
- Predicted specificity rests in part on a conservative heuristic rather than a calibrated cleavage-activity model.
- The vector-delivered sub-routes carry a second, distinct delivery problem that must not be conflated with the oligonucleotide one.

## Closure

`authorization` — Not refuted — waiting on a person with a bench.

## Best next action

Send the ask alongside the preprint. The proposal is ready; the missing input is a person.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-EWSR1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A3-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

[← ST-NUCLEIC-ACID](L1-st-nucleic-acid.md) · [← L0](L0-ecosystem.md)
