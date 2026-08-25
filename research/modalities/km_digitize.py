#!/usr/bin/env python3
"""Read a Kaplan-Meier curve off a raster figure, and bound the error of doing so.

WHY THIS EXISTS
---------------
`emc_ipd_survival.py` is a validated reconstruction instrument with an EMPTY input table, and it
says so in its own header: *"Digitizing a published figure requires the figure, and inventing a
coordinate would be fabricating clinical data."* `systems/views/L2-rt-ipd-survival.md` lists the
missing half explicitly --

    | Digitize the curves and numbers-at-risk tables of the open-access EMC series | ⛔ none built |

-- and names the consequence in the same table: the algorithmic control *"bounds algorithmic error
and CANNOT FAIL ON A MIS-READ PIXEL"*, so digitization error in this program is at present not
bounded by anything at all. This module is the missing instrument, and the error bound is its
primary output rather than an afterthought.

WHAT IT DOES
------------
Given a raster image of a survival plot, the pixel coordinates of two known points on each axis,
and a rule for recognising the curve's own pixels, it returns the step function `[[t, S], ...]` in
`CURVE_SCHEMA`'s `digitized` shape, plus per-curve diagnostics that say how much of the reading was
actually supported by pixels and how much was interpolated across a gap.

⛔ IT DOES NOT READ A NUMBERS-AT-RISK TABLE. Guyot's algorithm is driven by that table, and without
one the per-interval censored count is unidentifiable -- `emc_ipd_survival.assess_quality` refuses
such a curve rather than pooling it with a caveat. A risk table is typeset digits, not a curve, and
transcribing digits is a different instrument with a different failure mode (a misread `17` as `12`
is silent and local; a misread curve is loud and global). Transcribe them by hand, from the figure,
and record who did it in `digitized_by`.

★ THE CONTROL, AND THE ONE THING IT CANNOT DO
---------------------------------------------
`--control` renders synthetic Kaplan-Meier figures from cohorts whose patient-level data is known
exactly, degrades them in the ways a real journal figure is degraded, digitizes them back, and
reports the error. Two error scales are reported and they are not interchangeable:

  * `max_abs_km_deviation` -- the largest |S_read - S_true| over the curve. This is the quantity
    `emc_ipd_survival.assess_quality` already grades against, so the control speaks its language.
  * the reconstruction delta -- the digitized curve is fed through `emc_ipd_survival.reconstruct`
    with the TRUE risk table, and the recovered cohort is compared to the cohort that generated the
    figure. This is the number that matters, because a curve is only ever a means to patient-level
    data.

⛔ **A SYNTHETIC RENDER IS AN EASIER FIGURE THAN A JOURNAL FIGURE, SO THIS CONTROL BOUNDS ERROR
FROM BELOW, NOT FROM ABOVE.** It can REFUTE the digitizer -- a rule that cannot read a curve this
module drew itself will certainly not read Chiusole's -- and it cannot certify it. Named, so nobody
has to infer it, the ways a real figure is harder:

  1. lossy compression the renderer does not apply (JPEG is applied when Pillow is importable, and
     the artifact records whether that arm ran -- an absent arm is not a passed arm);
  2. curves drawn over a photographic or textured background;
  3. a legend, an annotation or a p-value box drawn ON TOP of the curve;
  4. two curves of the SAME colour separated only by dash pattern (the module refuses this case
     rather than guessing -- see `extract_series`);
  5. an axis whose calibration points are themselves read by eye, which is upstream of everything
     here and is not modelled at all.

The degradations that ARE modelled -- line width, gridlines, censor ticks, a shaded confidence
band, a second overlapping curve, resampling, additive noise, dashes, and JPEG when available --
are each reported separately rather than averaged, because an average over degradations hides the
one that breaks.

STDLIB ONLY
-----------
PNG decode and encode are implemented here on `zlib`, so the instrument and its control run in CI
with no environment build, exactly like the reconstructor it feeds. Pillow, if importable, is used
for ONE optional arm (JPEG) and for nothing else; its absence removes an arm and never changes a
number.

Run:      python3 research/modalities/km_digitize.py --control
Verify:   python3 research/modalities/km_digitize.py --check
Writes:   research/modalities/km-digitization-error.json
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import struct
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "research", "modalities", "km-digitization-error.json")

# The quality floor `emc_ipd_survival.assess_quality` grades a real curve against. Re-stated here
# ONLY as the control's pass mark; the floor itself is owned by that module (CLAUDE.md rule 1) and
# `_assert_floor_matches_the_reconstructor` fails the build if the two ever drift apart.
FLOOR_MAX_ABS_KM_DEVIATION = 0.05


# ---------------------------------------------------------------------------
# PNG -- decode and encode, on zlib alone
# ---------------------------------------------------------------------------
class Image:
    """An 8-bit RGB raster. `px[y][x]` is an (r, g, b) tuple; y = 0 is the TOP row."""

    __slots__ = ("width", "height", "px")

    def __init__(self, width: int, height: int, px: list[list[tuple[int, int, int]]]):
        self.width = width
        self.height = height
        self.px = px

    @classmethod
    def blank(cls, width: int, height: int, fill=(255, 255, 255)) -> "Image":
        return cls(width, height, [[fill] * width for _ in range(height)])

    def copy(self) -> "Image":
        return Image(self.width, self.height, [row[:] for row in self.px])


_PAETH = lambda a, b, c: (  # noqa: E731 -- kept as one expression to stay next to the spec
    a if abs(b - c) >= abs(a - c) <= abs(a - b) else (b if abs(a - c) >= abs(b - c) else c)
)


def _unfilter(raw: bytes, width: int, height: int, bpp: int, stride: int) -> bytearray:
    """PNG scanline defiltering, filter types 0-4 (RFC 2083 s6)."""
    out = bytearray(stride * height)
    pos = 0
    for y in range(height):
        ft = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        base = y * stride
        prev = base - stride
        if ft == 0:
            pass
        elif ft == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ft == 2:
            if y:
                for i in range(stride):
                    line[i] = (line[i] + out[prev + i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = out[prev + i] if y else 0
                line[i] = (line[i] + ((a + b) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = out[prev + i] if y else 0
                c = out[prev + i - bpp] if (y and i >= bpp) else 0
                line[i] = (line[i] + _PAETH(a, b, c)) & 0xFF
        else:
            raise ValueError(f"unknown PNG filter type {ft} on scanline {y}")
        out[base:base + stride] = line
    return out


def read_png(path: str) -> Image:
    """Decode a non-interlaced 8-bit PNG (grey, RGB, palette, with or without alpha) to RGB.

    ⛔ Refuses rather than guesses on interlaced or 16-bit input. A silently wrong decode would
    produce a plausible curve from a scrambled raster, which is the failure class CLAUDE.md s4
    calls a populated field that was never measured.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG (bad signature)")
    pos, idat, pal, trns = 8, bytearray(), None, None
    width = height = depth = ctype = interlace = None
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctag == b"IHDR":
            width, height, depth, ctype, _comp, _filt, interlace = struct.unpack(">IIBBBBB", body)
        elif ctag == b"PLTE":
            pal = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif ctag == b"tRNS":
            trns = body
        elif ctag == b"IDAT":
            idat += body
        elif ctag == b"IEND":
            break
    if interlace:
        raise ValueError(f"{path}: interlaced PNG is not supported")
    if depth != 8:
        raise ValueError(f"{path}: only 8-bit PNG is supported (got {depth}-bit)")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    stride = width * channels
    raw = zlib.decompress(bytes(idat))
    flat = _unfilter(raw, width, height, channels, stride)
    px: list[list[tuple[int, int, int]]] = []
    for y in range(height):
        row: list[tuple[int, int, int]] = []
        base = y * stride
        for x in range(width):
            i = base + x * channels
            if ctype == 0:
                v = flat[i]
                row.append((v, v, v))
            elif ctype == 4:
                v = flat[i]
                row.append((v, v, v))
            elif ctype == 2:
                row.append((flat[i], flat[i + 1], flat[i + 2]))
            elif ctype == 6:
                row.append((flat[i], flat[i + 1], flat[i + 2]))
            else:  # palette
                row.append(pal[flat[i]])
        px.append(row)
    _ = trns
    return Image(width, height, px)


def write_png(path: str, img: Image) -> None:
    """Encode an RGB Image as a non-interlaced 8-bit PNG."""
    raw = bytearray()
    for row in img.px:
        raw.append(0)
        for r, g, b in row:
            raw += bytes((r & 0xFF, g & 0xFF, b & 0xFF))

    def chunk(tag: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + tag + body + struct.pack(
            ">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", img.width, img.height, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    out += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(out)


# ---------------------------------------------------------------------------
# calibration -- the affine map from pixels to data, and its own error term
# ---------------------------------------------------------------------------
class Calibration:
    """Two known points per axis, given in PIXELS, and the DATA values they carry.

    ⚠ THE CALIBRATION IS READ BY EYE AND THIS MODULE CANNOT CHECK IT. Everything downstream is
    conditional on it, and a one-pixel error in an axis anchor is a systematic shift in every
    coordinate rather than noise around them. `pixel_uncertainty_px` records how confident the
    reader was, and `axis_shift_bound` propagates it into the units the curve is reported in --
    an honest constant offset beats an unstated exact-looking number.
    """

    def __init__(self, x_pix: tuple[float, float], x_val: tuple[float, float],
                 y_pix: tuple[float, float], y_val: tuple[float, float],
                 box: tuple[int, int, int, int], pixel_uncertainty_px: float = 1.0):
        if x_pix[0] == x_pix[1] or y_pix[0] == y_pix[1]:
            raise ValueError("calibration anchors must be distinct pixels on each axis")
        if x_val[0] == x_val[1] or y_val[0] == y_val[1]:
            raise ValueError("calibration anchors must carry distinct data values on each axis")
        self.x_pix, self.x_val = x_pix, x_val
        self.y_pix, self.y_val = y_pix, y_val
        self.box = box  # (x0, y0, x1, y1) inclusive plot interior, in pixels
        self.pixel_uncertainty_px = float(pixel_uncertainty_px)

    def t(self, x: float) -> float:
        f = (x - self.x_pix[0]) / (self.x_pix[1] - self.x_pix[0])
        return self.x_val[0] + f * (self.x_val[1] - self.x_val[0])

    def s(self, y: float) -> float:
        f = (y - self.y_pix[0]) / (self.y_pix[1] - self.y_pix[0])
        return self.y_val[0] + f * (self.y_val[1] - self.y_val[0])

    def units_per_pixel(self) -> tuple[float, float]:
        return (abs((self.x_val[1] - self.x_val[0]) / (self.x_pix[1] - self.x_pix[0])),
                abs((self.y_val[1] - self.y_val[0]) / (self.y_pix[1] - self.y_pix[0])))

    def axis_shift_bound(self) -> dict:
        upt, ups = self.units_per_pixel()
        return {"time_units_per_pixel": upt, "survival_per_pixel": ups,
                "pixel_uncertainty_px": self.pixel_uncertainty_px,
                "systematic_time_shift_bound": upt * self.pixel_uncertainty_px,
                "systematic_survival_shift_bound": ups * self.pixel_uncertainty_px,
                "⚠": "A SYSTEMATIC offset, not noise: it moves every point of the curve the same "
                      "way, so averaging over points does not reduce it and a tight scatter does "
                      "not detect it."}


# ---------------------------------------------------------------------------
# recognising the curve's own pixels
# ---------------------------------------------------------------------------
def color_matcher(rgb: tuple[int, int, int], tol: float = 60.0):
    """Match pixels within `tol` Euclidean RGB distance of a reference colour.

    Anti-aliased edge pixels are blends of the curve and the background, so `tol` is what decides
    how much of the drawn line thickness is seen. It is reported in the artifact rather than
    tuned per figure, because a tolerance chosen to make one curve read well is a fitted parameter.
    """
    r0, g0, b0 = rgb
    t2 = tol * tol

    def match(p):
        dr, dg, db = p[0] - r0, p[1] - g0, p[2] - b0
        return dr * dr + dg * dg + db * db <= t2

    return match


def dark_matcher(max_luma: int = 110, max_chroma: int = 45):
    """Match near-neutral dark pixels: a black curve, but not a coloured gridline or band.

    ⚠ USE ONLY WHEN THE FIGURE HAS EXACTLY ONE BLACK CURVE. With two, this matcher cannot tell
    them apart and `extract_series` refuses -- see its `two_black_curves` guard.
    """
    def match(p):
        r, g, b = p
        return (0.299 * r + 0.587 * g + 0.114 * b) <= max_luma and (max(p) - min(p)) <= max_chroma

    return match


def _columns(img: Image, box, matcher) -> list[list[int]]:
    x0, y0, x1, y1 = box
    cols: list[list[int]] = []
    for x in range(x0, x1 + 1):
        ys = [y for y in range(y0, y1 + 1) if matcher(img.px[y][x])]
        cols.append(ys)
    return cols


def _runs(ys: list[int]) -> list[tuple[int, int]]:
    """Contiguous vertical runs in a column's matched pixel list."""
    if not ys:
        return []
    out, start, prev = [], ys[0], ys[0]
    for y in ys[1:]:
        if y == prev + 1:
            prev = y
            continue
        out.append((start, prev))
        start = prev = y
    out.append((start, prev))
    return out


def estimate_line_width(cols: list[list[int]]) -> float:
    """Median height of the SHORTEST run in each populated column.

    A step curve is horizontal almost everywhere, so the modal run height is the drawn line width;
    the tall runs are the vertical drops and must not be allowed to inflate it. Taking the shortest
    run per column also survives a censor tick, which adds a second short run in the same column.
    """
    heights = sorted(min(hi - lo + 1 for lo, hi in _runs(ys)) for ys in cols if ys)
    if not heights:
        return 1.0
    return float(heights[len(heights) // 2])


def extract_series(img: Image, calib: Calibration, matcher, *,
                   max_gap_columns: int = 12,
                   refuse_if_disjoint_runs_exceed: int = 3,
                   min_start_survival: float | None = 0.90,
                   series_label: str = "series") -> dict:
    """Read one monotone step curve out of the plot box.

    THE ALGORITHM, AND WHY IT IS NOT "TAKE THE DARKEST PIXEL PER COLUMN"
    -------------------------------------------------------------------
    A Kaplan-Meier curve is horizontal except at events, where it drops vertically. In a column
    containing a drop, the matched pixels span the WHOLE drop, so a per-column centroid lands in the
    middle of a vertical segment -- a survival value the curve never takes. The reading therefore
    distinguishes the two cases by run height against the estimated line width:

      * a column whose tallest run is about one line width is FLAT: the value is the run's centre;
      * a taller run is a DROP: the value after it is its BOTTOM edge, minus half a line width,
        because a right-continuous step function takes the post-drop value at that time.

    Monotonicity is then ENFORCED rather than assumed, and every enforcement is COUNTED. A curve
    that needed many fixes was not read cleanly, and `monotonicity_fixes` is how a reviewer sees
    that without re-reading the figure.

    ⛔ IT REFUSES RATHER THAN GUESSES in two cases, both of which produce a confident wrong answer
    if guessed at:
      * `disjoint_runs`: more than `refuse_if_disjoint_runs_exceed` columns hold two or more runs
        separated by more than a line width -- i.e. a SECOND curve of the same colour is in the box,
        and nothing in the pixels says which run belongs to which series;
      * `gap`: a stretch of more than `max_gap_columns` consecutive columns with no matched pixel,
        which is an occlusion (a legend, an annotation) rather than a curve;
      * `does_not_start_at_one`: the reading begins below `min_start_survival`. A Kaplan-Meier
        curve starts at S = 1 by construction, so a reading that does not is not a reading of the
        curve -- the matcher has latched onto a band, a gridline or the axis. ⚠ Set it to None for
        the one legitimate exception, a LANDMARK plot whose axis deliberately starts part-way down;
        that is a property of the figure the caller can see and this function cannot.

    ⭐ WHY A THIRD GUARD EXISTS AT ALL, measured rather than anticipated: loosening the darkness
    threshold to rescue a heavily resampled figure produced a CONFIDENT, ADMISSIBLE-LOOKING, and
    completely wrong curve -- 3 step points, S(0) read as 0.005, every patient reconstructed as an
    event. The reconstruction's own deviation did catch that one, but only because it was gross.
    A refusal is the correct output for an unreadable figure, and a looser threshold is not a fix.
    """
    x0, y0, x1, y1 = calib.box
    cols = _columns(img, calib.box, matcher)
    lw = estimate_line_width(cols)
    populated = sum(1 for ys in cols if ys)
    if populated == 0:
        return {"ok": False, "refusal": "no_pixels_matched", "series_label": series_label,
                "digitized": [], "diagnostics": {"n_columns": len(cols), "n_populated": 0}}

    # --- the same-colour second-curve guard, checked BEFORE any value is produced --------------
    disjoint = 0
    for ys in cols:
        rr = _runs(ys)
        if len(rr) < 2:
            continue
        # a censor tick sits ON the curve, so its run is adjacent; a second curve is far away.
        far = sum(1 for a, b in zip(rr, rr[1:]) if (b[0] - a[1]) > max(3.0, 2 * lw))
        if far:
            disjoint += 1
    if disjoint > refuse_if_disjoint_runs_exceed:
        return {"ok": False, "refusal": "two_black_curves", "series_label": series_label,
                "digitized": [],
                "why": f"{disjoint} columns hold two runs separated by more than a line width. "
                       "Nothing in the pixels assigns a run to a series; digitize each curve "
                       "against its own colour, or crop the figure to one curve.",
                "diagnostics": {"n_columns": len(cols), "n_populated": populated,
                                "est_line_width_px": lw, "disjoint_columns": disjoint}}

    # --- per-column value -----------------------------------------------------------------------
    vals: list[tuple[int, float]] = []
    gap_run = longest_gap = 0
    fixes = 0
    prev_v = None
    for i, ys in enumerate(cols):
        x = x0 + i
        if not ys:
            gap_run += 1
            longest_gap = max(longest_gap, gap_run)
            continue
        gap_run = 0
        rr = _runs(ys)
        lo, hi = max(rr, key=lambda r: r[1] - r[0])
        tall = (hi - lo + 1) > 1.8 * lw
        if tall and prev_v is not None and lo < prev_v - 1.5 * lw:
            # ⭐ A CENSORING TICK, NOT AN EVENT. Both are tall runs, and taking the bottom of one
            # would read a drop of half a tick height at every censored patient -- in an indolent
            # disease that is most of the figure. The discriminator is DIRECTION: a Kaplan-Meier
            # step only ever goes DOWN from the level it was already at, so a run extending
            # meaningfully ABOVE that level straddles the curve and is a mark drawn on it.
            v = prev_v
        elif tall:
            v = hi - (lw - 1) / 2.0          # a drop: take the post-drop level
        else:
            v = (lo + hi) / 2.0              # flat: the centre of the line
        if prev_v is not None and v < prev_v - 1e-9:
            # survival cannot rise. A rise is anti-aliasing or a stray mark, not data.
            v = prev_v
            fixes += 1
        prev_v = v
        vals.append((x, v))

    if longest_gap > max_gap_columns:
        return {"ok": False, "refusal": "gap", "series_label": series_label, "digitized": [],
                "why": f"{longest_gap} consecutive columns hold no curve pixel, which is an "
                       "occlusion rather than a curve. Read the occluded stretch by hand or "
                       "refuse the figure.",
                "diagnostics": {"n_columns": len(cols), "n_populated": populated,
                                "est_line_width_px": lw, "longest_gap_columns": longest_gap}}

    # --- pixels -> data, then compress the run into step points ---------------------------------
    _, ups = calib.units_per_pixel()
    pts: list[list[float]] = []
    last_s = None
    for x, v in vals:
        t, s = calib.t(x), calib.s(v)
        s = min(1.0, max(0.0, s))
        if last_s is None or (last_s - s) >= 0.5 * ups:
            pts.append([round(t, 6), round(s, 6)])
            last_s = s
    if pts:
        tail_t, tail_s = calib.t(vals[-1][0]), min(1.0, max(0.0, calib.s(vals[-1][1])))
        if pts[-1][0] < tail_t:
            pts.append([round(tail_t, 6), round(tail_s, 6)])
    s_at_start = pts[0][1] if pts else None
    if min_start_survival is not None and (s_at_start is None
                                           or s_at_start < min_start_survival):
        return {"ok": False, "refusal": "does_not_start_at_one", "series_label": series_label,
                "digitized": [],
                "why": f"the reading starts at S={s_at_start}, below {min_start_survival}. A "
                       "Kaplan-Meier curve starts at 1, so this is not the curve. Pass "
                       "min_start_survival=None only for a genuine landmark plot.",
                "diagnostics": {"n_columns": len(cols), "n_populated": populated,
                                "est_line_width_px": lw,
                                "survival_at_first_read_column": s_at_start,
                                "monotonicity_fixes": fixes}}
    if pts and pts[0][0] > calib.x_val[0]:
        pts.insert(0, [float(calib.x_val[0]), pts[0][1]])

    return {"ok": True, "series_label": series_label, "digitized": pts,
            "diagnostics": {
                "n_columns": len(cols), "n_populated": populated,
                "n_columns_no_pixel": len(cols) - populated,
                "longest_gap_columns": longest_gap,
                "est_line_width_px": lw,
                "monotonicity_fixes": fixes,
                "survival_at_first_read_column": s_at_start,
                "step_points": len(pts),
                "axis": calib.axis_shift_bound()},
            "⚠": "digitized_by must record WHO calibrated the axes and from WHICH image file. "
                 "This function reads pixels; it cannot know where they came from."}


# ---------------------------------------------------------------------------
# THE CONTROL RENDERER -- a figure whose true cohort is known exactly
# ---------------------------------------------------------------------------
# ⛔ EVERYTHING BELOW DRAWS RATHER THAN READS. It exists so the reader above can be tested against
# a truth established independently of it, and it must never be used to produce a curve that is
# then reported as a reading of a published figure.
class _Rng:
    """A tiny deterministic LCG. `random` would do, but a fixed generator written here means a
    control's noise is reproducible from the source alone, with no seeding convention to remember."""

    def __init__(self, seed: int = 20260825):
        self.s = seed & 0xFFFFFFFF

    def next(self) -> float:
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF

    def normal(self, sigma: float) -> float:
        # Irwin-Hall: 12 uniforms sum to mean 6, variance 1. Cheap and adequate for pixel noise.
        return (sum(self.next() for _ in range(12)) - 6.0) * sigma


class Figure:
    """A rendered survival plot plus the EXACT calibration used to draw it."""

    def __init__(self, img: Image, calib: Calibration, t_max: float):
        self.img = img
        self.calib = calib
        self.t_max = t_max


def _hline(img, y, x0, x1, rgb, width=1):
    for dy in range(width):
        yy = int(round(y + dy - (width - 1) / 2.0))
        if 0 <= yy < img.height:
            for x in range(max(0, int(x0)), min(img.width, int(x1) + 1)):
                img.px[yy][x] = rgb


def _vline(img, x, y0, y1, rgb, width=1):
    if y1 < y0:
        y0, y1 = y1, y0
    for dx in range(width):
        xx = int(round(x + dx - (width - 1) / 2.0))
        if 0 <= xx < img.width:
            for y in range(max(0, int(y0)), min(img.height, int(y1) + 1)):
                img.px[y][xx] = rgb


def render_km(steps: list[tuple[float, float]], *, t_max: float,
              width: int = 760, height: int = 520, line_width: int = 2,
              curve_rgb=(0, 0, 0), gridlines: bool = False,
              censor_times: list[float] | None = None,
              ci_band: float = 0.0, second_curve: list[tuple[float, float]] | None = None,
              second_rgb=(200, 30, 30), dashed: bool = False,
              anchor_error_px: int = 0) -> Figure:
    """Draw a Kaplan-Meier step curve the way a journal draws one.

    `anchor_error_px` shifts the calibration REPORTED to the digitizer without moving a pixel --
    that is the "the axis anchors were read by eye" failure, modelled rather than assumed away.
    """
    left, right, top, bottom = 90, 30, 30, 70
    x0, x1 = left, width - right
    y0, y1 = top, height - bottom
    img = Image.blank(width, height)
    # ⚠ THE BOX MUST INCLUDE S = 1.0, WHICH IS DRAWN AT y0 ITSELF, PLUS THE LINE WIDTH ABOVE
    # IT. A box starting at y0 + 1 clips the whole first flat segment of every curve, and the
    # reader then refuses on a `gap` that is an artefact of the window rather than the figure.
    box = (x0 + 1, max(0, y0 - 4), x1 - 1, y1 - 1)

    def px(t):
        return x0 + (t / t_max) * (x1 - x0)

    def py(s):
        return y1 - s * (y1 - y0)

    if gridlines:
        for frac in (0.25, 0.5, 0.75):
            _hline(img, py(frac), x0, x1, (215, 215, 215))
        for k in range(1, 5):
            _vline(img, px(t_max * k / 5.0), y0, y1, (215, 215, 215))

    if ci_band > 0:
        # a light shaded 95%-style band around the curve -- the masunaga2025 figure shape
        prev_t, prev_s = 0.0, 1.0
        for t, s in steps + [(t_max, steps[-1][1] if steps else 1.0)]:
            for x in range(int(px(prev_t)), int(px(t)) + 1):
                lo, hi = py(min(1.0, prev_s + ci_band)), py(max(0.0, prev_s - ci_band))
                for y in range(int(lo), int(hi) + 1):
                    if y0 < y < y1 and img.px[y][x] == (255, 255, 255):
                        img.px[y][x] = (205, 225, 245)
            prev_t, prev_s = t, s

    def _dashed_hline(y, xa, xb, rgb):
        # 7 on / 4 off in PIXELS, which is what a dashed curve actually looks like. Dashing
        # step-by-step instead would make every gap as long as a flat segment and turn a readable
        # arm into a refusal, which is a property of the renderer, not of dashing.
        x = int(xa)
        while x <= int(xb):
            _hline(img, y, x, min(int(xb), x + 6), rgb, line_width)
            x += 11

    def draw_curve(pts, rgb):
        prev_t, prev_s = 0.0, 1.0
        h = _dashed_hline if dashed else (lambda y, xa, xb, c: _hline(img, y, xa, xb, c, line_width))
        for t, s in pts:
            h(py(prev_s), px(prev_t), px(t), rgb)
            _vline(img, px(t), py(prev_s), py(s), rgb, line_width)
            prev_t, prev_s = t, s
        h(py(prev_s), px(prev_t), px(t_max), rgb)

    if second_curve:
        draw_curve(second_curve, second_rgb)
    draw_curve(steps, curve_rgb)

    if censor_times:
        lookup = [(0.0, 1.0)] + list(steps)
        for ct in censor_times:
            s = 1.0
            for t, v in lookup:
                if t <= ct:
                    s = v
            _vline(img, px(ct), py(s) - 5, py(s) + 5, curve_rgb, max(1, line_width - 1))

    # axes last, so they sit on top exactly as a plotting library draws them
    _hline(img, y1, x0, x1, (0, 0, 0), 2)
    _vline(img, x0, y0, y1, (0, 0, 0), 2)
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        _hline(img, py(frac), x0 - 8, x0 - 1, (0, 0, 0), 2)
    for k in range(6):
        _vline(img, px(t_max * k / 5.0), y1 + 1, y1 + 8, (0, 0, 0), 2)

    calib = Calibration(x_pix=(px(0.0) + anchor_error_px, px(t_max) + anchor_error_px),
                        x_val=(0.0, t_max),
                        y_pix=(py(0.0) + anchor_error_px, py(1.0) + anchor_error_px),
                        y_val=(0.0, 1.0), box=box,
                        pixel_uncertainty_px=1.0 if anchor_error_px else 0.5)
    return Figure(img, calib, t_max)


# ---------------------------------------------------------------------------
# degradations -- what happens to a figure between the plotter and the reader
# ---------------------------------------------------------------------------
def resample(img: Image, factor: float) -> Image:
    """Downscale by box-average then upscale by nearest -- a figure re-rendered at the wrong size.

    This is the degradation a PDF page raster applies, and it is the one that fattens a 1-pixel
    line into an anti-aliased smear.
    """
    w2, h2 = max(2, int(img.width * factor)), max(2, int(img.height * factor))
    small = Image.blank(w2, h2)
    sx, sy = img.width / w2, img.height / h2
    for y in range(h2):
        for x in range(w2):
            xa, xb = int(x * sx), max(int(x * sx) + 1, int((x + 1) * sx))
            ya, yb = int(y * sy), max(int(y * sy) + 1, int((y + 1) * sy))
            n = 0
            r = g = b = 0
            for yy in range(ya, min(yb, img.height)):
                for xx in range(xa, min(xb, img.width)):
                    p = img.px[yy][xx]
                    r += p[0]
                    g += p[1]
                    b += p[2]
                    n += 1
            small.px[y][x] = (r // n, g // n, b // n)
    out = Image.blank(img.width, img.height)
    for y in range(img.height):
        for x in range(img.width):
            out.px[y][x] = small.px[min(h2 - 1, int(y / sy))][min(w2 - 1, int(x / sx))]
    return out


def add_noise(img: Image, sigma: float, seed: int = 20260825) -> Image:
    rng = _Rng(seed)
    out = img.copy()
    for y in range(img.height):
        row = out.px[y]
        for x in range(img.width):
            r, g, b = row[x]
            n = rng.normal(sigma)
            row[x] = (min(255, max(0, int(r + n))), min(255, max(0, int(g + n))),
                      min(255, max(0, int(b + n))))
    return out


def jpeg_roundtrip(img: Image, quality: int) -> Image | None:
    """JPEG the figure and read it back. Returns None when Pillow is not importable.

    ⛔ NONE IS NOT A PASS. The artifact records `jpeg_arm_ran: false` so an absent arm can never be
    mistaken for a survived one.
    """
    try:
        from PIL import Image as PILImage  # noqa: PLC0415 -- optional by design
    except Exception:  # noqa: BLE001
        return None
    buf = io.BytesIO()
    pil = PILImage.new("RGB", (img.width, img.height))
    pil.putdata([p for row in img.px for p in row])
    pil.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    back = PILImage.open(buf).convert("RGB")
    data = list(back.getdata())
    px = [data[y * img.width:(y + 1) * img.width] for y in range(img.height)]
    return Image(img.width, img.height, [[tuple(p) for p in row] for row in px])


# ---------------------------------------------------------------------------
# the control -- render a known cohort, degrade, read it back, report the error
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emc_ipd_survival as ipd_mod  # noqa: E402


def _assert_floor_matches_the_reconstructor() -> None:
    """One fact, one place. The floor is the reconstructor's; this module only quotes it.

    ⛔ A quoted constant that drifts from its source is how a control silently starts grading
    against a bar nobody set. Checked at import rather than in a test, because a stale bar in a
    published artifact is worse than a failing build.
    """
    if abs(ipd_mod.MAX_KM_DEVIATION - FLOOR_MAX_ABS_KM_DEVIATION) > 1e-12:
        raise AssertionError(
            f"km_digitize quotes a KM-deviation floor of {FLOOR_MAX_ABS_KM_DEVIATION} but "
            f"emc_ipd_survival.MAX_KM_DEVIATION is {ipd_mod.MAX_KM_DEVIATION}. The floor is owned "
            "there; update the quote, never the owner.")


_assert_floor_matches_the_reconstructor()


def _step_value(steps: list, t: float) -> float:
    """Right-continuous step lookup: S(t) is the value carried INTO t."""
    s = 1.0
    for tt, ss in steps:
        if tt <= t + 1e-9:
            s = ss
        else:
            break
    return s


def curve_error(read_steps: list, true_steps: list, t_max: float, n_grid: int = 400,
                step_guard: float | None = None) -> dict:
    """|S_read - S_true| on a dense grid, split into the two errors that get conflated.

    ⭐ AT A STEP, THE ERROR IS DOMINATED BY THE TIME AXIS, NOT THE SURVIVAL AXIS. If a drop is read
    one pixel column late, the reading is wrong by a FULL STEP HEIGHT for the width of that column
    -- and a step height is about 1/n. So in a 59-patient series a perfect vertical reading still
    shows ~0.025 of maximum deviation from a one-column timing error, while the same reader on a
    270-patient series shows ~0.004. A single `max` therefore reports mostly cohort size.

    Both numbers are returned and neither is dropped:
      * `max_abs_curve_error` -- everywhere, which is what `assess_quality`'s floor compares to;
      * `max_abs_curve_error_off_step` -- excluding a `step_guard` neighbourhood of every true
        event time, which is the reader's VERTICAL error with the timing question removed.
    """
    if step_guard is None:
        step_guard = t_max / 200.0
    event_times = [t for t, _ in true_steps]
    devs, off = [], []
    for k in range(n_grid + 1):
        t = t_max * k / n_grid
        d = abs(_step_value(read_steps, t) - _step_value(true_steps, t))
        devs.append(d)
        if all(abs(t - et) > step_guard for et in event_times):
            off.append(d)
    return {"max_abs_curve_error": round(max(devs), 4),
            "max_abs_curve_error_off_step": round(max(off), 4) if off else None,
            "mean_abs_curve_error": round(sum(devs) / len(devs), 4),
            "step_guard_time_units": round(step_guard, 4),
            "grid_points": n_grid + 1}


def _cohort_to_figure_inputs(cohort: list[dict], risk_times: list[float]):
    km = ipd_mod.kaplan_meier(cohort)
    steps = [(row["time"], row["survival"]) for row in km]
    risk_table = [[t, sum(1 for r in cohort if r["time"] >= t)] for t in risk_times]
    censor_times = sorted(r["time"] for r in cohort if not r["event"])
    return steps, risk_table, censor_times


def _emc_shaped_cohort() -> list[dict]:
    """59 patients, median not reached, heavy late censoring -- the shape EMC series actually have.

    The numbers are ARBITRARY AND SYNTHETIC. They are not derived from any patient, any series or
    any published figure, and nothing downstream of this control may cite them as data.
    """
    events = [6, 11, 14, 19, 23, 28, 33, 39, 44, 52, 61, 70, 84, 96, 110, 128, 150, 168]
    censored = [3, 5, 8, 9, 12, 15, 17, 18, 21, 25, 27, 30, 34, 36, 40, 43, 47, 50, 55, 58,
                63, 66, 72, 78, 82, 90, 100, 108, 115, 122, 133, 141, 155, 160, 172, 178,
                180, 180, 180, 180, 180]
    return ([{"time": float(t), "event": 1} for t in events]
            + [{"time": float(t), "event": 0} for t in censored])


SCENARIOS = [
    {"name": "clean", "render": {}, "why": "the reading floor: nothing is degraded, so any error "
     "here is the algorithm's own"},
    {"name": "thick_line", "render": {"line_width": 4},
     "why": "a 4-pixel curve: the level is ambiguous by +/- 2 px before anything else happens"},
    {"name": "gridlines", "render": {"gridlines": True},
     "why": "grey gridlines cross the curve everywhere; a darkness rule that catches them reads a "
            "horizontal line at every gridline height"},
    {"name": "censor_ticks", "render": {"censor_ticks": True},
     "why": "censoring marks are drawn ON the curve in the curve's own colour, so they enter the "
            "matcher as legitimate pixels"},
    {"name": "ci_band", "render": {"ci_band": 0.08},
     "why": "a shaded 95% band, which is what the largest reachable EMC series prints"},
    {"name": "second_curve_other_colour", "render": {"second_curve": True},
     "why": "the normal two-arm figure. The colour matcher must take one arm and ignore the other"},
    {"name": "second_curve_same_colour", "render": {"second_curve": True, "second_same_colour": True},
     "why": "⛔ THE CASE THE READER MUST REFUSE: two black curves, distinguishable only by dash "
            "pattern. A number here would be a guess wearing a measurement's clothes"},
    {"name": "resampled_0_6", "degrade": {"resample": 0.6},
     "why": "the figure re-rendered at 60% and blown back up -- what a PDF page raster does"},
    {"name": "resampled_0_6_lenient_matcher", "degrade": {"resample": 0.6},
     "matcher": {"max_luma": 175}, "arm": "diagnostic",
     "why": "the SAME degraded pixels read with a looser darkness threshold. Its job is to say "
            "whether the strict arm's refusal is information loss or matcher tuning -- a refusal "
            "nobody can attribute is not a finding"},
    {"name": "noise_sigma_8", "degrade": {"noise": 8.0},
     "why": "scan/compression noise short of visible artefacting"},
    {"name": "jpeg_q60", "degrade": {"jpeg": 60},
     "why": "lossy compression, which rings hardest exactly at the high-contrast curve edge"},
    {"name": "jpeg_q30_thick", "render": {"line_width": 3}, "degrade": {"jpeg": 30},
     "why": "the worst realistic combination: a heavy line under heavy compression"},
    {"name": "dashed", "render": {"dashed": True},
     "why": "a dashed arm: every gap is a column with no pixel, so the gap guard decides whether "
            "this is readable or refused"},
    {"name": "axis_anchor_off_by_one", "render": {"anchor_error_px": 1},
     "why": "the calibration itself read one pixel wrong -- a SYSTEMATIC shift, which is the error "
            "class no amount of curve-reading skill removes"},
]


def _synthetic_cohort(n: int, event_fraction: float, t_max: float) -> list[dict]:
    """A spread-out synthetic cohort of size n. SYNTHETIC: not a patient, not a series."""
    rng = _Rng(90210 + n)
    rows = []
    n_ev = int(round(n * event_fraction))
    for i in range(n):
        t = round(t_max * (0.03 + 0.94 * ((i * 7919 % n) / max(1, n - 1))), 1)
        rows.append({"time": max(1.0, t), "event": 1 if i < n_ev else 0})
    # ⛔ THE LAST PATIENT IS CENSORED, DELIBERATELY. A curve that reaches S = 0 is drawn ON the
    # x-axis, and a reader that excludes the axis row -- which it must, or the axis itself reads as
    # a curve at S = 0 across the whole width -- cannot see it. That is a real limitation of
    # reading any survival figure and it is recorded in `⛔_not_modelled`; it is not what this
    # table is measuring, so the cohort is built to avoid it.
    rows.sort(key=lambda r: r["time"])
    rows[-1]["event"] = 0
    _ = rng
    return rows


def cohort_size_sensitivity() -> dict:
    """How the headline error scales with n, on an otherwise IDENTICAL clean render.

    ⭐ WHAT THE TABLE MEASURES, AND THE HYPOTHESIS IT REFUTED. The obvious guess is that a maximum
    absolute deviation is worst for a SMALL series, because one step is about 1/n tall. Measured,
    that is wrong: the headline error grows WITH n. The quantity that actually binds is
    `max_survival_drop_within_one_pixel_column` -- when several events fall inside the same pixel
    column, a one-column timing error moves the reading by their SUM, and event density rises with
    n faster than step height falls. The off-step column stays small at every n, which is what
    shows that the headline number is a TIME-axis artefact rather than a survival-axis one.

    ⇒ Consequence for `assess_quality`: its floor is, in the region where a curve is otherwise
    readable, mostly a statement about how densely the events are packed against the figure's pixel
    width -- i.e. about the FIGURE'S RESOLUTION, not about the reader's care. A wider figure at the
    same cohort size scores better with no change to anything else.
    """
    rows = []
    for n, frac in ((20, 0.35), (59, 0.30), (150, 0.30), (270, 0.30)):
        t_max = 180.0
        cohort = _synthetic_cohort(n, frac, t_max)
        km = ipd_mod.kaplan_meier(cohort)
        steps = [(r["time"], r["survival"]) for r in km]
        if not steps:
            continue
        fig = render_km(steps, t_max=t_max)
        read = extract_series(fig.img, fig.calib, dark_matcher(), series_label=f"n{n}")
        # the largest survival drop that lands inside a single pixel column of THIS render
        upt, _ups = fig.calib.units_per_pixel()
        worst_col_drop, prev_t, prev_s, acc = 0.0, None, 1.0, 0.0
        for t, sv in steps:
            if prev_t is not None and (t - prev_t) <= upt:
                acc += prev_s - sv
            else:
                acc = prev_s - sv
            worst_col_drop = max(worst_col_drop, acc)
            prev_t, prev_s = t, sv
        row = {"n_patients": n, "n_events": sum(1 for r in cohort if r["event"]),
               "read_ok": read["ok"], "refusal": read.get("refusal"),
               "one_step_height_at_start": round(1.0 / n, 4),
               "max_survival_drop_within_one_pixel_column": round(worst_col_drop, 4)}
        if read["ok"]:
            row.update(curve_error(read["digitized"], steps, t_max))
        rows.append(row)
    return {
        "_what": "the same reader and the same clean render, at four cohort sizes",
        "⚠_synthetic": "Every cohort here is generated arithmetic. No row is a patient.",
        "rows": rows,
    }


def run_control() -> dict:
    cohort = _emc_shaped_cohort()
    risk_times = [0.0, 24.0, 48.0, 72.0, 96.0, 120.0, 144.0, 168.0]
    true_steps, risk_table, censor_times = _cohort_to_figure_inputs(cohort, risk_times)
    t_max = 180.0
    truth = {
        "n_patients": len(cohort),
        "n_events": sum(1 for r in cohort if r["event"]),
        "n_censored": sum(1 for r in cohort if not r["event"]),
        "median_survival": ipd_mod._median_survival(ipd_mod.kaplan_meier(cohort)),
        "risk_table": risk_table,
        "⚠": "SYNTHETIC. Not a patient, not a series, not a published figure.",
    }
    second = [(t, s * 0.82) for t, s in true_steps]

    # ⭐ THE BASELINE THAT MAKES EVERY OTHER ROW ATTRIBUTABLE. The same cohort's EXACT curve,
    # never rendered and never read, pushed through the same reconstruction with the same risk
    # table. Anything this baseline already loses is the ALGORITHM's or the RISK TABLE's, and
    # subtracting it is the only way a scenario's delta can be called digitization error.
    exact_curve = {"id": "exact_coordinates_baseline", "source_id": "control", "endpoint": "os",
                   "population": "synthetic control cohort", "time_unit": "months",
                   "digitized": [[0.0, 1.0]] + [[t, sv] for t, sv in true_steps],
                   "risk_table": risk_table, "total_events": None,
                   "digitized_by": "no digitization step -- exact coordinates"}
    exact_rec = ipd_mod.reconstruct(exact_curve)
    baseline = {
        "n_events": exact_rec["n_events"], "n_censored": exact_rec["n_censored"],
        "events_delta_vs_truth": exact_rec["n_events"] - truth["n_events"],
        "censored_delta_vs_truth": exact_rec["n_censored"] - truth["n_censored"],
        "internal_max_abs_km_deviation": exact_rec["max_abs_km_deviation"],
        "⭐_what_this_baseline_already_loses": (
            "Censorings that happen AFTER the last numbers-at-risk time are not identifiable from "
            "the published figure at all -- the risk table stops, so the algorithm has nothing to "
            "distribute them against. In this cohort that is every patient censored beyond the "
            "last risk time, and it is a property of what a paper PRINTS, not of any reading."),
    }

    results = []
    jpeg_ran = None
    for sc in SCENARIOS:
        rkw = dict(sc.get("render", {}))
        same_colour = rkw.pop("second_same_colour", False)
        if rkw.pop("censor_ticks", False):
            rkw["censor_times"] = censor_times
        if rkw.pop("second_curve", False):
            rkw["second_curve"] = second
            if same_colour:
                rkw["second_rgb"] = (0, 0, 0)
        fig = render_km(true_steps, t_max=t_max, **rkw)
        img = fig.img
        deg = sc.get("degrade", {})
        skipped = None
        if "resample" in deg:
            img = resample(img, deg["resample"])
        if "noise" in deg:
            img = add_noise(img, deg["noise"])
        if "jpeg" in deg:
            out = jpeg_roundtrip(img, deg["jpeg"])
            jpeg_ran = out is not None if jpeg_ran is None else (jpeg_ran and out is not None)
            if out is None:
                skipped = "Pillow not importable: the JPEG arm did NOT run"
            else:
                img = out

        row = {"scenario": sc["name"], "arm": sc.get("arm", "sweep"), "why": sc["why"],
               "render": {k: (True if k == "second_curve" else v) for k, v in rkw.items()
                          if k != "censor_times"},
               "degrade": deg or None, "skipped": skipped}
        if skipped:
            results.append(row)
            continue

        read = extract_series(img, fig.calib, dark_matcher(**sc.get("matcher", {})),
                              series_label=sc["name"])
        row["read_ok"] = read["ok"]
        row["refusal"] = read.get("refusal")
        row["diagnostics"] = read.get("diagnostics")
        if not read["ok"]:
            row["⭐"] = ("REFUSED, and for this scenario that is the CORRECT outcome"
                         if sc["name"] == "second_curve_same_colour"
                         else "refused: the reader could not support a number here")
            results.append(row)
            continue

        row.update(curve_error(read["digitized"], true_steps, t_max))
        curve = {"id": f"control_{sc['name']}", "source_id": "control", "endpoint": "os",
                 "population": "synthetic control cohort", "time_unit": "months",
                 "digitized": read["digitized"], "risk_table": risk_table,
                 "total_events": None,
                 "digitized_by": "km_digitize.extract_series (control render, no human step)"}
        try:
            rec = ipd_mod.reconstruct(curve)
            q = ipd_mod.assess_quality(curve, rec)
            row["reconstruction"] = {
                "n_reconstructed": rec["n_reconstructed"],
                "n_events": rec["n_events"], "n_censored": rec["n_censored"],
                "events_delta_vs_truth": rec["n_events"] - truth["n_events"],
                "censored_delta_vs_truth": rec["n_censored"] - truth["n_censored"],
                "events_delta_vs_exact_baseline": rec["n_events"] - baseline["n_events"],
                "censored_delta_vs_exact_baseline": rec["n_censored"] - baseline["n_censored"],
                "median_survival": ipd_mod._median_survival(ipd_mod.kaplan_meier(rec["ipd"])),
                "median_delta_vs_truth": None,
                "internal_max_abs_km_deviation": rec["max_abs_km_deviation"],
                "admissible_under_the_floor": q["admissible"],
                "quality_failures": q["failures"],
            }
            med = row["reconstruction"]["median_survival"]
            if med is not None and truth["median_survival"] is not None:
                row["reconstruction"]["median_delta_vs_truth"] = round(
                    med - truth["median_survival"], 3)
        except Exception as exc:  # noqa: BLE001
            row["reconstruction"] = {"error": f"{type(exc).__name__}: {exc}"}
        results.append(row)

    graded = [r for r in results if r.get("read_ok") and r.get("arm") != "diagnostic"]
    worst = max((r["max_abs_curve_error"] for r in graded), default=None)
    return {
        "truth": truth,
        "cohort_size_sensitivity": cohort_size_sensitivity(),
        "exact_coordinates_baseline": baseline,
        "scenarios": results,
        "jpeg_arm_ran": bool(jpeg_ran),
        "summary": {
            "scenarios_total": len(SCENARIOS),
            "scenarios_read": len(graded),
            "scenarios_refused": sum(1 for r in results if r.get("read_ok") is False),
            "scenarios_skipped": sum(1 for r in results if r.get("skipped")),
            "worst_max_abs_curve_error": worst,
            "worst_max_abs_curve_error_off_step": max(
                (r["max_abs_curve_error_off_step"] for r in graded
                 if r.get("max_abs_curve_error_off_step") is not None), default=None),
            "worst_censored_delta_vs_exact_baseline": max(
                (abs(r["reconstruction"]["censored_delta_vs_exact_baseline"]) for r in graded
                 if "censored_delta_vs_exact_baseline" in r.get("reconstruction", {})),
                default=None),
            "floor_max_abs_km_deviation": FLOOR_MAX_ABS_KM_DEVIATION,
            "worst_events_delta": max(
                (abs(r["reconstruction"]["events_delta_vs_truth"]) for r in graded
                 if "events_delta_vs_truth" in r.get("reconstruction", {})), default=None),
        },
    }


def build() -> dict:
    control = run_control()
    return {
        "_what": "A DIGITIZATION-ERROR bound for reading a Kaplan-Meier curve off a raster figure, "
                 "measured against cohorts whose patient-level data is known exactly.",
        "_why": "emc_ipd_survival.py's known-answer control is fed exact coordinates, so it bounds "
                "ALGORITHMIC error and is structurally incapable of failing on a mis-read pixel. "
                "Until this artifact existed, digitization error in this program was bounded by "
                "nothing.",
        "_not_medical_advice": "Nothing here is medical advice, and nothing here asserts efficacy, "
                               "safety or clinical readiness. Every cohort below is synthetic.",
        "⛔_direction_of_the_bound": (
            "A SYNTHETIC RENDER IS EASIER THAN A JOURNAL FIGURE. This control can REFUTE the "
            "reader and cannot certify it: an error measured here is a LOWER bound on the error "
            "of reading a real published curve. What it does establish exactly is that the "
            "pixel-to-data pipeline is sound under the degradations that ARE modelled, and which "
            "of them the reader refuses rather than guesses at."),
        "⛔_not_modelled": [
            "a curve drawn over a photographic or textured background",
            "a legend, annotation or p-value box drawn ON TOP of the curve",
            "an axis anchor grossly misidentified (the +/-1 px case IS modelled)",
            "a figure whose axis is non-linear or whose time origin is not zero",
            "a curve that REACHES S = 0: its final segment is drawn on the x-axis, and a reader "
            "that excludes the axis row -- which it must, or the axis reads as a curve at S = 0 "
            "across the full width -- cannot see it. Read that tail by hand.",
        ],
        "method_ref": ipd_mod.METHOD_REF,
        "control": control,
    }


def check() -> int:
    """Recompute and compare against the committed artifact."""
    if not os.path.exists(OUT):
        print(f"MISSING {OUT}", file=sys.stderr)
        return 1
    with open(OUT, encoding="utf-8") as fh:
        on_disk = json.load(fh)
    fresh = build()
    if on_disk.get("control", {}).get("summary") != fresh["control"]["summary"]:
        print("MISMATCH: committed control summary differs from a fresh run", file=sys.stderr)
        print(json.dumps(on_disk.get("control", {}).get("summary"), indent=2), file=sys.stderr)
        print(json.dumps(fresh["control"]["summary"], indent=2), file=sys.stderr)
        return 1
    print("km_digitize --check OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--control", action="store_true",
                    help="run the degradation sweep and write the artifact")
    ap.add_argument("--check", action="store_true",
                    help="verify the committed artifact against a fresh run")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    art = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(art, fh, indent=2, ensure_ascii=False)
    s = art["control"]["summary"]
    print(json.dumps(s, indent=2))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
