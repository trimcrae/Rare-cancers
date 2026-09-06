---
id: DOC-ATLAS-TISSUE-RNA-SUPPLEMENT-20260906
title: Tissue RNA prioritization methods and data supplement
level: cross-cutting
kind: memo
status: live
canonical_for: []
purpose: Make source membership, estimands, uncertainty and figure provenance reviewable.
scope: Frozen empirical packet, manuscript tables and plotting inputs.
audience: [external reviewers, collaborators]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-TISSUE-RNA-MANUSCRIPT-20260906]
---

# Methods and data supplement

## Source inventory and specimen scope

| Source | Units and usable specimens | Assay / release | Role |
|---|---|---|---|
| Hofvander2026 |704 source patients;9 primary EMC after fixed exclusions |19,116 gene symbols, gene TPM; author release v1.0.1 | New-to-this-analysis tissue cohort |
| GSE24369 |42 original arrays:6 EMC,17 LGFMS,6 MFS,6 desmoid,5 SFT,2 muscle pools | GPL6244 transcript-cluster RMA log2 signal | Retrospective same-histology anchor; also CHRNA6 discovery data |
| GSE28866 | Four EMC library/STT records; individual patient count unverified | Selected3SEQ peaks, supplied compressed normalized scale | Historical, different-estimand sample/organ context only |
| HPA |12 gene XML/JSON pairs; tissue/cell records are not independent subjects | XML version25; current methods/download25.1, Ensembl109 | Descriptive normal RNA, IHC and ICC/IF context |
| Cammareri2023 | Five EMC rows in original supplementary workbook | Whole-section PRAME QR005 IHC; both reader columns negative | External negative protein evidence, not paired with present RNA |

Nine retained Hofvander EMC IDs:11881-19,3371-22,3372-22,4716-22,4840-13,5149-18,5241-06,7931-19,8102-22. Excluded previously reported cases104-92,168-97 and536-00 map to source MDB9736 cases3,4 and7;5081-14 is a local recurrence. Original TableS1 diagnosis and nonblank specimen exception are preserved for every704-source sample. No patient date is inferred from an accession suffix. Blank publication references do not prove independence. Gene-fusion positive in this source can mean current RNA-sequencing or an earlier assay, not necessarily a known partner in every case.

Original-diagnosis primary comparators contain14 MLPS,13 LGFMS,18 synovial sarcomas; separate contexts contain60 MFS and10 DFSP. Shared-histology secondary contexts add11 primary SFT and11 desmoids. Source metadata sometimes uses revised or transcriptomic labels; original labels are primary and the separately reported revision sensitivity changes all relevant rows symmetrically. Purity and grade are unavailable for EMC adjustment.

Sequencing years for the nine EMC are2019(n=2),2020(n=1),2021(n=1),2022(n=2),2023(n=3). MLPS has2 comparators in2019 and5 in2021; LGFMS has7 and5; synovial sarcoma has10 in2019 and8 in2020. Consequently, each primary matched contrast contains3 EMC and the union is4 EMC. Context DFSP has only1 matched EMC and3 comparators in2021. Unsupported year cells remain null. All counts refer to the exact specimen policy, not the full published histology totals.

## Exact measurement contract

TPM source SHA256: `b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3`. Original GSE24369 family gzip SHA256: `98c83c8ca23b7052cf0d4d0099a7bf1af6c3c972276038c3a633e2a5349b3c37`. Full source digests and byte sizes are in the two frozen metadata manifests. Analysis uses released numeric precision, not the earlier rounded cache.

| Gene | GPL6244 probe | Role |
|---|---|---|
| CD276 |7984743|Address|
| SSTR2 |8009526|Address|
| PRAME |8074856|Address|
| FAP |8056257|Address|
| CD248 |7949588|Address|
| CSPG4 |7990545|Address|
| MSLN |7992071|Address|
| L1CAM |8175871|Address|
| GPC3 |8175234|Address|
| ALPP |8049123|Address|
| CDH17 |8151795|Address|
| CHRNA6 |8150550|Separate context control|

All transcript-cluster assignments for each selected probe resolve to the same gene. No probe mean, best probe, alias substitution or expression-dependent feature filter is used. Array finite signed log signals are valid; TPM must be finite and nonnegative. Zero observations remain ties. Missing/duplicate observations cause a recorded technical failure rather than deletion or imputation. Actual runs completed without these failures.

For EMC values x_i and comparator values y_j, A=(1/nm) Σ_iΣ_j[I(x_i>y_j)+0.5I(x_i=y_j)]. Pair counts are not independent-patient counts. The marginal summary is the mean of the3 histology effects. Matched effects first average within exact year, weighting by supported EMC counts, then average equally across histologies. A common EMC specimen can contribute to multiple histology contrasts; bootstrap sampling preserves that dependence by sharing its resample. No cross-platform scale or patient pooling is performed.

Bootstrap seed20260906,2000 replicates, stratified by histology/year. The conditional95% percentile intervals are pointwise, not familywise and not used to select genes. For CSPG4, a degenerate MLPS matched interval[0.66667,0.66667] reflects observed sparse strata and the resampling design, not absence of biological uncertainty. All singleton flags and patient placements are supplied. Independent5000-draw resampling reproduced the main matched interval endpoints; this numerical check does not remove small-sample limitations.

The allocation rule requires marginal composite≥0.70, each primary marginal/matched histology>0.5, and both summaries>0.5 after each single EMC and histology deletion. Year/comparator deletion and revised diagnoses are qualifiers. Deletions renormalize retained supported-year weights; a lost contrast remains undefined. Complete-case selection or imputation is not performed. No new replication success cutoff was added. The separate cross-cohort output compares signs and magnitudes against LGFMS primarily, MFS/SFT/desmoid secondarily.

## Tables and evidence files

TableS1, `../all12-gene-effects.csv`, includes every gene, both primary composites, conditional intervals and same-LGFMS effects. TableS2, `../all-hofvander-contrasts.csv`, contains60 gene×histology rows; `../all-year-cells.csv` provides all supported/unsupported cells. TableS3, `../all-shared-histology-replication.csv`, contains48 gene×shared-histology comparisons and individual-deletion ranges. `../all-primary-deletions.csv` retains every summary deletion. Full JSON adds every specimen value, placement, individual contrast and revised-label mapping.

TableS4, `normal-context.csv`, contains12 source-linked HPA records with normal IHC reliability/missingness and assay-location context. It is a descriptive extract, not a normal-sparing assessment. Source data include1092 RNA tissue/block records and1054 categorical normal-IHC cell records; neither total is a count of newly measured independent donors. HPA consensus RNA summarizes maxima across HPA/GTEx sources/subtissues. GPC3/CHRNA6 lack tissue-IHC rows in this recovery; absence of a row is not a negative stain. SSTR2/FAP uncertain IHC and ALPP multi-gene antibody warning remain explicit. PRAME's localization tags are not evidence of endogenous EMC peptide-HLA presentation.

PRAME supplementary workbook SHA256 `20b4bd1243be22e4eee2da7470da986091f91cc4959fa416708748ba99187ca7`, Sheet1 rows128–132. Five EMC were negative in both reader columns; blank percentage fields were not converted to measurements. Case2 has EWSR1::NR4A3 RNA-sequencing support, cases3–5 NR4A3-positive FISH, case1 no recorded ancillary method. This supports a negative result in those5 specimens, not universal PRAME absence or absent peptide-HLA presentation.

## Reproduction and figure status

Empirical programs are `../analyze.py` and `../replication.py`; all8 pre-outcome approved files are listed in `../coordinator-authorization.json`. Original scientific protocol bytes are preserved alongside frontmatter-corrected versions. Each analysis ran once: command elapsed46.38 and12.72 seconds, exit0. Runtime was Python3.12.14, NumPy2.3.5, openpyxl3.1.5; exact executable/version receipt is in `runtime.json`. Independent original-source arithmetic reproduced8,448 TPM values,504 array values,2,436 estimate/deletion blocks and266,772 scalar comparisons without discrepancy. These checks verify computation, not causal or clinical validity.

Source locations in the frozen manifests are original workstation paths. Source and reporting context must be packaged or mapped to byte-identical files for external reproduction; a portable execution adapter is being assessed separately. This draft does not claim that an unconfigured checkout is self-contained. The published-data URLs and exact digests make the intended inputs unambiguous.

`plot_figures.py` reads completed CSV effects and recorded TPM values, verifies pinned input hashes, and refuses rendering until its exact bytes, figure-inputs.json and every input match committed HEAD. Default execution checks readiness only. `--render` will create two vector PDFs and300-dpi PNGs plus figure provenance after coordinator integration. **No figure has yet been generated or visually inspected.** Rendering and visual inspection are required before figures can be called final; no placeholder image is represented as a result. Normal context remains a table rather than a redundant figure.

No authorship, funding, conflicts, ethics determination or publication readiness is inferred. The original empirical packet is unchanged by drafting; all new manuscript, table and plotting files reside under draft/.
