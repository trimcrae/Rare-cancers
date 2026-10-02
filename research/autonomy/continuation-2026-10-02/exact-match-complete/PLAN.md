---
id: DOC-ASO-EXACT-HIT-COMPLETE-20261002
title: Complete exact-hit recovery and frozen GENCODE annotations
level: cross-cutting
kind: memo
status: live
purpose: Recover the six omitted exact-hit occurrences and freeze transcript annotations from the accepted GENCODE50 source.
scope: Uncapped recovery for 19 exact-positive ASO designs and comparison to the existing Ensembl116 annotation snapshot; no extrema or ranking rerun.
audience: [maintainers, autonomous research agents, external reviewers]
date: "2026-10-02"
last_verified: unverified
---

# Bounded cloud recovery plan

This retrospective implementation closes a witness-list and annotation-provenance gap. It is not a preregistration. The prior accepted census reports 134 design-record-window occurrences for 19 research designs, but only 128 rows were retained under the first-20 cap. The six omitted occurrences comprise two for TCF12_e5__NR4A3_e3:d9 and one each for TFG_e2__NR4A3_e3:d6–d9. Their distinct transcript count is unknown until execution; do not call them six additional transcripts.

## Actual preparation and source inspection

Read the operating protocol and source artifacts through the GitHub connector at dece8fd886f554641a6c32276b00731af0d05438. No local Git operation, bulk-source fetch, installation, scientific corpus execution or compiler run occurred. Thirteen small synthetic Python tests ran locally and passed (0.004 seconds reported). These cover overlaps beyond 20 occurrences, endpoint windows, Ns, normalization and final missing newline, record separation, aliases, duplicate IDs, length/header failures, versioned gene IDs, saved-coordinate/sequence/gene mutations, census mismatches, parent strata, repeated-transcript counting, and annotation mismatch/missing cases. Full recovery remains unverified.

Authoritative GENCODE release50 documentation:
https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/_README.TXT

Its transcript-FASTA section defines the ordered fields as transcript ID, gene ID, Havana gene ID, Havana transcript ID, transcript name, gene name, sequence length, transcript biotype. The successful response was 69,086 bytes with SHA256 ea687e13394011dfa5734e89047513b4b6120ca9d4914c695045a5af605d4ae6, fetched 2026-10-02T14:31:57.3436253Z. The file header-format-source.json preserves that receipt and the relevant section. The initially guessed README.txt returned 404; the actual filename was obtained from the official directory listing. No GTF is necessary. The general GTF-format page is not substituted for this FASTA-specific documentation.

## Method and acceptance

Use Python's literal overlapping substring search (find, advancing by one after each occurrence) for only the 19 accepted target sequences in every normalized transcript. This scans exact targets only; no Hamming/gap extrema or rankings are recomputed. Separate designs sharing a target sequence retain separate occurrence rows. Matching never crosses records; every returned 16-base window is unambiguous. Uppercase and U-to-T normalization match the accepted scanner.

Coordinates are zero-based positions in the transcript's stored 5′→3′ sense sequence: [start_0based,end_0based_exclusive), with end=start+16. They are not genomic coordinates or antisense-strand coordinates.

Require the pinned result and source hashes, exact 19-design scope, all accepted per-design/per-stratum occurrence counts and nearest-gene sets, full corpus record/base counts, 134 recovered rows, and exact identity/sequence/gene agreement for all 128 saved rows. Duplicate record identifiers and duplicate occurrence identities fail. The recovered-minus-saved set must contain six rows with the accepted missing-count allocation; its transcript multiplicity is measured, never inferred.

Preserve full versioned transcript and gene IDs, gene/transcript names, transcript length, literal biotype and literal FASTA header for every hit transcript. The field transcript_biotype_gencode50 is a transcript annotation, not a gene biotype.

Compare each recovered transcript to the existing, hash-pinned Ensembl116 60-ID snapshot. Report transcript-version, stable-gene-ID, biotype and length agreement separately. A biotype disagreement is an output finding, not a reason to substitute the current label. Transcripts absent from that snapshot receive not_in_pinned_release116_snapshot; their GENCODE50 annotation remains available. No live REST lookup is made, avoiding accidental substitution of a later release. This comparison therefore covers only the existing snapshot, not a newly exhaustive Ensembl116 lookup.

## Inputs and runnable command

Use the exact bytes at branch revision dece8fd886f554641a6c32276b00731af0d05438:

- research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json: SHA256 ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec.
- research/autonomy/continuation-2026-10-02/exact-match-annotation/witnesses.tsv: Git blob ca711d16ecdec6cfd17c6775d321f88eae25d6a4.
- Same annotation directory, ensembl-transcripts.json: SHA256 e2257b8155635433fce8d49fda5039e20486497def7225f7dbe7682983ace50e.
- Same annotation directory, ensembl-release.json: SHA256 86e87c46ae1a424702676493d024d0508ce60f6c951b0b2803ce10269e09c20c.
- Reuse cloud-cached gencode.v50.transcripts.fa.gz, 183,554,921 bytes, SHA256 5a320f524d73b5793518eb19b118829033713443d0f42af20a67bb31cc06cf56. Original source: https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_50/gencode.v50.transcripts.fa.gz .

For GitHub raw inputs the base is:
https://raw.githubusercontent.com/trimcrae/Rare-cancers/dece8fd886f554641a6c32276b00731af0d05438/

Run with existing Python standard library; no compiler or package installation:
~~~sh
python3 -B test_recover_exact_hits.py
timeout 20m python3 -B recover_exact_hits.py \
  --result /inputs/aso-transcriptome.json \
  --fasta /inputs/gencode.v50.transcripts.fa.gz \
  --witnesses /inputs/witnesses.tsv \
  --ensembl /inputs/ensembl-transcripts.json \
  --release /inputs/ensembl-release.json \
  --out /output/exact-match-complete
~~~

The parent of --out must exist; --out itself must not exist. Runner checks at least 10 GiB free plus 5 MiB output reserve. Root's prepared wrapper adds a 10.5 GiB floor, tests before any download, and a 22-minute whole-lane deadline with subprocess-group termination; that outer allowance includes source preparation around the scoped recovery. Internal input/recovery deadline is 18 minutes, with a 20-minute command guard shown above; no network is present in the runner. Reuse the compressed input; never write the expanded FASTA. The task's transient disk budget is <1 GiB including the 184 MB compressed source, with final artifacts capped at 1 MiB. Runtime and memory estimates have not been benchmarked on this corpus; a deadline failure is not a scientific pass and should not trigger an unchanged retry.

## Outputs and stopping rule

- complete-exact-hits.tsv: all 134 recovered occurrences and release50 annotations.
- new-six-occurrences.tsv: recovered rows absent from the saved 128, preserving actual transcript multiplicities.
- gencode50-hit-headers.json: literal frozen source headers for every hit transcript.
- annotation-comparison.tsv: per-transcript release50 versus available release116 metadata.
- summary.json: acceptance status, input hashes, per-design counts, transcript/gene IDs, occurrence-level and transcript-level biotype counts, newly seen transcript IDs and comparison limits.
- manifest.json: output byte lengths and SHA256s.

Root should use process success plus the completed manifest/summary, not a partial output file, as the completion receipt. Stop on any source, test, coverage or saved-hit mismatch. One successful cloud execution closes this bounded task. No external submission, contact or repository publication is authorized by this plan. Biological interpretation remains limited: sequence matches and biotypes do not establish expression, abundance, cleavage, safety or clinical effects.
