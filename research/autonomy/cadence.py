#!/usr/bin/env python3
"""⛔⛔ THE CADENCE GATE — because the dial that fires sessions is NOT in this repository.

`autonomy-state.json` carries `cycle_interval_hours`. Until 2026-08-29 that number described a
cadence it did not set: the thing that actually starts a cycle is a Claude Routine
(`trig_01P9ZNSAw7rNLcKLBFYCwuHp`, cron `13 */4 * * *`), and **an agent cannot edit a Routine a human
created.** Measured that day, twice, against the live API:

    update_trigger: this routine was created via "http_api", not by an agent. Agents can only
    update routines they created (via create_trigger).

Both a cron change and a plain `enabled: false` were refused. So slowing the loop down by editing
`cycle_interval_hours` alone would have been the `subagent_width` failure again — a governed number
read by nothing, six sessions a day firing while every committed artifact said one.

⭐ **THE ESCAPE IS THE ONE THE DRIVER PROMPT DESIGNED IN.** That prompt is deliberately thin and says
so in as many words: *"this prompt is only the trigger … you can improve that file and cannot improve
this prompt."* The file is `.claude/skills/research-loop/SKILL.md`, and the fired session reads it
before acting. So the cadence gate lives HERE, in git, where it can be changed, tested and read —
and the skill's stop-condition table calls it first. A fire that arrives too soon exits in two tool
calls instead of running a cycle. An un-editable 4 h cron becomes an effective 24 h cadence without
anyone editing the cron.

⚠ **THIS IS A THROTTLE, NOT A LOCK.** It never refuses the FIRST cycle after an interval elapses, and
with no prior cycle observable it ALLOWS — "no receipt has ever been written" is a genuine absence of
a prior cycle, not a failed reading of one (CLAUDE.md §4). The one case it fails CLOSED is a prior
cycle it can SEE but cannot DATE, and only while a `budget_hold` is active: there, refusing costs one
skipped fire and permitting costs budget nobody has.

Usage:

    python3 research/autonomy/cadence.py --check   # exit 0 may start, 3 too soon, 4 unreadable-under-hold
    python3 research/autonomy/cadence.py --stamp   # record that a cycle is starting NOW
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "autonomy-state.json")
RECEIPTS = os.path.join(HERE, "receipts")

MAY_START, TOO_SOON, UNDATABLE_UNDER_HOLD = 0, 3, 4


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _parse(ts):
    if not isinstance(ts, str) or not ts.strip():
        return None
    try:
        return datetime.datetime.fromisoformat(ts.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def _et(dt):
    if dt is None:
        return "?"
    try:
        import zoneinfo
        dt = dt.astimezone(zoneinfo.ZoneInfo("America/New_York"))
    except Exception:
        pass
    return dt.strftime("%-I:%M %p ET %b %-d")


def load_state(path=STATE):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh), None
    except Exception as exc:                                    # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def interval_hours(state):
    """The declared cadence, or None. ⚠ Absent is NOT 4 — a default here would be a remembered
    number standing in for a measurement, and the whole bug this module exists for is a cadence
    that lived in one place and governed another."""
    v = (state or {}).get("cycle_interval_hours")
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
        return float(v)
    return None


def hold_is_active(state):
    hold = (state or {}).get("budget_hold")
    return isinstance(hold, dict) and bool(hold.get("active"))


def last_cycle_start(state, receipts_dir=RECEIPTS):
    """When the last cycle began, and HOW that was known — never a guess.

    Precedence: the state file's own stamp, then the git COMMITTER time of the newest receipt.
    ⛔ File mtime is deliberately absent, for the reason `health.py` gives beside
    `RECEIPT_TIME_KEYS`: a fresh `git clone` rewrites every mtime, so an ancient receipt would read
    as this minute's — a populated field that is not a measured one. Git's committer time survives a
    clone, which is exactly why it is the fallback and mtime is not.
    """
    stamped = _parse((state or {}).get("last_cycle_started_utc"))
    if stamped is not None:
        return stamped, "autonomy-state.json `last_cycle_started_utc`", None
    try:
        names = sorted(n for n in os.listdir(receipts_dir) if n.endswith(".json"))
    except OSError as exc:
        return None, None, f"receipts directory unreadable: {exc}"
    if not names:
        return None, None, None                                 # genuinely no prior cycle
    newest = os.path.join(receipts_dir, names[-1])
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", newest],
                             cwd=os.path.dirname(HERE), capture_output=True, text=True, timeout=30)
        ts = _parse((out.stdout or "").strip())
    except Exception as exc:                                    # noqa: BLE001
        return None, None, f"git log on {names[-1]} failed: {type(exc).__name__}: {exc}"
    if ts is None:
        return None, None, (f"{names[-1]} exists but git records no committer time for it, so the "
                            f"last cycle can be SEEN and not DATED")
    return ts, f"git committer time of receipts/{names[-1]}", None


def check(state=None, now=None, receipts_dir=RECEIPTS, state_path=None):
    """Return ``(exit_code, message, payload)``. Pure — takes its clock and its state as arguments.

    ⛔ `state_path` NAMES WHICH GOVERNOR FILE TO READ, AND IT EXISTS BECAUSE `state=None` DOES NOT
    MEAN "UNREADABLE" — it means "load it yourself". A caller that loaded the file, got None because
    the file was absent, and passed that None through was not exercising the fail-open branch: it was
    silently falling back to THIS module's `STATE`, i.e. the real repository file. Measured
    2026-08-29 by `test_the_gate_reads_handoffs_own_state_path`, which is exactly the test that would
    have believed it. Pass `state_path` and the fail-open branch is reachable and honest.
    """
    if state is None:
        # ⚠ `STATE` is read here rather than bound as a default argument: a default is evaluated at
        # import, so the module global could be repointed and this call would still read the old
        # path — a test that thinks it is exercising the fail-open branch and is not.
        state, err = load_state(state_path or STATE)
        if state is None:
            return MAY_START, (f"⚠ NOT GATED — autonomy-state.json is unreadable ({err}), so the "
                               f"declared cadence is unknown. Failing open: a gate that cannot read "
                               f"its own setting must not become a permanent outage."), {}
    now = now or _now()
    interval = interval_hours(state)
    held = hold_is_active(state)
    if interval is None:
        return MAY_START, ("⚠ NOT GATED — autonomy-state.json carries no positive "
                           "`cycle_interval_hours`, so there is no declared cadence to enforce."), {}
    last, basis, err = last_cycle_start(state, receipts_dir)
    if last is None:
        if err and held:
            return UNDATABLE_UNDER_HOLD, (
                f"⛔ DO NOT START. A budget hold is active and the last cycle cannot be dated — "
                f"{err}. Under a hold this fails CLOSED: one skipped fire costs a few hours, and a "
                f"fire nobody can account for costs budget that is already over pace. Fix the "
                f"reading (stamp `last_cycle_started_utc`), do not work around it."), {"error": err}
        note = err or "no receipt exists yet, so there is no prior cycle to be too soon after"
        return MAY_START, f"MAY START — {note}.", {"error": err}
    elapsed = (now - last).total_seconds() / 3600.0
    payload = {"interval_h": interval, "elapsed_h": round(elapsed, 2), "basis": basis,
               "last_cycle_et": _et(last), "budget_hold_active": held}
    if elapsed < interval:
        nxt = last + datetime.timedelta(hours=interval)
        payload["next_eligible_et"] = _et(nxt)
        return TOO_SOON, (
            f"⛔ TOO SOON — {elapsed:.1f} h since the last cycle ({basis}, {_et(last)}) against a "
            f"declared {interval:g} h cadence. Next eligible {_et(nxt)}. ⭐ EXIT NOW: write no "
            f"receipt, take no item, claim nothing. A skipped fire is the cadence working, not a "
            f"failure, and it is the ONLY way this cadence binds — the Routine's cron is "
            f"human-created and an agent cannot edit it (see this module's docstring)."), payload
    return MAY_START, (f"MAY START — {elapsed:.1f} h since the last cycle ({basis}, {_et(last)}) "
                       f"against a {interval:g} h cadence."), payload


def stamp(now=None, path=STATE):
    """Record that a cycle is starting. Called at §4.2 step 1, before any work."""
    now = now or _now()
    with open(path, encoding="utf-8") as fh:
        state = json.load(fh)
    state["last_cycle_started_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    state["_last_cycle_started_utc_means"] = (
        "Written by `cadence.py --stamp` at §4.2 step 1, BEFORE the cycle does anything. It is what "
        "the cadence gate measures against, and it is stamped at the START rather than at the "
        "receipt so that a cycle which dies mid-flight still counts as a fire — otherwise a crashing "
        "cycle would be re-fired every four hours forever, which is the exact herd the gate exists "
        "to stop.")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return state["last_cycle_started_utc"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="may a cycle start now?")
    ap.add_argument("--stamp", action="store_true", help="record that a cycle is starting now")
    ap.add_argument("--json", action="store_true", help="machine-readable")
    args = ap.parse_args(argv)
    if args.stamp:
        print(f"stamped last_cycle_started_utc = {stamp()}")
        return 0
    code, msg, payload = check()
    if args.json:
        print(json.dumps({"exit": code, "message": msg, **payload}, indent=2, ensure_ascii=False))
    else:
        print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main())
