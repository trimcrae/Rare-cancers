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
    FRESH-API-UNREADABLE — the artifact is recent, but the run history could not be read to confirm WHICH run
                           wrote it. Supervision is evidenced, on weaker evidence, and the verdict says so.
    FRESH                — the last completed run did refresh it.
The run history comes from the public Actions API, which needs no token on a public repo.

★★ AN UNREADABLE API IS NOT A DEAD SCHEDULER — AND SAYING SO COST A FALSE ALARM (2026-07-27, 4:18 PM ET).
`fetch_runs` returning None already meant "could not ask", and `classify` already had a branch to honour
that — but the branch was gated behind `age > stale_min`, so it only ever protected a STALE artifact. With a
FRESH one the guard was skipped entirely and control fell through to the `since_start is None` test, which
reads an unasked question as a measured zero and announces:

    FLEET UNSUPERVISED [ABSENT] — no run of step1-fanout-autoscale.yml has started in ever (artifact 3 min old)

...in a run that was itself a run of that workflow, over an artifact that run had written 2.8 minutes earlier.
The tick's own job was fully green: measure, reap, place and commit all succeeded. Seven minutes later the
identical script on the sibling schedule read the API fine and returned FRESH. So the alarm was not detecting
an outage, it was manufacturing one — the precise "unmeasured state reported as a measured zero" defect its
own `fetch_runs` docstring warns about, reintroduced one branch lower down.

Three things changed, and the ordering one is the actual fix:
  1. THE `runs is None` GUARD NOW RUNS BEFORE THE ABSENT TEST, AT EVERY AGE. Unreadable can no longer reach a
     scheduler verdict, whatever the artifact's age.
  2. THE REASON IS CARRIED, NOT SWALLOWED. `fetch_runs` returned a bare None, so the log could not say whether
     the API 403'd, timed out, or honestly returned zero runs — the 4:18 PM log is identical under all three,
     which is why the cause had to be reconstructed from a sibling run instead of read off the page. It now
     returns `(runs, error)` and the error is printed and stored in the verdict JSON.
  3. IT AUTHENTICATES WHEN IT CAN. Anonymous GitHub API is limited per SOURCE IP, and Actions runner IPs are
     shared, so this call competes with every other tenant on that runner — and the embedded copy of this
     alarm fires on EVERY autoscale tick (~30 today). `GITHUB_TOKEN` raises the ceiling to 1000/h per repo and
     is a header, not a dependency, so the zero-dependency property below is untouched. Absent token → falls
     back to anonymous, plus a short retry ladder.

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
import os
import sys
import time
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
    return ts.astimezone(ET).strftime("%I:%M %p ET %b %d, %Y").lstrip("0").replace(" 0", " ")


def _parse_z(s: str) -> datetime.datetime | None:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def fetch_runs(repo: str, workflow: str, per_page: int = 20,
               attempts: int = 3) -> tuple[list[dict] | None, str | None]:
    """Recent runs from the Actions API, as `(runs, error)`. `runs is None` means it could not be read.

    None is "could not ask", never "no runs" — reporting an unmeasured state as a measured zero is this
    repo's most expensive defect class, and on 2026-07-27 it did exactly that here (see the module docstring):
    an unreadable API was announced as "the SCHEDULER is not delivering" while the tick was green.

    ⚠ THE ERROR STRING IS THE POINT, NOT DECORATION. The previous version swallowed the exception, so a 403,
    a timeout and an honest empty list all printed the same line and the cause had to be inferred from a
    neighbouring run. Whatever this returns, the caller can now say WHY.

    Authenticates with GITHUB_TOKEN when present: anonymous limits are per source IP and Actions runner IPs
    are shared between tenants, which is the failure this is most exposed to. A header is not a dependency —
    the module still imports nothing outside the stdlib and nothing from the lane it watches.
    """
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?per_page={per_page}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "fleet-supervision-alarm"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last = None
    for i in range(max(1, attempts)):
        if i:
            time.sleep(min(2 ** i, 8))
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.loads(r.read().decode())
            runs = body.get("workflow_runs")
            if runs is None:
                # A 200 with no `workflow_runs` key is a malformed answer, not an empty history. Treating it
                # as [] would resurrect the measured-zero bug through the one door the retry ladder cannot see.
                last = "HTTP 200 but no `workflow_runs` key in the response"
                continue
            return runs, None
        except urllib.error.HTTPError as e:
            detail = "rate limit (anonymous limits are per shared runner IP)" if e.code in (403, 429) else ""
            last = f"HTTP {e.code} {e.reason}{' — ' + detail if detail else ''}"
        except (urllib.error.URLError, TimeoutError) as e:
            last = f"{type(e).__name__}: {getattr(e, 'reason', e)}"
        except (ValueError, OSError) as e:
            last = f"{type(e).__name__}: {e}"
    return None, f"{last} (after {max(1, attempts)} attempts, token={'yes' if token else 'no'})"


def classify(progress: dict | None, runs: list[dict] | None, now: datetime.datetime,
             stale_min: float, absent_min: float, fetch_error: str | None = None,
             armed: dict | None = None) -> dict:
    """Decide WHY supervision is or is not happening. Pure — all I/O is done by the caller, so this is tested."""
    out: dict = {"utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "et": _et(now),
                 "stale_min_threshold": stale_min, "absent_min_threshold": absent_min,
                 "runs_readable": runs is not None, "fetch_error": fetch_error}

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
    # ★★ IS THERE ANYTHING TO SUPERVISE AT ALL? THIS TEST COMES FIRST, AND IT IS THE ONE THIS MODULE WAS
    # MISSING FOR 19 DAYS (measured 2026-08-25).
    #
    # ⛔ THE COLLISION, STATED PLAINLY, BECAUSE BOTH HALVES ARE CORRECT IN ISOLATION. On 2026-08-06
    # `fleet_armed.py` landed and `publish_artifacts.sh` began SKIPPING the heartbeat commit while the
    # account holds zero instances — right, and trimcrae asked for it ("Why would we need supervision for
    # tests that aren't running?"). But `_generated_utc` on that artifact is the ONLY input to the staleness
    # verdict below, and the autoscale workflow's own comment says so two lines above the change: "a tick
    # whose artifacts were all absent published no heartbeat at all, and so read as a tick that never ran."
    # Idle-suppression therefore re-armed the exact landmine that comment was written to disarm.
    #
    # ⚠ THE EVIDENCE, NOT THE STORY. The frozen artifact is stamped 2026-08-06T22:31:27Z — the day
    # idle-suppression landed — and from then to 2026-08-25 this alarm returned FAILING on every tick,
    # naming a cause that was false ("The tick's CODE is broken"). Measured on 2026-08-25: 30 of the last 30
    # autoscale runs red, ~11 runs/hour, each one emailing and each one re-dispatching the supervision chain
    # under `if: always()`. The alarm was not reporting an outage; it WAS the outage.
    #
    # ⛔ AND THIS IS NOT A LOOSENED GATE — IT IS THE SAME GATE ASKED A PRIOR QUESTION. `fleet_armed.state()`
    # is FAIL-ARMED by construction: a census that is missing, unreadable, stale, or short a field returns
    # ARMED, as does any non-zero instance count. So this branch can only ever be taken on a FRESH
    # account-level reading of zero hosts — the one state in which "the fleet is unsupervised" is not a
    # finding about anything. The caller passes None on any doubt, which reproduces today's behaviour
    # exactly. Nothing that costs money is gated here: the tick has already run and already acted.
    if armed is not None and armed.get("armed") is False:
        out["verdict"], out["ok"] = "QUIET-NOTHING-TO-SUPERVISE", True
        out["armed"] = False
        out["armed_why"] = armed.get("why")
        out["armed_evidence"] = armed.get("evidence")
        out["detail"] = (f"there is nothing to supervise — {armed.get('why')}. A stale progress artifact is "
                         f"the CORRECT state here, because `publish_artifacts.sh` deliberately withholds the "
                         f"heartbeat commit while the account is empty; reading that silence as a broken tick "
                         f"is the one mistake this branch exists to prevent. The moment a host appears the "
                         f"census flips this to ARMED and every verdict below applies again, unchanged.")
        return out

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

    # ★★ AN UNASKED QUESTION IS NEVER AN ANSWER — AND THIS TEST MUST COME BEFORE THE SCHEDULER VERDICT.
    # This branch used to carry `and age > stale_min`, which meant it only protected a STALE artifact; with a
    # FRESH one an unreadable API fell through to the ABSENT test below and was announced as a dead scheduler
    # (2026-07-27 4:18 PM ET, over a 2.8-min-old artifact, inside a green tick). Nothing downstream of here
    # may read `runs` — every remaining verdict is derived from run history this function does not have.
    why = f" ({fetch_error})" if fetch_error else ""
    if runs is None:
        if age > stale_min:
            out["verdict"], out["ok"] = "STALE-CAUSE-UNKNOWN", False
            out["detail"] = (f"the artifact is {age:.0f} min old and the Actions API could not be read{why}, "
                             f"so ABSENT and FAILING cannot be separated. Treated as unsupervised.")
            return out
        # The artifact is recent, which is direct positive evidence that SOMETHING measured the fleet — the
        # tick is the only writer of `_generated_utc`. We just cannot apply the run-history discriminator to
        # say which run wrote it, so this is FRESH on weaker evidence and is named differently to admit that.
        # Green is the honest call: failing here would page a human about a fleet that was demonstrably
        # measured minutes ago, and an alarm that cries wolf is the same end state as no alarm.
        out["verdict"], out["ok"] = "FRESH-API-UNREADABLE", True
        out["detail"] = (f"the artifact is only {age:.0f} min old (window {stale_min:.0f} min), so the fleet "
                         f"WAS measured that recently — but the Actions API could not be read{why}, so the "
                         f"run-history check of WHICH run wrote it could not be applied. Not an outage: an "
                         f"unreadable API is not a dead scheduler.")
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
    ]
    # Printed only when it happened, and never silently: a read failure that leaves no trace in the log is
    # what forced the 4:18 PM cause to be reconstructed from a sibling run instead of read off the page.
    if not v.get("runs_readable", True):
        lines.append(f"[fleet-alarm] ⚠ RUN HISTORY UNREADABLE: {v.get('fetch_error')}"
                     f"   <- verdict below is NOT based on run history")
    lines.append(f"[fleet-alarm] VERDICT {v['verdict']}: {v['detail']}")
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

    # ⚠ FAIL-ARMED AT THE BOUNDARY, THE SAME CONTRACT `publish_artifacts.sh` HONOURS. Any exception at all —
    # module missing, census unreadable, a field absent — leaves `armed` as None, and `classify` then behaves
    # exactly as it did before this branch existed. Going quiet because a file could not be read is the
    # fail-quiet direction both this module and `fleet_armed` refuse.
    armed = None
    try:
        import fleet_armed
        armed = fleet_armed.state(lane="step1-fanout-autoscale")
    except Exception as e:  # noqa: BLE001 — any failure here must read as ARMED, never as idle
        print(f"[fleet-alarm] ⚠ arming state unreadable ({e}) — proceeding FAIL-ARMED")

    runs, fetch_error = fetch_runs(a.repo, a.workflow)
    v = classify(progress, runs, datetime.datetime.now(datetime.timezone.utc),
                 a.stale_min, a.absent_min, fetch_error=fetch_error, armed=armed)
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
