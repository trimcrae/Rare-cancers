---
id: DOC-METHYLATION-DENOMINATOR-AUDIT-20261002
title: Exact QC exclusions and source-native diagnostic eligibility in E-MTAB-9875
kind: memo
status: live
audience: [maintainers, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
purpose: Recover the excluded array identities and original eligibility fields without computing classifier performance.
scope: Primary Table S1, Table S3 denominator cells, supplementary methods, previously retrieved primary XML, and six SDRF channel records for three QC exclusions.
---

The three QC exclusions are recoverable by exact case and array identifiers. Primary Supplementary Table S1 contains 986 distinct case numbers. Its column J directly labels 820 rows `Yes`, 163 `No`, and three `FAILED`. Thus the source-native retained denominator is 983, without imposing a new diagnosis mapping or score threshold.

| Case | Sentrix identifier | Table S1 row | Final diagnosis | Histological subtype | SDRF source name and lines |
|---|---|---:|---|---|---|
| 847 | 203259060018_R07C01 | 806 | Osteosarcoma | Telangiectatic | Case_847; 1968–1969 |
| 848 | 203259060018_R08C01 | 807 | Osteosarcoma | Osteoblastic | Case_848; 1970–1971 |
| 982 | 203869580141_R08C01 | 938 | Osteosarcoma | Osteoblastic | Case_982; 1972–1973 |

Each identity is supported by Table S1 columns A/B and the exact red/green array filenames in the SDRF. The SDRF line numbers include its header. The three rows carry `FAILED` in H, J, N, O and Y, with `NA` in score column P. All three are recorded as EPIC and DNA FT in columns C/D. The paper states that three tumour samples failed the classifier QC, but the inspected table and supplementary methods do not identify the failed metric, threshold or case-specific technical reason. The recovered exclusion identities close the identity gap; specific QC reasons remain unavailable in these inspected sources. No cause was inferred from tumour purity, array position, histology, or tissue preparation.

The main-text coordinate for the exclusion statement is XML section `cjp2215-sec-0006`, first direct paragraph. The definition of represented and unrepresented diagnoses is section `cjp2215-sec-0003`, third direct paragraph. The latter states that core cases have diagnoses represented in classifier v12; unrepresented cases do not. These definitions explain Table S1 J without creating a new taxonomy.

Table S1 supports an exact **source-native** eligibility and adjudication ledger. `source-native-eligibility.tsv` copies 14 selected source columns for all 986 cases, with sheet and row coordinates. It preserves the authors' J flags, rather than recomputing membership from predictions. The retained fields include final diagnosis (F), subtype (G), diagnosis summary (H), initial diagnosis if modified (I), core membership (J), review findings (L), revision flag (M), prediction group (N), predicted class (O), and the supplied calibrated score (P). Demographics, anatomical site, purity and the full score vector were not needed in this derivative ledger. This is a source record, not an eligibility decision for the separate frozen 12-class experiment.

Six cases have revision flag M=`Yes`: 166, 254, 287, 884, 964 and 965. Their initial/final diagnosis pairs and review findings are preserved in `revised-diagnoses.tsv`:

| Case | Initial diagnosis, column I | Final diagnosis, column F |
|---|---|---|
| 166 | Myxofibrosarcoma | Malignant peripheral nerve sheath tumour (MPNST) |
| 254 | UPS | Leiomyosarcoma |
| 287 | UPS (High grade spindle cell sarcoma) | Dermatofibrosarcoma protuberans |
| 884 | Osteosarcoma osteoblastic | Sclerosing epithelioid fibrosarcoma |
| 964 | MPNST | CIC-rearranged sarcoma |
| 965 | MPNST | BCOR-rearranged sarcoma |

The methods describe review of discrepant results using pathology and available radiological, immunohistochemical and molecular evidence. These fields therefore permit a record of source adjudication but do not establish diagnoses assigned independently of classifier results. Column I is not a complete original-diagnosis column: most cells are blank, and case 1015 (row 967) contains `Central` despite M=`No`. A nonblank I field alone must not be converted into a revision flag. No missing initial diagnosis was filled from the final diagnosis.

A source discrepancy remains. In Table S3, D3 and E3 label the core validation cohorts at the source's 0.9 and 0.85 thresholds. D4 and E4 both contain the literal numeric value 821 under A4, `Total cases (excluding failed cases)`. Table S1 instead has exactly 820 `Yes` records, agreeing with the main text. The Table S3 values are constants, not formulas or stale formula caches. This bounded inspection establishes the discrepancy but does not explain its cause or identify an extra case. We did not alter either source, add a case, or select a threshold to reconcile it.

For future score transport, this ledger supplies explicit source QC exclusions, represented/unrepresented flags and adjudication fields. It does not by itself provide a prespecified mapping into another taxonomy, independent reference diagnoses, full vote-scale equivalence, or shared patient identifiers across studies. No classifier, performance metric, loss, threshold optimization, old 2,491-row overlap comparison, or raw-IDAT download was executed here.

Reproduction: run `audit_denominator.py` with the existing checkpoint03 source directory as its optional first argument. It verifies all four input hashes, checks the 986 unique cases and source-native flags, exports the ledger, and looks up only the three new exclusions in the SDRF. The executed audit passed. Root must independently inspect the recovered cells before integration. This checkpoint makes no publication-readiness claim.

Primary sources and SHA256:

- [Lyskjær et al. primary XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8185366/fullTextXML), previously retrieved `lyskjaer.xml`: `31c0987584ecc056960d5e4e6800efd3de8858598769240bb432f1f8b0077ba5`.
- [Primary supplements archive](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8185366/supplementaryFiles), member `CJP2-7-350-s001.xlsx`, 494,859 bytes: `6e549cfb75cc37f7cc7c0efc9c715917282b376e7f172155fee01f538c69587b`. XML attachment `cjp2215-supitem-0003` identifies this workbook as Tables S1–S5.
- Same archive, methods member `CJP2-7-350-s003.docx`, 22,875 bytes: `b658f5dfad81235e7be7a5546ef503c489b605573ec35cd496ddef5c4bcafe26`. XML attachment `cjp2215-supitem-0001` identifies this member as supplementary methods. Text extraction preserves numbered paragraph coordinates.
- [E-MTAB-9875 SDRF](https://www.ebi.ac.uk/biostudies/files/E-MTAB-9875/E-MTAB-9875.sdrf.txt), previously retrieved: `c6ffc854493f95d3b1c70bc18e0862abf269ea889e7ca2db153d435c80adc216`.

Direct PMC attachment requests returned HTML rather than Office bytes; two CDN alternatives returned 404. A Wiley alternative returned 403. Those access failures do not establish missing data. Europe PMC returned the actual 1,718,242-byte ZIP, hash `7037cc223859c46bb724da29db66f169e53a1fb3160c3310b2af8de5adbd59f8`. Only the workbook and methods members were persisted; the archive and figure supplements were not saved. `retrieval.json` records the successful archive/member hashes and initial failed attempts. The remaining failed probes are described here. Existing Python/openpyxl was reused; no runtime or package was installed. No UI, browser automation, rendering or build was run.
