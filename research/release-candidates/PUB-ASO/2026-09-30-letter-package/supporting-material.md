---
id: DOC-ASO-BRIEF-SUPPORT-20260930
title: Supporting methods and complete EMC antisense catalogue
kind: memo
status: live
purpose: Explain evidence, sequence comparisons and reproduction separately from the concise manuscript.
scope: The accepted 43-junction catalogue and one annotation-error control.
audience: [external reviewers, collaborators]
date: 2026-09-30
last_verified: 2026-09-30
---

# Supporting methods and complete EMC antisense catalogue

Tristan D. McRae | Supplement to Antisense sequence choices for extraskeletal myxoid chondrosarcoma

## 1. What this study contributes

The study combines a nucleotide-level evidence audit with the same normal-parent comparison for every junction in our catalogue. It extends our initial 190-design, 38-junction exon-3 analysis to 215 designs across 43 target junctions. The 215 design rows represent 201 distinct ASO sequences; some junction-position designs share a sequence. These are stages of this study, not a separately published resource. Five additional designs represent an annotation-error control and are excluded from target totals. Generating complementary oligonucleotides and screening normal transcripts are established practices; the contribution is the EMC-specific evidence and the observed changes in design choices. No claim of a new design algorithm or the first EMC catalogue is made.

## 2. Fusion evidence and its limits

Exact local sequences were sought in attributable deposits, primary articles, figures and associated source records. A fusion name or exon number alone was insufficient to establish a nucleotide junction. Table S1 distinguishes sequence deposits from reference reconstructions. Seven deposited records yield five distinct junctions, not seven independent patients. The full evidence table retains accession versions, deposit breakpoints, local sequences, citations and ambiguity. The 36 other target junctions are explicitly hypothetical exact reference joins; this is not a prevalence estimate or an exhaustive inventory of all possible EMC fusions.

{{EVIDENCE_TABLE}}

For USZ20-EMC1, Bangerter et al. Figure 4b reports EWSR1 and NR4A3 protein identifiers and genomic breakpoints (chr22:29692358 and chr9:102590323). GRCh37 transcript lookup maps ENST00000414183.2 exon 13 to NM_005243.4 exon 12, and ENST00000330847.1 exon 2 to NM_006981.4 exon 3. The resulting reference flanks agree with EWSR1_e12__NR4A3_e3 in this catalogue. Genome build and coordinate convention were inferred; patient-specific variants and insertions remain unknown. A literal EWSR1 exon-13/NR4A3 exon-2 join is retained only as an annotation-error control. Its centered 16-base target differs at eleven positions, including four of the six DNA-gap positions, from the coordinate-based reconstruction.

USZ22-EMC2 remains unassigned because the displayed intervals fall within exons and the displayed gene order is reversed. Brenca et al. describe engineered E-N, T-N* and T-N constructs; those descriptions support reference models, not deposited construct consensus sequences. No construct sequence is transferred to a patient-derived model merely because its fusion label agrees. A previous bounded search of two RNA-seq mate-1 prefixes (64 MiB each) recovered no qualifying junction reads. These nonrandom partial reads cannot establish absence; no full-read search or exact consensus reconstruction is claimed. The original source audit and its correction records remain in the reproducibility archive.

## 3. Design generation and normal RNA corpus

Each target is a reference fusion sequence with 30 bases on either side of its junction. Five overlapping 16-base sites contain six, seven, eight, nine or ten donor bases. Their reverse complements are the proposed ASOs, recorded 5' to 3'. DNA letters are used for RNA targets (T represents U). The proposed architecture is five LNA bases, six DNA bases and five LNA bases; no synthesis, chemical backbone specification or biological validation is implied. Junction labels identify the archived reference convention and are not universal exon identities. Unversioned archived transcript labels remain explicitly unversioned rather than being silently updated.

The normal comparison contains EWSR1, FUS, NR4A3, PGR, TAF15, TCF12 and TFG. There are 85 records representing 78 distinct mature RNA sequences and 39,478 distinct complete 16-base windows. All duplicate sequence aliases are retained in the manifest and matching-location tables. The baseline uses one archived canonical sequence per gene; the expanded comparison uses the captured alternative sequences for the same seven genes. This isolates the effect of the included RNA variants without changing gene coverage. It does not assert that every normal isoform is represented.

PGR coverage was added to the earlier six-gene comparison using an archived canonical sequence and seven accession-version records: NM_000926.4, NM_001202474.3, NM_001271161.2, NM_001271162.2, NR_073141.3, NR_073142.3 and NR_073143.3. Adding PGR increases the gap-spanning match for 50 of 215 designs. This is a separate effect of broader gene coverage, not the 23-design effect attributed to adding variants while holding the seven genes fixed. Retrieval receipts and raw accession records are preserved.

## 4. Sequence metrics and declared ranking

For each ASO, we compare its reverse-complement target to every complete 16-base normal window. The primary metric is the longest uninterrupted exact match that covers all six central DNA-gap positions (one-based target positions 6-11). Matches may extend into the flanks. If no complete six-base gap is matched, the score is zero; this does not mean there is no complementarity. We minimize the maximum such match across the entire normal corpus. All genomic/transcript coordinates and matching sequences are retained in the result tables where available.

The secondary metric is the minimum Hamming distance to any complete normal 16-base window: the fewest base differences across all sixteen positions. This is calculated across all windows, not only those producing the longest gap-spanning match. Among primary ties, we maximize this minimum distance and retain every remaining tie. The analysis plan was frozen before the catalogue-wide run. No activity cutoff, adjustable weights or threshold search is used. Primary ties, final ties and Pareto alternatives are all preserved. A design is a Pareto alternative if no other design at that junction is at least as good on both metrics and better on one; ten junctions contain competing alternatives. Neither metric has been biologically validated as a ranking rule for this proposed chemistry.

## 5. Results, adverse comparisons and controls

Adding the captured RNA variants changes the primary preferred-position set at nine of 43 target junctions. The longest gap-spanning match increases for 23 of 215 designs. The secondary rule narrows primary ties at 19 junctions. Final choices are unique at 27 junctions and tied at 16. No full 16-base exact match occurs in this parent-gene corpus; this does not establish transcriptome-wide specificity. Table 1 in the main text illustrates the deposited TCF12 junction. Table S2 provides all final choices and preserves evidence class and ties; the machine-readable files retain every design and metric.

An adverse example is the USZ20 reference reconstruction. Before adding PGR, its five gap-spanning match lengths were 11, 7, 8, 8 and 8 bases in donor-position order 6-10. With PGR included, all five reach eleven bases. The final comparison leaves donor positions 9 and 10 tied. The older subset result therefore cannot be reused as if it represented the expanded seven-gene comparison.

The annotation-error control tests the consequences of assigning a sequence from incompatible exon conventions; it is not evidence of a biological fusion. An earlier artificial-junction comparison found that 87 of 190 designs (45.8%) met a ten-base complementarity criterion, versus 40.6% in artificial controls. That cutoff was not a validated biological threshold, and the comparison did not establish an EMC-specific excess. Those negative constraints are preserved; the current ranking neither adopts that cutoff nor converts it into a selectivity claim.

## 6. Interpretation and remaining evidence gap

The catalogue supports selection under a stated parent-sequence comparison, not selection of the best therapeutic ASO. Most joins remain hypothetical, some source labels lack transcript versions, and reconstructed references are not patient consensus sequences. The comparison excludes other genes, unspliced RNA, bulges, thermodynamics, expression, accessibility, delivery and cleavage. Watt et al. studied different gap lengths and chemistries; their results justify caution about simple sequence counts but do not validate this six-base DNA-gap/LNA design. Exact biological junction confirmation, a broader normal-RNA screen and experimental testing remain necessary before claiming a selective lead. The current contribution is bounded by those missing data.

## 7. Reproduction and file dictionary

Data S1 (junction-catalogue.tsv) has one row per target junction plus the control. It includes reference identifiers and breakpoints, evidence classes, local sequence, primary and final choices, all tied ASOs and Pareto alternatives. Data S2 (all-designs.tsv) has all 220 design rows; control_only distinguishes the five control designs. The *_gap_run_bp fields are longest exact gap-spanning matches in the named corpus; expanded_seven_gene_min_hamming_bp is the fewest differences across all normal windows. Boolean choice fields encode the declared rule, not experimental selection. JSON arrays inside TSV cells preserve all ties and source mappings.

Data S3 (gap-match-locations.tsv) contains all maximum gap-spanning match sites. Data S4 (nearest-normal-windows.tsv) contains all windows attaining the minimum Hamming distance. Data S5 (normal-reference-manifest.tsv) and Data S6 (normal-reference-transcripts.fasta) record the normal corpus and aliases. Data S7 (junction-evidence.tsv) records primary fusion evidence. Data S8 (data-manifest.json) supplies SHA-256 digests and origin paths. These standalone files are the formal data supplement; the archive is an additional reproduction convenience.

Extract reproducibility.zip into an empty directory. Run python 2026-09-30-full-catalogue/analyze_catalogue.py --output regenerated. Python's standard library is sufficient and network access is unnecessary. The script first checks all eighteen pinned inputs, then writes new outputs without changing older evidence. Compare regenerated TSV, FASTA and summary.json files with the corresponding accepted results. An independent exhaustive checker previously verified all 220 designs, orientations, distances, sites and ties; its unchanged receipt is included. Do not execute the older 2026-09-26/evidence/analyze.py in place: that historical script has top-level writes. The archive preserves it as provenance only.

## Supporting references

Bangerter JL, Harnisch KJ, Chen Y, et al. Hum Cell 2023;36:446-455. doi:10.1007/s13577-022-00818-x. Primary source and Figure 4: https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/.

Brenca M, et al. Primary construct report and associated source material: https://pmc.ncbi.nlm.nih.gov/articles/PMC6766969/. Exact construct consensus sequences are not assigned from the paper alone.

Hedvat CV, Irving SG. Isolation and characterization of MINOR, a novel mitogen-inducible nuclear orphan receptor. Mol Endocrinol 1995;9:1692-1700. PMID:8614405. Related normal NR4A3 sequence record: U12767.1.

Design-method and mismatch-biology references are given as references 2 and 4 in the main manuscript. Deposit-specific primary references are retained in Data S7 and the original GenBank records.

{{CATALOGUE_TABLE}}
