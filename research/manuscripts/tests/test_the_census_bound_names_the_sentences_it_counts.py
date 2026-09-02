"""§2.3's census bound must count the sentences it then names, in `emc-fusion-partner-stratification.md`.

⛔⛔ WHY THIS EXISTS. The full-depth ablation run of 2026-09-02 (`S40-COVERAGE-INFLATION.md`) found
ONE blind sentence in this manuscript, and it is the paragraph that states the paper's exhaustiveness
limit — the single most load-bearing caveat in the document. The census marks it covered; perturbing
`second -> fourth` and `Two -> Six` in a clone turned NO guard red. "Two sentences in this paper are
most at risk of being read as a census" is a COUNT, and it is spelled out, so every numeric guard on
this manuscript was structurally unable to see it.

★ WHAT THE NUMBER IS A COUNT OF, AND WHERE IT LIVES. It counts the items the SAME paragraph then
enumerates and quotes — "The first is **\"…\"**", "The second is **\"…\"**". There is no artifact
under `research/` that owns it, and inventing one to derive it from would be worse than leaving it
open, so this guard derives it from the enumeration itself: the stated count must equal the number of
quoted items, and each ordinal must be used exactly once and in sequence. A caveat that under-counts
its own list is a caveat that silently leaves a sentence unqualified, which is the failure the
paragraph exists to prevent.

⛔ WHAT IS DELIBERATELY NOT BOUND. The same sentence's "no second reader checked the inclusion
decisions" is the PRISMA dual-screening idiom, not a count of anything this repository holds.
Asserting the word "second" there would pin a spelling and prove nothing, so it is left open and
named here. The sentence reddens on its other quantity instead.

⛔ AND NOTHING HERE MAY BE RELAXED INTO A MEMBERSHIP TEST. `"Two sentences" in text` passes while the
list beneath it grows to three, which is exactly the drift this guard is for.
"""
from __future__ import annotations

import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
PAPER = os.path.join(MANUSCRIPTS, "fusion-partner", "emc-fusion-partner-stratification.md")

#: The ordinals the paragraph may use, in order. Indexed by position, never typed at a call site.
_ORDINAL = ("first", "second", "third", "fourth", "fifth", "sixth")
_CARDINAL = ("No", "One", "Two", "Three", "Four", "Five", "Six")

#: `The first is **"no source pools the response data at all"**` — one enumerated at-risk sentence.
_ENUMERATED = re.compile(r"The (%s) is \*\*[“\"]([^”\"]+)[”\"]\*\*" % "|".join(_ORDINAL))


@pytest.fixture(scope="module")
def flat():
    if not os.path.exists(PAPER):
        pytest.fail(f"the stratification manuscript is missing at {PAPER}. It is committed, so "
                    "restore it rather than passing over the assertions that depend on it.")
    return re.sub(r"\s+", " ", open(PAPER, encoding="utf-8").read())


def test_the_census_bound_counts_the_at_risk_sentences_it_enumerates(flat):
    """⛔ The count, the enumeration and the ordinals, held together.

    Three ways this can go wrong and all three are silent today: the count drifts from the list; an
    ordinal repeats or skips, so a reader cannot tell which sentence is which; or the paragraph
    survives while the list under it is emptied by an edit elsewhere. The last is why an empty
    enumeration fails loudly instead of vacuously passing.
    """
    # ⛔ THE ANCHOR DELIBERATELY AVOIDS THE WORD "second". Anchoring on "no second reader" would
    # make this guard go red when an ablation swaps that ordinal — a red earned by pinning a
    # spelling rather than by binding a count, which is a FALSE RED in the reassuring direction and
    # exactly what `claim_ablation` is trying to measure. The PRISMA clause locates the same
    # sentence and carries no perturbable quantity.
    window = re.search(r"no PRISMA-style screening flow was run,[^*]{0,200}\*\*(.{0,2000})", flat)
    assert window, (
        "§2.3's process-limits sentence ('no PRISMA-style screening flow was run …') is no longer in "
        "the manuscript. That sentence is the paper's exhaustiveness bound; if it moved, re-anchor "
        "this guard, and if it was deleted that is a change to the paper's honesty scope and must "
        "be argued, not absorbed.")
    tail = window.group(1)

    enumerated = _ENUMERATED.findall(tail)
    assert enumerated, (
        "the paragraph states a count of at-risk sentences and then enumerates none of them. The "
        "count is only meaningful as a count OF that list, so an empty list makes the caveat "
        "unverifiable rather than merely terse.")
    ordinals = [o for o, _q in enumerated]
    assert ordinals == list(_ORDINAL[:len(enumerated)]), (
        f"the at-risk sentences are introduced as {ordinals}, which is not the ordinal sequence "
        f"{list(_ORDINAL[:len(enumerated)])} a reader counts along with — an ordinal repeated or "
        "skipped hides an item")

    quoted = [q for _o, q in enumerated]
    assert len(set(quoted)) == len(quoted), (
        f"the paragraph quotes the same at-risk sentence twice: {quoted}")

    stated = re.findall(r"^\s*(\w+) sentences in this paper are most at risk of being read as a "
                        r"census", tail[:400])
    assert len(stated) == 1, (
        f"the census bound states its count at {len(stated)} site(s) in the expected construction; "
        "it must state it exactly once, beside the list it counts")
    assert stated[0] == _CARDINAL[len(enumerated)], (
        f"§2.3 says {stated[0]!r} sentences are most at risk of being read as a census and then "
        f"enumerates {len(enumerated)} of them ({quoted}). A caveat that under-counts its own list "
        "leaves a sentence unqualified in a paper whose whole scope claim is this paragraph.")
