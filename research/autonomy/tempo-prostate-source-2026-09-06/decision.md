---
id: DOC-TEMPO-PROSTATE-SOURCE-20260906
title: Exact-v2 TempO-Seq prostate metadata supplies no deposited bridge to EMC
kind: memo
status: live
purpose: Preserve a specific public normal-reference source and its actual limitations.
scope: PMC10095552 and E-MTAB-12593 metadata and primary methods; no expression analysis.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

The primary article and public BioStudies JSON, IDF and SDRF were recovered through ordinary
public Europe PMC and EBI accession-only endpoints. Original bytes and status/time/hash receipts
are retained. A historical reviewer link in the published article was not used for access.

The complete SDRF contains 45 regions from 15 male prostate-cancer patients: each contributes
one neoplasm, one microenvironment and one normal-tissue region. These are 15 normal regions
from cancer patients, not 45 patients or healthy-donor tissue. All source sample and ENA run
identifiers are retained in sample-map.json. The primary methods describe pathologist-annotated
regions on adjacent unstained FFPE sections and the Human Whole Transcriptome v2.0 panel with
standard attenuators, 22,537 probes, STAR/TempO-SeqR mapping with up to two mismatches.

The article states that internal processing-control RNA and no-sample negative controls ran
on each plate. The public study's file inventory contains only IDF and SDRF, with biological
sample FASTQ links into ENA ERP144175. No processed count matrix or shared control measurement
was identified in this inventory. This is a statement about the inspected deposit, not every
possible supplementary or future source. No reads, count values or expression outcomes were
downloaded or analyzed.

Exact panel version improves assay matching to the EMC export but does not by itself establish
measurement invariance or separate tissue from study effects. This source does not supply an
EMC-bearing within-study comparator. No normal-only analysis or raw-read processing is selected.
The independent comparability decision in the portfolio narrows the actual requirement to an
identifiable gene-specific within-study contrast; absolute calibration and protein are not
universal prerequisites for RNA-only replication.
