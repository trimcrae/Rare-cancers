#!/usr/bin/env python3
"""FAIL A TICK THAT WENT GREEN WITHOUT RE-MEASURING.

WHY THIS EXISTS (2026-07-27, 9:40 AM ET). Eighteen GPUs were billing on the Step 1 fan-out and the only
readable progress artifact said `phases: {..., leg-complex-running: 10}`, `gpu_util` 9 of 10 below 5 %, and
`0 of 19 units advanced`. Three minutes after a launch that reads as a normal cold start. Forty-five minutes
after a launch it reads as a fleet-wide stall costing real money. The artifact could not tell you which,
because it carried NO GENERATION TIMESTAMP — `_snapshot_point` documented where in the tick it was taken and
never when. So the operator could not grade their own evidence, and an autoscale tick dispatched to refresh
it reported `success` in 36 seconds while (correctly, as it turned out) pushing its readout to the FLEET
branch, which was not the ref being read.

The fleet was fine. That is the point: the monitoring could not demonstrate it either way, and "I cannot
prove any of these 18 GPUs is doing work" is an unacceptable state to be in while paying for them.

THE DEFECT CLASS, stated generally: a monitoring job whose measurement silently no-ops still exits 0, because
every step "succeeded" — the collect ran, the commit step found nothing to commit and printed "no change",
and the run went green. Green then means "the plumbing did not throw", which a reader inevitably reads as
"the fleet was measured". This module makes the two mean the same thing: if the tick did not produce a
snapshot it measured ITSELF, THIS run, the tick FAILS.

★ IT MUST NEVER BE FIXED BY SKIPPING THE CHECK. A missing `_generated_utc`, an unparseable one, or a stale
one are all HARD FAILURES, never warnings and never a silent pass. The whole value of the gate is that it
cannot be satisfied by the absence of evidence — that is the exact failure it was written to catch.

Usage:  python3 assert_progress_fresh.py [path] [--max-age-min N]
Exit 0 = the artifact was regenerated within the window. Exit 1 = it was not, with the reason on stderr.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys

ET = datetime.timezone(datetime.timedelta(hours=-4))   # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

# Generous relative to a tick (the monitor step takes ~10 s) but far tighter than the 45-minute blind spot
# that motivated this. A tick that genuinely re-measured lands inside a minute or two; anything approaching
# this bound means the file on disk is a leftover from an EARLIER run that this run failed to overwrite.
DEFAULT_MAX_AGE_MIN = 10.0


def _et(ts: datetime.datetime) -> str:
    return ts.astimezone(ET).strftime("%I:%M %p ET %b %d, %Y").lstrip("0").replace(" 0", " ")


def check(path: str, max_age_min: float, now: datetime.datetime | None = None) -> tuple[bool, str]:
    """Return (ok, message). Never raises for an expected condition — the caller decides the exit code."""
    now = now or datetime.datetime.now(datetime.timezone.utc)

    try:
        with open(path) as f:
            snap = json.load(f)
    except FileNotFoundError:
        return False, (f"{path} DOES NOT EXIST. The progress check was supposed to write it this run. "
                       f"The tick measured nothing — failing rather than reporting green.")
    except json.JSONDecodeError as e:
        return False, f"{path} is not parseable JSON ({e}). Treated as no measurement at all."

    stamp = snap.get("_generated_utc")
    if not stamp:
        # An artifact written by code predating this field. Deliberately fatal: the entire incident was
        # caused by an undatable artifact, so "old enough to have no timestamp" is the condition, not an
        # excuse to wave it through.
        return False, ("the snapshot carries NO `_generated_utc`, so its age cannot be established and it "
                       "cannot be distinguished from a stale leftover. This is the exact defect the gate "
                       "exists to catch — do not silence it; make the writer stamp the file.")

    try:
        gen = datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return False, f"`_generated_utc` = {stamp!r} is not an ISO Z timestamp; age is unverifiable."

    age_min = (now - gen).total_seconds() / 60.0

    # A stamp from the FUTURE is not freshness, it is a broken clock or a hand-edited artifact. Bounded
    # generously (runner/host clock skew is real and small) but not unbounded, because "always fresh" is the
    # one answer this gate must never give by accident.
    if age_min < -2.0:
        return False, (f"`_generated_utc` is {abs(age_min):.1f} min in the FUTURE ({_et(gen)}). Clock skew or "
                       f"a hand-edited artifact — either way the age is not trustworthy.")

    if age_min > max_age_min:
        return False, (f"the snapshot is {age_min:.1f} min old (generated {_et(gen)}, now {_et(now)}), past "
                       f"the {max_age_min:.0f} min window. This run did NOT refresh it: the file on disk is a "
                       f"leftover from an earlier tick, so this tick measured nothing and must not pass.")

    return True, (f"snapshot regenerated {age_min:.1f} min ago ({_et(gen)}, now {_et(now)}) — "
                  f"within the {max_age_min:.0f} min window. This tick really did re-measure the fleet.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", nargs="?", default="step1-fanout-progress.json")
    ap.add_argument("--max-age-min", type=float, default=DEFAULT_MAX_AGE_MIN)
    a = ap.parse_args(argv)

    ok, msg = check(a.path, a.max_age_min)
    if ok:
        print(f"[fresh] ✅ {a.path}: {msg}")
        return 0
    # ::error:: so it surfaces in the GitHub UI rather than only in a log tail nobody scrolls back through.
    print(f"::error::STALE OR MISSING PROGRESS EVIDENCE — {a.path}: {msg}", file=sys.stderr)
    print(f"[fresh] ❌ {a.path}: {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
