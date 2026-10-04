---
id: DOC-TMEM266-RNA-LETTER-METHODS-20261004
title: Supplementary methods and remaining-question analyses for TMEM266 in EMC
level: L3
kind: manuscript
status: live
purpose: Preserve new molecular, sequence, cohort and confounding analyses with explicit inclusion decisions.
scope: Exploratory public data follow-up; incorporates and qualifies the frozen 3 October methods.
audience: [maintainers, external reviewers, collaborators]
date: 2026-10-04
last_verified: 2026-10-04
---

# Supplementary methods and remaining-question analyses

This accompanies the [revised working draft](DRAFT.md). The [3 October methods](../tmem266-prepublication-2026-10-03/SUPPLEMENT.md) retain discovery selection, normalization, raw-array scoring, bootstrap, probe annotation, FFPE extraction and V1-34 coverage details. Those methods are incorporated here; the explicit corrections below supersede their earlier statements that the array specimen crosswalk was unavailable and that no USZ read prefixes were examined. The original dated files remain unchanged. Neither version is a public release or submission-ready package.

The [new plan](PLAN.txt) distinguishes analyses specified before reading their target values from post-selection robustness checks. All additional tests are exploratory. Cohorts, arrays, probes, transcript estimates, reads and fragment identifiers are different units and are never added as independent patients or molecules.

## Cohort identities and molecular annotations

[cel_headers.py](cel_headers.py) reads only the first 65,536 bytes of each selected CEL file through authenticated byte ranges. Across 25 files this required 1,638,400 bytes and retained each range's SHA256 plus decoded generic and parent metadata in [cel-headers.json](cel-headers.json). Both the experiment-name parameter and DAT header repeat the six EMC identifiers:

| GEO sample | Specimen | In full 704-specimen atlas | In retained nine |
|---|---|---|---|
| GSM600934 | 104-92 | Yes; excluded | No |
| GSM600935 | 168-97 | Yes; excluded | No |
| GSM600936 | 2663-07 | No | No |
| GSM600937 | 536-00 | Yes; excluded | No |
| GSM600938 | 81-97 | No | No |
| GSM600939 | F415 | No | No |

[cohort_context.py](cohort_context.py) verifies these identifiers against all 704 original specimen rows, not only the retained subset. Distinct identifiers do not exclude undocumented patient aliases, so an aggregate 15-independent-patient claim remains unjustified. A reused supplement's row order differs from GEO order and is not a valid crosswalk.

The same script reads primary Hofvander [Table S3](https://pmc-oa-opendata.s3.amazonaws.com/PMC13133608.1/ccr-25-3740_supplementary_table_s3_suppts3.xlsx) and [Table S4](https://pmc-oa-opendata.s3.amazonaws.com/PMC13133608.1/ccr-25-3740_supplementary_table_s4_suppts4.xlsx), preserving source hashes in [cohort-context.json](cohort-context.json). Seven retained specimens have explicit NR4A3 fusion rows: EWSR1 partners in 4840-13, 5241-06, 7931-19 and 8102-22; TCF12 in 11881-19; HSPA8 in 3372-22; and TAF15 in 4716-22. The last row has medium confidence and a stop-codon annotation and is retained with that flag. Specimen 5149-18 has RT-PCR-verified FUS::NR4A2. Specimen 3371-22 has fusion-positive S1 metadata but no specimen-level S3 row; aggregate S4 information is consistent with a missing TAF15::NR4A3 case, which remains an indirect inference rather than a specimen-linked result.

Excluding 5149-18 and 3371-22 gives seven directly annotated NR4A3 cases with TMEM266 median 28.88 TPM, range 6.73–56.82, and A=1 against each primary comparator. No new validation follows from this inherited subset separation. No fusion-partner differential-expression test is supported by these small subgroups.

The predeclared descriptive CHRNA6 comparison reused the same specimens and added the eight eligible ossifying fibromyxoid tumors (OFMT). Both genes give A=1 against the three primary comparators; against OFMT, TMEM266 gives A=0.95833 in nine cases and 0.94643 in seven, whereas CHRNA6 gives A=1 in both. OFMT TMEM266 median is 2.81 TPM (0.33–16.27); CHRNA6 median is 0.325 (0–1.31). Individual values are retained, without optimized thresholds, a classifier, or diagnostic performance claims. There is no demonstrated incremental diagnostic value over CHRNA6.

## Array batch and sensitivity analyses

Decoded parent metadata place all six EMC scans on 2008-09-30, LGFMS on 2008-10-07 or 2008-10-15, and both muscle pools on 2009-02-20. The scanner identifier is the same, 50206370, but no shared date supports an EMC-versus-LGFMS within-date estimate. Histology and scan day are nonidentifiable in this selected comparison; neither a statistical adjustment nor control subtraction can recover an independently identified histology effect. Scan dates are assay metadata, not patient collection dates.

[array_robustness.py](array_robustness.py) reuses saved intensities and flags. Flag exclusion requires at least one retained probe in every fixed region per array; all 25 arrays remained complete. The primary upstream score gives A=0.97059 (95% conditional bootstrap interval 0.88235–1) after flag exclusion; the strict canonical-CDS score gives 0.95098 (0.82353–1). Subtracting each region's fixed GC-control mean before aggregation gives primary A=0.95098 (0.82353–1) and strict A=0.94118 (0.79412–1). Results are in [array-robustness.json](array-robustness.json), independently recomputed using separate arithmetic. These are technical sensitivity analyses, not new cohorts, corrected effects or selection-adjusted confidence intervals; they omit uncertainty about inseparable batch effects.

[muscle_profile.py](muscle_profile.py) fixes ACTA1, CKM, MYH1, MYH2 and MYH7 before inspecting their contrast. For each array, each RMA log2 expression is centered on the mean of the two muscle pools; the contrast subtracts the median of five centered markers from centered TMEM266. EMC median is 7.004693 (range 5.318306–8.170648), positive against either individual pool as well. However, all 34 non-EMC tumors also have positive contrasts: group medians are 5.119954 for desmoid, 5.402799 for LGFMS, 5.529912 for myxofibrosarcoma and 5.584384 for solitary fibrous tumor. [muscle-profile.json](muscle-profile.json) retains all values. Different gene backgrounds/dynamic ranges, two pooled references and disjoint scan dates prevent purity or cellular-mixture interpretation. This result does not exclude entrapped muscle or establish an EMC-specific muscle-independent pattern.

## FFPE detector-sequence corroboration

[exact_probe_counts.py](exact_probe_counts.py) searches the pre-existing 18.81 MB local TempO-Seq checkpoint for the fixed manufacturer 50-mer and its reverse complement, with no mismatch search. It finds one matching row in manufacturer orientation; no new raw FASTQ was downloaded. The original complete-run receipts report EOF for all 12 runs. Counting used a lossy algorithm with epsilon=0.000002 and bucket width 500,000, followed by persistence of sequences covering 99% of retained reads; this is not 99% of all raw reads. Positive persisted counts are lower bounds with conservative upper error ceil(epsilon × total reads). These deterministic bounds are not confidence intervals.

| Sample | Run | Retained count lower–upper bound |
|---|---|---|
| Si19 | SRR35940646 | 250–262 |
| Si17 | SRR35940647 | 538–551 |
| Si15 | SRR35940649 | 30–42 |
| Si14 | SRR35940650 | 534–548 |
| Si22, identity conflict | SRR35940654 | 822–833 |
| Si02 | SRR35940656 | 187–203 |

The other six entries are persistence-censored, not measured zero expression. Run/BioSample/alias mappings were independently checked against the original metadata; Si22 remains excluded from the identity-qualified set. The original raw FASTQ bytes were not newly reauthenticated. [exact-probe-counts.json](exact-probe-counts.json) binds the checkpoint, receipts and selected row by hash.

The exact match corroborates the detector-product design used in at least those libraries, while the manufacturer's entire batch revision remains unreported. These amplified products do not sequence endogenous RNA across a junction, count original molecules, validate positivity thresholds, or exclude off-target hybridization. This is supplementary assay provenance within the same series, not biological replication.

## USZ-23_EMC3 RNA and model ambiguity

GSE299349/GSM9037837 explicitly describes cells, a poly(A)-selected stranded library and Dragen RNA processing against hg38 RefSeq, in the Planas-Paz study cited by the draft. The September [sequence-discovery decision](../emc-sequence-discovery-2026-09-23/DECISION.md) and archived evidence retain a complete source-MD5-verified SRR33903995 analysis with 102 EWSR1–NR4A3 supporting reads, 88 fragment identifiers and 22 oriented starts. An independent reviewer recounted those archived records here; the whole fusion alignment was not rerun. Fusion and TMEM266 signals in one bulk cell preparation do not establish single-cell colocalization or a new independent patient.

Before reading target estimates, membership was fixed from NCBI Gene 123591: NM_152335, XM_005254160, XM_017021915, XM_047432151, XM_054377283, XM_054377284 and XM_054377285, retaining source versions. The official 1,821,812-byte quantification file has literal columns Name, Length, EffectiveLength, TPM and NumReads and 162,218 transcript rows. Two workers independently retrieved matching compressed and decompressed hashes. The coordinator's initial replay received HTTP 403; it is not represented as a successful third quantification download.

| Indexed reference | Length, nt | Effective length | TPM estimate | Estimated reads |
|---|---:|---:|---:|---:|
| NM_152335.3 | 2372 | 2102.855 | 21.279970 | 375.406 |
| XM_005254160.3 | 2338 | 2068.855 | 112.237256 | 1947.995 |
| XM_017021915.1 | 2615 | 2345.855 | 0 | 0 |

Summed TPM is 133.517226 and estimated reads 2323.401. The four newer fixed accessions are absent from this old index, not measured zeros. [usz-worker-quant.json](usz-worker-quant.json) preserves the verified values and hashes; [usz_quant.py](usz_quant.py) is the bounded retrieval and model-matching replay.

Historical references have different coding annotations: NM_152335.3 CDS 129–1724 (531 amino acids), XM_005254160.3 CDS 647–1690 (347 amino acids), and XM_017021915.1 CDS 372–1967 (531 amino acids), using 1-based inclusive transcript positions. All 30 array 25-mers match XM_005254160.3; 29 match each other model. The 50-mer target matches all three. Thus a region coding in the canonical model can be untranslated in another compatible model. The higher allocation to the predicted model is not evidence of biological predominance, because assignment uncertainty/equivalence classes were not available. [usz-reference-models.json](usz-reference-models.json) contains version-specific sequence receipts. No reference translation is presented as measured protein.

## Bounded alternative-junction read pilot

The dated plan was amended before fetching SRR33903995 raw prefixes. It fixed the first 15,000,000 compressed bytes per mate and three exact 40-nt anchors with 20 bases on either side: the reference-described 106-nt deletion boundary in XM_005254160.3 at cDNA position 476, the NM_152335.3 inclusion boundary at 404, and its canonical exon 4–5 join at 510, all 0-based. Both strands were searched; qualifying anchors require minimum Phred 20 across all 40 bases. Incomplete terminal FASTQ records were discarded; fragment IDs deduplicated mates.

[usz_prefix.py](usz_prefix.py) streams the fixed prefixes in memory, stores only selected matches and receipts, and examines 284,838 and 280,862 complete 151-nt records, respectively. Coordinator replay reproduced the worker's prefix hashes, counts and matches in [usz-prefix-replay.json](usz-prefix-replay.json). The alternative anchor appears in both mates of one fragment, SRR33903995.239812; every anchor base has Phred 40. The two canonical controls have no hits in these prefixes, which cannot establish their absence or an isoform ratio. There was no extension selected by the observed result.

Both mates describe one local boundary, not two independent molecules. The selected sequences and qualities are retained in [usz-selected-reads.json](usz-selected-reads.json). Reference-path validation places mate 1 exactly across three hg38 blocks, chr15:[76137832,76137895), [76156603,76156652), [76160094,76160133). Mate 2 reverse complement matches 150/151 bases across [76156630,76156652), [76160094,76160168), [76169815,76169870), with one mismatch outside the anchor at chr15:76169828. Their 61-nt overlap is exact. The alternative intron [76156652,76160094) is 3,442 bp with GT/AG boundaries; these joined read sequences are not contiguous DNA at that locus. All coordinates here are 0-based half-open. Current reference models also contain the local alternative join, so this is not a newly discovered isoform. One fragment cannot establish a predominant or complete transcript, tumor-tissue expression of that boundary, protein production, or function.

## Bounded sequence-specificity searches

NCBI human RefSeq RNA BLAST used blastn, word size 7, filtering off, reward 1, penalty −3, gap costs 5/2, E-value 1000 and at most 1000 subjects per query. The original query set comprised all 30 array 25-mers and the fixed 50-mer detector sequence; sequence hashes, submitted settings, retrieval and selected HSPs are in [blast_retrieve.py](blast_retrieve.py) and [blast-probe_RNA.json](blast-probe_RNA.json). Whole-query exact matches and ungapped candidates within two substitutions or uncovered terminal bases were retained separately. All primary, strict and downstream probes and the 50-mer recovered whole-query TMEM266 transcript matches. The first-exon context probe 760129 has only its expected partial current-reference overlap; both probes previously segregated as antisense-shared also match NR_120360.1/LOC101929439 exactly. No additional non-TMEM266 whole-query or two-substitution candidate was retrieved. However, 26/31 queries reached the subject limit, and shorter partial matches remain; the result does not prove exhaustive or experimental specificity.

A post-pilot follow-up submitted every observed positive sequence, namely the alternative 40-nt anchor and both complete 151-nt reads, to the same RNA search settings. The exact anchor matches XM_005254160.4 and XM_054377285.1; mate 1 has a 131-nt exact partial alignment to their revised 5′ models, and mate 2 aligns over 151 nt with one mismatch. All three searches reach the subject limit. These results corroborate compatibility with annotated TMEM266 sequence, not a newly discovered transcript or exhaustive uniqueness. The selected results are in [blast-observed_RNA.json](blast-observed_RNA.json).

The corresponding original probe search against human RefSeq genomic sequence, RID C4DCYTNP014, remained queued after approximately 31 minutes at the declared stopping checkpoint. [The status receipt](blast-genomic-status.json) records that unresolved route; no genome-wide negative or uniqueness conclusion is made. No local polling process remains; the remote service job may remain queued and expires independently. Exact locus checks and RNA alignments cannot substitute for a completed genome-wide search or measured hybridization specificity.

## Inclusion and unresolved routes

The [source gates](source-gates.txt) record fresh searches for protein, single-cell, spatial and full-transcript evidence. Named cohorts in Burns proteomics and CellSARCTx do not include EMC. A metadata-only range extraction from the public ProCan workbook found no authenticated EMC identity among all 10,474 shared strings; generic sarcoma labels were not reclassified. [procan_metadata.py](procan_metadata.py) and [procan-metadata.json](procan-metadata.json) reproduce that gate without protein measurements or the 79 MB full workbook. Other candidate cohorts had inaccessible/private identities or unsuitable modalities, and a retracted proteomics study was excluded. These outcomes are not biological negative results.

The completed checks add a usable fusion-supported culture, clarify sample and molecular scope, and narrow what existing assays establish. They do not close malignant-cell localization, full-length RNA phasing, protein expression, functional dependency, or diagnostic utility. Accessible source gaps in Brenca patient/run mapping and the full earlier CHRNA6 candidate list also remain. No additional paper is proposed from those gaps or from a speculative null result.

## Reproduction, review and release

Run the linked scripts from the repository root using the existing Python runtime, `PYTHONDONTWRITEBYTECODE=1`, and the repository's `.cache/python-deps` where specified. Do not silently overwrite frozen receipts; reproduce into a separate small destination when releasing. Public source files may change or refuse retrieval, so hashes and actual execution status accompany outputs. The scripts and selected evidence remain dependent on earlier repository inputs and are not yet a portable public deposit.

Independent workers challenged identity, molecular scope, assay counts, arithmetic, alternative annotations and publication claims. Those focused checks do not substitute for the repository-required ultra review of a frozen outgoing version. Final author review, a portable evidence package, venue formatting and outstanding repository integration checks remain release work. No publication, submission, outreach, public-record mutation or paid resource was used.
