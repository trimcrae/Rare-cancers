# Patient-linked assay availability in a serial-biopsy sarcoma trial

Serial-biopsy studies can report similar aggregate assay counts while supporting different patient-level comparisons. D’Angelo and colleagues reported clinical outcomes and molecular correlates from a sarcoma immunotherapy trial (NCT03282344), with biopsies scheduled at baseline and week 3.[1] Their public source data permit a further question: which patients contribute published measurements to each assay at each timepoint? We linked the clinical and sample tables to describe availability across assays, histologic cohorts and response groups. This audit concerns the composition of analyzable published subsets. It does not reassess treatment efficacy.

We used PatientSourceData.txt and SampleSourceData.txt from the mskcc/ImmunoSarc repository, pinned to revision b71c3373bc182f9c647a6f7bc1fbd641d24db917. Their respective Git blob identifiers are 8e65abf4208c2e6d9b96d8271752bfde4c85f443 and c3d9ee850299eb8930788468c87754b58d5a67f8. We joined records by Subject and checked PatientID, cohort, best response, progression-free survival and censoring concordance. All 133 sample rows linked to the 77 clinical records without duplicate patient-timepoint records. The sample table represented 69 patients with nonmissing PatientID values; eight clinical records had no PatientID. These denominators differ from the 84 patients enrolled in the original study.[1]

We defined availability from published values rather than patient-level assay flags. A value counted as available when it parsed as a finite number; missing tokens did not count. RNA immune-score availability required all nine reported immune/stromal scores, and pathway availability required all 15 reported pathway scores. CD8 immunohistochemistry (IHC) availability required a numeric CD8 quartile. We also counted any or all of the five IHC markers, whole-exome sequencing (WES) tumor mutational burden, and T-cell receptor (TCR) beta-chain diversity. A paired patient had qualifying values at both baseline and on-treatment timepoints. We retained the source cohort and response categories and performed no hypothesis tests or survival-model fitting.

Assay-specific pairs were fewer than paired sample records (Table 1). All 61 patients with an on-treatment row also had a baseline row. Only 31 patients had paired RNA immune scores, compared with 23 for CD8 IHC, 18 for all five IHC markers, 51 for WES tumor mutational burden and 36 for TCR beta-chain diversity. These counts identify different subsets; they are not interchangeable denominators for a common paired analysis. Progression sampling was sparse: three patients had progression rows, two had RNA immune scores, and none had pathway scores or numeric IHC quartiles.

**Table 1. Patients with published values by assay and timepoint.**

| Published record or measurement | Baseline | On-treatment | Paired | Progression |
|---|---:|---:|---:|---:|
| Any sample record | 69 | 61 | 61 | 3 |
| All nine RNA immune/stromal scores | 41 | 38 | 31 | 2 |
| All 15 RNA pathway scores | 41 | 38 | 31 | 0 |
| CD8 IHC quartile | 47 | 32 | 23 | 0 |
| At least one of five IHC quartiles | 52 | 38 | 30 | 0 |
| All five IHC quartiles | 39 | 24 | 18 | 0 |
| WES tumor mutational burden | 61 | 57 | 51 | 2 |
| TCR beta-chain diversity | 45 | 45 | 36 | 2 |

Counts are unique patients within each column. “Paired” requires the indicated measurement at both baseline and on-treatment timepoints. IHC markers are PDL1, CD8, CD68, FOXP3 and PD-1, as named in the source table. TCR beta-chain diversity uses the diversity_TRB field.

Histologic stratification revealed an assay-specific gap that aggregate biopsy counts conceal. The UPS/MFH/high-grade MFS cohort contained ten clinical records and seven on-treatment sample rows. Four patients had on-treatment RNA immune scores, including three with paired scores. Six had baseline CD8 IHC quartiles, but none had an on-treatment CD8 quartile or paired CD8 quartiles. Eight of the ten clinical records carried an IHC availability flag, and one on-treatment row contained other numeric IHC markers. Thus, absent CD8 values cannot be equated with absent biopsies or universal IHC nonperformance. The public table alone cannot explain whether missing values reflect tissue limitations, assay processing, reporting decisions or another cause.

Response groups also contributed different proportions of assay-specific pairs. The 77 clinical records comprised nine partial responses, 22 stable-disease responses and 46 progressive-disease responses. Paired RNA immune scores were available for four, eight and 19 patients, respectively. Paired CD8 IHC quartiles were available for two, three and 18 patients, respectively. Consequently, 18 of the 23 CD8-paired patients had progressive disease, compared with 46 of 77 clinical records overall. This describes the composition of the published subsets; it does not establish informative missingness, a response-associated mechanism or a biased treatment effect. Cross-sectional analyses and paired-change analyses nevertheless need their own assay-specific denominators.

The scheduled on-treatment biopsy also creates a timing question that the public data cannot fully resolve. The original study measured progression-free survival from treatment initiation.[1] Its public Figure3.R code selects timepoint-specific sample rows and uses treatment-origin progression-free survival in a two-argument survival object, without delayed entry. Two clinical records report events before nominal day 21, at days 17 and 19; neither has an on-treatment row. All 38 patients with on-treatment RNA immune scores have recorded follow-up beyond day 21. Subtracting 21 days uniformly within that subset would preserve its membership and event/censor ordering, and therefore its risk sets. Such a time translation cannot estimate or correct selection associated with reaching the biopsy. Individual biopsy dates and reasons for unavailable measurements would be needed to characterize that selection and align predictor availability with the survival estimand.

The original report already provided assay denominators and immune-outcome analyses.[1] The additional contribution here is a reproducible patient-linked map of assay, cohort and response availability, together with the limits of a nominal-landmark check. Future serial-biopsy reports should publish this map alongside collection dates, assay-specific eligibility and reasons for missing values. They should distinguish baseline predictors from post-treatment measurements and state the population and time origin for each survival comparison. These additions would help readers determine which biological and clinical comparisons the measured data support.

## Data and code availability

The [reproducible audit](../analysis/immunosarc_availability.mjs) and [machine-readable results](../results/immunosarc-availability.json) document the source inputs, availability definitions and patient-level checks. Original source data and figure code are available at the [pinned ImmunoSarc revision](https://github.com/mskcc/ImmunoSarc/tree/b71c3373bc182f9c647a6f7bc1fbd641d24db917).

## Reference

1. D’Angelo, S. P. et al. Nature Communications (2022). https://doi.org/10.1038/s41467-022-30874-8.
