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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mailer import llm_summarize, md_to_html, send_email  # noqa: E402

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
def gather(region):
    """Collect all the raw material once; used by both the LLM summary and the fallback."""
    now = now_et()
    ran, running, spot_in_use, aws_err = sagemaker_status(region)
    actions, gh_err = recent_actions_runs()
    sched = load_schedule()
    today = now.date()
    ordered, horizon = project_schedule(sched, today)
    active = [m for m in ordered if m.get("status") != "done"]
    completion = active[-1]["finish_date"] if active else today
    return dict(now=now, today=today, ran=ran, running=running, spot_in_use=spot_in_use,
                aws_err=aws_err, actions=actions, gh_err=gh_err, sched=sched, ordered=ordered,
                active=active, horizon=horizon, completion=completion)


def facts_block(g):
    """A compact plain-text digest of the raw state — the LLM's input, and the deterministic fallback's source."""
    L = []
    L.append(f"DATE: {fmt_date(g['today'])} (all times US Eastern, 12-hour).")
    L.append(f"PROJECTED PAPER COMPLETION (optimistic): {fmt_date(g['completion'])} (~{g['horizon']} days out).")
    L.append("")
    L.append("FINISHED IN LAST ~30h:")
    if g["aws_err"]:
        L.append(f"  (AWS unavailable: {g['aws_err']})")
    elif not g["ran"]:
        L.append("  (nothing finished)")
    for j in g["ran"]:
        extra = f" FAILURE: {j['failure']}" if j["failure"] else ""
        L.append(f"  - {j['name']}: {j['status']}, {j['instance']}, billable {j['billable_h']}, "
                 f"ended {fmt_dt(j['ended']) if j['ended'] else '?'}.{extra}")
    fails = [a for a in g["actions"] if a["failures"]]
    if fails:
        L.append("  CI runs with failures (may include retried/infra noise, not necessarily science): "
                 + "; ".join(f"{a['name']} ({a['failures']}/{a['total']})" for a in fails))
    L.append("")
    L.append("RUNNING NOW:")
    if not g["running"]:
        L.append("  (nothing running)")
    for j in g["running"]:
        L.append(f"  - {j['name']}: {j['instance']}, {j['secondary']}, elapsed {j['elapsed']}, "
                 f"started {fmt_dt(j['started'])}.")
    if g["running"]:
        L.append(f"  Spot slots in use: {g['spot_in_use']}/8.")
    L.append("")
    L.append("OPTIMISTIC SCHEDULE (milestone: status, start -> finish):")
    for m in g["ordered"]:
        when = "done" if m.get("status") == "done" else f"{fmt_date(m['start_date'])} -> {fmt_date(m['finish_date'])}"
        L.append(f"  - {m['title']} [{m.get('status')}, {m.get('track')}]: {when}")
    L.append(f"VENUE: {g['sched'].get('target_venue','?')}.")
    return "\n".join(L)


LLM_SYSTEM = (
    "You write a SHORT daily status email for Tristan (trimcrae), a solo researcher, about his NR4A3 "
    "PROTAC-degrader computational paper. You are given raw facts. Turn them into a bite-sized brief he can "
    "read at a glance on his phone. Rules: under ~170 words; NO tables; short bullets and plain prose; bold "
    "sparingly for the few things that matter. Lead with ONE headline line stating whether things are on "
    "track and the optimistic completion date. Then three tiny sections: '**Since yesterday**' (what "
    "finished; if a job FAILED or a run looks stalled, say so FIRST and plainly), '**Running now**' (or "
    "'nothing running'), and '**Path to done**' — a one-or-two-sentence prose timeline of the next few "
    "milestones with their optimistic dates, ending at the completion date. Keep all times/dates as given "
    "(US Eastern). Do not invent numbers. If nothing changed, say so briefly rather than padding."
)


def fallback_summary(g):
    """Deterministic bite-sized summary when no LLM key is present."""
    S = []
    n_run, n_fin = len(g["running"]), len(g["ran"])
    fails = sum(1 for j in g["ran"] if j["failure"])  # SageMaker job failures only; CI noise excluded
    head = f"On track for **{fmt_date(g['completion'])}** (optimistic)."
    if fails:
        head = f"⚠ {fails} failure(s) to check — " + head
    S.append(head)
    S.append("")
    S.append("**Since yesterday**")
    if g["aws_err"]:
        S.append(f"- AWS status unavailable ({g['aws_err']}).")
    elif n_fin:
        for j in g["ran"][:6]:
            flag = "❌ " if j["failure"] else ""
            S.append(f"- {flag}{j['name']} — {j['status']}")
    else:
        S.append("- No compute jobs finished.")
    S.append("")
    S.append("**Running now**")
    if n_run:
        for j in g["running"][:6]:
            S.append(f"- {j['name']} — {j['secondary'] or 'in progress'}, {j['elapsed']} in")
        S.append(f"- Spot slots: {g['spot_in_use']}/8")
    else:
        S.append("- Nothing running.")
    S.append("")
    S.append("**Path to done**")
    nxt = [m for m in g["active"] if m.get("status") != "done"][:3]
    for m in nxt:
        S.append(f"- {m['title'].split(' - ')[0].split(' (')[0]} → {fmt_date(m['finish_date'])}")
    S.append(f"- Projected completion: **{fmt_date(g['completion'])}**")
    return "\n".join(S)


def _summary_override():
    """A summary written elsewhere (e.g. by a scheduled Claude session, committed to email-outbox).

    SUMMARY_OVERRIDE_FILE (a path) takes precedence over SUMMARY_OVERRIDE (inline text). Empty => None.
    """
    ov_file = (os.environ.get("SUMMARY_OVERRIDE_FILE") or "").strip()
    if ov_file and Path(ov_file).exists():
        txt = Path(ov_file).read_text().strip()
        if txt:
            return txt
    return (os.environ.get("SUMMARY_OVERRIDE") or "").strip() or None


def build_bodies(region):
    g = gather(region)
    facts = facts_block(g)
    # Priority: a Claude-written summary (override) > Anthropic API > deterministic fallback.
    summary_md = _summary_override() or llm_summarize(facts, LLM_SYSTEM) or fallback_summary(g)

    # ---- plain text ----
    T = [f"NR4A3 PROTAC-degrader — daily status  ·  {fmt_dt(g['now'])}", "=" * 60, "",
         summary_md, "", "-" * 60,
         "Full detail (schedule source: research/manuscripts/degrader-paper-schedule.json):", ""]
    T.append(facts)
    text = "\n".join(T)

    # ---- HTML ----
    H = ['<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;'
         'font-size:15px;color:#1a1a1a;max-width:640px;line-height:1.55;margin:0 auto">']
    H.append('<div style="font-size:12px;color:#888">NR4A3 PROTAC-degrader — daily status · '
             f'{md_esc(fmt_dt(g["now"]))}</div>')
    H.append('<div style="margin:10px 0;padding:14px 16px;background:#f7f9fc;border:1px solid #e3e8ef;'
             'border-radius:10px">')
    H.append(md_to_html(summary_md))
    H.append("</div>")
    # slim details, collapsed-feel (not tables)
    H.append('<details style="margin-top:6px"><summary style="cursor:pointer;color:#2b6cb0;font-size:13px">'
             'Full detail &amp; schedule</summary>'
             '<pre style="white-space:pre-wrap;font-size:12px;color:#444;background:#fafafa;'
             'border:1px solid #eee;border-radius:8px;padding:10px;margin-top:6px">'
             f'{md_esc(facts)}</pre></details>')
    H.append('<div style="margin-top:10px;color:#aaa;font-size:11px">Optimistic dates — spot-capacity waits, '
             'failed shards and red-team findings routinely add days.</div>')
    H.append("</div>")
    html = "\n".join(H)

    fails = sum(1 for j in g["ran"] if j["failure"])  # SageMaker job failures only
    flag = "⚠ " if fails else ""
    subject = (f"{flag}NR4A3 degrader — {len(g['running'])} running, {len(g['ran'])} finished; "
               f"target {g['completion'].strftime('%b %-d')}")
    return subject, text, html


def md_esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ----------------------------------------------------------------------------- SES helpers (setup only)
def ses_probe(region):
    import boto3
    ses = boto3.client("ses", region_name=region)
    q = ses.get_send_quota()
    enabled = ses.get_account_sending_enabled().get("Enabled")
    ids = ses.list_identities().get("Identities", [])
    print(f"SES region={region}\n  account sending enabled: {enabled}")
    print(f"  24h quota: {q.get('Max24HourSend')}  sent(24h): {q.get('SentLast24Hours')}")
    print(f"  identities: {ids or '(none)'}")


def ses_verify(region, addrs):
    import boto3
    ses = boto3.client("ses", region_name=region)
    for a in addrs:
        ses.verify_email_identity(EmailAddress=a)
        print(f"  verification email requested for {a}")


# ----------------------------------------------------------------------------- main
def main():
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    mode = os.environ.get("MODE", "send").strip().lower()

    if mode == "probe":
        ses_probe(region)
        return
    if mode == "verify":
        mail_to = (os.environ.get("MAIL_TO") or "trimcrae@gmail.com").strip()
        mail_from = (os.environ.get("MAIL_FROM") or mail_to).strip()
        ses_verify(region, sorted({mail_from, mail_to}))
        return

    subject, text, html = build_bodies(region)

    if mode == "dry_run":
        Path("email_preview.txt").write_text(text)
        Path("email_preview.html").write_text(html)
        print(f"Subject: {subject}\n\n{text}\n\n[dry_run] wrote email_preview.{{txt,html}}; nothing sent.")
        return

    send_email(subject, text, html)


if __name__ == "__main__":
    sys.exit(main())
