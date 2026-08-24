"""Tables and figures must be first cited in the order they are numbered.

⛔ WHY. Journal style numbers display items by first mention, and the journal build FLOATS each one
to its first citation — so if the numbering and the citation order disagree, the built PDF prints
them out of sequence. On 2026-08-18 a blind screen found the journal PDF running 1, 2, 3, 6, 4, 5, 7.

⛔⛔ AND THE OUT-OF-ORDER CITATION WAS INTRODUCED BY A FIX. Two rounds earlier a screen found §2.2
citing Table 2 for a gene identity Table 2 has no column for. The correction named where the identity
does come from — "read from the deep hit list and from Table 6" — and that clause, 28,000 characters
before Table 6's next mention, silently became Table 6's FIRST citation and reordered the document.
The prose was true; the side effect was not visible in it.

★ SO THE CHEAP FIX WAS THE RIGHT ONE. Renumbering three tables would have touched the generator, the
manuscript, and every test pinning a number — a wide mechanical change to accommodate a stray
forward reference. Dropping the reference restored the order and changed one clause. This test is
what makes that distinction checkable rather than a judgement call, and it fires the moment a new
cross-reference reorders the document, which is the only moment it is cheap to fix.

⚠ THE FIGURE LEGENDS BLOCK IS EXCLUDED. It names every figure and table in numerical order by
construction, so including it would make every ordering look correct no matter what the body does.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ASO = os.path.join(os.path.abspath(os.path.join(HERE, "..")), "aso")
#: ⛔⛔ THIS GUARD READ ONE OF A PAIR FOR ITS WHOLE LIFE (round 16 seat 1, 2026-08-22). It is a
#: complete, working instrument, and it was pointed only at the DEPOSIT pair — so the CONDENSED pair
#: that is actually going to a journal had no display-item ordering check at all, and ablation found
#: "Table 1" perturbable in the journal tables file with nothing noticing. Same one-of-a-pair shape
#: this review has now closed a dozen times, in the guard whose whole subject is cross-references.
PAIRS = {
    "extended-report": (os.path.join(ASO, "fusion-junction-aso-research-article.md"),
                        os.path.join(ASO, "fusion-junction-aso-submission-tables.md")),
    "journal": (os.path.join(ASO, "fusion-junction-aso-journal-article.md"),
                os.path.join(ASO, "fusion-junction-aso-journal-tables.md")),
}

#: ⛔ THE FLOOR IS A SHARE OF THE FILE, NOT A CHARACTER COUNT. It read `> 20000` against an article
#: of 196 KB, so the two strips below could have eaten nine tenths of the manuscript and the
#: "is not empty after stripping" guard would still have reported the ordering checks as live.
#: Measured 2026-08-19: the body survives at 92% of the source. Half is a floor with room for the
#: figure-legends block to grow and none for a strip that runs away.
MIN_BODY_SHARE_OF_FILE = 0.5


def _raw(pair):
    article, _tables = PAIRS[pair]
    if not os.path.exists(article):
        pytest.fail(f"the manuscript is missing: {article}")
    return open(article, encoding="utf-8").read()


def _body(pair):
    text = re.sub(r"^---\n.*?\n---\n", "", _raw(pair), flags=re.S)  # repo frontmatter, not manuscript
    text = re.sub(r"^## Figure legends.*", "", text, flags=re.S | re.M)
    return text


def _declared_display_items(pair):
    """{"Table": n, "Figure": n} — how many of each the deposit actually carries.

    ⛔ DERIVED, NOT TYPED (2026-08-19). This was `[("Table", 7), ("Figure", 3)]`. Table 7 was
    generated after the constant was written and had to be chased by hand; an eighth table is under
    discussion in this very round. A typed count cannot notice a display item added upstream, and
    when one is added it fails for a reason that has nothing to do with citation order — the same
    defect `test_every_table_survives_into_the_journal_layout` records for its own caption count.
    Tables come from the generated tables document, figures from the manuscript's own legend block,
    because those are the two places a display item is actually created.
    """
    _article, tables_path = PAIRS[pair]
    assert os.path.exists(tables_path), (
        f"the generated tables document is missing: {tables_path} — the number of tables the deposit "
        "carries cannot be derived, and a typed number is what this replaced")
    tables = {int(n) for n in
              re.findall(r"^\*\*Table (\d+)\.", open(tables_path, encoding="utf-8").read(), re.M)}
    legends = re.search(r"^## Figure legends.*", _raw(pair), re.S | re.M)
    #: Supplementary panels are numbered S1, S2 … and are cited as "Supplementary Figure S1", not
    #: as "Figure 4", so they are deliberately outside this numbering.
    # ⚠ THE CONDENSED PAIR CARRIES NO FIGURE LEGENDS BLOCK, and that is a real difference between
    # the two documents rather than a missing input — so figures are simply absent there, and the
    # parametrisation below skips the kinds a pair does not declare instead of inventing a count.
    figures = ({int(n) for n in re.findall(r"^\*\*Figure (\d+)\.", legends.group(0), re.M)}
               if legends else set())
    assert tables, f"{pair} declares no tables at all, so its tables document is not being read"
    out = {"Table": max(tables)}
    if figures:
        out["Figure"] = max(figures)
    return out


def _first_citations(pair, kind):
    """{number: character offset of its first mention in the body}."""
    out = {}
    for match in re.finditer(rf"\b{kind} (\d+)\b", _body(pair)):
        out.setdefault(int(match.group(1)), match.start())
    return out


#: The (pair, kind) combinations that EXIST — computed, so a pair carrying no figure legends simply
#: contributes no Figure case.
#: ⛔ NOT A BARE `return` INSIDE THE TEST. Round 16 seat 5 found one of those in the title guard,
#: where it had silently meant "asserts nothing, reports PASSED" since the day it was written. An
#: absent case must be absent from the PARAMETRISATION, where it is visible in the test report, not
#: hidden behind an early exit that looks like a pass.
CASES = [(pair, kind) for pair in sorted(PAIRS)
         for kind in sorted(_declared_display_items(pair))]


@pytest.mark.parametrize("pair,kind", CASES, ids=[f"{p}-{k}" for p, k in CASES])
def test_every_display_item_is_cited_in_the_body_at_all(pair, kind):
    expected = _declared_display_items(pair)[kind]
    cited = _first_citations(pair, kind)
    missing = sorted(set(range(1, expected + 1)) - set(cited))
    assert not missing, (
        f"{kind}(s) {missing} are never cited in the body, so the journal build has no anchor to "
        f"float them to and a reader is never sent to them. The deposit declares {expected} "
        f"{kind.lower()}(s); this count is derived from the artefact that creates them, so if one "
        "was genuinely retired, retire it there.")


@pytest.mark.parametrize("pair,kind", CASES, ids=[f"{p}-{k}" for p, k in CASES])
def test_display_items_are_first_cited_in_numerical_order(pair, kind):
    cited = _first_citations(pair, kind)
    by_position = [n for n, _ in sorted(cited.items(), key=lambda kv: kv[1])]
    assert by_position == sorted(by_position), (
        f"{kind}s are first cited in the order {by_position}, not {sorted(by_position)}. The journal "
        f"build floats each {kind.lower()} to its first citation, so the PDF will print them out of "
        f"sequence.\nFix by REMOVING or MOVING the stray early reference where that is what happened "
        f"— a single cross-reference added for another reason can reorder the whole document — and "
        f"renumber only if the citation order is genuinely the intended one.")


@pytest.mark.parametrize("pair", sorted(PAIRS))
def test_the_body_was_found_and_is_not_empty_after_stripping(pair):
    """A stripping bug would make every ordering assertion above vacuously true."""
    BODY, RAW = _body(pair), _raw(pair)
    share = len(BODY) / len(RAW)
    assert share >= MIN_BODY_SHARE_OF_FILE, (
        f"the manuscript body came out at {len(BODY)} characters — {share:.0%} of the "
        f"{len(RAW)}-character source — after stripping the repo frontmatter and the "
        f"figure-legends block, against a floor of {MIN_BODY_SHARE_OF_FILE:.0%}. One of the two "
        "strips is eating the paper, and the ordering checks above would be asserting about "
        "whatever is left.")
    assert "Table 1" in BODY and "Figure 1" in BODY
