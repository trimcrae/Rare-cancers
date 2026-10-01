# Source-qualified reuse of the published EMC expression export

## Abstract

A published twelve-specimen EMC expression export can support reproducible internal diagnostics when its source identities and clinical semantics remain explicit. We recovered public BioSample metadata, qualified an accession conflict, and evaluated all 24 fixed gene/value/identity-scope clinical-label comparisons. None passed the full-family correction. Partial-rank associations among the three source-selected genes remained internal, with uncertainty sensitive to covariate and identity choices. These analyses qualify data reuse rather than independently validate a prognostic biomarker.

## Sources and methods

The verified PeerJ source [1] supplied a 1,423,709-byte expression workbook, SHA256 20165fd3ff09ec2d5a24b3c20b78515f42a3309119f248ed055c7484deb45e75. Its single visible sheet contained 9,500 gene-label rows and twelve Si specimen columns. All gene rows varied across specimens. Examination of every workbook archive member found no hidden sheet, external-link clinical dataset or time/event table within this export.

The exact public project PRJNA1357027 supplied twelve RNA-Seq, single-end BioSamples, each with a unique sample-name identifier matching an expression column. Public attributes included age, size, cellularity, fusion testing, metastasis and Prognosis G/B labels, with six specimens per label. The primary description refers to favorable/poor clinical courses with an eight-year distinction, but we did not independently verify the literal G/B code legend. Tests therefore retain those codes. Time values of 0–23 equalled 2020 minus collection year in all twelve records; they were not qualified survival durations and had no verified censor flag. No Cox or log-rank model was fit.

Si22's ENA alias and BioSample name indicated Si22, while its ENA library name indicated Si21. We preserved the conflict rather than harmonizing the label. Eleven unambiguous ENA records supplied RNA read counts; a source-reported spot count for the conflicting record was not mixed into that read-count covariate.

PXN, TYMS and H1FX were source-selected genes. Four expression settings—log2-CPM, within-specimen ranks among all 9,500 rows, censoring a repeated low value, and censoring the bottom quartile—were evaluated against literal Prognosis labels, both using all specimens and excluding Si22. The resulting 24 fixed comparisons used exact label permutations, stratified reranked bootstrap intervals and leave-one-specimen-out analyses. Correction retained the 24-test family and the two twelve-test identity-scope families. Separate three-gene correlation diagnostics considered specified export-level covariates and the eleven-source RNA count covariate; they were not prognostic validation tests.

Residual-rank associations and their nominal P values are descriptive; the P values do not incorporate nuisance-fitting uncertainty. Their BH values correct those nominal P values within the stated families.

## Results

None of the 24 clinical-label comparisons passed Benjamini–Hochberg correction across the complete family; minimum q was 0.06234. In the all-twelve smaller family, raw-expression contrasts had q=0.04453 for PXN/TYMS and 0.04906 for H1FX. After excluding the accession-conflicting specimen, none passed that scope's twelve-test correction; minimum q was 0.06926. Available exact assignments varied with retained observations, including 924, 462 and 210 label allocations. The H1FX bottom-quartile diagnostic used ten usable specimens. Smaller-family results do not overturn the complete-family result or establish out-of-sample prediction.

In the eleven-specimen RNA-count-adjusted internal diagnostics, partial correlations for PXN–TYMS, PXN–H1FX and TYMS–H1FX were approximately 0.816, 0.750 and 0.685, with corrected q=0.01590, 0.02235 and 0.03200. The TYMS–H1FX bootstrap interval included zero. Of 2,000 bootstrap attempts per pair, 1,993, 1,998 and 1,993 were finite; the remaining constant resamples were explicitly discarded. All pairwise expression settings and fixed export-covariate sensitivities remain in the results. In the broader twelve-test partial-rank family, TYMS–H1FX did not pass correction, and one jointly adjusted PXN–TYMS interval also included zero. Selection of the three genes in the source study limits inferential reuse of their associations.

Six numeric gene-label cells were compatible with Excel serial dates, but their source number format was text ('@') and data type numeric. That observation does not prove an earlier date-conversion event or identify a MARCH gene for renaming. H1FX was measured; H1-10 remained an unresolved alias and was not treated as another independent measured gene.

## Interpretation and reproducibility

Metadata recovery repairs the earlier export-only conclusion that no public clinical labels were available. It does not make collection year a survival endpoint, remove the library-name conflict or create an independent cohort. The strongest contribution is a documented reusable source with complete diagnostic sensitivities. A standalone prognostic or mechanistic paper is not supported by these internal comparisons.

The [full-matrix partial-rank audit](../deep-analysis/results/PeerJ-all9500-genes-and-fixed-partial-rank-diagnostics-final.json), [exact public project metadata](../deep-analysis/results/exact-RMS-publisher-and-PeerJ-public-project-metadata-actual.json), [all 24 label comparisons](../deep-analysis/results/PeerJ-all24-source-qualified-clinical-label-diagnostics-final.json) and [source export audit](../deep-analysis/results/PeerJ-exact-public-export-source-metadata-final.json) preserve literal joins, accessions, effects, full families, bootstrap counts and source hashes. The final label analysis completed in [run 36932382794, job 110604670838](https://github.com/trimcrae/Rare-cancers/actions/runs/36932382794/job/110604670838).

1. PeerJ primary study. [doi:10.7717/peerj.21497](https://doi.org/10.7717/peerj.21497). Public project: [PRJNA1357027](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA1357027).
