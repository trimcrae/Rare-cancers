#!/usr/bin/env python3
"""Figure — a longer catalytic gap buys junction-unique bases and concedes gap DNA at the design's
own seam, one for one.

THE RESULT THIS HAS TO MAKE LEGIBLE, and it is the paper's most original one. A junction-spanning
gapmer's catalytic gap straddles the breakpoint, so every base inside the gap comes either from the
donor exon or from the acceptor exon. The design's gap-level margin is the count on the SHORTER
side — the junction-unique bases that make the fusion distinguishable. The count on the LONGER side
is the contiguous run of gap DNA that the parent transcript contributing it pairs AT THIS DESIGN'S
OWN SEAM. Those two counts are complements: they tile the gap, so they sum to it exactly, for every
design in every geometry.

⛔⛔ THE DRAWN QUANTITY IS `parent_paired_gap_dna_nt`, AND IT IS NOT THE QUANTITY EVERY TABLE IN THE
PAPER PRINTS (figure-integrity review, 2026-08-19, confirmed independently and recomputed here).
The tables' column "longest parent duplex through the gap (bp)" is
`mature_parent_duplex_through_gap_bp` — the result of SEARCHING all six mature wild-type parent
transcripts for a run that covers the whole gap. This axis is arithmetic on the design's own seam
and searches nothing. For the very molecule panel A draws, 5'-GGGCATATCATCAAAC-3', the two read 3
and 8 bp (TFG). ⚠ AND THEY MOVE IN OPPOSITE DIRECTIONS ACROSS GEOMETRIES, so collapsing them is not
a rounding error, it inverts the result:

    mature-parent search, any length     181/190 -> 130/266 ->  87/342   FALLS
    mature-parent search, at ten bp       87/190 ->  88/266 ->  87/342   FLAT
    this axis, run of five or more        76/190 -> 228/266 -> 342/342   RISES

Lifted out alone with the old title, this figure told a reader that a longer gap monotonically
concedes wild-type parent duplex, which under the phrase's meaning everywhere else in the paper is
the opposite of what the screens measure. The title, the axis label, panel A's annotations and the
in-panel note now all name the own-seam quantity and carry the falling/flat reading beside it. The
canonical file's own header warns about the same collision ("THREE PARENT-DUPLEX COLUMNS, AND THEY
ARE NOT INTERCHANGEABLE"); this figure was the one display item that collapsed them.

⛔ SO IT IS AN IDENTITY, NOT A CORRELATION, AND THE FIGURE MUST NOT LOOK LIKE A CORRELATION. A
scatter with a fitted line would say "these tend to trade off". What is true is stronger and more
exact: margin and the own-seam parent-paired run sum to the gap, so within one geometry they move
INVERSELY along a line of slope -1 — a higher-margin register concedes a SHORTER own-seam run.
What a geometry fixes is the ceiling on margin, at half its gap rounded down; passing it takes a
longer gap, and a longer gap raises the own-seam parent-paired run at every register.
⚠ Superseded, retained (round 5, 2026-08-15): "no design can gain a nucleotide of margin without
handing RNase-H1 one more nucleotide of contiguous wild-type-parent duplex, and no choice of
register or gap length avoids it" — register choice is precisely what avoids it within a geometry.

⛔ AND THE PANEL IS SQUARE IN DATA UNITS, BECAUSE THE CAPTION CLAIMS A SLOPE (2026-08-19). Panel B
used to be 676 x 190 px over 6 x 10 data units: 112.667 px/unit across against 19.0 px/unit up, an
anisotropy of 5.93. The three identity lines were drawn at a measured -0.169, about 9.6 degrees off
horizontal, while the caption called them lines of slope -1. A reader saw three nearly flat dashes
and was told they were 45-degree lines. One scale now serves both axes, so the drawn slope IS the
stated slope and no caption caveat has to stand in for the geometry.

⚠ AND THE FIGURE MUST NOT SELL THE 5-10-5. A longer gap buys a markedly quieter transcriptome
(section 3.8, Table 7) and that is real. This figure is about what it costs, which is the half a
designer reaching for a longer gap does not see. The in-panel note states that cost as a fact rather
than as a pointer to a table, because a figure lifted out of the paper cannot resolve "Table 7".

⛔ EVERY NUMBER IS READ FROM THE COMMITTED ARTIFACTS, never typed. The per-design gap split is
`gap_bases_from_<donor>` and `gap_bases_from_NR4A3` and the margin is `gap_specificity_margin`, all
from the three atlases; the mature-parent readings are joined per design out of
`aso-gap-length-tradeoff.json`, against its own `thresholds` value for the criterion. This script
asserts the identity it is drawing rather than assuming it, and RAISES if any design in any geometry
violates it — a figure that quietly dropped the one counter-example would be the worst possible
failure here.

Dependency-free SVG, following the repository's other figure scripts. No matplotlib, no network.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from aso_figure_text import check_type_sizes, text_width, wrap  # noqa: E402

MOD = os.path.join(HERE, "..", "..", "modalities")
ATLASES = [
    ("nr4a3-fusion-junction-atlas.json", "5-6-5", "#1565c0"),
    ("nr4a3-fusion-junction-atlas-18mer-5-8-5.json", "5-8-5", "#ef6c00"),
    ("nr4a3-fusion-junction-atlas-20mer-5-10-5.json", "5-10-5", "#6a1b9a"),
]
#: The mature-parent SEARCH, per design and per geometry, plus the criterion it is read at. This is
#: the quantity the tables print and the one this figure must not be mistaken for.
TRADE = "aso-gap-length-tradeoff.json"
OUT = os.path.join(HERE, "aso-gap-length-tradeoff.svg")

#: The junction drawn in panel A. Chosen because it is the one with the most-reported breakpoint
#: and the one section 5.1 names a reagent at, so panel A is about a molecule the paper proposes.
PANEL_A_JUNCTION = "EWSR1_e12__NR4A3_e3"

W = 900
esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731

# --- type, in SVG pixels ----------------------------------------------------------------------
#: ⛔ 11.5 px IS THE FLOOR HERE AND IT IS LOAD-BEARING. At this canvas the narrowest render target
#: scales by about 0.193 mm/px, so 11.5 px prints at 6.3 pt and 9.5 px printed at 5.2-5.4 pt — which
#: is what a 2026-08-19 review measured off the built PDF for panel B's count labels. `check_type_
#: sizes` below is what makes that a gate rather than a comment.
FS_TITLE, FS_LEAD = 15, 11.5
FS_PANEL_HEAD, FS_PANEL_SUB = 13, 11.5
FS_GEOM_LABEL, FS_ANNOT, FS_BREAKPOINT = 12, 11.5, 11.5
FS_KEY, FS_TICK, FS_AXIS, FS_COUNT, FS_LEGEND, FS_NOTE = 11.5, 11.5, 12, 12, 11.5, 11.5


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
    """(junction, sequence, margin, donor gap bases, acceptor gap bases) per fusion-specific design.

    The sequence is carried so panel A can JOIN to the mature-parent search rather than re-deriving
    it — the two quantities are what this figure exists to keep apart.
    """
    out = []
    for panel in atlas["panels"]:
        for d in panel.get("designs") or []:
            if not d.get("fusion_specific"):
                continue
            out.append((panel["junction_label"], d["antisense_5to3"], d["gap_specificity_margin"],
                        d[DONOR_GAP_KEY], d[ACCEPTOR_GAP_KEY]))
    return out


def mature_parent_readings(trade):
    """The SEARCH the tables print, as (per-design lookup, criterion bp, any-length line, at-cut line).

    ⛔ DERIVED, NEVER TYPED. The any-length counts come from the artifact's own trade block; the
    counts at the criterion are recomputed here from `per_design` against the artifact's own
    threshold, so a change to either moves this figure's text.
    """
    cut = trade["thresholds"]["min_duplex_bp_for_hybrid_binding_domain"]["value"]
    per = {(r["junction"], r["antisense_5to3"], r["architecture"]): r for r in trade["per_design"]}
    any_length = trade["the_trade"]["improves_with_a_longer_gap"]["mature_parent_can_pair_the_whole_gap"]
    at_cut = {}
    for arch in any_length:
        rows = [r for r in trade["per_design"] if r["architecture"] == arch]
        hits = sum(1 for r in rows
                   if isinstance(r.get("mature_parent_duplex_through_whole_gap_bp"), (int, float))
                   and r["mature_parent_duplex_through_whole_gap_bp"] >= cut)
        at_cut[arch] = f"{hits} of {len(rows)}"
    return per, cut, any_length, at_cut


def main(argv=None):
    trade = load(TRADE)
    mature, cut_bp, any_length, at_cut = mature_parent_readings(trade)

    geoms = []
    for path, label, colour in ATLASES:
        atlas = load(path)
        gap = atlas["oligo_geometry"]["gap"]
        rows = designs_of(atlas)
        # ⛔ the identity, ASSERTED over every design before a single pixel is drawn
        for junction, _seq, margin, dn, ac in rows:
            if dn + ac != gap:
                raise SystemExit(f"{label} {junction}: gap split {dn}+{ac} != gap {gap}")
            if margin != min(dn, ac):
                raise SystemExit(f"{label} {junction}: margin {margin} != min({dn}, {ac})")
            if margin + max(dn, ac) != gap:
                raise SystemExit(f"{label} {junction}: margin + own-seam parent run != gap")
        geoms.append({"label": label, "colour": colour, "gap": gap, "rows": rows,
                      "n": len(rows), "best": max(r[2] for r in rows)})

    order = [g["label"] for g in geoms]
    lead = ("A longer catalytic gap buys junction-unique bases and concedes gap DNA at the "
            "design's own seam, one for one")
    #: ⛔ THE WITHDRAWAL TRAVELS ON THE FIGURE. The claim the old title made — that a longer gap
    #: concedes wild-type parent duplex — is what the mature-parent SEARCH denies, and a figure is
    #: the element most often read without its caption.
    withdrawal = (
        f"This ordinate is the design's own seam arithmetic, not the mature-parent search Tables 2, "
        f"3, 5 and 7 print under “longest parent duplex through the gap”. That search "
        f"FALLS as the gap lengthens ("
        + "; ".join(f"{any_length[k]} at {k}" for k in order)
        + f") and is FLAT at the {cut_bp}-base-pair criterion ("
        + "; ".join(f"{at_cut[k]} at {k}" for k in order)
        + "). Only the quantity drawn here rises.")

    # ── vertical layout, measured before anything is drawn ────────────────────────────────────
    lead_lines = wrap(lead, FS_TITLE, W - 80)
    withdrawal_lines = wrap(withdrawal, FS_LEAD, W - 80)
    y_title = 26
    y_withdraw = y_title + len(lead_lines) * (FS_TITLE + 6) + 4
    y_a_head = y_withdraw + len(withdrawal_lines) * (FS_LEAD + 4) + 18
    y_a_sub = y_a_head + 18

    cell, rowh = 21, 62
    top = y_a_sub + 32
    x0 = 176
    ky = top + len(geoms) * rowh + 2

    #: The mature-parent contrast on the SAME three molecules panel A draws, joined per design.
    panel_a = []
    for g in geoms:
        rows = [r for r in g["rows"] if r[0] == PANEL_A_JUNCTION]
        if not rows:
            raise SystemExit(f"{g['label']}: {PANEL_A_JUNCTION} carries no design")
        junction, seq, margin, dn, ac = max(rows, key=lambda r: r[2])
        rec = mature.get((junction, seq, g["label"]))
        if rec is None:
            raise SystemExit(f"{g['label']} {junction} {seq}: no mature-parent record to join")
        panel_a.append((g, seq, margin, dn, ac, rec))

    def _mature_words(rec):
        bp = rec.get("mature_parent_duplex_through_whole_gap_bp")
        if not isinstance(bp, (int, float)) or bp <= 0:
            return "none"
        gene = rec.get("mature_parent_duplex_gene")
        return f"{bp} bp ({gene})" if gene else f"{bp} bp"

    contrast = ("The same three molecules' mature-parent duplex through the whole gap — the column "
                "the tables print — reads "
                + ", ".join(f"{_mature_words(rec)} at {g['label']}" for g, _s, _m, _d, _a, rec
                            in panel_a)
                + ". It is a search over six wild-type parent transcripts, not this arithmetic, and "
                  "on this molecule the two disagree.")
    contrast_lines = wrap(contrast, FS_NOTE, W - 80)
    y_contrast = ky + 30

    y_b_head = y_contrast + len(contrast_lines) * (FS_NOTE + 4) + 22
    y_b_sub = y_b_head + 18

    # ── panel B geometry: ONE SCALE FOR BOTH AXES, so the drawn slope is the stated slope ──────
    # ⚠ SEPARATE RANGES, ONE SCALE. The margin never exceeds half the gap (it is the SHORTER side
    # by definition), so an x axis running to the gap length would leave the right half of the
    # panel permanently empty and imply a region designs could occupy. They cannot. The RANGES
    # therefore differ; the px-per-unit does not.
    xmax = max(m for g in geoms for _j, _s, m, _d, _a in g["rows"]) + 1
    ymax = max(g["gap"] for g in geoms)
    S = 42                                          # px per data unit, both axes
    L, T = 112, y_b_sub + 26
    PW, PH = S * xmax, S * ymax
    RMAX = 14.0                                     # radius of the largest bubble

    y_ticks = T + PH + 18
    y_axis_title = T + PH + 40
    col_x = L + PW + 52                             # the right-hand key column
    col_w = W - 32 - col_x

    #: ⛔ THE NOTE STATES THE FACT INSTEAD OF POINTING AT A TABLE (2026-08-19). It read "a longer
    #: gap also buys a markedly quieter transcriptome (Table 7); this figure is what it costs", and
    #: a figure lifted out of the paper — which is how a figure is usually met — cannot resolve
    #: "Table 7". ⚠ THE LIKE-FOR-LIKE BLOCK, NOT THE CORPUS ONE: the geometries are screened at
    #: different numbers of junctions, so only `matched_junctions` compares specificity rather than
    #: coverage, and the artifact's own bound (a longer probe at a fixed absolute mismatch budget is
    #: arithmetically at least as specific) travels with the number.
    matched = trade["the_trade"]["transcriptome_coincidence_falls_but_it_MUST"]["matched_junctions"]
    medians = " to ".join(f'{matched["by_geometry"][k]["near_matches"]["median"]:g}' for k in order)
    note = (f"The identity holds for every design individually, not on average. A longer gap also "
            f"buys a quieter transcriptome: over the {matched['n_junctions']} junctions every "
            f"geometry was screened at, the median near-match count falls {medians} across "
            f"{', '.join(order)}. Part of that fall is arithmetic — at a fixed absolute mismatch "
            f"budget a longer probe cannot hit more loci than its own sub-windows — and this "
            f"figure is what the rest of it costs.")
    note_lines = wrap(note, FS_NOTE, W - 80)
    y_note = y_axis_title + 26
    H = int(max(y_note + len(note_lines) * (FS_NOTE + 4) + 10, T + PH + 70))

    check_type_sizes(W, H, {
        "panel B count labels": FS_COUNT, "axis ticks": FS_TICK, "axis titles": FS_AXIS,
        "panel A annotations": FS_ANNOT, "breakpoint label": FS_BREAKPOINT,
        "geometry labels": FS_GEOM_LABEL, "key": FS_KEY, "legend": FS_LEGEND,
        "notes": FS_NOTE, "lead": FS_LEAD, "title": FS_TITLE,
    })

    # ── draw ──────────────────────────────────────────────────────────────────────────────────
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    for i, line in enumerate(lead_lines):
        p.append(f'<text x="40" y="{y_title + i * (FS_TITLE + 6)}" font-size="{FS_TITLE}" '
                 f'fill="#111" font-weight="600">{esc(line)}</text>')
    for i, line in enumerate(withdrawal_lines):
        p.append(f'<text x="40" y="{y_withdraw + i * (FS_LEAD + 4)}" font-size="{FS_LEAD}" '
                 f'fill="#b71c1c">{esc(line)}</text>')

    # ───────────────────────────────────────────── panel A: the mechanism on one real junction
    p.append(f'<text x="40" y="{y_a_head}" font-size="{FS_PANEL_HEAD}" fill="#111" '
             f'font-weight="600">A · the catalytic gap is tiled by the two counts</text>')
    p.append(f'<text x="40" y="{y_a_sub}" font-size="{FS_PANEL_SUB}" fill="#555">'
             f'The best-margin design at '
             f'{esc(PANEL_A_JUNCTION.replace("__", " :: ").replace("_", " "))}, '
             f'at each geometry. Wings fixed at five nucleotides, so only the gap changes.</text>')

    for gi, (g, _seq, _margin, dn, ac, _rec) in enumerate(panel_a):
        y = top + gi * rowh
        wing, gap = 5, g["gap"]
        total = wing * 2 + gap
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
        p.append(f'<text x="{bx}" y="{y - 11}" font-size="{FS_BREAKPOINT}" fill="#111" '
                 f'text-anchor="middle">breakpoint</text>')
        p.append(f'<text x="{x0 - 12}" y="{y + 15}" font-size="{FS_GEOM_LABEL}" fill="#111" '
                 f'text-anchor="end" font-weight="600">{g["label"]}</text>')
        p.append(f'<text x="{x0 + total * cell + 14}" y="{y + 15}" font-size="{FS_ANNOT}" '
                 f'fill="#333">margin {min(dn, ac)} + own-seam parent run {max(dn, ac)} = '
                 f'gap {gap}</text>')

    #: ⛔ THE KEY NAMES WHAT THE CODE DRAWS, NOT WHAT THE ARGUMENT IS ABOUT (figure-integrity screen,
    #: 2026-08-19). It read "junction-unique bases (the margin)" and "bases one wild-type parent
    #: pairs", but the fill above is chosen by WHICH EXON a base comes from: red is donor-side, green
    #: acceptor-side. Red is the margin only when the donor side is the shorter one. The panel's own
    #: junction is a perfect tie in all three geometries (3+3, 4+4, 5+5), so the asymmetry the caption
    #: asserts is never visible, and a reader carrying the key to any other register reads it
    #: backwards for the 76 of 190, 114 of 266 and 152 of 342 designs whose donor side is longer.
    for dx, fill, lab in ((0, "#c62828", "donor-exon gap bases"),
                          #: ⚠ NO MARKDOWN IN SVG TEXT. These labels are drawn verbatim: an
                          #: asterisk-wrapped gene name renders as literal asterisks, not italics,
                          #: and every other figure here sets gene names plain for that reason.
                          (250, "#2e7d32", "NR4A3 gap bases"),
                          (530, "#eceff1", "LNA wing, not cleaved")):
        p.append(f'<rect x="{x0 + 24 + dx}" y="{ky}" width="13" height="13" fill="{fill}" '
                 f'opacity="0.82" stroke="#37474f" stroke-width="0.6"/>')
        p.append(f'<text x="{x0 + 24 + dx + 19}" y="{ky + 11}" font-size="{FS_KEY}" fill="#555">'
                 f'{esc(lab)}</text>')

    for i, line in enumerate(contrast_lines):
        p.append(f'<text x="40" y="{y_contrast + i * (FS_NOTE + 4)}" font-size="{FS_NOTE}" '
                 f'fill="#666">{esc(line)}</text>')

    # ─────────────────────────────────────── panel B: every design, on three exact lines
    p.append(f'<text x="40" y="{y_b_head}" font-size="{FS_PANEL_HEAD}" fill="#111" '
             f'font-weight="600">B · every design in all three geometries, with no scatter to '
             f'fit</text>')
    p.append(f'<text x="40" y="{y_b_sub}" font-size="{FS_PANEL_SUB}" fill="#555">'
             f'{esc(sum(g["n"] for g in geoms))} designs over 38 junctions. Both axes are drawn at '
             f'{S} px per nucleotide, so the identity lines really are at 45 degrees.</text>')

    def px(v):
        return L + v * S

    def py(v):
        return T + PH - v * S

    p.append(f'<line x1="{L}" y1="{T + PH}" x2="{L + PW}" y2="{T + PH}" stroke="#444"/>')
    p.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T + PH}" stroke="#444"/>')
    for v in range(0, max(xmax, ymax) + 1):
        if v <= xmax:
            p.append(f'<text x="{px(v):.1f}" y="{T + PH + 16}" font-size="{FS_TICK}" fill="#333" '
                     f'text-anchor="middle">{v}</text>')
        if v <= ymax:
            p.append(f'<text x="{L - 9}" y="{py(v) + 4:.1f}" font-size="{FS_TICK}" fill="#333" '
                     f'text-anchor="end">{v}</text>')
    p.append(f'<text x="{L + PW / 2:.0f}" y="{y_axis_title}" font-size="{FS_AXIS}" fill="#111" '
             f'text-anchor="middle">gap-level margin (junction-unique bases inside the gap, '
             f'nt)</text>')
    #: ⛔ THE ORDINATE NAMES THE SEAM IT IS COMPUTED AT. "contiguous parent gap DNA" was read, by
    #: every table in the paper, as the mature-parent search; it is not.
    p.append(f'<text x="32" y="{T + PH / 2:.0f}" font-size="{FS_AXIS}" fill="#111" '
             f'text-anchor="middle" transform="rotate(-90 32 {T + PH / 2:.0f})">'
             f'contiguous gap DNA a parent pairs at this design’s own seam (nt)</text>')

    #: ⛔ ONE SCALE FOR ALL THREE SERIES (2026-08-19). The radius was normalised against
    #: `max(counts.values())` INSIDE the per-geometry loop, so each series was scaled by its own
    #: peak. Area was proportional to count within a series and comparable across series only
    #: because all three geometries happen to peak at the same 76 designs — a coincidence of this
    #: panel, not a property of the encoding. The caption says marker area is the number of designs,
    #: full stop, so the denominator has to be the maximum over every series drawn.
    counts_by_geometry = {}
    for g in geoms:
        counts = {}
        for _junction, _seq, margin, dn, ac in g["rows"]:
            counts[(margin, max(dn, ac))] = counts.get((margin, max(dn, ac)), 0) + 1
        counts_by_geometry[id(g)] = counts
    peak = max(k for counts in counts_by_geometry.values() for k in counts.values())

    for g in geoms:
        counts = counts_by_geometry[id(g)]
        xs = sorted({k[0] for k in counts})
        pts = " ".join(f"{px(x):.1f},{py(g['gap'] - x):.1f}" for x in
                       range(min(xs), max(xs) + 1))
        del xs
        p.append(f'<polyline points="{pts}" fill="none" stroke="{g["colour"]}" '
                 f'stroke-width="1.4" stroke-dasharray="5 3"/>')
        for (mx, run), k in sorted(counts.items()):
            #: ⛔ NO CONSTANT OFFSET — THE CAPTION SAYS AREA IS THE COUNT (2026-08-18). This
            #: read `3.0 + 8.4 * sqrt(k/max)`, whose area ratio between the 38- and 76-design
            #: points is about 0.60 where proportional area requires 0.50; a blind screen
            #: measured the drawn diameters and caught it. Radius proportional to the square
            #: root of the count makes area proportional to the count, which is what the
            #: caption claims and what a reader decodes a bubble by.
            r = RMAX * (k / peak) ** 0.5
            if text_width(str(k), FS_COUNT) > 2 * r:
                raise SystemExit(
                    f"panel B: the label {k} does not fit its own marker (r={r:.1f} px at "
                    f"{FS_COUNT} px type). Raise RMAX or lower FS_COUNT — the caption says the "
                    f"label is that count, so it cannot be dropped.")
            p.append(f'<circle cx="{px(mx):.1f}" cy="{py(run):.1f}" r="{r:.1f}" '
                     f'fill="{g["colour"]}" opacity="0.55" stroke="{g["colour"]}"/>')
            p.append(f'<text x="{px(mx):.1f}" y="{py(run) + 4.2:.1f}" font-size="{FS_COUNT}" '
                     f'fill="#ffffff" text-anchor="middle" font-weight="600">{k}</text>')

    # the key column, beside the plot rather than inside it: the panel is tall and narrow now
    ly = T + 12
    for g in geoms:
        p.append(f'<line x1="{col_x}" y1="{ly - 4}" x2="{col_x + 22}" y2="{ly - 4}" '
                 f'stroke="{g["colour"]}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        lines = wrap(f'{g["label"]}, gap {g["gap"]}: margin + own-seam run = {g["gap"]} '
                     f'({g["n"]} designs)', FS_LEGEND, col_w - 28)
        for i, line in enumerate(lines):
            p.append(f'<text x="{col_x + 28}" y="{ly + i * (FS_LEGEND + 4)}" '
                     f'font-size="{FS_LEGEND}" fill="#333">{esc(line)}</text>')
        ly += len(lines) * (FS_LEGEND + 4) + 8

    ly += 10
    for line in wrap("Marker area is the number of designs at that point and the label is that "
                     "count; the three lines are drawn from the identity, not fitted.",
                     FS_LEGEND, col_w):
        p.append(f'<text x="{col_x}" y="{ly}" font-size="{FS_LEGEND}" fill="#555">'
                 f'{esc(line)}</text>')
        ly += FS_LEGEND + 4

    ly += 10
    for line in wrap("A geometry's ceiling on margin is half its gap rounded down; clearing it "
                     "means a longer gap, and a longer gap raises the own-seam parent-paired run "
                     "at every register.", FS_LEGEND, col_w):
        p.append(f'<text x="{col_x}" y="{ly}" font-size="{FS_LEGEND}" fill="#555">'
                 f'{esc(line)}</text>')
        ly += FS_LEGEND + 4

    for i, line in enumerate(note_lines):
        p.append(f'<text x="40" y="{y_note + i * (FS_NOTE + 4)}" font-size="{FS_NOTE}" '
                 f'fill="#555">{esc(line)}</text>')
    p.append("</svg>")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(p) + "\n")
    print(f"wrote {os.path.basename(OUT)}: {W} x {H} px; "
          + "; ".join(f"{g['label']} {g['n']} designs, best margin {g['best']}" for g in geoms)
          + f" | mature-parent search any length {any_length} · at {cut_bp} bp {at_cut}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
