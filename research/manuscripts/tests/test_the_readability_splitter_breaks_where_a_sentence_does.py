#!/usr/bin/env python3
"""Where `lint_readability.sentences()` is allowed to break, and where it must not.

⚠ WHY THIS FILE EXISTS (AUT-PD-142, filed 2026-08-28 by CYC-0070-ba841eee, fixed 2026-09-01). The
splitter's opener class was `[A-Z(“"]`, so a sentence that opens with a house callout glyph — ⛔, ⚠,
★, ⭐, ⭑, ✅ — was GLUED to the sentence before it and the pair was reported at their combined
length. Two further openers failed the same way: a section reference (`§4.3's reading …`) and any
sentence whose predecessor ended inside a closer (`… own home.) What holds it …`,
`… EMCs.” So the honest reading …`), because the lookbehind saw `)` and `”` rather than the stop.

⭐ THE TWO DIRECTIONS ARE NOT SYMMETRIC AND THAT IS THE WHOLE SHAPE OF THIS SUITE. Failing to split
OVERSTATES a sentence's length: the screen is stricter than it should be, so nothing is let through.
Splitting where no sentence ends UNDERSTATES a length, and an understated length walks past
`--check` and past `publish_bar.py` clause 7 (`readable_enough_to_review`). So the positive cases
below pin what must break, and the negative cases pin what must NOT — and the negative cases are the
ones that protect the gate.

⛔ THE THIRD DEFECT IS HERE TOO, AND IT WAS HIDDEN BY THE FIRST. The fragment filter required
`[a-z]{3}`, so an ALL-CAPS callout sentence was discarded entirely. While it was glued to a
lowercase neighbour the joined string passed the filter; splitting correctly exposed it and DELETED
it, taking its caution markers with it (measured: `emc-atr-vulnerability-assessment.md` fell 17.1 ->
16.8 markers per 1000 words). A readability fix that silently spends caution is the one outcome the
`scientific-writing` skill §4 exists to prevent, so it is pinned as a test rather than a comment.
"""

from __future__ import annotations

import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))

import lint_readability as LR  # noqa: E402


def _split(text: str) -> list[str]:
    """Sentences of a one-paragraph document, text only."""
    return [s for _, s in LR.sentences(LR.body(text + "\n"))]


def _lengths(text: str) -> list[int]:
    return [len(s.split()) for s in _split(text)]


# ---------------------------------------------------------------------------------------------
# Positive: the openers that MUST break a sentence.
# ---------------------------------------------------------------------------------------------

#: Every glyph the fix handles, one per class, each written as this repository actually writes it.
#: ⛔ A glyph added to `_CALLOUT_OPENERS` without a row here is an unmeasured widening of the
#: splitter, and widening is the unsafe direction.
_GLYPHS = ["⛔", "⚠", "★", "⭐", "⭑", "✅", "✓", "✔", "✗", "✕", "✖", "❌", "◐", "○", "◆",
           "⏸", "⏳", "⚑", "⚙", "⚖", "⚫", "⚪", "🔒", "📦", "📏", "📞", "🗺", "⏱", "✍", "↯"]

_FIRST = "The reagent binds the fusion junction in every well of the matched dose-response panel."
_SECOND = "the second sentence carries its own claim and its own length entirely."


@pytest.mark.parametrize("glyph", _GLYPHS)
def test_a_callout_glyph_opens_a_new_sentence(glyph):
    """⛔ THE DEFECT ITSELF, one row per glyph class. The house style opens an emphatic sentence
    with a glyph on nearly every page of these manuscripts, so this is not an edge case — it is the
    ordinary sentence shape of the corpus."""
    joined = f"{_FIRST} {glyph} {_SECOND.capitalize()}"
    lens = _lengths(joined)
    assert len(lens) == 2, (
        f"`{glyph}` did not open a new sentence: the splitter returned {len(lens)} sentence(s) "
        f"({lens}) for a two-sentence paragraph, so it reports their combined length")
    assert max(lens) < len(joined.split()) - 2, (
        f"`{glyph}` produced a sentence as long as the whole paragraph ({max(lens)}w)")


def test_a_section_reference_opens_a_new_sentence():
    """`§` — named in AUT-PD-142 and hit in `emc-fusion-partner-stratification.md`."""
    lens = _lengths(f"{_FIRST} §4.3's conservative-floor reading is the one the table reports.")
    assert len(lens) == 2, f"a §-opened sentence was glued to its predecessor ({lens})"


@pytest.mark.parametrize("closer,shown", [(")", "own home.)"), ("”", "in EMCs.”"),
                                          ('"', 'in EMCs."'), ("]", "in EMCs.]"),
                                          ("’", "in EMCs.’"), ("'", "in EMCs.'")])
def test_terminal_punctuation_inside_a_closer_still_ends_the_sentence(closer, shown):
    """⛔ The lookbehind used to read the LAST character rather than the stop, so a sentence ending
    inside a quotation or a parenthesis never ended at all."""
    lens = _lengths(f"The screen reports what the {shown} So the honest reading is the shorter one.")
    assert len(lens) == 2, (
        f"a sentence ending in `.{closer}` did not end ({lens}); this is the quotation case the "
        "ledger row names")


def test_an_all_caps_callout_sentence_is_still_measured():
    """⛔⛔ THE REGRESSION THE FIX ITSELF WOULD HAVE INTRODUCED. Splitting correctly exposed the
    all-caps callout sentence to the `[a-z]{3}` fragment filter, which deleted it — and with it two
    caution markers in a real document. A sentence the screen cannot see is a sentence the ceiling
    cannot catch."""
    text = f"{_FIRST} ⚠ THE TIER DOES NOT MOVE, AND NEITHER DOES THE RANK."
    sents = _split(text)
    assert len(sents) == 2, f"the all-caps callout sentence was dropped, not split ({sents})"
    assert any("NEITHER DOES THE RANK" in s for s in sents), (
        "the all-caps callout sentence vanished from the measurement entirely")
    caution = sum(len(LR._CAUTION.findall(s)) for s in sents)
    assert caution >= 2, (
        f"the all-caps sentence's caution markers were lost ({caution} found); 'does not' and "
        "'neither' both live in it")


# ---------------------------------------------------------------------------------------------
# Negative: what must NOT break. ⛔ These are the tests that protect the gate — a false split
# shortens a sentence and a shortened sentence passes a ceiling it should have failed.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("opener,why", [
    ("—", "the em dash is this repository's commonest MID-sentence mark"),
    ("→", "an arrow is an operator, not a sentence opener"),
    ("⇒", "`⇒` reads as 'implies' inside a formula"),
    ("≈", "`≈` prefixes a quantity"),
    ("±", "`±` prefixes a quantity"),
    ("−", "a minus sign prefixes a quantity"),
    ("[", "`[7]` after a stop is a trailing citation, belonging to the sentence BEFORE it"),
])
def test_an_operator_or_a_citation_marker_does_not_open_a_sentence(opener, why):
    joined = f"{_FIRST} {opener} 190 units per day against the published comparator value here."
    lens = _lengths(joined)
    assert len(lens) == 1, (
        f"`{opener}` split a sentence it must not split ({lens}) — {why}. A false split UNDERSTATES "
        "length, which is the direction that lets a long sentence past publish_bar clause 7")


def test_a_glyph_in_the_middle_of_a_sentence_does_not_split_it():
    """`A sequence printed with ⚑ beside it` — the glyph is the subject matter, not a callout."""
    lens = _lengths("A sequence printed with ⚑ beside it carries that verdict wherever it appears.")
    assert len(lens) == 1, f"a mid-sentence glyph was treated as a sentence opener ({lens})"


def test_a_glyph_without_a_preceding_stop_does_not_split():
    """The break requires terminal punctuation BEFORE the whitespace. Splitting on a bare glyph
    would cut mid-clause wherever this repository uses one inline."""
    lens = _lengths("The reagent binds the junction and the parent transcript ⚠ is not engaged.")
    assert len(lens) == 1, f"a glyph with no preceding stop split a sentence ({lens})"


def test_an_abbreviation_still_does_not_end_a_sentence():
    """The `_ABBREV` guard has to survive the new pattern: `i.e. ≈190 ns/day` is one sentence."""
    lens = _lengths("The aggregate throughput is lower than the public edge, i.e. approximately "
                    "190 nanoseconds per day against 498 for the reference system on that card.")
    assert len(lens) == 1, f"an abbreviation ended a sentence ({lens})"


# ---------------------------------------------------------------------------------------------
# The corpus. ⭐ Two sentences that were really in the tree when this was fixed, pinned so the
# regression is a measurement of this repository rather than of a fixture.
# ---------------------------------------------------------------------------------------------

_REAL = (
    "The numbered list lives here so the builder can splice it at the anchor, as it does for the "
    "preprint. ⛔ The banner once claimed machine provenance while no generator existed, so the "
    "file read as machine-derived while being edited by hand and checked by nothing — the citation "
    "checker reads the PREPRINT and reports its references, which is why a green gate said nothing "
    "about the entries below."
)


def test_the_real_corpus_example_is_two_sentences_not_one():
    """⛔ Measured 2026-09-01 in `aso/fusion-junction-aso-journal-references.md`: reported as one
    67-word sentence, which is over the 60-word ceiling. Its real parts are both under it."""
    lens = _lengths(_REAL)
    assert len(lens) == 2, f"the real corpus example still measures as {len(lens)} sentence(s)"
    assert max(lens) <= LR.SENTENCE_CEILING, (
        f"the longer real part is {max(lens)}w, over the {LR.SENTENCE_CEILING}w ceiling — the "
        "example no longer demonstrates an artefact and should be re-chosen")
    assert sum(lens) > LR.SENTENCE_CEILING, (
        "the joined pair is no longer over the ceiling, so this fixture no longer pins the defect")


# ---------------------------------------------------------------------------------------------
# The bar the fix must not have moved. ⛔ A lower count has to come from a corrected COUNT, never
# from a loosened BAR (AUT-PD-142's own instruction, and `scientific-writing` §5).
# ---------------------------------------------------------------------------------------------

def test_the_ceiling_did_not_move_when_the_splitter_was_fixed():
    assert LR.SENTENCE_CEILING == 60, (
        "the splitter fix must not be accompanied by a ceiling change; a lower over-ceiling count "
        "has to come from a corrected count, not a loosened bar")


def test_a_genuinely_long_sentence_is_still_over_the_ceiling(tmp_path):
    """The positive control for the whole fix: correcting the splitter must not blind the screen."""
    doc = tmp_path / "long.md"
    doc.write_text("word " * 61 + "end.\n", encoding="utf-8")
    m = LR.measure(str(doc))
    assert m["over_ceiling"] == 1, f"a 61-word sentence stopped tripping the ceiling ({m})"


def test_every_declared_opener_glyph_is_covered_by_a_case():
    """⛔ THE ONE-OF-A-PAIR GUARD. `_CALLOUT_OPENERS` and `_GLYPHS` above are a pair; a glyph added
    to the splitter and not to the suite is an unmeasured widening in the unsafe direction."""
    missing = [g for g in LR._CALLOUT_OPENERS if g not in _GLYPHS]
    assert not missing, (
        f"these openers are in the splitter and in no test: {missing!r}. Add a row to _GLYPHS in "
        "the same commit that widens the splitter")


def test_the_splitter_pattern_still_requires_a_terminal_stop():
    """⛔ The single most damaging loosening available here is dropping the `(?<=[.!?])` guard so
    that a glyph anywhere splits. That would cut mid-clause and understate every length it touched.
    Asserted against the compiled pattern because a behavioural test cannot see a pattern that is
    permissive in a way no fixture happens to exercise."""
    assert "(?<=[.!?])" in LR._SENTENCE_SPLIT.pattern, (
        "the splitter no longer requires terminal punctuation before a break")
    assert re.search(r"\\s\+", LR._SENTENCE_SPLIT.pattern), (
        "the splitter no longer requires whitespace at the break, so it can cut inside a token")
