---
id: DOC-OPUS-CAMPAIGN-HOLD-ATR-RELEASE
title: "PUB-ATR-PANEL-ASK — paper-specific hold and its reopening conditions"
level: L4
kind: memo
status: live
purpose: >
  Record what is done on the ATR collaborator package's release path, what is blocked, and the exact
  condition under which each blocked item reopens, so no reader has to infer readiness from silence.
scope: >
  L4. Release path and provenance only. It changes no scientific claim, clears no blocker, and is not
  publication permission.
audience: [maintainers, external reviewers]
date: 2026-09-08
last_verified: 2026-09-08
---

# PUB-ATR-PANEL-ASK — paper-specific HOLD, and its exact reopening condition

Dated 2026-09-08. Written by the paper owner. This records what is done, what is blocked, and the
exact condition under which each blocked item reopens. It is not a review and asks for no decision
that has already been made.

## Done

- The one authorized repair batch from the completed final ultra review (U1, U2, U3, U4, E1, E2)
  is applied. Measured after: abstract 245 words, main 6,586, 1 figure, 5 tables, 6 display items,
  10 references. `lint_style` 0 ERROR across 15 files exit 0; `lint_consistency` 0 ERROR exit 0.
- Front matter is now in the shape `build_submission_pdf.parse_front_matter` requires. Verified by
  calling the builder's own functions: `declared_running_title` returns
  "NR4A3 fusion models and DSB predictions" and `parse_front_matter` returns all seven keys.
- ⚠ **The keywords line is newly authored.** Every term in it appears in the manuscript, but the
  selection and ordering are the owner's, not extracted from the document. It is submission
  metadata, not a scientific claim, and it is flagged here so nobody reads it as sourced.
- `PUB-ATR-PANEL-ASK`'s `what_it_would_claim` and `outcome_potential_why` are corrected to describe
  the computational report that exists rather than the experimental programme that has not been
  performed. Both keep the superseded sentence quoted verbatim behind a dated correction marker,
  because the publication schema sets `additionalProperties: false` and a new field for the old text
  is not schema-legal. `blocked_by: ["BLK-NO-WET-LAB"]` is unchanged. Views regenerated.

## ⭐ CLEARED 2026-09-08 · M1, the figure-stamp provenance rebuild

**The reopening condition below was met and the rebuild is done — commit `063ea1d5`.** The record of
the earlier block is kept beneath, unchanged, because how it was blocked is part of the evidence.

matplotlib 3.11.1 was already present, unpacked, in the uv archive cache at the cpython-311 ABI that
`/usr/bin/python3.11` uses. With those cached directories on `PYTHONPATH` it imports, along with
numpy 2.4.6 and pillow 12.3.0. `python3`'s import failure had not established that no available
runtime carried it. No package was downloaded, no pip attempt was repeated, and no TLS or proxy
control was touched.

ONE run of the existing committed generator from the same frozen scientific inputs, exit 0. The
regenerated PNG is **byte-identical** to the frozen one, `fa94675f…07a7`. Only the PDF (which carries
a creation timestamp) and the provenance stamps changed — so the plot was never stale and the finding
was a mis-recorded stamp, which is exactly what a rebuild can show and a re-stamp never could. All
three source stamps now equal their artifacts' raw sha256 prefixes. Visual QA performed on the
rendered PNG: three panels legible, Panel A's retained-segment rows and RG counts, Panel B's measured
band with its 0.000 and 1.000 anchors and three computed EMC points, Panel C's 177-nt / 59-codon
accounting, and no hue encoding.

⚠ This is release-provenance repair, not release completion. Nothing here is a preflight, a
production PDF QA, a publish-bar step or a venue action.

### The block as it stood, retained

All three stored source stamps in `research/manuscripts/figures/emc-atr-figure-provenance.json`
differ from the raw bytes of the artifacts they name. This is a provenance mismatch and is **not**
evidence that any plotted value is wrong.

The authorized repair is to run the existing committed generator once and take the outputs it
produces. That was attempted and **failed**:

```
$ python3 research/manuscripts/figures/emc_fusion_frame_figure.py
ModuleNotFoundError: No module named 'matplotlib'
GEN EXIT=1
$ python3 -m pip install matplotlib
ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

Two attempts, the second with `--timeout 120 --retries 3`, both timed out. `pypi.org` and
`files.pythonhosted.org` are in this environment's `no_proxy` list, so pip is going direct and the
direct route is not completing; the agent proxy's status page shows no policy denial for those hosts.

⛔ **The stamps were NOT re-written.** The provenance file's own `_why` says so in terms: "A number
changed in an artifact and not redrawn is a stale figure, and the fix is to redraw it, never to
re-stamp." Re-stamping without redrawing would convert a visible provenance mismatch into an
invisible one.

The original PNG, PDF and provenance JSON are retained unmodified, with hashes, at
`/tmp/claude-0/m1-lane/originals/`; the PNG is `fa94675f…07a7`, matching the frozen manifest.

**Reopening condition:** `matplotlib` importable in this environment. Then run
`python3 research/manuscripts/figures/emc_fusion_frame_figure.py` **once**, from the same frozen
scientific inputs, and take the PNG, PDF and stamp it produces; then the targeted provenance check
and a visual QA. No biological producer, no new alignment, no sweep.

## BLOCKED · registration in `build_submission_pdf.PAPERS`

The registration entry itself is prepared and applies cleanly. It is deliberately **not** applied,
for two measured reasons.

1. **The figure cannot render, at three independent points.** `markdown_to_html` has no image
   handling — measured, `IMG_TAGS: 0`, the inline image renders as a stray `!` plus a hyperlink.
   `split_figures` requires a `## Figure legends` section, which this manuscript does not have. And
   it splices an **SVG** in raw; the only artifacts are a 2220×2670 PNG and a PDF, and no SVG of
   this figure exists anywhere in the tree. Registering with `"figures": {}` would build a PDF that
   silently drops Figure 1 from a paper whose Results cite it.
2. **Registering arms a guard that would then be red.** The `committed_artifact` guard asserts that
   every registered paper's `out` path exists on disk. It cannot exist until the paper builds.

**Reopening condition:** a decision between (B2) an opt-in image rule in the builder, gated behind a
per-paper flag so no other registered paper's rendering changes, with a guard test and a
print-resolution decision for the raster; and (B3) a `## Figure legends` restructure plus a new SVG
artifact. Both touch either shared rendering code or the figure artifact, and neither is an
editorial change. Once one is chosen and built, register, commit the PDF and stamp, and the guard
goes green in that order.

## The `target_venue` change, and why it is not permission

`PUB-ATR-PANEL-ASK.target_venue` moved from `experimental_proposal` to `journal_submission` on
2026-09-08, in the same batch as the claim-field corrections, so that the computational report which
EXISTS is distinguishable in the graph from the experimental programme which has NOT been performed.

The manuscript's own editorial block rejects the proposal formats by name — Registered Report Stage 1
and Study Protocol on eligibility, Hypothesis/Perspective on fit — and then declares its venue as
Genes, Chromosomes and Cancer, Research Article, with a bioRxiv preprint. `preprint` is a defensible
alternative reading of the same block, since the report obtains its pre-commitment "by a dated
preprint carrying the prediction table"; `journal_submission` is chosen because it is what the block
declares, and the choice is recorded here rather than left implicit.

⛔ **This is a graph field for ordinary root adjudication and it is not publication permission.**
`blocked_by: ["BLK-NO-WET-LAB"]` is unchanged and still blocks the unperformed experimental
programme; it was not cleared, and it must not be cleared to make a publication check pass. No
preflight, production PDF QA, publish-bar step or venue action has been performed, and none is
implied by this field.

A prose note beside the field was attempted and reverted: `publication.schema.json` sets
`additionalProperties: false` on a publication row, so `target_venue_note` is not schema-legal. The
rationale lives here instead. The edited row validates against the schema with no errors.

## Not claimed

Full preflight was not run on this manuscript. No production PDF QA, no publish-bar step, no venue
action. `target_venue` remains as recorded; a proposal to change it exists as a separate diff and is
for ordinary root adjudication, not publication permission.
