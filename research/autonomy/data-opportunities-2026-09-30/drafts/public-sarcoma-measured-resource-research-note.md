# An auditable resource for public sarcoma imaging and RNA reanalysis

## Abstract

Published sarcoma experiments can support secondary research without new laboratory access, provided that source identities, sampling units and assay differences remain explicit. We assembled measured derivatives from five public imaging or expression sources, including all 42 released GSE174376 RNA libraries, 93 publisher worksheets and 450 fixed imaging tiles. Corrected spatial and pediatric-composition comparisons were null. Numerous human-tumor/PDX RNA differences were measurable, but source and assay were inseparable. Same-assay RMS programme, subtype and lineage-composition analyses yielded no corrected association. A published 12-specimen EMC export supported internal expression diagnostics and literal clinical-label sensitivity analyses, rather than independent prognostic validation. The resource provides reproducible measurements, full testing families and qualified source joins.

## Introduction

Public sarcoma studies contain measurements that can be reused when new specimens or laboratory experiments are impractical. Their scientific value depends on more than obtaining a file: repeated acquisitions may represent one clinical case, expression differences may reflect different assays, and annotations may identify a model or clone rather than an individual patient. We reanalysed five published sources while retaining these distinctions.[1–5] Our contribution is an auditable measurement and analysis resource. It does not propose a shared mechanism across heterogeneous sarcomas or validate a therapeutic target.

## Methods

### Sources, identities and analysis records

We retained literal source identifiers, source hashes, executable parsers and full measured outputs. Computational request failures were repaired where possible and kept separate from low signal or undefined measurements. Successful earlier measurements were preserved during repairs. Analysis families and sensitivity settings were recorded before their respective new fits within this exploratory campaign; the campaign was not a prospective clinical study.

Clinical patients were the analysis unit only when source metadata verified that unit. Elsewhere, repeated libraries, tiles or specimens were aggregated to source cases or literal identifier roots without declaring those roots independent clinical patients. We retained unresolved aliases rather than changing leading zeros, specimen suffixes or accession identities to increase sample size.

### Imaging and pediatric summaries

The UPS/MFS imaging mass-cytometry source contained 200 metadata records and 199 unique acquisitions. Acquisitions were aggregated to 24 source-verified clinical patients, comprising 14 untreated UPS and 10 high-grade MFS cases. Fifteen fixed marker-pair/radius comparisons used density-conditioned marker permutations and patient-level inference.

For Ewing imaging, one frozen nuclear segmentation was used for nine fixed tiles in each of 26 source cases. Marker measurements were repeated in nuclear masks and 2.5- and 5-µm expansions from the same centroids. Tile geometry included areas without predicted nuclei. Primary 5-µm comparisons adjusted for published CD68 and HLA-II abundance and geometric object density. Fifteen primary tests and all 135 fixed pair/radius/window/adjustment combinations were retained, with 10,000 case permutations, 2,000 reranked bootstrap attempts and leave-one-case-out analyses. These measurements did not reconstruct the authors’ cell-phenotype classifier.

Processed pediatric atlas summaries covered 89 specimens and 95 quality-control libraries. Specimens were aggregated into 62 literal identifier-prefix groups. Thirty-three quality/composition comparisons used broad tumor-class adjustment, within-class permutations and group-level bootstrap reranking. Raw differential expression was not refitted from controlled-access EGA raw data.

### RMS count and annotation analyses

Every released GSE174376 library was read, retaining exact archive-member receipts and 88 planned literal target strings. We calculated transcript-detection fractions and target fractions of summed human UMI under three barcode selections: all source barcodes, at least 500 human UMI, and at least 500 all-reference UMI. Library summaries were averaged equally within literal model roots. Barcode thresholds are sensitivity filters, not complete source quality-control definitions.

Human-nuclear/PDX-whole-cell differences used 14 matched literal roots, exact paired sign flips and a fixed 176-test family per barcode selection. A separate same-assay human-nuclear analysis related CSPG4 RNA to 13 historical programme panels across 14 roots. CSPG4 was removed from its own core-protein programme. Scores used exact per-gene midrank sums followed by reranking. All 78 endpoint/panel/barcode combinations were retained.

Public publisher assets supplied all 15 XLSX files and all 93 worksheets. Exact source-root subtype annotation supported 16 human-nuclear libraries in 13 roots: eight ERMS and five ARMS. Three specimen identifiers differed from source-table specimen IDs but shared an exact, consistently annotated literal root; only root-level subtype was transferred. Two SJRHB000026 human libraries were excluded because the source table used SJRHB00026. No specimen-specific age, site or treatment was assigned across these discrepancies.

Source Supplement 5 contained experimental 18-nucleotide lineage-clone barcodes, not the 16-nucleotide RNA cell barcodes. Fourteen of 15 literal sheet names matched baseline PDX library titles, representing 10 roots. We related RNA scores to mesoderm, myoblast and myocyte fractions calculated both from clone-assigned cell counts and by equally weighting positive clones. We did not infer per-cell state labels for the released count matrices. The extension comprised 84 subtype tests and 504 lineage-composition tests, using exact subtype-label permutations, 10,000 lineage root permutations, 2,000 reranked bootstrap attempts and root deletion analyses. Fixed families of 28 or 84 tests and a global 588-test correction were retained.

All 88 planned strings were also qualified against the complete pooled-state source table. Author-provided pooled-state summaries and adjusted p values were retained as published measurements, without treating pooled cells as new independent patient observations.

### Published EMC export and linked metadata

The PeerJ export comprised 9,500 literal gene-label rows and 12 specimen columns. We examined source-selected PXN, TYMS and H1FX pairs under the published values, within-specimen ranks and two low-value censoring sensitivities. Separate partial-rank diagnostics controlled specified export-level summaries.

Exact PRJNA1357027 BioSample metadata supplied 12 unique literal specimen joins and Prognosis B/G labels. The label legend and survival/event semantics were not independently established, so B/G remained literal source labels. The field Time equalled 2020 minus collection year for all 12 specimens and was not interpreted as survival duration. One source record had sample alias Si22 but ENA library name Si21; the conflict was retained. We examined all 24 gene/value-variant/identity-scope label comparisons, including exclusion of that record. Eleven unambiguous ENA records also supported a separate three-pair read-count-adjusted internal diagnostic.

Residual-rank associations and their nominal P values are descriptive; the P values do not incorporate nuisance-fitting uncertainty. Their BH values correct those nominal P values within the stated families.

## Results

| Source | Completed measured coverage | Analysis unit | Corrected result or qualification |
|---|---|---|---|
| UPS/MFS IMC | 200 metadata records; 199 acquisitions | 24 clinical patients | No corrected result in 15 tests; minimum q=0.300 |
| Ewing imaging | 26 cases; 234 fixed Cellpose tiles | Source case | Minimum primary q=0.180; minimum global-135 q=0.219 |
| Pediatric atlas | 89 specimens; 95 QC libraries | 62 literal prefix groups | No corrected result in 33 tests; minimum q=0.115 |
| RMS released counts | 42 libraries; 288,740 source barcodes | Library, then literal model root | Numerous human-sn/PDX-sc differences; source/assay confounded |
| RMS source-qualified extensions | 93 worksheets; 13 subtype roots; 10 lineage roots | Literal root | No corrected same-assay, subtype or lineage result |
| PeerJ EMC export | 9,500 rows × 12 specimens | Literal specimen ID | Internal correlations; no global-24 corrected clinical-label result |

### Imaging and pediatric composition

The complete threshold-imaging ledger covered 50 files: 24 Panel 2 and 26 Panel 3 files, totalling 450 fixed tiles. All 33 initial file-access failures were repaired while preserving the 17 earlier successful files. At each threshold factor, 0.8, 1.0 and 1.2, 318 tiles yielded finite analyses, giving 954 finite factor–tile analyses. The remaining 132 tiles lacked finite DNA thresholds.

The Ewing nuclear segmentation produced predictions on 201 of 234 tiles; 33 were DNA-percentile-degenerate. These 33 tiles are distinct from the threshold-ledger count of 132. The clinical workbook listed 28 source cases, the frozen images represented 26, and published abundance covariates were available for 25 imaged cases, with EWS105 absent. Primary comparisons used 25 or 24 cases depending on constant NKX2.2-related measurements. None of the 15 primary or 135 combined comparisons passed correction. All bootstrap attempts were finite. The HLA-DR channel alias denotes the source’s broad HLA-II reagent; PSMA3 is proteasome alpha 3, not FOLH1.

UPS/MFS and pediatric comparisons likewise yielded no corrected association. Four unadjusted endothelial-related pediatric intervals excluded zero, illustrating why individual intervals should not replace the full testing family.

### RMS measured RNA and source-qualified extensions

The 42 libraries comprised 20 human tumor libraries, 18 baseline PDX whole-cell libraries, three treated PDX nuclear libraries from one literal model, and one organoid library. Human libraries included 18 nuclear and two whole-cell assays. All libraries produced the complete 11,088 target-string/barcode summaries. H1FX was measured; H1-10 was unmapped. Historical aliases were retained as literal strings, rather than treated as independent genes or absent biology.

Of 176 primary human-nuclear/PDX-whole-cell tests, 174 were finite and 132 had q<0.05. Those differences did not identify source biology separately from assay. The same-assay CSPG4/programme analysis yielded no corrected result across its 78 tests; minimum q was 0.135.

All 588 source-qualified subtype and lineage-composition tests were finite and none passed either its fixed family correction or global correction. Primary minimum q values were 0.174 for subtype, 0.218 for cell-weighted lineage composition and 0.319 for equal-clone composition. Global minimum q was 0.362. Of 1,176,000 bootstrap attempts, 1,175,826 were finite and 174 constant draws were discarded; every test retained at least 1,994 finite draws.

The strongest primary CSPG4 detection/lineage contrast was an inverse association with the myocyte fraction across 10 PDX roots: rho=−0.867, permutation p=0.00260, fixed-family q=0.218. Its unadjusted reranked interval excluded zero, but it did not survive correction. The 14 matched source sheets contained 347 positive lineage clones and 46,762 clone-assigned cells. The unmatched SJRHB13757_X1 sheet, containing 74 positive clones and 3,351 assigned cells, remained in the source audit without being joined to SJRHB013757_X1. Source pooled-state summaries mapped 87 of 88 strings; H1-10 was the sole unmapped string. These summaries do not independently establish a CSPG4 cell-state mechanism. The author's pooled CSPG4 state contrasts are existing source findings, not discoveries or results refuted by these root-level tests.

### EMC internal diagnostics and clinical-label sensitivity

Internal PXN–TYMS and PXN–H1FX partial-rank correlations remained corrected in specified export-control analyses; TYMS–H1FX did not. A PXN–TYMS comparison controlling both export summaries had rho=0.801 but an unadjusted reranked bootstrap interval spanning −0.031 to 0.982. Read-count adjustment in the 11 unambiguous ENA records retained all three source-selected pair correlations after their separate three-test correction; the TYMS–H1FX bootstrap interval included zero.

Literal B/G labels split the 12 specimens equally. No clinical-label comparison survived the complete 24-test correction; minimum q was 0.0623. Some published-value comparisons passed the narrower all-12 family correction, while the record-exclusion family and within-specimen-rank sensitivity did not provide equivalent corrected support. These are internal, source-selected diagnostics without qualified survival endpoints or an independent cohort.

Six exported gene-label cells contained numeric values compatible with Excel date serials, but their source number format was text. This observation does not establish a symbol-conversion history and was not used to invent gene identities.

## Discussion

The resource extends published data reuse through complete measured coverage, exact annotation recovery and explicit units of inference. It includes null corrected comparisons and positive internal diagnostics with their full sensitivity families. Access errors, parser failures, low signal and unresolved identities remained distinct, allowing usable measurements to be completed rather than prematurely declared unavailable.

The completed analyses constrain biological interpretation. Spatial null results do not prove absence of organization. Human/PDX RNA differences cannot separate model biology from nuclear/whole-cell assay. Same-assay and source-qualified RMS extensions did not supply corrected evidence for a CSPG4 programme or lineage association. Experimental lineage fractions capture part of a library and are compositional; the published myogenesis and EGFR findings remain prior work.[4] RNA summaries do not measure proteoglycan abundance, glycan structure or targetability.

The EMC export provides a reproducible internal diagnostic, supplemented by genuine literal clinical metadata recovered from its declared accession. Ambiguous time/event definitions and a discordant source identity limit outcome interpretation. Reusing a paper’s selected genes in its own 12 specimens does not provide external prognostic validation.

The material is most suitable as a modest resource Research Note or a methods/data appendix to a focused biological study. Established segmentation, rank tests and permutations are not new methods. Multiple heterogeneous null or confounded analyses should not be divided into independent discovery manuscripts merely because each produces a table.

## Data and code availability

Executable source parsers, analysis code, source receipts and durable derivatives are recorded in this branch's [deep-analysis directory](../deep-analysis/). Complete durable results include the [50-file/450-tile ledger](../deep-analysis/results/spatial-all50-files450-tiles-complete-ledger-final.json), [same-source pixel measurements](../deep-analysis/results/spatial-all50-measured-source-final.json), [Ewing source/density analysis](../deep-analysis/results/Ewing-all26-source-case-density-and-geometry-final.json), [IMC density-conditioned tests](../deep-analysis/results/IMC-fixed-density-conditioned-null-final.json), [pediatric reranked bootstrap](../deep-analysis/results/pediatric-composition-reranked-bootstrap-final.json), [all 42 RMS measured outputs](../deep-analysis/results/RMS-all42-complete-measured-target-values.json), [paired aggregate comparisons](../deep-analysis/results/RMS-all42-frozen-target-aggregate-final.json), [same-assay programmes](../deep-analysis/results/RMS-all13-same-assay-programme-comparisons-final.json), [93 publisher-sheet receipts](../deep-analysis/results/RMS-complete15-publisher-workbooks93-sheets-final.json), [all 588 subtype/lineage comparisons](../deep-analysis/results/RMS-all588-source-qualified-subtype-lineage-final.json) and [all 24 EMC clinical-label diagnostics](../deep-analysis/results/PeerJ-all24-source-qualified-clinical-label-diagnostics-final.json).

The final source-qualified RMS analysis completed in [run 36936001053, job 110616354154](https://github.com/trimcrae/Rare-cancers/actions/runs/36936001053/job/110616354154). Primary sources, identities and hashes are retained for reproducible acquisition. GitHub Actions binary/worksheet artifacts have thirty-day retention; durable JSON derivatives and scripts are preserved in the branch. Source-ID exclusions and undefined endpoint semantics remain explicit.

## References

1. UPS/MFS imaging mass-cytometry primary study. [doi:10.1007/s00262-025-04123-y](https://doi.org/10.1007/s00262-025-04123-y). Raw imaging: S-BIAD1555.
2. Proteomic landscape of Ewing sarcoma primary tumors and metastases. [PMC13111610](https://pmc.ncbi.nlm.nih.gov/articles/PMC13111610/). Raw imaging: S-BIAD1597.
3. A single-cell atlas of cancer-educated ecotypes across high-risk pediatric sarcomas. [doi:10.21203/rs.3.rs-10374394/v1](https://doi.org/10.21203/rs.3.rs-10374394/v1).
4. The myogenesis program drives clonal selection and drug resistance in rhabdomyosarcoma. [doi:10.1016/j.devcel.2022.04.003](https://doi.org/10.1016/j.devcel.2022.04.003). RNA deposit: GSE174376.
5. PeerJ EMC primary study and supplementary expression export. [doi:10.7717/peerj.21497](https://doi.org/10.7717/peerj.21497). Declared sequencing project: PRJNA1357027.
