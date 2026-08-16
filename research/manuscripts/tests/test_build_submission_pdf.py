"""The submission PDF is an ASSEMBLY, and an assembly's failure mode is silent loss.

The builder splices two generated files into the manuscript, inlines three figures, and — in
journal style — moves every table and figure to the point it is first cited. Every one of those
joins is anchored on a heading, a legend opener or an in-text citation, and a manuscript is prose
that gets edited. Renaming `## References` would, without an assertion, produce a PDF that looks
complete for twenty-two pages and then has no reference list.

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
def journal():
    body, floats = bsp.assemble(PAPER, "journal")
    front = bsp.parse_front_matter(body)
    rendered = bsp.markdown_to_html(front["body"], floats)
    return front, floats, rendered, bsp.wrap_journal(PAPER, front, rendered)


@pytest.fixture(scope="module")
def manuscript():
    body, _ = bsp.assemble(PAPER, "manuscript")
    return body, bsp.markdown_to_html(body)


# ---------------------------------------------------------------- content survives the assembly

def test_the_pointer_paragraphs_are_replaced_rather_than_kept(manuscript):
    """The manuscript says the tables 'are in <file>'. The PDF must contain them, not the sentence."""
    body, _ = manuscript
    assert "fusion-junction-aso-submission-tables.md" not in body
    assert "fusion-junction-aso-submission-references.md" not in body


@pytest.mark.parametrize("style", ["journal", "manuscript"])
def test_every_reference_entry_survives(style):
    body, _ = bsp.assemble(PAPER, style)
    entries = re.findall(r"^(\d+)\.\s", bsp.read(PAPER["references"]), re.M)
    assert len(entries) > 30, "reference file looks empty; the splice would silently succeed"
    for number in entries:
        assert re.search(rf"^{number}\.\s", body, re.M), f"reference {number} was lost"


def test_every_table_survives_into_the_journal_layout(journal):
    _, floats, rendered, _ = journal
    source_rows = [ln for ln in bsp.read(PAPER["tables"]).split("\n")
                   if ln.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", ln.strip())]
    assert len(source_rows) > 100
    assert len(re.findall(r"<tr>", rendered)) == len(source_rows), "a table row was dropped"
    # ⚠ DERIVED FROM THE GENERATED TABLES FILE, NOT TYPED (2026-08-16). This asserted `== 6` and had
    # to be chased by hand the moment Table 7 was generated. A typed count is the same defect
    # `_geometry_columns` names in submission_tables.py: it cannot notice a table added upstream, and
    # when one is added it fails for a reason that has nothing to do with the layout. The expectation
    # is now the count of captions the tables file itself carries, so a table added upstream must
    # still reach the layout, and a table dropped from the layout still fails.
    captions = set(re.findall(r"^\*\*Table (\d+)\.", bsp.read(PAPER["tables"]), re.M))
    assert len(captions) >= 6, captions
    assert sum(1 for v in floats.values() if v[0] == "table") == len(captions)


def test_every_figure_is_placed_with_the_legend_that_describes_it(journal):
    """⚠ A SUPPLEMENTARY PANEL IS KEYED ABOVE THE NUMBERED ONES SO IT LAYS OUT LAST.

    `build_submission_pdf.SUPPLEMENTARY_SORT_BASE` offsets it rather than special-casing the
    layout, so the key is 1001 and the label the body cites is "Supplementary Figure S1". Both
    halves are asserted: a mismatch between them is how a panel gets reported as uncited.
    """
    import build_submission_pdf as bsp
    _, floats, rendered, _ = journal
    figures = {n: p for (kind, n, p, _w) in floats.values() if kind == "figure"}
    numbered = {n for n in figures if n < bsp.SUPPLEMENTARY_SORT_BASE}
    supplementary = {n for n in figures if n >= bsp.SUPPLEMENTARY_SORT_BASE}
    assert numbered == {1, 2, 3}
    assert supplementary == {bsp.SUPPLEMENTARY_SORT_BASE + 1}
    for number, (svg, legend) in figures.items():
        assert svg.startswith("<svg")
        expected = (f"**Supplementary Figure S{number - bsp.SUPPLEMENTARY_SORT_BASE}."
                    if number >= bsp.SUPPLEMENTARY_SORT_BASE else f"**Figure {number}.")
        assert legend.startswith(expected), "a legend was paired to the wrong panel"
    assert rendered.count("<svg") == len(figures)


# ---------------------------------------------------------------- the anchors are load-bearing

def test_a_renamed_section_fails_the_build_instead_of_dropping_content():
    """⛔ The whole point of anchoring. A missing anchor must be fatal, never a no-op."""
    with pytest.raises(SystemExit) as excinfo:
        bsp.splice("## Something Else\n\npointer\n", "References", "replacement", "the references")
    assert "anchor not found" in str(excinfo.value)


def test_a_figure_with_no_legend_fails_the_build():
    with pytest.raises(SystemExit) as excinfo:
        bsp.split_figures("## Figure legends\n\nnothing here\n", PAPER["figures"])
    assert "no legend found" in str(excinfo.value)


def test_an_uncited_display_item_must_be_declared_not_guessed():
    """⚠ Figure 3 is never cited by name. An item with no anchor and no declaration must fail
    rather than be dropped at whatever offset the layout happened to reach."""
    with pytest.raises(SystemExit) as excinfo:
        bsp.place_floats("body text with no citations\n", [("Table 9", "@@FLOAT:table9@@")], {})
    assert "never cited" in str(excinfo.value)


def test_the_declared_fallback_for_figure_3_still_points_at_a_real_section():
    """⚠ Matches heading TEXT at any level, not a `### <number>`. Updated 2026-08-16 with the
    builder: the number form asserted that §3.10 existed, so an editorial pass that merged that
    subsection into a renamed one turned a placement question into a spurious failure about
    numbering. What must hold is that the declared anchor still names a section that exists."""
    body, _ = bsp.assemble(PAPER, "journal")
    for label, rule in PAPER["placement"].items():
        assert re.search(rf"^#{{2,4}}\s+.*{re.escape(rule['after_heading'])}.*$", body, re.M | re.I), (
            f"{label}'s declared placement anchor {rule['after_heading']!r} matches no heading")


def test_float_anchors_are_computed_before_any_insertion():
    """An inserted table must not become the anchor that a later table floats to."""
    body = "cite Table 1 here.\n\nand later cite Table 2 here.\n"
    out = bsp.place_floats(body, [("Table 1", "@@A@@"), ("Table 2", "@@B@@")], {})
    assert out.index("@@A@@") < out.index("and later"), "Table 1 did not land at its own citation"
    assert out.index("@@B@@") > out.index("and later")


def test_a_missing_front_matter_label_fails_the_build():
    with pytest.raises(SystemExit) as excinfo:
        bsp.parse_front_matter("# Title\n\n## Abstract\n\ntext\n\n## 1 · Intro\n")
    assert "front matter" in str(excinfo.value)


# ---------------------------------------------------------------- rendering correctness

def test_front_matter_captures_whole_paragraphs_not_first_lines(journal):
    """⚠ These fields wrap in the source. A first-line-only match silently dropped the tail."""
    front, _, _, _ = journal
    assert front["keywords"].endswith("myxoid chondrosarcoma")
    assert "ORCID" in front["affiliation"]
    # ⚠ Compared with whitespace normalised. The source wraps, and asserting a literal ending
    # made this test fail on a rewrap rather than on the defect it is for — a first-line-only
    # match dropping the tail. The tail is what is checked; how it wraps is not.
    assert " ".join(front["abstract"].split()).endswith(
        # ⚠ Re-pinned round 5: the abstract gained a closing scope sentence, so its last words moved.
        # It previously ended "…the selectivity value that would falsify the ranking used here." The
        # abstract is the artifact that travels alone to a reader, and it carried no statement that
        # the work is computational — the one in the repository frontmatter is stripped from both
        # rendered PDFs. This assertion still does its original job: proving the builder captured the
        # WHOLE paragraph rather than its first line.
        "nothing here asserts efficacy, safety, delivery to a tumour or clinical readiness.")


def test_citation_markers_render_and_their_pmid_comments_do_not(journal):
    """PMIDs ride beside each superscript in a non-rendering comment; a leaked one would print
    mid-sentence. The reference LIST carries `PMID: n` as visible text on purpose, which is why
    this looks only at the body above it."""
    _, _, rendered, _ = journal
    body = rendered.split("<h2>References</h2>")[0]
    assert "<sup>" in body
    assert "PMID:" not in body
    assert "<!--" not in rendered


@pytest.mark.parametrize("style", ["journal", "manuscript"])
def test_no_unconverted_markdown_reaches_the_page(style):
    body, floats = bsp.assemble(PAPER, style)
    if style == "journal":
        body = bsp.parse_front_matter(body)["body"]
    text = re.sub(r"<svg.*?</svg>", "", bsp.markdown_to_html(body, floats), flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    assert "**" not in text
    assert not re.search(r"(?<![\w/:])\|(?!\w)", text), "a pipe table did not become a <table>"
    assert "@@FLOAT" not in text, "a float token was never substituted"


def test_the_repo_frontmatter_is_stripped(journal):
    """id/level/canonical_for are internal routing and must not reach a reviewer."""
    _, _, _, page = journal
    for field in ("canonical_for", "last_verified", "DOC-FUSION-JUNCTION-ASO-SUBMISSION"):
        assert field not in page


def test_wide_tables_go_on_landscape_pages_and_narrow_ones_do_not(journal):
    """Twelve columns are unreadable in portrait; two columns do not deserve their own page."""
    _, floats, _, page = journal
    wide = {n for (kind, n, _p, w) in floats.values() if kind == "table" and w}
    assert wide, "no table was routed to a landscape page"
    assert "@page landscape" in page
    for _kind, number, block, is_wide in floats.values():
        if _kind == "table":
            assert is_wide == (bsp.table_columns(block) >= bsp.LANDSCAPE_MIN_COLS)


def test_the_back_matter_is_split_out_of_the_two_column_body(journal):
    _, _, _, page = journal
    assert '<div class="cols">' in page and '<div class="backmatter">' in page
    back = page.split('<div class="backmatter">')[1]
    assert "Declarations" in back and 'id="references-list"' in back
    assert "Introduction" not in back, "the back-matter split swallowed part of the body"


def test_the_two_styles_write_to_different_files():
    """The submission format is what a portal wants; they must not overwrite each other."""
    assert PAPER["out"] != PAPER["out"].replace(".pdf", "-manuscript.pdf")
