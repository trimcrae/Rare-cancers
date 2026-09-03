"""Tests for the EMC mortality decomposition.

The properties locked here are the ones whose violation would publish a wrong clinical
number, not the ones that are convenient to assert. Two of them are regressions of real
bugs found while building this:

  * the reported band was first taken from the two EXTREME cross-series pairings, which
    produced a headline competing share running from -25% to 57%. A negative share is
    arithmetically impossible and was being published as a lower bound;
  * a cohort reporting 100% survival has no deaths to apportion, so its competing share
    is undefined rather than zero, and treating it as a number put a division by zero one
    refactor away.

Both are now separated, counted and excluded from the band, and both are tested against
the real functions rather than a mocked seam.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
MODULE = ROOT / "research/manuscripts/emc_mortality_decomposition.py"


def _load():
    spec = importlib.util.spec_from_file_location("emc_mortality_decomposition", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = _load()


# ---------------------------------------------------------------------------
# The arithmetic
# ---------------------------------------------------------------------------
def test_decompose_splits_all_cause_mortality_into_disease_and_the_rest():
    # 70% all-cause survival, 85% disease-specific: 30 points of death, 15 of them EMC.
    d = D.decompose(0.70, 0.85)
    assert d["all_cause_mortality_pct"] == 30.0
    assert d["disease_mortality_pct"] == 15.0
    assert d["competing_mortality_pct"] == 15.0
    assert d["competing_share_of_deaths_pct"] == 50.0
    assert d["coherent"] is True


def test_the_antitumour_ceiling_is_the_disease_mortality_there_is_to_remove():
    """The ceiling is what a therapy preventing EVERY EMC death would add, so it is
    exactly the disease-specific mortality -- not the all-cause mortality, which is the
    error that would overstate the whole portfolio's headroom."""
    d = D.decompose(0.65, 0.85)
    assert d["antitumour_ceiling_pct_points"] == 15.0
    assert d["antitumour_ceiling_pct_points"] < d["all_cause_mortality_pct"]


def test_disease_mortality_above_all_cause_is_flagged_incoherent_not_returned_as_negative():
    d = D.decompose(0.88, 0.85)          # 12 points of death, 15 of them 'EMC'
    assert d["coherent"] is False
    assert d["incoherence_note"] is not None
    assert "impossible" in d["incoherence_note"]


def test_zero_all_cause_mortality_gives_an_undefined_share_not_zero():
    """A cohort with no deaths has no cause split. Returning 0.0 here would read as
    'none of the deaths were competing', which is a claim about patients who do not
    exist."""
    d = D.decompose(1.00, 0.758)
    assert d["competing_share_of_deaths_pct"] is None


# ---------------------------------------------------------------------------
# Cross-series banding -- the regression that matters most
# ---------------------------------------------------------------------------
def _spec_with(series, pooled=None):
    return {"series": series, "pooled_reference": pooled or {}}


def test_the_reported_band_excludes_impossible_pairings_and_counts_them():
    spec = _spec_with([
        {"key": "ac_good", "overall_survival": {"10": 0.88}},   # 12 pts of death
        {"key": "ac_bad", "overall_survival": {"10": 0.65}},    # 35 pts of death
        {"key": "ds", "disease_specific_survival": {"10": 0.85}},  # 15 pts of EMC death
    ])
    out = D.cross_series(spec)["10_year"]

    # ac_good x ds is impossible (15 > 12); ac_bad x ds is fine.
    assert out["pairings_total"] == 2
    assert out["pairings_impossible"] == 1
    assert out["pairings_coherent"] == 1
    lo, hi = out["competing_share_of_deaths_pct_range"]
    assert lo >= 0 and hi >= 0, "a negative competing share must never reach the band"
    assert out["excluded_pairings"]["impossible"][0]["all_cause_source"] == "ac_good"


def test_a_no_death_cohort_paired_against_real_disease_deaths_is_impossible_not_undefined():
    """⚠ The distinction is not pedantic and the first version of this test had it
    backwards. A cohort reporting 100% survival paired against a disease-specific figure
    showing real EMC deaths is a CONTRADICTION -- there cannot be deaths from a cause in a
    population with no deaths -- so it belongs with the impossible pairings, which is the
    louder signal. Only a genuine 0/0 is undefined."""
    spec = _spec_with([
        {"key": "perfect", "overall_survival": {"5": 1.00}},
        {"key": "ds", "disease_specific_survival": {"5": 0.90}},
    ])
    out = D.cross_series(spec)["5_year"]
    assert out["pairings_impossible"] == 1
    assert out["pairings_undefined"] == 0
    assert out["pairings_coherent"] == 0
    assert out["competing_share_of_deaths_pct_range"] is None, (
        "with no coherent pairing there is no band, and inventing one from the "
        "degenerate pairing is exactly the bug this separation exists to stop")


def test_a_genuine_zero_over_zero_is_undefined_rather_than_impossible():
    spec = _spec_with([
        {"key": "perfect_ac", "overall_survival": {"5": 1.00}},
        {"key": "perfect_ds", "disease_specific_survival": {"5": 1.00}},
    ])
    out = D.cross_series(spec)["5_year"]
    assert out["pairings_undefined"] == 1
    assert out["pairings_impossible"] == 0
    assert out["competing_share_of_deaths_pct_range"] is None


def test_every_pairing_is_enumerated_not_just_the_extremes():
    """The original implementation looked at two pairings out of N x M. The count is the
    cheapest proof it no longer does."""
    spec = _spec_with([
        {"key": "a1", "overall_survival": {"10": 0.60}},
        {"key": "a2", "overall_survival": {"10": 0.65}},
        {"key": "a3", "overall_survival": {"10": 0.70}},
        {"key": "d1", "disease_specific_survival": {"10": 0.85}},
        {"key": "d2", "disease_specific_survival": {"10": 0.90}},
    ])
    out = D.cross_series(spec)["10_year"]
    assert out["pairings_total"] == 6
    assert out["pairings_coherent"] == 6


def test_the_pooled_reference_joins_the_ten_year_disease_specific_band():
    spec = _spec_with(
        [{"key": "ac", "overall_survival": {"10": 0.70}}],
        pooled={"value": 0.85, "registry_verbatim": "approximately 85%"},
    )
    out = D.cross_series(spec)["10_year"]
    assert "registry_pooled" in out["disease_specific_sources"]


# ---------------------------------------------------------------------------
# Within-series pairing
# ---------------------------------------------------------------------------
def test_within_series_pairs_the_horizon_nearest_the_actual_follow_up():
    """Pairing a crude death proportion observed over 9 years against a 15-year curve
    reading compares a number nobody measured against one that ran twice as long."""
    spec = {"series": [{
        "key": "s", "label": "s", "n": 100, "pairing": "within_series",
        "overall_survival": {"5": 0.90, "10": 0.70, "15": 0.60},
        "disease_death": {"events": 18, "denom": 99},
        "median_followup_months": 108,
    }], "pooled_reference": {}}
    row = D.within_series(spec)[0]
    assert row["horizon_years"] == 10.0
    assert row["median_followup_years"] == 9.0


def test_within_series_reports_its_own_estimator_mismatch():
    spec = {"series": [{
        "key": "s", "label": "s", "n": 100, "pairing": "within_series",
        "overall_survival": {"10": 0.70},
        "disease_death": {"events": 18, "denom": 99},
        "median_followup_months": 108,
    }], "pooled_reference": {}}
    row = D.within_series(spec)[0]
    assert "not the same estimator" in row["estimator_mismatch"]


def test_cross_series_rows_are_not_returned_by_within_series():
    spec = {"series": [{
        "key": "s", "label": "s", "n": 10, "pairing": "cross_series",
        "overall_survival": {"10": 0.70},
        "disease_death": {"events": 1, "denom": 10},
        "median_followup_months": 120,
    }], "pooled_reference": {}}
    assert D.within_series(spec) == []


# ---------------------------------------------------------------------------
# Provenance -- the figures must stay findable in the registry
# ---------------------------------------------------------------------------
def test_provenance_fails_when_a_quoted_registry_string_is_gone():
    spec = _spec_with([{"key": "s", "registry_verbatim": "82/65/58% (5/10/15-yr OS)"}])
    failures = D.verify_provenance(spec, json.dumps({"something": "else"}))
    assert len(failures) == 1
    assert "no longer appears" in failures[0]


def test_provenance_passes_when_the_string_is_still_there():
    spec = _spec_with([{"key": "s", "registry_verbatim": "82/65/58% (5/10/15-yr OS)"}])
    blob = json.dumps({"note": "outcomes were 82/65/58% (5/10/15-yr OS) overall"})
    assert D.verify_provenance(spec, blob) == []


def test_the_real_inputs_still_resolve_against_the_real_registry():
    """The guard above tests the mechanism; this one tests the wiring, against the real
    committed files. Mock the thing under test and you test the mock."""
    spec = json.loads((ROOT / "research/manuscripts/emc-mortality-decomposition-inputs.json")
                      .read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "research/data/emc-clinical-registry.json")
                          .read_text(encoding="utf-8"))
    assert D.verify_provenance(spec, D.registry_text_blob(registry)) == []


# ---------------------------------------------------------------------------
# The background check must not fabricate a verdict
# ---------------------------------------------------------------------------
def test_background_check_reports_not_run_rather_than_assuming_a_value():
    spec = {"background_mortality": {"ten_year_background_mortality": None,
                                     "cohort_age_median": 55}}
    out = D.background_check(spec, {})
    assert out["status"] == "NOT_RUN"
    assert "not evidence" in out["why"].lower() or "NOT evidence" in out["why"]


def test_background_check_runs_when_a_life_table_is_present():
    spec = {"background_mortality": {"ten_year_background_mortality": 0.13,
                                     "life_table_source": "SSA period life table"}}
    cross = {"10_year": {"competing_share_of_deaths_pct_median": 50.0,
                         "all_cause_survival_pct_range": [70.0, 88.0],
                         "extremes": {}}}
    out = D.background_check(spec, cross)
    assert out["status"] == "RUN"
    assert out["expected_background_mortality_pct_at_10y"] == 13.0


# ---------------------------------------------------------------------------
# The committed artifact
# ---------------------------------------------------------------------------
def test_the_committed_artifact_carries_no_negative_or_impossible_headline():
    art = ROOT / "research/manuscripts/emc-mortality-decomposition.json"
    # ⛔ NOT A SKIP. The artifact is COMMITTED, so "not generated in this checkout" can only mean a
    # broken tree — which is exactly the moment this guard has to speak rather than evaporate
    # (research/manuscripts/tests/test_no_guard_can_silently_not_run.py).
    assert art.exists(), f"{art.relative_to(ROOT)} is committed; a missing one is a broken checkout"
    payload = json.loads(art.read_text(encoding="utf-8"))
    for horizon, row in payload["cross_series"].items():
        band = row["competing_share_of_deaths_pct_range"]
        if band is None:
            continue
        assert min(band) >= 0, f"{horizon} publishes a negative competing share"
        assert max(band) <= 100, f"{horizon} publishes a share above 100%"
    for row in payload["within_series"]:
        assert row["coherent"], f"{row['series']} is published despite being incoherent"


def test_the_committed_artifact_states_its_directional_bias():
    """The subtraction is only publishable because its one bias runs against its own
    conclusion. If that sentence ever leaves the artifact, the artifact overclaims."""
    art = ROOT / "research/manuscripts/emc-mortality-decomposition.json"
    # ⛔ NOT A SKIP. The artifact is COMMITTED, so "not generated in this checkout" can only mean a
    # broken tree — which is exactly the moment this guard has to speak rather than evaporate
    # (research/manuscripts/tests/test_no_guard_can_silently_not_run.py).
    assert art.exists(), f"{art.relative_to(ROOT)} is committed; a missing one is a broken checkout"
    payload = json.loads(art.read_text(encoding="utf-8"))
    assert "UNDER-estimate" in payload["directional_bias"]
