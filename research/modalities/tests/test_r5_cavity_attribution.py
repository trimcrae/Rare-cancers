"""Unit tests for `r5_cavity_attribution` — which sub-cavity of R3's split site each method chose.

The load-bearing assertions are not the arithmetic. They are the three ways this module could
silently stop answering its question:

  · **it could define the cavities itself.** They belong to `r3-site-choice-audit.json`; a copy here
    would drift the moment that audit is re-run, and the whole point is that this follows it.
  · **it could break a tie.** A tie means the discriminating contacts do not decide, and inventing a
    winner would manufacture exactly the attribution the module exists to measure honestly.
  · **it could count the shared residues.** Four residues line BOTH cavities. Counting them lets the
    overlap between the two cavities decide which cavity a pose is in, which is circular.
"""
import json
import os

import r5_cavity_attribution as R


def test_the_cavity_definitions_are_read_from_the_r3_audit_and_not_typed_here():
    """⛔ ONE HOME. If this ever stops reading the audit, the two can disagree silently."""
    src = open(R.__file__).read()
    assert "r3-site-choice-audit.json" in src
    cav = R.cavity_definitions()
    with open(R.AUDIT) as fh:
        audit = json.load(fh)
    acc = audit["question_A_which_cavity_is_the_site"]["accepted_cavities"]
    assert [c["pocket"] for c in cav["cavities"]] == [c["pocket"] for c in acc]
    for got, want in zip(cav["cavities"], acc):
        assert got["lining_labels"] == want["lining_uniprot_labels"]
    # and the numbers that make the split readable travel with it
    assert cav["separation"]["centroid_separation_ang"] is not None
    assert cav["separation"]["pairwise_jaccard"] is not None


def test_the_shared_residues_are_dropped_from_the_call():
    """The 4 residues lining BOTH cavities cannot discriminate and must not vote."""
    cavs = [{"pocket": 1, "lining_resseq": [1, 2, 3, 4]},
            {"pocket": 2, "lining_resseq": [3, 4, 5, 6]}]
    disc = R.discriminating_sets(cavs)
    assert disc[1] == [1, 2] and disc[2] == [5, 6]
    assert disc["_shared_dropped"] == [3, 4]
    # a pose touching ONLY shared residues is AMBIGUOUS, never assigned
    assert R.call_cavity({3, 4}, disc)["cavity"] == "AMBIGUOUS"


def test_a_tie_is_ambiguous_and_is_never_broken():
    disc = {1: [10, 11], 2: [20, 21], "_shared_dropped": []}
    got = R.call_cavity({10, 20}, disc)
    assert got["cavity"] == "AMBIGUOUS"
    assert "tiebreak" in got["_why"]


def test_a_clear_majority_is_called_with_its_margin():
    disc = {1: [10, 11, 12], 2: [20, 21], "_shared_dropped": []}
    got = R.call_cavity({10, 11, 20}, disc)
    assert got["cavity"] == 1 and got["margin"] == 1
    assert got["counts"] == {1: 2, 2: 1}


def test_an_ungradeable_system_is_excluded_from_the_denominator_not_scored_as_agreement():
    """⛔ THE FAILURE THIS BLOCKS: an AMBIGUOUS or UNREAD row silently counted as 'same cavity' would
    turn missing evidence into agreement — CLAUDE.md §4, an absent reading is not a reading of
    absence."""
    rows = [{"same_cavity": True, "first_method": {"cavity": 1}, "second_method": {"cavity": 1}},
            {"same_cavity": None, "first_method": {"cavity": "AMBIGUOUS"},
             "second_method": {"cavity": 2}},
            {"same_cavity": None, "first_method": {"cavity": 1},
             "second_method": {"cavity": "UNREAD"}}]
    roll = R._rollup(rows, {"chosen_by_the_frozen_rule": {"pocket": 1}})
    assert roll["n_systems"] == 3
    assert roll["n_gradeable"] == 1
    assert roll["n_same_cavity"] == 1 and roll["n_different_cavity"] == 0


def test_the_rollup_says_different_cavities_when_they_are_different():
    rows = [{"same_cavity": False, "first_method": {"cavity": 1}, "second_method": {"cavity": 2}},
            {"same_cavity": False, "first_method": {"cavity": 1}, "second_method": {"cavity": 2}}]
    roll = R._rollup(rows, {"chosen_by_the_frozen_rule": {"pocket": 1}})
    assert roll["n_different_cavity"] == 2
    assert "DIFFERENT CAVITIES" in roll["_reads"]


def test_no_threshold_or_cutoff_is_defined_in_this_module():
    """⛔ The contact cutoff is the pipeline's own, reached through `pose_convergence_401.contact_a`."""
    src = open(R.__file__).read()
    assert "contact_a()" in src
    for forbidden in ("CUTOFF =", "CUTOFF=", "cutoff = 4.0", "cutoff=4.0"):
        assert forbidden not in src, "this module must not define a contact cutoff of its own"


def test_it_never_claims_binding():
    """Language discipline: a cavity call is a geometry statement, never a binding claim."""
    doc = R.__doc__ or ""
    assert "does not license" in doc.lower() or "DOES NOT LICENSE" in doc
    assert os.path.basename(R.OUT) == "r5-cross-method-cavity-attribution.json"
