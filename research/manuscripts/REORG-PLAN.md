---
id: DOC-MANUSCRIPTS-REORG-PLAN
title: Reorganisation plan for research/manuscripts/ — proposed per-route folders
level: L3
kind: memo
status: live
canonical_for: [the research/manuscripts folder taxonomy]
purpose: >
  Propose, BEFORE any file moves, exactly which of the 227 flat files in research/manuscripts/
  goes into which per-route subfolder, so the mapping can be reviewed rather than reverse-engineered
  from a diff of 190 renames.
scope: File placement only. It moves no science, changes no claim, and grades no route.
audience: [maintainers, autonomous research agents]
date: 2026-08-12
last_verified: 2026-08-12
---

# Reorganisation plan for `research/manuscripts/`

> **Status when written:** 227 files in one flat directory. This plan proposes **18 route folders** holding **190 files**; **29 tooling scripts** and **8 index/register files** stay at the root.

## Where the taxonomy comes from

It is **derived, not invented.** The folders are the publication endpoints in
[`systems/graph/publications.json`](../../systems/graph/publications.json), rendered as
[`systems/views/L3-publications.md`](../../systems/views/L3-publications.md), grouped by the
strategy family each endpoint's routes sit in ([`systems/graph/routes.json`](../../systems/graph/routes.json)).
Endpoints that share a deliverable, an audience or a body of working notes are merged so the result is
18 folders a human can hold in their head rather than 31 folders of two files each.

Two rules govern placement:

1. **A file lives with the paper it is FOR.** A red-team, a cover letter, a submission checklist, a
   literature-target list and a `*-map-edits.json` all belong to the route whose argument they serve —
   not to a folder of red-teams and a folder of cover letters.
2. **Cross-route documents are not forced into a route.** The roadmap, the systems map and the linter
   registries stay at the root, listed under "stays at the root" below with the reason.

Nothing here changes a document's content. Every move is a `git mv`; the only edits are to links and
to the paths hard-coded in checkers, workflows and the graph.

## Proposed folders

### `aso/` — 16 files

**Endpoints:** `PUB-ASO`

RT-ASO + RT-ASO-ASK (ST-NUCLEIC-ACID) — the junction ASO short communication, its working record, red-team, submission apparatus and every ASO literature-target list.

- `aso-citations-priorart-2026-08-08.md`
- `aso-delivery-antigen-2026-08-08.md`
- `fusion-junction-aso-paper-redteam.md`
- `fusion-junction-aso-references.json`
- `fusion-junction-aso-references.md`
- `fusion-junction-aso-research-article.md`
- `fusion-junction-aso-submission-plan.md`
- `fusion-junction-aso-submission-references.json`
- `fusion-junction-aso-submission-references.md`
- `fusion-junction-aso-submission-tables.md`
- `fusion-junction-aso-working-record.md`
- `hybrid-intron-aso-target.md`
- `hybrid-intron-map-edits.json`
- `lit-targets-aso-degrader-refile.json`
- `lit-targets-aso-delivery-routes.json`
- `lit-targets-aso-verify.json`

### `care-delivery/` — 5 files

**Endpoints:** `PUB-STRATEGY-ARCH`, `PUB-LOCOREGIONAL`, `PUB-CARE-DELIVERY`, `PUB-EMC-CLASSIFICATION`, `PUB-IPD-SURVIVAL`

ST-STRATEGY, ST-LOCOREGIONAL and ST-CARE-DELIVERY — trial reachability, scheduling and sequencing, and the radiotherapy/oligometastatic lanes.

- `emc-adaptive-scheduling-pazopanib.md`
- `emc-oligometastatic-rt-concept.md`
- `emc-radioresistance-reappraisal.md`
- `emc-rt-adaptive-lanes-map-edits.json`
- `emc-trial-reachability.md`

### `degrader/` — 51 files

**Endpoints:** `PUB-DEGRADER`, `PUB-ANDGATE`

RT-DEGRADER (ST-PROXIMITY) and its contributing routes (covalent probe, asymmetric design, ubiquitination-selective, ex-vivo pan-NR4A), plus RT-ANDGATE. The paper, its SI, every red-team/review/positioning memo and the ternary working records that feed them.

- `covalent-axis-q-rows-map-edits.json`
- `degrader-citation-audit-2026-08-08.md`
- `four-open-decisions-2026-08-07.md`
- `four-open-decisions-RULING-2026-08-07.md`
- `four-open-decisions-map-edits.json`
- `fusion-selective-andgate-degrader-paper.md`
- `lit-targets-degrader-citations.json`
- `lit-targets-e3-recruiter-recheck-2026-08-05.json`
- `lit-targets-e3-recruiter-trigger.json`
- `nr4a3-congeneric-rbfe-plan.md`
- `nr4a3-degrader-broader-indications.md`
- `nr4a3-degrader-carT-and-family-druggability-framing.md`
- `nr4a3-degrader-figures.md`
- `nr4a3-degrader-insilico-completeness.md`
- `nr4a3-degrader-ncs-presubmission-inquiry.md`
- `nr4a3-degrader-outreach-emails.md`
- `nr4a3-degrader-paper-SI.md`
- `nr4a3-degrader-paper-positioning.md`
- `nr4a3-degrader-paper-redteam.md`
- `nr4a3-degrader-paper-review-response.md`
- `nr4a3-degrader-paper.md`
- `nr4a3-degrader-preprint-plan.md`
- `nr4a3-degrader-preprint-si.md`
- `nr4a3-degrader-preprint.md`
- `nr4a3-degrader-reviewer-revisions-2026-07-15.md`
- `nr4a3-degrader-selectivity-architecture.md`
- `nr4a3-degrader-strategy-ternary-first.md`
- `nr4a3-emc-biology-evidence.md`
- `nr4a3-inverse-linker-design-2026-07-25.md`
- `nr4a3-orientation-basin-search-2026-07-25.md`
- `nr4a3-paralogue-dynamics-categorical-test-2026-07-25.md`
- `nr4a3-reach-rule-correction-2026-07-25.md`
- `nr4a3-ternary-selectivity-strategy-revision-2026-07-24.md`
- `nr4a3-transfer-anchor-and-handle-risk-2026-07-25.md`
- `pose-conditionality-map-edits.json`
- `q-queue-2026-08-07-map-edits.json`
- `q3-q4-q10-q16-map-edits.json`
- `r3-site-choice-audit-2026-08-03.md`
- `r3-site-choice-map-edits.json`
- `r3-site-choice-paper-edits.json`
- `r5-cross-method-pose-2026-08-06.md`
- `row4-pose-map-edits.json`
- `row4-second-method-map-edits.json`
- `selectivity-requirement-sizing.md`
- `three-row-audit-2026-08-03.md`
- `three-row-audit-map-edits.json`
- `valB-mini-r0-verdict-2026-07-25.md`
- `valB-reviewer-decision-2026-07-17.md`
- `valb-calibrator-rescope-2026-07-25.md`
- `valb-closure-triangle-pregate-2026-07-25.md`
- `valb-gate-defect-fix-audit-2026-07-25.md`

### `dependency/` — 9 files

**Endpoints:** `PUB-ATR`, `PUB-ATR-PANEL-ASK`, `PUB-SYNLETH`, `PUB-BIOMARKER-DEP`, `PUB-KINASE-LEADS`, `PUB-TXN-DEPENDENCY`

ST-DEPENDENCY — synthetic lethality and dependency: the ATR assessment and its collaborator package, the biomarker-selected classes, the transcriptional/proteostatic dependency, and the kinase lanes (SGK1, DNA-PK).

- `degrader-vs-synthetic-lethal.md`
- `emc-atr-collaborator-package-cover-letter.md`
- `emc-atr-collaborator-package.md`
- `emc-atr-vulnerability-assessment.md`
- `emc-biomarker-selected-classes.md`
- `emc-dnapk-nr4a3-lane-assessment.md`
- `emc-sgk1-lane-assessment.md`
- `emc-transcriptional-proteostatic-dependency.md`
- `kinase-lanes-map-edits.json`

### `endpoint/` — 24 files

**Endpoints:** `PUB-ENDPOINT`

RT-ENDPOINT-CHOICE (ST-DISSEMINATION) — the response-endpoint manuscript and the whole corpus/regime/placebo pipeline's data and figures.

- `emc-endpoint-alternatives-2026-08-08.md`
- `emc-endpoint-alternatives.json`
- `emc-endpoint-discordance.json`
- `emc-systemic-therapy-pooling.json`
- `endpoint-corpus-inputs.json`
- `endpoint-corpus.json`
- `endpoint-gap-distribution.svg`
- `endpoint-prior-art-audit.json`
- `endpoint-prior-art-inputs.json`
- `endpoint-regime-map.json`
- `endpoint-regime-map.svg`
- `endpoint-zero-response.svg`
- `lit-targets-chiusole2020-pfs.json`
- `lit-targets-cross-disease-endpoints.json`
- `lit-targets-endpoint-benchmarks.json`
- `lit-targets-xdisease-control-arm-detail.json`
- `lit-targets-xdisease-ctg-results.json`
- `lit-targets-xdisease-round5.json`
- `meta-analysis.md`
- `natural-history-inputs.json`
- `orr-dcr-reread.json`
- `placebo-arm-calibration.json`
- `placebo-arm-detail-inputs.json`
- `response-endpoint-indolent-tumours.md`

### `fusion-direct/` — 6 files

**Endpoints:** `PUB-CLOSED-ROUTES (fusion-direct half)`

ST-FUSION-DIRECT — targeting the fusion's other domains (RT-EWSR1-PROTEIN, RT-FET-LC-LIGAND, RT-DBD) and the fusion-selective framing that spans them.

- `fet-fusion-trial-eligibility-notice.md`
- `fusion-coactivator-ppi-paper.md`
- `fusion-condensate-disruption-paper.md`
- `fusion-selective-approaches-overview.md`
- `lit-targets-fusion-precedents.json`
- `nr4a3-fusion-targets-map-edits.json`

### `fusion-output/` — 12 files

**Endpoints:** `PUB-FUSION-OUTPUT`

RT-FUSION-OUTPUT — what the fusion actually transcribes: the paper, its SI, cover letter, submission checklist, and the cistrome/GEO readings the argument rests on.

- `emc-fourth-cohort-sra-2026-08-08.md`
- `fusion-output-graph-records.json`
- `gse243553-eno3-overlap-2026-08-08.md`
- `gse28866-tumour-vs-normal-reading.md`
- `lit-frenkel-2025-record.json`
- `lit-targets-nr4a3-cistrome.json`
- `nr4a3-cistrome-search-2026-08-08.md`
- `nr4a3-fusion-transcriptional-output-SI.md`
- `nr4a3-fusion-transcriptional-output-cover-letter.md`
- `nr4a3-fusion-transcriptional-output-repo-notes.md`
- `nr4a3-fusion-transcriptional-output-submission-checklist.md`
- `nr4a3-fusion-transcriptional-output.md`

### `fusion-partner/` — 6 files

**Endpoints:** `PUB-FUSION-PARTNER`

RT-PARTNER-STRAT — stratification by 5' fusion partner: the manuscript, the pooling artifact, the event counts and the graph records.

- `emc-fusion-partner-map-edits.json`
- `emc-fusion-partner-pooling.json`
- `emc-fusion-partner-stratification.md`
- `lit-targets-partner-events.json`
- `partner-event-counts-2026-08-08.md`
- `partner-strat-graph-records.json`

### `methods-record/` — 3 files

**Endpoints:** `PUB-METHODS`, `PUB-CLOSED-ROUTES`

RT-METHODS-PAPER (ST-DISSEMINATION) — the program's own failure record, the closed-routes negative record and the fact-check log they rest on.

- `closed-routes-negative-record.md`
- `degrader-methods-failure-record.md`
- `fact-check-log.md`

### `microenv/` — 2 files

**Endpoints:** `PUB-MATRIX-ADDRESS`

ST-MICROENV — RT-HYPOXIA-PRODRUG and the matrix-addressing routes: the hypoxia reading and its graph edits.

- `emc-hypoxia-map-edits.json`
- `emc-hypoxia-reading.md`

### `modality-census/` — 9 files

**Endpoints:** `PUB-MODALITY-CENSUS`, `PUB-PARKED-MODALITIES`

RT-MODALITY-CENSUS (ST-DISSEMINATION) — what modalities exist, what a civilian can actually buy, the novel/emerging scans and the frontier-capability watch lists.

- `cancer-modality-census.md`
- `emerging-modalities-scan-emc.md`
- `lit-targets-civilian-purchasing-b.json`
- `lit-targets-civilian-purchasing.json`
- `lit-targets-frontier-capability-2026-08-07.json`
- `lit-targets-frontier-capability-r2-2026-08-07.json`
- `novel-modalities-factcheck.md`
- `novel-modalities.md`
- `what-a-civilian-can-buy.md`

### `mtap-prmt5/` — 4 files

**Endpoints:** `PUB-MTAP-PRMT5`

RT-MTAP-PRMT5 (ST-DEPENDENCY) — its own folder because the hypothesis is at submission form with an SI, a cover letter and a pre/post runbook.

- `emc-mtap-prmt5-hypothesis-SI.md`
- `emc-mtap-prmt5-hypothesis-cover-letter.md`
- `emc-mtap-prmt5-hypothesis.md`
- `emc-mtap-prmt5-prepost.md`

### `neoantigen/` — 4 files

**Endpoints:** `PUB-NEOANTIGEN`, `PUB-HLA-COVERAGE`

RT-JUNCTION-NEOANTIGEN, RT-TCR-IMMTAC and RT-VACCINE (ST-IMMUNO) — the junction-neoantigen paper, HLA coverage, the clinical brief and the wider immunotherapy options memo.

- `clinical-brief-emc-neoantigen.md`
- `fusion-junction-neoantigen-paper.md`
- `hla-coverage-emc.md`
- `immunotherapy-options-emc.md`

### `occupancy/` — 4 files

**Endpoints:** `PUB-MONOVALENT`, `PUB-NR-OUTSIDE-NR4A3`

ST-OCCUPANCY — direct small-molecule engagement of the NR4A3 LBD (RT-MONOVALENT, RT-NR2F1) and the cryptic-pocket concept that frames it.

- `cryptic-pocket-atlas-concept.md`
- `lit-targets-nr4a3-lbd-vs-af1.json`
- `nr2f1-hormone-lane-map-edits.json`
- `nr4a3-monovalent-pocket-route.md`

### `program/` — 14 files

**Endpoints:** `PUB-EMC-PROGRAM`

Cross-route program documents: the treatment roadmap and strategy capstone, the route-option and path-family syntheses, the post-degrader grading, the paper-framing options and the map-audit/merge records. Not a route — the level above one.

- `degrader-paper-schedule.json`
- `emc-post-degrader-options.md`
- `emc-treatment-paper-outline.md`
- `emc-treatment-roadmap.md`
- `emc-treatment-strategy.md`
- `emc-unexplored-treatment-lanes.md`
- `instrument-register-prefix-map-edits.json`
- `lit-targets-emc-post-degrader.json`
- `map-audit-strategy.md`
- `map-merge-inventory.md`
- `paper-framing-options.md`
- `path-family-synthesis-map-edits.json`
- `path-family-synthesis.md`
- `target-route-options.md`

### `repurposing/` — 4 files

**Endpoints:** `PUB-REPURPOSING`

ST-REPURPOSING — RT-CARFILZOMIB primary with RT-TRABECTEDIN-PPARG and RT-PPARG-DOWNSTREAM contributing: the repurposing menu, its review and cover letter, and the PPARγ direction memo.

- `pparg-direction-emc.md`
- `repurposing-hypotheses-cover-letter.md`
- `repurposing-hypotheses-review.md`
- `repurposing-hypotheses.md`

### `surface-targets/` — 12 files

**Endpoints:** `PUB-SURFACE-TARGETS`

RT-B7H3 primary, with RT-CART-SURFACE, RT-PRAME-IMMTAC, RT-TCRT-CTA, RT-SSTR2 and RT-FAP-RLT contributing — the surface-target landscape, its SI, red-team, outreach and lane regrades.

- `car-t-strategies-emc.md`
- `emc-surface-antigen-map-edits.json`
- `emc-surface-target-landscape-cover-letter.md`
- `emc-surface-target-landscape-si.md`
- `emc-surface-target-landscape.md`
- `emc-surface-target-outreach.md`
- `emc-surface-target-redteam.md`
- `fap-rlt-2026-regrade.md`
- `fap-rlt-map-edits.json`
- `ofcs-cspg4-map-edits.json`
- `ofcs-var2csa-lane.md`
- `surface-targets-graph-records.json`

### `tcip/` — 5 files

**Endpoints:** `PUB-TCIP`

RT-TCIP (ST-PROXIMITY) — the induced-interface preprint, its SI, the interface-floor sizing and the graph edits that carry them.

- `pub-tcip-map-edits.json`
- `tcip-induced-interface-preprint-si.md`
- `tcip-induced-interface-preprint.md`
- `tcip-interface-floor-map-edits.json`
- `tcip-interface-floor-sizing.md`

## Stays at the root of `research/manuscripts/`

### Index and register files

| file | why it is not in a route folder |
|---|---|
| `README.md` | the folder map itself — an index, not a route document |
| `SUBMISSION-PACKET.md` | GENERATED, spans four manuscripts across four folders |
| `citation-provenance-ledger.json` | lint_citations.py's baseline ledger |
| `emc-systems-map.json` | cross-cutting register + its GENERATED view; checked by emc_systems_map_check.py, spans every route |
| `emc-systems-map.md` | GENERATED view of emc-systems-map.json |
| `nr4a3-program-map.md` | THE ROADMAP (CLAUDE.md rule 5) — the plan for the whole portfolio, not any one route; a route folder would demote it |
| `pinned-figures.json` | the consistency linter's own registry (rule 1.3) |
| `submission-metrics.json` | GENERATED, spans every submission |
| `REORG-PLAN.md` | this document |

### Tooling — 29 scripts

Every `.py` under `research/manuscripts/` stays where it is. They are invoked by path from
`.github/workflows/tests.yml`, from `scripts/preflight.sh` and from each other; moving them would
break those call sites for no navigational gain, and a generator is not a route document. Their
hard-coded *data* paths are rewritten to the new locations as part of the move.

- `aso_delivery_routes.py`
- `build_reference_list.py`
- `emc_endpoint_alternatives.py`
- `emc_endpoint_discordance.py`
- `emc_fusion_partner_pooling.py`
- `emc_systemic_therapy_pooling.py`
- `emc_systems_map_check.py`
- `endpoint_corpus.py`
- `endpoint_prior_art_audit.py`
- `endpoint_regime_figure.py`
- `endpoint_regime_map.py`
- `endpoint_result_figures.py`
- `fet_notice_sync_check.py`
- `line_citations.py`
- `lint_citations.py`
- `lint_claims.py`
- `lint_consistency.py`
- `lint_style.py`
- `orr_dcr_reread.py`
- `placebo_arm_calibration.py`
- `q3_q4_q10_q16_map_edits.py`
- `route_map_edits.py`
- `row4_pose_map_edits.py`
- `row4_second_method_map_edits.py`
- `submission_citations.py`
- `submission_metrics.py`
- `submission_packet.py`
- `submission_tables.py`
- `verify_map_edit_anchors.py`

`figures/` and `tests/` are already subdirectories and are untouched.

## Leftover — files that fit no route

**There are none in the sense of "unclassifiable".** Every one of the 227 files either belongs to a
publication endpoint or is one of the root-level items above. The closest thing to a leftover is the
`program/` folder, which is deliberately *not* a route: it holds the cross-route treatment roadmap,
the strategy capstone, the route-option and path-family syntheses and the map-audit records — documents
that sit one level ABOVE any single route and would be misfiled in all of them.

Three judgement calls worth naming, because a reader will otherwise wonder:

- **`nr4a3-program-map.md` stays at the root.** It is THE ROADMAP (CLAUDE.md §5) and carries the plan
  for the whole portfolio, not the degrader route alone. Filing it under `degrader/` would assert a
  scope the file explicitly no longer has (CLAUDE.md §5: the degrader "gets no special treatment").
- **`nr4a3-emc-biology-evidence.md` goes to `degrader/`** rather than `fusion-output/`: its own opening
  says it exists to replace "the two hand-wavy biological assumptions of the degrader program".
- **`degrader-vs-synthetic-lethal.md` goes to `dependency/`** rather than `degrader/`, because
  `publications.json` makes it the document for `PUB-SYNLETH`.

