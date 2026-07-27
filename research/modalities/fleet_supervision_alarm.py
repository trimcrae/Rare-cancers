#!/usr/bin/env python3
"""BE LOUD WHEN NOBODY IS WATCHING A BILLING FLEET — from OUTSIDE the thing being watched.

WHY THIS EXISTS (2026-07-27, 11:37 AM-12:01 PM ET). `assert_progress_fresh.py` already refuses to let a tick
go green without re-measuring. But it runs INSIDE the tick, so it can only fire when the tick RUNS. That
leaves the deeper hole untouched:

    A TICK THAT FAILED AND A TICK THAT NEVER RAN LEAVE THE IDENTICAL ARTIFACT — a stale file.

Both happened today, at once. At 11:37 AM ET the autoscale tick died on its FIRST step (a cost-model unit
test broken by another lane's ladder re-anchor) before the progress check ever ran, so it measured nothing;
the `always()` steps still committed, so the commit trail kept moving while `step1-fanout-progress.json` sat
at its 10:06 AM value. Meanwhile no `schedule` event had been delivered for 109 minutes. From the artifacts
alone those two are indistinguishable, and the fleet was 16 rentals deep.

★★ THE MEASUREMENT THAT MOTIVATED THE DESIGN — SCHEDULED DELIVERY IS ~2.5-4 HOURS, NOT ~1 HOUR.
`step1-fanout-autoscale.yml` asks for `*/20` and `vast-watchdog.yml` asks for `*/15`, and BOTH carry comments
claiming GitHub's throttle lands them "~55-65 min apart". That was true on 2026-07-26. Measured on 2026-07-27:

    autoscale schedule events : 12:52 AM, 4:19 AM, 7:44 AM, 10:05 AM ET  -> gaps 220, 208, 205, 141 min
    watchdog  schedule events : 1:59 AM, 5:56 AM, 8:53 AM, 11:37 AM ET   -> gaps 235, 238, 177, 164 min

So the operator's mental model ("something checks the fleet about every hour") was wrong by 3x, and the real
supervision between scheduled ticks was an agent hand-dispatching — 25 of the last 30 autoscale runs were
`workflow_dispatch`. When the agent stopped, supervision stopped, and nothing said so.

TWO CONSEQUENCES FOR THIS MODULE, both deliberate:
  1. A SECOND `schedule:` BUYS INDEPENDENCE FROM CODE, NOT FROM THROTTLE. This alarm cannot be taken down by
     the lane it watches (pure stdlib, no boto3, no Vast key, no import from the fan-out code — the exact
     coupling that broke the tick today), but it is throttled by the same scheduler. It therefore never
     claims to be a heartbeat, and it reports its OWN delivery gap so its silence is auditable too.
  2. THE THRESHOLD IS SET FROM MEASURED DELIVERY, NOT NOMINAL CRON. A 20-minute threshold against 141-238
     minute delivery is an alarm that is always red, which is an alarm nobody reads.

★★ AND THE PRIMARY SIGNAL IS **NOT** ARTIFACT AGE. This is the part that took a failed test to see, and it
is the reason the module is shaped the way it is.

If scheduled delivery is legitimately 141-238 minutes, then an artifact that is 200 minutes old is NORMAL,
and any age threshold honest about that must sit above ~240 min. But today's incident had the artifact only
**115 minutes** stale at the moment 16 GPUs were unsupervised. An age-threshold alarm tuned not to cry wolf
would have said FRESH throughout the entire incident. Age alone therefore CANNOT detect this failure class —
not as a tuning problem, but by construction.

The signal that does work is a comparison, and it is immune to throttle:

    DID THE LAST COMPLETED RUN ADVANCE `_generated_utc` PAST ITS OWN START TIME?

A run that started at 11:37 AM and left the artifact stamped 10:06 AM did not measure — knowable at 11:38 AM,
whatever the cron is doing. So this module leads with that, and uses age only for the one thing age is good
for: noticing that nothing has run at all.

    FAILING              — a run started, completed, and did not refresh the artifact. The tick's CODE is broken.
    STALE-BUT-RUNS-GREEN — same, but the run reported success: it went green WITHOUT measuring.
    ABSENT               — nothing has started in the absent window: the SCHEDULER is not delivering.
    STALE-CAUSE-UNKNOWN  — the artifact is old and the run history could not be read.
    FRESH                — the last completed run did refresh it.
The run history comes from the public Actions API, which needs no token on a public repo.

⚠ THIS MODULE NEVER RENTS, DESTROYS, NUDGES OR PRICES ANYTHING. It reads and it complains. Recovery belongs
to the tick and to `vast-watchdog.yml`, which hold the credentials and the reviewed reap/relaunch paths.

Usage:
    python3 fleet_supervision_alarm.py [--progress PATH] [--stale-min N] [--absent-min N] [--repo O/R]
                                       [--workflow F.yml] [--json OUT]
Exit 0 = supervised. Exit 1 = not supervised, with the cause named on stderr.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import urllib.error
import urllib.request

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

# ── thresholds, each justified by a measurement above ────────────────────────────────────────────────────
# Artifact age at which we call the fleet unsupervised. Measured scheduled delivery on 2026-07-27 was
# 141-238 min, so anything under ~4 h would be red permanently through no fault of the tick. 240 min is
# "even the WORST observed delivery gap should have produced a measurement by now".
DEFAULT_STALE_MIN = 240.0
# How recently a RUN must have STARTED for the scheduler to count as delivering. Same measurement, same
# logic: if nothing has even started in 4 h, the scheduler itself is the fault, not the code.
DEFAULT_ABSENT_MIN = 240.0

REPO = "trimcrae/Rare-cancers"
TICK_WORKFLOW = "step1-fanout-autoscale.yml"


def _et(ts: datetime.datetime) -> str:
    return ts.astimezone(ET).strftime("%-I:%M %p ET %b %-d, %Y")


def _parse_z(s: str) -> datetime.datetime | None:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def fetch_runs(repo: str, workflow: str, per_page: int = 20) -> list[dict] | None:
    """Recent runs from the PUBLIC Actions API. Returns None if it could not be read.

    None is "could not ask", never "no runs" — reporting an unmeasured state as a measured zero is this
    repo's most expensive defect class, and here it would turn a network blip into "the scheduler is dead".
    """
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?per_page={per_page}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "fleet-supervision-alarm"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()).get("workflow_runs") or []
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return None


def classify(progress: dict | None, runs: list[dict] | None, now: datetime.datetime,
             stale_min: float, absent_min: float) -> dict:
    """Decide WHY supervision is or is not happening. Pure — all I/O is done by the caller, so this is tested."""
    out: dict = {"utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "et": _et(now),
                 "stale_min_threshold": stale_min, "absent_min_threshold": absent_min}

    # ── how old is the evidence? ──
    gen = _parse_z((progress or {}).get("_generated_utc") or "")
    age = (now - gen).total_seconds() / 60.0 if gen else None
    out["artifact_generated_et"] = _et(gen) if gen else None
    out["artifact_age_min"] = round(age, 1) if age is not None else None
    out["live_instances"] = (progress or {}).get("live_instances")
    out["realised_usd_so_far"] = (progress or {}).get("realised_usd_so_far")

    # ── is the scheduler delivering? ──
    started, sched_gaps = [], []
    if runs is not None:
        for r in runs:
            t = _parse_z(r.get("run_started_at") or r.get("created_at") or "")
            if t:
                started.append((t, r))
        started.sort(key=lambda p: p[0])
        sched = [t for t, r in started if r.get("event") == "schedule"]
        sched_gaps = [round((b - a).total_seconds() / 60.0) for a, b in zip(sched, sched[1:])]
    out["scheduled_delivery_gaps_min"] = sched_gaps[-6:]
    last_start = started[-1][0] if started else None
    last_sched = max((t for t, r in started if r.get("event") == "schedule"), default=None)
    out["last_run_started_et"] = _et(last_start) if last_start else None
    out["last_scheduled_run_et"] = _et(last_sched) if last_sched else None
    since_start = (now - last_start).total_seconds() / 60.0 if last_start else None
    out["min_since_any_run_started"] = round(since_start, 1) if since_start is not None else None

    # ★ THE DISCRIMINATOR. The most recent run that actually COMPLETED: did it move `_generated_utc` past
    # its own start? An in-progress run is excluded — it has not had its chance yet, and counting it would
    # make the alarm fire on every tick's first 30 seconds.
    completed = [(t, r) for t, r in started if r.get("conclusion")]
    last_done_t, last_done = completed[-1] if completed else (None, None)
    out["last_completed_run_et"] = _et(last_done_t) if last_done_t else None
    out["last_completed_conclusion"] = (last_done or {}).get("conclusion")
    # Small grace: the artifact is written mid-run, so compare against the run's start, not its end.
    refreshed = bool(gen and last_done_t and gen >= last_done_t)
    out["last_run_refreshed_artifact"] = refreshed if last_done_t else None

    # ── verdict ──
    if age is None:
        out["verdict"], out["ok"] = "NO-ARTIFACT", False
        out["detail"] = ("the progress artifact is missing or carries no `_generated_utc`, so supervision "
                         "cannot be established at all.")
        return out

    # A completed run that did not refresh the artifact is a hard failure REGARDLESS OF AGE — that is the
    # whole point. Today's incident sat at 115 min stale, well inside any throttle-honest age window.
    if last_done_t is not None and not refreshed:
        out["ok"] = False
        if out["last_completed_conclusion"] == "failure":
            out["verdict"] = "FAILING"
            out["detail"] = (f"a run of {TICK_WORKFLOW} started {_et(last_done_t)} and FAILED, and the "
                             f"artifact is still stamped {_et(gen)} — the tick ran and measured nothing, so "
                             f"the fleet is unsupervised no matter how recently the cron fired. The tick's "
                             f"CODE is broken: read that run's FIRST red step.")
        else:
            out["verdict"] = "STALE-BUT-RUNS-GREEN"
            out["detail"] = (f"a run started {_et(last_done_t)} and reported "
                             f"{out['last_completed_conclusion']}, yet the artifact is still stamped "
                             f"{_et(gen)} — the tick went green WITHOUT measuring, which is exactly what "
                             f"assert_progress_fresh.py exists to prevent. Check it is still wired in.")
        return out

    if runs is None and age > stale_min:
        out["verdict"], out["ok"] = "STALE-CAUSE-UNKNOWN", False
        out["detail"] = (f"the artifact is {age:.0f} min old and the Actions API could not be read, so "
                         f"ABSENT and FAILING cannot be separated. Treated as unsupervised.")
        return out

    # Nothing has even started. Age is the right signal for exactly this one case.
    if since_start is None or since_start > absent_min:
        out["verdict"], out["ok"] = "ABSENT", False
        out["detail"] = (f"no run of {TICK_WORKFLOW} has started in "
                         f"{'ever' if since_start is None else f'{since_start:.0f} min'} (artifact "
                         f"{age:.0f} min old) — the SCHEDULER is not delivering, so fixing the tick's code "
                         f"would be the wrong response. Dispatch it manually; treat the cron as unreliable.")
        return out

    if age > stale_min:
        out["verdict"], out["ok"] = "STALE-CAUSE-UNKNOWN", False
        out["detail"] = (f"the artifact is {age:.0f} min old, past the {stale_min:.0f} min window, and "
                         f"neither an absent scheduler nor a failing run explains it.")
        return out

    out["verdict"], out["ok"] = "FRESH", True
    out["detail"] = (f"the last completed run ({_et(last_done_t)}) refreshed the artifact to {_et(gen)}, "
                     f"{age:.0f} min ago — the fleet really was measured.")
    return out


def render(v: dict) -> str:
    live, usd = v.get("live_instances"), v.get("realised_usd_so_far")
    lines = [
        f"[fleet-alarm] read at {v['et']}",
        f"[fleet-alarm] artifact generated : {v.get('artifact_generated_et')} "
        f"({v.get('artifact_age_min')} min old, threshold {v['stale_min_threshold']:.0f} min)",
        f"[fleet-alarm] last run started   : {v.get('last_run_started_et')} "
        f"({v.get('min_since_any_run_started')} min ago)",
        f"[fleet-alarm] last SCHEDULED run : {v.get('last_scheduled_run_et')}",
        f"[fleet-alarm] scheduled delivery gaps (min, oldest->newest): {v.get('scheduled_delivery_gaps_min')}"
        f"   <- nominal cron is every 20 min; this is what GitHub ACTUALLY delivers",
        f"[fleet-alarm] fleet at last measurement: live_instances={live}  realised=${usd}",
        f"[fleet-alarm] VERDICT {v['verdict']}: {v['detail']}",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--progress", default="step1-fanout-progress.json")
    ap.add_argument("--stale-min", type=float, default=DEFAULT_STALE_MIN)
    ap.add_argument("--absent-min", type=float, default=DEFAULT_ABSENT_MIN)
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--workflow", default=TICK_WORKFLOW)
    ap.add_argument("--json", default=None, help="also write the verdict here, so the alarm's own runs are auditable")
    a = ap.parse_args(argv)

    try:
        with open(a.progress) as f:
            progress = json.load(f)
    except (OSError, json.JSONDecodeError):
        progress = None

    v = classify(progress, fetch_runs(a.repo, a.workflow),
                 datetime.datetime.now(datetime.timezone.utc), a.stale_min, a.absent_min)
    print(render(v))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(v, f, indent=2)
            f.write("\n")
    if v["ok"]:
        return 0
    # ::error:: so the verdict is on the run summary, not only in a log tail. The non-zero exit is the part
    # that actually reaches a human: GitHub emails the repo owner when a SCHEDULED workflow fails.
    print(f"::error::FLEET UNSUPERVISED [{v['verdict']}] — {v['detail']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
