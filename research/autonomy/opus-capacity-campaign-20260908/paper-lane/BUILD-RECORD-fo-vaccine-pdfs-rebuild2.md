# Corrective rebuild of the four PDF pairs — second build, and why it was needed

**2026-09-08. Built at HEAD `7c9a71dcb`, gate `git status --porcelain` = 0 dirty, no worker running.**

## Why a second build exists
The first build (`BUILD-RECORD-fo-vaccine-pdfs.md`) was gated on a clean tree and started clean, but
**the parent wrote an untracked note 4 ms after the first PDF finished**, so builds 2–4 stamped
"tree not clean at build time" while build 1 did not. The two fusion-output renders of one paper
therefore carried **disagreeing provenance lines** — the failure the renderer's own comment exists to
prevent. No stamp was false; they were inconsistent, and the cause was the parent's own write.

⛔ This is a provenance repair, not a content change and not a stamp replacement. The sources were
untouched between the two builds.

## The four builds
One invocation each, no pipes, real exit codes — all four `EXIT=0`.
`python3 research/manuscripts/build_submission_pdf.py --paper {fusion-output,vaccine-path} --style {journal,manuscript}`

| file | build 1 bytes | build 2 bytes | pages b1 -> b2 |
|---|---:|---:|---|
| fusion-output journal | 1020137 | see AFTER below | 14 -> 14 |
| fusion-output manuscript | 968734 | see AFTER below | 30 -> 30 |
| vaccine-path journal | 901331 | see AFTER below | 13 -> 13 |
| vaccine-path manuscript | 798024 | see AFTER below | 16 -> 16 |

**Page counts are identical across the two builds**, which is the check that content did not move —
only the provenance line did.

## Stamps now, read from page 1 of each file
All four read `built from 7c9a71dcb` with **no "tree not clean" qualifier**, and the pair members
agree:
- `Version of 2026-09-08 · typeset preview · built from 7c9a71dcb` (both journal renders)
- `Version of 2026-09-08 · submission format · built from 7c9a71dcb` (both manuscript renders)

## Fences honoured
⛔ ATR was not rebuilt — its `e218` PDF is accepted and unchanged. ⛔ No manuscript, artifact,
producer or stamp file was edited. ⛔ No stamp was replaced alone and no passing current-source stamp
was claimed from old bytes. ⛔ No broad suite, preflight, figure producer or network call.

⚠ These are **collected, not root-accepted**. Files existing is not acceptance, and no scientific
readiness, efficacy, safety or clinical claim follows from a rebuilt PDF.
