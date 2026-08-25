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

import io
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
#: ⭐ EVERY SUBMISSION PDF, NOT ONE (2026-08-20). This guard was written for the preprint and named
#: a single path. When the condensed journal article was added it inherited the same builder, the
#: same stylesheet and therefore the same stranding defect, and no guard looked at it — the
#: shrinking-scope hole this repository keeps re-recording. A path is added here when a manuscript
#: becomes a submission text, on the same rule as `lint_style.TARGETS`.
#: ⛔ THE EXTENDED REPORT CAME OUT ON 2026-08-25 (trimcrae). Its build no longer exists.
DEPOSIT_PDFS = {
    "journal article": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-journal-article-manuscript.pdf"),
}

#: A page holding less than this is a stranded line, not a page.
MIN_CHARS = 300


def _page_texts(pdf_path):
    """(page number, extracted text) for every page of one deposit PDF.

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
    if not os.path.exists(pdf_path):
        pytest.fail(f"the deposit PDF is missing: {pdf_path}")
    pages = []
    for number, page in enumerate(extract_pages(pdf_path, laparams=LAParams()), start=1):
        text = "".join(el.get_text() for el in page if isinstance(el, LTTextContainer))
        pages.append((number, text.strip()))
    return pages


#: The section headings a NAT submission must start on a fresh page of its own. A short page that
#: OPENS with one of these is the format working, not a defect.
#:
#: ⛔⛔ WHY A LENGTH TEST ALONE STOPPED BEING ENOUGH (2026-08-25). Nucleic Acid Therapeutics requires
#: each major section to begin on a separate page, so `break-before: page` went on every h2 of the
#: manuscript build — and two REQUIRED pages immediately fell under the threshold: Keywords, which is
#: one line by nature, and Author Disclosure Statement, which is two. Both are correct. Relaxing
#: MIN_CHARS to admit them would have blinded the guard to the defect it exists for, which was still
#: present on the same build: two lines of the Methods tail alone on a page.
#:
#: ★ THE DISCRIMINATOR IS WHERE THE PAGE STARTS, NOT HOW MUCH IT HOLDS. A deliberately short section
#: opens with its own HEADING; a stranded line opens mid-sentence, in the middle of the paragraph it
#: was torn from. That is checkable, and it is the difference the length alone could never see.
SHORT_BY_DESIGN = (
    "Keywords",
    "Acknowledgments",
    #: Sage asks for this heading in its own right, after Acknowledgments; for a sole author it is
    #: one sentence. Added 2026-08-25 with the heading itself, not ahead of it.
    "Author Contributions",
    "Author Disclosure Statement",
    "Tables",
    "Figure legends",
)


def _opens_a_section(text):
    """Does this page BEGIN with a section heading? Then its shortness is the format, not a defect."""
    first = (text.lstrip().splitlines() or [""])[0].strip()
    return any(first == h or first.startswith(h) for h in SHORT_BY_DESIGN)


def _paper_for(label):
    """(this PDF's own `## ` headings, does its build force a page break before each one).

    ⚠ BOTH FACTS ARE READ OFF THE BUILDER AND THE MANUSCRIPT, NEVER LISTED HERE. `SHORT_BY_DESIGN`
    above is a deliberate hand-kept subset — the sections that are short in their own right — and
    it is the wrong set for the question below, which is "did a page break land here": that one is
    about EVERY section, including Discussion, and the paper's own headings are the only honest
    answer. A second list would go stale the next time the manuscript gains a section.
    """
    stem = DEPOSIT_PDFS[label][:-len("-manuscript.pdf")] + ".md"
    try:
        import sys
        sys.path.insert(0, MANUSCRIPTS)
        import build_submission_pdf as bsp
    except Exception:  # noqa: BLE001 — the builder has its own import gate
        return (), False
    for paper in bsp.PAPERS.values():
        if os.path.join(MANUSCRIPTS, paper.get("manuscript", "")) != stem:
            continue
        body = io.open(stem, encoding="utf-8").read() if os.path.exists(stem) else ""
        headings = tuple(re.sub(r"[*_`]", "", m.group(1)).strip()
                         for m in re.finditer(r"^##\s+(.+?)\s*$", body, re.M))
        return headings, bool((paper.get("layout") or {}).get("nat_submission"))
    return (), False


def _next_page_opens_a_section(pages, number, headings):
    """⛔ A SECTION'S LAST PAGE IS SHORT BY THE FORMAT, NOT BY A BADLY PLACED FLOAT (2026-08-25).

    Nucleic Acid Therapeutics requires each major section to begin on a separate page, so the
    submission build carries `break-before: page` on every h2. Under that rule the final page of
    any section whose prose does not happen to fill a whole page IS short, necessarily, and no
    amount of trimming removes it — shortening the section only changes WHICH words are left alone
    on it. `test_pdf_text_layer_is_orderable` measured exactly that on this manuscript: three
    successive trims of Materials and Methods moved its tail page from 318 to 293 to 260 characters
    and never emptied it. This is the same exemption, in the guard that measures the same build.

    ⚠ NARROW BY CONSTRUCTION. It applies only to a build that actually forces the break, and only
    to a page IMMEDIATELY FOLLOWED by one that opens a section. A short page in the MIDDLE of a
    section is still a failure, which is the defect this guard was written for; so is a short page
    in the preprint build, which carries no per-section break at all.
    """
    nxt = dict(pages).get(number + 1)
    if not nxt or not headings:
        return False
    first = (nxt.lstrip().splitlines() or [""])[0].strip()
    return any(first == h or first.startswith(h) for h in headings)


@pytest.mark.parametrize("label", sorted(DEPOSIT_PDFS))
def test_no_page_of_the_deposit_pdf_holds_only_a_stranded_line(label):
    pages = _page_texts(DEPOSIT_PDFS[label])
    assert pages, f"the {label} PDF has no pages"
    headings, forced_breaks = _paper_for(label)
    stranded = [(n, len(t)) for n, t in pages
                if len(t) < MIN_CHARS and not _opens_a_section(t)
                and not (forced_breaks and _next_page_opens_a_section(pages, n, headings))]
    if stranded:
        median = sorted(len(t) for _, t in pages)[len(pages) // 2]
        detail = "\n  ".join(
            f"page {n}: {c} characters — {dict(pages)[n][:90]!r}" for n, c in stranded)
        pytest.fail(
            f"{len(stranded)} page(s) of the {label} PDF carry less than {MIN_CHARS} characters "
            f"against a median of {median}:\n  {detail}\n\n"
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

    #: ⛔ WAS PAPERS["aso"] — the extended report, removed from the builder on 2026-08-25. The
    #: caption-footnote classing this measures is a property of `markdown_to_html`, not of that
    #: document, so it re-anchors to the ASO paper that still exists rather than being deleted.
    body, floats = builder.assemble(builder.PAPERS["aso-journal"], style="manuscript")
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


#: ⛔ TWO CAPTION-FOOTNOTE GUARDS WERE REMOVED 2026-08-25, AND THE COST IS REAL.
#: They measured that a caption's trailing note paragraphs get the `legend note` class so the
#: break rules reach them — the fix that closed a 110-character stranded page in 2026-08-19.
#: Only the extended report had captions shaped that way (an opener paragraph, then separate
#: note paragraphs); it left the gate, and the journal article writes each caption as ONE
#: paragraph, so the derivation found nothing to class and the second guard passed vacuously.
#: ⚠ A paper that reintroduces multi-paragraph captions is opting into untested classing.
#: Restore both from git history in the same change.