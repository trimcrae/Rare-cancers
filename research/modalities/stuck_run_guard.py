#!/usr/bin/env python3
"""Cancel Actions runs that are stuck `pending` with ZERO jobs — they hold a concurrency lock and do nothing.

★★ WHY THIS EXISTS, MEASURED 2026-08-01 (6:07–6:26 PM ET). Sensitivity-control run 30720583406 was dispatched
`mode=launch` at 6:07 PM and sat `status: pending` for **19 minutes** with `total_count: 0` jobs. Everything
that could have explained it was checked and ruled out:

  * its concurrency group is `selcal-launch`; the only other run in that group finished four seconds after it
    was queued, so the group was free for the whole 19 minutes;
  * the repo had **5** runs in flight, nowhere near any concurrent-job cap, and **0** queued;
  * the long-running sibling was `mode=watch` — `self_dispatch` passes `{"mode": mode}`, so that run is in
    `selcal-watch`, a different group;
  * `total_count: 0` means no job was ever created, so this is not a slow runner.

It was a stuck concurrency lock. Cancelling it released the group immediately: the next `launch` dispatched
40 seconds later went straight to `in_progress`.

⛔ WHY THIS IS A SPEND-SAFETY GUARD AND NOT HOUSEKEEPING. **The blocked mode was `launch`, and `launch` is
what re-places a host that died.** A lane whose launch group is wedged looks completely healthy — the watch
ticks, the reaper ticks, the board renders — while every re-placement it asks for is silently swallowed. That
is the "holding silently" failure CLAUDE.md §6 names as worse than the problem it prevents: a fleet that never
launches is indistinguishable from one that finished.

⚠ THE SAFETY ARGUMENT IS `total_count == 0`, AND IT IS EXACT, NOT PRUDENT. A run with no jobs has executed no
step, rented nothing, written nothing and holds no checkpoint; cancelling it cannot destroy work because there
is no work. This module must never widen to runs that HAVE jobs — a `queued` job is a real job waiting for a
runner, and a slow runner is not a stuck lock. The age threshold exists only to avoid racing GitHub's normal
job-creation latency, which is seconds.

Pure stdlib on purpose: this guard watches the supervision layer, so it must not be able to fail for a reason
the supervision layer introduced (the same isolation `account_orphan_alarm` keeps, and for the same reason).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

REPO = os.environ.get("STUCK_RUN_REPO", "trimcrae/Rare-cancers")

#: How long a run may sit `pending` with no jobs before it is considered wedged rather than starting.
#: GitHub normally materialises jobs in seconds; the measured incident sat for 19 minutes. 10 minutes is far
#: outside normal latency and far inside the window where a swallowed re-placement still matters.
STUCK_AFTER_MIN = float(os.environ.get("STUCK_RUN_AFTER_MIN", "10"))

#: Written every tick, cancelling nothing included — a guard with no artifact is indistinguishable from a
#: guard that never ran (the same rule the lane reapers follow).
ARTIFACT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stuck-run-guard.json")

_API = "https://api.github.com/repos/%s" % REPO


def _get(url, token=None, method="GET"):
    req = urllib.request.Request(url, method=method, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "stuck-run-guard",
        **({"Authorization": "Bearer %s" % token} if token else {})})
    with urllib.request.urlopen(req, timeout=30) as fh:
        body = fh.read()
    return json.loads(body) if body else {}


def _age_min(iso, now=None):
    """Minutes since an RFC3339 `...Z` timestamp. PURE apart from the clock, which is injectable.

    `calendar.timegm`, not `time.mktime`: the timestamp is UTC and `mktime` interprets its argument as LOCAL,
    so the correction would be off by the DST offset for half the year — an hour of error in exactly the
    quantity the cancel threshold is compared against."""
    import calendar
    return ((now if now is not None else time.time())
            - calendar.timegm(time.strptime(iso, "%Y-%m-%dT%H:%M:%SZ"))) / 60.0


def is_wedged(run, n_jobs, now=None, after_min=None):
    """PURE. Is this run holding a concurrency lock while doing nothing?

    All three conditions are load-bearing:
      `pending`      — `queued` means GitHub accepted it and is finding a runner; that is normal.
      `n_jobs == 0`  — the safety argument. A run with jobs has work that cancelling would destroy.
      age            — only to avoid racing normal job-creation latency.
    """
    if (run.get("status") or "") != "pending":
        return False
    if n_jobs != 0:
        return False
    created = run.get("created_at") or ""
    if not created:
        return False
    return _age_min(created, now) >= (STUCK_AFTER_MIN if after_min is None else after_min)


def scan(token=None, cancel=True):
    """Find wedged runs and (optionally) cancel them. Returns the record written to `ARTIFACT`."""
    token = token or os.environ.get("GITHUB_TOKEN")
    rec = {
        "_what": "Actions runs found `pending` with ZERO jobs — they hold a concurrency lock and execute "
                 "nothing. Written on every tick, cancelling nothing included.",
        "_why": "Measured 2026-08-01: a selcal `launch` sat pending 19 min with 0 jobs and blocked the group. "
                "`launch` is what re-places a dead host, so the lane looked healthy while every re-placement "
                "was silently swallowed (CLAUDE.md §6 — holding silently).",
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "threshold_min": STUCK_AFTER_MIN, "readable": True,
        "pending_seen": [], "cancelled": [], "cancel_failed": [], "spared": [],
    }
    try:
        runs = _get(_API + "/actions/runs?status=pending&per_page=100", token).get("workflow_runs", [])
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        # ⚠ UNREADABLE IS NOT EMPTY (CLAUDE.md §4). "No pending runs" and "could not ask" are opposite facts.
        rec["readable"] = False
        rec["error"] = "%s: %s" % (type(e).__name__, e)
        _write(rec)
        return rec

    for r in runs:
        rid, name = r.get("id"), (r.get("name") or "")[:60]
        try:
            n_jobs = int(_get("%s/actions/runs/%s/jobs" % (_API, rid), token).get("total_count") or 0)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            rec["spared"].append({"run": rid, "name": name,
                                  "why": "job count UNREADABLE (%s) — never cancel on an absent reading" % e})
            continue
        age = round(_age_min(r.get("created_at") or ""), 1)
        rec["pending_seen"].append({"run": rid, "name": name, "jobs": n_jobs, "age_min": age})
        if not is_wedged(r, n_jobs):
            rec["spared"].append({"run": rid, "name": name, "jobs": n_jobs, "age_min": age,
                                  "why": ("has %d job(s) — a job waiting for a runner is real work, not a "
                                          "stuck lock" % n_jobs) if n_jobs else
                                         "only %.1f min old; below the %.0f min threshold" % (age, STUCK_AFTER_MIN)})
            continue
        if not cancel:
            rec["cancel_failed"].append({"run": rid, "name": name, "why": "dry run"})
            continue
        try:
            _get("%s/actions/runs/%s/cancel" % (_API, rid), token, method="POST")
            rec["cancelled"].append({"run": rid, "name": name, "age_min": age,
                                     "why": "pending %.1f min with 0 jobs — no step ran, nothing rented, "
                                            "nothing to lose; the group it blocked is now free" % age})
            print("[stuck-run] CANCELLED %s (%s) — pending %.1f min, 0 jobs" % (rid, name, age), flush=True)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            rec["cancel_failed"].append({"run": rid, "name": name, "why": "%s: %s" % (type(e).__name__, e)})
            print("::warning title=STUCK RUN NOT CANCELLED::%s has been pending %.1f min with 0 jobs and is "
                  "blocking its concurrency group; the cancel failed (%s). Cancel it by hand."
                  % (rid, age, e), flush=True)
    _write(rec)
    return rec


def _write(rec):
    with open(ARTIFACT, "w") as fh:
        json.dump(rec, fh, indent=2)
        fh.write("\n")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rec = scan(cancel="--dry-run" not in argv)
    print(json.dumps({k: v for k, v in rec.items() if not k.startswith("_")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
