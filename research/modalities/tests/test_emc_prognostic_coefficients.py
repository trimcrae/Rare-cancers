"""Guards on the transcribed EMC Cox coefficients.

These are transcription guards first and interpretation guards second. A wrong digit in a hazard
ratio is silent -- it looks exactly like a right one -- so the tests that matter most here are the
ones that check a number against something ELSE the paper printed, and the ones that fail if a
stated refusal is ever removed.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_prognostic_coefficients as pc  # noqa: E402


@pytest.fixture(scope="module")
def doc():
    return pc.build()


def test_the_artifact_reproduces_from_its_generator():
    assert pc.check() == 0


def test_every_categorical_levels_count_sums_to_the_model_n():
    """Masunaga prints a patient count on every level; each variable must partition the 134."""
    assert pc._check_structure() == []
    checked = 0
    for m in pc.MODELS:
        if m["source_id"] != "masunaga2025":
            continue
        by_var: dict[str, list[dict]] = {}
        for r in m["rows"]:
            by_var.setdefault(r["variable"], []).append(r)
        for var, rows in by_var.items():
            if any(r.get("continuous") for r in rows):
                continue
            assert sum(r["n"] for r in rows) == m["n"], f"{m['model_id']}/{var}"
            checked += 1
    assert checked >= 20, "the partition guard stopped seeing most variables"


def test_masunaga_level_counts_agree_across_all_three_of_its_models():
    """The same 134 patients are modelled three times, so a level's n may not move between tables.

    This is the strongest transcription check available: a mistyped count in one table is caught by
    the other two, without needing the paper.
    """
    seen: dict[tuple[str, str], int] = {}
    for m in pc.MODELS:
        if m["source_id"] != "masunaga2025":
            continue
        for r in m["rows"]:
            key = (r["variable"], r["level"])
            if r["n"] is None:
                continue
            if key in seen:
                assert seen[key] == r["n"], f"{key} is {r['n']} in {m['model_id']}, {seen[key]} elsewhere"
            seen[key] = r["n"]
    assert len(seen) >= 15


def test_the_significance_star_and_the_interval_never_disagree():
    for m in pc.MODELS:
        for r in m["rows"]:
            if not pc.estimable(r):
                continue
            lo, hi = r["ci"]
            excludes_one = lo > 1.0 or hi < 1.0
            assert bool(r.get("starred_significant")) == excludes_one, (
                f"{m['model_id']}: {r['variable']}/{r['level']} {r['ci']} "
                f"star={r.get('starred_significant')}")


def test_every_hazard_ratio_lies_inside_its_own_interval():
    for m in pc.MODELS:
        for r in m["rows"]:
            if not pc.estimable(r):
                continue
            lo, hi = r["ci"]
            assert lo <= r["hr"] <= hi, f"{m['model_id']}: {r['variable']}/{r['level']}"


def test_a_zero_hazard_ratio_is_recorded_as_a_non_estimate_and_never_used():
    """HR = 0 is complete separation, not a measurement of zero risk."""
    zeros = [(m["model_id"], r) for m in pc.MODELS for r in m["rows"]
             if r.get("hr") == 0.0]
    assert len(zeros) == 3, "the three printed HR=0 rows are the ones this guard exists for"
    for model_id, r in zeros:
        assert r["non_estimate"] == "complete_separation", model_id
        assert r["ci"] is None, model_id
        assert not pc.estimable(r), model_id
    # and none of them reaches the concordance table
    for c in pc.concordance():
        assert c["masunaga2025"]["hr"] != 0.0
        assert c["chiusole2020"]["hr"] != 0.0


def test_absolute_risk_is_refused_structurally(doc):
    block = doc["⛔_what_is_structurally_impossible_from_print"]
    assert block["absolute_risk_computable"] is False
    assert "baseline" in block["why"].lower()


def test_flipping_the_absolute_risk_refusal_fails_the_check(monkeypatch):
    """The refusal is load-bearing, so prove the guard bites rather than trusting it."""
    real_build = pc.build

    def poisoned():
        d = real_build()
        d["⛔_what_is_structurally_impossible_from_print"]["absolute_risk_computable"] = True
        return d

    monkeypatch.setattr(pc, "build", poisoned)
    assert pc.check() == 1


def test_every_treatment_covariate_carries_its_confound(doc):
    treatment_vars = {r["variable"] for m in pc.MODELS for r in m["rows"] if r.get("treatment")}
    assert treatment_vars, "no treatment covariate is flagged -- the flag has been lost"
    for var in treatment_vars:
        assert var in doc["confounding_by_indication"], var
        assert len(doc["confounding_by_indication"][var]) > 100, var


def test_dropping_a_confound_entry_fails_the_structure_check(monkeypatch):
    trimmed = dict(pc.CONFOUNDING_BY_INDICATION)
    trimmed.pop("neoadjuvant_or_adjuvant_radiotherapy")
    monkeypatch.setattr(pc, "CONFOUNDING_BY_INDICATION", trimmed)
    errs = pc._check_structure()
    assert any("CONFOUNDING_BY_INDICATION" in e for e in errs)


def test_no_hazard_ratio_in_the_artifact_is_a_value_neither_paper_printed(doc):
    """The structural anti-pooling guard.

    A pooled or combined HR would be a NEW number -- some weighted function of the two cohorts'
    estimates -- so it cannot be one of the transcribed values. Scanning the artifact for any `hr`
    field outside the printed set catches a pool no matter what it is named, which a search for the
    word "pooled" cannot do (the module's own refusal text contains that word).
    """
    printed = {r["hr"] for m in pc.MODELS for r in m["rows"] if r.get("hr") is not None}
    assert len(printed) > 20

    found = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "hr" and v is not None:
                    found.append(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(doc)
    assert found, "no hr fields found at all -- the walker is broken, not the artifact"
    unprinted = sorted(set(found) - printed)
    assert unprinted == [], f"derived hazard ratios present: {unprinted}"


def test_that_walker_would_actually_catch_a_pooled_value(doc):
    """Mock the thing under test and you test the mock -- so poison a real artifact instead."""
    poisoned = json.loads(json.dumps(doc))
    poisoned["cross_cohort_direction"][0]["pooled"] = {"hr": 2.71828}
    printed = {r["hr"] for m in pc.MODELS for r in m["rows"] if r.get("hr") is not None}
    found = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "hr" and v is not None:
                    found.append(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(poisoned)
    assert sorted(set(found) - printed) == [2.71828]


def test_each_comparison_reports_two_cohorts_and_no_combination(doc):
    for c in doc["cross_cohort_direction"]:
        assert "⛔_not_pooled" in c
        assert {"masunaga2025", "chiusole2020"} <= set(c)
        assert "pooled_hr" not in c and "combined_hr" not in c


def test_the_site_comparison_declares_its_inverted_contrast():
    """Chiusole measures extremity-vs-central; Masunaga measures trunk-vs-lower-limb.

    If someone ever 'simplifies' this to same_contrast=True, the two cohorts would read as
    contradicting each other when in fact they agree.
    """
    rows = [c for c in pc.concordance() if c["covariate"] == "site_away_from_the_lower_limb"]
    assert rows, "the site comparison vanished"
    for c in rows:
        assert c["same_contrast"] is False
        assert c["directions_agree"] is True
        assert c["masunaga2025"]["direction"] == "harmful"
        assert c["chiusole2020"]["direction"] == "protective"
        assert "INVERSES" in c["note"]


def test_no_comparison_has_both_cohorts_excluding_one(doc):
    """The headline rests on this: consistency, not corroboration."""
    s = doc["cross_cohort_summary"]
    assert s["comparisons_where_both_exclude_1"] == 0
    assert s["comparisons_where_both_intervals_include_1"] == 9
    assert s["comparisons_where_exactly_one_excludes_1"] == 3
    assert s["comparisons"] == 12
    assert (s["comparisons_where_both_intervals_include_1"]
            + s["comparisons_where_exactly_one_excludes_1"]
            + s["comparisons_where_both_exclude_1"]) == s["comparisons"]


def test_the_one_disagreement_is_flagged_as_two_nulls(doc):
    dis = [c for c in doc["cross_cohort_direction"] if not c["directions_agree"]]
    assert len(dis) == 1
    assert dis[0]["covariate"] == "female_vs_male"
    assert dis[0]["both_null"] is True
    assert dis[0]["⛔_direction_between_two_nulls_is_noise"]


def test_the_stepwise_selection_is_recorded_on_every_multivariate_model():
    multis = [m for m in pc.MODELS if m["analysis"] == "multivariate"]
    assert len(multis) == 3
    for m in multis:
        assert m["selection"] == "stepwise", m["model_id"]


def test_the_chiusole_table_vs_text_discrepancy_is_recorded_unresolved():
    chi = next(m for m in pc.MODELS if m["source_id"] == "chiusole2020")
    assert chi["analysis"] == "univariate", "transcribe the table as the table labels itself"
    note = chi["⚠_table_vs_text_unresolved"]
    assert "multivariate" in note and "Univariate" in note


def test_the_log_hr_standard_error_is_only_ever_used_for_overlap():
    """A back-derived SE is one function call away from being an inverse-variance weight.

    It is exposed because the overlap statement needs it; this guard fails if it acquires a second
    caller, which is the moment someone has started meta-analysing.
    """
    import inspect
    src = inspect.getsource(pc)
    calls = src.count("log_hr_se(")
    # the def, the two uses inside concordance(), and the guard's own reference in the docstring
    assert calls <= 4, f"log_hr_se now has {calls} references -- check nothing is pooling"


def test_the_risk_table_census_answer_is_recorded(doc):
    for name, c in doc["cohorts"].items():
        assert c["risk_table_under_any_km_figure"] is False, name
    assert "0 risk tables" in doc["⛔_neither_cohort_prints_a_risk_table"]
