---
id: "DOC-CONTINUATION-2026-10-02-METHYLATION-USZ-CURRENT-SOURCE-AUDIT"
title: "Current USZ model junction-source audit"
level: "cross-cutting"
kind: "memo"
status: "live"
canonical_for: []
purpose: "Record the scoped evidence and reasoning for Current USZ model junction-source audit."
scope: "October 2 continuation; limited to the named sources, computations and review scope recorded in the body. No submission clearance."
audience: ["maintainers","autonomous research agents"]
date: "2026-10-02"
last_verified: "unverified"
_backfilled: "true"
---

# Current USZ model junction-source audit

Checked 2026-10-02 using current web text extraction and quiet HTTPS metadata requests. No email, access request, raw sequencing download, reconstruction, UI operation, screenshot or rendering was performed.

## Outcome

No nucleotide-resolved fusion junction or assay-native NR4A3 transcript accession/version was recovered for either model. The current evidence still supports only these reported labels:

| Model | Current reported fusion label | Exact junction sequence | Assay-native NR4A3 reference |
|---|---|---|---|
| USZ20-EMC1, RRID:CVCL_C6MX | EWSR1 exon 13 :: NR4A3 exon 2 | Not recovered | Not recovered |
| USZ22-EMC2, RRID:CVCL_C6MY | TAF15 exon 6 :: NR4A3 exon 2 | Not recovered | Not recovered |

This is a bounded current-source negative result, not proof that no qualifying information exists. Do not infer a nucleotide sequence from the labels or substitute a current RefSeq annotation for the assay's native reference.

## Difference from the cached handoff

Compared with `247a3d2f539e50b2b046e9d93237b60c2e787da1/research/autonomy/usage-sprint-2026-10-01/usz-junction-inputs/handoff.md`, this audit actually retrieved current publisher supplementary text and current repository-search metadata. The old unanswered supplementaryFiles endpoint was not replayed. Alternative primary publisher links resolve the two supplementary tables, but neither supplies the missing junction input. No cached scientific computation was repeated.

## Primary paper and supplements

Primary publication: Bangerter et al., Human Cell 36:446-455, PMID36316541, PMC9813045, DOI10.1007/s13577-022-00818-x.

https://link.springer.com/article/10.1007/s13577-022-00818-x

Current Methods describe FoundationOne HEME profiling and 150-base paired-end sequencing. Figure4's text caption reports the exon labels above; the main text says RNA-level confirmation was performed in tissue and corresponding models. The data-availability statement still offers datasets via the corresponding author on request, rather than naming a sequencing accession. No native NR4A3 transcript accession/version or nucleotide junction was found in the extracted article text. Figure images were not visually re-inspected under the morning restriction.

Current BioStudies literature record:

https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC9813045

The API lists two files, not a new sequencing deposition:

- `13577_2022_818_MOESM1_ESM.pdf`, 91,157 bytes. Publisher text extraction covers all three pages: a DNA short-variant table, with gene names, protein/CDS changes, genomic positions, coverage/read fractions and biomarkers. No EWSR1/TAF15::NR4A3 junction or native NR4A3 transcript reference appears in that extracted table. https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs13577-022-00818-x/MediaObjects/13577_2022_818_MOESM1_ESM.pdf
- `13577_2022_818_MOESM2_ESM.pdf`, 110,337 bytes. Publisher text extraction covers its one page, which is an STR table comparing tumor and cell-model alleles; it does not provide fusion sequence. https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs13577-022-00818-x/MediaObjects/13577_2022_818_MOESM2_ESM.pdf

A separate direct in-memory fetch of file2 yielded 110,337 bytes, SHA256 `a34b5e04253632759bdeee6ac5bba27c8e21fceacc0df24d29e26cc46528ae54`. The direct file1 fetch yielded only 3,038 bytes, inconsistent with the listed PDF size; it is not accepted as a PDF fingerprint. File1 conclusions rely on the successful publisher PDF text extraction, not that anomalous direct response. Neither file was persisted locally. No visual layout or image-only absence claim is made.

## Current registry identities

https://www.cellosaurus.org/CVCL_C6MX currently states: “EWSR1 exon 13 fused to NR4A3 exon 2”.

https://www.cellosaurus.org/CVCL_C6MY currently states: “TAF15 exon 6 fused to NR4A3 exon 2”.

Both entries cite PMID36316541 and display version6, last updated10April2025. Neither inspected entry supplies a junction sequence or transcript version. Their shared source is not independent corroboration.

## Current accession-search execution and rejected false positives

NCBI ESearch API base: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi . Parameters were `db=sra|gds|bioproject`, `retmode=json`, `retmax=20`.

1. Query `"USZ20-EMC1" OR "USZ22-EMC2"`: SRA returned count0. GEO/gds returned26 and BioProject7, but their explicit query translations dropped the USZ components and became `EMC1[All Fields] OR EMC2[All Fields]`. Those counts are not evidence for these models and were rejected.
2. Refined query `USZ20[All Fields] OR USZ22[All Fields] OR "36316541"[All Fields]`: GEO/gds and BioProject returned0. SRA returned2; it reported the PMID phrase unmatched and searched USZ20/USZ22.
3. Both SRA hits were resolved by metadata, not presumed to be models. EFetch: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=38994694,38994691&retmode=xml . They are Escherichia coli strains USZ22 and USZ20 in PRJNA1271740, with BioSamples SAMN48885752/SAMN48885750 and runs SRR33821836/SRR33821839. They concern bacterial WGS and are unrelated to the EMC models. No sequence reads were fetched.
4. ENA Portal API `/search` queries over sample_alias and description for USZ20/USZ22 returned a diagnostic query message; an exact sample_alias query in TSV explicitly returned `ERROR occurred. Not all results may have been written.` These are access/query failures, not zero-hit evidence. Example exact query: https://www.ebi.ac.uk/ena/portal/api/search?result=sample&query=sample_alias%3D%22USZ20-EMC1%22%20OR%20sample_alias%3D%22USZ22-EMC2%22&fields=sample_accession,sample_alias,description&format=tsv&limit=20 .
5. Bounded web searches used both full model names with junction/transcript/accession/NM_ terms and restricted EGA/GEO/SRA/ENA domains. No qualifying model-specific accession surfaced. This was not an exhaustive controlled-access metadata audit; private, unindexed or differently named datasets remain possible.

## Remaining exact input

A model-specific junction-spanning sequence/read with provenance and/or the native assay NR4A3 transcript accession and version is still required. Transcript identification alone may clarify exon numbering without resolving the nucleotide boundary. The two newly retrieved supplementary tables do not authorize a junction compatibility claim or new oligo design. No outreach occurred.
