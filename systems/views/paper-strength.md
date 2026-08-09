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

> ⭐ **THE QUESTION THIS ANSWERS: which paper could still help a patient?** Not which is closest to
> finished — that is what the first two versions of this view measured, and it ranked a rigorous
> negative above every live lead.
>
> ⛔ **THE BAND IS THE RANKING; THE SCORE ONLY ORDERS PAPERS WITHIN A BAND.** Every paper that could
> still report a positive sits above every paper we already know is a negative, and no score a
> negative can reach will lift it across that line. Negatives remain worth publishing — the field
> publishes almost none — and they are not treatment leads.
>
> ⚠ **The band is a JUDGEMENT, recorded per row in `publications.json` with a one-line reason.**
> It is not inferred from route states, because a paper can have open routes and still be a
> negative by construction. Disagree with the row, not with the arithmetic.
>
> ⭐ **A CLOSED ROUTE SUBTRACTS.** CLAUDE.md §0 records the day a ranking that rewarded finished
> work put four agents onto dead routes while live ones sat one free step from a result. A
> completed negative always scores full marks on "what do we hold if the experiment never
> happens?"; a live lead never does. Negatives are still worth publishing — they are not worth
> ranking first.
>
> ⚠ **Every component is printed, so the ranking can be argued with rather than obeyed.**

**Score** = 5 per open route · 2 per route blocked only on a human decision · −1 to −2 per closed route (by how it closed) · 3 per route whose status is `ready` · up to 5 for the fraction of remaining validation steps that are feasible today · 2 for having a drafted document, 1 for an outline · ±2 per open route for the confidence the graph records on it · **+4 for naming a decisive experiment a laboratory could run**.

⚠ **Two weights were changed on 2026-08-09 and both changes point the same way.** *Doable here* fell from 5 to 2, because it measures whether WE can finish a paper rather than whether the paper helps anyone — at 5 it was quietly rewarding work that needs nobody else, precisely when needing somebody else (a bench) is how a result reaches a patient. And naming a bench-ready test was added at 4, because that is the step that turns a paper into a treatment lead.

⛔ **A LOW SCORE CAN MEAN 'CLOSED' OR IT CAN MEAN 'NOBODY GRADED IT', AND THOSE ARE OPPOSITE THINGS.** `closure_kind` is unset on 21 of 68 routes, and an unset field contributes nothing in either direction — so a paper can sit low here purely because its routes have never been graded. The `ungraded` column is that reading, and a high number in it means **go grade the routes**, not **the paper is weak** (CLAUDE.md §4: an absent reading is not a reading of absence).

| # | endpoint | band | wet-lab test | score | open | closed | ungraded | ready | state |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | [**PUB-REPURPOSING**](../../research/manuscripts/repurposing-hypotheses.md) | ⭐ could still help a patient | ✅ yes | **17.4** | 2 | 0 | 0 | 1 | ◐ `drafted` |
| 2 | [**PUB-MTAP-PRMT5**](../../research/manuscripts/emc-mtap-prmt5-hypothesis.md) | ⭐ could still help a patient | ✅ yes | **14.0** | 1 | 0 | 0 | 1 | ◐ `drafted` |
| 3 | [**PUB-ASO**](../../research/manuscripts/fusion-junction-aso-paper.md) | ⭐ could still help a patient | ✅ yes | **13.7** | 1 | 0 | 0 | 0 | ◐ `drafted` |
| 4 | [**PUB-SURFACE-TARGETS**](../../research/manuscripts/emc-surface-target-landscape.md) | ⭐ could still help a patient | ✅ yes | **13.0** | 2 | 3 | 0 | 0 | ◐ `drafted` |
| 5 | [**PUB-ATR**](../../research/manuscripts/emc-atr-vulnerability-assessment.md) | ⭐ could still help a patient | ✅ yes | **12.0** | 1 | 0 | 0 | 1 | ◐ `drafted` |
| 6 | [**PUB-FUSION-PARTNER**](../../research/manuscripts/emc-fusion-partner-stratification.md) | ⭐ could still help a patient | — | **8.5** | 1 | 0 | 0 | 1 | ◐ `drafted` |
| 7 | [**PUB-STRATEGY-ARCH**](../../research/manuscripts/emc-trial-reachability.md) | ⭐ could still help a patient | — | **8.1** | 1 | 2 | 0 | 1 | ◐ `drafted` |
| 8 | [**PUB-ATR-PANEL-ASK**](../../research/manuscripts/emc-atr-collaborator-package.md) | ⭐ could still help a patient | ✅ yes | **8.0** | 0 | 0 | 0 | 0 | ◐ `drafted` |
| 9 | [**PUB-TXN-DEPENDENCY**](../../research/manuscripts/emc-transcriptional-proteostatic-dependency.md) | ⭐ could still help a patient | ✅ yes | **7.2** | 0 | 0 | ⚠ 2 | 0 | ◐ `drafted` |
| 10 | **PUB-KINASE-LEADS** | ⭐ could still help a patient | ✅ yes | **6.1** | 0 | 0 | ⚠ 4 | 0 | ◔ `outlined` |
| 11 | [**PUB-EMC-PROGRAM**](../../research/manuscripts/emc-treatment-roadmap.md) | ⭐ could still help a patient | ✅ yes | **6** | 0 | 0 | 0 | 0 | ◐ `drafted` · ⚠ 2 cited-only |
| 12 | [**PUB-MONOVALENT**](../../research/manuscripts/nr4a3-monovalent-pocket-route.md) | ⭐ could still help a patient | ✅ yes | **6.0** | 0 | 1 | 0 | 0 | ◐ `drafted` |
| 13 | [**PUB-MODALITY-CENSUS**](../../research/manuscripts/cancer-modality-census.md) | ⭐ could still help a patient | — | **5.0** | 0 | 0 | ⚠ 1 | 1 | ◐ `drafted` |
| 14 | **PUB-LOCOREGIONAL** | ⭐ could still help a patient | — | **2.0** | 0 | 0 | ⚠ 3 | 0 | ◔ `outlined` |
| 15 | [**PUB-DEGRADER**](../../research/manuscripts/nr4a3-degrader-paper.md) | ⛔ known negative / methods | — | **17.8** | 2 | 3 | 0 | 2 | ◐ `drafted` |
| 16 | [**PUB-METHODS**](../../research/manuscripts/degrader-methods-failure-record.md) | ⛔ known negative / methods | — | **14.0** | 1 | 0 | 0 | 1 | ◐ `drafted` |
| 17 | [**PUB-ENDPOINT**](../../research/manuscripts/response-endpoint-indolent-tumours.md) | ⛔ known negative / methods | — | **11.3** | 1 | 0 | 0 | 1 | ◐ `drafted` |
| 18 | [**PUB-FUSION-OUTPUT**](../../research/manuscripts/nr4a3-fusion-transcriptional-output.md) | ⛔ known negative / methods | — | **8.0** | 1 | 0 | 0 | 0 | ◐ `drafted` |
| 19 | [**PUB-TCIP**](../../research/manuscripts/tcip-induced-interface-preprint.md) | ⛔ known negative / methods | — | **6.3** | 1 | 0 | 0 | 0 | ◐ `drafted` |
| 20 | [**PUB-BIOMARKER-DEP**](../../research/manuscripts/emc-biomarker-selected-classes.md) | ⛔ known negative / methods | — | **5.8** | 0 | 0 | ⚠ 5 | 1 | ◐ `drafted` |
| 21 | **PUB-NR-OUTSIDE-NR4A3** | ⛔ known negative / methods | — | **2.6** | 0 | 0 | ⚠ 2 | 0 | ◔ `outlined` |
| 22 | **PUB-MATRIX-ADDRESS** | ⛔ known negative / methods | — | **2.0** | 0 | 0 | ⚠ 4 | 0 | ◔ `outlined` |
| 23 | [**PUB-ANDGATE**](../../research/manuscripts/fusion-selective-andgate-degrader-paper.md) | ⛔ known negative / methods | — | **1.0** | 0 | 1 | 0 | 0 | ◐ `drafted` |
| 24 | [**PUB-HLA-COVERAGE**](../../research/manuscripts/hla-coverage-emc.md) | ⛔ known negative / methods | — | **0.0** | 0 | 1 | 0 | 0 | ◐ `drafted` |
| 25 | [**PUB-SYNLETH**](../../research/manuscripts/degrader-vs-synthetic-lethal.md) | ⛔ known negative / methods | — | **0.0** | 0 | 1 | 0 | 0 | ◐ `drafted` |
| 26 | [**PUB-NEOANTIGEN**](../../research/manuscripts/fusion-junction-neoantigen-paper.md) | ⛔ known negative / methods | — | **-0.3** | 0 | 2 | 0 | 0 | ◐ `drafted` |
| 27 | [**PUB-CLOSED-ROUTES**](../../research/manuscripts/closed-routes-negative-record.md) | ⛔ known negative / methods | — | **-12.0** | 0 | 7 | 0 | 0 | ◐ `drafted` |
| 28 | **PUB-PARKED-MODALITIES** | ○ parked on a capability nobody has | — | **-5.0** | 0 | 5 | 0 | 0 | ○ `unwritten` |

## The open routes, which are the only ones that can still change an answer

⭐ **Read this list before the table above.** A route here is one the graph records as `closure_kind: open` — it has not been closed by a false premise, an instrument limit or arithmetic over a fixed fact, so a result is still available from it.

**PUB-REPURPOSING** — score 17.4
- [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) — *Could a PPARγ-directed agent act on a downstream effector of the fusion?* — `blocked` / `concept` / confidence `low` · last verified `2026-08-05`
- [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — *Does the best ex-vivo EMC drug-sensitivity evidence point at a proteasome inhibitor combination?* — `ready` / `concept` / confidence `low` · last verified `2026-08-09`

**PUB-MTAP-PRMT5** — score 14.0
- [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) — *Does this tumour carry the copy-number state that selects the PRMT5 axis?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-ASO** — score 13.7
- [RT-ASO](L2-rt-aso.md) — *Can an RNase-H gapmer or siRNA against the EWSR1::NR4A3 breakpoint junction silence the chimera while sparing wild-type NR4A3?* — `blocked` / `scoped` / confidence `moderate` · last verified `2026-08-06`

**PUB-SURFACE-TARGETS** — score 13.0
- [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) — *Is a PRAME-directed T-cell engager or receptor therapy applicable to EMC?* — `blocked` / `computed` / confidence `moderate` · last verified `2026-08-05`
- [RT-FAP-RLT](L2-rt-fap-rlt.md) — *Could a fibroblast-activation-protein radioligand reach EMC through its stroma?* — `blocked` / `concept` / confidence `unknown` · last verified `2026-08-05`

**PUB-ATR** — score 12.0
- [RT-ATR-ASSESS](L2-rt-atr-assess.md) — *Does EMC inherit a replication-stress vulnerability from its FET-fusion class, and can that be assessed computationally?* — `ready` / `computed` / confidence `low` · last verified `2026-08-06`

**PUB-FUSION-PARTNER** — score 8.5
- [RT-PARTNER-STRAT](L2-rt-partner-strat.md) — *Does the NR4A3 5' fusion partner identify which EMC patients the one systemically active drug class is reported to work in - and what does the published record actually support, as opposed to what it is repeatedly said to support?* — `ready` / `computed` / confidence `low` · last verified `2026-08-08`

**PUB-STRATEGY-ARCH** — score 8.1
- [RT-TRIAL-REACH](L2-rt-trial-reach.md) — *Can a patient with this disease actually reach the trials and the agents that a computational result would point them toward?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-DEGRADER** — score 17.8
- [RT-ASYMMETRIC](L2-rt-asymmetric.md) — *Are the two paralogue-sparing requirements actually the same requirement — and what changes if they are not?* — `ready` / `computed` / confidence `high` · last verified `2026-08-06`
- [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) — *Could pan-NR4A engagement be useful EX VIVO — during T-cell manufacturing — where selectivity does not matter?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-05`

**PUB-METHODS** — score 14.0
- [RT-METHODS-PAPER](L2-rt-methods-paper.md) — *What is the honest, publishable content of a computation-only program's own failure record?* — `ready` / `scoped` / confidence `high` · last verified `2026-08-05`

**PUB-ENDPOINT** — score 11.3
- [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) — *Is the objective-response rate a fit summary of a single-arm trial, and in which regime does it stop carrying information? Measured across trial arms in many diseases rather than in one.* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-FUSION-OUTPUT** — score 8.0
- [RT-FUSION-OUTPUT](L2-rt-fusion-output.md) — *Do the genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than in comparator tumours — beyond what an arbitrary gene set of the same size achieves on the same platform?* — `active` / `validated_in_silico` / confidence `moderate` · last verified `2026-08-08`

**PUB-TCIP** — score 6.3
- [RT-TCIP](L2-rt-tcip.md) — *Can chemically induced proximity recruit a transcriptional effector to the fusion instead of degrading it?* — `blocked` / `scoped` / confidence `low` · last verified `2026-08-06`

