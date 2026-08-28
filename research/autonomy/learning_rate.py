#!/usr/bin/env python3
"""Is the loop LEARNING, or only busy? — the detector the field does not have.

⛔⛔ THE CLAIM THIS IMPLEMENTS SURVIVED ADVERSARIAL REFUTATION 3-0 (the 2026-08-27 `/deep-research`
pass, 109 agents, instructed to break it): **no verified system detects "running but no longer
learning."** PanDA measures file mtime; Kubernetes probes and phi accrual consume liveness signals
only and are progress-blind by construction; a repo-wide grep of AlabOS for
`heartbeat|watchdog|liveness` returns zero hits.

⚠ AND THE NEIGHBOURING PROBLEM IS SOLVED, SO THIS MODULE MUST NOT BE SCOPED TO IT. Progress-versus-
liveness has named thresholds in production: PanDA runs a **900 s progress-verification cycle**
against a **7200 s no-file-written limit**, separately from its 1800 s heartbeat and 10800 s
lost-heartbeat path. `stuck_clock.py` is this repository's answer to THAT question. This module asks
the harder one: the work is advancing — is it advancing anything that matters?

★★ THE MEASURE, AND WHY COUNTING CLOSURES IS NOT ENOUGH. Measured 2026-08-28 against the nine-cycle
run of CYC-0033…CYC-0041: those cycles closed **six** ledger rows, so any "did anything close?"
detector would have graded them HEALTHY. Their route distribution is the tell —

    RT-AUTONOMY      5
    RT-PARTNER-STRAT 1

**five of six closures were the loop working on itself.** ⭐ That is precisely ORNL's published fault
signal for an autonomous campaign, transferred: *"the concentration of the experimental points in a
certain part of the image plane to full exclusion of other regions often suggests the effects of
instrumental crosstalk"* — read the SAMPLING TRAJECTORY, not the sample count. A loop that only ever
closes its own process defects is sampling one region of its portfolio to the exclusion of the rest.

⛔ SO THE VERDICT IS TWO-DIMENSIONAL AND BOTH HALVES ARE REQUIRED:
    (a) DID anything close in the window at all — the naive measure, still necessary;
    (b) WHERE did the closures land — concentration across `serves.route`.
Neither alone is the signal. (a) alone called the nine-cycle run healthy; (b) alone would flag a
window with one honest closure on one route, which is a normal small cycle.

⚠ SELF-MAINTENANCE IS NOT A DEFECT, AND THIS MODULE MUST NEVER SAY IT IS. Fixing the loop is real
work and this repository has spent whole sessions on it correctly. What the detector reports is that
the loop has been doing ONLY that for a window — a fact for a reader to act on, not a verdict on any
cycle. The honest failure it catches is a portfolio of forty routes advancing through none of them
while the machinery that advances them gets steadily better.

⭐ THE THRESHOLDS ARE ARIS'S, BORROWED RATHER THAN INVENTED, and they were named in this
repository's own prior-art scan on 2026-08-27 and left unadopted until now: `tools/iteration_log.py`
forces a change of direction after **two** empty rounds and calls in a human after **four**.

USAGE
    python3 research/autonomy/learning_rate.py            # the report
    python3 research/autonomy/learning_rate.py --check    # exit 1 if the window is not learning
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import stuck_clock  # noqa: E402

#: ARIS's numbers, in cycles. Two empty rounds force a change of direction; four call in a human.
CHANGE_DIRECTION_AFTER = 2
CALL_A_HUMAN_AFTER = 4

#: The loop's own maintenance route. Named, not guessed — a closure here is the loop improving the
#: machinery rather than the science.
SELF_ROUTE = "RT-AUTONOMY"

CLOSED = stuck_clock.CLOSED_STATES


def window_hours(cycles: int = CALL_A_HUMAN_AFTER, state_path: str | None = None) -> float:
    """The window, in hours, derived from the governor's own cadence — never typed."""
    return stuck_clock.cycle_interval_hours(state_path) * cycles


def closures(versions=None, since=None, repo: str = stuck_clock.REPO) -> list[tuple[str, str, datetime.datetime]]:
    """`[(row id, route, when)]` for every row that ENTERED a closed state in the window.

    ⛔ A transition, never a state. A row already `done` before the window is not a closure in it —
    counting states rather than transitions would make a healthy backlog look like constant progress
    forever, which is the same "presence is not provenance" error CLAUDE.md §4 records.
    """
    versions = versions if versions is not None else stuck_clock.ledger_versions(repo)
    out = []
    prev = None
    for v in versions:
        if prev is not None:
            for rid, row in v.rows.items():
                now = (row.get("state") or "").strip()
                was = (prev.rows.get(rid, {}).get("state") or "").strip()
                if now in CLOSED and was and was not in CLOSED:
                    if since is None or v.when >= since:
                        route = ((row.get("serves") or {}).get("route")) or "UNROUTED"
                        out.append((rid, route, v.when))
        prev = v
    return out


def report(repo: str = stuck_clock.REPO, hours: float | None = None, state_path=None) -> dict:
    h = window_hours(state_path=state_path) if hours is None else hours
    versions = stuck_clock.ledger_versions(repo)
    shallow = stuck_clock.is_shallow(repo)
    now = versions[-1].when if versions else datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(hours=h)
    # ⛔ SHALLOW CENSORS ONLY WHAT IT ACTUALLY HIDES. The first version reachable in a shallow clone
    # is the horizon; if it PREDATES the window, the window is fully readable and calling it censored
    # is a tool that can never answer. ⚠ Measured 2026-08-28: the clone here is shallow and the
    # horizon sits hours before a 16 h window, so the blanket rule returned CENSORED over 40 readable
    # closures across 14 routes — an honest-looking refusal that was simply wrong.
    horizon = versions[0].when if versions else None
    censored = shallow and (horizon is None or horizon > since)
    found = closures(versions, since=since, repo=repo)
    by_route = collections.Counter(r for _, r, _ in found)
    total = sum(by_route.values())
    self_share = (by_route.get(SELF_ROUTE, 0) / total) if total else 0.0
    return {
        "window_hours": h,
        "closures": total,
        "by_route": dict(by_route),
        "distinct_routes": len(by_route),
        "self_route_share": self_share,
        "shallow_clone": shallow,
        "horizon_inside_window": censored,
        "verdict": _verdict(total, by_route, self_share, censored),
    }


def _verdict(total: int, by_route, self_share: float, censored: bool) -> tuple[str, str]:
    """(code, one-line reason). ⛔ Censored only when the shallow horizon falls INSIDE the window —
    then an empty window cannot be told from an unreadable one, and refusing to grade is the
    direction that does not invent a finding."""
    if censored:
        return ("CENSORED",
                "the shallow clone's horizon falls inside the window, so an empty window cannot be "
                "distinguished from an unreadable one")
    if total == 0:
        return ("NOT-LEARNING",
                f"no ledger row entered a closed state in the window — {CHANGE_DIRECTION_AFTER} "
                f"empty rounds is ARIS's change-direction signal, {CALL_A_HUMAN_AFTER} calls a human")
    if len(by_route) == 1 and SELF_ROUTE in by_route:
        return ("SELF-MAINTAINING",
                f"all {total} closure(s) in the window served {SELF_ROUTE} — the loop is improving "
                f"its own machinery and advancing no research route. Not a defect; a fact to act on")
    if self_share >= 0.75 and total >= 4:
        return ("CONCENTRATED",
                f"{by_route.get(SELF_ROUTE, 0)} of {total} closures served {SELF_ROUTE} "
                f"({self_share:.0%}) — the sampling trajectory is concentrated in one region")
    return ("LEARNING",
            f"{total} closure(s) across {len(by_route)} route(s) in the window")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when the window is not learning")
    ap.add_argument("--hours", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    rep = report(hours=args.hours)
    if args.json:
        print(json.dumps(rep, indent=2, default=str))
    else:
        code, why = rep["verdict"]
        print(f"learning_rate: {code} — {why}")
        print(f"   window {rep['window_hours']:.0f} h | {rep['closures']} closure(s) | "
              f"{rep['distinct_routes']} route(s)")
        for route, n in sorted(rep["by_route"].items(), key=lambda kv: -kv[1]):
            print(f"      {n:>3}  {route}")
    return 1 if args.check and rep["verdict"][0] in ("NOT-LEARNING", "SELF-MAINTAINING") else 0


if __name__ == "__main__":
    raise SystemExit(main())
