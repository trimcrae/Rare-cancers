"""No figure may emit text that runs off its own canvas, or sits on top of its own plot.

⛔ WHY. SVG `<text>` does not wrap. A figure's annotations therefore fit only for as long as nobody
lengthens them, and nothing in the build says otherwise — the SVG is valid, the PDF renders, and the
sentence simply stops. On 2026-08-17 a blind screen of the built journal PDF filed a MAJOR: two
lines of Supplementary Figure S1 ran past the right edge and ended mid-word, at "one mole" and at
'It separates "more than chance"'. Confirmed at 300 dpi as a RENDERING fact, not an extraction one.

⛔⛔ AND THE LENGTHENING WAS ITSELF A FIX. The round before, those same annotations were corrected
for calling an expected value an "upper bound" — a real defect, in which the figure argued against
its own paper. The corrected wording is longer. So a fix with no width budget behind it produced the
next round's finding, which is the third time in this deposit that a remedy created the defect that
followed it. A prose edit cannot be trusted to stay inside a box that nothing measures.

★ WHAT THIS ASSERTS, AND WHY IT IS NOT THE GENERATOR AGREEING WITH ITSELF. It parses the COMMITTED
SVG — the artifact the PDF embeds — and measures each text element with the same pessimistic width
model the generator wraps against. That model is approximate by necessity (no font metrics are
available offline), so it is calibrated to over-estimate: a figure that passes here has margin in
hand, and one that fails is over the edge under any reasonable metric.
"""
from __future__ import annotations

import importlib.util
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.abspath(os.path.join(HERE, "..", "figures"))
CHANCE_GENERATOR = os.path.join(FIGDIR, "aso_chance_baseline_figure.py")

#: The ASO figures this deposit ships. Each must fit its own canvas.
FIGURES = ("aso-chance-baseline.svg", "aso-junction-space.svg",
           "aso-multipartner-seam.svg", "aso-gap-length-tradeoff.svg")

_SVG_SIZE = re.compile(r'<svg[^>]*width="(\d+(?:\.\d+)?)"[^>]*height="(\d+(?:\.\d+)?)"')
_TEXT = re.compile(r"<text\b([^>]*)>([^<]*)</text>")
_ATTR = re.compile(r'([\w:-]+)="([^"]*)"')


def _width_model():
    """The generator's own `_text_width`, so the test and the wrap agree on the metric."""
    spec = importlib.util.spec_from_file_location("aso_chance_baseline_figure", CHANCE_GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._text_width


_text_width = _width_model()


def _elements(svg):
    for match in _TEXT.finditer(svg):
        attrs = dict(_ATTR.findall(match.group(1)))
        text = match.group(2)
        if not text.strip():
            continue
        yield attrs, text


def _declared_text_nodes(svg):
    """How many `<text` elements the file opens, however they are written.

    ⛔ THE DENOMINATOR THAT WAS MISSING. `_TEXT` only matches `<text …>plain characters</text>` —
    a node with no child element and no entity-free content. A generator that starts wrapping its
    labels in `<tspan>`, or that emits `<text><title>…</title>label</text>`, produces a file this
    parser reads as having NO text at all, and every geometry assertion below then holds over an
    empty set and reports green. The count of opening tags is what the file itself declares, and
    the parse has to reach all of it.
    """
    return len(re.findall(r"<text\b", svg))


def _read(name):
    path = os.path.join(FIGDIR, name)
    #: ⛔ NOT A SKIP. These four SVGs are committed deposit artefacts and the PDFs are converted
    #: from them; an absent one is a broken deposit, not an absent test.
    assert os.path.exists(path), f"{name} is missing from {FIGDIR} — the deposit cannot ship it"
    return open(path, encoding="utf-8").read()


@pytest.mark.parametrize("name", FIGURES)
def test_the_figure_declares_a_canvas(name):
    assert _SVG_SIZE.search(_read(name)), (
        f"{name} has no width/height on its <svg> element, so nothing can bound its text")


@pytest.mark.parametrize("name", FIGURES)
def test_every_text_node_the_figure_declares_is_actually_parsed(name):
    """The coverage assertion the geometry checks below all depend on.

    Derived, not typed: the expectation is the figure's own count of `<text` opening tags, so a
    figure that gains or loses labels moves its own floor and a parser that stops seeing them
    fails here rather than passing everything downstream.
    """
    svg = _read(name)
    declared = _declared_text_nodes(svg)
    parsed = list(_elements(svg))
    blank = len(_TEXT.findall(svg)) - len(parsed)
    assert declared, f"{name} draws no text at all — every geometry check below would be vacuous"
    assert len(parsed) + blank == declared, (
        f"{name} declares {declared} <text> node(s) and this parser reads {len(parsed)} non-blank "
        f"plus {blank} blank — {declared - len(parsed) - blank} are invisible to it. The usual "
        "cause is a node with a child element (<tspan>, <title>) or markup inside its content. "
        "Every unparsed label is a label no overflow or overlap check ever looks at.")


@pytest.mark.parametrize("name", FIGURES)
def test_no_text_element_runs_off_the_right_edge(name):
    svg = _read(name)
    size = _SVG_SIZE.search(svg)
    width = float(size.group(1))
    overruns, measured, excluded, unreadable = [], 0, 0, []
    for attrs, text in _elements(svg):
        #: An anchored or rotated label is positioned by its own geometry, not by a left edge, and
        #: measuring it as if it ran rightwards from `x` reports a false overrun. Those are left to
        #: the eye; every unanchored line — which is all the prose — is measured.
        if attrs.get("text-anchor") in ("middle", "end") or "transform" in attrs:
            excluded += 1
            continue
        try:
            x = float(attrs.get("x", 0))
        except ValueError:
            #: ⛔ COUNTED, NOT SWALLOWED. A label whose `x` will not parse is a label nothing bounds,
            #: and `continue` reported that as "measured and fine".
            unreadable.append(text[:60])
            continue
        measured += 1
        font_size = float(attrs.get("font-size", 12))
        right = x + _text_width(text, font_size)
        if right > width:
            overruns.append((round(right), round(width), text[:70]))
    #: THE POPULATION HAS TO ADD UP. Every declared node is measured, excluded by the stated rule,
    #: or blank — nothing may vanish, and at least one node must actually be measured or the
    #: assertion below holds over nothing.
    assert not unreadable, (
        f"{name} has {len(unreadable)} <text> node(s) whose x coordinate will not parse, so "
        f"nothing bounds them: {unreadable[:4]}")
    assert measured, (
        f"{name}: all {excluded} parsed text node(s) are anchored or transformed, so this check "
        "measured nothing at all. Either the generator changed how it positions labels — in which "
        "case the exclusion rule needs rewriting, not the figure — or the parse is broken.")
    assert not overruns, (
        f"{name} emits {len(overruns)} line(s) past its {width:.0f}-unit canvas, which render "
        "CLIPPED MID-WORD in the PDF:\n"
        + "\n".join(f"  ends at {r} (canvas {w}): {t}…" for r, w, t in overruns)
        + "\nSVG does not wrap. Route the text through the generator's _wrap()/_wrapped_text() "
          "rather than shortening it, so the next edit cannot cross the edge again.")


@pytest.mark.parametrize("name", FIGURES)
def test_no_text_element_runs_off_the_bottom(name):
    svg = _read(name)
    size = _SVG_SIZE.search(svg)
    height = float(size.group(2))
    below, measured, unreadable = [], 0, []
    for attrs, text in _elements(svg):
        if "transform" in attrs:
            continue
        try:
            y = float(attrs.get("y", 0))
        except ValueError:
            unreadable.append(text[:60])
            continue
        measured += 1
        if y > height:
            below.append((round(y), round(height), text[:60]))
    assert not unreadable, (
        f"{name} has {len(unreadable)} <text> node(s) whose y coordinate will not parse: "
        f"{unreadable[:4]}")
    assert measured, f"{name}: no text baseline was measured against the canvas height"
    assert not below, (
        f"{name} places {len(below)} line(s) below its {height:.0f}-unit canvas, so they do not "
        "render at all:\n" + "\n".join(f"  baseline {y} (canvas {h}): {t}…" for y, h, t in below))


def test_the_chance_figure_key_does_not_overlap_its_plot_area():
    """The failure the wrap fix created on its way to fixing the clip.

    Wrapping the key turned one line into two, and the second landed a unit below the plot's top
    edge — on top of the tallest bars. The generator now measures the key and starts the plot below
    it; this holds that, by checking the key's last baseline against the axis frame the SVG draws.
    """
    svg = _read("aso-chance-baseline.svg")
    frame = re.search(r'<line x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="([\d.]+)"', svg)
    assert frame, "the chance figure no longer draws an axis line to measure against"
    #: ⚠ MATCH THE MARKER LEGEND ONLY. This used to also match "fall at or below", which later
    #: moved into the bottom caveats — so the test began measuring a line at the FOOT of the figure
    #: against the plot's top and failed on a correct drawing. (It also had an `and`/`or`
    #: precedence bug that made the first clause's `a.get("y")` guard apply to only one branch.)
    keys = [float(a["y"]) for a, t in _elements(svg)
            if a.get("y") and ("partners" in t or "plotted once" in t)]
    assert keys, "the chance figure's marker legend was not found"
    plot_top = min(float(m.group(1)) for m in
                   re.finditer(r'<rect x="[\d.]+" y="([\d.]+)"', svg))
    assert max(keys) < plot_top + 1, (
        f"the key's last baseline is at {max(keys):.0f} and the plot area starts at "
        f"{plot_top:.0f}; the key is drawn over the bars")


def test_the_chance_figure_actually_draws_the_reference_its_caption_describes():
    """⛔ A ZERO-HEIGHT <rect> RENDERS NOTHING, STROKE INCLUDED (2026-08-17, filed as a MAJOR).

    The chance reference was emitted as a rect from y(hi) to y(lo). The null gives ONE expected
    value, so those coincide and the rect shipped with `height="0.0"` — which the SVG spec says
    disables rendering of the element entirely. The panel carried no line while its own subtitle
    read "the line is what chance alone predicts" and the caption read "118 of the 176 fall at or
    below it". A reader had nothing to fall at or below, and a screen confirmed it at 600 dpi.

    ⚠ THE ROUND BEFORE FIXED THE WORDS AND NOT THE GEOMETRY — it corrected the degenerate
    "8.2–8.2 hits" label and the noun "band", and left the element that draws nothing untouched,
    because the defect was read as a labelling one. So this asserts a MARK EXISTS, not a wording.
    """
    svg = _read("aso-chance-baseline.svg")
    marks = []
    for m in re.finditer(r'<line\b([^>]*)/>', svg):
        a = dict(_ATTR.findall(m.group(1)))
        try:
            x1, x2, y1, y2 = (float(a["x1"]), float(a["x2"]), float(a["y1"]), float(a["y2"]))
        except (KeyError, ValueError):
            continue
        #: The reference: horizontal, spanning most of the plot, and not the axis frame (which is
        #: drawn in grey; the reference is the blue dashed one).
        if abs(y1 - y2) < 0.5 and (x2 - x1) > 200 and "dasharray" in m.group(1):
            marks.append((round(y1), round(x2 - x1)))
    assert marks, (
        "the chance figure draws no horizontal reference mark, but its subtitle and caption both "
        "describe 'the line'. A zero-height <rect> is not a line — it renders nothing at all.")

    #: And nothing that is supposed to be visible may be emitted at zero size. Bars for designs
    #: with no hits are legitimately zero-height, so this checks the reference specifically rather
    #: than banning zero sizes outright.
    for m in re.finditer(r'<rect\b([^>]*)/>', svg):
        a = dict(_ATTR.findall(m.group(1)))
        if "dasharray" in m.group(1) and float(a.get("height", 1) or 0) == 0:
            pytest.fail("the chance reference is still a zero-height dashed rect, which does not "
                        "render; emit a <line> when the null's two endpoints coincide")


@pytest.mark.parametrize("name", FIGURES)
def test_no_two_text_lines_are_drawn_on_top_of_each_other(name):
    """⛔ ONE SENTENCE ADDED TO A BOTTOM-ANCHORED BLOCK OVERPRINTED THE AXIS TITLE (2026-08-18).

    Supplementary Figure S1's caveat block was laid out UPWARD from a fixed canvas height, so
    adding a colour key to it — itself the fix for a different finding — pushed the block's first
    line onto the x-axis title's baseline. Both rendered on top of each other and neither could be
    read: the figure's only horizontal axis label was destroyed and so was the caveat, mid-sentence.
    A blind screen filed it as a BLOCKER and measured the overlap at 87% of the smaller box.

    ⚠ THE EXISTING GUARDS COULD NOT SEE IT. One checks text against the CANVAS edges and one checks
    the key against the PLOT; neither compares text to text, so a collision entirely inside the
    canvas passed both. The canvas height is now derived from what the text needs, and this asserts
    the property that failure had: no two lines may share a baseline band and overlap horizontally.
    """
    svg = _read(name)
    boxes = []
    for attrs, text in _elements(svg):
        if "transform" in attrs:
            continue
        try:
            x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
        except ValueError:
            continue
        size = float(attrs.get("font-size", 12))
        width = _text_width(text, size)
        anchor = attrs.get("text-anchor")
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        boxes.append((y, x, x + width, size, text))

    clashes = []
    for i, (y1, a1, b1, s1, t1) in enumerate(boxes):
        for y2, a2, b2, s2, t2 in boxes[i + 1:]:
            #: Two lines collide when their baselines sit within the taller glyph height of each
            #: other AND their horizontal extents overlap by more than a hair.
            if abs(y1 - y2) >= max(s1, s2) * 0.75:
                continue
            overlap = min(b1, b2) - max(a1, a2)
            if overlap > 2:
                clashes.append((round(overlap), t1[:44], t2[:44]))
    assert len(boxes) >= 2, (
        f"{name}: only {len(boxes)} text box(es) were built, so no pair could be compared and this "
        "check is vacuous. The overlap it exists for was 87% of a box, entirely inside the canvas, "
        "and invisible to both edge checks.")
    assert not clashes, (
        f"{name} draws {len(clashes)} pair(s) of text on top of each other, which render as "
        "overprinted and unreadable:\n"
        + "\n".join(f"  {o} units of overlap: {a!r} over {b!r}" for o, a, b in clashes[:4]))
