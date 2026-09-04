"""Maintenance findings must not restart a completed review; missing evidence is not clean."""
import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def recorder(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "review_recorder", Path(__file__).resolve().parents[1] / "record_bar_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seats = tmp_path / "seats"
    seats.mkdir()
    monkeypatch.setattr(module, "SEATS_DIR", seats)
    monkeypatch.setattr(module, "HARDENING_DIR", tmp_path / "state")
    monkeypatch.setattr(module, "_rel", str)
    return module


@pytest.mark.parametrize("finding,expected", [
    ({"blockers": [], "p1s": ["correct citation lacks a regression guard"]}, True),
    ({"blockers": ["unsupported result"], "p1s": []}, False),
    ({"blockers": [], "p1s": [], "status": "open"}, False),
    ({"p1s": []}, False),
    ({"blockers": []}, False),
])
def test_recorded_outcome_distinguishes_maintenance_and_unfinished_review(recorder, finding, expected):
    seat = {"blind": True, "reviewed_commit": "abc", **finding}
    (recorder.SEATS_DIR / "PUB-X-abc-seat-evidence.json").write_text(json.dumps(seat))
    assert recorder.record_hardening("PUB-X", "abc", 1, None) == 0
    result = json.loads((recorder.HARDENING_DIR / "PUB-X.json").read_text())
    assert result["converged"] is expected
    assert result["p1s"] == finding.get("p1s", [])
    assert result["blockers"] == finding.get("blockers", [])


def test_no_review_is_not_converged(recorder):
    assert recorder.record_hardening("PUB-X", "abc", 1, None) == 0
    result = json.loads((recorder.HARDENING_DIR / "PUB-X.json").read_text())
    assert result["converged"] is False
    assert result["seats"] == []
