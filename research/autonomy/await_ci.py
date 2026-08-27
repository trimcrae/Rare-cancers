#!/usr/bin/env python3
"""BLOCK UNTIL CI ON A COMMIT IS DECIDED, SO THE HARNESS CAN WAKE THE SESSION.

★★ WHY THIS EXISTS — THE STALL trimcrae SAW, DIAGNOSED. On 2026-08-27 a cycle ended its turn with an
"In flight" board reading `CI tests on 8b22933, adda6f6, 0743ac1`, and then nothing happened for two
hours until a human asked. The CI runs were fine; every one of them went green. What was missing was
a WAY BACK: the harness wakes a session when a backgrounded command exits or a subagent lands, and it
has no idea GitHub Actions exists. So the board named three things the session had no mechanism to
follow up on, and "in flight" and "abandoned" rendered identically.

⛔⛔ THE RULE THIS FILE EXISTS TO MAKE KEEPABLE: **NOTHING GOES ON AN IN-FLIGHT BOARD UNLESS SOMETHING
WILL BRING THE SESSION BACK FOR IT.** That is CLAUDE.md §1's `&`-versus-run_in_background test —
"after this command, is there anything that will bring the session back?" — applied to the reporting
rule rather than to a shell idiom. Run this with the tool's own `run_in_background`, and the exit IS
the wake.

    python3 research/autonomy/await_ci.py --sha $(git rev-parse HEAD) > ci.log 2>&1; echo "EXIT=$?" >> ci.log

⚠ AND IT WRITES A VERDICT, NOT A PING. Exit 0 = every run concluded successfully. Exit 1 = something
concluded red. Exit 2 = the deadline passed with runs still going, which is NOT a pass — an absent
reading is not a reading of absence (CLAUDE.md §4), and a poller that times out silently is the
"green board built from missing data" this repository has already paid for.

⚠ THE `cancelled` CONCLUSION IS NOT A FAILURE HERE, AND THAT IS DELIBERATE. Pushing again supersedes
the previous commit's runs, so `cancelled` is the normal fate of every head but the last. It is
reported and not counted red — but it is never counted GREEN either, because a cancelled run
measured nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com/repos/{repo}/actions/runs?head_sha={sha}&per_page=50"

#: GitHub reports a run as queued/in_progress/waiting/requested before it decides.
UNDECIDED = {"queued", "in_progress", "waiting", "requested", "pending", None}

#: ⛔ `cancelled` and `skipped` are NEITHER pass NOR fail — see the module docstring.
RED = {"failure", "timed_out", "startup_failure", "action_required", "stale"}
GREEN = {"success", "neutral"}


def _get(url: str, token: str | None, timeout: int = 25):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "emc-await-ci",
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.load(fh)


def poll(repo: str, sha: str, deadline_s: int, interval_s: int, token: str | None,
         require: int = 1, quiet: bool = False) -> int:
    started = time.monotonic()
    url = API.format(repo=repo, sha=sha)
    last_line = ""
    consecutive_errors = 0

    while True:
        elapsed = int(time.monotonic() - started)
        try:
            data = _get(url, token)
            consecutive_errors = 0
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            # ⚠ A TRANSIENT READ FAILURE IS NOT A VERDICT. Keep polling; only give up if the API is
            # unreadable for long enough that we would be reporting a guess.
            consecutive_errors += 1
            if not quiet:
                print(f"[await-ci] {elapsed:>5}s  API read failed ({type(exc).__name__}), "
                      f"attempt {consecutive_errors}", flush=True)
            if consecutive_errors >= 8:
                print(f"[await-ci] ⛔ the Actions API was unreadable {consecutive_errors} times in a "
                      f"row. NOT reporting a verdict — this is UNKNOWN, not green.", flush=True)
                return 2
            time.sleep(interval_s)
            if time.monotonic() - started > deadline_s:
                print("[await-ci] ⛔ deadline passed while the API was unreadable — UNKNOWN.", flush=True)
                return 2
            continue

        runs = data.get("workflow_runs") or []
        undecided = [r for r in runs if r.get("status") != "completed"
                     or r.get("conclusion") in UNDECIDED]
        decided = [r for r in runs if r not in undecided]

        line = f"{len(runs)} run(s): {len(decided)} decided, {len(undecided)} still going"
        if not quiet and line != last_line:
            print(f"[await-ci] {elapsed:>5}s  {line}", flush=True)
            last_line = line

        # ⚠ ZERO RUNS IS NOT "ALL DECIDED". Actions takes time to register a push, and treating an
        # empty list as success would make this poller return green before CI had even started —
        # the single most dangerous thing it could do.
        if runs and not undecided and len(runs) >= require:
            red = [r for r in decided if r.get("conclusion") in RED]
            other = [r for r in decided if r.get("conclusion") not in RED
                     and r.get("conclusion") not in GREEN]
            for r in decided:
                mark = "⛔" if r.get("conclusion") in RED else (
                    "✅" if r.get("conclusion") in GREEN else "◻")
                print(f"[await-ci] {mark} {r.get('conclusion')!s:<14} {r.get('name')}", flush=True)
            if red:
                print(f"[await-ci] ⛔ {len(red)} run(s) RED on {sha[:8]} — this is the cycle's work now.",
                      flush=True)
                return 1
            if other:
                print(f"[await-ci] ◻ {len(other)} run(s) neither passed nor failed "
                      f"({sorted({str(r.get('conclusion')) for r in other})}). A cancelled run "
                      "measured nothing; it is not evidence of green.", flush=True)
            print(f"[await-ci] ✅ CI decided GREEN on {sha[:8]}", flush=True)
            return 0

        if time.monotonic() - started > deadline_s:
            print(f"[await-ci] ⛔ deadline ({deadline_s}s) passed with {len(undecided)} run(s) still "
                  f"going on {sha[:8]}. That is UNKNOWN, not green — re-arm or look manually.",
                  flush=True)
            return 2

        time.sleep(interval_s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Wait until every Actions run for a commit has concluded, then exit with a "
                    "verdict. Run it with run_in_background so its exit wakes the session.")
    ap.add_argument("--sha", required=True, help="the commit to watch")
    ap.add_argument("--repo", default=os.environ.get("EMC_CI_REPO", "trimcrae/rare-cancers"))
    ap.add_argument("--deadline", type=int, default=2400, help="seconds before returning UNKNOWN (default 2400)")
    ap.add_argument("--interval", type=int, default=45, help="seconds between polls (default 45)")
    ap.add_argument("--require", type=int, default=1,
                    help="minimum runs that must exist before a verdict is taken (default 1), so a "
                         "push that has not registered yet cannot read as green")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    # ⛔ THE API MATCHES `head_sha` EXACTLY AND A SHORT SHA SILENTLY RETURNS ZERO RUNS. Measured
    # 2026-08-27: `--sha babb1dce` polled to its deadline and reported UNKNOWN, while the same
    # commit's full sha returned the failure immediately. A caller who abbreviates would therefore
    # wait out the whole deadline and be told nothing — a fake stall manufactured by the poller
    # itself, which is the exact failure class this file was written to remove. Refuse early and
    # say what to run instead.
    if len(args.sha) != 40 or not all(c in "0123456789abcdef" for c in args.sha.lower()):
        print(f"[await-ci] ⛔ --sha must be the FULL 40-character commit sha; got {args.sha!r} "
              f"({len(args.sha)} chars). The Actions API matches head_sha exactly, so a short sha "
              f"returns zero runs and this poller would wait out its whole deadline and report "
              f"UNKNOWN. Run: python3 research/autonomy/await_ci.py --sha $(git rev-parse "
              f"{args.sha or 'HEAD'})", flush=True)
        return 2

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return poll(args.repo, args.sha, args.deadline, args.interval, token,
                require=args.require, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
