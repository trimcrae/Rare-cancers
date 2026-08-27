"""Guards on the hook that refuses a Bash command backgrounding itself with a shell `&`.

⛔⛔ THE STALL THIS ATTACKS IS THE ONE THAT LOOKS LIKE PROGRESS. There are two ways to background work
here and they are NOT equivalent:

    run_in_background: true   the harness TRACKS the job and wakes the session when it exits
    ... &                     the shell detaches it; nothing tracks it, NOTHING EVER WAKES

A turn that ends after `... &` ends with the work orphaned. The session says "in flight", goes idle,
and never returns. Measured 2026-08-27, twice in one session: two preflight runs abandoned, one dead
at 35 lines with no exit marker, and the user had to notice the silence and say so.

★ AND IT IS THE SHAPE THAT LOOKS RESPONSIBLE, which is why a rule alone was never going to hold. `&`
keeps the foreground free — exactly what CLAUDE.md §1 demands — so it satisfies the letter of that
rule while destroying the thing the rule is for. This is the fifth rule in two days that was correct,
written down, and measured by nothing; it is the first to get a hook that can actually refuse.

⚠ THE FALSE-POSITIVE HALF MATTERS AS MUCH AS THE TRUE-POSITIVE HALF. `paper-hardening` §8b.1: a gate
that reds on true input is worse than one that greens on false input, because the first thing anyone
does is switch it off. `&&`, `2>&1`, `&>`, `1>&2` and any `&` inside a quoted string must pass
untouched, and each is pinned below.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
HOOK = REPO / ".claude" / "hooks" / "no-detached-background.py"
SETTINGS = REPO / ".claude" / "settings.json"


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("no_detached_background", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DETACHES = [
    ("./scripts/preflight.sh > log 2>&1 &", "the exact command that stalled, twice"),
    ("{ ./p.sh; echo EXIT=$?; } > log 2>&1 &", "a braced group, which is how preflight was run"),
    ("sleep 5 & wait", "backgrounds and then waits — still a detach, and it blocks the foreground too"),
    ("a & b", "`cmd & other` backgrounds cmd just as thoroughly as a trailing `&`"),
    ("python3 x.py &\n", "trailing newline after the operator"),
    ("cat <<'EOF'\nx &\nEOF\nsleep 1 &",
     "heredoc body is data, but a REAL detach after it must still be caught — stripping the body "
     "must not blind the scan to the rest of the command"),
]

#: ⛔⛔ THE HOOK'S FIRST LIVE ACT WAS TO BLOCK ITS OWN COMMIT. `git commit -F - <<'MSG' … MSG`
#: carrying this guard into the repository was refused, because the commit message EXPLAINS what a
#: trailing ampersand does and so contains one. It then blocked the patch that fixed it. A heredoc
#: body is DATA, not shell — and this is the false-positive-on-true-input failure the module docstring
#: names, produced by the module against itself within a minute of registration.
_HEREDOC_LIVE = "\n".join([
    "git commit -q -F - <<'MSG'",
    "    run_in_background: true   the harness tracks it",
    "    ... &                     detached, nothing ever wakes",
    "MSG",
    "git fetch -q origin main",
])

ALLOWED = [
    (_HEREDOC_LIVE, "THE LIVE CASE: an ampersand inside a heredoc commit message"),
    ("cat <<EOF\na & b\nEOF", "an unquoted heredoc body is data too"),
    ("a && b", "logical AND"),
    ("a && b && c", "chained AND"),
    ("cmd > log 2>&1", "the stderr redirect on nearly every command in this repo"),
    ("cmd &> log", "combined redirect"),
    ("cmd 1>&2", "stdout to stderr"),
    ("grep '&' file", "an ampersand inside a quoted string"),
    ("python3 -c \"print('a & b')\"", "quoted inside -c"),
    ("git log --format='%h %s' | grep '&&'", "a quoted && in a pipeline"),
]


@pytest.mark.parametrize("command,why", DETACHES, ids=[w for _, w in DETACHES])
def test_a_detaching_command_is_refused(hook, command, why):
    assert hook.detaches(command) is True, f"NOT caught: {why}"


@pytest.mark.parametrize("command,why", ALLOWED, ids=[w for _, w in ALLOWED])
def test_a_look_alike_is_not_refused(hook, command, why):
    """⛔ RED ON TRUE INPUT IS THE FAILURE THAT GETS A GATE SWITCHED OFF. Every one of these contains
    a literal `&` and none of them backgrounds anything."""
    assert hook.detaches(command) is False, f"FALSE POSITIVE on: {why}"


def test_the_hook_denies_through_its_real_cli_contract(hook):
    """Exercise the actual stdin/exit-code path, not just the predicate — a PreToolUse hook denies by
    exiting 2 with its reason on stderr, and a predicate that works inside a wrapper that does not is
    the one-of-a-pair defect this repository keeps finding."""
    payload = {"tool_name": "Bash", "tool_input": {"command": "./x.sh > log 2>&1 &"}}
    r = subprocess.run(["python3", str(HOOK)], input=json.dumps(payload),
                       capture_output=True, text=True)
    assert r.returncode == 2, "the hook did not DENY; a predicate nobody enforces guards nothing"
    assert "run_in_background" in r.stderr, "the denial must name the remedy, not just refuse"


def test_it_passes_a_clean_command_and_ignores_other_tools(hook):
    for payload in ({"tool_name": "Bash", "tool_input": {"command": "pytest -q && echo ok"}},
                    {"tool_name": "Read", "tool_input": {"file_path": "x &"}}):
        r = subprocess.run(["python3", str(HOOK)], input=json.dumps(payload),
                           capture_output=True, text=True)
        assert r.returncode == 0, f"blocked something it must not: {payload}"


def test_it_fails_OPEN_on_an_unreadable_payload(hook):
    """⚠ A hook that blocked every Bash call because the harness changed its payload shape would be
    worse than the defect it guards. Fail open, loudly in the code comment, never silently closed."""
    r = subprocess.run(["python3", str(HOOK)], input="not json", capture_output=True, text=True)
    assert r.returncode == 0


def test_the_hook_is_actually_registered(hook):
    """★ THE HALF THAT MAKES IT REAL. A hook file nobody registered is a rule nobody loads — the
    precise shape of the four rules this repository fixed the day before."""
    settings = json.loads(SETTINGS.read_text())
    pre = settings.get("hooks", {}).get("PreToolUse") or []
    matching = [h for h in pre if "no-detached-background" in json.dumps(h)]
    assert matching, "the hook exists on disk and is registered nowhere, so it never runs"
    assert any(h.get("matcher") == "Bash" for h in matching), "not matched to the Bash tool"


def test_claude_md_names_the_distinction(hook):
    """Reachability: the hook refuses at the call, but the reason has to be legible in the file that
    loads every session, or the refusal reads as an obstacle rather than a fix."""
    text = (REPO / "CLAUDE.md").read_text()
    assert "run_in_background" in text, "CLAUDE.md never names the form that comes back"
    # ⚠ ANY occurrence, not the first. The file mentions run_in_background in more than one place and
    # binding to text.index() pinned the OLDEST mention — a guard that reds on true input, caught on
    # its own first run.
    near = [text[max(0, i - 500):i + 700]
            for i in range(len(text)) if text.startswith("run_in_background", i)]
    assert any("&" in w and "detach" in w.lower() for w in near), (
        "CLAUDE.md names the tool flag but never says what it is UNLIKE. The whole defect is that a "
        "shell `&` looks like the same thing and orphans the work instead."
    )
