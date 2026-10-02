---
id: "DOC-CONTINUATION-2026-10-02-ASO-RESULT-INDEPENDENT-REVIEW"
title: "Independent ASO transcriptome-result review"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for Independent ASO transcriptome-result review."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Independent ASO transcriptome-result review

Date: 2026-10-02. Read-only scientific/result review, not the independent whole-corpus
sequence verification. No new cutoffs, fitting, designs or clinical validation.

## Evidence reviewed

- Executed result and rankings parsed directly from the GitHub job log:
  https://github.com/trimcrae/Rare-cancers/actions/runs/37009409052/job/110845272399
- Executing revision: b066a7e7bcffe4892c78f2d9462cc70b4d14945b.
- Frozen ASO catalogue/source revision:
  a916dab2979e27f930b417243f021b6c2b2ca371. This is the 215-design full catalogue,
  not the older 190-design preprint.
- Runner receipt: return code 0, 112.71063876152039 seconds;
  script SHA256 e611c035efc86aff077473741ff2224f3fb93bf0074673ceb856a288caaa92f8.
- GENCODE 50 source reported by the executed receipt:
  https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz
  183554921 compressed bytes;
  SHA256 5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56.
- The job reports synthetic oracle checks, 11 synthetic interval checks, and agreement
  with all 220 archived gap/bounded-Hamming baselines. Those executions were inspected
  as reported evidence; this review did not independently rerun them.
- The artifact-download tool returned artifact 11226449170, but retrieval of its
  signed ZIP URL returned HTTP403 locally. Complete result/design/ranking JSON was
  available in the job log. Raw transcript-position witness files were not inspected.

## Independently recomputed arithmetic

Using the parsed per-design rows and ranking records, excluding control=true rows:

| Quantity | Recomputed |
|---|---:|
| Targets | 215 |
| Junctions | 43 |
| Annotation-error controls, separate | 5 |
| Targets with larger maximum complete-core run | 212 |
| Targets with smaller minimum Hamming distance | 213 |
| Targets with full 16-base matches | 19 |
| Targets with unresolved/censored union minima | 0 |
| Junction primary choice sets changed | 42 |
| Junction final choice sets changed | 41 |

All 215 targets are 16 bases long. Every antisense sequence is the target's reverse
complement. No union maximum-run value decreased, and no union minimum Hamming distance
increased relative to the archive. Exactly the same 19 targets have union_gap=16 and
union_hamming=0. All 215 reported lower/upper Hamming bounds coincide with the reported
union minimum. The archive had no zero-Hamming target.

The corpus partitions sum correctly: 409 parent records plus 670261 other records =
670670 records; 1191711 parent windows plus 1468827150 other windows =
1470018861 unambiguous windows. The recorded sequence-base total is 1480179158;
100286 ambiguous windows are reported separately. These are scanner-reported coverage
counts, not independently recounted from the entire FASTA by this reviewer.

I recomputed every union primary set by minimizing union_gap within its junction,
and every final set by maximizing union_hamming among primary ties. All 43 sets agree
with the reported ranking arrays, with zero disagreements.

Changed sets do not necessarily displace every previous member:
- Only 15 primary sets are disjoint from the archived primary set.
- Only 23 final sets are disjoint from the archived final set.
- Thus "42/41 changed sets" is accurate; "42/41 previous choices eliminated" is not.
These are descriptive restatements of existing ranking arrays, not a new selection rule.

## Evidence-class denominators

| Catalogue evidence class | Designs | Junctions | Full matches |
|---|---:|---:|---:|
| hypothetical_exact_reference_join | 180 | 36 | 17 |
| deposited_sequence_match | 25 | 5 | 2 |
| coordinate_based_reference_reconstruction | 5 | 1 | 0 |
| construct_description_reference_reconstruction | 5 | 1 | 0 |
| Total, excluding controls | 215 | 43 | 19 |

Do not describe 19 observed patient fusion targets or 43 clinically established
junctions. Evidence class pertains to junction construction/source support; even a
deposited sequence does not supply measured efficacy, safety or normal-tissue expression.

## Two deposited-sequence examples

| Design | Target, 5' to 3' | ASO reverse complement, 5' to 3' | Reported matching gene | Exact record-window occurrences | Previously final |
|---|---|---|---|---:|---|
| TCF12_e5__NR4A3_e3:d9 | ATCTGATGGATATGCC | GGCATATCCATCAGAT | RBBP8-AS1 | 22 | Yes |
| EWSR1_e7__NR4A3_e2:d6 | AGCAGAAGCCCACTGC | GCAGTGGGCTTCTGCT | ANKRD11P1 | 1 | No |

For TCF12_e5__NR4A3_e3, archived primary donor offsets were [9,10] and final [9];
the expanded-corpus primary/final set is [6]. Thus the d9 match directly concerns an
archived final selection.

For EWSR1_e7__NR4A3_e2, archived primary offsets were [7,8] and final [7];
the expanded-corpus primary/final set is [7,8,9,10]. The d6 exact match concerns an
evaluated candidate that was not previously selected. These examples therefore have
different consequences for the archived ranking.

All five deposited-sequence junctions have changed primary and final sets, but those
changes include expanding or partially overlapping sets. The remaining three are
TAF15_e6__NR4A3_e3, TFG_e7__NR4A3_e3 and EWSR1_e10__NR4A3_intron2crypticExon.

## Independent gene-identity checks

HGNC's public API identifies RBBP8-AS1 as approved HGNC:58091, "RBBP8 antisense RNA 1",
locus type "RNA, long non-coding", Ensembl ENSG00000266850:
https://rest.genenames.org/fetch/symbol/RBBP8-AS1
Gene report:
https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:58091

NCBI Gene identifies ANKRD11P1 as "ANKRD11 pseudogene 1", Gene ID100287912,
HGNC:54737, Ensembl ENSG00000234429, gene type pseudo, RefSeq status INFERRED:
https://www.ncbi.nlm.nih.gov/gene/100287912

These authoritative records support the reported gene identities and make clear
that neither hit should be described as a matching protein-coding transcript merely
from its name. The gene checks do not independently verify the exact 16-mer positions
or every transcript record counted in the scanner.

GENCODE describes its ALL transcript FASTA as including reference chromosomes,
scaffolds, assembly patches and alternate loci:
https://www.gencodegenes.org/human/
Thus 22 record-window occurrences cannot be interpreted as 22 independent genes,
patients, tissues or expression observations. The archived FASTA likewise represents
normal-reference sequences, not normal-tissue expression measurements.

## Scientific interpretation

The expanded annotation corpus materially changes sequence-based specificity
descriptors and the fixed ranking rule. The 19 full-length matches demonstrate that
those target sequences are not unique within the reported annotated reference
transcript corpus, subject to independent confirmation of the source windows. This
is a concrete qualification of sequence uniqueness, including one previously final
design supported by a deposited fusion sequence.

It does not establish RNase-H cleavage, binding strength, cellular activity,
accessibility, tissue coexpression, delivery, clinical toxicity or a therapeutic
window. A lncRNA/pseudogene annotation is neither proof of a relevant off-target
effect nor a reason to dismiss exact complementarity without checking expression
and mechanism. Sequence scanning cannot resolve that question.

The comparison changes reference coverage while holding the targets and ranking
rule fixed. No new target optimization occurred. Hamming and complete-core-run
descriptors remain simplified sequence descriptors; ranking changes do not by
themselves show that new selections are clinically better.

## Outstanding verification and disposition

No arithmetic, evidence-class or ranking inconsistency was found in the reported
result. Treat the whole-corpus extrema and exact occurrence counts as scanner outputs
until the independent cloud verification finishes.

The independent pass should confirm source hashes, transcript IDs/versions and
orientations, literal 16-base witness windows, exact-match occurrence counts, and
the claimed extrema/bounds across all evaluated sequences. Checking only the two
highlighted genes would not establish completeness of the scan or absence of more
extreme matches for other designs. Preserve transcript/position evidence and the
record-versus-gene distinction in the resulting receipt.

The corpus covers annotated mature RNA and excludes a complete search of unspliced
pre-mRNA, all individual variants and expression-dependent exposure. Completion of
an independent scanner check would verify the computational result, not remove
these scientific limitations.

This review changed no source, code, ranking, manuscript or repository files.
Only this private review artifact was written. No UI, browser automation, large
corpus download, local build, paid API or model fitting was performed.

