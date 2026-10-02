---
id: DOC-CHECKPOINT05-HLA-HISTORICAL-FASTA
title: Deposited historical HLA Atlas FASTA identified
kind: memo
status: live
level: cross-cutting
purpose: Resolve the identity and accessibility of the deposited canonical search database before query scanning.
scope: Primary paper and PXD019643 metadata; full FASTA scan remains pending cloud execution.
audience: [maintainers, autonomous research agents]
date: 2026-10-02
last_verified: 2026-10-02
---

## New source result

The [official PXD019643 archive](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/04/PXD019643/) contains `sp_21_04_2020_decoy.fasta`. The [filtered PRIDE API record](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD019643/files/all?filenameFilter=sp_21_04_2020_decoy.fasta) identifies its category as FASTA, size as 27,229,450 bytes, checksum as `a8f95d9048d4688a0da109ff01e9d796563dad74`, submission date as June 15, 2020 and publication date as April 16, 2021. The metadata does not explicitly name the checksum algorithm. The filename contains 21_04_2020; this is not a verified formal UniProt release identifier.

The deposited [README](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/04/PXD019643/README.txt) contains 3,425 file rows: one FASTA and 483 RESULT records. All 483 RESULT records explicitly include FASTA ID 1 in their mapping. `audit_metadata.py` reproduces these metadata counts; it ran successfully and writes `metadata-association.json`. This establishes submission-level association with the result files, not an independent audit of every run's actual search parameters.

The exact [historical FASTA object](https://ftp.pride.ebi.ac.uk/pride/data/archive/2021/04/PXD019643/sp_21_04_2020_decoy.fasta) supports HTTP byte ranges. A 2,048-byte prefix request returned HTTP206 and Content-Range `bytes 0-2047/27229450`. It contains observed target headers beginning `sp|` and decoy headers beginning `DECOY_sp|`. The full FASTA has not been fetched or scanned locally. No query-presence/absence conclusion is claimed at this checkpoint.

## Important source discrepancy and eligibility

The [primary XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8054196/fullTextXML) identifies Swiss-Prot UP000005640 with 20,365 protein sequences, MHCquant 1.5.1, OpenMS 2.5, Comet 2016.01 rev.3 and Percolator 3.4. The [PRIDE project protocol](https://www.ebi.ac.uk/pride/ws/archive/v2/projects/PXD019643) instead reports 20,416 protein sequences plus a customized contaminant list and Percolator 3.1.1. Both describe an unspecific search with variable methionine oxidation, precursor tolerance 5 ppm, fragment bin tolerance 0.02 Da and local peptide-level 1% FDR. These count/version differences remain unresolved; do not silently equate every historical search to the deposited file or infer a unique formal Swiss-Prot release from the filename.

Reported HLA-I search limits were length 8–12 residues, digest mass 800–2,500 Da and charge 2–3; HLA-II limits were 8–25 residues, 800–5,000 Da and charge 2–5. The scanner reports length eligibility separately; it does not calculate mass/charge observability. The long provisional class-II query is outside the canonical class-I length range. No I/L equivalence sensitivity is necessary for these four strings, which contain neither letter.

The separate cryptic HLA-I analysis used PEAKS Studio X top-ten de novo candidates and Peptide-PRISM matching to six-frame HG38 and three-frame Ensembl 90 transcriptome translations, with stratified 10% FDR. The deposited Swiss-Prot FASTA is not an audit of those translated search spaces, nor evidence that a fusion-junction sequence was represented there. Primary XML enumerates one PDF and five XLSX supplements; no supplement or full result file was downloaded in this bounded task after the concrete FASTA object was located.

## Bounded cloud execution contract

Post-plan terminology clarification (October 2): the frozen plan's phrase "database searchability" means sequence representation in the FASTA only. Representation alone is insufficient to establish eligibility under all algorithmic, mass/charge and modification settings, or successful search/identification. Length flags address only the explicitly reported length filters.

Run `python -B test_scan.py` and `python -B scan_historical_fasta.py --output historical-fasta-scan.json` on a CPU-only cloud worker. Standard library only; no installation or raw-spectrum downloads. The scanner streams exactly the pinned object, retains one protein record at a time, limits total bytes to 27,229,450 and rejects unexpected length or checksum mismatch before writing results. It computes SHA1 and SHA256; matching the reported 40-hex checksum is described as observed SHA1 agreement, not an explicitly named PRIDE algorithm. Hash the final scanner and preserve its execution output.

Exact matches are counted separately for observed `DECOY_` headers, `sp|` targets and other nondecoy headers. The last category is not automatically a human protein or contaminant. Counts include all record occurrences; up to 20 witnesses per query retain headers and zero-based starts with explicit capping. Record boundaries are never joined; wrapped sequence lines are joined; X and stop characters are retained and cannot create a match across them. The six tiny tests passed locally, including exhaustive binary short-pattern comparison with a slicing oracle, line wraps, record boundaries, actual decoy-prefix handling, invalid input, duplicates and witness capping. The full scan has not yet run in this worker's evidence.

## Interpretation amendment proposed after the scan

Replace the draft's broad unresolved-FASTA statement only after a checksum-verified cloud receipt is available. State that the four fixed queries were searched in the specifically deposited FASTA, report target and decoy findings separately, and retain the paper/deposit count/version discrepancy and the separate unexamined cryptic search space. Even no occurrence anywhere would mean absence from this deposited canonical sequence search space, not a negative experimental test of the candidate or proof of normal-tissue absence. Query boundaries remain provisional. The existing processed-atlas counts and donor analyses were not repeated.

## Access and provenance

All successful metadata responses and their hashes are retained in `retrievals.jsonl`. Two exploratory file filters (`filter=fileName=fasta` and `fileName=fasta`) were ignored by the API and returned the same first 100 rows as the unfiltered request; those responses are not treated as exhaustive evidence of FASTA absence. The official API description revealed the correct `filenameFilter` parameter. No captcha was bypassed. An initial XML text-print command failed because the console encoding could not represent a Unicode space; UTF-8 printing succeeded. This did not affect the stored source bytes. No modern protein database substitution, spectrum processing or submission action occurred.
