---
id: DOC-CHECKPOINT06-HLA-CRYPTIC-EVIDENCE
title: Historical cryptic-search gap and one deposited protocol witness
kind: memo
status: live
date: 2026-10-02
last_verified: 2026-10-02
audience: [external reviewers]
purpose: Distinguish a qualified search construction from verified sequence representation and serialized per-output metadata.
scope: Marcu 2021 primary XML, PXD019643 deposit metadata, one bounded mzIdentML output; no spectrum reanalysis or publication clearance.
---

The historical cryptic-search construction is documented, but representation of the four provisional sequences remains unknown. This checkpoint also recovered one checksum-verified output whose serialized protocol names the canonical FASTA and reports fields differing from the paper and project summaries. Those fields are evidence about the deposited output, not independent proof of execution settings.

## Frozen question and inspected sources

The frozen question and stop condition are in plan.md. The coordinator supplied base 5fd0416de98158880d49689cda0861c3baa0a3a1. The base RESULTS.md and manuscript-draft.md were read through GitHub's file API after finding the local checkout deliberately stale; their Git blobs were 1dc784aa2cbb6890f1afe15170fee0ed44cb69a3 and 0e687680b20379d91e677cfbb65750f72f14d197. The previously completed canonical scan and processed-release analysis were not repeated.

The reused [primary XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8054196/fullTextXML), in the methods paragraph beginning "Identification of cryptic HLA-I peptides", reports PEAKS Studio X, ten de novo candidates per fragment spectrum, Peptide-PRISM matching against six-frame HG38 and three-frame Ensembl 90 transcriptome translations, stratified 10% FDR, and NetMHCpan-4.0 binder prediction. Figure 5A independently describes that construction. The names HG38 and Ensembl 90 qualify the intended reference context; they do not identify the exact input file bytes, record selection, annotation package, translated index or Atlas-specific run configuration. All four sequence-representation statuses remain UNKNOWN. A six-frame reference-genome search is not automatically a fusion-junction search, and a provisional fusion sequence may not be declared absent without checking the qualified historical inputs.

The [deposit README](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/04/PXD019643/README.txt) has 3,425 rows: 1 FASTA, 1,471 PEAK, 1,470 RAW and 483 RESULT. Its sole FASTA is the already examined canonical object. Filename screening for cryptic, prism, denovo or parameter found only the synthetic-cryptic-peptide raw file. This describes the README and filename screen, not every file's contents or all possible external deposits. No historical cryptic input object or per-run PEAKS/Peptide-PRISM configuration was identified in this bounded audit.

The cited algorithm paper, Erhard et al. (2020), DOI 10.1158/2326-6066.CIR-19-0886, was accessible as a search-indexed primary-publisher methods excerpt, but direct publisher retrieval returned HTTP403. It describes optional additional search classes beyond the genome/transcriptome core. That generic capability is not evidence those options were used by the Atlas; no Atlas-specific settings are inferred from it. It is contextual only and is not a pinned database input.

## New deposited protocol witness

We selected the smallest fileSizeBytes among the 16 RESULT entries in the reused 100-row PRIDE response, breaking ties by filename. We did not claim this was the smallest of all 483 outputs. This size-based selection chose AM_AUT01-DN13_Skin_W6-32_10_DDA_merged_400-650mz_standard_all_ids_merged_psm_perc_filtered.mzid.gz. It was the first and only result output fetched; no failed result alternatives preceded it. The [exact official object](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/04/PXD019643/AM_AUT01-DN13_Skin_W6-32_10_DDA_merged_400-650mz_standard_all_ids_merged_psm_perc_filtered.mzid.gz) returned 78,546 compressed bytes. Its SHA1 equals the PRIDE checksum 6fd0ddf159917003808f1c93843b45520f2324f7. SHA256 is ebbae14f847dd4a3a554c5b818fa1399fbdc2005a22b46288ab1690b3570e1ed. PRIDE's fileSizeBytes of 814,334 equals the decompressed XML length, not the compressed response length. The metadata does not explicitly name its checksum algorithm.

The source uses namespace http://psidev.info/psi/pi/mzIdentML/1.1. The following locations are relative to that namespace; the exact elements are preserved in sample-run-parameters.xml and the complete original compressed object is retained as sample-run.mzid.gz.

| Source location | Serialized field | Observed value |
| --- | --- | --- |
| AnalysisSoftwareList/AnalysisSoftware[@name='Percolator']/@version | Percolator version | 3.02 |
| AnalysisSoftwareList/AnalysisSoftware[@name='TOPP software']/@version | TOPP version | OpenMS TOPP v2.5.0-HEAD-HASH-NOTFOUND-HEAD-HASH-NOTFOUND |
| AnalysisProtocolCollection/SpectrumIdentificationProtocol/AdditionalSearchParams/userParam[@name='Comet:db']/@value | database | sp_21_04_2020_decoy.fasta |
| DataCollection/Inputs/SearchDatabase/@location | database location | sp_21_04_2020_decoy.fasta |
| AnalysisProtocolCollection/SpectrumIdentificationProtocol/ParentTolerance/cvParam | positive and negative tolerance | 6.0 parts per million |
| AnalysisProtocolCollection/SpectrumIdentificationProtocol/FragmentTolerance/cvParam | positive and negative tolerance | 0.01 dalton |
| AnalysisProtocolCollection/SpectrumIdentificationProtocol/AdditionalSearchParams/userParam[@name='Comet:variable_modifications']/@value | variable modifications | Oxidation (M) |
| AnalysisProtocolCollection/SpectrumIdentificationProtocol/AdditionalSearchParams/userParam[@name='Comet:digestion_enzyme']/@value | digestion | unspecific cleavage |

This internal database reference strengthens the submission-level association for this one output only. It does not identify a separate cryptic search space. The primary paper reports Percolator 3.4 and 5 ppm precursor tolerance; the project protocol reports Percolator 3.1.1. Neither is identical to this output's serialized version/tolerance. The paper's 0.02 Da Comet fragment-bin tolerance and mzIdentML's plus/minus 0.01 Da fragment tolerance may denote different parameter quantities; we do not treat them as an execution contradiction or equate them. We have not established whether these fields reflect execution, conversion defaults, or another stage. The output's training/test FDR fields and generic Threshold element likewise must not be substituted for the final identification filter.

## Remaining primary gap and stopping decision

A historical cryptic-representation scan needs the exact genome/transcriptome sequence and annotation files or an author-qualified reproducible construction manifest, with record selection, relevant software version and options. Determining whether any query was actually evaluated in a particular spectrum further needs the Atlas-specific PEAKS candidate exports and Peptide-PRISM run configuration. Sequence representation alone would still not establish candidate generation, identification, HLA presentation or measured absence.

The supplementary PDF could contain useful details but was not inspected: the BMJ and Europe PMC routes returned 403; PMC returned HTML rather than PDF; the blob URL derived from XML returned 404. These failures are preserved in retrievals.jsonl. No access challenge was bypassed. We do not claim that the inaccessible supplement lacks the needed input. No new qualified sequence input was obtained, so no cryptic scanning script or cloud dispatch is warranted. The smallest next action is to recover that supplement or a historical Atlas cryptic-input/configuration manifest; re-scanning the canonical FASTA would not resolve this gap.

## Optional replacement paragraph for the working draft

One deposited DN13 skin class-I mzIdentML output internally names sp_21_04_2020_decoy.fasta. Its serialized protocol reports Percolator 3.02 and a precursor tolerance of 6 ppm, differing from the paper's summary. These fields do not independently establish execution settings, and this single output cannot characterize all runs. The cryptic analysis instead used PEAKS candidates and translations of HG38 and Ensembl 90. We did not recover exact historical cryptic input files or Atlas-specific configurations, so representation of the four queries in that search remains unresolved. Neither canonical sequence absence nor this metadata audit establishes a negative mass-spectrometric test or absence of HLA presentation.

## Validation and limits

The audit.py script verifies the compressed checksum, observed decompressed length, metadata selection, README type counts and source hashes. XML parsing succeeded. The companion note preserves all prior uncertainty; no biological claim was strengthened. No new empirical spectrum search, canonical scan, processed release analysis, checkout, git operation, UI operation, runtime install, paid computation, publication or outreach occurred. The unavailable system python alias was replaced by the already installed bundled Python. The task used small scoped files on a low-space volume and stopped after one concrete metadata witness and a defined cryptic-input gap; no process remains running.
