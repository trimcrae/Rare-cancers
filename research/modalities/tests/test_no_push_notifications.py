"""⛔ THIS REPO DOES NOT NOTIFY trimcrae. These tests make that a property, not a promise.

trimcrae, 2026-07-31, verbatim: **"You're emailing me way too much. You should not be emailing me."**

WHAT HAD HAPPENED. Earlier the same day the supervision escalation was rebuilt as a GitHub Issue channel —
deduplicated, self-closing, titled, silent on unmeasured verdicts. It worked. That was the problem: **every
issue open, comment and close emails the repo owner** through their GitHub notification settings, so a
channel built to be RELIABLE was, by construction, a channel that mailed him — and the self-test proving it
worked mailed him four more times (issues #17 and #18, both since closed).

★ THE REQUIREMENT WAS NEVER "NOTIFY HIM". It is that supervision survives with no LLM in the loop, which is
a PULL requirement, met by `alarm_state.py` writing a committed board that carries its own expiry.

THE THREE PUSH PATHS THAT LIVED IN THIS REPO'S OWN CODE, and the guard for each below:

    1. issue writes          -> the `issues:` PERMISSION is revoked from the alarm workflows, and the module
                                that used it is deleted. A capability, not a config flag: a default is one
                                CLI argument away from being back on in an edit nobody reviews as a
                                notification change.
    2. `mailer.send_email`   -> the SES branch RAISES instead of sending. SMTP is untouched, because the
                                weekly newsletter (`method-watch.yml`, Fridays) is wanted.
    3. a deliberate `exit 1` -> a failed SCHEDULED run emails the owner; that was literally its stated
                                purpose in both alarm workflows. Now an `::error` annotation, which is
                                equally visible and sends nothing.

⚠ WHAT THESE TESTS DELIBERATELY DO NOT COVER, so nobody reads a green build as "he cannot be emailed at all":
GitHub still emails the owner when ANY OTHER scheduled workflow fails, and this repo has several. That list
is inventoried in `research/compute/notification-channels.md`; it is a settings-and-ownership question, not
something a test in this directory can assert.
"""
from __future__ import annotations

import ast
import os
import pathlib
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

WF = pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows"
MODALITIES = pathlib.Path(__file__).resolve().parents[1]

#: The two workflows whose whole job is to report on supervision — i.e. the ones with a standing motive to
#: acquire a notification channel. They are the ones that had one.
ALARM_WORKFLOWS = ("fleet-supervision-alarm.yml", "lane-staleness-watch.yml")


def _yaml(path):
    yaml = pytest.importorskip("yaml", reason="PyYAML is not in this environment")
    return yaml.safe_load(path.read_text())


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · THE ISSUE CHANNEL — the capability is gone, not merely switched off
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("wf", ALARM_WORKFLOWS)
def test_no_alarm_workflow_requests_the_issues_permission(wf):
    """★ THE CHEAP, STRONG GUARD. Without `issues:` write, no code path in the job can open, comment on or
    close an issue, whatever a later edit to any module decides. Checked at BOTH levels, because a job-level
    block silently overrides the top-level one."""
    doc = _yaml(WF / wf)
    top = doc.get("permissions") or {}
    assert "issues" not in top, f"{wf} requests top-level issues permission: {top.get('issues')!r}"
    for name, job in (doc.get("jobs") or {}).items():
        perms = (job or {}).get("permissions") or {}
        assert "issues" not in perms, f"{wf} job {name} requests issues permission: {perms.get('issues')!r}"


def test_no_workflow_anywhere_grants_issue_write():
    """Widened past the two alarm workflows on purpose: the lesson is about the CLASS of change, and the
    next agent who wants to 'just let it open a tracking issue' will not necessarily edit those two files."""
    yaml = pytest.importorskip("yaml", reason="PyYAML is not in this environment")
    offenders = []
    for p in sorted(WF.glob("*.yml")):
        try:
            doc = yaml.safe_load(p.read_text())
        except Exception:  # noqa: BLE001 — an unparseable workflow is another test's problem, not this one
            continue
        if not isinstance(doc, dict):
            continue
        scopes = [doc.get("permissions") or {}]
        scopes += [(j or {}).get("permissions") or {} for j in (doc.get("jobs") or {}).values()]
        for s in scopes:
            if isinstance(s, dict) and s.get("issues") == "write":
                offenders.append(p.name)
    assert not offenders, (f"{offenders} grant issues:write. Opening an issue emails the repo owner and "
                           f"trimcrae asked not to be emailed — see research/compute/notification-channels.md")


def test_the_issue_escalation_module_is_gone():
    """Deleted rather than disabled. A dormant push module in a repo whose owner has said 'do not email me'
    is a thing a future agent switches back on; git history keeps the record."""
    assert not (MODALITIES / "alarm_issue.py").exists(), \
        "alarm_issue.py is back. It is a PUSH channel — every issue write emails the repo owner."


def test_nothing_still_calls_the_deleted_escalation():
    """A workflow calling a module that no longer exists would fail the run — which, on a schedule, emails
    him. The dangling reference is itself a notification bug."""
    for p in sorted(WF.glob("*.yml")):
        assert "alarm_issue" not in p.read_text(), f"{p.name} still references the deleted push module"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · THE MAIL CHANNEL — SES refuses; SMTP survives because the weekly newsletter is wanted
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_ses_branch_raises_instead_of_sending():
    import mailer
    with pytest.raises(mailer.SesDeliberatelyDisabled) as e:
        mailer._send_ses("a@b.c", "trimcrae@gmail.com", "subj", "text", "<p>html</p>")
    assert "disabled" in str(e.value).lower()


def test_send_email_without_MAIL_PASSWORD_refuses_rather_than_silently_choosing_a_dead_path(monkeypatch):
    """★ THE ACTUAL 2026-07-31 DEFECT, pinned. `lane-staleness-watch.yml` passed the AWS keys and not
    MAIL_PASSWORD, so `send_email` silently chose SES; SES answered AccessDenied; the exception was caught
    into a `::warning` nobody read — for 159 consecutive runs, while the step looked like coverage. Now the
    same mistake is loud."""
    import mailer
    monkeypatch.delenv("MAIL_PASSWORD", raising=False)
    assert mailer.transport_name() == "ses"
    with pytest.raises(mailer.SesDeliberatelyDisabled):
        mailer.send_email("subj", "text", "<p>html</p>", mail_to="trimcrae@gmail.com")


def test_the_smtp_branch_is_untouched_because_the_weekly_newsletter_is_wanted(monkeypatch):
    """CLAUDE.md §5: the Friday newsletter is 'the surviving cadence'. Killing SES must not kill that."""
    import mailer
    monkeypatch.setenv("MAIL_PASSWORD", "x")
    assert mailer.transport_name() == "smtp"
    src = (MODALITIES / "mailer.py").read_text()
    assert "smtplib" in src and "def _send_smtp" in src


def test_neither_alarm_workflow_sends_mail_any_more():
    for wf in ALARM_WORKFLOWS:
        src = (WF / wf).read_text()
        body = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
        for banned in ("send_email", "MAIL_PASSWORD", "MAIL_TO", "import mailer"):
            assert banned not in body, f"{wf} still has a mail path: {banned}"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · THE RED-RUN CHANNEL — a failed scheduled run emails the owner, so the alarms stopped failing
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("wf", ALARM_WORKFLOWS)
def test_the_alarm_workflows_do_not_fail_the_run_as_a_notification_device(wf):
    """These two used to end with `exit 1` and said so in their headers: the point WAS the email. The
    verdict now lives in the committed board, so the run stays green and says its piece in an annotation.

    ★ THE TEST IS SCOPED TO VERDICT-CONDITIONED STEPS, and that scoping is the whole craft of it. A blanket
    "no `exit 1` anywhere" also catches `TERNARY ROOT EMPTY`, which fails because its WORK failed — normal
    CI, and exactly the kind of false positive that gets a guard deleted. What is banned is narrower and is
    the actual defect: a step that exists ONLY to turn a bad verdict into a red run, i.e. into an email. A
    step is verdict-conditioned when its `if:` reads the check step's return code.
    """
    doc = _yaml(WF / wf)
    offenders = []
    for job_name, job in (doc.get("jobs") or {}).items():
        for step in (job or {}).get("steps") or []:
            cond, run = str(step.get("if") or ""), str(step.get("run") or "")
            if ".outputs.rc" in cond and "exit 1" in run:
                offenders.append(f"{job_name}/{step.get('name')}")
    assert not offenders, (
        f"{wf}: {offenders} fail the run purely because the verdict was bad. GitHub emails the repo owner "
        f"when a SCHEDULED workflow fails — that is a push channel, and restoring it is a notification "
        f"decision needing trimcrae's word, not a CI decision.")
    assert "::error" in (WF / wf).read_text(), f"{wf} must still be LOUD without being a notification"


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 4 · THE REPLACEMENT IS A PULL CHANNEL, STRUCTURALLY
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_board_writer_cannot_send_or_open_anything():
    """`alarm_state.py` is the replacement, so it is the file most likely to grow a notification later.
    Asserted on CALLS and IMPORTS rather than raw text: its docstring discusses email at length, and a text
    match failing on the incident notes is the kind of false positive that gets a guard deleted."""
    tree = ast.parse((MODALITIES / "alarm_state.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            assert name not in ("send_email", "sendmail", "create", "comment", "post", "urlopen",
                                "Request", "destroy", "rent", "submit"), f"push-shaped call {name}"
    assert imported <= {"argparse", "datetime", "json", "os", "sys", "__future__"}, \
        f"unexpected imports: {imported}"
    for banned in ("mailer", "boto3", "smtplib", "urllib", "requests"):
        assert banned not in imported, f"the board writer must not import {banned}"


def test_the_alarm_workflows_write_the_board_instead():
    """A guard that only removes channels would leave supervision with no output at all. One of the two must
    actually publish the verdict, or the whole thing is silence with extra steps."""
    committed = [wf for wf in ALARM_WORKFLOWS if "alarm_state.py" in (WF / wf).read_text()]
    assert committed, "no alarm workflow writes the pull board — the verdict now goes nowhere"
    src = (WF / "lane-staleness-watch.yml").read_text()
    # ⚠ THE PROPERTY IS "THE BOARD REACHES `main`", NOT "A LITERAL `git add` APPEARS HERE". This asserted the
    # `git add` line directly and broke on 2026-08-01 when the publish moved into
    # `research/compute/publish_artifacts.sh` — the board was MORE reliably published (a conflict can no
    # longer wedge it), and the test failed anyway because it was pinned to the mechanism. A test that fails
    # when an implementation improves is a test that discourages the improvement.
    assert "alarm-state.json" in src, "the board must be produced by this workflow"
    published = ("git add research/modalities/alarm-state.json" in src
                 or ("publish_artifacts.sh" in src and "alarm-state.json" in src))
    assert published, ("the board must be COMMITTED; an unpushed board is a board frozen at its last commit. "
                       "Either stage it directly or pass it to publish_artifacts.sh.")
