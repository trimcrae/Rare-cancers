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

## BLOCKED · M1, the figure-stamp provenance rebuild

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

## Not claimed

Full preflight was not run on this manuscript. No production PDF QA, no publish-bar step, no venue
action. `target_venue` remains as recorded; a proposal to change it exists as a separate diff and is
for ordinary root adjudication, not publication permission.
