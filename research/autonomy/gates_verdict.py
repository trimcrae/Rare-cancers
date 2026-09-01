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
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import envread  # noqa: E402

# ⛔ WHY THE HTTP DESCRIBER IS IMPORTED FROM `await_ci` RATHER THAN COPIED HERE. Two modules in this
# directory poll the same Actions API about the same repository, and this file already carries a note
# (DEFAULT_REPO, AUT-PROP-034) about what happened the last time they each kept their own copy of a
# shared fact. One fact, one place (CLAUDE.md §1) applies to a diagnostic routine exactly as it does
# to a number. ⚠ The seat that wrote this (S37-ERROR-BODIES, 2026-09-01) owned only these two files,
# so the shared helper lives in the larger of the two rather than in a module of its own; promoting
# it to `research/autonomy/httperr.py` is a one-line follow-up and is recorded as such.
import await_ci  # noqa: E402

#: The authority on whether the trunk is green. CLAUDE.md §6: `tests.yml` runs BOTH suites in full on
#: every push with the real dependencies, and it — not a local preflight — is what decides `main`.
WORKFLOW = "tests.yml"
BRANCH = "main"

#: The repository this verdict is ABOUT when `GITHUB_REPOSITORY` is unset — running by hand in a dev
#: sandbox, which is the only place that happens.
DEFAULT_REPO = "trimcrae/Rare-cancers"


def repo_read() -> envread.EnvRead:
    """Which repository's trunk this reads, three-valued (AUT-PROP-034).

    ⛔⛔ WHY THIS IS NO LONGER `os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO)`, AND THE REASON IS
    SPECIFIC TO THIS FILE. Everything downstream of the fetch treats an empty run list as a
    MEASUREMENT: `decide()` reads "no completed, graded run" and returns `_no_verdict`, `main()` then
    writes no file, and `health.py`'s `gates_green` row stays `unmeasured`. That chain is right for
    "the API answered and nothing is graded yet" and WRONG for "we asked the wrong server". A
    `GITHUB_REPOSITORY` exported empty — a `${VAR}` that expanded to nothing, an `env:` whose value
    did not resolve — makes `os.environ.get` return `""` rather than the default (see `envread`), the
    URL becomes `repos//actions/...`, and the trunk's gate verdict silently becomes a question nobody
    asked. ⚠ The unmeasured row that results is INDISTINGUISHABLE from the honest one, which is the
    property that makes this read worth changing and most others in this directory not.

    ⭐ AND `unset` IS STILL FINE AND STILL SAYS SO. Running this by hand in a sandbox has no
    `GITHUB_REPOSITORY`; that is `unset-using-default`, a reading rather than an absence of one.
    """
    return envread.read("GITHUB_REPOSITORY", default=DEFAULT_REPO,
                        validate=envread.repo_slug,
                        what="whose trunk gate verdict this writes")


def token_read() -> envread.EnvRead:
    """The API credential, three-valued.

    ⚠ UNSET IS LEGITIMATE AND IS NOT AN ERROR: this repository is public, so an unauthenticated read
    works at a lower rate limit. ⛔ EXPORTED-AND-EMPTY IS NOT. It sends `Authorization: Bearer ` with
    nothing after it, GitHub answers 401, and the 401 lands in `main()`'s `except` clause — which
    writes nothing and prints "could NOT read", reporting an API problem when the real cause is a
    variable somebody set to nothing. ⚠ `GITHUB_TOKEN or GH_TOKEN` also SKIPS an empty
    `GITHUB_TOKEN` and quietly uses `GH_TOKEN`, hiding the same fact; `envread.first_set` stops at
    the broken one rather than stepping over it.
    """
    return envread.first_set(("GITHUB_TOKEN", "GH_TOKEN"),
                             validate=envread.opaque_token, secret=True,
                             what="the Actions API credential")


#: ⚠ MODULE-LEVEL, AND IT CARRIES A VALUE ONLY WHEN THE READ IS USABLE — `None` otherwise, which is
#: itself the signal. Kept because callers and tests refer to `gates_verdict.REPO`; `main()` refuses
#: rather than substituting anything for a None.
REPO = repo_read().value

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


def fetch(token: str | None, per_page: int = 40, repo: str | None = None) -> list:
    # ⚠ `repo` is a PARAMETER with the module constant as its fallback, so a caller that has already
    # taken the three-valued read passes the value it validated rather than trusting a global that
    # was computed at import time under a different environment.
    url = ("https://api.github.com/repos/%s/actions/workflows/%s/runs"
           "?branch=%s&status=completed&per_page=%d" % (repo or REPO, WORKFLOW, BRANCH, per_page))
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

    # ⛔ FAIL CLOSED ON THE ENVIRONMENT, EXACTLY AS THIS FILE ALREADY FAILS CLOSED ON THE API. An
    # unusable `GITHUB_REPOSITORY` or an unusable token means we cannot take the reading, and this
    # module's whole contract is that a reading it could not take leaves `gates_green` UNMEASURED
    # rather than guessed. Both print WHY, both write nothing, and both still exit 0 — the exit code
    # belongs to the tick, which must go on to publish the board and send the stall alarm.
    repo = repo_read()
    token = token_read()
    for r in (repo, token):
        if not r.usable:
            print("[gates-verdict] %s Writing nothing, so `gates_green` stays `unmeasured`, which is "
                  "the honest state." % r.detail)
            return 0
    if repo.defaulted:
        print("[gates-verdict] %s" % repo.detail)

    try:
        runs = fetch(token.value, repo=repo.value)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, KeyError) as exc:
        # ⛔ FAIL CLOSED. No file -> health.py reports `gates_green` unmeasured, which is what we
        # actually know. Never substitute a guess for a reading.
        # ⛔ AND SAY WHY IT COULD NOT BE READ, IN THE SERVER'S OWN WORDS (S37-ERROR-BODIES,
        # 2026-09-01). Failing closed is only half the job: `gates_green: unmeasured` is honest but
        # it is also INERT — it names no action, and this row had already sat unmeasured for 47.2 h
        # once (see `test_main_keeps_a_per_commit_verdict`). `str(HTTPError)` yields
        # `HTTP Error 403: Forbidden` — the REASON, never the body — so a rate limit that clears in
        # four minutes and a token that will never work again printed the same sentence. They no
        # longer do: `describe_http_error` quotes the body and, on a 403, the `X-RateLimit-*`
        # headers that separate those two cases.
        print("[gates-verdict] could NOT read %s (%s) — writing nothing, so the row stays "
              "`unmeasured`, which is the honest state"
              % (WORKFLOW, await_ci.describe_http_error(exc)))
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
