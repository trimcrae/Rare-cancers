"""The pull board replaces a push channel, so it has to answer the questions the push channel answered.

An issue that appeared on your phone told you three things for free: that something was wrong, when it
started, and — by being closed — that it had cleared. A file has to say all of that ON THE PAGE, plus the
one thing the issue could not: whether anyone is still looking. These tests pin exactly that, and pin the
two ways a board like this quietly lies — a row that vanishes reading as a row that cleared, and a staleness
window that was typed rather than derived.
"""
from __future__ import annotations

import datetime
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import alarm_state as st  # noqa: E402

NOW = datetime.datetime(2026, 7, 31, 16, 0, 0, tzinfo=datetime.timezone.utc)   # 12:00 PM ET


def _fleet(verdict="FAILING", ok=False, runs_readable=True, detail="the tick ran and measured nothing"):
    return {"verdict": verdict, "ok": ok, "detail": detail, "runs_readable": runs_readable,
            "artifact_age_min": 300.0, "live_instances": 16, "realised_usd_so_far": 68.98}


def _lanes(*rows):
    return {"lanes": [{"lane": k, "verdict": v, "ok": o, "detail": d, "label": k} for k, v, o, d in rows]}


def _ledger(tmp_path, tick=16.0):
    p = tmp_path / "work-ledger.json"
    p.write_text(json.dumps({"_expected_tick_min": tick}))
    return str(p)


def _build(conditions, previous=None, now=NOW, ledger=None):
    return st.build(previous, conditions, now, ledger_path=ledger or "/nonexistent/work-ledger.json")


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · THE VERDICT IS RECORDED FAITHFULLY — the board re-derives nothing
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_failing_fleet_verdict_is_recorded_verbatim_and_flagged():
    b = _build(st.conditions_from_fleet_verdict(_fleet()))
    c = b["conditions"][0]
    assert c["key"] == "fleet-supervision" and c["verdict"] == "FAILING" and c["ok"] is False
    assert c["needs_attention"] is True
    assert c["detail"] == "the tick ran and measured nothing"
    assert b["ok"] is False and b["needs_attention"] == ["fleet-supervision"]


def test_the_payload_carries_the_numbers_a_reader_needs_without_running_anything():
    c = _build(st.conditions_from_fleet_verdict(_fleet()))["conditions"][0]
    assert c["payload"]["live_instances"] == 16
    assert c["payload"]["realised_usd_so_far"] == 68.98


def test_healthy_lanes_are_recorded_too():
    """On a pull board a green row is the ONLY way to tell 'watched and fine' from 'not watched at all' —
    which is the entire distinction the supervision work exists around."""
    b = _build(st.conditions_from_lane_report(_lanes(("a", "ADVANCING", True, "x"),
                                                     ("b", "IDLE-UNEXPECTED", False, "y"))))
    assert {c["key"] for c in b["conditions"]} == {"lane:a", "lane:b"}
    assert b["needs_attention"] == ["lane:b"]
    assert b["ok"] is False


def test_an_all_green_board_says_so_and_lists_nothing():
    b = _build(st.conditions_from_lane_report(_lanes(("a", "ADVANCING", True, "x"))))
    assert b["ok"] is True and b["needs_attention"] == [] and b["n_conditions"] == 1


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · UNMEASURED IS NOT THE SAME AS BAD, AND NEITHER IS IT THE SAME AS FINE
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_an_unreadable_api_verdict_is_listed_as_unmeasured_not_as_an_outage():
    """★ 2026-07-27, 4:18 PM ET: an unreadable Actions API was announced as FLEET UNSUPERVISED [ABSENT] over
    a 3-minute-old artifact inside a green tick. On a board that lands in `needs_attention`, it would send
    the reader chasing an outage that never happened."""
    b = _build(st.conditions_from_fleet_verdict(
        _fleet("STALE-CAUSE-UNKNOWN", ok=False, runs_readable=False)))
    c = b["conditions"][0]
    assert c["unmeasured"] is True and c["needs_attention"] is False
    assert b["needs_attention"] == [] and b["unmeasured"] == ["fleet-supervision"]
    assert b["ok"] is True, "an unanswered question must not by itself make the board red"


def test_a_lane_UNKNOWN_is_unmeasured():
    b = _build(st.conditions_from_lane_report(_lanes(("z", "UNKNOWN", False, "state unreadable"))))
    assert b["unmeasured"] == ["lane:z"] and b["needs_attention"] == []


def test_a_measured_stale_verdict_IS_an_outage():
    """The same verdict name with the API readable is a real 4h+ stale artifact, and must not be muted."""
    b = _build(st.conditions_from_fleet_verdict(
        _fleet("STALE-CAUSE-UNKNOWN", ok=False, runs_readable=True)))
    assert b["needs_attention"] == ["fleet-supervision"] and b["ok"] is False


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · HISTORY — the thing a snapshot cannot answer: "has this been red all night?"
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_condition_that_stays_bad_accumulates_how_long_and_how_many_runs():
    b1 = _build(st.conditions_from_fleet_verdict(_fleet()))
    later = NOW + datetime.timedelta(minutes=48)
    b2 = st.build(b1, st.conditions_from_fleet_verdict(_fleet()), later,
                  ledger_path="/nonexistent/work-ledger.json")
    c = b2["conditions"][0]
    assert c["consecutive_bad_runs"] == 2
    assert c["bad_since_utc"] == "2026-07-31T16:00:00Z"
    assert c["bad_for_min"] == 48.0


def test_recovery_clears_the_history_so_the_next_incident_starts_clean():
    b1 = _build(st.conditions_from_fleet_verdict(_fleet()))
    b2 = st.build(b1, st.conditions_from_fleet_verdict(_fleet("FRESH", ok=True, detail="measured")), NOW,
                  ledger_path="/nonexistent/work-ledger.json")
    c = b2["conditions"][0]
    assert c["ok"] is True and c["consecutive_bad_runs"] == 0 and c["bad_since_utc"] is None
    assert b2["ok"] is True and b2["needs_attention"] == []


def test_a_verdict_change_is_stamped():
    b1 = _build(st.conditions_from_fleet_verdict(_fleet("FAILING")))
    later = NOW + datetime.timedelta(minutes=20)
    b2 = st.build(b1, st.conditions_from_fleet_verdict(_fleet("ABSENT")), later,
                  ledger_path="/nonexistent/work-ledger.json")
    assert b2["conditions"][0]["last_change_utc"] == "2026-07-31T16:20:00Z"


def test_a_row_whose_SOURCE_stopped_reporting_is_carried_over_marked_NOT_dropped():
    """★ THE QUIET LIE THIS BOARD COULD TELL. If a producing step dies it supplies no rows; dropping its
    keys would render 'we stopped checking' identically to 'it cleared' — the measured-zero defect, which is
    the most expensive class of bug in this repo."""
    b1 = _build(st.conditions_from_lane_report(_lanes(("a", "IDLE-UNEXPECTED", False, "dead"))))
    # next run: only the FLEET source reported; the lane source produced nothing at all
    b2 = st.build(b1, st.conditions_from_fleet_verdict(_fleet("FRESH", ok=True)), NOW,
                  ledger_path="/nonexistent/work-ledger.json")
    carried = [c for c in b2["conditions"] if c["key"] == "lane:a"]
    assert carried, "a lane whose source stopped reporting vanished from the board"
    assert carried[0]["stale_carried_over"] is True
    assert carried[0]["unmeasured"] is True and carried[0]["needs_attention"] is False
    assert "NOT RE-MEASURED" in carried[0]["detail"]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 4 · THE ARTIFACT CARRIES ITS OWN EXPIRY, AND THE WINDOW IS DERIVED
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_staleness_window_is_READ_from_the_work_ledger_not_typed_here(tmp_path):
    """CLAUDE.md §1: the cadence has one home — `work_ledger.EXPECTED_TICK_MIN`, published into every
    work-ledger.json. A board that typed its own copy would drift the moment the supervisor's inputs change."""
    b = _build(st.conditions_from_fleet_verdict(_fleet()), ledger=_ledger(tmp_path, tick=16.0))
    assert b["_expected_tick_min"] == 16.0
    assert "work-ledger.json" in b["_stale_window_basis"] and "Not typed here" in b["_stale_window_basis"]
    assert b["_stale_after_utc"] == "2026-07-31T16:48:00Z"   # 16 min x 3 missed ticks


def test_a_changed_cadence_moves_the_deadline_with_no_edit_here(tmp_path):
    b = _build(st.conditions_from_fleet_verdict(_fleet()), ledger=_ledger(tmp_path, tick=30.0))
    assert b["_expected_tick_min"] == 30.0
    assert b["_stale_after_utc"] == "2026-07-31T17:30:00Z"


def test_an_unreadable_ledger_ADMITS_the_window_is_not_derived(tmp_path):
    """⚠ A number that looks derived and is not is worse than an admitted guess. Measured cost of getting
    this wrong: the issue that fired at 11:38 AM ET read 'the artifact is 8 min old, past the 1 min window'
    over an artifact that only refreshes on the ~16 min collect cadence."""
    b = _build(st.conditions_from_fleet_verdict(_fleet()), ledger=str(tmp_path / "absent.json"))
    assert b["_expected_tick_min"] == st.FALLBACK_TICK_MIN
    assert "NOT DERIVED" in b["_stale_window_basis"]


def test_the_board_tells_a_reader_it_is_dead_without_running_anything():
    """The whole point of the pull channel: a supervision chain that has stopped cannot report that it
    stopped, so the deadline is written INTO the artifact."""
    b = _build(st.conditions_from_fleet_verdict(_fleet("FRESH", ok=True)))
    for k in ("_generated_utc", "_generated_et", "_stale_after_utc", "_stale_after_et", "_stale_after_means"):
        assert b.get(k), f"missing {k}"
    assert "NOTHING IS WATCHING" in b["_stale_after_means"]
    late = st._parse_z(b["_stale_after_utc"]) + datetime.timedelta(minutes=1)
    assert "NOTHING IS WATCHING" in st.render(b, late)
    assert "NOTHING IS WATCHING" not in st.render(b, NOW)


def test_the_board_states_that_it_is_pull_only():
    b = _build(st.conditions_from_fleet_verdict(_fleet()))
    assert "should not be emailing me" in b["_this_channel_is_PULL_ONLY"]
    assert "PULL ONLY" in st.render(b, NOW)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 5 · THE CLI CANNOT BECOME A NOTIFICATION BY FAILING
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_it_exits_zero_even_when_everything_is_wrong(tmp_path, capsys):
    """⚠ A non-zero exit fails the run, and a failed SCHEDULED run emails the repo owner. A recorder that
    exits non-zero would silently reinstate the push channel it replaced."""
    v = tmp_path / "v.json"
    v.write_text(json.dumps(_fleet("FAILING")))
    rc = st.main(["--fleet-verdict", str(v), "--state", str(tmp_path / "board.json"),
                  "--ledger", str(tmp_path / "absent.json"), "--write"])
    assert rc == 0
    assert "need attention" in capsys.readouterr().out


def test_a_missing_source_file_is_recorded_not_raised(tmp_path, capsys):
    rc = st.main(["--fleet-verdict", str(tmp_path / "nope.json"), "--state", str(tmp_path / "b.json"),
                  "--write"])
    assert rc == 0
    board = json.loads((tmp_path / "b.json").read_text())
    assert board["_sources_unreadable"], "a step that produced no verdict must be recorded, not ignored"
    assert "source unreadable" in capsys.readouterr().out


def test_the_written_board_round_trips_and_is_the_history_store(tmp_path):
    v = tmp_path / "v.json"
    v.write_text(json.dumps(_fleet("FAILING")))
    state, ledger = str(tmp_path / "board.json"), _ledger(tmp_path)
    st.main(["--fleet-verdict", str(v), "--state", state, "--ledger", ledger, "--write"])
    st.main(["--fleet-verdict", str(v), "--state", state, "--ledger", ledger, "--write"])
    board = json.loads(open(state).read())
    assert board["conditions"][0]["consecutive_bad_runs"] == 2, \
        "history must survive in the artifact — there is no side store by design"


def test_without_write_nothing_is_persisted(tmp_path):
    v = tmp_path / "v.json"
    v.write_text(json.dumps(_fleet()))
    state = tmp_path / "board.json"
    assert st.main(["--fleet-verdict", str(v), "--state", str(state)]) == 0
    assert not state.exists()
