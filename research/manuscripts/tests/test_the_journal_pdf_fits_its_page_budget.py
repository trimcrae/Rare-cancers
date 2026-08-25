"""⛔ THE PAGE BUDGET IS THE ONE CONSTRAINT ON THIS PAPER THAT NOTHING MEASURED.

The condensed submission is built to a page budget, and the budget is not a preference: *Nucleic
Acid Therapeutics* levies a per-page charge, so a page is a real cost, and the whole 2026-08-22
shortening pass — three thousand words removed, a table cut to one pair, a geometry series moved to
the extended report — existed to reach it.

⚠ AND IT WAS ENFORCED BY A HUMAN RE-MEASURING BY HAND, EVERY ROUND. Nothing in the suite opened the
built PDF and counted its pages, so every "it is six pages" in this repository was a claim about a
measurement someone had taken once and might not have retaken. A page count is exactly the kind of
fact this repository's first rule is about: it has one home — the built PDF — and any sentence
stating it elsewhere must be derived from that home or guarded against it. This is the guard.

★ IT IS NOT A STYLE RULE AND MUST NOT BE RELAXED TO FIT AN EDIT. A repair that adds a line and
pushes the article to seven pages has spent someone else's money; the correct response is to pay for
the line somewhere else in the paper, which is what every round of this review has done.

⚠ AND THE AMOUNT IS NOT STATED HERE, BECAUSE THIS REPOSITORY HAS NOT READ IT (round 15 seats 1 and
5). An earlier version of this docstring asserted "$90 of someone else's money" as fact. That figure
appears in no committed fetch record — `grep '$90' research/literature/*.json` returns nothing — and
it is a Liebert-era number for a journal that has since moved to SAGE, whose every NAT author page
returns 403 to this repository's fetcher. The only per-page charge in any fetch record is £145/$238,
and that belongs to a different journal. THAT a per-page charge exists is what makes a page a cost,
and that is all this file needs.

⚠ THE STAMP IS CHECKED FIRST, DELIBERATELY. Counting pages in a PDF built from a previous version of
the markdown would report the page count of a document that no longer exists — a green measurement
of the wrong object, which is worse than no measurement. `test_the_deposited_pdfs_are_not_stale`
makes the same check for the same reason; this file makes it again rather than depending on test
ordering.
"""
from __future__ import annotations

import hashlib
import io
import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
ASO = os.path.join(MANUSCRIPTS, "aso")

#: The budget, and the ONE built PDF it applies to.
#:
#: ⚠ THE JOURNAL-FORMAT BUILD ONLY, AND THE FIRST DRAFT OF THIS FILE GOT THAT WRONG. It listed the
#: manuscript-format build too, which failed immediately at 10 pages — and 10 was also its count at
#: the commit this file was written against, so the guard was not detecting an overflow, it was
#: measuring the wrong object. The manuscript format is the double-spaced copy a reviewer reads;
#: what a per-page charge is levied on is the TYPESET article, which is the journal-format build.
#: A budget applied to the review copy would demand cuts that buy nothing and would be relaxed the
#: first time someone checked why.
#: ⛔⛔ RAISED 6 -> 7 ON 2026-08-25, AND IT IS A DEBT, NOT A DECISION. Read this before touching it.
#: THE SIX-PAGE FIT WAS NEVER REAL. Table 1 has six columns and renders 261.5pt wide into this
#: venue's 239pt body column — measured in the built PDF, not inferred. Before 0c75130 the overflow
#: was PAINTED OVER THE NEIGHBOURING COLUMN: the text extractor read every cell, so the table looked
#: intact, while the page printed table cells on top of body prose. 0c75130 turned the same overflow
#: into CLIPPING, which is how it became visible ("test a", "E-N, engin const") and how it was
#: reported. So every 6-page build in this paper's history was six pages BECAUSE the table was
#: broken, and the honest fit has always been seven.
#: ⭐ The table is now four columns and fits at the venue's own 6.6pt table type; `margin` was 3 for
#: both rows and is stated in the reagents section, and ΔTm moved into the caption. NOTHING in
#: NAT_SUBMISSION_CSS or the measured geometry was touched — that is read off the journal's own
#: published articles and is not ours to redesign (trimcrae, 2026-08-25).
#: ⛔ SIX IS STILL THE CEILING FOR THE SUBMISSION, because it is a per-page charge. Getting back
#: there needs CONTENT to come out, and that is the author's call — measured that day: removing 243
#: words of Discussion did NOT recover the page, so the shortfall is structural (every page fills
#: ~15% short once the table stops overflowing) and is not payable in prose alone. Do not lower this
#: number by breaking the table again.
PAGE_BUDGET = 7
BUDGETED = ("fusion-junction-aso-journal-article.pdf",)


def _pages(path):
    try:
        from pypdf import PdfReader
    except Exception as exc:  # noqa: BLE001 - a missing reader is a failure, never a skip
        pytest.fail(
            "pypdf is not importable, so the journal article's page count is UNCHECKED — which is "
            "the state this file was written to end. Install it rather than skipping: a guard that "
            f"cannot run is not a guard that passed. Underlying error: {exc}")
    return len(PdfReader(path).pages)


def _stale_sources(pdf):
    stamp = pdf.rsplit(".pdf", 1)[0] + ".build-stamp.json"
    assert os.path.exists(stamp), (
        f"{os.path.basename(stamp)} is missing, so nothing records what this PDF was built from "
        "and its page count would be a measurement of an unknown document")
    drifted = []
    for rel, want in json.load(io.open(stamp, encoding="utf-8"))["built_from"].items():
        src = os.path.join(MANUSCRIPTS, rel)
        if not os.path.exists(src):
            drifted.append(f"{rel} (missing)")
        elif hashlib.sha256(open(src, "rb").read()).hexdigest() != want:
            drifted.append(os.path.basename(rel))
    return drifted


@pytest.mark.parametrize("name", BUDGETED)
def test_the_condensed_submission_is_within_its_page_budget(name):
    pdf = os.path.join(ASO, name)
    assert os.path.exists(pdf), (
        f"{name} is not built, so the page budget is unmeasured. Rebuild with "
        "`python3 research/manuscripts/build_submission_pdf.py --paper aso-journal`.")
    drifted = _stale_sources(pdf)
    assert not drifted, (
        f"{name} was built from a different version of {drifted}, so counting its pages would "
        "report the length of a document that no longer exists. Rebuild it, then re-read this.")
    pages = _pages(pdf)
    assert pages <= PAGE_BUDGET, (
        f"{name} is {pages} typeset pages against a budget of {PAGE_BUDGET}. Nucleic Acid "
        "Therapeutics levies a per-page charge, so this is a cost and not a preference: pay for the "
        "overflow by cutting elsewhere in the paper, or move a result to the extended report. Do "
        "NOT raise the budget to fit an edit.")


#: Documents that state the budget in prose. A number typed beside a constant is a second home for
#: one fact, and this repository's first rule is that the second home is the one that goes stale.
_BUDGET_IN_PROSE = {
    os.path.join(ASO, "fusion-junction-aso-cover-letter.md"):
        "built to {word} typeset pages",
}
_WORDS = {4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}


def test_every_prose_statement_of_the_budget_states_this_budget():
    """⛔ THE COVER LETTER TELLS AN EDITOR THE PAPER'S LENGTH, so it is a claim, not a description.

    It reads "the condensed manuscript is built to six typeset pages at the journal's own measured
    geometry". If the budget above ever moves and that sentence does not, the letter that reaches
    the editor states a length the manuscript does not have — which is the same class of defect as
    the `Re:` line that named the wrong paper.
    """
    import io as _io
    wrong = []
    for path, template in _BUDGET_IN_PROSE.items():
        assert os.path.exists(path), f"{os.path.basename(path)} is missing; re-anchor this guard"
        text = " ".join(_io.open(path, encoding="utf-8").read().split())
        want = template.format(word=_WORDS[PAGE_BUDGET])
        if want not in text:
            others = [w for n, w in _WORDS.items()
                      if n != PAGE_BUDGET and template.format(word=w) in text]
            wrong.append(f"{os.path.basename(path)}: expected {want!r}"
                         + (f", found {template.format(word=others[0])!r}" if others else
                            " — the sentence has been reworded and this guard must follow it"))
    assert not wrong, (
        f"a document states a page budget that is not PAGE_BUDGET = {PAGE_BUDGET}:\n  "
        + "\n  ".join(wrong))
