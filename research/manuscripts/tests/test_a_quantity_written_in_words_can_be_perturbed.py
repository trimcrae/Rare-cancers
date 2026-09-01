"""AUT-PD-148 — a quantity written in words was unfalsifiable by construction.

⛔⛔ THE DEFECT, MEASURED 2026-09-01 ON THE TREE AT `bd8aac753`. `claim_ablation.ablate` perturbed
digit runs and nothing else, so a censused sentence stating its quantity in words came back
`not-applied — the sentence states no number`. That is not "this claim is unwatched"; it is the
instrument declining to look. The gate above it carried the SAME rule a second time —
`_sample` selected on `re.search(r"\\d", sentence)` — so such a sentence was never even offered.

★ THE OBSERVATION THAT DISCRIMINATES, on one sentence of a floored manuscript, same tree, same
interpreter, before and after:

    "*FUS* is a further reported partner, in two of five variant cases in a recent series, and
     supplies eight of the junctions modelled here."

    HEAD          ablate -> not-applied  "the sentence states no number"
    after the fix ablate -> applied      "two -> six"   RED, 25 guard modules noticed

⭐ AND THE RED IS THE POINT. One of those 25 is the guard written for that very clause: it reads the
two and the five out of a committed abstract quotation. So the pre-fix verdict was uninformative in
the direction that matters — the claim is well guarded and the harness could not tell, which is
exactly what the row said would happen.

⚠ WHAT THIS FILE IS NOT. It does not run an ablation: that costs a repository clone and a pytest
subprocess per perturbation, and the gate that pays for it is
`test_the_census_word_covered_survives_ablation.py`. These are the pure-function assertions
underneath it — what counts as a quantity, what a perturbation of one looks like, and that a number
word inside a construct the flattener drops is never touched.
"""
from __future__ import annotations

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import claim_ablation as ca  # noqa: E402
import claim_coverage as cc  # noqa: E402


# ---------------------------------------------------------------------------------------------
# The population predicate — the copy that used to live in the gate as well.
# ---------------------------------------------------------------------------------------------

def test_a_sentence_stating_its_quantity_in_words_states_a_quantity():
    assert ca.states_a_quantity("A further reported partner, in two of five variant cases.")
    assert ca.states_a_quantity("The entire experience is three to five patients with no events.")
    assert ca.states_a_quantity("A threefold difference at the same denominator.")


def test_a_sentence_with_a_digit_still_states_a_quantity():
    assert ca.states_a_quantity("The two junctions account for 68.4% of confirmed cases.")


def test_a_sentence_with_no_quantity_at_all_states_none():
    assert not ca.states_a_quantity("The screens address hybridisation rather than cleavage.")


def test_the_predicate_has_one_home():
    """⛔ THE RULE EXISTED TWICE AND BOTH COPIES HAD TO BE WIDENED. A sentence the gate never offers
    is as unfalsifiable as one the harness cannot perturb, and the second copy is the one that gets
    forgotten — so the gate now asks this function instead of carrying its own regex."""
    gate = io.open(os.path.join(HERE, "test_the_census_word_covered_survives_ablation.py"),
                   encoding="utf-8").read()
    body = gate[gate.index("def _sample("):gate.index("@pytest.mark.parametrize")]
    assert "states_a_quantity" in body, "the gate no longer uses the shared predicate"
    assert 're.search(r"\\d", r["sentence"])' not in body, (
        "the gate has re-grown its own digit-only population rule, so a word quantity is once again "
        "never offered for ablation")


# ---------------------------------------------------------------------------------------------
# The perturbations themselves.
# ---------------------------------------------------------------------------------------------

def test_a_number_word_is_a_perturbation_site():
    span = "in two of five variant cases"
    got = [(before, after) for _s, _e, before, after in ca.perturbations(span, [])]
    assert got == [("two", "six"), ("five", "nine")], got


def test_digits_are_offered_before_words():
    """⛔ ORDER IS LOAD-BEARING. `ablate` stops at the first perturbation that trips a guard, so
    digits first leaves every verdict this harness reached before 2026-09-01 exactly where it was."""
    span = "three of the 190 designs"
    kinds = [before for _s, _e, before, _a in ca.perturbations(span, [])]
    assert kinds == ["190", "three"], kinds


def test_the_swap_preserves_case_and_nothing_else():
    assert ca._match_case("Three", "seven") == "Seven"
    assert ca._match_case("THREE", "seven") == "SEVEN"
    assert ca._match_case("three", "seven") == "seven"


def test_a_longer_number_word_is_never_matched_as_a_shorter_one():
    """⛔ `seventeen` must not be perturbed as `seven` with a stray `teen` left behind — the table
    contains both words and Python's `|` is first-match, not longest-match.

    ⚠ MUTATION-TESTED, AND THE MUTATION SURVIVED, WHICH IS RECORDED RATHER THAN TIDIED AWAY: sorting
    the alternation shortest-first in a scratch copy left all 16 tests green. The property that
    holds this is the `\b` on BOTH sides — `seven` inside `seventeen` fails the trailing boundary —
    not the sort order, and the module's comment was corrected to say so."""
    got = [(before, after) for _s, _e, before, after in ca.perturbations("seventeen arms", [])]
    assert got == [("seventeen", "nineteen")], got
    for compound in ("seventeen", "nineteen", "halfway", "tenure"):
        assert ca._NUMBER_WORD.fullmatch(compound) or not ca._NUMBER_WORD.search(compound), (
            f"{compound} is matched in part rather than whole or not at all")


def test_a_number_word_inside_a_word_is_not_a_quantity():
    """`\\b` anchors: `oneself`, `tenure`, `halfway` state no count."""
    assert ca.perturbations("oneself, tenure and halfway", []) == []


def test_the_replacement_always_changes_the_quantity():
    """A swap to the same value perturbs nothing and would score the sentence blind for free."""
    for word, swap in ca._NUMBER_WORD_SWAP.items():
        assert word != swap, f"{word} is swapped for itself"
        assert swap in ca._NUMBER_WORD_SWAP, (
            f"{word} -> {swap}, which is not itself a number word this module recognises")


def test_a_number_word_inside_a_stripped_construct_is_never_perturbed():
    """⛔⛔ THE FALSE-RED DIRECTION, FOR WORDS. A heading, a table row, a block quote, a fenced block
    and a citation comment are all removed by the flattener, so a number word inside one is not part
    of the claim and mutating it would redden a guard about something else entirely."""
    raw = ("A claim of two cases.\n\n### Section three · Partner prevalence\n\nAnd five more.")
    flat = "A claim of two cases. And five more."
    span = cc.locate(raw, flat).group(0)
    got = [before for _s, _e, before, _a in ca.perturbations(span, cc.stripped_spans(span))]
    assert got == ["two", "five"], got


# ---------------------------------------------------------------------------------------------
# The status a reader can count — AUT-PD-148 asked for this before it asked for the mutation.
# ---------------------------------------------------------------------------------------------

def test_quantity_kind_separates_the_three_populations():
    assert ca.quantity_kind("in two of five variant cases", []) == ca.WORDS
    assert ca.quantity_kind("68.4% of confirmed cases", []) == ca.DIGITS
    assert ca.quantity_kind("three of the 190 designs", []) == ca.BOTH
    assert ca.quantity_kind("hybridisation rather than cleavage", []) == ca.NONE


def test_a_sentence_with_no_quantity_is_still_not_applied():
    """⛔ THE FIX MUST NOT INVENT A PERTURBATION WHERE THERE IS NO QUANTITY. `not-applied` on a
    predicate sentence is the honest answer and stays; what changed is which sentences reach it."""
    assert ca.perturbations("The screens address hybridisation rather than cleavage.", []) == []


# ---------------------------------------------------------------------------------------------
# The verdict must say how much of its witness set could run.
# ---------------------------------------------------------------------------------------------

def test_a_verdict_states_how_much_of_its_witness_set_could_run():
    """⛔⛔ MEASURED THIS SESSION AND IT NEARLY COST A FALSE FINDING. `_witness_cmds` runs
    `sys.executable -m pytest`, so a driver interpreter without pytest reddens EVERY pytest witness
    at baseline. `_baseline_reds` then subtracts 25 of 26 commands — the all-red bailout needs 26 of
    26 — and `ablate` returns a full APPLIED/BLIND verdict computed from the one survivor. A reader
    of that BLIND is told "no guard noticed" about guards that were never in a position to notice.

    ★ MEASURED, BOTH READINGS, ON ONE SENTENCE OF A FLOORED MANUSCRIPT:
        under /usr/local/bin/python3 (no pytest)   26 commands, 25 already red  -> BLIND
        under the interpreter that has pytest       26 commands,  1 already red  -> RED, "two -> six"
    """
    assert ca.subtraction_note(26, 0) == "", "a fully green baseline should add no clause"
    note = ca.subtraction_note(26, 25)
    assert "25 of 26" in note and "rests on 1 of them" in note, note


def test_the_subtraction_note_reaches_a_blind_verdict():
    """The clause is worth nothing if `ablate` does not append it to the reason a reader sees."""
    src = io.open(os.path.join(os.path.dirname(HERE), "claim_ablation.py"), encoding="utf-8").read()
    assert '"baseline": baseline' in src, "an ablation verdict no longer carries its baseline"
    assert '", ".join(tried) + subtracted' in src, (
        "the blind reason no longer carries the subtraction note")


# ---------------------------------------------------------------------------------------------

def test_this_module_names_no_censused_document():
    """⛔⛔ REFLEXIVE. `claim_coverage._test_patterns` credits a test module's string literals to
    every document whose basename appears anywhere in its source, and `claim_ablation.guards_reading`
    re-runs any module that names one. A file full of example sentences that typed a manuscript
    filename would change the counts it is written to defend, and would be re-run inside every
    ablation clone."""
    src = io.open(os.path.abspath(__file__), encoding="utf-8").read()
    named = sorted({os.path.basename(p) for p in cc.PAPERS if os.path.basename(p) in src})
    assert not named, (
        f"this module names {named}, so its literals are now credited as coverage of those "
        f"documents — describe the sentence instead of naming its file")
