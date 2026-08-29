"""A quantity written out in words is unfalsifiable by the ablation harness. Count it, do not fake it.

⛔⛔ THE DEFECT, FOUND 2026-08-28 BY READING A BLIND VERDICT INSTEAD OF TRUSTING IT (AUT-PD-148).
`claim_ablation.ablate` perturbs digit runs and nothing else. A sentence whose real claim is
"three to five patients with no events" contains digits only inside an identifier and a list marker,
so the harness moved those, reported a verdict about them, and said nothing whatever about the
quantity a reviewer would check first. Re-measured 2026-08-29 on the sentence that found it: the
digit runs are the `15` of a gene name and the `1` of a numbered list.

★★ BOTH VERDICTS LIE ABOUT SUCH A SENTENCE, IN OPPOSITE DIRECTIONS, WHICH IS WHY "IT IS ONLY BLIND"
IS NOT AN ANSWER:

  BLIND on the digits   reads as "no guard watches this claim" — nothing touched the claim.
  RED on the digits     reads as "this claim is watched" — an exon number moved, not the quantity.
                        This is the reassuring direction, and therefore the dangerous one.

⛔⛔ AND THE OBVIOUS FIX IS THE TRAP. Teaching the mutator to rewrite number words would make more
sentences pass ablation without binding one extra claim, so the census would report coverage it
never won — a guard that appears to cover more because its mutator got noisier is worse than the gap
it replaced — and it would rewrite prose into nonsense on the way ("ten null ensembles" -> "seven
null ensembles" is a sentence, not a test). So NOTHING was widened. The population is COUNTED
instead: `claim_coverage.quantity_words` names the words, every `ablate` return carries them, and
`claim-coverage.json` reports three per-document fields. Measured 2026-08-29 over all 32 censused
documents, `sentences`, `covered`, `with_a_number`, `with_a_number_covered`, `uncovered` and
`uncovered_with_a_number` are unchanged to the digit; nothing left the blind list; no floor moved.

⚠ NOTE ON THIS FILE'S OWN LITERALS AND ITS SILENCE ABOUT MANUSCRIPTS. `claim_coverage._test_patterns`
credits a test module's regex-shaped literals to any document whose basename appears in its source,
and `claim_ablation.guards_reading` re-runs such a module inside the ablation clone. Naming a
manuscript here would therefore either inflate that document's coverage with a module that binds
nothing in it, or make the ablation harness re-run a module that performs ablations. The scope is
read from `claim_coverage.COVERAGE_FLOOR` instead, which lives in the census module and is not
scanned for either.
"""
from __future__ import annotations

import os
import re
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import claim_ablation  # noqa: E402
import claim_coverage  # noqa: E402

PAPERS = tuple(claim_coverage.COVERAGE_FLOOR)


def test_the_detector_reads_the_quantity_a_reviewer_would_check():
    """The shape that found the defect, and the shapes around it."""
    assert claim_coverage.quantity_words(
        "the entire experience is three to five patients with zero reported responses"
    ) == ["five", "three", "zero"]
    assert claim_coverage.quantity_words(
        "Ten null ensembles were built as scrambles of each design."
    ) == ["ten"], "a sentence-initial quantity is the same claim as a lower-case one"
    assert claim_coverage.quantity_words(
        "Both reagents sit close to that ten-base-pair criterion."
    ) == ["ten"], "a hyphenated compound states its quantity as plainly as a bare word does"
    assert claim_coverage.quantity_words(
        "The fourth records the longest contiguous duplex six parent transcripts form."
    ) == ["fourth", "six"], "an ordinal is a quantity a reviewer checks"


def test_a_longer_number_word_is_not_shadowed_by_a_shorter_one():
    """⛔ THE ALTERNATION IS ORDERED, SO ONLY THE CLOSING BOUNDARY STOPS `nine` EATING `nineteen`.

    Without it every "nineteen" would be reported as "nine" and every "tenth" as "ten" — a wrong
    word in a field whose whole content is which word the harness could not reach.
    """
    assert claim_coverage.quantity_words("nineteen designs carry a sense-strand near-match") == [
        "nineteen"]
    assert claim_coverage.quantity_words("the tenth ensemble was screened identically") == ["tenth"]
    assert claim_coverage.quantity_words("sixteen of the fifteen thousand records") == [
        "fifteen", "sixteen", "thousand"]


def test_an_identifier_and_a_bare_digit_are_not_word_quantities():
    """⛔ THE FIELD MUST NOT DOUBLE-COUNT WHAT `has_number` ALREADY REPORTS.

    `has_number` is what the harness CAN perturb; this is what it cannot. A sentence stating its
    quantity in digits has no gap here, and reporting one would inflate a gap count — the same
    direction of error, one field over.
    """
    assert claim_coverage.quantity_words("TAF15::NR4A3 was assigned in 23 of 26 cases.") == []
    assert claim_coverage.quantity_words("The 5-6-5 gapmer motif was retained throughout.") == []
    assert claim_coverage.quantity_words("No quantity of any kind is asserted in this clause.") == []


def test_the_pronoun_and_ordering_tokens_are_deliberately_out_of_the_set():
    """⛔ `one`, `first` AND `second` ARE EXCLUDED ON A MEASUREMENT, AND THIS PINS THE DECISION.

    The measurement — how many covered sentences the three tokens add, and how many of those state a
    quantity rather than use a pronoun or an ordering word — has one home, the comment above
    `claim_coverage._QUANTITY_WORDS`, and is not restated here.
    ⚠ THE UNDER-COUNT IS REAL AND IS THE COST: a claim resting on the word "one" is not flagged.
    Widening the set is a legitimate, deliberate act — it just may not happen silently, because this
    test holds the decision the measurement there paid for.
    """
    for token in ("one", "first", "second"):
        assert claim_coverage.quantity_words(f"the {token} series that ran a model") == [], (
            f"{token!r} entered the quantity set. That is a real widening with a measured cost — "
            "re-read the count in `claim_coverage._QUANTITY_WORDS` and re-take it before accepting "
            "the noise, rather than letting the field grow by accident.")


def _rows(predicate):
    """Every censused row of a floored document satisfying `predicate`, with its paper key.

    ⛔ A LIST RATHER THAN THE FIRST HIT, BECAUSE A SENTENCE THAT WILL NOT LOCATE IS A DIFFERENT
    DEFECT. `ablate` answers NOT_APPLIED both for a sentence the flattener has diverged from and for
    one whose quantity is in words; a test that took the first candidate and hit the former would
    report this instrument broken when the file is what moved. Its own guard is
    `test_every_censused_sentence_can_be_found_in_its_own_file.py`; here such a row is passed over
    and the pass-overs are printed if nothing usable is left.
    """
    return [(paper, row) for paper in PAPERS
            for row in claim_coverage.census(paper) if predicate(row)]


def test_the_harness_says_when_a_covered_sentences_quantity_is_only_in_words():
    """⛔⛔ THE SHARP CASE: COVERED, A QUANTITY IN WORDS, AND NO DIGIT AT ALL.

    `test_the_census_word_covered_survives_ablation.py` never samples these — its sample requires a
    digit — so they are counted as covered and perturbed by nothing, and until this row existed
    nothing said so. `ablate` must answer NOT_APPLIED and NAME the words, not return the generic
    "states no number", which is a different and innocent silence.

    ★ THIS DOUBLES AS THE ANTI-INFLATION GUARD. If some later change teaches the mutator to rewrite
    number words, this sentence stops being NOT_APPLIED and this test goes red — which is the
    conversation that change deserves, because it moves what the word "covered" is allowed to mean.
    """
    candidates = _rows(lambda r: r["covered"] and r["quantity_words"] and not r["has_number"])
    assert candidates, (
        "no floored document has a covered sentence whose quantity is written out with no digit "
        "anywhere in it. Either every such sentence has been bound — the count has one home, "
        "`with_a_word_quantity_and_no_digit_covered` in claim-coverage.json — or the detector has "
        "stopped matching, which is the same silence wearing the costume of progress.")

    passed_over, measured = [], None
    for paper, row in candidates:
        result = claim_ablation.ablate(paper, row)
        assert result["status"] == claim_ablation.NOT_APPLIED, (
            "the harness claims to have perturbed a sentence containing no digit: "
            f"{result['reason']}\n  {row['sentence'][:140]}")
        if "diverged" in result["reason"]:
            passed_over.append(row["sentence"][:90])
            continue
        measured = (row, result)
        break
    assert measured, (
        f"all {len(candidates)} candidate sentences are unlocatable in their own files, so this "
        "test measured nothing — the flattener and the manuscripts have diverged, which is a "
        "different defect with its own guard:\n  " + "\n  ".join(passed_over[:6]))

    row, result = measured
    assert result["word_quantities"] == row["quantity_words"], (
        "the ablation result and the census disagree about which words state this sentence's "
        f"quantity: {result['word_quantities']} vs {row['quantity_words']}")
    assert "WORDS" in result["reason"], (
        "the reason folds a quantity the harness cannot reach into the generic no-number silence, "
        f"so a reader cannot tell the two apart: {result['reason']}")


def test_an_applied_verdict_carries_the_words_it_could_not_reach():
    """⛔ THE COMMON CASE, AND THE ONE THAT READS AS A CLEAN VERDICT: DIGITS *AND* A WORD QUANTITY.

    The harness perturbs the digits — an identifier, an exon number, a list marker — and returns
    APPLIED. Whatever it then says is about those digits. The words must travel with the verdict or
    the caller has no way to know the claim went unread.

    ⚠ `witnesses=[]` DELIBERATELY: this test measures what `ablate` REPORTS, not what any guard
    does, and running the real guards here would price a bookkeeping check like a coverage sweep.
    """
    candidates = _rows(lambda r: r["covered"] and r["quantity_words"] and r["has_number"])
    assert candidates, (
        "no floored document has a covered sentence stating both a digit and a quantity in words, "
        "so this test measured nothing. The count has one home, `with_a_word_quantity_covered` in "
        "claim-coverage.json; if it is now zero, the detector has stopped matching.")

    result = row = None
    for paper, candidate in candidates:
        result, row = claim_ablation.ablate(paper, candidate, witnesses=[]), candidate
        if result["status"] == claim_ablation.APPLIED:
            break
    assert result["status"] == claim_ablation.APPLIED, (
        f"not one of {len(candidates)} candidates could be perturbed, the last saying "
        f"{result['reason']!r}, so this test says nothing about what an APPLIED verdict carries:\n"
        f"  {row['sentence'][:140]}")
    assert result["word_quantities"] == row["quantity_words"], (
        f"an APPLIED verdict dropped the words it could not reach: {result['word_quantities']} vs "
        f"{row['quantity_words']}")
    assert "WORDS" in result["reason"], (
        "an APPLIED verdict on a sentence whose quantity is in words reads as a verdict about that "
        f"quantity, and says nothing to correct the reader: {result['reason']}")


@pytest.mark.parametrize("paper", PAPERS)
def test_the_gap_count_is_a_subset_of_the_coverage_it_qualifies(paper):
    """⛔ A GAP COUNT LARGER THAN THE POPULATION IT QUALIFIES IS ARITHMETIC, NOT A READING.

    The three committed fields nest: sentences stating a word quantity ⊇ those of them the census
    calls covered ⊇ those with no digit at all. A violation means the report is counting different
    row sets under names that imply one, which is how a plausible-looking record gets written.
    """
    rows = claim_coverage.census(paper)
    wq = [r for r in rows if r["quantity_words"]]
    cov = [r for r in wq if r["covered"]]
    nodigit = [r for r in cov if not r["has_number"]]
    assert len(nodigit) <= len(cov) <= len(wq) <= len(rows)
    for r in nodigit:
        # ⛔ THE SAME PREDICATE THE CENSUS USES, NOT A LOOKALIKE. `str.isdigit` is true for a
        # superscript numeral that `\d` does not match, so a paper carrying one would fail this
        # test while the census was right — a guard reddening on a correct tree, which is worse than
        # one that greens on bad input because the first thing anybody does is loosen it.
        assert not re.search(r"\d", r["sentence"]), (
            "a sentence counted as stating no digit contains one, so the sharper subset is not "
            f"the population it is named for:\n  {r['sentence'][:140]}")


def test_this_module_does_not_credit_itself_as_coverage_of_any_manuscript():
    """⛔⛔ THE GUARD THAT COUNTS A GAP MUST NOT SHRINK IT BY EXISTING. Measured, not assumed.

    A regex-shaped string literal here, credited to a document this file happened to name, would
    report coverage of a paper this module never checks — the census inflating itself with its own
    guard, which is exactly the false positive the whole census was rebuilt to remove.
    """
    me = os.path.basename(__file__)
    credited = sorted({rel for rel in claim_coverage.PAPERS
                       for row in claim_coverage.census(rel)
                       for w in row["read_by"] if w.endswith(me)})
    assert not credited, (
        "the census credits this module with covering:\n  " + "\n  ".join(credited)
        + "\n\nA literal here has taken a regex shape and is being counted as though it bound a "
          "claim. Rewrite it.")
