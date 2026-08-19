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

⛔⛔ AND THE LIVE-TEXT HALF WAS ITSELF FAIL-QUIET UNTIL 2026-08-19, in exactly the way the second
paragraph above warns about. It searched for `\bT[Jj]\b` over the file's RAW bytes as well as its
inflated streams, and a two-byte token that common turns up by chance inside compressed data.
Measured on the four shipped figures, the raw bytes alone carry 0, 0, 2 and 1 such hits — the two
in `aso-chance-baseline.pdf` sit inside a Flate stream between `\x7fA` and `\x92 \x185`, and are
not operators at all. So for two of the four figures a converter that outlined every glyph would
have produced a file with no text operator anywhere and this assertion would still have passed on
compression noise. It now counts only text-showing OPERATORS inside inflated content streams, and
it counts them against the label set of the SVG the figure is drawn from, so losing SOME labels
fails too rather than only losing all of them.
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


def _inflated(path):
    """Only the decompressed content streams, with the raw container bytes deliberately excluded.

    An operator search has to run over this and not over `_expanded`: compressed bytes are
    indistinguishable from PDF syntax, so any short token will be "found" in them sooner or later.
    """
    raw = open(path, "rb").read()
    blobs = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.S):
        try:
            blobs.append(zlib.decompress(m.group(1)))
        except Exception:  # noqa: BLE001 - a non-Flate stream is expected, not an error
            pass
    return b"\n".join(blobs)


#: A text-showing operator, in the two forms a converter emits: `(text) Tj` / `<hexcodes> Tj` for a
#: single run, and `[ ... ] TJ` for a kerned array. Chromium's PDF path writes the hex form one
#: glyph at a time, which is why the counts below run into the hundreds for a figure with a few
#: dozen labels. Matching the OPERAND is what separates an operator from two bytes of entropy.
_SHOW_TEXT = re.compile(rb"(?:\)|>|\])\s*T[Jj][\s\[<(/]")


def _label_count(name):
    """How many non-blank `<text>` nodes the SVG this PDF is converted from draws.

    Derived from the sibling artifact rather than typed, so a figure that gains or loses labels
    moves its own floor. ⛔ NOT A SKIP IF THE SVG IS ABSENT: the PDF is generated FROM it, so a
    missing SVG means the deposit cannot be rebuilt, which is a finding and not a reason to stop
    checking.
    """
    svg_path = os.path.join(FIGDIR, name.replace(".pdf", ".svg"))
    assert os.path.exists(svg_path), (
        f"{name} has no sibling SVG at {svg_path}; the PDF is converted from it, so its label set "
        "cannot be derived and the figure cannot be regenerated")
    svg = open(svg_path, encoding="utf-8").read()
    return len([t for t in re.findall(r"<text\b[^>]*>([^<]*)</text>", svg) if t.strip()])


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

    #: ⛔ INFLATED STREAMS ONLY, AND OPERATOR FORM ONLY. See the module docstring: over the raw
    #: bytes this assertion passed on compression noise for two of the four figures.
    show = _SHOW_TEXT.findall(_inflated(path))
    labels = _label_count(name)
    assert len(show) >= labels, (
        f"{name} carries {len(show)} text-showing operator(s) in its content streams against "
        f"{labels} non-blank <text> node(s) in the SVG it is drawn from. Every label must survive "
        "conversion as selectable text; a converter that outlines glyphs produces a figure that is "
        "sharp, vector, and unsearchable. The floor is the SVG's own label count, so it moves with "
        "the figure — if the figure genuinely lost labels, that is the finding.\n"
        "⚠ Do NOT restore a raw-bytes search to make this pass: `\\bT[Jj]\\b` matches by chance "
        "inside Flate streams, which is the defect this replaced."
    )

    # A subsetted font is named `ABCDEF+Family`; the six-letter tag is the subset marker. Full-font
    # embedding is not a correctness defect but it bloats the deposit, and its ABSENCE here would
    # mean no font is embedded at all, which breaks rendering on a machine without the family.
    fonts = re.findall(rb"/BaseFont\s*/([A-Z]{6}\+[^\s/\]>]+)", data)
    assert fonts, (
        f"{name} embeds no subsetted font. Either no font is embedded — in which case the figure "
        "renders differently wherever the family is missing — or the glyphs were outlined."
    )
