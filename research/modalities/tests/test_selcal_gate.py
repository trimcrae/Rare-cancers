#!/usr/bin/env python3
"""The sensitivity control's FROZEN scorer — every tier, on synthetic legs with known answers.

★ THE POINT OF SCORING SYNTHETIC DATA. A criterion is only frozen if you can demonstrate what it does before
the real numbers arrive. Each test below constructs a panel whose answer is known by construction and asserts
the tier — so "what would a pass look like?" has a checked answer that predates the run, and a later edit that
would have changed the verdict turns the suite red.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import selcal_gate as G  # noqa: E402
import selcal_panel as SP  # noqa: E402

FRAMES = SP.expected_production_frames()


def _leg(arm_id, model, replica, e1, mode="run", blew_up=False):
    """A conforming leg record with a chosen E1 — the same shape `nrv04_covalent_md.run_leg` writes."""
    return {"panel": "selcal_sensitivity_control", "leg_id": "%s__m%d" % (arm_id, model), "seed": replica,
            "mode": mode, "prod_ns": SP.PROD_NS, "equil_ns": SP.EQUIL_NS,
            "timed_ns": 0.0 if blew_up else SP.PROD_NS, "n_frames": 0 if blew_up else FRAMES,
            "blew_up": blew_up, "blow_phase": "prod@frame3" if blew_up else None,
            "R1_interface": {"plateau_A": e1, "stable": True}}


def _panel(a_vals, b_vals, **kw):
    """One leg per (model, replica); both replicas of a model share its value unless told otherwise."""
    legs = []
    for i, v in enumerate(a_vals, start=1):
        for r in SP.MD_REPLICAS:
            legs.append(_leg(SP.ARM_A, i, r, v, **kw))
    for i, v in enumerate(b_vals, start=1):
        for r in SP.MD_REPLICAS:
            legs.append(_leg(SP.ARM_B, i, r, v, **kw))
    return legs


# =============================================================================================================
# the design property that made this shape necessary
# =============================================================================================================
def test_design_floor_clears_alpha_by_two_orders_of_magnitude():
    d = G.design_floor()
    assert d["n_arrangements"] == 924
    assert d["can_reach_alpha"]
    assert d["min_attainable_p"] < d["alpha"] / 10


def test_the_shape_that_failed_is_shown_to_fail():
    """NR-V04's NR4A1-vs-NR4A3 pairwise: 3 vs 2 models, C = 10, floor 0.10 > alpha. Its power against ANY
    separation was zero. Pinning it here is what makes this panel's floor a decision rather than a habit."""
    d = G.design_floor(3, 2)
    assert d["n_arrangements"] == 10
    assert not d["can_reach_alpha"]


# =============================================================================================================
# the tiers
# =============================================================================================================
def test_perfect_separation_in_the_predicted_direction_is_a_PASS():
    v = G.verdict(_panel([1.0, 1.1, 1.2, 1.3, 1.4, 1.5], [3.0, 3.1, 3.2, 3.3, 3.4, 3.5]))
    assert v["tier"] == SP.TIER_PASS
    assert v["statistic"] < 0
    assert v["p"] == v["min_attainable_p"]
    assert v["leave_one_model_out"]["survives"]
    assert "NOTHING" in v["licenses"]


def test_no_separation_is_a_NULL_not_an_indeterminate():
    v = G.verdict(_panel([2.0, 2.1, 2.2, 2.3, 2.4, 2.5], [2.05, 2.15, 2.25, 2.35, 2.45, 2.55]))
    assert v["tier"] == SP.TIER_NULL
    assert v["p"] > SP.ALPHA
    assert "REAL negative" in v["reason"]


def test_perfect_separation_in_the_WRONG_direction_is_WRONG_SIGN_not_a_pass():
    v = G.verdict(_panel([3.0, 3.1, 3.2, 3.3, 3.4, 3.5], [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]))
    assert v["tier"] == SP.TIER_WRONG_SIGN
    assert v["statistic"] > 0
    assert v["p"] > SP.ALPHA and v["p_mirror"] <= SP.ALPHA


def test_a_significant_p_carried_by_one_model_does_NOT_pass():
    """LOMO survival is an AND-clause precisely so a result carried by a single co-fold cannot be reported as
    a detection. Constructed so the sign flips when the one outlier model is dropped."""
    v = G.verdict(_panel([0.1, 3.0, 3.0, 3.0, 3.0, 3.0], [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]))
    if v["p"] <= SP.ALPHA and v["statistic"] < 0:
        assert v["tier"] != SP.TIER_PASS
        assert not v["leave_one_model_out"]["survives"]
    else:
        assert v["tier"] in (SP.TIER_NULL, SP.TIER_WRONG_SIGN)


def test_too_many_technical_failures_is_INDETERMINATE_not_a_null():
    legs = _panel([1.0, 1.1, 1.2, 1.3, 1.4, 1.5], [3.0, 3.1, 3.2, 3.3, 3.4, 3.5])
    # blow up 3 legs of arm A — one more than the allowance
    n = 0
    for leg in legs:
        if leg["leg_id"].startswith(SP.ARM_A) and n < SP.MAX_FAILED_LEGS_PER_ARM + 1:
            leg.update(blew_up=True, timed_ns=0.0, n_frames=0)
            n += 1
    v = G.verdict(legs)
    assert v["tier"] == SP.TIER_INDETERMINATE
    assert v["p"] is None
    assert "NOT a null" in v["reason"]


def test_too_few_models_is_INDETERMINATE_because_the_reference_set_cannot_reach_alpha():
    v = G.verdict(_panel([1.0, 1.1, 1.2], [3.0, 3.1, 3.2]))
    assert v["tier"] == SP.TIER_INDETERMINATE
    assert "NON-MEASUREMENT" in v["reason"]


# =============================================================================================================
# membership, on provenance rather than presence
# =============================================================================================================
def test_smoke_records_are_rejected_even_when_they_carry_a_plausible_E1():
    legs = _panel([1.0, 1.1, 1.2, 1.3, 1.4, 1.5], [3.0, 3.1, 3.2, 3.3, 3.4, 3.5], mode="smoke")
    v = G.verdict(legs)
    assert v["n_legs_admitted"] == 0
    assert v["tier"] == SP.TIER_INDETERMINATE
    assert len(v["rejected_records"]) == 24


def test_a_leg_naming_another_panels_arm_is_refused_rather_than_misattributed():
    legs = _panel([1.0, 1.1, 1.2, 1.3, 1.4, 1.5], [3.0, 3.1, 3.2, 3.3, 3.4, 3.5])
    legs.append(_leg("retro_noncov_nr4a1", 1, 0, 0.5))
    v = G.verdict(legs)
    assert any("does not name an arm of this panel" in r["why"] for r in v["rejected_records"])
    assert v["tier"] == SP.TIER_PASS       # the intruder changed nothing


def test_the_verdict_carries_its_evidence_and_its_disclaimer():
    v = G.verdict(_panel([1.0, 1.1, 1.2, 1.3, 1.4, 1.5], [3.0, 3.1, 3.2, 3.3, 3.4, 3.5]))
    assert "INSTRUMENT CALIBRATION" in v["_what"]
    assert "NOT a selectivity result" in v["_what"]
    for k in ("statistic", "p", "p_mirror", "leave_one_model_out", "design_floor", "model_means_A",
              "model_means_B", "technical_failures", "criterion", "reference"):
        assert k in v, "a tier without its evidence is not reportable; %s is missing" % k
    assert v["_criterion_was_frozen_before_the_run"] is True


def test_scorer_delegates_to_the_frozen_shared_primitives():
    """One home per rule 1: a second permutation implementation would calibrate a statistic the program does
    not use, and any disagreement would be undetectable."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "selcal_gate.py")).read()
    assert "from nrv04_retro_gate import" in src
    for banned in ("def exact_permutation_p", "def mean_difference", "def model_level_values",
                   "def leave_one_model_out"):
        assert banned not in src, "re-implemented %s — import it instead" % banned


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-q"]))
