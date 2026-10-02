---
id: DOC-ASO-EXPANDED-REFERENCE-CHOICES-20261002
title: Expanded-reference choices across 43 target junctions
kind: generated
status: generated
level: L3
generator: build-expanded-choices.ps1
purpose: Transfer every tied final choice from fixed per-design sequence descriptors into a readable resource.
scope: Saved-row ranking arithmetic and source-bound choices; no activity, expression or safety inference.
audience: [maintainers, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Expanded-reference choices across 43 target junctions

This table contains all 43 target junctions (215 design records). The annotation-error control and its five designs are excluded and reported separately.

Offsets count donor bases in the forward 16-base target. Antisense sequences run 5′–3′ and retain every final tie. Gap is maximum perfect contiguous match covering the complete six-base core (nucleotides); Hamming is minimum full-window mismatch count. Primary selection minimizes gap, then final selection maximizes Hamming among ties. These sequence choices are not validated therapeutic leads.

| Junction | Evidence class | Archived final offsets | Expanded final offsets | Changed | Disjoint | Expanded selected antisense (offset:sequence) | Gap (nt) | Hamming |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: |
| EWSR1_e1__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 6,10 | True | True | d6:CAGGGCATATCCGTGG<br>d10:GCATATCCGTGGACGC | 14 | 2 |
| EWSR1_e4__NR4A3_e3 | hypothetical_exact_reference_join | 7 | 6,7,8,9,10 | True | False | d6:CAGGGCATATCAGTGG<br>d7:AGGGCATATCAGTGGG<br>d8:GGGCATATCAGTGGGA<br>d9:GGCATATCAGTGGGAG<br>d10:GCATATCAGTGGGAGG | 14 | 1 |
| EWSR1_e7__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 8,9,10 | True | False | d8:GGGCATATTCTGCTGC<br>d9:GGCATATTCTGCTGCC<br>d10:GCATATTCTGCTGCCC | 14 | 1 |
| EWSR1_e9__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 6 | True | True | d6:CAGGGCATATCACCAG | 14 | 2 |
| EWSR1_e10__NR4A3_e3 | hypothetical_exact_reference_join | 8,9 | 6,9,10 | True | False | d6:CAGGGCATATCTAGAT<br>d9:GGCATATCTAGATCAA<br>d10:GCATATCTAGATCAAG | 14 | 1 |
| EWSR1_e12__NR4A3_e3 | coordinate_based_reference_reconstruction | 9,10 | 7,8,9,10 | True | False | d7:AGGGCATATCATCAAA<br>d8:GGGCATATCATCAAAC<br>d9:GGCATATCATCAAACC<br>d10:GCATATCATCAAACCA | 14 | 1 |
| EWSR1_e13__NR4A3_e3 | hypothetical_exact_reference_join | 9,10 | 8,9,10 | True | False | d8:GGGCATATCTCCACGG<br>d9:GGCATATCTCCACGGA<br>d10:GCATATCTCCACGGAG | 13 | 1 |
| EWSR1_e15__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 9,10 | True | True | d9:GGCATATCCGGGGGCG<br>d10:GCATATCCGGGGGCGG | 13 | 1 |
| TAF15_e1__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 9 | True | True | d9:GGCATATCCGACATGA | 13 | 2 |
| TAF15_e4__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 6,7,10 | True | True | d6:CAGGGCATATCTGACT<br>d7:AGGGCATATCTGACTG<br>d10:GCATATCTGACTGACT | 14 | 1 |
| TAF15_e6__NR4A3_e3 | deposited_sequence_match | 8 | 6 | True | True | d6:CAGGGCATATCTTGTG | 13 | 1 |
| TAF15_e8__NR4A3_e3 | hypothetical_exact_reference_join | 7,8 | 6,7,8,9,10 | True | False | d6:CAGGGCATATCACCAA<br>d7:AGGGCATATCACCAAA<br>d8:GGGCATATCACCAAAA<br>d9:GGCATATCACCAAAAT<br>d10:GCATATCACCAAAATT | 14 | 1 |
| TAF15_e9__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 10 | True | True | d10:GCATATCAGCATCTGT | 15 | 1 |
| TAF15_e11__NR4A3_e3 | hypothetical_exact_reference_join | 9,10 | 7,8,9,10 | True | False | d7:AGGGCATATCATCAAA<br>d8:GGGCATATCATCAAAC<br>d9:GGCATATCATCAAACC<br>d10:GCATATCATCAAACCA | 14 | 1 |
| TAF15_e12__NR4A3_e3 | hypothetical_exact_reference_join | 8,9 | 6 | True | True | d6:CAGGGCATATCTCGCC | 13 | 2 |
| TAF15_e14__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 6 | True | True | d6:CAGGGCATATCTCCTC | 14 | 1 |
| TCF12_e3__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 10 | True | True | d10:GCATATCTGATCCACT | 13 | 2 |
| TCF12_e5__NR4A3_e3 | deposited_sequence_match | 9 | 6 | True | True | d6:CAGGGCATATCCATCA | 13 | 1 |
| TCF12_e7__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 7,8,9,10 | True | False | d7:AGGGCATATCAAGCGC<br>d8:GGGCATATCAAGCGCT<br>d9:GGCATATCAAGCGCTG<br>d10:GCATATCAAGCGCTGC | 13 | 2 |
| TCF12_e9__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 6,7 | True | True | d6:CAGGGCATATCTTGCA<br>d7:AGGGCATATCTTGCAT | 13 | 2 |
| TCF12_e11__NR4A3_e3 | hypothetical_exact_reference_join | 9,10 | 8 | True | True | d8:GGGCATATCTAGAATG | 13 | 2 |
| TCF12_e13__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 6,7,10 | True | True | d6:CAGGGCATATCTGTGA<br>d7:AGGGCATATCTGTGAG<br>d10:GCATATCTGTGAGAGG | 14 | 1 |
| TCF12_e17__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 7 | True | True | d7:AGGGCATATCTCTATA | 13 | 2 |
| TCF12_e19__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 10 | True | True | d10:GCATATCTCTGACTTG | 14 | 2 |
| FUS_e1__NR4A3_e3 | hypothetical_exact_reference_join | 7,8 | 9,10 | True | True | d9:GGCATATCGTTTGAGG<br>d10:GCATATCGTTTGAGGC | 12 | 1 |
| FUS_e3__NR4A3_e3 | hypothetical_exact_reference_join | 6,10 | 6,10 | False | False | d6:CAGGGCATATTGTTCT<br>d10:GCATATTGTTCTGGCT | 14 | 1 |
| FUS_e5__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 10 | True | True | d10:GCATATCTCCACCTCC | 14 | 2 |
| FUS_e7__NR4A3_e3 | hypothetical_exact_reference_join | 7,8 | 8 | True | False | d8:GGGCATATCACCAAAT | 13 | 1 |
| FUS_e8__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 9 | False | False | d9:GGCATATCGGAGTCAT | 12 | 2 |
| FUS_e10__NR4A3_e3 | hypothetical_exact_reference_join | 9,10 | 7,8,9,10 | True | False | d7:AGGGCATATCATCAAA<br>d8:GGGCATATCATCAAAC<br>d9:GGCATATCATCAAACC<br>d10:GCATATCATCAAACCA | 14 | 1 |
| FUS_e11__NR4A3_e3 | hypothetical_exact_reference_join | 8,9,10 | 10 | True | False | d10:GCATATCTCCTCGCCC | 13 | 2 |
| FUS_e13__NR4A3_e3 | hypothetical_exact_reference_join | 9,10 | 8,9 | True | False | d8:GGGCATATCCATGTGA<br>d9:GGCATATCCATGTGAG | 14 | 2 |
| TFG_e2__NR4A3_e3 | hypothetical_exact_reference_join | 8 | 10 | True | True | d10:GCATATCTTCATCTTT | 15 | 1 |
| TFG_e3__NR4A3_e3 | hypothetical_exact_reference_join | 8,9,10 | 6 | True | True | d6:CAGGGCATATCAAATA | 14 | 1 |
| TFG_e4__NR4A3_e3 | hypothetical_exact_reference_join | 7 | 6,7,10 | True | False | d6:CAGGGCATATCATTTT<br>d7:AGGGCATATCATTTTC<br>d10:GCATATCATTTTCAGG | 14 | 1 |
| TFG_e5__NR4A3_e3 | hypothetical_exact_reference_join | 9 | 8,9 | True | False | d8:GGGCATATCTGAAACC<br>d9:GGCATATCTGAAACCT | 14 | 1 |
| TFG_e6__NR4A3_e3 | hypothetical_exact_reference_join | 10 | 8 | True | True | d8:GGGCATATCTTCAATC | 13 | 1 |
| TFG_e7__NR4A3_e3 | deposited_sequence_match | 8,9 | 7,8 | True | False | d7:AGGGCATATCTGAATA<br>d8:GGGCATATCTGAATAC | 14 | 1 |
| EWSR1_e7__NR4A3_e2 | deposited_sequence_match | 7 | 7,8,9,10 | True | False | d7:CAGTGGGCTTCTGCTG<br>d8:AGTGGGCTTCTGCTGC<br>d9:GTGGGCTTCTGCTGCC<br>d10:TGGGCTTCTGCTGCCC | 15 | 1 |
| PGR_e2__NR4A3_e2 | hypothetical_exact_reference_join | 6,7,8,9,10 | 6,7,8 | True | False | d6:GCAGTGGGCTCTTCCA<br>d7:CAGTGGGCTCTTCCAT<br>d8:AGTGGGCTCTTCCATT | 14 | 1 |
| TAF15_e6__NR4A3_e2 | hypothetical_exact_reference_join | 9 | 6,7,8,9,10 | True | False | d6:GCAGTGGGCTCTTGTG<br>d7:CAGTGGGCTCTTGTGT<br>d8:AGTGGGCTCTTGTGTG<br>d9:GTGGGCTCTTGTGTGT<br>d10:TGGGCTCTTGTGTGTG | 14 | 1 |
| TAF15_e6__NR4A3_intron2crypticExon | construct_description_reference_reconstruction | 10 | 6,7 | True | True | d6:TGATGAGGGCCTTGTG<br>d7:GATGAGGGCCTTGTGT | 14 | 1 |
| EWSR1_e10__NR4A3_intron2crypticExon | deposited_sequence_match | 7 | 6 | True | True | d6:TGATGAGGGCCTAGAT | 14 | 2 |

Source: https://raw.githubusercontent.com/trimcrae/Rare-cancers/dece8fd886f554641a6c32276b00731af0d05438/research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json

Source SHA256: `ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec`. All ranking sets and saved changed flags were recomputed from the fixed design rows before writing this table; archived row choice flags were also checked. No transcriptome search was rerun.
