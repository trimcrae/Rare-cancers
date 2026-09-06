---
id: DOC-ZULLOW-EMC-SOURCE-20260906
title: Zullow 2022 seven-EMC expression source check
kind: memo
date: 2026-09-06
last_verified: 2026-09-06
status: live
purpose: Decide whether the named Zullow seven-EMC cohort supplies a usable public expression source.
audience: [maintainers, autonomous research agents]
scope: Source metadata and provenance only; no expression analysis
---

No publicly usable seven-EMC expression asset was identified in the named deposit or the
directly documented source chain. This is a precise source-level stop, not proof that the
measurements never existed or that no other public repository contains them.

## Primary source and deposited records

The recovered original [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9465545/)
is the author manuscript for PMID 35390276, DOI 10.1016/j.molcel.2022.03.019. Its Human
Subjects methods report 10 MLS, 10 Ewing and 7 EMC RNA-seq cases, diagnosed by two MD Anderson
pathologists. Tumor RNA isolation describes snap-frozen MD Anderson Institutional Tissue Bank
material, pathology review, and Qiagen RNA isolation. These are article-level statements, not
recovered individual EMC identifiers.

The Tumor RNA-seq Data Analysis methods explicitly describe EMC and MLS as sequenced in this
study, with STAR gene counts. They describe Ewing and SMARCB1-null tumor data as obtained from
McBride 2018 and counted with FeatureCounts. This creates an unresolved distinction between
the Human Subjects Ewing cases, deposited Ewing records, and the Ewing data used in the published
contrast. Do not treat all article comparator data as one uniformly generated cohort.

The [GEO family SOFT](https://ftp.ncbi.nlm.nih.gov/geo/series/GSE179nnn/GSE179720/soft/GSE179720_family.soft.gz)
has 138 sample records: 53 RNA-Seq, 46 ChIP-Seq, 16 ATAC-seq and 23 OTHER. Of these, 22 have
primary-tumor source metadata and RNA-Seq strategy: 12 MLS (GSM5429866–GSM5429877) and 10
Ewing (GSM5429902–GSM5429911). No complete SOFT text matches EMC, chondrosarcoma or NR4A3.
This conclusion uses the complete family metadata and sample characteristics, not the title.
The linked BioProject PRJNA744758 ENA run report independently contains 138 distinct samples
and runs; every primary RNA sample title matches a GEO record. No additional primary EMC
record emerged in this project report. The deposit's series-level supplementary asset is only
GSE179720_RAW.tar; individual processed STAR count URLs exist for the MLS/Ewing samples.
The tar and individual expression files were not downloaded.

`primary-RNA-crosswalk.tsv` preserves exact GSM, sample title, sample-label and specimen-string
tokens, group characteristics, platform, BioSample and SRA relations, matched ENA runs, library
layout/instrument, and exact processed RNA URLs. Filename specimen strings are not asserted to
be unique biological patients. All 22 deposited primary RNA records specify NextSeq 500,
single-end libraries. Metadata describes hg19/refFlat and STAR v2.5.2b count generation.
No gene identifiers or expression measurements were inspected; exact gene mapping remains a
dependency if a relevant EMC asset is later supplied.

## Missing Table S1 and unresolved MLS counts

The actual article link is
https://pmc.ncbi.nlm.nih.gov/articles/instance/9465545/bin/NIHMS1790495-supplement-2.xlsx.
Its caption identifies patient/tumor metadata for MLS, DSCRT, Ewing, EMC and low-grade
fibromyxoid sarcoma, not an expression matrix. The article advertises a 14.4 KB workbook.
The retrieved response was HTTP 200 but only 1,816 bytes of HTML with `POW_CHALLENGE`.
**`TableS1.xlsx` in this packet is those original challenge-response bytes, not a valid XLSX.**
The ZIP-signature check fails. No challenge was executed or bypassed. The DOI resolver yielded
a publisher redirect to Cell, whose article endpoint returned HTTP 403. Table S1 was therefore
not recovered and no worksheet, cell range, or patient row was inferred.

The paper reports n=10 MLS; the deposit has 12 MLS records, including MLPS001 and MLPS008 in
GSM5429876/77. The article states outlier replicates were excluded after visual inspection of
a clustered heatmap. It does not identify excluded samples in the inspected methods.
This is a possible explanation for the numerical discrepancy, not a demonstrated reconciliation.
In particular, the last two GSM records must not be silently designated the excluded two.

## Directly reused source chain

The key resources table names SRP052896 as reused BAF-perturbed-cancer RNA-seq (Le Loarer 2015).
Its public ENA report was preserved (35 run records); several titles are generic, so absence of
an EMC title there is not proof of absent EMC. More decisively, Zullow's methods assign their
EMC to newly sequenced material and do not identify this reused accession as its origin.

The directly cited [McBride 2018 article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6791822/)
was recovered. Its data availability identifies GSE108028 for cell lines and deidentified NCI
synovial-sarcoma RNA, and EGA EGAS00001002920 for patient-associated MD Anderson synovial
and epithelioid sarcoma samples. Its article text has no EMC or chondrosarcoma match. It does
not document a transfer of Zullow's seven EMC cases to that source. No controlled-access request
or additional raw-data retrieval was attempted. These links do not establish the missing EMC
expression asset.

## Independence and batch assessment

The source supports newly profiled institutional EMC/MLS material, but Table S1 is unavailable
and the EMC sample records are missing. Recruitment independence from the existing atlas
cohort is consequently unverified. Institutional affiliation alone was not used to assert
independence or overlap, and no broad local provenance inventory was opened.

Shared article-level library/counting methods make a within-study EMC-versus-MLS comparison
a plausible future route. They do not establish that tissue group and technical batch are
not completely confounded. The MLS titles share date token 20190408 and Ewing titles share
20190920; these are filename tokens, not verified sequencing-batch assignments. There is no
EMC date/run metadata to assess crossing or adjustment. Quantile normalization in the published
analysis does not supply missing batch comparability. Raw counts, absolute calibration and
protein measurements are not being imposed as universal requirements here.

Next concrete dependency: a public EMC gene-level measurement asset with documented sample
labels and relevant comparator/batch provenance, plus the Table S1 crosswalk if available.
Recovering Table S1 alone would clarify subjects but would not establish deposited expression.
No expression analysis is ready to commission from this packet.

## Audit and execution

Original successful response bytes, exact URLs, HTTP statuses, UTC retrieval start times,
headers, sizes and SHA-256 values are in `retrievals.jsonl`. HTTP failures retain URL/time/error
but their response bodies were not captured. An initial ENA request had literal backticks in
the URL and returned 400; the corrected quoted request succeeded. Europe PMC fullTextXML
and the initial NCBI OA utility URL returned 404. The successful original article HTML came
from an ordinary anonymous GET to its public URL. A web-tool rendering showed a challenge;
no browser challenge was solved. No credentials, spending, outreach or access escalation.

`build_metadata.py` reproducibly builds the metadata crosswalk and checks, without opening
measurement files. `checks.json` records all seven successful response hash checks, sample
counts, ENA matching, and detection that the supposed workbook response is HTML. The initial
text extraction encountered absent bs4 and Windows stdout encoding; extraction then used
the standard-library HTML parser and UTF-8 output. These were extraction failures, not passed
analyses. No repository gate or publication check was run, as allocated. No commit was made.

Worker: isolated source task `zullow_emc_source`; model GPT-6 (exact runtime variant not exposed
in this worker), effort inherited (contract requested medium; no independent runtime record).
Base 6ca5e76b559914510e28c0c6ad4bfb7ad1a3c544. Started approximately 06:59 UTC;
freeze time and elapsed are in `execution.json`. Subscription usage unavailable. Only this
packet directory was written. No asynchronous processes or background tasks remain running.
Coordinator verification/integration remains outstanding.

Metadata-only amendment, 2026-09-06: repository document metadata now uses the required schema;
the scientific source-stop decision and all source bytes remain unchanged. The original README
and freeze manifest are preserved in `README-original.md.txt` and `manifest-original.json`.
The original invalid `TableS1.xlsx` response filename is retained with the warning above.
