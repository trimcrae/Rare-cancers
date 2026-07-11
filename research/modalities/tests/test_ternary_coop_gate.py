"""Unit tests for ternary_coop_gate.py — the pure prereg-§3 retrospective-bar gate.

Exercises each of the four sub-gates (technical convergence, quantitative VHL panel, NR-V04 affinity
control, NR4A family transfer) and the top-level verdict logic (True only if ALL pass; False on any
available fail; None while any is deferred) — all without numpy/MD/GPU. Reads the REAL frozen thresholds
from nr4a3-ternary-coop-prereg.json so a drift between the JSON and the code is caught here."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop_gate as g  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(os.path.dirname(HERE), "nr4a3-ternary-coop-prereg.json")


def _bar():
    return g.load_frozen(FROZEN)


# --- fixtures: a fully-passing results dict, then break one field at a time -----------------------------------
def _passing_results():
    return {
        "legs": [
            {"name": "vhl_calib_hi", "n_replicas": 3, "hysteresis_kcal": 0.4, "ci95_half_width_kcal": 1.0,
             "n_starting_poses": 2, "rank_reversal_under_loo": False, "pathology": False},
            {"name": "nrv04_nr4a1_ternary", "n_replicas": 3, "cycle_closure_kcal": 0.8,
             "ci95_half_width_kcal": 1.2, "n_starting_poses": 2, "rank_reversal_under_loo": False,
             "pathology": False},
        ],
        "vhl_panel": {
            "n_systems": 6, "n_class_correct": 6,
            "predicted_alpha": [0.2, 0.5, 1.0, 5.0, 30.0, 90.0],
            "measured_alpha": [0.3, 0.4, 1.2, 6.0, 25.0, 93.0],
            "inactive_stereo_control_classified_competent": False,
            "survives_leave_one_compound_out": True,
        },
        "nrv04_affinity_control": {
            "active_vs_epimer_binary_vhl_kcal": 3.5, "binary_vhl_ci_low": 2.1, "binary_vhl_ci_high": 4.9,
            "active_vs_epimer_effective_ternary_kcal": 2.4, "any_retained_pose_reverses": False,
        },
        "nr4a_family_transfer": {
            "recruit_diff_nr4a1_vs_nr4a2_kcal": 1.6, "recruit_diff_nr4a1_vs_nr4a2_ci_lo": 0.5,
            "recruit_diff_nr4a1_vs_nr4a2_ci_hi": 2.7,
            "recruit_diff_nr4a1_vs_nr4a3_kcal": 1.3, "recruit_diff_nr4a1_vs_nr4a3_ci_lo": 0.3,
            "recruit_diff_nr4a1_vs_nr4a3_ci_hi": 2.3,
            "joint_prob_nr4a1_best": 0.94, "survives_pose_and_conformer_sensitivity": True,
        },
    }


# =============================================================================================================
# top-level verdict
# =============================================================================================================
def test_full_pass_authorizes_prospective():
    res = g.evaluate_retrospective_bar(_passing_results(), FROZEN)
    assert res["prospective_ranking_authorized"] is True
    assert all(s["passed"] is True for s in res["sub_gates"].values())


def test_empty_results_defers_everything():
    res = g.evaluate_retrospective_bar({}, FROZEN)
    assert res["prospective_ranking_authorized"] is None
    assert all(s["passed"] is None for s in res["sub_gates"].values())


def test_any_available_fail_makes_verdict_false_even_with_deferred():
    # only the affinity control present, and it FAILS → verdict False despite the other three deferred
    bad = {"nrv04_affinity_control": {"active_vs_epimer_binary_vhl_kcal": 0.5, "binary_vhl_ci_low": -1.0,
                                      "binary_vhl_ci_high": 2.0,
                                      "active_vs_epimer_effective_ternary_kcal": 0.1,
                                      "any_retained_pose_reverses": True}}
    res = g.evaluate_retrospective_bar(bad, FROZEN)
    assert res["prospective_ranking_authorized"] is False


# =============================================================================================================
# sub-gate 1 — technical convergence
# =============================================================================================================
def test_technical_convergence_pass():
    assert g.gate_technical_convergence(_passing_results(), _bar())["passed"] is True


def test_technical_convergence_too_few_replicas_fails():
    r = _passing_results()
    r["legs"][0]["n_replicas"] = 2
    out = g.gate_technical_convergence(r, _bar())
    assert out["passed"] is False
    assert any("n_replicas" in x for f in out["failures"] for x in f["reasons"])


def test_technical_convergence_wide_ci_fails():
    r = _passing_results()
    r["legs"][1]["ci95_half_width_kcal"] = 2.0  # > 1.5
    assert g.gate_technical_convergence(r, _bar())["passed"] is False


def test_technical_convergence_loo_reversal_fails():
    r = _passing_results()
    r["legs"][0]["rank_reversal_under_loo"] = True
    assert g.gate_technical_convergence(r, _bar())["passed"] is False


def test_technical_convergence_single_pose_fails():
    r = _passing_results()
    r["legs"][0]["n_starting_poses"] = 1
    assert g.gate_technical_convergence(r, _bar())["passed"] is False


def test_technical_convergence_deferred_when_no_legs():
    out = g.gate_technical_convergence({}, _bar())
    assert out["passed"] is None and out["available"] is False


# =============================================================================================================
# sub-gate 2 — VHL panel
# =============================================================================================================
def test_vhl_panel_pass():
    assert g.gate_vhl_panel(_passing_results(), _bar())["passed"] is True


def test_vhl_panel_class_correct_below_five_of_six_fails():
    r = _passing_results()
    r["vhl_panel"]["n_class_correct"] = 4
    assert g.gate_vhl_panel(r, _bar())["passed"] is False


def test_vhl_panel_inactive_stereo_competent_fails():
    r = _passing_results()
    r["vhl_panel"]["inactive_stereo_control_classified_competent"] = True
    assert g.gate_vhl_panel(r, _bar())["passed"] is False


def test_vhl_panel_low_tau_fails():
    r = _passing_results()
    # reverse the predicted order vs measured → tau strongly negative
    r["vhl_panel"]["predicted_alpha"] = [90.0, 30.0, 5.0, 1.0, 0.5, 0.2]
    out = g.gate_vhl_panel(r, _bar())
    assert out["passed"] is False
    assert out["kendall_tau"] is not None and out["kendall_tau"] < 0.5


def test_vhl_panel_leave_one_out_fail():
    r = _passing_results()
    r["vhl_panel"]["survives_leave_one_compound_out"] = False
    assert g.gate_vhl_panel(r, _bar())["passed"] is False


def test_vhl_panel_scales_requirement_for_larger_panel():
    # 12-system panel must get >= ceil(5/6*12)=10 correct; 9 fails, 10 passes (other criteria held ok)
    r = _passing_results()
    r["vhl_panel"]["n_systems"] = 12
    r["vhl_panel"]["predicted_alpha"] = list(range(12))
    r["vhl_panel"]["measured_alpha"] = list(range(12))
    r["vhl_panel"]["n_class_correct"] = 9
    assert g.gate_vhl_panel(r, _bar())["passed"] is False
    r["vhl_panel"]["n_class_correct"] = 10
    assert g.gate_vhl_panel(r, _bar())["passed"] is True


# =============================================================================================================
# sub-gate 3 — NR-V04 affinity control
# =============================================================================================================
def test_affinity_control_pass():
    assert g.gate_nrv04_affinity_control(_passing_results(), _bar())["passed"] is True


def test_affinity_control_binary_margin_too_small_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["active_vs_epimer_binary_vhl_kcal"] = 2.0  # < 3.0
    assert g.gate_nrv04_affinity_control(r, _bar())["passed"] is False


def test_affinity_control_ci_includes_zero_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["binary_vhl_ci_low"] = -0.5  # straddles zero
    assert g.gate_nrv04_affinity_control(r, _bar())["passed"] is False


def test_affinity_control_ternary_margin_too_small_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["active_vs_epimer_effective_ternary_kcal"] = 1.0  # < 2.0
    assert g.gate_nrv04_affinity_control(r, _bar())["passed"] is False


def test_affinity_control_pose_reversal_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["any_retained_pose_reverses"] = True
    assert g.gate_nrv04_affinity_control(r, _bar())["passed"] is False


# =============================================================================================================
# sub-gate 4 — NR4A family transfer
# =============================================================================================================
def test_family_transfer_pass():
    assert g.gate_nr4a_family_transfer(_passing_results(), _bar())["passed"] is True


def test_family_transfer_small_diff_fails():
    r = _passing_results()
    r["nr4a_family_transfer"]["recruit_diff_nr4a1_vs_nr4a3_kcal"] = 0.5  # < 1.0
    assert g.gate_nr4a_family_transfer(r, _bar())["passed"] is False


def test_family_transfer_ci_touches_zero_fails():
    r = _passing_results()
    r["nr4a_family_transfer"]["recruit_diff_nr4a1_vs_nr4a2_ci_lo"] = -0.1  # not > 0
    assert g.gate_nr4a_family_transfer(r, _bar())["passed"] is False


def test_family_transfer_low_joint_prob_fails():
    r = _passing_results()
    r["nr4a_family_transfer"]["joint_prob_nr4a1_best"] = 0.90  # must be > 0.90 (strict)
    assert g.gate_nr4a_family_transfer(r, _bar())["passed"] is False


def test_family_transfer_sensitivity_fail():
    r = _passing_results()
    r["nr4a_family_transfer"]["survives_pose_and_conformer_sensitivity"] = False
    assert g.gate_nr4a_family_transfer(r, _bar())["passed"] is False


# =============================================================================================================
# frozen-threshold sanity (guards against silent drift in the JSON)
# =============================================================================================================
def test_frozen_thresholds_match_prereg_numbers():
    b = _bar()
    assert b["technical_convergence"]["min_replicas_per_leg"] == 3
    assert b["technical_convergence"]["ci95_half_width_kcal_max"] == 1.5
    assert b["vhl_panel"]["correct_cooperativity_class_min_of_6"] == 5
    assert b["vhl_panel"]["kendall_tau_min"] == 0.5
    assert b["nrv04_affinity_control"]["active_vs_epimer_binary_vhl_min_kcal"] == 3.0
    assert b["nrv04_affinity_control"]["active_vs_epimer_effective_ternary_min_kcal"] == 2.0
    assert b["nr4a_family_transfer"]["each_difference_min_kcal"] == 1.0
    assert b["nr4a_family_transfer"]["joint_prob_nr4a1_best_min"] == 0.90


def test_kendall_tau_pure_helper():
    assert g._kendall_tau([1, 2, 3], [1, 2, 3]) == 1.0
    assert g._kendall_tau([1, 2, 3], [3, 2, 1]) == -1.0
