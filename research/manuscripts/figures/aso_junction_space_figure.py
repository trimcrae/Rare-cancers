#!/usr/bin/env python3
"""Figure — the frame-compatible junction space across NR4A3 fusion partners.

WHAT IT HAS TO SHOW, AND WHY A TABLE DOES NOT. The result in §3.1 is that grading 207 donor-exon ×
acceptor-exon pairs leaves 32 emittable ones, and that the refusals are STRUCTURAL rather than
selective: NR4A3 exon 2 carries no coding sequence and is refused in every pair, exon 4 falls
outside the plausible resumption range in every pair, and so the entire surviving space is one
column. Stated as a number, "32 of 207" reads like a filter that happened to pass 15%. Drawn as a
grid, the shape is immediate: two columns are uniformly refused for a reason that has nothing to do
with any partner, and within the surviving column the pattern is a single arithmetic condition on
donor coding phase.

⛔ EVERY CELL IS READ FROM `nr4a3-fusion-junction-atlas.json`. Nothing is recomputed here — not the
grades, not the counts, not which pairs are emittable. A figure that re-derived its own grades could
disagree with the artifact the manuscript cites, silently.

⛔⛔ THE LAYOUT IS SIZED BACKWARDS FROM THE PRINTED PAGE, AND THAT IS THE WHOLE REASON IT CHANGED
(blind screen of the built PDF, 2026-08-17). The figure used to be one 760 × 1509 px column: the
renderers cap a figure's printed HEIGHT, so the binding limit was 218 mm of height, the scale came
out at 0.144 mm per SVG pixel, and the 9.5 px row labels printed at 3.88 pt with the in-figure notes
at 4.3 pt — below any size a reader can read and below every publisher's floor. The same cap left
the grid occupying about a fifth of the text width with the right two-thirds of the page blank.

⭐ THE FIX IS GEOMETRIC, NOT COSMETIC, because the data is three columns wide and seventy-seven rows
tall and no font size rescues that aspect ratio. The donor-exon blocks are laid out in TWO panels
side by side — the grid continued, the way a long list is set in two columns — which roughly halves
the height, lets the width bind instead, and brings every label to 6.6 pt or better in both built
styles and in the standalone deposit figure at 180 mm.

  ⚠ THE THREE ACCEPTOR COLUMNS REPEAT IN BOTH PANELS AND THE LEGEND'S READING SURVIVES THAT. The
  columns of this figure are the NR4A3 acceptor exons, of which there are three however the rows are
  arranged; the in-frame cells still fall under e3 and nowhere else, in both panels. Splitting on
  the ACCEPTOR axis would have destroyed that reading, so the split is on the donor axis only.

⚠ EVERY SIZE BELOW IS A PRINTED SIZE IN DISGUISE. `_check_type_sizes` converts each one through the
narrowest scale the three renderers produce and fails the build if anything lands under 6 pt, so a
future layout edit cannot quietly reintroduce the defect this rewrite exists for.

Dependency-free SVG. No matplotlib, no network.
"""
import json
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "modalities", "nr4a3-fusion-junction-atlas.json")
OUT = os.path.join(HERE, "aso-junction-space.svg")

GRADE_FILL = OrderedDict([
    ("EMITTABLE", ("#2e7d32", "frame-compatible, panel emitted")),
    ("OUT_OF_FRAME", ("#e0e0e0", "out of frame")),
    ("NON_CODING_ACCEPTOR", ("#bdbdbd", "acceptor exon carries no coding sequence")),
    ("SEAM_NOT_PRODUCED", ("#9e9e9e", "acceptor outside plausible resumption range")),
])

# --- geometry, in SVG pixels ------------------------------------------------------------------
#: Cells are WIDE and short. Height is the expensive axis — seventy-seven donor exons have to fit a
#: page — and width is the free one, so the grid spends the width it was previously leaving blank.
CELL_W, CELL_H = 100, 11
GAPX, GAPY = 5, 3
ROW_PITCH = CELL_H + GAPY
MARGIN = 36
LABEL_W = 30            #: the donor-exon label gutter, right-aligned against the grid
PANEL_GAP = 64
BLOCK_GAP = 10          #: between one partner's block and the next inside a panel
BLOCK_HEAD = 18         #: the partner name above its block

# --- type, in SVG pixels ----------------------------------------------------------------------
#: ⛔ 11 px IS THE FLOOR AND IT IS LOAD-BEARING. At the width the renderers give this canvas it
#: prints at 6.6–7.0 pt; anything smaller reintroduces the defect above. `_check_type_sizes` is
#: what makes that a check rather than a comment.
FS_TITLE, FS_SUB = 17, 13
FS_PARTNER, FS_COLHEAD, FS_AXIS = 13, 12, 12
FS_ROW, FS_LEGEND, FS_NOTE = 11, 11, 11
MIN_PRINTED_PT = 6.0

#: The three ways this SVG is printed, as (available width mm, height ceiling mm). Whichever limit
#: binds decides the scale, so the smallest of the three scales is the one every type size must
#: clear. ⚠ These mirror `build_submission_pdf.MANUSCRIPT_CSS` / `JOURNAL_CSS` and
#: `svg_to_submission_formats.DEFAULT_WIDTH_MM`; they are stated here because this file cannot
#: import them, and a change there that shrinks a figure must be reflected here or this check is
#: measuring a page nobody prints.
RENDER_TARGETS = {
    "manuscript style (174 mm text width, 218 mm ceiling)": (174.0, 218.0),
    "journal style (182 mm column span, 205 mm ceiling)": (182.0, 205.0),
    "standalone deposit figure (180 mm, 247 mm ceiling)": (180.0, 247.0),
}
MM_PER_PT = 25.4 / 72.0


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, max_px, font_px, char_px=0.52):
    """Greedy word wrap to a pixel width, in a font whose average advance is `char_px` em.

    ⚠ APPROXIMATE ON PURPOSE, AND SAFE IN THE ONE DIRECTION THAT MATTERS. 0.52 em is above the
    measured average for Liberation Sans lowercase prose, so a line that fits this estimate fits the
    rendered box. Over-estimating costs a line break; under-estimating would push text off the
    canvas, which is the failure this figure was already carrying at the bottom of the page.
    """
    limit = max(8, int(max_px / (font_px * char_px)))
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if len(trial) > limit and current:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def split_into_panels(blocks, n_panels=2):
    """Distribute the partner blocks over `n_panels` columns, in order, balancing height.

    ⛔ ORDER IS PRESERVED. The panels are a CONTINUATION of one grid, so a reader running down the
    left panel and on into the right meets the partners in the artifact's own order; re-sorting them
    to balance better would make the figure disagree with every table beside it.
    """
    heights = [BLOCK_HEAD + len(donors) * ROW_PITCH + BLOCK_GAP for _, donors in blocks]
    best, best_cost = None, None
    for cut in range(1, len(blocks)):
        left, right = sum(heights[:cut]), sum(heights[cut:])
        cost = max(left, right)
        if best_cost is None or cost < best_cost:
            best, best_cost = cut, cost
    if best is None:                                    # one block: nothing to split
        return [blocks]
    return [blocks[:best], blocks[best:]] if n_panels == 2 else [blocks]


def _check_type_sizes(width_px, height_px, sizes):
    """Fail the build if any label would print below `MIN_PRINTED_PT` in any of the three targets.

    ⛔ THIS IS THE INSTRUMENT THE DEFECT GOT PAST. Nothing measured printed type: the figure
    provenance check hashes the artifacts a figure is drawn from, the truncation test decodes the
    PNG, and the vector test reads the deposited PDF — none of them knows how big a label is once
    the renderer has scaled the canvas. So a legible SVG shipped as an illegible figure and every
    gate stayed green.
    """
    worst = None
    for name, (width_mm, height_mm) in RENDER_TARGETS.items():
        scale = min(width_mm / width_px, height_mm / height_px)      # mm per SVG pixel
        if worst is None or scale < worst[1]:
            worst = (name, scale)
    name, scale = worst
    printed = {label: px * scale / MM_PER_PT for label, px in sizes.items()}
    too_small = {k: v for k, v in printed.items() if v < MIN_PRINTED_PT}
    if too_small:
        detail = ", ".join(f"{k} {v:.2f} pt" for k, v in sorted(too_small.items()))
        raise SystemExit(
            f"in-figure type would print below {MIN_PRINTED_PT} pt in the {name}: {detail}. "
            f"The canvas is {width_px} x {height_px} px and that target scales it by "
            f"{scale:.5f} mm/px. Widen the canvas or shorten it — raising the font alone only "
            f"works while the WIDTH is the binding limit.")
    return name, scale, printed


def main(argv=None):
    d = json.load(open(SRC))
    pairs = d["graded_pairs"]
    partners = d["partners_scored"]
    acceptors = sorted({p["acceptor_exon_start"] for p in pairs})

    by = {}
    for p in pairs:
        by[(p["donor_symbol"], p["donor_exon_end"], p["acceptor_exon_start"])] = p.get("grade")

    blocks = [(partner,
               sorted({p["donor_exon_end"] for p in pairs if p["donor_symbol"] == partner}))
              for partner in partners]
    panels = split_into_panels(blocks)

    grid_w = len(acceptors) * (CELL_W + GAPX) - GAPX
    panel_w = LABEL_W + grid_w
    W = MARGIN * 2 + len(panels) * panel_w + (len(panels) - 1) * PANEL_GAP

    n_emit = d["n_emittable_junctions"]
    n_graded = d["n_pairs_graded"]
    text_w = W - 2 * MARGIN

    title = "Frame compatibility across the NR4A3 fusion junction space"
    subtitle = (f"{n_graded} donor-exon × acceptor-exon pairs graded over {len(partners)} "
                f"partners; {n_emit} are frame-compatible, and all of them lie in one acceptor "
                f"column. The grid is continued in the right-hand panel; the three acceptor "
                f"columns repeat in both.")
    note = ("Frame compatibility is an arithmetic property of exon structure. This is not a claim "
            "about which junctions patients carry: breakpoint recurrence is a clinical "
            "observation, and no partner-and-exon-resolved series exists for most of this space.")

    sub_lines = wrap(subtitle, text_w, FS_SUB)
    note_lines = wrap(note, text_w, FS_NOTE)

    # --- vertical layout, measured before anything is drawn -----------------------------------
    y = 26                                                          # title baseline
    y_sub = y + 22
    y_axis = y_sub + (len(sub_lines) - 1) * (FS_SUB + 5) + 26       # "NR4A3 acceptor exon"
    y_colhead = y_axis + 16
    grid_top = y_colhead + 6

    panel_bottoms = []
    placed = []                                                     # (x0, partner, donors, y0)
    for index, panel in enumerate(panels):
        x0 = MARGIN + index * (panel_w + PANEL_GAP)
        yy = grid_top
        for partner, donors in panel:
            placed.append((x0, partner, donors, yy + BLOCK_HEAD))
            yy += BLOCK_HEAD + len(donors) * ROW_PITCH + BLOCK_GAP
        panel_bottoms.append(yy)

    # ⭐ THE LEGEND GOES IN THE SHORTER PANEL'S OWN COLUMN, under its last block. That space is the
    # figure's only genuinely spare area — the panels are balanced on height, so it is small — and
    # putting the legend there keeps the whole figure a page shorter than setting it below the grid.
    short = min(range(len(panels)), key=lambda i: panel_bottoms[i])
    legend_x = MARGIN + short * (panel_w + PANEL_GAP)
    legend_y = panel_bottoms[short] + 26
    legend_bottom = legend_y + len(GRADE_FILL) * (CELL_H + 10)

    y_note = max(max(panel_bottoms), legend_bottom) + 30
    H = y_note + (len(note_lines) - 1) * (FS_NOTE + 6) + 18

    _check_type_sizes(W, H, {
        "row labels": FS_ROW, "legend": FS_LEGEND, "notes": FS_NOTE,
        "column headers": FS_COLHEAD, "axis caption": FS_AXIS, "partner names": FS_PARTNER,
        "subtitle": FS_SUB, "title": FS_TITLE,
    })

    # --- draw ----------------------------------------------------------------------------------
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{MARGIN}" y="{y}" font-size="{FS_TITLE}" fill="#111" font-weight="600">'
         f'{esc(title)}</text>']
    for i, line in enumerate(sub_lines):
        p.append(f'<text x="{MARGIN}" y="{y_sub + i * (FS_SUB + 5)}" font-size="{FS_SUB}" '
                 f'fill="#555">{esc(line)}</text>')

    for index in range(len(panels)):
        x0 = MARGIN + index * (panel_w + PANEL_GAP)
        gx = x0 + LABEL_W
        p.append(f'<text x="{gx + grid_w / 2:.1f}" y="{y_axis}" font-size="{FS_AXIS}" fill="#333" '
                 f'text-anchor="middle" font-weight="600">NR4A3 acceptor exon</text>')
        for j, a in enumerate(acceptors):
            cx = gx + j * (CELL_W + GAPX) + CELL_W / 2
            p.append(f'<text x="{cx:.1f}" y="{y_colhead}" font-size="{FS_COLHEAD}" fill="#333" '
                     f'text-anchor="middle">e{esc(a)}</text>')

    for x0, partner, donors, y0 in placed:
        gx = x0 + LABEL_W
        # The partner name sits ABOVE its block rather than in the exon-label column, so that every
        # donor exon can carry its own label — an unlabelled first row would make the row a reader
        # counts from ambiguous, which is the one thing a grid like this has to get right.
        p.append(f'<text x="{x0}" y="{y0 - 5}" font-size="{FS_PARTNER}" fill="#111" '
                 f'font-weight="600">{esc(partner)}</text>')
        for i, dn in enumerate(donors):
            ry = y0 + i * ROW_PITCH
            p.append(f'<text x="{gx - 6}" y="{ry + CELL_H - 1}" font-size="{FS_ROW}" fill="#555" '
                     f'text-anchor="end">e{esc(dn)}</text>')
            for j, a in enumerate(acceptors):
                g = by.get((partner, dn, a))
                fill = GRADE_FILL.get(g, ("#ffffff", ""))[0]
                cx = gx + j * (CELL_W + GAPX)
                p.append(f'<rect x="{cx}" y="{ry}" width="{CELL_W}" height="{CELL_H}" '
                         f'fill="{fill}" stroke="#ffffff" stroke-width="0.6"/>')

    ly = legend_y
    for g, (fill, label) in GRADE_FILL.items():
        n = sum(1 for v in by.values() if v == g)
        p.append(f'<rect x="{legend_x}" y="{ly}" width="{CELL_H + 4}" height="{CELL_H}" '
                 f'fill="{fill}" stroke="#ffffff" stroke-width="0.6"/>')
        p.append(f'<text x="{legend_x + CELL_H + 12}" y="{ly + CELL_H - 1}" '
                 f'font-size="{FS_LEGEND}" fill="#333">{esc(label)} ({esc(n)})</text>')
        ly += CELL_H + 10

    for i, line in enumerate(note_lines):
        p.append(f'<text x="{MARGIN}" y="{y_note + i * (FS_NOTE + 6)}" font-size="{FS_NOTE}" '
                 f'fill="#666">{esc(line)}</text>')
    p.append('</svg>')

    with open(OUT, "w") as fh:
        fh.write("\n".join(x for x in p if x) + "\n")
    counts = {g: sum(1 for v in by.values() if v == g) for g in GRADE_FILL}
    name, scale, printed = _check_type_sizes(W, H, {"row labels": FS_ROW, "notes": FS_NOTE})
    print(f"wrote {OUT}  ({n_graded} pairs, {n_emit} emittable) {counts}")
    print(f"  canvas {W} x {H} px; narrowest target is the {name}, {scale:.5f} mm/px — "
          f"row labels print at {printed['row labels']:.2f} pt, notes at {printed['notes']:.2f} pt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
