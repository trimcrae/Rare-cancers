---
id: DOC-MODALITY-CENSUS-2-QUANTIFIER-SITES
title: "Every site carrying the per-gene universal quantifier 'all five druggable guardians ... lower'"
level: L4
kind: investigation-artifact
status: live
date: 2026-09-09
lane: MODALITY-CENSUS-2
campaign: OPUS-CAPACITY-CAMPAIGN-20260908
---

# Site list — the false universal quantifier

Search performed at HEAD `65328136ec847a2ae4192cc8274cb6d5a12a6de2` over tracked and untracked
`.md` / `.json` / `.py` (transcript `.jsonl` excluded as raw capture, not a claim surface).
Raw output: `checks/02-quantifier-site-search/stdout.txt`.

**The defect is not confined to §3.2a. It has six LIVE sites, in four different owners.**

## A · Live sites (would need repair; only site 1 is in this lane's diff)

| # | file | line | text carrying the quantifier | owner |
|---|---|---:|---|---|
| 1 | `research/manuscripts/modality-census/cancer-modality-census.md` | 245 | "all five druggable guardians are lower on both platforms" | PUB-MODALITY-CENSUS — **the unapplied diff in this lane corrects this one** |
| 2 | `research/manuscripts/dependency/emc-biomarker-selected-classes.md` | 218 | "All five druggable guardians together are lower in EMC" | **PUB-BIOMARKER-DEP — a different manuscript** |
| 3 | `research/modalities/census_route_expression_grading.py` | 490 | `"observed": "⛔ All five druggable guardians together are LOWER in EMC than in comparator …"` | **the generator — source of truth for site 4** |
| 4 | `research/modalities/census-route-expression-grading.json` | 1512 | same string, generated | generated from site 3 — **do not hand-edit** |
| 5 | `systems/graph/routes.json` | 6101 | "Abundance: all five druggable guardians read LOWER in EMC on both platforms" (`RT-APOPTOSIS-DEP` grade value) | canonical graph |
| 6 | `systems/views/L2-rt-apoptosis-dep.md` | 23 | same string, generated | generated from site 5 — **do not hand-edit** |

Repair order is forced by generation: **3 → 4** (re-run the grading producer) and **5 → 6**
(edit the graph, re-run the view generator). Sites 1 and 2 are hand-written prose.

## B · Near-miss sites that are *not* defective

* `systems/graph/modalities.json:1438` (`MOD-MCL1-BCLXL.zero_dollar_next_step`) says "guardians
  concordantly LOWER" with **no numeral and no universal quantifier over the five genes**. It is a
  module-level statement in module-level words. Reporting it as a site would be wrong.
* `systems/views/modality-census.md:71` restates that same modalities.json string — same reading.
* `systems/graph/routes.json:6148–6150` and `systems/views/L2-rt-apoptosis-dep.md:56–58` say
  "guardian ABUNDANCE is lower" — again module-level, correct as written.

## C · Frozen / historical copies — must NOT be edited

Left exactly as they are; they are dated before/after evidence:
`research/autonomy/opus-capacity-campaign-20260908/paper-lane/PARENT-TD1-PATCHES-2026-09-08/BEFORE/{cancer-modality-census.md:233, census-route-expression-grading.json:1512, census_route_expression_grading.py:451}`,
`.../TD1-residual-2/before/{research__manuscripts__modality-census__cancer-modality-census.md:237, research__modalities__census-route-expression-grading.json:1512, research__modalities__census_route_expression_grading.py:478}`,
`.../BM1-executed-artifacts/{BEFORE,AFTER}-emc-biomarker-selected-classes.md:{193,202}`,
`.../A2-executed-artifacts/unclosed-route-census.json:475`,
`.../HANDOFF-biomarker-frozen-readiness.md:156`,
`.../PORTFOLIO-INVESTIGATIONS-2026-09-08/VIEWS-REGEN-1/regenerated/L2-rt-apoptosis-dep.md:23`
(a regeneration of site 6, so it inherits site 5's text and moves only when site 5 does).

## D · The defect was already found once, on the sibling paper, and never carried across

`research/autonomy/review-seats/PUB-BIOMARKER-DEP-20d33f34…-seat-citations-and-instruments.json`
already records, for **PUB-BIOMARKER-DEP §2.5**, that "All five druggable guardians together are
LOWER" conceals two genes reading higher on GPL6244, BCL2L2 at *t* = +2.908 — with the same per-gene
Welch values this lane re-derived independently. `…-seat-statistics.json` adds a second finding on the
same row: the artifact's own banding rule calls the GPL6244 **MCL1** read *flat* (|t| < 2, t = −1.93),
so "MCL1 individually included" is itself weaker than stated.

**Neither seat finding was propagated to PUB-MODALITY-CENSUS §3.2a, to the grading generator, or to
the graph.** The census inherited a sentence whose defect was already on the record for its sibling.
That cross-paper propagation gap — not the arithmetic — is the durable finding here.

⛔ **None of this reverses anything.** The module result is real on both platforms, the
`RT-APOPTOSIS-DEP` route verdict ("against at the abundance level", route restored to open) stands,
and `MOD-MCL1-BCLXL` stays a `candidate`. Saying so is part of the finding.
