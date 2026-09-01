"""⛔⛔ THE HOOK THAT ENFORCES CLAUDE.md §3 HAD NEVER ONCE FIRED, AND NOTHING TESTED IT.

`escalation-debt-at-turn-end.sh` refuses a stop when a `requires_trimcrae` row has never been sent.
CLAUDE.md §3 names it as the enforcement for a rule added on 2026-08-29 — added precisely BECAUSE a
correct rule sat in the file that loads every session, measured by nothing, while fourteen decisions
went unsent.

⚠ THE REMEDY HAD THE SAME DEFECT. It read the ledger with
`printf '%s' "$LEDGER_JSON" | python3 - <<'PYEOF'` — a pipe AND a heredoc on one stdin. The heredoc
supplies the SCRIPT and the piped JSON is discarded, so `json.load(sys.stdin)` saw ZERO bytes, raised,
and hit a bare `except: sys.exit(0)`. Measured directly: that construction with a script reporting
`len(sys.stdin.read())` prints 0. On the day it was found there were FIFTEEN open `requires_trimcrae`
rows and not one carried `notified_utc`.

★ SO THE ASSERTIONS HERE ARE ABOUT REACHABILITY FIRST AND VERDICTS SECOND. A hook that returns 0
because it read nothing is indistinguishable, from the outside, from a hook that read everything and
found nothing wrong — and this file exists because that difference went unnoticed for days.
"""
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
HOOK = os.path.join(REPO, ".claude", "hooks", "escalation-debt-at-turn-end.sh")

REFUSES = 2


def _ledger(tmp_path, entries):
    """A ledger on disk plus a git repo whose origin/main does NOT carry it.

    The hook prefers `git show origin/main:…` and falls back to the working tree, so a scratch repo
    with no origin exercises the fallback — which is the path a test can control.
    """
    root = tmp_path / "repo"
    (root / "research" / "autonomy").mkdir(parents=True)
    (root / ".claude" / "hooks").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / "research" / "autonomy" / "research-ledger.json").write_text(
        json.dumps({"entries": entries}), encoding="utf-8")
    import shutil
    shutil.copy(HOOK, root / ".claude" / "hooks" / os.path.basename(HOOK))
    return root


def _run(root):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    return subprocess.run(
        ["bash", str(root / ".claude" / "hooks" / os.path.basename(HOOK))],
        input="{}", capture_output=True, text=True, env=env, cwd=str(root))


def test_an_unsent_decision_refuses_the_stop(tmp_path):
    """The one behaviour the hook exists for, and the one it never performed."""
    r = _run(_ledger(tmp_path, [
        {"id": "AUT-X", "requires_trimcrae": True, "state": "queued", "score": 99.0,
         "what": "a decision only trimcrae can take"}]))
    assert r.returncode == REFUSES, (
        "an unsent requires_trimcrae row did not refuse the stop — the hook either did not read the "
        f"ledger or did not act on it (rc={r.returncode}, stderr={r.stderr[:300]!r})")
    assert "AUT-X" in r.stderr


def test_a_ledger_it_cannot_read_says_so_instead_of_passing_quietly(tmp_path):
    """⛔ THE DEFECT'S OWN SHAPE, PINNED. A bare `except: sys.exit(0)` cannot tell "this ledger is
    malformed" from "I was handed nothing", and both looked exactly like "nothing is wrong"."""
    root = _ledger(tmp_path, [])
    (root / "research" / "autonomy" / "research-ledger.json").write_text("{not json", encoding="utf-8")
    r = _run(root)
    assert r.returncode == 0, "an unreadable ledger must not block a session"
    assert "UNMEASURED" in r.stderr, (
        "the hook stood down silently on a ledger it could not parse. Silence here is the exact "
        f"state that hid this defect for days. stderr={r.stderr[:300]!r}")


def test_a_notified_row_does_not_refuse(tmp_path):
    """⚠ THE CONTROL. A hook that refuses everything passes the first test; this says it still opens
    — and `notified_utc` is what opens it, which is the whole point of requiring the stamp."""
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = _run(_ledger(tmp_path, [
        {"id": "AUT-X", "requires_trimcrae": True, "state": "queued", "score": 99.0,
         "what": "already sent", "notified_utc": now}]))
    assert r.returncode == 0, f"a freshly-notified row still refused the stop: {r.stderr[:300]!r}"


def test_a_closed_decision_is_not_chased(tmp_path):
    """⚠ THIS LEDGER'S FIELD IS `state`, NOT `status`, AND THE HOOK READ ONLY `status`. Harmless
    while it was inert; a false alarm on every stop the moment it started working."""
    r = _run(_ledger(tmp_path, [
        {"id": "AUT-DONE", "requires_trimcrae": True, "state": "done", "score": 99.0,
         "what": "resolved long ago"}]))
    assert r.returncode == 0, (
        "a row in state 'done' was chased as an unsent decision — the hook is reading a field this "
        f"ledger does not use. stderr={r.stderr[:300]!r}")


def test_it_finds_its_repository_with_no_env_var(tmp_path):
    """AUT-PD-201's defect, in this hook too: a hardcoded absolute path makes it a no-op wherever
    the project lives somewhere else, and every test above runs with the variable unset.

    ⛔⛔ IT ASSERTS **WHICH** LEDGER WAS READ, NOT MERELY THAT SOMETHING REFUSED — AND THE FIRST
    VERSION DID NOT. Found by mutation on 2026-09-01: restoring the hardcoded
    `REPO="${CLAUDE_PROJECT_DIR:-/home/user/Rare-cancers}"` left this test GREEN, because on the
    machine it was written on that path exists. The hook cd'd into the REAL repository, found its
    fifteen genuinely unsent rows, and refused — the right exit code for entirely the wrong reason,
    while the scratch ledger this test built went unread.
    ★ A row id that exists only in `tmp_path` is the discriminating observation, and it is the same
    lesson as the fake API keyed on its own assumption: a double shaped like the thing it is
    standing in for measures the double.
    """
    root = _ledger(tmp_path, [
        {"id": "AUT-SCRATCH-ONLY", "requires_trimcrae": True, "state": "queued", "score": 1.0,
         "what": "a row that exists nowhere but this tmp_path"}])
    r = _run(root)
    assert r.returncode == REFUSES
    assert "AUT-SCRATCH-ONLY" in r.stderr, (
        "the hook refused, but not over the ledger this test wrote — it resolved some other "
        f"repository, so its own location is not what it used. stderr={r.stderr[:300]!r}")


def test_it_cannot_trap_a_session(tmp_path):
    root = _ledger(tmp_path, [
        {"id": "AUT-X", "requires_trimcrae": True, "state": "queued", "score": 1.0, "what": "w"}])
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    r = subprocess.run(["bash", str(root / ".claude" / "hooks" / os.path.basename(HOOK))],
                       input=json.dumps({"stop_hook_active": True}),
                       capture_output=True, text=True, env=env, cwd=str(root))
    assert r.returncode == 0, "a Stop hook that fires when already active can loop a session forever"
