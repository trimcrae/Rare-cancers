"""Guards on the EMC recurrence-timing curation.

The transcription guards check each printed percentage against its own count, which is what catches
a mistyped numerator. The interpretation guards protect the two statements that are easiest to
strengthen by accident: that the cross-cohort divergence is CONSISTENT with censoring rather than
established by it, and that an IQR fitting inside the follow-up window is not reassurance.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_recurrence_timing as rt  # noqa: E402


@pytest.fixture(scope="module")
def doc():
    return rt.build()


def test_the_artifact_reproduces_from_its_generator():
    assert rt.check() == 0


def test_every_printed_percentage_reproduces_from_its_own_count():
    assert rt._check_structure() == []
    checked = 0
    for c in rt.COHORTS:
        for e in c["events"]:
            assert abs(100.0 * e["count"] / c["n"] - e["printed_percent"]) <= 0.1, e["event"]
            checked += 1
    assert checked == 5


def test_masunagas_distant_metastasis_count_reconciles_from_a_second_paragraph():
    """38 unexposed + 1 exposed = 39, printed elsewhere in the same paper."""
    mas = next(c for c in rt.COHORTS if c["source_id"] == "masunaga2025")
    dm = next(e for e in mas["events"] if e["event"] == "distant_metastasis")
    assert dm["count"] == 38 + 1
    assert "38 + 1 = 39" in dm["⭐_independently_reconcilable"]


def test_every_event_names_its_anchor():
    """Masunaga measures local recurrence from surgery and metastasis from diagnosis, in one
    sentence. An event that loses its anchor can be silently compared to the wrong clock."""
    for c in rt.COHORTS:
        for e in c["events"]:
            assert e.get("anchor"), f"{c['source_id']}/{e['event']}"


def test_the_cross_cohort_comparison_refuses_to_run_across_anchors(doc, monkeypatch):
    assert doc["cross_cohort_time_to_distant_metastasis"]["same_anchor"] is True
    assert rt._check_no_cross_anchor_comparison() == []
    # and prove the guard bites: repoint one anchor and it must complain
    chi = next(c for c in rt.COHORTS if c["source_id"] == "chiusole2020")
    dm = next(e for e in chi["events"] if e["event"] == "distant_metastasis")
    monkeypatch.setitem(dm, "anchor", "surgery")
    assert rt._check_no_cross_anchor_comparison() != []


def test_every_median_lies_inside_its_own_iqr():
    for c in rt.COHORTS:
        for e in c["events"]:
            if e.get("iqr_months"):
                lo, hi = e["iqr_months"]
                assert lo <= e["median_months"] <= hi, e["event"]


def test_the_headline_is_the_within_cohort_observation(doc):
    """The finding must be the one no second cohort is needed for.

    If a later edit promoted the cross-cohort divergence to the headline, this fails -- that
    comparison cannot separate follow-up length from era, and saying so is the whole point.
    """
    f = doc["⭐_the_finding"]
    assert "one paper, one set of patients and one clock" in f["why_it_is_the_one_worth_carrying"]
    assert "⛔_what_it_does_not_say" in f
    assert "lead-time" in f["⛔_what_it_does_not_say"].lower()


def test_the_headline_numbers_are_the_ones_actually_derived(doc):
    """The statement prints months; they must come from the computation, not from memory."""
    lr = next(b for b in doc["events_beyond_the_observation_window"]
              if b["event"] == "local_recurrence")
    stmt = doc["⭐_the_finding"]["statement"]
    assert f"{lr['upper_quartile_months']} months" in stmt
    assert f"{lr['months_beyond']} months BEYOND" in stmt
    assert f"{lr['cohort_median_followup_months']} months" in stmt
    assert lr["upper_quartile_exceeds_median_followup"] is True


def test_the_cross_cohort_divergence_is_never_asserted_as_established(doc):
    x = doc["cross_cohort_time_to_distant_metastasis"]
    note = x["⚠_consistent_with_censoring_and_not_established_by_it"]
    assert "cannot discriminate follow-up length from era" in note
    assert "never as demonstrated" in note
    # the ratio is real and derived
    assert x["ratio_of_medians"] == round(
        x["chiusole2020"]["median_months"] / x["masunaga2025"]["median_months"], 2)
    assert x["ratio_of_medians"] > 4


def test_an_iqr_inside_the_window_is_explicitly_not_reassurance(doc):
    """The row that would otherwise be misread.

    distant_metastasis is the one event whose upper quartile sits inside the follow-up window, and
    a reader could take that as 'no censoring problem here'. Truncation is what produces a tidy
    IQR, so the inference only runs one way, and the artifact has to say so.
    """
    inside = [b for b in doc["events_beyond_the_observation_window"]
              if not b["upper_quartile_exceeds_median_followup"]]
    assert len(inside) == 1 and inside[0]["event"] == "distant_metastasis"
    note = doc["⛔_an_iqr_that_fits_inside_the_window_is_not_reassurance"]
    assert "not evidence against it" in note
    assert "only runs one way" in note


def test_no_surveillance_interval_is_recommended_anywhere(doc):
    """The refusal that keeps this file from becoming clinical advice."""
    assert "⛔_no_hazard_and_therefore_no_schedule" in doc
    assert "cannot be differentiated into a hazard" in doc["⛔_no_hazard_and_therefore_no_schedule"]
    blob = json.dumps(doc, ensure_ascii=False).lower()
    for forbidden in ("recommended interval", "every 3 months", "every 6 months",
                      "surveillance schedule of", "should be scanned"):
        assert forbidden not in blob, forbidden
    assert "no surveillance interval, schedule or duration is recommended" in blob


def test_the_derived_chiusole_count_is_flagged_as_derived():
    """40.8 % of 49 -> 20 is a back-conversion, and POLICY-evidence forbids doing it for pooling."""
    chi = next(c for c in rt.COHORTS if c["source_id"] == "chiusole2020")
    dm = next(e for e in chi["events"] if e["event"] == "distant_metastasis")
    assert dm["count"] == 20
    assert round(0.408 * chi["n"]) == 20
    assert "⚠_count_is_derived_not_printed" in dm


def test_nothing_is_pooled(doc):
    assert "⛔_nothing_is_pooled" in doc
    blob = json.dumps(doc, ensure_ascii=False)
    assert "pooled_median" not in blob and "combined_median" not in blob
