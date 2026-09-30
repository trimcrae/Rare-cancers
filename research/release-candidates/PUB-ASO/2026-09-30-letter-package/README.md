---
id: DOC-ASO-BRIEF-PACKAGE-20260930
title: Concise EMC antisense manuscript and complete catalogue
kind: memo
status: live
purpose: Guide author proofreading and independent reuse of the full data supplement.
scope: Brief Communication package with accepted parent-gene comparisons; no submission or preprint update.
audience: [maintainers, external reviewers, collaborators]
date: 2026-09-30
last_verified: 2026-09-30
---

# Concise EMC antisense manuscript and complete catalogue

Start with the [two-page main PDF](ASO-brief-communication.pdf), also available as [editable Word](ASO-brief-communication.docx). The [five-page supporting PDF](ASO-supporting-material.pdf) contains methods, provenance and all final sequence choices; [supporting Word](ASO-supporting-material.docx) is editable. This is an author-proofreading draft prepared as a Nucleic Acid Therapeutics Brief Communication. It has not been submitted. Publisher pagination may differ.

The study's contribution is an EMC sequence catalogue that separates documented fusion junctions from reference assumptions and shows how the included normal RNA variants change design choices. It is a computation-only contribution for experimental planning. It does not identify a biologically selective lead. The ranking covers mature RNA from seven fusion-parent genes, not the whole transcriptome.

## Formal supplementary data

Submit these standalone data files with the manuscript, rather than supplying only a repository link:

- [Data S1: complete junction catalogue](data/junction-catalogue.tsv): 43 targets and one annotation-error control; evidence, sequence choices and all ties.
- [Data S2: all design comparisons](data/all-designs.tsv): 215 target designs and five control designs.
- [Data S3: all longest gap-spanning match sites](data/gap-match-locations.tsv).
- [Data S4: all nearest normal windows](data/nearest-normal-windows.tsv).
- [Data S5: normal reference manifest](data/normal-reference-manifest.tsv).
- [Data S6: frozen normal sequences](data/normal-reference-transcripts.fasta).
- [Data S7: fusion evidence](data/junction-evidence.tsv).
- [Data S8: data origin and SHA-256 manifest](data/data-manifest.json).

The supporting document explains units, coordinates, fields, aliases, evidence classes and selection rules. Every data file is byte-identical to its accepted source; no new threshold or ranking was fitted for this paper.

## Reproducibility

Download [reproducibility.zip](reproducibility.zip), extract it into an empty directory, and follow REPRODUCE.txt. Python's standard library is sufficient:

```text
python 2026-09-30-full-catalogue/analyze_catalogue.py --output regenerated
```

All eighteen required inputs are pinned and included. Full published articles and images are linked through the source audit rather than duplicated in the archive. The historical September 26 analyze.py is provenance only and must not be executed in place because it writes to its own evidence directory.

The [archive verification](archive-verification.json) records a fresh extraction, checks of all 98 archived file hashes, and byte-identical reproduction of all seven generated result files. The prior independent exhaustive numerical verification is included unchanged in the archive; it was not rerun for unchanged scientific inputs. Accepted numerical source commit: a916dab2979e27f930b417243f021b6c2b2ca371.

The [builder](build_package.py) generates both Word documents, Table 1, standalone data copies and the archive directly from committed inputs. Run it from this repository with python-docx installed. PDF rendering is separate. The [archive checker](verify_archive.py) accepts --work NEW_DIRECTORY and --report REPORT_PATH. Original Markdown sources remain editable; table placeholders are populated by the builder rather than manually transcribed.

## Review boundary

The [venue and citation record](venue-and-citations.json) records current formatting requirements and primary-source claim boundaries. The main text is 423 words, the abstract 78 words, with one main table and two supporting tables. No new whole-transcriptome analysis, biological experiment, journal submission, public preprint update or release object is part of this package. Scientific review, rendered-page inspection and repository gate receipts must be read with their recorded scope; the package is not a claim that every publication-approval condition has been satisfied.
