---
id: DOC-PUB-ASO-CONCISE-20260927-README
title: "Concise ASO letter revision"
kind: runbook
status: live
date: 2026-09-27
last_verified: 2026-09-27
purpose: Describe the concise editorial candidate and its accepted scientific inputs.
scope: Author-review format revision and preserved supporting evidence.
audience: [maintainers, external reviewers]
---

# Concise ASO letter revision

This is an editorial condensation of the accepted September 26 candidate at commit `840e567796e27ee0d95e6da68d55a269dcd51e40`, prompted by the author's September 27 short-format instruction and Cancer Genetics editorial precedent. It replaces the main presentation for author review, without changing scientific inputs or results. The original candidate, private uploads and published dataset remain preserved.

- `letter.md` is the editable narrative source; `ASO-letter.docx` is the generated author-review document.
- `build_letter.py` reproduces the Word document with python-docx; `build-report.json` records counts and hashes. A rebuilt ZIP container may have different byte hashes despite identical content.
- `venue-format.md` records the short-format decision and exact journal uncertainties. The former CBC full-article recommendation is superseded for this presentation.
- `editorial-verification.json` records the read-only advisor check, final text-preservation check, visual inspection and unchanged supporting-file bindings.
- Detailed methods remain in the accepted `2026-09-26/supplementary-methods.md` and the unchanged eight-page `ASO-supplementary-methods.docx`. No supplementary cross-reference edit was needed: section numbers are independent and all former main tables are already reproduced there.
- The existing `ASO-supplementary-data.zip` and [versioned public data and code](https://doi.org/10.5281/zenodo.22986104) remain the reproducibility record. Large files are reused from the frozen source checkout rather than duplicated here.

The original 1,360-word main prose is reduced substantially. Actual new counts and pagination are recorded in the build and verification files. This is a complete short author-review narrative, not a representation that a venue-specific submission package or an exclusive-consideration declaration is ready. Author approval and journal submission were not performed.

## Review reuse

The completed independent ultra review and exact-revision full verification of the scientific candidate remain applicable to unchanged science. The new focused advisor pass checks only whether condensation distorts claims, citations or limitations. No scientific analysis or broad test suite was rerun. Canonical DOCX rendering and an all-page visual inspection validate only the new document layout.

External render and ownership receipts are held under `work/aso-concise-format-20260927/` in the orchestrator workspace. The coordinator owns integration and shared status; this writer changes only this new candidate directory.
