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

THE THRESHOLD. 300 characters, against a median near 4,300. The three legitimately short pages are a
section opener (~790), a sparse landscape table whose numerals extract thinly (~570), and the figure
legends preamble (~480) — all far above the cut, while the defect sat at 110. This is deliberately
NOT a fraction of the median: a stranded line is an absolute defect, and a paper that grew denser
should not raise the bar for what counts as an empty page.
"""
from __future__ import annotations

import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
DEPOSIT_PDF = os.path.join(MANUSCRIPTS, "aso",
                           "fusion-junction-aso-research-article-manuscript.pdf")

#: A page holding less than this is a stranded line, not a page.
MIN_CHARS = 300


def _page_texts():
    try:
        from pypdf import PdfReader
    except ImportError:                                     # pragma: no cover - env dependent
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            pytest.skip("neither pypdf nor PyPDF2 is installed in this sandbox")
    if not os.path.exists(DEPOSIT_PDF):
        pytest.fail(f"the deposit PDF is missing: {DEPOSIT_PDF}")
    return [(n + 1, (p.extract_text() or "").strip())
            for n, p in enumerate(PdfReader(DEPOSIT_PDF).pages)]


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


def test_the_caption_footnotes_are_classed_so_their_break_rules_can_reach_them():
    """The guard behind the guard: the CSS is only live if the class is actually emitted.

    Both refuted fixes above failed silently because a rule was written for a class no element
    carried. This asserts the element side of that join, in the built HTML, so a future refactor
    that stops classing caption footnotes fails here with a clear reason rather than surfacing
    later as a stray page.
    """
    import sys
    if MANUSCRIPTS not in sys.path:
        sys.path.insert(0, MANUSCRIPTS)
    import build_submission_pdf as builder

    body, floats = builder.assemble(builder.PAPERS["aso"], style="manuscript")
    html = builder.markdown_to_html(body, floats)
    assert 'class="legend note"' in html, (
        "no caption footnote carries `legend note` in the built HTML, so the rule that keeps a "
        "caption block on one page reaches nothing. Check that markdown_to_html still tracks the "
        "caption span from the '**Table n.' opener to the first pipe row.")
