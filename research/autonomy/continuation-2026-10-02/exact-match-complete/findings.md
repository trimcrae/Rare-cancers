---
id: DOC-ASO-COMPLETE-EXACT-ANNOTATION-FINDINGS-20261002
title: Complete exact-match witnesses and frozen transcript annotations
level: L3
kind: memo
status: live
purpose: Report uncapped exact-match coordinates and GENCODE50 transcript labels for the nineteen accepted positive designs.
scope: Complete134 design-record-window occurrences; source-specific annotation and saved-snapshot comparison, without activity or expression inference.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: "2026-10-02"
---

# Complete exact-match annotation

The bounded [cloud recovery](https://github.com/trimcrae/Rare-cancers/actions/runs/37021819798/job/110886519492) passed at code revision `909b1491786a7985e82a8880fe84a09cfb01c6da`. Thirteen synthetic tests passed before retrieval. The recovery captured all134 accepted exact design–record–window occurrences for19 designs in63 distinct versioned transcripts and12 versioned gene IDs. It agreed with every accepted per-design/per-stratum count and gene set, and reproduced all128 saved witness identities, coordinates and target sequences. This fills the earlier witness cap; it does not change the19-positive count, extrema or ranking results.

## Six recovered occurrences

Coordinates below are zero-based transcript-sense half-open intervals, not genomic coordinates.

| Design | Transcript | Interval | Gene | Frozen transcript biotype |
| --- | --- | --- | --- | --- |
| TCF12_e5__NR4A3_e3:d9 | ENST00000583086.1 | [111,127) | RBBP8-AS1 | lncRNA |
| TCF12_e5__NR4A3_e3:d9 | ENST00000795113.1 | [128,144) | RBBP8-AS1 | lncRNA |
| TFG_e2__NR4A3_e3:d6 | ENST00000529903.1 | [481,497) | ZNF215 | protein_coding |
| TFG_e2__NR4A3_e3:d7 | ENST00000529903.1 | [480,496) | ZNF215 | protein_coding |
| TFG_e2__NR4A3_e3:d8 | ENST00000529903.1 | [479,495) | ZNF215 | protein_coding |
| TFG_e2__NR4A3_e3:d9 | ENST00000529903.1 | [478,494) | ZNF215 | protein_coding |

The six rows represent three newly captured transcripts. Four overlapping TFG-design matches occur in the same ZNF215 transcript. All22 TCF12d9 occurrences have RBBP8-AS1 lncRNA annotations; the one deposited EWSR1d6 occurrence remains an ANKRD11P1 processed-pseudogene transcript. These are transcript-record counts, not independent genes, people or tissues.

## Complete biotype distribution

Biotypes were taken directly from field8 of the hash-pinned GENCODE50 transcript FASTA. The [official field-format receipt](header-format-source.json) identifies the defining release README. No gene-name inference or live label substitution was used.

| Transcript biotype | Design-record-window occurrences | Distinct transcripts |
| --- | ---: | ---: |
| protein_coding | 75 | 24 |
| lncRNA | 28 | 25 |
| nonsense_mediated_decay | 18 | 7 |
| protein_coding_CDS_not_defined | 10 | 4 |
| retained_intron | 2 | 2 |
| processed_pseudogene | 1 | 1 |
| Total | 134 | 63 |

The existing pinned Ensembl116 snapshot covers60 of these63 transcripts. For all60, transcript version, gene stable ID, biotype and transcript length agree with the frozen GENCODE50 headers. The three newly captured transcripts are absent from that saved snapshot; their Ensembl116 comparison is unavailable. Their GENCODE50 labels are complete. Matching this selected snapshot does not establish equivalence of entire annotation releases.

## Evidence and limits

The [complete table](results/complete-exact-hits.tsv), [new-six table](results/new-six-occurrences.tsv), [literal headers](results/gencode50-hit-headers.json), [annotation comparison](results/annotation-comparison.tsv) and [summary](results/summary.json) are retained with source and output SHA256s. The source gzip is183,554,921bytes, SHA256 `5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56`. The scan covers670,670 records and1,480,179,158 bases. Recovery took76.16seconds; the complete lane took173.06seconds and left92,214,603,776bytes free.

The downloaded11,039-byte workflow ZIP matched GitHub's SHA256 `386303dedb76adb21e29d4a40f3faf85eb7fbed093dd014fb858f0a4bba649f2`. Exact output bytes and execution/test logs are retained under `results/`. Root independently aggregated the tables and checked target sequences and interval widths; see `root-result-check.json`. The code received a focused independent static review before execution.

This is recovery of the previously accepted19-positive scope, not a fresh negative census of all215 targets. Earlier independent exact-census and union-extrema results remain separately preserved. A transcript biotype is an annotation, not tissue expression, abundance, accessibility, RNase-H cleavage, delivery, selectivity or clinical safety. Neither coding nor noncoding classification establishes biological importance of a match.
