---
id: DOC-VIEW-PAPER-STRENGTH
title: Paper strength — which endpoint is strongest, and on what
level: L3
kind: generated
status: generated
generator: systems/systems_check.py
purpose: Rank every publication endpoint by the standing of the routes under it and by whether it can be finished without a laboratory this programme does not have — so 'which paper is strongest?' has one home instead of being re-derived from 68 route grades by hand.
scope: One row per publication endpoint. It ranks evidential standing and reachability. It does NOT rank scientific or clinical importance.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-09
last_verified: 2026-08-09
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Paper strength

> ⛔ **THIS RANKS EVIDENTIAL STANDING AND REACHABILITY — NOT IMPORTANCE.** Nothing in the graph
> knows which result would matter most to a patient, and a number that pretended to would be the
> most dangerous object here. What it does know is which papers rest on routes that are still
> **open**, which are **finished negatives**, and which can be completed **without a laboratory this
> programme does not have**.
>
> ⭐ **A CLOSED ROUTE SUBTRACTS.** CLAUDE.md §0 records the day a ranking that rewarded finished
> work put four agents onto dead routes while live ones sat one free step from a result. A
> completed negative always scores full marks on "what do we hold if the experiment never
> happens?"; a live lead never does. Negatives are still worth publishing — they are not worth
> ranking first.
>
> ⚠ **Every component is printed, so the ranking can be argued with rather than obeyed.**

**Score** = 5 per open route · 2 per route blocked only on a human decision · −1 to −2 per closed route (by how it closed) · 3 per route whose status is `ready` · up to 5 for the fraction of remaining validation steps that are feasible today · 2 for having a drafted document, 1 for an outline · **±2 per open route for the confidence the graph records on it**.

⛔ **A LOW SCORE CAN MEAN 'CLOSED' OR IT CAN MEAN 'NOBODY GRADED IT', AND THOSE ARE OPPOSITE THINGS.** `closure_kind` is unset on 23 of 68 routes, and an unset field contributes nothing in either direction — so a paper can sit low here purely because its routes have never been graded. The `ungraded` column is that reading, and a high number in it means **go grade the routes**, not **the paper is weak** (CLAUDE.md §4: an absent reading is not a reading of absence).

| # | endpoint | score | open | closed | ungraded | ready | doable here | state | routes |
|---:|---|---:|---:|---:|---:|---:|---|---|---:|
| 1 | [**PUB-DEGRADER**](../../research/manuscripts/nr4a3-degrader-paper.md) | **18.9** | 2 | 3 | 0 | 2 | 38% of 8 | ◐ `drafted` | 5 |
| 2 | [**PUB-METHODS**](../../research/manuscripts/degrader-methods-failure-record.md) | **17.0** | 1 | 0 | 0 | 1 | 100% of 1 | ◐ `drafted` | 1 |
| 3 | [**PUB-REPURPOSING**](../../research/manuscripts/repurposing-hypotheses.md) | **14.0** | 2 | 0 | 0 | 1 | 20% of 5 | ◐ `drafted` | 3 |
| 4 | [**PUB-ENDPOINT**](../../research/manuscripts/response-endpoint-indolent-tumours.md) | **13.3** | 1 | 0 | 0 | 1 | 67% of 3 | ◐ `drafted` | 1 |
| 5 | [**PUB-EMC-PROGRAM**](../../research/manuscripts/emc-treatment-roadmap.md) | **13.0** | 2 | 0 | 0 | 1 | 0% of 2 | ◐ `drafted` | 2 |
| 6 | **PUB-STRATEGY-ARCH** | **11.9** | 1 | 0 | ⚠ 2 | 1 | 57% of 7 | ◔ `outlined` | 3 |
| 7 | [**PUB-ASO**](../../research/manuscripts/fusion-junction-aso-paper.md) | **10.7** | 1 | 0 | 0 | 0 | 33% of 6 | ◐ `drafted` | 2 |
| 8 | [**PUB-MTAP-PRMT5**](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md) | **10.0** | 1 | 0 | 0 | 1 | 0% of 3 | ◐ `drafted` | 1 |
| 9 | [**PUB-FUSION-OUTPUT**](../../research/manuscripts/nr4a3-fusion-transcriptional-output.md) | **9.5** | 1 | 0 | 0 | 0 | 50% of 6 | ◐ `drafted` | 1 |
| 10 | [**PUB-FUSION-PARTNER**](../../research/manuscripts/emc-fusion-partner-stratification.md) | **9.2** | 1 | 0 | 0 | 1 | 25% of 4 | ◐ `drafted` | 1 |
| 11 | [**PUB-SURFACE-TARGETS**](../../research/manuscripts/emc-surface-target-landscape.md) | **9.0** | 2 | 3 | 0 | 0 | 0% of 8 | ◐ `drafted` | 6 |
| 12 | [**PUB-TCIP**](../../research/manuscripts/tcip-induced-interface-preprint.md) | **8.3** | 1 | 0 | 0 | 0 | 67% of 3 | ◐ `drafted` | 1 |
| 13 | [**PUB-ATR**](../../research/manuscripts/emc-atr-vulnerability-assessment.md) | **8.0** | 1 | 0 | 0 | 1 | 0% of 1 | ◐ `drafted` | 1 |
| 14 | [**PUB-BIOMARKER-DEP**](../../research/manuscripts/emc-biomarker-selected-classes.md) | **7.0** | 0 | 0 | ⚠ 5 | 1 | 40% of 10 | ◐ `drafted` | 5 |
| 15 | [**PUB-MODALITY-CENSUS**](../../research/manuscripts/cancer-modality-census.md) | **5.0** | 0 | 0 | ⚠ 1 | 1 | 0% of 1 | ◐ `drafted` | 1 |
| 16 | **PUB-NR-OUTSIDE-NR4A3** | **5.0** | 0 | 0 | ⚠ 2 | 0 | 80% of 5 | ◔ `outlined` | 2 |
| 17 | [**PUB-TXN-DEPENDENCY**](../../research/manuscripts/emc-transcriptional-proteostatic-dependency.md) | **5.0** | 0 | 0 | ⚠ 2 | 0 | 60% of 5 | ◐ `drafted` | 2 |
| 18 | [**PUB-ATR-PANEL-ASK**](../../research/manuscripts/emc-atr-collaborator-package.md) | **4.0** | 0 | 0 | 0 | 0 | 0% of 1 | ◐ `drafted` | 1 |
| 19 | **PUB-KINASE-LEADS** | **3.7** | 0 | 0 | ⚠ 4 | 0 | 55% of 11 | ◔ `outlined` | 4 |
| 20 | **PUB-LOCOREGIONAL** | **3.5** | 0 | 0 | ⚠ 3 | 0 | 50% of 6 | ◔ `outlined` | 3 |
| 21 | **PUB-MATRIX-ADDRESS** | **3.5** | 0 | 0 | ⚠ 4 | 0 | 50% of 8 | ◔ `outlined` | 4 |
| 22 | [**PUB-MONOVALENT**](../../research/manuscripts/nr4a3-monovalent-pocket-route.md) | **3.5** | 0 | 1 | 0 | 0 | 50% of 2 | ◐ `drafted` | 1 |
| 23 | [**PUB-ANDGATE**](../../research/manuscripts/fusion-selective-andgate-degrader-paper.md) | **1.0** | 0 | 1 | 0 | 0 | 0% of 1 | ◐ `drafted` | 1 |
| 24 | [**PUB-NEOANTIGEN**](../../research/manuscripts/fusion-junction-neoantigen-paper.md) | **0.7** | 0 | 2 | 0 | 0 | 33% of 3 | ◐ `drafted` | 2 |
| 25 | [**PUB-HLA-COVERAGE**](../../research/manuscripts/hla-coverage-emc.md) | **0.0** | 0 | 1 | 0 | 0 | 0% of 1 | ◐ `drafted` | 1 |
| 26 | [**PUB-SYNLETH**](../../research/manuscripts/degrader-vs-synthetic-lethal.md) | **0.0** | 0 | 1 | 0 | 0 | 0% of 1 | ◐ `drafted` | 1 |
| 27 | **PUB-PARKED-MODALITIES** | **-5.0** | 0 | 5 | 0 | 0 | 0% of 6 | ○ `unwritten` | 5 |
| 28 | [**PUB-CLOSED-ROUTES**](../../research/manuscripts/closed-routes-negative-record.md) | **-12.0** | 0 | 7 | 0 | 0 | 0% of 3 | ◐ `drafted` | 7 |

## The open routes, which are the only ones that can still change an answer

⭐ **Read this list before the table above.** A route here is one the graph records as `closure_kind: open` — it has not been closed by a false premise, an instrument limit or arithmetic over a fixed fact, so a result is still available from it.

**PUB-DEGRADER** — score 18.9
- [RT-ASYMMETRIC](L2-rt-asymmetric.md) — *Are the two paralogue-sparing requirements actually the same requirement — and what changes if they are not?* — `ready` / `computed` / confidence `high` · last verified `2026-08-06`
- [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) — *Could pan-NR4A engagement be useful EX VIVO — during T-cell manufacturing — where selectivity does not matter?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-05`

**PUB-METHODS** — score 17.0
- [RT-METHODS-PAPER](L2-rt-methods-paper.md) — *What is the honest, publishable content of a computation-only program's own failure record?* — `ready` / `scoped` / confidence `high` · last verified `2026-08-05`

**PUB-REPURPOSING** — score 14.0
- [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) — *Could a PPARγ-directed agent act on a downstream effector of the fusion?* — `blocked` / `concept` / confidence `low` · last verified `2026-08-05`
- [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — *Does the best ex-vivo EMC drug-sensitivity evidence point at a proteasome inhibitor combination?* — `ready` / `concept` / confidence `low` · last verified `2026-08-09`

**PUB-ENDPOINT** — score 13.3
- [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) — *Is the objective-response rate a fit summary of a single-arm trial, and in which regime does it stop carrying information? Measured across trial arms in many diseases rather than in one.* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-EMC-PROGRAM** — score 13.0
- [RT-TRABECTEDIN](L2-rt-trabectedin.md) — *Is trabectedin, an approved sarcoma agent, mechanistically well matched to a FET-fusion sarcoma like EMC?* — `ready` / `concept` / confidence `low` · last verified `2026-08-05`
- [RT-ICI-TKI](L2-rt-ici-tki.md) — *Does the checkpoint-inhibitor plus anti-angiogenic combination have an EMC signal worth pursuing?* — `delegated` / `concept` / confidence `moderate` · last verified `2026-08-05`

**PUB-STRATEGY-ARCH** — score 11.9
- [RT-TRIAL-REACH](L2-rt-trial-reach.md) — *Can a patient with this disease actually reach the trials and the agents that a computational result would point them toward?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-ASO** — score 10.7
- [RT-ASO](L2-rt-aso.md) — *Can an RNase-H gapmer or siRNA against the EWSR1::NR4A3 breakpoint junction silence the chimera while sparing wild-type NR4A3?* — `blocked` / `scoped` / confidence `moderate` · last verified `2026-08-06`

**PUB-MTAP-PRMT5** — score 10.0
- [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) — *Does this tumour carry the copy-number state that selects the PRMT5 axis?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-FUSION-OUTPUT** — score 9.5
- [RT-FUSION-OUTPUT](L2-rt-fusion-output.md) — *Do the genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than in comparator tumours — beyond what an arbitrary gene set of the same size achieves on the same platform?* — `active` / `validated_in_silico` / confidence `moderate` · last verified `2026-08-08`

**PUB-FUSION-PARTNER** — score 9.2
- [RT-PARTNER-STRAT](L2-rt-partner-strat.md) — *Does the NR4A3 5' fusion partner identify which EMC patients the one systemically active drug class is reported to work in - and what does the published record actually support, as opposed to what it is repeatedly said to support?* — `ready` / `computed` / confidence `low` · last verified `2026-08-08`

**PUB-SURFACE-TARGETS** — score 9.0
- [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) — *Is a PRAME-directed T-cell engager or receptor therapy applicable to EMC?* — `blocked` / `computed` / confidence `moderate` · last verified `2026-08-05`
- [RT-FAP-RLT](L2-rt-fap-rlt.md) — *Could a fibroblast-activation-protein radioligand reach EMC through its stroma?* — `blocked` / `concept` / confidence `unknown` · last verified `2026-08-05`

**PUB-TCIP** — score 8.3
- [RT-TCIP](L2-rt-tcip.md) — *Can chemically induced proximity recruit a transcriptional effector to the fusion instead of degrading it?* — `blocked` / `scoped` / confidence `low` · last verified `2026-08-06`

**PUB-ATR** — score 8.0
- [RT-ATR-ASSESS](L2-rt-atr-assess.md) — *Does EMC inherit a replication-stress vulnerability from its FET-fusion class, and can that be assessed computationally?* — `ready` / `computed` / confidence `low` · last verified `2026-08-06`

