"""The captured Nucleic Acid Therapeutics guidelines still hash to the digest they carry.

⛔ WHY A DIGEST, AND WHY IT NEEDS A GUARD. This repository cannot fetch the journal's Submission
Guidelines: `journals.sagepub.com` returns HTTP 403 to the egress proxy, to a plain CI fetch and to
a real headless Chromium alike. The page was therefore read by a PERSON and pasted in, and the
capture is the source of record for every NAT figure stated anywhere here — the word and abstract
caps graded in `submission-metrics.json`, the per-page fee, the preprint policy, the reference style,
the Statements-and-Declarations template, the article type on the built PDFs' masthead.

★ A "verbatim capture" is a provenance claim, and CLAUDE.md §4 is explicit that presence is never
evidence of provenance. The digest in the file makes the claim checkable; this makes it CHECKED.
⚠ A STALE DIGEST ON A "VERBATIM" RECORD IS WORSE THAN NO DIGEST — it is a correct-looking assurance
over text somebody edited, which is the shape of every fail-quiet defect in this repository. So an
edit to the capture must either be accompanied by a new digest (a fresh read of the page, dated) or
fail here.

⛔ AND THE CAPTURE IS NOT EDITED TO FIX THIS TEST. If the two disagree, the capture is wrong: restore
it, or re-read the page in a browser and replace BOTH the text and the digest with the new reading's,
moving the file to a new dated name. The date in the filename is the warranty.
"""
from __future__ import annotations

import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CAPTURE = os.path.join(REPO, "research", "literature",
                       "nat-submission-guidelines-2026-08-23.md")

#: Phrases the rest of the repository quotes from this page. Each is cited somewhere as the reason
#: a manuscript is shaped the way it is, so its ABSENCE would silently strand that reasoning.
QUOTED = [
    "4,000-word limit",
    "Unstructured abstract of no more than 200 words",
    "Maximum total of five (5) figures and/or tables",
    "Accepts preprints? Yes",
    "The preferred format for your manuscript is Word",
    "The journal follows the Sage Vancouver reference style",
    "a minimum of 4 keywords, listed after the abstract",
    "Statements and Declarations",
    "$90/page",
]


def _text():
    assert os.path.exists(CAPTURE), (
        f"{os.path.relpath(CAPTURE, REPO)} is missing, and it is the source of record for every "
        "Nucleic Acid Therapeutics limit this repository states. Without it those limits are "
        "recollections.")
    return io.open(CAPTURE, encoding="utf-8").read()


def test_the_capture_hashes_to_the_digest_it_declares():
    text = _text()
    claimed = re.search(r"sha256 of the capture below:\*\* `([0-9a-f]{64})`", text)
    assert claimed, "the capture declares no sha256, so nothing can tell whether it was edited"
    fenced = re.search(r"```text\n(.*?)\n```\s*$", text, re.S)
    assert fenced, "the verbatim block is gone; the file is no longer a capture"
    got = hashlib.sha256(fenced.group(1).encode("utf-8")).hexdigest()
    assert got == claimed.group(1), (
        "the captured guidelines no longer hash to the digest recorded beside them:\n"
        f"  declared {claimed.group(1)}\n  actual   {got}\n"
        "Somebody edited a document that says of itself that it is verbatim. Restore it from git, "
        "or replace it with a fresh dated read of the page and its own digest.")


def test_every_phrase_the_repository_quotes_is_in_the_capture():
    """⛔ A QUOTE WITH NO SOURCE IS A RECOLLECTION WEARING A CITATION.

    Each string below is quoted elsewhere — in `submission_metrics.py`'s NAT row, in the preprint
    checklist, in the .docx builder — as the reason something is the way it is. If the capture stops
    containing one, the quote that cites it has become unsourced, and CLAUDE.md §7 forbids exactly
    that.
    """
    text = _text()
    missing = [q for q in QUOTED if q not in text]
    assert not missing, (
        f"{len(missing)} phrase(s) this repository quotes are not in the capture: {missing}. "
        "Either the capture was replaced by a newer read that words them differently — in which "
        "case update every place that quotes them — or a quote was written from memory.")
