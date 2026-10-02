---
id: "DOC-DATA-OPPORTUNITIES-2026-09-30-DRAFTS-AUTHENTIC-EMC-SCREEN-SOURCE-APPENDIX"
title: "Supplementary note: Authentication, endpoint support and genotypic limits of published EMC drug screens"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Supplementary note: Authentication, endpoint support and genotypic limits of published EMC drug screens."
scope: "September 30 measured-data campaign; retain the source qualifications, execution boundaries and historical status stated in the body."
audience: ["maintainers","external reviewers"]
date: "2026-09-30"
last_verified: "unverified"
_backfilled: "true"
---

# Supplementary note: Authentication, endpoint support and genotypic limits of published EMC drug screens

Published EMC models provide direct experimental measurements that cannot be supplied by the unresolved H-EMC-SS identity in a general proteomic atlas. Their value for secondary analysis nevertheless depends on preserving model identity, assay endpoints and the number of independent tumors.

We replayed the complete Iwata NCC-EMC1-C1 screening and dose-response workbooks [1]. All 221 screening means and standard deviations, and all 24 tabulated IC50 values, agreed with the previously extracted source records. The 221 rows represent compounds tested in one patient-derived model; they do not represent 221 biological replicates or an independent EMC cohort. The screening values ranged from −1.691% to 220.504%, including one negative value and 50 values above 100%. We retained these literal normalized measurements and their reported standard deviations. Clipping them to 0%–100% would alter the source data and the resulting rankings.

Among the 24 compounds with both screening and IC50 measurements, the Spearman rank association was 0.04087 (nominal P=0.8496). This is a selection-conditioned descriptive comparison: the 24 compounds were selected for dose-response testing, rather than randomly sampled from the screen. It does not establish that either endpoint is erroneous. The publicly acquired primary article preview did not expose the complete screening concentration, exposure and normalization methods, so the causes of the weak ranking agreement remain unresolved.

An actual image audit accounted for every released IC50 entry: Supplementary Figure 2 contained 21 panels in a two-frame TIFF and main Figure 4 contained brigatinib, panobinostat and romidepsin. We retained the literal Doxorubicin/Doxorubicin (Adriamycin) alias and Mitoxantron/Mitoxantrone spelling qualification. Crizotinib and S-Crizotinib, and ixazomib and ixazomib citrate, remained separate entries. Figure concentrations are µM; the workbook explicitly reports IC50 in nM (1 µM=1,000 nM).

The ordinary DOI-scoped public Figure 4 page returned its complete caption and 970×756 image, resolving the earlier thumbnail/caption limitation. The two returned image URLs were byte-identical and represent one figure. Its caption identifies NCC-EMC1-C1 passage 24 for the three main panels; this passage is not automatically assigned to all supplementary panels. Curves were not digitized or refitted. Complete experimental methods, replicate counts, error-bar definitions and raw replicate measurements remain unverified.

The authors had already identified brigatinib, panobinostat and romidepsin as candidates with low IC50 values. Their tabulated IC50 values were 1.73, 3.37 and 8.04 nM, respectively. These are published experimental leads, not discoveries from this reanalysis. Fifteen predefined chemical families also contained multiple literal formulation or CAS rows. Within-family screening ranges included 70.66 percentage points for ceritinib, 57.23 for afatinib and 53.23 for the specified non-S crizotinib family. These differences warrant retaining exact source identities. They cannot establish formulation-specific biology without verified comparable concentrations and experimental replication.

A distinct study established USZ20-EMC1 and USZ22-EMC2, molecularly confirmed EMC models with EWSR1–NR4A3 and TAF15–NR4A3 fusion contexts [2]. Its full 40-drug screen was conducted only in USZ20-EMC1. The Methods specifies passage 5, whereas the Results specifies passage 6; we preserve this source discrepancy. The screen used 384-well ultra-low-attachment plates, 800 cells per well, 50 µl medium, six-day exposure and whole-well ATP measurement normalized to vehicle controls. Per-drug curves were described as six-dose, three-log designs, with concentrations spanning 33 pM–200 µM across the library. This does not imply that every drug had that complete library-wide concentration range.

The acquired primary XML contains no numeric response tables. Its two declared supplements contain genotype and STR information. Figure 5 supplies all 40 ordinal response summaries, divided by the source authors into 17 chemotherapies and 23 targeted agents. We decoded every row against the actual five legend colors in the SHA-verified source image; the maximum RGB distance between a row patch and its assigned legend color was one unit. This is recovery of the published category, not estimation of a continuous AUC or IC50.

| Source Figure 5 panel | Rows | High | Good | Moderate | Low | None |
|---|---:|---:|---:|---:|---:|---:|
| A: author-labeled chemotherapies | 17 | 1 | 1 | 5 | 2 | 8 |
| B: author-labeled targeted agents | 23 | 0 | 2 | 4 | 8 | 9 |
| Total | 40 | 1 | 3 | 9 | 10 | 17 |

The literal legend associates these classes with <10%, 11–20%, 21–40%, 41–70% and >71% cell viability, respectively; its interval gaps were retained. The caption describes AUC-based assessment combining efficacy and potency, but a continuous per-drug AUC export was not recovered from the verified primary and declared supplements. Accordingly, the color classes were not converted to raw viability values or transplanted as cutoffs for another assay. AZD5153 is the fourth moderate targeted row; Encorafenib is the first low row. Literal source spellings Abmaciclib, Naraparib Tosylate and WE-822 remain uncorrected.

Carfilzomib, doxorubicin and venetoclax were selected by the original authors for follow-up in both USZ20-EMC1 and USZ22-EMC2, at passages 8–10. These are three selected drugs across two models, rather than a second complete 40-drug screen or an 80-row response matrix. The follow-up used 96-well plates, 1,000 cells per well and reported triplicates, with a six-day endpoint; Figure 6 describes mean±SD. The authors reported high sensitivity to carfilzomib and good-to-moderate sensitivity to doxorubicin in both models. Venetoclax's moderate initial USZ20 screen classification was followed by no monotherapy response in either validation model. These selected observations do not estimate a general screen-validation rate.

Figure 6 contains carfilzomib/venetoclax and carfilzomib/doxorubicin combination curves and ZIP, Loewe, Bliss and HSA heatmaps. We retain the actual figure-defined combinations despite a differently worded Discussion sentence. The original authors reported synergy in USZ20 and additive effects in USZ22; these are prior results, not newly computed synergy scores. Raw replicate curves and numeric synergy matrices were not recovered from the verified archive. Responses in one model per fusion partner cannot identify a fusion-partner effect or establish fusion-independent biology.

We compared every Figure 5 drug label with the complete 221-row Iwata screen while retaining all source records. Ten of 40 labels had a unique exact literal-name match. Removing parenthetical aliases and normalizing case and whitespace yielded 25 total label candidates, each unique at that naming stage. A broader formulation-family diagnostic yielded candidates for 27 labels, but 12 of these had two distinct Iwata source/CAS rows: 39 returned screening rows across 27 Bangerter labels. These counts are nested naming diagnostics, not independent matched compounds. The 24 selected Iwata dose-response rows contained four literal/qualified label candidates, or six after the broader formulation diagnostic.

No CAS identifier was reported for any of the 40 Bangerter figure rows. We therefore did not assign chemical identities, choose a formulation or average candidate rows. The source spellings noted above were not silently repaired. The complete comparison retains measured Iwata means, standard deviations and selected IC50 values alongside the Bangerter source category. The source summaries, dose support and experimental formats differ. No pooled potency estimate, cross-assay response correlation or transferred sensitivity cutoff was computed.

We acquired and checked both primary genotype and short-tandem-repeat supplements. The genotype table reported nine additional alterations of unknown functional impact for USZ20-EMC1. For USZ22-EMC2, it reported MLL3 E1689fs*28, KDM5C splice-site 1584−2A>T, and FANCA A40V. Variant read fractions were 19.54%, 13.00% and 49.86%, respectively; the FANCA alteration had unknown functional impact. Neither that variant nor the repair-gene label establishes homologous-recombination deficiency or POLQ dependence. Both models were reported microsatellite stable, with tumor mutational burdens of 1.36 and 1.7 mutations/Mb.

MTAP, SMARCB1, POLQ, CDKN2A, CDKN2B and TP53 were absent from the listed additional alterations. Their omission does not establish complete specimen-specific coverage, a negative variant result, wild-type function or intact protein expression. A source growth-summary discrepancy was also retained: Figure 3 prints 5.01 days for USZ20-EMC1, while the prose/caption gives 5.09 days; USZ22-EMC2 is reported as 6.05 days. No growth curve was refitted. The STR supplement matched each source tumor to its corresponding model across 15 loci and amelogenin. These are two authenticated tumor-derived models, rather than four independent specimens for drug-response inference.

The completed reanalysis supplies all 40 published ordinal summaries, complete literal-name candidate comparisons, unclipped screening measurements, endpoint comparisons and model-level source qualifications. It provides no new validated treatment, clinical efficacy estimate or population therapeutic window.

## Data and reproducibility

The [complete literal 221 screening and 24 IC50 measurements](../deep-analysis/results/Iwata-complete221-screen-and24-IC50-literal-measurements-final.json) preserve every reported mean, standard deviation, formulation and CAS identifier. The [primary source replay](../deep-analysis/results/authentic-EMC-complete221-compound-screen-final.json) records their workbook concordance and endpoint diagnostics. The [two-model genotype and STR audit](../deep-analysis/results/authentic-EMC-two-model-genotype-supplements.json) preserves the separate authenticated models and literal genotypic qualifications.

The [exact provider/unit audit](../deep-analysis/results/Iwata-exact-public-primary-providers-and-IC50-units-final.json), [actual 24-panel image reconciliation](../deep-analysis/results/Iwata-all24-actual-source-curve-label-reconciliation-final.json) and [complete public Figure 4 caption/assets](../deep-analysis/results/Iwata-normal-public-Fig4-caption-and-assets-final.json) preserve source bytes, OCR, manual label qualifications and access limits. Final figure checks completed in [run 36937405322](https://github.com/trimcrae/Rare-cancers/actions/runs/36937405322) and [run 36938047423](https://github.com/trimcrae/Rare-cancers/actions/runs/36938047423).

The [complete Bangerter primary and actual figure audit](../deep-analysis/results/Bangerter-complete40-drug-primary-and-actual-figure-source-final.json) preserves primary body text, source captions, tables and archive receipts. The [all 40 measured ordinal rows and complete source-overlap qualification](../deep-analysis/results/Bangerter-all40-measured-ordinal-and-complete-source-overlap-final.json) preserves every row, legend/pixel anchors, all candidate source identities and unresolved joins. Source acquisition completed in [run 36939274161/job 110626780030](https://github.com/trimcrae/Rare-cancers/actions/runs/36939274161/job/110626780030); the successful ordinal/overlap replay completed in [run 36940580660/job 110630922274](https://github.com/trimcrae/Rare-cancers/actions/runs/36940580660/job/110630922274). The figure SHA256 is 3d22b276d0b845d7d11ca8ef967caefedc3c4798a3d41e2b0ea129912106eb36; the frozen Iwata extraction SHA256 is 52cfb777f196fdd2440bc74382e7aa276515acc6a9ed79d0660a16ccaef50bb2. Original binary assets remain in the execution artifacts with thirty-day retention; source hashes, derivations and measured tables are durable in the repository.

## References

1. Iwata S, Noguchi R, Osaki J, et al. Establishment and characterization of NCC-EMC1-C1: a novel patient-derived cell line of extraskeletal myxoid chondrosarcoma. Human Cell. 2025;38:122. [doi:10.1007/s13577-025-01250-7](https://doi.org/10.1007/s13577-025-01250-7).
2. Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. Human Cell. 2023;36:446–455. [doi:10.1007/s13577-022-00818-x](https://doi.org/10.1007/s13577-022-00818-x). [PMCID: PMC9813045](https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/).
