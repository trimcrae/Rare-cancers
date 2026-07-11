"""Unit tests for ternary_coop_gate.py — the pure, HARDENED prereg-§3 retrospective-bar gate.

Covers the four scientific sub-gates + CI-coverage + top-level verdict logic, AND every failure mode the
reviewer required (fix 8): NaN/inf, missing required booleans, <6 systems, n_class_correct>n_systems,
missing/duplicated system IDs, unverified systems, missing expected legs, reordered arrays, tied cooperativity,
reversed/incomplete intervals, positive estimate with a negative CI, probability outside [0,1], and every
numeric boundary at exactly the registered threshold. No numpy/MD/GPU — reads the REAL frozen JSON so any
JSON<->code drift is caught here."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop_gate as g  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(os.path.dirname(HERE), "nr4a3-ternary-coop-prereg.json")
NAN = float("nan")
INF = float("inf")


def _frozen():
    return g.load_frozen(FROZEN)


# =============================================================================================================
# fully-passing fixtures
# =============================================================================================================
def _passing_legs():
    exp = _frozen()["frozen_manifest"]["ternary_pilot_expected_leg_ids"]
    return [{"name": nm, "n_replicas": 3, "hysteresis_kcal": 0.4, "ci95_half_width_kcal": 1.0,
             "n_starting_poses": 2, "rank_reversal_under_loo": False, "pathology": False} for nm in exp]


def _passing_panel_systems():
    # 6 systems: 2 strong-cooperative, 2 weak/negative, 1 inactive control, 1 independent (MZ1). Predicted
    # alpha tracks measured (tau_b = 1 over the 5 scoring systems). Inactive control predicted non-competent.
    return [
        {"id": "smarca2_strong_a", "role": "cooperative", "verified": True, "independent_vhl": False,
         "is_mz1": False, "predicted_alpha": 40.0, "measured_alpha": 60.0, "dg_coop_ci_half_width_kcal": 1.0},
        {"id": "smarca2_strong_b", "role": "cooperative", "verified": True, "independent_vhl": False,
         "is_mz1": False, "predicted_alpha": 8.0, "measured_alpha": 10.0, "dg_coop_ci_half_width_kcal": 1.0},
        {"id": "smarca2_weak_a", "role": "anti_cooperative", "verified": True, "independent_vhl": False,
         "is_mz1": False, "predicted_alpha": 0.3, "measured_alpha": 0.2, "dg_coop_ci_half_width_kcal": 1.1},
        {"id": "smarca2_neutral_b", "role": "neutral", "verified": True, "independent_vhl": False,
         "is_mz1": False, "predicted_alpha": 1.0, "measured_alpha": 1.1, "dg_coop_ci_half_width_kcal": 1.2},
        {"id": "mz1_brd4", "role": "cooperative", "verified": True, "independent_vhl": True,
         "is_mz1": True, "predicted_alpha": 18.0, "measured_alpha": 20.0, "dg_coop_ci_half_width_kcal": 0.9},
        {"id": "smarca2_inactive_cis", "role": "inactive_control", "verified": True, "independent_vhl": False,
         "is_mz1": False, "predicted_alpha": 0.4, "measured_alpha": None, "dg_coop_ci_half_width_kcal": None},
    ]


def _passing_decision_quantities():
    base = ["nrv04_active_vs_epimer_binary_vhl", "nrv04_active_vs_epimer_effective_ternary",
            "nr4a1_vs_nr4a2_effective_recruit", "nr4a1_vs_nr4a3_effective_recruit"]
    dyn = ["vhl_dg_coop::%s" % s["id"] for s in _passing_panel_systems() if s["role"] != "inactive_control"]
    return [{"id": i, "estimate": 2.5, "ci_lo": 1.6, "ci_hi": 3.4, "half_width": 0.9, "interval_level": 0.95}
            for i in base + dyn]


def _passing_results():
    return {
        "legs": _passing_legs(),
        "vhl_panel": {"systems": _passing_panel_systems()},
        "nrv04_affinity_control": {
            "active_vs_epimer_binary_vhl_kcal": 3.5, "binary_vhl_ci_low": 2.1, "binary_vhl_ci_high": 4.9,
            "active_vs_epimer_effective_ternary_kcal": 2.4, "any_retained_pose_reverses": False},
        "nr4a_family_transfer": {
            "recruit_diff_nr4a1_vs_nr4a2_kcal": 1.6, "recruit_diff_nr4a1_vs_nr4a2_ci_lo": 0.5,
            "recruit_diff_nr4a1_vs_nr4a2_ci_hi": 2.7,
            "recruit_diff_nr4a1_vs_nr4a3_kcal": 1.3, "recruit_diff_nr4a1_vs_nr4a3_ci_lo": 0.3,
            "recruit_diff_nr4a1_vs_nr4a3_ci_hi": 2.3,
            "joint_prob_nr4a1_best": 0.94, "survives_pose_and_conformer_sensitivity": True},
        "decision_quantities": _passing_decision_quantities(),
    }


# =============================================================================================================
# top-level verdict
# =============================================================================================================
def test_full_pass_authorizes_prospective():
    res = g.evaluate_retrospective_bar(_passing_results(), FROZEN)
    assert res["prospective_ranking_authorized"] is True, res["sub_gates"]
    assert all(s["passed"] is True for s in res["sub_gates"].values())


def test_empty_results_defers_everything():
    res = g.evaluate_retrospective_bar({}, FROZEN)
    assert res["prospective_ranking_authorized"] is None
    assert all(s["passed"] is None for s in res["sub_gates"].values())


def test_any_available_fail_makes_verdict_false_even_with_deferred():
    bad = {"nrv04_affinity_control": {"active_vs_epimer_binary_vhl_kcal": 0.5, "binary_vhl_ci_low": -1.0,
           "binary_vhl_ci_high": 2.0, "active_vs_epimer_effective_ternary_kcal": 0.1,
           "any_retained_pose_reverses": True}}
    res = g.evaluate_retrospective_bar(bad, FROZEN)
    assert res["prospective_ranking_authorized"] is False


# =============================================================================================================
# fix 1 — non-finite rejection + fail-closed booleans
# =============================================================================================================
def test_num_rejects_nan_inf_and_bool():
    assert g._num(NAN) is None
    assert g._num(INF) is None
    assert g._num(-INF) is None
    assert g._num(True) is None
    assert g._num("x") is None
    assert g._num(2.5) == 2.5


def test_nan_hysteresis_fails_not_passes():
    r = _passing_results()
    r["legs"][0]["hysteresis_kcal"] = NAN
    assert g.gate_technical_convergence(r, _frozen())["passed"] is False


def test_nan_margin_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["active_vs_epimer_binary_vhl_kcal"] = NAN
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is False


def test_missing_pathology_bool_fails_closed():
    r = _passing_results()
    del r["legs"][0]["pathology"]
    out = g.gate_technical_convergence(r, _frozen())
    assert out["passed"] is False
    assert any("pathology" in x for f in out["failures"] for x in f["reasons"])


def test_missing_pose_reversal_bool_fails_closed():
    r = _passing_results()
    del r["nrv04_affinity_control"]["any_retained_pose_reverses"]
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is False


def test_nonbool_safety_field_fails():
    r = _passing_results()
    r["legs"][0]["rank_reversal_under_loo"] = "false"   # string, not bool
    assert g.gate_technical_convergence(r, _frozen())["passed"] is False


# =============================================================================================================
# fix 2 — expected-leg + expected-system manifests / panel structure
# =============================================================================================================
def test_missing_expected_leg_fails():
    r = _passing_results()
    r["legs"] = r["legs"][:-1]   # drop one required pilot leg
    out = g.gate_technical_convergence(r, _frozen())
    assert out["passed"] is False and out["missing_expected_legs"]


def test_fewer_than_six_systems_fails():
    r = _passing_results()
    r["vhl_panel"]["systems"] = r["vhl_panel"]["systems"][:5]
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False
    assert any("n_systems" in x for x in out["failures"])


def test_duplicate_system_ids_fail():
    r = _passing_results()
    r["vhl_panel"]["systems"][1]["id"] = r["vhl_panel"]["systems"][0]["id"]
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False
    assert any("duplicate" in x for x in out["failures"])


def test_missing_system_id_fails():
    r = _passing_results()
    del r["vhl_panel"]["systems"][0]["id"]
    assert g.gate_vhl_panel(r, _frozen())["passed"] is False


def test_unverified_system_fails():
    r = _passing_results()
    r["vhl_panel"]["systems"][0]["verified"] = False
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False
    assert any("verified" in x for x in out["failures"])


def test_missing_independent_vhl_fails_composition():
    r = _passing_results()
    r["vhl_panel"]["systems"][4]["independent_vhl"] = False   # remove the only independent system
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False
    assert any("independent-VHL" in x for x in out["failures"])


def test_reordered_systems_still_pass():
    r = _passing_results()
    r["vhl_panel"]["systems"] = list(reversed(r["vhl_panel"]["systems"]))
    assert g.gate_vhl_panel(r, _frozen())["passed"] is True


def test_expected_system_id_coverage_enforced_when_frozen(tmp_path):
    # inject a non-empty expected_system_ids into a copy of the frozen JSON and confirm coverage is enforced
    import json
    fr = g.load_frozen(FROZEN)
    fr["calibration"]["layer1_vhl_panel"]["expected_system_ids"] = ["mz1_brd4", "not_present_id"]
    p = tmp_path / "frozen.json"
    p.write_text(json.dumps(fr))
    r = _passing_results()
    out = g.gate_vhl_panel(r, g.load_frozen(str(p)))
    assert out["passed"] is False
    assert any("not_present_id" in x for x in out["failures"])


# =============================================================================================================
# fix 3 — in-gate class correctness + LOO
# =============================================================================================================
def test_class_correct_below_required_fails():
    r = _passing_results()
    # flip a strong-cooperative prediction to clearly anti-cooperative -> class wrong for that system
    r["vhl_panel"]["systems"][0]["predicted_alpha"] = 0.2
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False


def test_n_class_correct_cannot_exceed_n_systems_by_construction():
    # class_correct is COMPUTED, never supplied; it can never exceed n_systems
    r = _passing_results()
    out = g.gate_vhl_panel(r, _frozen())
    assert out["class_correct"] <= out["n_systems"]


def test_inactive_control_competent_fails():
    r = _passing_results()
    r["vhl_panel"]["systems"][5]["predicted_alpha"] = 50.0   # inactive control predicted strongly cooperative
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False
    assert any("competent" in x for x in out["failures"])


def test_loo_fragile_six_system_five_of_six_fails():
    # make exactly one scoring system misclassified -> 5/6 class-correct main passes required(6)=5, but LOO
    # dropping a CORRECT system leaves 4/5 < required(5)=5 -> LOO fails (documented n=6 strictness).
    r = _passing_results()
    r["vhl_panel"]["systems"][1]["predicted_alpha"] = 0.2   # was cooperative(8) -> now anti; class wrong
    out = g.gate_vhl_panel(r, _frozen())
    assert out["passed"] is False
    assert out["loo_failures"]


# =============================================================================================================
# fix 4 — Kendall tau-b + ties
# =============================================================================================================
def test_tau_b_perfect_and_reversed():
    assert g.kendall_tau_b([(1, 1), (2, 2), (3, 3)]) == 1.0
    assert g.kendall_tau_b([(1, 3), (2, 2), (3, 1)]) == -1.0


def test_tau_b_handles_ties_without_inflation():
    # predicted ties on two systems; measured distinct -> tau_b uses the tie-corrected denominator, not a
    # spurious concordant/discordant from an arbitrary rank order.
    t = g.kendall_tau_b([(5.0, 1.0), (5.0, 2.0), (9.0, 3.0)])
    assert t is not None and -1.0 <= t <= 1.0


def test_tied_measured_values_still_score():
    r = _passing_results()
    # two scoring systems share a measured alpha (practically indistinguishable) — must not crash or auto-fail
    r["vhl_panel"]["systems"][0]["measured_alpha"] = 20.0
    r["vhl_panel"]["systems"][4]["measured_alpha"] = 20.0
    out = g.gate_vhl_panel(r, _frozen())
    assert out["kendall_tau_b"] is not None


def test_low_tau_fails():
    r = _passing_results()
    # invert predictions among scoring systems -> tau_b strongly negative
    scoring = [s for s in r["vhl_panel"]["systems"] if s["role"] != "inactive_control"]
    measured = sorted(s["measured_alpha"] for s in scoring)
    for s, m in zip(scoring, reversed(measured)):
        s["predicted_alpha"] = m
    out = g.gate_vhl_panel(r, _frozen())
    assert out["kendall_tau_b"] is not None and out["kendall_tau_b"] < 0.5
    assert out["passed"] is False


# =============================================================================================================
# fix 5 — interval validation + probability bounds
# =============================================================================================================
def test_binary_ci_entirely_below_zero_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["binary_vhl_ci_low"] = -4.0
    r["nrv04_affinity_control"]["binary_vhl_ci_high"] = -2.0   # entirely below zero must NOT pass
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is False


def test_binary_ci_straddles_zero_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["binary_vhl_ci_low"] = -0.5
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is False


def test_reversed_interval_fails():
    r = _passing_results()
    r["nrv04_affinity_control"]["binary_vhl_ci_low"] = 4.9
    r["nrv04_affinity_control"]["binary_vhl_ci_high"] = 2.1   # lo > hi
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is False


def test_family_missing_upper_bound_fails():
    r = _passing_results()
    del r["nr4a_family_transfer"]["recruit_diff_nr4a1_vs_nr4a2_ci_hi"]
    assert g.gate_nr4a_family_transfer(r, _frozen())["passed"] is False


def test_positive_estimate_negative_ci_fails():
    # positive point estimate but an interval that includes/does not exclude zero on the favored side
    r = _passing_results()
    r["nr4a_family_transfer"]["recruit_diff_nr4a1_vs_nr4a3_ci_lo"] = -0.1
    assert g.gate_nr4a_family_transfer(r, _frozen())["passed"] is False


def test_probability_outside_unit_interval_fails():
    for bad in (1.2, -0.1, INF, NAN):
        r = _passing_results()
        r["nr4a_family_transfer"]["joint_prob_nr4a1_best"] = bad
        assert g.gate_nr4a_family_transfer(r, _frozen())["passed"] is False


# =============================================================================================================
# fix 6 — CI coverage manifest
# =============================================================================================================
def test_ci_coverage_pass():
    assert g.gate_ci_coverage(_passing_results(), _frozen())["passed"] is True


def test_ci_coverage_missing_required_id_fails():
    r = _passing_results()
    r["decision_quantities"] = [e for e in r["decision_quantities"]
                                if e["id"] != "nr4a1_vs_nr4a2_effective_recruit"]
    out = g.gate_ci_coverage(r, _frozen())
    assert out["passed"] is False and any("missing required" in x for x in out["failures"])


def test_ci_coverage_missing_dynamic_panel_dq_fails():
    r = _passing_results()
    sid = _passing_panel_systems()[0]["id"]
    r["decision_quantities"] = [e for e in r["decision_quantities"] if e["id"] != "vhl_dg_coop::%s" % sid]
    assert g.gate_ci_coverage(r, _frozen())["passed"] is False


def test_ci_coverage_wide_halfwidth_fails():
    r = _passing_results()
    r["decision_quantities"][0]["ci_lo"] = 0.0
    r["decision_quantities"][0]["ci_hi"] = 4.0     # half-width 2.0 > 1.5
    r["decision_quantities"][0]["half_width"] = 2.0
    assert g.gate_ci_coverage(r, _frozen())["passed"] is False


def test_ci_coverage_wrong_interval_level_fails():
    r = _passing_results()
    r["decision_quantities"][0]["interval_level"] = 0.90
    assert g.gate_ci_coverage(r, _frozen())["passed"] is False


def test_ci_coverage_inconsistent_halfwidth_fails():
    r = _passing_results()
    r["decision_quantities"][0]["half_width"] = 0.1   # inconsistent with (3.4-1.6)/2=0.9
    assert g.gate_ci_coverage(r, _frozen())["passed"] is False


def test_per_system_dg_coop_ci_missing_fails():
    r = _passing_results()
    r["vhl_panel"]["systems"][0]["dg_coop_ci_half_width_kcal"] = None
    assert g.gate_vhl_panel(r, _frozen())["passed"] is False


# =============================================================================================================
# reviewer-confirmed judgment calls + boundary values (fix 8: every numeric boundary at exactly threshold)
# =============================================================================================================
def test_strict_joint_prob_boundary():
    r = _passing_results()
    r["nr4a_family_transfer"]["joint_prob_nr4a1_best"] = 0.90   # must FAIL (strict >)
    assert g.gate_nr4a_family_transfer(r, _frozen())["passed"] is False
    r["nr4a_family_transfer"]["joint_prob_nr4a1_best"] = 0.9001
    assert g.gate_nr4a_family_transfer(r, _frozen())["passed"] is True


def test_binary_margin_exactly_threshold_passes():
    r = _passing_results()
    r["nrv04_affinity_control"]["active_vs_epimer_binary_vhl_kcal"] = 3.0   # >= 3.0 passes
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is True
    r["nrv04_affinity_control"]["active_vs_epimer_binary_vhl_kcal"] = 2.999
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is False


def test_ternary_margin_exactly_threshold_passes():
    r = _passing_results()
    r["nrv04_affinity_control"]["active_vs_epimer_effective_ternary_kcal"] = 2.0
    assert g.gate_nrv04_affinity_control(r, _frozen())["passed"] is True


def test_family_diff_exactly_threshold_passes():
    r = _passing_results()
    r["nr4a_family_transfer"]["recruit_diff_nr4a1_vs_nr4a3_kcal"] = 1.0   # >= 1.0 passes
    assert g.gate_nr4a_family_transfer(r, _frozen())["passed"] is True


def test_ci_halfwidth_exactly_threshold_passes():
    r = _passing_results()
    e = r["decision_quantities"][0]
    e["ci_lo"], e["ci_hi"], e["half_width"] = 1.0, 4.0, 1.5   # exactly 1.5 passes
    assert g.gate_ci_coverage(r, _frozen())["passed"] is True


def test_ci95_leg_halfwidth_boundary():
    r = _passing_results()
    r["legs"][0]["ci95_half_width_kcal"] = 1.5   # <= 1.5 passes
    assert g.gate_technical_convergence(r, _frozen())["passed"] is True
    r["legs"][0]["ci95_half_width_kcal"] = 1.51
    assert g.gate_technical_convergence(r, _frozen())["passed"] is False


def test_larger_panel_class_rule_scales():
    # 12-system panel -> required = max(5, ceil(5/6*12)) = 10. Build 12 verified systems: 10 correct passes.
    r = _passing_results()
    sys12 = []
    for k in range(10):   # 10 scoring cooperative, predicted correct
        sys12.append({"id": "c%d" % k, "role": "cooperative", "verified": True, "independent_vhl": (k == 0),
                      "is_mz1": (k == 0), "predicted_alpha": 10.0 + k, "measured_alpha": 12.0 + k,
                      "dg_coop_ci_half_width_kcal": 1.0})
    sys12.append({"id": "w0", "role": "anti_cooperative", "verified": True, "independent_vhl": False,
                  "is_mz1": False, "predicted_alpha": 0.3, "measured_alpha": 0.2, "dg_coop_ci_half_width_kcal": 1.0})
    sys12.append({"id": "w1", "role": "neutral", "verified": True, "independent_vhl": False,
                  "is_mz1": False, "predicted_alpha": 1.0, "measured_alpha": 1.1, "dg_coop_ci_half_width_kcal": 1.0})
    r["vhl_panel"]["systems"] = sys12
    out = g.gate_vhl_panel(r, _frozen())
    assert out["required_class_correct"] == 10
    assert out["n_systems"] == 12


# =============================================================================================================
# frozen-threshold + S_d definitional sanity (guards JSON drift)
# =============================================================================================================
def test_frozen_thresholds_match_prereg_numbers():
    b = _frozen()["retrospective_bar"]
    assert b["technical_convergence"]["min_replicas_per_leg"] == 3
    assert b["technical_convergence"]["ci95_half_width_kcal_max"] == 1.5
    assert b["vhl_panel"]["min_systems"] == 6
    assert b["vhl_panel"]["kendall_variant"] == "tau_b"
    assert b["vhl_panel"]["kendall_tau_min"] == 0.5
    assert b["vhl_panel"]["class_boundaries"]["alpha_favorable_min"] == 2.0
    assert b["vhl_panel"]["class_boundaries"]["alpha_unfavorable_max"] == 0.5
    assert b["nrv04_affinity_control"]["active_vs_epimer_binary_vhl_min_kcal"] == 3.0
    assert b["nrv04_affinity_control"]["active_vs_epimer_effective_ternary_min_kcal"] == 2.0
    assert b["nr4a_family_transfer"]["each_difference_min_kcal"] == 1.0
    assert b["nr4a_family_transfer"]["joint_prob_nr4a1_best_min"] == 0.90
    assert b["ci_coverage"]["ci_half_width_kcal_max"] == 1.5
    assert b["ci_coverage"]["required_interval_level"] == 0.95


def test_sd_combination_rule_fully_defined():
    cr = _frozen()["combination_rule"]
    for field in ("form", "ranking_direction", "term_definitions", "units", "missing_data_behavior",
                  "tie_policy", "weights_frozen", "robustness_requirement"):
        assert field in cr, "combination_rule missing %s" % field
    for term in ("c", "min_c", "m_t(c)", "m_c(c)", "SD(c*)", "counterexample", "strain_norm", "ubiq_incompat"):
        assert term in cr["term_definitions"], "term_definitions missing %s" % term
    assert cr["weights_frozen"] == {"w_t": 1.0, "w_c": 1.0, "lambda": 1.0, "gamma": 1.0, "eta": 0.5, "rho": 0.5}
    assert cr["robustness_requirement"]["top_k"] == 3


def test_required_correct_helper():
    assert g._required_correct(6) == 5
    assert g._required_correct(7) == 6
    assert g._required_correct(12) == 10
    assert g._required_correct(5) == 5   # floor


def test_classify_alpha_bands():
    assert g.classify_alpha(3.0, 2.0, 0.5) == "cooperative"
    assert g.classify_alpha(0.3, 2.0, 0.5) == "anti_cooperative"
    assert g.classify_alpha(1.0, 2.0, 0.5) == "neutral"
    assert g.classify_alpha(2.0, 2.0, 0.5) == "cooperative"   # boundary inclusive
    assert g.classify_alpha(0.5, 2.0, 0.5) == "anti_cooperative"
    assert g.classify_alpha(None, 2.0, 0.5) is None
    assert g.classify_alpha(NAN, 2.0, 0.5) is None
