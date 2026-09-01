---
id: DOC-VIEW-RT-TRABECTEDIN
title: RT-TRABECTEDIN — Trabectedin (± RT or combination)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Is trabectedin, an approved sarcoma agent, mechanistically well matched to a FET-fusion sarcoma like EMC?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-TRABECTEDIN — Trabectedin (± RT or combination)

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ○ ready · concept · confidence low · verified 2026-09-01

**Grade** (owned by [`research/IDEAS.md`](../../research/IDEAS.md)): NEAR-TERM LEAD — approved, mechanism-fit

## What has to land for this route to move

```mermaid
flowchart LR
  RT_TRABECTEDIN["○ RT-TRABECTEDIN"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_TRABECTEDIN
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

✓ Already cleared by this route: `BLK-PARALOGUE-DDG`, `BLK-TERNARY-GEOMETRY`.

## Scientific rationale

Trabectedin is approved and used in sarcoma, and the argument for it here is mechanistic — it is proposed to displace FET-fusion transcription factors from target promoters, the mechanism invoked for FUS::DDIT3 in myxoid liposarcoma. ⛔ THE EMC CLINICAL RECORD IS SMALL AND CONTAINS NO LOCATED OBJECTIVE RESPONSE. Two independent series report EMC patients treated with trabectedin under formal response assessment and neither records one: Morioka 2016 (PMID 27418251, randomised phase 2 sub-analysis, central radiology review) contributes TWO EMC subjects of a five-subject arm whose other three had mesenchymal chondrosarcoma — both EMC subjects had stable disease, PFS 13.0 and 7.4 months, and the arm's single objective response was an MCS patient; Palmerini 2022 (PMID 36568164, Italian Sarcoma Group TrObs post-hoc, investigator-assessed RECIST 1.1) contributes THREE EMC patients — 0 objective responses, 2 stable, 1 progressive. Located EMC record: 0 objective responses in 5 patients, stated SEPARATELY and NOT pooled (two designs, two populations — POLICY-evidence §2.6). ⛔ THE ~12.5-MONTH MEDIAN PFS PREVIOUSLY QUOTED HERE AS AN EMC FIGURE WAS WITHDRAWN BY THE CITED REGISTRY ON 2026-08-07 AND IS NOT REPLACED BY ANOTHER MEDIAN — it is the Morioka arm's Kaplan-Meier median over all five mixed subjects and coincides with subject 5's own value, also mesenchymal chondrosarcoma. No EMC-specific median PFS exists in the located record. ⚠ The 'impressive response' case in the literature is a RADIOTHERAPY + trabectedin case whose own title claims synergy between the two, so it does not support this route's monotherapy alias; a candidate identifier for it has been located but is UNVERIFIED and is not indexed in PubMed. Denominator, search and every reading: research/literature/emc-trabectedin-denominator-2026-09-01.json. No efficacy, safety, eligibility or clinical-readiness claim is made for EMC, and 0 of 5 is far too small to claim inactivity either.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-EMC-CLINICAL-REGISTRY` | the EMC trabectedin row as CORRECTED on 2026-08-07: n=2 EMC subjects of a 5-subject mixed arm, PRIMARY provenance, orrEvents 0, both stable disease. The registry also records that the arm-wide ~12.5-month median PFS is withdrawn as an EMC figure (treatments.systemicEvidenceCorrections.superseded, row 'Trabectedin'), and its own intro says cytotoxic chemotherapy mainly stabilises disease. ⚠ It does not yet carry the second series (Palmerini 2022, PMID 36568164, EMC n=3, 0 objective responses) — that row is proposed, and until it lands the registry alone understates the located denominator | `direct` |

## Remaining unknowns

- Whether the mechanistic fit is real or a post-hoc story. ⚠ It cannot be a story fitted to a single EMC response, because no objective response in an EMC patient has been located — the fit is argued from myxoid liposarcoma and from disease control.
- How the agent interacts with the fusion's specific programme, which has never been measured in EMC.
- The '± RT' half of this route is unaddressed, and the only claimed impressive-response case is an RT COMBINATION whose identifier is UNVERIFIED and not PubMed-indexed — the registry records radiotherapy in localized EMC as `contested` and adjuvant chemotherapy as `consensus-against`.
- Whether a third Italian series (Chiusole 2020, PMID 32612944 — disease control in 2 of 3 on second-line trabectedin) describes patients already counted in the Italian TrObs post-hoc. Both report 3 EMC patients and 2 of 3 with disease control, and the TrObs enrolment window sits inside Chiusole's. Until that is excluded the rows may not be summed (POLICY-evidence §2.3).

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A larger EMC series, or a measured effect on the fusion's transcriptional output | ⛔ none built | **no** | BLK-NO-EMC-DATA |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Blockers this route RETIRES

- **BLK-PARALOGUE-DDG** — The paralogue ΔΔG margin — selectivity that reduces to exp(−ΔΔG/RT)
- **BLK-TERNARY-GEOMETRY** — Ternary geometry — assembly, E3, exit vector, ubiquitin transfer

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) | combination vs monotherapy | `BLK-NO-EMC-DATA` | monotherapy rests on two small disease-control series with 0 located objective responses in EMC, NOT on the RT-combination case (whose identifier is unverified) and a mechanism fit; the combination rests additionally on a published result in a sibling sarcoma and on the fusion→PPARG axis |
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) | unbiased screen hit vs mechanism-fit argument | `BLK-NO-EMC-DATA` | trabectedin is argued from mechanism fit plus small clinical disease-control series (0 objective responses located in 5 EMC patients); carfilzomib is an empirical ex-vivo screen hit with no fusion rationale |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) | whether the closure is about molecular selectivity or about clinical activity | `BLK-CLASS-INHERITANCE` | this route stays live because its claim is clinical activity; RT-HDAC-BET is closed only on the fusion-SELECTIVITY claim, and both are chromatin-acting and neither is molecularly fusion-selective |

## Readiness — what this could become today

**`internal_note`**

This is clinical-evidence synthesis rather than a computational contribution. It belongs as landscape context in a paper, not as a result.

**Missing:**
- a larger EMC series — the located record is 5 patients across two series with 0 objective responses
- the second series (Palmerini 2022, PMID 36568164) as a curated registry row, and an EV-/ART- id for it so this route can cite it directly rather than in prose

## Where this route ends — the paper

**[PUB-EMC-PROGRAM](L3-publications.md)** — [Attacking an "undruggable" fusion oncoprotein by computation alone: a driver-directed treatment program for EWSR1::NR4A3](../../research/manuscripts/program/emc-treatment-roadmap.md)

`context` · ◐ `drafted` · aimed at `journal_submission`

**This route contributes:** Cited to establish current care and the categorical gap. Explicitly not this program's contribution — it is clinical-evidence synthesis. ⛔ There is no single EMC response to overstate: the located record is 0 objective responses in 5 EMC patients across two series.

**The paper would claim:** The gap in EMC care is categorical rather than a matter of degree — nothing in clinical use addresses the driver — and a computation-only program can enumerate the driver-directed routes, state a falsifiable kill criterion for each, and place the borrowed standard-of-care agents as context rather than as its own contribution.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Nothing computational advances it. Its role is as the near-term comparator any new route has to beat, which is a role it plays without further work.

| horizon | effect |
|---|---|
| Six months | Only via new clinical reports. |
| Two years | Same. |
| Cost trend | flat |
| Automation outlook | Literature monitoring is already automated. |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Best next action

Keep as cited landscape context, at the weight the record supports: disease control in a handful of EMC patients, 0 objective responses located in 5, and no EMC-specific median PFS. ⛔ Do not quote ~12.5 months as an EMC figure and do not write 'EMC responder'. Free next step: curate Palmerini 2022 (PMID 36568164) into the registry.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-FUS-T1](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 evidence:** [EV-PALMERINI-2022](L5-evidence-base.md#evidence--the-literature-this-program-cites)

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
