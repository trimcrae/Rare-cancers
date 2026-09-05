---
id: DOC-PUB-ASO-NAT-REVISION-NOTE-2026-09-04
title: ASO submission revision and data provenance
kind: memo
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Identify the corrected interpretations and distinguish this submission from its historical archive.
scope: Supplementary File 2 for the computation-only NAT manuscript.
audience: [external reviewers, maintainers]
---

# Supplementary File 2

## Revision and data provenance

This note accompanies the manuscript “NR4A3 fusion-junction antisense gapmers for extraskeletal myxoid chondrosarcoma: reagents, test articles and a pre-registrable knockdown experiment.” It identifies the interpretation corrections in this submission and the relationship between its sequence record and the preceding computational archive.

## Historical archive

The preceding analysis is archived at doi:10.5281/zenodo.22229096. This identifier refers to the published historical snapshot, not to the text of the present submission. The submission supplies a corrected sequence record as Supplementary File 1 and explains its interpretation here. The archive remains a source for computational code, per-design outputs and screen parameters; its superseded temperature-bound and model-correspondence statements must be read with the corrections below.

## Melting temperature interpretation

The sequence record retains the legacy field names predicted_tm_fusion_c and predicted_tm_best_parent_c so its numerical outputs remain reproducible. Both are nearest-neighbour calculations for an unmodified DNA:RNA hybrid, in degrees Celsius. They are not measurements or validated predictions for the proposed gapmers, which have locked-nucleic-acid wings and a phosphorothioate backbone. Those chemical effects are not included in the model.

Subtracting the two model fields gives 26.6 and 36.0 degrees Celsius for the named EWSR1 and TAF15 reagents, respectively. The present Table 1 labels these values as model differences and removes the earlier lower-bound symbol. Neither a lower bound for the modified chemistry nor cancellation of modification effects has been established. Supplementary File 1 replaces the unsupported cancellation explanation with this limitation. Its sequence rows and numerical model outputs are unchanged from the repository source; the correction changes explanatory comments only.

## Cell model correspondence

The reported NR4A3 exon-2 acceptor labels for the Zurich cell models do not by themselves establish their nucleotide junctions relative to this design panel. The present Table 1 therefore requires nucleotide-junction confirmation, consistent with the manuscript's discussion of coding-exon and transcript-exon numbering. The earlier categorical statement that these models match other designs is superseded. No cell model was obtained or sequenced in this work.

## Reproduction and scope

The release contains build_data.py and data-build-stamp.json. The script derives the corrected sequence record and tables from the named repository sources, checks that every non-comment CSV row is unchanged, and records SHA-256 hashes of its inputs and outputs. The upload manifest separately identifies the exact manuscript and submission files. These records document the revision; they do not replace the archived scientific computations or imply that an experiment was performed.

All sequences remain unsynthesised, untested research reagents, not for administration to any person or animal. No cleavage, potency, delivery, safety or therapeutic window was established. Experimental use requires confirmation of the test article's breakpoint at nucleotide resolution and the controls and limitations specified in the manuscript.
