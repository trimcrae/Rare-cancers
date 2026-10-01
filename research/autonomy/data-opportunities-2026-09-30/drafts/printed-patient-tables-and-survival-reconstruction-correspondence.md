# Printed patient tables provide an additional check on reconstructed survival in ultra-rare cancer

Published Kaplan–Meier figures can be valuable sources when individual records are unavailable. Their reconstruction also depends on time calibration, censor allocation and source consistency. We examined two published small sarcoma series that provide printed patient-level endpoints, asking whether those tables add information beyond matching a plotted curve. This is a source-concordance analysis; it does not estimate comparative treatment efficacy.

## Methods

We transcribed the eleven first-line anthracycline progression-free survival records in a published EMC series, retaining their printed units and censor annotations [1]. In source order, the times were 7*, 4, 8, 2, 8, 10, 5*, 7, 4, 5* and 3 months, where asterisks indicate the three surgery-related censorings. The remaining eight records were events. We used the usual event-before-censor Kaplan–Meier convention for ties. Restricted mean survival time (RMST) integrates the observed survival function to a stated horizon; it is not an extrapolated mean. We retained the printed table, figure digitization, five risk counts and full calculation receipts separately.

To assess whether plot matching alone identifies the printed records, we constructed a hypothetical eleven-record dataset constrained by fifteen digitized Figure 2 ordinates and the printed risk counts. This is an explicit counterexample, not recovered patient data. We also evaluated 4,096 hypothetical rounding and tie variants with event/censor status fixed and times restricted to half-month neighborhoods of the printed values. The intervals were [t−0.5,t+0.5), with a small inward offset at boundaries. The exercise does not prove that the authors rounded their times or supply confidence intervals.

A separate trabectedin/BSC series supplied eight printed patient records, including two EMC and three mesenchymal chondrosarcoma (MCS) patients receiving trabectedin and three MCS patients receiving best supportive care [2]. We preserved each endpoint's source censor marker, including a BSC record whose PFS asterisk remains printed despite a reason referring to progression. We did not replace source censoring based on an inferred clinical history.

## Results

The eleven printed anthracycline records gave a Kaplan–Meier median of 8 months and six-month survival of 0.6364. RMST was 5.0000 months to six months, 6.1455 to eight months and 6.4848 to ten months. Leaving out one record gave median estimates of 7–8 months and six-month RMST of 4.9–5.3 months. The series reported four partial responses among ten response-evaluable patients; this denominator is distinct from the eleven treated patients contributing printed PFS.

Figure 2's accompanying description places six-month PFS near 50%, and the fifteen digitized points gave approximately 0.52 at six months. Nevertheless, its printed risk counts at 2, 4, 6, 8 and 10 months—10, 7, 5, 1 and 0—were all reproduced from the printed table when counts were taken strictly after the tick. Agreement with those counts therefore did not resolve the curve/table discrepancy.

The constructed eleven-record counterexample retained eight events and three censorings. It matched all five risk counts and all fifteen digitized ordinates to a maximum absolute survival difference of 0.00481, while giving median PFS of 7.985 months, six-month survival of 0.5195 and six-month RMST of 4.969 months. Its first event at 2.0 months was within the specified calibration constraints. These records show that excellent agreement with a digitized curve and risk table can coexist with disagreement with separately printed patient endpoints. They do not establish the original unprinted times or a unique reconstruction.

Across the 4,096 hypothetical nearest-month and tie variants, the median ranged from 6.5 to 8.5 months; six-month RMST ranged from 4.8182 to 5.1818 and eight-month RMST from 5.6932 to 6.3909. Six-month survival remained 0.6364. Thus the tested local timing uncertainty did not reconcile the table with the approximately 0.52 curve ordinate. These ranges describe the specified perturbation set only.

For the second eight-record series, our preserved patient-table calculation reproduced the published four group medians: PFS/OS of 12.5/26.4 months for trabectedin and 1.0/6.4 for BSC. That concordance is useful as a source check. It does not make these groups an EMC comparison: both EMC records were in the treated group and every BSC patient had MCS.

## Discussion

Reconstructed survival should be assessed against every available representation of an endpoint: printed patient rows, curve ordinates, risk counts, censor markers and prose. Plot and risk-table concordance alone may leave a materially different patient-table summary unresolved. Conversely, a small series with consistent printed medians may still lack an appropriate histologic comparator.

The contribution is a reproducible consistency check on published ultra-rare-cancer sources, rather than a new survival cohort or a treatment-effect claim. Guyot-style reconstruction provides a useful method [3]; our counterexample qualifies what source agreement can establish in this particular small series. Any downstream analysis should preserve the discrepancy and identify which source representation it uses.

## Data and reproducibility

The [complete precision/concordance analysis](../deep-analysis/results/printed-IPD-complete-precision-and-concordance.json), [printed clinical records](../deep-analysis/results/printed-clinical-IPD-actual.json) and [figure-reading record](../../../modalities/km-figure-readings.json) preserve the observations, hypothetical variants and source units. The analysis completed in [run 36896523203, job 110484838853](https://github.com/trimcrae/Rare-cancers/actions/runs/36896523203/job/110484838853). Independent checks reproduced 173 reported arithmetic quantities without differences. No simulated record is labeled as observed patient data.

## References

1. Clinical Sarcoma Research. 2013;3:16. [doi:10.1186/2045-3329-3-16](https://doi.org/10.1186/2045-3329-3-16). [PMC3879193](https://pmc.ncbi.nlm.nih.gov/articles/PMC3879193/).
2. Morioka et al. BMC Cancer. 2016. [doi:10.1186/s12885-016-2511-y](https://doi.org/10.1186/s12885-016-2511-y). [PMC4946242](https://pmc.ncbi.nlm.nih.gov/articles/PMC4946242/).
3. Guyot P et al. BMC Medical Research Methodology. 2012;12:9. [doi:10.1186/1471-2288-12-9](https://doi.org/10.1186/1471-2288-12-9).
