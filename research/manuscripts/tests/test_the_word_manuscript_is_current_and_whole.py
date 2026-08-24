"""The Word file a Nucleic Acid Therapeutics submission uploads is current, and contains its figure.

⛔ WHY A WORD FILE IS A GATED ARTIFACT AND NOT A CONVENIENCE. Read at primary source 2026-08-23 and
captured to `research/literature/nat-submission-guidelines-2026-08-23.md`: "The preferred format for
your manuscript is Word … The LaTeX files are also accepted." PDF is not among the accepted
manuscript formats, and the same page says a manuscript that does not conform "will be returned to
you for amendments prior to peer review". A stale or figure-less .docx is therefore a returned
submission, in a file nothing else in this repository reads.

⛔⛔ AND THE THING THIS FILE CATCHES THAT NOTHING ELSE COULD. `build_submission_docx.py` first wrote
its build stamp to `<stem>-manuscript.build-stamp.json` — the SAME path `build_submission_pdf.py`
uses for `<stem>-manuscript.pdf`. Whichever builder ran last owned the file, so the PDF staleness
gate would have been reading the .docx's hashes and vice versa, with no symptom either way. The
collision is asserted against below rather than merely fixed, because "these two names differ" is a
property that a later rename silently breaks.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import zipfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
DOCX = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-journal-article-manuscript.docx")
STAMP = DOCX + ".build-stamp.json"


def _stamp():
    assert os.path.exists(STAMP), (
        f"{os.path.basename(STAMP)} is missing. Build with "
        "`python3 research/manuscripts/build_submission_docx.py`.")
    return json.load(io.open(STAMP, encoding="utf-8"))


def test_the_word_file_exists_at_all():
    """⚠ ABSENCE IS A FINDING, NEVER A SKIP — a skipped gate on a missing submission file reads
    exactly like a passing one, and the file is the thing being submitted."""
    assert os.path.exists(DOCX), (
        f"{os.path.basename(DOCX)} is not built, and it is the file Nucleic Acid Therapeutics asks "
        "for. Build it with `python3 research/manuscripts/build_submission_docx.py` (needs "
        "`libreoffice-writer`; libreoffice-core alone reports every input as unloadable).")


def test_its_stamp_does_not_collide_with_the_manuscript_pdfs():
    """⛔ THE TWO ARTIFACTS MUST NOT SHARE A STAMP. See this module's docstring."""
    pdf_stamp = DOCX.replace(".docx", ".build-stamp.json")
    assert os.path.abspath(pdf_stamp) != os.path.abspath(STAMP), (
        "the .docx build stamp resolves to the same path as the manuscript PDF's. Whichever "
        "builder runs last then owns the file and both staleness gates read the wrong hashes.")


def test_the_word_file_is_not_stale():
    """Every source it renders hashes to what is on disk now. mtimes are not evidence."""
    drifted = []
    for rel, want in sorted(_stamp()["built_from"].items()):
        path = os.path.join(MANUSCRIPTS, rel)
        if not os.path.exists(path):
            drifted.append(f"{rel} (declared at build, now absent)")
            continue
        if hashlib.sha256(open(path, "rb").read()).hexdigest() != want:
            drifted.append(rel)
    assert not drifted, (
        f"{os.path.basename(DOCX)} was built from a different version of: {', '.join(drifted)}. "
        "Rebuild with `python3 research/manuscripts/build_submission_docx.py`. A Word file that "
        "disagrees with the manuscript is the copy an editor reads.")


def test_the_figure_travels_as_bytes_rather_than_as_a_link():
    """⛔⛔ COUNT THE PAYLOAD, NEVER THE POINTER (measured 2026-08-23).

    LibreOffice happily writes `<w:drawing>` for an image it merely LINKS to, so a .docx pointing at
    `file:///home/user/...` carries a drawing element, an empty `word/media/`, and a broken frame
    for every reader who is not this container. The verifier that shipped it counted the drawing
    elements. This counts the files.
    """
    with zipfile.ZipFile(DOCX) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/")]
        xml = z.read("word/document.xml").decode("utf-8")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
        payloads = {n: z.read(n) for n in media}
    drawings = len(re.findall(r"<w:drawing", xml)) + len(re.findall(r"<w:pict", xml))
    assert media, (
        "word/media is EMPTY while the document has "
        f"{drawings} image reference(s) — every figure is a LINK, not an embed.")
    assert drawings == len(media), (
        f"{drawings} image reference(s) against {len(media)} embedded file(s); the difference is "
        "linked and will not travel.")
    outward = re.findall(r'Target="(file:[^"]*|[A-Za-z]:[\\/][^"]*)"', rels)
    assert not outward, (
        f"the .docx references paths on the build machine: {outward}. Those resolve to nothing "
        "anywhere else.")
    for name, blob in payloads.items():
        assert len(blob) > 1024, f"{name} is {len(blob)} bytes — that is not a 300 dpi figure"


@pytest.mark.parametrize("what,floor", [("words", 500), ("headings", 4), ("images", 1)])
def test_the_conversion_did_not_quietly_drop_the_manuscript(what, floor):
    """The builder measures the archive it produced; this holds that measurement to a floor.

    ⚠ Floors, not targets — they fire on a catastrophic conversion (a title page only, an unstyled
    wall of text, a lost figure) and never on ordinary editing. NAT asks that "heading levels are
    clear, and the sections clearly defined", which is what the heading floor is about.
    """
    measured = _stamp().get("measured", {})
    assert what in measured, (
        f"the build stamp records no `{what}`. Rebuild — an older stamp cannot vouch for this file.")
    assert measured[what] >= floor, (
        f"the converted .docx has {measured[what]} {what} against a floor of {floor}.")
