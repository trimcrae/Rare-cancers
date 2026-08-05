---
id: DOC-VIEW-RT-METHODS-PAPER
title: RT-METHODS-PAPER — The honest methods paper on the degrader program's own failure record
level: L2
kind: generated
status: generated
generator: systems/systems_check.py
purpose: What is the honest, publishable content of a computation-only program's own failure record?
scope: Level 2 — one route.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# RT-METHODS-PAPER — The honest methods paper on the degrader program's own failure record

**Family:** [ST-DISSEMINATION](L1-st-dissemination.md) · **state:** ○ ready · scoped · confidence high · verified 2026-08-05

**Grade** (owned by [`research/manuscripts/emc-post-degrader-options.md`](../../research/manuscripts/emc-post-degrader-options.md#route-3---publish-the-methods-result-the-program-has-already-earned--rank-1)): Tier 1, rank 1 — DELIVERABLE

## What has to land for this route to move

```mermaid
flowchart LR
  RT_METHODS_PAPER["○ RT-METHODS-PAPER"]:::fam
  classDef fam stroke-width:2px;
  classDef blk stroke-width:2px;
  classDef perm stroke-width:4px;
  classDef tech stroke-width:1px,stroke-dasharray:4 3;
```

**Reading it.** A solid arrow is what holds this route down today. A dashed arrow is a capability that WOULD retire a blocker — dashed because it has not landed, and the date beside it is a forecast, not a schedule.

✓ Already cleared by this route: `BLK-NO-WET-LAB`.

## Scientific rationale

This program has accumulated something genuinely uncommon: a complete record of which in-silico instruments recovered known answers and which did not, on a real target, with the failures documented rather than discarded. Most published computational drug-discovery work reports the successes. A rigorous negative-and-methods record stops other groups repeating the same failures, and that is a real contribution regardless of whether any route here reaches a patient.

## Supporting evidence

| ref | supports | strength |
|---|---|---|
| `V5` | a ternary free-energy method failing a known-answer control on sign, systematically | `direct` |
| `V7` | an absolute free-energy engine missing a benchmark by more than the margin it is used to compute | `direct` |
| `V21` | an anti-target panel failing to recover its own cognate ligands | `direct` |

## Remaining unknowns

- Whether a venue will take a paper whose principal content is negative and methodological — though the material is unusually complete, which is the argument for it.

## Required validation

| what | instrument | feasible today | blocked by |
|---|---|---|---|
| The record is already validated by construction: each instrument's known-answer control IS the validation, and the failures are the content | ⛔ none built | yes | — |

## Blockers this route RETIRES

- **BLK-NO-WET-LAB** — No wet lab and no collaborator — an ask needs a self-interested taker before its size matters

## Readiness — what this could become today

**`journal_submission`**

Nothing blocks it. It is the only route in the portfolio with no scientific blocker at all — it is finished when the writing stops.

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

It has no blockers, it does not get cheaper or easier by waiting, and it is the portfolio's floor — the outcome that holds even if every other family fails. Deferring the one unblocked deliverable while blocked ones are watched would be exactly backwards.

| horizon | effect |
|---|---|
| Six months | None. Waiting adds material but the core record is already complete. |
| Two years | The record grows, but a negative result published later is worth less to the people it would have saved effort. |
| Cost trend | flat |
| Automation outlook | Drafting is largely automatable; the judgement about what a failure means is not. |

## Best next action

Write it. Nothing blocks it, and it is the only row on the board that is true regardless of how every other row resolves.

*Cost:* $0

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
