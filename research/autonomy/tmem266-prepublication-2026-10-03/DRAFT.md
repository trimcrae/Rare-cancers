---
id: DOC-TMEM266-RNA-LETTER-DRAFT-20261003
title: Comparative enrichment of TMEM266-associated RNA in extraskeletal myxoid chondrosarcoma
level: L3
kind: manuscript
status: live
purpose: Report an exploratory comparative EMC RNA association and its transcript-region support.
scope: Public tissue reanalysis; no cellular localization, full-length transcript, protein or clinical validation.
audience: [maintainers, external reviewers, collaborators]
date: 2026-10-03
last_verified: 2026-10-03
---

# Comparative enrichment of TMEM266-associated RNA in extraskeletal myxoid chondrosarcoma

Tristan D. McRae

Working research-letter draft, 3 October 2026. This exploratory secondary analysis has not been submitted or approved for publication. Author affiliation and correspondence details remain to be supplied for an outgoing version.

To the Editor,

Extraskeletal myxoid chondrosarcoma (EMC) has a distinctive transcriptional phenotype, but a tissue-level RNA association does not by itself identify the cells or protein products responsible. The development of CHRNA6 RNA in situ hybridization illustrates the value of following an expression observation with direct localization in EMC tissue.[1] We investigated TMEM266, also known as C15orf27 or HVRP1, as a candidate emerging from a comparative transcriptomic screen. The question was whether its EMC-associated signal was reproducible across assays and extended into upstream coding regions, rather than being supported only by a downstream transcript segment.

This was an exploratory discovery analysis, not a prespecified single-gene validation study. A frozen UniProt-based universe of 2,694 measurable membrane-associated genes was screened in the public tissue RNA-sequencing resource of Hofvander and colleagues.[2] Nine eligible primary EMC specimens were compared separately with myxoid liposarcoma (n=14), low-grade fibromyxoid sarcoma (LGFMS; n=13), and synovial sarcoma (n=18). Previously identified reused specimens and a recurrence were excluded. Twenty-one genes met the recorded discovery criteria, and 16 met the subsequent array follow-up criteria; TMEM266 was selected for further investigation from these results. All nominations, including established markers and unsuccessful candidates, are retained in the analysis record.

TMEM266 abundance in the nine EMC specimens had a median of 28.88 transcripts per million (TPM; range, 6.73–56.82). Every EMC value exceeded every value in each primary comparator group. The corresponding empirical probability of superiority, A, was 1.00 in all three comparisons; A gives half credit to ties and describes the observed distributions, not prospective diagnostic accuracy. The discovery intersection-union test, using the largest of the three directional P values with Benjamini–Hochberg adjustment over the screened genes, yielded q=0.00961. Comparisons restricted to shared sequencing years also yielded A=1.00, but contained only three EMC specimens per comparison and four distinct EMC specimens overall. These small subsets reduce one source of confounding without establishing generalizability.

In the original GSE24369 tissue arrays, the uniquely assigned C15orf27/TMEM266 transcript cluster showed higher expression in six EMC specimens than in LGFMS (n=17; A=0.922), myxofibrosarcoma (n=6; A=0.917), solitary fibrous tumor (n=5; A=0.900), and desmoid tumors (n=6; A=1.00).[3] This is concordance across assay datasets, with unresolved patient overlap: both the RNA-sequencing and array resources include Lund material, and a specimen crosswalk was unavailable. Their EMC counts must therefore not be added as independent patients. GSE24369 was also used in the earlier CHRNA6 discovery study.[1]

We next examined whether the array association extended beyond downstream TMEM266 sequence. Before inspecting raw probe intensities, we recovered the 30 physical 25-mer probes for transcript cluster 7985066, assigned them to 13 annotated regions, and froze an upstream score using 14 probes across six regions corresponding to canonical exons 2–7. Each probe was converted to its intensity percentile among all finite features on its own array; probes were averaged within regions and the six region means weighted equally. This additional analysis reused all six EMC and 17 LGFMS arrays and is evidence about the location of the RNA-associated signal, not a new validation cohort.

The upstream score was higher in EMC than LGFMS, with A=0.971 and an exploratory 95% array-bootstrap interval of 0.882–1.000 (2,000 resamples). All six regions showed the same direction, with individual A values of 0.824–0.980. Current transcript annotation placed two of the 14 probes partly in the 5′ untranslated region; an annotation-defined sensitivity analysis retaining only 12 probes wholly within coding exons 3–7 gave A=0.951 (95% interval, 0.824–1.000). Median upstream percentile scores were 0.708 in EMC and 0.420 in LGFMS. Fixed probes matched for GC content also showed a smaller class shift (medians, 0.525 and 0.519; A=0.853), so the control analysis does not eliminate technical confounding. The bootstrap intervals are conditional descriptions after gene selection, not selection-adjusted confirmation. Exact probe matches were checked within the TMEM266 locus; genome-wide cross-hybridization specificity was not established.

Normal tissue provides a substantial counterweight to the tumor comparisons. The two normal skeletal-muscle RNA pools in GSE24369 had upstream scores of 0.693 and 0.704, within the EMC range; the strict coding-region scores likewise overlapped. These pools are descriptive controls, not estimates of interindividual normal-muscle variation. Consequently, the result supports enrichment relative to selected sarcomas but does not establish tumor specificity or exclude entrapped muscle as a contributor. Small analyses of anatomical site and muscle-associated transcripts also cannot resolve the cellular source.

A separate published FFPE series supplies limited orthogonal tissue evidence.[4] Its expression export contains a TMEM266-targeted measurement for each of 12 pathology-reviewed EMC tissue areas. One deposited sample has a Si22/Si21 identifier conflict; excluding it leaves 11 specimens with a median of 3.978 on the authors' Log2CPM scale (range, −0.376–7.223). The manufacturer's matching Human Whole Transcriptome 2.0 design spans the canonical TMEM266 exon 10–11 junction outside the identified antisense-overlap region.[5] This supports interpretation of a spliced TMEM266 target region, subject to the unreported exact assay-manifest revision and assay specificity. It is not a count of positive tumors: the export does not establish a validated detection threshold, and the junction is shared by coding and alternative transcript models. The source's provenance discrepancies and lack of a valid EMC external-validation cohort further limit its evidential weight (Supplementary Methods).

These measurements support an EMC-associated RNA pattern that includes upstream coding regions as well as a downstream splice-junction target. They do not phase those regions into a single full-length molecule. Sparse downstream coverage in one source-authenticated EMC-derived culture provides additional locus-level support, but its two sequencing runs are technical replicates and do not establish a complete coding transcript.[6] Prior work on TMEM266 forms in mouse cerebellum likewise makes a gene-level signal an insufficient basis for inferring the protein product in EMC.[7] No tumor-cell localization, TMEM266 protein expression, voltage-sensing function, dependency, or therapeutic window was demonstrated here.

The practical next experiment is tissue localization with separately targeted upstream and downstream TMEM266 regions, interpreted alongside EMC morphology and fusion identity and with muscle and stromal controls. The contribution of this reanalysis is to identify a specific, substantial comparative RNA association and show that it is not confined to the downstream target alone. Bounded literature searches did not retrieve a direct EMC-specific TMEM266 claim, but coverage of all candidates from earlier screens was incomplete; we therefore make no claim of first discovery. Whether the association resides in malignant cells, and whether those cells produce a full-length protein, remain the questions that determine its biological and translational significance.

## Data, code, and declarations

Original data are available through the sources below; the RNA-sequencing expression resource is also deposited at [Zenodo](https://doi.org/10.5281/zenodo.17866629). Analysis plans, selected measurements, source hashes, scripts, and independent arithmetic checks are retained in the accompanying [Supplementary Methods](SUPPLEMENT.md) and its linked repository folders. The current analysis package is local and has not been deposited as a public release. No new patients were recruited or specimens collected for this secondary analysis; this statement does not assert a new ethics approval or exemption.

Funding: none. Competing interests: none declared, under the author's standing declarations. OpenAI Codex assisted with source retrieval, code, analysis, independent computational checks, and drafting; human author review and responsibility for an outgoing version remain required.

## References

1. Dulken et al. CHRNA6 RNA In Situ Hybridization Is a Useful Tool for the Diagnosis of Extraskeletal Myxoid Chondrosarcoma. *Modern Pathology*. 2024. [doi:10.1016/j.modpat.2024.100464](https://doi.org/10.1016/j.modpat.2024.100464).
2. Hofvander J et al. Transcriptomic Subgroups in Soft Tissue Tumors Correlate with Morphologic Subtype, Genomic Features, and Outcome. *Clinical Cancer Research*. 2026;32:1825–1834. [doi:10.1158/1078-0432.CCR-25-3740](https://doi.org/10.1158/1078-0432.CCR-25-3740).
3. Möller E et al. FUS-CREB3L2/L1–Positive Sarcomas Show a Specific Gene Expression Profile with Upregulation of CD24 and FOXL1. *Clinical Cancer Research*. 2011;17:2646–2656. [Original article](https://aacrjournals.org/clincancerres/article/17/9/2646/12912/FUS-CREB3L2-L1-Positive-Sarcomas-Show-a-Specific); [GSE24369](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE24369).
4. Chaiboonchoe A et al. Prognostic biomarkers for enhanced risk stratification in extraskeletal myxoid chondrosarcoma: a retrospective cohort study. *PeerJ*. 2026;14:e21497. [doi:10.7717/peerj.21497](https://doi.org/10.7717/peerj.21497).
5. BioSpyder. Human Whole Transcriptome 2.0 manifest, 190620 revision. [Official assay manifest](https://www.biospyder.com/s/190620HumanWholeTranscriptome20Manifest.xlsx).
6. Davila JI et al. Impact of RNA degradation on fusion detection by RNA-seq. *BMC Genomics*. 2016;17:814. [doi:10.1186/s12864-016-3161-9](https://doi.org/10.1186/s12864-016-3161-9); [GSM2113301](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM2113301).
7. Kawai T et al. Insight into the function of a unique voltage-sensor protein (TMEM266) and its short form in mouse cerebellum. *Biochemical Journal*. 2022;479:1127–1145. [doi:10.1042/BCJ20220033](https://doi.org/10.1042/BCJ20220033).
