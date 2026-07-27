"""The freshness gate must fail CLOSED — absence of evidence is never a pass.

Every test here is a case where something is wrong with the artifact and the gate must say so. That asymmetry
is the point: the gate exists because a monitoring tick that measured nothing still exited 0, so the only
bug that matters is the gate returning ok=True when it should not.
"""
import datetime
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import assert_progress_fresh as apf  # noqa: E402


NOW = datetime.datetime(2026, 7, 27, 13, 41, 0, tzinfo=datetime.timezone.utc)


def _write(tmp_path, payload):
    p = tmp_path / "step1-fanout-progress.json"
    p.write_text(json.dumps(payload) if not isinstance(payload, str) else payload)
    return str(p)


def _stamp(minutes_ago):
    return (NOW - datetime.timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_fresh_snapshot_passes(tmp_path):
    path = _write(tmp_path, {"_generated_utc": _stamp(0.5), "n_units": 19})
    ok, msg = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert ok, msg
    assert "re-measure" in msg


def test_the_exact_incident_is_caught(tmp_path):
    """45 minutes stale: the 8:56 AM artifact still being read at 9:41 AM with 18 GPUs billing."""
    path = _write(tmp_path, {"_generated_utc": _stamp(45), "n_units": 19})
    ok, msg = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert not ok
    assert "45.0 min old" in msg
    assert "did NOT refresh" in msg


def test_missing_timestamp_is_fatal_not_a_warning(tmp_path):
    """An artifact written by pre-fix code. Undatable == ungradable == fail; never a soft pass."""
    path = _write(tmp_path, {"n_units": 19, "_snapshot_point": "START of the tick"})
    ok, msg = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert not ok
    assert "_generated_utc" in msg


def test_missing_file_is_fatal(tmp_path):
    ok, msg = apf.check(str(tmp_path / "nope.json"), apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert not ok
    assert "DOES NOT EXIST" in msg


def test_unparseable_file_is_fatal(tmp_path):
    path = _write(tmp_path, "{not json")
    ok, msg = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert not ok
    assert "not parseable" in msg


def test_garbage_timestamp_is_fatal(tmp_path):
    path = _write(tmp_path, {"_generated_utc": "yesterday afternoon"})
    ok, msg = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert not ok
    assert "unverifiable" in msg


def test_future_timestamp_cannot_buy_freshness(tmp_path):
    """'Always fresh' is the one answer this gate must never give by accident."""
    path = _write(tmp_path, {"_generated_utc": _stamp(-30)})
    ok, msg = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert not ok
    assert "FUTURE" in msg


def test_small_clock_skew_is_tolerated(tmp_path):
    """Runner/host skew is real and small; it must not produce a spurious red."""
    path = _write(tmp_path, {"_generated_utc": _stamp(-1)})
    ok, _ = apf.check(path, apf.DEFAULT_MAX_AGE_MIN, now=NOW)
    assert ok


@pytest.mark.parametrize("age,ok_expected", [(9.0, True), (11.0, False)])
def test_window_boundary(tmp_path, age, ok_expected):
    path = _write(tmp_path, {"_generated_utc": _stamp(age)})
    ok, _ = apf.check(path, 10.0, now=NOW)
    assert ok is ok_expected


def test_main_exit_codes(tmp_path, capsys):
    good = _write(tmp_path, {"_generated_utc": _stamp(0.2)})
    assert apf.main([good]) == 0
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps({"_generated_utc": "2026-01-01T00:00:00Z"}))
    assert apf.main([str(stale)]) == 1
    assert "::error::" in capsys.readouterr().err


def test_the_writer_actually_stamps_the_field():
    """Contract test: the gate is only meaningful if mode_monitor emits the field it reads.

    Without this, someone renaming the key in congeneric_fanout_vast.py would leave a gate that fails every
    run, and the tempting fix would be to delete the gate rather than restore the field.
    """
    import inspect

    import congeneric_fanout_vast as cf

    src = inspect.getsource(cf.mode_monitor)
    assert '"_generated_utc": _utcnow()' in src
    assert '"_generated_et": _et_now()' in src
