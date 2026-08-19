"""The title is a claim, and nothing in the suite read it.

⛔ WHY THIS FILE EXISTS. The title is the one sentence that reaches every reader — a search result,
a citation line, a preprint server's listing — and for most of them it is the ONLY sentence. It
states three quantitative things:

  * a RATE ("Nearly half of junction-spanning gapmer designs …"), which is 87/190;
  * a CRITERION ("… over a ten-base-pair duplex through the catalytic gap"), which is the cut the
    whole paper is stated at and which §2.5 says is adopted rather than measured; and
  * a TRADE ("… and a longer gap trades gap-level margin against parent-paired gap DNA"), which is
    §2.9's identity.

Every one of the three can go stale silently. The rate word is not a number, so no numeric linter
sees it; a cut that moved from ten would leave the title reading ten with every count beneath it
recomputed; and the trade clause names two quantities that Figure 3's own axis was found (2026-08-19)
to be a DIFFERENT quantity from the one its caption claimed — `parent_paired_gap_dna_nt`, arithmetic
on the design's own seam, against the searched mature-parent duplex. A title naming the wrong pair
of quantities is that same confusion at the top of the paper.

★ NOTHING HERE IS TYPED. The rate comes from `aso-parent-null.json`'s `observed`, the criterion from
its `method.min_duplex_bp`, and the two traded quantities are required to be §2.9's own — read out
of §2.9 at run time, because §2.9 is what the title is summarising.

⚠ THE RATE IS CHECKED AS A BAND, NOT AS A STRING. "Nearly half" is a claim with a truth condition:
it is true of 0.4579 and false of 0.62. The bands below are what each English quantifier licenses,
so the guard fires both when the measurement moves out from under the word and when the word is
changed to one the measurement does not support.
"""
from __future__ import annotations

import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
ARTICLE = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-research-article.md")
NULL = os.path.join(REPO, "research", "modalities", "aso-parent-null.json")

_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
          "fifteen sixteen seventeen eighteen nineteen twenty").split()

#: What an English quantifier over a proportion licenses. Longest phrases first — the scanner is
#: leftmost-longest, so "nearly half" is never read as "half".
_RATE_BANDS = [
    ("more than half", (0.500, 1.000)),
    ("just under half", (0.430, 0.500)),
    ("just over half", (0.500, 0.570)),
    ("nearly half", (0.400, 0.500)),
    ("almost half", (0.400, 0.500)),
    ("about half", (0.450, 0.550)),
    ("a majority of", (0.500, 1.000)),
    ("a minority of", (0.000, 0.500)),
    ("nearly a third", (0.280, 0.334)),
    ("about a third", (0.290, 0.380)),
    ("a third of", (0.300, 0.370)),
    ("a quarter of", (0.200, 0.300)),
    ("two thirds of", (0.620, 0.710)),
    ("most", (0.500, 1.000)),
    ("half of", (0.475, 0.525)),
    ("every", (1.000, 1.000)),
    ("all", (1.000, 1.000)),
    ("none of", (0.000, 0.000)),
    ("no ", (0.000, 0.000)),
]
_RATE_SCANNER = re.compile("|".join(re.escape(p) for p, _ in _RATE_BANDS), re.I)


def _artifact():
    if not os.path.exists(NULL):
        pytest.fail("aso-parent-null.json is missing; the title's rate and criterion are unchecked")
    return json.load(open(NULL, encoding="utf-8"))


def _text():
    if not os.path.exists(ARTICLE):
        pytest.fail("the manuscript is missing; its title is unchecked")
    return open(ARTICLE, encoding="utf-8").read()


def _front_matter_title():
    m = re.search(r'^title:\s*"(.+?)"\s*$', _text(), flags=re.M)
    assert m, "the front matter carries no `title:` line; nothing names this deposit"
    return " ".join(m.group(1).split())


def _h1():
    m = re.search(r"^#\s+(.+?)\s*$", _text(), flags=re.M)
    assert m, "the manuscript has no H1; the rendered document has no title"
    return " ".join(m.group(1).split())


def _plain(title):
    """Markdown emphasis stripped — the YAML title carries none and the H1 does."""
    return re.sub(r"[*_`]", "", title)


def test_the_front_matter_title_and_the_printed_title_are_the_same_claim():
    """Two copies of one sentence in one file is a divergence waiting to happen.

    The YAML title is what the repository's own tooling indexes; the H1 is what the PDF builds
    print. A round that edits one and not the other ships a deposit whose metadata and cover page
    disagree, and nothing else in the suite compares them.
    """
    front, h1 = _plain(_front_matter_title()), _plain(_h1())
    assert front == h1, (
        "the front-matter `title:` and the printed H1 have diverged.\n"
        f"  front matter: {front}\n"
        f"  H1          : {h1}\n"
        "One of them is what a reader sees and the other is what the tooling indexes.")


def test_the_titles_rate_word_is_one_the_measurement_supports():
    """87 of 190 is 45.8%. "Nearly half" is true of that; "most" would not be."""
    observed = _artifact()["observed"]
    rate = observed["n_liable"] / observed["n_designs"]
    title = _plain(_front_matter_title())
    found = [m.group(0).lower().strip() for m in _RATE_SCANNER.finditer(title)]
    assert found, (
        f"the title states no rate at all: {title!r}. It carries this paper's central negative — "
        f"{observed['n_liable']} of {observed['n_designs']} designs pair a wild-type parent — and a "
        "title that drops the proportion drops the finding.")
    bands = dict(_RATE_BANDS)
    for phrase in found:
        low, high = bands[phrase]
        assert low <= rate <= high, (
            f"the title says {phrase!r}, which licenses a rate in [{low:.3f}, {high:.3f}]; the "
            f"measurement is {observed['n_liable']}/{observed['n_designs']} = {rate:.4f} "
            f"(aso-parent-null.json:observed). Either the word or the measurement has moved.")


def test_the_title_states_the_criterion_the_artifact_was_read_at():
    """The rate is meaningless without its cut, and the cut is adopted rather than measured."""
    cut = _artifact()["method"]["min_duplex_bp"]
    title = _plain(_front_matter_title())
    stated = re.search(r"\b([a-z]+|\d+)-base-pair\b", title, re.I)
    assert stated, (
        f"the title states a rate with no criterion: {title!r}. The same designs are 92.1% liable "
        f"at seven base pairs and 3.2% at thirteen (aso-parent-null.json:cut_sensitivity), so a "
        "rate without its cut is not a claim.")
    token = stated.group(1).lower()
    value = int(token) if token.isdigit() else (_WORDS.index(token) if token in _WORDS else None)
    assert value == cut, (
        f"the title states a {token}-base-pair criterion; the artifact was read at "
        f"{cut} (aso-parent-null.json:method.min_duplex_bp).")


def test_the_titles_trade_clause_names_the_two_quantities_section_2_9_trades():
    """§2.9's identity is between the gap-level margin and the parent-paired gap DNA.

    ⚠ THIS IS THE AXIS FIGURE 3 GOT WRONG. Its ordinate is `parent_paired_gap_dna_nt` — arithmetic
    on the design's own seam — while its caption called it the parent duplex the design concedes,
    which is the SEARCHED mature-parent quantity. The title trades two named quantities; both have
    to be quantities §2.9 actually trades, or the top line of the paper carries the same conflation.
    """
    title = _plain(_front_matter_title())
    clause = re.search(r"\btrades?\s+(.+)$", title, re.I)
    assert clause, (
        f"the title no longer states the gap-length trade: {title!r}. §2.9's identity — margin and "
        "parent-paired gap DNA are complements inside one gap — is the paper's second result.")
    sides = [s.strip(" .,;") for s in re.split(r"\bagainst\b|\bfor\b", clause.group(1)) if s.strip()]
    assert len(sides) == 2, (
        f"the title's trade clause names {len(sides)} quantit(ies), not two: {sides}. A trade is "
        "between two things.")

    body = re.sub(r"^---\n.*?\n---\n", "", _text(), flags=re.S)
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^#{2,3}\s*([\d.]+)\s*·", body, flags=re.M)]
    section = None
    for index, (start, number) in enumerate(heads):
        if number == "2.9":
            section = body[start:heads[index + 1][0] if index + 1 < len(heads) else len(body)]
    assert section, "§2.9 is not in the manuscript, so the title's trade clause has no source"
    flat = " ".join(_plain(section).split()).lower()
    for side in sides:
        assert side.lower() in flat, (
            f"the title trades {side!r}, which §2.9 never names. The two quantities §2.9 trades are "
            "complements inside one gap; a title naming something else is claiming a different "
            "result from the one measured. §2.9 is the section this clause summarises.")
