#!/usr/bin/env python3
"""Daily NR4A3 PROTAC-degrader status email.

Composes and sends a once-a-day email with three sections:
  1. What ran yesterday   - SageMaker training jobs that finished in the last ~30 h (+ recent GitHub Actions runs).
  2. What is running now   - in-progress SageMaker training jobs, with elapsed time and spot-slot usage.
  3. Optimistic schedule   - a day-by-day projection to paper completion, walked from *today* over the
                             maintained critical-path plan in research/manuscripts/degrader-paper-schedule.json.

ALL times are rendered in US Eastern, 12-hour AM/PM (repo standing rule #1). Read-only against AWS/GitHub;
it starts nothing.

Modes (env MODE, default 'send'):
  send      - compose + send the email (SES by default; Gmail SMTP if MAIL_PASSWORD is set).
  dry_run   - compose + print the text body and write email_preview.{txt,html}; send nothing.
  probe     - report SES sending state (quota, sandbox, verified identities) so we can pick a delivery path.
  verify    - trigger SES identity-verification emails for MAIL_FROM and MAIL_TO (one-time, sandbox setup).

Env: AWS creds + AWS_DEFAULT_REGION (default us-east-2); MAIL_TO (default trimcrae@gmail.com);
     MAIL_FROM (default = MAIL_TO); optional MAIL_PASSWORD/MAIL_USERNAME/SMTP_HOST/SMTP_PORT for SMTP;
     optional GITHUB_TOKEN + GITHUB_REPOSITORY for the Actions section.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEDULE_FILE = REPO_ROOT / "research" / "manuscripts" / "degrader-paper-schedule.json"


# ----------------------------------------------------------------------------- time helpers (ET, 12-hour)
def now_et() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).astimezone(ET)


def to_et(t: dt.datetime) -> dt.datetime:
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ET)


def fmt_dt(t: dt.datetime) -> str:
    """e.g. 'Wed Jul 15, 7:04 AM ET' — 12-hour, no leading zero on the hour."""
    t = to_et(t)
    return t.strftime("%a %b %-d, %-I:%M %p ET")


def fmt_date(d: dt.date) -> str:
    return d.strftime("%a %b %-d, %Y")


def human_dur(seconds: float) -> str:
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m = rem // 60
    if h >= 24:
        d, h = divmod(h, 24)
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


# ----------------------------------------------------------------------------- SageMaker
def sagemaker_status(region: str):
    """Return (ran_yesterday, running, spot_in_use). Empty/degrades gracefully if AWS is unreachable."""
    ran, running, spot_in_use = [], [], 0
    try:
        import boto3
    except Exception:  # noqa: BLE001
        return ran, running, spot_in_use, "boto3 unavailable"
    try:
        sm = boto3.client("sagemaker", region_name=region)
        cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=30)

        def describe(name):
            try:
                return sm.describe_training_job(TrainingJobName=name)
            except Exception:  # noqa: BLE001
                return {}

        # finished in the window
        for status in ("Completed", "Stopped", "Failed"):
            summaries = sm.list_training_jobs(
                StatusEquals=status, SortBy="CreationTime", SortOrder="Descending",
                MaxResults=50, LastModifiedTimeAfter=cutoff,
            )["TrainingJobSummaries"]
            for s in summaries:
                d = describe(s["TrainingJobName"])
                rc = d.get("ResourceConfig", {})
                bt = d.get("BillableTimeInSeconds")
                tt = d.get("TrainingTimeInSeconds")
                sav = f"{(1 - bt/tt)*100:.0f}%" if (bt and tt) else "-"
                ran.append({
                    "name": s["TrainingJobName"],
                    "status": status,
                    "instance": f"{rc.get('InstanceType','?')} x{rc.get('InstanceCount',1)}",
                    "spot": d.get("EnableManagedSpotTraining", False),
                    "ended": d.get("TrainingEndTime") or s.get("LastModifiedTime"),
                    "billable_h": f"{bt/3600:.2f}h" if bt else "-",
                    "savings": sav,
                    "failure": (d.get("FailureReason") or "").split("\n")[0][:140] if status == "Failed" else "",
                })

        # in progress now
        summaries = sm.list_training_jobs(
            StatusEquals="InProgress", SortBy="CreationTime", SortOrder="Descending", MaxResults=50,
        )["TrainingJobSummaries"]
        now = dt.datetime.now(dt.timezone.utc)
        for s in summaries:
            d = describe(s["TrainingJobName"])
            rc = d.get("ResourceConfig", {})
            ic = rc.get("InstanceCount", 1)
            spot = d.get("EnableManagedSpotTraining", False)
            if spot:
                spot_in_use += ic
            created = s.get("CreationTime")
            running.append({
                "name": s["TrainingJobName"],
                "instance": f"{rc.get('InstanceType','?')} x{ic}",
                "spot": spot,
                "secondary": d.get("SecondaryStatus", ""),
                "started": created,
                "elapsed": human_dur((now - created).total_seconds()) if created else "-",
            })
        return ran, running, spot_in_use, None
    except Exception as e:  # noqa: BLE001
        return ran, running, spot_in_use, f"AWS/SageMaker error: {e}"


# ----------------------------------------------------------------------------- GitHub Actions (optional)
def recent_actions_runs():
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "trimcrae/Rare-cancers")
    if not token:
        return [], None
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"https://api.github.com/repos/{repo}/actions/runs?created=%3E{since}&per_page=40"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "User-Agent": "daily-status-email",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:  # noqa: BLE001
        return [], f"GitHub API error: {e}"
    # Collapse many runs of the same workflow into one line: total count + failures.
    agg = {}
    for run in data.get("workflow_runs", []):
        name = run.get("name") or run.get("display_title", "")
        concl = run.get("conclusion") or run.get("status")
        a = agg.setdefault(name, {"name": name, "total": 0, "failures": 0, "conclusion": concl})
        a["total"] += 1
        if concl not in ("success", "in_progress", "queued", None):
            a["failures"] += 1
    out = sorted(agg.values(), key=lambda a: (-a["failures"], -a["total"]))[:12]
    return out, None


# ----------------------------------------------------------------------------- schedule projection
def load_schedule():
    try:
        return json.loads(SCHEDULE_FILE.read_text())
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "milestones": []}


def remaining_days(m):
    if m.get("status") == "done":
        return 0
    if m.get("status") == "in_progress" and m.get("remaining_days") is not None:
        return m["remaining_days"]
    return m.get("optimistic_days", 1)


def project_schedule(sched, today: dt.date):
    """Longest-path over deps. Returns milestones enriched with start/finish day-offsets + dates."""
    ms = {m["id"]: dict(m) for m in sched.get("milestones", [])}
    finish_off = {}

    def compute(mid, seen):
        if mid in finish_off:
            return finish_off[mid]
        if mid in seen:  # cycle guard
            return 0
        seen = seen | {mid}
        m = ms[mid]
        start = max([compute(dep, seen) for dep in m.get("depends_on", []) if dep in ms] or [0])
        if m.get("status") == "done":
            start, fin = 0, 0
        else:
            fin = start + remaining_days(m)
        m["_start_off"], m["_finish_off"] = start, fin
        finish_off[mid] = fin
        return fin

    for mid in ms:
        compute(mid, set())
    for m in ms.values():
        m["start_date"] = today + dt.timedelta(days=m["_start_off"])
        m["finish_date"] = today + dt.timedelta(days=m["_finish_off"])
    ordered = sorted(ms.values(), key=lambda m: (m["_finish_off"], m["_start_off"], m["title"]))
    horizon = max([m["_finish_off"] for m in ms.values()] or [0])
    return ordered, horizon


# ----------------------------------------------------------------------------- rendering
def build_bodies(region):
    now = now_et()
    ran, running, spot_in_use, aws_err = sagemaker_status(region)
    actions, gh_err = recent_actions_runs()
    sched = load_schedule()
    today = now.date()
    ordered, horizon = project_schedule(sched, today)
    active = [m for m in ordered if m.get("status") != "done"]
    completion = active[-1]["finish_date"] if active else today
    SPOT_QUOTA = 8

    # ---- plain text ----
    L = []
    L.append(f"NR4A3 PROTAC-degrader paper - daily status")
    L.append(f"Generated {fmt_dt(now)}")
    L.append("")
    L.append(f"Projected paper completion (optimistic, if all goes to plan): {fmt_date(completion)}"
             f"  (~{horizon} days out)")
    L.append("=" * 68)

    L.append("")
    L.append("1) WHAT RAN YESTERDAY (SageMaker jobs finished in the last ~30h)")
    L.append("-" * 68)
    if aws_err:
        L.append(f"  [AWS unavailable: {aws_err}]")
    if not ran and not aws_err:
        L.append("  (no training jobs finished in the window)")
    for j in ran:
        tag = {"Completed": "OK", "Stopped": "STOPPED", "Failed": "FAILED"}.get(j["status"], j["status"])
        line = f"  [{tag}] {j['name']}  ({j['instance']}, spot={j['spot']})"
        if j["ended"]:
            line += f"  ended {fmt_dt(j['ended'])}"
        L.append(line)
        L.append(f"           billable {j['billable_h']}, spot-savings {j['savings']}")
        if j["failure"]:
            L.append(f"           reason: {j['failure']}")
    if actions:
        L.append("")
        L.append("  Recent GitHub Actions workflows (last ~30h, run count / failures):")
        for a in actions:
            fail = f", {a['failures']} failed" if a["failures"] else ""
            L.append(f"    - {a['name']}  ({a['total']} run{'s' if a['total'] != 1 else ''}{fail})")
    elif gh_err:
        L.append(f"  [GitHub Actions: {gh_err}]")

    L.append("")
    L.append("2) WHAT IS RUNNING NOW (in-progress SageMaker jobs)")
    L.append("-" * 68)
    if not running and not aws_err:
        L.append("  Nothing in flight.")
    for j in running:
        L.append(f"  * {j['name']}  ({j['instance']}, spot={j['spot']})")
        L.append(f"      {j['secondary']}, elapsed {j['elapsed']}, started {fmt_dt(j['started'])}")
    if running:
        L.append(f"  Spot instances in use: {spot_in_use} / {SPOT_QUOTA}  "
                 f"({max(0, SPOT_QUOTA - spot_in_use)} free slots)")

    L.append("")
    L.append("3) OPTIMISTIC SCHEDULE TO PAPER COMPLETION (day by day, if all goes to plan)")
    L.append("-" * 68)
    if sched.get("error"):
        L.append(f"  [schedule file unreadable: {sched['error']}]")
    L.append(f"  Venue: {sched.get('target_venue','?')}")
    L.append("")
    L.append("  Milestones (optimistic start -> finish):")
    for m in ordered:
        mark = {"done": "[x]", "in_progress": "[~]", "pending": "[ ]"}.get(m.get("status"), "[ ]")
        when = "DONE" if m.get("status") == "done" else f"{fmt_date(m['start_date'])} -> {fmt_date(m['finish_date'])}"
        L.append(f"  {mark} ({m.get('track','')[:4]:>4}) {m['title']}")
        L.append(f"        {when}")
    # day-by-day agenda
    L.append("")
    L.append("  Day-by-day (active milestones each day):")
    for off in range(0, horizon + 1):
        day = today + dt.timedelta(days=off)
        todays = [m for m in active if m["_start_off"] <= off < m["_finish_off"]]
        # a milestone that finishes exactly today is worth showing as landing
        landing = [m for m in active if m["_finish_off"] == off and off > 0]
        label = "TODAY" if off == 0 else fmt_date(day)
        if todays:
            names = "; ".join(f"{m['id']}" for m in todays)
            L.append(f"    {label}: {names}")
        elif landing:
            L.append(f"    {label}: (buffer)")
        else:
            L.append(f"    {label}: (buffer / no scheduled milestone)")
        for m in landing:
            L.append(f"        -> lands: {m['title']}")
    L.append("")
    L.append(f"  Finish line: {ordered[-1]['title'] if ordered else '?'} on {fmt_date(completion)}.")
    L.append("  Durations are optimistic ('all goes to plan'); spot-capacity waits, failed shards, and")
    L.append("  red-team findings routinely add days. Source: research/manuscripts/degrader-paper-schedule.json")
    text = "\n".join(L)

    # ---- HTML ----
    def esc(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    H = ['<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;'
         'font-size:14px;color:#1a1a1a;max-width:760px;line-height:1.5">']
    H.append('<h2 style="margin:0 0 2px">NR4A3 PROTAC-degrader paper — daily status</h2>')
    H.append(f'<div style="color:#666;font-size:12px">Generated {esc(fmt_dt(now))}</div>')
    H.append(f'<div style="margin:10px 0;padding:10px 14px;background:#eef6ff;border-left:4px solid #2b6cb0;'
             f'border-radius:4px"><b>Projected completion (optimistic):</b> {esc(fmt_date(completion))} '
             f'<span style="color:#666">(~{horizon} days out)</span></div>')

    H.append('<h3 style="margin:18px 0 4px;border-bottom:2px solid #ddd;padding-bottom:3px">'
             '1 · What ran yesterday</h3>')
    if aws_err:
        H.append(f'<div style="color:#a00">AWS unavailable: {esc(aws_err)}</div>')
    if not ran and not aws_err:
        H.append('<div style="color:#666">No training jobs finished in the window.</div>')
    if ran:
        H.append('<table style="border-collapse:collapse;width:100%;font-size:13px">')
        H.append('<tr style="text-align:left;color:#666">'
                 '<th style="padding:3px 6px">Job</th><th>Status</th><th>Instance</th>'
                 '<th>Billable</th><th>Ended</th></tr>')
        colors = {"Completed": "#2f855a", "Stopped": "#b7791f", "Failed": "#c53030"}
        for j in ran:
            c = colors.get(j["status"], "#333")
            ended = fmt_dt(j["ended"]) if j["ended"] else "-"
            H.append(f'<tr style="border-top:1px solid #eee"><td style="padding:3px 6px;font-family:monospace">'
                     f'{esc(j["name"])}</td>'
                     f'<td style="color:{c};font-weight:600">{esc(j["status"])}</td>'
                     f'<td>{esc(j["instance"])}</td><td>{esc(j["billable_h"])}</td>'
                     f'<td style="white-space:nowrap">{esc(ended)}</td></tr>')
            if j["failure"]:
                H.append(f'<tr><td colspan="5" style="padding:0 6px 4px;color:#c53030;font-size:12px">'
                         f'{esc(j["failure"])}</td></tr>')
        H.append("</table>")
    if actions:
        def _act(a):
            c = "#c53030" if a["failures"] else "#666"
            extra = f', {a["failures"]} failed' if a["failures"] else ""
            return f'{esc(a["name"])} (<span style="color:{c}">{a["total"]} run{"s" if a["total"]!=1 else ""}{extra}</span>)'
        H.append('<div style="margin-top:8px;font-size:12px;color:#555"><b>Recent Actions workflows:</b> '
                 + ", ".join(_act(a) for a in actions) + "</div>")

    H.append('<h3 style="margin:18px 0 4px;border-bottom:2px solid #ddd;padding-bottom:3px">'
             '2 · What is running now</h3>')
    if not running and not aws_err:
        H.append('<div style="color:#666">Nothing in flight.</div>')
    if running:
        H.append('<table style="border-collapse:collapse;width:100%;font-size:13px">')
        H.append('<tr style="text-align:left;color:#666"><th style="padding:3px 6px">Job</th>'
                 '<th>Instance</th><th>Phase</th><th>Elapsed</th><th>Started</th></tr>')
        for j in running:
            H.append(f'<tr style="border-top:1px solid #eee"><td style="padding:3px 6px;font-family:monospace">'
                     f'{esc(j["name"])}</td><td>{esc(j["instance"])}</td><td>{esc(j["secondary"])}</td>'
                     f'<td>{esc(j["elapsed"])}</td><td style="white-space:nowrap">{esc(fmt_dt(j["started"]))}</td></tr>')
        H.append("</table>")
        H.append(f'<div style="font-size:12px;color:#555;margin-top:4px">Spot instances in use: '
                 f'{spot_in_use}/{SPOT_QUOTA} ({max(0,SPOT_QUOTA-spot_in_use)} free slots)</div>')

    H.append('<h3 style="margin:18px 0 4px;border-bottom:2px solid #ddd;padding-bottom:3px">'
             '3 · Optimistic schedule to completion</h3>')
    H.append(f'<div style="font-size:12px;color:#555;margin-bottom:6px">Venue: {esc(sched.get("target_venue","?"))}</div>')
    H.append('<table style="border-collapse:collapse;width:100%;font-size:13px">')
    H.append('<tr style="text-align:left;color:#666"><th style="padding:3px 6px"></th><th>Milestone</th>'
             '<th>Track</th><th style="white-space:nowrap">Optimistic window</th></tr>')
    badge = {"done": ("✓", "#2f855a"), "in_progress": ("▶", "#2b6cb0"), "pending": ("○", "#999")}
    for m in ordered:
        sym, c = badge.get(m.get("status"), ("○", "#999"))
        when = "done" if m.get("status") == "done" else f'{fmt_date(m["start_date"])} → {fmt_date(m["finish_date"])}'
        H.append(f'<tr style="border-top:1px solid #eee"><td style="padding:3px 6px;color:{c};font-weight:700">'
                 f'{sym}</td><td>{esc(m["title"])}</td><td style="color:#666">{esc(m.get("track",""))}</td>'
                 f'<td style="white-space:nowrap">{esc(when)}</td></tr>')
    H.append("</table>")
    # day-by-day
    H.append('<div style="margin-top:10px;font-size:12px"><b>Day-by-day (active milestones):</b>'
             '<ul style="margin:4px 0;padding-left:18px">')
    for off in range(0, horizon + 1):
        day = today + dt.timedelta(days=off)
        todays = [m for m in active if m["_start_off"] <= off < m["_finish_off"]]
        landing = [m for m in active if m["_finish_off"] == off and off > 0]
        label = "<b>Today</b>" if off == 0 else esc(fmt_date(day))
        if todays:
            body = "; ".join(esc(m["id"]) for m in todays)
        else:
            body = '<span style="color:#999">buffer</span>'
        line = f"<li>{label}: {body}"
        if landing:
            line += " — <i>lands: " + "; ".join(esc(m["title"]) for m in landing) + "</i>"
        H.append(line + "</li>")
    H.append("</ul></div>")
    H.append(f'<div style="margin-top:8px;color:#666;font-size:11px">Optimistic — spot-capacity waits, '
             f'failed shards, and red-team findings routinely add days. '
             f'Source: research/manuscripts/degrader-paper-schedule.json</div>')
    H.append("</div>")
    html = "\n".join(H)

    subject = (f"NR4A3 degrader — {len(running)} running, {len(ran)} finished; "
               f"target {completion.strftime('%b %-d')}")
    return subject, text, html


# ----------------------------------------------------------------------------- delivery
def send_ses(region, mail_from, mail_to, subject, text, html):
    import boto3
    ses = boto3.client("ses", region_name=region)
    ses.send_email(
        Source=mail_from,
        Destination={"ToAddresses": [mail_to]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": text}, "Html": {"Data": html}},
        },
    )
    print(f"Sent via SES: {mail_from} -> {mail_to}")


def send_smtp(mail_from, mail_to, subject, text, html):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("MAIL_USERNAME", mail_from)
    pw = os.environ["MAIL_PASSWORD"]
    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, mail_from, mail_to
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL(host, port) as s:
        s.login(user, pw)
        s.sendmail(mail_from, [mail_to], msg.as_string())
    print(f"Sent via SMTP ({host}:{port}): {mail_from} -> {mail_to}")


def ses_probe(region):
    import boto3
    ses = boto3.client("ses", region_name=region)
    q = ses.get_send_quota()
    enabled = ses.get_account_sending_enabled().get("Enabled")
    ids = ses.list_identities().get("Identities", [])
    print(f"SES region={region}")
    print(f"  account sending enabled: {enabled}")
    print(f"  24h quota: {q.get('Max24HourSend')}  sent(24h): {q.get('SentLast24Hours')}  rate: {q.get('MaxSendRate')}/s")
    print(f"  (sandbox accounts have a 200/day quota and can only send to VERIFIED identities)")
    print(f"  identities: {ids or '(none)'}")
    if ids:
        attrs = ses.get_identity_verification_attributes(Identities=ids).get("VerificationAttributes", {})
        for i in ids:
            print(f"    {i}: {attrs.get(i, {}).get('VerificationStatus')}")


def ses_verify(region, addrs):
    import boto3
    ses = boto3.client("ses", region_name=region)
    for a in addrs:
        ses.verify_email_identity(EmailAddress=a)
        print(f"  verification email requested for {a} (click the link AWS sends)")


# ----------------------------------------------------------------------------- main
def main():
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    mode = os.environ.get("MODE", "send").strip().lower()
    mail_to = os.environ.get("MAIL_TO", "trimcrae@gmail.com").strip()
    mail_from = os.environ.get("MAIL_FROM", mail_to).strip()

    if mode == "probe":
        ses_probe(region)
        return
    if mode == "verify":
        ses_verify(region, sorted({mail_from, mail_to}))
        return

    subject, text, html = build_bodies(region)

    if mode == "dry_run":
        Path("email_preview.txt").write_text(text)
        Path("email_preview.html").write_text(html)
        print(f"Subject: {subject}\n")
        print(text)
        print("\n[dry_run] wrote email_preview.txt and email_preview.html; nothing sent.")
        return

    # send
    if os.environ.get("MAIL_PASSWORD"):
        send_smtp(mail_from, mail_to, subject, text, html)
    else:
        send_ses(region, mail_from, mail_to, subject, text, html)


if __name__ == "__main__":
    sys.exit(main())
