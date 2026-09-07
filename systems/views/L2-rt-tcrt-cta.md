---
id: DOC-VIEW-RT-TCRT-CTA
title: RT-TCRT-CTA — TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could engineered T cells against a cancer-testis antigen be ported to EMC, as was done in synovial sarcoma?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-TCRT-CTA — TCR-T / engineered T cells vs a cancer-testis antigen (synovial-sarcoma port)

**Family:** [ST-IMMUNO](L1-st-immuno.md) · **state:** ✓ parked · computed · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/neoantigen/immunotherapy-options-emc.md`](../../research/manuscripts/neoantigen/immunotherapy-options-emc.md)): DOWNGRADED to weak — gating fact resolved, mostly negative

## What has to land for this route to move

```mermaid
flowchart LR
  RT_TCRT_CTA["✓ RT-TCRT-CTA"]:::fam
  BLK_ANTIGEN_COLD[["BLK-ANTIGEN-COLD — EMC is antigen-cold, and the fusion ju…"]]:::perm
  BLK_ANTIGEN_COLD --> RT_TCRT_CTA
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_TCRT_CTA
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

⛔ **1 of these is permanent** (`BLK-ANTIGEN-COLD`) — a fact about the biology, drawn double-walled, with no way out by definition. No technology arrives to fix it.

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

The synovial-sarcoma precedent shows the approach works in a translocation sarcoma, and porting an approved approach is far cheaper than inventing one.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-CTA-EXPRESSION` | EMC is cancer-testis-antigen-low on the available measured data | `surrogate` |
| `ART-EMC-EXPRESSION-PANELS` | The EMC expression series required_validation[0] asked for, and the reason its antigens are still unread: cross_platform_board.by_state.NOT_READABLE_ON_EITHER_PLATFORM lists CTAG1B, MAGEA3 and SSX2. | `direct` |

## Remaining unknowns

- Whether a real EMC series would agree with the surrogate measurement that downgraded this.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A real EMC expression series  ⭐ ADJUDICATED 2026-09-02 (AUT-PD-116, seat s31-emc-data-blocks). SATISFIED AS WRITTEN — and this is the one entry in the population that is. Three EMC tumour series are now read: the two arrays in `ART-EMC-EXPRESSION-PANELS` (`platforms`, licensed by `reads.control`) and the fourth cohort. ⛔ AND THE ANSWER THE SERIES WAS WANTED FOR IS STILL UNREAD: CTAG1B, MAGEA3 and SSX2 all sit in `reads.read_8_SURFACE_ANTIGEN.cross_platform_board.by_state.NOT_READABLE_ON_EITHER_PLATFORM`, and none of the three has an assigned probe in the fourth cohort's committed gene table. That is an instrument state on three instruments and NEVER a negative about the tumour, so this entry's satisfaction is a fact about the RECORD and moves nothing about the route's science. ⚠ `readiness.missing` still reads "a real EMC expression series" and now disagrees with this entry; that field belongs to the route's grade owner and is left visibly disagreeing rather than papered over. ⚠ THE RULE THIS APPLIES, THE FOURTH COHORT'S DESIGN AND LIMITS, AND THE PER-GENE COVERAGE ALL HAVE ONE HOME AND ARE NOT RESTATED HERE: research/modalities/emc-fourth-cohort-route-readout.json — its "⭐ the_rule_this_adjudication_applies" field, its cohort block, and per_route.RT-TCRT-CTA. | ⛔ none built | yes | — |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-ANTIGEN-COLD** | `fundamental_biological_limit` | *permanent* |
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) | which CTA | `BLK-NO-EMC-DATA` | EMC is NY-ESO-1-rare and MAGE-A4-low on measured data; PRAME is separately expressed and separately graded |

## Readiness — what this could become today

**`internal_note`**

Downgraded on a measurement rather than on reasoning, which is the useful kind of downgrade — but it means the route needs a better measurement, not a better argument.

**Missing:**
- a real EMC expression series

## Where this route ends — the paper

**[PUB-SURFACE-TARGETS](L3-publications.md)** — [Fixed-panel tissue RNA prioritization in extraskeletal myxoid chondrosarcoma](../../research/manuscripts/surface-targets/emc-tissue-rna-prioritization.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The cancer-testis antigen arm ported from synovial sarcoma, downgraded on a measurement rather than on an argument.

**The paper would claim:** A fixed panel of 11 therapeutic-address genes, with CHRNA6 as a separate established RNA-marker control, can be assessed using within-cohort tissue RNA ranks and prespecified sarcoma comparators. In the overlap-reduced Hofvander cohort of nine primary EMC specimens, CSPG4 alone meets the frozen tissue-validation allocation rule; its LGFMS contrast agrees with the original GSE24369 array contrast, but year-deletion sensitivity and DFSP context limit generalization. This supports a qualified rationale for EMC tissue protein and compartment validation, not validated surface expression, normal sparing, treatment selection or efficacy. All other fixed-panel results and discordant protein/normal-context evidence are retained.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

The gating fact was resolved and came back mostly negative. Only better data reopens it, and that data is watched.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | Only via an EMC dataset. |
| Cost trend | flat |
| Automation outlook | Re-grading would be automatic once data lands. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-IMMUNO](L1-st-immuno.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is antigen-cold and the fusion junction is a weak peptide-HLA — a property of this tumour and this junction, not of any modality here.
- Surface-antigen selectivity was measured on cell-line surrogates rather than on EMC tissue, so the negatives are as provisional as the positives would have been.
- One route's predicted binders span junction seams that a corrected exon index says do not exist; that result is void and the question is open.

## Closure

`premise_false` — EMC is CTA-low on measured data; a real EMC series is what could change it.

## Best next action

Keep registered for automatic re-grade when EMC expression data lands. ⛔ CORRECTED 2026-09-02 (AUT-PD-116): three EMC tumour series are now read and the re-grade this field promised cannot be taken from any of them — CTAG1B, MAGEA3 and SSX2 are unreadable on both arrays and have no assigned probe in the fourth cohort. ⚠ Superseded, retained: "Keep registered for automatic re-grade when EMC expression data lands." The live next step is a CTA-covering instrument, not another cohort.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

| L4 instrument | cited as | known-answer control |
|---|---|---|
| [INS-HLA-COVERAGE](registers/instruments.md) — HLA population-coverage calculator | **disclosed failing** | `none` |

**L5 artifacts:** [ART-HLA-COVERAGE](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-IMMUNO](L1-st-immuno.md) · [← L0](L0-ecosystem.md)
