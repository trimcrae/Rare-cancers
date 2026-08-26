#!/usr/bin/env python3
"""Read whether `main`'s trunk gate is green, and write the verdict `health.py` cannot measure itself.

⛔ WHY THIS IS A SEPARATE FILE AND NOT A FUNCTION IN `health.py`. `health.py` is stdlib-only with no
network BY DESIGN: it has to keep working when everything else has stopped, which is the only
condition under which anyone reads it. So it takes the trunk's gate verdict as a FILE from a caller
that does have the network — the same shape `alarm_state.py` takes `--fleet-verdict`. This is that
caller, and it runs only inside `autonomy-tick.yml`, which has a GITHUB_TOKEN and `actions: read`.

★ THE ROW THIS EXISTS TO CLOSE HAD NEVER BEEN MEASURED ONCE. Every board this loop has written
carries `gates_green: NO-GATE-VERDICT / unmeasured`, and `health.py --check` counts it in a line
reading "1 UNMEASURED ['gates_green'] — unmeasured is not ok". CLAUDE.md §4: a row reading UNKNOWN is
an unanswered question wearing the costume of a status, and this one costs a $0 API read.

⛔ AND IT FAILS CLOSED, LOUDLY. If the API errors, rate-limits, or returns something this cannot
parse, NO FILE IS WRITTEN and the row stays `unmeasured`. A guessed "probably green" is strictly
worse than the unmeasured it replaces: `gates_green` is what stops a cycle from trying to commit onto
a red trunk, so a false green sends every cycle into a gate failure it was supposed to be spared.

Usage (from the Actions tick only):
    python3 research/autonomy/gates_verdict.py --out /tmp/gates.json
    python3 research/autonomy/gates_verdict.py --out /tmp/gates.json --dry-run   # print, write nothing

Exit 0 always. A verdict this could not read must not fail the tick that also publishes the board and
sends the stall alarm — losing those to a bad API minute would remove the pull channel AND the push
channel to fix a row that is merely unmeasured.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import urllib.error
import urllib.request

#: The authority on whether the trunk is green. CLAUDE.md §6: `tests.yml` runs BOTH suites in full on
#: every push with the real dependencies, and it — not a local preflight — is what decides `main`.
WORKFLOW = "tests.yml"
REPO = os.environ.get("GITHUB_REPOSITORY", "trimcrae/Rare-cancers")
BRANCH = "main"

#: ⚠ `cancelled` and `skipped` are NOT verdicts. A cancelled run says the trunk was never tested, not
#: that it passed and not that it failed, and letting one stand as either is how a concurrency-group
#: cancellation gets read as a green trunk.
VERDICT_CONCLUSIONS = {"success", "failure", "timed_out", "startup_failure"}
GREEN = {"success"}


def decide(runs: list, now: datetime.datetime) -> dict:
    """Pure function over the API's run list (newest first) -> the verdict file's contents.

    Kept pure so the whole decision is testable with no network and no token, and so `--dry-run`
    exercises the REAL logic rather than a parallel copy of it.
    """
    graded = [r for r in runs
              if r.get("status") == "completed" and r.get("conclusion") in VERDICT_CONCLUSIONS]
    if not graded:
        return {"_no_verdict": "no completed, graded run of %s on %s in the window read — cancelled "
                               "and skipped runs are not verdicts" % (WORKFLOW, BRANCH)}

    latest = graded[0]
    ok = latest.get("conclusion") in GREEN
    ref = "%s @ %s" % (WORKFLOW, str(latest.get("head_sha") or "")[:12])
    checked = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if ok:
        return {"ok": True, "red_since_utc": None, "ref": ref, "checked_utc": checked,
                "detail": "the trunk is green: %s concluded `success` on %s at %s."
                          % (WORKFLOW, BRANCH, latest.get("updated_at"))}

    # ⚠ AGE IT ON THE OLDEST CONTIGUOUS FAILURE, NOT THE NEWEST. Every push makes a new run, so
    # dating the redness from the latest one would reset the clock on every commit and a trunk red
    # for three days would report as red for ten minutes, forever inside the grace window.
    since = latest.get("created_at")
    for r in graded:
        if r.get("conclusion") in GREEN:
            break
        since = r.get("created_at")

    exhausted = all(r.get("conclusion") not in GREEN for r in graded)
    return {
        "ok": False,
        "red_since_utc": since,
        "ref": ref,
        "checked_utc": checked,
        "detail": "the trunk is RED: %s concluded %r on %s (run %s).%s"
                  % (WORKFLOW, latest.get("conclusion"), BRANCH, latest.get("html_url"),
                     "" if not exhausted else
                     " ⚠ EVERY graded run in the window read is red, so `red_since_utc` is a LOWER "
                     "BOUND — the redness may predate the window and the real age is at least this."),
    }


def fetch(token: str | None, per_page: int = 40) -> list:
    url = ("https://api.github.com/repos/%s/actions/workflows/%s/runs"
           "?branch=%s&status=completed&per_page=%d" % (REPO, WORKFLOW, BRANCH, per_page))
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "emc-autonomy-tick",
        **({"Authorization": "Bearer %s" % token} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as fh:
        return json.loads(fh.read().decode())["workflow_runs"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="/tmp/gates.json")
    ap.add_argument("--dry-run", action="store_true", help="print the verdict; write no file")
    args = ap.parse_args(argv)

    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        runs = fetch(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, KeyError) as exc:
        # ⛔ FAIL CLOSED. No file -> health.py reports `gates_green` unmeasured, which is what we
        # actually know. Never substitute a guess for a reading.
        print("[gates-verdict] could NOT read %s (%s: %s) — writing nothing, so the row stays "
              "`unmeasured`, which is the honest state" % (WORKFLOW, type(exc).__name__, exc))
        return 0

    verdict = decide(runs, now)
    if "_no_verdict" in verdict:
        print("[gates-verdict] %s — writing nothing" % verdict["_no_verdict"])
        return 0

    print("[gates-verdict] ok=%s ref=%s — %s" % (verdict["ok"], verdict["ref"], verdict["detail"]))
    if not args.dry_run:
        pathlib.Path(args.out).write_text(json.dumps(verdict, indent=2) + "\n")
        print("[gates-verdict] wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
