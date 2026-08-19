#!/usr/bin/env python3
"""Figure — why one 16-mer spans three partners' junctions.

THE RESULT THIS HAS TO MAKE LEGIBLE. A single gapmer, 5'-GGGCATATCATCAAAC-3', is junction-spanning
and fusion-specific at EWSR1::NR4A3, TAF15::NR4A3 and FUS::NR4A3 at once. Stated as a sentence that
sounds like a coincidence. Drawn, the mechanism is visible in one line: the three donors' last ten
nucleotides before the breakpoint are identical, because EWSR1, TAF15 and FUS are FET-family
paralogues with similar low-complexity amino-termini, and the acceptor side is the same NR4A3 exon
in all three. The oligonucleotide's 16-nt window lies entirely inside that identity.

⚠ THE SAME PANEL MUST SHOW THE LIABILITY, NOT ONLY THE ASSET. The identity that lets one reagent
cover three fusions is the identity that makes the parent transcripts hard to discriminate from, and
a figure showing only the coverage would be selling the result. The divergent positions are marked,
the gap-level margin is printed, and the caption line says both things.

⛔ SEQUENCES ARE READ FROM `nr4a3-fusion-junction-atlas.json`, never typed. The seam strings, the
donor/acceptor split and the shared donor run all come from the artifact; this script aligns and
draws them, and it asserts the identity it claims rather than assuming it (see `_shared_prefix`).

Dependency-free SVG. No matplotlib, no network.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "modalities", "nr4a3-fusion-junction-atlas.json")
OUT = os.path.join(HERE, "aso-multipartner-seam.svg")

OLIGO = "GGGCATATCATCAAAC"          # the multi-partner lead reagent, looked up in the artifact
CW = 17                              # per-base cell width
W, T, L = 880, 84, 150


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def revcomp(s):
    return s.translate(str.maketrans("ACGTacgt", "TGCAtgca"))[::-1]


def _shared_prefix(seqs):
    """Length of the common SUFFIX of the donor halves — asserted, not assumed."""
    n = 0
    while all(len(s) > n and s[-(n + 1)] == seqs[0][-(n + 1)] for s in seqs):
        n += 1
    return n


def main(argv=None):
    d = json.load(open(SRC))
    entry = d["isoform_coverage"]["multi_partner_exact"][OLIGO]
    labels = [entry["designed_for"]] + list(entry["also_covers"])
    seams = {p["junction_label"]: p["seam_mRNA"] for p in d["panels"]}

    donors, acceptors = [], []
    for lab in labels:
        dn, ac = seams[lab].split("|")
        donors.append(dn)
        acceptors.append(ac)

    shared = _shared_prefix(donors)
    assert all(a == acceptors[0] for a in acceptors), "acceptor halves differ; the figure's premise"
    target = revcomp(OLIGO)
    split = entry["seam_split_per_junction"][labels[0]]
    d_bases, a_bases = split["donor_bases"], split["acceptor_bases"]
    assert target == donors[0][-d_bases:] + acceptors[0][:a_bases], (
        "the oligonucleotide's target window is not the seam window the artifact records")

    ncols = len(donors[0]) + len(acceptors[0])
    #: +166 rather than +150 since 2026-08-19: the handling note added below the margin sentence
    #: is a fourth footer line, and at the old height its baseline sat 8 px from the canvas edge
    #: with descenders inside the last few pixels. An SVG has no overflow, so a line that does
    #: not fit is simply not drawn — the failure mode the chance-baseline panel already hit.
    H = T + len(labels) * 30 + 166
    seam_x = L + len(donors[0]) * CW

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="32" y="30" font-size="15" fill="#111" font-weight="600">'
         f'One 16-mer spans three partners’ breakpoints</text>',
         f'<text x="32" y="48" font-size="12" fill="#555">'
         f'The three FET-family donors are identical over the {esc(shared)} nucleotides before the '
         f'breakpoint, and the acceptor exon is the same in all three.</text>']

    # the target window, shaded behind the sequence rows
    win_x0 = seam_x - d_bases * CW
    p.append(f'<rect x="{win_x0}" y="{T - 16}" width="{(d_bases + a_bases) * CW}" '
             f'height="{len(labels) * 30 + 8}" fill="#fff8e1" stroke="#f9a825" stroke-width="0.9"/>')

    for r, lab in enumerate(labels):
        y = T + r * 30
        gene = lab.split("_")[0]
        p.append(f'<text x="{L - 12}" y="{y}" font-size="11.5" fill="#111" text-anchor="end">'
                 f'{esc(lab.replace("__", "::").replace("_", " "))}</text>')
        row = donors[r] + acceptors[r]
        for c, base in enumerate(row):
            in_donor = c < len(donors[r])
            divergent = in_donor and c < len(donors[r]) - shared and any(
                donors[k][c] != base for k in range(len(donors)))
            fill = "#c62828" if divergent else ("#1565c0" if in_donor else "#2e7d32")
            weight = "700" if divergent else "400"
            # ⛔ COLOUR IS NOT THE ONLY CHANNEL, BECAUSE FOR TWO CLASSES OF READER IT CARRIES
            # NOTHING (2026-08-13). The three roles were encoded as blue donor / green acceptor /
            # red divergent, and the pair the reader most needs to separate — the green acceptor
            # bases and the red divergent ones — sit at almost the same relative luminance (0.18
            # against 0.15). That is the textbook red/green confusion for deuteranopia and
            # protanopia, about 8% of male readers, AND it collapses to the same grey when a
            # journal prints in black and white or a reader photocopies the page. Bold weight was
            # the only non-colour cue and 13px bold monospace is not a cue anyone reliably sees.
            # ⚠ A BOX, NOT A DIFFERENT PALETTE. Re-hueing would fix the colour-blind case and not
            # the greyscale one; a drawn rectangle is legible under both, and under neither does it
            # depend on the reader distinguishing anything at all.
            if divergent:
                p.append(f'<rect x="{L + c * CW + 0.6:.1f}" y="{y - 11}" '
                         f'width="{CW - 1.2:.1f}" height="14" rx="2" '
                         f'fill="none" stroke="#c62828" stroke-width="1.1"/>')
            p.append(f'<text x="{L + c * CW + CW / 2:.1f}" y="{y}" font-size="13" fill="{fill}" '
                     f'font-family="monospace" font-weight="{weight}" '
                     f'text-anchor="middle">{esc(base)}</text>')
        p.append(f'<text x="{L + ncols * CW + 14}" y="{y}" font-size="10.5" fill="#777">'
                 f'{esc(gene)}</text>')

    # seam marker
    p.append(f'<line x1="{seam_x}" y1="{T - 20}" x2="{seam_x}" y2="{T + len(labels) * 30 - 6}" '
             f'stroke="#111" stroke-width="1.4"/>')
    p.append(f'<text x="{seam_x}" y="{T - 26}" font-size="11" fill="#111" text-anchor="middle" '
             f'font-weight="600">breakpoint</text>')

    # the gapmer architecture under the window
    gy = T + len(labels) * 30 + 26
    geom = d["oligo_geometry"]
    wing, gap = geom["wing"], geom["gap"]
    segs = [("LNA wing", wing, "#90a4ae"), ("DNA gap (RNase-H1)", gap, "#ef6c00"),
            ("LNA wing", wing, "#90a4ae")]
    sx = win_x0
    for name, ln, col in segs:
        p.append(f'<rect x="{sx}" y="{gy}" width="{ln * CW}" height="17" fill="{col}" '
                 f'opacity="0.85" stroke="#ffffff"/>')
        p.append(f'<text x="{sx + ln * CW / 2:.1f}" y="{gy + 12}" font-size="9.5" fill="#ffffff" '
                 f'text-anchor="middle">{esc(name)}</text>')
        sx += ln * CW
    p.append(f'<text x="{win_x0}" y="{gy + 33}" font-size="11" fill="#333">'
             f'5′-{esc(OLIGO)}-3′ (antisense), {esc(d_bases)} donor and {esc(a_bases)} '
             f'acceptor bases either side of the seam</text>')

    # ⛔ THE CAPTION DESCRIBED A CUE THE FIGURE NO LONGER USED (2026-08-13). It read "red and bold"
    # after the boxes above were added precisely BECAUSE bold weight is not a cue a reader reliably
    # sees — so the figure's own legend sent a greyscale or colour-blind reader looking for the one
    # distinction it had been redrawn to stop relying on. A figure that describes itself wrongly is
    # worse than one that describes itself thinly, because the reader trusts the legend.
    p.append(f'<text x="32" y="{H - 52}" font-size="10.5" fill="#666">'
             f'Blue, donor exon; green, NR4A3 acceptor exon; boxed and red, positions at which the '
             f'three donors differ. Shaded box, the oligonucleotide’s target window.</text>')
    p.append(f'<text x="32" y="{H - 36}" font-size="10.5" fill="#666">'
             f'The same paralogy that lets one reagent cover three fusions is why these designs are '
             f'hard to discriminate from the parent transcripts: this reagent’s gap-level</text>')
    p.append(f'<text x="32" y="{H - 22}" font-size="10.5" fill="#666">'
             f'margin is {esc(entry["gap_specificity_margin"])} junction-unique '
             f'bases inside the six-nucleotide catalytic gap. Coverage is predicted from sequence '
             f'and has not been measured.</text>')
    #: ⛔ THE PANEL NAMES A SEQUENCE AND CARRIED NO HANDLING NOTE (figure-integrity and safety
    #: screens, 2026-08-19). Every table caption carries the chemistry-and-canonical-file note;
    #: this figure prints the lead reagent and three raw target windows and carried none, while
    #: being one of the most extractable elements in the document.
    p.append(f'<text x="32" y="{H - 8}" font-size="10.5" fill="#666">'
             f'Research use only, not for administration. The bases alone, ordered as unmodified '
             f'DNA, are a different molecule; order from fusion-junction-aso-sequences.csv.</text>')
    p.append('</svg>')

    with open(OUT, "w") as fh:
        fh.write("\n".join(p) + "\n")
    print(f"wrote {OUT}  (shared donor run {shared} nt: {donors[0][-shared:]}; "
          f"gap margin {entry['gap_specificity_margin']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
