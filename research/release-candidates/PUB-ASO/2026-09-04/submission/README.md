---
id: DOC-PUB-ASO-NAT-SUBMISSION-SUPPORT-2026-09-04
title: ASO NAT submission support package
kind: memo
status: live
date: 2026-09-04
last_verified: 2026-09-04
purpose: Describe the shortest path from existing candidate files to a human-approved submission.
scope: Three source files for an unsubmitted draft; excludes scientific revision and external actions.
audience: [maintainers, external reviewers]
---

# NAT support package — unsubmitted draft

This package prepares a human decision. It records no submission, approval, portal answer or publication-readiness verdict. The inventory pins existing local bytes to the base revision and two working-tree edits recorded in `upload-manifest.json`.

1. **Freeze the current candidate bytes for drafting.** Use `../manuscript.md` with its companion references, tables, figure and sequence CSV, pinned by the manifest hashes. `../candidate.pdf` and `../candidate.html` are assembled previews; the candidate README records earlier checks. This repair did not rerender or inspect them. Author acceptance is not required to prepare and check explicitly unsubmitted draft variants.

2. **Generate and check unsubmitted draft upload variants next.** The manifest separates candidate sources/previews from existing canonical Word, anonymous PDF and print-figure artifacts. Their existence and hashes do not establish derivation from this candidate. From the frozen candidate bytes, create a separate title page, double-spaced Word manuscript with references/tables, and separate figure legends. Prepare/check an anonymized draft main file, including metadata and identifying links; confirm whether it is needed against the live review model at release. Validate one acceptable Figure 1 print variant against the candidate SVG, and confirm the CSV designation. No Word/PDF or anonymous candidate variant was generated here; the composed PDF is a preview, not a substitute for individual uploads.

3. **Track pending declarations and version history.** Keep unresolved declarations visibly marked while drafting proceeds. At the final upload-package decision, complete the marked assertions in `cover-letter.md`, including authorship, responsibility, conflicts, funding, ethics/consent, originality and concurrent consideration. The candidate author block and end matter supply the draft statements. `systems/graph/publications.json` (PUB-ASO.posted) records Qeios v1 on 27 August and v2 on 4 September 2026, DOI 10.32388/VL3LJR.2. This candidate is a later condensed revision; do not label it the deposited v2. Qeios changes remain the author's act. No reviewers have been selected; supply names and conflict checks only if the portal requires them or the author chooses them.

4. **Reconcile the archive and ordering record before final approval.** The candidate cites 10.5281/zenodo.22229096 for existing analyses, not this candidate revision. The existing preprint checklist, section 3-vii, documents drift including misleading absolute melting-temperature columns in the published CSV. Decide the frozen archive/version and exact corrected ordering record to accompany the accepted source; verify actual archive bytes and correction records before claiming they contain it. This task neither retrieved nor inspected an archive ZIP. Do not copy historical extended-report SI into NAT uploads. A laboratory reply and an actual future bench preregistration are not prerequisites for this computational proposal (candidate README; NAT revision checklist B3/B6).

5. **Review and approve the concrete final upload set.** Author review, completed declarations and fee decisions belong here, after draft generation and verification. At release time, check current NAT instructions, article type, portal designations, anonymity, fees and print-colour choice. The historical checklist and `research/manuscripts/SUBMISSION-PACKET.md` are planning sources, not current portal evidence. Remove draft markers and provenance notes only after author confirmation; review all generated files and the portal proof. The coordinator integrates and runs the normal gate once, followed by applicable final-release checks. Obtain the author's explicit journal-submission approval for the exact files and costs before submission: `research/autonomy/publication-authority.json` has no standing journal grant.

The manifest names and hashes existing local evidence. Missing variants have no invented paths or hashes. Hash checks establish byte identity only. The only work performed here is support-document preparation and focused integrity checks; no preflight, science suite, new scientific review, remote operation or background process was started.
