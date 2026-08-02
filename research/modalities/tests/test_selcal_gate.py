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


# =============================================================================================================
# the tier travels with its CONSEQUENCE
# =============================================================================================================
def test_every_tier_says_what_it_unblocks():
    """★★ A tier without its consequence sends the reader to another file for the one question a verdict
    provokes: what happens now? The branch was written in `selectivity-resolution-options.md` §3/§4 BEFORE
    this panel ran — which is what makes it quotable — but the artifact anyone actually opens is
    selcal-verdict.json."""
    import selcal_gate as G
    import selcal_panel as P
    for tier in (P.TIER_PASS, P.TIER_NULL, P.TIER_WRONG_SIGN, P.TIER_INDETERMINATE):
        row = G.next_step_for(tier)
        assert row.get("unblocks"), tier
        assert row["_written_before_the_panel_ran"] is True
        assert "selectivity-resolution-options.md" in row["_source"]


def test_only_a_PASS_unblocks_anything():
    """⛔ The load-bearing asymmetry. NULL, WRONG_SIGN and INDETERMINATE each buy nothing, and a reader must
    not be able to take 'the control ran' as licence to spend."""
    import selcal_gate as G
    import selcal_panel as P
    assert "step 3" in G.next_step_for(P.TIER_PASS)["unblocks"]
    for tier in (P.TIER_NULL, P.TIER_WRONG_SIGN, P.TIER_INDETERMINATE):
        assert G.next_step_for(tier)["unblocks"].startswith("NOTHING"), tier


def test_a_pass_names_the_blocking_artifact_and_is_not_a_4d_extension():
    """Step 3 needs a NEW preregistration; §4d may not be invoked on a wrong-sign result, and any re-use of
    the 16 landed NR-V04 legs must be declared inside it IN ADVANCE."""
    import selcal_gate as G
    import selcal_panel as P
    blk = G.next_step_for(P.TIER_PASS)["blocking_artifact"]
    assert "NEW PREREGISTRATION" in blk.upper()
    assert "4d" in blk and "16 landed" in blk


def test_a_pass_still_carries_what_it_forbids():
    """A PASS licenses EXACTLY ONE SENTENCE. The consequence field must not read as a general green light."""
    import selcal_gate as G
    import selcal_panel as P
    row = G.next_step_for(P.TIER_PASS)
    assert "_what_a_pass_licenses" in row["still_forbidden"]
    assert "re-scores no landed NR-V04 leg" in row["still_forbidden"]


def test_no_cost_or_leg_count_is_typed_into_the_verdict():
    """⛔ CLAUDE.md §1. Step 3's shape and price have ONE home — `recommended_sequence`, which DERIVES them.
    A number copied into a verdict artifact goes stale silently and is then quoted."""
    import re

    import selcal_gate as G
    blob = repr(G.NEXT_STEP_BY_TIER)
    assert "recommended_sequence" in blob, "it must point at the derivation"
    assert not re.search(r"\$\s?\d", blob), "no dollar figure may be typed here"
    assert not re.search(r"\b36\b|\b24\b", blob), "no leg count may be typed here"


def test_the_branch_is_attached_on_EVERY_exit_of_verdict():
    """A field present on some return paths and absent on others is worse than absent everywhere: the reader
    cannot tell which they are holding. The INDETERMINATE admissibility exits are the easy ones to miss."""
    import selcal_gate as G
    v = G.verdict([])                      # no legs at all -> an early admissibility exit
    assert v["tier"] == "INDETERMINATE"
    assert v["next_step"]["unblocks"].startswith("NOTHING")
    src = open(G.__file__).read()
    body = src[src.index("def verdict(legs)"):]
    body = body[:body.index("\ndef ", 10)]
    assert "return out" not in body, "every exit must go through _with_next_step"


def test_render_shows_the_consequence_not_just_the_label():
    import selcal_gate as G
    assert "NEXT:" in G.render(G.verdict([]))


# =============================================================================================================
# ⛔ SUPPRESSION MUST WITHHOLD THE LABEL *AND* EVERYTHING THAT DISCLOSES IT
# =============================================================================================================
def test_suppression_withholds_the_consequence_not_just_the_tier():
    """★★ MEASURED ON THE LIVE LANE AT 21 OF 24 LEGS, 2026-08-02 — and introduced by the very field it now
    governs. Adding `next_step` meant an incomplete panel published `tier: None` (correctly suppressed) beside
    `next_step.unblocks = "NOTHING. Step 3 is NOT bought…"` — the NULL tier's consequence, stated in prose.

    Suppression exists to withhold the LABEL on a partial panel. A field that re-publishes the label's MEANING
    defeats it exactly, and is worse than a leaked label because it reads as a settled decision rather than a
    peek. This is the no-interim-analysis rule, and it is not satisfied by hiding one field of two.
    """
    import selcal_gate as G
    import selcal_panel as P
    v = G.verdict([])
    assert v["next_step"]["unblocks"].startswith("NOTHING")     # …before suppression
    G.suppress_for_incomplete_panel(v, "incomplete")
    assert v["tier"] is None
    assert v["tier_suppressed"] == P.TIER_INDETERMINATE
    txt = repr(v["next_step"])
    assert "WITHHELD" in txt
    for leak in ("step 3", "Step 3", "NOTHING. Step 3", "money spent to reproduce"):
        assert leak not in txt, f"the suppressed tier's consequence leaked: {leak!r}"


def test_a_withheld_consequence_does_not_read_as_unblocks_nothing():
    """⚠ An ABSENT field would itself disclose — "no consequence" is what NULL/WRONG_SIGN/INDETERMINATE all
    say, so silence would narrow the tier to those three. It must say the question has not been ASKED."""
    import selcal_gate as G
    v = G.suppress_for_incomplete_panel(G.verdict([]), "incomplete")
    assert "not 'nothing is unblocked'" in v["next_step"]["unblocks"]
    assert v.get("next_step_suppressed") is True


def test_suppression_is_atomic_and_has_one_home():
    """The label and its disclosure must move together. A call site that pops `tier` by hand would drift the
    moment another disclosing field is added — which is precisely how this defect arrived."""
    import inspect

    import selcal_vast_launch as L
    src = inspect.getsource(L)
    body = src[src.index("def mode_collect("):]
    body = body[:body.index("\ndef ", 10)]
    assert "suppress_for_incomplete_panel" in body
    assert 'v.pop("tier"' not in body, "suppression must go through the gate, not be re-implemented here"
