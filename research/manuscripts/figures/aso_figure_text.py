#!/usr/bin/env python3
"""Shared text metrics and printed-type gate for the four ASO figure generators.

⛔ WHY ONE MODULE AND NOT FOUR COPIES. Two of this deposit's figure defects were width defects and
one was a type-size defect, and each was fixed in the one generator that happened to be under
review:

  * `aso_chance_baseline_figure.py` grew a pessimistic advance-width model and a wrapper after a
    blind screen of the built journal PDF found two of its lines clipped mid-word (2026-08-17);
  * `aso_junction_space_figure.py` grew `_check_type_sizes` after the same screen found its row
    labels printing at 3.88 pt, because the renderers cap a figure's printed HEIGHT and that made
    the height the binding limit (2026-08-17);
  * neither instrument existed in the other two generators, so on 2026-08-19 a review measured
    Figure 3B's count labels at 5.44 pt and Figure 2's architecture labels at 5.56 pt — both below
    every publisher's floor, both invisible to every gate in the repository.

A per-file instrument only protects the file it was written in. These live here so a fifth figure
inherits them, and so `RENDER_TARGETS` — which mirrors the stylesheets, and is the fact the type
gate turns on — has ONE home rather than one per generator.

⚠ THE WIDTH MODEL IS APPROXIMATE ON PURPOSE AND ROUNDS UP. There is no font metric available
offline (no matplotlib, no network), so `_text_width` uses a coarse per-class advance for Helvetica
and over-estimates. Wrapping one word early is invisible; wrapping one word late is the defect.
`tests/test_aso_figure_text_fits.py` measures the emitted SVG against the real canvas with this
same model, so the test and the wrap cannot disagree about the metric.
"""
from __future__ import annotations

#: The three ways an ASO figure is printed, as (available width mm, height ceiling mm). Whichever
#: limit binds decides the scale, so the SMALLEST of the three scales is the one every type size
#: has to clear.
#:
#: ⚠ THESE MIRROR `build_submission_pdf.MANUSCRIPT_CSS` / `JOURNAL_CSS` and
#: `svg_to_submission_formats.DEFAULT_WIDTH_MM`. They are restated here because a figure generator
#: cannot import either without dragging a PDF builder into a dependency-free drawing script; a
#: change there that shrinks a figure must be reflected here, or this gate is measuring a page
#: nobody prints.
RENDER_TARGETS = {
    "manuscript style (174 mm text width, 218 mm ceiling)": (174.0, 218.0),
    "journal style (182 mm column span, 205 mm ceiling)": (182.0, 205.0),
    "standalone deposit figure (180 mm, 247 mm ceiling)": (180.0, 247.0),
}
MM_PER_PT = 25.4 / 72.0

#: ⛔ THE FLOOR, AND IT IS LOAD-BEARING. Below 6 pt no reader reads a label and no publisher accepts
#: one. A generator that cannot meet it must widen or shorten its canvas — raising the font alone
#: only works while the WIDTH is the binding limit, which is exactly the trap Figure 1 fell into.
MIN_PRINTED_PT = 6.0

_NARROW = set("iljItf.,;:'\"|!()[]{}-`")
_WIDE = set("mwMW@%")


def text_width(text, font_size):
    """Pessimistic advance width of `text` at `font_size`, in SVG user units."""
    ems = 0.0
    for ch in str(text):
        if ch in _NARROW:
            ems += 0.30
        elif ch in _WIDE:
            ems += 0.90
        elif ch.isupper() or ch.isdigit():
            ems += 0.62
        elif ch == " ":
            ems += 0.28
        else:
            ems += 0.53
    return ems * font_size


def wrap(text, font_size, max_width):
    """`text` split into the fewest lines that each fit `max_width`. Never splits a word."""
    lines, current = [], ""
    for word in str(text).split():
        trial = f"{current} {word}".strip()
        if current and text_width(trial, font_size) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines or [""]


def wrapped_text(x, y, text, font_size, max_width, fill, leading=1.25, **attrs):
    """One `<text>` per wrapped line, stacked downward. Returns (svg_elements, height_used)."""
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    step = font_size * leading
    out = []
    for i, line in enumerate(wrap(text, font_size, max_width)):
        out.append(f'<text x="{x}" y="{y + i * step:.1f}" font-size="{font_size}" '
                   f'fill="{fill}"{extra}>{line}</text>')
    return out, len(out) * step


#: ⚠ SMALL COUNTS ARE SET AS WORDS, THE WAY THE MANUSCRIPT SETS THEM. A derived count printed as a
#: digit reads as a different register from the prose beside it ("the 10-base-pair criterion" against
#: "the ten-base-pair criterion"), and the fix must not be to type the word — that is how a derived
#: number becomes a typed one. Anything outside the map falls through to its digits.
_WORDS = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
          6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}


def number_word(value):
    """`10` -> "ten"; anything the map does not cover -> its own digits."""
    try:
        return _WORDS.get(int(value), str(value))
    except (TypeError, ValueError):
        return str(value)


def narrowest_target(width_px, height_px):
    """(target name, mm per SVG pixel) for whichever of `RENDER_TARGETS` scales this canvas least."""
    return min(((name, min(w / width_px, h / height_px))
                for name, (w, h) in RENDER_TARGETS.items()), key=lambda pair: pair[1])


def check_type_sizes(width_px, height_px, sizes, minimum=MIN_PRINTED_PT):
    """Raise if any label would print below `minimum` in any render target.

    ⛔ THIS IS THE INSTRUMENT THE DEFECT GOT PAST, TWICE. Provenance hashes the artifacts a figure
    is drawn from, the truncation test decodes the PNG, and the vector test reads the deposited PDF
    — none of them knows how big a label is once the renderer has scaled the canvas. So a legible
    SVG shipped as an illegible figure and every gate stayed green.

    `sizes` is {what the label is: font-size in SVG px}.
    """
    name, scale = narrowest_target(width_px, height_px)
    printed = {label: px * scale / MM_PER_PT for label, px in sizes.items()}
    too_small = {k: v for k, v in printed.items() if v < minimum}
    if too_small:
        detail = ", ".join(f"{k} {v:.2f} pt" for k, v in sorted(too_small.items()))
        raise SystemExit(
            f"in-figure type would print below {minimum} pt in the {name}: {detail}. "
            f"The canvas is {width_px} x {height_px} px and that target scales it by "
            f"{scale:.5f} mm/px. Widen the canvas or shorten it — raising the font alone only "
            f"works while the WIDTH is the binding limit.")
    return name, scale, printed
