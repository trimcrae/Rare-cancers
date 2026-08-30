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
PAGE_BUDGET = 6
BUDGETED = ("fusion-junction-aso-journal-article.pdf",)

#: ⛔⛔ A DECLARED OVERAGE, AND IT IS NOT A RAISED BUDGET. `PAGE_BUDGET` is untouched at 6 and stays
#: the number a submission must meet. What this records is that the paper is knowingly over it right
#: now, why, on whose authority, and what closes it.
#:
#: ⚠ THE DISTINCTION IS THE WHOLE POINT, because raising the budget to fit an edit is the
#: self-serving move this file's docstring forbids and `amendment_guard` exists to catch. A raised
#: budget is silent: it makes the overflow disappear and nothing ever asks for it back. A DECLARED
#: overage is loud in three directions at once — the count must be EXACT (a further page fails), an
#: UNDECLARED overage still fails exactly as before, and once the paper is back within budget this
#: block must be DELETED or the test fails on its own staleness. It cannot rot into a higher ceiling.
#:
#: ★ trimcrae, 2026-08-30, in session, verbatim: "The 6 page limit is a hard requirement for
#: submission to NAT but there's going to be at least one more round here. So be very strict about
#: adding things that don't need to be added and avoid reviewer response bloat but we don't need to
#: strictly limit v2 just for the sake of v2 being 6 pages." The v2 PREPRINT goes to Qeios, which
#: caps nothing; the 6-page limit binds at the NAT submission, which is not what is being prepared.
DECLARED_OVERAGE = {
    "pages": 7,
    "reason": "Round 22's hostile referee found that *FUS* supplies 8 of the 38 junctions the panel "
              "models and is never introduced as an EMC fusion partner in the condensed article. "
              "Introducing it needs a citation, and the 24th reference is a four-line block that "
              "will not split across a column — that block, not the sentence, is the page. Measured "
              "both ways: 6 pages without the FUS clause and its reference, 7 with.",
    "already_paid": "~80 words were cut to fund it and bought one line: a duplicated Acknowledgments "
                    "sentence, a Disclosure sentence that restated the one after it, a Discussion "
                    "restatement of the Introduction's novelty point, and two sentences about the "
                    "same convention merged. The remaining candidates are evidence and caveats.",
    "authorised_by": "trimcrae, 2026-08-30 (quoted above)",
    "closes_when": "The NAT submission is prepared. At that point the paper must reach 6 pages "
                   "again — by cutting, or by trimcrae accepting the per-page charge — and THIS "
                   "BLOCK MUST BE DELETED. It is not a licence to spend further pages: anything "
                   "that would make it 8 fails here.",
}


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
    if pages <= PAGE_BUDGET:
        # ⛔ AND THE DECLARATION MUST NOT OUTLIVE THE OVERAGE IT DECLARES. A stale block would sit
        # there reading as permission for a page nobody is spending, and the next edit that costs
        # one would pass unnoticed. Deleting it is part of getting back under budget.
        assert DECLARED_OVERAGE is None, (
            f"{name} is {pages} pages, within the budget of {PAGE_BUDGET}, and DECLARED_OVERAGE is "
            "still set. Delete that block: an overage declaration for an overage that no longer "
            "exists is a raised ceiling wearing a receipt.")
        return
    assert DECLARED_OVERAGE is not None, (
        f"{name} is {pages} typeset pages against a budget of {PAGE_BUDGET}. Nucleic Acid "
        "Therapeutics levies a per-page charge, so this is a cost and not a preference: pay for the "
        "overflow by cutting elsewhere in the paper, or move a result to the extended report. Do "
        "NOT raise the budget to fit an edit. If the overage is deliberate and authorised, declare "
        "it in DECLARED_OVERAGE with its exact page count, its reason and who authorised it.")
    assert pages == DECLARED_OVERAGE["pages"], (
        f"{name} is {pages} pages and DECLARED_OVERAGE names {DECLARED_OVERAGE['pages']}. A "
        "declaration authorises ONE known overage, not a direction of travel — re-measure, and if "
        "the extra page is warranted get it authorised rather than widening the number here.")
