"""Every fusion-output table cell reaches the built page — cause-blind, read out of the PDF.

⛔ WHAT SHIPPED. Table 9 is seven columns; `LANDSCAPE_MIN_COLS` is 8, so `render_table`'s
`wide_body` rescue never fired for it and it set at full body width inside an 88 mm journal
column. In `nr4a3-fusion-transcriptional-output.pdf` at f44b75588 its last column, SEMA3C, ran off
the right edge of the paper: nine `n, p = …` occupancy readings that §3.11 argues from were not on
the page and not in the text layer. `test_a_display_item_cell_is_not_clipped.py` would have caught
it and does not reach this paper — it is scoped to the ASO builds by name — so the same defect
class was guarded for one paper and unguarded for another.

⚠ WHAT THIS CANNOT SEE, stated so a green run is not over-read: a cell that is PRESENT but
OVERPRINTED by the column beside it is in the text layer either way, and this file will pass on it.
That symptom was found by rasterising page 7, not by reading text, and only a rasterised page can
retire it.

★ WHAT THIS ASSERTS: every source table cell long enough to be evidence survives into both built
formats, and the stamp is checked first so the measurement is of the current source.
"""
from __future__ import annotations

import hashlib
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
SOURCE = os.path.join(MANUSCRIPTS, "fusion-output", "nr4a3-fusion-transcriptional-output.md")
BUILDS = ("nr4a3-fusion-transcriptional-output.pdf",
          "nr4a3-fusion-transcriptional-output-manuscript.pdf")
#: A cell too short to be evidence of anything appears somewhere in any document by accident.
MIN_CELL = 8

pypdf = pytest.importorskip("pypdf")


def _squash(text):
    return re.sub(r"\s+", "", text)


def _plain(cell):
    """A markdown cell as the PDF prints it: a link prints its TEXT, emphasis prints neither marker.

    ⚠ The link rule is not cosmetic. Appendix A's cells carry
    `[nr4a3-cistrome-search-2026-08-08.md](nr4a3-cistrome-search-2026-08-08.md)`, and comparing the
    raw markdown against the printed page reports a 1,600-character cell as missing when every word
    of it is on the page — a false clipping report, which is the way this kind of guard dies.
    """
    #: ⛔ CODE SPANS COME OUT FIRST, THE SAME ORDER `inline()` STASHES THEM IN, and for the same
    #: reason: this cell carries `` `per_peakset.*.panel.n_genes` `` and the words "empirical p*"
    #: later in the same sentence, so an emphasis rule run first pairs those two asterisks and
    #: DELETES the 200 characters between them — reporting a cell that is wholly on the page as
    #: clipped. A guard that manufactures its own findings is worse than none.
    held = []

    def _hold(match):
        held.append(match.group(1))
        return f"\x00{len(held) - 1}\x00"

    cell = re.sub(r"`([^`]+)`", _hold, cell)
    cell = re.sub(r"\[([^\]]+)\]\([^)\s]+\)", r"\1", cell)
    cell = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
    cell = re.sub(r"\*(.+?)\*", r"\1", cell)
    cell = re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], cell)
    cell = cell.replace("\\|", "|")
    return cell.strip()


def _cells():
    lines = open(SOURCE, encoding="utf-8").read().split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\|[\s:|-]+\|?\s*$", lines[i + 1].strip()):
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                for cell in lines[j].strip().strip("|").split("|"):
                    text = _plain(cell)
                    if len(_squash(text)) >= MIN_CELL:
                        out.append((i + 1, text))
                j += 1
            i = j
            continue
        i += 1
    return out


@pytest.mark.parametrize("build", BUILDS)
def test_every_table_cell_survives_into_the_built_pdf(build):
    pdf = os.path.join(MANUSCRIPTS, "fusion-output", build)
    stamp = pdf.rsplit(".pdf", 1)[0] + ".build-stamp.json"
    assert os.path.exists(pdf) and os.path.exists(stamp), f"{build} has not been built"
    #: ⚠ THE STAMP FIRST: reading a PDF built from an older source is a green measurement of the
    #: wrong object, which is worse than no measurement.
    for rel, want in json.load(open(stamp, encoding="utf-8"))["built_from"].items():
        got = hashlib.sha256(open(os.path.join(MANUSCRIPTS, rel), "rb").read()).hexdigest()
        assert got == want, f"{build} was built from a different version of {rel}"
    text = _squash("".join(p.extract_text() for p in pypdf.PdfReader(pdf).pages))
    cells = _cells()
    assert len(cells) > 100, f"only {len(cells)} cells were collected — the parser missed the tables"
    missing = [(line, cell) for line, cell in cells if _squash(cell) not in text]
    assert not missing, (
        f"{build}: {len(missing)} table cells are not in the built page — a column that overflows "
        "its container is cut at the paper's edge and takes its readings with it:\n  "
        + "\n  ".join(f"line {line}: {cell!r}" for line, cell in missing[:12]))
