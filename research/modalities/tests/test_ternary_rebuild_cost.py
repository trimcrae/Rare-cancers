"""RUNG 5b-T's price is DERIVED, and this is the checker that says so.

CLAUDE.md rule 1: *"A total is DERIVED, never typed — regenerate it and let the checker verify it sums.
Hand-carried totals drift silently."* These tests are that checker. They do not assert a remembered dollar
figure — they assert that the per-arm attribution reproduces the measured job total, that the rung buys no
GPU-hours, and that the planning rate is READ from the ladder rather than typed into the module.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_rebuild_cost as TRC  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_measured_basis_sums_to_the_job_total():
    """Per-arm + fixed must reproduce the run's own start/finish delta, inside the rounding bound."""
    rec = TRC.reconciliation()
    assert rec["sums"], (
        "the per-step attribution does not reproduce the measured job total: derived %s s vs %s s "
        "(residual %s, bound %s). A residual outside the bound means the attribution is wrong."
        % (rec["derived_s"], rec["measured_job_total_s"], rec["residual_s"], rec["residual_bound_s"]))


def test_the_rung_buys_no_gpu_hours():
    """The $0 answer is a consequence of 0.0 reference GPU-hours, not an assertion about dollars."""
    doc = TRC.derive()
    assert doc["derived_cost"]["reference_gpu_h"] == 0.0
    assert doc["derived_cost"]["usd_plan"] == 0.0
    assert doc["derived_cost"]["usd_range"] == [0.0, 0.0]
    assert doc["derived_cost"]["ladder_total_unchanged"] is True


def test_the_plan_rate_is_read_not_typed():
    """The rate must come out of the regenerated ladder; a module that carries its own copy has drifted."""
    doc = TRC.derive()
    rate = doc["derived_cost"]["plan_rate"]
    assert rate["read"] is True, rate.get("why")
    with open(os.path.join(HERE, "vast-ladder-repricing.json")) as f:
        ladder = json.load(f)
    assert rate["plan_usd_per_reference_gpu_h"] == ladder["plan_usd_per_reference_gpu_h"]
    assert rate["range_usd_per_reference_gpu_h"] == ladder["range_usd_per_reference_gpu_h"]


def test_every_arm_is_counted_including_the_harness_controls():
    """★ Dropping the positive controls is the failure this lane already paid for once.

    A near-zero score with no control cannot be told apart from broken plumbing, and this rung's E3 is CRBN,
    so a VHL-only harness control does not cover the assembly it is used for.
    """
    doc = TRC.derive()
    u = doc["units"]
    assert len(u["poscontrol_arms"]) == 2
    assert any("CRBN" in a for a in u["poscontrol_arms"]), \
        "the CRBN harness control is missing — this rung assembles a CRBN ternary"
    assert any("VHL" in a for a in u["poscontrol_arms"])
    assert u["paralogue_arms"] == ["NR4A1", "NR4A2", "NR4A3"]
    assert u["predicted_complexes"] == 5 * u["seeds_per_arm"]


def test_the_reproducibility_bar_is_cleared_not_merely_met():
    """`nr4a_ternary_signature` refuses the word 'reproducible' below 3 models per arm; 16 clears it."""
    doc = TRC.derive()
    u = doc["units"]
    assert u["models_per_arm_read_by_V1"] >= u["min_models_for_reproducibility"]
    assert u["min_models_for_reproducibility"] == 3


def test_what_could_not_be_priced_is_named_rather_than_invented():
    """An honest partial beats a fabricated total — so the unpriced items must be listed, with reasons."""
    doc = TRC.derive()
    assert len(doc["unpriced"]) >= 2
    for item in doc["unpriced"]:
        assert "UNPRICED" in item or "unpriced" in item


def test_wall_clock_is_declared_a_floor():
    """The dollar figure is robust; the minutes are not, and the artifact has to say which is which."""
    doc = TRC.derive()
    assert "floor" in doc["derived_wall_clock"]["_is_a_floor_not_an_estimate"].lower()
    assert doc["derived_wall_clock"]["total_min"] > 0


def test_cli_check_mode_exits_clean():
    """`--check` is what CI runs; it must regenerate and agree without writing anything."""
    out = subprocess.run(
        [sys.executable, os.path.join(HERE, "ternary_rebuild_cost.py"), "--check"],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "SUMS" in out.stdout


def test_gate_arm_B_thresholds_match_the_null_they_claim():
    """The reproducibility bar quotes a binomial tail — so the tail must actually be that number.

    A pre-registered criterion whose stated p-value does not follow from its own thresholds is worse than no
    criterion: it reads as calibrated and is not.
    """
    from math import comb
    b = TRC.GATE["B_reproducible_not_one_models_accident"]["threshold"]
    n = b["models_per_arm"]
    tail_hi = sum(comb(n, k) for k in range(b["min_present_on_focus"], n + 1)) / 2 ** n
    tail_lo = sum(comb(n, k) for k in range(0, b["max_present_on_each_comparator"] + 1)) / 2 ** n
    assert round(tail_hi, 4) == 0.0384, tail_hi
    assert round(tail_lo, 4) == 0.0384, tail_lo
    assert "0.0384" in TRC.GATE["B_reproducible_not_one_models_accident"]["null"]
    # the two tails must be mirrors, or the arm is silently asymmetric
    assert abs(tail_hi - tail_lo) < 1e-12


def test_gate_arm_C_registers_its_own_risk_before_the_run():
    """★ A risk named only after the result is worthless. Arm C is at risk today and has to say so."""
    c = TRC.GATE["C_the_geometry_the_categorical_axis_depends_on_survives_assembly"]
    risk = c["known_risk_registered_in_advance"]
    assert "14" in risk and "12" in risk, risk
    assert "crbn|M0" in risk and "crbn|M17" in risk, risk
    assert c["reading_if_it_fails"].startswith("⛔ NO-GO")


def test_the_gate_needs_all_three_arms():
    assert TRC.GATE["_all_three_arms_must_pass"] is True
    arms = [k for k in TRC.GATE if k[:2] in ("A_", "B_", "C_")]
    assert len(arms) == 3, arms
    assert TRC.GATE["STOP_conditions_that_are_refusals_not_results"]


def test_scope_refuses_the_claims_this_rung_cannot_make():
    """Requirement 4: the honest scope travels WITH the gate, not in a footnote after the result."""
    not_licensed = " ".join(TRC.SCOPE["a_pass_does_NOT_license"]).lower()
    for forbidden in ("affinity", "free-energy", "efficacy", "blind"):
        assert forbidden in not_licensed, forbidden
    assert "R12" in " ".join(TRC.SCOPE["a_pass_does_NOT_license"])
    inherited = " ".join(TRC.SCOPE["inherited_limits_that_travel_with_every_result"])
    assert "R5" in inherited and "V17" in inherited and "V2" in inherited


def test_the_degrader_must_come_from_the_smiles_recorded_library():
    """The §2.5 ternaries are dead because their molecule is unrecoverable. That must not recur."""
    src = TRC.DEGRADER_SOURCE
    assert src["artifact"].endswith("nr4a3-linker-library-chem.json")
    assert "constructs[].canonical_smiles" in src["fields"]
    assert "constructs[].inchikey" in src["fields"]
    assert src["e3_arm_required"] == "crbn"
    # the shortest committed length is a fact about the library, not a preference — check it against it
    with open(os.path.join(HERE, "nr4a3-linker-library-chem.json")) as f:
        lib = json.load(f)
    shortest = min(c["n_backbone_atoms_measured"] for c in lib["constructs"])
    assert shortest == src["shortest_committed_backbone_atoms"], (shortest, src)
    # `..._none` carries no pendant, so it cannot present a covalent handle whatever its length
    ids = {c["construct_id"] for c in lib["constructs"]
           if c["n_backbone_atoms_measured"] == shortest
           and c["construct_id"].startswith("crbn")
           and not c["construct_id"].endswith("_none")}
    assert set(src["crbn_constructs_at_the_shortest_length_bearing_an_electrophile"]) == ids, ids


def test_preflight_names_the_runs_that_died_without_it():
    """The empty snap mask killed two runs; the assertion that prevents it is part of the spec."""
    p = TRC.PREFLIGHT
    assert p["snap_masks_must_be_non_empty"] is True
    assert "30753431082" in p["why"] and "30754028742" in p["why"]
    assert p["reference_masks"]["unbound_lig1"] == 33
    assert p["reference_masks"]["unbound_lig2"] == 18


def test_committed_artifact_matches_a_fresh_derivation():
    """A committed artifact that has drifted from its own generator is a stale fact reading as a live one."""
    path = os.path.join(HERE, "ternary-rebuild-cost.json")
    assert os.path.exists(path), "run ternary_rebuild_cost.py to generate it"
    with open(path) as f:
        committed = json.load(f)
    fresh = TRC.derive()
    assert committed["derived_cost"]["reference_gpu_h"] == fresh["derived_cost"]["reference_gpu_h"]
    assert committed["derived_wall_clock"]["total_s"] == fresh["derived_wall_clock"]["total_s"]
    assert committed["units"] == fresh["units"]
