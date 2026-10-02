---
id: DOC-ASO-ANNOTATION-CONTROL-CHOICES-20261002
title: Separate annotation-error control choices
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

# Separate annotation-error control choices

This one historical annotation-error control junction contains five designs and is excluded from the 43 target-junction and 215 target-design summaries. It is not assigned to the USZ20 model.

Offsets count donor bases in the forward 16-base target. Antisense sequences run 5′–3′ and retain every final tie. Gap is maximum perfect contiguous match covering the complete six-base core (nucleotides); Hamming is minimum full-window mismatch count. Primary selection minimizes gap, then final selection maximizes Hamming among ties. These sequence choices are not validated therapeutic leads.

| Junction | Evidence class | Archived final offsets | Expanded final offsets | Changed | Disjoint | Expanded selected antisense (offset:sequence) | Gap (nt) | Hamming |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: |
| EWSR1_e13__NR4A3_e2 | annotation_error_control | 9,10 | 8,9 | True | False | d8:AGTGGGCTCTCCACGG<br>d9:GTGGGCTCTCCACGGA | 14 | 1 |

Source: https://raw.githubusercontent.com/trimcrae/Rare-cancers/dece8fd886f554641a6c32276b00731af0d05438/research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json

Source SHA256: `ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec`. All ranking sets and saved changed flags were recomputed from the fixed design rows before writing this table; archived row choice flags were also checked. No transcriptome search was rerun.
