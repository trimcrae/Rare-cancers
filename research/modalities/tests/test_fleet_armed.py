"""The gate that lets an idle supervision lane stop committing non-events — and every way it must NOT fail.

★ CONTEXT (2026-08-06). Eleven lanes were committing ~1,476 times a day, 703 of those saying in their own
subject line that they had done nothing, while the account held zero instances. The churn was deliberate —
the commit trail was the liveness channel — but the design had no OFF state, so it heartbeat identically
whether or not there was a fleet.

⛔ THE ASYMMETRY THAT DRIVES EVERY TEST HERE. Being wrongly ARMED costs a commit. Being wrongly IDLE means a
supervision lane goes quiet over a fleet that is actually billing — the 2026-08-01 failure, where a watch
loop had exited 24 minutes earlier and nothing said so while a host billed. So every ambiguous input must
return ARMED, and the tests below are mostly about doubt, not about the happy path.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fleet_armed as fa  # noqa: E402


def _census(tmp_path, **over):
    doc = {"n_instances": 0, "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    doc.update(over)
    p = tmp_path / "census.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return str(p)


# ───────────────────────── it must go idle only in the one safe case ─────────────────────────

def test_zero_instances_and_a_fresh_census_is_the_only_idle_state(tmp_path):
    st = fa.state(census_path=_census(tmp_path))
    assert st["armed"] is False
    assert "ZERO instances" in st["why"]


def test_any_instance_at_all_arms_it(tmp_path):
    st = fa.state(census_path=_census(tmp_path, n_instances=1))
    assert st["armed"] is True, "one live instance is a fleet; supervision is not optional"


# ───────────────────────── every form of doubt must FAIL ARMED ─────────────────────────

def test_a_missing_census_fails_armed(tmp_path):
    st = fa.state(census_path=str(tmp_path / "nope.json"))
    assert st["armed"] is True and "FAIL-ARMED" in st["why"]


def test_an_unreadable_census_fails_armed(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    st = fa.state(census_path=str(p))
    assert st["armed"] is True and "FAIL-ARMED" in st["why"]


def test_a_stale_census_fails_armed(tmp_path):
    """⛔ THE SHARPEST ONE. A census saying zero from four hours ago is not evidence the account is empty —
    it is evidence nobody has looked. An absent reading is not a reading of absence (CLAUDE.md §4), and this
    is the exact shape of the 2026-08-01 incident: a lane's census was 16 minutes stale while its host
    billed, and the staleness was reported as a status instead of as an unanswered question."""
    old = (datetime.now(timezone.utc) - timedelta(seconds=fa.MAX_CENSUS_AGE_S + 600))
    st = fa.state(census_path=_census(tmp_path, utc=old.strftime("%Y-%m-%dT%H:%M:%SZ")))
    assert st["armed"] is True and "stale" in st["why"].lower()


def test_a_census_with_no_instance_count_fails_armed(tmp_path):
    st = fa.state(census_path=_census(tmp_path, n_instances=None))
    assert st["armed"] is True and "FAIL-ARMED" in st["why"]


def test_a_census_with_an_unparseable_timestamp_fails_armed(tmp_path):
    st = fa.state(census_path=_census(tmp_path, utc="last Tuesday"))
    assert st["armed"] is True and "FAIL-ARMED" in st["why"]


def test_a_census_with_no_timestamp_at_all_fails_armed(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"n_instances": 0}), encoding="utf-8")
    st = fa.state(census_path=str(p))
    assert st["armed"] is True and "FAIL-ARMED" in st["why"]


# ───────────────────────── the surviving heartbeat ─────────────────────────

def test_the_census_lane_is_never_gated_by_its_own_reading(tmp_path):
    """⭐ WHY ONE LANE STAYS NOISY ON PURPOSE. If every lane could go quiet, "no commits at all" would stop
    being a signal and the 2026-08-01 lesson would be undone from the other direction. The lane that OWNS the
    census is exempt: it is the thing that would discover a host appearing, so its heartbeat is the one that
    still carries information when the fleet is empty."""
    st = fa.state(lane=fa.CENSUS_LANE, census_path=_census(tmp_path))
    assert st["armed"] is True
    assert st["evidence"]["exempt"] is True


# ───────────────────────── the exit contract the workflows depend on ─────────────────────────

def test_the_idle_exit_code_cannot_be_confused_with_a_crash(tmp_path, monkeypatch, capsys):
    """⛔ IDLE IS 10, NOT 1. Workflows branch on this exit code. If idle were 1, then a traceback — an
    ImportError, a bad path, any crash — would exit 1 and be read as "nothing to supervise", turning every
    failure of this module into silent unsupervision. That is the fail-quiet direction, so the two are kept
    numerically apart."""
    monkeypatch.setattr(fa, "CENSUS", _census(tmp_path))
    assert fa.main([]) == 10
    assert fa.main([fa.CENSUS_LANE]) == 0
    assert json.loads(capsys.readouterr().out.split("}\n{")[0] + "}")["armed"] is False


def test_the_live_census_path_is_the_account_level_one():
    """A per-mode board filters to one mode's labels and structurally cannot see a host another lane holds.
    Gating on one of those would be a lane-local belief — the thing this module exists to avoid."""
    assert fa.CENSUS.endswith("ternary-vast-account-census.json")
    if os.path.exists(fa.CENSUS):
        with open(fa.CENSUS, encoding="utf-8") as fh:
            doc = json.load(fh)
        assert "n_instances" in doc, "the census lost the field the gate reads"
        assert "instances" in doc, "account-level census must enumerate, not just count"


def test_main_reads_the_census_it_is_pointed_at(tmp_path, monkeypatch):
    """⛔ IT DID NOT, AND THE TEST ABOVE WAS MEASURING THE WALL CLOCK (fixed 2026-08-06).

    `state(lane=None, census_path=CENSUS, ...)` bound the default at IMPORT, so
    `monkeypatch.setattr(fa, "CENSUS", tmp)` could not reach it. `main()` passes no `census_path`, so
    the exit-contract test silently read the REAL committed census and passed only while that file was
    younger than MAX_CENSUS_AGE_S. It went red at 511 minutes, on a commit that touched nothing in this
    directory.

    ⚠ THE HARM IS THE MISDIRECTION, NOT THE RED. What the test actually measured — whether the live
    census is fresh — is already measured by the account-census alarms, which were reporting
    CENSUS-STALE at the time. A clock-dependent assertion in a module about *exit codes* sends whoever
    receives the failure hunting in the wrong file, and the real signal was already elsewhere.

    This pins the seam directly: point the module at a fixture and it must read the fixture.
    """
    monkeypatch.setattr(fa, "CENSUS", _census(tmp_path, n_instances=7))
    st = fa.state()
    assert st["evidence"].get("n_instances") == 7, \
        f"state() read something other than the census it was pointed at: {st}"
    assert fa.main([]) == 0

    monkeypatch.setattr(fa, "CENSUS", _census(tmp_path))
    assert fa.main([]) == 10, "a fresh, empty census the module was pointed at must read as idle"


def test_the_exempt_census_lane_is_actually_used_by_the_census_writer():
    """⛔ IT WAS NOT, AND THE EXEMPTION WAS INERT FOR 8.9 HOURS (measured 2026-08-06).

    `CENSUS_LANE` is exempt so that idle still leaves one commit trail and "no commits at all" stays a
    real signal — CLAUDE.md §6(b), and this module's own docstring. **No workflow passed that name.**
    The only writer of the account census published it under `ternary-reps-forensic`, which IS gated,
    so on an empty account the fresh census was written, read, judged IDLE, and DISCARDED. The
    committed copy aged past `account_orphan_alarm.py`'s 45-minute threshold, which suppresses every
    lane verdict — leaving the account-keyed alarm unable to say whether any host was billing, which is
    the exact 2026-08-01 failure that alarm exists to catch.

    ⚠ THE GATE WAS OBEYING ITS INPUT. The defect was a STRING, and it read as safe in three documents.
    So the wiring is asserted here rather than described: whoever writes the census must publish it
    under the exempt lane.
    """
    repo = os.path.abspath(__file__)
    for _ in range(4):                       # tests/ -> modalities/ -> research/ -> repo root
        repo = os.path.dirname(repo)
    wf = os.path.join(repo, ".github", "workflows")
    writers = [f for f in sorted(os.listdir(wf)) if f.endswith(".yml")
               and "ternary_reps_diag.py --census" in open(os.path.join(wf, f), encoding="utf-8").read()]
    assert writers, "no workflow writes the account census — the gate's exemption protects nothing"
    for f in writers:
        body = open(os.path.join(wf, f), encoding="utf-8").read()
        assert f'PUBLISH_HEARTBEAT_LANE="{fa.CENSUS_LANE}"' in body, (
            f"{f} writes the account census but never publishes it under the exempt lane "
            f"{fa.CENSUS_LANE!r} — an idle tick will discard the fresh census and blind every "
            f"account-keyed alarm")
        # ...and it must not be smuggled back into a gated publish alongside the forensic.
        for line in body.splitlines():
            if "ternary-vast-account-census.json" in line and "publish_artifacts.sh" in line:
                raise AssertionError(f"{f}: the census is an argument to a gated publish — {line.strip()}")
