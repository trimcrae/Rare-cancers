"""A list item is one string of markdown, however many source lines it is wrapped across.

⛔ THE DEFECT THIS PINS, MEASURED IN A SHIPPED DEPOSIT (2026-09-08, by rasterising pages of
`nr4a3-fusion-transcriptional-output.pdf` and `-manuscript.pdf`). `markdown_to_html`'s list branch
rendered the marker line with `inline()` and then called `inline()` AGAIN on each continuation
line, splicing the second result into the `<li>` the first had already closed. `inline()` is a
whole-string parser — its emphasis rules carry `re.S` exactly so a span may cross a line break — so
every span that wrapped became unclosable and its markup PRINTED. Nine bold pairs leaked across the
two formats, including §4.2's "**It is not specific to EMC, to this gene set, or to these three
cohorts**" and "**The surviving gene is the pre-designated positive control**".

⚠ BOLD IS ONLY WHERE IT WAS VISIBLE. A wrapped link, a wrapped code span and a backslash escape
whose partner sat on the next line took the same path, so this test exercises all four rather than
the one that happened to be noticed.

★ WHAT THIS ASSERTS: markup that wraps inside an item is rendered; an item that does not wrap is
rendered exactly as an unwrapped item always was; and the continuation line is still JOINED with a
single space, so no word is fused to the next.
"""
from __future__ import annotations

import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDER = os.path.join(os.path.abspath(os.path.join(HERE, "..")), "build_submission_pdf.py")


def _builder():
    spec = importlib.util.spec_from_file_location("build_submission_pdf", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bold_that_wraps_inside_a_list_item_is_rendered_not_printed():
    html = _builder().markdown_to_html(
        "- A leading clause. **It is not specific to EMC, to this\n"
        "  gene set, or to these three cohorts**: the rest of the item.\n")
    assert "**" not in html, html
    assert "<strong>It is not specific to EMC, to this gene set, or to these three " \
           "cohorts</strong>" in html, html


def test_italic_link_code_and_escape_all_survive_the_wrap():
    module = _builder()
    html = module.markdown_to_html(
        "- *ENO3 carries 2-4 peaks in every deep\n"
        "  experiment* and see [the acinic cell\n"
        "  deposit](https://example.org/x) and `a_long\n"
        "  _name` and HLA-B\\*15:01 versus HLA-A\\\n"
        "  *01:01.\n")
    assert "<em>ENO3 carries 2-4 peaks in every deep experiment</em>" in html, html
    assert '<a href="https://example.org/x">the acinic cell deposit</a>' in html, html
    assert "`" not in html, html
    #: The escaped asterisks must still be literal characters, never emphasis, after the join.
    assert "<em>" in html and html.count("<em>") == 1, html


def test_an_item_that_does_not_wrap_is_unchanged_and_the_join_is_one_space():
    module = _builder()
    assert module.markdown_to_html("- **Whole item on one line.** Tail.\n") == \
        "<ul>\n<li><strong>Whole item on one line.</strong> Tail.</li>\n</ul>"
    wrapped = module.markdown_to_html("- first\n  second\n")
    assert "<li>first second</li>" in wrapped, wrapped


def test_a_second_item_is_still_its_own_li():
    html = _builder().markdown_to_html(
        "- one **wrapping\n  bold** here\n- two **also\n  wrapping** here\n")
    assert html.count("<li>") == 2, html
    assert html.count("<strong>") == 2, html
    assert "**" not in html, html
