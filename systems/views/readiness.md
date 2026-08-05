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
| [RT-ASO-ASK](L2-rt-aso-ask.md) | ST-NUCLEIC-ACID | `experimental_proposal` | a collaborator with an EMC or FET-fusion line |
| [RT-ATR-PANEL](L2-rt-atr-panel.md) | ST-DEPENDENCY | `experimental_proposal` | a collaborator with an EMC line |
| [RT-PRAME-IMMTAC](L2-rt-prame-immtac.md) | ST-IMMUNO | `experimental_proposal` | expression confirmation on EMC tissue |
| [RT-SSTR2](L2-rt-sstr2.md) | ST-RADIOLIGAND | `experimental_proposal` | any expression measurement in EMC |
| [RT-TRABECTEDIN-PPARG](L2-rt-trabectedin-pparg.md) | ST-REPURPOSING | `experimental_proposal` | the direction of the PPARγ effect in EMC |
| [RT-METHODS-PAPER](L2-rt-methods-paper.md) | ST-DISSEMINATION | `journal_submission` | — |
| [RT-ASO](L2-rt-aso.md) | ST-NUCLEIC-ACID | `chemrxiv` | a named delivery candidate |
| [RT-ATR-ASSESS](L2-rt-atr-assess.md) | ST-DEPENDENCY | `preprint` | an EMC-specific measurement |
| [RT-DEGRADER](L2-rt-degrader.md) | ST-PROXIMITY | `preprint` | a passing selectivity known-answer control; an anti-target panel that recovers its own cognate ligands |
| [RT-PANNR4A-EXVIVO](L2-rt-pannr4a-exvivo.md) | ST-IMMUNO | `preprint` | a cellular persistence readout |
| [RT-ASYMMETRIC](L2-rt-asymmetric.md) | ST-OCCUPANCY | `reproducible_workflow` | — |
| [RT-TCIP](L2-rt-tcip.md) | ST-PROXIMITY | `reproducible_workflow` | the enumeration run for this configuration |
| [RT-6MP](L2-rt-6mp.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-AF3-INTERFACE](L2-rt-af3-interface.md) | ST-PROXIMITY | `internal_note` | a co-folder validated on assembly |
| [RT-ANDGATE](L2-rt-andgate.md) | ST-PROXIMITY | `internal_note` | arm-2 chemistry |
| [RT-B7H3](L2-rt-b7h3.md) | ST-IMMUNO | `internal_note` | a tissue-level measurement |
| [RT-CARFILZOMIB](L2-rt-carfilzomib.md) | ST-REPURPOSING | `internal_note` | a resolvable primary citation for the ex-vivo evidence |
| [RT-CART-SURFACE](L2-rt-cart-surface.md) | ST-IMMUNO | `internal_note` | a selective surface antigen |
| [RT-COVALENT-PROBE](L2-rt-covalent-probe.md) | ST-OCCUPANCY | `internal_note` | a criterion that passes its positive control |
| [RT-CRISPR-CAS13](L2-rt-crispr-cas13.md) | ST-NUCLEIC-ACID | `internal_note` | a solid-tumour vector |
| [RT-DBD](L2-rt-dbd.md) | ST-FUSION-DIRECT | `internal_note` | — |
| [RT-EWSR1-PROTEIN](L2-rt-ewsr1-protein.md) | ST-FUSION-DIRECT | `internal_note` | — |
| [RT-FAP-RLT](L2-rt-fap-rlt.md) | ST-RADIOLIGAND | `internal_note` | any measurement in EMC |
| [RT-FET-LC-LIGAND](L2-rt-fet-lc-ligand.md) | ST-FUSION-DIRECT | `internal_note` | — |
| [RT-GLUE](L2-rt-glue.md) | ST-PROXIMITY | `internal_note` | a prospective glue design method |
| [RT-HDAC-BET](L2-rt-hdac-bet.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-ICI-TKI](L2-rt-ici-tki.md) | ST-IMMUNO | `internal_note` | a larger clinical series |
| [RT-JUNCTION-NEOANTIGEN](L2-rt-junction-neoantigen.md) | ST-IMMUNO | `internal_note` | regenerated predictions against the corrected exon index |
| [RT-MONOVALENT](L2-rt-monovalent.md) | ST-OCCUPANCY | `internal_note` | a functional readout; a sized selectivity requirement |
| [RT-PPARG-DOWNSTREAM](L2-rt-pparg-downstream.md) | ST-REPURPOSING | `internal_note` | a directional read of the PPARγ axis in EMC |
| [RT-RIBOZYME](L2-rt-ribozyme.md) | ST-NUCLEIC-ACID | `internal_note` | a solid-tumour vector; a modern demonstration of trans-splicing ribozymes |
| [RT-RIPTAC](L2-rt-riptac.md) | ST-PROXIMITY | `internal_note` | paralogue selectivity; a chemistry programme |
| [RT-RXR](L2-rt-rxr.md) | ST-REPURPOSING | `internal_note` | — |
| [RT-SYNLETH-DEP](L2-rt-synleth-dep.md) | ST-DEPENDENCY | `internal_note` | EMC-specific functional-genomics data |
| [RT-SYNPROMOTER](L2-rt-synpromoter.md) | ST-NUCLEIC-ACID | `internal_note` | a direct binding-specificity read in EMC |
| [RT-TCR-IMMTAC](L2-rt-tcr-immtac.md) | ST-IMMUNO | `internal_note` | a stronger presented epitope |
| [RT-TCRT-CTA](L2-rt-tcrt-cta.md) | ST-IMMUNO | `internal_note` | a real EMC expression series |
| [RT-TRABECTEDIN](L2-rt-trabectedin.md) | ST-REPURPOSING | `internal_note` | a larger clinical series |
| [RT-UBIQ-SELECTIVE](L2-rt-ubiq-selective.md) | ST-PROXIMITY | `internal_note` | an observed transfer geometry |
| [RT-VACCINE](L2-rt-vaccine.md) | ST-IMMUNO | `internal_note` | an immunogenicity argument |

[← L0](L0-ecosystem.md)
