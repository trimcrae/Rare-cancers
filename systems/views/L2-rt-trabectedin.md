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

**Family:** [ST-REPURPOSING](L1-st-repurposing.md) · **state:** ○ ready · concept · confidence moderate · verified 2026-08-05

**Grade** (owned by [`research/IDEAS.md`](../../research/IDEAS.md)): NEAR-TERM LEAD — approved, mechanism-fit

## Scientific rationale

Trabectedin is approved for soft-tissue sarcoma and its mechanism — interfering with transcription-factor-driven programmes at the DNA minor groove — is a plausible fit for a disease whose entire biology is one aberrant transcription factor. There is a reported EMC responder. For an ultra-rare cancer with no targeted agent, an approved drug with a mechanistic story and a reported response is the shortest path that exists.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `EV-EMC-CLINICAL` | a reported EMC response to an approved agent | `direct` |

## Remaining unknowns

- Whether the mechanistic fit is real or a post-hoc story fitted to a single response.
- How the agent interacts with the fusion's specific programme, which has never been measured in EMC.

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

## Readiness — what this could become today

**`internal_note`**

This is clinical-evidence synthesis rather than a computational contribution. It belongs as landscape context in a paper, not as a result.

**Missing:**
- a larger clinical series

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

## Best next action

Keep as cited landscape context. Do not overstate a single response.

*Cost:* $0

[← ST-REPURPOSING](L1-st-repurposing.md) · [← L0](L0-ecosystem.md)
