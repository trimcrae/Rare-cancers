---
id: DOC-PUB-ASO-READABLE-20260928-README
title: "ASO letter rewritten for clarity"
kind: runbook
status: live
date: 2026-09-28
last_verified: 2026-09-28
purpose: Bind the readable author review letter to the unchanged scientific evidence.
scope: Narrative revision and GitHub proofreading copy only.
audience: [maintainers, external reviewers]
---

# ASO letter rewritten for clarity

The author asked for a coherent explanation of the science, with the former draft's density as an example of the problem rather than a checklist of edits. This revision develops the question first, follows the evidence through the two findings, and then explains their significance and limits. It is a replacement author-review narrative, not a separate lay summary or a new scientific investigation.

`letter.md` is the source. `ASO-letter.docx` and `ASO-letter.pdf` are the author-review files. `build_letter.py` reuses the accepted September 27 document builder and excludes repository frontmatter from the document. One layout change keeps paragraphs together across page breaks. The builder requires python-docx. Final output counts and hashes are in `build-report.json` and `editorial-verification.json`.

The prior GitHub proofreading version at commit `ee77c1cb6f0d854b11238a27c4c5afafe19e4e13` remains intact in `2026-09-27-concise/`. The accepted scientific candidate is `840e567796e27ee0d95e6da68d55a269dcd51e40`. Scientific inputs, calculations, source evidence and conclusions are unchanged. References 2 and 3 have been renumbered to follow their new order of appearance; the underlying sources are unchanged.

## Supporting evidence

The accepted eight-page Supplementary Methods remains unchanged. Its source is `2026-09-26/supplementary-methods.md`. It already contains every detail omitted from the shorter narrative:

- Sections S1 and S2 distinguish deposited fusion sequences, reference reconstructions and unresolved observations, with exact transcript identifiers and coordinates.
- Section S3 supplies the design architecture, all binding positions, complete normal-reference counts, exact sequences, tied matches, hypothetical controls and cutoff sensitivity. The former ten-base criterion remains explicitly unvalidated.
- Section S4 preserves the unsuccessful partial, nonrandom sequencing-read search and its limits. No negative evidence was discarded or treated as a confirmation.
- Sections S5 and S7 explain the relationship to the preceding catalogue, the interpretation corrections and the remaining patient-sequence gaps.

The existing supplementary data ZIP and [versioned data and code archive](https://doi.org/10.5281/zenodo.22986104) remain the reproducibility record. They are reused without copying large archives or rerunning accepted analyses.

## Verification and scope

One independent read-only advisor reviewed the new narrative for reader comprehension and scientific fidelity. The only requested repair was citation ordering. Root corrected that ordering, checked source-to-Word text identity and visually inspected both final rendered pages. The accepted ultra review and prior full scientific verification are retained for unchanged science only; they are not represented as new checks of this editorial version.

Exact review and render bindings are recorded in `editorial-verification.json`. External ownership, rendering and coordinator receipts are under `work/aso-readable-format-20260928/` in the orchestrator workspace. The coordinator performs the applicable normal document gate, commit, GitHub push and public-file verification after root freezes the draft.

This work updates only the GitHub proofreading copy. Final author review, journal and article-type selection, current other-journal consideration and journal submission authorization remain separate. No journal submission, provider preprint update or data-deposit change is authorized by this revision.
