"""Guards on the EMC radiotherapy re-examination.

The load-bearing pieces are the inversion arithmetic, the overlap computation, and the
primary/secondary provenance split. The last of those is the one most easily lost by a later edit
tidying the records into a uniform shape, so it is asserted from several directions.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import emc_radiotherapy_contradiction as rc  # noqa: E402


@pytest.fixture(scope="module")
def doc():
    return rc.build()


def test_the_artifact_reproduces_from_its_generator():
    assert rc.check() == 0


def test_all_structural_guards_hold():
    assert rc._check_structure() == []
    assert rc._check_inversion() == []


def test_inverting_a_hazard_ratio_swaps_and_reciprocates_its_bounds():
    """The one piece of real arithmetic in the file."""
    inv = rc.invert(4.0, [2.0, 8.0])
    assert inv["hr"] == 0.25
    assert inv["ci"] == [0.125, 0.5]
    # order is reversed, never merely reciprocated in place
    assert inv["ci"][0] < inv["ci"][1]


def test_the_inversion_round_trips_on_the_real_estimate():
    """⚠ RELATIVE tolerance, not absolute.

    invert() rounds to 4 decimal places, so the reciprocal of a large bound survives with only as
    many significant figures as that rounding leaves: 1/115.3 rounds to 0.0087, and 1/0.0087 comes
    back as 114.9 rather than 115.3. An absolute tolerance that is sensible for an HR near 12 is
    meaningless against a bound near 115, which is exactly the error this assertion first made.
    """
    b = next(e for e in rc.ESTIMATES if e["source_id"] == "bishop2019")
    inv = rc.invert(b["hr"], b["ci"])
    assert 1.0 / inv["hr"] == pytest.approx(b["hr"], rel=0.01)
    assert 1.0 / inv["ci"][1] == pytest.approx(b["ci"][0], rel=0.01)
    assert 1.0 / inv["ci"][0] == pytest.approx(b["ci"][1], rel=0.01)


def test_the_overlap_is_computed_and_not_asserted(doc):
    c = doc["comparison"]
    inv = c["bishop2019_inverted_to_a_radiotherapy_effect"]["ci"]
    mas = c["masunaga2025_as_printed"]["ci"]
    lo, hi = max(inv[0], mas[0]), min(inv[1], mas[1])
    assert c["intervals_overlap"] is (lo <= hi)
    assert c["overlap_interval"] == [round(lo, 4), round(hi, 4)]
    assert c["both_point_estimates_protective"] is True


def test_the_overlap_finding_would_fail_if_the_estimates_moved(monkeypatch):
    """Prove the conclusion is derived, not written in.

    Push Masunaga's interval entirely above Bishop's inverted upper bound and the module must stop
    reporting an overlap.
    """
    mas = next(e for e in rc.ESTIMATES if e["source_id"] == "masunaga2025")
    monkeypatch.setitem(mas, "ci", [1.5, 4.0])
    monkeypatch.setitem(mas, "hr", 2.0)
    c = rc.comparison()
    assert c["intervals_overlap"] is False
    assert c["overlap_interval"] is None
    assert c["both_point_estimates_protective"] is False


def test_the_headline_quotes_the_derived_numbers(doc):
    c = doc["comparison"]
    inv = c["bishop2019_inverted_to_a_radiotherapy_effect"]
    head = doc["⭐_the_headline"]
    assert str(inv["hr"]) in head
    assert str(c["overlap_interval"][0]) in head and str(c["overlap_interval"][1]) in head


def test_every_significance_flag_agrees_with_its_own_interval():
    for e in rc.ESTIMATES:
        lo, hi = e["ci"]
        assert (lo > 1.0 or hi < 1.0) == (e["p"] < 0.05), e["source_id"]


def test_no_pooled_hazard_ratio_exists_anywhere(doc):
    """Structural anti-pooling guard: every hr in the artifact is printed or an exact inversion."""
    printed = {e["hr"] for e in rc.ESTIMATES}
    allowed = set(printed)
    for e in rc.ESTIMATES:
        allowed.add(rc.invert(e["hr"], e["ci"])["hr"])
    found = []

    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k == "hr" and isinstance(v, (int, float)):
                    found.append(v)
                else:
                    walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(doc)
    assert found
    assert not (set(found) - allowed), f"derived hazard ratios present: {set(found) - allowed}"


def test_every_secondary_record_says_it_was_not_read_directly(doc):
    """POLICY-evidence 1.3: never launder a citation."""
    secondary = [c for c in rc.MODALITY_CASE_REPORTS if c["provenance"] == "secondary"]
    assert secondary, "no secondary records -- the guard would pass vacuously"
    for c in secondary:
        assert "⛔_not_read_directly" in c, c["modality"]
    for c in rc.MODALITY_CASE_REPORTS:
        assert c["provenance"] in ("primary", "secondary")
        assert c["read_from"]
    assert doc["provenance_split"]["secondary"]
    assert doc["counts"]["primary_records"] + doc["counts"]["secondary_records"] == (
        len(rc.ESTIMATES) + len(rc.MODALITY_CASE_REPORTS))


def test_stripping_a_secondary_marker_fails_the_structure_check(monkeypatch):
    sec = next(c for c in rc.MODALITY_CASE_REPORTS if c["provenance"] == "secondary")
    trimmed = {k: v for k, v in sec.items() if k != "⛔_not_read_directly"}
    patched = [trimmed if c is sec else c for c in rc.MODALITY_CASE_REPORTS]
    monkeypatch.setattr(rc, "MODALITY_CASE_REPORTS", patched)
    assert any("not-read-directly" in e for e in rc._check_structure())


def test_both_comparable_estimates_are_primary():
    """The comparison is the module's central claim; neither side may rest on a review."""
    for e in rc.ESTIMATES:
        assert e["provenance"] == "primary", e["source_id"]
        assert "literature-cache" in e["read_from"] or "emc-prognostic-coefficients" in e["read_from"]


def test_the_carbon_ion_finding_records_how_it_was_searched(doc):
    ci = doc["carbon_ion"]
    assert ci["found_in_this_histology"] is False
    assert "354" in ci["how_searched"]
    assert "⛔_absence_of_evidence" in ci
    assert "may exist and be unpublished" in ci["⛔_absence_of_evidence"]
    # the rejected search-summary lead is recorded rather than silently dropped
    assert "never a citation" in ci["⚠_a_search_summary_suggested_otherwise_and_was_not_used"]


def test_no_efficacy_claim_is_made(doc):
    blob = json.dumps(doc, ensure_ascii=False).lower()
    assert "this does not show radiotherapy works" in blob
    assert "fails to establish the disagreement" in blob
    for forbidden in ("radiotherapy is effective", "proven benefit", "should receive radiotherapy"):
        assert forbidden not in blob, forbidden


def test_the_case_reports_are_labelled_existence_proofs(doc):
    note = doc["⛔_case_reports_are_existence_proofs"]
    assert "can never answer" in note
    for c in rc.MODALITY_CASE_REPORTS:
        assert c["n"] == 1


def test_the_dose_response_is_still_declared_unbuildable(doc):
    note = doc["⛔_the_dose_response_is_still_unbuildable"]
    assert "per patient" in note.lower()
    # and the arm-level dose data that makes the route's wording wrong is actually present
    b = next(e for e in rc.ESTIMATES if e["source_id"] == "bishop2019")
    m = next(e for e in rc.ESTIMATES if e["source_id"] == "masunaga2025")
    assert b["dose_gy"]["median"] == 50 and b["dose_gy"]["range"] == [50, 65]
    assert m["dose_gy"]["neoadjuvant"] == [40, 50] and m["dose_gy"]["adjuvant"] == [50, 66]
    assert b["dose_gy"]["per_arm"] is None


def test_bishop_arms_sum_to_its_cohort():
    b = next(e for e in rc.ESTIMATES if e["source_id"] == "bishop2019")
    assert sum(b["arms"].values()) == b["n"] == 41


def test_masunaga_arms_sum_to_its_cohort():
    m = next(e for e in rc.ESTIMATES if e["source_id"] == "masunaga2025")
    assert sum(m["arms"].values()) == m["n"] == 134


def test_the_garbled_table_is_flagged_and_depended_on_by_nothing(doc):
    """A table that could not be parsed must not become a reported discrepancy."""
    b = next(e for e in rc.ESTIMATES if e["source_id"] == "bishop2019")
    note = b["⚠_the_univariate_table_could_not_be_parsed_reliably"]
    assert "NOT REPORTED AS A DISCREPANCY" in note
    assert "nothing in this module depends on it" in note
