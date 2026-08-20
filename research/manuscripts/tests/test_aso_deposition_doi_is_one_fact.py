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

HERE = os.path.dirname(os.path.abspath(__file__))
ASO = os.path.join(os.path.dirname(HERE), "aso")
MANIFEST = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-research-article.md")

#: Every DOI the article prints in the Zenodo prefix. The deposit's own is the only one there is;
#: a reference-list DOI is a publisher's and carries a different prefix.
ZENODO_DOI = re.compile(r"10\.5281/zenodo\.\d+")


def test_the_article_prints_the_manifests_doi_and_prints_only_that_one():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    declared = manifest.get("deposition_doi")
    assert declared, ("the archive manifest carries no `deposition_doi`. It is the one place the "
                      "deposit's identifier lives; the article transcribes it from there.")

    article = open(ARTICLE, encoding="utf-8").read()
    found = set(ZENODO_DOI.findall(article))
    assert found, ("the article prints no Zenodo DOI. Both [ARCHIVE DOI] placeholders were to be "
                   f"replaced with {declared} — Methods -> Availability, and Declarations -> Data "
                   "and code availability.")
    assert found == {declared}, (
        f"the article prints {sorted(found)} and the manifest declares {declared}. A DOI that "
        "differs between two lines of one paper still RESOLVES from both — to two different "
        "records — so this cannot be caught by reading the page.")


def test_no_archive_doi_placeholder_survives_in_the_article():
    article = open(ARTICLE, encoding="utf-8").read()
    assert "ARCHIVE DOI" not in article, (
        "an [ARCHIVE DOI — PLACEHOLDER] block is still in the article. The placeholder says in "
        "terms that the citation does not resolve; shipping it is shipping that sentence.")


def test_both_availability_statements_carry_it():
    """Two statements, two audiences: Methods for a reader reproducing, Declarations for a screener.

    ⚠ COUNTED, NOT SEARCHED-ONCE. The two are written independently and an edit has already dropped
    one of them once in this paper's history; a test that only asserts "the DOI appears" passes on
    a paper that lost one of its two availability statements.
    """
    article = open(ARTICLE, encoding="utf-8").read()
    assert len(ZENODO_DOI.findall(article)) >= 2, (
        "the deposit DOI appears fewer than twice. Methods -> Availability and Declarations -> "
        "Data and code availability each carry it.")
