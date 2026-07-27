"""The alarm's whole value is that it SEPARATES 'nobody ran the tick' from 'the tick ran and broke'.

Both leave an identical stale artifact, which is why the 2026-07-27 incident was unreadable for ~1h45m. So
the tests are mostly about the verdict being the RIGHT one, not merely non-green.
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fleet_supervision_alarm as fsa  # noqa: E402

NOW = datetime.datetime(2026, 7, 27, 16, 1, 0, tzinfo=datetime.timezone.utc)   # 12:01 PM ET


def _prog(minutes_old, **kw):
    gen = NOW - datetime.timedelta(minutes=minutes_old)
    d = {"_generated_utc": gen.strftime("%Y-%m-%dT%H:%M:%SZ"), "live_instances": 16}
    d.update(kw)
    return d


def _run(minutes_ago, event="schedule", conclusion="success"):
    t = NOW - datetime.timedelta(minutes=minutes_ago)
    return {"run_started_at": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "event": event, "conclusion": conclusion}


def _c(progress, runs, stale=240.0, absent=240.0):
    return fsa.classify(progress, runs, NOW, stale, absent)


def test_a_recently_measured_fleet_is_green():
    """The run started 8 min ago and the artifact is stamped 5 min ago: it measured during that run."""
    v = _c(_prog(5), [_run(8)])
    assert v["ok"] is True and v["verdict"] == "FRESH"


def test_an_old_artifact_is_FRESH_if_the_last_run_is_the_one_that_wrote_it():
    """Throttle honesty: 200 min between scheduled ticks is NORMAL here, so a 200-min-old artifact written by
    the last completed run is not an incident and must not page anyone."""
    v = _c(_prog(200), [_run(205)])
    assert v["ok"] is True and v["verdict"] == "FRESH"


def test_no_runs_at_all_is_ABSENT_not_FAILING():
    """The scheduler stopped delivering. Fixing the tick's code would be the wrong response, so the verdict
    must not point there."""
    v = _c(_prog(300), [])
    assert v["ok"] is False and v["verdict"] == "ABSENT"
    assert "SCHEDULER" in v["detail"]


def test_THE_REAL_INCIDENT_a_failing_run_over_a_only_mildly_stale_artifact_fires():
    """★ THE REGRESSION TEST FOR 2026-07-27. At 12:01 PM ET the artifact was 115 min old — INSIDE any
    throttle-honest age window — while a run had started 24 min earlier and died on its first step. An
    age-threshold alarm says FRESH here and the fleet stays unsupervised. The comparison must fire."""
    v = _c(_prog(115), [_run(24, event="workflow_dispatch", conclusion="failure")])
    assert v["ok"] is False and v["verdict"] == "FAILING"
    assert "CODE is broken" in v["detail"]


def test_that_incident_would_NOT_be_caught_by_age_alone():
    """Stated as a test so nobody later 'simplifies' this back into an age check."""
    assert 115 < fsa.DEFAULT_STALE_MIN


def test_a_run_that_goes_GREEN_without_measuring_is_its_own_verdict():
    """The defect assert_progress_fresh.py was written for; if it reappears the alarm must name it rather
    than blaming the scheduler."""
    v = _c(_prog(60), [_run(10, conclusion="success")])
    assert v["verdict"] == "STALE-BUT-RUNS-GREEN" and v["ok"] is False


def test_an_in_progress_run_is_not_counted_against_the_artifact():
    """A tick writes its artifact mid-run. Counting a still-running tick as 'did not refresh' would make the
    alarm fire on every tick's first seconds."""
    v = _c(_prog(200), [_run(205, conclusion="success"), _run(1, conclusion=None)])
    assert v["ok"] is True and v["verdict"] == "FRESH"


def test_unreadable_actions_api_is_NOT_reported_as_a_dead_scheduler():
    """`None` means 'could not ask'. Reporting it as 'no runs' would turn a network blip into a false ABSENT
    — the measured-zero defect class this repo keeps paying for."""
    v = _c(_prog(300), None)
    assert v["verdict"] == "STALE-CAUSE-UNKNOWN" and v["ok"] is False


def test_a_missing_or_undatable_artifact_is_fatal_never_a_pass():
    for p in (None, {}, {"_generated_utc": "not-a-timestamp"}):
        v = _c(p, [_run(5)])
        assert v["ok"] is False and v["verdict"] == "NO-ARTIFACT"


def test_the_threshold_is_looser_than_the_worst_measured_delivery_gap():
    """Measured scheduled delivery on 2026-07-27 was 141-238 min. A threshold at or under that is red
    permanently through no fault of the tick, and an always-red alarm is not an alarm."""
    assert fsa.DEFAULT_STALE_MIN > 238
    assert fsa.DEFAULT_ABSENT_MIN > 238


def test_it_reports_the_delivery_gaps_so_the_stale_55_65_min_claim_cannot_be_requoted():
    """Both workflows' comments still claim GitHub lands them '~55-65 min apart'. That was 2026-07-26. The
    alarm prints what delivery ACTUALLY was, so the number is measured on every run instead of remembered."""
    runs = [_run(600), _run(400), _run(180), _run(20)]
    v = _c(_prog(5), runs)
    assert v["scheduled_delivery_gaps_min"] == [200, 220, 160]


def test_it_never_imports_the_fanout_lane():
    """The alarm must not be takeable-down by the thing it watches — today's tick died on a cost-model unit
    test, and an alarm sharing that import would have died with it."""
    src = open(os.path.join(os.path.dirname(__file__), "..", "fleet_supervision_alarm.py")).read()
    for forbidden in ("import boto3", "congeneric_fanout", "gpu_backend", "import yaml", "vast_cost_model"):
        assert forbidden not in src, forbidden


def test_it_rents_prices_and_destroys_nothing():
    """Recovery belongs to the tick and the watchdog, which hold the credentials. An alarm that can act is an
    alarm that can act WRONGLY while unsupervised."""
    src = open(os.path.join(os.path.dirname(__file__), "..", "fleet_supervision_alarm.py")).read()
    for forbidden in ("DELETE", "_vast_request", "create_instance", "destroy", "VAST_API_KEY"):
        assert forbidden not in src, forbidden
