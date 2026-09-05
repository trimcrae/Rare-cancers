---
id: DOC-PUB-ASO-NAT-CANDIDATE-PACKAGE-2026-09-04
title: ASO NAT candidate package
kind: memo
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Preserve a shortened, rendered ASO candidate for author review.
scope: Candidate source and layout verification; not submission or release authority.
audience: [maintainers, external reviewers]
---

# ASO manuscript for Nucleic Acid Therapeutics

This is the condensed journal submission package, prepared separately from the historical canonical article and Qeios v2. It has not been submitted to the journal. The manuscript has **2,251 main-text words, a 200-word abstract, 24 references, two tables and one figure**. It is approximately 41% shorter than the 3,803-word canonical journal text.

Use [the submission instructions](submission/README.md) and [upload manifest](submission/upload-manifest.json) for the individual files. [candidate.pdf](candidate.pdf) is a six-page author preview; the double-spaced Word files are the journal manuscript. The preview does not determine typeset pages or fees.

The final focused science review resolves two unsupported interpretations: the unmodified DNA:RNA calculation does not establish a lower temperature bound for LNA/phosphorothioate chemistry, and the reported cell-model exon labels require nucleotide-junction confirmation. The manuscript also retains the exact genomic-hit disclosure, the limited scope of the computational framework step, the natural-log variance assumption, negative results and research-only limitations. The numerical sequence records and scientific tables are unchanged apart from explanatory labels. GPT-6-Astra assistance and the author's previously declared nonfinancial interest are disclosed.

The [focused review](submission/focused-science-review.json) is independent of manuscript authoring, but not blind. It uses the completed round-34 work as a baseline; it does not transfer a historical automated publication approval to these new bytes. The [disclosure delta](submission/disclosure-delta-review.json) verifies that the only subsequent source change carries forward an existing declaration. Read [verification.json](verification.json) for exact evidence, limits and repository-check status. This manual journal package is not an automated publish_bar receipt, and PUB-ASO remains excluded from automatic aiXiv posting.

The public archive at [Zenodo](https://doi.org/10.5281/zenodo.22229096) is the preceding analysis. Its downloaded ZIP matches the public checksum, and all 782 CSV data rows match this revision. The corrected interpretation travels with Supplementary Files 1 and 2; the archive is not represented as a new deposition of this manuscript.

To rebuild data, run `python research/release-candidates/PUB-ASO/2026-09-04/build_data.py` from this checkout. To rebuild the preview, run `build_candidate.py` with Python, pypdf and Chromium; `--html-only` generates HTML. To rebuild the Word uploads, run `build_uploads.py --soffice PATH` with LibreOffice and python-docx. `build_revision_note.py` requires ReportLab. Builders record input/output hashes. Rebuilding an artifact requires renewing its visual verification and upload hashes.
