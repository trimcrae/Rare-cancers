---
id: DOC-NGO-EMC-SOURCE-20260906
title: Ngo external mesenchymal RNA panel source stop
kind: memo
status: live
purpose: Preserve the recovered public source evidence and identify the missing EMC comparator asset.
scope: Ngo2025 article, exact supplements, linked figure repository, and exact EGA DAC metadata; no expression analysis.
audience: [maintainers, autonomous research agents]
date: 2026-09-06
last_verified: 2026-09-06
---

The named external panel is reported to contain EMC, but this source recovery did not establish a downloadable EMC gene matrix or sample roster. Stop this route at source availability. It is not an independent validation dataset ready for analysis, and is not evidence that no such data exist elsewhere.

## Resolved provenance

- Ngo2025: PMID41313621, PMC12728484, DOI10.1002/cac2.70077. The exact article JATS was copied without a second retrieval from the coordinator's recovered source; its original retrieval receipt is preserved in `article-retrieval.json`.
- Figure 1I's legend describes an external RNA-seq panel of 1,041 samples from 32 mesenchymal entities, and defines EMCS as extraskeletal myxoid chondrosarcoma. This supports reported EMC inclusion only. It does not give EMC sample count, patient IDs, gene columns, or an accession.
- Supplementary methods page 3, lines 78-80, attribute an external cohort of **12 EpS and 1,041 selected soft tissue tumors** to Centre Leon Berard, Lyon, France. Preserve those two quantities separately: the source does not say that the 12 EpS are included in 1,041. No original panel accession or source citation accompanies this statement.
- The source describes study scRNA-seq and spatial data as EpS. They must not be recast as EMC measurements.

## Exact public assets inspected

The EuropePMC `PMC12728484/supplementaryFiles` endpoint returned HTTP200 and a valid 5,387,708-byte ZIP. Its original bytes are `supplementary-response.bin`. Its four members are the article figure GIF/JPG and the exact `CAC2-45-1760-s001.pdf` / `CAC2-45-1760-s002.xlsx` supplements. The two supplements are extracted without rewriting. `retrieval-log.json` records HTTP status, URLs, timestamps, headers and SHA256 hashes. The source archive and extracted member checksums are independently checked by `verify_inventory.py`.

The PDF has 39 pages. Relevant methods pages 3, 4, 12 and 13 were text-extracted, rendered with Poppler and visually inspected. Page 3 identifies the provider; pages 12-13 describe signature evaluation on the 1,041-sample panel. The PDF does not provide an external-panel accession or an EMC roster in those methods. The full extraction is retained for checking source context, not as an analysis output.

The XLSX contains ten sheets, Supplementary Tables S1-S10. `xlsx-inventory.json` preserves dimensions, titles and headers only. These are histological criteria, study cohort clinical metadata, EpS/EERT differential results, EpS enrichment results, study molecular assays/variants, EpS cell-cluster markers, and antibodies. No sheet is an external-panel gene-by-sample matrix or external-panel roster. During initial format inspection, a five-row preview incidentally displayed some first data rows; no expression results were analyzed or used, and the durable inventory was narrowed to header rows only.

The article's actual ASCII GitHub href resolves publicly. The API root listing contains only LICENSE, Main and README.md; Main contains five scripts for Figure1B,1C,1E,1H,1K/Sup15A. There is no Figure1I script in that listing and no expression or metadata directories. The README's illustrative tree and required input filenames are not downloadable data. Original repository listings with Git blob/tree hashes and the README bytes are frozen. No script was executed and no repository-wide biological analysis was performed.

## EGA scope

The exact public DAC page for EGAC50000000552 lists one dataset, **EGAD50000001419**, with this scope: bulk RNA-seq of 33 EpS and 3 EERT; WES of 30 EpS and 3 EERT; scRNA-seq of 8 EpS; Visium spatial transcriptomics of 3 EpS. Its Samples column says 99; this is not established to mean 99 distinct patients. The page does not identify EMC or the external 1,041-sample panel. Thus this DAC is evidence for the study EpS/EERT deposition, not the external panel's accession. The article names policy EGAP50000000502, but policy membership was not separately inspected.

Python's initial EGA fetch failed certificate verification. A normal curl fetch using system certificate trust returned HTTP200; TLS verification was not disabled. Original response bytes and response headers are retained. No login, access request or contact occurred.

## Technical comparability remains unresolved

The study bulk methods describe FFPE RNA, TruSeq RNA Exome capture, paired-end 2x75 sequencing on NextSeq/NovaSeq, STAR against hg19, Salmon1.4/GRCh37 and DESeq2 variance stabilization. They do not explicitly map those preparation/platform statements to each external EMC sample. The external-panel comparison section reports variance-stabilized raw counts, per-gene Z scores and exclusion below 10 million unique reads. This describes the published processing, not a new filtering proposal. No sample-level batch, preservation, library or recruitment metadata were recovered for the external EMC subset. The published transformation alone cannot establish comparability with this program's existing EMC data, nor recruitment independence or lack of sample overlap.

## Freeze and next action

Actual EMC count: unknown. Actual EMC sample identities: unknown. Original external-panel accession: unestablished. Gene-level matrix: not supplied in inspected supplements or linked repository. Independent recruitment and batch comparability: unverified. The next useful evidence would be a public, explicitly identified Centre Leon Berard external-panel gene matrix accompanied by sample diagnosis and provenance metadata. Do not reopen on the same unchanged article/DAC/README alone.

This isolated writer worked from `43dcda877f8d634701ce9bdecb88ac884416ff02` and changed only this directory. Model family: GPT-6; parent allocation specifies medium; exact executable model variant and token usage were not exposed to this worker. Bounded allocation: at most 15 minutes. Validation: source SHA256 checks, ZIP CRC/member-byte checks, XML/PDF/XLSX parse checks, ten-sheet inventory, GitHub listing structure and targeted PDF visual review. No repository gates, commits, manuscript edits, expression contrasts, target selection, classifier, controlled-data access or paid work were run. All subprocesses used for this task completed; nothing remains running. This is a source-stop packet for coordinator verification, not manuscript readiness.
