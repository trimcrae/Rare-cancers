"""Fleet reports preserve unpadded Eastern timestamps without GNU strftime flags."""
import datetime
import importlib

import pytest


@pytest.mark.parametrize("module", [
    "account_orphan_alarm", "work_ledger", "lane_staleness_watch", "alarm_state",
    "fleet_supervision_alarm", "assert_progress_fresh",
])
@pytest.mark.parametrize("utc,expected", [
    ("2026-07-02T04:00:00+00:00", "12:00 AM ET Jul 2, 2026"),
    ("2026-07-02T16:05:00+00:00", "12:05 PM ET Jul 2, 2026"),
    ("2026-07-22T13:00:00+00:00", "9:00 AM ET Jul 22, 2026"),
])
def test_portable_fleet_timestamp(module, utc, expected):
    assert importlib.import_module(module)._et(datetime.datetime.fromisoformat(utc)) == expected


def test_short_timestamps_preserve_minutes_and_missing_values():
    import job_progress_monitor as monitor
    import work_ledger as ledger
    ts = datetime.datetime.fromisoformat("2026-07-22T13:00:00+00:00")
    assert ledger._et_short(ts) == "9:00 AM ET"
    assert monitor._et("2026-07-22T13:00:00Z") == "9:00 AM ET"
    assert ledger._et_short(None) == "ETA unknown"
    assert ledger._et(None) is None
