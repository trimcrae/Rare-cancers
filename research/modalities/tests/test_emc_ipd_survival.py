"""Known-answer control and guard tests for `emc_ipd_survival.py`.

WHAT THE CONTROL ACTUALLY CONTROLS
----------------------------------
`test_reconstruction_recovers_a_cohort_it_never_saw` builds a cohort with KNOWN patient-level
data, computes its EXACT Kaplan-Meier curve and numbers-at-risk table, hands ONLY those two
published-figure-shaped objects to the reconstructor, and asserts the original cohort comes back.
The truth is established independently of the thing under test, which is what makes it a
known-answer control rather than a round-trip against itself.

⛔ AND WHAT IT DOES NOT CONTROL, STATED HERE SO NOBODY HAS TO INFER IT. The control feeds EXACT
coordinates. A real curve is read off a figure by eye, so this bounds ALGORITHMIC error and is
structurally incapable of failing on digitization error. That second source is bounded per curve
by `max_abs_km_deviation` against the quality floor, never by this test.

The `--check` guard test perturbs the REAL committed artifact on disk and asserts the REAL
`main(["--check"])` refuses it AND writes nothing -- because a guard exercised only against a mock
is a test of the mock (CLAUDE.md s6, the 2026-08-06 census-lookup incident).
"""

from __future__ import annotations

import json
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import emc_ipd_survival as mod  # noqa: E402


# ---------------------------------------------------------------------------
# the cohort the reconstructor is not allowed to see
# ---------------------------------------------------------------------------
def _truth_cohort() -> list[dict]:
    """A cohort with the shape EMC actually has: long follow-up, heavy late censoring."""
    events = [4, 4, 9, 13, 13, 18, 26, 31, 38, 47, 55]
    censored = [7, 11, 16, 16, 22, 29, 34, 34, 41, 44, 50, 52, 58, 60, 60]
    return [{"time": float(t), "event": 1} for t in events] + [
        {"time": float(t), "event": 0} for t in censored
    ]


def _published_figure(cohort: list[dict], risk_times: list[float]) -> dict:
    """Everything a paper prints, and nothing it does not: a curve and a risk table."""
    km = mod.kaplan_meier(cohort)
    digitized = [[0.0, 1.0]] + [[row["time"], row["survival"]] for row in km]
    risk_table = []
    for t in risk_times:
        n = sum(1 for r in cohort if r["time"] >= t)
        risk_table.append([t, n])
    return {
        "id": "control_synthetic",
        "source_id": "control",
        "endpoint": "os",
        "population": "synthetic control cohort",
        "time_unit": "months",
        "digitized": digitized,
        "risk_table": risk_table,
        "total_events": sum(1 for r in cohort if r["event"]),
        "digitized_by": "constructed exactly; not read from a figure",
    }


# ---------------------------------------------------------------------------
# the control
# ---------------------------------------------------------------------------
def test_reconstruction_recovers_a_cohort_it_never_saw():
    truth = _truth_cohort()
    curve = _published_figure(truth, risk_times=[0.0, 15.0, 30.0, 45.0])

    rec = mod.reconstruct(curve)

    n_true_events = sum(1 for r in truth if r["event"])
    assert rec["n_events"] == n_true_events, (
        f"recovered {rec['n_events']} events, truth has {n_true_events}"
    )
    # Total cohort size is recovered to within one patient: censoring is assumed uniform inside
    # each risk interval, so a boundary case can land one either side. Anything larger is a bug.
    assert abs(rec["n_reconstructed"] - len(truth)) <= 1, (
        f"recovered n={rec['n_reconstructed']}, truth n={len(truth)}"
    )
    # The reconstruction must reproduce the curve it was built from.
    assert rec["max_abs_km_deviation"] <= mod.MAX_KM_DEVIATION


def test_the_recovered_survival_curve_matches_the_truth_at_every_printed_time():
    truth = _truth_cohort()
    curve = _published_figure(truth, risk_times=[0.0, 15.0, 30.0, 45.0])

    rec = mod.reconstruct(curve)
    km_true = mod.kaplan_meier(truth)
    km_rec = mod.kaplan_meier(rec["ipd"])

    for t in (10.0, 20.0, 30.0, 40.0, 50.0):
        s_true = mod.survival_at(km_true, t)
        s_rec = mod.survival_at(km_rec, t)
        assert s_true is not None and s_rec is not None
        assert abs(s_true - s_rec) <= mod.MAX_KM_DEVIATION, (
            f"t={t}: truth S={s_true:.4f}, reconstructed S={s_rec:.4f}"
        )


def test_the_control_is_sensitive_enough_to_fail():
    """A control that cannot fail is not a control.

    Corrupt the risk table the way a real mis-read would and assert the reconstruction moves
    away from the truth. Without this, the two assertions above could be passing on tolerance
    alone and nobody would know.
    """
    truth = _truth_cohort()
    good = _published_figure(truth, risk_times=[0.0, 15.0, 30.0, 45.0])
    bad = json.loads(json.dumps(good))
    bad["risk_table"] = [[t, max(1, n // 3)] for t, n in bad["risk_table"]]

    rec_bad = mod.reconstruct(bad)
    assert rec_bad["n_reconstructed"] < len(truth) - 1, (
        "a three-fold-wrong risk table produced a cohort indistinguishable from the truth, "
        "which means the assertions above are not testing anything"
    )


# ---------------------------------------------------------------------------
# the quality floor is a refusal, not a caveat
# ---------------------------------------------------------------------------
def test_a_curve_with_no_risk_table_is_refused_rather_than_reconstructed():
    truth = _truth_cohort()
    curve = _published_figure(truth, risk_times=[0.0, 15.0, 30.0, 45.0])
    curve.pop("risk_table")

    with pytest.raises(ValueError, match="risk table"):
        mod.reconstruct(curve)

    q = mod.assess_quality(curve, None, error="no risk table")
    assert q["admissible"] is False
    assert any("no_numbers_at_risk_table" in f for f in q["failures"])


def test_a_curve_without_digitization_provenance_is_inadmissible():
    truth = _truth_cohort()
    curve = _published_figure(truth, risk_times=[0.0, 15.0, 30.0, 45.0])
    curve.pop("digitized_by")
    rec = mod.reconstruct(curve)
    q = mod.assess_quality(curve, rec)
    assert q["admissible"] is False
    assert "no_digitization_provenance" in q["failures"]


def test_median_survival_is_none_when_not_reached_rather_than_a_number():
    """In an indolent disease "not reached" is the common answer and must never render as 0."""
    cohort = [{"time": float(t), "event": 0} for t in range(1, 20)]
    cohort.append({"time": 5.0, "event": 1})
    km = mod.kaplan_meier(cohort)
    assert mod._median_survival(km) is None


# ---------------------------------------------------------------------------
# the artifact contract
# ---------------------------------------------------------------------------
def test_the_curves_table_is_empty_and_the_artifact_says_so():
    """Guards the one thing that would be fabrication: a curve coordinate nobody read."""
    assert mod.CURVES == [], (
        "CURVES is non-empty. A coordinate typed into the generator has no derivation behind it "
        "and looks identical whether it was measured or guessed. Digitized curves must arrive "
        "through load_digitized_curves(), which can only return a curve attached to a recipe "
        "naming the image it was read from."
    )
    payload = mod.build()
    loaded = mod.load_digitized_curves()
    assert payload["curves_hand_typed"] == 0
    assert payload["curves_supplied"] == len(loaded)
    if not loaded:
        assert "NO CURVES DIGITIZED" in payload["status"]
        assert payload["pooled"] is None


def test_every_loaded_curve_carries_its_provenance_and_passed_an_external_check():
    """⚠ THIS IS THE PROPERTY THE EMPTINESS ASSERTION USED TO STAND IN FOR.

    While no figure had been read, "CURVES is empty" was a complete defence against a fabricated
    clinical datum. It is no longer, because curves now exist -- so the property has to be asserted
    directly: every coordinate in this program traces to a COMMITTED image, a recorded reader, and
    a quantity the paper printed that the reconstruction never saw.
    """
    for curve in mod.load_digitized_curves():
        assert curve["digitized"], curve["id"]
        assert curve["risk_table"], f"{curve['id']}: admitted without a numbers-at-risk table"
        assert curve["digitized_by"], f"{curve['id']}: no digitization provenance"
        assert curve.get("image"), f"{curve['id']}: names no source image"
        img = os.path.join(os.path.dirname(mod.READINGS), "figures", curve["image"])
        assert os.path.exists(img), (
            f"{curve['id']}: its source image {curve['image']} is not committed, so the reading "
            "cannot be re-run or refuted by anyone reading the artifact")
        chk = curve.get("external_check") or {}
        assert chk.get("printed_value") is not None, (
            f"{curve['id']}: admitted with no externally printed quantity to check the READING "
            "against. Self-consistent arithmetic is not evidence that a figure was read right.")


def test_a_reading_that_fails_its_external_check_is_not_loaded(tmp_path, monkeypatch):
    """Shown capable of failing: flip the external check in the artifact and the loader drops it."""
    if not os.path.exists(mod.READINGS):
        pytest.skip("no readings artifact in this checkout")
    with open(mod.READINGS, encoding="utf-8") as fh:
        doc = json.load(fh)
    before = len(mod.load_digitized_curves())
    if not before:
        pytest.skip("no curves loaded in this checkout")
    for reading in doc["readings"]:
        for rec in (reading.get("reconstructions") or {}).values():
            rec["external_check_passes"] = False
    perturbed = tmp_path / "readings.json"
    with open(perturbed, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    monkeypatch.setattr(mod, "READINGS", str(perturbed))
    assert mod.load_digitized_curves() == []


def test_check_refuses_a_perturbed_artifact_and_writes_nothing(tmp_path, monkeypatch):
    # ⛔ ISOLATED 2026-08-29 (AUT-PD-187). This mutated the LIVE tracked artifact and restored it in
    # a `finally` — safe only while nothing else reads it, and this suite runs under xdist. See
    # research/manuscripts/tests/tracked_tree_guard.py for what that cost. The producer's OUT is
    # redirected at a private copy, so what is under test is unchanged and the tree is never written.
    assert os.path.exists(mod.OUT), "run `python3 research/modalities/emc_ipd_survival.py` first"
    copy = tmp_path / os.path.basename(mod.OUT)
    shutil.copyfile(mod.OUT, copy)
    monkeypatch.setattr(mod, "OUT", str(copy))

    with open(mod.OUT, encoding="utf-8") as fh:
        payload = json.load(fh)
    payload["curves_supplied"] = 99  # the kind of hand edit the banner forbids
    with open(mod.OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    mtime_before = os.path.getmtime(mod.OUT)

    assert mod.main(["--check"]) == 1, "--check accepted a hand-edited artifact"

    with open(mod.OUT, encoding="utf-8") as fh:
        assert json.load(fh)["curves_supplied"] == 99, "--check rewrote the artifact"
    assert os.path.getmtime(mod.OUT) == mtime_before


def test_check_passes_on_the_committed_artifact():
    assert mod.main(["--check"]) == 0


def test_every_candidate_source_resolves_to_a_real_registry_citation():
    """The work list must point at sources that exist.

    CANDIDATE_SOURCES is free to build and therefore easy to let rot: a renamed or removed
    citation key would leave a row pointing at nothing, and the list would still LOOK like a
    plan. CLAUDE.md s6 records the cost of exactly this shape -- a name wired to a value
    nothing used, documented in three places, which read as safe while doing nothing. So the
    linkage is asserted rather than described.
    """
    path = os.path.join(mod.REPO, "research", "data", "emc-clinical-registry.json")
    with open(path, encoding="utf-8") as fh:
        registry = json.load(fh)
    citations = registry.get("registry", registry)["citations"]

    assert mod.CANDIDATE_SOURCES, "the work list is empty -- enumerating it costs nothing"
    unresolved = [
        row["source_id"] for row in mod.CANDIDATE_SOURCES if row["source_id"] not in citations
    ]
    assert not unresolved, f"candidate rows point at citations that do not exist: {unresolved}"


def test_every_checked_candidate_records_what_the_graphic_actually_showed():
    """Presence on the work list must never be mistaken for evidence.

    ⚠ *Superseded, retained: this guard asserted `not checked or mod.CURVES` -- that no row could
    claim `figure_checked` while the artifact reported zero curves.* That was right while nothing
    had been read and is wrong now, and in a way worth naming: FOUR of the five figures checked on
    2026-08-25 produced NO curve, because they print no numbers-at-risk row. Under the old form,
    correctly recording four negatives would have required either lying about the flag or
    inventing a curve. **A checked row with no curve is the normal outcome of looking.**

    What replaces it is stronger: a flag must be accompanied by the FINDING it stands for, and a
    row that claims a digitized curve must have one that the loader actually returns.
    """
    checked = [r for r in mod.CANDIDATE_SOURCES if r.get("figure_checked")]
    for row in checked:
        finding = row.get("figure_finding")
        assert finding, (
            f"{row['source_id']}: figure_checked is True with no figure_finding. A flag without a "
            "finding is a populated field that was never measured -- the 2026-07-31 failure.")
        assert "km_figures" in finding, row["source_id"]
        assert "numbers_at_risk_row" in finding, row["source_id"]

    loaded = {c["source_id"] for c in mod.load_digitized_curves()}
    for row in checked:
        if row["figure_finding"].get("digitized"):
            assert row["source_id"] in loaded, (
                f"{row['source_id']}: claims a digitized curve that load_digitized_curves() does "
                "not return")
    for source_id in loaded:
        row = next(r for r in mod.CANDIDATE_SOURCES if r["source_id"] == source_id)
        assert row.get("figure_checked"), (
            f"{source_id}: a curve was loaded from a figure the work list still calls unchecked")


# ---------------------------------------------------------------------------
# transcribed patient-level data
# ---------------------------------------------------------------------------
def test_every_printed_ipd_row_names_its_table_and_its_verification():
    """Transcription's failure mode is a silent digit, so provenance is the whole guard.

    ⛔ A misread `17` as `12` produces a perfectly plausible cohort and no symptom. The defence is
    that each row names the exact table and row it came from and records that the digits were
    checked against the PDF TEXT LAYER, not only against a rendered page — a raster is exactly
    where an OCR-style slip happens.
    """
    for row in mod.PRINTED_IPD:
        assert row.get("printed_in"), row
        assert "Table" in row["printed_in"], row["printed_in"]
        assert "text layer" in (row.get("verified_against") or ""), row
        assert row["source_id"] in {c["source_id"] for c in mod.CANDIDATE_SOURCES}, row


def test_printed_ipd_carries_only_the_disease_this_program_is_about():
    """The one table transcribed here also lists MESENCHYMAL chondrosarcoma patients.

    Taking a whole table because the paper is EMC-relevant is the ICD-O-3 conflation
    RT-DIAGNOSTIC-PATHWAY exists to record, so the histology is asserted rather than assumed.
    """
    for row in mod.PRINTED_IPD:
        assert row["histology"] in {"EMCS", "EMC"}, row


def test_printed_rows_are_reported_but_never_pooled():
    payload = mod.build()
    block = payload["printed_patient_level_data"]
    assert block["n_rows"] == len(mod.PRINTED_IPD)
    pooled = payload.get("pooled")
    if pooled:
        assert pooled["n_patients"] != block["n_rows"] + 0, "printed rows leaked into the pool"
        for curve_id in pooled["curves_pooled"]:
            assert "morioka" not in curve_id


# ---------------------------------------------------------------------------
# what "pooled" is allowed to mean
# ---------------------------------------------------------------------------
def _fake_record(rid, source, endpoint, times):
    return {"id": rid, "source_id": source, "endpoint": endpoint,
            "population": f"synthetic {source}",
            "ipd": [{"time": float(t), "event": 1} for t in times]}


def test_pooling_across_endpoints_raises_rather_than_caveats():
    """⛔ A category error, not a bias. OS and PFS are different events on different clocks, so a
    curve over both estimates nothing — and a caveat on a number that wrong travels worse than a
    crash. Shown capable of failing by the same-endpoint case immediately below."""
    mixed = [_fake_record("a", "s1", "os", [1, 2, 3]),
             _fake_record("b", "s2", "pfs", [1, 2, 3])]
    with pytest.raises(ValueError) as exc:
        mod.pool_reconstructions(mixed)
    assert "endpoint" in str(exc.value)


def test_pooling_within_one_endpoint_is_allowed():
    same = [_fake_record("a", "s1", "os", [1, 2, 3]),
            _fake_record("b", "s2", "os", [4, 5, 6])]
    out = mod.pool_reconstructions(same)
    assert out["n_patients"] == 6
    assert out["endpoint"] == "os"
    assert out["sources_pooled"] == ["s1", "s2"]
    assert "⛔_this_is_not_a_pool" not in out


def test_a_single_curve_says_it_is_not_a_pool():
    """The state this program is actually in: one admitted curve wearing the word 'pooled'."""
    one = [_fake_record("a", "s1", "pfs", [1, 2, 3])]
    out = mod.pool_reconstructions(one)
    note = out.get("⛔_this_is_not_a_pool")
    assert note, "a one-curve pool did not say so"
    assert "s1" in note and "NOT a pooled" in note


@pytest.mark.committed_artifact
def test_the_committed_artifact_does_not_present_one_curve_as_a_pool():
    payload = mod.build()
    pooled = payload.get("pooled")
    if not pooled:
        pytest.skip("no curves admitted in this checkout")
    if len(pooled["curves_pooled"]) == 1:
        assert "⛔_this_is_not_a_pool" in pooled
