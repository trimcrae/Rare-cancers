#!/usr/bin/env python3
"""⛔⛔ A LENGTH CEILING THAT ONLY EVER RATCHETS DOWN, BECAUSE "CORRECTIONS REPLACE" WAS WRITTEN
DOWN FOR NINE DAYS AND MEASURED BY NOTHING.

★ trimcrae, 2026-08-31, on being shown the paper at eight pages against a ceiling of seven:
*"If we are going from 6 pages to 8 pages, that's a 33% increase just in response to reviewer
feedback. That's clearly over hedging and scope creep. Not only should we aggressively cut the fat,
we need to be more strict in our process about adding more length to satisfy one of our internal
reviewers."*

⚠ WHAT IT COST, MEASURED TWICE ON THIS ONE PAPER.
  · Rounds 8-13: main text 2,914 -> 5,976 words, MONOTONICALLY — not one round shrank it. Every P1
    was closed by APPENDING a qualifying clause instead of editing the sentence that was wrong, so
    the curve could not do anything but rise. §5 reached 1.89x §3 in a paper where §3 carries the
    result.
  · Round 9 on the condensed article: eight suggestions applied as blockers took it 4,614 -> 5,563
    words and six typeset pages -> eight, against a hard 6-page budget. An hour then went into
    cutting cited case reports and coverage arithmetic to FUND additions that should not have been
    made. Every individual cut looked defensible.
  · Round 26, 2026-08-31 — the one that produced this file. Two genuine corrections were written as
    EXPANSIONS ("covers every position of GRCh38" -> "covers GRCh38 end to end, skipping only
    windows that carry an ambiguous base"), costing 13 words and, through re-wrapping, a page.
    Rewritten as REPLACEMENTS ("covers unambiguous GRCh38") the same corrections came in 11 words
    SHORTER than the text they replaced. ★ The finding was never the problem. The prose was.

★★ SO THE RULE `paper-hardening` §1 ALREADY STATES — *"a correction REPLACES text; it does not
append to it"* — IS ENFORCED HERE RATHER THAN TRUSTED. It is the fifth rule in this repository found
to be correct, load-bearing and measured by nothing (`subagent_width`, `fleet_armed.CENSUS_LANE`,
the escalation debt, the merge debt, this).

⛔ WHAT THIS IS NOT: A VENUE LIMIT. `test_the_journal_pdf_fits_its_page_budget.py` owns the 6-page
NAT requirement and its declared overage. This is a RATCHET on the repository's own process: the
paper may shrink freely and may not grow, whatever the venue allows. An uncapped venue (aiXiv caps
nothing) does not license padding — `paper-hardening` §1 says so in those words.

★ HOW TO CHANGE A CEILING, AND THE TWO DIRECTIONS ARE NOT SYMMETRIC.
  · DOWN — after a real cut, lower it here in the same commit. That is the ratchet working, and it
    needs no permission.
  · UP — only when trimcrae has said this paper may get longer, recorded in
    `research/autonomy/amendments.jsonl` like any other governed change. ⛔ NEVER raise it to make a
    round's edit fit: that is the self-serving amendment `amendment_guard` exists to catch, and it
    is exactly how "over hedging and scope creep" happened twice already.
"""
from __future__ import annotations

import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
ASO = os.path.join(MANUSCRIPTS, "aso")

#: ⛔ CEILINGS, NOT TARGETS: the main-text word count may fall freely and may not rise.
#: Measured with `research/manuscripts/submission_metrics.py`, which is the one home of the counting
#: rule — this file re-implements none of it.
#: ⚠ THE HEADROOM IS DELIBERATE AND SMALL. A ceiling set exactly at today's count reds on a
#: one-word clarification, and a gate that reds on true input is one its reader learns to loosen
#: (`paper-hardening` §8b.1). A ceiling set far above it measures nothing. Twenty words is about
#: half a typeset line in this two-column layout: enough to reword a sentence, not enough to add a
#: paragraph of hedging, which is the thing being prevented.
_HEADROOM = 20

WORD_CEILING = {
    #: ⭐ SET 2026-08-31 at 3,799 words, the count after round 26's corrections were rewritten as
    #: replacements and the accumulated duplication was cut. ⚠ THAT IS 93 WORDS BELOW THE ROUND-26
    #: PIN (3,886 at 7a7f40825) — the round REDUCED the paper, which is the direction §1 asks for
    #: and the first round in this series to achieve it.
    #: What came out, so a later reader can tell fat from evidence: the cited framework's five-step
    #: enumeration (its verbatim is in `lit-targets-aso-instruments.json`, so nothing left the
    #: record); three restatements in the Introduction; and the THIRD copy of one concession, which
    #: the abstract and the Methods both still carry and both still bind.
    #: ⛔ NO BOUND, INTERVAL, CONDEMNATION OR CONCESSION WAS REMOVED. If one ever is, it is a finding
    #: in its own right and is named here (`paper-hardening` §1, class 4).
    "fusion-junction-aso-journal-article.md": 3799 + _HEADROOM,
}


def _main_text_words(rel):
    """The main-text word count, taken from `submission_metrics.measure` and NOT re-implemented.

    ⛔ THE FIRST VERSION OF THIS FILE COUNTED ITS OWN WAY AND GOT 4,120 WHERE THE REPOSITORY'S
    COUNTER GETS 3,793 — an 8.6% disagreement, because a naive split over the same span counts
    HTML comment markers, superscript tags and heading text that `submission_metrics` strips. A
    ceiling set against a second counter is a ceiling on a quantity nobody reports, and the venue
    limit, the metrics artifact and this gate would have drifted independently.
    ★ CLAUDE.md rule 1: one fact, one place. The counting rule has a home; this reads it.
    """
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location(
        "_submission_metrics_for_ceiling", os.path.join(MANUSCRIPTS, "submission_metrics.py"))
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 — a missing counter is a failure, never a skip
        pytest.fail(
            "submission_metrics.py is not importable, so the paper's length is UNMEASURED and this "
            f"ceiling is not a gate. Install rather than skip: {exc}")
    measured = module.measure(os.path.join(ASO, rel))["main_words"]
    assert isinstance(measured, int) and measured > 500, (
        f"submission_metrics reports {measured!r} main-text words for {rel}, which is not a "
        "plausible count for this paper — the ceiling below would be meaningless against it")
    return measured


@pytest.mark.parametrize("rel", sorted(WORD_CEILING))
def test_the_paper_has_not_grown_past_its_ceiling(rel):
    """⛔⛔ THE PROPERTY. A hardening round may shrink this paper and may not grow it."""
    words = _main_text_words(rel)
    ceiling = WORD_CEILING[rel]
    assert words <= ceiling, (
        f"{rel} is {words} words of main text against a ceiling of {ceiling} "
        f"({words - ceiling} over).\n"
        "⛔ DO NOT RAISE THE CEILING TO FIT THE EDIT. That is the self-serving amendment this file "
        "exists to catch, and it is how this paper went 2,914 -> 5,976 words over six rounds and "
        "6 -> 8 pages over one.\n"
        "★ THE FIX IS ALMOST ALWAYS THE SAME ONE, and it worked on every correction in round 26: "
        "write the correction as a REPLACEMENT for the sentence that is wrong, not as a qualifier "
        "appended to it. Round 26's two corrections came in 11 words SHORTER that way than the "
        "text they replaced, having cost 13 words and a whole page as appended clauses.\n"
        "★ If the paper genuinely needs to be longer, that is trimcrae's call — record it in "
        "research/autonomy/amendments.jsonl and raise the ceiling in the same commit.")


@pytest.mark.parametrize("rel", sorted(WORD_CEILING))
def test_the_ceiling_has_not_drifted_far_above_the_paper(rel):
    """★ THE OTHER DIRECTION, AND IT IS THE ONE A RATCHET ROTS BY. A ceiling left far above a paper
    that has since been cut measures nothing while still reporting green — the coverage ratchet's
    own failure mode, one axis over. After a real cut, lower the ceiling in the same commit."""
    words = _main_text_words(rel)
    ceiling = WORD_CEILING[rel]
    assert ceiling - words <= 200, (
        f"{rel} is {words} words against a ceiling of {ceiling}, {ceiling - words} of headroom. "
        "The paper has been cut and the ceiling was not lowered with it, so this gate is now "
        "reporting green over a gap a whole round's worth of padding would fit inside. Lower "
        f"WORD_CEILING to {words + _HEADROOM} in the commit that made the cut.")


def test_the_ceiling_would_actually_stop_a_round_that_padded_the_paper():
    """⛔⛔ THE POSITIVE CONTROL, AND WITHOUT IT THIS FILE IS THREE ASSERTIONS ABOUT A NUMBER.

    A ceiling passes when the paper is short enough. So does a ceiling wired to nothing, a ceiling
    whose counter silently returns 0, and a ceiling set at a million. `paper-hardening` §8b: an
    instrument is a new unmeasured claim until something perturbs it — and this repository has
    already shipped a coverage census that reported 100% because its patterns matched everything,
    and a mutation harness that reported clean runs because no file was ever edited.

    ⚠ PERTURB THE MEASUREMENT, NOT THE MANUSCRIPT. Round 26 mutated the live article to test a
    guard and had to restore it byte for byte; CLAUDE.md §6 requires a copy. Here nothing needs
    copying at all — the quantity under test is a word count, so a padded count is the honest
    perturbation and no file is touched.
    """
    rel = "fusion-junction-aso-journal-article.md"
    ceiling = WORD_CEILING[rel]
    real = _main_text_words(rel)
    assert real <= ceiling, "precondition: the real paper is inside its ceiling"

    #: One round of the failure this file exists to prevent: ~120 words of appended qualifying
    #: clauses, which is roughly what round 9 added to this same paper in one sitting.
    padded = real + 120
    assert not padded <= ceiling, (
        f"a paper {padded - real} words longer than today's would still pass a ceiling of "
        f"{ceiling}, so this gate would not have caught round 9 (which added 949 words) or round "
        "26 (which added 13 words and a page). The ceiling has too much headroom to bind")

    #: And the other direction, so the ceiling is not merely large-and-loose: a paper that has been
    #: legitimately CUT must still pass, or the gate reds on the outcome it is asking for.
    assert real - 200 <= ceiling, "a shorter paper must still pass; this gate forbids growth only"
