#!/usr/bin/env python3
"""Every rendered figure must contain the bottom of the figure.

⛔⛔ WHY THIS EXISTS. Measured 2026-08-15: `svg_to_submission_formats.py` was truncating a constant
86.3 CSS-pixel band off the bottom of every figure it produced, and had been doing so for every
deposited figure. Headless Chromium's `--window-size=W,H` sizes the WINDOW; the viewport it yields
is shorter by a fixed browser-chrome band, and the screenshot is viewport-sized. Content the page
draws below that line is captured as blank white rather than dropped — so the PNG came out at
exactly the requested pixel count, exactly the requested dpi and exactly the right aspect ratio,
with a clean white strip where the bottom of the figure should be.

⛔ EVERY EXISTING CHECK PASSED ON THE TRUNCATED FILES. `check_figure_specs.py` reads dpi, format and
printed width. `aso_figure_provenance.py` hashes the ARTIFACTS a figure was drawn from, so it goes
red when the data moves and can say nothing about what was painted. The converter itself asserts
page geometry, isotropic scale and font references. Not one of them looked at a pixel, which is why
a defect that removed a third of a caption survived every gate in the repository.

⭐ WHAT WAS LOST IS THE PART THAT MAKES THIS WORTH A TEST RATHER THAN A FIX. In each figure the
truncated band held the bottom caption lines, and in this repository the bottom caption line is
where the limitation lives: "Counts are predictions from sequence search, not measured off-target
activity"; the disclosure of the ten designs not plotted; and the sentence stating that the paralogy
which lets one reagent cover three fusions is what makes those designs hard to discriminate from
their parents. A silent truncation that eats captions is a silent truncation that eats caveats.

WHAT THIS ASSERTS. For each figure: find the lowest drawn element in the SVG, then decode the PNG
and confirm painted pixels reach it. Pure stdlib — this repository has no PIL — and slow enough
(a full unfilter of a 2126-pixel-wide image) to be worth the seconds it takes, because the
alternative is trusting a renderer that has already been wrong.
"""
import json
import os
import re
import struct
import zlib

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(os.path.dirname(HERE), "figures")

#: Painting is antialiased and a baseline is not the bottom of a glyph, so the last painted row can
#: legitimately sit a pixel or two either side of the lowest baseline. The defect this catches was
#: 86 pixels, so the tolerance never has to be tight to be useful.
TOLERANCE_SVG_PX = 6.0


#: ⛔ THE FIGURES THIS MUST COVER ARE NAMED BY A COMMITTED ARTIFACT (2026-08-19, lane C2).
#: `if not out: pytest.skip("no rendered ASO figures in this checkout")` meant that losing the
#: PNGs — a partial regeneration, a merge that dropped binaries — turned the truncation guard off
#: entirely and the run stayed green. Worse, the loop's own `if os.path.exists(png)` silently
#: dropped any figure whose raster had gone missing, so coverage could shrink one figure at a time
#: with nothing to show for it. Both are now failures, and the expected set is read from
#: `aso-figure-provenance.json` rather than from whatever is on disk today.
PROVENANCE = os.path.join(FIGS, "aso-figure-provenance.json")


def _svg_files():
    if not os.path.isdir(FIGS):
        pytest.fail(f"the figures directory is missing at {FIGS}; it is committed, and no rendered "
                    "figure is checked for truncation without it.")
    if not os.path.exists(PROVENANCE):
        pytest.fail(f"the figure provenance artifact is missing at {PROVENANCE}; it is committed, "
                    "and it is what names the figures this guard has to cover.")
    expected = sorted(json.load(open(PROVENANCE, encoding="utf-8"))["figures"])
    out, missing = [], []
    for name in expected:
        svg = os.path.join(FIGS, name + ".svg")
        png = os.path.join(FIGS, name + ".png")
        if os.path.exists(svg) and os.path.exists(png):
            out.append((svg, png))
        else:
            missing.append(name + ("" if os.path.exists(svg) else " (no .svg)")
                           + ("" if os.path.exists(png) else " (no .png)"))
    if missing:
        pytest.fail(f"the provenance artifact names {missing}, and the rendered pair is not on "
                    "disk, so those figures are unchecked for truncation. Regenerate them rather "
                    "than letting the guard shrink to what happens to be present.")
    assert out, "the provenance artifact names no figure at all; this guard would assert nothing"
    return out


def _lowest_drawn_y(svg_text):
    """The largest y coordinate the SVG paints anything at (text baselines and element tops)."""
    ys = [float(m) for m in re.findall(r'<text[^>]*\by="([\d.]+)"', svg_text)]
    ys += [float(m) for m in
           re.findall(r'<(?:line|rect|circle|polyline|polygon)[^>]*\b(?:y2|cy)="([\d.]+)"',
                      svg_text)]
    return max(ys) if ys else 0.0


def _png_rows(path):
    """(width, height, channels, unfiltered rows). Stdlib only: no PIL in this environment."""
    data = open(path, "rb").read()
    pos, idat, hdr = 8, [], None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", payload[:13])
        elif typ == b"IDAT":
            idat.append(payload)
    w, h, depth, colour, _comp, _filt, interlace = hdr
    #: ⛔ NOT A SKIP (2026-08-19, lane C2). These PNGs are written by this repository's own
    #: renderer, so an 8-bit non-interlaced encoding is a property of the pipeline. An unexpected
    #: one means the renderer changed under us — which is precisely when the truncation check must
    #: speak, not fall silent for that figure while its siblings report green.
    if depth != 8 or interlace != 0:
        pytest.fail(f"{os.path.basename(path)} is {depth}-bit, interlace={interlace}; this "
                    "repository's renderer writes 8-bit non-interlaced PNGs, so the encoding "
                    "changed and this figure went unmeasured. Teach the reader the new encoding "
                    "rather than skipping the figure.")
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[colour]
    raw = zlib.decompress(b"".join(idat))
    stride = w * nch
    rows, prev, i = [], bytearray(stride), 0
    for _y in range(h):
        ft = raw[i]
        i += 1
        line = bytearray(raw[i:i + stride])
        i += stride
        for x in range(stride):
            a = line[x - nch] if x >= nch else 0
            b = prev[x]
            c = prev[x - nch] if x >= nch else 0
            if ft == 1:
                line[x] = (line[x] + a) & 255
            elif ft == 2:
                line[x] = (line[x] + b) & 255
            elif ft == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if (pa <= pb and pa <= pc) else
                                      (b if pb <= pc else c))) & 255
        rows.append(bytes(line))
        prev = line
    return w, h, nch, rows


def _last_painted_row(w, h, nch, rows):
    last = -1
    for y in range(h):
        row = rows[y]
        if any(row[x * nch] < 200 for x in range(0, w, 3)):
            last = y
    return last


@pytest.mark.parametrize("svg_path,png_path", _svg_files(),
                         ids=lambda p: os.path.basename(p) if isinstance(p, str) else p)
def test_the_rendered_png_reaches_the_bottom_of_the_drawing(svg_path, png_path):
    svg = open(svg_path, encoding="utf-8").read()
    m = re.search(r'<svg[^>]*\bheight="([\d.]+)"', svg)
    assert m, f"{svg_path}: no height on the root <svg>"
    canvas_h = float(m.group(1))
    lowest = _lowest_drawn_y(svg)

    w, h, nch, rows = _png_rows(png_path)
    last = _last_painted_row(w, h, nch, rows)
    assert last >= 0, f"{png_path}: nothing painted at all"
    last_svg_y = last * canvas_h / h

    assert last_svg_y >= lowest - TOLERANCE_SVG_PX, (
        f"{os.path.basename(png_path)} is TRUNCATED: the SVG draws down to y={lowest:.1f} of a "
        f"{canvas_h:.0f}-pixel canvas, but the render stops at y={last_svg_y:.1f}. "
        f"{lowest - last_svg_y:.1f} pixels of the figure — in this repository, usually the caption "
        f"and its caveats — are missing. See VIEWPORT_PAD_PX in svg_to_submission_formats.py.")


@pytest.mark.parametrize("svg_path,png_path", _svg_files(),
                         ids=lambda p: os.path.basename(p) if isinstance(p, str) else p)
def test_the_png_aspect_ratio_still_matches_the_svg(svg_path, png_path):
    """The crop must not overshoot. A short PNG is the failure mode the fix could introduce."""
    svg = open(svg_path, encoding="utf-8").read()
    sw = float(re.search(r'<svg[^>]*\bwidth="([\d.]+)"', svg).group(1))
    sh = float(re.search(r'<svg[^>]*\bheight="([\d.]+)"', svg).group(1))
    data = open(png_path, "rb").read()
    pw, ph = struct.unpack(">II", data[16:24])
    assert abs((pw / ph) - (sw / sh)) < 0.005, (
        f"{os.path.basename(png_path)}: {pw}x{ph} does not match the SVG's {sw:.0f}x{sh:.0f} "
        f"aspect ratio — the pad-and-crop step has cropped the wrong number of rows")
