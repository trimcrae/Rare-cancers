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


@pytest.mark.parametrize("title", ["Placebo + Sandostatin LAR", "Placebo+Sandostatin LAR",
                                   "Placebo  +  Everolimus", "BSC + Regorafenib"])
def test_a_combination_title_is_backboned_on_the_title_alone(title):
    """The `+` in an arm title must fire whether or not it is spaced.

    THIS TEST CANNOT BE OBSERVED IN AN ARTIFACT, which is why it is here. The `+` alternative was
    written inside the pattern's leading `\\b`, which scopes over the whole alternation; a word
    boundary before `+` needs a word character to its LEFT, so `Placebo+Drug` matched and
    `Placebo + Drug` did not. Over the 552 corpus arms the correction changes the backbone call for
    93 arms, and the two carrying a control token were ALREADY caught by the registry signal -- so
    `placebo-arm-calibration.json` is byte-identical before and after, and a revert would be silent.

    The two signals are meant to agree. This asserts the title half on its own, with `detail` empty
    so the registry half cannot supply the answer.
    """
    assert P.classify(_arm("NCT_X", title), {}) == "control_plus_active_backbone"


def test_a_control_token_with_no_combination_is_not_backboned_by_the_plus_rule():
    """The counterpart. Broadening the pattern must not make every control arm backboned, or the
    classifier would be conservative to the point of measuring nothing."""
    assert P.classify(_arm("NCT_Y", "Placebo"), _detail("NCT_Y", "Placebo", ["Drug: Placebo"])) == \
        "placebo_or_bsc_alone"


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


# ------------------------------------------------- the census denominator decomposition

def _census():
    import json
    with open(os.path.join(MANUSCRIPTS, "endpoint-corpus.json")) as fh:
        doc = json.load(fh)
    return doc["C3_dispositions"], doc["C3b_census_denominator_decomposed"]


def test_the_two_query_families_partition_the_screened_records():
    """The decomposition must ACCOUNT FOR the pooled denominator, not sit beside it.

    If the two families do not sum to `studies_screened`, then either a payload is being read into
    neither family or the pooled figure includes something the paper does not describe. Both are
    reasons a reader could not reconcile section 5's table with its own totals.
    """
    disp, dec = _census()
    bor = dec["best_overall_response_family"]
    pla = dec["placebo_arm_family"]
    assert bor["screened"] + pla["screened"] == disp["studies_screened"]
    assert (bor["no_four_cell_block"] + pla["no_four_cell_block"]
            == disp["study_posted_results_but_no_four_cell_block"])


def test_the_narrow_denominator_is_the_stricter_test_and_the_paper_leads_with_it():
    """The point of computing the split is that the strict figure is LOWER.

    If the best-overall-response family ever became the higher share, leading the abstract with it
    would be quoting the more flattering number, and this test is what would stop that going out.
    """
    _, dec = _census()
    assert (dec["best_overall_response_family"]["share_not_re_readable_pct"]
            <= dec["placebo_arm_family"]["share_not_re_readable_pct"])
    with open(os.path.join(MANUSCRIPTS, "response-endpoint-indolent-tumours.md"),
              encoding="utf-8") as fh:
        abstract = fh.read().split("## Abstract", 1)[1].split("## 1. Background", 1)[0]
    assert str(dec["best_overall_response_family"]["share_not_re_readable_pct"]) in abstract, (
        "the abstract must quote the strict denominator's share, not only the pooled one")


def test_records_exceed_distinct_trials_by_exactly_the_overlap():
    """A trial matching both frozen queries appears in both payloads.

    `studies_screened` counts RECORDS. Section 5.1 reports a per-trial share as well, and that is
    only meaningful if the two counts differ by the measured overlap.
    """
    disp, dec = _census()
    r = dec["records_versus_distinct_trials"]
    assert r["records_screened"] == disp["studies_screened"]
    assert r["distinct_ncts_screened"] == r["records_screened"] - r["distinct_ncts_in_both_families"]
    assert r["distinct_ncts_with_a_four_cell_block"] > 0
    expect = round(100.0 * (r["distinct_ncts_screened"] - r["distinct_ncts_with_a_four_cell_block"])
                   / r["distinct_ncts_screened"], 1)
    assert r["share_not_re_readable_pct_on_distinct_trials"] == expect


def test_the_distinct_trial_count_equals_the_corpus_trial_count():
    """The trials WITH a four-cell block are exactly the corpus's distinct trials.

    Two independent counts of the same set, from different loops. If they diverge, one of them is
    counting something else and the census no longer shares the corpus's denominator, which is the
    property POLICY-evidence 2.6(h) requires.
    """
    import json
    with open(os.path.join(MANUSCRIPTS, "endpoint-corpus.json")) as fh:
        doc = json.load(fh)
    assert (doc["C3b_census_denominator_decomposed"]["records_versus_distinct_trials"]
            ["distinct_ncts_with_a_four_cell_block"] == doc["C6_counts"]["distinct_trials"])


# ------------------------------------------------- the stratification is exhaustive

def _sens():
    import json
    with open(os.path.join(MANUSCRIPTS, "orr-dcr-reread.json")) as fh:
        return json.load(fh)


def test_every_phase_present_in_the_corpus_has_a_stratum():
    """Section 4.2 rests on being exhaustive, so a phase in the corpus and not in the table is a bug.

    ⛔ THIS IS A REGRESSION. The block reported phase 2 and phase 3 and omitted PHASE1 entirely --
    370 arms, more than either reported stratum, and the ONLY stratum that moves the gap DOWN. It
    also called itself pre-stated. Reporting the strata that raise a number and not the one that
    lowers it is the shape selective reporting takes, whether or not anyone intended it.
    """
    doc = _sens()
    sens = doc["R4_sensitivities"]
    phases = set()
    for r in doc["R2_per_arm_rows"]:
        phases.update(r["phases"] or [])
    reported = " ".join(v.get("_label", "") for v in sens.values() if isinstance(v, dict)).lower()
    for ph in phases:
        if ph in ("EARLY_PHASE1", "PHASE4"):
            continue  # 2 and 1 arms respectively; below any stratum worth a median
        n = ph.replace("PHASE", "")
        assert f"phase {n}" in reported, (
            f"{ph} is in the corpus but has no stratum in R4_sensitivities")


def test_the_any_and_only_phase_strata_are_actually_different_filters():
    """`"PHASE2" in phases` is not `phases == ["PHASE2"]`, and the difference was mislabelled.

    The published row called "phase 2 only" was really phase 2 ANY: 355 arms including the 237
    registered as PHASE1|PHASE2. Phase-2-only is 114. Both are legitimate; neither may carry the
    other's name.
    """
    sens = _sens()["R4_sensitivities"]
    for n in ("1", "2", "3"):
        any_, only = sens[f"phase_{n}_any"], sens[f"phase_{n}_only"]
        assert only["arms"] < any_["arms"], f"phase {n}: 'only' must be a strict subset of 'any'"
        assert "alone or combined" in any_["_label"]
        assert any_["_label"] != only["_label"]


def test_the_only_phase_strata_partition_the_phased_arms():
    """The disjoint rows plus the unphased ones must account for every arm exactly once.

    Otherwise "the 'only' rows are the disjoint partition" in section 4.2 is an assertion about a
    table rather than a property of it.
    """
    doc = _sens()
    sens = doc["R4_sensitivities"]
    rows = doc["R2_per_arm_rows"]
    disjoint = sum(sens[k]["arms"] for k in
                   ("phase_1_only", "phase_2_only", "phase_3_only", "no_phase_recorded"))
    multi = len([r for r in rows if len(r["phases"] or []) > 1])
    other = len([r for r in rows if (r["phases"] or []) in (["EARLY_PHASE1"], ["PHASE4"])])
    assert disjoint + multi + other == len(rows), (
        f"{disjoint} disjoint + {multi} multi-phase + {other} other != {len(rows)} arms")


def test_no_committed_file_claims_the_strata_were_pre_specified():
    """The corpus was frozen before retrieval. The strata were not, and said they were.

    POLICY-evidence 2.6(g) pre-specifies queries, window, screening and extraction -- nothing about
    stratification -- and the frozen protocol names no stratum. A false pre-specification claim is
    the kind a reader cannot check and must therefore take on trust, which is why it has to go.
    """
    import json
    sens = _sens()["R4_sensitivities"]
    assert any("NOT_pre_specified" in k for k in sens), (
        "R4 must state that its strata were not pre-specified")
    with open(os.path.join(MANUSCRIPTS, "lit-targets-cross-disease-endpoints.json")) as fh:
        protocol = fh.read().lower()
    for word in ("stratum", "strata", "stratif"):
        assert word not in protocol, (
            f"the frozen protocol now mentions {word!r}; if strata really were pre-specified, "
            f"update R4's disclaimer to say so rather than leaving it overstating the weakness")


# ------------------------------------------------- figure 3's binomial expectation

def test_the_figure_and_the_artifact_compute_the_same_expectation():
    """Figure 3 draws an expectation; the artifact publishes one. They must be the same number.

    They are computed by separate code paths over the same rows -- the figure so it can draw, the
    artifact so the value is auditable as JSON rather than only as pixels. Nothing but this test
    stops one being corrected and the other left behind, and the figure is where the argument is
    made.
    """
    import json
    import endpoint_result_figures as F
    with open(os.path.join(MANUSCRIPTS, "orr-dcr-reread.json")) as fh:
        rr = json.load(fh)
    rows = rr["R2_per_arm_rows"]
    bands = rr["R8_zero_response_readouts"]["disjoint_bins_observed_against_binomial"]["bands"]

    orrs = sorted(r["objective_response"]["pct"] for r in rows)
    p = round(orrs[len(orrs) // 2], 1) / 100.0
    for band, (lo, hi) in zip(bands, R.ZERO_RESPONSE_BINS):
        sub = [r for r in rows if lo <= r["n"] <= (hi if hi is not None else 10 ** 9)]
        assert band["arms"] == len(sub), band["band"]
        drawn = sum((1 - p) ** r["n"] for r in sub) / len(sub)
        assert abs(band["expected_zero_response_pct"] - 100 * drawn) < 0.05, band["band"]


def test_the_expectation_is_not_taken_at_a_guessed_midpoint():
    """Regression on the defect this replaced.

    The top band is open-ended, so it has no midpoint; one was invented (n = 60) against a real
    median of 128.5. That drew the expectation at 0.8% where the exact value is 0.5% and the
    observation is 0.0%, making the binomial look like a worse fit than it is -- in the figure whose
    whole claim is that the two agree. If a midpoint list ever comes back, this fails.
    """
    import inspect
    import endpoint_result_figures as F
    # Comments are stripped first. The first version of this test searched the raw source and
    # matched the word `mids` inside the comment EXPLAINING why midpoints were removed, so it failed
    # on the fixed code. A guard that reads prose is testing the prose.
    src = "\n".join(ln for ln in inspect.getsource(F.figure_zero_response).split("\n")
                    if not ln.lstrip().startswith("#"))
    assert "mids" not in src, (
        "figure 3 is back to a guessed n per band; the top band has no midpoint to guess")
    assert '(1 - p) ** r["n"]' in src, (
        "figure 3 no longer averages each arm's own zero-response probability")


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
