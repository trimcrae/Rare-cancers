---
id: DOC-PEERJ21497-SOURCE-20260906
title: Data S1 supplies twelve processed EMC columns but leaves atlas validation dependencies unresolved
kind: memo
status: live
purpose: Record the exact recovered workbook and distinguish repaired availability from missing validation.
scope: PeerJ 21497 Data S1 only; no expression contrast, survival model or target ranking.
audience: [maintainers, external reviewers]
date: 2026-09-06
last_verified: 2026-09-06
---

The named workbook is publicly recoverable. It contains a substantial sample-column matrix,
not merely selected-gene summaries, but it is processed data rather than raw probe counts.
This repairs one access dependency. It does not by itself reopen the therapeutic-address atlas
or establish independent biological validation.

## Actual source and integrity

The existing 219,239-byte full JATS XML and original failed PeerJ landing response were copied
without alteration from the coordinator's discovery folder, alongside its retrieval receipt.
The failed publisher route was not repeated. The public Europe PMC supplementaryFiles endpoint
for PMC13374579 returned HTTP 200, application/zip, 4,457,390 bytes. The exact response is
`supplementaryFiles.response`; its SHA256 is
25076d95a63c07cb2b78f5feae702e389905ccdf5c7aeeb0eb46475c68c707fb.
Only the named workbook was extracted from the archive; other supplemental materials remain
uninspected archive members. The web tool could not render this binary endpoint; the recorded
ordinary HTTP request succeeded without credentials or challenge solving.

Data S1, `peerj-14-21497-s009.xlsx`, has 1,423,709 bytes and MD5
49b5b32fee3ceaaac7b10fd580a5484a, both matching the article's `supp-9/media` metadata.
The extracted bytes match the archive member exactly. All source URLs, dates, statuses,
headers, hashes and member names are retained in the two retrieval receipts and inventory.

## What the workbook actually provides

There is exactly one visible sheet, `EMC_Gene-expression_Log2CPM`, with occupied range
A1:M9501. A1 is `symbol`. B1:M1 are Si01, Si02, Si05, Si09, Si10, Si14, Si15, Si16,
Si17, Si19, Si20 and Si22, in that order. Each of the 9,500 feature rows has twelve finite
numeric values: 114,000 values, no missing cells. All are noninteger and 2,894 are negative.
These structural observations support the sheet's processed log2CPM label and rule out
interpreting the cells as nonnegative raw sequencing counts. No expression comparison was run.

There are 9,494 distinct string labels and six distinct numeric labels in column A:
A2029=37316, A2434=39873, A2604=38777, A4631=38412, A5072=36951, A6673=37681.
They are preserved as unresolved identifiers; no date or gene-name repair was inferred.
The 9,500 distinct row labels therefore must not be described as 9,500 verified gene symbols.
There are no probe IDs, genomic/transcript accessions, additional annotation columns,
hidden data sheets, comments, formulas, defined names or external workbook links.

The article states a final 12-patient, **9,909-gene** analysis, whereas this released matrix
has **9,500 feature rows**. The 409-row difference is unresolved; neither the workbook nor
this inspection identifies the omitted entities. This is not evidence that the missing
targets specifically account for the difference.

## Fixed panel representation

The frozen twelve-symbol panel comes from `atlas-sample-organ-2026-09-06/protocol.md`.
Matching used exact case-sensitive symbol equality; no alias remapping or new target selection.
For each present row, B:M contain all twelve processed source values. Their lexical strings,
sample headers and source cell addresses are preserved in `workbook-inventory.json`.

| Target | Symbol cell | Interpretation |
|---|---|---|
| CHRNA6 | A3508 | Processed row present |
| CD276 | A2216 | Processed row present |
| SSTR2 | A8058 | Processed row present |
| FAP | A6166 | Processed row present |
| CD248 | A6193 | Processed row present |
| CSPG4 | A7155 | Processed row present |
| MSLN | A3270 | Processed row present |
| PRAME | None | Not in released matrix; reason unknown |
| L1CAM | None | Not in released matrix; reason unknown |
| GPC3 | None | Not in released matrix; reason unknown |
| ALPP | None | Not in released matrix; reason unknown |
| CDH17 | None | Not in released matrix; reason unknown |

Presence supplies a reported processed measurement, not a detection threshold, calibrated
abundance, protein localization, target accessibility or efficacy. For absent symbols, the
workbook cannot distinguish unmeasured, filtered, annotation loss or omitted export. Do not
substitute zero or describe them as biologically absent.

## Dependency outcome

| Dependency | Outcome | Exact evidence and remaining limit |
|---|---|---|
| Public twelve-column processed matrix | Repaired | Data S1 A1:M9501, independently decoded; not raw counts |
| Fixed-panel source values | Repaired for seven symbols | Source rows above; five absent with unresolved reason |
| Complete final analysis matrix | Missing | Article says 9,909 genes; export has 9,500 rows, six nonstring labels |
| Raw 22-case 22,537-probe matrix | Missing in workbook | One processed sheet, twelve sample columns; SRA reprocessing was not commissioned |
| Probe-to-gene mapping and exact assay feature identities | Missing | Only a `symbol` column; no probe manifest or transcript identifiers |
| Reproducible filtering and normalization | Missing | Article describes discarding all-zero and duplicated-symbol genes, low-expression filtering, UQ normalization and edgeR CPM; workbook lacks starting counts, factors, exact filtering parameters and log transform/prior-count details |
| Known batch correction state of these values | Missing | Article results and Figure S1 caption describe correction; workbook does not identify pre/post-correction state, method, covariates or factors |
| Public external MI-ONCOSEQ matrix | Missing in workbook | No external data sheet or six-sample columns; article says investigators obtained matrices through journal editors, which does not make them part of Data S1 |
| Sample-column alignment | Repaired only within export | Each row uses the same twelve named headers |
| Sample-to-patient, aliquot and institution crosswalk | Missing in workbook | No clinical/sample metadata; institutional recruitment statements cannot assign individual Si labels |
| Independence from earlier EMC datasets | Conditional patient-count evidence in article; no crosswalk in workbook | Article reports twelve patients, not merely twelve libraries; exact overlap identities remain unresolved, as explained below |
| Same-assay normal and non-EMC comparator measurements | Missing in workbook | Twelve EMC-labelled columns only |
| Tissue composition, purity and block-age effects | Not addressed by this workbook | No column-aligned covariate sheet; bulk FFPE assay does not locate malignant-cell expression |
| Assay response calibration and analytical sensitivity | Not addressed | Processed values and positive-control reproducibility claims are not target-specific calibration |
| Protein/spatial localization or therapeutic selectivity | Not addressed | Transcript matrix supplies neither |

The primary clinical methods explicitly start from **22 patients**, exclude seven for quality,
one outlier and two without applicable prognosis, and describe the final cohort as **12 EMC
patients with complete molecular and clinical data** (`/article/body/sec[2]/sec[2]/p[1:2]`).
That is substantive source-reported patient-count evidence, stronger than counting headers.
However, it does not enumerate a Si-to-patient/aliquot mapping or explicitly state that each
workbook column is one different patient; the retrieved main Table 1 supplies aggregate clinical
counts. The workbook itself supplies no such mapping. No patient overlap with prior cohorts
can be assigned from these materials. This is a precise unresolved mapping, not affirmative
evidence that the cohort contains repeat patients.

If the twelve columns do represent twelve distinct patients and the earlier discovery cohort
contains at most six patients, no more than six can overlap and at least six must be new.
This conditional cardinality bound is valid, but does not identify the new patients and does
not repair the normal-comparator or cross-platform measurement dependencies. The workbook
inspection did not reverify the size of the earlier discovery cohort. An older bound for four
candidate records cannot simply be carried over to a source reporting twelve patients.

Primary text locators and exact source text are retained in `article-source-locators.json`.
The article's within-dataset z-score comparisons and nonsignificant tests of three selected
genes are source claims, not evidence that distinct assay scales become interchangeable.
No such transformation, pooling or cross-platform claim was reproduced here.

## Verification and stop

`inspect_workbook.py` reads with bundled openpyxl and separately decodes the original XLSX
ZIP/XML/shared strings. It compared every one of the **123,513 nonempty cells** between
decoders, including numeric-label and negative-value cases, without converting absent targets
to zero. The original archive/member and JATS MD5/size checks also passed. The script produces
the complete feature-cell inventory and deterministic structural/panel inventory. The saved
verifier re-executes extraction and checks output equality and source/dependency hashes.
There was no authoring or resaving of the source workbook, no inferential analysis and no
rendered scientific figure.

The bounded source inspection is complete. The coordinator must review the source package
and decide whether a separately specified experiment can make a useful contribution with
these repaired and unresolved dependencies. A new paper, expression analysis or prognosis
model has not been authorized by this result.
