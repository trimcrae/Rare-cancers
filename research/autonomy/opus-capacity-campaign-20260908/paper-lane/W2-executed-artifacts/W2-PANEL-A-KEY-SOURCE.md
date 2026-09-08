# W2 — what Panel A's dashed boxes and ticks encode, from the committed generator and its data

Worker W2, EMC capacity campaign, paper lane. Read-only. Nothing shared was written.
No figure regenerated, no image opened, no manuscript edited.

Start: `date -u` = 2026-09-08T11:55:49Z; `git rev-parse HEAD` = `f5a16b5bd571df8ae56964e40f3248eccddb9276`;
`git status --porcelain` = empty.

Contract's pinned input revision is `c365b4e836358274703cef278417193f615629f3`.
`git diff --stat c365b4e8 HEAD -- research/manuscripts/figures/emc_fusion_frame_figure.py` = empty:
the generator is byte-identical at the pinned revision and at HEAD, so line numbers below hold for both.

---

## 1 · The ticks — generator lines and data fields

`research/manuscripts/figures/emc_fusion_frame_figure.py`

    118  def protein(y, name, length, ticks, boxes, note=None):
    119      axA.add_patch(Rectangle((0, y), length, bar_h, facecolor=PALE, edgecolor=INK, lw=0.9))
    120      for t in ticks:
    121          axA.plot([t, t], [y, y + bar_h], color=INK, lw=0.55, solid_capstyle="butt")

    130  protein(9.62, "EWSR1", 656, rg["EWSR1"]["rg_positions"], [(300, 332), (455, 638)], "30 RG")
    131  protein(8.72, "TAF15", 592, rg["TAF15"]["rg_positions"], [(326, 572)], "31 RG")

    140  for t in rg["NR4A3"]["rg_positions"]:
    141      axA.plot([t, t], [yn, yn + bar_h], color=INK, lw=0.55)

    166  for label, parent, cut, note in cuts:
    ...
    168      for t in rg[parent]["rg_positions"]:
    169          if t <= cut:
    170              axA.plot([t, t], [y, y + bar_h], color=INK, lw=0.55, solid_capstyle="butt")

`rg` is bound at line 93: `rg = extra["composition"]["rg_content"]`, where `extra` is
`research/modalities/emc-fet-frame-and-composition.json` (SOURCES[2], lines 40-44, 52-56).

The data field is therefore `composition.rg_content.<PROTEIN>.rg_positions`. Its producer defines it:

`research/modalities/emc_fet_frame_and_composition.py`

     90  def rg_positions(seq: str):
     91      """1-based positions of the first residue of every RG dipeptide."""
     92      return [m.start() + 1 for m in re.finditer("(?=RG)", seq)]
    330      name: {"rg_dipeptides": len(rg_positions(seq)),
    331             "rg_positions": rg_positions(seq)}

Verified by recomputation from the committed sequences in
`research/modalities/emc-construct-inputs.json` (`uniprot_sequences`): the recomputed
`[m.start()+1 for m in re.finditer("(?=RG)", seq)]` equals the committed `rg_positions` exactly for
EWSR1 (n=30), TAF15 (n=31) and NR4A3 (n=2). Committed NR4A3 positions are `[371, 508]`.

**Established:** a Panel A tick is drawn at the 1-based residue index of the **arginine of an RG
dipeptide** (overlapping matches counted). One tick = one RG dipeptide. In the fusion rows the same
positions are drawn, filtered to `t <= cut` (line 169), which is exactly the "N of M RG" text on each
row.

## 2 · The dashed boxes — generator lines and data fields

    118  def protein(y, name, length, ticks, boxes, note=None):
    ...
    122      for b0, b1 in boxes:
    123          axA.add_patch(Rectangle((b0, y - 0.13), b1 - b0, bar_h + 0.26, facecolor="none",
    124                                  edgecolor=INK, lw=1.3, linestyle=(0, (3, 1.6))))

    130  protein(9.62, "EWSR1", 656, ..., [(300, 332), (455, 638)], "30 RG")
    131  protein(8.72, "TAF15", 592, ..., [(326, 572)], "31 RG")

⚠ **The box coordinates are hard-coded literals in the generator; they are not read from any file.**
The generator reads no box field at all. Their provenance is by numeric identity only:

`research/modalities/emc-fet-construct-designs.json`, `rgg_boxes_operational`:

    1461      "rgg_boxes_operational": [
    1462       {
    1463        "start": 300,
    1464        "end": 332,
    1465        "n_RG": 8
    1466       },
    1467       {
    1468        "start": 455,
    1469        "end": 638,
                "n_RG": 22
           }]                                  (construct "GFP-EWSR1 (full length)")

    1482      "rgg_boxes_operational": [
    1483       {
    1484        "start": 326,
    1485        "end": 572,
    1486        "n_RG": 26
    1487       }
    1488      ],                                 (construct "GFP-TAF15 (full length)")

    1498      "rgg_boxes_operational": [],       (construct "GFP-NR4A3 (full length)")

The generator's literals match these three entries exactly, and NR4A3 — whose committed list is
empty — gets no box drawn (lines 134-150 contain no `Rectangle(... linestyle=...)` dashed call).

The operational definition behind those spans, `research/modalities/emc_fet_idr_census.py`:

    108  # An RGG box is a window dense in RG dipeptides. The literature definition is qualitative ("RGG-rich
    109  # domain"); this makes it countable. Both parameters are declared and echoed into the artifact.
    110  RGG_WINDOW = 60          # residues
    111  RGG_MIN_RG_IN_WINDOW = 6  # >= this many RG dipeptides in the window opens a box

    162  def rgg_boxes(seq):
    163      """Windows dense in RG dipeptides, merged into boxes. Returns 1-based inclusive spans."""
    ...
    186          # A box starts at its FIRST RG, not at the sliding window's left edge. ...
    189          out.append({"start": inside[0] + 1, "end": min(inside[-1] + 3, len(seq)),
    190                      "n_RG": len(inside)})

Recomputing `rgg_boxes` from the committed sequences reproduces the same spans:
EWSR1 `[(300,332,8),(455,638,22)]`, TAF15 `[(326,572,26)]`, NR4A3 `[]`.

The artifact also states, in `emc-fet-construct-designs.json:1518`, why the box count is not the
paper's axis:

    "_why_not_count_RGG_DOMAINS": "the source names 3 RGG-rich domains in EWSR1; the census's
     operational box-finder merges them into 2 boxes on this sequence. Rather than tune the box
     definition until it returns 3 ... the axis is the underlying RG count, which needs no definition
     at all. The box count is reported for context only."

**Established:** a dashed box is the **operationally defined RGG box** — a maximal merged run of
60-residue windows each containing >= 6 RG dipeptides, trimmed to start at its first RG and to end
two residues past its last RG. It is *not* a literature-annotated RGG domain, and the repository
itself records that this finder returns 2 boxes on EWSR1 where the source paper names 3 domains.

## 3 · What the code establishes vs. what it leaves open

**Establishes**
- Tick semantics and their exact data field (§1), including the fusion-row filter `t <= cut`.
- Box semantics, the two parameters that define them, and that the drawn spans equal the committed
  `rgg_boxes_operational` for EWSR1/TAF15 and the empty list for NR4A3.
- That the figure contains **no key-drawing code**: there is no `legend()`, no proxy handle, and no
  text object naming "RG", "RGG", "dipeptide" or "box" anywhere in Panel A other than the row-end
  strings `"30 RG"`, `"31 RG"`, `"2 RG"` (lines 130, 131, 143) and the per-fusion `"N of M RG"`
  strings (line 173). U1's "no key or legend anywhere in the figure" is confirmed from the code side.
- That Panel A contains **four different weights of vertical black line**, none of them keyed:
  RG ticks `lw=0.55` (121, 141, 170), dashed box outline `lw=1.3` (124), fusion end-cap `lw=1.1`
  (171), and the single `C166` marker `lw=1.6` (144).

**Leaves open (UNRESOLVED)**
- **Whether the drawn box coordinates are still current.** They are hard-coded, so the provenance
  mechanism at lines 67-82 — which hashes only the three source files — cannot detect a divergence
  between `rgg_boxes_operational` and the literals at lines 130-131. Today they agree; nothing in the
  committed code enforces that. This is a stale-figure risk, recorded, not repaired here (no shared
  write in scope).
- **Legibility.** Code shows intent only. Whether a 0.55-lw tick at 300 and one at 302 resolve as two
  ticks at print size is not settled by the code and I did not open the image.
- **Provenance of the box concept for a reader.** The generator's own docstring calls them "the
  operational RGG boxes" (line 10), but that phrase is in the .py file, not in the figure and not
  (as far as this task establishes) in the manuscript caption. Whether the caption already carries
  wording is outside this task's inputs: UNRESOLVED here.

## 4 · Where the code agrees with U1's pixels, and where it does not

| U1 pixel observation | code | verdict |
|---|---|---|
| ticks inside EWSR1 and TAF15 bars, irregular and clustered | lines 120-121 driven by `rg_positions` | **agree**; U1's inference "RG dipeptides" is now sourced |
| two dashed boxes on EWSR1, ~295-330 and ~455-640 | literals `(300,332)`, `(455,638)` | **agree** within U1's stated estimation error |
| one dashed box on TAF15, ~325-570 | literal `(326,572)` | **agree** |
| dashed boxes are unlabelled | no legend/label code exists | **agree** |
| `C166` above the NR4A3 bar, tick on the NR4A3 bar | lines 144-145 draw it at x=166 on the NR4A3 row | **agree** |
| NR4A3 bar subdivided; the dark block "is itself split by an internal vertical line" | line 141 draws NR4A3 RG ticks at 371 and 508; the LBD block spans 373-626 (lines 136-139, `lbd_start`=373) | **agree** for the 508 tick |
| U1 reports ticks "inside the EWSR1 and TAF15 bars" and does not report a distinct tick on NR4A3 at ~371 | line 141 does draw one at 371 | **does not agree / UNRESOLVED.** Residue 371 is 2 residues left of the zinc-finger/LBD block boundary at 373, whose `lw=0.9` edge is drawn over the same region. Whether the tick is occluded, merged with that edge, or simply below U1's reporting threshold is not decidable from code, and I did not re-open the image. |
| ticks are absent from the NR4A3 bar as a *category* | code draws them | **do not state** that NR4A3 has no RG ticks in any caption |

## 5 · Proposed minimal caption/key wording

Justified sentence-for-sentence by §1-§2. It adds no biological claim, names no efficacy, and
asserts nothing about legibility.

> **Panel A.** Bars are drawn to residue scale on the shared axis. Each thin vertical tick marks one
> RG dipeptide, at the 1-based position of its arginine
> (`emc-fet-frame-and-composition.json`, `composition.rg_content.<protein>.rg_positions`); the count
> printed at the right of each wild-type bar is that protein's total. Dashed rectangles mark
> operationally defined RGG boxes — maximal merged runs of 60-residue windows containing at least six
> RG dipeptides, trimmed to the first and last RG they contain (`emc_fet_idr_census.py`,
> `RGG_WINDOW = 60`, `RGG_MIN_RG_IN_WINDOW = 6`); the spans drawn are
> `rgg_boxes_operational` in `emc-fet-construct-designs.json`. This finder returns two boxes on
> EWSR1 and one on TAF15; the source paper names three RGG-rich domains in EWSR1, and the box
> definition was deliberately not tuned to reproduce that count. NR4A3 has no box because the finder
> returns none for it; its two RG ticks are drawn nonetheless. Below the dotted rule, each fusion row
> shows the retained 5' segment ending at a heavy end-cap at its breakpoint, carrying only the RG
> ticks at or before that breakpoint; the right-hand text gives the retained residue range and the
> retained-of-total RG count.

Two items the caption alone cannot fix, for whoever integrates it:
1. Four vertical-line weights in Panel A carry four meanings (RG tick, box outline, breakpoint
   end-cap, `C166`). The caption above names all four, but a reader must distinguish them by weight;
   whether that is legible at print size is **UNRESOLVED** and would need a pixel check, not a code
   check.
2. The box spans are hard-coded at generator lines 130-131 and are not covered by the provenance
   hash. Recommend (not done here) that the generator read `rgg_boxes_operational` instead.

End: recorded in `W2-END-STATE.txt`.
