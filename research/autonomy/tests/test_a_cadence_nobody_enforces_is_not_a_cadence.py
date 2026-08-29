"""⛔⛔ THE CADENCE AND THE HOLD, BOTH MEASURED — because both are numbers that lived in JSON.

Two guards are asserted here and they fail in the same way if unwired.

1. `cadence.py` — the loop's declared `cycle_interval_hours` governed nothing, because the thing
   that fires a cycle is a human-created Claude Routine an agent is refused permission to edit
   (measured 2026-08-29: both a cron change and `enabled: false` were rejected). The gate is the
   only place the declared cadence binds, so a gate that fails open on a case it should refuse is
   the whole feature missing.

2. `health.py`'s `budget_recovering` row, extended the same day to read `budget_hold`. A hold
   DECLARES a posture; without this the posture is `subagent_width` again — defined in JSON,
   asserted by one test, read by no code for a fortnight (CLAUDE.md §1).

⭐ EVERY POSTURE DIAL IS MUTATED SEPARATELY. The one-of-a-pair defect class that `paper-hardening`
records — a guard that catches three of four sites and is green anyway — is caught only by
single-site mutation, so `test_every_posture_dial_is_actually_checked` drives the list of dials off
`HOLD_POSTURE_DIALS` itself rather than repeating it, and fails if a dial is added and unchecked.
"""
from __future__ import annotations

import copy
import datetime
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUT = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(AUT))
sys.path.insert(0, AUT)

import cadence          # noqa: E402
import health           # noqa: E402

UTC = datetime.timezone.utc
STATE_PATH = os.path.join(AUT, "autonomy-state.json")


def live_state():
    with open(STATE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- the cadence gate

def _state(**over):
    base = {"cycle_interval_hours": 24, "last_cycle_started_utc": "2026-08-29T00:00:00Z"}
    base.update(over)
    return base


def _at(hours_after_midnight):
    return datetime.datetime(2026, 8, 29, tzinfo=UTC) + datetime.timedelta(hours=hours_after_midnight)


def test_a_fire_inside_the_interval_is_refused():
    code, msg, payload = cadence.check(_state(), now=_at(4))
    assert code == cadence.TOO_SOON, msg
    assert payload["next_eligible_et"], "a refusal must say when the next fire is eligible"


def test_a_fire_after_the_interval_is_allowed():
    code, _, _ = cadence.check(_state(), now=_at(24.5))
    assert code == cadence.MAY_START


def test_the_boundary_is_not_off_by_one_interval():
    """⚠ The one-sided error that would make this gate silently double the cadence."""
    assert cadence.check(_state(), now=_at(23.99))[0] == cadence.TOO_SOON
    assert cadence.check(_state(), now=_at(24.01))[0] == cadence.MAY_START


def test_a_longer_declared_interval_actually_refuses_for_longer():
    """⛔ THE DIAL MUST BE READ, NOT HARD-CODED. A gate that refuses on a constant would pass every
    test above while ignoring the number the governor moves."""
    assert cadence.check(_state(cycle_interval_hours=4), now=_at(6))[0] == cadence.MAY_START
    assert cadence.check(_state(cycle_interval_hours=24), now=_at(6))[0] == cadence.TOO_SOON


def test_no_prior_cycle_allows_rather_than_blocks(tmp_path):
    """An absent receipt is a genuine absence of a prior cycle, not a failed reading of one."""
    code, msg, _ = cadence.check({"cycle_interval_hours": 24}, now=_at(1),
                                 receipts_dir=str(tmp_path))
    assert code == cadence.MAY_START, msg


def test_an_unreadable_state_file_fails_open_rather_than_wedging(tmp_path, monkeypatch):
    """⛔ A GATE THAT CANNOT READ ITS OWN SETTING MUST NOT BECOME AN OUTAGE WITH A VIRTUOUS NAME —
    the failure health.py records for `blocks` rows that no future cycle could ever clear."""
    monkeypatch.setattr(cadence, "STATE", str(tmp_path / "missing.json"))
    assert cadence.check(None, now=_at(1))[0] == cadence.MAY_START


def test_a_cycle_that_cannot_be_dated_fails_CLOSED_only_while_held(tmp_path):
    """The single case that fails closed, and it must not fail closed without a hold."""
    (tmp_path / "CYC-9999.json").write_text("{}", encoding="utf-8")   # seen, not datable by git
    held = {"cycle_interval_hours": 24, "budget_hold": {"active": True}}
    free = {"cycle_interval_hours": 24}
    assert cadence.check(held, now=_at(1), receipts_dir=str(tmp_path))[0] == \
        cadence.UNDATABLE_UNDER_HOLD
    assert cadence.check(free, now=_at(1), receipts_dir=str(tmp_path))[0] == cadence.MAY_START


def test_mtime_is_never_the_clock(tmp_path):
    """⛔ A fresh `git clone` rewrites every mtime, so an ancient receipt would read as this minute's
    — health.py refuses mtime beside RECEIPT_TIME_KEYS and this module must refuse it identically."""
    src = os.path.join(AUT, "cadence.py")
    body = open(src, encoding="utf-8").read()
    assert "getmtime" not in body and "st_mtime" not in body, \
        "cadence.py reached for a file mtime; git committer time is the clone-stable clock"


def test_the_cli_exit_code_is_the_answer():
    """The skill's stop-condition table branches on the exit code, so it must be non-zero to refuse."""
    out = subprocess.run([sys.executable, os.path.join(AUT, "cadence.py"), "--check"],
                         capture_output=True, text=True, cwd=ROOT, timeout=60)
    assert out.returncode in (cadence.MAY_START, cadence.TOO_SOON,
                              cadence.UNDATABLE_UNDER_HOLD), out.stderr


def test_the_skill_actually_calls_the_gate():
    """⛔⛔ THE WIRING, ASSERTED. The driver Routine's prompt cannot be edited by an agent, so the
    skill is the ONLY place this gate can be invoked from. A gate no procedure calls is the
    `subagent_width` shape exactly: correct, tested and dead."""
    skill = os.path.join(ROOT, ".claude", "skills", "research-loop", "SKILL.md")
    body = open(skill, encoding="utf-8").read()
    assert "cadence.py --check" in body, \
        "research-loop's contract never runs the cadence gate, so the cadence binds nowhere"


# --------------------------------------------------------------------------- the budget hold

def test_the_live_state_honours_its_own_hold():
    row = health.c_budget_recovering(live_state(), None, datetime.datetime.now(UTC))
    assert row["ok"], row["detail"]


@pytest.mark.parametrize("posture_key", sorted(health.HOLD_POSTURE_DIALS))
def test_every_posture_dial_is_actually_checked(posture_key):
    """⭐ SINGLE-SITE MUTATION, DRIVEN OFF THE TABLE. Add a dial to HOLD_POSTURE_DIALS and this test
    grows a case on its own; wire it to nothing and that case fails."""
    state_key, sense = health.HOLD_POSTURE_DIALS[posture_key]
    st = copy.deepcopy(live_state())
    bound = st["budget_hold"]["declared_posture"][posture_key]
    st[state_key] = bound - 1 if sense == "min" else bound + 1
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"], f"loosening `{state_key}` past its declared bound went unnoticed"
    assert row["verdict"] == "HOLD-NOT-IN-FORCE"


def test_a_posture_key_nothing_reads_is_red_not_silently_skipped():
    st = copy.deepcopy(live_state())
    st["budget_hold"]["declared_posture"]["max_something_invented"] = 1
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-NOT-IN-FORCE"


def test_a_clean_cycle_may_not_decrement_through_the_hold_floor():
    """⛔ THE WHOLE REASON THE HOLD EXISTS. `backoff_level` is a FAILURE counter that a clean cycle
    LOWERS, so a level raised for budget reasons is undone by the first cycle that goes well."""
    st = copy.deepcopy(live_state())
    st["backoff_level"] = st["budget_hold"]["floor_backoff_level"] - 1
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-FLOOR-BREACHED"


def test_the_hold_expires_into_a_review_never_into_full_cadence():
    st = copy.deepcopy(live_state())
    st["budget_hold"]["review_after_utc"] = "2026-08-01T00:00:00Z"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-NEEDS-A-FRESH-READING"


def test_a_held_backoff_is_not_reported_as_stuck():
    """⚠ THE REGRESSION THIS EXTENSION EXISTS TO PREVENT. `budget_recovering`'s condition is entirely
    a DURATION, so before the hold was readable a deliberate multi-day hold went red at 24 h and
    stayed red — a permanent red on a governor doing exactly what it was told."""
    st = copy.deepcopy(live_state())
    st["backoff_since_utc"] = "2026-08-01T00:00:00Z"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert row["ok"] and row["verdict"] == "BUDGET-HELD"


def test_without_a_hold_the_old_stuck_reading_is_unchanged():
    """The extension must not have bought its green by weakening the row for everyone."""
    st = copy.deepcopy(live_state())
    st.pop("budget_hold")
    st["backoff_since_utc"] = "2026-08-01T00:00:00Z"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "STUCK"
