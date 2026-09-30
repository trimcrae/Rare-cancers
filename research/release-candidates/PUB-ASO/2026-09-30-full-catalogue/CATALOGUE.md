---
id: DOC-PUB-ASO-SEQUENCE-CATALOGUE-20260930
title: ASO choices across catalogued EMC junctions
kind: memo
status: live
date: 2026-09-30
last_verified: 2026-09-30
purpose: Provide the tied best choices under an explicit normal-parent sequence comparison.
audience: [maintainers, external reviewers]
scope: Five fixed 16-base positions at each of 43 target junctions and one control.
---

# ASO sequence catalogue

All ASO sequences below run 5′ to 3′. Multiple sequences in a cell are tied;
their order is by binding position, not preference. **These are choices by a
declared sequence screen, not validated therapeutic leads.**

“Gap match” is the longest consecutive exact normal-RNA match covering the
proposed six-base DNA gap; shorter is preferred. Among tied positions, “nearest
RNA differences” is the minimum number of mismatches to any complete normal
16-base window; larger is preferred. The corpus contains 85 reference records
from seven parent genes, not the whole human transcriptome.

A gap-match value of zero means no complete exact six-base-gap match in this
corpus, not absence of other complementarity.

The [method and findings](README.md) explain the scope. The
[complete design table](results/all-designs.tsv) includes all five positions,
primary ties and competing alternatives. The
[junction table](results/junction-catalogue.tsv) gives exact reference context,
source accessions, coordinates and uncertainty. Exon labels below are shorthand
for those pinned sequences, not universal exon numbering.

## Junctions matching deposited fusion sequences

Five distinct junctions are supported by seven deposited records. This is not a patient count.

| Catalogue junction | Tied ASO choices, 5′–3′ | Gap match (bases) | Nearest RNA differences (bases) |
| --- | --- | ---: | ---: |
| TAF15 exon 6 / NR4A3 exon 3 | `GGGCATATCTTGTGTG` | 9 | 3 |
| TCF12 exon 5 / NR4A3 exon 3 | `GGCATATCCATCAGAT` | 8 | 5 |
| TFG exon 7 / NR4A3 exon 3 | `GGGCATATCTGAATAC`<br>`GGCATATCTGAATACT` | 11 | 2 |
| EWSR1 exon 7 / NR4A3 exon 2 | `CAGTGGGCTTCTGCTG` | 8 | 4 |
| EWSR1 exon 10 / NR4A3 cryptic exon | `GATGAGGGCCTAGATC` | 11 | 3 |

## Reference reconstruction from reported coordinates

The USZ20 model maps to this reference junction. Patient-specific variants or inserted bases remain unresolved.

| Catalogue junction | Tied ASO choices, 5′–3′ | Gap match (bases) | Nearest RNA differences (bases) |
| --- | --- | ---: | ---: |
| EWSR1 exon 12 / NR4A3 exon 3 | `GGCATATCATCAAACC`<br>`GCATATCATCAAACCA` | 11 | 4 |

## Reference reconstruction from a construct description

This corresponds to the Brenca T-N engineered construct description, not an exact deposited construct or patient RNA consensus.

| Catalogue junction | Tied ASO choices, 5′–3′ | Gap match (bases) | Nearest RNA differences (bases) |
| --- | --- | ---: | ---: |
| TAF15 exon 6 / NR4A3 cryptic exon | `GAGGGCCTTGTGTGTG` | 10 | 4 |

## Hypothetical exact reference joins

These exact sequence joins lack resolved source correspondence in the accepted evidence. Some partner or exon labels have appeared in papers; that alone does not establish the exact sequence.

| Catalogue junction | Tied ASO choices, 5′–3′ | Gap match (bases) | Nearest RNA differences (bases) |
| --- | --- | ---: | ---: |
| EWSR1 exon 1 / NR4A3 exon 3 | `GGGCATATCCGTGGAC` | 6 | 3 |
| EWSR1 exon 4 / NR4A3 exon 3 | `AGGGCATATCAGTGGG` | 7 | 3 |
| EWSR1 exon 7 / NR4A3 exon 3 | `GGCATATTCTGCTGCC` | 7 | 4 |
| EWSR1 exon 9 / NR4A3 exon 3 | `GGCATATCACCAGGCT` | 7 | 4 |
| EWSR1 exon 10 / NR4A3 exon 3 | `GGGCATATCTAGATCA`<br>`GGCATATCTAGATCAA` | 8 | 4 |
| EWSR1 exon 13 / NR4A3 exon 3 | `GGCATATCTCCACGGA`<br>`GCATATCTCCACGGAG` | 9 | 4 |
| EWSR1 exon 15 / NR4A3 exon 3 | `GGGCATATCCGGGGGC` | 6 | 3 |
| TAF15 exon 1 / NR4A3 exon 3 | `GGGCATATCCGACATG` | 7 | 4 |
| TAF15 exon 4 / NR4A3 exon 3 | `GGCATATCTGACTGAC` | 8 | 5 |
| TAF15 exon 8 / NR4A3 exon 3 | `AGGGCATATCACCAAA`<br>`GGGCATATCACCAAAA` | 7 | 4 |
| TAF15 exon 9 / NR4A3 exon 3 | `GGGCATATCAGCATCT` | 6 | 3 |
| TAF15 exon 11 / NR4A3 exon 3 | `GGCATATCATCAAACC`<br>`GCATATCATCAAACCA` | 11 | 4 |
| TAF15 exon 12 / NR4A3 exon 3 | `GGGCATATCTCGCCGC`<br>`GGCATATCTCGCCGCC` | 6 | 4 |
| TAF15 exon 14 / NR4A3 exon 3 | `GGGCATATCTCCTCCT` | 10 | 4 |
| TCF12 exon 3 / NR4A3 exon 3 | `GGGCATATCTGATCCA` | 11 | 5 |
| TCF12 exon 7 / NR4A3 exon 3 | `GGGCATATCAAGCGCT` | 8 | 5 |
| TCF12 exon 9 / NR4A3 exon 3 | `GGGCATATCTTGCATA` | 8 | 3 |
| TCF12 exon 11 / NR4A3 exon 3 | `GGCATATCTAGAATGC`<br>`GCATATCTAGAATGCT` | 8 | 4 |
| TCF12 exon 13 / NR4A3 exon 3 | `GGCATATCTGTGAGAG` | 8 | 4 |
| TCF12 exon 17 / NR4A3 exon 3 | `GGCATATCTCTATAAT` | 7 | 5 |
| TCF12 exon 19 / NR4A3 exon 3 | `GGGCATATCTCTGACT` | 8 | 4 |
| FUS exon 1 / NR4A3 exon 3 | `AGGGCATATCGTTTGA`<br>`GGGCATATCGTTTGAG` | 8 | 4 |
| FUS exon 3 / NR4A3 exon 3 | `CAGGGCATATTGTTCT`<br>`GCATATTGTTCTGGCT` | 9 | 4 |
| FUS exon 5 / NR4A3 exon 3 | `GGGCATATCTCCACCT` | 9 | 4 |
| FUS exon 7 / NR4A3 exon 3 | `AGGGCATATCACCAAA`<br>`GGGCATATCACCAAAT` | 7 | 4 |
| FUS exon 8 / NR4A3 exon 3 | `GGCATATCGGAGTCAT` | 0 | 5 |
| FUS exon 10 / NR4A3 exon 3 | `GGCATATCATCAAACC`<br>`GCATATCATCAAACCA` | 11 | 4 |
| FUS exon 11 / NR4A3 exon 3 | `GGGCATATCTCCTCGC`<br>`GGCATATCTCCTCGCC`<br>`GCATATCTCCTCGCCC` | 9 | 4 |
| FUS exon 13 / NR4A3 exon 3 | `GGCATATCCATGTGAG`<br>`GCATATCCATGTGAGA` | 7 | 4 |
| TFG exon 2 / NR4A3 exon 3 | `GGGCATATCTTCATCT` | 10 | 3 |
| TFG exon 3 / NR4A3 exon 3 | `GGGCATATCAAATAAT`<br>`GGCATATCAAATAATG`<br>`GCATATCAAATAATGT` | 9 | 4 |
| TFG exon 4 / NR4A3 exon 3 | `AGGGCATATCATTTTC` | 9 | 4 |
| TFG exon 5 / NR4A3 exon 3 | `GGCATATCTGAAACCT` | 8 | 3 |
| TFG exon 6 / NR4A3 exon 3 | `GCATATCTTCAATCTG` | 9 | 4 |
| PGR exon 2 / NR4A3 exon 2 | `GCAGTGGGCTCTTCCA`<br>`CAGTGGGCTCTTCCAT`<br>`AGTGGGCTCTTCCATT`<br>`GTGGGCTCTTCCATTG`<br>`TGGGCTCTTCCATTGC` | 9 | 4 |
| TAF15 exon 6 / NR4A3 exon 2 | `GTGGGCTCTTGTGTGT` | 8 | 3 |

## Annotation-error control

This historical label-transfer control is excluded from the 43 target-junction and 215-design summaries. It is not assigned to the USZ20 model.

| Catalogue junction | Tied ASO choices, 5′–3′ | Gap match (bases) | Nearest RNA differences (bases) |
| --- | --- | ---: | ---: |
| EWSR1 exon 13 / NR4A3 exon 2 | `GTGGGCTCTCCACGGA`<br>`TGGGCTCTCCACGGAG` | 9 | 4 |

