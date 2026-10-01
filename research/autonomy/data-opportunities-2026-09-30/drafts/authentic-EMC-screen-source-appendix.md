# Supplementary note: Authentication, endpoint support and genotypic limits of published EMC drug screens

Published EMC models provide direct experimental measurements that cannot be supplied by the unresolved H-EMC-SS identity in a general proteomic atlas. Their value for secondary analysis nevertheless depends on preserving model identity, assay endpoints and the number of independent tumors.

We replayed the complete Iwata NCC-EMC1-C1 screening and dose-response workbooks [1]. All 221 screening means and standard deviations, and all 24 tabulated IC50 values, agreed with the previously extracted source records. The 221 rows represent compounds tested in one patient-derived model; they do not represent 221 biological replicates or an independent EMC cohort. The screening values ranged from −1.691% to 220.504%, including one negative value and 50 values above 100%. We retained these literal normalized measurements and their reported standard deviations. Clipping them to 0%–100% would alter the source data and the resulting rankings.

Among the 24 compounds with both screening and IC50 measurements, the Spearman rank association was 0.04087 (nominal P=0.8496). This is a selection-conditioned descriptive comparison: the 24 compounds were selected for dose-response testing, rather than randomly sampled from the screen. It does not establish that either endpoint is erroneous. The publicly acquired primary article preview did not expose the complete screening concentration, exposure and normalization methods, so the causes of the weak ranking agreement remain unresolved.

The authors had already identified brigatinib, panobinostat and romidepsin as candidates with low IC50 values. Their tabulated IC50 values were 1.73, 3.37 and 8.04 nM, respectively. These are published experimental leads, not discoveries from this reanalysis. Fifteen predefined chemical families also contained multiple literal formulation or CAS rows. Within-family screening ranges included 70.66 percentage points for ceritinib, 57.23 for afatinib and 53.23 for the specified non-S crizotinib family. These differences warrant retaining exact source identities. They cannot establish formulation-specific biology without verified comparable concentrations and experimental replication.

A distinct study established USZ20-EMC1 and USZ22-EMC2, molecularly confirmed EMC models including EWSR1–NR4A3 and TAF15–NR4A3 fusion contexts [2]. Its 40-drug screen used six-dose curves, concentrations spanning 33 pM–200 µM across the library, six days of exposure, and whole-well ATP measurement normalized to vehicle controls. Carfilzomib, doxorubicin and venetoclax were subsequently tested in both models. These endpoints were not pooled with the NCC-EMC1-C1 screen or treated as interchangeable IC50 experiments.

We acquired and checked both primary genotype and short-tandem-repeat supplements. The genotype table reported nine additional alterations of unknown functional impact for USZ20-EMC1. For USZ22-EMC2, it reported MLL3 E1689fs*28, KDM5C splice-site 1584−2A>T, and FANCA A40V. Variant read fractions were 19.54%, 13.00% and 49.86%, respectively; the FANCA alteration had unknown functional impact. Neither that variant nor the repair-gene label establishes homologous-recombination deficiency or POLQ dependence. Both models were reported microsatellite stable, with tumor mutational burdens of 1.36 and 1.7 mutations/Mb.

MTAP, SMARCB1, POLQ, CDKN2A, CDKN2B and TP53 were absent from the listed additional alterations. Their omission does not establish complete specimen-specific coverage, a negative variant result, wild-type function or intact protein expression. The STR supplement matched each source tumor to its corresponding model across 15 loci and amelogenin. These are two authenticated tumor-derived models, rather than four independent specimens for drug-response inference.

The completed reanalysis supplies exact compound joins, unclipped measurements, endpoint comparisons and model-level source qualifications. It provides no new validated treatment, clinical efficacy estimate or population therapeutic window.

## Data and reproducibility

The [complete 221-compound source replay](../deep-analysis/results/authentic-EMC-complete221-compound-screen-final.json) retains all published means, standard deviations, dose-response values and source hashes. The [two-model genotype and STR audit](../deep-analysis/results/authentic-EMC-two-model-genotype-supplements.json) preserves the separate authenticated models and literal genotypic qualifications.

## References

1. Iwata S, Noguchi R, Osaki J, et al. Establishment and characterization of NCC-EMC1-C1: a novel patient-derived cell line of extraskeletal myxoid chondrosarcoma. Human Cell. 2025;38:122. [doi:10.1007/s13577-025-01250-7](https://doi.org/10.1007/s13577-025-01250-7).
2. Bangerter et al. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. [doi:10.1007/s13577-022-00818-x](https://doi.org/10.1007/s13577-022-00818-x). [PMCID: PMC9813045](https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/).
