"""`Q10` — the TCIP interface-floor ablation's prediction, tested against the committed monovalent run.

⚠ The tests that matter here are the ones that stop the two axes being conflated. `Q10`'s whole hazard is
that a mechanism measured on ONE instrument (a second body's orientation acceptance) reads like a
prediction about ANOTHER (a backbone-atom window over cysteines), so:

  * `test_axis_A_counts_only_the_E3_specific_refusal` — the warhead-anchor refusal is 6x larger and is NOT
    retired by dropping the E3 arm. Counting it would manufacture the prediction's confirmation.
  * `test_both_configurations_go_through_one_reader` — a difference produced by two different readers is
    not a difference.
  * `test_the_verdict_does_not_read_axis_A_as_a_rescue` — holding on axis A and rescuing the route are
    different claims and must never render alike.
"""
import json
import os

import pytest

import inhibitor_configuration_prediction as Q10

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "nr4a3-inhibitor-configuration-prediction.json")


@pytest.fixture(scope="module")
def doc():
    if not os.path.exists(ART):
        pytest.skip("artifact not built")
    return json.load(open(ART, encoding="utf-8"))


@pytest.fixture(scope="module")
def mono():
    return json.load(open(Q10.MONO, encoding="utf-8"))


# ==========================================================================================================
# THE READER — one function, both sides
# ==========================================================================================================
def test_cell_stats_is_pure_arithmetic_over_one_row():
    row = {"target_atoms": 14, "width": 0,
           "all_competitors_atoms": {"A": 12, "B": 14, "C": 20, "D": None}}
    s = Q10.cell_stats(row)
    assert s["first_competitor_atoms"] == 12
    assert s["margin_atoms"] == -2, "a competitor reached first must give a NEGATIVE margin"
    assert s["rank_of_target"] == 2, "ties share the best rank; one competitor is strictly shorter"
    assert s["n_competitors"] == 3, "a None requirement is not a competitor"


def test_a_row_with_no_target_or_no_competitors_returns_None_rather_than_a_zero():
    assert Q10.cell_stats({"target_atoms": None, "all_competitors_atoms": {"A": 3}}) is None
    assert Q10.cell_stats({"target_atoms": 3, "all_competitors_atoms": {}}) is None


def test_both_configurations_go_through_one_reader(mono):
    """★ A difference produced by two different readers is not a difference. Both sides must be
    summarised by `configuration_summary`, which calls `cell_stats` and nothing else."""
    import inspect
    src = inspect.getsource(Q10.axis_b)
    assert src.count("configuration_summary") == 2, (
        "axis_b must summarise both configurations through the same function")


def test_the_rank_recomputed_here_agrees_with_the_committed_one_where_it_exists(mono):
    """The monovalent artifact carries its own `rank_of_target`. Recomputing it and agreeing is the
    cross-check that the reader is reading what it thinks it is."""
    rows = mono["family_wide_window"]["monovalent"]["corridor"]
    checked = 0
    for r in rows:
        if "rank_of_target" not in r:
            continue
        s = Q10.cell_stats(r)
        if s is None:
            continue
        assert s["rank_of_target"] == r["rank_of_target"], r["cell"]
        checked += 1
    assert checked > 0, "no committed rank was available to check against"


# ==========================================================================================================
# AXIS A — the ablation's own axis
# ==========================================================================================================
def test_axis_A_counts_only_the_E3_specific_refusal(doc):
    """⛔ THE LOAD-BEARING TEST. `placement_admissibility` refuses on two grounds and only ONE is
    E3-specific. A monovalent molecule still needs room at the warhead."""
    f = doc["★_axis_A_admissible_space"]["admissibility_filter"]
    assert f["⭑_retired_by_removing_the_E3_arm"] == f["n_refused_because_the_E3_ANCHOR_IS_BURIED"]
    assert f["⛔_NOT_retired"] == f["n_refused_because_the_WARHEAD_ANCHOR_HAS_NO_ROOM"]
    assert f["⛔_NOT_retired"] > f["⭑_retired_by_removing_the_E3_arm"], (
        "if the warhead refusal ever became the smaller term this reading needs revisiting deliberately")


def test_axis_A_reports_losses_beside_gains(doc):
    """A gain-only readout would render a net loss as a confirmation."""
    for conv, t in doc["★_axis_A_admissible_space"]["paired_transitions"].items():
        assert set(t) >= {"closed_to_open", "open_to_closed", "net_change_in_open_cells"}
        assert t["net_change_in_open_cells"] == t["closed_to_open"] - t["open_to_closed"]


def test_the_paired_transitions_are_read_from_the_committed_artifact_not_recomputed(doc, mono):
    src = mono["paired_transitions"]["by_convention"]
    for conv, t in doc["★_axis_A_admissible_space"]["paired_transitions"].items():
        assert t["closed_to_open"] == src[conv]["closed_to_open"]
        assert t["open_to_closed"] == src[conv]["open_to_closed"]


# ==========================================================================================================
# AXIS B and the discriminator
# ==========================================================================================================
def test_axis_B_reproduces_the_committed_open_window_counts(doc, mono):
    biv = mono["summary"]["bivalent"]
    for conv, r in doc["★_axis_B_the_selectivity_window"].items():
        assert r["bivalent"]["n_open_window"] == biv[conv]["n_open"], conv
        assert r["monovalent"]["n_open_window"] == mono["summary"]["monovalent"][conv]["n_open"], conv


def test_the_discriminator_test_names_the_observation_that_separates_the_two_hypotheses(doc):
    d = doc["★_the_discriminator_test"]
    assert "COST" in d["_what"] and "DISCRIMINATOR" in d["_what"]
    for conv, r in d["by_convention"].items():
        assert r["margin_degraded"] is not None and r["rank_degraded"] is not None


def test_the_discriminator_verdict_matches_its_own_evidence(doc):
    d = doc["★_the_discriminator_test"]
    both = [c for c, r in d["by_convention"].items() if r["margin_degraded"] and r["rank_degraded"]]
    assert sorted(both) == d["conventions_where_BOTH_margin_and_rank_degrade"]
    assert ("DISCRIMINATOR, NOT ONLY A COST" in d["⭐_verdict"]) == bool(both)


# ==========================================================================================================
# THE VERDICT — the two axes must never render alike
# ==========================================================================================================
def test_the_verdict_does_not_read_axis_A_as_a_rescue(doc):
    v = doc["★_verdict"]
    assert v["prediction_holds_on_axis_A"] is True
    assert v["prediction_rescues_the_route"] is False
    assert "DOES NOT RESCUE" in v["headline"]
    assert "NEVER PREDICTED" in v["headline"]


def test_the_stale_row_correction_names_both_documents(doc):
    st = doc["⭑_the_stale_row_this_pass_corrects"]
    assert "§10.1a" in st["what_the_board_says"]
    assert "path-family-synthesis" in st["what_the_board_says"]
    assert st["the_committed_answer"] == "WORSE"


def test_the_cost_section_does_not_inherit_the_TCIP_correction(doc):
    """⛔ §10.1b's 2026-08-06 correction — a TCIP retires only R12 — applies to the TCIP row, not this
    one. A monovalent inhibitor induces no ternary, so R9 and R10 go with R12."""
    c = doc["★_what_picking_this_configuration_costs"]
    joined = " ".join(c["retires"])
    for r in ("R9", "R10", "R12"):
        assert r in joined
    assert "TCIP" in c["⚠_do_not_confuse_this_with_the_TCIP_row"]


def test_the_non_covalent_monovalent_route_is_explicitly_not_refuted(doc):
    blob = " ".join(doc["⛔_what_this_does_not_license"])
    assert "NON-covalent monovalent" in blob


def test_the_pose_marginalisation_cites_the_second_method_result(doc):
    ev = doc["_pose_marginalisation"]["evidence"]
    assert ev["read"] is True
    assert ev["R5_resolved"] is False


def test_the_ablation_numbers_are_read_from_their_one_home(doc):
    tc = json.load(open(Q10.TCIP, encoding="utf-8"))[Q10.ABLATION_KEY]
    got = doc["the_prediction"]["_from"]
    assert got["ratio_at_the_committed_floor"] == tc["ratio_at_the_committed_floor"]
    assert got["ratio_with_no_interface_floor"] == tc["ratio_with_no_interface_floor"]
    assert got["the_sign_inverts"] is True
