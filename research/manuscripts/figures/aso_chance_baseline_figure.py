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

⛔ ONE BAR IS ONE MOLECULE, AND IT WAS NOT ALWAYS. This figure previously drew one bar per ROW of
`per_design`, and a row is a (junction, design) PAIR. Five of these 16-mers are junction-spanning at
THREE partners' seams at once — the multi-partner designs section 3.2 headlines — so each was drawn
three times and counted three times in the at-or-below fraction. That is pseudoreplication: it
inflates exactly the designs the paper is proudest of, and it inflates the statistic used to defend
them. The series is now the artifact's de-duplicated one, and the five multi-partner sequences carry
a marker so a reader can see that the collapse happened rather than having to trust it.

⛔ AND THE EXCLUDED SET IS NAMED, PLURAL, WITH ITS OWN COUNTS. Ten designs come from TWO modelled
breakpoints rather than from real exon junctions, and FOUR of the ten exceed the band — the caption
that said "a modelled control seam" and "the two extreme outliers" was singular and undercounted on
both. They are not plotted, because grading real-junction designs against sequence no patient
transcript is known to carry is the comparison a reviewer would object to; they are described in
full instead, from the artifact's own `figure_series.excluded` block.

⛔ NOTHING IS COMPUTED HERE. Every value is read from `offtarget-chance-baseline.json`; this script
draws it. If a number in the figure disagrees with the manuscript, the artifact is the arbiter and
the manuscript is wrong — not the other way round, and not this file. The membership of the plotted
series, the at-or-below count, the excluded set and its ranges are all resolved by
`offtarget_chance_baseline.py` and read here as given, so that no second implementation of "which
designs count" can drift away from the first.

Dependency-free SVG, following the repository's other figure scripts: no matplotlib, no network.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "modalities", "offtarget-chance-baseline.json")
OUT = os.path.join(HERE, "aso-chance-baseline.svg")

W, H = 900, 460
L, R, T, B = 78, 28, 72, 104         # margins
PLOT_W, PLOT_H = W - L - R, H - T - B



#: ⛔ A PYTHON LIST LITERAL REACHED THE RENDERED FIGURE (fixed 2026-08-17). The subtitle interpolated
#: `multi_junction_span` straight into the SVG, so a blind screen of the deposit PDF read
#: "spanning [2, 3] partners' seams — one molecule, plotted once, not [2, 3] times". The legend
#: beneath said it correctly in words. A reader of the figure alone saw source code.
#: ⚠ The old wording also overran the panel and clipped its final glyph; saying it once, shorter,
#: fixes both.
def _span_words(span):
    """[2, 3] -> "two or three"; a scalar -> its own word. Never a bracketed literal."""
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
    vals = sorted(span) if isinstance(span, (list, tuple, set)) else [span]
    names = [words.get(v, str(v)) for v in vals]
    if len(names) == 1:
        return names[0]
    return " or ".join([", ".join(names[:-1]), names[-1]]) if len(names) > 2 else " or ".join(names)

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(argv=None):
    d = json.load(open(SRC))
    lo, hi = d["null_model"]["expected_hits_per_oligo_ge_15_of_16"]
    fs = d["figure_series"]
    exc = fs["excluded"]
    rows = fs["series"]                      # already one per distinct oligonucleotide, ranked
    obs = [r["offtarget_le1mm"] for r in rows]
    multi = [r["n_junctions"] > 1 for r in rows]
    n = fs["n_plotted"]
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
    # ⛔ A DEGENERATE RANGE READS AS A FORMATTING FAILURE (blind screen of the built PDF,
    # 2026-08-17). When the two endpoints coincide this printed "(8.2–8.2 hits)", which a reader
    # takes for a broken template rather than for a band of zero width — and the subtitle above
    # still speaks of a "chance upper bound" as though a band existed. Print the single value when
    # there is one value; print the band only when it IS a band.
    _band = f'{lo} hits' if f'{lo}' == f'{hi}' else f'{lo}–{hi} hits'
    # ⛔⛔ IT IS A MEAN, NOT AN UPPER BOUND, AND ONE THIRD OF THE DESIGNS SIT ABOVE IT (blind screen
    # of the built manuscript PDF, 2026-08-17, filed as a MAJOR). The figure's own subtitle read
    # "N of 176 fall at or below the chance UPPER BOUND" and its footnote "58 of the 176 plotted
    # designs exceed the BAND" — of a reference that is the EXPECTED value for an arbitrary 16-mer,
    # 8.2, drawn as a single line because `lo` and `hi` coincide. Nothing can exceed an upper bound,
    # so a reader who takes the word at face value concludes that 58 designs are above chance, which
    # is the opposite of what the caption and §5 say ("the observed mean is 9.2, a ratio of 1.12";
    # "on the mean it comes in at chance"). A figure is the element most often read alone, and this
    # one argued against its own paper.
    # ★ THE NOUN NOW FOLLOWS THE GEOMETRY: a line when the endpoints coincide, a band only when
    # there really are two, so the words cannot drift from what is drawn.
    _is_band = f'{lo}' != f'{hi}'
    _ref = "chance band" if _is_band else "chance expectation"
    _above = "exceed that band" if _is_band else "sit above it"
    _at_or_below = "fall at or below it"
    p.append(f'<text x="{L + 8}" y="{y(hi) - 6:.1f}" font-size="11" fill="#1565c0">'
             f'expected from chance alone for any 16-mer ({_band})</text>')

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

    # one bar per DISTINCT oligonucleotide, ranked; above-band designs are the only ones coloured.
    # A multi-partner design carries a marker above its bar: it is one molecule at three seams, and
    # the marker is what tells the reader the three seams were collapsed rather than dropped.
    bw = max(PLOT_W / n - 1.6, 1.2)
    for i, val in enumerate(obs):
        above = val > hi
        col = "#c62828" if above else "#2e7d32"
        p.append(f'<rect x="{x(i) - bw / 2:.1f}" y="{y(val):.1f}" width="{bw:.1f}" '
                 f'height="{T + PLOT_H - y(val):.1f}" fill="{col}" opacity="0.85"/>')
        if multi[i]:
            cx, cy, s = x(i), y(val) - 7, 4.0
            p.append(f'<polygon points="{cx:.1f},{cy - s:.1f} {cx + s:.1f},{cy:.1f} '
                     f'{cx:.1f},{cy + s:.1f} {cx - s:.1f},{cy:.1f}" fill="#111"/>')

    n_at_or_below = fs["n_at_or_below_chance_upper"]
    scanned = f'{fs["transcripts_scanned"]:,}'
    p.append(f'<text x="{L}" y="24" font-size="15" fill="#111" font-weight="600">'
             f'Transcriptome load per junction gapmer against chance expectation</text>')
    p.append(f'<text x="{L}" y="42" font-size="12" fill="#555">'
             f'{esc(n)} distinct oligonucleotides at real exon junctions, ranked; exact plus '
             f'≤1-mismatch matches over {esc(scanned)} transcripts.</text>')
    # ⚠ the key's marker is a POLYGON, not the character ◆. A glyph the installed font lacks
    # renders as a tofu box in the PDF and nowhere else, which is the class of defect that is
    # invisible until a proof arrives; the polygon is the same shape the plot itself draws.
    p.append(f'<polygon points="{L + 4.5},50 {L + 8.5},54 {L + 4.5},58 {L + 0.5},54" '
             f'fill="#111"/>')
    p.append(f'<text x="{L + 14}" y="58" font-size="12" fill="#555">'
             f'{esc(n_at_or_below)} of {esc(n)} {_at_or_below}; the line is what chance alone '
             f'predicts, not a ceiling. Marked: '
             f'the {esc(fs["n_multi_junction_sequences"])} designs spanning '
             f'{_span_words(fs["multi_junction_span"])} partners’ seams: one molecule, '
             f'plotted once.</text>')
    p.append(f'<text x="{L + PLOT_W / 2:.0f}" y="{H - 66}" font-size="12" fill="#333" '
             f'text-anchor="middle">distinct oligonucleotides, ranked by observed load</text>')
    p.append(f'<text x="18" y="{T + PLOT_H / 2:.0f}" font-size="12" fill="#333" '
             f'text-anchor="middle" transform="rotate(-90 18 {T + PLOT_H / 2:.0f})">'
             f'transcriptome matches at ≤1 mismatch</text>')

    # ⚠ the caveats travel ON the figure, because a figure is what gets reused without its caption
    gc_lo, gc_hi = exc["above_gc_percent_range"]
    hit_lo, hit_hi = exc["above_offtarget_le1mm_range"]
    p.append(f'<text x="{L}" y="{H - 46}" font-size="10.5" fill="#666">'
             f'The {_ref} assumes independent uniform bases; the transcriptome span it is computed '
             f'over is the exhaustive scan\'s measured one. It separates "more than chance" from '
             f'"at chance" and is not a significance test.</text>')
    p.append(f'<text x="{L}" y="{H - 30}" font-size="10.5" fill="#666">'
             f'Counts are predictions from sequence search, not measured off-target activity. '
             f'{esc(fs["n_above_chance_upper"])} of the {esc(n)} plotted designs {_above}; on the '
             f'mean the set comes in at chance.</text>')
    p.append(f'<text x="{L}" y="{H - 14}" font-size="10.5" fill="#666">'
             f'Not plotted: {esc(exc["n_excluded"])} designs at {esc(exc["n_breakpoints"])} '
             f'modelled breakpoints rather than real exon junctions; '
             f'{esc(exc["n_above_chance_upper"])} of those {_above}, at '
             f'{esc(hit_lo)}–{esc(hit_hi)} matches and {esc(gc_lo)}–{esc(gc_hi)}% GC.</text>')
    p.append('</svg>')

    svg = "\n".join(p)
    if argv is None:
        argv = sys.argv[1:]
    if "--write" in argv or True:
        with open(OUT, "w") as fh:
            fh.write(svg + "\n")
        print(f"wrote {OUT}  ({n} distinct designs, band {lo}-{hi}, {n_at_or_below} at or below, "
              f"{exc['n_excluded']} excluded from {exc['n_breakpoints']} modelled breakpoints)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
