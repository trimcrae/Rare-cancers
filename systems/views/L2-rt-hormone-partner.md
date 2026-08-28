---
id: DOC-VIEW-RT-HORMONE-PARTNER
title: RT-HORMONE-PARTNER — Hormonal therapy for hormone-responsive 5′ fusion partners
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Can a hormone-responsive 5′ fusion partner import a druggable transcriptional input that the driver does not otherwise offer?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-HORMONE-PARTNER — Hormonal therapy for hormone-responsive 5′ fusion partners

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ parked · computed · confidence moderate · verified 2026-08-28

**Grade** (owned by [`research/modalities/hormone-partner-lane.json`](../../research/modalities/hormone-partner-lane.json)): ⛔ THE PRINCIPLE SURVIVES AND THE REACH DOES NOT (graded 2026-08-09 from a lane that ran 2026-08-07). A hormone-responsive 5′ partner is reported in ONE EMC patient in the world literature and in ZERO of the 84 partner-genotyped EMC cases across the two cohorts this repository cites — Wilson 95% upper bound 4.4%. The dominant partner, which carries roughly four in five cases, answers NO: across 345 retrieved full-text records no source characterises the EWSR1 promoter as responsive to any druggable stimulus. ⭐ What survives is the general mechanism, which the sweep strengthened rather than merely repeated: across every partner retrieved, the imported regulatory input is the PARTNER's and never NR4A3's own — 12 partners across 3 tumour types, including a second disease where the imported element is an enhancer. ⭐ THE LAST UNGRADED PARTNER IS NOW GRADED, AND IT ANSWERS NO (2026-08-28). HSPA8 — the one partner whose gene family plausibly carried an inducible element — has no reported hormone response element in its promoter. Across every PubMed record returned by three intersecting queries, read exhaustively (7 on the HSC70/HSPA8 promoter, 8 on hormone-response-element language, 13 on the intersection), the only cis-elements ever localised in a mammalian hsc70 promoter are Sp1 sites, and the one inducible input ever mapped there is ETHANOL. ⛔ THE DISCRIMINATING RECORD IS THE ONE THAT DOES FIND AN OESTROGEN LINK: in a human ER-positive line the mapped site is the HSPA8 3′UTR, reached by an oestrogen-regulated microRNA — a segment an HSPA8::NR4A fusion transcript does not carry, because such a fusion takes its 3′ end from the NR4A gene. ⚠ This is a RETRIEVAL negative, not a measurement: nobody has asked whether the human HSPA8 promoter contains an ERE. Grade and every identifier: ART-HSPA8-PROMOTER-GRADE.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_HORMONE_PARTNER["✓ RT-HORMONE-PARTNER"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_HORMONE_PARTNER
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

A 5′ partner can bring its own promoter and its own regulation, and the repository already holds a reported instance of exactly that with durable benefit on an approved agent. No hormonal route exists among the forty-three, which makes this a registered lane with nowhere to live.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `ART-HORMONE-PARTNER-LANE` | the hormone-responsive-partner fraction in EMC is zero of 84 partner-genotyped cases with a Wilson 95% upper bound of 4.4%, and no retrieved source gives the dominant partner's promoter a druggable inducible input | `direct` |
| `ART-HSPA8-PROMOTER-GRADE` | the HSPA8 promoter is not characterised anywhere in PubMed-indexed literature as carrying a hormone response element or as driven by a nuclear-receptor ligand, so the route's last ungraded partner imports no druggable hormonal input | `direct` |

## Remaining unknowns

- Whether an unbiased RNA-seq-genotyped EMC series would move the reach figure in either direction — the cited denominators come from targeted assays that one of the source reports states would have missed its own case, and this is the single observation that could move it.
- ⭐ ANSWERED 2026-08-28, AND THE ANSWER IS NO. Superseded, retained: "Whether the one partner whose gene family plausibly carries a druggable inducible input (HSPA8) has one, which is ungraded because nothing was retrieved for it." It is no longer ungraded — ART-HSPA8-PROMOTER-GRADE records the retrieval. ⚠ WHAT REPLACES IT IS A NARROWER UNKNOWN AND IT IS REAL: whether the human HSPA8 promoter contains a hormone response element NOBODY HAS LOOKED FOR. Every study that dissected that promoter was asking about something else — ethanol, oxidative stress, a cystic-fibrosis corrector, a transgenic cassette — so the absence is an absence of asking, not a measured negative. A response-element scan of the promoter sequence, or a nuclear-receptor cistrome read at the HSPA8 TSS, would close it and neither was run.
- Whether any anti-oestrogen outcome exists in a hormone-partnered UTERINE tumour, which would take the axis past n = 1 in a different disease.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| ⛔ TAKEN 2026-08-07 and returned a negative — the pooled hormone-responsive partner fraction across the partner-genotyped series curated here | ⛔ none built | yes | — |
| ⛔ TAKEN 2026-08-28 and returned a negative — the targeted literature query for whether the HSPA8 promoter carries a druggable inducible element, the last partner left ungraded. No hormone response element is reported; the promoter's only localised cis-elements are Sp1 sites. ART-HSPA8-PROMOTER-GRADE. | ⛔ none built | yes | — |
| Confirmation that a partner's promoter drives the fusion in a hormone-dependent way | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Blockers

| blocker | kind | what would retire it |
|---|---|---|
| **BLK-NO-EMC-DATA** | `insufficient_data` | `TECH-EMC-EXPRESSION-DATA`, `TECH-VIRTUAL-CELL` |

## Readiness — what this could become today

**`internal_note`**

The route's own sizing question was asked and answered against it. What is left is a paragraph in a paper, not a lane.

**Missing:**
- nothing at the arithmetic level — the pooled fraction was computed and is a negative

## Where this route ends — the paper

**[PUB-NR-OUTSIDE-NR4A3](L3-publications.md)** — *Nuclear-receptor pharmacology outside NR4A3 in a NR4A3-driven sarcoma* (unwritten)

`primary` · ◔ `outlined` · aimed at `preprint`

**This route contributes:** The half of the paper where the druggable input is imported by the 5′ partner rather than supplied by the driver's own receptor.

**The paper would claim:** Two nuclear-receptor routes exist in this disease that do not act on its own receptor — one where a 5′ fusion partner imports a druggable transcriptional input, and one targeting dormancy through a receptor that has the published tool compound this program's own receptor never had.

**It is not written because:** ⚠ ITS BLOCKER IS RETIRED AND BOTH ROUTES ARE GRADED, BOTH NEGATIVELY, FOR DIFFERENT REASONS. The dormancy route is UNREAD — its receptor has no probe on either readable platform, an instrument limit that no further expression work can close. The partner route is graded on REACH: a hormone-responsive 5′ partner is reported in one EMC patient in the world literature and in none of the partner-genotyped cases the cited cohorts cover, and the dominant partner has no retrieved druggable input. ⭐ The general mechanism survives and was strengthened by that sweep — the regulatory input a fusion imports is the PARTNER's, never NR4A3's own — which is the claim worth publishing and is a statement about fusion architecture rather than about a drug. ⛔ Superseded, retained: "neither has had its expression lookup run." One has; the other never needed one; and the arithmetic the partner route was waiting on had already been on disk since 2026-08-07.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Only somebody else's RNA-seq-genotyped series could move the reach figure, and that data is not this programme's to generate.

| horizon | effect |
|---|---|
| Cost trend | flat |

**Revisit when:**
- **TECH-EMC-EXPRESSION-DATA** — A fetchable public EMC RNA-seq or proteomics deposit beyond the single existing model, enabling a target-regulon readout and per-a *(expected 2029, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Best next action

⭐ THE $0 STEP THIS FIELD NAMED IS DONE (2026-08-28) AND THE ROUTE IS NOW GENUINELY PARKED. Superseded, retained: "Run the one $0 Europe PMC query on the HSPA8 promoter to close the last ungraded partner, then report the reach negative in the nuclear-receptor paper." ⚠ THAT SENTENCE IS WHY THIS ROUTE WAS MIS-PARKED: it named a takeable free step beside `status: parked`, and once the queue began trusting `state.status` the route was hidden with the step still open (AUT-PD-086). The query was run — through PubMed rather than Europe PMC, which 403s at this sandbox's egress — and it returned NO. What is left is a paragraph in PUB-NR-OUTSIDE-NR4A3, not a lane: no validation this route names is both open and feasible today, the wet-lab confirmation is blocked by BLK-NO-WET-LAB, and only somebody else's RNA-seq-genotyped EMC series (TECH-EMC-EXPRESSION-DATA) can move the reach figure.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
