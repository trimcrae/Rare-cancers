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


def _read(name):
    path = os.path.join(FIGDIR, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} has not been drawn")
    return open(path, encoding="utf-8").read()


@pytest.mark.parametrize("name", FIGURES)
def test_the_figure_declares_a_canvas(name):
    assert _SVG_SIZE.search(_read(name)), (
        f"{name} has no width/height on its <svg> element, so nothing can bound its text")


@pytest.mark.parametrize("name", FIGURES)
def test_no_text_element_runs_off_the_right_edge(name):
    svg = _read(name)
    size = _SVG_SIZE.search(svg)
    width = float(size.group(1))
    overruns = []
    for attrs, text in _elements(svg):
        #: An anchored or rotated label is positioned by its own geometry, not by a left edge, and
        #: measuring it as if it ran rightwards from `x` reports a false overrun. Those are left to
        #: the eye; every unanchored line — which is all the prose — is measured.
        if attrs.get("text-anchor") in ("middle", "end") or "transform" in attrs:
            continue
        try:
            x = float(attrs.get("x", 0))
        except ValueError:
            continue
        font_size = float(attrs.get("font-size", 12))
        right = x + _text_width(text, font_size)
        if right > width:
            overruns.append((round(right), round(width), text[:70]))
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
    below = []
    for attrs, text in _elements(svg):
        try:
            y = float(attrs.get("y", 0))
        except ValueError:
            continue
        if "transform" in attrs:
            continue
        if y > height:
            below.append((round(y), round(height), text[:60]))
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
    keys = [float(a["y"]) for a, t in _elements(svg)
            if a.get("y") and "fall at or below" in t or "plotted once" in t]
    assert keys, "the chance figure's key text was not found"
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
