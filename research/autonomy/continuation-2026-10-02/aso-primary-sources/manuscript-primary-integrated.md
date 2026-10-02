---
id: DOC-ASO-PRIMARY-SOURCE-SNAPSHOT-20261002
title: NR4A3 fusion-junction gapmer designs and sensitivity to reference-transcript coverage
kind: manuscript
status: live
level: L3
purpose: Integrate targeted verified primary references into the consolidated EMC catalogue and reference-expansion draft.
scope: >
  Working integration draft based on frozen catalogue and continuation evidence.
  Source inspection and committed execution receipts support the stated sequence
  computations. This draft has not received the required independent ultra review,
  outgoing-package validation or publication clearance. Complete exact-witness coverage and frozen release-specific transcript labels
  were recovered in a separate bounded execution.
audience: [maintainers, collaborators, external reviewers]
date: "2026-10-02"
last_verified: "unverified"
---

# NR4A3 fusion-junction gapmer designs and sensitivity to reference-transcript coverage

**Working consolidated manuscript draft — integration review required.**

This working draft is not the current accepted concise outgoing package. That package is the [September 30 letter candidate](https://github.com/trimcrae/Rare-cancers/tree/da7fab35440a74ea1c46c4ab197cead793333711/research/release-candidates/PUB-ASO/2026-09-30-letter-package); references here to the older 190-design journal article are historical comparisons. Neither preparing this copy nor adding citations modifies or revalidates the accepted brief.

## Abstract

Fusion-junction antisense oligonucleotides offer a sequence-defined approach to studying *NR4A3*-rearranged extraskeletal myxoid chondrosarcoma (EMC), but the presence of a fusion does not establish that a short junction-spanning target is absent from normal-reference RNA. We assembled a source-qualified catalogue of 215 design records spanning 43 junctions, representing 201 distinct target 16-mers, with five annotation-error controls analyzed separately. Twenty-five designs match deposited fusion sequences, ten reconstruct reference junctions from coordinates or a construct description, and 180 are hypothetical reference joins. Holding targets and a two-stage ranking rule fixed, we expanded an archived 85-record normal-parent corpus with GENCODE release 50 transcripts. Maximum contiguous perfect matches covering the complete six-base gap increased for 212 designs, and minimum full-target Hamming distances decreased for 213. Nineteen distinct targets matched complete normal-reference 16-base windows: 17 hypothetical joins and two deposited-sequence designs. One of the latter had been an archived final choice. Primary and final choice sets changed at 42 and 41 junctions; 15 and 23, respectively, became disjoint from the archived sets. Independent implementations confirmed the complete exact-match census and both union descriptors for all 220 designs, including controls. The contribution is an inspectable EMC sequence catalogue and a demonstration that reference coverage changes its computational choices. The proposed 5-LNA/6-DNA/5-LNA architecture, sequence ordering and experimental selectivity criterion remain unvalidated. No oligonucleotide was synthesized, and no expression, cleavage, efficacy or safety was measured.

## Introduction

EMC is characterized by rearrangements involving *NR4A3*. Primary studies identified *EWSR1*–*NR4A3* fusion transcripts and compared tumors and engineered models bearing *EWSR1*–*NR4A3* or *TAF15*–*NR4A3*.[10,11] The earlier computational study developed junction-spanning gapmer designs and a proposed experiment to test fusion knockdown alongside wild-type transcripts.[1] Fusion-junction antisense oligonucleotides have experimental precedent in *BCR–ABL* leukemia, and reference-sequence off-target annotation is implemented in established design software such as PFRED.[2,13] The present contribution is a source-qualified EMC catalogue and reference comparison, rather than a new molecular mechanism or search algorithm.

A rearrangement can create a novel RNA junction without making every short sequence across that junction unique. A 16-base target can also occur in an unrelated annotated transcript. Its component parent-gene sequences can support partial contiguous pairing through the proposed DNA gap even when a full-length exact match is absent. Accordingly, the existence of a junction-spanning design, the absence of a full match in a restricted reference set, and biological selectivity are different propositions.

The earlier article examined 190 designs at 38 junctions and several separately scoped parent, precursor, transcriptome and genome searches.[1] The accepted catalogue subsequently expanded source coverage and distinguished deposited sequences, reference reconstructions and hypothetical joins.[3] Here we consolidate that catalogue with a fixed-target reference-expansion analysis. We ask whether adding a broad annotated transcript resource changes the two sequence descriptors and the choices obtained from their prespecified ordering. This comparison does not replace the earlier precursor or genome searches, nor does it test whether the revised choices perform better in cells.

## Materials and methods

### Catalogue, sequence evidence and proposed chemistry

The frozen catalogue contains five 16-base placements at each of 43 target junctions, plus five designs for one historical annotation-error control. The target set comprises 25 designs at five junctions matching deposited fusion sequences, five designs at one coordinate-based reference reconstruction, five at one construct-description reconstruction, and 180 at 36 hypothetical exact reference joins.[3] These categories describe sequence evidence, not independent patients, experimental ASOs or confirmed therapeutic targets. The 215 target records contain 201 distinct target sequences. Duplicate sequences retain their separate catalogue identities.

Each forward target uses the DNA alphabet, with T representing U; its antisense sequence is its reverse complement. Five proposed LNA residues flank each side of a six-residue DNA gap. In the target orientation the complete gap occupies positions 6–11, one-based. This fixed 5-LNA/6-DNA/5-LNA architecture permits five breakpoint-spanning placements; its chemistry and six-base gap have not been optimized or experimentally validated here. Gapmer studies with other configurations establish the use of a central DNA region and modified flanks for RNase-H-dependent targeting, but do not validate this particular 5-LNA/6-DNA/5-LNA proposal.[14,15] Exact reference sequence and coordinate conventions, rather than exon labels alone, define each catalogue junction.

### Reference corpora and sequence descriptors

The archived normal-parent corpus contains 85 records representing 78 distinct sequences from seven genes, with 354,763 bases and 353,488 complete unambiguous 16-base windows.[3] The expanded comparison retains this corpus and adds the GENCODE v50 ALL transcript FASTA.[4] The latter contains 670,670 scanned records, 1,480,179,158 bases and 1,470,018,861 unambiguous 16-base windows; 100,286 additional windows contain ambiguous bases. The resource includes alternate loci and assembly-associated records. Counts are transcript-record windows, including aliases, and do not measure independent genes, people or tissues.

For each design, the first descriptor is the maximum length of a contiguous exact match that includes the entire six-base core within an eligible full 16-base transcript-oriented window. A zero value means no perfect complete-core match, not absence of complementarity. The second is the minimum Hamming distance across eligible full windows. The discovery search enumerated distances through three substitutions. Values beyond its search radius would remain bounded rather than be assigned an invented exact value; archived exact distances provide upper bounds. All observed union minima were resolved at distances zero to two.[5]

Primary choice sets minimize the maximum complete-core run within each junction. Among primary ties, final choice sets maximize the minimum full-window Hamming distance; remaining ties are preserved. Targets and ordering were held fixed. No expression filter, biological cutoff, weighted score or newly optimized sequence was introduced. A set was counted as changed if any member differed; disjointness was assessed separately because a changed set can retain previous choices.

### Computational verification

Discovery included an independent literal-window synthetic oracle, interval checks and agreement with all 220 archived gap and bounded Hamming comparisons. A separate Aho–Corasick exact-pattern implementation confirmed all 440 design-by-GENCODE-stratum exact-occurrence counts and directly checked the saved original witnesses.[5,6]

A subsequent implementation used literal patterns to challenge all 220 reported union extrema against both pinned corpora. It enumerated every Hamming pattern through each claimed radius, requiring attainment and excluding smaller distances. For a nonzero gap maximum g it required attainment at g and excluded all eligible complete-core intervals at g+1; the zero case excluded any complete-core match, and 16 is the structural upper bound. Both corpora retained the requirement for a complete unambiguous aligned 16-base window. The committed execution receipt records passing certificates for all 220 Hamming minima and complete-core maxima.[7] This implementation differs from the discovery engine's two-bit representation and hash lookup, while sharing Hamming-neighborhood mathematics. It does not independently certify each stratum's nonzero extrema or occurrence counts.

### Annotation and interpretation

A separate literal exact-target recovery captured all 134 accepted design–record–window occurrences across 63 versioned transcripts and 12 gene IDs, reproducing all 128 previously saved witnesses and every accepted per-design count.[9] Thirteen synthetic tests preceded the recovery. Transcript biotypes were read directly from the pinned GENCODE v50 FASTA headers. The six additional occurrences involve two RBBP8-AS1 lncRNA transcripts and four overlapping placements in one protein-coding ZNF215 transcript. For the 60 transcripts covered by the earlier Ensembl116 snapshot, version, gene stable ID, biotype and length agree; the other three have no comparison in that saved snapshot.[8,9] This selected-set agreement does not establish whole-release equivalence.

## Results

### Corpus expansion changes sequence descriptors and choices

Maximum complete-core runs increased for 212 of 215 designs, and minimum Hamming distances decreased for 213. No change was in the opposite direction, as expected when reference windows are added. Nineteen designs had union minimum Hamming distance zero, 165 had distance one, and 31 had distance two. These are design-record counts rather than counts of distinct patients or junctions.

Primary choice sets changed for 42 of 43 junctions and final sets for 41. Only 15 primary and 23 final sets were disjoint from their archived counterparts. Thus the set-change totals do not mean that every archived choice was eliminated at those junctions. All five deposited-sequence junctions had changed primary and final sets. These changes establish sensitivity of the declared sequence ordering, not improved efficacy or selectivity of replacement choices.

The [expanded-reference choice table](https://github.com/trimcrae/Rare-cancers/blob/4818db097f97ff8f862cd02bb9a2ddcf6c76cb71/research/autonomy/continuation-2026-10-02/aso-consolidation/expanded-reference-choices.md) reports every final tied antisense sequence for all 43 target junctions, with evidence class, archived and expanded offsets, changed/disjoint flags and both sequence descriptors. Its [TSV](https://github.com/trimcrae/Rare-cancers/blob/4818db097f97ff8f862cd02bb9a2ddcf6c76cb71/research/autonomy/continuation-2026-10-02/aso-consolidation/expanded-reference-choices.tsv) is the machine-readable resource. The five annotation-error control designs are represented in a [separate control-junction table](https://github.com/trimcrae/Rare-cancers/blob/4818db097f97ff8f862cd02bb9a2ddcf6c76cb71/research/autonomy/continuation-2026-10-02/aso-consolidation/annotation-control-choices.md), outside the target summaries. All transferred ranking sets were recomputed from the fixed per-design rows and checked against the saved results; this table generation does not rerun a transcriptome search.

### Exact matches include a previously selected deposited-sequence design

The 19 exact-positive target 16-mers are distinct: 17 arise from hypothetical joins and two from deposited-sequence matches. None belongs to either reference-reconstruction category. The two deposited examples differ in their relationship to prior selection.

| Catalogue design | Target 5′–3′ | Antisense 5′–3′ | Reference gene | Exact record-window occurrences | Archived final choice? |
| --- | --- | --- | --- | ---: | --- |
| TCF12_e5__NR4A3_e3:d9 | ATCTGATGGATATGCC | GGCATATCCATCAGAT | RBBP8-AS1 | 22 | Yes |
| EWSR1_e7__NR4A3_e2:d6 | AGCAGAAGCCCACTGC | GCAGTGGGCTTCTGCT | ANKRD11P1 | 1 | No |

For the *TCF12* junction, archived primary offsets were [9,10] and the final set was [9]; both expanded sets are [6]. For the *EWSR1* junction, archived primary offsets were [7,8] and the final set was [7]; both expanded sets are [7,8,9,10]. The exact match at its d6 design therefore concerns an evaluated design that had not been selected.

All 22 *RBBP8-AS1* witnesses have frozen GENCODE50 lncRNA annotations; the *ANKRD11P1* witness is annotated processed_pseudogene.[9] Neither these annotations nor the exact matches establish healthy-tissue expression, accessibility or RNase-H-mediated cleavage. Twenty-two occurrences are not 22 genes. Conversely, noncoding or pseudogene annotation does not justify dismissing a sequence match.

### Reinterpretation of the originally highlighted reagents

The historical journal-article version highlighted antisense sequences GGGCATATCATCAAAC and GGGCATATCTTGTGTG using its earlier six-parent comparison.[1] They remain traceable research designs, but the original short parent-match values must not be presented as their maxima in the expanded reference corpus.

| Design highlighted in the earlier article | Accepted evidence class | Archived 85-record gap maximum | Expanded union gap maximum | Archived → union minimum Hamming distance |
| --- | --- | ---: | ---: | --- |
| EWSR1_e12__NR4A3_e3:d8; GGGCATATCATCAAAC | Coordinate-based reference reconstruction | 11 | 14 | 3 → 1 |
| TAF15_e6__NR4A3_e3:d8; GGGCATATCTTGTGTG | Deposited-sequence match | 9 | 14 | 3 → 2 |

For the *EWSR1* junction the archived final offsets [9,10] become [7,8,9,10]; its originally highlighted d8 design is included in the expanded tie but was not a final choice in the September 30 catalogue. For the *TAF15* junction, the archived final offset [8] becomes [6]. These are comparisons under the catalogue's ordering, which is distinct from the older article's prevalence and gap-margin rationale. The new result does not identify a biologically validated replacement reagent.

### Test-article identity remains upstream of experimental interpretation

Bangerter and colleagues reported the patient-derived USZ20-EMC1 and USZ22-EMC2 models, with RNA-level confirmation of *EWSR1*–*NR4A3* and *TAF15*–*NR4A3*, respectively; their Figure 4 reports exon labels.[12] This establishes reported model fusions, not an independently recovered nucleotide consensus for the test articles used here. The accepted catalogue maps USZ20 to a coordinate-based reference reconstruction, not to a patient RNA consensus, while USZ22 remains unresolved.[3] The historical EWSR1 exon-13/NR4A3 exon-2 label-transfer design is retained only as an annotation-error control and is excluded from target summaries. Exon labels or protein-fusion plausibility do not establish a nucleotide-resolved junction. Candidate design-to-model correspondence therefore requires the actual test article's junction sequence before synthesis or interpretation. Brenca and colleagues describe engineered E-N, T-N and T-N* cDNAs by exon span, including a cryptic-intron sequence in T-N.[11] Reconstructing a reference sequence from such a description does not itself establish the literal sequence of a deposited construct or an endogenous test article.

## Discussion

The original study's useful contribution was to connect EMC fusion-junction design, normal-parent complementarity and a falsifiable laboratory comparison. The consolidated catalogue strengthens that connection by retaining sequence-evidence classes, exact reference identities and tied computational choices. Reference expansion shows why this record must remain conditional on its search corpus: a short target can have an exact match in unrelated annotated RNA, and apparently preferable placements can change when additional windows are included.

These findings do not demonstrate that earlier calculations were wrong for their restricted inputs. The older 190-design analyses, their precursor and genomic searches, null comparisons and modeled thermodynamic separations retain their original denominators and assumptions in the archived work.[1] They are not relabeled as results for the 215-design catalogue or combined with the present counts. In particular, the eight full-duplex sites reported by an earlier separately filtered analysis and the present 19 exact-positive targets concern different instruments and scopes; neither is a simple updated count of the other.

Experimental studies show why sequence searches require cellular follow-up: Yoshida and colleagues observed complementarity-dependent expression changes with tested LNA gapmers in human cells, whereas Lima and colleagues found that RNA accessibility and RNase H1 conditions influenced whether off-target binding produced cleavage in a SOD1 minigene system.[14,15] These different chemistries and models do not supply a universal match-length or mismatch cutoff for the proposed EMC designs. A future experiment would compare fusion-positive and matched fusion-negative material, confirm the target sequence, measure a fusion dose–response alongside wild-type *NR4A3*, and assess additional candidate-matched transcripts. The original proposed ratio of wild-type *NR4A3* to fusion half-maximal knockdown concentrations remains an acceptor-specific experimental endpoint, not a comprehensive safety measure. Its proposed cutoff of 5 and variance/power assumptions were adopted conventions rather than observed biology.[1] The new sequence results supply additional hypotheses and reference transcripts to examine; they do not validate that cutoff or permit inference of activity from match length alone. Previously screened scramble controls retain their historical scope and have not been certified by this 220-design expansion.

The catalogue is dominated by hypothetical joins. The 35 other designs also differ in their evidence: a deposited sequence, a reference reconstruction and a validated active oligonucleotide are not interchangeable. Adjacent placements overlap, identical 16-mers recur under different catalogue labels, and transcript aliases recur in the reference corpus. No confidence interval treating the 215 records as independent biological samples is intended. The computational ordering and fixed chemistry were not trained against cleavage or toxicity measurements.

GENCODE transcript annotation does not measure expression in healthy tissues or tumors. It is not comprehensive coverage of unspliced RNA, individual variants, uptake, subcellular localization or binding-site accessibility. Independent certification supports the declared union extrema and exact-match counts, not a therapeutic window. Delivery, dose-dependent activity and unintended effects remain experimental questions. Every listed sequence is a research design; none is proposed for administration to a person or animal.

## Data availability and draft status

The earlier article and its historical analyses cite the frozen archive DOI 10.5281/zenodo.22229096 [1]. That archive is not asserted to contain the September 30 catalogue or October 2 continuation. The new catalogue is pinned at Git revision `a916dab2979e27f930b417243f021b6c2b2ca371`, and this draft uses continuation evidence at `dece8fd886f554641a6c32276b00731af0d05438`.[3,5] Source FASTA and catalogue digests, result files, witnesses and verification receipts remain separately identifiable. The accepted files and existing public records have not been modified by preparing this draft.

The author has recorded: “This research received no funding” and “The author declares no competing interests.” These [standing declarations](https://github.com/trimcrae/Rare-cancers/blob/4818db097f97ff8f862cd02bb9a2ddcf6c76cb71/research/autonomy/author-declarations.json) are retained. The revised AI-use disclosure must account for both the prior Claude-assisted work and this Codex-assisted continuation without implying that an unperformed reference audit occurred. The required independent ultra-reasoning review of the consolidated manuscript has not been completed or runtime-verified here; computational execution receipts are not that review. This draft carries no submission clearance.

## Sources

References 2 and 10–15 are primary research publications. References 1 and 3–9 identify historical project records, computational artifacts, execution receipts or the reference resource; they are not external biological validation.

1. [Historical journal-article source at the consolidation pin](https://github.com/trimcrae/Rare-cancers/blob/dece8fd886f554641a6c32276b00731af0d05438/research/manuscripts/aso/fusion-junction-aso-journal-article.md), including its existing primary-literature citations and [frozen earlier archive](https://doi.org/10.5281/zenodo.22229096). This is not the current accepted concise package. Historical claims are not freshly re-audited in this drafting task.
2. Sciabola S, Xi H, Cruz D, et al. PFRED: A computational platform for siRNA and antisense oligonucleotides design. *PLOS ONE*. 2021;16(1):e0238753. [Primary methods study](https://doi.org/10.1371/journal.pone.0238753).
3. [Frozen catalogue methods and evidence classes](https://github.com/trimcrae/Rare-cancers/blob/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/README.md); [catalogue](https://github.com/trimcrae/Rare-cancers/blob/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/CATALOGUE.md).
4. [GENCODE release 50 official resource description](https://www.gencodegenes.org/human/release_50.html) and [GENCODE v50 ALL transcript FASTA](https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz). Input SHA256: `5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56`.
5. [Pinned continuation report](https://github.com/trimcrae/Rare-cancers/blob/dece8fd886f554641a6c32276b00731af0d05438/research/autonomy/continuation-2026-10-02/aso-transcriptome-report.md); [full per-design result](https://github.com/trimcrae/Rare-cancers/blob/dece8fd886f554641a6c32276b00731af0d05438/research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json), SHA256 `ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec`.
6. [Independent exact-census execution](https://github.com/trimcrae/Rare-cancers/actions/runs/37011070408/job/110850663697).
7. [Committed independent union-extrema receipt](https://github.com/trimcrae/Rare-cancers/blob/dece8fd886f554641a6c32276b00731af0d05438/research/autonomy/continuation-2026-10-02/extrema-confirmation/results/extrema-confirmation.json); [execution](https://github.com/trimcrae/Rare-cancers/actions/runs/37017553101/job/110872050719), code revision `e4e41e8cc93e66c2a576ec8a6f6f4acba5c5d496`.
8. [Saved-witness annotation and response provenance](https://github.com/trimcrae/Rare-cancers/blob/dece8fd886f554641a6c32276b00731af0d05438/research/autonomy/continuation-2026-10-02/exact-match-annotation/findings.md).

9. [Complete exact-hit coordinates and frozen transcript labels](https://github.com/trimcrae/Rare-cancers/blob/4818db097f97ff8f862cd02bb9a2ddcf6c76cb71/research/autonomy/continuation-2026-10-02/exact-match-complete/findings.md); [successful recovery](https://github.com/trimcrae/Rare-cancers/actions/runs/37021819798/job/110886519492), code revision `909b1491786a7985e82a8880fe84a09cfb01c6da`.

10. Labelle Y, Zucman J, Stenman G, et al. Oncogenic conversion of a novel orphan nuclear receptor by chromosome translocation. *Human Molecular Genetics*. 1995;4(12). [Primary fusion report](https://doi.org/10.1093/hmg/4.12.2219); [PubMed record](https://pubmed.ncbi.nlm.nih.gov/8634690/). Metadata and abstract were verified; publisher full text was not accessible in this task.
11. Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. *Journal of Pathology*. 2019;249(1). [Primary functional study](https://doi.org/10.1002/path.5284); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6766969/).
12. Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. *Human Cell*. 2023;36(1); published online November 1, 2022. [Primary model report](https://doi.org/10.1007/s13577-022-00818-x); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/).
13. Skórski T, Szczylik C, Malaguarnera L, Calabretta B. Gene-targeted specific inhibition of chronic myeloid leukemia cell growth by BCR-ABL antisense oligodeoxynucleotides. *Folia Histochemica et Cytobiologica*. 1991;29(3):85–89. [Primary report, PubMed](https://pubmed.ncbi.nlm.nih.gov/1794439/). Precedent is supported at abstract level; full text was not obtained.
14. Yoshida T, Naito Y, Yasuhara H, et al. Evaluation of off-target effects of gapmer antisense oligonucleotides using human cells. *Genes to Cells*. 2019;24(12). [Primary cellular study](https://doi.org/10.1111/gtc.12730); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6915909/).
15. Lima WF, Vickers TA, Nichols J, Li C, Crooke ST. Defining the factors that contribute to on-target specificity of antisense oligonucleotides. *PLOS ONE*. 2014;9(7):e101752. [Primary mechanistic study](https://doi.org/10.1371/journal.pone.0101752); [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4114480/).
