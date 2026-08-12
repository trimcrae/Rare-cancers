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
        "CURVES is non-empty. Every entry must carry `digitized_by` naming who read the figure "
        "and with what tool; a coordinate without that provenance is a fabricated clinical datum."
    )
    payload = mod.build()
    assert payload["curves_supplied"] == 0
    assert "NO CURVES DIGITIZED" in payload["status"]
    assert payload["pooled"] is None


def test_check_refuses_a_perturbed_artifact_and_writes_nothing(tmp_path):
    assert os.path.exists(mod.OUT), "run `python3 research/modalities/emc_ipd_survival.py` first"
    backup = tmp_path / "artifact.json"
    shutil.copy(mod.OUT, backup)
    try:
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
    finally:
        shutil.copy(backup, mod.OUT)


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


def test_no_candidate_claims_its_figure_has_been_read():
    """Presence on the work list must never be mistaken for evidence.

    A row with figure_checked True and no corresponding entry in CURVES would assert that a
    published figure was read while the artifact still reports zero curves -- the 2026-07-31
    failure in a new costume, where a populated field was read as a measured one.
    """
    checked = [r["source_id"] for r in mod.CANDIDATE_SOURCES if r.get("figure_checked")]
    assert not checked or mod.CURVES, (
        f"rows claim a figure was read while CURVES is empty: {checked}"
    )
