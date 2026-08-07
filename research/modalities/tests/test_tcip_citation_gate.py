"""Q12's citation gate — checked against the REAL repository, offline.

⛔ These deliberately exercise the real files rather than fixtures. `test_fleet_armed`'s lesson is
the reason: every keep-alive test there monkeypatched the seam, so a lookup that resolved against the
wrong directory produced no symptom and passed every test. The properties here are all "does this
module read the actual workflow / the actual memo correctly", and a mocked workflow would test the
mock.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tcip_citation_gate as tcg  # noqa: E402


def test_the_doi_is_registered_in_the_ENFORCED_list_not_merely_present_in_the_file():
    """⛔ A DOI in the print-only section resolves in the log and gates nothing."""
    reg = tcg.measure_doi_registration()
    assert reg["error"] is None, reg["error"]
    assert reg["registered"] is True
    assert reg["in_enforced_section"] is True, (
        "the DOI must sit inside verify-refs.yml's FIXED_DOIS array, whose length derives the "
        "expected count the verdict enforces")


def test_the_two_grep_measurements_are_labelled_and_are_allowed_to_differ():
    """The memo's `grep -c` counts LINES on a bare fragment; the registration counts the full DOI.

    Reporting either as the other is how an unexplained 1-versus-2 costs a future session an hour.
    """
    reg = tcg.measure_doi_registration()
    assert reg["memo_grep_pattern"] == "jacs.5c05634"
    assert reg["memo_grep_c_result"] >= reg["n_occurrences_of_full_doi"]
    assert reg["n_occurrences_of_full_doi"] >= 1


def test_the_stale_memo_is_detected_rather_than_narrated():
    """⭐ The reusable finding: a blocker recorded in prose does not un-record itself when fixed."""
    doc = tcg.build(skip_network=True)
    assert doc["route_memo_claim"]["error"] is None
    # The memo still carries the `grep -c ... -> 0` sentence, and the DOI IS registered.
    assert doc["memo_is_stale"] is True, (
        "if this ever goes False, either the memo was corrected (good — then delete this "
        "assertion's premise, not the module) or the DOI was removed from the workflow (bad)")
    assert doc["gate_dischargeable_by_plain_dispatch"] is True


def test_the_gate_status_is_cleared_and_says_what_that_permits():
    doc = tcg.build(skip_network=True)
    assert doc["gate_status"] == "CLEARED"
    assert "quote" in doc["_gate_status_means"]


def test_clearing_the_gate_moves_exactly_one_permission_and_no_measurement():
    """⛔ The whole point of the grading. One row moves; the longer list does not."""
    g = tcg.grade_against_failure_record()
    assert len(g["what_the_cleared_gate_moves"]) == 1
    assert len(g["what_it_does_not_move"]) > len(g["what_the_cleared_gate_moves"])
    moved = g["what_the_cleared_gate_moves"][0]
    assert "QUOTE" in moved["statement"]
    # No row in the moved list may mention a number, a blocker, or a binding claim.
    for bad in ("blocker", "binding", "kcal", "measurement"):
        assert bad not in moved["statement"].lower()


def test_the_grading_names_the_blockers_as_untouched():
    g = tcg.grade_against_failure_record()
    blockers = next(r for r in g["what_it_does_not_move"] if "blockers" in r["statement"])
    for b in ("BLK-R4-BINDS", "BLK-INDUCED-COMPLEX", "BLK-PARALOGUE-DDG", "BLK-NO-WET-LAB"):
        assert b in blockers["still"]


def test_the_grading_keeps_the_R9_R10_R12_discrepancy_separate():
    """Both are 'a Q12 thing' and conflating them would let a cleared gate look like a fixed graph."""
    g = tcg.grade_against_failure_record()
    assert "R12 only" in g["the_R9_R10_R12_discrepancy_is_untouched"]
    assert "clearing the citation gate does nothing about it" in \
        g["the_R9_R10_R12_discrepancy_is_untouched"]


def test_the_unverified_pagination_is_stated_rather_than_glossed():
    """The run verified title/journal/year. Volume, pages and PMCID it did not, and must say so."""
    ev = tcg.VERIFICATION_EVIDENCE
    assert ev["matched"] == ["title", "journal", "year"]
    assert "VOLUME, PAGES and PMCID" in ev["⚠_not_verified_by_this_run"]


def test_the_artifact_states_that_no_claim_ceiling_moves():
    doc = tcg.build(skip_network=True)
    assert "§2.3" in doc["claim_ceiling"]
    assert "raises no claim ceiling" in doc["claim_ceiling"]
