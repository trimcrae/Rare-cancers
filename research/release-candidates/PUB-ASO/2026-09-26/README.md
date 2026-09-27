---
id: DOC-PUB-ASO-CBC-CANDIDATE-20260926
title: Revised ASO submission candidate for CBC
kind: memo
status: live
date: 2026-09-26
last_verified: 2026-09-26
purpose: Identify the revised manuscript, evidence, validation and remaining submission actions.
scope: Manual local journal candidate; no submission or public update authorized by this record.
audience: [maintainers, external reviewers]
---

# Revised ASO submission candidate

Target journal: **Computational Biology and Chemistry**, Original Research, using the subscription route. The revised paper leads with a recovered reference correspondence for USZ20 and additional normal-parent isoform matches in 9 of 35 source-linked designs. It preserves USZ22 as unresolved and makes no experimental or therapeutic claim.

The editable main manuscript is submission/ASO-manuscript.docx. The supporting document is submission/ASO-supplementary-methods.docx. Supplementary Data is submission/ASO-supplementary-data.zip; it includes exact inputs, source receipts, 40 design rows with five hypothetical controls flagged, all matching locations, cutoff sensitivity and standard-library Python analysis. Separate highlights and a data-derived graphical abstract with caption are in the same directory. cover-letter.md is the editable letter draft. The generated PDFs are author previews, not replacements for the editable files.

The independent ultra review found no scientific submission blocker. ultra-review.json preserves the actual review response and runtime model/effort, and review-freeze.json identifies the originally reviewed bytes. The sole review finding was an omitted saved read-probe aggregate; repair-record.json documents its addition. Scientific bodies are unchanged by the repository metadata and layout repairs. Final validation and focused verification records identify their exact scope; an old canonical publication-bar result does not certify this candidate.

The historical manual ASO package at research/release-candidates/PUB-ASO/2026-09-04/README.md explicitly distinguished its files from automated publish_bar clearance. The present candidate uses the same separation: actual source and artifact evidence, a frozen ultra review, layout checks and exact-revision repository checks are reported individually. Gate logic, historical reviews and the canonical publication binding are preserved.

This is a substantive revision of the preceding resource, not another enlarged hypothetical catalogue. The main 35-design subset, original 190-design panel and 782-row historical CSV have different scopes. Seven deposited records identify five seams, not seven independent patients. The source investigation and read prefixes remain preserved at the original dated workspace; the journal supplement avoids duplicating 128 MiB of read prefixes and supplies their retrieval recipe and hashes instead.

Before submission, the author must review the final text, confirm any current consideration by another journal, and approve journal submission. The correspondence address was recovered from the author's September23 instruction and is included in the private journal copy. The publication-history check located Qeios versions1–4, including version4 posted September15 (10.32388/VL3LJR.4); the cover letter discloses that history. The recovered complete official guide specifies Option C: a repository deposit with citation/link remains required. repository-deposit/ records the prepared data-only package and verified upload to owned draft 22986104 under reserved DOI 10.5281/zenodo.22986104. Publication and public read-back remain pending. Publication of a qualifying version of the existing ASO data archive falls under the standing Zenodo grant and remains subject to the applicable identity, integrity and release checks. It does not require a new per-deposit approval. Exact public-release timing at initial journal submission is unverified. The cover letter omits an unverified exclusive-consideration declaration. Existing funding, financial-interest and nonfinancial-survivorship declarations are carried forward. No contact, journal submission or public preprint update has occurred. The dataset version is an unpublished draft under the existing ASO archive concept.

To reproduce the new sequence findings, unzip Supplementary Data, enter evidence/, and run python analyze.py with Python 3.11 or later. No third-party modules or network access are needed for that analysis. build_uploads.py rebuilds the Word files and graphical abstract using python-docx and Matplotlib. The original 64-MiB prefixes can optionally be fetched and replayed with python read_prefix_probe.py --fetch --mib 64, comparing the retrieved prefix hashes with the saved receipts.
