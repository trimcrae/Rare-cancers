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
#: ⛔ BOTH TITLES (round 14 seat 4). This guard opened the extended report only, so the CONDENSED
#: submission's title — the one that reaches a NAT reader, a search result and a citation line —
#: was checked by nothing at all. That is the ninth instrument this review has found bound to one
#: of a pair while its docstring reasons about "the title".
ARTICLES = {
    "extended-report": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-research-article.md"),
    "journal-article": os.path.join(MANUSCRIPTS, "aso",
                                    "fusion-junction-aso-journal-article.md"),
}
ARTICLE = ARTICLES["extended-report"]
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


def _text(article=None):
    article = article or ARTICLE
    if not os.path.exists(article):
        pytest.fail(f"{os.path.basename(article)} is missing; its title is unchecked")
    return open(article, encoding="utf-8").read()


def _front_matter_title(article=None):
    m = re.search(r'^title:\s*"(.+?)"\s*$', _text(article), flags=re.M)
    assert m, "the front matter carries no `title:` line; nothing names this deposit"
    return " ".join(m.group(1).split())


def _h1(article=None):
    m = re.search(r"^#\s+(.+?)\s*$", _text(article), flags=re.M)
    assert m, "the manuscript has no H1; the rendered document has no title"
    return " ".join(m.group(1).split())


def _plain(title):
    """Markdown emphasis stripped — the YAML title carries none and the H1 does."""
    return re.sub(r"[*_`]", "", title)


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_front_matter_title_and_the_printed_title_are_the_same_claim(paper):
    """Two copies of one sentence in one file is a divergence waiting to happen.

    The YAML title is what the repository's own tooling indexes; the H1 is what the PDF builds
    print. A round that edits one and not the other ships a deposit whose metadata and cover page
    disagree, and nothing else in the suite compares them.
    """
    front, h1 = _plain(_front_matter_title(ARTICLES[paper])), _plain(_h1(ARTICLES[paper]))
    assert front == h1, (
        "the front-matter `title:` and the printed H1 have diverged.\n"
        f"  front matter: {front}\n"
        f"  H1          : {h1}\n"
        "One of them is what a reader sees and the other is what the tooling indexes.")


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_titles_rate_word_is_one_the_measurement_supports(paper):
    """87 of 190 is 45.8%. "Nearly half" is true of that; "most" would not be."""
    observed = _artifact()["observed"]
    rate = observed["n_liable"] / observed["n_designs"]
    title = _plain(_front_matter_title(ARTICLES[paper]))
    # ⭐ AN EXACT RATIO IS A RATE, AND A STRICTLY BETTER ONE (2026-08-22). The condensed title says
    # "87 of 190" where the extended report says "nearly half": no band to license, both numbers
    # checked against the artifact directly, and the reader is told the denominator. A guard that
    # accepted only English quantifiers would have refused the more precise title — so it accepts
    # either, and an exact ratio is checked EXACTLY rather than against a band.
    exact = re.findall(r"\b(\d+) of (\d+)\b", title)
    for n, d in exact:
        assert (int(n), int(d)) == (observed["n_liable"], observed["n_designs"]), (
            f"the title states {n} of {d}; the screen measured "
            f"{observed['n_liable']} of {observed['n_designs']} "
            "(aso-parent-null.json:observed). Either the title or the measurement has moved.")
    found = [m.group(0).lower().strip() for m in _RATE_SCANNER.finditer(title)]
    assert found or exact, (
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


@pytest.mark.parametrize("paper", sorted(ARTICLES), ids=sorted(ARTICLES))
def test_the_title_states_the_criterion_the_artifact_was_read_at(paper):
    """The rate is meaningless without its cut, and the cut is adopted rather than measured."""
    cut = _artifact()["method"]["min_duplex_bp"]
    title = _plain(_front_matter_title(ARTICLES[paper]))
    # ⚠ THREE SPELLINGS, ONE PROPERTY. The extended report writes "a ten-base-pair duplex"; the
    # condensed title, which is built to a page budget where every character is charged for, writes
    # "at 10 bp". Both name the same cut, and a guard that admitted only the hyphenated form would
    # be enforcing a house style rather than a measurement.
    stated = re.search(r"\b([a-z]+|\d+)[- ]base[- ]pairs?\b|\b(\d+)\s*bp\b", title, re.I)
    assert stated, (
        f"the title states a rate with no criterion: {title!r}. The same designs are 92.1% liable "
        f"at seven base pairs and 3.2% at thirteen (aso-parent-null.json:cut_sensitivity), so a "
        "rate without its cut is not a claim.")
    token = (stated.group(1) or stated.group(2)).lower()
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

    ⚠ EXTENDED REPORT ONLY, AND DELIBERATELY — NOT A ONE-OF-A-PAIR GAP. §2.9's gap-length series was
    moved whole out of the condensed submission for the six-page budget, so its title states no
    trade and must not: a guard demanding one there would demand a claim the paper no longer makes.
    The three tests above ARE parametrised over both, because a rate word, a criterion and the
    front-matter/H1 agreement are owed by any title of this work.
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


#: The cover letter's `Re:` line is a SECOND HOME for the title, and the letter says so in its own
#: margin note — "the line above is copied from it verbatim; retitle the manuscript and this line
#: must be recopied, not retyped". Until 2026-08-22 that instruction was backed by nothing, and it
#: had already failed twice: once carrying a pre-rename title, and once carrying the EXTENDED
#: report's title after the submission split in two, so the one line an editor reads first named a
#: manuscript the envelope did not contain.
COVER_LETTER = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-cover-letter.md")


def test_the_cover_letters_subject_line_is_the_submitted_manuscripts_own_title():
    """⛔ THE ONE LINE AN EDITOR READS FIRST, AND IT NAMES A DOCUMENT."""
    assert os.path.exists(COVER_LETTER), "the cover letter is missing; re-anchor this guard"
    text = open(COVER_LETTER, encoding="utf-8").read()
    line = [l for l in text.splitlines() if l.startswith("**Re:**")]
    assert len(line) == 1, (
        f"the cover letter carries {len(line)} `**Re:**` lines; exactly one names the submission")
    stated = re.search(r'"(.+)"\s*$', line[0])
    assert stated, f"the cover letter's Re: line quotes no title: {line[0]!r}"
    want = _plain(_h1(ARTICLES["journal-article"]))
    assert stated.group(1) == want, (
        "the cover letter's Re: line and the submitted manuscript's title have diverged.\n"
        f"  letter    : {stated.group(1)}\n"
        f"  manuscript: {want}\n"
        "Recopy the manuscript's H1 into the letter — do not retype it, and do not edit the "
        "manuscript to match the letter.")
