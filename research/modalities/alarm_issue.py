#!/usr/bin/env python3
"""ESCALATE AN ALARM TO A GITHUB ISSUE — the only channel that needs nothing but `GITHUB_TOKEN`.

★★ WHY THIS EXISTS, AND WHAT WAS MEASURED (2026-07-31).

The fleet is supervised. What was NOT working is the path by which a problem reaches a human:

  1. `lane-staleness-watch.yml`'s mail step has NEVER delivered — not once, across 159 failing runs. Its env
     block passes only the AWS keys, so `mailer.send_email` (mailer.py, the `MAIL_PASSWORD` test) takes the
     SES branch, and SES answers:

         AccessDenied ... User `arn:aws:iam::646605541856:user/nr4a3-ci-submitter' is not authorized to
         perform `ses:SendEmail' on resource `.../identity/trimcrae@gmail.com'
         (run 30602768073, job 91068780404, 2026-07-31 03:55 AM UTC — and `mode=probe` in run 30626375302
          fails identically on `ses:GetSendQuota`)

     The workflow's own comment blamed the SES *sandbox*. It is not the sandbox: a sandboxed account answers
     `MessageRejected: Email address is not verified`. This is a MISSING IAM POLICY, and `MAIL_PASSWORD` has
     never appeared in that workflow in any commit on any branch, so the branch that does work was never on.
     The exception was caught into `::warning title=LANE-WATCH MAIL NOT DELIVERED::`, which nobody reads.
     One home for the whole channel picture and the exact fix: `research/compute/notification-channels.md`.

  2. That left ONE channel reaching a human with no agent watching: GitHub's own notification on a FAILED
     SCHEDULED RUN. And that channel was saturated — `vast-watchdog.yml` failed on 38 consecutive scheduled
     runs from 2026-07-28 13:42 UTC to 2026-07-31 08:44 UTC before going green. A channel that has been
     crying wolf for three days is not a channel.

⚠ SO THE REQUIREMENT IS NOT "ANOTHER ALARM", IT IS AN ESCALATION THAT SURVIVES BEING RIGHT REPEATEDLY.
A hundred issues for one condition is the same cry-wolf failure in a new costume. Hence, in order:

  DEDUPLICATED   one OPEN issue per distinct alarm condition, matched on an HTML marker in the body. The
                 body is edited in place and a COMMENT is posted only when the verdict CHANGES — because a
                 body edit sends no notification and a comment does, so the phone buzzes on news, not on
                 the hourly re-confirmation of news it already had.
  SELF-CLOSING   the condition clearing closes the issue. This is what makes the channel trustworthy: an
                 OPEN issue means a LIVE problem, a CLOSED one means it cleared. Without that half, the
                 issue list decays into the same unread backlog as the red-run list.
  TITLED         the title says WHAT IS WRONG, because on a phone the title is all you get. "Alarm fired"
                 is not a title.
  ★ SILENT WHEN THE QUESTION WAS NEVER ANSWERED. `fleet_supervision_alarm` separates a measured outage from
                 an unreadable API (FRESH-API-UNREADABLE, STALE-CAUSE-UNKNOWN) and `lane_staleness_watch`
                 does the same with UNKNOWN. This module HOLDS on those: it neither opens nor closes. Not
                 opening keeps the 4:18 PM 2026-07-27 false alarm off a human's phone; not CLOSING matters
                 just as much, because an unreadable API silently retiring a live issue would be the
                 measured-zero defect with the safety rail removed.

⚠ AND WHAT IT MUST NOT BE — the same rule `fleet-supervision-alarm.yml` is built on. It shares NO code with
the lanes it reports on: pure stdlib, no boto3, no Vast key, no import of any lane module. The failure it
exists to report is precisely a shared-dependency failure, and an escalation that dies with the thing it
escalates is not an escalation. It also rents, prices, reaps and destroys nothing — it opens and closes
issues, and that is the entire blast radius of `issues: write`.

Usage:
    python3 alarm_issue.py --fleet-verdict /tmp/fleet-supervision-verdict.json
    python3 alarm_issue.py --lane-report   /tmp/lane-staleness-verdict.json
    python3 alarm_issue.py --self-test fire|fire-changed|recover   # exercise the channel end to end
    python3 alarm_issue.py ... --dry-run                            # decide, print, touch nothing

Exit 0 when the channel worked (including "nothing to do"). Exit 1 only when the ESCALATION ITSELF failed —
a red run on a broken notification path is the point: an unexercised channel is exactly what just turned
out to be broken.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ET = datetime.timezone(datetime.timedelta(hours=-4))  # EDT. CLAUDE.md §1: always US Eastern, 12-hour.

API = "https://api.github.com"
DEFAULT_REPO = "trimcrae/Rare-cancers"
DEFAULT_LABEL = "fleet-alarm"
DEFAULT_ASSIGNEE = "trimcrae"

# ── the marker set. Dedupe keys off `alarm-key`; the rest is state carried IN the issue body so this module
# needs no store of its own. That is deliberate: a state file would be one more thing that can be stale, on
# a branch, or missing — the exact class of bug this repo keeps paying for (CLAUDE.md §7).
_MARK = "<!-- alarm-{}: {} -->"
_MARK_RE = "<!--\\s*alarm-{}:\\s*(.*?)\\s*-->"

# ★ VERDICTS THAT NAME A FAILURE TO MEASURE, NOT A MEASURED FAILURE. Firing on one of these pages a human
# about a question nobody asked. Each is listed with the module that produces it so the set cannot drift
# into a general-purpose mute.
UNMEASURED_VERDICTS = frozenset({
    "UNKNOWN",              # lane_staleness_watch: a CRITICAL field could not be read, so no honest verdict
    "FRESH-API-UNREADABLE",  # fleet_supervision_alarm: ok=True already; listed so the intent is pinned
    "TICKS-UNREADABLE",     # lane_staleness_watch supervision: ok=True already; same
})

OPEN, CLOSE, HOLD = "OPEN", "CLOSE", "HOLD"


def _et(ts: datetime.datetime) -> str:
    return ts.astimezone(ET).strftime("%-I:%M %p ET %b %-d, %Y")


def _z(ts: datetime.datetime) -> str:
    return ts.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_z(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return None


def _short(text: str, n: int = 74) -> str:
    """First clause of a detail string, for a title a phone can show in one line."""
    t = " ".join(str(text or "").split())
    for stop in (" — ", ". ", "; "):
        if stop in t[:n + 20]:
            t = t.split(stop)[0]
            break
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


# ═══════════════════════════════════════════════════════════════════════════ conditions
class Condition:
    """One distinct alarm condition: the unit of deduplication AND of auto-closure.

    `ok` and `verdict` come straight from the producing module — this module re-derives nothing, because a
    second opinion on the same evidence is a second thing to keep in sync (CLAUDE.md §1).
    """

    def __init__(self, key, title, verdict, ok, detail, evidence_readable=True, payload=None, source=""):
        self.key = key
        self.title = title
        self.verdict = verdict
        self.ok = bool(ok)
        self.detail = detail
        self.evidence_readable = bool(evidence_readable)
        self.payload = payload or {}
        self.source = source


def decide(cond: Condition) -> tuple[str, str]:
    """OPEN / CLOSE / HOLD, and why. Pure, so the policy is testable without touching GitHub.

    ★ HOLD IS NOT A WEAKER CLOSE. It means "we did not learn anything this run", so an existing issue keeps
    its state and no new one is created. Collapsing HOLD into CLOSE would let an unreadable API retire a
    live alarm; collapsing it into OPEN is the 2026-07-27 4:18 PM false alarm.
    """
    if cond.ok:
        return CLOSE, f"verdict {cond.verdict} is OK — if an issue is open for this condition it has cleared"
    if cond.verdict in UNMEASURED_VERDICTS:
        return HOLD, (f"verdict {cond.verdict} names a FAILURE TO MEASURE, not a measured failure — "
                      f"escalating it would page a human about a question nobody answered")
    if not cond.evidence_readable:
        return HOLD, ("the discriminating evidence could not be read this run, so this verdict rests on an "
                      "unasked question — an unreadable API is not an outage")
    return OPEN, f"verdict {cond.verdict} is a MEASURED failure"


def conditions_from_fleet_verdict(v: dict) -> list[Condition]:
    """`fleet_supervision_alarm.py --json` -> one condition. One fleet, one supervision question."""
    verdict = v.get("verdict", "?")
    live, usd = v.get("live_instances"), v.get("realised_usd_so_far")
    where = f"{live} host(s) billing" if live else "fleet"
    title = (f"FLEET UNSUPERVISED [{verdict}] — {_short(v.get('detail', ''))}"
             if not v.get("ok") else f"fleet supervision {verdict}")
    return [Condition(
        key="fleet-supervision",
        title=title[:160],
        verdict=verdict,
        ok=v.get("ok", False),
        detail=v.get("detail", ""),
        # `runs_readable` is the alarm's own record of whether it could apply its discriminator.
        evidence_readable=v.get("runs_readable", True) is not False,
        payload={"artifact_generated_et": v.get("artifact_generated_et"),
                 "artifact_age_min": v.get("artifact_age_min"),
                 "live_instances": live, "realised_usd_so_far": usd,
                 "last_completed_run_et": v.get("last_completed_run_et"),
                 "last_completed_conclusion": v.get("last_completed_conclusion"),
                 "scheduled_delivery_gaps_min": v.get("scheduled_delivery_gaps_min"),
                 "fetch_error": v.get("fetch_error"), "at_risk": where},
        source="fleet-supervision-alarm.yml",
    )]


def conditions_from_lane_report(r: dict) -> list[Condition]:
    """`lane_staleness_watch.py --json` -> ONE CONDITION PER LANE, healthy ones included.

    The healthy ones are the auto-close half: a report that only listed the red lanes could open issues but
    never retire them, and an issue list that only grows is the backlog this exists to avoid.
    """
    out = []
    for lane in r.get("lanes", []):
        verdict = lane.get("verdict", "?")
        title = (f"LANE {lane.get('lane')} [{verdict}] — {_short(lane.get('detail', ''))}"
                 if not lane.get("ok") else f"lane {lane.get('lane')} {verdict}")
        out.append(Condition(
            key=f"lane:{lane.get('lane')}",
            title=title[:160],
            verdict=verdict,
            ok=lane.get("ok", False),
            detail=lane.get("detail", ""),
            # The lane module encodes unreadability in the VERDICT (UNKNOWN), not in a flag, so there is no
            # second signal to consult and inventing one here would be a re-derivation.
            evidence_readable=True,
            payload={"label": lane.get("label"), "provider": lane.get("provider"),
                     "evidence_age_min": lane.get("evidence_age_min"),
                     "census_basis": lane.get("census_basis"),
                     "supervision": (lane.get("supervision") or {}).get("verdict")},
            source="lane-staleness-watch.yml",
        ))
    return out


# ═══════════════════════════════════════════════════════════════════════════ body rendering
def _mark(name, value):
    return _MARK.format(name, value)


def read_mark(body: str, name: str, default=None):
    m = re.search(_MARK_RE.format(re.escape(name)), body or "")
    return m.group(1) if m else default


def render_body(cond: Condition, *, now: datetime.datetime, first_seen: datetime.datetime,
                firings: int, run_url: str) -> str:
    rows = [("first seen", _et(first_seen)), ("last checked", _et(now)), ("firings", str(firings)),
            ("produced by", f"`{cond.source}`")]
    if run_url:
        rows.append(("this run", run_url))
    for k, val in cond.payload.items():
        if val not in (None, "", [], {}):
            rows.append((k.replace("_", " "), f"`{val}`"))
    table = "\n".join(f"| {k} | {v} |" for k, v in rows)
    return "\n".join([
        _mark("key", cond.key),
        _mark("verdict", cond.verdict),
        _mark("first-seen-utc", _z(first_seen)),
        _mark("firings", firings),
        "",
        f"### {cond.verdict}",
        "",
        cond.detail or "_(the producing module supplied no detail)_",
        "",
        "| | |",
        "|---|---|",
        table,
        "",
        "---",
        "**This issue is opened, updated and closed automatically by "
        "`research/modalities/alarm_issue.py`.** An OPEN issue means the condition is LIVE; it closes itself "
        "on the first run that finds the condition cleared. Closing it by hand does not silence anything — "
        "the next run that still sees the condition opens a fresh one. What reaches a human and what does "
        "not (including why the email channel never delivered): `research/compute/notification-channels.md`.",
    ])


# ═══════════════════════════════════════════════════════════════════════════ github
class GitHubIssues:
    """The thinnest possible REST client — stdlib only, injectable transport so the policy is testable.

    ⚠ DEDUPE READS THE ISSUES LIST, NEVER THE SEARCH API. GitHub's search index is eventually consistent by
    seconds-to-minutes; an issue created one run ago can be missing from a search, and a dedupe that misses
    is a dedupe that opens a second issue. The list endpoint is strongly consistent.
    """

    def __init__(self, repo=DEFAULT_REPO, token=None, transport=None, attempts=3):
        self.repo = repo
        self.token = token if token is not None else (os.environ.get("GITHUB_TOKEN")
                                                      or os.environ.get("GH_TOKEN") or "")
        self._transport = transport
        self.attempts = max(1, attempts)

    # -- transport ---------------------------------------------------------
    def request(self, method: str, path: str, payload=None):
        if self._transport is not None:
            return self._transport(method, path, payload)
        url = path if path.startswith("http") else f"{API}{path}"
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "alarm-issue",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if data is not None:
            headers["Content-Type"] = "application/json"
        last = None
        for i in range(self.attempts):
            if i:
                time.sleep(min(2 ** i, 8))
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=30) as r:
                    raw = r.read().decode()
                return json.loads(raw) if raw.strip() else {}
            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode()[:300]
                except Exception:  # noqa: BLE001  (diagnostics must never be the thing that raises)
                    pass
                last = f"HTTP {e.code} {e.reason} on {method} {path} — {body}"
                if e.code in (401, 403, 404, 410, 422):
                    break   # a permission or shape error will not improve on retry
            except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
                last = f"{type(e).__name__}: {e} on {method} {path}"
        raise RuntimeError(last or f"{method} {path} failed")

    # -- operations --------------------------------------------------------
    def open_issues(self) -> list[dict]:
        """Every OPEN issue, PRs filtered out (the issues endpoint returns both)."""
        out, page = [], 1
        while page <= 5:
            batch = self.request("GET", f"/repos/{self.repo}/issues?state=open&per_page=100&page={page}")
            if not isinstance(batch, list) or not batch:
                break
            out += [i for i in batch if "pull_request" not in i]
            if len(batch) < 100:
                break
            page += 1
        return out

    def create(self, title, body, labels, assignees):
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = list(labels)
        if assignees:
            payload["assignees"] = list(assignees)
        return self.request("POST", f"/repos/{self.repo}/issues", payload)

    def update(self, number, **fields):
        return self.request("PATCH", f"/repos/{self.repo}/issues/{number}", fields)

    def comment(self, number, body):
        return self.request("POST", f"/repos/{self.repo}/issues/{number}/comments", {"body": body})

    def ensure_label(self, name, color="B60205",
                     description="Opened and closed automatically by alarm_issue.py"):
        """Best effort. A missing label must never be the reason an alarm fails to reach a human."""
        try:
            self.request("GET", f"/repos/{self.repo}/labels/{name}")
            return True
        except RuntimeError:
            pass
        try:
            self.request("POST", f"/repos/{self.repo}/labels",
                         {"name": name, "color": color, "description": description})
            return True
        except RuntimeError:
            return False


# ═══════════════════════════════════════════════════════════════════════════ reconcile
def reconcile(conditions, client: GitHubIssues, *, now=None, run_url="", label=DEFAULT_LABEL,
              assignees=(DEFAULT_ASSIGNEE,), dry_run=False) -> list[dict]:
    """Drive the issue list to match the conditions. Returns one action row per condition."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    existing = {}
    for issue in client.open_issues():
        k = read_mark(issue.get("body") or "", "key")
        if k and k not in existing:      # oldest wins, so a hand-made duplicate cannot orphan the tracked one
            existing[k] = issue

    actions = []
    for cond in conditions:
        want, why = decide(cond)
        issue = existing.get(cond.key)
        row = {"key": cond.key, "verdict": cond.verdict, "decision": want, "why": why,
               "issue": issue.get("number") if issue else None, "action": "none", "title": cond.title}

        if want == HOLD:
            row["action"] = "held"
            actions.append(row)
            continue

        if want == CLOSE:
            if issue is None:
                row["action"] = "none"        # nothing open: silence is the correct state
            elif dry_run:
                row["action"] = "would-close"
            else:
                client.comment(issue["number"],
                               f"✅ **RECOVERED** — {_et(now)}\n\nThe condition cleared: the producing module "
                               f"now reports `{cond.verdict}`.\n\n> {cond.detail}\n\nClosing automatically. "
                               f"An open issue here always means a live problem.")
                client.update(issue["number"], state="closed", state_reason="completed")
                row["action"] = "closed"
            actions.append(row)
            continue

        # want == OPEN
        if issue is None:
            body = render_body(cond, now=now, first_seen=now, firings=1, run_url=run_url)
            if dry_run:
                row["action"] = "would-create"
            else:
                if label:
                    client.ensure_label(label)
                created = client.create(cond.title, body, [label] if label else [], assignees)
                row["issue"] = created.get("number")
                row["action"] = "created"
            actions.append(row)
            continue

        old_body = issue.get("body") or ""
        prev_verdict = read_mark(old_body, "verdict")
        first_seen = _parse_z(read_mark(old_body, "first-seen-utc") or "") or now
        try:
            firings = int(read_mark(old_body, "firings") or "1") + 1
        except ValueError:
            firings = 2
        body = render_body(cond, now=now, first_seen=first_seen, firings=firings, run_url=run_url)
        changed = prev_verdict != cond.verdict
        if dry_run:
            row["action"] = "would-comment" if changed else "would-update"
            actions.append(row)
            continue
        client.update(issue["number"], title=cond.title, body=body)
        # ★ A COMMENT ONLY ON CHANGE. A body edit sends no notification and a comment does, so this is the
        # difference between "your phone buzzes when the situation changes" and "your phone buzzes hourly
        # until you mute the repo" — which is the failure mode that made the red-run channel useless.
        if changed:
            client.comment(issue["number"],
                           f"⚠ **{prev_verdict} → {cond.verdict}** at {_et(now)}\n\n> {cond.detail}")
            row["action"] = "commented"
        else:
            row["action"] = "updated"
        actions.append(row)
    return actions


def render(actions, *, now=None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if not actions:
        return f"[alarm-issue] {_et(now)} — no conditions supplied; nothing to escalate."
    lines = [f"[alarm-issue] read at {_et(now)}"]
    for a in actions:
        num = f"#{a['issue']}" if a.get("issue") else "—"
        lines.append(f"[alarm-issue] {a['action']:<13} {num:<6} {a['key']:<26} {a['verdict']:<22} {a['why']}")
    opened = [a for a in actions if a["action"] in ("created", "commented")]
    closed = [a for a in actions if a["action"] == "closed"]
    held = [a for a in actions if a["action"] == "held"]
    lines.append(f"[alarm-issue] {len(opened)} notified · {len(closed)} auto-closed · {len(held)} held "
                 f"(unmeasured — deliberately neither opened nor closed)")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════ self-test
def self_test_conditions(phase: str, now=None) -> list[Condition]:
    """A condition that exercises the whole channel without lying about the fleet.

    ★ IT USES ITS OWN KEY. `alarm-self-test` can never collide with `fleet-supervision` or a `lane:*` key,
    so a self-test can neither mask a real alarm nor be mistaken for one, and the title says so first.
    A notification path that has not been exercised is exactly the thing that just turned out to be broken,
    so this stays in the tree permanently and is re-runnable at any time for $0.
    """
    now = now or datetime.datetime.now(datetime.timezone.utc)
    stamp = _et(now)
    if phase == "recover":
        return [Condition(key="alarm-self-test", title="[alarm self-test] channel healthy",
                          verdict="SELF-TEST-CLEARED", ok=True,
                          detail=f"self-test recovery phase at {stamp} — this proves auto-closure works.",
                          source="alarm_issue.py --self-test")]
    if phase == "unmeasured":
        return [Condition(key="alarm-self-test", title="[alarm self-test] unmeasured", verdict="UNKNOWN",
                          ok=False, detail=f"self-test unmeasured phase at {stamp} — must be HELD.",
                          source="alarm_issue.py --self-test")]
    changed = phase == "fire-changed"
    return [Condition(
        key="alarm-self-test",
        title=("[alarm self-test] ESCALATION CHANNEL — verdict changed, expect a comment" if changed
               else "[alarm self-test] ESCALATION CHANNEL — this is a drill, no fleet is affected"),
        verdict="SELF-TEST-CHANGED" if changed else "SELF-TEST-FIRING",
        ok=False,
        detail=(f"Deliberate self-test at {stamp}. NO fleet, lane or rental is affected. It exists to prove, "
                f"end to end, that an alarm condition reaches a human: an issue opens, a second firing does "
                f"NOT open a second issue, a changed verdict posts a comment, and recovery closes it."),
        payload={"phase": phase},
        source="alarm_issue.py --self-test",
    )]


# ═══════════════════════════════════════════════════════════════════════════ cli
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fleet-verdict", default=None, help="fleet_supervision_alarm.py --json output")
    ap.add_argument("--lane-report", default=None, help="lane_staleness_watch.py --json output")
    ap.add_argument("--self-test", default=None,
                    choices=["fire", "fire-changed", "recover", "unmeasured"],
                    help="exercise the channel with a synthetic condition on its own key")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO)
    ap.add_argument("--label", default=DEFAULT_LABEL)
    ap.add_argument("--assignee", action="append", default=None,
                    help="notified on open; defaults to %s" % DEFAULT_ASSIGNEE)
    ap.add_argument("--dry-run", action="store_true", help="decide and print, touch nothing")
    ap.add_argument("--json", default=None, help="also write the action rows here")
    a = ap.parse_args(argv)

    now = datetime.datetime.now(datetime.timezone.utc)
    conditions: list[Condition] = []
    if a.self_test:
        conditions += self_test_conditions(a.self_test, now)
    for path, fn in ((a.fleet_verdict, conditions_from_fleet_verdict),
                     (a.lane_report, conditions_from_lane_report)):
        if not path:
            continue
        try:
            with open(path) as fh:
                conditions += fn(json.load(fh))
        except (OSError, json.JSONDecodeError) as e:
            # ⚠ A MISSING VERDICT FILE IS NOT "EVERYTHING IS FINE". The producing step died before writing
            # one, which is itself a supervision failure — but this module cannot name WHICH condition, so
            # it refuses rather than silently escalating nothing (which would read as green).
            print(f"::error title=ALARM SOURCE UNREADABLE::{path}: {type(e).__name__}: {e} — the escalation "
                  f"channel could not be given a verdict to act on.", file=sys.stderr)
            return 1

    if not conditions:
        print("[alarm-issue] no verdict source given; nothing to escalate.")
        return 0

    assignees = a.assignee if a.assignee is not None else [DEFAULT_ASSIGNEE]
    client = GitHubIssues(repo=a.repo)
    if not client.token and not a.dry_run:
        print("::error title=ALARM CHANNEL HAS NO TOKEN::GITHUB_TOKEN is absent, so the issue channel — the "
              "one escalation that needs no other credential — cannot run.", file=sys.stderr)
        return 1
    try:
        actions = reconcile(conditions, client, now=now, run_url=_run_url(), label=a.label,
                            assignees=assignees, dry_run=a.dry_run)
    except RuntimeError as e:
        print(f"::error title=ESCALATION CHANNEL BROKEN::{e}. This is the notification path itself failing, "
              f"which is why it reddens the run.", file=sys.stderr)
        return 1

    print(render(actions, now=now))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"now_utc": _z(now), "now_et": _et(now), "actions": actions}, fh, indent=2)
            fh.write("\n")
    return 0


def _run_url() -> str:
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo, run = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID")
    return f"{server}/{repo}/actions/runs/{run}" if repo and run else ""


if __name__ == "__main__":
    sys.exit(main())
