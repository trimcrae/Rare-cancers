#!/usr/bin/env python3
"""Pins for the valB FAIL blast-radius derivation.

The point of these tests is NOT that the arithmetic runs -- it is that the three claims the program is about to
act on cannot be quietly reversed: (a) sigma_leg is bounded by measurement and the bound is an UPPER one,
(b) the frozen prereg rule is recorded and NOT amended, (c) the S decision rule can admit but never kill on one
draw."""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import valb_failure_propagation as P  # noqa: E402
from valb_triangle_closure import closure_noise_floor  # noqa: E402


# ---- 1. the sigma_leg bound -------------------------------------------------------------------------------
def test_sigma_leg_bound_uses_the_designs_own_sd_relation():
    """sigma_edge = sqrt(2)*sigma_leg is closure_noise_floor's relation, not one invented here."""
    b = P.sigma_leg_now_bounded()
    assert b["measured_sigma_edge_kcal"] == pytest.approx(P.MEASURED["cycle_sd_kcal"])
    assert b["sigma_leg_upper_bound_kcal"] == pytest.approx(
        P.MEASURED["cycle_sd_kcal"] / math.sqrt(2.0), abs=1e-4)


def test_the_bound_is_tighter_than_the_designs_original_upper_bound():
    """If this ever fails, the measurement stopped buying anything and the file's premise is gone."""
    b = P.sigma_leg_now_bounded()
    assert b["sigma_leg_upper_bound_kcal"] < b["superseded_upper_bound"]
    assert b["uncertainty_factor_after"] < b["uncertainty_factor_before"]


def test_it_is_labelled_an_upper_bound_with_both_reasons_intact():
    """Quoting the bound as a VALUE would understate the triangle's power. Both reasons must survive edits."""
    b = P.sigma_leg_now_bounded()
    why = b["why_it_is_an_upper_bound_not_a_value"]
    assert set(why) == {"a_homology_model_swap", "b_independent_solvation"}
    assert "single-seed" in why["a_homology_model_swap"] or "same_seed" in why["a_homology_model_swap"]


def test_the_excluded_range_is_the_one_where_the_triangle_was_hopeless():
    """The design's 0.5 and 0.7 rows must genuinely sit above the new bound, or 'excluded' is a false claim."""
    b = P.sigma_leg_now_bounded()
    rows = {r["sigma_leg"]: r for r in closure_noise_floor()["rows"]}
    for sl in (0.5, 0.7):
        assert sl > b["sigma_leg_upper_bound_kcal"]
        assert rows[sl]["power_at_n1"]["detect_1.478"] < 0.25


# ---- 2. the frozen rule is RECORDED, not retuned ----------------------------------------------------------
def test_the_frozen_prereg_rule_is_not_amended_here():
    """binary_departure_prereg's 0.2 proxy must be untouched -- this file records, it does not retune."""
    import inspect

    import valb_triangle_closure as V
    src = inspect.getsource(V.binary_departure_prereg)
    assert "sigma_leg) > 0.2" in src, "the frozen proxy was edited; that needs a dated defect-fix, not a commit"
    f = P.frozen_rule_vs_measured_power()
    assert f["action_taken_here"].startswith("NONE")


def test_the_proxy_is_graded_against_the_computed_crossing_not_against_a_hunch():
    """The first draft of this analysis assumed the proxy was misfiring. It is not -- 0.200 against a computed
    0.80-power crossing near 0.216. This test exists so that correction cannot be silently undone."""
    f = P.frozen_rule_vs_measured_power()
    assert f["frozen_rule_fires"] is True
    assert 0.0 < f["actual_power_to_detect_1.478_at_that_sigma"] < 1.0
    assert f["proxy_error_vs_computed"] < 0.15, "the proxy and the computed crossing must still agree closely"
    assert "nearly right" in f["the_finding"]
    assert "the_honest_residual" in f


def test_the_amendment_is_not_sold_as_a_rescue():
    """At the measured upper bound a conventional threshold demotes anyway. If this ever flips to True without
    the power changing, someone has oversold the fix."""
    f = P.frozen_rule_vs_measured_power()
    assert f["would_amending_it_rescue_a_null_R"] is False
    assert "not the verdict" in f["why_not"]
    assert "LOW STAKES" in f["action_proposed_to_trimcrae"]


def test_the_power_crossing_brackets_the_measured_bound():
    """The whole live question is whether the true sigma_leg is above or below the crossing. If the bound fell
    below it, the question would be closed and §7 would be pointless."""
    crossing = P.power_threshold_crossing()
    hi = P.sigma_leg_now_bounded()["sigma_leg_upper_bound_kcal"]
    lo = P.sigma_leg_now_bounded()["sigma_leg_lower_bound_kcal"]
    assert lo < crossing < hi, "the crossing must sit INSIDE the bounded interval or §7 buys nothing"


# ---- 3. the propagation table ------------------------------------------------------------------------------
def test_every_quantity_declares_its_expression_and_status():
    rows = P.error_algebra()
    assert len(rows) >= 5
    for r in rows:
        assert r["expression"] and r["status"] and r["consequence"]


def test_the_failed_quantity_and_the_flagship_are_classified_oppositely():
    """This is the file's central claim. If these two ever read the same, the analysis has collapsed."""
    rows = {r["quantity"].split(" (")[0]: r for r in P.error_algebra()}
    coop = rows["ddG_coop"]
    s = rows["S"]
    assert "MEASURED FAILURE" in coop["status"]
    assert "NUMERICAL ONLY" in coop["cancellation"]
    assert "ALGEBRAIC" in s["cancellation"]
    assert "NOT DIRECTLY IMPLICATED" in s["status"]


def test_the_binary_rbfe_lane_and_the_categorical_axes_are_untouched():
    rows = {r["quantity"].split(" (")[0]: r for r in P.error_algebra()}
    assert rows["ddG_bind"]["status"] == "UNAFFECTED"
    assert rows["the categorical axes"]["status"] == "UNAFFECTED"


# ---- 4. the S decision rule --------------------------------------------------------------------------------
def test_s_rule_is_a_preregistration_until_R_exists():
    out = P.s_resolvability_from_R_ternary()
    assert out["verdict"].startswith("NOT YET MEASURED")


def test_s_rule_branches_in_the_right_order():
    thr = P.s_resolvability_from_R_ternary()["R_ternary_resolution_threshold"]
    crit = P.s_resolvability_from_R_ternary()["R_ternary_critical_for_S"]
    assert thr < crit, "a resolvable R must not immediately be a stopping R"
    assert P.s_resolvability_from_R_ternary(R_ternary=0.0)["verdict"] == "ADMIT"
    assert P.s_resolvability_from_R_ternary(R_ternary=(thr + crit) / 2)["verdict"] == "HOLD"
    assert P.s_resolvability_from_R_ternary(R_ternary=crit * 1.1)["verdict"] == "STOP_AND_REDRAW"


def test_a_large_R_can_never_be_written_as_a_kill():
    """closure_noise_floor's asymmetry: one draw cannot convict. The worst verdict must be a redraw."""
    out = P.s_resolvability_from_R_ternary(R_ternary=99.0)
    assert out["verdict"] == "STOP_AND_REDRAW"
    assert "never a kill" in out["rule"]["STOP_AND_REDRAW"]


def test_the_sign_of_R_does_not_matter():
    a = P.s_resolvability_from_R_ternary(R_ternary=2.5)["verdict"]
    b = P.s_resolvability_from_R_ternary(R_ternary=-2.5)["verdict"]
    assert a == b


def test_the_state_function_blind_spot_is_stated():
    """An ADMIT bounds the non-conservative class ONLY. If this text goes, ADMIT starts reading as a
    certification it is not."""
    out = P.s_resolvability_from_R_ternary()
    assert "blind" in out["_blind_spot_stated"]
    assert "state-function" in out["_blind_spot_stated"]


# ---- 5. S's own error-bar scope ----------------------------------------------------------------------------
def test_the_replicate_over_mbar_factor_is_derived_from_the_measured_inputs():
    e = P.s_error_bar_scope()
    lo, hi = P.MEASURED["per_leg_mbar_se_kcal"]
    assert e["replicate_sd_over_mbar_se_measured"] == pytest.approx(
        P.MEASURED["cycle_sd_kcal"] / ((lo + hi) / 2.0), abs=0.01)


def test_the_correction_widens_rather_than_narrows():
    e = P.s_error_bar_scope()
    assert e["S_err_after_the_measured_correction_kcal"] > e["S_err_as_it_would_be_reported_kcal"]


def test_the_second_seed_option_carries_its_unverified_warning():
    """The seed -> model wrap is a real trap on the SMARCA2 lane and is UNVERIFIED for 5a-KS. If this text is
    dropped, someone buys a second seed that re-runs the first model."""
    opt = P.s_error_bar_scope()["options"]["add_one_seed_per_arm"]
    assert "UNVERIFIED" in opt


# ---- 6. the estimator note ---------------------------------------------------------------------------------
def test_paired_interval_is_recomputed_not_asserted():
    n = P.estimator_note()["paired_estimator_recomputed_here"]
    assert n["mean_kcal"] == pytest.approx(-0.599, abs=0.001)
    assert n["paired_sd_kcal"] == pytest.approx(P.MEASURED["cycle_sd_kcal"], abs=0.001)


def test_the_note_does_not_propose_switching_estimators():
    e = P.estimator_note()
    assert "record it" in e["action"]
    assert "estimator-independent" in e["what_is_unaffected"]


# ---- 7. narrowing sigma_leg from the triangle's own legs ---------------------------------------------------
def test_narrowing_is_not_computable_before_the_legs_land():
    n = P.narrow_sigma_leg_from_triangle_legs()
    assert n["estimate"].startswith("NOT YET COMPUTABLE")
    assert n["cost"].startswith("$0")


def test_narrowing_declares_the_ratio_is_transferred_not_measured():
    """The transfer is the whole weakness. If this flag goes, the estimate starts reading as a measurement of
    the triangle's own spread, which it is not -- the triangle has no replicates."""
    n = P.narrow_sigma_leg_from_triangle_legs()
    assert n["_ratio_is_transferred_not_measured_here"] is True


def test_narrowing_can_land_on_either_side_of_the_crossing():
    """If it could only ever clear (or only ever fail), it would not be a measurement worth taking."""
    crossing = P.power_threshold_crossing()
    ratio = P.s_error_bar_scope()["replicate_sd_over_mbar_se_measured"]
    lo_se, hi_se = crossing / ratio * 0.5, crossing / ratio * 1.5
    assert P.narrow_sigma_leg_from_triangle_legs(lo_se)["clears_conventional_power"] is True
    assert P.narrow_sigma_leg_from_triangle_legs(hi_se)["clears_conventional_power"] is False


# ---- 8. the wiring into the reducer -------------------------------------------------------------------------
# Built BEFORE R landed, because a reader written after seeing the number is not a pre-registration. The repo
# has been bitten by the opposite failure -- a diagnostic "built but never wired to any dispatch path" -- and
# these tests exist so the addendum cannot silently stop being emitted.
def _addendum(R_t=0.05, R_b=0.03, ses=(0.09, 0.10, 0.11, 0.095)):
    import valb_triangle_reduce as VR
    return VR._measured_sigma_addendum({"R_ternary": R_t, "R_binary": R_b}, R_t - R_b, list(ses), 0.045, 0.7)


def test_the_addendum_never_overwrites_the_frozen_decision():
    """The narrowed band makes R_RESOLVED_PATH_ERROR easier to reach -- the HOPEFUL branch. A change that
    favours the outcome we want must not be applied silently to the frozen rule."""
    a = _addendum()
    assert "NOT the lane's verdict" in a["_do_not_conflate"]
    assert a["ambiguous_band_at_measured_bound"][1] < a["ambiguous_band_frozen"][1]


def test_the_superseded_assumption_is_retained_not_dropped():
    a = _addendum()
    assert a["sigma_leg_upper_bound_superseded_assumption"] == 0.7
    assert a["sigma_leg_upper_bound_measured"] < 0.7


def test_the_5aks_verdict_is_driven_by_R_ternary_not_R_coop():
    """S lives in the ternary environment. If this ever keys off R_coop, a large R_ternary cancelled by a
    large R_binary would wrongly read as safe."""
    safe = _addendum(R_t=0.05, R_b=0.03)["5aKS_resume_verdict"]["verdict"]
    # same R_coop (0.02) but a large R_ternary -> must NOT read the same
    risky = _addendum(R_t=2.00, R_b=1.98)["5aKS_resume_verdict"]["verdict"]
    assert safe == "ADMIT"
    assert risky == "STOP_AND_REDRAW"


def test_the_addendum_spans_all_three_decisions():
    assert _addendum(R_t=0.05, R_b=0.03)["decision_at_measured_bound"] == "R_CONSISTENT_WITH_ZERO"
    assert _addendum(R_t=0.90, R_b=0.20)["decision_at_measured_bound"] == "AMBIGUOUS_AT_n1"
    assert _addendum(R_t=2.00, R_b=0.40)["decision_at_measured_bound"] == "R_RESOLVED_PATH_ERROR"


def test_the_addendum_consumes_the_triangles_own_mbar_ses():
    """This is the whole point of §7 -- the estimate must move with the legs' own SEs, not be a constant."""
    tight = _addendum(ses=(0.04, 0.04, 0.05, 0.045))["sigma_leg_from_the_triangles_own_legs"]
    loose = _addendum(ses=(0.12, 0.13, 0.14, 0.125))["sigma_leg_from_the_triangles_own_legs"]
    assert tight["sigma_leg_estimate_kcal"] < loose["sigma_leg_estimate_kcal"]
    assert tight["clears_conventional_power"] is True
    assert loose["clears_conventional_power"] is False


def test_the_addendum_survives_legs_with_no_mbar_se():
    """A leg record missing mbar_se_kcal must not crash the reduction -- it must degrade to 'not computable'."""
    a = _addendum(ses=(None, None, None, None))
    assert a["sigma_leg_from_the_triangles_own_legs"]["estimate"].startswith("NOT YET COMPUTABLE")


# ---- 9. the memoisation must not leak a shared mutable ------------------------------------------------------
def test_cached_derivations_hand_back_copies():
    """These are memoised because a bisection over Monte Carlo draws is expensive. `build_report` EMBEDS the
    returned dicts, so handing back the cached object itself would let any downstream mutation corrupt every
    later call in the process -- a silent, order-dependent bug of exactly the kind this repo keeps finding."""
    a = P.sigma_leg_now_bounded()
    a["sigma_leg_upper_bound_kcal"] = 999.0
    assert P.sigma_leg_now_bounded()["sigma_leg_upper_bound_kcal"] != 999.0

    b = P.power_at_measured_bound()
    b["graded_at"] = "clobbered"
    assert P.power_at_measured_bound()["graded_at"] != "clobbered"


def test_memoisation_is_deterministic_not_just_fast():
    """Caching is only legitimate because closure_noise_floor seeds its RNG with a fixed constant. If that
    ever changes, the cache would freeze one arbitrary draw and this test should fail."""
    P.power_threshold_crossing.cache_clear()
    first = P.power_threshold_crossing()
    P.power_threshold_crossing.cache_clear()
    assert P.power_threshold_crossing() == first


# ---- report ------------------------------------------------------------------------------------------------
def test_report_is_json_serialisable_and_complete():
    import json
    rep = P.build_report()
    json.dumps(rep)
    for k in ("1_sigma_leg_now_bounded", "2_frozen_rule_vs_measured_power", "3_error_algebra",
              "4_s_resolvability_prereg", "5_s_error_bar_scope", "6_estimator_note"):
        assert k in rep
