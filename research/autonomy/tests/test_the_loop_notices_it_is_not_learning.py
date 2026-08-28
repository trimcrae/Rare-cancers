"""A loop that only ever closes its own process defects is sampling one region of its portfolio.

⛔⛔ THE CLAIM THIS PINS survived 3-0 adversarial refutation in the 2026-08-27 `/deep-research` pass,
which was told to break it: **no verified system detects "running but no longer learning."** PanDA
measures file mtime; Kubernetes probes and phi accrual are progress-blind by construction.

★★ AND THE TEST THAT MATTERS MOST IS `test_counting_closures_alone_would_have_called_the_incident_healthy`.
Measured against CYC-0033…CYC-0041: those nine cycles closed SIX ledger rows, so a naive "did
anything close?" detector grades them healthy. Five of the six served RT-AUTONOMY. The signal is the
DISTRIBUTION, borrowed from ORNL's published fault diagnostic — read the sampling trajectory, not the
sample count.

⚠ SELF-MAINTENANCE IS NOT GRADED AS A DEFECT and no test here asserts that it is. Fixing the loop is
real work. What is reported is that a window contained ONLY that.
"""

from __future__ import annotations

import datetime
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import learning_rate as L  # noqa: E402
import stuck_clock  # noqa: E402

T0 = datetime.datetime(2026, 8, 28, 8, 0, tzinfo=datetime.timezone.utc)


def _v(n, rows):
    return stuck_clock.Version(sha=f"sha{n}", when=T0 + datetime.timedelta(hours=n), rows=rows)


def _row(state, route="RT-ASO"):
    return {"state": state, "serves": {"route": route}}


def test_a_closure_is_a_transition_not_a_state():
    """⛔ A row already `done` before the window is not a closure in it. Counting states would make a
    finished backlog read as permanent progress — 'presence is not provenance' (CLAUDE.md §4)."""
    versions = [_v(0, {"A": _row("done")}), _v(1, {"A": _row("done")})]
    assert L.closures(versions) == []


def test_a_row_that_closes_is_counted_once_with_its_route():
    versions = [_v(0, {"A": _row("queued", "RT-ATR")}), _v(1, {"A": _row("done", "RT-ATR")})]
    got = L.closures(versions)
    assert [(i, r) for i, r, _ in got] == [("A", "RT-ATR")]


def test_counting_closures_alone_would_have_called_the_incident_healthy():
    """⭐⭐ THE INCIDENT, REPRODUCED. Six closures — a naive detector says healthy. Five serve the
    loop's own route, and THAT is the finding."""
    before = {f"P{i}": _row("queued", "RT-AUTONOMY") for i in range(5)}
    before["S"] = _row("queued", "RT-PARTNER-STRAT")
    after = {f"P{i}": _row("done", "RT-AUTONOMY") for i in range(5)}
    after["S"] = _row("done", "RT-PARTNER-STRAT")
    got = L.closures([_v(0, before), _v(1, after)])
    assert len(got) == 6, "the naive count is six and a count-only detector stops here"
    import collections
    by = collections.Counter(r for _, r, _ in got)
    code, why = L._verdict(6, by, by["RT-AUTONOMY"] / 6, censored=False)
    assert code == "CONCENTRATED", f"the distribution was not read: {code} — {why}"
    assert "83%" in why or "5 of 6" in why


def test_a_window_with_only_self_route_closures_is_named():
    import collections
    by = collections.Counter({"RT-AUTONOMY": 3})
    code, why = L._verdict(3, by, 1.0, censored=False)
    assert code == "SELF-MAINTAINING"
    assert "Not a defect" in why, "self-maintenance must not be graded as a defect"


def test_an_empty_window_is_not_learning():
    import collections
    code, why = L._verdict(0, collections.Counter(), 0.0, censored=False)
    assert code == "NOT-LEARNING"
    assert "ARIS" in why or "empty rounds" in why


def test_a_healthy_spread_is_learning():
    import collections
    by = collections.Counter({"RT-ASO": 3, "RT-ATR": 2, "RT-AUTONOMY": 1})
    code, _ = L._verdict(6, by, 1 / 6, censored=False)
    assert code == "LEARNING"


def test_one_honest_closure_on_one_route_is_not_flagged():
    """⚠ THE FALSE POSITIVE THAT WOULD GET THIS TURNED OFF. A small cycle closing one thing on one
    research route is normal; only a run of at least four with a 75% concentration is a trajectory."""
    import collections
    for n in (1, 2):
        by = collections.Counter({"RT-AUTONOMY": n})
        by["RT-ASO"] = 1
        code, _ = L._verdict(n + 1, by, n / (n + 1), censored=False)
        assert code == "LEARNING", f"{n} self-closures plus one research closure was flagged"


def test_the_boundary_is_deliberate_and_is_asserted_rather_than_left_to_drift():
    """⚠ WRITTEN AFTER THE TEST ABOVE FAILED, AND THE CODE WAS RIGHT. The first version of that test
    asserted 3 self-closures plus 1 research closure should pass — but that is 75% of a four-closure
    window on the loop's own machinery, which is exactly what CONCENTRATED is for. The floor is
    `total >= 4` AND `self_share >= 0.75`: below four closures a window is too small to be a
    trajectory, and at four the concentration has to be three-quarters. Both halves are pinned here
    so a future edit that loosens either is a failing test rather than a quiet widening."""
    import collections
    just_under = collections.Counter({"RT-AUTONOMY": 2, "RT-ASO": 1})
    assert L._verdict(3, just_under, 2 / 3, censored=False)[0] == "LEARNING", \
        "a three-closure window was graded a trajectory"
    at_the_line = collections.Counter({"RT-AUTONOMY": 3, "RT-ASO": 1})
    assert L._verdict(4, at_the_line, 0.75, censored=False)[0] == "CONCENTRATED", \
        "three of four closures on the loop's own route is the signal, not noise"


def test_a_shallow_horizon_inside_the_window_refuses_to_grade():
    """⛔ Refusing to grade is the direction that does not invent a finding."""
    code, why = L._verdict(0, {}, 0.0, censored=True)
    assert code == "CENSORED" and "unreadable" in why


def test_a_shallow_horizon_OUTSIDE_the_window_still_grades(monkeypatch):
    """⚠ Measured 2026-08-28: the blanket shallow rule returned CENSORED over 40 readable closures
    across 14 routes. A tool that can never answer is not a cautious tool."""
    versions = [_v(0, {"A": _row("queued")}), _v(1, {"A": _row("done")})]
    monkeypatch.setattr(stuck_clock, "ledger_versions", lambda *a, **k: versions)
    monkeypatch.setattr(stuck_clock, "is_shallow", lambda *a, **k: True)
    monkeypatch.setattr(L, "window_hours", lambda **k: 0.5)
    rep = L.report(hours=0.5)
    assert rep["verdict"][0] != "CENSORED", "a horizon older than the window still censored the grade"


def test_the_thresholds_are_arias_borrowed_numbers():
    assert (L.CHANGE_DIRECTION_AFTER, L.CALL_A_HUMAN_AFTER) == (2, 4)


def test_the_window_is_derived_from_the_governor_not_typed():
    """One fact one place: the cadence lives in autonomy-state.json and is read, never restated."""
    import inspect
    src = inspect.getsource(L.window_hours)
    assert "cycle_interval_hours" in src
