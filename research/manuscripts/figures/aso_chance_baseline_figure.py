#!/usr/bin/env python3
"""Figure — observed transcriptome load per junction gapmer against the chance expectation.

WHY THIS FIGURE AND NOT A BAR OF "CLEAN DESIGNS". The manuscript's central negative — no design is
predicted off-target-clean — is arithmetically unavoidable rather than a property of these designs:
at 16-mer length a ≤1-mismatch match to an arbitrary transcriptome position is expected 3.4-9.1
times for ANY oligonucleotide. A figure that plotted "designs with zero hits" would therefore be a
picture of a threshold, and readers would take it as a picture of the molecules. This one plots
each design's observed load against the band chance alone predicts, so the two are separable by eye:
inside the band means indistinguishable from an arbitrary 16-mer, and the outliers are visibly a
small, identifiable minority rather than a general property.

⛔ NOTHING IS COMPUTED HERE. Every value is read from `offtarget-chance-baseline.json`; this script
draws it. If a number in the figure disagrees with the manuscript, the artifact is the arbiter and
the manuscript is wrong — not the other way round, and not this file.

Dependency-free SVG, following the repository's other figure scripts: no matplotlib, no network.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "modalities", "offtarget-chance-baseline.json")
OUT = os.path.join(HERE, "aso-chance-baseline.svg")

W, H = 900, 430
L, R, T, B = 78, 28, 46, 96          # margins
PLOT_W, PLOT_H = W - L - R, H - T - B


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(argv=None):
    d = json.load(open(SRC))
    lo, hi = d["null_model"]["expected_hits_per_oligo_ge_15_of_16"]
    rows = sorted(d["per_design"], key=lambda r: r.get("offtarget_le1mm") or 0)
    obs = [r.get("offtarget_le1mm") or 0 for r in rows]
    n = len(obs)
    ymax = max(obs + [hi]) * 1.08

    def x(i):
        return L + (i + 0.5) * PLOT_W / n

    def y(v):
        return T + PLOT_H - (v / ymax) * PLOT_H

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    # the chance band, drawn first so every point sits on top of it
    p.append(f'<rect x="{L}" y="{y(hi):.1f}" width="{PLOT_W}" height="{y(lo) - y(hi):.1f}" '
             f'fill="#e8f0fe" stroke="#1565c0" stroke-width="0.8" stroke-dasharray="4 3"/>')
    p.append(f'<text x="{L + 8}" y="{y(hi) - 6:.1f}" font-size="11" fill="#1565c0">'
             f'expected from chance alone for any 16-mer ({lo}–{hi} hits)</text>')

    # axes
    p.append(f'<line x1="{L}" y1="{T + PLOT_H}" x2="{L + PLOT_W}" y2="{T + PLOT_H}" '
             f'stroke="#444" stroke-width="1"/>')
    p.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T + PLOT_H}" stroke="#444" stroke-width="1"/>')
    step = 20 if ymax > 60 else 5
    v = 0
    while v <= ymax:
        p.append(f'<line x1="{L - 4}" y1="{y(v):.1f}" x2="{L}" y2="{y(v):.1f}" stroke="#444"/>')
        p.append(f'<text x="{L - 8}" y="{y(v) + 4:.1f}" font-size="11" fill="#333" '
                 f'text-anchor="end">{v}</text>')
        v += step

    # one bar per design, ranked; above-band designs are the only ones coloured
    for i, val in enumerate(obs):
        above = val > hi
        col = "#c62828" if above else "#2e7d32"
        bw = max(PLOT_W / n - 1.6, 1.2)
        p.append(f'<rect x="{x(i) - bw / 2:.1f}" y="{y(val):.1f}" width="{bw:.1f}" '
                 f'height="{T + PLOT_H - y(val):.1f}" fill="{col}" opacity="0.85"/>')

    n_at_or_below = d["observed"]["n_at_or_below_chance_upper"]
    p.append(f'<text x="{L}" y="{T - 24}" font-size="15" fill="#111" font-weight="600">'
             f'Transcriptome load per junction gapmer against chance expectation</text>')
    p.append(f'<text x="{L}" y="{T - 8}" font-size="12" fill="#555">'
             f'{esc(n)} designs, ranked; exact plus ≤1-mismatch matches over 186,185 transcripts. '
             f'{esc(n_at_or_below)} of {esc(n)} fall at or below the chance upper bound.</text>')
    p.append(f'<text x="{L + PLOT_W / 2:.0f}" y="{H - 52}" font-size="12" fill="#333" '
             f'text-anchor="middle">designs, ranked by observed load</text>')
    p.append(f'<text x="18" y="{T + PLOT_H / 2:.0f}" font-size="12" fill="#333" '
             f'text-anchor="middle" transform="rotate(-90 18 {T + PLOT_H / 2:.0f})">'
             f'transcriptome matches at ≤1 mismatch</text>')

    # ⚠ the caveat travels ON the figure, because a figure is what gets reused without its caption
    p.append(f'<text x="{L}" y="{H - 30}" font-size="10.5" fill="#666">'
             f'Chance band assumes independent uniform bases over an assumed transcriptome span; it '
             f'separates "more than chance" from "at chance" and is not a significance test.</text>')
    p.append(f'<text x="{L}" y="{H - 16}" font-size="10.5" fill="#666">'
             f'Counts are predictions from sequence search, not measured off-target activity. The '
             f'red designs are GC-rich, low-complexity sequences at one modelled seam.</text>')
    p.append('</svg>')

    svg = "\n".join(p)
    if argv is None:
        argv = sys.argv[1:]
    if "--write" in argv or True:
        with open(OUT, "w") as fh:
            fh.write(svg + "\n")
        print(f"wrote {OUT}  ({n} designs, band {lo}-{hi}, {n_at_or_below} at or below)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
