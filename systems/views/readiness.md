---
id: DOC-VIEW-READINESS
title: Readiness — what each route could become today
level: cross-cutting
kind: generated
status: generated
generator: systems/systems_check.py
purpose: "For every route: the highest output it could reach now, and what is missing for more."
scope: All routes carrying a readiness assessment.
audience: ["maintainers", "autonomous research agents"]
date: 2026-08-05
last_verified: 2026-08-05
---

<!-- GENERATED FILE — DO NOT EDIT. Regenerate with:
     python3 systems/systems_check.py --write-views
     Source of truth: systems/graph/*.json -->

# Readiness

The ladder is ordered but is **not** a quality ranking — `experimental_proposal` is not better
than `journal_submission`; they are different outputs and a route can be ready for one and not
the other. Where a route cannot reach an output, the missing items are a work list.

| route | family | attainable today | what is missing |
|---|---|---|---|
| [RT-ASO-ASK](L2-rt-aso-ask.md) | ST-NUCLEIC-ACID | `experimental_proposal` | a collaborator with an EMC or FET-fusion line; an engineered or isogenic fusion-positive model expressing abundant wild-type NR4A3 and EWSR1 — an EMC line alone cannot carry the sp |
| [RT-ATR-PANEL](L2-rt-atr-panel.md) | ST-DEPENDENCY | `experimental_proposal` | a collaborator with an EMC line |
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) | ST-IMMUNO | `experimental_proposal` | expression confirmation on EMC tissue |
| [RT-SSTR2](L2-rt-sstr2.md) | ST-RADIOLIGAND | `experimental_proposal` | any expression measurement in EMC |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) | ST-REPURPOSING | `experimental_proposal` | a PPARγ ACTIVITY readout in EMC, not an abundance one — the direction is stated at T1 with a model-identity caveat in research/manuscripts/repurposing/pparg-direction-emc.md |
| [RT-ENDPOINT-CHOICE](L2-rt-endpoint-choice.md) | ST-DISSEMINATION | `journal_submission` | — |
| [RT-FUSION-OUTPUT](L2-rt-fusion-output.md) | ST-DISSEMINATION | `journal_submission` | — |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | ST-DISSEMINATION | `journal_submission` | the MM-GBSA decoy null's primary run output committed as a JSON — it lives in S3, and it is the headline evidence of the recommended framing (the $0 CI job named in paper-framing-o |
| [RT-ASO](L2-rt-aso.md) | ST-NUCLEIC-ACID | `chemrxiv` | a named delivery candidate FOR THE SYSTEMIC ROUTE -- rescoped 2026-08-12; the local and inhaled routes never required one, and grading the whole route on the systemic route's missi |
| [RT-ATR-ASSESS](L2-rt-atr-assess.md) | ST-DEPENDENCY | `preprint` | an EMC-specific measurement |
| [RT-DEGRADER](L2-rt-degrader.md) | ST-PROXIMITY | `preprint` | a passing selectivity known-answer control; an anti-target panel that recovers its own cognate ligands |
| [RT-MODALITY-CENSUS](L2-rt-modality-census.md) | ST-DISSEMINATION | `preprint` | — |
| [RT-MTAP-PRMT5](L2-rt-mtap-prmt5.md) | ST-DEPENDENCY | `preprint` | nothing for the preprint — it is written and every figure resolves to a committed artifact |
| [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) | ST-IMMUNO | `preprint` | a cellular persistence readout |
| [RT-PARTNER-STRAT](L2-rt-partner-strat.md) | ST-REPURPOSING | `preprint` | a non-zero TAF15 event count on the RESPONSE endpoint - the entire published TAF15::NR4A3 antiangiogenic-TKI experience is 3-5 patients with ZERO responses, and a zero-event arm yi |
| [RT-TCIP](L2-rt-tcip.md) | ST-PROXIMITY | `preprint` | a staged transcriptional-effector body, so the result can name an effector rather than a size class |
| [RT-VACCINE-COMBINATION](L2-rt-vaccine-combination.md) | ST-IMMUNO | `preprint` | the Stage 0 computational items; any EMC tissue result |
| [RT-ASYMMETRIC](L2-rt-asymmetric.md) | ST-OCCUPANCY | `reproducible_workflow` | — |
| [RT-6MP](L2-rt-6mp.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-AF3-INTERFACE](L2-rt-af3-interface.md) | ST-PROXIMITY | `internal_note` | a co-folder validated on assembly |
| [RT-ALK-HIT](L2-rt-alk-hit.md) | ST-REPURPOSING | `internal_note` | a dependency prior for the named targets, which is queued and $0; an attribution experiment, which needs the model the screen ran on |
| [RT-ANDGATE](L2-rt-andgate.md) | ST-PROXIMITY | `internal_note` | arm-2 chemistry |
| [RT-APOPTOSIS-DEP](L2-rt-apoptosis-dep.md) | ST-DEPENDENCY | `internal_note` | a dependency or BH3-profiling readout in an EMC model — abundance cannot answer this and the class prior contains no EMC line |
| [RT-ARGININE](L2-rt-arginine.md) | ST-DEPENDENCY | `internal_note` | nothing — the $0 observation this route was registered for has been taken, and it came back against the premise |
| [RT-B7H3](L2-rt-b7h3.md) | ST-IMMUNO | `internal_note` | a tissue-level measurement |
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-CART-SURFACE](L2-rt-cart-surface.md) | ST-IMMUNO | `internal_note` | a selective surface antigen |
| [RT-CHAPERONE](L2-rt-chaperone.md) | ST-DEPENDENCY | `internal_note` | a client-binding measurement, which is not an expression question |
| [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) | ST-OCCUPANCY | `internal_note` | a criterion that passes its positive control |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) | ST-NUCLEIC-ACID | `internal_note` | a solid-tumour vector |
| [RT-DBD](L2-rt-dbd.md) | ST-FUSION-DIRECT | `internal_note` | — |
| [RT-DIAGNOSTIC-PATHWAY](L2-rt-diagnostic-pathway.md) | ST-CARE-DELIVERY | `internal_note` | nothing — the route is CLOSED. The measurement landed and the endpoint was closed as not-a-paper. |
| [RT-DNAPK](L2-rt-dnapk.md) | ST-DEPENDENCY | `internal_note` | a sarcoma-class dependency prior for the kinase, which is queued and $0; a measurement in a cell carrying the fusion, which needs a model |
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) | ST-FUSION-DIRECT | `internal_note` | — |
| [RT-EZH2](L2-rt-ezh2.md) | ST-DEPENDENCY | `internal_note` | nothing — the selection question was asked and answered negatively |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) | ST-RADIOLIGAND | `internal_note` | any measurement in EMC |
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) | ST-FUSION-DIRECT | `internal_note` | — |
| [RT-GLUE](L2-rt-glue.md) | ST-PROXIMITY | `internal_note` | a prospective glue design method |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-HORMONE-PARTNER](L2-rt-hormone-partner.md) | ST-REPURPOSING | `internal_note` | nothing at the arithmetic level — the pooled fraction was computed and is a negative |
| [RT-HYPOXIA-PRODRUG](L2-rt-hypoxia-prodrug.md) | ST-MICROENV | `internal_note` | a third EMC series — the falsifier the owning memo names |
| [RT-ICI-TKI](L2-rt-ici-tki.md) | ST-IMMUNO | `internal_note` | a larger clinical series |
| [RT-IMMUNOCYTOKINE](L2-rt-immunocytokine.md) | ST-MICROENV | `internal_note` | an isoform-resolved read, which needs RNA-seq rather than an array — the fourth public cohort is the first candidate that could carry it |
| [RT-IPD-SURVIVAL](L2-rt-ipd-survival.md) | ST-CARE-DELIVERY | `internal_note` | ⛔ THE CEILING IS WHAT THE FIGURES PRINT, NOT THE INSTRUMENT. Both instruments now exist and both have controls; the reachable literature supplies one admissible EMC curve.; more cu |
| [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) | ST-IMMUNO | `internal_note` | patient-cd4-demo.json regenerated at the corrected junction — the class-II arm and every CD8∧CD4 figure are withheld until it is; the TAF15::NR4A3 panel regenerated — patient_neoep |
| [RT-LIMB-PERFUSION](L2-rt-limb-perfusion.md) | ST-LOCOREGIONAL | `internal_note` | primary-site curation from the pooled series' primary reports, which is $0 for the open-access ones; a search of the perfusion literature for myxoid histologies specifically |
| [RT-LUNG-DIRECTED](L2-rt-lung-directed.md) | ST-LOCOREGIONAL | `internal_note` | metastatic-site and lesion-burden curation from the pooled series' primary reports, which is $0 for the open-access ones and is this route's single highest-value step |
| [RT-MATRIX-ADDRESS](L2-rt-matrix-address.md) | ST-MICROENV | `internal_note` | a stain or a binding assay on EMC tissue — the epitope is a modification pattern and there is no further expression observation that could reach it |
| [RT-MATRIX-SYNTHESIS](L2-rt-matrix-synthesis.md) | ST-MICROENV | `internal_note` | a restatement of the premise in a form this reading does not already contradict |
| [RT-MDM2](L2-rt-mdm2.md) | ST-DEPENDENCY | `internal_note` | a direct TP53 sequence call, which no available EMC dataset supplies |
| [RT-MDT-LUNG](L2-rt-mdt-lung.md) | ST-LOCOREGIONAL | `internal_note` | a quantitative contribution that a 2025 review has not already made in prose — currently the only candidate is the BED-versus-local-control tabulation, and roughly seven positively |
| [RT-METASTASECTOMY](L2-rt-metastasectomy.md) | ST-CARE-DELIVERY | `internal_note` | metastatic site and burden, which appear in free text rather than as curated data |
| [RT-MONOVALENT](L2-rt-monovalent.md) | ST-OCCUPANCY | `internal_note` | a functional readout; the occupancy-to-output transfer functions that would turn the stated requirement into a number (MISSING-1, MISSING-2) |
| [RT-NR2F1](L2-rt-nr2f1.md) | ST-OCCUPANCY | `internal_note` | a platform that carries a probe for the receptor — the two readable array series do not |
| [RT-POLQ](L2-rt-polq.md) | ST-DEPENDENCY | `internal_note` | nothing at the expression level — the class selects on a lesion this data cannot see, and on what it CAN see the answer is negative |
| [RT-POPULATION-REGISTRY](L2-rt-population-registry.md) | ST-CARE-DELIVERY | `internal_note` | a signed data-use agreement, which only trimcrae can obtain |
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | ST-REPURPOSING | `internal_note` | a PPARγ ACTIVITY (target-gene) readout in EMC — the direction itself is now stated at T1 with a model-identity caveat in research/manuscripts/repurposing/pparg-direction-emc.md |
| [RT-RET](L2-rt-ret.md) | ST-REPURPOSING | `internal_note` | the primary paper's full text, which is paywalled and unreachable at $0; a phospho-receptor measurement in EMC tissue, which nobody has published |
| [RT-RIBOZYME](L2-rt-ribozyme.md) | ST-NUCLEIC-ACID | `internal_note` | a solid-tumour vector; a modern demonstration of trans-splicing ribozymes |
| [RT-RIPTAC](L2-rt-riptac.md) | ST-PROXIMITY | `internal_note` | paralogue selectivity; a chemistry programme |
| [RT-RISK-MODEL](L2-rt-risk-model.md) | ST-CARE-DELIVERY | `internal_note` | the reconstructed dataset, and per-arm curves rather than pooled ones |
| [RT-RT-INTENSIFY](L2-rt-rt-intensify.md) | ST-LOCOREGIONAL | `internal_note` | per-patient dose and modality data, which none of the curated series publishes; a particle-registry search by histology |
| [RT-RXR](L2-rt-rxr.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-SCHEDULING](L2-rt-scheduling.md) | ST-STRATEGY | `internal_note` | nothing to start — the inputs are committed, and their shape is now known to be four separate medians rather than one pooled value |
| [RT-SEQUENCING](L2-rt-sequencing.md) | ST-STRATEGY | `internal_note` | nothing at the analysis level — the question was asked and the record answered that it cannot support the claim |
| [RT-SGK1](L2-rt-sgk1.md) | ST-DEPENDENCY | `internal_note` | a phospho-substrate or activity readout, which is what the substrate signal hints at and abundance cannot deliver |
| [RT-SURGICAL-QUALITY](L2-rt-surgical-quality.md) | ST-CARE-DELIVERY | `internal_note` | margin status and treatment setting, which no curated cohort here records |
| [RT-SURVEILLANCE](L2-rt-surveillance.md) | ST-CARE-DELIVERY | `internal_note` | the time-resolved recurrence hazard, which RT-IPD-SURVIVAL would supply |
| [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) | ST-DEPENDENCY | `internal_note` | EMC-specific functional-genomics data |
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) | ST-NUCLEIC-ACID | `internal_note` | a direct binding-specificity read in EMC |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) | ST-IMMUNO | `internal_note` | a stronger presented epitope, and one not confined to a single allele — both corrected e7::e3 strong binders are HLA-B*15:01 |
| [RT-TCRT-CTA](L2-rt-tcrt-cta.md) | ST-IMMUNO | `internal_note` | a real EMC expression series |
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) | ST-REPURPOSING | `internal_note` | a larger clinical series |
| [RT-TRIAL-REACH](L2-rt-trial-reach.md) | ST-STRATEGY | `internal_note` | non-US registry coverage, which needs an authenticated endpoint this programme does not have |
| [RT-TXN-CDK](L2-rt-txn-cdk.md) | ST-DEPENDENCY | `internal_note` | nothing — the question was asked and answered |
| [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) | ST-PROXIMITY | `internal_note` | an observed transfer geometry |
| [RT-VACCINE](L2-rt-vaccine.md) | ST-IMMUNO | `internal_note` | an immunogenicity argument |

[← L0](L0-ecosystem.md)
