"""The preprint deposition's metadata is read out of the manuscript, and reads correctly.

⛔ WHY THIS IS GATED. `scripts/zenodo_preprint.py` mints a DOI whose landing page carries a title,
an abstract and a keyword list. Those are read from the manuscript rather than typed, which is the
right design and moves the risk: a pattern that reads the WRONG span produces a plausible record
under a permanent identifier, and a published Zenodo version cannot be edited.

⛔⛔ THE FAILURE THIS FILE EXISTS FOR ALREADY HAPPENED, on the script's first run. The keyword
pattern `(.+?)(?=\\s*$|\\n\\n)` was applied to whitespace-COLLAPSED text, where there is no `\\n\\n`
to stop at and `\\s*$` matches at the end of the string — so the lazy quantifier ran to the end of
the document and produced 35 "keywords", the first seven real and the remainder the entire paper
from §1 to the reference list. It was caught by `--build-only` printing the values.

★ AND A FLOOR ALONE WOULD HAVE PASSED IT. The script already required at least 4 keywords, which is
the venue's rule, and 35 clears that comfortably. Over-matching and under-matching are different
failures and need bounds in both directions; that is the property asserted below, not a style
preference about how many keywords a paper should have.
"""
from __future__ import annotations

import io
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))

#: ⛔ A PLAIN IMPORT, NOT `importorskip`. `test_no_guard_can_silently_not_run.py` rejected the
#: first version of this line and was right to: an importorskip on a module that stops importing is
#: a PERMANENT SKIP, and this whole file would then vouch for a deposition script nothing had run.
#: `zenodo_preprint` is repository code with no third-party dependency, so an ImportError here is a
#: broken script rather than a missing package, and failing loudly is the correct response.
import zenodo_preprint as zp  # noqa: E402

ARTICLE = os.path.join(REPO, "research", "manuscripts", zp.PAPER["manuscript"])


@pytest.fixture(scope="module")
def meta():
    return zp.metadata()


def test_the_title_is_the_manuscripts_own_h1(meta):
    """One home for the title. A record whose title has drifted names a different paper."""
    h1 = re.sub(r"[*_`]", "", re.search(r"^#\s+(.+)$", io.open(ARTICLE, encoding="utf-8").read(),
                                        re.M).group(1)).strip()
    assert meta["title"] == h1, (
        f"the deposition title and the manuscript's H1 disagree:\n  record: {meta['title']!r}\n"
        f"  paper : {h1!r}")


def test_the_keyword_list_is_bounded_in_both_directions(meta):
    """⛔ A CEILING AS WELL AS A FLOOR — see this module's docstring."""
    kw = meta["keywords"]
    assert 4 <= len(kw) <= 15, (
        f"{len(kw)} keyword(s). Under 4 fails the venue's rule; over 15 is a pattern that has "
        "escaped its paragraph, which is the failure that actually occurred.")
    long = [k for k in kw if len(k) > 80]
    assert not long, (
        f"{len(long)} keyword(s) run past 80 characters, so the pattern is matching prose: "
        f"{[k[:60] + '…' for k in long]}")
    assert not any("#" in k or "**" in k for k in kw), (
        f"a keyword carries markdown, so the match crossed a heading: {kw}")


def test_the_description_carries_the_abstract_and_the_handling_notice(meta):
    """⛔ THE LANDING PAGE IS READ BY PEOPLE WHO WILL NEVER OPEN THE PDF.

    CLAUDE.md's language discipline is not suspended by the medium: whatever states the work in
    public states its limits with it. The no-administration notice is the one sentence that must
    survive every rendering of this paper.
    """
    d = meta["description"]
    assert "ultra-rare sarcoma" in d, "the abstract is not in the description"
    assert "not for administration to any person or animal" in d, (
        "the deposition description drops the research-use-only notice. It appears on the landing "
        "page, which is what a reader sees before deciding whether to open anything.")
    assert "does not supersede" in d, (
        "the description no longer says this paper does not supersede the extended report. That "
        "sentence is why this is a separate record rather than a new version of the archive.")


def test_it_points_at_the_archive_the_paper_actually_cites(meta):
    """The related identifier and the paper's Data availability must name one DOI, not two."""
    dois = [r["identifier"] for r in meta["related_identifiers"] if r["scheme"] == "doi"]
    assert len(dois) == 1, f"expected exactly one related DOI, got {dois}"
    assert dois[0] in io.open(ARTICLE, encoding="utf-8").read(), (
        f"the record points at {dois[0]}, which the manuscript does not cite. A reader following "
        "the link would arrive somewhere the paper never sent them.")


def test_it_is_a_preprint_record_and_not_a_dataset(meta):
    """⛔ THE TYPE IS THE WHOLE POINT: a journal asks for a preprint DOI, not a dataset's."""
    assert meta["upload_type"] == "publication" and meta["publication_type"] == "preprint", (
        f"this record would be deposited as {meta['upload_type']}/"
        f"{meta.get('publication_type')}, which is not what Nucleic Acid Therapeutics' "
        "'enter the preprint DOI' field is asking for.")
