#!/usr/bin/env python3
"""Guards for RUNG `5b-T` — the assembly-route ternary rebuild and its pre-registered gate.

These are the properties that make the rung's output readable at all, so they run BEFORE anything is docked,
assembled or predicted:

  · the degrader is READ from the committed library, never perceived — and its InChIKey is checked, because
    "the molecule cannot be recovered from the model" is precisely why the §2.5 ternaries are unusable;
  · every substructure role is UNIQUE, because a mapping that is not unique cannot pin an atom;
  · the E3 placement's transform is recovered from its own stored landmarks and REPRODUCES the placement's
    recorded anchor — the self-check that makes the whole assembled frame trustworthy;
  · the gate's thresholds come from the artifact that REGISTERED them on 2026-08-02, not from this file;
  · arm (C) is reported under BOTH reach conventions and they are NOT merged;
  · a refusal never renders as a zero, and a failed harness control makes the run uninterpretable.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, MOD)

import pytest                                                    # noqa: E402

import nr4a3_5bt_assemble as A                                   # noqa: E402
import nr4a3_5bt_gate as GT                                      # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# The molecule is RECORDED, not perceived
# ---------------------------------------------------------------------------------------------------------


def test_degrader_comes_from_the_committed_library_with_an_inchikey():
    c, err = A.recorded_degrader()
    assert err is None, err
    assert c["construct_id"] == A.CONSTRUCT_ID
    assert c["canonical_smiles"] and c["inchikey"]
    # the InChIKey is the thing a replicate can be matched on; the §2.5 ternaries have none
    assert len(c["inchikey"].split("-")) == 3


def test_the_construct_is_one_the_cost_artifact_named():
    cost = json.load(open(os.path.join(MOD, "ternary-rebuild-cost.json")))
    named = cost["spec"]["degrader_source"]["crbn_constructs_at_the_shortest_length_bearing_an_electrophile"]
    assert A.CONSTRUCT_ID in named, "the built construct must be one of the four the rung registered"


def test_the_construct_survives_the_canonical_library_ruling():
    """Row 25 was ruled on with a controlled A/B, and `5b-T` is INVARIANT to which way it went. If that ever
    stops being true for the construct this module builds, the rung's inputs have moved underneath it."""
    doc = json.load(open(os.path.join(MOD, "nr4a3-linker-library-canonical.json")))
    rel = doc["release_condition"]
    row = next((r for r in rel["candidates"] if r["construct_id"] == A.CONSTRUCT_ID), None)
    assert row is not None, "%s is not among the released candidates" % A.CONSTRUCT_ID
    assert row["in_executed"] and row["in_corrected"] and row["in_library_chem"]
    assert row["smiles_identical_across_both"]


def test_every_substructure_role_is_unique():
    c, _ = A.recorded_degrader()
    m, roles, err = A.degrader_mol(c)
    assert err is None, err
    assert set(roles) == {"warhead", "electrophile", "glutarimide"}
    assert all(len(v) > 0 for v in roles.values())
    # the electrophile must sit OUTSIDE the warhead and OUTSIDE the IMiD — it is a linker-borne handle
    assert not (set(roles["electrophile"]) & set(roles["warhead"]))
    assert not (set(roles["electrophile"]) & set(roles["glutarimide"]))


def test_the_docked_warhead_is_a_substructure_of_the_degrader():
    """⛔ THE POINT OF DOCKING *THIS* FRAGMENT. `results/nr4a3-matrix/docked_*.sdf` holds 13 screening
    molecules and NONE of them carries the degrader's warhead core, so a fragment taken from there would not
    be a sub-pose of the degrader at all — it would be a different chemotype, and the snap mask would be
    measuring an unrelated molecule's overlap."""
    from rdkit import Chem
    c, _ = A.recorded_degrader()
    deg = Chem.MolFromSmiles(c["canonical_smiles"])
    war = Chem.MolFromSmiles(A.WARHEAD_SMILES)
    q = Chem.MolFromSmarts(A.WARHEAD_SMARTS)
    assert len(deg.GetSubstructMatches(q)) == 1
    assert len(war.GetSubstructMatches(q)) == 1


def test_the_screening_sdf_is_NOT_a_source_of_the_warhead_pose():
    from rdkit import Chem
    q = Chem.MolFromSmarts(A.WARHEAD_SMARTS)
    path = os.path.join(A.REPO, "results", "nr4a3-matrix", "docked_nr4a3.sdf")
    hits = [m for m in Chem.SDMolSupplier(path, removeHs=True, sanitize=True)
            if m is not None and m.HasSubstructMatch(q)]
    assert not hits, ("a screening ligand now carries the warhead core; the assembly's fragment source "
                      "should be re-examined rather than left implicit")


# ---------------------------------------------------------------------------------------------------------
# The frame — the one thing that replaces the absent native ternary
# ---------------------------------------------------------------------------------------------------------


def test_there_is_no_native_nr4a3_ternary_to_superpose_into():
    """The constraint this rung is shaped by, asserted so it cannot be quietly forgotten: the cost artifact's
    own `common frame` slot says the published protocol's reference does not exist here."""
    cost = json.load(open(os.path.join(MOD, "ternary-rebuild-cost.json")))
    slot = next(s for s in cost["spec"]["input_slots"] if s["slot"] == "the common frame")
    assert "NO NATIVE NR4A3 TERNARY" in slot["note"].upper()


def test_the_e3_placement_transform_reproduces_its_own_anchor():
    pl, err = A.exemplar_placement()
    assert err is None, err
    assert pl["meta_basin_id"] == A.BASIN_ID and pl["pose_id"]
    rows, detail, err = A.placed_registry_arm(pl)
    assert err is None, err
    assert rows and detail["n_atoms"] > 1000
    # `recover_transform` refuses above 0.05 A; the committed artifact reproduces to ~0.001
    assert detail["anchor_reproduced_to_A"] <= 0.05


def test_the_placed_arm_is_the_ternary_conformer_and_says_so():
    """6BOY is a TERNARY. Using it as the frame is fine; using its conformer as site 2 is what the cost
    artifact warned about, so the provenance note has to be on the record."""
    pl, _ = A.exemplar_placement()
    _, detail, _ = A.placed_registry_arm(pl)
    note = " ".join(str(v) for v in detail.values())
    assert "TERNARY" in note.upper() and "6BOY" in note


def test_the_matched_superposition_reproduces_the_basin_searchs_own_numbers():
    """⛔ MATCHED, or the comparison is three independent searches. The committed basins artifact records the
    core RMSDs; this rung must be building in the SAME frame, not a similar one."""
    basins = json.load(open(os.path.join(MOD, "nr4a3-orientation-basins.json")))
    recs = A.matched_receptors()
    for p in ("NR4A1", "NR4A2"):
        ref = basins["target_frame"]["superposition_%s" % p]
        got = recs[p]["superposition"]
        assert got["n_ca_pairs"] == ref["n_ca_pairs"]
        assert abs(got["core_rmsd_A"] - ref["core_rmsd_A"]) < 1e-6
        assert recs[p]["transform_recovery_rms_A"] < 1e-3


def test_the_docking_box_is_derived_not_typed():
    boxes = A.dock_box()
    assert set(boxes) == set(A.PARALOGUES)
    for p, b in boxes.items():
        assert b and b["n_reference_atoms"] > 0
        assert all(s > 10.0 for s in b["size"]), "a box smaller than the ligand is not a box"


def test_plan_mode_resolves_every_committed_input(tmp_path):
    out = tmp_path / "plan.json"
    rc = A.main(["--mode", "plan", "--out", str(out)])
    doc = json.load(open(out))
    assert rc == 0 and doc["ok"], doc.get("problems")
    assert doc["degrader"]["inchikey"]
    assert doc["e3_placement"]["anchor_reproduced_to_A"] <= 0.05


# ---------------------------------------------------------------------------------------------------------
# The gate — registered before the run, and its arithmetic
# ---------------------------------------------------------------------------------------------------------


def test_the_gate_criteria_are_read_from_the_artifact_that_registered_them():
    spec, err = GT.gate_spec()
    assert err is None, err
    assert spec["_registered"].startswith("2026-08-02")
    assert spec["_all_three_arms_must_pass"] is True
    thr = spec["B_reproducible_not_one_models_accident"]["threshold"]
    assert (thr["models_per_arm"], thr["min_present_on_focus"], thr["max_present_on_each_comparator"]) \
        == (16, 12, 4)


def test_the_binomial_tails_are_the_registered_ones():
    assert round(GT.binomial_tail_at_least(12, 16), 4) == 0.0384
    assert round(GT.binomial_tail_at_most(4, 16), 4) == 0.0384


def test_between_is_indeterminate_and_not_a_pass():
    """The third outcome. 11/16 on the focus arm with clean comparators is NOT a pass, and a module that
    rounded it up would be inventing a result the preregistration refused."""
    spec, _ = GT.gate_spec()
    thr = spec["B_reproducible_not_one_models_accident"]["threshold"]
    assert 11 < thr["min_present_on_focus"]
    assert 5 > thr["max_present_on_each_comparator"]


def test_min_models_bar_is_imported_not_typed():
    import nr4a_ternary_signature as S
    assert GT.min_models() == S.MIN_MODELS_FOR_REPRODUCIBILITY >= 3


def test_arm_C_reports_both_conventions_and_does_not_merge_them():
    frame = {"construct_id": A.CONSTRUCT_ID,
             "degrader": {"n_backbone_atoms_measured": 14},
             "placement": {"meta_basin_id": A.BASIN_ID},
             "arms": [{"paralogue": "NR4A3", "detail": {"arm_C_inputs": {}}}]}
    out = GT.arm_C(frame, "/tmp/does-not-exist")
    c2 = out["C2_chemoselectivity_window"]
    assert set(c2) == {"through_space", "corridor"}, "both conventions, always"
    assert "verdict_by_convention" in out and set(out["verdict_by_convention"]) == set(c2)
    # the pendant reach key is read from the design module, never typed here
    assert out["construct"]["reach_key"] == "dab_branch"
    # and the registered at-risk note travels with the arm
    assert "AT RISK" in out["_registered_at_risk_in_advance"]


def test_arm_C_window_verdicts_are_the_committed_numbers():
    """⚠ REGISTERED AT RISK IN ADVANCE, and this pins what "at risk" actually costs: at the 14 backbone atoms
    of the shortest committed CRBN construct, the two conventions DISAGREE at this rung's own placement. That
    is a fact about the committed artifact, not about anything this run produces, so it is asserted here
    rather than discovered in the readout."""
    frame = {"construct_id": A.CONSTRUCT_ID,
             "degrader": {"n_backbone_atoms_measured": 14},
             "placement": {"meta_basin_id": A.BASIN_ID},
             "arms": [{"paralogue": "NR4A3", "detail": {"arm_C_inputs": {}}}]}
    c2 = GT.arm_C(frame, "/tmp/does-not-exist")["C2_chemoselectivity_window"]
    assert c2["through_space"]["verdict"] == "FAIL"
    assert c2["corridor"]["verdict"] == "PASS"
    assert c2["through_space"]["closed_by"] and c2["corridor"]["closed_by"]


def test_an_unmeasurable_C1_is_REFUSED_and_never_a_zero():
    frame = {"construct_id": A.CONSTRUCT_ID,
             "degrader": {"n_backbone_atoms_measured": 14},
             "placement": {"meta_basin_id": A.BASIN_ID},
             "arms": [{"paralogue": "NR4A3", "detail": {"arm_C_inputs": {}}}]}
    c1 = GT.arm_C(frame, "/tmp/does-not-exist")["C1_electrophile_reaches_C397"]
    assert c1["verdict"] == "REFUSED"
    assert c1["measured"] is None
    assert "not a zero" in c1["why"].lower()


def test_a_failed_harness_control_makes_the_run_uninterpretable(tmp_path):
    bad = tmp_path / "poscontrol.json"
    bad.write_text(json.dumps({"case": "6HAX_B_A_FWZ", "positive_control_passes": False,
                               "sentence": "did not reach the bar"}))
    rows, ok, sentence = GT.harness_controls([str(bad)])
    assert ok is False
    assert "UNINTERPRETABLE" in sentence


def test_an_absent_harness_control_is_not_a_pass(tmp_path):
    rows, ok, sentence = GT.harness_controls([str(tmp_path / "nope.json")])
    assert ok is False and rows[0]["ran"] is False


def test_the_gate_refuses_rather_than_reading_the_arms_when_a_control_fails(tmp_path):
    bad = tmp_path / "poscontrol.json"
    bad.write_text(json.dumps({"positive_control_passes": False}))
    doc = GT.run(str(tmp_path), str(tmp_path / "frame.json"), [str(bad)])
    assert doc["verdict"] == "UNINTERPRETABLE"
    assert "A_and_B" not in doc, "the arms must not be read behind a failed control"


def test_no_models_is_a_refusal_not_a_null_result(tmp_path):
    spec, _ = GT.gate_spec()
    doc = GT.arm_A_and_B({"NR4A3": [], "NR4A1": [], "NR4A2": []}, spec)
    assert doc["verdict"] == "REFUSED"
    assert "unread is not absent" in doc["sentence"]


def test_the_scope_block_names_everything_a_pass_does_not_license(tmp_path):
    bad = tmp_path / "pc.json"
    bad.write_text(json.dumps({"positive_control_passes": False}))
    doc = GT.run(str(tmp_path), str(tmp_path / "frame.json"), [str(bad)])
    text = json.dumps(doc["_scope"]).lower()
    for must in ("affinity", "r12", "degradation", "blind", "generalisation", "r5", "r3"):
        assert must in text, "the scope block must name %r" % must


def test_the_inherited_R3_failure_travels_with_the_result():
    """`R3` FAILED on 2026-08-03 and site 1 comes from the same metadynamics/release pipeline. That is a
    condition on the reading, not a footnote, so the module has to carry it in the artifact itself."""
    dep = GT._r3_dependency({"arms": [{"detail": {}}]})
    assert "0.259" in json.dumps(dep) and "0.53" in json.dumps(dep)
    assert dep["answer"].startswith("NO")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
