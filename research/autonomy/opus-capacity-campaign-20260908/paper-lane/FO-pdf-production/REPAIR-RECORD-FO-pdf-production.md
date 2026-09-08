# FO PDF production repair — parser/layout repair, two rebuilds, and what is still open

**2026-09-08. Owner: FO PDF production. Untracked working note. Nothing committed, nothing pushed.**
⛔ A rebuilt PDF is a **production artifact**. Nothing here asserts scientific readiness, efficacy,
safety, selectivity or clinical acceptance, and nothing here settles the Figure 4 estimand.

---

## 1 · The parser/layout repair

Four defects were found. Two are the ones root observed; two more were found by rasterising pages
during QA of the repair. All four are **renderer/layout**, and none of them is a scientific finding.

### 1.1 The five panels were never wired up (root's defect, journal pp. 8–9 / manuscript pp. 17–19)

`inline()` has no image rule, and the `fusion-output` registry entry did not set `inline_images`.
Every `![Figure N](../figures/figN-….png)` therefore reached the page as a stray `!` and a blue
hyperlink to a file that does not travel with the deposit — `!Figure 1` … `!Figure 5`, printed
above five legends describing panels that were not on the page.

Root's independent stamp reading corroborates it from the provenance side: **both f44 FO stamps
list only the markdown and no figure at all**, while both Vaccine stamps list their two SVGs. The
FO build never registered a figure because it never rendered one.

**Repair (registry, not new machinery):** `fusion-output` now sets `"inline_images": True`, the
same opt-in `atr-panel-ask` already uses; the five PNGs are added to `stamp_sources`, because
`figures` is legitimately empty for this paper and `_write_build_stamp` hashes only those two
places; and `layout: {"raster_full_width": True}` gives the panels both columns in the journal
build. The width is an aspect-ratio fact about these five files — 3261×1904, 3921×1351, 3291×1474,
4582×1455 and 2635×1538 px, i.e. 1.71 to 3.15 times as wide as tall — so in an 88 mm column
Figure 4 would print about 28 mm tall.

### 1.2 A list item was parsed one source line at a time (root's `**` leak)

`markdown_to_html`'s list branch called `inline()` on the marker line and then **again** on each
continuation line, splicing the second result into the `<li>` the first had already closed.
`inline()` is a whole-string parser — its emphasis rules carry `re.S` exactly so a span may cross a
line break — so **every span that wrapped became unclosable and its markup printed**.

Root saw it in Discussion 4.2. It was wider than that: **nine bold pairs across the two formats**
(§2.2, §2.4 twice, §3.11, §4.2 twice, plus the italic/bold `***ENO3* … carcinoma.**` opener). And
bold is only where it was *visible* — measured against the pre-fix builder, a wrapped link printed
as literal `[text](` plus a bare URL and a wrapped code span printed its backticks
(`evidence/11-fixture-fails-against-prefix-builder-attempt2.txt`).

**Repair:** the item's marker line and its continuation lines are collected first, joined with the
same single space the old code spliced with, and `inline()` is called **once** on the whole item —
the shape the paragraph and blockquote branches already had. An item with no wrapped markup renders
exactly as before.

### 1.3 Table 9 (found during QA) — clipped in the shipped build, overprinting after the reflow

Table 9 is **seven** columns; `LANDSCAPE_MIN_COLS` is 8, so `render_table`'s `wide_body` rescue
never fired and it set at full body width inside an 88 mm column.

- **In the shipped f44 journal PDF** it sat in column two and its last column, `SEMA3C`, ran off
  the right edge: **nine `n, p = …` occupancy readings that §3.11 argues from were not on the page
  and not in the text layer.**
- **After the panels reflowed the page** it sat in column one instead, and the same overflow
  printed straight over the prose beside it.

Same defect, two symptoms. **Repair:** `full_width_tables: ("Table 9.",)` — the mechanism the ATR
package's Supplementary Table S3 already uses.

### 1.4 Table 3 (found during QA) — pre-existing, not caused by this repair

Five columns, again under the threshold. Its `citation` column is **cut at the text measure** in
the shipped build as well as this one: rasterised and zoomed, "Brenca *et al.*, *J* " is cut
mid-glyph and "2019;249(1):90" loses its en-dash and "101" — in this build the en-dash stopped
reaching the text layer at all. **Repair:** the same declaration, `"Table 3."`.

⚠ `test_a_display_item_cell_is_not_clipped.py` exists for exactly this defect class and is scoped
**to the ASO builds by name**, so it could never have seen either table.

### 1.5 Source-format syntax — the two changes, and the proof no prose moved

Two mechanical changes to `nr4a3-fusion-transcriptional-output.md`, both required by the repair:

1. **Alt text.** The alt text is the caption the image carries into the PDF's text layer; `Figure 1`
   is a label, not a caption. Each image now carries **its own legend's title sentence, copied
   verbatim** (emphasis markers dropped — an alt attribute is plain text). No new words.
2. **The five legends were blockquotes.** They rendered as centred quotes with none of the
   repository's legend break rules, so a legend had nothing keeping it with its panel. The `> `
   prefixes are removed on all 42 lines; the legends are now paragraphs, which
   `markdown_to_html` gives `class="legend"`. **Not one word changed.**

**Shown, not asserted** (`evidence/21-source-prose-is-unchanged.txt`): with the image lines
collapsed to a marker and the `> ` prefixes stripped, the **word stream is identical** —
19,598 tokens before, 19,598 after, `IDENTICAL word stream: True`.

⛔ No scientific text, no number, no figure byte. `git status --porcelain research/manuscripts/figures/`
is **empty**: the five original PNGs are untouched and are what the deposit embeds.

---

## 2 · The unchanged scientific content, shown

`evidence/75-FINAL-text-layer-before-after-diff.txt` diffs the extracted text of the f44 PDFs
against the rebuilt ones, with the running furniture and the provenance stamp removed. Every
difference is one of four things:

| what differs | why |
|---|---|
| `**five … samples**` → `five … samples` (×9 pairs) | the literal markers that used to print |
| `!Figure 1` … `!Figure 5` | the stray `!` and dead link, replaced by the panel |
| running page numbers, hyphenation splits | reflow |
| Table 9's `SEMA3C` column, Table 3's `90–101` / `83–93` | cells that were **cut off** and are now on the page |

**No sentence, number, statistic or claim differs.** The only content that *moved* moved from
"absent" to "present".

⛔ **Page counts are not content-equivalence.** The prior dated correction stands: page-count
equality is consistent with equivalence, never proof of it. Here the counts moved anyway —
journal 14 → 19, manuscript 30 → 33 — and that is expected: five panels and two full-width tables.

---

## 3 · The builds

⚠ **Three builds exist, not two, and the record says so.** The contract was one build per format.
Builds 1 and 2 were that. **Visual QA of build 1 then found §1.3's overprint on journal page 7**,
which the repair itself had caused, so a corrective build 3 was run. Every attempt is preserved in
its own file; no failure was overwritten and no build record was replaced.

| build | format | file | exit | HEAD | pages |
|---|---|---|---|---|---|
| B1 | journal | `builds/B1-journal.txt` | **0** | `5f40f49b4` | 16 |
| B2 | manuscript | `builds/B2-manuscript.txt` | **0** | `d5eb86e80` | 33 |
| B3 | journal | `builds/B3-corrective-journal.txt` | **0** | `1dc44e452` | **19** |
| B3 | manuscript | `builds/B3-corrective-manuscript.txt` | **0** | `1dc44e452` | **33** |

Command, unpiped, exit code from `$?`:
`python3 research/manuscripts/build_submission_pdf.py --paper fusion-output --style {journal,manuscript}`

### Identities

| artifact | bytes | sha256 |
|---|---:|---|
| journal, f44 original (**preserved**, `before/`) | 1,020,450 | `db31cba3a5f2916fecc25c404a9631e22d3564a06fcf053719796bf8d2ec932f` |
| journal, rebuilt | 2,151,011 | `ee8532e1cb60e06a62dd480b73b08ef1b8f4b27f3415788134273b56dbb043e3` |
| manuscript, f44 original (**preserved**, `before/`) | 968,545 | `781439631cc28a65c52f4caa6f665ad6bd78525f8e94ca1ad537bb897c4081ce` |
| manuscript, rebuilt | 2,090,720 | `796679340ab50e8b381f5e5c615841c6134bcd38489752efe5fae2f686614682` |

The size roughly doubles because five PNGs totalling 1.47 MB are now embedded as data URIs.

### The stamps — the requirement root imposed, met

Both rebuilt `.build-stamp.json` files now list **the markdown and all five rendered panels**, each
hash matching the file on disk (`evidence/30-…`, `after/*.build-stamp.json`). The f44 originals,
which list the markdown only, are collected read-only in `f44-stamps/` — **located, not rebuilt and
not fabricated**; both were present in that commit, so there is no absence to report.

### Honest cleanliness statement

- **Both stamps read `built from 1dc44e452, tree not clean at build time`, and that is true.**
  16 dirty entries at build time: my own uncommitted renderer, source and test edits, plus other
  owners' in-flight work in this shared tree. Nothing was rebuilt to obtain a nicer stamp.
- **The pair members agree** (same HEAD, same qualifier), which builds 1 and 2 did not — they
  straddled two parent commits. That inconsistency is the reason build 3 is a pair.
- **Pre-existing renderer noise, not silenced:** the seven-file "no deposited filename declared"
  warning and the two pypdf `DeprecationWarning`s. **New in these builds:**
  `Object count 4143 exceeds defined trailer size 4141`, a pypdf notice that appears once the
  embedded images enlarge the object table. Recorded, not suppressed; the exit code is 0 and the
  page count and text layer read correctly.

---

## 4 · Visual QA, actually performed

Rasterised with `ghostscript` (no `pdftoppm`, no `pdftotext` in this environment) and **read**:

| page | before | after |
|---|---|---|
| journal p9 (root's PNG) | `!Figure 4`, `!Figure 5`, `**It is not specific…**`, `**The surviving gene…**` | ✅ panels drawn, bold rendered, markers gone |
| manuscript p18 (root's PNG) | `!Figure 2` … `!Figure 5`, no panels | ✅ Figure 1 drawn with its legend directly under it |
| journal p3/p4 (Table 3) | citation column cut mid-glyph at the measure | ✅ spans both columns, `90–101` and `83–93` complete |
| journal p7/p8 (Table 9) | `SEMA3C` column off the page (before); overprinting the prose (build 1) | ✅ spans both columns, all nine readings legible |
| journal pp. 10–12 | — | ✅ Figures 1–5 full measure, legends beneath, no clipping or collision |
| manuscript pp. 18–22 | — | ✅ one panel per page with its legend; §4 opens under Figure 5 |

### Residuals — stated, not fixed

1. ⚠ **Figure 4's in-panel type is small even at full measure.** It is 3.15:1, so at 174 mm it
   stands ~55 mm tall and its per-cell statistics are near the bottom of what prints legibly.
   **Legibility is unverified**: nothing here was read at 100 %, and no figure was redrawn.
   The same caveat the ATR stylesheet already records applies with more force.
2. ⚠ In the journal build **Figure 1 sits at the foot of p10 with its legend continuing onto p11.**
   `break-inside: avoid` binds the figure, not figure-plus-legend.
3. ⚠ In manuscript style `figure.figure { break-before: page }` gives each panel its own page, so
   pp. 19–21 carry a panel, its legend and white space. That is the house rule for display items;
   it was not changed.
4. ⚠ **`test_a_display_item_cell_is_not_clipped.py` remains ASO-scoped.** A new FO-scoped fixture
   covers this paper; the general gap is named, not closed.

---

## 5 · Checks

All exit codes real, unpiped. Every attempt is its own file in `evidence/`; failures are kept.

- `74-renderer-guards-final-settled.txt` — **192 passed, EXIT=0** on the settled tree: the builder
  suite, both clipping guards, page-emptiness, text-layer order, display-item order, figure text,
  truncation, justification, page budget, code spans, and the three new fixtures.
- `11-fixture-fails-against-prefix-builder-attempt2.txt` — the list fixture **fails against the
  pre-fix builder**, so it is a guard rather than a decoration.
- Preserved failures, each explained above: `13-` (two builder guards pinned to `next(...)`),
  `15-` (stale stamp before the rebuild), `51-`, `52-`, `54-` (three attempts at the new table
  fixture's own normalisation).
- ⛔ **`71-settled-tree-guards-final.txt` shows 87 failures, all in
  `test_fusion_partner_prose_matches_its_artifact.py`, and none of them is mine.** They are caused
  by **another owner's uncommitted edits** to `emc_fusion_partner_pooling.py`,
  `fusion-partner/emc-fusion-partner-pooling.json` and `-stratification.md` in this shared working
  tree. Proof: the same file passes **141 tests, EXIT=0** in a pristine worktree at the same HEAD
  (`73-fusion-partner-guard-on-pristine-HEAD.txt`). Reported, not touched.

### Two existing guards were generalised, not weakened

`test_an_opted_in_paper_emits_an_img_carrying_its_caption` and
`test_the_embedded_bytes_are_the_figure_file_itself` both read
`next(k for k in PAPERS if inline_images)` — the **first** opted-in paper — and hard-coded ATR's
filename. `fusion-output` sorts ahead of `atr-panel-ask`, so it would have silently *displaced* the
ATR deposit as the sole subject at the moment a second paper needed checking. Both now iterate
**every** opted-in paper and **every** panel, checking each embedded payload against the file that
paper's own manuscript names. Strictly more is checked than before.

---

## 6 · What is still open — the scientific hold

⚠ **The Figure 4 estimand HOLD is unresolved and is untouched by this work.** Embedding a panel
makes its legend readable; it does not settle what the panel estimates. Nothing in this repair
examined, defended or altered that question, and nothing here may be read as progress on it.

⛔ Fences honoured: **no Vaccine, ATR, ASO or corpus rebuild** — the accepted ATR and ASO PDFs are
untouched. No figure producer, no redraw, no scientific rerun, no dependency install, no network.
The root diagnostic page PNGs were used as **page QA evidence only** and never as a figure source.
There is no wet lab, and a rebuilt PDF establishes no efficacy, safety, selectivity or readiness.

---

## 7 · Exactly what this owner changed, for the integrator

**Mine — integrate these:**

| file | change |
|---|---|
| `research/manuscripts/build_submission_pdf.py` | §1.1–1.4: the list-item parse, and the `fusion-output` registry entry (`inline_images`, `stamp_sources`, `layout`) |
| `research/manuscripts/fusion-output/nr4a3-fusion-transcriptional-output.md` | §1.5 only: alt text, and `> ` removed from the five legends. **Word stream identical.** |
| `research/manuscripts/tests/test_build_submission_pdf.py` | two guards generalised from "the first opted-in paper" to every opted-in paper and every panel |
| `research/manuscripts/tests/test_a_wrapped_list_item_keeps_its_markup.py` | **new** |
| `research/manuscripts/tests/test_the_fusion_output_panels_reach_the_page.py` | **new** |
| `research/manuscripts/tests/test_the_fusion_output_tables_survive_their_column.py` | **new** |
| `…/nr4a3-fusion-transcriptional-output{,-manuscript}.pdf` and `.build-stamp.json` | the two rebuilds |
| `research/autonomy/…/paper-lane/FO-pdf-production/` | this record, `before/`, `after/`, `f44-stamps/`, `builds/`, `evidence/`, `visual-qa/` |

⛔ **Not mine — do not attribute or integrate as part of this repair.** The working tree also shows
`emc_fusion_partner_pooling.py`, `fusion-partner/emc-fusion-partner-pooling.json`,
`emc-fusion-partner-stratification.md` and `emc-fusion-partner-correction-register.md` modified.
Another owner is writing them in this shared tree; they are the cause of the 87 failures in §5 and
this owner did not touch them.

⛔ Nothing was committed and nothing was pushed.

---

## 8 · Addendum — the whitespace-blind check finished

`evidence/76-FINAL-squashed-content-diff.txt` compares the two formats with **every whitespace and
line break removed on both sides**, so reflow, moved hyphens and re-wrapped columns cannot register
as differences. It agrees with §2: the changes are deleted `**` / `*` / `***` markers, deleted
`!Figure N` links, moving page numbers, and **insertions only** of text that was previously cut off
the page — Table 9's `SEMA3C` header and its nine readings, and the `e` that restores `percentil`
to `percentile` at the measure edge.

⚠ **That file is truncated at 40 opcodes per format by its own generator** and is corroboration,
not the primary evidence. The untruncated comparison is
`evidence/75-FINAL-text-layer-before-after-diff.txt`.
