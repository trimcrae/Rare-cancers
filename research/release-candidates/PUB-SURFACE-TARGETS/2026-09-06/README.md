---
id: DOC-EMC-TISSUE-RNA-RELEASE-20260906
title: Tissue RNA preprint and reproducibility package
kind: runbook
status: live
date: 2026-09-06
last_verified: 2026-09-06
purpose: Identify the exact outgoing article, supplement, source package and release evidence.
scope: Qualified fixed-panel CSPG4 tissue-validation preprint; no clinical or publication claim.
audience: [maintainers, collaborators, external reviewers]
---

The reader document is `emc-tissue-rna-prioritization-submission.pdf`: seven article pages followed by four pages of supplementary information. Component PDFs and editable Markdown are in `research/manuscripts/surface-targets/`. All eleven outgoing pages were visually inspected. `final-outgoing-manifest.json` identifies exact outgoing bytes.

`emc-tissue-rna-code-data-supplement.zip` is the actual code/data supplement. Extract it to a new directory and follow its README for the pinned Python environment and offline replay command. It includes source hashes, specimen/probe mappings, protocols, all-panel results, reproduction code, normal/PRAME context and historical 3SEQ support. Source-specific rights and retrieval notes are inside; the author's proposed article license does not override third-party rights. The numerical replay is portable with its pinned runtime. The optional figure-generation adapter requires a Git checkout; the original inspected figures are also included.

The independent scientific ultra review is under `ultra-review/`, with its original report, frozen input manifest and actual dispatch/completion records preserved. Maintenance finding M1 is repaired without changing six actual figures; optional E1 was deferred with reasons. Final focused verification is supported; the full candidate gate is pending at this checkpoint; a prepared file is not yet a declaration that the publication bar is green.

`aixiv-metadata.proposed.json` prepares the service's title, abstract, author, category and keywords. aiXiv's verified interface takes one PDF; no ZIP attachment route was established. Deliver or deposit the actual code/data supplement with a submission and record its real location before claiming public availability. No new deposit DOI or public analysis URL is asserted here. Funding and competing-interest declarations remain unsupplied; no no-conflict or no-funding attestation was invented. No posting was performed.
