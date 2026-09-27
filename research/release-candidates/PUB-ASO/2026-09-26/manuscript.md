---
id: DOC-PUB-ASO-CBC-20260926-MANUSCRIPT
title: "Transcript provenance changes fusion junction antisense comparisons in extraskeletal myxoid chondrosarcoma"
kind: manuscript
status: live
date: 2026-09-26
last_verified: 2026-09-26
purpose: Preserve the reviewed ASO candidate and its attributable supporting record.
scope: Local submission preparation with distinct source evidence classes.
audience: [maintainers, external reviewers]
---

# Transcript provenance changes fusion junction antisense comparisons in extraskeletal myxoid chondrosarcoma

Tristan D. McRae

Independent researcher, unaffiliated. Correspondence: trimcrae@gmail.com. ORCID: 0000-0002-1823-1451.

## Abstract

Fusion-junction antisense design requires an exact RNA sequence, but published fusion labels can refer to different transcript annotations. We investigated primary EMC sequence records and model descriptions, then compared five binding positions at seven source-linked junctions with an expanded normal-parent transcript corpus. Coordinates and protein identifiers in the published USZ20-EMC1 figure resolve its EWSR1 exon-13/NR4A3 exon-2 labels to reference boundaries represented as exon 12/exon 3 in the previous catalogue. This establishes reference correspondence, not a patient RNA consensus. The companion USZ22-EMC2 junction remains unresolved. Seven deposited fusion records support five distinct junctions. Expanding from six parent transcripts to 77 records representing 71 distinct sequences lengthens the consecutive match spanning the proposed six-base DNA gap for 9 of 35 designs. An alternative nonfusion NR4A3 splice sequence extends the centred TCF12-junction design's match from seven to eleven bases. Existing register effects persist. The accompanying accession-level evidence table, reference sequences, per-position comparisons and code distinguish deposited sequences, reference reconstructions and hypothetical controls. These findings correct a model correspondence and identify specific omitted normal-transcript matches; they do not establish RNA cleavage, biological selectivity or an EMC-specific excess of partial complementarity.

Keywords: extraskeletal myxoid chondrosarcoma; NR4A3; fusion transcript; antisense oligonucleotide; transcript annotation; sequence specificity

## 1. Introduction

An antisense oligonucleotide directed across a fusion junction must recognize the actual joined RNA. Gene names alone do not specify that sequence: alternative donor boundaries, acceptors and transcript annotations can change it. EMC provides a tractable example because primary studies identify NR4A3 fusion transcripts and experimental models, while the nucleotide correspondence between those sources and a design catalogue requires separate verification.[1–3]

Our preceding computational resource contains 190 designs across 38 modelled NR4A3 exon-3 junctions, with five binding positions per junction. Most are hypothetical. It already demonstrated that shifting a 16-nucleotide design by one base can change its match to a normal parent transcript. Partial complementarity and chemistry-dependent off-target activity are established antisense-design concerns.[4,5] The present question is narrower: which existing designs can be connected to attributable biological sources, and which sequence comparisons change when the actual transcript annotations and additional parent isoforms are considered? We investigated source provenance before expanding comparisons.

## 2. Methods

### 2.1. Source resolution

We examined primary papers, their supplementary files, seven existing fusion-sequence deposits and attributable public sequencing metadata. This was a targeted investigation, not an exhaustive case survey. Evidence classes separate directly deposited junction sequence, reference reconstruction from reported coordinates, previous reconstruction from an engineered-construct description, unresolved observations and hypothetical controls. Neither an exon label nor a fusion name alone was accepted as an exact RNA junction.

For Bangerter et al.'s models,[2] we transcribed the coordinates and protein identifiers displayed in Figure 4, resolved those identifiers to versioned GRCh37 Ensembl transcripts, and compared exon boundaries with cDNA, independent genomic sequence and RefSeq annotations. The inferred genome build and coordinate convention are recorded separately from the figure's literal observations. Each GenBank fusion record was searched for a unique exact anchor containing 16 bases on each side of the candidate seam. Seven records yielded five distinct junctions; records were not counted as independent patients.

Brenca et al.'s engineered constructs were treated separately.[3] Their corrected sequencing accession and subsequent attributable sample metadata identified public runs.[6,7] A bounded search of two fixed 64-MiB compressed mate-1 prefixes used exact 16+16-base anchors for 44 existing reference junctions in both orientations. Search limits, amendments, retrieval receipts and the negative result are retained in Supplementary Methods.

### 2.2. Designs and reference comparison

We reused five 16-nucleotide designs at each of seven source-linked junctions: five deposit-supported junctions, the USZ20 reference reconstruction and a previously reconstructed TAF15 cryptic-exon construct. The source classes remain distinct. The proposed architecture is five LNA residues, six DNA residues and five LNA residues, with a phosphorothioate backbone; chemistry was not experimentally evaluated. Donor contributions of 6–10 target bases place the seam within the central gap. Five hypothetical designs produced by transferring the USZ20 exon labels literally to the catalogue transcripts serve as a separate annotation-error control.

The baseline consists of the original six mature parent transcripts. We added the three transcripts resolved from the source figure and all 68 accessions returned by a scoped UCSC curated-RefSeq query for EWSR1, TAF15, TCF12, TFG, FUS and NR4A3. The resulting corpus contains 77 records and 71 distinct sequences, including one curated noncoding record. "Normal" here denotes nonfusion reference sequence, not measured expression in a particular healthy tissue. Accession versions, locus-query intervals, sequence hashes and retrieval dates are supplied.

For each design, we measured the longest consecutive exact match to a forward normal-RNA window spanning target positions 6–11, corresponding to all six DNA-gap positions. No mismatch or bulge is allowed within that run. All tied maxima, complete 16-base windows and mismatch positions are retained. Descending substring enumeration and an independent exhaustive-window implementation agreed. We report lengths rather than optimize a cutoff; sensitivity results span cutoffs of 6–16 bases, including the previously adopted, biologically unvalidated ten-base criterion. These deterministic comparisons require no significance test.

AI tools assisted source retrieval, code generation, sequence analysis and drafting. Checks included pinned-input hashes, independently obtained reference sequences, two matching implementations and a separate AI computational critique. Such checks do not constitute experimental validation or human peer review.

## 3. Results

### 3.1. Published coordinates resolve one model correspondence

USZ20-EMC1 is labelled EWSR1 exon 13 joined to NR4A3 exon 2.[2] Figure 4b also supplies chr22:29692358, chr9:102590323, ENSP00000400142 and ENSP00000333122. Their GRCh37 transcript parents are ENST00000414183.2 and ENST00000330847.1. The coordinates mark the last base of the displayed EWSR1 exon 13 and the first base of NR4A3 exon 2. These same boundaries are exon 12 of NM_005243.4 and exon 3 of NM_006981.4 (Table 1). Thirty-base flanks agree between transcript and genomic retrievals and match the catalogue's EWSR1 exon-12/NR4A3 exon-3 join.

The centred reconstructed antisense sequence is GGGCATATCATCAAAC. Transferring the labels "13/2" literally to the catalogue's different transcripts instead gives AGTGGGCTCTCCACGG: 11 of 16 aligned positions differ, including four of the six gap positions. Across all five positions, the hypothetical label-transfer controls differ at 11–12 whole-sequence and 2–4 gap positions. This is a concrete annotation error, not a prediction of differential cleavage.

USZ22-EMC2 remains unresolved. Figure 4d shows NR4A3 chr9:102590347–102590387 followed by TAF15 chr17:34149754–34149794, opposite the paper's TAF15–NR4A3 description. Both 41-base intervals fall inside the relevant displayed exons. They cannot be converted into an exact directional RNA seam by choosing the nearest exon boundaries.

**Table 1. Source annotations for the USZ20 reference reconstruction.** Positions are 1-based GRCh37 reference coordinates. Build and terminal-base convention are inferred from annotation concordance.

| Gene | Figure-linked transcript | Figure exon and boundary | RefSeq transcript and exon |
| --- | --- | --- | --- |
| EWSR1 | ENST00000414183.2 | Exon 13 ends at chr22:29692358 | NM_005243.4 exon 12 |
| NR4A3 | ENST00000330847.1 | Exon 2 starts at chr9:102590323 | NM_006981.4 exon 3 |

### 3.2. Additional isoforms change specific sequence comparisons

The seven deposited fusion records are AF162670.1, AJ243810.1, AJ245932.1, AY532911.1, AF289510.1, AF524261.1 and S81242.1. The first three share the same TAF15 junction; the remaining records support distinct TFG, TCF12 and two EWSR1 junctions. Their local seam sequences agree with the existing designs. Recovering these deposits was part of the preceding resource, not a new discovery here.

Nine of 35 source-linked designs have longer gap-spanning matches in the expanded parent corpus; none has an exact 16-base target match in that corpus. Table 2 gives all five positions for each junction. The centred TCF12 design GGGCATATCCATCAGA increases from seven to eleven consecutive bases. Its fusion target TCTGATGGATATGCCC and the nonfusion window AAATGTGGATATGCCC share the final eleven bases, covering the complete proposed gap. This sequence occurs in NR4A3 NM_173200.3 and the original MINOR/NR4A3 cDNA U12767.1 associated with Hedvat and Irving.[8] These concordant records are not independent biological replications.

The changes have more than one cause. Two TFG-junction designs acquire longer matches to FUS NM_001170634.1 and NM_001170937.1. Cryptic-exon designs acquire matches across a nonfusion NR4A3 splice in NM_173200.3. The USZ20 designs retain their baseline values of 7–11 bases. At the historical ten-base criterion, 14/35 versus 21/35 source-linked designs meet the cutoff in the baseline and expanded corpora, respectively. Three of five hypothetical label-transfer controls also increase, from eight to nine bases, and remain excluded from those denominators.

**Table 2. Longest exact normal-parent match spanning the complete six-base gap.** Entries follow donor contributions of 6, 7, 8, 9 and 10 target bases, in that order; the middle entry is centred. All values are nucleotides. Exon labels use the catalogue annotation. Deposited sequences, a patient-model reference reconstruction and a construct reconstruction are different evidence classes, not a patient cohort.

| Junction | Source class | Original six transcripts | Expanded corpus |
| --- | --- | --- | --- |
| EWSR1 e12 / NR4A3 e3 | USZ20 reconstruction | 11, 7, 8, 8, 8 | 11, 7, 8, 8, 8 |
| EWSR1 e7 / NR4A3 e2 | Fusion deposit | 11, 8, 8, 8, 8 | 11, 8, 8, 8, 8 |
| EWSR1 e10 / NR4A3 cryptic exon | Fusion deposit | 7, 11, 12, 13, 14 | 12, 11, 12, 13, 14 |
| TAF15 e6 / NR4A3 e3 | Fusion deposits | 12, 11, 9, 11, 12 | 12, 11, 9, 11, 12 |
| TAF15 e6 / NR4A3 cryptic exon | Construct reconstruction | 7, 7, 7, 7, 7 | 12, 11, 9, 7, 7 |
| TCF12 e5 / NR4A3 e3 | Fusion deposit | 11, 8, 7, 7, 7 | 13, 12, 11, 7, 7 |
| TFG e7 / NR4A3 e3 | Fusion deposit | 13, 12, 11, 9, 9 | 13, 12, 11, 11, 12 |

The bounded Brenca-data probe scanned 1,961,217 and 2,420,522 complete reads from SRR13435278 and SRR13435264, respectively, with zero exact candidate junction anchors. This provided no sequence-confirmation upgrade; it is not evidence that the constructs or complete-run junction reads are absent.

## 4. Discussion

This revision establishes a source-auditable correspondence for one patient-derived model and identifies additional matches missed by one-transcript-per-gene comparisons. Its contribution is the explicit mapping and accession-specific findings. It does not introduce the general principle that antisense specificity depends on sequence, position and chemistry.[4,5] The USZ20 result also corrects our previous interpretation that the published figure lacked sufficient nucleotide information to assess reference correspondence. It does contain informative coordinates and identifiers; the missing evidence is the patient's actual mature-RNA consensus.

The earlier 190-design resource and its artificial-junction controls remain historical comparisons using their original inputs. Under the adopted ten-base criterion, 87/190 primary designs and 40.6% of artificial controls met the original parent-pairing criterion. Those results did not establish an EMC-specific excess. The present 35-design audit uses a selected, source-linked set and a changed normal corpus; its counts neither update the entire catalogue nor estimate patient coverage. The original sequences are preserved separately, with a correction record explaining the changed interpretation.

The principal limitations can be stated together. USZ20 is a reference reconstruction: the genome build and coordinate convention are inferred, and patient variants or insertions remain unexcluded. USZ22 needs a directional RNA call or spanning reads. The Brenca prefix search is partial, nonrandom, single-mate and restricted to exact reference anchors. The normal comparison is confined to parent-gene isoforms and does not establish tissue expression or transcriptome-wide specificity. No oligonucleotide was synthesized or tested. Gap-spanning match length, absence of a complete match and any selected cutoff establish neither cleavage nor potency, safety or a therapeutic window. Within that scope, the dataset makes source identity and normal-transcript choice auditable before experimental lead selection.

## Data availability

Supplementary Data contains versioned reference inputs, a junction-evidence table, all 40 design rows with five hypothetical controls explicitly flagged, tied normal-match locations, cutoff sensitivity results and reproducible Python code. Supplementary Methods explains the bounded read probe and provides retrieval instructions and hashes; the large read prefixes are retained in the local evidence record. The preceding catalogue is archived at https://doi.org/10.5281/zenodo.22229096. That historical deposit does not contain this revision's new analysis, and no new public deposition is claimed.

## Funding and competing interests

No external funding supported this work. The author has no competing financial interests and declares a nonfinancial interest as an EMC survivor.

## Author contribution and ethics statement

Tristan D. McRae is the sole author and directed the investigation. The study uses published material and public sequence records; it reports no new recruitment, specimen collection or experiments.

## Declaration of generative AI and AI assisted technologies

Claude (Anthropic) assisted the preceding resource's code, sequence screens, literature work and drafting. OpenAI Codex with GPT-6-Astra assisted source retrieval, computational analysis, verification and preparation of this revision. Methods describe the research uses and checks. An independent AI critique was an internal check, not journal peer review. The author is responsible for the manuscript and its submission.

## References

[1] Panagopoulos I, Mertens F, Isaksson M, et al. Molecular genetic characterization of the EWS/CHN and RBP56/CHN fusion genes in extraskeletal myxoid chondrosarcoma. Genes Chromosomes Cancer. 2002;35:340–352. https://doi.org/10.1002/gcc.10127

[2] Bangerter JL, Harnisch KJ, Chen Y, Hagedorn C, Planas-Paz L, Pauli C. Establishment, characterization and functional testing of two novel ex vivo extraskeletal myxoid chondrosarcoma (EMC) cell models. Human Cell. 2023;36:446–455. https://doi.org/10.1007/s13577-022-00818-x

[3] Brenca M, Stacchiotti S, Fassetta K, et al. NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol. 2019;249:90–101. https://doi.org/10.1002/path.5284

[4] Watt AT, Swayze G, Swayze EE, Freier SM. Likelihood of nonspecific activity of gapmer antisense oligonucleotides is associated with relative hybridization free energy. Nucleic Acid Ther. 2020;30:215–228. https://doi.org/10.1089/nat.2020.0847

[5] Andersson P, Burel SA, Estrella H, et al. Assessing hybridization-dependent off-target risk for therapeutic oligonucleotides: updated industry recommendations. Nucleic Acid Ther. 2025;35:16–33. https://doi.org/10.1089/nat.2024.0072

[6] Brenca M, et al. Correction to NR4A3 fusion proteins trigger an axon guidance switch that marks the difference between EWSR1 and TAF15 translocated extraskeletal myxoid chondrosarcomas. J Pathol. 2021;254:606. https://doi.org/10.1002/path.5737

[7] Baldazzi D, et al. DElite: a tool for integrated differential expression analysis. Front Genet. 2024;15:1440994. https://doi.org/10.3389/fgene.2024.1440994. Supplementary File 2, metadata_file.csv.

[8] Hedvat CV, Irving SG. The isolation and characterization of MINOR, a novel mitogen-inducible nuclear orphan receptor. Mol Endocrinol. 1995;9:1692–1700. https://pubmed.ncbi.nlm.nih.gov/8614405/; GenBank U12767.1.
