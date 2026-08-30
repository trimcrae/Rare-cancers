"""⛔⛔ A TABLE CELL CLIPPED AT A COLUMN EDGE, IN THE PDF A REVIEWER ACTUALLY READS.

Round 19's blind seat found Table 1's last column truncated mid-word in two of the four built
PDFs — `fusion-junction-aso-journal-article.pdf`, the canonical submission artifact, and
`-anonymized.pdf`, what a double-anonymized reviewer receives. The header printed **test a** for
"test article"; the cells printed **E-N, engin const** and **T-N*, engin const** for "E-N,
engineered construct" and "T-N*, engineered construct". It is the column that tells a laboratory
which construct the reagent is the test article for.

★ MECHANISM, MEASURED IN PRINT MEDIA AND NOT INFERRED (2026-08-30, AUT-PD-188): the table laid out
at 100.99 mm inside a 99.10 mm column, and the last column's right edge fell 1.75 mm past the
container. Under `table-layout: auto` a table cannot be narrower than its min-content width, and
here that width is held by the reagent column, whose `.seq` span is `white-space: nowrap` on
purpose — an invisible newline inside a delimited oligonucleotide is the wrong-reagent hazard this
whole deposit is built around. The repair took the in-column cell padding from 4.8pt to 3.6pt,
which is the one width in the table carrying no information.

⛔ WHY THIS GUARD READS THE PDF RATHER THAN THE STYLESHEET. Three repairs were reasoned from the
CSS before the geometry was ever measured, and all three were wrong: `table-layout: fixed` (no
change, 6 pages to 7, and it is the same edit that once printed a corrupted 16-mer by forcing cells
narrower than their content), a lower `wide_body` column threshold (no change anywhere — `wide_body`
requires `not _IN_FLOAT` and every display item here renders through `render_float`, so it is false
by construction), and a smaller font (no change). **A rule read is not a width observed**, so this
file opens the built artifact and looks for the text.

★ AND IT IS DELIBERATELY CAUSE-BLIND. It asserts the outcome — every cell of every source table
survives into the built PDF — so it catches clipping, overprinting and a dropped column alike,
including from a mechanism nobody has met yet. Whitespace is ignored on both sides, because a cell
that WRAPS is correct and a cell that is CUT is not; deleted characters survive no normalisation.

⛔ WHAT THIS GUARD CANNOT SEE, said plainly, because a green run is not proof the tables are sound.
(1) **A clipped HEADER, when its words occur anywhere else in the paper.** "test article" was
truncated to "test a" in the same defect and this file does NOT catch it, because the caption
underneath legitimately says "their test article" and the search is document-wide. The two CELLS
are caught, and they and the header share one cause — a column overflowing its container — so the
mechanism is guarded even though one of its two symptoms is not. (2) **A cell shorter than
`MIN_CELL`**, which cannot be searched for honestly. (3) **Text present but overprinted**: these
characters are in the text layer either way, which is exactly how a corrupted 16-mer once passed
a text dump — `test_the_journal_display_items_say_what_their_rows_say` and the sequence-manifest
join are what stand between a reader and a wrong reagent, not this file. (4) **Whether the cell
landed in the right ROW or the right COLUMN** — presence, not position.

⚠ THE STAMP IS CHECKED FIRST, for the reason `test_the_journal_pdf_fits_its_page_budget` gives:
reading a PDF built from a previous version of the markdown is a green measurement of the wrong
object, which is worse than no measurement.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")
TABLES = os.path.join(ASO, "fusion-junction-aso-journal-tables.md")

#: ⛔ THE TWO BUILDS THAT CARRY THE DEFECT, AND THEY ARE THE TWO THAT GO OUT. The preprint and
#: manuscript formats do not opt into `tables_in_column`, so their tables span the full measure and
#: were never clipped — they are checked anyway, because a guard scoped to the builds that happened
#: to be broken would not notice the next one.
BUILDS = ("fusion-junction-aso-journal-article.pdf",
          "fusion-junction-aso-journal-article-anonymized.pdf",
          "fusion-junction-aso-journal-article-preprint.pdf",
          "fusion-junction-aso-journal-article-manuscript.pdf")

#: ⛔ AUT-PD-188 IS OPEN, AND THESE TWO BUILDS STILL CARRY IT. The guard is armed rather than
#: withheld: `strict=True` means the day the defect is fixed this file goes RED as an XPASS and
#: whoever fixed it must delete this marker, so the exemption cannot outlive the defect. It is
#: scoped to the two builds that set `tables_in_column`; the preprint and manuscript formats are
#: asserted for real, today.
#: ★ WHY IT IS NOT SIMPLY FIXED HERE, MEASURED 2026-08-30 AND NOT INFERRED: Table 1's min-content
#: is 100.99 mm inside an 84.35 mm column — over by 16.64 mm, which is MORE THAN THE ENTIRE WIDTH
#: OF ITS LAST COLUMN (15.81 mm), so deleting that column outright would still leave it 0.83 mm
#: over. 42% of the column is the reagent cell, whose `.seq` span is `white-space: nowrap` on
#: purpose. The table does not fit in one column and no in-column lever closes 16.64 mm; the one
#: rendering that is correct — `column-span: all` — costs a seventh page against a budget of six,
#: at a journal that charges per page. That trade is not a builder's to make silently.
#: ✅ EMPTY BECAUSE AUT-PD-188 IS CLOSED (2026-08-30, round 23). Table 1 was 16.64 mm too wide for
#: an 84.35 mm column and its last column clipped mid-word in both two-column builds — the header
#: printed "test a" for "test article" and the cells "E-N, engin const" for "E-N, engineered
#: construct", in the PDF a reviewer receives.
#: ★ THE FIX WAS CONTENT, NOT LAYOUT, AND THAT IS WHY IT COST NOTHING. The marker priced the repair
#: at `column-span: all` and a seventh page; by the time it was fixed the seventh page was already
#: spent on the FUS clause, so the priced repair had silently become an EIGHTH page, which
#: `test_the_journal_pdf_fits_its_page_budget.py` forbids. The column carried "E-N" and "T-N*"
#: under the header "test article", and the CAPTION already said what a test article is — so the
#: column moved into the caption ("E-N for the *EWSR1* reagent and T-N* for the *TAF15* one") and
#: the width pressure went with it. Nothing was cut and the paper stayed at seven pages.
#: ⚠ KEEP THIS SET AND `_case` RATHER THAN INLINE THE PARAMETRISATION: the next display item that
#: overflows needs a place to be registered, and a marker with nowhere to go becomes a deleted test.
KNOWN_CLIPPED: set[str] = set()


def _case(build):
    if build in KNOWN_CLIPPED:
        return pytest.param(build, marks=pytest.mark.xfail(
            strict=True,
            reason="a display item is known to overflow its column in this build. State the "
                   "measurement, the page cost of the fix, and delete this entry in the commit "
                   "that fixes it — strict=True means the suite goes red the day it is fixed."))
    return build

#: A cell too short to be evidence of anything: "3", "≥ 26.6", a bare mark. A one- or two-character
#: run appears somewhere in any document by accident, so it can neither pass nor fail honestly.
MIN_CELL = 8


def _squash(text):
    """Every whitespace run removed, so a WRAPPED cell reads the same and a CUT cell does not."""
    return re.sub(r"\s+", "", text)


def _plain(cell):
    """A markdown cell as the PDF prints it: emphasis markers gone, entities as glyphs."""
    cell = re.sub(r"\*\*(.+?)\*\*", r"\1", cell)
    cell = re.sub(r"\*(.+?)\*", r"\1", cell)
    cell = re.sub(r"`(.+?)`", r"\1", cell)
    cell = re.sub(r"\[(.+?)\]\([^)]*\)", r"\1", cell)
    return cell.strip()


def _source_cells():
    """Every cell and header of every pipe table in the display-item file, longest first."""
    if not os.path.exists(TABLES):
        pytest.fail(f"{os.path.basename(TABLES)} is missing, so no display item is checked. It is "
                    "a committed artifact, so its absence is a broken tree and not a skip.")
    cells = []
    for line in open(TABLES, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:\-|]+\|", line):        # the alignment rule
            continue
        for raw in line.strip("|").split("|"):
            plain = _plain(raw)
            if len(_squash(plain)) >= MIN_CELL:
                cells.append(plain)
    if not cells:
        pytest.fail(f"no pipe-table cells parsed out of {os.path.basename(TABLES)} — the guard "
                    "would pass vacuously, which is the failure it exists to prevent.")
    return sorted(set(cells), key=len, reverse=True)


def _pdf_text(path):
    #: ⛔ A FAIL, NOT A SKIP. pypdf is on the pip line and `./scripts/dev-setup.sh` installs it, so a
    #: missing import is a broken sandbox, not a reason for this guard to evaporate with its input —
    #: which is exactly what `test_no_guard_can_silently_not_run` refuses.
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        pytest.fail(f"pypdf is not importable ({exc}), so no built PDF can be read and this guard "
                    "would pass vacuously. Run ./scripts/dev-setup.sh.")
    return "".join(page.extract_text() or "" for page in PdfReader(path).pages)


def _not_stale(pdf):
    """The stamp's `built_from` against the live digests, before anything is read out of the PDF."""
    stamp_path = pdf[:-4] + ".build-stamp.json"
    if not os.path.exists(stamp_path):
        pytest.fail(f"{os.path.basename(pdf)} carries no build stamp, so nothing can say whether "
                    "its text belongs to the current sources.")
    stamp = json.load(open(stamp_path, encoding="utf-8"))
    for name, recorded in (stamp.get("built_from") or {}).items():
        live = os.path.join(ASO, os.path.basename(name))
        if not os.path.exists(live):
            continue
        digest = hashlib.sha256(open(live, "rb").read()).hexdigest()
        if isinstance(recorded, str) and len(recorded) == 64 and digest != recorded:
            pytest.fail(
                f"{os.path.basename(pdf)} is STALE against {os.path.basename(name)} — rebuild it "
                "with scripts/regenerate_aso_chain.sh. Reading a PDF built from sources that have "
                "since changed measures a document that no longer exists.")


@pytest.mark.parametrize("build", [_case(b) for b in BUILDS])
def test_every_display_item_cell_survives_into_the_built_pdf(build):
    pdf = os.path.join(ASO, build)
    if not os.path.exists(pdf):
        pytest.fail(f"{build} is missing. It is a committed artifact, so its absence is a broken "
                    "tree and not a skip.")
    _not_stale(pdf)
    printed = _squash(_pdf_text(pdf))
    missing = [c for c in _source_cells() if _squash(c) not in printed]
    assert not missing, (
        f"{build}: {len(missing)} display-item cell(s) do not appear in the built PDF, so the "
        f"column they sit in is being clipped, overprinted or dropped: {missing!r}. "
        "Whitespace is already ignored, so a cell that merely WRAPPED would have passed — these "
        "characters are absent from the page. Measure the table against its container in print "
        "media before changing any stylesheet rule; see this file's header for the three repairs "
        "that were reasoned from the CSS and were all wrong.")
