---
id: DOC-PUB-ASO-NAT-SUBMISSION-SUPPORT-2026-09-04
title: ASO NAT submission support package
kind: memo
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Describe the shortest path from existing candidate files to a human-approved submission.
scope: Exact journal upload files and final author actions; no external submission authority.
audience: [maintainers, external reviewers]
---

# NAT submission instructions

The exact upload files are identified by SHA-256 in [upload-manifest.json](upload-manifest.json). The manuscript is an Original Paper. Use the current files here, not the historical Word/PDF files under `research/manuscripts/aso/`.

| Portal role | File | Use |
|---|---|---|
| Main document | [manuscript.docx](manuscript.docx) | Includes declarations, references, tables and Figure 1. |
| Anonymous main document | [manuscript-anonymized.docx](manuscript-anonymized.docx) | Use instead if the portal requests anonymous review; author identifiers and metadata are removed. |
| Title page | [title-page.docx](title-page.docx) | Author, correspondence and declarations. |
| Figure 1 | [figure-1.eps](figure-1.eps) | Vector CMYK artwork; one figure upload. |
| Figure legends | [figure-legends.docx](figure-legends.docx) | Separate editable legend. |
| Supplementary File 1 | [fusion-junction-aso-sequences.csv](fusion-junction-aso-sequences.csv) | Corrected explanatory comments; all 782 sequence-data rows preserved. For anonymous review use [the version with identifiers removed from comments](anonymous/fusion-junction-aso-sequences.csv). |
| Supplementary File 2 | [supplementary-file-2.pdf](supplementary-file-2.pdf) | Revision and historical-archive interpretation note. Use [the anonymous version](supplementary-file-2-anonymized.pdf) with an anonymous main document. |
| Cover letter | [cover-letter.md](cover-letter.md) | Copy the letter body into the portal; omit repository front matter. |

NAT's public instructions currently describe both single- and double-anonymized review in different places; both variants are prepared so the portal's requested file designation can be followed without rewriting the paper. Supply one main-document variant and one revision-note variant, not both. The historical extended-report supplementary material is not part of this journal upload set.

## Final author actions

1. Approve this exact revision and responsibility for it, including the AI-use disclosure and carried-forward nonfinancial-interest statement.
2. Confirm current journal consideration/related submissions and whether anything newer than Qeios v2 has been posted. If true when submitting, add to the letter: “This manuscript is not under consideration at another journal.”
3. Complete the portal declarations and authorize journal submission. Retain the existing no-print-colour preference. The recorded budget is $600; request a new cost decision if an actual quote exceeds it.

These are submission acts. Manuscript preparation, archive reconciliation, file verification and repository checks are coordinator work and are recorded in [the verification record](../verification.json). No journal submission has been made. No laboratory reply or future experimental preregistration is required to submit this computational proposal; the manuscript requires nucleotide-junction confirmation before experimental ordering.

The [NAT instructions](https://journals.sagepub.com/author-instructions/NAT), checked 4 September 2026, allow 4,000 main words, 200 abstract words and five display items. Current charges are $90 per typeset page: six pages would be $540, but the journal's production count controls the charge. The double-spaced Word page count is not a fee estimate. Preprints are permitted; disclose their DOI and do not update them during journal peer review.
