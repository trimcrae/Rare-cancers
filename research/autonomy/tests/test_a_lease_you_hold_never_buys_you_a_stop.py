#!/usr/bin/env python3
"""AUT-PD-140 — the stall of 2026-08-28, and the arithmetic that hid it.

⛔⛔ WHAT HAPPENED. A session finished one cycle, claimed `AUT-PD-132` for its second, wrote no code
and stopped. The `Stop` hook built for exactly that moment stayed silent, and it was silent for a
reason that reads as correct: `continuity.py --check` returned 0 because the loop was AT CAPACITY —
five leases against a governed `subagent_width` of 5. The fifth lease was the claim the stopping
session had just made. It was waiting for itself.

★ THE FIX IS ONE SENTENCE — a worker is never blocked by itself — and these tests hold both halves
of it. Your own cycle's lease is not a worker you are waiting for. A seat you dispatched, and any
other session's cycle, still is: the capacity reading was right about those and is unchanged.

⛔ AND THE SECOND HALF IS THE ONE THAT GENERALISES BEYOND THIS FILE. The at-capacity branch printed
"THIS IS NOT PERMISSION TO STOP WORKING" and then returned 0. Inside a `Stop` hook only the exit code
is ever read — the hook exits on the code before it prints a line of that text — so the prose was a
caveat delivered to nobody. `test_no_output_demands_work_while_the_exit_code_permits_stopping` asserts
the two halves agree, for every state, forever.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import continuity as C  # noqa: E402

SESSION = "c84c64dd-64ab-5333-a9ee-09837d80ad76"
MINE = "CYC-0070-c84c64dd"          # this session's own cycle
SEAT = "SEAT-s1-c84c64dd"           # a worker THIS session dispatched — a different worker
OTHERS = ["CYC-0069-8226e21b", "SEAT-s1-1f1a2449", "SEAT-s2-1f1a2449", "SEAT-s3-1f1a2449"]

#: Phrases that tell the reader work is theirs to do right now. If one is printed, exiting 0 makes
#: the tool contradict itself in the only channel a Stop hook reads.
DEMANDS_WORK = ("NOT PERMISSION TO STOP", "YOU ARE THE WORKER", "READY AND NOT MOVING")


def _item(**kw):
    base = {"id": "AUT-X", "state": "queued", "owner": None, "blocked_by": None,
            "cost_class": "free", "score": 10.0, "what": "a free, ready, unblocked thing"}
    base.update(kw)
    return base


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A ledger, a width dial, and a session identity — the three inputs the verdict reads."""
    def install(entries, width=5, session=SESSION):
        led = tmp_path / "research-ledger.json"
        led.write_text(json.dumps({"entries": entries}), encoding="utf-8")
        monkeypatch.setattr(C, "LEDGER", str(led))
        state = tmp_path / "autonomy-state.json"
        state.write_text(json.dumps({"subagent_width": width}), encoding="utf-8")
        monkeypatch.setattr(C, "STATE", str(state))
        if session is None:
            monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
        else:
            monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", session)
    return install


def _held(owner, n):
    return [_item(id=f"{owner}-held-{i}", state="in_progress", owner=owner) for i in range(n)]


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE REGRESSION, in the shape it actually occurred.
# ---------------------------------------------------------------------------------------------

def test_your_own_claim_does_not_fill_the_cap_that_excuses_you(world, capsys):
    """⛔⛔ THE BUG, VERBATIM: four other workers, a cap of 5, and your own fresh claim making five.

    Before the fix this returned 0 and the Stop hook printed nothing. The session stopped with a
    claimed row untouched for 39 minutes and trimcrae was the one who noticed.
    """
    world([_item(id="READY")] + [_item(id="H", state="in_progress", owner=o) for o in OTHERS]
          + [_item(id="MINE", state="in_progress", owner=MINE)])
    rc = C.main(["--check"])
    out = capsys.readouterr().out
    assert rc == 1, ("your own lease filled the cap and bought you a stop — the session was waiting "
                     "for itself, which is the 2026-08-28 stall exactly")
    assert "YOU ARE THE WORKER" in out
    assert "MINE" in out, "the row you hold must be named, so the ending is falsifiable"


def test_capacity_still_stops_new_work_when_the_workers_are_other_people(world, capsys):
    """★ THE HALF THAT MUST NOT REGRESS. Five OTHER workers is a real stop: no room to start."""
    world([_item(id="READY")]
          + [_item(id=f"H{i}", state="in_progress", owner=o)
             for i, o in enumerate(OTHERS + ["CYC-0071-deadbeef"])])
    rc = C.main(["--check"])
    assert rc == 0, "a genuinely full loop is still a real stop — this is not the defect"
    assert "AT CAPACITY" in capsys.readouterr().out


def test_a_full_loop_still_does_not_excuse_a_row_you_hold_yourself(world, capsys):
    """⛔ CAPACITY AND YOUR OWN LEASE ARE DIFFERENT CLAIMS. Even with the cap genuinely full of other
    workers, a row YOU hold has no worker the moment you stop. Capacity licenses starting nothing
    NEW; it has never licensed abandoning what you already took."""
    world([_item(id="READY")]
          + [_item(id=f"H{i}", state="in_progress", owner=o)
             for i, o in enumerate(OTHERS + ["CYC-0071-deadbeef"])]
          + [_item(id="MINE", state="in_progress", owner=MINE)])
    assert C.main(["--check"]) == 1
    assert "YOU ARE THE WORKER" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------------
# Who counts as "me" — the distinction the whole fix rests on.
# ---------------------------------------------------------------------------------------------

def test_a_seat_you_dispatched_is_a_different_worker(world):
    """⛔ THE ONE-WAY DOOR. A driver that dispatches seats and claims at dispatch is doing the right
    thing, and the hook's remedy #1 tells it to. `SEAT-…` names a worker that is elsewhere and still
    running when this session stops; only `CYC-…-<this session>` names the session itself."""
    world([_item(id="READY")] + [_item(id="S", state="in_progress", owner=SEAT)])
    assert C.own_cycle_owners() == set(), "a seat is a worker you sent, not you"
    assert SEAT in {o for _, o in C.live_leases()}


def test_another_sessions_cycle_is_a_different_worker(world):
    world([_item(id="READY")] + [_item(id="O", state="in_progress", owner="CYC-0069-8226e21b")])
    assert C.own_cycle_owners() == set()


def test_the_session_identifies_itself_without_being_told(world):
    """★ NO FLAG REQUIRED, BECAUSE THE HOOK PASSES NONE. The Stop hook calls `--check --limit 5` and
    nothing else, so a fix that needed `--me` would have been unreachable from the one caller that
    matters — the unreachable-guard trap this repository has hit repeatedly."""
    world([_item(id="MINE", state="in_progress", owner=MINE)])
    assert C.own_cycle_owners() == {MINE}


def test_me_still_works_when_it_is_passed(world):
    world([_item(id="MINE", state="in_progress", owner="CYC-9999-ffffffff")], session=None)
    assert C.own_cycle_owners("CYC-9999-ffffffff") == {"CYC-9999-ffffffff"}


def test_an_unreadable_session_id_claims_nothing(world):
    """⚠ FAILING CLOSED IN THE DIRECTION THAT COSTS NOTHING. With no session id and no `--me` the
    tool cannot tell which lease is its own, so it claims none — the verdict is then exactly what it
    was before this change rather than a guess about identity."""
    world([_item(id="MINE", state="in_progress", owner=MINE)], session=None)
    assert C.own_cycle_owners() == set()


def test_a_short_session_id_is_not_matched_by_prefix(world):
    """⚠ AN 8-CHARACTER DISCRIMINATOR IS THE CONTRACT; a shorter id must not match loosely."""
    world([_item(id="MINE", state="in_progress", owner=MINE)], session="c84c")
    assert C.own_cycle_owners() == set()


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE GENERALISATION: the words and the exit code are one statement, not two.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("name,entries", [
    ("nothing running", [_item(id="READY")]),
    ("own lease", [_item(id="READY"), _item(id="M", state="in_progress", owner=MINE)]),
    ("others at capacity", [_item(id="READY")] + [_item(id=f"H{i}", state="in_progress", owner=o)
                            for i, o in enumerate(OTHERS + ["CYC-0071-deadbeef"])]),
    ("own lease inside a full cap",
     [_item(id="READY"), _item(id="M", state="in_progress", owner=MINE)]
     + [_item(id=f"H{i}", state="in_progress", owner=o)
        for i, o in enumerate(OTHERS + ["CYC-0071-deadbeef"])]),
    ("empty backlog", []),
    ("everything blocked", [_item(id="B", blocked_by=["BLK-HUMAN"])]),
])
def test_no_output_demands_work_while_the_exit_code_permits_stopping(world, capsys, name, entries):
    """⛔⛔ THE INVARIANT THAT WOULD HAVE CAUGHT THIS WITHOUT ANYONE PREDICTING IT.

    A `Stop` hook reads the exit code and returns on it BEFORE printing a byte of stdout. So a branch
    that tells the reader to keep working and then returns 0 is not hedged, it is silent — and that
    is precisely how the at-capacity branch behaved for as long as it existed. This asserts the two
    channels agree in every state, including states nobody has thought of yet.
    """
    world(entries)
    rc = C.main(["--check"])
    out = capsys.readouterr().out
    demanded = [p for p in DEMANDS_WORK if p in out]
    if demanded:
        assert rc != 0, (f"[{name}] printed {demanded} and returned 0. Inside the Stop hook that "
                         f"text is never shown: the hook exits on the code. Either the words or the "
                         f"code is wrong, and they must not disagree.")
