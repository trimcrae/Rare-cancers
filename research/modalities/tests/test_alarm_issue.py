"""The escalation channel's value is that it survives BEING RIGHT REPEATEDLY.

Measured 2026-07-31: the mail escalation had never delivered (159 failing `lane-staleness-watch` runs, every
one of them an `AccessDenied` on `ses:SendEmail` swallowed into a `::warning`), which left GitHub's
failed-scheduled-run notification as the only path to a human — and that path had been saturated by 38
consecutive `vast-watchdog` failures. So these tests are mostly about the three properties that separate a
usable channel from a second source of noise: it deduplicates, it closes itself, and it stays quiet about
questions nobody answered.
"""
from __future__ import annotations

import ast
import datetime
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import alarm_issue as ai  # noqa: E402

MOD = os.path.join(os.path.dirname(__file__), "..", "alarm_issue.py")
NOW = datetime.datetime(2026, 7, 31, 16, 0, 0, tzinfo=datetime.timezone.utc)   # 12:00 PM ET


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# a fake GitHub that records everything, so the tests assert on ACTIONS TAKEN, not on mocks called
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
class FakeGitHub(ai.GitHubIssues):
    def __init__(self, issues=None):
        super().__init__(repo="o/r", token="t", transport=self._route)
        self.issues = list(issues or [])
        self._next = max([i["number"] for i in self.issues], default=0) + 1
        self.calls = []

    def _route(self, method, path, payload):
        self.calls.append((method, path, payload))
        if method == "GET" and "/issues?" in path:
            return [i for i in self.issues if i.get("state", "open") == "open"] if "page=1" in path else []
        if method == "GET" and "/labels/" in path:
            return {"name": "fleet-alarm"}
        if method == "POST" and path.endswith("/issues"):
            new = {"number": self._next, "state": "open", "title": payload["title"],
                   "body": payload["body"], "labels": payload.get("labels", [])}
            self._next += 1
            self.issues.append(new)
            return new
        if method == "PATCH" and "/issues/" in path:
            n = int(path.rsplit("/", 1)[1])
            issue = next(i for i in self.issues if i["number"] == n)
            issue.update(payload)
            return issue
        if method == "POST" and path.endswith("/comments"):
            n = int(path.split("/issues/")[1].split("/")[0])
            issue = next(i for i in self.issues if i["number"] == n)
            issue.setdefault("comments", []).append(payload["body"])
            return {"id": 1}
        raise AssertionError(f"unexpected call {method} {path}")

    # convenience
    def created(self):
        return [c for c in self.calls if c[0] == "POST" and c[1].endswith("/issues")]

    def comments(self):
        return [c for c in self.calls if c[0] == "POST" and c[1].endswith("/comments")]

    def closes(self):
        return [c for c in self.calls if c[0] == "PATCH" and (c[2] or {}).get("state") == "closed"]


def _fleet(verdict, ok, *, runs_readable=True, detail="the tick ran and measured nothing"):
    return {"verdict": verdict, "ok": ok, "detail": detail, "runs_readable": runs_readable,
            "artifact_age_min": 300.0, "live_instances": 16, "realised_usd_so_far": 68.98}


def _run(conditions, gh, **kw):
    return ai.reconcile(conditions, gh, now=NOW, run_url="https://x/run/1", **kw)


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 1 · DEDUPE — the property that keeps this from being cry-wolf in a new costume
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_a_first_firing_opens_exactly_one_issue():
    gh = FakeGitHub()
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    assert [a["action"] for a in acts] == ["created"]
    assert len(gh.created()) == 1
    assert len(gh.issues) == 1


def test_a_SECOND_firing_of_the_SAME_condition_does_not_open_a_second_issue():
    """★ THE CORE REGRESSION. `fleet-supervision-alarm.yml` runs hourly; a condition that lasts a weekend
    would otherwise produce ~50 issues, which is the same unread backlog the red-run channel became."""
    gh = FakeGitHub()
    cond = ai.conditions_from_fleet_verdict(_fleet("FAILING", False))
    _run(cond, gh)
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    assert len(gh.issues) == 1, "a second firing opened a second issue"
    assert [a["action"] for a in acts] == ["updated"]
    assert acts[0]["issue"] == 1


def test_a_repeat_firing_updates_the_body_but_posts_NO_comment():
    """A body edit sends no notification; a comment does. Re-confirming yesterday's news must not buzz."""
    gh = FakeGitHub()
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    before = len(gh.comments())
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    assert len(gh.comments()) == before, "an unchanged verdict posted a notifying comment"
    assert any(c[0] == "PATCH" for c in gh.calls)


def test_the_firing_count_and_first_seen_survive_across_runs():
    """State lives IN the issue body, so there is no side file to go stale or land on the wrong branch."""
    gh = FakeGitHub()
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    body = gh.issues[0]["body"]
    assert ai.read_mark(body, "firings") == "3"
    assert ai.read_mark(body, "first-seen-utc") == "2026-07-31T16:00:00Z"


def test_a_CHANGED_verdict_posts_a_comment_and_retitles():
    """A change is news, and news is the one thing worth a notification."""
    gh = FakeGitHub()
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("ABSENT", False, detail="the SCHEDULER is not "
                                                        "delivering")), gh)
    assert acts[0]["action"] == "commented"
    assert len(gh.issues) == 1
    assert "FAILING → ABSENT" in gh.issues[0]["comments"][-1]
    assert "ABSENT" in gh.issues[0]["title"]


def test_two_DIFFERENT_conditions_get_two_issues():
    """Dedupe is per condition, not global — two dead lanes are two problems."""
    gh = FakeGitHub()
    report = {"lanes": [{"lane": "step1_fanout", "verdict": "BILLING-NOT-ADVANCING", "ok": False,
                         "detail": "4 hosts billing, no new evidence in 96 min", "label": "step 1"},
                        {"lane": "valb_reps", "verdict": "IDLE-UNEXPECTED", "ok": False,
                         "detail": "no host at all and 3 units unfinished", "label": "valB"}]}
    acts = _run(ai.conditions_from_lane_report(report), gh)
    assert [a["action"] for a in acts] == ["created", "created"]
    assert len({i["number"] for i in gh.issues}) == 2


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 2 · AUTO-CLOSE — what makes an OPEN issue mean something
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_recovery_closes_the_issue():
    gh = FakeGitHub()
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FRESH", True, detail="the last completed run "
                                                        "refreshed the artifact")), gh)
    assert acts[0]["action"] == "closed"
    assert gh.issues[0]["state"] == "closed"
    assert gh.issues[0]["state_reason"] == "completed"
    assert "RECOVERED" in gh.issues[0]["comments"][-1]


def test_recovery_with_nothing_open_does_nothing_at_all():
    """The steady state is green. A healthy fleet must not generate API writes, let alone issues."""
    gh = FakeGitHub()
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FRESH", True)), gh)
    assert acts[0]["action"] == "none"
    assert gh.issues == [] and not gh.created() and not gh.closes()


def test_a_closed_issue_is_invisible_so_a_recurrence_opens_a_fresh_one():
    """Dedupe reads OPEN issues only. Reopening a stale thread would hand a new incident someone else's
    history; a fresh issue is the honest record, and the closed one stays as the record of the last one."""
    gh = FakeGitHub()
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    _run(ai.conditions_from_fleet_verdict(_fleet("FRESH", True)), gh)
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    assert acts[0]["action"] == "created"
    assert len([i for i in gh.issues if i["state"] == "open"]) == 1


def test_a_lane_report_carries_the_HEALTHY_lanes_too():
    """Auto-closure is only possible if the healthy lanes reach this module — a report of red lanes alone
    could open issues forever and never retire one."""
    report = {"lanes": [{"lane": "a", "verdict": "ADVANCING", "ok": True, "detail": "x"},
                        {"lane": "b", "verdict": "IDLE-UNEXPECTED", "ok": False, "detail": "y"}]}
    conds = ai.conditions_from_lane_report(report)
    assert {c.key for c in conds} == {"lane:a", "lane:b"}
    assert [ai.decide(c)[0] for c in conds] == [ai.CLOSE, ai.OPEN]


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 3 · NEVER FIRE ON A CONDITION THAT IS MERELY UNMEASURED
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_an_unreadable_api_verdict_does_NOT_open_an_issue():
    """★ 2026-07-27, 4:18 PM ET: an unreadable Actions API was announced as `FLEET UNSUPERVISED [ABSENT]`
    over a 3-minute-old artifact, inside a green tick. That must never reach a phone."""
    gh = FakeGitHub()
    acts = _run(ai.conditions_from_fleet_verdict(
        _fleet("STALE-CAUSE-UNKNOWN", False, runs_readable=False)), gh)
    assert acts[0]["action"] == "held"
    assert not gh.created(), "an unmeasured verdict opened an issue"


def test_FRESH_API_UNREADABLE_opens_nothing():
    gh = FakeGitHub()
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FRESH-API-UNREADABLE", True)), gh)
    assert acts[0]["action"] == "none" and not gh.created()


def test_a_lane_UNKNOWN_verdict_opens_nothing():
    """`lane_staleness_watch` returns UNKNOWN when a CRITICAL field could not be read — ok is False, but no
    honest verdict was reached, so there is nothing to page about."""
    gh = FakeGitHub()
    acts = _run(ai.conditions_from_lane_report(
        {"lanes": [{"lane": "z", "verdict": "UNKNOWN", "ok": False, "detail": "state unreadable"}]}), gh)
    assert acts[0]["action"] == "held" and not gh.created()


def test_an_unmeasured_verdict_does_NOT_close_a_LIVE_issue_either():
    """★ THE HALF THAT IS EASY TO MISS. HOLD is not a weaker CLOSE: letting an unreadable API retire an open
    alarm would be the measured-zero defect with the safety rail removed."""
    gh = FakeGitHub()
    _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    acts = _run(ai.conditions_from_fleet_verdict(
        _fleet("STALE-CAUSE-UNKNOWN", False, runs_readable=False)), gh)
    assert acts[0]["action"] == "held"
    assert not gh.closes(), "an unreadable API closed a live alarm"
    assert gh.issues[0]["state"] == "open"


def test_decide_is_pure_and_states_its_reason():
    for verdict in sorted(ai.UNMEASURED_VERDICTS):
        want, why = ai.decide(ai.Condition("k", "t", verdict, False, "d"))
        assert want == ai.HOLD and why


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 4 · THE TITLE IS THE WHOLE NOTIFICATION
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_title_says_what_is_wrong_not_that_something_fired():
    c = ai.conditions_from_fleet_verdict(
        _fleet("FAILING", False, detail="a run of step1-fanout-autoscale.yml started 11:37 AM ET and "
                                        "FAILED, and the artifact is still stamped 10:06 AM ET"))[0]
    assert c.title.startswith("FLEET UNSUPERVISED [FAILING] —")
    assert "step1-fanout-autoscale.yml" in c.title
    assert len(c.title) <= 160
    for banned in ("alarm fired", "alert", "notification"):
        assert banned not in c.title.lower()


def test_a_lane_title_names_the_lane_and_the_verdict():
    c = ai.conditions_from_lane_report({"lanes": [{"lane": "step1_fanout", "ok": False,
                                                   "verdict": "BILLING-NOT-ADVANCING",
                                                   "detail": "4 hosts billing, 96 min with no new evidence"}]})[0]
    assert c.title.startswith("LANE step1_fanout [BILLING-NOT-ADVANCING] —")
    assert "4 hosts billing" in c.title


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 5 · STRUCTURAL — the alarm must not be able to die with the thing it reports on
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_it_imports_nothing_outside_the_stdlib_and_nothing_from_any_lane():
    """An escalation that shares a dependency with the fleet dies with the fleet. `boto3` is specifically
    banned: the mail path's dependency on it is half of why the email channel never delivered."""
    tree = ast.parse(open(MOD).read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    allowed = {"argparse", "datetime", "json", "os", "re", "sys", "time", "urllib", "__future__"}
    assert imported <= allowed, f"unexpected imports: {imported - allowed}"


def test_it_can_neither_rent_nor_destroy_nor_price_anything():
    """`issues: write` is the entire blast radius, and that is a structural property, not a promise.

    Asserted on CALLS rather than on raw text, exactly as `test_lane_staleness_watch` does: the docstring
    discusses Vast, boto3 and destruction at length, and a text match would fail on the incident notes —
    which is the kind of false positive that gets a guard deleted.
    """
    tree = ast.parse(open(MOD).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            assert name not in ("destroy", "reap", "rent", "submit", "launch", "collect", "nudge",
                                "run", "Popen", "system", "check_output", "client"), \
                f"destructive/side-effecting call {name}"


def test_dedupe_never_uses_the_eventually_consistent_search_api():
    """GitHub's search index lags by seconds to minutes. A dedupe that misses opens a second issue, which is
    the exact failure this module exists to prevent."""
    src = open(MOD).read()
    assert "/search/" not in src and "search/issues" not in src


def test_pull_requests_are_not_mistaken_for_issues():
    """The issues endpoint returns PRs too; matching one would attach an alarm to somebody's branch."""
    gh = FakeGitHub()
    gh.issues.append({"number": 99, "state": "open", "title": "a PR", "pull_request": {"url": "x"},
                      "body": ai._mark("key", "fleet-supervision")})
    acts = _run(ai.conditions_from_fleet_verdict(_fleet("FAILING", False)), gh)
    assert acts[0]["action"] == "created" and acts[0]["issue"] != 99


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 6 · THE CLI — a missing verdict must never read as green
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_an_unreadable_verdict_file_is_an_error_not_silence(tmp_path, capsys):
    rc = ai.main(["--fleet-verdict", str(tmp_path / "nope.json"), "--dry-run"])
    assert rc == 1
    assert "ALARM SOURCE UNREADABLE" in capsys.readouterr().err


def test_dry_run_touches_nothing(tmp_path, capsys, monkeypatch):
    p = tmp_path / "v.json"
    p.write_text(json.dumps(_fleet("FAILING", False)))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    def boom(*a, **k):
        raise AssertionError("dry-run reached the network")
    monkeypatch.setattr(ai.GitHubIssues, "request", boom)
    monkeypatch.setattr(ai.GitHubIssues, "open_issues", lambda self: [])
    assert ai.main(["--fleet-verdict", str(p), "--dry-run"]) == 0
    assert "would-create" in capsys.readouterr().out


def test_no_token_is_a_red_run_not_a_quiet_one(tmp_path, capsys, monkeypatch):
    """The one credential we are certain of is GITHUB_TOKEN. If even that is gone, say so loudly rather than
    exiting 0 — a silent escalation channel is the thing being fixed."""
    p = tmp_path / "v.json"
    p.write_text(json.dumps(_fleet("FAILING", False)))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert ai.main(["--fleet-verdict", str(p)]) == 1
    assert "ALARM CHANNEL HAS NO TOKEN" in capsys.readouterr().err


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 7 · THE SELF-TEST — an unexercised channel is exactly what just turned out to be broken
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
def test_the_self_test_uses_its_own_key_so_it_can_never_mask_a_real_alarm():
    keys = {ai.self_test_conditions(p, NOW)[0].key for p in ("fire", "fire-changed", "recover", "unmeasured")}
    assert keys == {"alarm-self-test"}
    assert "fleet-supervision" not in keys


def test_the_self_test_walks_fire_dedupe_change_recover():
    gh = FakeGitHub()
    a1 = _run(ai.self_test_conditions("fire", NOW), gh)
    a2 = _run(ai.self_test_conditions("fire", NOW), gh)
    a3 = _run(ai.self_test_conditions("fire-changed", NOW), gh)
    a4 = _run(ai.self_test_conditions("recover", NOW), gh)
    assert [a[0]["action"] for a in (a1, a2, a3, a4)] == ["created", "updated", "commented", "closed"]
    assert len(gh.issues) == 1 and gh.issues[0]["state"] == "closed"


def test_the_self_tests_unmeasured_phase_is_held():
    gh = FakeGitHub()
    assert _run(ai.self_test_conditions("unmeasured", NOW), gh)[0]["action"] == "held"


def test_the_self_test_title_says_it_is_a_drill():
    t = ai.self_test_conditions("fire", NOW)[0].title
    assert t.startswith("[alarm self-test]") and "drill" in t.lower()


# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
# 8 · THE WORKFLOWS ARE WIRED TO IT, AND NO LONGER CLAIM EMAIL COVERAGE THEY DO NOT HAVE
# ═════════════════════════════════════════════════════════════════════════════════════════════════════════
WF = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".github", "workflows")


@pytest.mark.parametrize("wf", ["fleet-supervision-alarm.yml", "lane-staleness-watch.yml"])
def test_the_alarm_workflows_actually_call_the_channel_and_hold_the_permission(wf):
    src = open(os.path.join(WF, wf)).read()
    assert "alarm_issue.py" in src, f"{wf} produces a verdict nobody escalates"
    assert "issues: write" in src, f"{wf} cannot open an issue without issues: write"
    assert "if: ${{ always() }}" in src, f"{wf} must escalate on the run where the check went red"


def test_the_lane_watch_no_longer_advertises_email_it_cannot_send():
    """CLAUDE.md §1: a comment promising a notification that cannot be sent is a documentation defect. SES
    has never been authorised for `nr4a3-ci-submitter`, and the sandbox story in the old comment was the
    wrong diagnosis."""
    src = open(os.path.join(WF, "lane-staleness-watch.yml")).read()
    assert "SES may still be sandboxed" not in src
    assert "notification-channels.md" in src, "the honest status must point at its one home"
    assert 'default: "0"' in src.split("email_on_fail")[1][:400], \
        "an undeduplicated email channel must not default on"
