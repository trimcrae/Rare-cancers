#!/usr/bin/env python3
"""Every parenthesis and bracket a deposit document opens is closed, and closed in its own paragraph.

⛔ WHY THIS EXISTS, AND IT IS A MEASURED FIX-INDUCED DEFECT (2026-08-19). Three commits in sequence
did this to one sentence in §2.10:

  258c2ea  ... free energies — nearest-neighbour values ... in this work (§6) — every one ...  BALANCED
  f4025a3  ... free energies (nearest-neighbour values ... in this work (§6)) every one ...    BALANCED
  a9e40e8  ... free energies (nearest-neighbour values ... in this work (§6) — every one ...   UNBALANCED

`f4025a3` converted an em-dash pair to a parenthetical to clear the prose-style gate, correctly
producing a nested `))`. `a9e40e8` was hunting a DIFFERENT defect — an em-dash conversion really had
produced a stray doubled `)` elsewhere — recognised `))` as that signature, and deleted one. The
second `)` was not stray: it closed the outer parenthetical. The fix pattern-matched a shape and
never checked the balance, and the manuscript carried an unclosed parenthesis into three builds.

⭐ THE INVARIANT IS ABSOLUTE, NOT A BASELINE. A count that "should not change" needs a stored
previous value and someone to compare it; a count that must be ZERO needs neither and cannot rot.
`scripts/blast_radius.py` still records the balance so a diff can show it moved, but the gate is
here, where CI runs it on every push without anyone remembering to snapshot first.

⚠ PARAGRAPH-LOCAL, NOT FILE-TOTAL. A file-total balance is satisfied by two errors of opposite sign
in different sections, which is precisely the state a hand-repair produces. No sentence in these
documents opens a parenthetical it does not close before the next blank line.

$0, stdlib, no network.
"""
import os
import re

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASO = os.path.join(os.path.dirname(_HERE), "aso")

#: The documents a depositor uploads. Working records, memos and review reports are deliberately
#: absent: they quote broken text on purpose, and a gate applied where it cannot hold is a gate
#: someone will loosen (CLAUDE.md §6).
DEPOSIT_DOCUMENTS = (
    "fusion-junction-aso-research-article.md",
    "fusion-junction-aso-supplementary-information.md",
    "fusion-junction-aso-submission-tables.md",
)

PAIRS = (("(", ")"), ("[", "]"))


def _paragraphs(text):
    """(1-based start line, paragraph) for each blank-line-separated block."""
    out, line = [], 1
    for para in text.split("\n\n"):
        out.append((line, para))
        line += para.count("\n") + 2
    return out


def _strip_uncounted(para):
    """Remove spans where an unmatched delimiter is legitimate.

    Fenced and inline code carry regexes and shell fragments; a markdown link's `](` is structure,
    not prose. Emoticons are not used in these documents and are not exempted.
    """
    para = re.sub(r"```.*?```", " ", para, flags=re.S)
    para = re.sub(r"`[^`]*`", " ", para)
    return para


@pytest.mark.parametrize("name", DEPOSIT_DOCUMENTS)
def test_no_paragraph_opens_a_delimiter_it_does_not_close(name):
    path = os.path.join(_ASO, name)
    assert os.path.exists(path), (
        f"{path} is missing. A deposit document that is absent is a failure, never a skip — this "
        "gate is meaningless if it silently covers two files instead of three.")
    text = open(path, encoding="utf-8").read()

    bad = []
    for start, para in _paragraphs(text):
        clean = _strip_uncounted(para)
        for opener, closer in PAIRS:
            delta = clean.count(opener) - clean.count(closer)
            if delta:
                flat = re.sub(r"\s+", " ", para).strip()
                bad.append(f"line {start}: {delta:+d} unmatched '{opener}{closer}' — {flat[:160]}")
    assert not bad, (
        f"{len(bad)} paragraph(s) of {name} open a delimiter they do not close:\n" + "\n".join(bad))


def test_this_guard_fails_on_the_defect_it_was_written_for():
    """Prove the guard by reintroducing a9e40e8's exact edit — and prove the reintroduction landed.

    ⚠ ASSERT THAT THE MUTATION CHANGED THE TEXT. One "proof" in this ledger compared identical text
    twice, because the replacement string never matched the file's line wrapping, and reported a
    guard as proven when it had never been exercised.
    """
    path = os.path.join(_ASO, DEPOSIT_DOCUMENTS[0])
    original = open(path, encoding="utf-8").read()

    fixed = "applied anywhere in this work, §6) — every one of the 190 designs"
    broken = "applied anywhere in this work (§6) — every one of the 190 designs"
    assert original.count(fixed) == 1, (
        "the §2.10 sentence this proof mutates has been reworded; re-anchor the proof on the text ⛔ CHECK THE MEANING BEFORE THE REGEX: if the claim was INVERTED or DROPPED, re-anchoring makes the guard agree with the new wording and the finding disappears. Re-anchor only when the sentence says the same thing in different words."
        "that is there now rather than deleting it — an unexercised guard is an absent one.")
    mutated = original.replace(fixed, broken, 1)
    assert mutated != original, "the mutation did not change the text; this proof would be vacuous"

    offenders = []
    for start, para in _paragraphs(mutated):
        clean = _strip_uncounted(para)
        if clean.count("(") != clean.count(")"):
            offenders.append(start)
    assert offenders, (
        "reintroducing the unclosed parenthetical of a9e40e8 did NOT trip the balance check, so "
        "the check would not have caught the defect it exists for.")
