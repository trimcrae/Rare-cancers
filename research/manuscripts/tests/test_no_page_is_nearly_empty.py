"""No page of the deposit PDF may carry a single stranded line.

⛔ WHY. A blind screen of the deposit PDF on 2026-08-19 found manuscript page 42 holding one line —
"reagent's own loci are neither cleaner nor dirtier for being its own." — and nothing else: 110
characters against a median page of 4,235, with Table 6, the table that line's caption describes, not
starting until page 43. The reader met a caption, then a near-blank page, then the table.

⛔⛔ AND A FIX FOR THIS EXACT PAGE HAD ALREADY BEEN WRITTEN, THAT MORNING, AND DID NOTHING. The CSS
carried a comment naming the orphaned sentence and the 110-character count, adding
`orphans: 3; widows: 3` to `p.legend` as the remedy. It could not have worked: only the paragraph
matching "**Table n." was ever given the `legend` class, so every caption FOOTNOTE — including the
one that orphaned — rendered as a bare `<p>` the rule never reached. The comment described the
symptom accurately and the fix missed the element entirely, and nothing measured the result.

★ THE REAL CAUSE, IN THREE MEASUREMENTS, because two plausible fixes were tried and refuted first:
  1. give the footnote the `legend` class  -> page 42 still 110 chars. Chromium's print path does
     not honour `widows`/`orphans` inside a box it has already abandoned for `break-inside: avoid`,
     so no widow rule of any strength could have fixed this.
  2. tighten `p.legend.note` margins       -> page 42 still 110 chars, because the class was still
     not being applied: MANUSCRIPT style never calls `render_float` at all. `assemble` returns an
     empty float map and splices tables straight into the body, so the flag keyed to the float path
     was False for every table in the deposit artefact.
  3. track the caption span in `markdown_to_html` itself, from the "**Table n." opener to the first
     pipe row, and set the notes tighter -> 9 footnotes classed, page 42 gone, document 58 -> 57
     pages, no page under 400 characters.

⚠ SO THIS TEST MEASURES THE PDF, NOT THE CSS. Every fix above looked correct in the stylesheet; two
of the three changed nothing in the artefact. The only honest check is the rendered page.

⛔⛔ AND IT MEASURED NOTHING IN CI UNTIL 2026-08-19, for the same reason its sibling
`test_justification_does_not_degrade` did: the extractor was `pypdf`, which
`.github/workflows/tests.yml` does not install (`pytest numpy scipy pymbar rdkit pyyaml boto3
jsonschema biopython pdfminer.six`). Every CI run took `pytest.skip("neither pypdf nor PyPDF2 is
installed in this sandbox")`. A guard written after a blind screen found a 110-character page, and
never once run by the machine that gates the commits. The extractor is now `pdfminer.six`, which CI
does install, and a missing import fails rather than skipping.

THE THRESHOLD. 300 characters, against a median near 4,300 (pdfminer reads this build at a median
of 4,754 and a minimum of 612). The three legitimately short pages are a
section opener (~790), a sparse landscape table whose numerals extract thinly (~570), and the figure
legends preamble (~480) — all far above the cut, while the defect sat at 110. This is deliberately
NOT a fraction of the median: a stranded line is an absolute defect, and a paper that grew denser
should not raise the bar for what counts as an empty page.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
DEPOSIT_PDF = os.path.join(MANUSCRIPTS, "aso",
                           "fusion-junction-aso-research-article-manuscript.pdf")

#: A page holding less than this is a stranded line, not a page.
MIN_CHARS = 300


def _page_texts():
    """(page number, extracted text) for every page of the deposit PDF.

    ⛔ NOT A SKIP IF THE PARSER IS MISSING — see the docstring. `pdfminer.six` is on this
    repository's CI install line so that PDF guards can actually run there.
    """
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LAParams, LTTextContainer
    except ImportError as exc:                              # pragma: no cover - env dependent
        pytest.fail(
            f"pdfminer.six is not importable ({exc}), so no page of the deposit PDF was measured. "
            "CI installs it on purpose. Install it rather than restoring a skip — this guard was "
            "written for a defect a human found by eye, and it has never caught one itself.")
    if not os.path.exists(DEPOSIT_PDF):
        pytest.fail(f"the deposit PDF is missing: {DEPOSIT_PDF}")
    pages = []
    for number, page in enumerate(extract_pages(DEPOSIT_PDF, laparams=LAParams()), start=1):
        text = "".join(el.get_text() for el in page if isinstance(el, LTTextContainer))
        pages.append((number, text.strip()))
    return pages


def test_no_page_of_the_deposit_pdf_holds_only_a_stranded_line():
    pages = _page_texts()
    assert pages, "the deposit PDF has no pages"
    stranded = [(n, len(t)) for n, t in pages if len(t) < MIN_CHARS]
    if stranded:
        median = sorted(len(t) for _, t in pages)[len(pages) // 2]
        detail = "\n  ".join(
            f"page {n}: {c} characters — {dict(pages)[n][:90]!r}" for n, c in stranded)
        pytest.fail(
            f"{len(stranded)} page(s) carry less than {MIN_CHARS} characters against a median of "
            f"{median}:\n  {detail}\n\n"
            "A caption block that overflows its page by a line or two strands that line, and the "
            "display item it describes is then pushed a further page away. Fix it by making the "
            "block FIT — tighten the caption-footnote margins in build_submission_pdf.py — not by "
            "adding a widow rule: Chromium's print path ignores widows/orphans inside a box it has "
            "already given up on for `break-inside: avoid`, which is why the first two attempts at "
            "this defect changed nothing measurable.")


#: A paragraph that opens a display item's caption block. The pipe row, heading, panel or float
#: token that ends the block is `_CAPTION_BLOCK_ENDS`.
_CAPTION_OPENER = re.compile(r"^\*\*(?:Supplementary )?(?:Table|Figure) (?:S?\d+)\.")
_CAPTION_BLOCK_ENDS = re.compile(r"^(?:\||#{1,6}\s|<svg|<figure|@@FLOAT|-{3,}$)")


def _built_manuscript():
    import sys
    if MANUSCRIPTS not in sys.path:
        sys.path.insert(0, MANUSCRIPTS)
    import build_submission_pdf as builder

    body, floats = builder.assemble(builder.PAPERS["aso"], style="manuscript")
    return body, builder.markdown_to_html(body, floats)


def _caption_footnote_paragraphs(body):
    """Every paragraph of the assembled markdown that sits inside a caption block below its opener.

    Derived from the source the builder is about to render, so the expectation moves when a table
    gains or loses a footnote. ⚠ This is the count the CSS class has to reach; it is NOT read back
    out of the builder, because the defect being guarded was a rule and an element disagreeing.
    """
    found, in_caption = [], False
    for para in re.split(r"\n\s*\n", body):
        first = para.strip().split("\n", 1)[0].strip()
        if not first:
            continue
        if _CAPTION_BLOCK_ENDS.match(first):
            in_caption = False
            continue
        if _CAPTION_OPENER.match(first):
            in_caption = True
            continue
        if in_caption:
            found.append(" ".join(para.split())[:80])
    return found


def test_the_caption_footnotes_are_classed_so_their_break_rules_can_reach_them():
    """The guard behind the guard: the CSS is only live if the class is actually emitted.

    Both refuted fixes above failed silently because a rule was written for a class no element
    carried. This asserts the element side of that join, in the built HTML, so a future refactor
    that stops classing caption footnotes fails here with a clear reason rather than surfacing
    later as a stray page.

    ⛔ IT USED TO ASSERT `'class="legend note"' in html` — ONE OCCURRENCE, WHERE THE DOCUMENTED FIX
    CLASSED NINE. Eight of the nine could have fallen back to a bare `<p>` and the assertion would
    still have read green, which is the same shape of hole as the rule that reached no element:
    something is classed, so the join "works". The expectation is now the number of caption
    footnotes the assembled manuscript actually carries, derived at run time.
    """
    body, html = _built_manuscript()
    expected = _caption_footnote_paragraphs(body)
    assert expected, (
        "the assembled manuscript carries no caption footnote at all — either every table caption "
        "lost its notes or this derivation has stopped matching the source, and either way the "
        "count below would be asserting nothing")
    classed = html.count('class="legend note"')
    assert classed == len(expected), (
        f"{classed} paragraph(s) carry `legend note` in the built HTML against {len(expected)} "
        f"caption footnote(s) in the assembled markdown. Every note under a caption must keep the "
        "class, or the break rule that holds a caption block on one page reaches only part of it "
        "and the rest orphans:\n  " + "\n  ".join(expected))


def test_no_caption_footnote_falls_through_to_a_bare_paragraph():
    """The same join asserted on the RENDERED structure rather than on a count.

    A count can be satisfied by classing the wrong paragraphs. What the defect actually was is a
    bare `<p>` sitting between a table's caption and its grid, so that is what is checked: between
    each caption opener and the table it introduces, every paragraph must carry a legend class.
    """
    _, html = _built_manuscript()
    openers = [m.start() for m in re.finditer(r'<p class="legend caption">', html)]
    assert openers, "no table caption is classed at all in the built HTML"
    offenders = []
    for start in openers:
        grid = html.find('<div class="tablewrap">', start)
        block = html[start:grid if grid != -1 else len(html)]
        for m in re.finditer(r"<p(?![^>]*class=)[^>]*>(.{0,70})", block):
            offenders.append(m.group(1))
    assert not offenders, (
        f"{len(offenders)} paragraph(s) between a table caption and its grid render as bare <p> "
        "and so carry no break rule at all:\n  " + "\n  ".join(offenders[:6])
        + "\n\nThis is the exact element/rule mismatch that stranded manuscript page 42: the CSS "
          "named `p.legend`, the orphaned footnote was a bare `<p>`, and the stylesheet looked "
          "correct.")
