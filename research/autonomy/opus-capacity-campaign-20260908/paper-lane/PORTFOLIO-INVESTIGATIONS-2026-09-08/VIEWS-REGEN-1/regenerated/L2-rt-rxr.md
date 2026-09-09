---
id: DOC-VIEW-RT-RXR
title: RT-RXR — RXR-heterodimer modulation of the fusion
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Could modulating an RXR heterodimer change the fusion's activity?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-RXR — RXR-heterodimer modulation of the fusion

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ parked · scoped · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/program/emc-post-degrader-options.md`](../../research/manuscripts/program/emc-post-degrader-options.md)): ✕ CLOSED 2026-08-03 — NR4A3 does not heterodimerise with RXR

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

Registered with its closing measurement. Nuclear receptors commonly act as RXR heterodimers, which would give a well-precedented pharmacological handle — but the published evidence is that this receptor does not form a permissive heterodimer with RXR.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `EV-ZETTERSTROM-1996` | NOR-1/NR4A3 is unable to form heterodimers with RXR, measured on the receptor itself — the published primary negative the closure rests on. ⚠ Measured on WILD-TYPE NOR-1; the transfer to the chimera holds because the LBD is byte-identical in both and the fusion alters only the N-terminal region. | `direct` |

## Remaining unknowns

- Whether the published negative is correct. It is a direct measurement, so only a contradicting primary measurement of the same fact reopens this — no method advance does.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A primary measurement contradicting the published negative | ⛔ none built | **no** | BLK-NO-WET-LAB |

## Not to be confused with

| route | the axis it turns on | blockers the distinction turns on | why |
|---|---|---|---|
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | which receptor's dimer is being modulated | `BLK-NO-EMC-DATA` | this closes an NR4A3:RXR dimer that does not form. It says NOTHING about PPARγ:RXR biology downstream of the fusion, which is a different dimer and a live route |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) | which receptor's dimer is being modulated | `BLK-NO-EMC-DATA` | same scoping — the closed dimer is NR4A3:RXR, not the PPARγ:RXR axis this route's agonist half acts on |

## Readiness — what this could become today

**`internal_note`**

Closed on a published measurement; the output is the closure and its citation.

## Where this route ends — the paper

**[PUB-CLOSED-ROUTES](L3-publications.md)** — [Seven routes closed on argument rather than on experiment — the negative record of an EWSR1::NR4A3 route search](../../research/manuscripts/methods-record/closed-routes-negative-record.md)

`contributing` · ◐ `drafted` · aimed at `preprint`

**This route contributes:** A closure resting on a published measurement rather than on argument, with the one observation that would reopen it named and scanned for.

**The paper would claim:** A route can be closed rigorously without an experiment when the closure is definitional or is arithmetic over a fixed measured fact, and separating those permanent closures from the merely instrument-limited ones is what keeps a portfolio from re-litigating settled questions — with wild-type NR4A3 pharmacology failing to transfer to the chimera as the worked example.

## Strategic timing — the wait equation

**Recommendation: `monitor`**

Closed on the receptor's own measured biology. It is `premise_false` and not `definitional`, so a contradicting primary measurement would reopen it — which is why it keeps a trigger rather than none.

**Revisit when:**
- **TECH-RXR-HETERODIMER-REPORT** — A primary report of NR4A3 forming a permissive or ligand-modulable heterodimer with RXR in cells, contradicting the published nega *(expected beyond-2031, basis `speculative`)*

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-REPURPOSING](L1-st-repurposing.md), which is where these are asserted — a family limitation binds every route inside it.*

- EMC is nearly absent from public functional-genomics data, so mechanism fit is argued from class membership rather than measured in this disease.
- Several routes here rest on a direction of effect that has never been read in EMC tissue; an expression readout would settle them cheaply and does not exist.
- A repurposing hypothesis is a hypothesis. Nothing here asserts efficacy in EMC.

## Closure

`premise_false` — Closed on the receptor's own measured biology. Not definitional — it rests on a published measurement, so a contradicting primary measurement is the only thing that reopens it, and no method advance does.

## Best next action

Nothing. The scan carries the one observation that would reopen it.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

**L5 objects:** [OBJ-NR4A1-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A2-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about), [OBJ-NR4A3-WT](L5-evidence-base.md#objects--the-biological-and-molecular-entities-the-program-reasons-about)

**L5 evidence:** [EV-ZETTERSTROM-1996](L5-evidence-base.md#evidence--the-literature-this-program-cites)

**L5 artifacts:** [ART-TARGET-ROUTE-CENSUS](L5-evidence-base.md#artifacts--the-files-a-claim-can-be-checked-against)

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
