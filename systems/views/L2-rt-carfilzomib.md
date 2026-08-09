---
id: DOC-VIEW-RT-CARFILZOMIB
title: RT-CARFILZOMIB — Carfilzomib ± anthracycline (± venetoclax)
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Does the best ex-vivo EMC drug-sensitivity evidence point at a proteasome inhibitor combination?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-CARFILZOMIB — Carfilzomib ± anthracycline (± venetoclax)

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ○ ready · concept · confidence low · verified 2026-08-09

**Grade** (owned by [`research/manuscripts/repurposing-hypotheses.md`](../../research/manuscripts/repurposing-hypotheses.md)): ◐ THE OBSERVATION STANDS AND BOTH IN-SILICO RATIONALES FOR IT FAILED (regraded 2026-08-09, first time this route's axis has ever been read). ⭐ WHAT IS UNCHANGED AND IS STILL THIS PORTFOLIO'S BEST EVIDENCE: carfilzomib, with venetoclax, was active across two PATIENT-DERIVED EMC models. It is the only agent in this programme measured on cells that carry this disease, and nothing below touches that. ⛔ DEPENDENCY SAYS THERE IS NOTHING TO SELECT ON. Across the 91 screened sarcoma lines PSMB1, PSMC1, PSMD1 and VCP are dependencies in 100%, and carfilzomib's own target PSMB5 in 97.8%, with selectivity against the rest of DepMap between -0.10 and +0.17. A target required in every line of the class and equally required outside it cannot be the basis of a selective argument. SQSTM1 at 0% and NFE2L1 at 7.7% are the internal control and behave. ⛔ AND THE PROTEOSTATIC-LOAD EXPLANATION IS NOT SUPPORTED. Read 18 was built to test whether this myxoid, matrix-secreting tumour carries the folding and disposal burden that would make degradative capacity limiting, with the grading rule written and committed BEFORE the fetch returned. On the 35-tumour platform the rule fired on the unfolded-protein response (+2.11) while the secretory/matrix-load proxy - the module carrying the actual argument - was FLAT at -0.20; on the 16-tumour platform everything was null. ⚠ IT STAYS OPEN because the ex-vivo result is a measurement in the right cells and outranks two failed in-silico rationales for it; what has collapsed is the case for SELECTIVITY, not the observation. Confidence drops from moderate to low. Superseded, retained: 'NEAR-TERM LEAD - best ex-vivo EMC evidence', which was graded 2026-08-05 before any of this was measured.

## What has to land for this route to move

```mermaid
flowchart LR
  RT_CARFILZOMIB["○ RT-CARFILZOMIB"]:::fam
  BLK_NO_EMC_DATA{{"BLK-NO-EMC-DATA — EMC is nearly absent from public functi…"}}:::blk
  BLK_NO_EMC_DATA --> RT_CARFILZOMIB
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

This carries the best ex-vivo EMC drug-sensitivity evidence in the repository — an actual measurement on actual EMC material, which is rarer than anything else in this family. An approved agent with an ex-vivo signal is a strong near-term lead by the standards available for this disease.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `EV-BANGERTER-2023` | ex-vivo drug sensitivity measured on EMC material: carfilzomib high sensitivity VALIDATED IN BOTH USZ20-EMC1 and USZ22-EMC2 (triplicate 6-point dose-response). ⚠ Scope: the 40-drug discovery panel ran on USZ20-EMC1 ALONE, and venetoclax showed NO monotherapy response — it enters only through combination additivity/synergy. | `direct` |

## Remaining unknowns

- Whether ex-vivo sensitivity transfers to clinical benefit, which it frequently does not.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A clinical series | ⛔ none built | **no** | BLK-NO-EMC-DATA |

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
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) | unbiased screen hit vs mechanism-fit argument | `BLK-NO-EMC-DATA` | carfilzomib is an empirical ex-vivo hit with NO fusion rationale; trabectedin is argued from mechanism fit and a clinical series. Same family, same status, same blocker, opposite kinds of support |

## Readiness — what this could become today

**`internal_note`**

The evidence is ex-vivo on n=2 patient-derived models with no in-vivo and no clinical data in EMC. That is the ceiling — not a citation gap; the primary identifier was resolved 2026-08-05 (PMID 36316541 / PMC9813045, integrity.json OC-4).

## Where this route ends — the paper

**[PUB-REPURPOSING](L3-publications.md)** — [Mechanism-based drug-repurposing hypotheses for extraskeletal myxoid chondrosarcoma](../../research/manuscripts/repurposing-hypotheses.md)

`primary` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** The proteasome-inhibitor hypothesis and the ex-vivo EMC evidence behind it — the only ex-vivo EMC result in the portfolio, and currently the paper's weakest citation.

**The paper would claim:** Existing agents not yet reported in EMC can be mapped to EMC's molecular and microenvironmental axes by three independent methods, each candidate graded by an explicit evidence tier — a hypothesis-generating menu that asserts no efficacy for any agent it names.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

The ex-vivo result is committed and its citation resolved. What is missing is in-vivo or clinical evidence in EMC, which this program cannot generate.

| horizon | effect |
|---|---|
| Six months | None. |
| Two years | None on the citation; a clinical series would change the route. |
| Cost trend | flat |
| Automation outlook | The literature lookup is automatable and is already wired. |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Best next action

Treat as landscape context; the ex-vivo result is banked and needs no further lookup.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 evidence:** [EV-BANGERTER-2023](L5-evidence-base.md#evidence--the-literature-this-program-cites)

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
