#!/usr/bin/env python3
"""Does a published Kaplan-Meier figure PRINT a numbers-at-risk row? Measured, not eyeballed.

WHY THIS EXISTS
---------------
`systems/POLICY-evidence.md` §2.7(a) makes one condition mandatory before a curve may be
reconstructed at all: *"A numbers-at-risk table is mandatory. Without one the per-interval censored
count is unidentifiable and the reconstruction is assumption rather than inversion. A curve without
a risk table is REFUSED, not admitted with a caveat -- a caveat travels badly and a refusal is
checkable."*

⛔ THE REFUSAL WAS NOT CHECKABLE. Every admissibility verdict this program holds was reached by an
agent LOOKING at a rasterised page and writing `numbers_at_risk_row: false` into a JSON field. That
is a real observation and it is the right kind of observation, but it is unre-runnable and
unfalsifiable: nothing in the repository can disagree with it, and the field is
indistinguishable from one somebody defaulted. CLAUDE.md §4 names exactly this -- a populated field
is not a measured one. The two largest reachable series in this disease are refused on the strength
of that field, so the field is load-bearing.

⛔ AND THE OBVIOUS INSTRUMENT IS STRUCTURALLY BLIND. `emc-ipd-admissibility-2026-08-12.json` searched
the full text of five papers for "at risk" and found zero, then said so in its own headline: in JATS
XML and in most journal PDFs the at-risk row is drawn INSIDE the figure image, where no text search
can see it. Measured again here and it is worse than that -- of the nine Kaplan-Meier figures in the
five reachable EMC papers, EIGHT are raster images with no text layer at all (four of them in an
encoding this reader has to decline outright) and one is vector text. A single-arm detector is wrong
for this corpus whichever arm it picks.

WHAT IS MEASURED
----------------
A numbers-at-risk row has a STRUCTURE that survives having no readable glyphs: it is a horizontal
band of narrow, well-separated marks BELOW the axis, positioned at the same x coordinates as the
axis tick labels, one mark per tick. An axis title is a band too, and it is what the rule has to
discriminate against -- so a band qualifies only when its marks are (a) at least `MIN_MATCHED_TICKS`
aligned with the tick-label band's marks, and (b) narrow, a digit rather than a word.

  TEXT arm  -- the figure is vector and its numbers are real text. Tokens and their boxes come from
               the PDF text layer, so the rule runs on tokens whose VALUES are also readable, and a
               detected row is reported with the risk table it carries.
  PIXEL arm -- the figure is an embedded raster. Tokens are ink clusters recovered from the pixels;
               their positions are readable and their values are NOT. A detected row is reported as
               a row of unknown values, which is enough for the admissibility question and is not
               enough to reconstruct anything: the values are then read by eye through
               `km_digitize.py`, which is where digitization provenance is recorded.

⛔ WHAT A `present` VERDICT DOES NOT MEAN. It means a risk row is printed, which is §2.7(a)'s
condition and only that condition. It says nothing about how many timepoints it carries, whether
they are legible, whether the curve is an EMC cohort, or whether §2.1/§2.3 would let the series be
pooled with any other.

⛔ AND A `absent` VERDICT IS ABOUT THE FIGURE IMAGE THIS RAN ON. A paper can print its risk table in
a separate table, in a supplement, or in prose; this detector reads figures. Where the paper's own
text carries the numbers, that is a different and better route than reading pixels, and it is not
this instrument's job to find it.

THE CONTROL
-----------
`--check` renders synthetic figures with and without a risk row and asserts the detector separates
them, including the two mutations that would make a structural rule useless: a band of marks that is
NOT tick-aligned must not fire (that is an axis title), and a tick-aligned band of WIDE marks must
not fire (that is a row of words). The real-figure runs are recorded in `km-risk-row-detection.json`
with the sha256 of every PDF read, so a later session can re-derive them; the figures themselves are
not committed, because their licences do not permit it.

Usage:
    python3 research/modalities/km_risk_row_detect.py --pdf-dir <dir>   # measure real figures
    python3 research/modalities/km_risk_row_detect.py --check          # synthetic controls only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from km_digitize import Image, read_png, write_png  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "km-risk-row-detection.json")

# ── the rule's constants, all in FRACTIONS OF THE FIGURE WIDTH so they do not depend on dpi ──
INK_LUMA_MAX = 170          # a pixel this dark or darker is ink -- a glyph is drawn in black
# ⛔ AN AXIS IS NOT ALWAYS BLACK, AND ONE THRESHOLD FOR BOTH JOBS SILENTLY LOSES FIGURES. Measured
# 2026-08-27: masunaga2025 draws its x axis as a light grey rule whose darkest pixels sit between
# luma 200 and 230, so at the glyph threshold its three Kaplan-Meier figures had NO axis at all and
# dropped out of the corpus unmeasured -- the worst failure available here, because a figure that
# never reaches the rule reads afterwards as a figure nobody had to refuse.
RULE_LUMA_MAX = 235         # ...but a RULE may be grey; this threshold finds the axis only
AXIS_MIN_SPAN = 0.45        # a horizontal rule spanning this much of the figure is an axis
CLUSTER_GAP = 0.012         # blank columns wider than this split one mark from the next
BAND_GAP = 3                # blank rows this many or more end a band
MIN_MARKS = 3               # a risk row carries at least this many numbers
MIN_MATCHED_TICKS = 3       # ...and at least this many of them sit under a tick label
TICK_TOL = 0.020            # "under a tick label" means within this fraction of the width
MAX_MARK_WIDTH = 0.055      # a number is narrower than this; a word is not
MIN_GLYPH_WIDTH = 0.004     # ...and wider than this; below it, the mark is a drawn tick
# ⛔ AND THE TICK LABELS MUST SIT JUST UNDER THE AXIS. Measured 2026-08-27: in a SWIMMER PLOT every
# bar is a long horizontal run, so the bottom-most long run is a bar rather than an axis, and the
# real tick labels turned up eleven bands lower -- where they aligned with the bar ends and were
# read as a numbers-at-risk row. A figure whose tick labels are nowhere near the candidate axis has
# not been understood, and the honest verdict is `undetermined`.
MAX_TICK_GAP = 0.10         # tick labels within this fraction of the figure HEIGHT below the axis
# ⛔ AND THE RISK ROW SITS JUST UNDER THE TICK LABELS, not anywhere below them. Measured 2026-08-27
# on martinbroto2020's swimmer plot: with a bar mistaken for the axis, the real tick labels lay 62%
# of the figure height further down and aligned with the bar ends, which the rule read as a risk
# row. A row printed most of a figure away from the axis it annotates is not annotating that axis.
MAX_RISK_GAP = 0.25         # ...and the risk row within this fraction of the height below THEM
LABEL_RE = re.compile(r"(number|no\.?|patients?|subjects?|n)\s*(of\s+)?(patient\s+)?at\s+risk", re.I)


# ---------------------------------------------------------------------------
# tokens -- the one shape both arms produce
# ---------------------------------------------------------------------------
class Token:
    """One readable mark: its box in figure coordinates, and its text where an arm knows it.

    x0/x1 and y0/y1 are in PIXELS with y growing DOWNWARD, matching `km_digitize.Image`. The text
    arm's PDF coordinates grow upward and are flipped on the way in, so the structural rule is
    written once.
    """

    __slots__ = ("x0", "y0", "x1", "y1", "text")

    def __init__(self, x0: float, y0: float, x1: float, y1: float, text: str | None = None):
        self.x0, self.y0, self.x1, self.y1, self.text = x0, y0, x1, y1, text

    @property
    def cx(self) -> float:
        return 0.5 * (self.x0 + self.x1)

    @property
    def cy(self) -> float:
        return 0.5 * (self.y0 + self.y1)

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    def as_dict(self) -> dict:
        d = {"cx": round(self.cx, 1), "cy": round(self.cy, 1), "w": round(self.width, 1)}
        if self.text is not None:
            d["text"] = self.text
        return d


def _bands(tokens: list[Token], tol: float) -> list[list[Token]]:
    """Group tokens into horizontal rows: same band iff their vertical centres agree within `tol`."""
    out: list[list[Token]] = []
    for tok in sorted(tokens, key=lambda t: t.cy):
        if out and abs(tok.cy - out[-1][-1].cy) <= tol:
            out[-1].append(tok)
        else:
            out.append([tok])
    return [sorted(b, key=lambda t: t.cx) for b in out]


def decide(tokens: list[Token], width: float, page_text: str = "",
           axis_y: float | None = None, max_tick_gap: float | None = None,
           max_risk_gap: float | None = None) -> dict:
    """The rule, run on tokens from either arm.

    The tick-label band is the first band below the axis that is made of glyphs rather than of drawn
    tick marks, and it is found by position and width rather than by reading it, so the rule is
    identical in both arms. Every band BELOW it is then tested for tick alignment and mark
    narrowness; a band at or above it can never be a risk row.
    """
    result = {
        "n_tokens": len(tokens),
        "bands": [],
        "label_phrase_found": bool(LABEL_RE.search(page_text)) if page_text else False,
        "verdict": "absent",
        "matched_ticks": 0,
        "risk_row_band_index": None,
    }
    if len(tokens) < MIN_MARKS:
        result["verdict"] = "undetermined"
        result["⚠"] = ("fewer marks below the axis than a tick-label row would carry: this figure's "
                       "axis region was not recovered, so the question is unanswered rather than "
                       "answered no")
        return result
    bands = _bands(tokens, tol=max(3.0, 0.008 * width))
    # ⛔ THE TICK-LABEL BAND IS NOT ALWAYS THE FIRST ONE, AND ASSUMING IT WAS PRODUCED A FALSE
    # POSITIVE ON A REAL PAPER. Measured 2026-08-27: masunaga2025 Fig. 3 draws TICK MARKS below its
    # axis, so band 0 held three zero-width marks, band 1 held the tick labels -- and the labels,
    # being narrow and sitting exactly under the ticks, satisfied every clause of the rule. The
    # reference band is therefore the first band that is made of GLYPHS: at least MIN_MARKS of them
    # and wider than a drawn tick.
    ref = next((i for i, b in enumerate(bands)
                if len(b) >= MIN_MARKS
                and sorted(t.width for t in b)[len(b) // 2] >= MIN_GLYPH_WIDTH * width), None)
    if ref is None:
        result["verdict"] = "undetermined"
        result["⚠"] = ("no glyph-shaped band below the axis: the tick labels were not recovered, so "
                       "there is nothing to measure alignment against")
        return result
    if (axis_y is not None and max_tick_gap is not None
            and min(t.y0 for t in bands[ref]) - axis_y > max_tick_gap):
        result["verdict"] = "undetermined"
        result["⚠"] = ("the first glyph band sits far below the candidate axis, so that rule is "
                       "probably not an axis: in a bar chart the bottom-most long horizontal run is "
                       "a BAR. This figure was not understood and is not reported as a negative")
        result["tick_gap_px"] = round(min(t.y0 for t in bands[ref]) - axis_y, 1)
        return result
    result["tick_label_band_index"] = ref
    tick_x = [t.cx for t in bands[ref]]
    for i, band in enumerate(bands):
        matched = sum(1 for t in band
                      if any(abs(t.cx - tx) <= TICK_TOL * width for tx in tick_x))
        widths = sorted(t.width for t in band)
        med_w = widths[len(widths) // 2]
        rec = {"index": i, "n_marks": len(band), "matched_ticks": matched,
               "median_mark_width_frac": round(med_w / width, 4),
               "role": ("tick_labels" if i == ref else
                        "above_tick_labels" if i < ref else "candidate"),
               "marks": [t.as_dict() for t in band][:16]}
        result["bands"].append(rec)
        if i <= ref:
            continue
        near_enough = (max_risk_gap is None
                       or min(t.y0 for t in band) - max(t.y1 for t in bands[ref]) <= max_risk_gap)
        rec["near_enough_to_tick_labels"] = near_enough
        if (len(band) >= MIN_MARKS and matched >= MIN_MATCHED_TICKS
                and med_w <= MAX_MARK_WIDTH * width and near_enough):
            if result["risk_row_band_index"] is None:
                result["verdict"] = "present"
                result["risk_row_band_index"] = i
                result["matched_ticks"] = matched
                if all(t.text is not None for t in band):
                    result["risk_row_text"] = [t.text for t in band]
    if result["verdict"] == "absent" and result["label_phrase_found"]:
        # ⚠ The label is drawn and no aligned band was recovered. That is a CONFLICT, not a no:
        # the row is printed somewhere this arm could not group. Never resolve it silently.
        result["verdict"] = "undetermined"
        result["⚠"] = ("the page prints an at-risk LABEL but no tick-aligned band was recovered; "
                       "the structural arm and the label disagree and a human must look")
    return result


# ---------------------------------------------------------------------------
# PIXEL arm
# ---------------------------------------------------------------------------
def _luma(px) -> float:
    r, g, b = px
    return 0.299 * r + 0.587 * g + 0.114 * b


def _is_ink(px) -> bool:
    return _luma(px) <= INK_LUMA_MAX


def _is_rule(px) -> bool:
    return _luma(px) <= RULE_LUMA_MAX


def find_axis_row(img: Image) -> tuple[int, int, int] | None:
    """The BOTTOM-MOST long horizontal RULE, and the x range it spans: a plot's x axis.

    ⚠ Taken from the bottom rather than the top because a boxed plot frame has two long rules and
    only the lower one has an at-risk row beneath it.
    ⚠ And measured as the longest CONTIGUOUS run of ink in the row, never as the row's ink COUNT:
    a row crossing a dashed curve, a legend and a shaded interval can hold as many ink pixels as an
    axis while being nothing like a line.
    """
    need = int(AXIS_MIN_SPAN * img.width)
    for y in range(img.height - 1, -1, -1):
        row = img.px[y]
        best = run = 0
        start = best_start = 0
        for x in range(img.width):
            if _is_rule(row[x]):
                if run == 0:
                    start = x
                run += 1
                if run > best:
                    best, best_start = run, start
            else:
                run = 0
        if best >= need:
            return y, best_start, best_start + best - 1
    return None


def pixel_tokens(img: Image, axis_y: int, x0: int = 0, x1: int | None = None) -> list[Token]:
    """Ink clusters below the axis, recovered as boxes with no glyph recognition of any kind.

    ⛔ RESTRICTED TO THE AXIS'S OWN x RANGE (with a small margin), because a figure raster usually
    carries a legend or a second panel beside the plot and ink from those is not part of any band
    beneath this axis.
    """
    x1 = img.width - 1 if x1 is None else x1
    span = max(1, x1 - x0)
    lo = max(0, int(x0 - 0.06 * span))
    hi = min(img.width - 1, int(x1 + 0.06 * span))
    top = min(img.height - 1, axis_y + max(2, img.height // 200))
    rows = []
    for y in range(top, img.height):
        xs = [x for x in range(lo, hi + 1) if _is_ink(img.px[y][x])]
        rows.append((y, xs))
    tokens: list[Token] = []
    band: list[tuple[int, list[int]]] = []
    blank = 0
    for y, xs in rows + [(img.height, [])]:
        if xs:
            band.append((y, xs))
            blank = 0
        else:
            blank += 1
            if band and blank >= BAND_GAP:
                tokens.extend(_clusters(band, span))
                band = []
    if band:
        tokens.extend(_clusters(band, span))
    return tokens


def _clusters(band: list[tuple[int, list[int]]], width: int) -> list[Token]:
    ys = [y for y, _ in band]
    cols = sorted({x for _, xs in band for x in xs})
    if not cols:
        return []
    gap = max(2, int(CLUSTER_GAP * width))
    out: list[Token] = []
    start = prev = cols[0]
    for x in cols[1:] + [cols[-1] + gap + 1]:
        if x - prev > gap:
            out.append(Token(start, min(ys), prev, max(ys)))
            start = x
        prev = x
    return out


# ---------------------------------------------------------------------------
# TEXT arm
# ---------------------------------------------------------------------------
def _numeric(text: str) -> float | None:
    t = (text or "").strip().replace(",", "")
    try:
        return float(t)
    except ValueError:
        return None


def looks_like_an_x_axis(band: list[Token], min_span: float) -> bool:
    """Is this band of tokens the tick-label row of a time axis?

    ⛔ A LONG HORIZONTAL RULE IS NOT AN AXIS -- A TABLE DRAWS THOSE, and anchoring on one turned a
    table footnote into a numbers-at-risk row on this very corpus (measured 2026-08-27). The
    signature used instead is what an axis actually is: at least MIN_MARKS numbers, strictly
    increasing left to right, roughly evenly spaced, and spanning at least `min_span`.
    """
    vals = [_numeric(t.text) for t in band]
    if len(vals) < MIN_MARKS or any(v is None for v in vals):
        return False
    if any(b <= a for a, b in zip(vals, vals[1:])):
        return False
    gaps = [b.cx - a.cx for a, b in zip(band, band[1:])]
    if not gaps or min(gaps) <= 0:
        return False
    mean = sum(gaps) / len(gaps)
    spread = max(abs(g - mean) for g in gaps) / mean
    span = band[-1].cx - band[0].cx
    return spread <= 0.35 and span >= min_span


def page_tokens(page) -> list[Token]:
    """Every word on the page as a box, flipped so y grows DOWNWARD like the pixel arm's."""
    from pdfminer.layout import LTTextLine  # noqa: PLC0415

    height = page.bbox[3]
    toks: list[Token] = []

    def walk(obj):
        for el in obj:
            if isinstance(el, LTTextLine):
                toks.extend(_split_line(el))
            elif hasattr(el, "__iter__"):
                walk(el)

    walk(page)
    return [Token(t.x0, height - t.y1, t.x1, height - t.y0, t.text) for t in toks]


def text_axis_band(page) -> list[Token] | None:
    """The tick-label row of a vector plot, found by its own signature rather than by a drawn line.

    ⛔ THREE ANCHORS WERE TRIED HERE AND THE FIRST TWO WERE WRONG, both in the direction that
    invents readings. (1) No anchor at all: every paragraph became a band, and the rule reported a
    numbers-at-risk row on 26 of 29 figures -- title pages and reference lists included. (2) The
    longest horizontal RULE on the page: a table draws those too, and a table footnote was read as a
    risk row. (3) This one -- the tick row itself, identified by `looks_like_an_x_axis`. It needs no
    drawn line, which matters because morioka2016's Kaplan-Meier axis is reported as a line by no
    PDF layout reader tried here, and anchoring on the one line that IS reported placed the y-axis
    labels BELOW the anchor and lost the figure.

    Ambiguity is resolved by taking the LARGEST such row on the page, never the first one found.
    """
    toks = page_tokens(page)
    if len(toks) < MIN_MARKS:
        return None
    best = None
    for band in _bands(toks, tol=3.0):
        short = [t for t in band if len(t.text or "") <= 4]
        if len(short) < MIN_MARKS:
            continue
        if not looks_like_an_x_axis(short, 0.20 * page.bbox[2]):
            continue
        if best is None or len(short) > len(best):
            best = short
    return best


def _split_line(line) -> list[Token]:
    """One token per whitespace-separated run of characters, with a real box around it."""
    from pdfminer.layout import LTChar  # noqa: PLC0415

    out: list[Token] = []
    cur: list = []
    for ch in line:
        if isinstance(ch, LTChar) and ch.get_text().strip():
            cur.append(ch)
        elif cur:
            out.append(_token_from_chars(cur))
            cur = []
    if cur:
        out.append(_token_from_chars(cur))
    return out


def _token_from_chars(chars) -> Token:
    x0 = min(c.x0 for c in chars)
    x1 = max(c.x1 for c in chars)
    y0 = min(c.y0 for c in chars)
    y1 = max(c.y1 for c in chars)
    return Token(x0, y0, x1, y1, "".join(c.get_text() for c in chars))


# ---------------------------------------------------------------------------
# synthetic controls -- the only figures this file can carry in a bare checkout
# ---------------------------------------------------------------------------
def _draw_block(img: Image, x0: int, y0: int, x1: int, y1: int, rgb=(0, 0, 0)) -> None:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= y < img.height and 0 <= x < img.width:
                img.px[y][x] = rgb


def synthetic_figure(*, risk_row: bool, aligned: bool = True, narrow: bool = True,
                     tick_marks: bool = False, label_drop: int = 0,
                     risk_drop: int = 0) -> Image:
    """A Kaplan-Meier-shaped figure: a plot frame, an axis, tick labels, a title, and optionally a
    row of marks beneath them.

    ⛔ THE MARKS ARE BLOCKS, NOT GLYPHS, and that is the honest scope of this control: it exercises
    the STRUCTURAL rule -- band segmentation, tick alignment, mark width -- which is the whole of
    what the pixel arm decides on. It does not and cannot exercise glyph reading, because the pixel
    arm does not read glyphs.
    """
    w, h = 900, 700 + risk_drop + label_drop
    img = Image.blank(w, h)
    axis_y = 500
    _draw_block(img, 100, axis_y, 860, axis_y + 3)                 # the x axis
    _draw_block(img, 100, 40, 103, axis_y)                         # the y axis
    for i in range(6):                                             # a descending step curve
        x = 100 + i * 120
        _draw_block(img, x, 60 + i * 60, x + 120, 63 + i * 60, (30, 30, 160))
    ticks = [100, 252, 404, 556, 708, 860]
    if tick_marks:                                                 # drawn ticks below the axis
        for tx in ticks:
            _draw_block(img, tx - 1, axis_y + 4, tx + 1, axis_y + 14)
    for tx in ticks:                                               # tick labels
        _draw_block(img, tx - 8, axis_y + 20 + label_drop, tx + 8, axis_y + 44 + label_drop)
    _draw_block(img, 380, axis_y + 70, 560, axis_y + 92)           # a wide axis title
    if risk_row:
        # ⚠ The WIDE case draws three marks rather than six, because six marks 70 px wide span
        # nearly the whole width and the axis finder then reads the row itself as a second axis.
        # A row of words under an axis looks like this: few of them, and each one wide.
        marks = ticks if narrow else ticks[1:4]
        for tx in marks:
            cx = tx if aligned else tx + 60
            half = 8 if narrow else 35
            top = axis_y + 120 + risk_drop
            _draw_block(img, cx - half, top, cx + half, top + 24)
    return img


def run_control() -> dict:
    """Four synthetic figures, and the detector must separate them the same way every time."""
    cases = [
        ("plain_no_risk_row", {"risk_row": False}, "absent"),
        ("risk_row_present", {"risk_row": True}, "present"),
        ("misaligned_band", {"risk_row": True, "aligned": False}, "absent"),
        ("wide_marks_band", {"risk_row": True, "narrow": False}, "absent"),
        # ⛔ THE REGRESSION THIS CONTROL EXISTS FOR IS A REAL ONE, CAUGHT ON A REAL PAPER: with
        # ticks drawn below the axis, an earlier version of the rule read the TICK LABELS as the
        # risk row and reported a numbers-at-risk table on masunaga2025 Fig. 3, which has none.
        ("tick_marks_no_risk_row", {"risk_row": False, "tick_marks": True}, "absent"),
        ("tick_marks_with_risk_row", {"risk_row": True, "tick_marks": True}, "present"),
        # ⛔ the swimmer-plot failure: what was taken for an axis has its tick labels nowhere near it
        ("tick_labels_far_below", {"risk_row": False, "label_drop": 120}, "undetermined"),
        # ⛔ the second half of the swimmer-plot failure: an aligned narrow band far below the ticks
        ("aligned_band_far_below", {"risk_row": True, "risk_drop": 260}, "absent"),
    ]
    out = {
        "_what": "Synthetic figures with a known answer, so the rule is shown to separate a risk "
                 "row from the two things that would otherwise be mistaken for one.",
        "⛔_scope": "Blocks, not glyphs: this bounds the STRUCTURAL rule and nothing else. It is "
                    "structurally incapable of failing on a real figure that is hard to read, "
                    "which is the same limit POLICY-evidence.md §2.7 records for the "
                    "reconstruction's own known-answer control.",
        "cases": [],
        "passed": True,
    }
    for name, kwargs, expect in cases:
        img = synthetic_figure(**kwargs)
        axis = find_axis_row(img)
        if axis is None:
            toks, scale, axis_y = [], img.width, None
        else:
            axis_y, ax0, ax1 = axis
            toks, scale = pixel_tokens(img, axis_y, ax0, ax1), max(1, ax1 - ax0)
        res = decide(toks, scale, axis_y=axis_y if axis is not None else None,
                     max_tick_gap=MAX_TICK_GAP * img.height,
                     max_risk_gap=MAX_RISK_GAP * img.height)
        ok = res["verdict"] == expect
        out["cases"].append({"case": name, "expected": expect, "got": res["verdict"],
                             "axis_row": axis_y, "n_bands": len(res["bands"]),
                             "matched_ticks": res["matched_ticks"], "passed": ok})
        out["passed"] = out["passed"] and ok
    return out


# ---------------------------------------------------------------------------
# reading real papers
# ---------------------------------------------------------------------------
def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def images_and_text(pdf_path: str):
    """Every embedded raster, plus each page's text tokens and text.

    ⛔ EMBEDDED, NOT RE-RENDERED. A page raster made by poppler at 200 dpi is a resampled copy of
    an image the publisher already stored; taking the stored image gives the digitizer the pixels
    the journal shipped, which is the best input that exists at $0.
    """
    from pdfminer.high_level import extract_pages  # noqa: PLC0415
    from pdfminer.layout import LTFigure, LTImage, LAParams  # noqa: PLC0415

    for pno, page in enumerate(extract_pages(pdf_path, laparams=LAParams()), 1):
        imgs = []

        declined = []

        def walk(obj):
            for el in obj:
                if isinstance(el, LTImage):
                    img = _image_to_raster(el)
                    if img is not None:
                        imgs.append((img, el.srcsize, [round(v, 1) for v in el.bbox]))
                    else:
                        declined.append({
                            "srcsize": list(el.srcsize),
                            "bbox": [round(v, 1) for v in el.bbox],
                            "filters": [f[0].name for f in (el.stream.get_filters() or [])],
                            "bits": el.stream.get_any(("BPC", "BitsPerComponent"))})
                elif isinstance(el, LTFigure):
                    walk(el)

        walk(page)
        yield pno, page, imgs, declined


def _image_to_raster(el) -> Image | None:
    """Decode an embedded image into 8-bit RGB, or decline.

    Handles the three encodings this corpus actually uses -- Flate RGB, Flate grayscale and Flate
    CMYK. A JPEG (DCTDecode) is DECLINED rather than half-decoded: saying so is a finding about the
    figure, and a wrong decode would be a measurement of noise.
    """
    try:
        w, h = el.srcsize
        stream = el.stream
        filters = [f[0].name for f in (stream.get_filters() or [])]
        if any(f in ("DCTDecode", "JPXDecode", "CCITTFaxDecode") for f in filters):
            return None
        bits = stream.get_any(("BPC", "BitsPerComponent"))
        if bits != 8:
            return None
        data = stream.get_data()
    except Exception:  # noqa: BLE001 -- an undecodable image is a finding, never a crash
        return None
    n = w * h
    px: list[list[tuple[int, int, int]]] = []
    if len(data) == n * 3:
        for y in range(h):
            row = data[y * w * 3:(y + 1) * w * 3]
            px.append([(row[3 * x], row[3 * x + 1], row[3 * x + 2]) for x in range(w)])
    elif len(data) == n:
        for y in range(h):
            row = data[y * w:(y + 1) * w]
            px.append([(row[x], row[x], row[x]) for x in range(w)])
    elif len(data) == n * 4:
        for y in range(h):
            row = data[y * w * 4:(y + 1) * w * 4]
            out = []
            for x in range(w):
                c, m, yy, k = row[4 * x:4 * x + 4]
                out.append((((255 - c) * (255 - k)) // 255, ((255 - m) * (255 - k)) // 255,
                            ((255 - yy) * (255 - k)) // 255))
            px.append(out)
    else:
        return None
    return Image(w, h, px)


KM_CAPTION_RE = re.compile(r"(kaplan|survival|progression[- ]free|recurrence[- ]free)", re.I)


def crop_from_page_raster(page_png: str, page_bbox, img_bbox) -> Image | None:
    """Cut one figure out of a rendered PAGE, for a figure this file's decoder cannot open.

    ⭐ THE FALLBACK EXISTS BECAUSE THE ALTERNATIVE IS AN UNMEASURED FIGURE. chiusole2020 stores its
    four survival curves as JPEG, which a pure-stdlib reader cannot decode, so the second-largest
    reachable EMC series would otherwise sit at `undetermined` while its page rasters -- already
    published to the literature cache by the retrieval workflow -- carry the same figures.
    ⚠ A PAGE RASTER IS A RESAMPLED COPY, so this is the WEAKER input: the crop is whatever dpi the
    render used, and a risk row printed in small type is closer to the resolution floor here than in
    the publisher's own image. It is recorded per figure as `source: page_raster`.
    """
    img = read_png(page_png)
    scale = img.width / float(page_bbox[2])
    x0 = max(0, int(img_bbox[0] * scale))
    x1 = min(img.width - 1, int(img_bbox[2] * scale))
    top = max(0, int((page_bbox[3] - img_bbox[3]) * scale))
    bot = min(img.height - 1, int((page_bbox[3] - img_bbox[1]) * scale))
    if x1 - x0 < 50 or bot - top < 50:
        return None
    return Image(x1 - x0 + 1, bot - top + 1,
                 [row[x0:x1 + 1] for row in img.px[top:bot + 1]])


def read_pdf(source_id: str, pdf_path: str, dump_dir: str | None = None,
             page_png_dir: str | None = None) -> dict:
    """Every plot-shaped figure in one paper, with a verdict and the measurement behind it."""
    rec = {"source_id": source_id, "pdf": os.path.basename(pdf_path),
           "pdf_sha256": sha256(pdf_path), "pdf_bytes": os.path.getsize(pdf_path),
           "figures": []}
    for pno, page, imgs, declined in images_and_text(pdf_path):
        page_text = " ".join(_page_text(page))
        km_page = bool(KM_CAPTION_RE.search(page_text))
        for idx, (img, srcsize, ibox) in enumerate(imgs, 1):
            axis = find_axis_row(img)
            if axis is None:
                continue
            axis_y, ax0, ax1 = axis
            toks = pixel_tokens(img, axis_y, ax0, ax1)
            res = decide(toks, max(1, ax1 - ax0), axis_y=axis_y,
                         max_tick_gap=MAX_TICK_GAP * img.height,
                         max_risk_gap=MAX_RISK_GAP * img.height)
            if not _looks_like_a_plot(res):
                continue
            entry = {"page": pno, "image_index": idx, "arm": "pixel",
                     "image_px": list(srcsize), "axis_row_px": axis_y,
                     "axis_span_px": [ax0, ax1],
                     "caption_head": _caption_for(page, ibox, page_text), **res}
            if dump_dir:
                name = f"{source_id}_p{pno}_i{idx}.png"
                write_png(os.path.join(dump_dir, name), img)
                entry["dumped"] = name
            rec["figures"].append(entry)
        for d in declined:
            crop = None
            if page_png_dir:
                png = _page_png(page_png_dir, source_id, pno)
                if png:
                    try:
                        crop = crop_from_page_raster(png, page.bbox, d["bbox"])
                    except Exception as exc:  # noqa: BLE001
                        d["crop_error"] = f"{type(exc).__name__}: {exc}"
            if crop is not None:
                axis = find_axis_row(crop)
                if axis is not None:
                    axis_y, ax0, ax1 = axis
                    toks = pixel_tokens(crop, axis_y, ax0, ax1)
                    res = decide(toks, max(1, ax1 - ax0), axis_y=axis_y,
                                 max_tick_gap=MAX_TICK_GAP * crop.height,
                                 max_risk_gap=MAX_RISK_GAP * crop.height)
                    if _looks_like_a_plot(res) or res["verdict"] == "undetermined":
                        entry = {"page": pno, "image_index": None, "arm": "pixel",
                                 "source": "page_raster", "page_png": os.path.basename(png),
                                 "image_px": [crop.width, crop.height], "axis_row_px": axis_y,
                                 "axis_span_px": [ax0, ax1],
                                 "encoding": d["filters"],
                                 "caption_head": _caption_for(page, d["bbox"], page_text), **res}
                        if dump_dir:
                            name = f"{source_id}_p{pno}_crop{len(rec['figures'])}.png"
                            write_png(os.path.join(dump_dir, name), crop)
                            entry["dumped"] = name
                        rec["figures"].append(entry)
                        continue
            # ⛔ AN IMAGE THIS DECODER CANNOT READ IS `undetermined`, NEVER `absent`. chiusole2020
            # stores its four survival curves as JPEG, which a pure-stdlib decoder cannot open --
            # and a missing reading is not a reading of absence (CLAUDE.md §4).
            rec["figures"].append({
                "page": pno, "image_index": None, "arm": "pixel",
                "caption_head": _caption_for(page, d["bbox"], page_text),
                "verdict": "undetermined",
                "bands": [], "matched_ticks": 0, "n_tokens": 0,
                "image_px": d["srcsize"], "encoding": d["filters"],
                "⛔": ("embedded image encoding not decodable by this pure-stdlib reader "
                       f"({'+'.join(d['filters']) or 'unknown'}); the figure was NOT read, and "
                       "this row is an unanswered question rather than a negative")})
        if km_page and not imgs and not declined:
            tick = text_axis_band(page)
            if tick is None:
                continue
            span = max(1.0, tick[-1].cx - tick[0].cx)
            lo, hi = tick[0].cx - 0.10 * span, tick[-1].cx + 0.10 * span
            top = min(t.cy for t in tick) - 1.0
            toks = [t for t in page_tokens(page) if t.cy >= top and lo <= t.cx <= hi]
            res = decide(toks, span, page_text=page_text,
                         max_risk_gap=MAX_RISK_GAP * page.bbox[3])
            if not _looks_like_a_plot(res):
                continue
            rec["figures"].append({"page": pno, "image_index": None, "arm": "text",
                                   "tick_row_text": [t.text for t in tick],
                                   "tick_row_span_pt": round(span, 1),
                                   "caption_head": _caption_head(page_text), **res})
    rec["n_figures"] = len(rec["figures"])
    rec["n_with_risk_row"] = sum(1 for f in rec["figures"] if f["verdict"] == "present")
    rec["n_without"] = sum(1 for f in rec["figures"] if f["verdict"] == "absent")
    rec["n_undetermined"] = sum(1 for f in rec["figures"] if f["verdict"] == "undetermined")
    return rec


def _page_text(page) -> list[str]:
    from pdfminer.layout import LTTextContainer  # noqa: PLC0415
    out = []

    def walk(obj):
        for el in obj:
            if isinstance(el, LTTextContainer):
                out.append(el.get_text())
            elif hasattr(el, "__iter__"):
                walk(el)

    walk(page)
    return out


def _caption_for(page, img_bbox, page_text: str) -> str:
    """The caption NEAREST this figure, because a page holds more than one.

    ⚠ Taking the page's first "Fig..." labelled chiusole2020's Figure 2 as its Figure 1 and
    martinbroto2020's swimmer plot as the waterfall above it -- a mislabelled reading, which is the
    failure this repository's own retrieval record warns is worse than a missing one.
    """
    from pdfminer.layout import LTTextLine  # noqa: PLC0415

    best, best_d = None, None
    stack = [page]
    while stack:
        for el in stack.pop():
            if isinstance(el, LTTextLine):
                text = el.get_text().strip()
                if re.match(r"(Fig(?:ure)?\.?\s*\d+)", text, re.I):
                    d = abs(el.y1 - img_bbox[1])
                    if best_d is None or d < best_d:
                        best, best_d = text, d
            elif hasattr(el, "__iter__"):
                stack.append(el)
    if best:
        return best[:130].replace("\n", " ").strip()
    return _caption_head(page_text)


def _caption_head(page_text: str) -> str:
    m = re.search(r"(Fig(?:ure)?\.?\s*\d+[^\n]{0,110})", page_text)
    return (m.group(1) if m else page_text[:80]).replace("\n", " ").strip()


def _looks_like_a_plot(res: dict) -> bool:
    """A figure whose axis region holds no tick-label band is a photograph, not a plot.

    ⚠ Asked of the band the RULE identified, never of band 0: a plot that draws tick marks puts
    those in band 0, and keying on it dropped masunaga2025 Fig. 1 out of the corpus entirely --
    an unmeasured figure, which reads afterwards exactly like a figure nobody needed to refuse.
    """
    return res.get("tick_label_band_index") is not None


def _page_png(page_png_dir: str, source_id: str, pno: int) -> str | None:
    """The rendered page, under either of the two names poppler produces (page-3 / page-03)."""
    for name in (f"{source_id}_page-{pno}.png", f"{source_id}_page-{pno:02d}.png"):
        path = os.path.join(page_png_dir, name)
        if os.path.exists(path):
            return path
    return None


def build(pdf_dir: str, dump_dir: str | None = None, page_png_dir: str | None = None,
          provenance: dict | None = None) -> dict:
    doc = {
        "_generated_by": "research/modalities/km_risk_row_detect.py",
        "_what": "Whether each reachable EMC Kaplan-Meier figure PRINTS a numbers-at-risk row -- "
                 "the condition POLICY-evidence.md §2.7(a) makes mandatory before a curve may be "
                 "reconstructed at all.",
        "_not_medical_advice": "Nothing here is medical advice, and nothing here asserts efficacy, "
                               "safety or clinical readiness.",
        "⛔_this_is_an_admissibility_reading_not_a_digitization": "A `present` verdict says a row "
            "is printed. The VALUES in it are read separately, by eye, through km_digitize.py, "
            "which is where digitization provenance lives.",
        "method": {
            "rule": "A band of marks below the axis is a numbers-at-risk row iff it carries at "
                    "least MIN_MARKS marks, at least MIN_MATCHED_TICKS of them sit within TICK_TOL "
                    "of a tick-label mark, and its median mark is no wider than MAX_MARK_WIDTH. "
                    "The first band below the axis is taken as the tick labels.",
            "arms": {"pixel": "ink clusters from an embedded raster; positions readable, values not",
                     "text": "word boxes from the PDF text layer, for a vector figure"},
            "constants": {"INK_LUMA_MAX": INK_LUMA_MAX, "AXIS_MIN_SPAN": AXIS_MIN_SPAN,
                          "CLUSTER_GAP": CLUSTER_GAP, "BAND_GAP": BAND_GAP,
                          "MIN_MARKS": MIN_MARKS, "MIN_MATCHED_TICKS": MIN_MATCHED_TICKS,
                          "TICK_TOL": TICK_TOL, "MAX_MARK_WIDTH": MAX_MARK_WIDTH},
        },
        "⛔_the_figures_are_not_committed": "Their licences do not permit it. What makes this "
            "re-derivable instead is the recipe: the branch and path every PDF was read from, and "
            "the sha256 of each file as read. A reading whose input digest does not match is a "
            "reading of a different document.",
        "inputs": provenance or {},
        "control": run_control(),
        "sources": [],
    }
    for name in sorted(os.listdir(pdf_dir)):
        if not name.endswith(".pdf"):
            continue
        doc["sources"].append(read_pdf(name[:-4], os.path.join(pdf_dir, name), dump_dir,
                                       page_png_dir))
    doc["_totals"] = {
        "papers": len(doc["sources"]),
        "figures": sum(s["n_figures"] for s in doc["sources"]),
        "with_risk_row": sum(s["n_with_risk_row"] for s in doc["sources"]),
        "without": sum(s["n_without"] for s in doc["sources"]),
        "undetermined": sum(s["n_undetermined"] for s in doc["sources"]),
    }
    return doc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf-dir", help="directory of article PDFs to read")
    ap.add_argument("--dump-dir", help="write each figure raster here (licence permitting)")
    ap.add_argument("--page-png-dir", help="rendered page PNGs, used only for figures whose "
                                           "embedded encoding this reader cannot decode")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--cache-ref", default=None, help="git ref the input PDFs came from")
    ap.add_argument("--cache-path", default=None, help="path prefix inside that ref")
    ap.add_argument("--cache-commit", default=None, help="commit of that ref, as read")
    ap.add_argument("--page-raster-note", default=None, help="how the page PNGs were produced")
    ap.add_argument("--check", action="store_true", help="synthetic controls only")
    args = ap.parse_args(argv)
    if args.check or not args.pdf_dir:
        ctl = run_control()
        print(json.dumps(ctl, indent=2, ensure_ascii=False))
        return 0 if ctl["passed"] else 1
    if args.dump_dir:
        os.makedirs(args.dump_dir, exist_ok=True)
    provenance = {"cache_branch": args.cache_ref, "cache_path": args.cache_path,
                  "cache_commit": args.cache_commit,
                  "page_rasters": args.page_raster_note}
    doc = build(args.pdf_dir, args.dump_dir, args.page_png_dir, provenance)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps(doc["_totals"], indent=2))
    return 0 if doc["control"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
