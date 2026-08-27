#!/usr/bin/env python3
"""A worker's STATUS is not its PROGRESS, and only one of them can be trusted.

⛔⛔ MEASURED 2026-08-27, AND trimcrae FOUND IT BEFORE THE LOOP DID. A seat was dispatched, died on
its FIRST message, and `ListAgents` reported it `running` for 2 h 36 m. The driver relayed that
status as "in flight" seven times and held its claim on AUT-PROP-012 open throughout. The seat's
entire output was: "I'll start by reading the ledger entry and the relevant files."

★ ASKING `ListAgents` WAS ASKING THE WRONG QUESTION. It answers "is this agent alive?" — a liveness
ping. A status field cannot separate a seat thinking hard from a seat that stopped existing.
CLAUDE.md §4 already said so: an unproven pipeline gets PROGRESS checks, and "no error yet" is not
progress.

⭐ THE SHAPE IS BORROWED. ARIS (15,294★, MIT) runs `tools/watchdog.py` as a separate process
watching STATE-FILE WRITES, and it only ever reports. That was ranked in this repository's own
`method-watch-autonomy-prior-art.md` hours before the stall and nobody read it.
"""

from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import stalled_holder as S  # noqa: E402


def _fixture(tmp_path, owner, minutes_quiet, state="in_progress", body="x", write_transcript=True):
    led = tmp_path / "ledger.json"
    led.write_text(json.dumps({"entries": [
        {"id": "AUT-PROP-012", "state": state, "owner": owner}]}), encoding="utf-8")
    tasks = tmp_path / "tasks"
    tasks.mkdir(exist_ok=True)
    if write_transcript:
        p = tasks / f"{owner}.output"
        p.write_text(body, encoding="utf-8")
        t = time.time() - minutes_quiet * 60
        os.utime(p, (t, t))
    return str(tasks), str(led)


def test_the_exact_stall_is_caught(tmp_path):
    """⛔⛔ THE REGRESSION, WITH THE REAL NUMBERS: 156 minutes quiet, holding AUT-PROP-012, its whole
    output one sentence about what it was about to do."""
    tasks, led = _fixture(tmp_path, "fusion-partner-relation-seat", 156,
                          body="I'll start by reading the ledger entry and the relevant files.")
    rows = S.stalled(tasks, led)
    assert [(r[0], r[1]) for r in rows] == [("AUT-PROP-012", "fusion-partner-relation-seat")]
    assert S.main(["--tasks-dir", tasks, "--ledger", led, "--check"]) == 1


def test_a_working_seat_is_not_reported(tmp_path):
    """⚠ THE DIRECTION THAT COSTS WORK. A seat is legitimately silent through one long tool call —
    the modalities suite is ~20 minutes and moves nothing — so the threshold must clear the longest
    honest silence this repository produces, or the guard cries wolf and gets muted."""
    tasks, led = _fixture(tmp_path, "busy-seat", 4)
    assert S.stalled(tasks, led) == []
    assert S.STALL_MINUTES > 20, "the threshold no longer clears a modalities suite"


def test_a_released_claim_is_not_reported_however_dead_the_worker(tmp_path):
    """★ THE SUBJECT IS THE PARKED ITEM, NOT THE DEAD AGENT. Once the lease is released the harm is
    gone, and a finished worker's cold transcript must not keep firing — that is how a guard becomes
    noise and stops being read."""
    tasks, led = _fixture(tmp_path, "dead-seat", 999, state="done")
    assert S.stalled(tasks, led) == []
    tasks2, led2 = _fixture(tmp_path, None, 999)
    assert S.stalled(tasks2, led2) == []


def test_a_holder_with_no_transcript_is_never_reported(tmp_path):
    """⚠ MOST OWNERS ARE NOT SUBAGENTS. A cycle id holds items across sessions and has no transcript
    here; reporting those every single turn is the cry-wolf failure this repository has already lost
    the value of several guards to. Only a holder this session can OBSERVE going quiet is a finding."""
    tasks, led = _fixture(tmp_path, "CYC-0031-somewhere-else", 999, write_transcript=False)
    assert S.stalled(tasks, led) == []


def test_it_reports_and_never_acts(tmp_path, capsys):
    """⛔ ARIS's own rule, and the right one: the watchdog "only reports the problem, never restarts
    a verdict-bearing run". Killing a seat and releasing a lease is a judgement, and a judgement made
    by a watchdog is how live work gets thrown away."""
    tasks, led = _fixture(tmp_path, "quiet-seat", 200)
    S.main(["--tasks-dir", tasks, "--ledger", led])
    out = capsys.readouterr().out
    assert "prompt to LOOK, not a verdict" in out
    assert json.load(open(led, encoding="utf-8"))["entries"][0]["owner"] == "quiet-seat", (
        "the watchdog mutated the ledger; it must only report")
