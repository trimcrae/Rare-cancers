"""The deposited ASO figure PDFs must be VECTOR, and that was a claim with no instrument.

⛔ WHY THIS EXISTS. The preprint checklist has asserted, in prose, that the submission PDFs carry
"no image XObjects, subsetted fonts, live text". Nothing checked it. Measured 2026-08-17: the claim
is TRUE — zero image XObjects across all four figures — but it had been true only by the good
behaviour of the converter, and a converter option, a font fallback or a matplotlib backend change
could have rasterised a panel at any point without turning a single gate red. A raster figure in a
deposit is not cosmetic: it is unreadable at print resolution, it cannot be re-typeset by a journal,
and it is the kind of defect a reader finds and the author cannot fix without redoing the deposit.

⚠ AND THE FIRST DIAGNOSTIC THAT LOOKED AT THIS WAS WRONG, WHICH IS WHY THE PARSE BELOW IS FUSSY.
A `grep -a` for `/Image` over the raw bytes returned 1, 4, 137 and 40 hits and read as "these are
rasterised". Every one was a false positive: `/ImageB`, `/ImageC` and `/ImageI` are legacy ProcSet
tokens declaring which imaging models a page MAY use, not evidence that any image exists, and the
rest was noise from grepping compressed streams. The discriminating observation is `/Subtype /Image`
inside an object dictionary, and nothing weaker.

The parse is dependency-free on purpose: pypdf, pikepdf and pymupdf are all absent from this
environment, and a guard that skips when its parser is missing is the fail-quiet shape this
repository has shipped before.
"""
import os
import re
import zlib

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FIGDIR = os.path.join(REPO, "research", "manuscripts", "figures")

#: The four ASO figures the deposit ships — three numbered in the manuscript plus the supplementary
#: one. Listed rather than globbed because `figures/` also holds figures belonging to four other
#: papers, and this guard makes a claim about THIS deposit.
ASO_FIGURE_PDFS = (
    "aso-junction-space.pdf",
    "aso-multipartner-seam.pdf",
    "aso-chance-baseline.pdf",
    "aso-gap-length-tradeoff.pdf",
)


def _expanded(path):
    """The file's bytes plus every FlateDecode stream it holds, decompressed.

    A PDF keeps its content streams compressed, so a search over the raw file cannot see the
    operators inside them. Streams that fail to inflate are skipped rather than raising — some are
    not Flate at all, and their absence cannot create a false PASS here because every assertion
    below is either "count is zero" (more data can only add hits) or "count is positive" (checked
    against the raw bytes as well).
    """
    raw = open(path, "rb").read()
    blobs = [raw]
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        try:
            blobs.append(zlib.decompress(m.group(1)))
        except Exception:  # noqa: BLE001 - a non-Flate stream is expected, not an error
            pass
    return b"\n".join(blobs)


@pytest.mark.parametrize("name", ASO_FIGURE_PDFS)
def test_the_deposited_figure_carries_no_raster_image(name):
    path = os.path.join(FIGDIR, name)
    # ⛔ NOT A SKIP. These four files are tracked; if one is absent the deposit is broken, and a
    # skip would report that as "nothing to check".
    assert os.path.exists(path), f"{name} is missing from {FIGDIR} — the deposit cannot ship it"
    data = _expanded(path)
    images = re.findall(rb"/Subtype\s*/Image", data)
    assert not images, (
        f"{name} embeds {len(images)} raster image XObject(s). The submission figures must be "
        "vector so a journal can re-typeset them and so they survive print resolution. Redraw from "
        "the SVG rather than relaxing this — check for a matplotlib artist forcing rasterisation "
        "(rasterized=True, or an alpha-blended collection above the AGG threshold)."
    )


@pytest.mark.parametrize("name", ASO_FIGURE_PDFS)
def test_the_deposited_figure_carries_live_text_in_subsetted_fonts(name):
    """Vector-ness alone is not enough: text converted to outlines is vector and still unsearchable.

    ⚠ THE TWO HALVES FAIL DIFFERENTLY AND BOTH MATTER. A converter that outlines glyphs produces a
    figure with no `/BaseFont` and no text operators — perfectly sharp, and a reader cannot select,
    search or screen-read a single label. That is the failure this half catches, and the raster
    check above is blind to it.
    """
    path = os.path.join(FIGDIR, name)
    assert os.path.exists(path), f"{name} is missing from {FIGDIR} — the deposit cannot ship it"
    data = _expanded(path)

    show = re.findall(rb"\bT[Jj]\b", data)
    assert show, (
        f"{name} contains no text-showing operator, so its labels have been converted to outlines "
        "or dropped. The axis labels and legends must remain selectable text."
    )

    # A subsetted font is named `ABCDEF+Family`; the six-letter tag is the subset marker. Full-font
    # embedding is not a correctness defect but it bloats the deposit, and its ABSENCE here would
    # mean no font is embedded at all, which breaks rendering on a machine without the family.
    fonts = re.findall(rb"/BaseFont\s*/([A-Z]{6}\+[^\s/\]>]+)", data)
    assert fonts, (
        f"{name} embeds no subsetted font. Either no font is embedded — in which case the figure "
        "renders differently wherever the family is missing — or the glyphs were outlined."
    )
