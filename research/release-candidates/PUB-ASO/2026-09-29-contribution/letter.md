---
id: DOC-PUB-ASO-CONTRIBUTION-20260929-LETTER
title: "Fusion junctions and normal RNA matches in antisense designs for extraskeletal myxoid chondrosarcoma"
kind: manuscript
status: live
date: 2026-09-29
last_verified: 2026-09-29
purpose: Present the model correspondence and newly identified normal RNA matches as a clear scientific contribution.
scope: Author requested narrative revision with unchanged scientific inputs and results.
audience: [maintainers, external reviewers]
---

# Fusion junctions and normal RNA matches in antisense designs for extraskeletal myxoid chondrosarcoma

Tristan D. McRae

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID: 0000-0002-1823-1451.

To the Editor,

Antisense oligonucleotides (ASOs) can be designed to bind the RNA junction created by a cancer gene fusion. This approach has been tested experimentally against EWS–FLI1 in Ewing sarcoma.[1] For extraskeletal myxoid chondrosarcoma (EMC), we link a patient-derived cell model to a defined reference junction and to our ASO designs. We also identify longer matches to normal RNA for nine of 35 designs when alternative transcripts are included. Together, these findings establish which sequences the designs represent and revise how distinct some appear from normal RNA.

We developed our computational catalogue using 16-base ASOs complementary to sequences spanning EMC fusion junctions. For each junction, we generated five designs by shifting the binding position one base at a time. For this study, we selected seven junctions from the catalogue and its extensions based on links to deposited fusion sequences or detailed model descriptions. We retained all five positions per junction, giving 35 designs. The supporting dataset distinguishes deposited sequences from reference reconstructions.

Bangerter et al. established the patient-derived EMC cell model USZ20-EMC1.[2] We used the coordinates and sequence identifiers in their fusion diagram (Figure 4b) to reconstruct its reference junction. Reconciling the transcript references linked this junction to five of our designs. Exon numbers, which label segments of RNA, differed between the references. Copying those numbers without reconciling the references would select a different sequence: the resulting ASOs differed at 11 of 16 bases in the centred comparison. Thus, a model's fusion label alone is insufficient to choose its ASO target.

We then asked how normal transcript choice affects the sequence comparison. We compared the 35 designs first with one reference RNA per fusion-partner gene, then with an expanded set containing alternative transcripts, or isoforms, from the same six genes. Each ASO has a central six-base DNA region called the gap. We measured the longest stretch of consecutive matching bases between its intended target and a normal RNA that covered the entire gap.

Including additional isoforms increased this match length for nine designs. For one TCF12–NR4A3 design, it rose from seven to eleven bases because of an alternative NR4A3 transcript described by Hedvat and Irving.[3] The five USZ20 comparisons were unchanged. No design had a complete 16-base match in the expanded set.

Checking unintended RNA matches is established antisense practice.[4] Our contribution is to connect specific EMC fusion evidence to designs and identify the normal transcripts that alter their sequence comparisons. The accompanying sequences, source records and code make those connections inspectable and reproducible.[5]

The USZ20 reconstruction assumes a genome reference and coordinate convention; it does not establish the patient's exact RNA sequence. The companion model, USZ22-EMC2, remains unresolved. Our normal comparison covers reference RNAs from the fusion-partner genes, not the whole transcriptome or measured expression in healthy tissue. It does not update the entire catalogue or estimate patient coverage. No ASO was synthesized or tested. These results guide sequence interpretation but cannot establish cleavage, selectivity or safety.

## Declarations

The author directed this public-data study. It involved no new recruitment or experiments and received no external funding. The author has no competing financial interests and declares a nonfinancial interest as an EMC survivor. Claude assisted the preceding resource. OpenAI Codex with GPT-6-Astra assisted retrieval, analysis, verification and drafting. Computational checks and an independent AI critique do not constitute experimental validation or human peer review. The author is responsible for the manuscript.

## References

[1] Tanaka K, Iwakuma T, Harimaya K, Sato H, Iwamoto Y. EWS-Fli1 antisense oligodeoxynucleotide inhibits proliferation of human Ewing's sarcoma and primitive neuroectodermal tumor cells. J Clin Invest. 1997;99:239–247. doi:10.1172/JCI119152.

[2] Bangerter JL, Harnisch KJ, Chen Y, et al. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. Human Cell. 2023;36:446–455. doi:10.1007/s13577-022-00818-x.

[3] Hedvat CV, Irving SG. The isolation and characterization of MINOR, a novel mitogen-inducible nuclear orphan receptor. Mol Endocrinol. 1995;9:1692–1700. PMID:8614405; GenBank U12767.1.

[4] Andersson P, Burel SA, Estrella H, et al. Assessing hybridization-dependent off-target risk for therapeutic oligonucleotides: updated industry recommendations. Nucleic Acid Ther. 2025;35:16–33. doi:10.1089/nat.2024.0072.

[5] McRae TD. Transcript provenance and normal-parent sequence comparisons for EMC fusion-junction antisense designs [dataset]. Zenodo; 2026. doi:10.5281/zenodo.22986104.
