#!/usr/bin/env python3
"""Build the Word (.docx) manuscript a Nucleic Acid Therapeutics submission actually needs.

⛔ WHY THIS EXISTS AT ALL, AND IT IS NOT A CONVENIENCE. Read at primary source 2026-08-23 and
captured verbatim to `research/literature/nat-submission-guidelines-2026-08-23.md`:

    "The preferred format for your manuscript is Word. You do not need to follow a template, but
     please ensure your heading levels are clear, and the sections clearly defined.
     The LaTeX files are also accepted."

PDF is not among the accepted manuscript formats, and this repository built nothing else. The same
page says a manuscript that does not conform "will be returned to you for amendments prior to peer
review" — so a submission carrying only PDFs is returned before anyone reads it. That is the whole
justification for this file; it is not a nicer export.

★ IT REUSES THE PDF PIPELINE RATHER THAN RE-IMPLEMENTING IT. `build_submission_pdf.assemble` +
`wrap_manuscript` already turn the manuscript and its companions into one HTML document with the
tables spliced in and the display items in place. Producing a SECOND renderer would give the
submission two documents that could disagree, which is the one-of-a-pair defect this repository
keeps paying for. So: same HTML, one substitution, then a converter.

⛔⛔ THE ONE SUBSTITUTION, AND WHY IT IS NOT OPTIONAL. LibreOffice's HTML import DROPS INLINE `<svg>`
SILENTLY — measured here, not assumed: the first conversion of this manuscript produced a 23 KB
.docx with 5,148 words, 16 headings, 2 tables and ZERO images, while the figure legend sat in the
text describing a figure that was not there. The output looked entirely healthy. So each inline
`<svg>` is replaced by an `<img>` pointing at the 300 dpi PNG this repository already renders beside
the SVG, and the image count in the RESULT is asserted against the number of figures the paper
declares. A conversion that loses a figure fails the build.

⚠ REQUIRES LibreOffice WITH THE WRITER FILTERS (`soffice` plus `libreoffice-writer`). `libreoffice-core`
alone is not enough and fails in a way that reads as a corrupt input rather than a missing filter:
every source, including a two-line `.txt`, reports "Error: source file could not be loaded".
BOTH filters are named explicitly for the same reason — without `--infilter` the HTML loads as a
Writer/WEB document and the .docx comes out in web layout, and without the explicit output filter
the run aborts with "no export filter for ... docx found".

    python3 research/manuscripts/build_submission_docx.py            # every paper that declares one
    python3 research/manuscripts/build_submission_docx.py --paper aso-journal
"""
from __future__ import annotations

import argparse
import base64
import struct
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_submission_pdf as bsp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

#: The output filter LibreOffice needs by name. `--convert-to docx` alone aborts.
DOCX_FILTER = "docx:MS Word 2007 XML"
#: And the input filter, so the HTML loads as a Writer document rather than Writer/Web.
HTML_FILTER = "HTML (StarWriter)"

#: ⛔ A FLOOR, NOT A TARGET. The check below asserts the converted document is not a stub; it is
#: deliberately far under any real manuscript so that it fires on catastrophe (an empty convert, a
#: title page only) and never on ordinary editing. The real content check is the figure count.
MIN_WORDS = 500


def _svg_to_png(html, paper):
    """Replace every inline <svg> with the PNG this repository already renders beside it.

    ⛔ THE PNG IS NOT GENERATED HERE. `svg_to_submission_formats.py` renders it and
    `aso_figure_provenance.py --check` pins it; this only points at it. A missing PNG is an error,
    never a silent drop — the whole reason this function exists is that a silent drop is exactly
    what LibreOffice does on its own.
    """
    figures = sorted(set((paper.get("figures") or {}).values()))
    pngs = []
    for svg in figures:
        png = os.path.join(HERE, "figures", svg.replace(".svg", ".png"))
        if not os.path.exists(png):
            raise SystemExit(
                f"{os.path.relpath(png, REPO)} is missing, and the .docx converter cannot embed the "
                f"figure without it. Render it with svg_to_submission_formats.py — do NOT let the "
                f"conversion proceed, because LibreOffice drops the inline SVG without a word.")
        pngs.append(png)

    blocks = list(re.finditer(r"<svg\b.*?</svg>", html, re.S | re.I))
    if len(blocks) != len(pngs):
        raise SystemExit(
            f"the manuscript HTML holds {len(blocks)} inline <svg> block(s) but the paper declares "
            f"{len(pngs)} figure(s). The substitution is positional, so an uneven pair would put "
            f"the wrong image under a legend.")
    # ⛔⛔ A `file://` SRC PRODUCES A LINKED IMAGE, NOT AN EMBEDDED ONE, AND THE DIFFERENCE IS
    # INVISIBLE IN EVERY COUNT. Measured here: the first working version wrote
    # `<img src="file:///home/user/.../aso-multipartner-seam.png">`, LibreOffice converted it
    # happily, `<w:drawing>` appeared exactly once — and `word/media/` was EMPTY. The .docx carried
    # a pointer into this machine's filesystem, so it would have rendered as a broken frame for
    # every reader outside this container, which is to say for the journal. The verifier below
    # passed it, because counting `<w:drawing>` counts the REFERENCE. That is CLAUDE.md §4's
    # "presence is never evidence of provenance" reproduced inside the check written to enforce it.
    # A data: URI leaves LibreOffice nothing to link TO, so the bytes go into the archive; the
    # verifier now reads `word/media/` and would fail this again.
    # ⛔⛔ AND `style="width:100%"` PUT THE FIGURE IN AT THE WRONG SHAPE, WHICH IS THE OTHER WAY A
    # CONVERSION LOSES A FIGURE WITHOUT LOSING THE COUNT (trimcrae, 2026-08-25: "the figures on the
    # word doc look super weird"). LibreOffice's HTML import has no containing block to resolve a
    # PERCENTAGE against, so it does not fall back to the image's natural size — it invents a box.
    # MEASURED in the built .docx: `aso-multipartner-seam.png` is 2126x1068 (a 2:1 landscape panel)
    # and `<wp:extent>` placed it at 0.79in wide by 3.56in tall — squeezed into a narrow vertical
    # frame at roughly 1:4.5, so the panel rendered unreadable while every check here stayed green.
    # ⚠ THE COUNT CANNOT SEE THIS. `_verify` asserts that the bytes are in `word/media/` and that
    # the drawing count matches; an image can be present, embedded and correctly counted while being
    # displayed at a shape nobody can read. The geometry is asserted below for that reason.
    # ★ THE FIX IS ABSOLUTE UNITS DERIVED FROM THE FILE'S OWN PIXELS. Width is the A4 text measure
    # (210mm less 25mm margins each side), height follows from the PNG's real aspect ratio, so the
    # figure cannot be placed at a shape its source does not have.
    for block, png in zip(reversed(blocks), reversed(pngs)):
        raw = open(png, "rb").read()
        px_w, px_h = _png_size(raw, png)
        mm_w = 160.0
        mm_h = mm_w * px_h / px_w
        b64 = base64.b64encode(raw).decode("ascii")
        img = (f'<img src="data:image/png;base64,{b64}" '
               f'style="width:{mm_w:.1f}mm;height:{mm_h:.1f}mm" />')
        html = html[:block.start()] + img + html[block.end():]
    return html, len(pngs)


def _png_size(raw, path):
    """(width, height) in pixels, read from the PNG's own IHDR rather than assumed.

    ⛔ NOT A GUESS AND NOT A CONSTANT. The whole defect this guards against was a figure placed at
    a shape its source does not have, so the shape has to come out of the file.
    """
    if raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise SystemExit(f"{os.path.basename(path)} is not a PNG this can measure; the figure's "
                         f"aspect ratio would have to be assumed, which is the defect itself.")
    return struct.unpack(">II", raw[16:24])


def _verify(docx_path, want_figures):
    """⛔ A PRODUCED FILE IS NOT A CORRECT FILE. Read what is actually in the archive.

    CLAUDE.md §4: presence is never evidence of provenance, and a plausible-looking record is more
    dangerous than an empty one. Everything checked here is something only a real conversion can
    produce — body words, heading styles, embedded images — never something an empty template fills
    in.
    """
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        media_px = {}
        for n in media:
            raw = z.read(n)
            if raw[:8] == b"\x89PNG\r\n\x1a\n" and raw[12:16] == b"IHDR":
                media_px[n] = struct.unpack(">II", raw[16:24])
    words = len(re.sub(r"<[^>]+>", " ", xml).split())
    headings = len(re.findall(r'w:pStyle w:val="Heading', xml))
    #: ⛔ THE IMAGE COUNT IS THE NUMBER OF FILES IN `word/media/`, NEVER THE NUMBER OF `<w:drawing>`
    #: ELEMENTS. A linked image has a drawing element and no bytes; see the note in `_svg_to_png`.
    #: Counting the references is what let a .docx pointing at this container's filesystem pass.
    images = len(media)
    referenced = len(re.findall(r"<w:drawing", xml)) + len(re.findall(r"<w:pict", xml))
    problems = []
    if referenced != images:
        problems.append(f"{referenced} image reference(s) against {images} embedded file(s) in "
                        f"word/media — the difference is a LINKED image, which renders as a broken "
                        f"frame for anyone who does not have this filesystem")
    if words < MIN_WORDS:
        problems.append(f"only {words} words in the body (floor {MIN_WORDS}) — the convert produced a stub")
    if not headings:
        problems.append("no Heading styles — NAT asks that heading levels be clear, and a .docx of "
                        "undifferentiated body text does not meet that")
    if images != want_figures:
        problems.append(f"{images} embedded image(s) against {want_figures} declared figure(s); "
                        f"word/media holds {len(media)} file(s). LibreOffice drops what it cannot "
                        f"import WITHOUT reporting it, so this is the check that catches it")
    #: ⛔⛔ SHAPE, NOT JUST PRESENCE. A figure can be embedded, counted and correctly referenced
    #: while being DISPLAYED at a shape nobody can read, and every check above passes it. Measured
    #: 2026-08-25: a 2126x1068 panel was placed at 0.79in by 3.56in — squeezed to about 1:4.5 from a
    #: source that is 2:1 — because the <img> carried `width:100%`, which LibreOffice's HTML import
    #: has no containing block to resolve. `_svg_to_png` now emits absolute mm derived from the
    #: file's own pixels; this asserts the RESULT rather than trusting that it did.
    #: ⚠ The tolerance is 2%, which is rounding to the nearest 0.1mm and nothing else. This is not a
    #: taste check — it fires only when the placed box disagrees with the source image's own aspect.
    placed = [(int(a), int(b)) for a, b in re.findall(r'<wp:extent cx="(\d+)" cy="(\d+)"', xml)]
    natural = [px for _, px in sorted(media_px.items())]
    for (cx, cy), (px_w, px_h) in zip(placed, natural):
        if not cx or not cy or not px_h:
            continue
        want, got = px_w / px_h, cx / cy
        if abs(got - want) / want > 0.02:
            problems.append(
                f"a figure is placed at aspect {got:.2f} ({cx / 914400:.2f}in x "
                f"{cy / 914400:.2f}in) against its source image's {want:.2f} ({px_w}x{px_h}px) — "
                f"the picture is in the file and is being drawn at the wrong shape")
    if problems:
        raise SystemExit(f"{os.path.relpath(docx_path, REPO)} converted but is not a usable "
                         "submission file:\n  - " + "\n  - ".join(problems))
    return {"words": words, "headings": headings, "images": images}


def build(name, paper):
    out_docx = os.path.join(HERE, paper["out"].replace(".pdf", "-manuscript.docx"))

    body, floats = bsp.assemble(paper, "manuscript")
    title = re.sub(r"[*_`]", "", re.search(r"^#\s+(.*)$", body, re.M).group(1))
    html = bsp.wrap_manuscript(
        title, bsp.markdown_to_html(body, floats),
        f'<p class="version">{bsp.provenance_line(paper, "manuscript")}</p>')
    html, n_figures = _svg_to_png(html, paper)

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise SystemExit(
            "no `soffice` on PATH. The .docx is what a Nucleic Acid Therapeutics submission "
            "uploads, so this is a real gap rather than an optional export: install "
            "`libreoffice-writer` (libreoffice-core alone reports every input as unloadable), or "
            "run this on a runner that has it.")

    with tempfile.TemporaryDirectory() as work:
        src = os.path.join(work, os.path.basename(out_docx).replace(".docx", ".html"))
        with open(src, "w", encoding="utf-8") as fh:
            fh.write(html)
        env = dict(os.environ, HOME=work)
        proc = subprocess.run(
            [soffice, "--headless", "--norestore",
             f"-env:UserInstallation=file://{os.path.join(work, 'profile')}",
             "--infilter=" + HTML_FILTER, "--convert-to", DOCX_FILTER,
             "--outdir", work, src],
            capture_output=True, text=True, timeout=900, env=env)
        made = src.replace(".html", ".docx")
        if not os.path.exists(made):
            raise SystemExit(
                f"LibreOffice did not write a .docx.\nstdout: {proc.stdout.strip()}\n"
                f"stderr: {proc.stderr.strip()}")
        counts = _verify(made, n_figures)
        shutil.move(made, out_docx)

    stamp = {"built_from": {}}
    for rel in paper.get("stamp_sources", ()):
        path = os.path.join(HERE, rel)
        if os.path.exists(path):
            stamp["built_from"][rel] = hashlib.sha256(open(path, "rb").read()).hexdigest()
    for svg in sorted(set((paper.get("figures") or {}).values())):
        png = os.path.join(HERE, "figures", svg.replace(".svg", ".png"))
        if os.path.exists(png):
            stamp["built_from"][f"figures/{svg.replace('.svg', '.png')}"] = \
                hashlib.sha256(open(png, "rb").read()).hexdigest()
    stamp["artifact"] = os.path.basename(out_docx)
    stamp["measured"] = counts
    stamp["_what"] = ("sha256 of each document AND figure raster this .docx renders, written by "
                      "build_submission_docx.py, plus what the converted archive was measured to "
                      "contain. The .docx is current when every hash here matches the file on "
                      "disk; mtimes are not evidence.")
    #: ⛔⛔ `.docx` -> `.build-stamp.json` COLLIDES WITH THE MANUSCRIPT PDF'S STAMP AND SILENTLY
    #: OVERWRITES IT (caught 2026-08-23, before it shipped). `build_submission_pdf` writes
    #: `<stem>-manuscript.build-stamp.json` for `<stem>-manuscript.pdf`; substituting the same way
    #: here produces the identical path, so whichever builder ran last owned the file and
    #: `test_the_deposited_pdfs_are_not_stale` would have been reading the .docx's hashes. Two
    #: artifacts, two stamps: the suffix is APPENDED, not substituted.
    with open(out_docx + ".build-stamp.json", "w", encoding="utf-8") as fh:
        json.dump(stamp, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print(f"{name}: wrote {os.path.relpath(out_docx, REPO)} "
          f"({os.path.getsize(out_docx) // 1024} KB, {counts['words']} body words, "
          f"{counts['headings']} styled headings, {counts['images']} embedded figure(s))")
    return 0


#: ⚠ ENUMERATED, AND NARROWLY. Only a paper going to a venue that wants Word gets one; building a
#: .docx of the 84-page extended report would be work for a submission nobody is making.
DOCX_PAPERS = ("aso-journal",)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--paper", choices=sorted(DOCX_PAPERS))
    args = ap.parse_args(argv)
    names = [args.paper] if args.paper else sorted(DOCX_PAPERS)
    return max(build(n, bsp.PAPERS[n]) for n in names)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
