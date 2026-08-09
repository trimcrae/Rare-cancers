"""Unit tests for the load-bearing logic of the cross-disease endpoint producers.

WHY THIS FILE EXISTS. Six producers shipped with no tests on their logic. One of them,
`placebo_arm_calibration.classify`, decides which trial arms may carry a natural-history reading,
and it was wrong twice in opposite directions before anyone tested it. If it is wrong a third time
the manuscript publishes a false natural-history response rate, which is the worst error available
in this analysis.

Every test below is a pure function call. No producer is monkeypatched and no artifact is mocked,
because the whole point is to exercise the real decision.
"""
from __future__ import annotations

import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, MANUSCRIPTS)

import endpoint_corpus as C  # noqa: E402
import endpoint_regime_map as M  # noqa: E402
import orr_dcr_reread as R  # noqa: E402
import placebo_arm_calibration as P  # noqa: E402


# ---------------------------------------------------------------- classify()

def _arm(nct, title):
    return {"nct_id": nct, "arm_title": title, "arm_group_type": "UNRESOLVED"}


def _detail(nct, label, interventions):
    return {nct: {"arm_groups": [{"type": "PLACEBO_COMPARATOR", "label": label,
                                  "interventions": interventions}]}}


def test_regression_an_active_agent_absent_from_every_name_list_is_not_untreated():
    """The first historical failure, kept as a named regression.

    `Placebo + Sandostatin LAR` was passed as untreated. Octreotide is an active antitumour agent
    in neuroendocrine tumours -- the class PROMID and CLARINET were built on -- and it appears in no
    drug-name list anyone would think to write. The registry's interventions are what catch it.
    """
    arm = _arm("NCT_A", "Placebo + Sandostatin LAR")
    detail = _detail("NCT_A", "Placebo + Sandostatin LAR",
                     ["Drug: Placebo", "Drug: Sandostatin LAR"])
    assert P.classify(arm, detail) == "control_plus_active_backbone"


def test_regression_a_sibling_arm_group_must_not_certify_an_arm_as_untreated():
    """The second historical failure, which the first fix introduced.

    Outcome-measure group titles do not match protocol arm labels, so an intervention lookup can
    match the WRONG group. `Part 2: Placebo + Chemotherapy` was passed as untreated on the strength
    of a sibling arm registered as `Drug: Placebo`. A structural signal that can override a correct
    one is more dangerous than a name list, because it looks authoritative.
    """
    arm = _arm("NCT_B", "Part 2: Placebo + Chemotherapy")
    detail = {"NCT_B": {"arm_groups": [
        {"type": "PLACEBO_COMPARATOR", "label": "Placebo", "interventions": ["Drug: Placebo"]},
        {"type": "EXPERIMENTAL", "label": "Chemotherapy", "interventions": ["Other: Chemotherapy"]},
    ]}}
    assert P.classify(arm, detail) == "control_plus_active_backbone"


def test_an_unmatchable_label_is_unclassified_and_never_untreated():
    """The failure direction that matters. A false backboned call costs one arm of calibration; a
    false untreated call puts a treated arm inside a natural-history estimate."""
    arm = _arm("NCT_C", "Placebo/Placebo Arm (Arm 1)")
    detail = {"NCT_C": {"arm_groups": [
        {"type": "EXPERIMENTAL", "label": "Cohort A", "interventions": ["Drug: Pemetrexed"]}]}}
    verdict = P.classify(arm, detail)
    assert verdict == "control_arm_unclassified_no_registry_match"
    assert verdict not in ("placebo_or_bsc_alone", "observation_no_active_agent")


def test_a_genuine_no_intervention_arm_is_observation():
    arm = _arm("NCT_D", "Observation")
    detail = {"NCT_D": {"arm_groups": [
        {"type": "NO_INTERVENTION", "label": "Observation", "interventions": []}]}}
    assert P.classify(arm, detail) == "observation_no_active_agent"


def test_a_placebo_only_arm_is_placebo_alone():
    arm = _arm("NCT_E", "Placebo")
    detail = _detail("NCT_E", "Placebo", ["Drug: Placebo"])
    assert P.classify(arm, detail) == "placebo_or_bsc_alone"


def test_an_arm_with_no_control_token_is_not_a_control_arm():
    assert P.classify(_arm("NCT_F", "Docetaxel 75 mg/m2"), {}) == "not_a_control_arm"


@pytest.mark.parametrize("name", ["Drug: Placebo", "placebo", "Other: Best Supportive Care",
                                  "BSC", "Drug: Matching Placebo"])
def test_inert_interventions_are_recognised(name):
    assert P.INERT_INTERVENTION.match(name), name


@pytest.mark.parametrize("name", ["Drug: Sandostatin LAR", "Other: Chemotherapy",
                                  "Drug: Pembrolizumab", "Biological: rituximab"])
def test_active_interventions_are_not_treated_as_inert(name):
    assert not P.INERT_INTERVENTION.match(name), name


# ---------------------------------------------------------------- arm-type matching

def test_arm_type_resolves_exactly_normalised_and_by_containment():
    types = {"Placebo Arm": "PLACEBO_COMPARATOR", "Drug A": "EXPERIMENTAL"}
    assert C._match_arm_type("Placebo Arm", types) == "PLACEBO_COMPARATOR"
    assert C._match_arm_type("placebo  arm!", types) == "PLACEBO_COMPARATOR"
    assert C._match_arm_type("Placebo Arm (Arm 1)", types) == "PLACEBO_COMPARATOR"


def test_an_unmatchable_arm_type_is_UNRESOLVED_not_None():
    """UNRESOLVED and None were once the same value, which made 'could not determine' read exactly
    like 'not a control arm' for 415 of 552 arms."""
    assert C._match_arm_type("Totally Unrelated", {"Placebo": "PLACEBO_COMPARATOR"}) == "UNRESOLVED"
    assert C._match_arm_type("anything", {}) == "UNRESOLVED"


def test_a_registry_arm_with_no_type_is_distinguishable_from_a_failed_match():
    assert C._match_arm_type("Arm X", {"Arm X": None}) == "NOT_STATED_IN_REGISTRY"


# ---------------------------------------------------------------- the gap identity

def test_the_gap_identity_holds_on_a_constructed_arm():
    corpus = {"C2_arms": [{
        "nct_id": "NCT_G", "arm_title": "A", "arm_group_type": "EXPERIMENTAL",
        "conditions": ["X"], "phases": ["PHASE2"], "control_arm_candidate": False,
        "cells": {"CR": 1, "PR": 2, "SD": 5, "PD": 2}, "evaluable_n": 10,
        "retrieved_file": "test"}]}
    row = R.rows_from_corpus(corpus)[0]
    assert row["objective_response"]["events"] == 3
    assert row["disease_control"]["events"] == 8
    assert row["gap_pp"] == 50.0
    assert row["disease_control"]["events"] - row["objective_response"]["events"] == \
        row["cells"]["SD"]


def test_cells_that_do_not_sum_to_the_denominator_fail_the_build():
    """The assertion exists in production code. This proves it fires rather than being dead."""
    corpus = {"C2_arms": [{
        "nct_id": "NCT_H", "arm_title": "A", "arm_group_type": "EXPERIMENTAL",
        "conditions": ["X"], "phases": [], "control_arm_candidate": False,
        "cells": {"CR": 1, "PR": 2, "SD": 5, "PD": 2}, "evaluable_n": 99,
        "retrieved_file": "test"}]}
    with pytest.raises(AssertionError):
        R.rows_from_corpus(corpus)


# ---------------------------------------------------------------- contours

def test_zero_event_contour_matches_the_closed_form():
    for p in (0.05, 0.10, 0.128, 0.25):
        expected = math.ceil(math.log(0.10) / math.log(1 - p))
        assert M.n_for_90pct_chance_of_one_event(p) == expected
    # and it is the n at which P(0 events) first drops to 0.10 or below
    n = M.n_for_90pct_chance_of_one_event(0.128)
    assert M.p_zero_events(0.128, n) <= 0.10
    assert M.p_zero_events(0.128, n - 1) > 0.10


def test_a_rate_at_or_below_the_null_has_no_design_rather_than_a_number():
    """The distinction that produced a wrong headline. A rate at or below the null returns None --
    the comparison is undefined -- and a rate just above it returns NO_DESIGN_WITHIN_BOUND. Neither
    may be silently counted as 'not below the contour'."""
    assert M.required_n_against_null(M.DESIGN_NULL) is None
    assert M.required_n_against_null(0.0) is None
    assert M.required_n_against_null(0.051) == M.NO_DESIGN
    n = M.required_n_against_null(0.30)
    assert isinstance(n, int) and 0 < n <= M.DESIGN_N_MAX


def test_the_share_below_the_design_contour_excludes_undefined_conditions():
    """Regression on the wrong headline: 16 of 44 conditions have an undefined comparison, and
    counting them in the denominator understated the finding as 31.8% instead of 50.0%."""
    import json
    with open(os.path.join(MANUSCRIPTS, "endpoint-regime-map.json")) as fh:
        g = json.load(fh)["G4_what_the_map_reads"]
    defined = g["conditions_where_the_design_comparison_is_defined"]
    below = g["conditions_whose_median_trial_is_below_the_design_contour"]
    assert g["share_below_the_design_contour_pct"] == round(100 * below / defined, 1)
    assert defined < g["conditions_placed"], "undefined conditions must be excluded, not hidden"


# ---------------------------------------------------------------- wilson agreement

def test_the_two_wilson_implementations_agree():
    """The interval is implemented separately in two producers. Nothing checked they match."""
    for ev, n in ((0, 10), (1, 10), (5, 20), (42, 47), (47, 47)):
        a = R.wilson(ev, n)
        b = P.wilson(ev, n)
        assert a == b, (ev, n, a, b)


def test_quantile_matches_linear_interpolation_on_a_known_series():
    vals = [1.0, 2.0, 3.0, 4.0]
    assert R._quantile(vals, 0.25) == 1.8
    assert R._quantile(vals, 0.75) == 3.2
    assert R._quantile(vals, 0.0) == 1.0
    assert R._quantile(vals, 1.0) == 4.0
