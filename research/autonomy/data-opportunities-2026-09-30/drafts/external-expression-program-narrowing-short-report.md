# An external tissue RNA test narrows a proposed NR4A3 expression program

## Abstract

Literature-derived gene sets can separate tumor groups while providing limited evidence for a broader regulatory program. We tested a frozen nineteen-gene NR4A3-related set in an author-released RNA-sequencing matrix containing 704 soft-tissue tumor specimens. Removing recorded nonprimary specimens and three known reused EMC specimens left 644 eligible specimens, including nine EMCs. The nineteen-gene score showed rank separation from three prespecified comparator histologies (equal-histology superiority A = 0.880; conditional bootstrap interval 0.796–0.955). However, the sixteen genes outside the three established fusion-related genes gave A = 0.473 (0.347–0.603). A complementary audit of all 32 released fusion ATAC marker panels found window-sensitive overlaps with established genes and no overlap with the broader sixteen-gene component in the four NR4A3 fusion arms. These results transfer and narrow a composite expression contrast without establishing a new nineteen-gene program, direct fusion regulation, or therapeutic dependence.

## Introduction

Extraskeletal myxoid chondrosarcoma (EMC) provides an example of the distinction between a molecular association and a mechanistic program. Published experiments connect NR4A3 chimeras to SEMA3C, PPARG, and ENO3 in different experimental systems and with different fusion partners [1–3]. Other proposed genes are supported by native-receptor or indirect expression evidence. A pooled nineteen-gene set can therefore combine evidence of different kinds. Earlier array analyses found that this pooled set did not clear their matched-size reference thresholds on either platform. Those analyses also exposed comparator and reference-pool sensitivity. We retained those unfavorable results and asked whether the fixed set transferred to a subsequently released tissue RNA-sequencing dataset.

## Methods

We used the public author matrix associated with Hofvander and colleagues' transcriptomic study [4], pinned to repository commit 984a5eddeb3d616dea2f404ed4032c8f78fba60e. The matrix contained 19,116 unique gene symbols and 704 tumor-specimen columns; its SHA256 was b0d665d1bd1d96ace1faf66cc5a4d7ab7e41cb487c8f0f61734f102a1f9a7af3. Original diagnoses, sequencing year, specimen exceptions, and previous-publication comments were reconciled against Table S1. We excluded all recorded specimen exceptions symmetrically across diagnoses, together with EMC specimens 104-92, 168-97, and 536-00, whose comments explicitly linked them to the earlier EMC discovery cohort. EMC local recurrence 5081-14 was also excluded. Nine retained EMC specimen identifiers and every eligibility decision are provided with the analysis.

The source study reports one tumor per patient. Our executable join verifies unique laboratory identifiers, rather than independently reconstructing patient identity across all historical publications. We therefore describe observed units as specimens and characterize the analysis as reduced for known overlap, rather than universally independent.

Primary comparators were fixed before expression analysis: fourteen myxoid liposarcomas, thirteen low-grade fibromyxoid sarcomas, and eighteen synovial sarcomas. Myxofibrosarcoma and dermatofibrosarcoma protuberans were separate context comparisons. Each gene was converted to its within-specimen fractional midrank among all 19,116 genes; a set score was the mean of its gene ranks with equal positive weights. This transfer amendment changes the measurement scale from the earlier array scores and does not pool assays. We retained the complete nineteen-gene set, the three established genes as a descriptive component, and the remaining sixteen genes as a separate component. No membership, cutoff, or comparator was selected using new expression values.

For each comparator, A is the fraction of EMC-comparator pairs in which the EMC score is higher, allocating half weight to ties. The primary summary gives each comparator histology equal weight. Exact-year contrasts weight supported years by their EMC specimen counts. Each primary comparator supports three EMCs; their combined support comprises only four unique EMC specimen IDs. We calculated 2,000 histology-and-year stratified bootstrap intervals and retained all EMC, year, and comparator-histology deletions. Singleton year cells remain fixed, so intervals are conditional on sparse observed support and do not represent all biological uncertainty.

## Results

The nineteen-gene score showed marginal A = 0.8804, with a conditional 95% bootstrap interval of 0.7965–0.9550. Histology-specific values were 0.7063 against myxoid liposarcoma, 0.9658 against low-grade fibromyxoid sarcoma, and 0.9691 against synovial sarcoma. Exact-year A was 1.000 for each primary comparator. Leaving out one EMC specimen retained marginal A between 0.8655 and 0.9210; deleting one primary histology gave 0.8361–0.9675. These deletions describe sensitivity within the observed dataset and cannot resolve unrecorded cohort overlap or batch effects.

The two components behaved differently. The three-gene composite gave A = 1.000 against each primary comparator, whereas the remaining sixteen genes gave marginal A = 0.4733 (interval 0.3467–0.6029) and year-matched A = 0.5365 (0.3651–0.7238). The sixteen-gene histology contrasts were 0.4127, 0.3590, and 0.6481, respectively. Its year-matched estimate fell below 0.5 in some EMC and histology deletions. Thus transfer of the pooled score does not demonstrate enrichment of its remaining genes as a group.

| Frozen set | Genes | Marginal A | Conditional 95% interval | Exact-year A |
|---|---:|---:|---|---:|
| Pooled literature set | 19 | 0.8804 | 0.7965–0.9550 | 1.0000 |
| Established component | 3 | 1.0000 | 1.0000–1.0000 | 1.0000 |
| Remaining component | 16 | 0.4733 | 0.3467–0.6029 | 0.5365 |

Perfect separation of the three-gene composite does not mean that each constituent is elevated against every histology. For example, PPARG alone gave marginal A = 0.0159 against myxoid liposarcoma, and SEMA3C gave A = 0.2426 against the myxofibrosarcoma context group. Composite ranks and individual gene contrasts answer different questions. The degenerate 1.000–1.000 bootstrap interval reflects the observed separated samples, including sparse year cells, and should not be read as certainty in the population.

We also compared the nineteen-gene score with 10,000 diagnosis-blinded gene sets approximately matched for median log TPM, variability, and detection frequency. Its marginal and year-matched scores exceeded 97.2% and 99.51% of these draws, giving upper-tail empirical values of 0.0281 and 0.0050. This sensitivity addresses measured gene-level distributional differences; it does not match gene-gene correlation, prove EMC specificity, or reverse the older array null failures. Context comparisons were less uniform: the pooled score gave A = 0.6556 against myxofibrosarcoma and 0.9333 against dermatofibrosarcoma protuberans. Only one EMC specimen supported the year-matched dermatofibrosarcoma comparison.

Companion analyses retained predefined extracellular-matrix, nuclear-receptor, transcription, proteostasis, apoptosis, chromatin, and repair annotation modules rather than selecting promising individual rows. Seventeen of eighteen historical modules had complete symbol coverage; the p53-output module was withheld because RPS27L was absent. Module transcript scores are not measures of glycan structure, receptor activity, phosphorylation, genomic loss, apoptotic priming, or drug dependence. Their full signed comparator effects and deletion sensitivities accompany this report without a significance-selected module discovery claim.

## Complementary fusion ATAC source analysis

We interrogated all 32 author-released marker BED panels from GSE243553 and reconciled missing target annotations against official GRCh38 gene coordinates. The frozen nineteen-gene set, its three-gene established component and its remaining sixteen genes were evaluated in the four NR4A3 fusion arms. A broad promoter window, 10 kb upstream and 15 kb downstream, was retained alongside a narrow 2 kb upstream and 0.5 kb downstream sensitivity. Across all arms and windows, the output retains 14,144 gene-level rows and 192 summaries. These data concern engineered HEK293T cells, rather than EMC tissue.

Within the broad window, the established component had overlaps in zero of three genes for EWSR1–NR4A3, two of three for TAF15–NR4A3 and TCF12–NR4A3 (ENO3 and PPARG), and one of three for TFG–NR4A3 (PPARG). The remaining sixteen genes had zero overlaps in all four arms. Under the narrow window, all nineteen targets had zero overlaps in those arms. Promoter window choice therefore materially changes the apparent support for the established component.

We retained a fixed descriptive family of twelve arm/set comparisons against a 202-gene DDR background. Only the broad-window TAF15 arm met the two-percent background-hit floor; its established-component comparison had corrected q=0.1248. The TCF12 comparison had nominally lower corrected q=0.0103, but only two of 202 background genes overlapped, below the prespecified floor. The background was not matched for accessibility or gene-gene correlation, so these hypergeometric results do not establish biological enrichment.

The released marker BEDs are author-defined differential-accessibility calls; their associated code does not establish that these files represent a specific fusion-versus-empty-control contrast. Native NR4A3 and reciprocal-fusion marker BEDs were not present. Eight other fusion arms had some overlaps with the sixteen-gene component (eleven arm/window summaries across both windows), reinforcing that a zero in a particular marker panel is not a statement of gene absence. ATAC accessibility is not direct fusion binding, expression regulation or dependency. Neither the broad overlaps nor their narrow-window disappearance provide an independently verified EMC mechanism. These source-defined results qualify the existing RNA argument and do not supply a separate functional paper.

## Discussion

This analysis demonstrates a narrow form of transfer: a fixed literature-derived score separates EMC specimens from specified comparators in another RNA assay, while its broader sixteen-gene component remains weak and comparator dependent. The positive signal is compatible with the established genes carrying the composite contrast. It does not establish new fusion binding, direct regulation, or a shared nineteen-gene cellular program. The three established genes themselves have different mechanistic provenance: ENO3 experiments used TFG::NR4A3, while SEMA3C and PPARG experiments used other chimeras and experimental systems. Their expression cannot be treated as interchangeable evidence for EWSR1::NR4A3 regulation in these specimens.

The external dataset provides a larger comparator pool but only nine retained EMC specimens and four with primary exact-year support. Bulk TPM is compositional; tissue admixture, sampling site, RNA quality, and sequencing-year differences remain alternatives to tumor-cell regulation. Known overlap exclusions improve the interpretation but do not replace a complete patient crosswalk. No validated recurrence or treatment endpoint was joined, and no survival or therapeutic-effect estimate is implied.

The contribution is a measured qualification of an existing expression argument, with the unfavorable old null results and the weak sixteen-gene component visible. Published tissue measurements support testing and narrowing the pooled expression claim; they do not establish a new mechanistic or treatment-design result.

## References

1. Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol. 2019;249(1):90–101. DOI: 10.1002/path.5284.
2. Filion C, Motoi T, Olshen AB, et al. The EWSR1/NR4A3 fusion protein of extraskeletal myxoid chondrosarcoma activates the PPARG nuclear receptor gene. J Pathol. 2009;217:83–93. DOI: 10.1002/path.2445.
3. Kim AY, Lim B, Choi J, Kim J. The TFG-TEC oncoprotein induces transcriptional activation of the human beta-enolase gene via chromatin modification of the promoter region. Mol Carcinog. 2016. PMID 26310886; DOI: 10.1002/mc.22384.
4. Hofvander et al. Transcriptomic subgroups in soft tissue tumors correlate with morphologic subtype, genomic features, and outcome. Clinical Cancer Research. 2026. DOI: 10.1158/1078-0432.CCR-25-3740. Author-released data: https://doi.org/10.5281/zenodo.17866629.

5. Frenkel et al. Nature Biotechnology. 2025. DOI: 10.1038/s41587-024-02347-4. GEO: GSE243553.

The [complete 32-panel ATAC analysis](../deep-analysis/results/ATAC-all32-marker-panels-and-frozen-program-actual.json) retains every coordinate and call, fixed families, annotation repairs and source limitations. It completed in [run 36921168639, job 110567359954](https://github.com/trimcrae/Rare-cancers/actions/runs/36921168639/job/110567359954).

Data and code: frozen source hashes, specimen selection, all three set scores, comparator contrasts, matched-gene draws, and complete sensitivity results are provided with the accompanying repository.
