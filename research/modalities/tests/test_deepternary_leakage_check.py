"""Are DeepTernary's quoted numbers blind performance, or reproduction of structures it trained on?

This program has repeatedly cited DeepTernary's qualification figures — 0.66/0.83 on 5T35, 0.62 on 6HAX and
6HR2 — as evidence it "already recovers these exact complexes". `deepternary-qualification-protocol.md`
labelled that step a SOFTWARE-REPRODUCTION control and was right to. The error was in the later quoting, this
session included.

These tests pin the distinction so it cannot blur again, and pin the one thing that makes the planned fix
worth running at all: that 9DTY and 9DTX are absent from the disclosed set, so the head-to-head is blind.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(HERE, "deepternary-leakage-check.json")
EXC = os.path.join(HERE, "deepternary_exclusion_set.json")


def _art():
    return json.load(open(ART))


def _seen(doc, pdb):
    return next(r["in_training_or_exclusion_set"] for r in doc["structures"] if r["pdb"] == pdb)


def test_the_two_selcal_references_are_absent_so_the_head_to_head_is_blind():
    """If either were present, running DeepTernary on them would prove nothing and the fix experiment would
    have to be redesigned before a line of it was built."""
    doc = _art()
    assert _seen(doc, "9DTY") is False
    assert _seen(doc, "9DTX") is False
    assert "genuine blind test" in doc["finding_valid_blind_test"]


def test_the_quoted_qualification_structures_are_present_and_the_artifact_says_so():
    doc = _art()
    for pdb in ("5T35", "6HAX", "6HR2", "6BN7", "6BOY"):
        assert _seen(doc, pdb) is True, pdb
    f = doc["finding_qualification_numbers_are_not_blind"]
    assert "REPRODUCTION OF SEEN STRUCTURES, not blind performance" in f
    assert "including by me in this session" in f, "the misquote must be owned, not attributed elsewhere"


def test_the_expected_performance_of_the_fix_is_stated_as_unknown():
    """⚠ The temptation after a bad result is to quote a number that makes the fix sound certain. The 0.62-0.83
    figures cannot do that job, and the artifact has to say the expected blind performance is unknown."""
    c = _art()["consequence_for_the_fix"]
    assert "UNKNOWN" in c and "assumed worse" in c
    assert "open question, not as a fix with a known answer" in c


def test_absence_from_the_list_is_not_claimed_as_proof_of_unseen():
    """An absent reading is not a reading of absence (CLAUDE.md §4) — here in its exact form: the exclusion set
    is what DeepTernary DISCLOSES, so 'not listed as seen' is weaker than 'proven unseen'."""
    caveat = _art()["_the_one_caveat_on_this_artifact"]
    assert "not PROVEN unseen" in caveat and "not listed as seen" in caveat


def test_the_artifact_matches_the_committed_exclusion_set():
    """The lookup is re-derivable, so it cannot drift from the list it claims to read."""
    ids = set(x.upper() for x in json.load(open(EXC))["ids"])
    doc = _art()
    assert doc["n_ids_in_exclusion_set"] == len(ids)
    for r in doc["structures"]:
        assert r["in_training_or_exclusion_set"] == (r["pdb"] in ids), r["pdb"]


def test_it_licenses_nothing():
    assert "NOTHING about NR4A3" in _art()["_licenses"]
