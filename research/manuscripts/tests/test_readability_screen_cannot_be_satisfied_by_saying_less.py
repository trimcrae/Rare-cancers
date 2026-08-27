#!/usr/bin/env python3
"""The readability screen's safety properties.

⛔ THE THREAT MODEL IS NOT "the tool miscounts". It is that a loop optimising a readability number
finds the cheapest path to it, and the cheapest path is DELETING THE DIFFICULT SENTENCE. Every test
here is a case where the screen must refuse to reward that, or must refuse to lie about what it
measured.

★ Two of them are regressions from bugs this module actually had on its first two runs, both in the
extractor, and in OPPOSITE directions — one manufactured a 108-word sentence that did not exist, the
other erased every long sentence in the corpus by splitting at line wraps. The erasing kind shipped
green.
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import lint_readability as LR  # noqa: E402


def _measure(tmp_path, text, name="doc.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return LR.measure(str(p))


# ---------------------------------------------------------------------------------------------
# The extractor. Both directions, both measured.
# ---------------------------------------------------------------------------------------------

def test_a_hard_wrapped_sentence_is_measured_whole(tmp_path):
    """⛔⛔ THE BUG THAT SHIPPED GREEN. These manuscripts wrap at ~100 columns. Splitting per LINE
    reported the published ASO article as 359 sentences of mean 11.8 words with NOTHING over the
    ceiling — a screen that would have called the very paper that prompted it exemplary."""
    wrapped = (
        "The selectivity ratio is the wild-type concentration divided by the fusion's, taken\n"
        "from a matched dose-response in the same wells, at a cut of five adopted as a\n"
        "convention rather than measured, and it is the margin assessment the published\n"
        "recommendations specify at this stage of a programme like this one.\n"
    )
    m = _measure(tmp_path, wrapped)
    assert m["sentences"] == 1, f"a wrapped sentence was split at its line breaks ({m['sentences']} found)"
    assert m["max_len"] > 40, (
        f"the wrapped sentence measured only {m['max_len']} words; line wraps are being treated as "
        "sentence boundaries, which erases exactly the sentences this screen exists to find")


def test_a_horizontal_rule_is_a_hard_boundary(tmp_path):
    """The opposite bug: a `Keywords.` line glued across a `---` to the next paragraph produced a
    phantom 108-word sentence. A gate that flags a sentence which does not exist teaches the reader
    to distrust it."""
    m = _measure(tmp_path, "Keywords. antisense oligonucleotide; gapmer; RNase-H1.\n\n---\n\n"
                           "EMC is defined in most cases by an in-frame fusion of one gene to another.\n")
    assert m["max_len"] < 25, f"text was joined across a horizontal rule (longest {m['max_len']}w)"


def test_citation_markup_is_not_counted_as_words(tmp_path):
    """⚠ A RED ON TRUE INPUT IS WORSE THAN A GREEN ON FALSE INPUT, because the first thing anyone
    does is loosen it. Counting `<sup>23</sup>` and `<!--PMID:29937513-->` as words would flag
    sentences for the crime of carrying citations."""
    bare = "The fusion is present in most tumours of this type and defines the disease.\n"
    cited = ("The fusion is present in most tumours<sup>23</sup><!--PMID:29937513--> of this "
             "type and defines the disease.<sup>16</sup><!--PMID:36103645-->\n")
    assert _measure(tmp_path, bare)["max_len"] == _measure(tmp_path, cited, "b.md")["max_len"], (
        "citation markup changed the measured sentence length")


def test_frontmatter_tables_and_appendices_are_not_prose(tmp_path):
    doc = ("---\ntitle: a very long frontmatter title that would otherwise count as a sentence here\n---\n\n"
           "The reagent works.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
           "## Appendix A\n\nThis superseded sentence in the appendix must not be measured at all.\n")
    m = _measure(tmp_path, doc)
    assert m["sentences"] == 1, f"non-prose was measured as prose ({m['sentences']} sentences)"


# ---------------------------------------------------------------------------------------------
# The safety property: you cannot pass by saying less.
# ---------------------------------------------------------------------------------------------

_LONG = ("The panel screen may indicate that a design is not established as selective, and no "
         "difference was demonstrated between the two arms, which is a limitation we do not "
         "resolve here, although the point estimate could favour one arm at 95% CI and we did "
         "not test the alternative, so the reading is preliminary and unverified throughout.\n")


def test_splitting_a_long_sentence_keeps_every_caution_marker(tmp_path):
    """★ THE MOVE THE SKILL ASKS FOR IS SAFE, AND THIS PROVES IT RATHER THAN ASSERTING IT.
    Splitting moves words; it does not remove qualifications."""
    split = ("The panel screen may indicate that a design is not established as selective. "
             "No difference was demonstrated between the two arms. That is a limitation we do "
             "not resolve here. The point estimate could favour one arm at 95% CI. We did not "
             "test the alternative, so the reading is preliminary and unverified throughout.\n")
    before, after = _measure(tmp_path, _LONG), _measure(tmp_path, split, "after.md")
    assert after["max_len"] < before["max_len"], "the split did not shorten the longest sentence"
    assert after["caution_markers"] >= before["caution_markers"], (
        f"splitting lost caution ({before['caution_markers']} -> {after['caution_markers']}); the "
        "marker set is too fragile to protect the thing it exists to protect")


def test_deleting_the_qualification_is_visible_as_a_caution_drop(tmp_path):
    """⛔⛔ THE FAILURE MODE THIS WHOLE MODULE EXISTS FOR. The 'improved' text below is shorter,
    reads better, and is OVERSTATED. The screen must be able to see that."""
    gutted = "The panel screen shows the design is selective, and one arm is favoured.\n"
    before, after = _measure(tmp_path, _LONG), _measure(tmp_path, gutted, "after.md")
    assert after["max_len"] < before["max_len"], "precondition: the gutted text is shorter"
    assert after["caution_markers"] < before["caution_markers"], (
        "deleting every hedge, null and limitation did not register as a caution drop — the check "
        "that stops a readability pass from buying clarity with honesty is blind")


# ---------------------------------------------------------------------------------------------
# The gate's own contract.
# ---------------------------------------------------------------------------------------------

def test_check_fails_a_sentence_over_the_ceiling(tmp_path, monkeypatch):
    doc = tmp_path / "over.md"
    doc.write_text("word " * (LR.SENTENCE_CEILING + 5) + "end.\n", encoding="utf-8")
    monkeypatch.setattr(LR, "_load_baseline", dict)
    assert LR.main(["--check", str(doc)]) == 1


def test_check_passes_a_short_document(tmp_path, monkeypatch):
    """The positive control. Without it the suite would pass on a gate that fails everything."""
    doc = tmp_path / "ok.md"
    doc.write_text("The reagent binds the junction. It does not bind the parent transcript.\n",
                   encoding="utf-8")
    monkeypatch.setattr(LR, "_load_baseline", dict)
    assert LR.main(["--check", str(doc)]) == 0


def test_check_fails_when_caution_falls_below_the_pinned_baseline(tmp_path, monkeypatch):
    """⛔ The ratchet. A document may become more readable; it may not become less careful."""
    doc = tmp_path / "gutted.md"
    doc.write_text("The design is selective and one arm is favoured.\n", encoding="utf-8")
    monkeypatch.setattr(LR, "_load_baseline", lambda: {str(doc): 999.0})
    assert LR.main(["--check", str(doc)]) == 1, (
        "a collapse in caution against the pinned baseline did not fail the check")


def test_the_report_never_fails_the_build(tmp_path):
    """⛔ A BAD SCORE IS ADVISORY, BY DESIGN. Gating on a mean would instruct this loop to shorten
    sentences by any means available, and the cheapest means is deletion (Goodhart)."""
    doc = tmp_path / "awful.md"
    doc.write_text("word " * 200 + "end.\n", encoding="utf-8")
    assert LR.main(["--report", str(doc)]) == 0, (
        "the report failed the build on a score; that turns the screen into a target")


# ---------------------------------------------------------------------------------------------
# Survivors of the first mutation run, pinned here. Both had a comment claiming to prevent them
# and no test measuring it — "writing 'do not raise this' above a constant does not bind it".
# ---------------------------------------------------------------------------------------------

def test_the_ceiling_itself_is_pinned(tmp_path, monkeypatch):
    """⛔⛔ THE MUTATION MOST LIKELY TO BE MADE IN GOOD FAITH: raise SENTENCE_CEILING until the
    document passes.

    ⚠ Found surviving a mutation run: every ceiling test built its document as `CEILING + 5` words,
    so the constant could be set to 100000 and the whole suite stayed green. A test that scales with
    the thing it is checking measures nothing about it. The value is asserted CONCRETELY, and the
    fixture below is 61 words regardless of what the constant says.
    """
    assert LR.SENTENCE_CEILING == 60, (
        "the sentence ceiling moved. That is allowed — but it is a deliberate act with a reason, not "
        "a way to make a red document green. Change this assertion in the same commit and say why.")
    doc = tmp_path / "sixtyone.md"
    doc.write_text("word " * 61 + "end.\n", encoding="utf-8")
    monkeypatch.setattr(LR, "_load_baseline", dict)
    assert LR.main(["--check", str(doc)]) == 1, "a 61-word sentence did not trip the 60-word ceiling"


def test_a_rule_with_no_blank_lines_still_breaks_the_paragraph(tmp_path):
    """The tight `---` case. The earlier boundary test surrounded the rule with blank lines, which
    already separate paragraphs, so it passed whether or not the rule itself was a boundary."""
    m = _measure(tmp_path,
                 "Keywords. antisense oligonucleotide; gapmer; RNase-H1; fusion transcript\n"
                 "---\n"
                 "EMC is defined in the large majority of cases by an in-frame fusion of one gene.\n")
    assert m["max_len"] < 20, (
        f"text was joined across a tight horizontal rule (longest {m['max_len']}w) — this is how a "
        "phantom 108-word sentence was manufactured in the first place")
