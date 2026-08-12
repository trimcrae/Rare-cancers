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

CELL, GAPX, GAPY = 13, 2, 2
L, T = 96, 92
ROW_GAP = 16


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(argv=None):
    d = json.load(open(SRC))
    pairs = d["graded_pairs"]
    partners = d["partners_scored"]
    acceptors = sorted({p["acceptor_exon_start"] for p in pairs})

    by = {}
    for p in pairs:
        by[(p["donor_symbol"], p["donor_exon_end"], p["acceptor_exon_start"])] = p.get("grade")

    # one block per partner, rows = donor exons, columns = NR4A3 acceptor exons
    blocks, yy = [], T
    for partner in partners:
        donors = sorted({p["donor_exon_end"] for p in pairs if p["donor_symbol"] == partner})
        blocks.append((partner, donors, yy + 14))   # +14 leaves room for the partner label above
        yy += len(donors) * (CELL + GAPY) + ROW_GAP + 18

    grid_w = len(acceptors) * (CELL + GAPX)
    W = max(L + grid_w + 300, 760)
    H = yy + 92

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    n_emit = d["n_emittable_junctions"]
    n_graded = d["n_pairs_graded"]
    p.append(f'<text x="{L - 60}" y="30" font-size="15" fill="#111" font-weight="600">'
             f'Frame compatibility across the NR4A3 fusion junction space</text>')
    p.append(f'<text x="{L - 60}" y="48" font-size="12" fill="#555">'
             f'{esc(n_graded)} donor-exon × acceptor-exon pairs graded over {esc(len(partners))} '
             f'partners; {esc(n_emit)} are frame-compatible, and all of them lie in one column.</text>')

    # column headers
    for j, a in enumerate(acceptors):
        cx = L + j * (CELL + GAPX) + CELL / 2
        p.append(f'<text x="{cx:.1f}" y="{T - 8}" font-size="11" fill="#333" '
                 f'text-anchor="middle">e{esc(a)}</text>')
    p.append(f'<text x="{L + grid_w / 2:.1f}" y="{T - 26}" font-size="11.5" fill="#333" '
             f'text-anchor="middle" font-weight="600">NR4A3 acceptor exon</text>')

    for partner, donors, y0 in blocks:
        # the partner name sits ABOVE its block rather than in the exon-label column, so that every
        # donor exon can carry its own label — an unlabelled first row would make the row a reader
        # counts from ambiguous, which is the one thing a grid like this has to get right
        p.append(f'<text x="{L}" y="{y0 - 4}" font-size="12" fill="#111" '
                 f'font-weight="600">{esc(partner)}</text>')
        for i, dn in enumerate(donors):
            ry = y0 + i * (CELL + GAPY)
            p.append(f'<text x="{L - 8}" y="{ry + 10}" font-size="9.5" fill="#777" '
                     f'text-anchor="end">e{esc(dn)}</text>')
            for j, a in enumerate(acceptors):
                g = by.get((partner, dn, a))
                fill = GRADE_FILL.get(g, ("#ffffff", ""))[0]
                cx = L + j * (CELL + GAPX)
                p.append(f'<rect x="{cx}" y="{ry}" width="{CELL}" height="{CELL}" fill="{fill}" '
                         f'stroke="#ffffff" stroke-width="0.6"/>')

    # legend
    ly = T
    lx = L + grid_w + 30
    for g, (fill, label) in GRADE_FILL.items():
        n = sum(1 for v in by.values() if v == g)
        p.append(f'<rect x="{lx}" y="{ly}" width="{CELL}" height="{CELL}" fill="{fill}" '
                 f'stroke="#ffffff" stroke-width="0.6"/>')
        p.append(f'<text x="{lx + CELL + 7}" y="{ly + 11}" font-size="11" fill="#333">'
                 f'{esc(label)} ({esc(n)})</text>')
        ly += CELL + 8

    p.append(f'<text x="{L - 60}" y="{H - 34}" font-size="10.5" fill="#666">'
             f'Frame compatibility is an arithmetic property of exon structure. This is not a claim '
             f'about which junctions patients carry: breakpoint recurrence is a clinical</text>')
    p.append(f'<text x="{L - 60}" y="{H - 20}" font-size="10.5" fill="#666">'
             f'observation, and no partner-and-exon-resolved series exists for most of this space.</text>')
    p.append('</svg>')

    with open(OUT, "w") as fh:
        fh.write("\n".join(x for x in p if x) + "\n")
    counts = {g: sum(1 for v in by.values() if v == g) for g in GRADE_FILL}
    print(f"wrote {OUT}  ({n_graded} pairs, {n_emit} emittable) {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
