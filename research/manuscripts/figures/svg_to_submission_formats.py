#!/usr/bin/env python3
"""Render a committed figure SVG to the two formats a journal actually asks for: vector PDF and a
300 dpi PNG.

WHY THIS EXISTS AT ALL. The three ASO figures are dependency-free SVG, written by hand-rolled
generators precisely so that no plotting library has to be installed to reproduce them. That is the
right trade for reproducibility and the wrong one for submission: Springer Nature (and every other
publisher) wants line art as vector PDF or EPS, with a raster companion at >=300 dpi, and no
submission portal accepts a bare `.svg`. So the SVG stays the source of truth and this script is the
only step that turns it into deliverables. Nothing here draws, computes or restyles anything --- if a
number is wrong, the generator and its artifact are where it is wrong, never this file.

WHY HEADLESS CHROMIUM AND NOT A LIBRARY. Measured in this sandbox on 2026-08-12: there is no
`cairosvg`, no `PIL`, no `matplotlib`, no `inkscape`, no `rsvg-convert`, and no `playwright` python
package. There IS a full Chromium at `/opt/pw-browsers/chromium` (it ships with the Playwright
browser bundle for unrelated reasons), and Chromium's `--print-to-pdf` goes through Skia's PDF
backend, which emits real vector paths and real embedded text rather than a rasterised page. Two
things follow, and the second is the one that matters:

  * it needs no install, no `pip`, and no network, so this script runs in CI and in this sandbox
    identically; and
  * it is the SAME renderer that draws the SVG when a reviewer opens the file in a browser, so the
    PDF is a faithful copy of the thing that was inspected before it shipped. A separate rasteriser
    (cairo, librsvg) would be a second implementation of SVG with its own font handling and its own
    disagreements, and a figure that looks right in the browser and wrong in the PDF is exactly the
    class of defect nobody catches until a proof arrives.

VERIFIED VECTOR, NOT A PICTURE OF A FIGURE. The output PDF carries subsetted TrueType fonts
(`AAAAAA+LiberationSans`, `BAAAAA+LiberationSans-Bold`) and ~640 `Tj` text-showing operators for
Figure 3, not a single embedded image. That is worth stating because "print to PDF" is a phrase that
also describes screenshot-into-a-page, and the whole reason a journal wants vector is that the text
stays selectable and the strokes stay resolution-free.

FONTS ARE SUBSTITUTED, AND THE SUBSTITUTION IS THE CORRECT ONE. The generators ask for
`Helvetica,Arial,sans-serif`. Neither Helvetica nor Arial is installed here (`fc-list` shows 59
faces, none of them either), so fontconfig resolves the stack to **Liberation Sans**, which is
metric-compatible with Arial by design --- same advance widths, so every label occupies exactly the
box the generator's layout assumed. This is a substitution the figure was always going to undergo on
any machine without licensed Arial, and it is benign; it is recorded here so that a future reader
comparing a PDF built elsewhere does not mistake a font name for a rendering bug.

GEOMETRY, AND THE ONE MEASURED SURPRISE. The page is sized to fit a BOX --- 180 mm wide (Springer
Nature's full double-column measure, comfortably inside the 7.5 in ceiling `check_figure_specs.py`
enforces) by 247 mm tall (a figure page) --- at the SVG's own aspect ratio, with whichever limit
binds first deciding the scale and the readout naming which one it was.
Chromium QUANTIZES `@page size`: asking for 180 mm x 86 mm yields a MediaBox of 510 x 244.08 pt
(179.917 mm x 86.106 mm), and it does so identically whether the request is spelled in mm, pt or in.
The drawn content, however, lands at exactly 510.236 x 243.780 pt --- exactly the 180 x 86 mm asked
for --- so the ~0.08 mm disagreement is between the page box and the ink, not a distortion of the
ink. The SVG is given `width:100%;height:100%` and keeps its default `preserveAspectRatio`
(`xMidYMid meet`), so it can only ever letterbox, never stretch and never crop drawn content; the
sliver that overhangs the page edge is background whitespace. `_check_page_geometry` asserts the
scale is isotropic and the aspect error is small, and fails loudly if a future Chromium changes this,
rather than shipping a silently squashed figure.

WHY THE PNG NEEDS A CHUNK WRITTEN BY HAND. Chromium's `--screenshot` emits a PNG with `IHDR` and
`IDAT` and nothing else --- no `pHYs`, so no resolution. `check_figure_specs.py` reads
`im.info["dpi"]`, would get nothing, and would tell you to regenerate at 300 dpi a figure that is
already there. So this script writes the `pHYs` chunk itself, in pure stdlib. Note what it is and is
not: the DETAIL is carried entirely by the pixel count, which is computed as
`width_mm / 25.4 * dpi` and rendered at that many pixels; `pHYs` only records the physical size those
pixels were authored for. The header is therefore never a claim about detail that was not rendered,
which is the failure `check_figure_specs.py`'s docstring warns about ("REGENERATE at 300, do not
relabel"). The stored value is pixels-per-metre as an INTEGER, so 300 dpi is written as 11811 ppm and
reads back as 299.9994 dpi --- identical to what matplotlib writes for every other figure in this
directory, and the reason that file's honest bar is 299 and not 300.

DETERMINISM. Re-running this on unchanged inputs must produce byte-identical files, so that a
regenerated deliverable shows up in `git status` only when the figure really changed. Two sources of
noise are removed: Skia stamps `/CreationDate` and `/ModDate` with the wall clock, which are
overwritten in place with a fixed timestamp of *identical byte length* (so the xref offsets stay
valid and the PDF stays loadable), and the wrapper's `<title>` --- which Chromium copies into the
PDF `/Title` --- is set from the output filename rather than from a path or a clock. Set
`SOURCE_DATE_EPOCH` to choose the stamp; it defaults to a fixed constant.

NO NETWORK, BY CONSTRUCTION. The SVG is inlined into the wrapper rather than referenced with
`<img src=...>`, so the page has no subresources to fetch and no dependence on where the file sits
on disk. Chromium is additionally launched with background networking, component updates, sync and
first-run behaviour all disabled.

    python3 research/manuscripts/figures/svg_to_submission_formats.py            # the three ASO figures
    python3 research/manuscripts/figures/svg_to_submission_formats.py --all      # every *.svg here
    python3 research/manuscripts/figures/svg_to_submission_formats.py \
        --svg research/manuscripts/figures/aso-chance-baseline.svg --width-mm 88 --dpi 600
"""
import argparse
import binascii
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))

# The figures of the ASO research article, in manuscript order. Named explicitly rather than
# globbed, because this directory also holds matplotlib-authored figures that already have their
# PDF and PNG and must not be re-rendered through a different pipeline.
# ⚠ THE ORDER CHANGED ON 2026-08-15 AND THE ORDER IS THE POINT. External review observed that the
# paper's most original result — the gap-length identity of section 3.8 — was buried with no figure,
# while Figure 2 was given to the multi-partner molecule, which section 3.2 states is a hypothesis
# about junctions no patient is known to carry. Visual emphasis was contradicting the paper's own
# caveat. The gap-length figure is now Figure 2, the multi-partner seam is Figure 3, and the
# chance-expectation bar chart moved to the supplement.
ASO_FIGURES = [
    "aso-junction-space.svg",         # Figure 1
    "aso-gap-length-tradeoff.svg",    # Figure 2  (was: none — the result had no figure)
    "aso-multipartner-seam.svg",      # Figure 3  (was: Figure 2)
    "aso-chance-baseline.svg",        # Supplementary Figure S1 (was: Figure 3)
]

# Springer Nature's full double-column measure. 180 mm = 7.087 in, inside check_figure_specs.py's
# 7.5 in ceiling. Single column is 88 mm; pass --width-mm to choose it.
DEFAULT_WIDTH_MM = 180.0
DEFAULT_DPI = 300

# ⚠ WIDTH IS NOT THE ONLY BINDING DIMENSION, AND FOR ONE OF THESE THREE IT IS NOT THE BINDING ONE.
# A figure page has a height too --- 247 mm at Springer Nature, once running heads and the caption
# are allowed for. Figure 1 is a portrait grid, 760 x 1509 px, so setting it to the 180 mm double
# column makes it 357 mm tall: half a metre of figure on a 297 mm page, which the production system
# would silently shrink to fit and which would therefore NOT be the size anything here reported.
# So the target is a BOX, not a width: whichever of the two limits binds first decides the scale,
# and the reported physical size is the one that survives that choice.
DEFAULT_MAX_HEIGHT_MM = 247.0

MM_PER_IN = 25.4
PT_PER_IN = 72.0
CSS_PX_PER_IN = 96.0

# A fixed PDF timestamp, used when SOURCE_DATE_EPOCH is unset. The exact instant is arbitrary and
# meaningless; what matters is that it never changes, so two renders of one figure agree byte for
# byte. Must stay 14 digits so the in-place overwrite preserves the PDF's byte offsets.
FIXED_PDF_DATE = "20000101000000"

CHROMIUM_CANDIDATES = [
    os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"), "chromium"),
    "/opt/pw-browsers/chromium",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]

# Everything that stops Chromium reaching the network, touching a shared profile, or varying its
# output run to run. `--no-sandbox` is required because this runs as root in a container.
BASE_FLAGS = [
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--hide-scrollbars",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-sync",
    "--disable-default-apps",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-client-side-phishing-detection",
    "--metrics-recording-only",
    "--disable-breakpad",
    "--force-color-profile=srgb",
    "--disable-lcd-text",            # grayscale AA: subpixel AA would bake the display's stripe order into the PNG
]


class ConversionError(RuntimeError):
    pass


def find_chromium():
    """Locate a Chromium binary, or say precisely what was looked for and not found."""
    for path in CHROMIUM_CANDIDATES:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            return path
    found = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("chrome")
    if found:
        return found
    raise ConversionError(
        "no Chromium found. Looked at: " + ", ".join(CHROMIUM_CANDIDATES) + ". This script needs a "
        "browser to rasterise and to print; it deliberately has no library fallback, because none is "
        "installed here and a second SVG implementation would render differently from the one the "
        "figure was inspected in.")


def svg_dimensions(svg_text):
    """The SVG's intrinsic size in CSS px, preferring the viewBox.

    The viewBox is the authority because it is what the drawing's coordinates are expressed in; the
    width/height attributes are a default presentation size and a generator is free to disagree with
    them. These three generators do not, but reading the viewBox means this works for any SVG.
    """
    head = svg_text[:2000]
    m = re.search(r'viewBox\s*=\s*["\']\s*([-\d.eE]+)[,\s]+([-\d.eE]+)[,\s]+'
                  r'([-\d.eE]+)[,\s]+([-\d.eE]+)\s*["\']', head)
    if m:
        return float(m.group(3)), float(m.group(4))
    m_w = re.search(r'\bwidth\s*=\s*["\']([\d.]+)(?:px)?["\']', head)
    m_h = re.search(r'\bheight\s*=\s*["\']([\d.]+)(?:px)?["\']', head)
    if m_w and m_h:
        return float(m_w.group(1)), float(m_h.group(1))
    raise ConversionError("could not read a viewBox or a width/height pair from the SVG root")


def build_wrapper(svg_text, title, w_px, h_px, width_mm, height_mm):
    """An HTML page holding the SVG, carrying BOTH output geometries in one document.

    One wrapper rather than two, scoped with `@media print`, so the PDF and the PNG are provably the
    same document rendered twice: on screen the SVG sits at its intrinsic pixel size (so the
    screenshot's pixel count is a clean multiple of it), and in print it fills a page sized in
    millimetres. Two separate wrappers would have allowed the two deliverables to drift apart in a
    way no check here would notice.
    """
    # An XML declaration or a DOCTYPE is legal at the top of a standalone .svg and illegal in the
    # middle of an HTML document; strip either before inlining.
    body = re.sub(r'^\s*<\?xml[^>]*\?>\s*', '', svg_text)
    body = re.sub(r'^\s*<!DOCTYPE[^>]*>\s*', '', body, flags=re.IGNORECASE)
    return (
        '<!doctype html>\n'
        '<meta charset="utf-8">\n'
        f'<title>{title}</title>\n'
        '<style>\n'
        '  html, body { margin:0; padding:0; background:#ffffff; }\n'
        f'  svg {{ display:block; width:{w_px:g}px; height:{h_px:g}px; }}\n'
        '  @media print {\n'
        f'    @page {{ size:{width_mm:.4f}mm {height_mm:.4f}mm; margin:0; }}\n'
        '    html, body { width:100%; height:100%; overflow:hidden; }\n'
        '    svg { position:absolute; top:0; left:0; width:100%; height:100%; }\n'
        '  }\n'
        '</style>\n'
        f'{body}\n')


def run_chromium(binary, extra_flags, url, profile_dir):
    """Run Chromium once, with a private profile, and surface a real failure as a real failure."""
    cmd = [binary] + BASE_FLAGS + [f"--user-data-dir={profile_dir}"] + extra_flags + [url]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
    if proc.returncode != 0:
        raise ConversionError(
            f"chromium exited {proc.returncode}\ncmd: {' '.join(cmd)}\n"
            f"stderr tail:\n{proc.stderr.decode('utf-8', 'replace')[-2000:]}")
    return proc


# --------------------------------------------------------------------------------------------
# PDF


def _pdf_media_box(data):
    m = re.search(rb'/MediaBox\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]', data)
    if not m:
        raise ConversionError("no /MediaBox in the produced PDF; it is not a page-shaped document")
    return tuple(float(x) for x in m.groups())


def _check_page_geometry(data, w_px, h_px):
    """Fail loudly if the figure was distorted or the page came out the wrong shape.

    The failure this guards against is silent: a squashed figure is a finished-looking figure, and
    nobody re-measures a PDF that opened. Two independent checks --- the page's own aspect ratio, and
    the isotropy of the transform Skia actually wrote into the content stream --- because the first
    would not catch a uniform page with a non-uniform `cm`.
    """
    x0, y0, x1, y1 = _pdf_media_box(data)
    page_w, page_h = x1 - x0, y1 - y0
    want = w_px / h_px
    got = page_w / page_h
    if abs(got - want) / want > 0.01:
        raise ConversionError(
            f"page aspect {got:.5f} differs from the SVG's {want:.5f} by more than 1% --- the figure "
            f"would be letterboxed or cropped, not merely rounded")
    m = re.search(rb'\bq\s+([\d.]+)\s+0\s+0\s+([\d.]+)\s+0\s+0\s+cm', data)
    if m:
        sx, sy = float(m.group(1)), float(m.group(2))
        if sx and abs(sx - sy) / sx > 1e-6:
            raise ConversionError(f"anisotropic scale in the PDF content stream: {sx} x {sy} --- the "
                                  f"drawing is stretched")
    return page_w, page_h


def _pdf_fix_dates(path):
    """Overwrite Skia's wall-clock timestamps with a fixed one, IN PLACE and at identical length.

    A PDF's cross-reference table stores absolute byte offsets, so a replacement of a different
    length silently corrupts the file. Chromium always writes `D:YYYYMMDDHHMMSS+00'00'`, and the
    substitute is built to that exact shape; the length is asserted rather than assumed.
    """
    stamp = os.environ.get("SOURCE_DATE_EPOCH")
    if stamp:
        import time
        digits = time.strftime("%Y%m%d%H%M%S", time.gmtime(int(stamp)))
    else:
        digits = FIXED_PDF_DATE
    data = open(path, "rb").read()
    n = 0

    def sub(m):
        nonlocal n
        old = m.group(0)
        new = m.group(1) + b"(D:" + digits.encode() + b"+00'00')"
        if len(new) != len(old):
            raise ConversionError(
                f"date replacement would change the PDF's length ({len(old)} -> {len(new)}) and "
                f"invalidate every xref offset; refusing")
        n += 1
        return new

    data = re.sub(rb"(/(?:CreationDate|ModDate)\s*)\(D:\d{14}\+00'00'\)", sub, data)
    open(path, "wb").write(data)
    return n


def render_pdf(binary, wrapper_url, out_path, w_px, h_px, profile_dir):
    run_chromium(binary, ["--print-to-pdf=" + out_path, "--no-pdf-header-footer"],
                 wrapper_url, profile_dir)
    if not os.path.exists(out_path):
        raise ConversionError(f"chromium reported success but wrote no {out_path}")
    data = open(out_path, "rb").read()
    if not data.startswith(b"%PDF"):
        raise ConversionError(f"{out_path} is not a PDF")
    page_w_pt, page_h_pt = _check_page_geometry(data, w_px, h_px)
    n_text = data.count(b"/Font")
    _pdf_fix_dates(out_path)
    return page_w_pt, page_h_pt, n_text


# --------------------------------------------------------------------------------------------
# PNG


def _png_chunks(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ConversionError("not a PNG")
    i = 8
    out = []
    while i < len(data):
        (ln,) = struct.unpack(">I", data[i:i + 4])
        typ = data[i + 4:i + 8]
        out.append((typ, data[i + 8:i + 8 + ln]))
        i += 12 + ln
        if typ == b"IEND":
            break
    return out


def _png_build(chunks):
    out = [b"\x89PNG\r\n\x1a\n"]
    for typ, payload in chunks:
        out.append(struct.pack(">I", len(payload)))
        out.append(typ)
        out.append(payload)
        out.append(struct.pack(">I", binascii.crc32(typ + payload) & 0xFFFFFFFF))
    return b"".join(out)


def png_set_resolution(path, dpi):
    """Insert (or replace) the pHYs chunk that records what physical size these pixels are for.

    Stored as pixels per METRE, as an integer, which is why 300 dpi reads back as 299.9994 --- see
    the module docstring and `check_figure_specs.py`. pHYs must precede IDAT, so it goes directly
    after IHDR.
    """
    chunks = [c for c in _png_chunks(open(path, "rb").read()) if c[0] != b"pHYs"]
    ppm = int(round(dpi / 0.0254))
    phys = (b"pHYs", struct.pack(">IIB", ppm, ppm, 1))
    idx = next(i for i, (t, _) in enumerate(chunks) if t == b"IHDR") + 1
    chunks.insert(idx, phys)
    open(path, "wb").write(_png_build(chunks))
    return ppm * 0.0254


#: ⛔⛔ HEADLESS CHROMIUM'S VIEWPORT IS SHORTER THAN THE WINDOW IT WAS ASKED FOR, AND EVERY FIGURE
#: THIS SCRIPT HAS EVER PRODUCED WAS TRUNCATED BECAUSE OF IT (measured 2026-08-15).
#: `--window-size=W,H` sizes the WINDOW; the viewport it yields is a constant band shorter, and the
#: screenshot is viewport-sized. Anything the page draws below that line is captured as blank white
#: rather than dropped, so the PNG comes out at exactly the requested pixel count, at exactly the
#: requested dpi, with a clean white strip where the bottom of the figure should be. Every check
#: this script performs — pixel count, dpi, aspect ratio, font references — passes on a truncated
#: file, which is why it survived: nothing here was looking at the pixels.
#:
#: MEASURED, by rendering a ruler SVG at four canvas heights: the unpainted band is 86.3 CSS px at
#: H = 300, 460, 664 and 1000. Constant, not proportional. WHAT IT COST, on the three figures that
#: were already deposited: Figure 3's x-axis title and its three caveat lines, including "Counts are
#: predictions from sequence search, not measured off-target activity" and the disclosure of the ten
#: designs not plotted; Figure 2's whole three-line caption, including the sentence its own
#: generator's docstring insists must appear, that the paralogy letting one reagent cover three
#: fusions is what makes those designs hard to discriminate from the parents; and 95 px off the
#: bottom of Figure 1. In each case the line that vanished was a limitation, which is the worst
#: possible selection bias for a silent truncation to have.
#:
#: THE FIX: ask for a window taller than the drawing by more than that band, so the whole page falls
#: inside the viewport, then crop the screenshot back to the drawing's own height. Padding without
#: cropping would deliver a file of the wrong aspect ratio at the wrong dpi.
VIEWPORT_PAD_PX = 220


def png_crop_height(path, keep_rows):
    """Trim a PNG to its first `keep_rows` rows, in place. Pure stdlib: no PIL, no cairo.

    The cropped band is the padding added to defeat the viewport shortfall above, so it is white
    background by construction — but this re-encodes rather than assuming that, because a crop that
    silently kept drawn content would be a second truncation with the same signature as the first.
    """
    chunks = _png_chunks(open(path, "rb").read())
    ihdr = next(payload for typ, payload in chunks if typ == b"IHDR")
    w, h, depth, colour, comp, filt, interlace = struct.unpack(">IIBBBBB", ihdr[:13])
    if depth != 8 or interlace != 0 or colour not in (0, 2, 4, 6):
        raise ConversionError(f"{path}: cannot crop depth {depth} colour {colour} "
                              f"interlace {interlace}")
    if keep_rows >= h:
        return w, h
    nch = {0: 1, 2: 3, 4: 2, 6: 4}[colour]
    stride = w * nch
    raw = zlib.decompress(b"".join(p for t, p in chunks if t == b"IDAT"))
    out, prev, pos = [], bytearray(stride), 0
    for _y in range(keep_rows):
        ft = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
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
        out.append(b"\x00" + bytes(line))          # re-emit with filter None; size is not the point
        prev = line
    new = [(b"IHDR", struct.pack(">IIBBBBB", w, keep_rows, depth, colour, comp, filt, interlace))]
    new += [(t, p) for t, p in chunks if t not in (b"IHDR", b"IDAT", b"IEND")]
    new.append((b"IDAT", zlib.compress(b"".join(out), 9)))
    new.append((b"IEND", b""))
    open(path, "wb").write(_png_build(new))
    return w, keep_rows


def png_dimensions(path):
    data = open(path, "rb").read()
    for typ, payload in _png_chunks(data):
        if typ == b"IHDR":
            return struct.unpack(">II", payload[:8])
    raise ConversionError("no IHDR")


def render_png(binary, wrapper_url, out_path, w_px, h_px, width_mm, dpi, profile_dir):
    """Screenshot at whatever device scale puts `width_mm` worth of pixels on the page at `dpi`.

    The window is the SVG's intrinsic size, so the scale factor is the only lever and the pixel
    count is a clean multiple of the drawing's own coordinates. Chromium rounds the product up to
    a whole pixel, so the delivered dpi is measured back off the file rather than assumed.
    """
    # ceil, not round: rounding DOWN would deliver a file a hair under the requested dpi (measured:
    # 299.9486 for Figure 1 at 124.4 mm), and "just under 300" is the one reading a submission
    # portal is entitled to reject. A spare pixel costs nothing.
    target_px = math.ceil(width_mm / MM_PER_IN * dpi)
    scale = target_px / w_px
    # ⛔ THE WINDOW IS PADDED AND THE SCREENSHOT IS CROPPED BACK. See VIEWPORT_PAD_PX: asking for a
    # window exactly as tall as the drawing leaves the last ~86 CSS px of it outside the viewport,
    # where it is captured as blank white at the correct pixel count and the correct dpi.
    run_chromium(binary, [
        f"--window-size={int(round(w_px))},{int(round(h_px)) + VIEWPORT_PAD_PX}",
        f"--force-device-scale-factor={scale:.10f}",
        "--default-background-color=FFFFFFFF",
        "--screenshot=" + out_path,
    ], wrapper_url, profile_dir)
    if not os.path.exists(out_path):
        raise ConversionError(f"chromium reported success but wrote no {out_path}")
    png_crop_height(out_path, int(math.ceil(h_px * scale)))
    px_w, px_h = png_dimensions(out_path)
    # The honest dpi is the one the delivered pixels actually represent at the target width, not
    # the one that was requested. They differ by Chromium's sub-pixel rounding.
    actual_dpi = px_w / (width_mm / MM_PER_IN)
    if actual_dpi < dpi - 1.0:
        raise ConversionError(
            f"{out_path} came out at {actual_dpi:.1f} dpi, below the {dpi} requested")
    stored = png_set_resolution(out_path, actual_dpi)
    return px_w, px_h, stored


# --------------------------------------------------------------------------------------------


def fit_box(w_px, h_px, width_mm, max_height_mm):
    """Largest size with the SVG's aspect ratio that fits inside the width x height box.

    Returns the size and which limit bound, so the caller can SAY which one it was. A figure
    silently shrunk to fit is the same defect as a figure silently stretched: the number reported
    stops describing the file.
    """
    height_mm = width_mm * h_px / w_px
    if max_height_mm and height_mm > max_height_mm:
        return max_height_mm * w_px / h_px, max_height_mm, "height"
    return width_mm, height_mm, "width"


def convert(svg_path, width_mm=DEFAULT_WIDTH_MM, dpi=DEFAULT_DPI, out_dir=None, binary=None,
            max_height_mm=DEFAULT_MAX_HEIGHT_MM):
    binary = binary or find_chromium()
    svg_path = os.path.abspath(svg_path)
    out_dir = out_dir or os.path.dirname(svg_path)
    stem = os.path.splitext(os.path.basename(svg_path))[0]
    pdf_path = os.path.join(out_dir, stem + ".pdf")
    png_path = os.path.join(out_dir, stem + ".png")

    svg_text = open(svg_path, encoding="utf-8").read()
    w_px, h_px = svg_dimensions(svg_text)
    width_mm, height_mm, bound_by = fit_box(w_px, h_px, width_mm, max_height_mm)
    # The <title> becomes the PDF's /Title. Deriving it from the figure's own name keeps it
    # deterministic and keeps the on-disk path out of the deliverable.
    wrapper = build_wrapper(svg_text, stem, w_px, h_px, width_mm, height_mm)

    with tempfile.TemporaryDirectory(prefix="svg2sub-") as tmp:
        html_path = os.path.join(tmp, "wrapper.html")
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(wrapper)
        url = "file://" + html_path
        profile = os.path.join(tmp, "profile")
        page_w_pt, page_h_pt, n_font = render_pdf(binary, url, pdf_path, w_px, h_px, profile)
        px_w, px_h, stored_dpi = render_png(binary, url, png_path, w_px, h_px,
                                            width_mm, dpi, profile)

    return {
        "svg": svg_path,
        "svg_px": (w_px, h_px),
        "target_mm": (round(width_mm, 3), round(height_mm, 3)),
        "bound_by": bound_by,
        "pdf": pdf_path,
        "pdf_page_pt": (round(page_w_pt, 3), round(page_h_pt, 3)),
        "pdf_page_mm": (round(page_w_pt / PT_PER_IN * MM_PER_IN, 3),
                        round(page_h_pt / PT_PER_IN * MM_PER_IN, 3)),
        "pdf_font_refs": n_font,
        "pdf_bytes": os.path.getsize(pdf_path),
        "png": png_path,
        "png_px": (px_w, px_h),
        "png_dpi": round(stored_dpi, 4),
        "png_width_in": round(px_w / stored_dpi, 3),
        "png_bytes": os.path.getsize(png_path),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--svg", action="append", default=None,
                    help="an SVG to convert; repeatable. Default: the three ASO figures.")
    ap.add_argument("--all", action="store_true", help="convert every *.svg in the figures directory")
    ap.add_argument("--width-mm", type=float, default=DEFAULT_WIDTH_MM,
                    help=f"target printed width (default {DEFAULT_WIDTH_MM:g} mm, "
                         f"Springer Nature double column; single column is 88)")
    ap.add_argument("--max-height-mm", type=float, default=DEFAULT_MAX_HEIGHT_MM,
                    help=f"printed-height ceiling (default {DEFAULT_MAX_HEIGHT_MM:g} mm, a Springer "
                         f"Nature figure page). A portrait figure is scaled down to fit it. 0 disables.")
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI, help=f"PNG resolution (default {DEFAULT_DPI})")
    ap.add_argument("--out-dir", default=None, help="where to write (default: beside the SVG)")
    args = ap.parse_args(argv)

    if args.all:
        targets = sorted(os.path.join(HERE, f) for f in os.listdir(HERE) if f.endswith(".svg"))
    elif args.svg:
        targets = [os.path.abspath(p) for p in args.svg]
    else:
        targets = [os.path.join(HERE, f) for f in ASO_FIGURES]

    missing = [t for t in targets if not os.path.exists(t)]
    if missing:
        print("missing: " + ", ".join(missing), file=sys.stderr)
        return 2

    binary = find_chromium()
    print(f"renderer: {binary}")
    rows = []
    for t in targets:
        r = convert(t, width_mm=args.width_mm, dpi=args.dpi, out_dir=args.out_dir, binary=binary,
                    max_height_mm=args.max_height_mm)
        rows.append(r)
        note = "" if r["bound_by"] == "width" else "   [scaled to the height ceiling, not the width]"
        print(f"\n{os.path.basename(r['svg'])}  ({r['svg_px'][0]:g} x {r['svg_px'][1]:g} px)"
              f"  -> {r['target_mm'][0]:g} x {r['target_mm'][1]:g} mm{note}")
        print(f"  PDF  {os.path.basename(r['pdf']):32s} {r['pdf_page_pt'][0]:8.2f} x "
              f"{r['pdf_page_pt'][1]:7.2f} pt   {r['pdf_page_mm'][0]:7.2f} x "
              f"{r['pdf_page_mm'][1]:6.2f} mm   {r['pdf_font_refs']:3d} font refs   "
              f"{r['pdf_bytes']:8,d} B")
        print(f"  PNG  {os.path.basename(r['png']):32s} {r['png_px'][0]:8d} x {r['png_px'][1]:7d} px   "
              f"{r['png_dpi']:7.4f} dpi   {r['png_width_in']:6.3f} in wide   {r['png_bytes']:8,d} B")
    # ⛔ THE SUMMARY LINE ASSERTED A WIDTH THE RUN ABOVE IT HAD JUST CONTRADICTED (2026-08-13). It
    # printed "at 180 mm wide" unconditionally, including for `aso-junction-space`, which the height
    # ceiling scales to 124.4 mm — and the preprint checklist duly recorded all three figures as
    # "180 mm wide". A per-figure note two lines up said otherwise and the summary won, because a
    # summary is what gets copied. Name the exceptions where the summary is made.
    capped = [r for r in rows if r["bound_by"] != "width"]
    tail = "" if not capped else (
        "; " + ", ".join(f"{os.path.basename(r['svg'])} is {r['target_mm'][0]:g} mm, held by the "
                         f"{args.max_height_mm:g} mm height ceiling" for r in capped))
    print(f"\nwrote {2 * len(rows)} file(s) for {len(rows)} figure(s) at "
          f"{args.width_mm:g} mm wide{tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
