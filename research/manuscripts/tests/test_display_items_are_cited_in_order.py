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
ARTICLE = os.path.join(os.path.abspath(os.path.join(HERE, "..")), "aso",
                       "fusion-junction-aso-research-article.md")


def _body():
    if not os.path.exists(ARTICLE):
        pytest.fail(f"the manuscript is missing: {ARTICLE}")
    text = open(ARTICLE, encoding="utf-8").read()
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)       # repo frontmatter, not manuscript
    text = re.sub(r"^## Figure legends.*", "", text, flags=re.S | re.M)
    return text


BODY = _body()


def _first_citations(kind):
    """{number: character offset of its first mention in the body}."""
    out = {}
    for match in re.finditer(rf"\b{kind} (\d+)\b", BODY):
        out.setdefault(int(match.group(1)), match.start())
    return out


@pytest.mark.parametrize("kind,expected", [("Table", 7), ("Figure", 3)])
def test_every_display_item_is_cited_in_the_body_at_all(kind, expected):
    cited = _first_citations(kind)
    missing = sorted(set(range(1, expected + 1)) - set(cited))
    assert not missing, (
        f"{kind}(s) {missing} are never cited in the body, so the journal build has no anchor to "
        f"float them to and a reader is never sent to them")


@pytest.mark.parametrize("kind", ["Table", "Figure"])
def test_display_items_are_first_cited_in_numerical_order(kind):
    cited = _first_citations(kind)
    by_position = [n for n, _ in sorted(cited.items(), key=lambda kv: kv[1])]
    assert by_position == sorted(by_position), (
        f"{kind}s are first cited in the order {by_position}, not {sorted(by_position)}. The journal "
        f"build floats each {kind.lower()} to its first citation, so the PDF will print them out of "
        f"sequence.\nFix by REMOVING or MOVING the stray early reference where that is what happened "
        f"— a single cross-reference added for another reason can reorder the whole document — and "
        f"renumber only if the citation order is genuinely the intended one.")


def test_the_body_was_found_and_is_not_empty_after_stripping():
    """A stripping bug would make every ordering assertion above vacuously true."""
    assert len(BODY) > 20000, (
        f"the manuscript body came out at {len(BODY)} characters after stripping frontmatter and "
        "the figure-legends block; the ordering checks above would be asserting about nothing")
    assert "Table 1" in BODY and "Figure 1" in BODY
