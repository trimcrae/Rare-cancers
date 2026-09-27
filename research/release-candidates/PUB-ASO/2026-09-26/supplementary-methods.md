---
id: DOC-PUB-ASO-CBC-20260926-SUPPLEMENTARY-METHODS
title: "Supplementary methods for transcript provenance and antisense comparisons in EMC"
kind: manuscript
status: live
date: 2026-09-26
last_verified: 2026-09-26
purpose: Preserve the reviewed ASO candidate and its attributable supporting record.
scope: Local submission preparation with distinct source evidence classes.
audience: [maintainers, external reviewers]
---

# Supplementary methods for transcript provenance and antisense comparisons in EMC

Tristan D. McRae

This supplement documents source recovery, coordinate reconstruction and the 35-design source-linked analysis. Five hypothetical annotation-error controls are reported separately. Main-text and supplementary section numbers are independent. The complete preceding 190-design screen is historical context, not a newly screened cohort.

The investigation was completed on 26 September 2026 using public papers and sequence records. Prior catalogue inputs were captured from repository revision 3d550114538a1545e1eab03e1a93f69566da47de. Supplementary Data includes the exact copied inputs and their original hashes. This targeted investigation does not claim an exhaustive survey of all EMC cases.

## S1. Primary-source investigation

| Source | What was actually recovered and inspected | Contribution and limit |
|---|---|---|
| Bangerter et al., DOI 10.1007/s13577-022-00818-x, PMC9813045 | Full XML, original Figure 4 PNG, both supplemental PDFs via Europe PMC archive | Figure 4 provides coordinates and protein IDs. Table S1 contains other DNA alterations; Table S2 contains STR profiles. Neither supplement supplies a junction consensus. Data availability directs requests to the corresponding author; no request was sent. |
| GenBank AF162670.1, AJ243810.1, AJ245932.1 | Actual GenBank sequence and record metadata | Same TAF15 e6/NR4A3 e3 16+16-base junction anchor; prior repository finding reused. Records are not counted as independent patients. |
| GenBank AY532911.1 and AF289510.1 | Actual sequence and metadata | TFG e7/NR4A3 e3 and TCF12 e5/NR4A3 e3 anchors; prior findings reused. AY532911 is cited directly as a deposit rather than assigned an invented PMID. |
| GenBank AF524261.1 and S81242.1 | Actual sequence and metadata | EWSR1 e10/NR4A3 cryptic-exon and EWSR1 e7/NR4A3 e2 anchors. The prior fusion-type naming conflict and distant S81242 discrepancy remain unresolved and were not silently corrected. |
| Brenca et al., DOI 10.1002/path.5284, PMC6766969 | Full XML, construct descriptions and sequencing methods | Distinguishes E-N, T-N and T-N*. A named engineered construct does not identify either Zurich model. |
| Brenca correction, DOI 10.1002/path.5737, PMC8451045 | Publisher/PMC HTML after XML endpoint returned HTTP 500 | Corrected sequencing-data location is PRJNA692081 / SRP301712. The old institutional link is not the end of the access investigation. |
| Baldazzi et al., DOI 10.3389/fgene.2024.1440994, PMC11614847 | Full XML and `DataSheet2.zip`, especially `Supplementary_File_2/metadata_file.csv` | Attributable EN/TN cell-model labels for eight runs. Not an independent biological validation of the 2019 experiments. |
| ENA PRJNA692081 metadata | 23 run records with sample aliases, FASTQ URLs, sizes and whole-file MD5s | Public reads are accessible. Two bounded mate-1 prefixes were actually retrieved and searched. The original whole-file MD5s cannot verify truncated prefixes; prefix SHA-256s are reported instead. |
| Hedvat and Irving 1995; U12767.1; NM_173200.3 | Primary bibliographic abstract and both full nucleotide records | The alternative nonfusion NR4A3 splice sequence is present in an original cDNA and reviewed RefSeq. U12767 source qualifiers say peripheral blood/T-lymphocyte; this does not measure expression or toxicity in any future test system. |
| Anderson et al., DOI 10.3390/cancers15051623, PMC10001040 | Full XML and relevant figure/table descriptions | Useful prior example of nucleotide/protein breakpoint interpretation. It supplies no new NR4A3 acceptor consensus for the present dataset. Its main junction-peptide tables concern other EWSR1 fusion partners. |
| Watt et al. 2020 and Andersson et al. 2025 | Primary experimental abstract and industry-recommendation abstract, respectively | Existing literature already motivates off-target sequence analysis and biological verification. No novel universal design principle is claimed. |

The initial Springer supplement host failed DNS resolution, but Europe PMC supplied the archive successfully. Every actual retrieval, including failures and final URLs, is preserved in `retrieval.jsonl`. The archive was initially saved with a `.pdf` filename before its ZIP content type was identified; it is correctly retained as `sources/Bangerter-supplementaryFiles.zip`. Its original receipt hash still identifies the same bytes. A filename or failed route was never treated as proof that a source was unavailable.

Primary source links: [Bangerter](https://pmc.ncbi.nlm.nih.gov/articles/PMC9813045/), [Brenca](https://pmc.ncbi.nlm.nih.gov/articles/PMC6766969/), [Brenca correction](https://pmc.ncbi.nlm.nih.gov/articles/PMC8451045/), [DElite](https://pmc.ncbi.nlm.nih.gov/articles/PMC11614847/), [Anderson](https://pmc.ncbi.nlm.nih.gov/articles/PMC10001040/), [Hedvat](https://pubmed.ncbi.nlm.nih.gov/8614405/), [Watt](https://pmc.ncbi.nlm.nih.gov/articles/PMC7418465/), [Andersson](https://doi.org/10.1089/nat.2024.0072).

## S2. Coordinate and sequence reconstruction

`figure-observations.json` records the literal visual observations, separately from inference. Both root and advisor read Figure 4. ENSP IDs are protein identifiers. GRCh37 Ensembl `lookup/id` resolves each protein to its parent nucleotide transcript and version; `lookup/id?expand=1` and `sequence/id?type=cdna` supply exon spans and cDNA. Exon lengths must sum to cDNA length, and protein/transcript IDs and versions must agree.

For USZ20, the displayed EWSR1 ENST00000414183.2 exon 13 ends at 29692358 and NR4A3 ENST00000330847.1 exon 2 begins at 102590323. Taking 30 bases before and after those boundaries produces the same sequence as catalogue EWSR1 ENST00000397938 exon 12 / NR4A3 ENST00000395097 exon 3. Independent UCSC hg19 sequence windows and RefSeq NM_005243.4 / NM_006981.4 exon coordinates corroborate it. Build and 1-based terminal-base convention are inferred from this concordance, not stated in the original figure. The output therefore has the class `reference_reconstruction_from_reported_coordinates`; it is not a patient sequence accession.

For USZ22, NR4A3 102590347–102590387 is at exon offsets 25–65, and TAF15 34149754–34149794 is at offsets 111–151. The intervals are internal to their displayed exons. Their width, displayed gene-order discrepancy and undefined caller semantics preclude an exact RNA seam. No candidate is generated by snapping these positions to exon boundaries.

For each deposited fusion record, the script searches the actual deposited RNA sequence for an exact 16-base donor plus 16-base acceptor anchor and requires a unique position. The table records the resulting adjacent deposit coordinates. This verifies local sequence identity; it does not verify every base of the entire transcript or count recurrent patients. The seven records identify five junctions because three TAF15 records have the same seam. Patent records were not used as patient evidence.

## S3. Design and normal-transcript comparison

All oligonucleotides are reused existing designs. Thirty-five rows cover seven distinct source-linked junctions: five direct-deposit junctions, one coordinate-reconstructed patient-model junction and one previously reconstructed engineered TAF15 cryptic-exon junction. Five additional EWSR1 e13/NR4A3 e2 rows are a hypothetical label-transfer error control and are excluded from the 35-design summaries. Every design is reverse-complement checked against its target window and verified to span its specified reference join. Sequences use a DNA alphabet to represent RNA.

The initial comparison retained the six previously used mature parent transcripts and added the three Ensembl transcripts actually named by the source figure. This revealed three longer TCF12-design matches. A recorded amendment then expanded to all curated RefSeq accessions returned for the same six gene symbols in their archived hg38 locus intervals. The query returned 37 EWSR1, 18 TCF12, four FUS, four TFG, three NR4A3 and two TAF15 accessions, including one curated noncoding record. All 68 accession versions were fetched from NCBI. Together with the six originals and three figure-linked transcripts, there are 77 reference records and 71 unique sequences. This is the captured, scoped curated parent corpus, not every human transcript isoform or every normal transcript.

The metric is the longest exact, consecutive match in a forward normal RNA window that covers target positions 6–11 inclusive, corresponding to the symmetric 16-mer's six DNA-gap positions. It can be zero if the full gap does not match. No mismatches or bulges are permitted inside that run. Reverse-complementing the target during a normal RNA scan would test the wrong hybridization orientation; the ASO is already the target's reverse complement.

Two independent implementations agree: exhaustive 16-base window comparison with extension from the six-base gap, and descending substring enumeration restricted to intervals spanning that gap. All tied longest-match locations, full normal windows, whole-window match counts and mismatch positions are retained. Twenty-five source-linked metrics and five hypothetical-control metrics were reused and checked because the normal-corpus input changed. Ten cryptic-exon subset metrics were newly calculated under the same six-parent baseline; they are explicitly marked `legacy_metric_reused=false`.

### Results without a biological cutoff

| Junction | Longest match at donor-base counts 6, 7, 8, 9, 10: original six-parent basis | Expanded parent corpus |
|---|---|---|
| EWSR1 e12 / NR4A3 e3 (USZ20 reconstruction) | 11, 7, 8, 8, 8 | 11, 7, 8, 8, 8 |
| EWSR1 e7 / NR4A3 e2 | 11, 8, 8, 8, 8 | 11, 8, 8, 8, 8 |
| EWSR1 e10 / NR4A3 cryptic exon | 7, 11, 12, 13, 14 | 12, 11, 12, 13, 14 |
| TAF15 e6 / NR4A3 e3 | 12, 11, 9, 11, 12 | 12, 11, 9, 11, 12 |
| TAF15 e6 / NR4A3 cryptic exon | 7, 7, 7, 7, 7 | 12, 11, 9, 7, 7 |
| TCF12 e5 / NR4A3 e3 | 11, 8, 7, 7, 7 | 13, 12, 11, 7, 7 |
| TFG e7 / NR4A3 e3 | 13, 12, 11, 9, 9 | 13, 12, 11, 11, 12 |

Nine of 35 lengths increase; no full 16-base target match occurs in the expanded corpus. Three of five hypothetical label-error controls also increase from 8 to 9 bases, reported separately. At the previously adopted ten-base criterion, the selected source-linked subset changes from 14/35 to 21/35. The complete 6–16-base sensitivity table is released; none of these cutoffs is validated as a biological boundary.

The TCF12 centred normal window is `AAATGTGGATATGCCC`, compared with fusion target `TCTGATGGATATGCCC`. The last 11 bases match and include all gap positions. This motif is found at U12767.1 positions 80–95 and NM_173200.3 positions 762–777. These records are concordant evidence for a sequence, not independent biological replications; RefSeq cites U12767 among its source records.

Two TFG designs gain longer matches to FUS NM_001170634.1 and NM_001170937.1, with 14/16 total identity and 11/12 consecutive gap-spanning bases. Cryptic-exon designs gain matches at the nonfusion NR4A3 exon-2/cryptic-exon splice in NM_173200.3. These distinct mechanisms are retained in the per-hit table rather than attributed entirely to the figure-linked NR4A3 isoform.

The literal-label control compares each USZ20 reconstructed design with the same-register hypothetical e13/e2 design. Distances are 11–12 of 16 aligned positions, including 2–4 of the six gap positions. These are Hamming distances under a specified alignment, not binding or cleavage predictions.

## S4. Bounded sequencing-data probe

The Brenca correction identifies PRJNA692081. DElite's archived metadata labels EN samples S315/S316/S317/S363 and TN samples S367/S385/S386/S318. Removing the documented `S` prefix matches ENA numeric sample aliases. Thus S315 maps to SRR13435278 and S386 to SRR13435264. DElite describes these as cell-model replicates; a generic BioSample `tissue=EMC` label must not turn them into patient-tumour observations.

The first probe searched 16 MiB compressed prefixes of mate 1 against the existing primary and noncoding-acceptor junctions and returned zero hits. Reading the original Brenca construct methods established that T-N contains the cryptic exon. A recorded amendment added both existing cryptic-exon junctions and expanded to a fixed 64 MiB compressed prefix per run. The final library contains 44 reference joins, each tested for an exact 16+16-base anchor in both read orientations. No anchor-length relaxation was used. The intended quality summary is Phred ≥20 across the anchor; there were no raw anchor hits to filter.

The final probe scanned 1,961,217 and 2,420,522 complete four-line FASTQ records, respectively, before the deliberate gzip truncation. Both returned zero exact anchors. Prefix hashes, URLs, byte counts, parser termination and saved bytes support exact offline replay. The finite prefix, single mate, targeted exact library, unknown construct sequence deviations and low representation limit detection. The result neither validates nor refutes a construct and does not establish that complete deposited RNA data cannot resolve it. It is an adverse/no-gain result, retained rather than converted into a claim of confirmation.

## S5. Comparison with the preceding resource

The previous resource already demonstrated binding-position dependence, catalogued most of these deposit-backed seams and retained the adverse artificial-join comparison. This investigation adds the actual source-figure annotation crosswalk for a patient-derived model, a negative result for assigning its companion model, and a versioned normal-isoform comparison that changes specific sequence-match lengths. It does not recast prior GenBank recovery, general mismatch sensitivity or standard off-target screening as novel.

## S6. Reproduction and file definitions

Unzip Supplementary Data and run Python 3.11 or later from its evidence directory:

```text
python analyze.py
```

The script uses only the Python standard library and makes no network requests. It checks the copied input hashes, annotation relationships, reconstructed sequence agreement, deposited anchors, antisense orientation and agreement of two matching implementations. It regenerates all eleven results files in results/. An output-checksum manifest enables comparison with the released results. Source retrieval URLs, dates, versions and checksums are in retrieval.jsonl; unsuccessful retrieval routes are preserved.

junction-evidence.tsv distinguishes each source observation and reconstruction. design-comparisons.tsv contains 40 rows, of which five have control_only=true and are excluded from the main 35-design summaries. The legacy_metric_reused column distinguishes accepted metrics from newly calculated cryptic-exon baseline comparisons. longest-normal-match-locations.tsv preserves every tied maximum, normal reference identifier, zero-based window start, complete normal window and one-based mismatch positions. displayed-transcript-exons.tsv uses one-based inclusive genomic coordinates. normal-reference-transcripts.fasta and its manifest contain the precise normal corpus. model-crosswalk.json separates USZ20 inference from unresolved USZ22 observations. literal-label-error-control.tsv, cutoff-sensitivity.tsv and normal-isoform-corroboration.json support the corresponding comparisons. summary.json records derived counts and check scope.

Large compressed read prefixes are not duplicated in the journal supplement. Their saved outputs and receipts are included. They can be retrieved and searched with the following command; this downloads a fixed 64 MiB from each of two runs and requires at least 128 MiB plus temporary working space:

```text
python read_prefix_probe.py --fetch --mib 64
```

Compare fetched prefix hashes to the original .receipt.json records before interpreting a rerun. Whole-file ENA MD5 values do not verify partial files. Offline replay with the original saved prefixes reproduced the reported complete-record counts and zero anchors. The probe is optional for reproducing the positive coordinate and parent-isoform findings; those depend only on the included reference inputs.

The original fusion-junction-aso-sequences.csv in inputs/ retains 782 non-comment rows spanning the preceding primary catalogue, extensions and controls. It is a historical input, not the current 40-row comparison table. Historical orderable or do_not_order fields encode computational rules and are not biological or clinical recommendations. The preceding artificial-junction result is not recomputed using the expanded corpus.

## S7. Interpretation corrections and remaining evidence

The USZ20 crosswalk replaces the earlier interpretation that the paper lacked information sufficient to assess catalogue correspondence. It does not supply a patient consensus. The alternative NR4A3 transcript explains the reported exon-2 label, and the displayed EWSR1 annotation also changes exon rank. The original six-transcript match lengths remain correct for that corpus; they must not be presented as all-isoform results.

A previous explanation that a primer in retained NR4A3 exon 3 could never recover an upstream cryptic-exon fusion is withdrawn. A reverse primer in retained exon 3 can amplify such a transcript with a suitable upstream donor primer. Exclusion would require the actual primer sequences and orientation. This correction does not change the present sequence calculations.

USZ20 needs a mature-RNA consensus or a fully specified original directional call, including genome build, coordinate convention and inserted bases. USZ22 needs the actual donor end, acceptor start and direction. Brenca constructs need attributable spanning reads or the physical construct sequence. A complete transcriptome/pre-mRNA search and tissue expression context would be needed before selecting experimental leads; the current parent-isoform audit does not provide those data. Cleavage, accessibility, potency and normal-transcript effects require experiments.

