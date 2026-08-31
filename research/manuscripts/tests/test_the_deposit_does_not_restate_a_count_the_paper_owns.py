#!/usr/bin/env python3
"""⛔⛔ A DEPOSITED FILE MAY NOT ASSERT A COUNT THE MANUSCRIPT OWNS, BECAUSE IT WILL GO STALE THERE.

⚠ WHAT THIS COST, MEASURED ACROSS TWO ROUNDS AND ONE FILE. `research/modalities/aso_parent_gap_
pairing.py` is in the 496-path archive both papers cite, and it carried the panel's survivor count in
THREE places:

  · its module docstring — "five of the nine designs the manuscript calls clean" (a draft in which
    nine were called clean; the manuscript said three). Found by round 23.
  · its `_what_this_is_not` bullet — "The two designs surviving every screen in the manuscript have
    a longest run of ZERO". Found by round 23, and the repair UNIVERSALLY QUANTIFIED it into
    something false: "Every design that survives every screen has a longest run of ZERO."
  · the comment documenting `MIN_DUPLEX_BP` — "The two designs that survive every screen have a
    longest run of ZERO … so the candidate set is threshold-independent." Found by round 24, one
    round after the other two were repaired, in the same file.

★ THE SHAPE IS NOT "A STALE NUMBER". It is CLAUDE.md's one-fact-one-place rule with a delivery
mechanism: a count whose one home is the paper, restated inside an immutable archive, goes stale
without anybody editing it and cannot be corrected in place — only superseded by a new version.
Each of the three was true when written.

⛔ AND THE THIRD WAS THE WORST PLACED. It documented the threshold the paper's central negative is
read against, and it told a reviewer the result does not turn on that threshold — while the archive's
own test proves it does for one of the three designs.

★★ SO THE RULE THIS ENFORCES IS NARROW AND CHECKABLE: a deposited file may DESCRIBE the screen it
computes, and may state what it measures. It may not assert how many designs the MANUSCRIPT reports
as surviving, because that number is the paper's and the paper is where it is maintained. A
historical statement is fine and is detected by its own past tense or by an explicit supersession
marker — that is rule 1.2 working, not an exception to this one.
"""
from __future__ import annotations

import io
import json
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
ASO = os.path.join(MANUSCRIPTS, "aso")

MANIFEST = os.path.join(ASO, "fusion-junction-aso-archive-manifest.json")
ARTICLE = os.path.join(ASO, "fusion-junction-aso-journal-article.md")

#: The count-bearing phrasings that have actually appeared, as a present-tense assertion about the
#: panel's survivors. ⚠ DERIVED FROM THE THREE REAL INSTANCES rather than invented: every one said
#: "<number> design(s) … surviv|clear … every screen".
#: ⚠ THE COUNT MUST BE ADJACENT TO "designs", NOT MERELY NEAR IT. A `{0,60}` window matched "all
#: five … designs that clear every screen" in the extended report (where the real count follows the
#: noun) and the "23" of "Round 23 found it saying …" — three false positives on the first run, on
#: honest sentences. A gate that reds on true input is one its reader learns to skip.
_ASSERTION = re.compile(
    r"(?P<count>\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d{1,3})\b)"
    r"\s+(?:\w+\s+){0,2}designs?\b[^.\n]{0,80}?"
    r"\b(?:survive|surviving|survives|clear|clearing|clears)\b[^.\n]{0,40}?"
    r"\bevery screen\b",
    re.IGNORECASE)

#: Past tense or an explicit supersession marker means the sentence is a RECORD of what was once
#: true, which rule 1.2 requires to be retained. Those are not defects.
#: ⚠ A QUOTED ASSERTION IS A REPORT OF ONE. Rule 1.2 requires a superseded sentence to be RETAINED
#: verbatim, so every correctly-written retraction quotes the claim it retracts — and the first
#: version of this guard flagged its own retraction notes. A quotation mark or a past-tense reporting
#: verb marks the sentence as a record rather than a claim.
_HISTORICAL = re.compile(
    r"[\"“”']|\b(?:called|was|were|used to|previously|formerly|until|superseded|retained|"
    r"corrected|found|said|saying|read|entered|stale|wrong|incorrect)\b", re.IGNORECASE)

_WORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
         "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _manifest():
    with io.open(MANIFEST, encoding="utf-8") as fh:
        return json.load(fh)


def _paper_survivor_count():
    """The number the MANUSCRIPT reports, which is the one home of this fact."""
    text = re.sub(r"\s+", " ", io.open(ARTICLE, encoding="utf-8").read())
    m = _ASSERTION.search(text)
    assert m, ("the manuscript no longer states how many designs clear every screen, so this guard "
               "has no reference count. If the claim moved, re-anchor here rather than deleting.")
    raw = m.group("count").lower()
    return _WORD.get(raw, int(raw) if raw.isdigit() else None)


def _sentences(text):
    return re.split(r"(?<=[.!?])\s+|\n(?=#)|\n\n", text)


def test_the_reference_count_is_readable_from_the_paper():
    """⛔ THE PRECONDITION. A guard that cannot read the paper's own number would pass every
    deposited file for any value, which is the vacuity this whole file exists to replace."""
    n = _paper_survivor_count()
    assert isinstance(n, int) and 0 < n < 100, (
        f"the survivor count read out of the manuscript is {n!r}, which is not a plausible count")


def test_no_deposited_file_asserts_a_survivor_count_that_disagrees_with_the_paper():
    """⛔⛔ THE PROPERTY. Three sites in one file got this wrong across two rounds."""
    paper_n = _paper_survivor_count()
    deposited = [f["path"] for f in _manifest()["files"]
                 if f["path"].endswith((".py", ".md", ".json"))
                 and not f["path"].endswith("fusion-junction-aso-journal-article.md")]
    assert deposited, "no deposited text files; this guard would pass vacuously"

    wrong = []
    for rel in deposited:
        full = os.path.join(REPO, rel)
        if not os.path.exists(full):
            continue
        try:
            body = io.open(full, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        for sentence in _sentences(body):
            m = _ASSERTION.search(sentence)
            if not m or _HISTORICAL.search(sentence):
                continue
            raw = m.group("count").lower()
            said = _WORD.get(raw, int(raw) if raw.isdigit() else None)
            if said is not None and said != paper_n:
                wrong.append((rel, said, " ".join(sentence.split())[:170]))

    assert not wrong, (
        f"the manuscript reports {paper_n} designs clearing every screen, and {len(wrong)} "
        f"deposited file(s) assert a different number:\n  "
        + "\n  ".join(f"{rel}: says {said} — {quote}" for rel, said, quote in wrong)
        + "\n\n⛔ Do NOT just change the number. A count whose one home is the paper should not be "
          "restated inside an immutable archive at all — it goes stale there and cannot be "
          "corrected in place, only superseded. Say what the module MEASURES instead, or mark the "
          "sentence as historical (rule 1.2), which this guard already permits.")


def test_the_pattern_catches_the_three_sentences_that_actually_shipped():
    """★ THE MUTATION HALF, DRIVEN RATHER THAN DESCRIBED. Each of these reached `origin/main` inside
    the deposited archive; a pattern that misses any of them is measuring nothing. And the last two
    cases assert the converse — the guard must NOT fire on a correct or a historical sentence, or it
    reds on honest input and gets loosened."""
    shipped = [
        ("The two designs surviving every screen in the manuscript have a longest run of ZERO "
         "at any length.", 2),
        ("The two designs that survive every screen have a longest run of ZERO — no window of any "
         "parent pairs their gap at any length — so the candidate set is threshold-independent.", 2),
        ("Three designs clear every screen applied here, none at a junction any patient is "
         "reported to carry.", 3),
    ]
    for sentence, expected in shipped:
        m = _ASSERTION.search(sentence)
        assert m, f"the pattern does not match a sentence that actually shipped: {sentence[:80]}"
        raw = m.group("count").lower()
        assert _WORD.get(raw, raw) == expected, (
            f"the pattern read {raw!r} where the sentence says {expected}")

    historical = ("It read 'The two designs that survive every screen have a longest run of ZERO' "
                  "until it was corrected.")
    assert _HISTORICAL.search(historical), (
        "a retained supersession quote is not recognised as historical, so rule 1.2's own remedy "
        "would fail this guard — which is how a correctly-written retraction gets deleted")

    assert not _ASSERTION.search(
        "Every design's raw longest run is released so another threshold can be applied."), (
        "the pattern fires on a sentence asserting no survivor count at all")
