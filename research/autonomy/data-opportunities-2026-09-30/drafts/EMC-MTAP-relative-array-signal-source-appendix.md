# Relative 9p21 array signals in ten published EMC profiles

This supplementary analysis asks a limited genomic question: do published EMC methylation-array intensities provide an obvious relative signal of MTAP loss? It does not establish absolute copy number, protein loss or drug dependence. The source's original copy-number landscape was already reported; this locus-focused reuse is supporting evidence rather than a first EMC copy-number study.

## Sources and analysis

We acquired all 28 required paired IDAT sources: ten EMC array profiles and eighteen FFPE normal-muscle/reactive references. The ten EMC profiles used nine 450K and one EPIC array; the references used six 450K and twelve EPIC arrays. All 56 IDAT files had distinct source hashes. Array profiles are not independently verified clinical patients, and shared query chips were retained as provenance rather than interpreted as independent collection events.

We used minfi 1.48 preprocessing and total methylated-plus-unmethylated intensity. The common intensity intersection comprised 452,453 probes. Standard conumee 1.6, pinned to hovestadt/conumee commit cc1caffa49143ef06fde5036b434846649542623, retained 439,031 probes from its native annotation and rebuilt 15,136 hg19 bins after the intersection. A separate author-pipeline sensitivity used dstichel/conumee commit 372c3f0342ce8eec3e7eca03c45d5bce2f1d0a3a, the same retained common probes and rebuilt bins, with its BAF correction. Source annotations, centromere handling and the author implementation's reference-dropping behavior were preserved explicitly.

The specified hg19 locus ranges contained sixteen MTAP probes, five CDKN2A probes and three CDKN2B probes. These counts describe those ranges rather than coverage of every transcript or exon. CNV.detail summarizes each specified locus by its median probe log2 ratio before the stated baseline corrections. Standard analysis comprised ten EMC fits against all eighteen references, ten against same-platform references, and eighteen leave-one-normal-reference-out controls. The author sensitivity comprised ten EMC fits and eighteen normal controls. All 66 fits completed, generating 198 locus rows, with no invalid locus corrections or MAD fallbacks. Rebuilding bins after restricting the annotation avoided treating excluded probes as present in the common assay.

## Results

| Analysis | Profiles | MTAP locus-detail log2-ratio range | Corresponding relative-ratio range |
|---|---:|---:|---:|
| Standard, all references | 10 EMC | −0.13419 to +0.04717 | 0.91118–1.03324 |
| Standard, same-platform references | 10 EMC | −0.08677 to +0.06196 | 0.94163–1.04388 |
| Pinned author BAF sensitivity | 10 EMC | −0.15473 to +0.09867 | 0.89830–1.07079 |
| Standard normal leave-one-out | 18 normals | −0.08485 to +0.07325 | 0.94288–1.05208 |
| Author BAF normal leave-one-out | 18 normals | −0.11007 to +0.12256 | 0.92655–1.08866 |

No EMC MTAP relative ratio was below 0.8 under either main pipeline. Here 0.8 is a descriptive comparison value, not a validated deletion threshold. The median across profiles of the standard all-reference MTAP locus-detail log2 ratio was −0.02006.

CDKN2A ranges were −0.13907 to +0.03985 under standard analysis and −0.18686 to +0.09189 under the author sensitivity. CDKN2B ranged from −0.40264 to +0.08585 and from −0.37223 to +0.06941, respectively. One EMC CDKN2B range was below a relative ratio of 0.8 in both pipelines. This three-probe observation does not establish adjacent MTAP deletion. Normal controls also showed locus and profile variation; high-noise reference profiles limit genotype interpretation.

## Interpretation

The observed MTAP signals do not supply a strong-loss lead in these ten profiles. Normal-reference copy neutrality, tumor purity, ploidy and the relation between probe intensities and genomic dosage were not independently established. A near-reference signal cannot exclude subclonal or purity-diluted loss, and neither a low signal nor a near-reference signal establishes methylthioadenosine accumulation, PRMT5 dependence or response to an inhibitor.

The original Foundation reported-call table also lacks a specimen-specific negative-callability manifest for these genes. Its absence of reported MTAP calls therefore cannot substitute for a negative genotype. Raw-array analysis addresses a different source question and should remain separate from the repaired Foundation sample identities.

Koelsche et al. already included ten EMC comparators in their 2019 Ewing-like-sarcoma methylation study and used the author conumee fork [1]. The 2021 sarcoma-classifier publication also reported a largely flat EMC copy-number landscape [2]. Exact profile overlap with the 2019 comparator set was not resolved, so this analysis is not claimed as an independent clinical cohort or a novel flat-genome discovery.

## Reproducibility

Complete [standard/reference sensitivities](../deep-analysis/results/EMC-all10-raw-MTAP-CDKN2A-CDKN2B-standard-and-reference-sensitivities-final.json), [pinned author BAF results](../deep-analysis/results/EMC-all10-raw-MTAP-CDKN2A-CDKN2B-pinned-author-BAF-final.json) and [2019 full-body prior-art check](../deep-analysis/results/EMC-exact2019-full-body-CNV-prior-art.json) retain per-profile loci, source hashes, annotations, bins and fit receipts. Both pipelines completed in [run 36929679794, job 110595657557](https://github.com/trimcrae/Rare-cancers/actions/runs/36929679794/job/110595657557). This note supports source qualification of the MTAP hypothesis.

1. Koelsche et al. DNA methylation profiling distinguishes Ewing-like sarcoma with EWSR1–NFATc2 fusion from Ewing sarcoma. Journal of Cancer Research and Clinical Oncology. 2019;145:1273–1281. [doi:10.1007/s00432-019-02895-2](https://doi.org/10.1007/s00432-019-02895-2).
2. Koelsche et al. Sarcoma classification by DNA methylation profiling. Nature Communications. 2021;12:498. [doi:10.1038/s41467-020-20603-4](https://doi.org/10.1038/s41467-020-20603-4).
