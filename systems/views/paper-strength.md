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

⭐ **Score** = **the paper's BEST route, plus half of every other route.** A route is worth 5 if it is open, 5 if it is blocked only on a human decision, −1 to −2 if it is closed (by how it closed); ±2 to −3 more for the confidence the graph records on an open one, and +1 if its status is `ready`. To that: **+8 for a bench ask that is already built, or for a finding that needs no bench at all · +4 for a decisive experiment a lab would still have to build, or for a result that reaches a patient through clinical practice** · 1 for having a drafted document, ½ for an outline.

⚠ **THE WEIGHTS ARE HEURISTICS AND THEY EXIST ONLY TO ORDER OUR OWN QUEUE** (trimcrae, 2026-08-09: *"we can absolutely change the weights till we like it … their only role is internal prioritization"*). Nothing here is a claim about scientific merit, and no external reader should be handed this table as one.

⛔ **THREE TERMS MEASURING OUR OWN READINESS WERE REMOVED OR CUT ON 2026-08-09, AND ALL THREE HAD SURVIVED A RUBRIC CHANGE THAT RETIRED THEIR STATED REASONS.** *Doable here* is **gone** — it measured the fraction of remaining work needing nobody else, and its own comment already conceded that is "not the same as whether the paper can help anyone"; it is still computed and printed, it just no longer moves the rank. *Ready* fell 3 → 1: it means ready to WRITE UP, a fact about our queue, and it was paying full marks to a route whose only remaining validation is a clinical series nobody here can run. *Drafted* halved to 1. Meanwhile `low` confidence deepened to −3, because this is a ranking of what is worth somebody's bench time.

⛔ **AND THE BOOLEAN `wet_lab_test_named` IS RETIRED, HAVING FAILED IN BOTH DIRECTIONS AT ONCE.** It could not tell a test somebody had **already run** from one a lab could pick up — PUB-REPURPOSING drew the full flag on a completed third-party *ex-vivo* screen. And it scored **zero** for the one paper that reaches a patient with no laboratory at all, whose own note read *"which is why the flag is False and not a demerit"* while the flag was costing it the largest single term in the score. `patient_path` replaces it with five graded values, printed in the table.

⛔ **A LOW SCORE CAN MEAN 'CLOSED' OR IT CAN MEAN 'NOBODY GRADED IT', AND THOSE ARE OPPOSITE THINGS.** `closure_kind` is unset on 28 of 83 routes, and an unset field contributes nothing in either direction — so a paper can sit low here purely because its routes have never been graded. The `ungraded` column is that reading, and a high number in it means **go grade the routes**, not **the paper is weak** (CLAUDE.md §4: an absent reading is not a reading of absence).

| # | endpoint | band | path to a patient | score | open | closed | ungraded | doable here | state |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | [**PUB-MTAP-PRMT5**](../../research/manuscripts/mtap-prmt5/emc-mtap-prmt5-hypothesis.md) | ⭐ could still help a patient | 🧪 **bench, pre-built** | **15.0** | 1 | 0 | 0 | 0% of 3 | ◐ `drafted` |
| 2 | [**PUB-ATR-PANEL-ASK**](../../research/manuscripts/dependency/emc-atr-collaborator-package.md) | ⭐ could still help a patient | 🧪 **bench, pre-built** | **14.0** | 0 | 0 | 0 | 0% of 1 | ◐ `drafted` |
| 3 | [**PUB-MORTALITY-MECHANISM**](../../research/manuscripts/emc-mortality-mechanisms-paper.md) | ⭐ could still help a patient | ⭐ **no bench needed** | **12.0** | 0 | 0 | ⚠ 6 | 57% of 14 | ◐ `drafted` |
| 4 | [**PUB-REPURPOSING**](../../research/manuscripts/repurposing/repurposing-hypotheses.md) | ⭐ could still help a patient | 🧪 bench, to build | **12.0** | 2 | 0 | 0 | 50% of 6 | ◐ `drafted` |
| 5 | **PUB-CARE-DELIVERY** | ⭐ could still help a patient | 🏥 clinical adoption | **11.5** | 4 | 0 | 0 | 29% of 7 | ○ `unwritten` |
| 6 | [**PUB-STRATEGY-ARCH**](../../research/manuscripts/care-delivery/emc-trial-reachability.md) | ⭐ could still help a patient | ⭐ **no bench needed** | **11.5** | 1 | 2 | 0 | 57% of 7 | ◐ `drafted` · ✎ short report |
| 7 | **PUB-IPD-SURVIVAL** | ⭐ could still help a patient | ⭐ **no bench needed** | **11.0** | 1 | 0 | 0 | 100% of 2 | ○ `unwritten` |
| 8 | [**PUB-SURFACE-TARGETS**](../../research/manuscripts/surface-targets/emc-tissue-rna-prioritization.md) | ⭐ could still help a patient | 🧪 bench, to build | **11.0** | 2 | 3 | 0 | 20% of 10 | ◐ `drafted` |
| 9 | [**PUB-ATR**](../../research/manuscripts/dependency/emc-atr-vulnerability-assessment.md) | ⭐ could still help a patient | 🧪 bench, to build | **8.0** | 1 | 0 | 0 | 0% of 1 | ◐ `drafted` |
| 10 | [**PUB-FUSION-PARTNER**](../../research/manuscripts/fusion-partner/emc-fusion-partner-stratification.md) | ⭐ could still help a patient | 🏥 clinical adoption | **8.0** | 1 | 0 | 0 | 25% of 4 | ◐ `drafted` |
| 11 | **PUB-LOCOREGIONAL** | ⭐ could still help a patient | 🏥 clinical adoption | **5.5** | 0 | 0 | ⚠ 4 | 50% of 8 | ◔ `outlined` |
| 12 | [**PUB-TXN-DEPENDENCY**](../../research/manuscripts/dependency/emc-transcriptional-proteostatic-dependency.md) | ⭐ could still help a patient | 🧪 bench, to build | **5.0** | 0 | 0 | ⚠ 2 | 60% of 5 | ◐ `drafted` |
| 13 | **PUB-KINASE-LEADS** | ⭐ could still help a patient | 🧪 bench, to build | **4.5** | 0 | 0 | ⚠ 4 | 55% of 11 | ◔ `outlined` |
| 14 | [**PUB-MONOVALENT**](../../research/manuscripts/occupancy/nr4a3-monovalent-pocket-route.md) | ⭐ could still help a patient | 🧪 bench, to build | **4.0** | 0 | 1 | 0 | 50% of 2 | ◐ `drafted` |
| 15 | [**PUB-MODALITY-CENSUS**](../../research/manuscripts/modality-census/cancer-modality-census.md) | ⭐ could still help a patient | — | **2.0** | 0 | 0 | ⚠ 1 | 0% of 1 | ◐ `drafted` |
| 16 | [**PUB-EMC-PROGRAM**](../../research/manuscripts/program/emc-treatment-roadmap.md) | ⭐ could still help a patient | — | **1** | 0 | 0 | 0 | — | ◐ `drafted` · ⚠ 2 cited-only |
| 17 | [**PUB-DEGRADER**](../../research/manuscripts/degrader/nr4a3-degrader-paper.md) | ⛔ known negative / methods | — | **10.5** | 2 | 3 | 0 | 38% of 8 | ◐ `drafted` |
| 18 | [**PUB-METHODS**](../../research/manuscripts/methods-record/degrader-methods-failure-record.md) | ⛔ known negative / methods | — | **9.0** | 1 | 0 | 0 | 100% of 1 | ◐ `drafted` |
| 19 | [**PUB-ASO**](../../research/manuscripts/aso/fusion-junction-aso-journal-article.md) | ⛔ known negative / methods | 🧪 bench, to build | **8.5** | 1 | 0 | 0 | 64% of 11 | ◉ `posted_preprint` |
| 20 | [**PUB-ENDPOINT**](../../research/manuscripts/endpoint/response-endpoint-indolent-tumours.md) | ⛔ known negative / methods | — | **7.0** | 1 | 0 | 0 | 67% of 3 | ◐ `drafted` |
| 21 | [**PUB-EMC-CLASSIFICATION**](../../research/manuscripts/care-delivery/emc-icdo-9231-classification.md) | ⛔ known negative / methods | 🏥 clinical adoption | **6.0** | 1 | 1 | 0 | 25% of 4 | ◐ `drafted` |
| 22 | [**PUB-FUSION-OUTPUT**](../../research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md) | ⛔ known negative / methods | — | **6.0** | 1 | 0 | 0 | 50% of 6 | ◐ `drafted` |
| 23 | [**PUB-TCIP**](../../research/manuscripts/tcip/tcip-induced-interface-preprint.md) | ⛔ known negative / methods | — | **3.0** | 1 | 0 | 0 | 67% of 3 | ◐ `drafted` |
| 24 | [**PUB-VACCINE-PATH**](../../research/manuscripts/neoantigen/emc-vaccine-development-path.md) | ⛔ known negative / methods | — | **3.0** | 1 | 0 | 0 | 50% of 4 | ◐ `drafted` |
| 25 | [**PUB-BIOMARKER-DEP**](../../research/manuscripts/dependency/emc-biomarker-selected-classes.md) | ⛔ known negative / methods | — | **2.0** | 0 | 0 | ⚠ 5 | 40% of 10 | ◐ `drafted` |
| 26 | **PUB-MATRIX-ADDRESS** | ⛔ known negative / methods | — | **0.5** | 0 | 0 | ⚠ 4 | 50% of 8 | ◔ `outlined` |
| 27 | **PUB-NR-OUTSIDE-NR4A3** | ⛔ known negative / methods | — | **0.5** | 0 | 0 | ⚠ 2 | 80% of 5 | ◔ `outlined` |
| 28 | [**PUB-ANDGATE**](../../research/manuscripts/degrader/fusion-selective-andgate-degrader-paper.md) | ⛔ known negative / methods | — | **0.0** | 0 | 1 | 0 | 0% of 1 | ◐ `drafted` |
| 29 | [**PUB-NEOANTIGEN**](../../research/manuscripts/neoantigen/fusion-junction-neoantigen-paper.md) | ⛔ known negative / methods | — | **0.0** | 0 | 2 | 0 | 33% of 3 | ◐ `drafted` |
| 30 | [**PUB-HLA-COVERAGE**](../../research/manuscripts/neoantigen/hla-coverage-emc.md) | ⛔ known negative / methods | — | **-1.0** | 0 | 1 | 0 | 0% of 1 | ◐ `drafted` |
| 31 | [**PUB-SYNLETH**](../../research/manuscripts/dependency/degrader-vs-synthetic-lethal.md) | ⛔ known negative / methods | — | **-1.0** | 0 | 1 | 0 | 0% of 1 | ◐ `drafted` |
| 32 | [**PUB-CLOSED-ROUTES**](../../research/manuscripts/methods-record/closed-routes-negative-record.md) | ⛔ known negative / methods | — | **-7.0** | 0 | 7 | 0 | 0% of 3 | ◐ `drafted` |
| 33 | **PUB-PARKED-MODALITIES** | ○ parked on a capability nobody has | — | **-6.0** | 0 | 5 | 0 | 0% of 6 | ○ `unwritten` |

## The open routes, which are the only ones that can still change an answer

⭐ **Read this list before the table above.** A route here is one the graph records as `closure_kind: open` — it has not been closed by a false premise, an instrument limit or arithmetic over a fixed fact, so a result is still available from it.

**PUB-MTAP-PRMT5** — score 15.0
- [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) — *Does this tumour carry the copy-number state that selects the PRMT5 axis?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-REPURPOSING** — score 12.0
- [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) — *Could a PPARγ-directed agent act on a downstream effector of the fusion?* — `blocked` / `concept` / confidence `low` · last verified `2026-08-28`
- [RT-CARFILZOMIB](L2-rt-carfilzomib.md) — *Does the best ex-vivo EMC drug-sensitivity evidence point at a proteasome inhibitor combination?* — `blocked` / `concept` / confidence `low` · last verified `2026-08-28`

**PUB-CARE-DELIVERY** — score 11.5
- [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md) — *How much of EMC's survival is decided by whether the first operation cleared the tumour, and by where it was performed?* — `ready` / `computed` / confidence `low` · last verified `2026-09-02`
- [RT-SURVEILLANCE](L2-rt-surveillance.md) — *Does follow-up in EMC stop before the disease does, and how much resectable recurrence is lost when it does?* — `ready` / `computed` / confidence `low` · last verified `2026-09-02`
- [RT-METASTASECTOMY](L2-rt-metastasectomy.md) — *In a lung-metastasis-dominant indolent sarcoma, what should decide whether — and how often — metastases are resected?* — `ready` / `computed` / confidence `low` · last verified `2026-09-02`
- [RT-RISK-MODEL](L2-rt-risk-model.md) — *Can the prognostic factors reported piecemeal across EMC's series be combined into a stratification that would let treatment intensity be matched to risk?* — `ready` / `computed` / confidence `low` · last verified `2026-09-02`

**PUB-STRATEGY-ARCH** — score 11.5
- [RT-TRIAL-REACH](L2-rt-trial-reach.md) — *Can a patient with this disease actually reach the trials and the agents that a computational result would point them toward?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-IPD-SURVIVAL** — score 11.0
- [RT-IPD-SURVIVAL](L2-rt-ipd-survival.md) — *Can the time-to-event data this disease's clinical questions all require be recovered from the curves already published?* — `ready` / `computed` / confidence `low` · last verified `2026-08-25`

**PUB-SURFACE-TARGETS** — score 11.0
- [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) — *Is a PRAME-directed T-cell engager or receptor therapy applicable to EMC?* — `parked` / `computed` / confidence `low` · last verified `2026-08-28`
- [RT-FAP-RLT](L2-rt-fap-rlt.md) — *Could a fibroblast-activation-protein radioligand reach EMC through its stroma?* — `blocked` / `concept` / confidence `unknown` · last verified `2026-08-05`

**PUB-ATR** — score 8.0
- [RT-ATR-ASSESS](L2-rt-atr-assess.md) — *Does EMC inherit a replication-stress vulnerability from its FET-fusion class, and can that be assessed computationally?* — `ready` / `computed` / confidence `low` · last verified `2026-08-06`

**PUB-FUSION-PARTNER** — score 8.0
- [RT-PARTNER-STRAT](L2-rt-partner-strat.md) — *Does the NR4A3 5' fusion partner identify which EMC patients the one systemically active drug class is reported to work in - and what does the published record actually support, as opposed to what it is repeatedly said to support?* — `ready` / `computed` / confidence `low` · last verified `2026-08-08`

**PUB-DEGRADER** — score 10.5
- [RT-ASYMMETRIC](L2-rt-asymmetric.md) — *Are the two paralogue-sparing requirements actually the same requirement — and what changes if they are not?* — `ready` / `computed` / confidence `high` · last verified `2026-08-06`
- [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) — *Could pan-NR4A engagement be useful EX VIVO — during T-cell manufacturing — where selectivity does not matter?* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-05`

**PUB-METHODS** — score 9.0
- [RT-METHODS-PAPER](L2-rt-methods-paper.md) — *What is the honest, publishable content of a computation-only program's own failure record?* — `ready` / `scoped` / confidence `high` · last verified `2026-08-05`

**PUB-ASO** — score 8.5
- [RT-ASO](L2-rt-aso.md) — *Can an RNase-H gapmer or siRNA against the EWSR1::NR4A3 breakpoint junction silence the chimera while sparing wild-type NR4A3?* — `blocked` / `scoped` / confidence `moderate` · last verified `2026-08-13`

**PUB-ENDPOINT** — score 7.0
- [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) — *Is the objective-response rate a fit summary of a single-arm trial, and in which regime does it stop carrying information? Measured across trial arms in many diseases rather than in one.* — `ready` / `computed` / confidence `moderate` · last verified `2026-08-09`

**PUB-EMC-CLASSIFICATION** — score 6.0
- [RT-POPULATION-REGISTRY](L2-rt-population-registry.md) — *What do population-level treatment patterns and outcomes say about EMC that the published series cannot?* — `blocked` / `concept` / confidence `low` · last verified `2026-08-23`

**PUB-FUSION-OUTPUT** — score 6.0
- [RT-FUSION-OUTPUT](L2-rt-fusion-output.md) — *Do the genes an NR4A3 chimera is published to bind read higher in EMC tumour tissue than in comparator tumours — beyond what an arbitrary gene set of the same size achieves on the same platform?* — `active` / `validated_in_silico` / confidence `moderate` · last verified `2026-08-08`

**PUB-TCIP** — score 3.0
- [RT-TCIP](L2-rt-tcip.md) — *Can chemically induced proximity recruit a transcriptional effector to the fusion instead of degrading it?* — `blocked` / `scoped` / confidence `low` · last verified `2026-08-06`

**PUB-VACCINE-PATH** — score 3.0
- [RT-VACCINE-COMBINATION](L2-rt-vaccine-combination.md) — *Does a breakpoint-matched junction construct add anything to a backbone that already has EMC-specific activity?* — `blocked` / `concept` / confidence `low` · last verified `2026-08-19`

