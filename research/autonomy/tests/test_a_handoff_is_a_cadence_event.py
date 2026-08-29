"""⛔⛔ A HANDOFF CREATES A SESSION, SO IT IS A CADENCE EVENT — AND IT COST $5.39 TO LEARN.

Measured 2026-08-29 (CYC-0088). trimcrae's budget hold landed at 11:51Z and took the cadence to 24 h.
At 13:41Z that cycle built a handoff and spawned a successor MINUTES after its own cycle. The
successor spent $5.39 before it was interrupted, under a hold whose entire purpose was to stop
exactly that spend.

⚠ THE PROVENANCE WAS NOT THE BUG, AND THAT IS THE WHOLE LESSON. `handoff.build` reads `origin/main`
and did so correctly; the hold simply had not been pushed when it read. Fixing provenance harder
would have changed nothing. What was missing is that **a cycle can start two ways** — the Routine
fires one, a handoff spawns one — and the gate was only on the first.

★ THIS SUITE IS NOT NEUTRALISED. `test_a_handoff_never_hands_over_what_it_did_not_push.py` patches
`cadence_verdict` away because its subject is the divergence refusal; here the cadence refusal IS the
subject, so it is driven through `handoff.main` end to end.
"""
from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import cadence  # noqa: E402
import handoff as HF  # noqa: E402


@pytest.fixture(autouse=True)
def _no_divergence(monkeypatch):
    """Neutralise the OTHER refusal, so a failure here can only be the cadence one."""
    monkeypatch.setattr(HF, "unpushed_rows", lambda w, t: [])
    monkeypatch.setattr(HF, "unpushed_receipt_files", lambda: [])


def _run(argv, monkeypatch, verdict):
    monkeypatch.setattr(HF, "cadence_verdict", lambda: verdict)
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = HF.main(argv)
    return code, out.getvalue(), err.getvalue()


TOO_SOON = (cadence.TOO_SOON, "⛔ TOO SOON — 0.6 h since the last cycle against a 24 h cadence.", {})
HELD = (cadence.UNDATABLE_UNDER_HOLD, "⛔ DO NOT START. A budget hold is active.", {})
OK = (cadence.MAY_START, "MAY START — 25.0 h since the last cycle.", {})


def test_a_successor_inside_the_interval_is_refused(monkeypatch):
    code, out, err = _run(["--reason", "x"], monkeypatch, TOO_SOON)
    assert code == 4, f"a handoff inside the cadence interval was allowed (exit {code})"
    assert out.strip() == "", "a refused handoff still printed a prompt somebody could paste"
    assert "TOO SOON" in err


def test_the_refusal_says_what_to_do_instead(monkeypatch):
    """⛔ A REFUSAL WITH NO REMEDY IS AN OUTAGE. Not spawning loses nothing — state is in git and the
    Routine fires again on its own — and the message has to say so, or the next session works around
    it."""
    _, _, err = _run(["--reason", "x"], monkeypatch, TOO_SOON)
    assert "REMEDY" in err and "re-reads the ledger" in err


def test_an_undatable_cycle_under_a_hold_is_refused(monkeypatch):
    assert _run(["--reason", "x"], monkeypatch, HELD)[0] == 4


def test_a_due_successor_is_still_built(monkeypatch):
    """★ THE POSITIVE CONTROL. Without it this suite would pass on a module that refuses everything,
    which is the failure mode `health.py` calls an outage with a virtuous name."""
    code, out, _ = _run(["--reason", "x"], monkeypatch, OK)
    assert code == 0 and out.strip(), "a handoff that was genuinely due produced nothing"


def test_the_json_payload_is_also_gated(monkeypatch):
    """⚠ ONE OF A PAIR. `--json` is the branch a spawning session actually calls — gating only the
    prose branch would leave the real path open, which is the one-of-a-pair defect class."""
    code, out, _ = _run(["--json", "--reason", "x"], monkeypatch, TOO_SOON)
    assert code == 4 and out.strip() == ""
    code, out, _ = _run(["--json", "--reason", "x"], monkeypatch, OK)
    assert code == 0 and "create_session" in json.loads(out)


def test_the_escape_exists_and_is_explicit(monkeypatch):
    """⭐ --ignore-cadence is for a successor genuinely due whose stamp is wrong. It must WORK, so the
    gate never becomes unclearable, and it must be a FLAG rather than a default."""
    assert _run(["--reason", "x", "--ignore-cadence"], monkeypatch, TOO_SOON)[0] == 0
    assert _run(["--reason", "x"], monkeypatch, TOO_SOON)[0] == 4


def test_the_gate_reads_handoffs_own_state_path(monkeypatch, tmp_path):
    """⛔ THE SEAM, ASSERTED. `cadence_verdict` must read THIS module's STATE — a gate pointed at a
    path the module does not own is a gate the module cannot be tested against."""
    monkeypatch.setattr(HF, "STATE", tmp_path / "absent.json")
    code, why, _ = HF.cadence_verdict()
    assert code == cadence.MAY_START, "an unreadable governor wedged the handoff instead of failing open"
    assert "NOT GATED" in why


def test_production_main_actually_calls_the_seam(monkeypatch):
    """⛔⛔ THE WIRING. A seam every test patches and production never calls is the `subagent_width`
    shape exactly: correct, tested and dead."""
    called = []
    monkeypatch.setattr(HF, "cadence_verdict", lambda: (called.append(1), OK)[1])
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        HF.main(["--reason", "x"])
    assert called, "handoff.main never consulted the cadence gate"
