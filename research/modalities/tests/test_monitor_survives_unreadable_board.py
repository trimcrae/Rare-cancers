"""A transient Vast read failure must cost the tick its BOARD VIEW, never its whole watch.

THE INCIDENT THIS PINS (2026-07-27, run 30288877243). At 1:21:48 PM ET the step-1 tick's `Progress check`
raised `RuntimeError: vast API GET /instances/ -> 403` and exited 1 at 1:22:20 PM. That step is the FIRST of
the tick's watch half, so GitHub skipped the freshness gate, the collect and the reap. `step1-fanout-progress.json`
stayed stamped 12:42 PM while eleven rentals kept billing and three stopped hosts went unadjudicated — the
lane's supervision was down for ~19 min and nothing said so.

THE BUG WAS A DEAD HANDLER, WHICH IS WHY A SOURCE TEST IS NOT ENOUGH. `mode_monitor` already carried a
carefully-argued `if live is None:` branch documented as covering "the API call failed". It could never fire
for that case: `_live_instances` RAISES, it does not return None. The comment described a safety property the
code did not have. So these tests exercise the behaviour rather than reading the prose back.

THE 403 IS AN EDGE VERDICT, NOT AN AUTHORISATION ONE — the body is nginx's HTML page, and at 1:22:14 PM, six
seconds BEFORE the tick gave up, `vast-watchdog` listed instances fine on the SAME key from a different
runner. Same key, same minute, opposite outcome: transient throttling, so surviving it is correct.

⚠ THE COMPLEMENTARY FAILURE IS WORSE AND IS TESTED TOO. "Survive" must not become "assume zero". A blind read
reported as `live_instances: 0` reads as "nothing is billing", and a false zero on a RENTAL board is the
version of this repo's most expensive defect class that actually costs money. It must be null, and nothing
may be destroyed on a read we did not get.
"""
from __future__ import annotations

import inspect
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class _StubS3:
    """Accepts the puts `mode_monitor` makes and answers every get as 'absent'."""

    def __init__(self):
        self.puts = []

    def put_object(self, **kw):
        self.puts.append(kw)
        return {}

    def get_object(self, **kw):
        raise RuntimeError("absent")

    def head_object(self, **kw):
        raise RuntimeError("absent")

    def list_objects_v2(self, **kw):
        return {}


def _run_monitor(monkeypatch, tmp_path, live_effect):
    """Run `mode_monitor` with S3 stubbed out and `_live_instances` doing `live_effect`."""
    import congeneric_fanout_vast as cfv

    monkeypatch.setenv("VAST_CKPT_BUCKET", "test-bucket")
    monkeypatch.setenv("VAST_API_KEY", "test-key")
    monkeypatch.setattr(cfv, "BUCKET", "test-bucket", raising=False)
    monkeypatch.setattr(cfv, "_s3", lambda: _StubS3())
    monkeypatch.setattr(cfv, "_live_instances", live_effect)
    # Everything below the board read reads S3; stub it to a consistent "nothing recorded yet".
    monkeypatch.setattr(cfv, "_get_json", lambda *a, **k: None)
    monkeypatch.setattr(cfv, "_get_text", lambda *a, **k: None)
    monkeypatch.setattr(cfv, "_exists", lambda *a, **k: False)
    monkeypatch.setattr(cfv, "committed_progress", lambda *a, **k: (-1, None))
    monkeypatch.chdir(tmp_path)
    cfv.mode_monitor()
    return json.loads((tmp_path / "step1-fanout-progress.json").read_text())


def test_a_transient_403_does_not_take_down_the_progress_check(monkeypatch, tmp_path, capsys):
    """The exact 1:21 PM failure: the board read raises, and the tick must still produce its readout."""
    def boom(_key):
        raise RuntimeError(
            "vast API GET /instances/ -> 403: <html><head><title>403 Forbidden</title></head>")

    snap = _run_monitor(monkeypatch, tmp_path, boom)

    # The artifact exists and is freshly stamped — which is precisely what the freshness gate downstream
    # asserts, and precisely what did not happen at 1:21 PM.
    assert snap["_generated_utc"], "the tick must still stamp a fresh measurement"
    out = capsys.readouterr().out
    assert "UNKNOWN" in out, "a blind board read must be reported as UNKNOWN"


def test_a_blind_read_is_recorded_as_NULL_and_never_as_a_measured_ZERO(monkeypatch, tmp_path):
    """Surviving the failure must not turn 'we could not ask' into 'nothing is billing'."""
    def boom(_key):
        raise RuntimeError("vast API GET /instances/ -> 403: <html>")

    snap = _run_monitor(monkeypatch, tmp_path, boom)

    assert snap["live_instances"] is None, (
        "a board we could not read must be null, never 0 — a false zero on a RENTAL board reads as "
        "'nothing is billing' and is the version of this defect class that costs money")
    assert snap["_vast_unreadable"], "the reason for the blindness must survive into the artifact"
    assert "403" in snap["_vast_unreadable"]


def test_a_readable_board_still_reports_its_real_count(monkeypatch, tmp_path):
    """The degradation must be scoped to failure — a good read is unchanged, null means only 'unknown'."""
    snap = _run_monitor(monkeypatch, tmp_path, lambda _key: [
        {"id": 1, "label": "s1f-00-x", "actual_status": "running", "cur_state": "running",
         "status_msg": "success", "gpu_name": "RTX 4090", "start_date": None},
    ])
    assert snap["live_instances"] == 1
    assert snap["_vast_unreadable"] is None


def test_nothing_is_ever_condemned_on_a_read_we_did_not_get():
    """Destroying a rental is irreversible, so it must require a board read that actually succeeded.

    Guarded at the source because the runtime safety is INCIDENTAL: on a blind read `live` is `[]`, so the
    adjudication loop iterates nothing today. Anyone seeding `live` from a cache would silently hand a
    destroy path a stale instance list, so the guard must be explicit and stay explicit.
    """
    import congeneric_fanout_vast as cfv
    src = inspect.getsource(cfv.mode_monitor)
    assert "if key and not unreadable:" in src, (
        "the stuck-start adjudication must be gated on a SUCCESSFUL board read — it destroys instances")


def test_the_launcher_still_fails_closed_because_it_spends_money():
    """The read-failure tolerance is scoped to the WATCH. `mode_launch` must keep propagating.

    This is the boundary that makes the change safe rather than a softening: never renting when you cannot
    see what you already hold is the one path by which this lane could really over-rent.
    """
    import congeneric_fanout_vast as cfv
    src = inspect.getsource(cfv.mode_launch)
    assert "live = _live_instances(key)" in src, (
        "mode_launch must call _live_instances bare so a failed read RAISES and no rental happens")
    assert "except" not in src.split("live = _live_instances(key)")[0][-400:], (
        "mode_launch must not have acquired a swallow around its board read")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
