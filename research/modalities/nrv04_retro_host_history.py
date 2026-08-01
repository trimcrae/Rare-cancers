#!/usr/bin/env python3
"""What happened to the HOSTS a retro unit was placed on — read out of the supervision ticks themselves.

★★ WHY THE TICK LOG AND NOT THE VAST API (2026-08-01). `/instances/` lists only LIVE instances, so a host
that is already gone is invisible there: asking Vast about a dead rental returns nothing, and nothing is not
an answer (CLAUDE.md §4b). The supervision tick, by contrast, prints a line every time it acts —
`[retro-reap] auto-stopped <id> (<label>) — <why>`, the nudge lines, the idle-guard verdict and the per-offer
submit refusals — and those runs are retained. So the log IS the rental's death certificate, and it names the
cause: `result-in-S3` / `terminal-state` / `duplicate-instance` / the over-age backstop / an idle-guard
condemnation, versus no line at all, which means the host vanished on its own (a preemption).

⚠ THE DISTINCTION THIS EXISTS TO DRAW. "The host died" and "WE destroyed the host" look identical from S3 —
both leave a truncated run.log and no leg record — and they have opposite remedies. One is a market fact to
be waited out; the other is our own control plane cancelling work in progress, which no amount of re-renting
will fix. Guessing between them is exactly the 'probably X' §4 forbids.

Read-only: GitHub API + stdlib. Rents nothing, writes nothing to S3.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY") or "trimcrae/Rare-cancers"
API = "https://api.github.com"
WORKFLOW = os.environ.get("RETRO_HISTORY_WORKFLOW") or "fusion-cpu-extras.yml"
N_RUNS = int(os.environ.get("RETRO_HISTORY_RUNS") or "70")
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nrv04-retro-host-history.json")

#: Lines that say something happened TO a host. Each is a distinct cause and they must not be merged.
#:
#: ⚠ IT IS A CLASSIFIER, NOT A FILTER (2026-08-01). The first version used this as the *inclusion* test and
#: returned 0 hits over 30 scanned ticks — which reads as "nothing ever happened to these hosts" and is
#: exactly the absent-reading-as-reading-of-absence trap (CLAUDE.md §4b). The reap's own per-instance census
#: line (`[retro-reap]   id=<id> status=... label=...`) matches none of these words, so the evidence was
#: being discarded by the very tool sent to find it. Every line naming a host is now kept; this only labels.
_ACTION_RE = re.compile(
    r"(auto-stopped|destroy|DESTROY|nudge|NUDGE|condemn|CONDEMN|idle-guard|idle_guard|"
    r"resources_unavailable|outbid|OUTBID|preempt|terminal-state|result-in-S3|duplicate-instance|"
    r"exceeded \d+min|submit|refus|REFUS|HOLD|hold_cause|breaker|BLOCKED)")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop at the 302 instead of following it. See `_job_log`."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102, ARG002
        raise _Redirect(newurl)


class _Redirect(Exception):
    def __init__(self, url):
        super().__init__(url)
        self.url = url


def _req(url, token, raw=False):
    r = urllib.request.Request(url)
    r.add_header("Accept", "application/vnd.github+json")
    if token:
        r.add_header("Authorization", "Bearer %s" % token)
    with urllib.request.urlopen(r, timeout=90) as fh:
        data = fh.read()
    return data if raw else json.loads(data.decode())


def _job_log(job_id, token):
    """The raw log text for one job.

    ⚠ THE AUTH HEADER MUST NOT FOLLOW THE REDIRECT (measured 2026-08-01: 53 of 53 fetches failed with the
    naive version, and only the `unreadable_jobs` counter made that visible rather than reading as "these
    hosts have no history"). `/actions/jobs/<id>/logs` answers **302** to a short-lived signed blob URL;
    urllib re-sends `Authorization: Bearer …` to that host, which rejects a credential it never asked for.
    So: catch the redirect, then fetch the signed URL BARE."""
    url = f"{API}/repos/{REPO}/actions/jobs/{job_id}/logs"
    op = urllib.request.build_opener(_NoRedirect)
    r = urllib.request.Request(url)
    r.add_header("Accept", "application/vnd.github+json")
    if token:
        r.add_header("Authorization", "Bearer %s" % token)
    try:
        with op.open(r, timeout=90) as fh:
            return fh.read().decode("utf-8", "replace")
    except _Redirect as e:
        with urllib.request.urlopen(urllib.request.Request(e.url), timeout=90) as fh:
            return fh.read().decode("utf-8", "replace")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ids = [t for t in (os.environ.get("RETRO_HISTORY_HOSTS") or " ".join(argv)).replace(",", " ").split() if t]
    unit = os.environ.get("RETRO_HISTORY_UNIT") or ""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not ids and not unit:
        print("[host-history] nothing to look for — set RETRO_HISTORY_HOSTS and/or RETRO_HISTORY_UNIT")
        return {}
    needles = list(ids) + ([unit] if unit else [])
    out = {"_what": "Supervision-tick lines naming a retro unit's hosts — the rental death certificates.",
           "repo": REPO, "unit": unit, "hosts": ids, "runs_scanned": 0, "hits": []}
    try:
        runs = _req(f"{API}/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page={N_RUNS}", token)
    except urllib.error.HTTPError as e:  # noqa: PERF203 — one failure must be visible, not swallowed
        print(f"[host-history] could not list runs: {e}")
        return out
    for run in runs.get("workflow_runs", []) or []:
        try:
            jobs = _req(f"{API}/repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=100", token)
        except Exception as e:  # noqa: BLE001
            print(f"[host-history] run {run['id']}: jobs unreadable: {e}")
            continue
        for job in jobs.get("jobs", []) or []:
            if job.get("name") != "nrv04_vast_launch" or job.get("conclusion") == "skipped":
                continue
            out["runs_scanned"] += 1
            try:
                text = _job_log(job["id"], token)
            except Exception as e:  # noqa: BLE001
                if out.get("unreadable_jobs", 0) < 3:      # the CAUSE once, not 53 identical lines
                    print(f"[host-history] job {job['id']}: logs unreadable: {type(e).__name__}: {e}")
                out["unreadable_jobs"] = out.get("unreadable_jobs", 0) + 1
                continue
            # PROOF THE LOG WAS ACTUALLY READ. Without this, "0 hits" and "0 bytes fetched" render alike.
            out["bytes_scanned"] = out.get("bytes_scanned", 0) + len(text)
            for ln in text.splitlines():
                if not any(n in ln for n in needles):
                    continue
                m = _ACTION_RE.search(ln)
                out["hits"].append({"run": run["id"], "job": job["id"],
                                    "created_utc": run.get("created_at"),
                                    "action": m.group(1) if m else None, "line": ln.strip()[:600]})
    out["hits"].sort(key=lambda h: (h["created_utc"] or "", h["line"][:30]))
    print(json.dumps(out, indent=1)[:200000], flush=True)
    print(f"[host-history] {out['runs_scanned']} tick job(s) scanned, {len(out['hits'])} matching line(s)")
    try:
        with open(OUT_JSON, "w") as fh:
            json.dump(out, fh, indent=1)
        print(f"[host-history] wrote {OUT_JSON}")
    except Exception as e:  # noqa: BLE001
        print(f"[host-history] could not write artifact: {e}")
    return out


if __name__ == "__main__":
    main()
