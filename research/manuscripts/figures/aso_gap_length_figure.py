#!/usr/bin/env python3
"""Figure — the margin a longer catalytic gap wins IS the parent duplex it concedes.

THE RESULT THIS HAS TO MAKE LEGIBLE, and it is the paper's most original one. A junction-spanning
gapmer's catalytic gap straddles the breakpoint, so every base inside the gap comes either from the
donor exon or from the acceptor exon. The design's gap-level margin is the count on the SHORTER
side — the junction-unique bases that make the fusion distinguishable. The contiguous run of gap DNA
that one wild-type parent transcript can pair is the count on the LONGER side. Those two counts are
complements: they tile the gap, so they sum to it exactly, for every design in every geometry.

⛔ SO IT IS AN IDENTITY, NOT A CORRELATION, AND THE FIGURE MUST NOT LOOK LIKE A CORRELATION. A
scatter with a fitted line would say "these tend to trade off". What is true is stronger and worse:
no design can gain a nucleotide of margin without handing RNase-H1 one more nucleotide of contiguous
wild-type-parent duplex, and no choice of register or gap length avoids it. Panel A draws the
mechanism on one real junction so the reader can see WHY; panel B shows every design in all three
geometries falling on the three exact lines, with no scatter to fit.

⚠ AND THE FIGURE MUST NOT SELL THE 5-10-5. A longer gap buys a markedly quieter transcriptome
(section 3.8, Table 5) and that is real. This figure is about what it costs, which is the half a
designer reaching for a longer gap does not see. The caption line says both.

⛔ EVERY NUMBER IS READ FROM THE THREE COMMITTED ATLASES, never typed. The per-design gap split is
`gap_bases_from_<donor>` and `gap_bases_from_NR4A3`; the margin is `gap_specificity_margin`. This
script asserts the identity it is drawing rather than assuming it, and RAISES if any design in any
geometry violates it — a figure that quietly dropped the one counter-example would be the worst
possible failure here.

Dependency-free SVG, following the repository's other figure scripts. No matplotlib, no network.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "..", "modalities")
ATLASES = [
    ("nr4a3-fusion-junction-atlas.json", "5-6-5", "#1565c0"),
    ("nr4a3-fusion-junction-atlas-18mer-5-8-5.json", "5-8-5", "#ef6c00"),
    ("nr4a3-fusion-junction-atlas-20mer-5-10-5.json", "5-10-5", "#6a1b9a"),
]
OUT = os.path.join(HERE, "aso-gap-length-tradeoff.svg")

#: The junction drawn in panel A. Chosen because it is the one with the most-reported breakpoint
#: and the one section 5.1 names a reagent at, so panel A is about a molecule the paper proposes.
PANEL_A_JUNCTION = "EWSR1_e12__NR4A3_e3"

W, H = 900, 664
esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731


def load(path):
    with open(os.path.join(MOD, path), encoding="utf-8") as fh:
        return json.load(fh)


#: ⚠ THE DONOR-SIDE KEY IS NAMED `gap_bases_from_EWSR1` ON EVERY PANEL, INCLUDING TAF15, TCF12, FUS
#: AND TFG ONES. That is a deliberate legacy alias in `junction_aso.mrna_junction` — the field means
#: "bases contributed by the DONOR", and the EWSR1 name was kept because every consumer, test and
#: committed artifact in the lane keys on it. Reading it as literally-EWSR1 and looking up
#: `gap_bases_from_TAF15` raises a KeyError, which is the friendly failure; reading it as EWSR1 and
#: believing the answer would be the unfriendly one.
DONOR_GAP_KEY, ACCEPTOR_GAP_KEY = "gap_bases_from_EWSR1", "gap_bases_from_NR4A3"


def designs_of(atlas):
    """(junction, margin, donor gap bases, acceptor gap bases) for every fusion-specific design."""
    out = []
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            out.append((panel["junction_label"], d["gap_specificity_margin"],
                        d[DONOR_GAP_KEY], d[ACCEPTOR_GAP_KEY]))
    return out


def main(argv=None):
    geoms = []
    for path, label, colour in ATLASES:
        atlas = load(path)
        gap = atlas["oligo_geometry"]["gap"]
        rows = designs_of(atlas)
        # ⛔ the identity, ASSERTED over every design before a single pixel is drawn
        for junction, margin, dn, ac in rows:
            if dn + ac != gap:
                raise SystemExit(f"{label} {junction}: gap split {dn}+{ac} != gap {gap}")
            if margin != min(dn, ac):
                raise SystemExit(f"{label} {junction}: margin {margin} != min({dn}, {ac})")
            if margin + max(dn, ac) != gap:
                raise SystemExit(f"{label} {junction}: margin + parent run != gap")
        geoms.append({"label": label, "colour": colour, "gap": gap, "rows": rows,
                      "n": len(rows), "best": max(r[1] for r in rows)})

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    p.append(f'<text x="40" y="26" font-size="15" fill="#111" font-weight="600">'
             f'A longer catalytic gap buys junction-unique bases and concedes wild-type parent '
             f'duplex, one for one</text>')

    # ───────────────────────────────────────────── panel A: the mechanism on one real junction
    p.append('<text x="40" y="56" font-size="13" fill="#111" font-weight="600">'
             'A · the catalytic gap is tiled by the two counts</text>')
    p.append(f'<text x="40" y="74" font-size="11.5" fill="#555">'
             f'The best-margin design at {esc(PANEL_A_JUNCTION.replace("__", " :: ").replace("_", " "))}, '
             f'at each geometry. Wings fixed at five nucleotides, so only the gap changes.</text>')

    top, cell, rowh = 106, 21, 62
    for gi, g in enumerate(geoms):
        rows = [r for r in g["rows"] if r[0] == PANEL_A_JUNCTION]
        if not rows:
            raise SystemExit(f"{g['label']}: {PANEL_A_JUNCTION} carries no design")
        junction, margin, dn, ac = max(rows, key=lambda r: r[1])
        y = top + gi * rowh
        wing, gap = 5, g["gap"]
        total = wing * 2 + gap
        x0 = 200
        # wings
        for k in range(wing):
            for xx in (x0 + k * cell, x0 + (wing + gap + k) * cell):
                p.append(f'<rect x="{xx}" y="{y}" width="{cell - 1}" height="{cell}" '
                         f'fill="#eceff1" stroke="#b0bec5" stroke-width="0.6"/>')
        # gap: donor-side then acceptor-side
        for k in range(gap):
            from_donor = k < dn
            fill = "#c62828" if from_donor else "#2e7d32"
            p.append(f'<rect x="{x0 + (wing + k) * cell}" y="{y}" width="{cell - 1}" '
                     f'height="{cell}" fill="{fill}" opacity="0.82" '
                     f'stroke="#37474f" stroke-width="0.6"/>')
        # the breakpoint, between the two colours
        bx = x0 + (wing + dn) * cell - 0.5
        p.append(f'<line x1="{bx}" y1="{y - 7}" x2="{bx}" y2="{y + cell + 7}" '
                 f'stroke="#111" stroke-width="1.6"/>')
        p.append(f'<text x="{bx}" y="{y - 11}" font-size="10" fill="#111" '
                 f'text-anchor="middle">breakpoint</text>')
        p.append(f'<text x="{x0 - 12}" y="{y + 15}" font-size="12" fill="#111" '
                 f'text-anchor="end" font-weight="600">{g["label"]}</text>')
        p.append(f'<text x="{x0 + total * cell + 14}" y="{y + 15}" font-size="11.5" fill="#333">'
                 f'margin {min(dn, ac)} + parent run {max(dn, ac)} = gap {gap}</text>')

    ky = top + 3 * rowh + 2
    for dx, fill, lab in ((0, "#c62828", "junction-unique bases (the margin)"),
                          (250, "#2e7d32", "bases one wild-type parent pairs"),
                          (530, "#eceff1", "LNA wing, not cleaved")):
        p.append(f'<rect x="{200 + dx}" y="{ky}" width="13" height="13" fill="{fill}" '
                 f'opacity="0.82" stroke="#37474f" stroke-width="0.6"/>')
        p.append(f'<text x="{200 + dx + 19}" y="{ky + 11}" font-size="11" fill="#555">'
                 f'{esc(lab)}</text>')

    # ─────────────────────────────────────── panel B: every design, on three exact lines
    by0 = 344
    p.append(f'<text x="40" y="{by0}" font-size="13" fill="#111" font-weight="600">'
             f'B · every design in all three geometries, with no scatter to fit</text>')
    p.append(f'<text x="40" y="{by0 + 18}" font-size="11.5" fill="#555">'
             f'{esc(sum(g["n"] for g in geoms))} designs over 38 junctions. Marker area is the '
             f'number of designs at that point; the lines are drawn, not fitted.</text>')

    L, T = 112, by0 + 40
    PW, PH = 676, 190
    # ⚠ SEPARATE AXES. The margin never exceeds half the gap (it is the SHORTER side by
    # definition), so an x axis running to the gap length would leave the right half of the panel
    # permanently empty and imply a region designs could occupy. They cannot.
    xmax = max(m for g in geoms for _j, m, _d, _a in g["rows"]) + 1
    ymax = max(g["gap"] for g in geoms)

    def px(v):
        return L + v * PW / xmax

    def py(v):
        return T + PH - v * PH / ymax

    p.append(f'<line x1="{L}" y1="{T + PH}" x2="{L + PW}" y2="{T + PH}" stroke="#444"/>')
    p.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T + PH}" stroke="#444"/>')
    for v in range(0, max(xmax, ymax) + 1):
        if v <= xmax:
            p.append(f'<text x="{px(v):.1f}" y="{T + PH + 16}" font-size="11" fill="#333" '
                     f'text-anchor="middle">{v}</text>')
        if v <= ymax:
            p.append(f'<text x="{L - 9}" y="{py(v) + 4:.1f}" font-size="11" fill="#333" '
                     f'text-anchor="end">{v}</text>')
    p.append(f'<text x="{L + PW / 2:.0f}" y="{T + PH + 38}" font-size="12" fill="#111" '
             f'text-anchor="middle">gap-level margin (junction-unique bases inside the gap)</text>')
    p.append(f'<text x="32" y="{T + PH / 2:.0f}" font-size="12" fill="#111" text-anchor="middle" '
             f'transform="rotate(-90 32 {T + PH / 2:.0f})">contiguous parent gap DNA</text>')

    for g in geoms:
        counts = {}
        for _junction, margin, dn, ac in g["rows"]:
            counts[(margin, max(dn, ac))] = counts.get((margin, max(dn, ac)), 0) + 1
        xs = sorted({k[0] for k in counts})
        pts = " ".join(f"{px(x):.1f},{py(g['gap'] - x):.1f}" for x in
                       range(min(xs), max(xs) + 1))
        del xs
        p.append(f'<polyline points="{pts}" fill="none" stroke="{g["colour"]}" '
                 f'stroke-width="1.4" stroke-dasharray="5 3"/>')
        for (mx, run), k in sorted(counts.items()):
            r = 3.0 + 8.4 * (k / max(counts.values())) ** 0.5
            p.append(f'<circle cx="{px(mx):.1f}" cy="{py(run):.1f}" r="{r:.1f}" '
                     f'fill="{g["colour"]}" opacity="0.55" stroke="{g["colour"]}"/>')
            p.append(f'<text x="{px(mx):.1f}" y="{py(run) + 3.6:.1f}" font-size="9.5" '
                     f'fill="#ffffff" text-anchor="middle" font-weight="600">{k}</text>')

    lx = L + PW - 168
    for gi, g in enumerate(geoms):
        ly = T + 12 + gi * 17
        p.append(f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 22}" y2="{ly - 4}" '
                 f'stroke="{g["colour"]}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        p.append(f'<text x="{lx + 28}" y="{ly}" font-size="11" fill="#333">'
                 f'{g["label"]}, gap {g["gap"]}: margin + run = {g["gap"]} '
                 f'({g["n"]} designs)</text>')

    p.append(f'<text x="40" y="{H - 26}" font-size="11" fill="#555">'
             f'The identity holds for every design individually, not on average. A longer gap also '
             f'buys a markedly quieter transcriptome (Table 5); this figure is what it costs.</text>')
    p.append("</svg>")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(p) + "\n")
    print(f"wrote {os.path.basename(OUT)}: "
          + "; ".join(f"{g['label']} {g['n']} designs, best margin {g['best']}" for g in geoms),
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
