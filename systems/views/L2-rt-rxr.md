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

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ✓ closed · computed · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md)): ✕ CLOSED 2026-08-03 — NR4A3 does not heterodimerise with RXR

## What has to land for this route to move

*This route inherits no blocker and retires none — there is no dependency structure to draw. Its state is decided by the evidence on this page alone.*

## Scientific rationale

Registered with its closing measurement. Nuclear receptors commonly act as RXR heterodimers, which would give a well-precedented pharmacological handle — but the published evidence is that this receptor does not form a permissive heterodimer with RXR.

## Remaining unknowns

- Whether the published negative is correct. It is a direct measurement, so only a contradicting primary measurement of the same fact reopens this — no method advance does.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| A primary measurement contradicting the published negative | ⛔ none built | **no** | — |

## Readiness — what this could become today

**`internal_note`**

Closed on a published measurement; the output is the closure and its citation.

## Strategic timing — the wait equation

**Recommendation: `closed`**

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

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
