---
id: DOC-PUB-ASO-CONTRIBUTION-20260929-README
title: "ASO letter with the contribution stated at the outset"
kind: runbook
status: live
date: 2026-09-29
last_verified: 2026-09-29
purpose: Bind the revised author review letter to its source evidence and unchanged scientific results.
scope: Narrative revision and authorized GitHub proofreading copy only.
audience: [maintainers, external reviewers]
---

# ASO letter with the contribution stated at the outset

The letter now opens with the specific EMC model correspondence and additional normal RNA matches. It explains how the author generated the designs and why these seven junctions were selected. The model example identifies Bangerter and colleagues' cell model and Figure 4b explicitly. The normal RNA analysis is described as this study's comparison. The contribution remains a sequence mapping and comparison resource; it is not evidence of an effective or selective ASO.

`letter.md` is the manuscript source. `ASO-letter.docx` and `ASO-letter.pdf` are the proofreading files. `build_letter.py` is byte-identical to the accepted September 28 builder. The layout and rendering workflow are unchanged. The final letter contains 486 main-text words and five references across two pages. Counts and artifact hashes are recorded in `build-report.json` and `editorial-verification.json`.

The only added literature reference is Tanaka et al. The full primary paper was inspected to support the limited statement that fusion-junction ASOs have been experimentally tested. Its breakpoint-directed oligonucleotides must be distinguished from its most extensively tested initiation-region oligonucleotide, which also affected normal EWS RNA. `citation-evidence.json` records the source, inspected locations and claim boundary. No experimental result from that paper is attributed to EMC or to the present designs.

## Scientific evidence

The accepted scientific candidate at `840e567796e27ee0d95e6da68d55a269dcd51e40`, its eight-page Supplementary Methods and its data archive remain unchanged. The September 27 and September 28 proofreading candidates are preserved intact. The new letter reuses the existing results and does not recalculate the full catalogue.

All 35 designs are the author's existing computational designs: 20 from the primary 190-design panel, five from the noncoding-acceptor extension and ten from the cryptic-exon extensions. Five separate hypothetical label-transfer controls remain excluded. Selection is based on source correspondence, with all five binding positions retained for each selected junction. The exact lineage and source classes are preserved in the accepted Supplementary Methods, sections S1–S3, and its design/input tables.

The [versioned data and code archive](https://doi.org/10.5281/zenodo.22986104) supplies exact sequences, source records, controls, adverse results and offline reproduction. Supplementary Methods sections S5 and S7 distinguish new findings from preceding work and preserve unresolved evidence. Earlier interpretation corrections remain part of that record; the present letter does not characterize them as errors in the primary cell-model paper.

## Verification and handoff

One independent read-only advisor checked the revised contribution, design lineage, primary citation and fidelity to accepted results. No blocker or repair was identified. Root inspected both rendered pages and checked that the Markdown, Word and PDF text agree. The accepted scientific ultra review and full verification are reused for unchanged science only.

External source, render and coordinator receipts are retained under `work/aso-contribution-format-20260929/` in the orchestrator workspace. The coordinator owns the settled-tree normal gate, narrow commit, nonforce GitHub proofreading push, public-byte verification and ownership release. The new candidate is frozen at handoff.

This revision does not authorize a journal submission, public preprint update, data-deposit change, main merge, pull request or contact with researchers. Journal and article-type selection and final author review remain separate.
