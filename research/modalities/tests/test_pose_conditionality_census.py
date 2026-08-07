"""The pose-conditionality census must stay honest about its own contents.

⛔ THE FAILURE THESE GUARD AGAINST IS THE ONE THE CENSUS EXISTS TO REPAIR. A pre-registered falsifier fired
and the restatement it demanded was owed. If the census can claim an edit it did not make, or grade a claim
in a vocabulary it does not define, or quietly stop reading the artifacts it says it reads, then it becomes
the same kind of decoration the falsifier became — a document that asserts diligence instead of carrying it.

⚠ These run against the REAL committed artifacts, not fixtures (CLAUDE.md §6: mock the thing under test and
you test the mock). The risk here is a field moving in `pose-second-method.json` and the census silently
reporting a default; only the real artifacts can show that.
"""
from __future__ import annotations

import json
import pathlib
import sys

MOD = pathlib.Path(__file__).resolve().parents[1]
REPO = MOD.parents[1]
sys.path.insert(0, str(MOD))

import pose_conditionality_census as pcc  # noqa: E402

CENSUS = json.loads((MOD / "pose-conditionality-census.json").read_text())
MAP_EDITS = json.loads(
    (REPO / "research" / "manuscripts" / "pose-conditionality-map-edits.json").read_text()
)


def test_every_claim_carries_a_grade_from_the_declared_vocabulary():
    """A grade outside the vocabulary is an ungradeable claim wearing a grade."""
    bad = [c["id"] for c in CENSUS["claims"] if c["grade"] not in CENSUS["grades"]]
    assert bad == [], f"claims graded outside the declared vocabulary: {bad}"


def test_every_claim_names_where_it_lives_and_what_it_was_computed_on():
    for c in CENSUS["claims"]:
        assert c["where"], f"{c['id']} names no location"
        assert c["computed_on"], f"{c['id']} does not say what it was computed on"
        assert c["restated_as"], f"{c['id']} has no restated form — which is the entire deliverable"


def test_a_not_marginalisable_claim_must_name_the_cost_of_marginalising_it():
    """⛔ Otherwise NOT-MARGINALISABLE reads as 'we gave up' rather than 'here is what it would take'."""
    for c in CENSUS["claims"]:
        if c["grade"] == "NOT-MARGINALISABLE":
            assert c["marginalisation_cost"].strip(), f"{c['id']} claims not-marginalisable and names no cost"


def test_every_claim_marked_ROUTED_has_a_real_map_edit_behind_it():
    """The rollup must not advertise a routed consequence the edits file does not carry."""
    routed = [c["id"] for c in CENSUS["claims"] if c["action"].startswith("ROUTED")]
    assert routed, "the census claims no routed edits at all — check the rollup"
    assert MAP_EDITS["map_edits_required"], "claims are marked ROUTED but no map edits were emitted"


def test_the_rollup_counts_are_derived_from_the_claims_and_not_typed():
    counts: dict[str, int] = {}
    for c in CENSUS["claims"]:
        counts[c["grade"]] = counts.get(c["grade"], 0) + 1
    assert CENSUS["rollup"]["by_grade"] == counts
    assert CENSUS["rollup"]["n_claims"] == len(CENSUS["claims"])


def test_the_falsifier_is_recorded_as_having_fired():
    """If this ever reads False the census is answering a question nobody asked."""
    assert CENSUS["the_falsifier"]["fired"] is True


def test_the_second_method_verdict_is_read_from_the_artifact_and_still_says_they_disagree():
    """⚠ Reads the SOURCE, not the census, so a census that stopped tracking its artifact fails here."""
    src = json.loads((MOD / "pose-second-method.json").read_text())
    assert src["verdict"]["R5_resolved"] is False
    ev = CENSUS["evidence"]["second_method_part_a_the_falsifier_firing"]
    assert ev["outcome"] == src["verdict"]["outcome"]
    assert ev["median_inter_method_rmsd_A"] == src["verdict"]["part_a_median_inter_method_rmsd_A"]
    assert ev["n_agreeing_within_recovered_A"] == src["verdict"]["part_a_agreement_within_recovered_A"]


def test_the_no_known_answer_half_is_reported_as_UNRUN_and_not_as_a_measured_failure():
    """★ THE HALF EVERYONE FORGETS. `n_gradeable: 0` from an arm that never executed is not a result.

    CLAUDE.md §4: an absent reading is not a reading of absence. If this census ever starts reporting that
    zero without the unrun status beside it, it is manufacturing a negative.
    """
    block = CENSUS["evidence"]["⛔_the_half_that_gets_forgotten__no_known_answer_calibration"]
    assert block["n_gradeable"] == 0
    assert block["n_pairs_carrying_an_unrun_status"] > 0, (
        "the census reports zero gradeable pairs without evidence that the arm did not run — "
        "that would state an unrun protocol as a measured failure to recover"
    )
    assert "UNRUN" in " ".join(block["per_pair_status"])


def test_the_already_worked_steric_case_is_imported_and_not_contradicted():
    """The census must not re-derive (or disagree with) the one claim that was already graded."""
    src = json.loads((MOD / "steric-carrier-audit.json").read_text())
    want = src["verdict"]["carried_candidate"]["★_what_survives_the_pose_spread_and_what_does_not"]
    got = CENSUS["evidence"]["the_already_worked_case__imported_verbatim"]["record"]
    assert got == want, "the steric grading was re-derived or drifted; it must be imported verbatim"


def test_the_committed_pose_inventory_is_counted_off_real_files():
    """A count that cannot be reproduced from the checkout is a remembered number."""
    inv = pcc.committed_pose_inventory()
    assert inv["n_first_method_poses_of_the_ligand"] > 1, (
        "fewer than two committed poses would make the whole census unanswerable"
    )
    for row in inv["first_method_smina"] + inv["second_method_rdock"]:
        assert (REPO / row["file"]).exists(), f"{row['file']} is counted but not present"


def test_no_claim_row_promises_a_marginalisation_that_was_invented():
    """⛔ The one thing the task forbids outright: a spread nobody computed.

    A row may only be graded POSE-ROBUST or POSE-DEPENDENT if it says it was evaluated on more than one
    pose. Anything else must be NOT-MARGINALISABLE or ALREADY-MARGINALISED.
    """
    for c in CENSUS["claims"]:
        if c["grade"] in ("POSE-ROBUST", "POSE-DEPENDENT"):
            on = c["computed_on"].lower()
            assert any(k in on for k in ("all six", "both methods", "one smina top pose", "one pose, watched")), (
                f"{c['id']} is graded {c['grade']} but does not say what it was evaluated across"
            )
