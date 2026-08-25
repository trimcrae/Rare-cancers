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
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from aso_figure_text import blend_over_white, check_type_sizes  # noqa: E402
from aso_figure_text import text_width as _text_width  # noqa: E402,F401
from aso_figure_text import wrap as _wrap  # noqa: E402
from aso_figure_text import wrapped_text as _wrapped_text  # noqa: E402,F401

SRC = os.path.join(HERE, "..", "..", "modalities", "offtarget-chance-baseline.json")
OUT = os.path.join(HERE, "aso-chance-baseline.svg")

W, H = 900, 460
L, R, T, B = 78, 28, 72, 104         # margins
PLOT_W, PLOT_H = W - L - R, H - T - B

#: ⛔ 11.5 px IS THE PRINTED FLOOR AT THIS CANVAS. The caveat block was set at 10.5 px, which prints
#: at 5.75-5.89 pt once the renderers scale a 900-px canvas — below every publisher's floor and
#: below the size the junction-space panel was rewritten to clear. `check_type_sizes` is the gate.
FS_TITLE, FS_SUB, FS_KEY = 15, 12, 12
FS_TICK, FS_AXIS, FS_BAND, FS_CAVEAT = 11.5, 12, 11.5, 11.5



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


#: ⛔⛔ SVG DOES NOT WRAP, AND A LONGER SENTENCE IS THEREFORE A CLIPPED ONE (blind screen of the
#: built journal PDF, 2026-08-17, filed as a MAJOR). The round before, this figure's annotations were
#: reworded to fix a real defect — they called an expected value an "upper bound". The corrected
#: wording is longer, `<text>` has no width to wrap against, and two lines ran past the canvas and
#: stopped mid-word: "one mole" and 'It separates "more than chance"'. Confirmed at 300 dpi as a
#: RENDERING fact, not an extraction artifact.
#:
#: ★ SO THE FIX IS NOT A SHORTER SENTENCE. Editing the prose back under the limit leaves the next
#: edit free to cross it again, which is how this arrived: a wording fix with no width budget behind
#: it. Text is wrapped against the canvas at emit time, so the figure CANNOT produce a line that
#: overruns, whatever anyone writes.
#:
#: ⚠ THE WIDTH MODEL NOW LIVES IN `aso_figure_text`, IMPORTED ABOVE, because two other generators
#: needed it and a per-file instrument only protects the file it was written in. It is re-bound to
#: the private names this module has always exported, so `tests/test_aso_figure_text_fits.py` —
#: which loads THIS module to borrow the metric — keeps measuring the emitted SVG with exactly the
#: model the wrap used.


def _unit_phrase(fs):
    """The artifact's own name for one bar, as a noun phrase. "one distinct oligonucleotide" -> …

    ⛔ THE TITLE NAMED A UNIT THE SERIES IS NOT DRAWN IN (figure-integrity review, 2026-08-19). It
    read "per junction gapmer", and a junction gapmer is a (junction, design) RECORD — there are
    190 of them at real exon junctions and 176 bars on this panel, because nine 16-mers span two or
    three partners' seams. So the one line of the figure most likely to be quoted named the unit
    whose count is the one the panel does NOT draw, over a series whose own subtitle says
    "distinct oligonucleotides", and the manuscript caption had already been corrected to "per
    molecule". Read from `figure_series.unit`, which is where the plotted unit is decided.
    """
    unit = str(fs.get("unit") or "").strip()
    if not unit:
        raise SystemExit(
            "this panel's title names the unit one bar is, and `figure_series.unit` is absent from "
            "offtarget-chance-baseline.json. Re-derive the artifact rather than typing a unit here.")
    return unit[4:] if unit.startswith("one ") else unit


def _n_records(d, fs):
    """How many design RECORDS the plotted molecules were collapsed from, counted from the artifact.

    ⚠ COUNTED, NEVER TYPED, and counted over the seam class the figure plots, so a record admitted
    or excluded upstream moves this number instead of leaving the panel asserting a collapse of the
    wrong size.
    """
    plotted = fs.get("seam_class_plotted")
    return sum(1 for r in (d.get("per_design") or []) if r.get("seam_class") == plotted)


def _caveat_texts(fs, exc, n, ref, above, obs, expected, n_records):
    """The lines that travel ON the figure, because a figure is reused without its caption.

    ⚠ A FUNCTION, NOT AN INLINE BLOCK, so `main` can MEASURE them before it decides the canvas
    height. Measuring after drawing is what let a one-sentence addition overprint the axis title.

    ⛔ THE ZERO-HEIGHT BARS ARE A CAVEAT, NOT A DETAIL (figure-integrity review, 2026-08-19).
    Recomputed from the artifact's own ranked series: 40 of the 176 bars are zero, and a zero bar
    draws nothing at all, which blanks 22.7% of the abscissa. The manuscript caption says so; this
    block — the SELF-CONTAINED version, the one that travels when the panel is lifted out of the
    paper — did not, so a lifted figure read as a 136-bar series starting a fifth of the way in.

    ⛔ AND "ON THE MEAN THE SET COMES IN AT CHANCE" ASSERTED A COMPARISON WITH NEITHER NUMBER ON
    THE PANEL. Both are here now, with the ratio the phrase is a gloss of and the median beside it,
    because the excess is a right tail and not a shift of the whole set.
    """
    gc_lo, gc_hi = exc["above_gc_percent_range"]
    hit_lo, hit_hi = exc["above_offtarget_le1mm_range"]
    zeros = sum(1 for v in obs if not v)
    mean = statistics.mean(obs)
    median = statistics.median(obs)
    return [
        #: ⛔ THE DENOMINATOR OF EVERY LINE BELOW IS MOLECULES, AND THE PANEL NEVER SAID SO
        #: (figure-integrity review, 2026-08-19). "118 of 176", "58 of the 176", "40 of the 176" —
        #: a reader who knows the paper reports 190 designs and meets 176 here has no way, from the
        #: panel alone, to tell a collapse from a silently dropped set of fourteen. The marker key
        #: says the multi-seam designs are plotted once; it names neither count, so the arithmetic
        #: is unavailable exactly where the figure is read without its caption.
        (f'One bar is one molecule and not one design record: the {esc(n_records)} design records '
         f'at real exon junctions are {esc(n)} distinct oligonucleotides, because the '
         f'{esc(fs["n_multi_junction_sequences"])} marked designs each span more than one partner’s '
         f'seam and enter the series once rather than once per seam.'),
        (f'The {ref} assumes independent uniform bases; the transcriptome span it is computed over '
         f'is the exhaustive scan\'s measured one. It separates "more than chance" from "at chance" '
         f'and is not a significance test. {esc(fs["n_at_or_below_chance_upper"])} of {esc(n)} bars '
         f'fall at or below that line.'),
        (f'Counts are predictions from sequence search, not measured off-target activity. Bars are '
         f'green at or below the line and red above it, which repeats each bar\'s own height and '
         f'carries no information of its own. '
         f'{esc(fs["n_above_chance_upper"])} of the {esc(n)} plotted designs {above}; on the mean '
         f'the set comes in at chance — {mean:.1f} observed against {expected:.1f} expected, a '
         f'ratio of {mean / expected:.2f}, while the median is {median:g}, so the excess is a long '
         f'right tail rather than a shift of the whole set.'),
        (f'{esc(zeros)} of the {esc(n)} bars are zero and therefore draw nothing at all, so '
         f'{100.0 * zeros / n:.1f}% of the abscissa is blank. The series begins at the left edge, '
         f'not where the first visible bar is.'),
        (f'Not plotted: {esc(exc["n_excluded"])} designs at {esc(exc["n_breakpoints"])} modelled '
         f'breakpoints rather than real exon junctions; {esc(exc["n_above_chance_upper"])} of those '
         f'{above}, at {esc(hit_lo)}\u2013{esc(hit_hi)} matches and '
         f'{esc(gc_lo)}\u2013{esc(gc_hi)}% GC.'),
    ]


def main(argv=None):
    d = json.load(open(SRC))
    lo, hi = d["null_model"]["expected_hits_per_oligo_ge_15_of_16"]
    fs = d["figure_series"]
    exc = fs["excluded"]
    rows = fs["series"]                      # already one per distinct oligonucleotide, ranked
    obs = [r["offtarget_le1mm"] for r in rows]
    multi = [r["n_junctions"] > 1 for r in rows]
    n = fs["n_plotted"]
    n_records = _n_records(d, fs)
    unit = _unit_phrase(fs)
    ymax = max(obs + [hi]) * 1.08

    n_at_or_below = fs["n_at_or_below_chance_upper"]
    scanned = f'{fs["transcripts_scanned"]:,}'
    _at_or_below = "fall at or below it"
    _is_band = f"{lo}" != f"{hi}"
    _ref = "chance band" if _is_band else "chance expectation"
    _above = "exceed that band" if _is_band else "sit above it"

    # ⛔ THE HEADER'S HEIGHT FOLLOWS ITS TEXT, OR A WRAPPED KEY LANDS ON THE PLOT. Wrapping fixed
    # the clipped lines and immediately created the next problem: the key's second line sat at a
    # baseline one unit below the plot's top edge, where a tall bar is. The plot now starts below
    # whatever the key actually occupies, measured rather than assumed, so an edit to the key text
    # moves the axes instead of colliding with them.
    #: ⚠ THE MARKER KEYS THE CLAUSE IT PREFIXES. The diamond is the plot's marker key, and this line
    #: used to open with the 118/176 split — so the glyph appeared to define the split rather than
    #: the marked designs, which is the one thing it does define. The keyed clause now comes first.
    #: ⚠ THE KEY LINE KEYS THE MARKER AND NOTHING ELSE. It used to carry the 118/176 split as well,
    #: grafted onto a diamond legend it has nothing to do with, and with a pronoun ("at or below
    #: it") whose referent arrived only in the following clause. The split now sits with the
    #: caveats, where the line it refers to has already been named.
    _key = (f'the {esc(fs["n_multi_junction_sequences"])} designs spanning '
            f'{_span_words(fs["multi_junction_span"])} partners’ seams, each one molecule plotted '
            f'once.')
    _key_lines = _wrap(_key, FS_KEY, W - R - (L + 14))
    _top = T + max(0, len(_key_lines) - 1) * 15
    #: ⛔⛔ THE CANVAS GROWS TO FIT THE FOOTNOTES; THE FOOTNOTES DO NOT CLIMB INTO THE PLOT
    #: (2026-08-18, filed as a BLOCKER). The caveat block was laid out UPWARD from a fixed H, so
    #: adding one sentence to it — a colour key, itself a fix for a different finding — pushed the
    #: block's first line onto the x-axis title's baseline. Both printed on top of each other and
    #: neither was legible: the figure's only horizontal axis label was destroyed, and so was the
    #: first caveat, mid-sentence. Bottom-anchored layout means every future edit to this text is
    #: one line away from doing it again, so the geometry is now anchored at the TOP and the height
    #: is DERIVED from what the text actually needs.
    _plot_h = 284                                    # the design's plot height, held fixed
    _caveat_step = FS_CAVEAT * 1.30
    _avail = W - R - L
    _caveat_lines = [line for caveat in _caveat_texts(fs, exc, n, _ref, _above, obs, hi,
                                                      n_records)
                     for line in _wrap(caveat, FS_CAVEAT, _avail)]
    _axis_title_y = _top + _plot_h + 38
    _caveats_top = _axis_title_y + 16
    H_eff = int(_caveats_top + len(_caveat_lines) * _caveat_step + 10)

    check_type_sizes(W, H_eff, {
        "caveats": FS_CAVEAT, "axis ticks": FS_TICK, "axis titles": FS_AXIS,
        "chance-line label": FS_BAND, "marker key": FS_KEY, "subtitle": FS_SUB,
        "title": FS_TITLE,
    })

    def x(i):
        return L + (i + 0.5) * PLOT_W / n

    def y(v):
        return _top + _plot_h - (v / ymax) * _plot_h

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H_eff}" '
         f'viewBox="0 0 {W} {H_eff}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H_eff}" fill="#ffffff"/>']

    # the chance band, drawn first so every point sits on top of it
    # ⛔⛔ A ZERO-HEIGHT <rect> DRAWS NOTHING AT ALL — NOT EVEN ITS STROKE (blind screen of the built
    # journal PDF, 2026-08-17, filed as a MAJOR and confirmed by the screener at 600 dpi against the
    # page's vector content: the only horizontal path spanning the plot was the axis baseline).
    # This reference was always emitted as a rect from y(hi) to y(lo). Those coincide — the null
    # gives ONE expected value, 8.2 — so the rect shipped with `height="0.0"`, and the SVG spec is
    # explicit that a zero value for width or height disables rendering of the element. The panel
    # therefore had no line on it, while its own subtitle said "the line is what chance alone
    # predicts" and the caption said "118 of the 176 fall at or below it". A reader had nothing to
    # fall at or below.
    # ⚠ THE EARLIER ROUND FIXED THE WORDS AND NOT THE GEOMETRY. It changed the degenerate "8.2–8.2
    # hits" label to a single value and renamed "band" to "expectation" — correct, and it left the
    # element that draws nothing exactly as it was, because the defect was read as a labelling one.
    # A degenerate range needs BOTH: the right noun and a mark to attach it to.
    #: ⛔⛔ A LINE GOES ON TOP OF THE BARS; A BAND GOES BEHIND THEM — AND THE COMMENT ABOVE WAS
    #: WRITTEN FOR THE BAND (2026-08-25). "Drawn first so every point sits on top of it" is right
    #: for a filled region and wrong for the reference this figure actually draws. Until now the
    #: bars were `opacity="0.85"`, so the line GHOSTED through them and the ordering never showed
    #: itself. Removing that transparency — which had to go, because one transparent element makes
    #: Ghostscript rasterise the whole EPS (see `blend_over_white`) — turned the ghost into an
    #: occlusion: measured on the 300 dpi render, the bars covered the reference wherever a design
    #: exceeded it, which is exactly the population the caption counts ("N of 176 fall at or below
    #: it"). A reader could no longer see the line at the only place the comparison is in doubt.
    #: ★ SO THE LINE IS HELD BACK AND APPENDED AFTER THE BARS, and it is now fully legible across
    #: the whole plot rather than a 15%-contrast ghost — better than either previous state. The
    #: band branch keeps its original position, because a filled region behind the data is correct.
    reference_over_bars = []
    if f"{lo}" == f"{hi}":
        reference_over_bars.append(
            f'<line x1="{L}" y1="{y(hi):.1f}" x2="{L + PLOT_W}" y2="{y(hi):.1f}" '
            f'stroke="#1565c0" stroke-width="1.1" stroke-dasharray="4 3"/>')
    else:
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
    p.append(f'<text x="{L + 8}" y="{y(hi) - 6:.1f}" font-size="{FS_BAND}" fill="#1565c0">'
             f'expected from chance alone for any 16-mer ({_band})</text>')

    # axes
    p.append(f'<line x1="{L}" y1="{_top + _plot_h}" x2="{L + PLOT_W}" y2="{_top + _plot_h}" '
             f'stroke="#444" stroke-width="1"/>')
    p.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{_top + _plot_h}" stroke="#444" stroke-width="1"/>')
    step = 20 if ymax > 60 else 5
    v = 0
    while v <= ymax:
        p.append(f'<line x1="{L - 4}" y1="{y(v):.1f}" x2="{L}" y2="{y(v):.1f}" stroke="#444"/>')
        p.append(f'<text x="{L - 8}" y="{y(v) + 4:.1f}" font-size="{FS_TICK}" fill="#333" '
                 f'text-anchor="end">{v}</text>')
        v += step

    # one bar per DISTINCT oligonucleotide, ranked; above-band designs are the only ones coloured.
    # A multi-partner design carries a marker above its bar: it is one molecule at three seams, and
    # the marker is what tells the reader the three seams were collapsed rather than dropped.
    bw = max(PLOT_W / n - 1.6, 1.2)
    for i, val in enumerate(obs):
        above = val > hi
        col = "#c62828" if above else "#2e7d32"
        #: ⛔ PRE-BLENDED, NOT `opacity=` — see `blend_over_white`. One transparent element makes
        #: Ghostscript rasterise the ENTIRE EPS, and this figure drew 176 of them.
        p.append(f'<rect x="{x(i) - bw / 2:.1f}" y="{y(val):.1f}" width="{bw:.1f}" '
                 f'height="{_top + _plot_h - y(val):.1f}" fill="{blend_over_white(col, 0.85)}"/>')
        if multi[i]:
            #: ⚠ AN OPEN CIRCLE, NOT A DIAMOND (2026-08-19). Table 6 defines ◆ as "a locus returned
            #: by the design Table 2 names as best available at that seam"; this marker means the
            #: multi-junction collapse. One deposit cannot carry a diamond with two unrelated
            #: definitions, and this is the display item whose marker nothing else depends on.
            p.append(f'<circle cx="{x(i):.1f}" cy="{y(val) - 7:.1f}" r="3.4" fill="none" '
                     f'stroke="#111" stroke-width="1.3"/>')

    #: The reference the caption counts against, laid over the bars — see the block that built it.
    p.extend(reference_over_bars)

    p.append(f'<text x="{L}" y="24" font-size="{FS_TITLE}" fill="#111" font-weight="600">'
             f'Transcriptome load per {esc(unit)} against chance expectation</text>')
    p.append(f'<text x="{L}" y="42" font-size="{FS_SUB}" fill="#555">'
             f'{esc(n)} distinct oligonucleotides at real exon junctions, ranked; exact plus '
             f'≤1-mismatch matches over {esc(scanned)} transcripts.</text>')
    # ⚠ the key's marker is a DRAWN SHAPE, not a character. A glyph the installed font lacks
    # renders as a tofu box in the PDF and nowhere else, which is the class of defect that is
    # invisible until a proof arrives; this circle is the same shape the plot itself draws.
    p.append(f'<circle cx="{L + 4.5}" cy="54" r="3.4" fill="none" stroke="#111" '
             f'stroke-width="1.3"/>')
    for _i, _line in enumerate(_key_lines):
        p.append(f'<text x="{L + 14}" y="{58 + _i * 15}" font-size="{FS_KEY}" fill="#555">{_line}</text>')
    p.append(f'<text x="{L + PLOT_W / 2:.0f}" y="{_axis_title_y}" font-size="{FS_AXIS}" fill="#333" '
             f'text-anchor="middle">distinct oligonucleotides, ranked by observed load</text>')
    p.append(f'<text x="18" y="{_top + _plot_h / 2:.0f}" font-size="{FS_AXIS}" fill="#333" '
             f'text-anchor="middle" transform="rotate(-90 18 {_top + _plot_h / 2:.0f})">'
             f'transcriptome matches at ≤1 mismatch</text>')

    # ⚠ the caveats travel ON the figure, because a figure is what gets reused without its caption
    gc_lo, gc_hi = exc["above_gc_percent_range"]
    hit_lo, hit_hi = exc["above_offtarget_le1mm_range"]
    _cursor = _caveats_top
    for _line in _caveat_lines:
        p.append(f'<text x="{L}" y="{_cursor:.1f}" font-size="{FS_CAVEAT}" fill="#666">{_line}</text>')
        _cursor += _caveat_step

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
