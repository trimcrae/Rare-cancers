"""The submission PDF is an ASSEMBLY, and an assembly's failure mode is silent loss.

The builder splices three generated files into one document and inlines three figures. Every one
of those joins is anchored on a heading or a legend opener in the manuscript, and a manuscript is
prose that gets edited. Renaming `## References` would, without an assertion, produce a PDF that
looks complete for thirty-three pages and then has no reference list — the kind of defect nobody
finds until a reviewer does.

These tests exercise the real files, not fixtures. A fixture would prove the regex works; only the
real manuscript proves the anchors it is aimed at still exist.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import build_submission_pdf as bsp  # noqa: E402

PAPER = bsp.PAPERS["aso"]


@pytest.fixture(scope="module")
def assembled():
    return bsp.assemble(PAPER)


@pytest.fixture(scope="module")
def rendered(assembled):
    return bsp.markdown_to_html(assembled)


def test_the_pointer_paragraphs_are_replaced_rather_than_kept():
    """The manuscript says the tables 'are in <file>'. The PDF must contain them, not the sentence."""
    body = bsp.assemble(PAPER)
    assert "fusion-junction-aso-submission-tables.md" not in body
    assert "fusion-junction-aso-submission-references.md" not in body


def test_every_reference_entry_survives_the_splice(assembled):
    refs = bsp.read(PAPER["references"])
    entries = re.findall(r"^(\d+)\.\s", refs, re.M)
    assert len(entries) > 30, "reference file looks empty; the splice would silently succeed"
    for number in entries:
        assert re.search(rf"^{number}\.\s", assembled, re.M), f"reference {number} was lost"


def test_every_table_row_survives_the_splice(assembled):
    tables = bsp.read(PAPER["tables"])
    rows = [ln for ln in tables.split("\n")
            if ln.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", ln.strip())]
    assert len(rows) > 100
    assert sum(1 for ln in assembled.split("\n") if ln.strip().startswith("|")) >= len(rows)


def test_each_figure_is_placed_above_the_legend_that_describes_it(assembled):
    """A panel and its legend must be adjacent, and in that order."""
    for prefix in PAPER["figures"]:
        figure_at = [m.start() for m in re.finditer(r"<figure class=\"figure\">", assembled)]
        legend_at = assembled.index("**" + prefix)
        assert any(pos < legend_at for pos in figure_at), f"{prefix} legend has no figure above it"
    assert assembled.count("<figure class=\"figure\">") == len(PAPER["figures"])


def test_a_renamed_section_fails_the_build_instead_of_dropping_content():
    """⛔ The whole point of anchoring. A missing anchor must be fatal, never a no-op."""
    with pytest.raises(SystemExit) as excinfo:
        bsp.splice("## Something Else\n\npointer\n", "References", "replacement", "the references")
    assert "anchor not found" in str(excinfo.value)


def test_a_figure_with_no_legend_fails_the_build():
    with pytest.raises(SystemExit) as excinfo:
        bsp.inline_figures("# paper\n\nno legends here\n", PAPER["figures"])
    assert "no legend found" in str(excinfo.value)


def test_citation_markers_render_and_their_pmid_comments_do_not(rendered):
    """PMIDs ride beside each superscript in a non-rendering comment; a leaked one would print
    mid-sentence. The reference LIST carries `PMID: n` as visible text on purpose, which is why
    this looks only at the body above it."""
    body = rendered.split("<h2>References</h2>")[0]
    assert "<sup>" in body
    assert "PMID:" not in body
    assert "<!--" not in rendered


def test_no_unconverted_markdown_reaches_the_page(rendered):
    """Bold and pipe-table syntax leaking through as literal text is the visible failure."""
    text = re.sub(r"<svg.*?</svg>", "", rendered, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    assert "**" not in text
    assert not re.search(r"(?<![\w/:])\|(?!\w)", text), "a pipe table did not become a <table>"


def test_the_repo_frontmatter_is_stripped(rendered):
    """id/level/canonical_for are internal routing and must not reach a reviewer."""
    for field in ("canonical_for", "last_verified", "DOC-FUSION-JUNCTION-ASO-SUBMISSION"):
        assert field not in rendered


def test_the_tables_go_on_landscape_pages(rendered):
    """Twelve-column tables are unreadable in portrait; the named page is what fixes that."""
    page = bsp.wrap_html("t", rendered)
    assert 'section class="landscape"' in page
    assert "@page landscape" in page
    section = re.search(r'<section class="landscape">(.*?)</section>', page, re.S).group(1)
    assert section.count("<table") == 6, "the landscape section lost a table"


def test_the_reference_list_is_marked_up_for_hanging_indent(rendered):
    assert 'id="references-list"' in bsp.wrap_html("t", rendered)
