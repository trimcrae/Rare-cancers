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

## ⭐ CLEARED 2026-09-08 · registration in `build_submission_pdf.PAPERS`

**Resolved by option B2 — commit `0e542b84`.** Per-paper opt-in raster handling was added to the
existing builder, the paper is registered, and the production PDF and its build stamp are committed
alongside so the `committed_artifact` guard is green rather than armed-and-red. `pytest` over the
builder module: 110 passed, exit 0. The built PDF carries the figure on page 2 at full native
2220×2670 with its caption on the same page. Unflagged papers render byte-identically, reproduced by
the parent independently of the worker's report.

⭐ **CLOSED 2026-09-08 — the selected figure IS verified readable.** Root rendered and viewed all
nine pages of the outgoing PDF and accepted the full-width Figure 1. That settles legibility **for
the rendering that actually ships**, by inspection rather than by arithmetic.

⚠ **The historical failure stays on the record as history, not as an open item.** The journal-column
placement DID fail, measured at 3.03 pt tick labels and 2.71 pt smallest type, and that measurement
is why the full-width placement exists. It is not a live concern.

⚠ **The UNUSED manuscript-style variant's 5.42 pt smallest text remains unresolved and is NOT a
gate.** It is a different rendering that this paper does not ship. The 6 pt threshold behind that
figure is an **asserted readability convention, not a sourced venue rule**, and the venue guidelines
that might settle it return HTTP 403 from CI — an unresolved retrieval, not a route to work around.

### The block as it stood, retained

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

## The `target_venue` decision, and why it is not permission

**Settled 2026-09-08: `PUB-ATR-PANEL-ASK.target_venue` is `preprint`.** It was
`experimental_proposal`, briefly `journal_submission`, and is now `preprint` — the release endpoint
for the computational report that actually exists.

The manuscript's own editorial block rejects the proposal formats by name (Registered Report Stage 1
and Study Protocol on eligibility, Hypothesis/Perspective on fit) and declares Genes, Chromosomes and
Cancer, Research Article, with a bioRxiv preprint. That journal destination remains possible and its
history is preserved in the field's own dated correction; ⛔ **recording `preprint` here is NOT
current journal-submission permission**, and the intermediate `journal_submission` value should not
be read as having granted any.

⛔ **This is a settled graph field, not publication permission.**
`blocked_by: ["BLK-NO-WET-LAB"]` is unchanged and still blocks the unperformed experimental
programme; it was not cleared, and it must not be cleared to make a publication check pass. No
preflight, production PDF QA, publish-bar step or venue action has been performed, and none is
implied by this field.

A prose note beside the field was attempted and reverted: `publication.schema.json` sets
`additionalProperties: false` on a publication row, so `target_venue_note` is not schema-legal. The
rationale lives here instead. The edited row validates against the schema with no errors, and
`blocked_by: ["BLK-NO-WET-LAB"]` is unchanged.

## ⭐ CLEARED 2026-09-08 · `S3 clipped in outgoing PDF` — and a second defect found with it

**Resolved at `9ec78c4f`.** The reopening condition below was met: the rebuilt outgoing PDF was
rasterised and inspected, and S3 now carries all five columns — `Field`, the three EWSR1 types and
**TAF15_NR4A3** complete through `UNRESOLVED` — entirely within the page, with its continued table and
both tail notes on the same page. **Type size is unchanged**; the diff contains no font rule, which was
deliberate: the existing `.wide-body-table` class would have spanned *and* dropped to 6.4 pt, trading a
clipped column for an unreadable one in the same batch where a figure was widened for being too small.
128 of 128 S3 body cells are present in the rendered text.

⭐ **A second defect was found while fixing the first, and it was already shipping.** `render_table`'s
`cells()` split every row on every `|` and did not honour the markdown escape `\|`. S3 carries the
fusion seam as `TAKAAVEWFD\|DMPCVQAQYS`, so two 5-cell rows became 9-cell rows with a trailing
backslash printed — which is part of why the grid was wider than the page in the first place. The
parser now splits on unescaped pipes only. Blast radius was measured before touching a shared
function: escaped pipes appear in 2 rows of this paper and one each in two files that are no
registered paper's source. Unflagged papers remain byte-identical in both styles; the builder module
passes 110 tests.

⚠ The rebuilt PDF is 9 pages rather than 7, because narrowing those two rows changed the table's
geometry.

### The hold as it stood, retained

## ⛔ LEADING-PAPER HOLD, 2026-09-08: `S3 clipped in outgoing PDF`

Root visually inspected all seven pages of the outgoing PDF at `1cd34ea1`, sha256
`18e999a8e81a8b2e671040de69d108d468eeb20dd1de45e2f60f82149f4e7b73`.

⭐ **The page-3 full-width figure is READABLE AND ACCEPTED** for this computational preprint layout.
That closes the figure-legibility question for this PDF. The unused manuscript-style variant's
5.42 pt smallest text is NOT a gate for it; that variant's limitation is recorded honestly above and
is not a release requirement for a different output.

⛔ **One concrete production defect remains: Supplementary Table S3 on page 6 is too wide for the
right-hand column, and its TAF15 column is visibly clipped at the page edge.** Page 7 currently
carries only that table's tail note.

**Reopening condition, exactly:** a corrected actual proof of the rebuilt outgoing PDF in which every
source cell of S3 and its caption sit within the page bounds at unchanged type size. Not a
re-render, not a claim — an inspected proof. Type must not be shrunk to fit; that would trade this
defect for the one just fixed.

The repair is scoped to a full-width placement for this table behind this paper's own `PAPERS` entry,
using the stylesheet's existing `column-span: all` mechanism. It is not a table-layout refactor, and
two-column main tables that fit may stay where they are.

## Deposit metadata, corrected 2026-09-08

The outgoing PDF's `/Title` ended `[typeset preview]` and its `/Subject` said *"NOT the deposited
version — the file to cite and deposit is emc-atr-collaborator-package-manuscript.pdf"*. Both were
false for this paper: the journal-style render IS the selected outgoing file, and the manuscript-style
file it pointed at is not shipped, so a downloader following that instruction would look for something
that does not exist.

Corrected through a **per-paper opt-in** (`layout.is_outgoing_file`). The scientific title is
unchanged; the preview suffix and the misdirection are gone; the subject now reads *"Preprint
manuscript, not peer reviewed. This file is the outgoing version of this text and the only rendering
of it that is circulated."*

⛔ **No DOI, no publication date, and no claim that the file is deposited anywhere** — verified by
scanning the emitted subject for each. "Journal" remains this renderer's style name and carries no
journal-submission authority. Every other registered paper keeps the two-build wording, which is true
for them: `aso-journal`, `fusion-output` and `vaccine-path` all read `is_outgoing_file=None` and
retain `[typeset preview]`. Builder module: 110 passed.

## Current outgoing artifact, and the next release step

The outgoing PDF at `be39c96f` is sha256 `42a7c4eefff20d00…`, 9 pages. ⚠ **It is NOT the
`a11ae7c6…` build named in the S3 originals receipt** — that hash was the S3-repair build at
`9ec78c4f`, and the deposit-metadata correction rebuilt the file afterwards. Both are real builds of
the same scientific bytes; the receipt binds the earlier one and this record names the current one so
neither is mistaken for the other.

⛔ **The next release step is a candidate-bound FULL PREFLIGHT and `publish_bar` via the existing
authorized route** — not another review and not a broad unscoped baseline. It must not be started
against an unsettled candidate: the ATR focused verification is still running, and the deposit
metadata only just settled.

⚠ `systems_check.py --check` currently reports **2,394 ERROR / 271 WARN**. No full-preflight pass is
implied by any check recorded here.

## Not claimed

Full preflight was not run on this manuscript. No publish-bar step and no venue action.
`target_venue` is settled at `preprint` (above) — the earlier sentence here, saying a proposal to
change it was still unapplied, is superseded and was stale.

⚠ A production PDF has now been built and committed, and the figure was checked to be present on the
page with its caption — but **print-size legibility remains unverified**, which is the one open item
this record still carries.
