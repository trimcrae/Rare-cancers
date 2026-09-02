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

def _held_state(**over):
    """A state carrying an ACTIVE, well-formed budget hold — CONSTRUCTED, never read.

    ⛔⛔ THE THIRD INSTANCE OF THE SAME DEFECT IN THIS FILE, AND THE FIRST TWO ARE WRITTEN UP TEN
    LINES APART BELOW (2026-09-02: the floor test and the stuck test both stopped deriving their
    fixtures from `live_state()` for exactly this reason). ⚠ MEASURED 2026-09-02: eight tests here
    were red on clean `origin/main` — every one of them a hold test that read the live hold, and
    every one red because the live hold is `active: false`, suspended for the sprint by the person
    who set it. `c_budget_recovering` then returns NO-BACKOFF before it ever consults a posture, so
    loosening a dial IS unnoticed, the assertion is correct, and the CODE IS FINE. The tests were
    measuring the posture of a coordination file rather than the behaviour of the guard.
    ★★ AND THE FALSE RED IS THE LESS DANGEROUS HALF, in the words this file already uses: a test
    that derives its fixture from a live artifact does not fail when the behaviour breaks — it
    fails, or PASSES, according to where the artifact happens to sit. Every one of these eight would
    have gone GREEN-WHILE-EXERCISING-NOTHING under a hold shaped slightly differently.
    ⭐ DRIVEN OFF `HOLD_POSTURE_DIALS`, so a dial added to the table gets a declared bound and a
    live value here automatically — the same property `test_every_posture_dial_is_actually_checked`
    already has, and the reason that test can keep asserting on `declared_posture[posture_key]`.
    Each live dial is set EXACTLY to its declared bound: honouring the hold, and one step away from
    violating it in either direction.
    """
    posture, dials = {}, {}
    for pkey, (skey, sense) in health.HOLD_POSTURE_DIALS.items():
        bound = 8 if sense == "min" else 4
        posture[pkey] = bound
        dials[skey] = bound
    state = {
        "backoff_level": 0,
        "backoff_since_utc": "2026-09-01T00:00:00Z",
        "budget_hold": {
            "active": True,
            "reason": "constructed-fixture (not a real hold — see _held_state)",
            "floor_backoff_level": 0,
            # ⛔ FAR ENOUGH OUT THAT THE REVIEW STAMP IS NOT THE THING UNDER TEST. A fixture whose
            # review window has already passed reds every case here as HOLD-NEEDS-A-FRESH-READING,
            # which is a different branch from the one each test names.
            "review_after_utc": "2099-01-01T00:00:00Z",
            "declared_posture": posture,
        },
    }
    state.update(dials)
    state.update(over)
    return state


def test_the_live_state_honours_its_own_hold():
    row = health.c_budget_recovering(live_state(), None, datetime.datetime.now(UTC))
    assert row["ok"], row["detail"]


@pytest.mark.parametrize("posture_key", sorted(health.HOLD_POSTURE_DIALS))
def test_every_posture_dial_is_actually_checked(posture_key):
    """⭐ SINGLE-SITE MUTATION, DRIVEN OFF THE TABLE. Add a dial to HOLD_POSTURE_DIALS and this test
    grows a case on its own; wire it to nothing and that case fails."""
    state_key, sense = health.HOLD_POSTURE_DIALS[posture_key]
    st = _held_state()
    bound = st["budget_hold"]["declared_posture"][posture_key]
    st[state_key] = bound - 1 if sense == "min" else bound + 1
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"], f"loosening `{state_key}` past its declared bound went unnoticed"
    assert row["verdict"] == "HOLD-NOT-IN-FORCE"


def test_a_posture_key_nothing_reads_is_red_not_silently_skipped():
    st = _held_state()
    st["budget_hold"]["declared_posture"]["max_something_invented"] = 1
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-NOT-IN-FORCE"


def test_a_live_dial_that_is_not_a_NUMBER_is_a_violation_not_a_pass():
    """⛔ A DIAL THE ROW CANNOT READ IS A HOLD THAT IS NOT IN FORCE (CLAUDE.md §4: an absent reading
    is not a reading of absence). `hold_posture_violations` says so in its own docstring — "a dial
    that is absent or non-numeric counts as a VIOLATION, not as a pass" — and nothing asserted it,
    so a mutation that turned that branch into `pass` survived every test in this file. The softer
    reading, "nothing to check, therefore fine", is how a guard becomes decoration.
    """
    for missing in (None, "12", True, [4]):
        st = _held_state()
        skey = health.HOLD_POSTURE_DIALS["max_subagent_width"][0]
        if missing is None:
            st.pop(skey)
        else:
            st[skey] = missing
        row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
        assert not row["ok"] and row["verdict"] == "HOLD-NOT-IN-FORCE", (
            f"`{skey}`={missing!r} is unreadable and was graded {row['verdict']!r}, not a violation")


def test_a_clean_cycle_may_not_decrement_through_the_hold_floor():
    """⛔ THE WHOLE REASON THE HOLD EXISTS. `backoff_level` is a FAILURE counter that a clean cycle
    LOWERS, so a level raised for budget reasons is undone by the first cycle that goes well.

    ⛔⛔ THE FIXTURE IS CONSTRUCTED, NOT DERIVED, AND THAT IS THE POINT (2026-09-02). This test used
    to read `st["backoff_level"] = st["budget_hold"]["floor_backoff_level"] - 1` off the LIVE state.
    When the sprint set `floor_backoff_level: 0` that expression became `-1`, which
    `c_budget_recovering` refuses as `LEVEL-UNREADABLE` before any floor comparison — correctly, at
    its own `level < 0` guard. So the test went red with the behaviour untouched.
    ★★ AND THE FALSE RED IS THE LESS DANGEROUS HALF. A test that derives its fixture from a live
    artifact does not fail when the behaviour breaks; it fails, or PASSES, according to where the
    artifact happens to sit. A differently-shaped live state would have let this assert green while
    exercising nothing. The floor property is a property of the code, so the posture that exercises
    it is built here.
    """
    st = _held_state()
    st["budget_hold"]["floor_backoff_level"] = 2
    st["backoff_level"] = 1
    # ⛔ THE DURATION IS READ BEFORE THE FLOOR IS, so this line is load-bearing. A raised level with
    # no `backoff_since_utc` returns BACKOFF-AGE-UNKNOWN and never reaches the floor comparison —
    # measured, and it is how the first draft of this very fix failed: a fixture that exercises a
    # different branch from the one the test's name claims.
    st["backoff_since_utc"] = "2026-09-01T00:00:00Z"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-FLOOR-BREACHED", (
        "a level below the hold's declared floor must be refused; got "
        f"{row['verdict']!r}")


def test_the_floor_is_breached_at_level_ZERO_too_and_that_is_the_worst_case():
    """⛔ ONE OF A PAIR, IN THE CODE THIS TIME. `c_budget_recovering` checks the hold floor TWICE —
    once inside the level-0 branch and once in the raised-level branch — and the two blocks are
    byte-identical. Every floor test above sets `backoff_level = 1`, so only the second copy was
    exercised: a single-site mutation that disabled the LEVEL-0 copy passed all 22 tests.
    ⭐ AND LEVEL 0 IS THE CASE THAT MATTERS MOST. The hold exists because `backoff_level` is a
    failure counter that a clean cycle LOWERS; a level that has been decremented all the way to 0
    through a floor of 2 is that decrement having run to completion, which is the exact event the
    floor was pinned to stop.
    """
    st = _held_state()
    st["budget_hold"]["floor_backoff_level"] = 2
    assert st["backoff_level"] == 0, "the fixture must be at level 0 for this to test what it says"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-FLOOR-BREACHED", (
        f"a level-0 breach of a floor of 2 was graded {row['verdict']!r}")


def test_a_negative_backoff_level_is_unreadable_rather_than_below_every_floor():
    """⭐ THE BRANCH THAT MASKED THE TEST ABOVE, NOW PINNED DELIBERATELY.

    A negative `backoff_level` is not "further below the floor" — it is not a reading at all, and
    `c_budget_recovering` must say UNMEASURED rather than manufacture a floor breach from it. This
    case was being exercised by accident, as the reason the floor test failed; an accident is not a
    test, so it gets one.
    """
    st = copy.deepcopy(live_state())
    st["budget_hold"]["floor_backoff_level"] = 2
    st["backoff_level"] = -1
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "LEVEL-UNREADABLE", (
        f"a negative level must be UNMEASURED, not a floor breach; got {row['verdict']!r}")


def test_the_hold_expires_into_a_review_never_into_full_cadence():
    st = _held_state()
    st["budget_hold"]["review_after_utc"] = "2026-08-01T00:00:00Z"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "HOLD-NEEDS-A-FRESH-READING"


def test_a_held_backoff_is_not_reported_as_stuck():
    """⚠ THE REGRESSION THIS EXTENSION EXISTS TO PREVENT. `budget_recovering`'s condition is entirely
    a DURATION, so before the hold was readable a deliberate multi-day hold went red at 24 h and
    stayed red — a permanent red on a governor doing exactly what it was told."""
    st = _held_state(backoff_since_utc="2026-08-01T00:00:00Z")
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert row["ok"] and row["verdict"] == "BUDGET-HELD"


def test_without_a_hold_the_old_stuck_reading_is_unchanged():
    """The extension must not have bought its green by weakening the row for everyone.

    ⛔ `backoff_level` IS SET HERE RATHER THAN INHERITED (2026-09-02, same defect as the floor test).
    The stuck reading is about a RAISED backoff that has not come down, so the fixture must carry
    one. Inheriting the live level meant that whenever the loop was healthy — level 0, which is the
    state this repository is in most of the time — the row was correctly green and the test read
    that green as a failure to be STUCK.
    """
    st = copy.deepcopy(live_state())
    st.pop("budget_hold")
    st["backoff_level"] = 1
    st["backoff_since_utc"] = "2026-08-01T00:00:00Z"
    row = health.c_budget_recovering(st, None, datetime.datetime.now(UTC))
    assert not row["ok"] and row["verdict"] == "STUCK", (
        f"a backoff raised since 2026-08-01 and never lowered is STUCK; got {row['verdict']!r}")
