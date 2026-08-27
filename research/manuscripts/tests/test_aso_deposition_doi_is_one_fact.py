"""The archive DOI is printed twice in the article and must be the manifest's, both times.

⛔ WHY A TEST AND NOT `pinned-figures.json`. The manifest's own `how_to_deposit_and_mint_the_doi`
step 6 says to "register the DOI in research/manuscripts/pinned-figures.json so the consistency
linter holds the two copies together". It cannot: `lint_consistency.py` reads every
`artifact_figures` entry through `float(...)`, so that registry holds NUMBERS, and an attempt to pin
a DOI there fails with `A-key-missing ... (ValueError)` — a message that names the wrong cause and
would have sent the next reader looking for a missing key that is present. The instruction was
written before anyone tried it. The need behind it is real and is met here instead.

⚠ THE HAZARD IS SPECIFIC. A DOI that differs between two lines of one paper does not fail loudly;
it resolves, from one of those lines, to somebody else's Zenodo record. That is worse than a dead
link, and neither the claim linter nor the citation linter can see it — claim STRENGTH and citation
PROVENANCE are both orthogonal to whether two transcriptions of one identifier agree.
"""
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ASO = os.path.join(os.path.dirname(HERE), "aso")
MANIFEST = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")
#: ⛔ THE FIFTH GUARD SCOPED TO ONE OF A PAIR (round 11). Four sibling instruments were widened in
#: rounds 9 and 10 after each was found reporting on both submission documents while reading one.
#: This one bound ARTICLE to the extended report alone, so the journal article's Zenodo DOI — which
#: it prints in Data availability and which a depositor follows — was asserted by nothing, while the
#: manifest's own deposit step claims to "hold the two copies together".
ARTICLES = [
    os.path.join(ASO, "fusion-junction-aso-research-article.md"),
    os.path.join(ASO, "fusion-junction-aso-journal-article.md"),
]

#: ⛔⛔ AND THE WIDENING WAS ONE OF A PAIR OF ITS OWN (round 10's audit, item MISCOVERED D). The list
#: above was added for `test_the_article_prints_the_manifests_doi_and_prints_only_that_one`; the
#: other two functions kept reading `ARTICLE = ARTICLES[0]`, the extended report, so the fix for the
#: one-of-a-pair class landed as one of a pair. Measured: an unresolvable
#: `[ARCHIVE DOI — PLACEHOLDER: this citation does not resolve]` shipped in the JOURNAL article's
#: Methods with this module reporting `3 passed`.
#: ★ NO MODULE-LEVEL `ARTICLE` SURVIVES ON PURPOSE. A single-document default is what silently
#: re-scopes a function to one paper the next time somebody adds one; every function here is
#: parametrized over `ARTICLES`, so a third document is covered by adding one path.

#: Every DOI the article prints in the Zenodo prefix. The deposit's own is the only one there is;
#: a reference-list DOI is a publisher's and carries a different prefix.
ZENODO_DOI = re.compile(r"10\.5281/zenodo\.\d+")

#: A bolded statement whose own heading says "availability", and the text under it. The heading
#: wording differs between the two papers and is the venue's to set, so the SUBJECT is what this
#: matches rather than any of the three spellings in use today.
_AVAILABILITY_HEADING = re.compile(r"\*\*([^*\n]*availability[^*\n]*)\*\*", re.I)


def _availability_statements(article):
    """Every availability statement in one document, as (heading, body-of-that-statement).

    The statement runs to the next bolded run-in heading or the next section heading, whichever
    comes first — the same paragraph a reader following "Data availability" would read.
    """
    out = []
    for m in _AVAILABILITY_HEADING.finditer(article):
        rest = article[m.end():]
        stop = len(rest)
        for terminator in (re.search(r"\n\s*\*\*", rest), re.search(r"\n#{1,6}\s", rest)):
            if terminator:
                stop = min(stop, terminator.start())
        out.append((m.group(1).strip(), rest[:stop]))
    return out


def test_the_article_prints_the_manifests_doi_and_prints_only_that_one():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    declared = manifest.get("deposition_doi")
    assert declared, ("the archive manifest carries no `deposition_doi`. It is the one place the "
                      "deposit's identifier lives; the article transcribes it from there.")

    for path in ARTICLES:
        article = open(path, encoding="utf-8").read()
        found = set(ZENODO_DOI.findall(article))
        name = os.path.basename(path)
        assert found, (f"{name} prints no Zenodo DOI. Every [ARCHIVE DOI] placeholder was to be "
                       f"replaced with {declared}.")
        assert found == {declared}, (
            f"{name} prints {sorted(found)} and the manifest declares {declared}. A DOI that "
            "differs between two lines of one paper still RESOLVES from both — to two different "
            "records — so this cannot be caught by reading the page.")


@pytest.mark.parametrize("path", ARTICLES, ids=[os.path.basename(p) for p in ARTICLES])
def test_no_archive_doi_placeholder_survives_in_the_article(path):
    article = open(path, encoding="utf-8").read()
    assert "ARCHIVE DOI" not in article, (
        f"an [ARCHIVE DOI — PLACEHOLDER] block is still in {os.path.basename(path)}. The "
        "placeholder says in terms that the citation does not resolve; shipping it is shipping "
        "that sentence.")


@pytest.mark.parametrize("path", ARTICLES, ids=[os.path.basename(p) for p in ARTICLES])
def test_both_availability_statements_carry_it(path):
    """Two statements, two audiences: Methods for a reader reproducing, Declarations for a screener.

    ⚠ COUNTED, NOT SEARCHED-ONCE. The two are written independently and an edit has already dropped
    one of them once in this paper's history; a test that only asserts "the DOI appears" passes on
    a paper that lost one of its two availability statements.
    """
    article = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    assert len(ZENODO_DOI.findall(article)) >= 2, (
        f"the deposit DOI appears fewer than twice in {name}. Methods -> Availability and "
        "Declarations -> Data and code availability each carry it.")
    #: ⛔ AND THE COUNT ALONE IS WEAKER THAN IT LOOKS, WHICH IS WHY THE PREDICATE BELOW IS HERE.
    #: The DOI is printed as a markdown link, `[doi:10.5281/zenodo.N](https://doi.org/10.5281/
    #: zenodo.N)`, so ONE statement already yields two matches — the journal article reaches the
    #: count above with a single availability statement. What is asserted here instead is a
    #: property that extends itself: EVERY bolded statement whose heading says "availability" must
    #: carry the deposit identifier. The two papers head theirs differently ("Availability.",
    #: "Data and code availability.", "Data availability.") and a named list of headings is the
    #: thing somebody must remember to extend.
    for heading, block in _availability_statements(article):
        assert ZENODO_DOI.search(block), (
            f"{name}'s '{heading}' statement names no deposit DOI. An availability statement "
            "without the identifier sends a reader to a deposit they cannot find, and the other "
            "statement's copy does not help them — they are reading this one.")
