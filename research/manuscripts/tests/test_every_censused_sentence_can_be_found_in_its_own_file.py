#!/usr/bin/env python3
"""AUT-PD-132 — a censused sentence the harness cannot find is a claim nothing can test.

⛔⛔ THE HOLE, MEASURED 2026-08-28. `claim_ablation` perturbs a sentence in a clone and asks whether
any guard notices. To perturb it, it must first FIND it in the raw file — and for 22 of the 238
covered sentences across four documents it could not, because the locator tolerated only the line
wrapping `_prose` removes, while `_prose` also strips `<!--…-->`, `<sup>…</sup>` and whole heading,
table, quote and fence lines. Those sentences came back NOT_APPLIED: counted as covered, perturbed by
nothing, and never reported as a gap because the gate asserts only that SOMETHING was applied.

★ AND THE SELECTION WAS THE WORST POSSIBLE ONE. The gap between two surviving tokens is where a
citation marker lives, so the sentences the harness could not test were the CITED ones — the
best-evidenced claims in the paper, including a pinned figure:

    after "…breakpoint distribution of an 18-case series,"
      raw: '<sup>16</sup><!--PMID:12378528--> the two junctions account for 68.4%…'

⛔ THIS FILE IS THE FLOOR THAT MAKES THE HOLE VISIBLE. The ablation gate samples; this does not. It
asks one question of every covered sentence in every censused document, in about a second, with no
clone and no subprocess: can the harness find you at all?
"""

from __future__ import annotations

import io
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import claim_coverage as cc  # noqa: E402


@pytest.mark.parametrize("key", sorted(cc.PAPERS))
def test_every_covered_sentence_is_findable_in_its_own_raw_file(key):
    """⛔⛔ THE REGRESSION. Before the fix this failed for four documents at once — 11 sentences in
    the ASO journal article, 7 in the fusion-partner synthesis, 3 of the 7 in the response-endpoint
    note and 1 in the vaccine path."""
    raw = io.open(cc.PAPERS[key], encoding="utf-8").read()
    missing = [r["sentence"] for r in cc.census(key)
               if r["covered"] and cc.locate(raw, r["sentence"]) is None]
    assert not missing, (
        f"{len(missing)} covered sentence(s) in {os.path.basename(cc.PAPERS[key])} cannot be found "
        f"in the raw file, so `claim_ablation` can never perturb them and they are counted as "
        f"watched while being tested by nothing. Fix the locator or the flattener — never the "
        f"census — starting with: {missing[0][:120]!r}")


# ---------------------------------------------------------------------------------------------
# One test per construct `_prose` removes. Each is a way a sentence can go silently untestable.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("gap,what", [
    ("<sup>16</sup>", "a citation superscript — the one that hid the pinned 68.4% figure"),
    ("<!--PMID:12378528-->", "a PMID comment"),
    ("<sup>16</sup><!--PMID:12378528-->", "both, adjacent, which is the real shape in these files"),
    ("\n\n## Abstract\n\n", "a heading line, dropped whole"),
    ("\n\n### 3.5 · Partner prevalence\n\n", "a numbered heading with the repository's separator"),
    ("\n\n| document | why |\n|---|---|\n", "a table"),
    ("\n\n> a pulled quote\n\n", "a block quote"),
    ("\n```\n", "a fence MARKER line — see the test below for what a fence does NOT drop"),
    ("\n", "the plain line wrap the old locator already handled"),
])
def test_a_sentence_spanning_a_stripped_construct_is_still_found(gap, what):
    raw = f"The two junctions account for 68.4%{gap} of molecularly confirmed cases."
    flat = "The two junctions account for 68.4% of molecularly confirmed cases."
    m = cc.locate(raw, flat)
    assert m is not None, f"a sentence spanning {what} could not be located"
    assert m.group(0).startswith("The two junctions")


def test_the_dropped_line_branch_is_multiline_scoped():
    """⚠ THE BUG INSIDE THE FIX, CAUGHT BY MEASURING RATHER THAN BY READING. `_COMMENT` and `_SUP`
    are compiled `re.S`; `_DROPPED_LINE` is compiled `re.M`. The first version of `_GAP` inlined all
    three patterns but scoped only the first two, so `^`/`$` in the dropped-line branch anchored to
    the ends of the WHOLE FILE and matched nothing — 9 of the 15 sentences stayed unlocatable, every
    one across a heading, a table or a quote. A pattern inlined without its flags is a different
    pattern."""
    assert "(?m:" in cc._GAP, "the dropped-line branch lost its multiline scope"
    assert cc._GAP.count("(?s:") == 2, "the comment and sup branches must keep dot-all"


# ---------------------------------------------------------------------------------------------
# ⛔ The match is verified, not trusted — a locator that wanders is worse than one that fails.
# ---------------------------------------------------------------------------------------------

def test_a_sentence_that_is_not_there_is_not_found():
    assert cc.locate("The two junctions account for 68.4%.", "The three junctions account") is None


def test_the_returned_span_reflattens_to_exactly_the_sentence():
    """★ THE GUARANTEE THAT MAKES THE TOLERANT PATTERN SAFE. `ablate` mutates whatever span comes
    back, so a span that merely CONTAINS the sentence would corrupt a neighbouring claim."""
    raw = ("Junction A holds.\n\n## Heading\n\nThe two junctions account for 68.4%"
           "<sup>16</sup> of cases.\n\nJunction B holds.")
    flat = "The two junctions account for 68.4% of cases."
    m = cc.locate(raw, flat)
    assert m is not None
    assert cc._flatten(m.group(0)) == flat
    assert "Junction A" not in m.group(0) and "Junction B" not in m.group(0)


def test_an_empty_sentence_finds_nothing_rather_than_everything():
    assert cc.locate("anything at all", "") is None


def test_the_ablation_harness_uses_this_locator():
    """⛔ ONE LOCATOR, NEXT TO THE FLATTENER IT INVERTS. Two copies drift, and the copy that drifts
    is the one nobody is testing."""
    sys.path.insert(0, os.path.dirname(HERE))
    import claim_ablation as ca
    raw = "The two junctions account for 68.4%<sup>16</sup> of cases."
    assert ca._locate(raw, "The two junctions account for 68.4% of cases.") is not None


def test_fence_CONTENT_is_prose_to_the_flattener_and_that_is_a_separate_defect():
    """⚠ FOUND BY THIS FILE'S OWN FIRST DRAFT, WHICH ASSUMED A FENCED BLOCK WAS DROPPED WHOLE.

    `_prose` drops lines STARTING WITH ``` and keeps everything between them, so a code block's
    contents are flattened into claim prose and can be censused as a sentence. Three censused
    documents carry fences today, `emc-fusion-partner-stratification.md` among them. That is filed
    as its own row rather than fixed here: changing what `_prose` keeps moves `covered` for every
    document and every floor that holds one, which is the blast radius `claim_coverage` already
    records for the pattern-narrowing question.
    ⛔ THE TEST PINS THE CURRENT BEHAVIOUR SO THE FIX IS A DELIBERATE CHANGE WITH THIS ASSERTION
    FAILING, not a silent shift in what counts as a claim.
    """
    assert cc._flatten("A claim.\n\n```\nsome code line\n```\n\nmore claim.") == (
        "A claim. some code line more claim.")


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE FALSE *RED* THE TOLERANT LOCATOR MADE POSSIBLE, AND THE HALF THAT LIES REASSURINGLY.
# ---------------------------------------------------------------------------------------------

def test_a_citation_marker_inside_the_span_is_never_perturbed():
    """⛔⛔ THE DANGEROUS DIRECTION. Once the locator could match across a stripped construct, the
    span handed to `ablate` could contain `<sup>16</sup>` and `<!--PMID:12378528-->`. `ablate`
    perturbs every digit run in the span it is given, so it would have mutated a CITATION NUMBER,
    watched a citation guard go red, and reported the sentence bound — while the claim's own number
    stayed unwatched. A false BLIND wastes a session; a false RED retires a real gap.
    """
    import re
    raw = "The two junctions account for 68.4%<sup>16</sup><!--PMID:12378528--> of 58 cases."
    flat = "The two junctions account for 68.4% of 58 cases."
    span = cc.locate(raw, flat).group(0)
    skip = cc.stripped_spans(span)
    runs = [m.group(0) for m in re.finditer(r"\d+", span)
            if not any(s <= m.start() < e for s, e in skip)]
    assert runs == ["68", "4", "58"], f"perturbable runs were {runs}"
    assert "16" not in runs, "a citation superscript is perturbable — a false RED is now possible"
    assert "12378528" not in runs, "a PMID comment is perturbable — same defect, worse identifier"


def test_a_number_inside_a_dropped_heading_is_never_perturbed():
    """The span can now cross `### 3.5 · …`. Mutating that 3 or 5 changes a heading, not a claim."""
    import re
    raw = "A claim of 12 cases.\n\n### 3.5 · Partner prevalence\n\nAnd 34 more."
    flat = "A claim of 12 cases. And 34 more."
    span = cc.locate(raw, flat).group(0)
    skip = cc.stripped_spans(span)
    runs = [m.group(0) for m in re.finditer(r"\d+", span)
            if not any(s <= m.start() < e for s, e in skip)]
    assert runs == ["12", "34"], f"perturbable runs were {runs}"


def test_stripped_spans_reports_nothing_for_plain_prose():
    assert cc.stripped_spans("The two junctions account for 68.4% of cases.") == []
