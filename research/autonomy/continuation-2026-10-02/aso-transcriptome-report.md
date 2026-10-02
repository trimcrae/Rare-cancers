---
id: "DOC-CONTINUATION-2026-10-02-ASO-TRANSCRIPTOME-REPORT"
title: "Reference-transcript coverage changes sequence-based ranking of NR4A3 fusion-junction ASO designs"
level: "L3"
kind: "manuscript"
status: "live"
canonical_for: []
purpose: "Working research draft: Reference-transcript coverage changes sequence-based ranking of NR4A3 fusion-junction ASO designs."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","external reviewers"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Reference-transcript coverage changes sequence-based ranking of NR4A3 fusion-junction ASO designs

## Abstract

We asked whether enlarging the normal-reference transcript corpus changes sequence
descriptors and rankings for a frozen catalogue of 215 junction-targeting antisense
oligonucleotide (ASO) designs. Targets and selection rules were held fixed. Adding
GENCODE release 50 to the archived 85-transcript reference increased the longest
complete-core perfect-match run for 212 designs and reduced minimum Hamming distance
for 213. Nineteen target sequences had full 16-base matches: 17 were hypothetical
reference joins and two were supported by deposited fusion sequences. Primary and
final choice sets changed for 42 and 41 of 43 junctions, respectively; only 15 and 23
became disjoint from their archived sets. One deposited-sequence example affected an
archived final selection. These results qualify sequence uniqueness and ranking
stability under reference expansion. They do not establish biological off-target
activity, clinical risk or improved efficacy. An independent whole-corpus exact-match
census confirmed all 440 design-stratum counts; nonzero extrema were not independently
recensused.

## Question and methods

The frozen September 30 full catalogue contains five 16-base target placements for
each of 43 NR4A3 fusion junctions, together with five separate annotation-error
controls.[1] Of the 215 target designs, 180 represent 36 hypothetical exact reference
joins. The remaining 35 designs span seven junctions: 25 designs from five
deposited-sequence matches, five from one coordinate-based reference reconstruction,
and five from one construct-description reconstruction. These evidence classes do
not denote numbers of patients or experimentally tested ASOs.
The 215 design records contain 201 distinct target 16-mers; the 19 exact-positive
targets are all distinct sequences.

We retained the archived normal-parent reference FASTA and added the GENCODE 50
ALL transcript FASTA.[2,3] The archived corpus contains 85 records, 354763 bases and
353488 unambiguous 16-base windows. The GENCODE scan reports 670670 records,
1480179158 bases and 1470018861 unambiguous windows; another 100286 windows contain
ambiguous bases. Its parent and other-gene partitions contain 409 and 670261 records,
respectively. The ALL resource includes chromosomes, scaffolds, assembly patches and
alternate loci. Counts therefore represent record-window occurrences, not independent
genes, people or tissues.

The targets, antisense reverse complements and ranking rule were unchanged. For each
design, the scanner records the longest perfect contiguous run containing the
complete six-base core and searches full-target Hamming distances through three
mismatches. For the proposed 5-LNA/6-DNA/5-LNA architecture, the core occupies target
positions 6–11 (one-based). The descriptor is evaluated over complete, unambiguous
16-base transcript-oriented windows. The union combines the archived reference with the expanded transcript
corpus. A censored search result above three is retained as a bound rather than
assigned a fictitious distance; archived exact distances supply an upper bound.
Primary selection minimizes the maximum complete-core run; the secondary rule
maximizes minimum full-target Hamming distance among primary ties. No expression
filter, new cutoff, new sequence optimization or clinical-risk threshold was applied.

Before scanning, the execution passed a synthetic independent-window oracle,
11 synthetic interval checks, and agreement with all 220 archived gap and bounded
Hamming values, including the controls.[4] A separate result audit recomputed the
215-design arithmetic and every union ranking from the saved rows, checked sequence
orientation, and found no disagreement. A separate Aho-Corasick implementation then
scanned all 670670 records and 1470018861 unambiguous windows, confirming all 440
design-stratum exact-match counts.[7] It directly verified 7339 original witnesses
and 128 independent exact-match coordinates, requiring coverage of all 880 original
metric groups with the first min(20,count) witnesses. These checks validate exact
counts and sampled coordinates/scores, not global nonzero Hamming minima or gap maxima.

## Results

All reported union minima were resolved, with coincident lower and upper bounds.
Nineteen designs had minimum Hamming distance zero, 165 had distance one and 31 had
distance two. Maximum complete-core runs increased for 212 of 215 designs; minimum
Hamming distances decreased for 213. None changed in the opposite direction,
consistent with expansion of the reference set.

The 19 full-length matches comprise 17 hypothetical-join designs and two
deposited-sequence designs. No full-length match was reported in either the
coordinate-based or construct-description reconstruction category. The two
deposited-sequence examples have different implications for previous selection:

| Design | Target, 5' to 3' | Matching reference gene | Reported exact record-window occurrences | Archived final selection |
|---|---|---|---:|---|
| TCF12_e5__NR4A3_e3:d9 | ATCTGATGGATATGCC | RBBP8-AS1 | 22 | Yes |
| EWSR1_e7__NR4A3_e2:d6 | AGCAGAAGCCCACTGC | ANKRD11P1 | 1 | No |

The corresponding antisense sequences are GGCATATCCATCAGAT and GCAGTGGGCTTCTGCT.
HGNC and NCBI support the gene identities.[5,6] Current Ensembl records annotate
RBBP8-AS1 transcript ENST00000795030.1 as lncRNA and ANKRD11P1 transcript
ENST00000378334.3 as processed_pseudogene.[8] Separate cDNA retrieval confirmed the
respective targets at transcript positions 346–361 and 3420–3435 (one-based).
Versions match the frozen witnesses; live annotation release equivalence was not
established. Expression, accessibility and susceptibility to ASO action remain unknown.
The 22 RBBP8-AS1 occurrences must not be interpreted as 22 distinct off-target genes.

For TCF12_e5__NR4A3_e3, archived primary donor offsets were [9,10] and the final
selection was [9]. Both expanded-corpus sets are [6]; the full match at d9 therefore
concerns a previously selected design. For EWSR1_e7__NR4A3_e2, archived primary offsets
were [7,8] and the final selection was [7]. Both expanded-corpus sets are
[7,8,9,10]. Its d6 full match concerns an evaluated design that had not been selected.

Across all 43 junctions, 42 primary choice sets and 41 final choice sets changed.
However, only 15 primary sets and 23 final sets were disjoint from their originals.
A changed set can retain an archived choice, acquire a tie or lose only some members;
set change is not equivalent to elimination of every previous selection. All five
deposited-sequence junctions had changed primary and final sets.

## Interpretation and limitations

Reference coverage materially affects these sequence descriptors and their fixed
ranking rule. Full-length matches qualify claims of uniqueness within the examined
annotated transcript corpus, including a deposited-sequence design that had been an
archived final choice. The result does not imply that the original calculations were
incorrect for their explicitly restricted reference set.

A mature-transcript annotation is not a measurement of healthy-tissue expression.
The scan does not comprehensively cover unspliced pre-mRNA, individual sequence
variation, tissue-specific exposure or the experimental accessibility of a binding
site. Exact complementarity does not establish RNase-H cleavage, binding strength,
delivery, toxicity or a therapeutic window. Conversely, noncoding-RNA or pseudogene
status does not by itself justify dismissing a sequence match. Ranking changes do
not demonstrate that replacement choices are clinically better.

The catalogue is dominated by hypothetical joins; its 35 other designs have varied
sequence-support evidence and are not 35 validated therapeutic candidates.
Independent verification now supports the full exact-match census and checked
witnesses. Nonzero Hamming minima and global gap maxima retain the original
oracle/baseline and direct-witness support, without a second exhaustive census.
No publication-readiness or clinical-validation conclusion follows from this report.

## Reproducibility and sources

The successful discovery execution was run37009409052, job110845272399, at code
revision b066a7e7bcffe4892c78f2d9462cc70b4d14945b.[4] Its runner SHA256 is
e611c035efc86aff077473741ff2224f3fb93bf0074673ceb856a288caaa92f8.
Independent verification passed in run37011070408, job110850663697, at
5e289f506e5eb5e934192b8c68d69870e67e4b50; its script SHA256 is
593c4efa4e2526fbc404ae7657348aeedf4ed07bdb24dde33f1410ff65a41731.[7]
The three input SHA256 values are:

- Catalogue TSV: f231499b036e4c6b79f729cee0a44a4c482ab6215167e61c2fc0c4a3ceed7799.
- Archived FASTA: 4cabff15767f8d7b38aefc75fa46233a954d13ac7802010b672aee3d9723c580.
- GENCODE gzip: 5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56.

1. [Frozen full catalogue](https://github.com/trimcrae/Rare-cancers/blob/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/all-designs.tsv).
2. [Archived normal-reference FASTA](https://github.com/trimcrae/Rare-cancers/blob/a916dab2979e27f930b417243f021b6c2b2ca371/research/release-candidates/PUB-ASO/2026-09-30-full-catalogue/results/normal-reference-transcripts.fasta).
3. [GENCODE 50 transcript FASTA](https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz) and [release resource descriptions](https://www.gencodegenes.org/human/).
4. [Executed workflow and result](https://github.com/trimcrae/Rare-cancers/actions/runs/37009409052/job/110845272399); [pinned analysis code](https://github.com/trimcrae/Rare-cancers/tree/b066a7e7bcffe4892c78f2d9462cc70b4d14945b/research/autonomy/continuation-2026-10-02).
5. [HGNC RBBP8-AS1 record](https://rest.genenames.org/fetch/symbol/RBBP8-AS1): HGNC:58091; ENSG00000266850.
6. [NCBI ANKRD11P1 record](https://www.ncbi.nlm.nih.gov/gene/100287912): HGNC:54737; ENSG00000234429. Gene-identity resources accessed October 2, 2026.
7. [Independent exact-census and witness verification](https://github.com/trimcrae/Rare-cancers/actions/runs/37011070408/job/110850663697).
8. Ensembl [RBBP8-AS1 transcript annotation](https://rest.ensembl.org/lookup/id/ENST00000795030?expand=1;content-type=application/json) and [cDNA](https://rest.ensembl.org/sequence/id/ENST00000795030?type=cdna;content-type=application/json); [ANKRD11P1 transcript annotation](https://rest.ensembl.org/lookup/id/ENST00000378334?expand=1;content-type=application/json) and [cDNA](https://rest.ensembl.org/sequence/id/ENST00000378334?type=cdna;content-type=application/json). Accessed October 2, 2026.
