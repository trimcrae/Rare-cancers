#!/usr/bin/env python3
"""RESTART ANY LANE'S SUPERVISION LOOP THAT IS GONE WHILE ITS HOSTS ARE STILL BILLING.

★★ WHY THIS EXISTS, and it is the fourth instance of one shape in a single day (2026-08-01). Four separate
failures, all "a supervisor that looks healthy while supervising nothing":

  1. the step-1 supervisor's chain broke and nothing restarted it (~19 h outage);
  2. the GCP lane's tick could reap but structurally could never launch;
  3. the selcal lane went silent 77 min while two hosts billed;
  4. a `cofold_watch` can exit down a path that does not re-arm, leaving a billing host unwatched.

`step1-fanout-autoscale.yml`'s `resurrect-supervisor` job already solves (1) for exactly ONE lane, and it is
the working precedent: something OUTSIDE the loop notices the loop is gone and restarts it. This module is
that job generalised — the same predicate, the same fail-closed rule, applied to every lane whose supervision
is a dispatchable long-running watch.

★★ THE ONE THING THIS MODULE REFUSES TO DO: INFER A LOOP'S LIVENESS FROM ITS ARTIFACT'S FRESHNESS.
Measured today, and it is why a naive version of this file would have made things worse. At 2:25 PM ET the
selcal lane's census was 24 minutes stale while host `46524315` billed — the exact signature of a dead watch —
and the watch was ALIVE. Run 30711255780 was `in_progress` at 36+ minutes; it had simply checked out sha
`31defb65`, a vintage of `selcal_vast_launch.py` in which `_tick_publish` does not exist (verified:
`git cat-file -p 31defb6568:research/modalities/selcal_vast_launch.py | grep -c _tick_publish` -> 0), so it
committed nothing until its window ended. A resurrector keyed on staleness would have dispatched a SECOND
supervisor onto a lane that already had one — two loops holding the same cadence against one Vast API key,
which is the hazard the lane's own concurrency group exists to prevent.

  ⛔ A STALE ARTIFACT IS EVIDENCE ABOUT THE PUBLISHER, NOT ABOUT THE LOOP.
  ✅ THE LIVENESS SIGNAL IS THE ACTIONS API'S OWN `queued`/`in_progress` STATE — the same signal
     `resurrect-supervisor` uses, and the only one that distinguishes *loop alive, publishing stale* from
     *loop gone*.

★ WHY THE TRIGGER IS "A LIVE HOST", NOT THE ALARM'S `UNSUPERVISED-BILLING` VERDICT. `account_orphan_alarm.py`
already DETECTS this condition and is deliberately report-only; consuming its verdict is a legitimate design
and this module does consume its report — but for the HOST COUNT (`n_live`), not for the verdict. The verdict
is a conjunction of "host alive" AND "artifact stale", and the staleness half is exactly the inference struck
out above. Keying on it would (a) fire on the false positive measured today, and (b) MISS the true positive it
is supposed to catch: a lane whose census is FRESH — because a $0 collect tick just wrote it — and whose watch
loop is nonetheless gone. `n_live > 0` plus "no live watch run" catches both. The verdict is reported beside
the decision so a reader can see what the alarm thought; it never gates the dispatch.

★ THE ALARM'S OWN CONSERVATISM IS INHERITED, NOT RE-DERIVED. If the account census is stale or unreadable the
alarm suppresses its lane verdicts and says so; this module then sees no trustworthy `n_live` and dispatches
NOTHING. An unreadable world is never a reason to act.

WHAT IT MAY DISPATCH, AND WHY THAT IS SAFE. Only modes that CANNOT rent — pinned by AST in
`tests/test_supervisor_resurrect.py`, the same technique that pins the account alarm as report-only. A
supervision mode reaps, reads and reports; if resurrecting a lane could buy a host, an API blip would become a
purchase. `cofold_watch` calls `mode_reap` and `_live_labels` and never `submit`.

FOUR CONTROLS, and each is a test rather than a claim (CLAUDE.md §4 — a guard nobody has watched fail is not
known to work):

    live host, no live watch      -> DISPATCH        (the outage this exists to end)
    live host, watch alive/queued -> SKIP supervisor_alive     (never two loops on one lane)
    no live host                  -> SKIP no_live_hosts        (nothing to supervise, nothing dispatched)
    liveness unreadable           -> SKIP liveness_unreadable  (fail CLOSED: assume alive, warn once)

`queued` counts as ALIVE for the same reason it does in `resurrect-supervisor`: these lanes' concurrency
groups are `cancel-in-progress: false`, so a successor dispatched during a handoff sits queued rather than
collapsing — and a hand-dispatched recovery run sits queued behind the running loop. Treating queued as dead
is how a resurrector becomes the duplicate-supervisor generator.

CLI:  python3 supervisor_resurrect.py [--root DIR] [--report PATH] [--json OUT] [--dry-run]
Exit 0 always unless --strict: a watchdog that fails its own job loudly still must not fail the tick it rides.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

#: The alarm's committed report. READ ONLY — this module never writes it and never changes the alarm.
ALARM_REPORT = "account-orphan-alarm.json"
#: This module's own readout. A decision nobody can date is a decision nobody can audit.
READOUT = "supervisor-resurrect.json"

#: How old the alarm's report may be before its host counts stop being believable. A report older than this
#: means the thing that refreshes it has itself stopped — in which case this module knows nothing about live
#: hosts and must not act on the last thing it saw.
#:
#: ★ MEASURED, NOT GUESSED: over the 30 most recent commits of `account-orphan-alarm.json` on `main`
#: (2026-08-01) the DELIVERED gaps were median 7.3 min, p90 8.9, max 9.2 — the alarm rides every step-1 tick.
#: 25 min is ~2.7x the worst delivered gap, so ordinary jitter (and the throttling CLAUDE.md §6 warns about)
#: cannot trip it, while a genuinely stopped refresher does. Re-measure with:
#:   git log origin/main --format=%at -30 -- research/modalities/account-orphan-alarm.json
#: ⚠ THE FAILURE THIS BOUNDS IS REAL AND WAS SEEN TODAY: at 2:39 PM ET the committed report still said the
#: selcal lane held 1 live host, seven minutes after that host had been reaped. Acting on a memory of the
#: account is not acting on the account.
REPORT_STALE_MIN = 25.0

#: US Eastern, the only timezone this repo reports in (CLAUDE.md §1). EDT = UTC-4.
ET_OFFSET_H = -4.0

# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# the registry — one entry per lane whose supervision is a DISPATCHABLE long-running watch
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# ⚠ WHY THIS IS NOT "every lane in `account_orphan_alarm.ACCOUNT_LANES`". Most lanes there have no restartable
# supervisor at all — a lane whose progress is driven by a cron tick has nothing for this module to restart,
# and dispatching its tick would be a different act with a different blast radius. Naming the lanes that DO
# have one keeps the decision auditable; a lane absent from here is reported as `not_resurrectable` rather
# than silently skipped, so forgetting to register a new watch lane is LOUD (the same argument as the alarm's
# explicit registry).
#
# FIELDS
#   lane        MUST match a key in `account_orphan_alarm.ACCOUNT_LANES` — that is where `n_live` comes from.
#   workflow    the workflow file whose run is the supervision loop.
#   inputs      the dispatch inputs, NAMED EXPLICITLY AND IN FULL. Omitting an input is what silently
#               disabled placement on seven green ticks on 2026-07-27: an absent input reads as null. A
#               resurrected supervisor must hold the same cadence as a hand-started one.
#   watch_jobs  which JOB names inside that workflow constitute "the loop is running". The selcal workflow
#               splits `cpu` ($0 modes, 25-40 s) from `gpu` (the renting and supervising modes), and only the
#               latter can be a supervision loop — so a 30-second `cofold_collect` run must not read as a
#               live watch. Empty tuple = any queued/in-progress run of the workflow counts.
#   rents       AST-pinned FALSE. See the module docstring: a resurrector that can buy is not a watchdog.
RESURRECTABLE: list[dict] = [
    {
        "lane": "selcal-cofold",
        "label": "Selectivity control — SMARCA2/4 co-fold panel (Vast)",
        "workflow": "selectivity-control-vast.yml",
        "mode": "cofold_watch",
        # `watch_minutes` is named rather than left blank: blank means the module default (55), and a
        # resurrected watch that silently ran a different window than the hand-started one would make the
        # re-arm cadence unreproducible.
        "inputs": {"mode": "cofold_watch", "watch_minutes": "55"},
        "watch_jobs": ("gpu",),
        "why": ("`mode_cofold_watch` is the only thing that reaps this lane's co-fold hosts, and every one of "
                "its exit paths leaves the hosts running — the host cannot stop its own billing (CLAUDE.md "
                "§6). Two of those paths do not re-arm."),
    },
]


def _utcnow(t=None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t if t is not None else time.time()))


def _et(t=None) -> str:
    """US Eastern, 12-hour (CLAUDE.md §1). Never UTC, never 24-hour."""
    return time.strftime("%-I:%M %p ET %a %b %-d, %Y",
                         time.gmtime((t if t is not None else time.time()) + ET_OFFSET_H * 3600))


def _parse_iso(s):
    if not isinstance(s, str) or not s:
        return None
    try:
        return time.mktime(time.strptime(s.strip().rstrip("Z"), "%Y-%m-%dT%H:%M:%S")) - time.timezone
    except (ValueError, OverflowError):
        return None


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# the decision — PURE, so all four controls are testable without a network
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
def lane_hosts(report, lane):
    """(n_live, alarm_verdict, why_not) for one lane, from the alarm's committed report. PURE.

    ⚠ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4). Every path that cannot MEASURE the host
    count returns `None`, never 0 — a lane whose count is unknown is not a lane with no hosts, and the caller
    must be able to tell those apart. Returning 0 here on an unreadable report would read as "nothing is
    billing" and silently retire the whole watchdog."""
    if not isinstance(report, dict):
        return None, None, "the alarm report is not readable as an object"
    # The alarm suppresses every lane verdict when the account census itself is stale or unreadable, and says
    # so at the top level. Inherit that rather than re-deriving it: if it could not grade the account, this
    # module knows nothing about live hosts.
    top = str(report.get("verdict") or "")
    if top in ("CENSUS-UNKNOWN", "CENSUS-STALE"):
        return None, top, "the alarm could not grade the account census (%s), so no lane host count is trusted" % top
    lanes = report.get("lanes")
    if not isinstance(lanes, list):
        return None, top, "the alarm report carries no per-lane verdicts"
    for lv in lanes:
        if isinstance(lv, dict) and lv.get("lane") == lane:
            n = lv.get("n_live")
            if not isinstance(n, int):
                return None, lv.get("verdict"), "the alarm reports no integer `n_live` for this lane"
            return n, lv.get("verdict"), None
    return None, top, "lane %r does not appear in the alarm's registry" % lane


def report_age_min(report, now=None):
    """Minutes since the alarm report was generated, or None if it carries no usable stamp. PURE."""
    t = _parse_iso((report or {}).get("generated_utc")) if isinstance(report, dict) else None
    if t is None:
        return None
    return round(((now if now is not None else time.time()) - t) / 60.0, 1)


def decide(report, live_watches, lanes=None, now=None, stale_after_min=REPORT_STALE_MIN):
    """One decision per registered lane. PURE — no network, no clock beyond `now`, no dispatch.

    `live_watches`: lane key -> number of queued/in-progress supervision runs, or **None for UNREADABLE**.
    The distinction is the whole point: 0 means "measured, none alive" and is the only value that licenses a
    dispatch; None means the Actions API did not answer and we assume a loop IS alive (fail closed).
    """
    lanes = RESURRECTABLE if lanes is None else lanes
    age = report_age_min(report, now)
    out = []
    for spec in lanes:
        lane = spec["lane"]
        n_live, verdict, why_hosts = lane_hosts(report, lane)
        live = live_watches.get(lane, None) if isinstance(live_watches, dict) else None
        d = {"lane": lane, "label": spec.get("label"), "workflow": spec["workflow"],
             "mode": spec.get("mode"), "alarm_verdict": verdict, "n_live_hosts": n_live,
             "live_watch_runs": live, "report_age_min": age, "dispatch": False}

        # ── ORDER MATTERS, and this is the order the controls are written in. Liveness is asked FIRST because
        # an unreadable Actions API is the one state where nothing else can license an action: even a lane
        # that is certainly billing must not get a second supervisor when we cannot see the first.
        if live is None:
            d.update(action="SKIP", reason="liveness_unreadable",
                     detail=("the Actions API did not return a run list for %s, so whether a supervisor is "
                             "alive is UNKNOWN. Failing CLOSED (assume alive): a missed resurrection is "
                             "recovered on the next tick, a storm of duplicate supervisors is not."
                             % spec["workflow"]))
        elif age is not None and age > stale_after_min:
            d.update(action="SKIP", reason="report_stale",
                     detail=("the alarm report is %.1f min old (> %.0f), so its host counts describe a past "
                             "account. The thing that refreshes it has itself stopped — that is the incident, "
                             "and dispatching off a stale count would be acting on a memory."
                             % (age, stale_after_min)))
        elif n_live is None:
            d.update(action="SKIP", reason="hosts_unreadable",
                     detail="%s. An absent reading is not a reading of absence (CLAUDE.md §4): this is not "
                            "evidence that nothing is billing, and it is not licence to dispatch either."
                            % (why_hosts or "the lane's live-host count is unreadable"))
        elif n_live <= 0:
            d.update(action="SKIP", reason="no_live_hosts",
                     detail="no host wearing this lane's label prefix is live, so there is nothing to "
                            "supervise and nothing is dispatched. A watch with no fleet is pure noise.")
        elif live > 0:
            d.update(action="SKIP", reason="supervisor_alive",
                     detail=("%d supervision run(s) of %s are queued or in progress — `queued` counts as "
                             "alive on purpose (cancel-in-progress: false, so a successor waits rather than "
                             "collapsing). A stale artifact is evidence about the publisher, not about the "
                             "loop: on 2026-08-01 this lane's census was 24 min stale while its watch ran "
                             "36+ min, because that run predated `_tick_publish`."
                             % (live, spec["workflow"])))
        else:
            d.update(action="DISPATCH", dispatch=True, reason="unsupervised_billing",
                     inputs=dict(spec.get("inputs") or {}),
                     detail=("%d host(s) are billing on this lane and NO run of %s is queued or in progress — "
                             "the supervision loop is gone while the meter runs. %s"
                             % (n_live, spec["workflow"], spec.get("why") or "")))
        out.append(d)
    return out


# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
# the probe and the dispatch — the only impure parts
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════
REPO = os.environ.get("GITHUB_REPOSITORY") or "trimcrae/Rare-cancers"
_API = "https://api.github.com/repos/%s" % REPO


def _api_get(path, token=None, timeout=25):
    import urllib.error
    import urllib.request
    h = {"Accept": "application/vnd.github+json", "User-Agent": "supervisor-resurrect"}
    if token:
        h["Authorization"] = "Bearer %s" % token
    req = urllib.request.Request(_API + path, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as fh:
            return json.load(fh)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        print("[resurrect] API read failed for %s (%s) — that is UNREADABLE, not empty" % (path, e),
              flush=True)
        return None


def probe_live_watches(spec, token=None, get=None):
    """How many supervision runs of this lane's workflow are queued or in progress. None = UNREADABLE.

    ⚠ WHY THE JOB NAMES MATTER. The selcal workflow's `cpu` job runs the $0 modes and finishes in 25-40 s;
    only its `gpu` job can hold a supervision loop. Counting any in-progress run would let a 30-second
    `cofold_collect` mask a watch that is genuinely gone — the mirror image of the staleness mistake, and
    just as wrong. A `queued` run has no started job yet, so it counts as alive on its own.

    ⚠ AND THE FAIL-CLOSED DIRECTION IS DELIBERATE at every step: a run whose job list cannot be read counts
    as ALIVE, because "I could not look inside" must never license a second supervisor."""
    get = get or (lambda p: _api_get(p, token))
    wf = spec["workflow"]
    want = set(spec.get("watch_jobs") or ())
    n = 0
    for status in ("queued", "in_progress"):
        page = get("/actions/workflows/%s/runs?status=%s&per_page=30" % (wf, status))
        if not isinstance(page, dict) or not isinstance(page.get("workflow_runs"), list):
            return None
        for run in page["workflow_runs"]:
            rid = run.get("id")
            if status == "queued" or not want or rid is None:
                n += 1
                continue
            jobs = get("/actions/runs/%s/jobs" % rid)
            if not isinstance(jobs, dict) or not isinstance(jobs.get("jobs"), list):
                n += 1  # unreadable job list -> assume this run IS the supervisor
                continue
            if any(j.get("name") in want and j.get("status") in ("queued", "in_progress")
                   for j in jobs["jobs"]):
                n += 1
    return n


def dispatch(spec, token, ref="main", post=None):
    """Fire the lane's supervision workflow. Returns (ok, detail). Never raises."""
    import urllib.error
    import urllib.request
    if not token:
        return False, "no GITHUB_TOKEN — cannot dispatch %s" % spec["workflow"]
    body = json.dumps({"ref": ref, "inputs": dict(spec.get("inputs") or {})}).encode()
    if post is not None:
        return post(spec, body)
    req = urllib.request.Request(
        "%s/actions/workflows/%s/dispatches" % (_API, spec["workflow"]),
        data=body, method="POST",
        headers={"Authorization": "Bearer %s" % token, "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "User-Agent": "supervisor-resurrect"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True, "dispatched %s %s" % (spec["workflow"], spec.get("inputs"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return False, "dispatch of %s FAILED (%s)" % (spec["workflow"], e)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Restart any lane's supervision loop that is gone while its "
                                             "hosts are still billing.")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--report", default=None, help="path to account-orphan-alarm.json")
    ap.add_argument("--json", default=None, help="where to write this run's readout")
    ap.add_argument("--ref", default=os.environ.get("GIT_BRANCH") or "main")
    ap.add_argument("--dry-run", action="store_true", help="decide and report; dispatch nothing")
    ap.add_argument("--now", default=None)
    args = ap.parse_args(argv)

    rpath = args.report or os.path.join(args.root, ALARM_REPORT)
    try:
        with open(rpath) as fh:
            report = json.load(fh)
    except (OSError, ValueError) as e:
        print("[resurrect] could not read %s (%s) — nothing is graded and nothing is dispatched. This is "
              "UNREADABLE, not 'no hosts'." % (rpath, e), flush=True)
        report = None

    now = _parse_iso(args.now) if args.now else time.time()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    live = {}
    for spec in RESURRECTABLE:
        live[spec["lane"]] = probe_live_watches(spec, token)
    decisions = decide(report, live, now=now)

    for d in decisions:
        spec = next(s for s in RESURRECTABLE if s["lane"] == d["lane"])
        if d["dispatch"] and not args.dry_run:
            ok, detail = dispatch(spec, token, ref=args.ref)
            d["dispatched"], d["dispatch_detail"] = ok, detail
            if ok:
                print("::warning title=LANE SUPERVISION WAS DOWN — RESTARTED::%s had %s host(s) billing and "
                      "no queued or in-progress run of %s. A fresh `%s` was dispatched. This warning is the "
                      "signal that a watch loop exited without re-arming; if it repeats, read the previous "
                      "run's tail." % (d["lane"], d["n_live_hosts"], d["workflow"], d.get("mode")), flush=True)
            else:
                print("::error title=LANE SUPERVISION DOWN AND COULD NOT BE RESTARTED::%s — %s. %s host(s) "
                      "are billing unwatched; dispatch `%s` by hand."
                      % (d["lane"], detail, d["n_live_hosts"], d.get("mode")), flush=True)
        elif d["dispatch"]:
            d["dispatched"], d["dispatch_detail"] = False, "--dry-run"
        if d["reason"] == "liveness_unreadable":
            print("::warning title=SUPERVISOR LIVENESS UNREADABLE::%s — %s" % (d["lane"], d["detail"]),
                  flush=True)
        print("[resurrect] %-16s %-8s %-22s hosts=%s watches=%s | %s"
              % (d["lane"], d["action"], d["reason"], d["n_live_hosts"], d["live_watch_runs"], d["detail"]),
              flush=True)

    out = {"_what": "Which lanes had a billing host with no supervision loop alive, and what was done. "
                    "Liveness comes from the Actions API, NEVER from an artifact's freshness.",
           "generated_utc": _utcnow(now), "generated_et": _et(now),
           "alarm_report": os.path.basename(rpath), "alarm_report_age_min": report_age_min(report, now),
           "report_stale_after_min": REPORT_STALE_MIN, "dry_run": bool(args.dry_run),
           "decisions": decisions}
    opath = args.json or os.path.join(args.root, READOUT)
    try:
        with open(opath, "w") as fh:
            json.dump(out, fh, indent=1)
            fh.write("\n")
    except OSError as e:
        print("[resurrect] could not write %s (%s)" % (opath, e), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
