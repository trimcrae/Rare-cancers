"""THE CARRIER AUDIT'S THREE LOAD-BEARING PROPERTIES, PINNED — because each of them is a mistake this
repository has already made once, in a different file, on a different day.

`steric_carrier_audit.py` answers Tier-1 row 3 of `path-family-synthesis.md`: does anything committed already
put a heavy atom inside the I484 or L534 denied lobe? Its ANSWER is in the artifact. What is pinned here is
the set of properties without which the answer would be misleading even when the arithmetic is right.

  1. **A SIGNAL IS NEVER EMITTED WITHOUT ITS NULL.** `score_pose()` already refuses to; the occupancy
     statistic this file adds is a SECOND statistic on the same molecules and could easily have shipped
     without one. 46 of 46 molecules reaching a lobe reads like a discovery and is nearly meaningless
     alone — the poses were docked into the cavity the lobes sit in. Only `signal − null` is gradeable.

  2. **"NOT SCORABLE" MUST NEVER COLLAPSE INTO "SCORED, REACHED NOTHING".** The committed construct set
     carries SMILES and no coordinates, so no occupancy of it has been measured in either direction.
     CLAUDE.md §4: an absent reading is not a reading of absence. A future edit that reports the construct
     set as a zero would satisfy row 3's falsifier with a fabrication, so the distinction is asserted.

  3. **A TRANSFERRED POSE MUST NOT RENDER AS AN IN-FRAME ONE.** `score_pose()` takes coordinates and cannot
     tell you they came from a different opened conformer. The audit decides frame identity atom-by-atom
     first, and anything it had to superpose is kept in its own block with that superposition's core RMSD.
     ⚠ And specifically: the transform-recovery residual is ZERO BY CONSTRUCTION (it re-derives a transform
     from a model that transform produced) — an earlier draft reported that zero as the fit quality, which
     is precisely "a populated field is not a measured one". The real metric must be a real one.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import steric_carrier_audit as A  # noqa: E402

ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "steric-carrier-audit.json")


@pytest.fixture(scope="module")
def art():
    if not os.path.exists(ART):
        pytest.skip("steric-carrier-audit.json not committed in this checkout")
    with open(ART) as fh:
        return json.load(fh)


# ── 1 · the null is not optional ─────────────────────────────────────────────────────────────────────────
def test_every_scored_molecule_carries_its_own_occupancy_null(art):
    for block in art["scored_in_frame"] + art["scored_after_transfer"]:
        for mol in block["molecules"]:
            occ = mol["occupancy_with_its_null"]
            assert occ["occupancy_signal_rate"] is not None, mol["molecule"]
            assert occ["occupancy_null_rate"] is not None, (
                "%s emitted an occupancy signal with no matched null" % mol["molecule"])
            assert occ["occupancy_signal_minus_null"] is not None, mol["molecule"]


def test_the_null_class_is_the_programs_own_conserved_positions(art):
    block = art["scored_in_frame"][0]
    by_class = block["molecules"][0]["occupancy_with_its_null"]["by_class"]
    assert "conserved_or_shared" in by_class, "the false-positive control class is missing entirely"
    assert by_class["conserved_or_shared"]["n_positions"] > 0


def test_occupancy_is_measured_at_every_pocket5_position_not_only_the_two_targets(art):
    """The null cannot exist if occupancy is only computed where the answer is wanted."""
    import selectivity_mechanism_options as S
    mol = art["scored_in_frame"][0]["molecules"][0]
    assert set(mol["lobe_occupancy"]) == {str(u) for u in S.POCKET5}


def test_the_headline_is_the_difference_not_the_count(art):
    """A verdict that quoted only 'n molecules reached a lobe' would be the failure the rule warns about."""
    pooled = art["verdict"]["answer_for_the_committed_POSE_sets"]["pooled_occupancy_with_its_null"]
    assert pooled["signal_rate"] is not None and pooled["null_rate"] is not None
    assert pooled["signal_minus_null"] == pytest.approx(
        round(pooled["signal_rate"] - pooled["null_rate"], 3), abs=1e-6)
    assert "SIGNAL MINUS NULL" in art["verdict"]["★_the_reading_that_matters_most"]


# ── 2 · not-scorable is not a zero ───────────────────────────────────────────────────────────────────────
def test_the_construct_set_is_reported_unscorable_and_never_as_a_measured_zero(art):
    c = art["constructs"]
    assert c["⛔_scorable_through_score_pose"] is False
    assert c["coordinate_fields_found"] == []
    verdict = art["verdict"]["answer_for_the_CONSTRUCT_set"]
    assert "NOT SCORABLE" in verdict
    # the falsifier's own words must not be claimed for a set that was never placed
    assert "reach" not in verdict.lower() or "NOT SCORABLE" in verdict


def test_the_construct_count_is_derived_not_summed_over_overlapping_groups(art):
    """`virtual_library` is the UNION of the two placement groups; summing all three doubles the library."""
    c = art["constructs"]
    assert c["_the_groups_are_a_partition"]["verified_here"] is True
    assert c["_the_groups_are_a_partition"]["agrees_with_the_canonical_ruling_n_constructs"] is True
    assert c["n_distinct_constructs"] < sum(c["group_sizes"].values())


def test_the_canonical_library_ruling_is_imported_not_restated(art):
    """Row 25's ruling has one home; this audit must point at it rather than re-decide it."""
    w = art["constructs"]["which_set_is_canonical"]
    assert "nr4a3-linker-library-canonical.json" in w["settled_by"]
    assert w["EXECUTED"]["status"].startswith("FROZEN")


# ── 3 · a transferred pose is a weaker object and must look like one ─────────────────────────────────────
def test_in_frame_and_transferred_results_live_in_separate_blocks(art):
    assert "scored_in_frame" in art and "scored_after_transfer" in art
    for b in art["scored_in_frame"]:
        assert "superposition" not in b, "an in-frame block must not carry a superposition"
    for b in art["scored_after_transfer"]:
        assert "⚠_this_is_not_in_frame_arithmetic" in b


def test_frame_identity_is_decided_atom_by_atom(art):
    for row in art["pose_source_census"]:
        assert "identical_to_rule_frame" in row and "why" in row
    assert any(r["identical_to_rule_frame"] for r in art["pose_source_census"])
    assert any(r["identical_to_rule_frame"] is False for r in art["pose_source_census"]), (
        "a census in which nothing fails identity is not testing identity")


def test_the_transfer_quality_metric_is_a_measured_number_not_the_zero_residual(art):
    """⚠ The regression this exists for: a by-construction zero was once reported as the post-fit RMSD."""
    for b in art["scored_after_transfer"]:
        sup = b["superposition"]
        assert sup["⚠_transform_recovery_residual_A"] == 0.0, (
            "if this stops being zero the recovery idiom changed and the note below is now wrong")
        assert sup["core_rmsd_A"] > 0.0, (
            "%s reports a zero core RMSD — that is the by-construction residual leaking back in"
            % b["source"])
        assert 0.0 < sup["core_fraction"] <= 1.0


# ── the control, and the conditions, must be attached to the record itself ───────────────────────────────
def test_the_M4_relocation_control_travels_with_the_artifact(art):
    ctl = art["⛔_control_imported_verbatim_from_the_rule"]
    with open(os.path.join(os.path.dirname(ART), "steric-design-rule.json")) as fh:
        rule = json.load(fh)
    assert ctl == rule["⛔_control"], "the control must be imported verbatim, never re-typed"
    assert ctl["median_centroid_shift_A"]["NR4A1"] and ctl["median_centroid_shift_A"]["NR4A2"]


def test_R5_is_inherited_and_R3_is_not(art):
    inh = art["⚠_inheritance"]
    assert inh["inherits_R5"] is True
    assert inh["inherits_R3"] is False
    assert "INCONCLUSIVE" in inh["why"]


def test_roadmap_edits_are_described_not_applied(art):
    m = art["map_edits_required"]
    assert "DESCRIBED, NOT APPLIED" in m["_convention"]
    assert m["targets"] and all("where" in t and "edit" in t for t in m["targets"])


def test_the_design_targets_are_read_from_the_rule_not_hard_coded():
    src = open(A.__file__).read()
    assert 'rule["design_targets"]' in src, "the two vectors must come from the rule's artifact"
