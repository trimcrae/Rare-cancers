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
| `V21` | an anti-target panel that recovers only 7 of its own 10 cognate crystallographic ligands and is therefore unreadable | `direct` |

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

**Missing:**
- the MM-GBSA decoy null's primary run output committed as a JSON — it lives in S3, and it is the headline evidence of the recommended framing (the $0 CI job named in paper-framing-options.md §2.1)

## Strategic timing — the wait equation

**Recommendation: `pursue_now`**

It has no blockers, it does not get cheaper or easier by waiting, and it is the portfolio's floor — the outcome that holds even if every other family fails. Deferring the one unblocked deliverable while blocked ones are watched would be exactly backwards.

| horizon | effect |
|---|---|
| Six months | None. Waiting adds material but the core record is already complete. |
| Two years | The record grows, but a negative result published later is worth less to the people it would have saved effort. |
| Cost trend | flat |
| Automation outlook | Drafting is largely automatable; the judgement about what a failure means is not. |

## Claim ceiling — what this route may NOT be used to claim

*Inherited from [ST-DISSEMINATION](L1-st-dissemination.md), which is where these are asserted — a family limitation binds every route inside it.*

- A methods paper documents what was done and what failed. It makes no claim about whether any route would work.
- The failure record's value depends on it being complete and honest, including the results that went against the program's own thesis.

## Best next action

Write it — no scientific blocker. ⚠ But the FRAMING choice (P1 vs P6) is trimcrae's and is not settled here.

*Cost:* $0

## What this route rests on — drill down

*L4 instruments and L5 objects, evidence and artifacts. Every row here is asserted by this route; the [evidence base](L5-evidence-base.md) shows the same edges from the other end.*

| L4 instrument | cited as | known-answer control |
|---|---|---|
| [V1](registers/instruments.md) — Structural selectivity descriptor (selcal_interface_signature) | support | `passes` |
| [V6](registers/instruments.md) — Relative FEP (OpenFE, the congeneric lane) | support | `passes` |
| [V8](registers/instruments.md) — ABFE engine, hydration | support | `passes` |
| [V10](registers/instruments.md) — Interface-mutation physics (pmx/GROMACS) | support | `passes` |
| [V3](registers/instruments.md) — Ligand pose prediction (dock + MM-GBSA) | **disclosed failing** | `inconclusive` |
| [V4](registers/instruments.md) — Selectivity free energy (ABFE) — the selectivity known-answer test | **disclosed failing** | `none` |
| [V5](registers/instruments.md) — Alchemical ternary cooperativity (valB_mini ΔΔG_coop) | **disclosed failing** | `fails` |
| [V7](registers/instruments.md) — ABFE engine, absolute | **disclosed failing** | `fails` |
| [V9](registers/instruments.md) — λ-overlap diagnostic on the standing ABFE block | **disclosed failing** | `none` |
| [V11](registers/instruments.md) — Interface-stability endpoint (E1) | **disclosed failing** | `fails` |
| [V12](registers/instruments.md) — Sequence-only co-folding (Boltz-2 ternary) | **disclosed failing** | `fails` |
| [V13](registers/instruments.md) — Cryptic-opening free-energy profile (metadynamics F(Rg)) | **disclosed failing** | `fails` |
| [V14](registers/instruments.md) — BioEmu unbiased ensemble cross-check | **disclosed failing** | `none` |
| [V15](registers/instruments.md) — PocketMiner + four permutation nulls | **disclosed failing** | `mixed` |
| [V16](registers/instruments.md) — The causal matched-pair test S (RUNG 5a-KS) | **disclosed failing** | `none` |
| [V17](registers/instruments.md) — The exposure criterion EXPOSED_RSA = 0.25 | **disclosed failing** | `fails` |
| [V19](registers/instruments.md) — The generation-matched null (winner's-curse / generative confound) | **disclosed failing** | `mixed` |
| [V20](registers/instruments.md) — Single-snapshot MM-GBSA margin > 0 as a selectivity verdict | **disclosed failing** | `fails` |
| [V21](registers/instruments.md) — The anti-target docking panel (antitarget_dock) | **disclosed failing** | `fails` |
| [V22](registers/instruments.md) — The scoring-independent second pose method (rDock) | **disclosed failing** | `none` |

[← ST-DISSEMINATION](L1-st-dissemination.md) · [← L0](L0-ecosystem.md)
