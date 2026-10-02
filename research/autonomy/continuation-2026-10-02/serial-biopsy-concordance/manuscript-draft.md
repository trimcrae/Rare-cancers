---
id: "DOC-CONTINUATION-20261002-SERIAL-BIOPSY-DRAFT"
title: "Patient-linked assay availability and paired CD8 changes in a sarcoma trial"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Patient-linked assay availability and paired CD8 changes in a sarcoma trial."
scope: "October 2 working extension of the preserved September 30 draft; measured-data availability and descriptive paired CD8 changes, without submission clearance."
audience: ["maintainers","external reviewers"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Patient-linked assay availability and paired CD8 changes in a sarcoma trial

Serial-biopsy studies can report similar aggregate assay counts while supporting different patient-level comparisons. The public clinical, molecular and supplementary data from the sarcoma immunotherapy study NCT03282344 permit an additional analysis: which patients contribute published measurements to each assay at each timepoint, what clinical outcomes describe those subsets, and do CD8 RNA and IHC changes agree in the shared paired patients?[1] We linked these sources and recovered numerical CD8 and PD-1 immunohistochemistry (IHC) values. The analysis concerns the composition of measured subsets, rather than treatment efficacy or biomarker validation. The linked exports provide no separately verified EMC-specific subset and concern NCT03282344, distinct from IMMUNOSARC1.

We used PatientSourceData.txt and SampleSourceData.txt from mskcc/ImmunoSarc, pinned to revision b71c3373bc182f9c647a6f7bc1fbd641d24db917. The respective Git blob identifiers were 8e65abf4208c2e6d9b96d8271752bfde4c85f443 and c3d9ee850299eb8930788468c87754b58d5a67f8. We joined records by Subject and checked PatientID, cohort, best response, progression-free survival (PFS) and censoring concordance. All 133 sample rows linked to the 77 clinical records without duplicate patient–timepoint records. The sample table represented 69 patients; eight clinical records had missing PatientID values. These source denominators differ from the 84 patients enrolled in the original study.[1]

Availability required a finite published value, with zero retained as measured. RNA immune-score availability required all nine reported immune/stromal scores; a finite T-cell(CD8) score identified exactly the same rows across all 133 records. A pair required qualifying baseline and on-treatment values for the same patient. We retained source histological cohorts and response categories.

The public sample table contains IHC quartiles rather than the complete numerical CD8 and PD-1 measurements. We therefore followed the numerical source used by the published figure code into Supplementary Table S1 and the source-data workbook. Joining their CD8 and PD-1 sheets by published PatientID and timepoint recovered 165 finite numerical cells across 133 sample rows and two markers; 101 cells remained unmeasured. There were no unmatched rows or conflicting numerical values between the published sources. Five numerical measurements had no corresponding quartile, all at progression: two CD8 and three PD-1 values. A missing quartile therefore did not always mean the absence of a published measurement.

For clinical composition, we calculated Kaplan–Meier PFS and restricted mean survival time (RMST) through 168 days descriptively. Event coding, PFSCensor==1, was verified directly in pinned Figure2.R. Source values within 1e−9 days of an integer day were canonicalized to preserve printed day ties. We performed no treatment comparison, biomarker hypothesis test or adjusted survival-model fit.

Assay-specific pairs were fewer than paired sample records (Table 1). Every on-treatment sample record had a baseline counterpart, but only 31 patients had paired RNA immune scores, 23 had numerical CD8 pairs and 28 had numerical PD-1 pairs. The identities of these subsets differed; they are not interchangeable denominators for a common paired analysis.

**Table 1. Unique patients with published records or measurements.**

| Record or measurement | Baseline | On-treatment | Paired | Progression |
|---|---:|---:|---:|---:|
| Any sample record | 69 | 61 | 61 | 3 |
| All nine RNA immune/stromal scores | 41 | 38 | 31 | 2 |
| Numerical CD8 IHC | 47 | 32 | 23 | 2 |
| Numerical PD-1 IHC | 48 | 33 | 28 | 3 |

“Paired” requires the indicated measurement at both baseline and on-treatment timepoints. Columns are separate populations and should not be summed.

The UPS/MFH/high-grade MFS cohort illustrates an assay-specific gap concealed by aggregate biopsy counts. It contained ten clinical records and seven on-treatment sample rows. Four patients had on-treatment RNA immune scores, including three with paired scores. Six had baseline numerical CD8 values, but none had an on-treatment CD8 value or a CD8 pair. Numerical PD-1 values were available for seven patients at baseline and one on treatment, yielding one pair. Eight clinical records carried an IHC availability flag. Neither the absence of CD8 measurements nor a general availability flag identifies whether a particular assay was performed successfully or reported completely.

The 77 clinical records included nine partial responses, 22 stable-disease responses and 46 progressive-disease responses, with 67 PFS events. Overall median PFS was 62 days and RMST through 168 days was 91.19 days. Assay-specific paired subsets had different response and PFS compositions (Table 2). Paired RNA availability yielded similar descriptive RMST to its complement; paired CD8 and PD-1 availability did not. These are observed subset descriptions. Future paired availability cannot be treated as a baseline exposure, and the contrasts do not identify causal effects, informative missingness or a biological mechanism.

**Table 2. Clinical composition by paired measurement availability.**

| Measurement | Paired patients | PR / SD / PD | Median PFS, days | RMST to 168 days | Patients without a pair | Median PFS, days | RMST to 168 days |
|---|---:|---|---:|---:|---:|---:|---:|
| RNA immune scores | 31 | 4 / 8 / 19 | 62 | 90.17 | 46 | 62 | 91.84 |
| Numerical CD8 IHC | 23 | 2 / 3 / 18 | 56 | 72.36 | 54 | 63 | 98.99 |
| Numerical PD-1 IHC | 28 | 2 / 6 / 20 | 59 | 78.02 | 49 | 63 | 98.13 |

PR, partial response; SD, stable disease; PD, progressive disease. Each complement includes all clinical records without that qualifying pair, including patients with one available timepoint. No inferential comparison is implied.

Within the measured pairs, the median on-treatment minus baseline CD8 change was −0.02 percentage points, ranging from −4.74 to 28.17; 11 patients increased and 12 decreased. The PD-1 median change was −0.03 percentage points, ranging from −1.42 to 11.27; 12 increased, 15 decreased and one was unchanged. These descriptive measurements characterize their respective selected subsets and do not establish treatment-induced immune changes.

The primary paper reports a pooled cross-sectional CD8 RNA–IHC Spearman correlation of 0.74.[1] That comparison does not establish agreement in within-patient change. Exact patient and timepoint joins identified only 13 patients with both assays at baseline and on treatment. Using published MCP-counter scores in their reported units and numerical IHC in percentage points, six had changes in the same direction (four decreasing, two increasing) and seven had opposing directions; none had an exactly zero change. The Spearman correlation of the two continuous changes was 0.0604. These complete cases spanned eight histology categories, with no UPS/MFH/high-grade MFS case. This sparse, selected comparison does not contradict the pooled association, establish longitudinal interchangeability or identify a cause of disagreement. Published numeric values are normalized decimal inputs; an independent calculation using captured original IHC value literals preserved every direction and rank despite trailing-digit differences in three cells. Patient/timepoint equality does not establish identical aliquots or spatially equivalent biopsies.

The scheduled week-3 biopsy creates a further timing question. Published Figure3.R selects timepoint-specific sample rows and uses treatment-origin PFS without delayed entry. Two clinical records had events before nominal day 21, at days 17 and 19; neither had an on-treatment row. All 38 patients with on-treatment RNA scores had recorded follow-up beyond day 21. Subtracting 21 days uniformly within that subset preserves membership, event/censor ordering and risk sets. This translation cannot correct selection associated with reaching or contributing a biopsy. Individual collection dates and reasons for unavailable measurements are needed to align predictor availability with the survival estimand.

The original report already supplied assay denominators and immune-outcome analyses.[1] Our additional contribution is a reproducible patient-linked map that distinguishes sample records, quartiles and recovered numerical measurements, describes the clinical composition of assay-specific pairs, and tests descriptive CD8 change concordance in the much smaller shared subset. Its scope is the published data: unavailable values may reflect tissue limitations, processing, reporting or other causes that these sources cannot distinguish. Serial-biopsy reports should provide collection dates, assay-specific eligibility and reasons for missing measurements alongside this map, with an explicit time origin and population for every outcome analysis.

## Data and code availability

The original clinical, sample and figure-code sources are available at the [pinned ImmunoSarc revision](https://github.com/mskcc/ImmunoSarc/tree/b71c3373bc182f9c647a6f7bc1fbd641d24db917). The executed [availability and PFS composition](../../data-opportunities-2026-09-30/deep-analysis/results/ImmunoSarc-availability-PFS-composition-actual.json), [numerical IHC reconciliation](../../data-opportunities-2026-09-30/deep-analysis/results/ImmunoSarc-measured-numeric-IHC-actual.json) and [final CD8/PD-1 outcome composition](../../data-opportunities-2026-09-30/deep-analysis/results/ImmunoSarc-CD8-PD1-outcome-composition-final.json) retain patient identifiers, literal inputs, source hashes and execution receipts. The final measured-IHC analysis completed in [run 36900530648](https://github.com/trimcrae/Rare-cancers/actions/runs/36900530648), job 110498362040.

The October 2 paired extension is reproduced by [analyze_pairs.py](analyze_pairs.py), the [frozen plan](plan.md), [all-patient ledger](patient-ledger.tsv) and [exact results](results.json), with input hashes and actual execution in [receipt.json](receipt.json). Seven synthetic tests and a distinct source-literal/rational-arithmetic [review](review/review.json) passed. No raw RNA pipeline or new primary IHC extraction was run for this extension. The original September 30 draft remains unchanged.

## Reference

1. D'Angelo SP et al. Pilot study of bempegaldesleukin in combination with nivolumab in patients with metastatic sarcoma. Nature Communications. 2022;13:3477. PMID:35710741. [doi:10.1038/s41467-022-30874-8](https://doi.org/10.1038/s41467-022-30874-8).
