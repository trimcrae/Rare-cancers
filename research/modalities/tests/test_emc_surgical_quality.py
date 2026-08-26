"""Guards on the EMC surgical-margin curation.

The transcription guards matter most: a mistyped count is silent. The strongest one here needs a
second module to agree -- Masunaga's Table 1 margin row and its Cox tables were typed from different
pages, and subtracting the non-operated patients must reconcile them exactly.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_surgical_quality as sq  # noqa: E402
import emc_prognostic_coefficients as pc  # noqa: E402


@pytest.fixture(scope="module")
def doc():
    return sq.build()


def test_the_artifact_reproduces_from_its_generator():
    assert sq.check() == 0


def test_every_margin_column_partitions_its_printed_denominator():
    assert sq._check_structure() == []


def test_the_two_masunaga_strata_sum_to_its_total_column():
    """Table 1 prints three columns; the outer two must reconstruct the first, cell by cell."""
    mas = next(s for s in sq.SERIES if s["source_id"] == "masunaga2025")
    for cell in ("R0", "R1", "R2", "no_surgery"):
        assert (mas["margin_nonmetastatic"][cell] + mas["margin_metastatic"][cell]
                == mas["margin_all_registered"][cell]), cell


def test_table_1_reconciles_with_the_cox_tables_in_the_other_module():
    """⭐ The cross-module check. Two independent transcriptions of overlapping facts."""
    assert sq.cross_check_against_the_cox_tables() == []
    mas = next(s for s in sq.SERIES if s["source_id"] == "masunaga2025")
    non = mas["margin_nonmetastatic"]
    assert non["R0"] == 104
    assert non["R1"] + non["R2"] == 30
    assert non["R0"] + non["R1"] + non["R2"] == 134
    # and the Cox side really does say so, rather than the assertion above being self-referential
    seen = {}
    for m in pc.MODELS:
        if m["source_id"] != "masunaga2025":
            continue
        for r in m["rows"]:
            if r["variable"] == "surgical_margin" and r["n"] is not None:
                seen[r["level"]] = r["n"]
    assert seen == {"R0": 104, "R1_or_R2": 30}


def test_perturbing_either_side_breaks_the_cross_check(monkeypatch):
    """Mock the thing under test and you test the mock -- so perturb a real transcription."""
    mas = next(s for s in sq.SERIES if s["source_id"] == "masunaga2025")
    bumped = dict(mas["margin_nonmetastatic"])
    bumped["R0"] = 105
    monkeypatch.setitem(mas, "margin_nonmetastatic", bumped)
    assert sq.cross_check_against_the_cox_tables() != []


def test_no_rate_is_computed_over_the_chiusole_curative_intent_cohort(doc):
    """Informative missingness: the field exists for 40 of 49, and 49 must never be a denominator."""
    chi_rates = doc["chiusole2020_rates"]
    for k, v in chi_rates.items():
        if isinstance(v, dict) and "denominator" in v:
            assert v["denominator"] != 49, k
    assert "⛔_no_rate_over_the_curative_intent_cohort" in chi_rates


def test_every_rate_names_its_own_denominator(doc):
    """The module's central discipline: no bare 'positive-margin rate' anywhere."""
    found = 0
    for block in ("masunaga2025_rates", "chiusole2020_rates"):
        for k, v in doc[block].items():
            if isinstance(v, dict) and "proportion" in v:
                assert "denominator" in v and v["denominator"] > 0, k
                lo, hi = v["wilson95"]
                assert lo <= v["proportion"] <= hi, k
                found += 1
    assert found >= 6


def test_the_denominators_really_do_disagree(doc):
    """The headline claims the denominator moves the answer by more than any interval's width.

    If that stopped being true the headline would be wrong, so it is asserted rather than described.
    """
    r = doc["masunaga2025_rates"]
    loc = r["positive_margin_among_operated_localized_at_diagnosis"]
    met = r["positive_margin_among_operated_metastatic_at_diagnosis"]
    spread = met["proportion"] - loc["proportion"]
    assert spread > 0.15, "the metastatic/localized gap has closed; the headline needs rewriting"
    widest = max(v["wilson95"][1] - v["wilson95"][0]
                 for v in r.values() if isinstance(v, dict) and "wilson95" in v)
    assert spread < widest, (
        "the gap now exceeds every interval width -- it would be a stronger claim than the "
        "headline makes, which is also a reason to rewrite it")


def test_R2_gets_no_rate_because_the_paper_prints_NA(doc):
    chi = next(s for s in sq.SERIES if s["source_id"] == "chiusole2020")
    r2 = chi["outcome_by_margin"]["R2"]
    assert r2["local_recurrence"] is None and r2["metastases"] is None
    # No COMPUTED rate may carry R2. A key that merely records the refusal must not satisfy this
    # test either way, so only the rate dicts are inspected.
    rate_keys = [k for k, v in doc["chiusole2020_rates"].items()
                 if isinstance(v, dict) and "proportion" in v]
    assert rate_keys, "no rates at all -- the test would pass vacuously"
    assert not any("R2" in k for k in rate_keys)


def test_the_unplanned_excision_proxies_never_become_the_thing(doc):
    block = doc["unplanned_excision"]
    assert block["recorded_in_any_reachable_series"] is False
    assert block["candidate_proxies"]["is_the_thing"] is False
    assert "⛔_why_not" in block["candidate_proxies"]
    # and no rate is derived from them anywhere
    blob = json.dumps(doc, ensure_ascii=False)
    assert "unplanned_excision_rate" not in blob


def test_the_absent_treatment_setting_is_recorded_as_a_reading(doc):
    """An absent reading is not a reading of absence -- but here it IS a reading, and says why."""
    ts = doc["treatment_setting"]
    assert ts["recorded_in_any_reachable_series"] is False
    assert "⛔_this_is_a_reading_not_a_gap" in ts
    assert ts["what_would_answer_it"]
    for s in sq.SERIES:
        assert s["treatment_setting_printed"] is None
        assert s["⛔_setting_absent"]


def test_nothing_is_pooled_across_the_two_series(doc):
    """Each rate belongs to exactly one series; no combined denominator may appear."""
    mas_denoms = {v["denominator"] for v in doc["masunaga2025_rates"].values()
                  if isinstance(v, dict) and "denominator" in v}
    chi_denoms = {v["denominator"] for v in doc["chiusole2020_rates"].values()
                  if isinstance(v, dict) and "denominator" in v}
    combined = 156 + 40
    assert combined not in mas_denoms | chi_denoms
    assert "⛔_nothing_is_pooled" in doc


def test_the_wilson_helper_is_the_repositorys_one_wilson():
    """One fact, one home: a second Wilson implementation here would be a second home for it."""
    import emc_locoregional_eligibility as loco
    assert sq.wilson is loco.wilson


def test_the_route_answer_quotes_rates_this_module_actually_computes(doc):
    """The headline prints percentages; they must be the ones derived, not remembered."""
    answer = doc["⭐_the_route_question_this_answers"]["answer"]
    r = doc["masunaga2025_rates"]
    for key, pct in (("positive_margin_among_all_operated", "25.0 %"),
                     ("positive_margin_among_operated_localized_at_diagnosis", "22.4 %"),
                     ("positive_margin_among_operated_metastatic_at_diagnosis", "40.9 %")):
        assert f"{r[key]['proportion'] * 100:.1f} %" == pct
        assert pct in answer
    c = doc["chiusole2020_rates"]["positive_margin_among_those_with_the_field_recorded"]
    assert f"{c['proportion'] * 100:.1f} %" == "35.0 %"
    assert "35.0 %" in answer
