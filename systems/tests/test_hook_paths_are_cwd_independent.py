"""Every hook command must resolve independently of the working directory.

⛔⛔ A RELATIVE HOOK PATH IS A ONE-WAY DOOR, AND ONE WAS SHIPPED ON 2026-08-27. The anti-detach
PreToolUse hook was registered as `python3 .claude/hooks/no-detached-background.py`. The Bash tool's
working directory PERSISTS between calls, so a single `cd research/autonomy/receipts` inside one
compound command moved it — and every subsequent Bash call, `pwd` included, died before running:

    python3: can't open file
    '/home/user/Rare-cancers/research/autonomy/receipts/.claude/hooks/no-detached-background.py'

★ THE RESOLVED PATH IS THE WHOLE DIAGNOSIS: `<persisted cwd>/.claude/hooks/…`. And it is
UNRECOVERABLE from inside the session, because every recovery command is itself a Bash call that the
broken hook refuses first. A PreToolUse hook on Bash is the most dangerous place in this repository
to put a relative path: it runs before every command, so when it cannot be found, nothing can run —
including the fix.

⚠ FOUND BY THE SUCCESSOR SESSION, WITHIN MINUTES OF BEING SPAWNED, AND THAT IS THE HANDOFF WORKING.
The session that shipped the bug had already ended its cycle. The one that inherited the repo hit it,
diagnosed it from the resolved path rather than guessing, and fixed it (`69d8a6ac1`).

⭐ THIS FILE EXISTS BECAUSE THAT FIX CLOSED THE INSTANCE AND NOT THE CLASS. `paper-hardening` §8b.2,
measured over 33 mutations: a fix bound to a LIST regresses at a sibling; a fix bound to a PREDICATE
does not. A second relative hook command was still sitting in the same file — `SessionStart` running
`./scripts/dev-setup.sh` — and would have been found by the next person to trip it rather than by a
test. Both now go through `CLAUDE_PROJECT_DIR`, and this guard is scoped by the property so a hook
added tomorrow is covered without anyone remembering.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
SETTINGS = REPO / ".claude" / "settings.json"

#: A command that names a file inside this repository, HOWEVER it is spelled — bare, `./`-prefixed,
#: or already routed through CLAUDE_PROJECT_DIR.
#: ⛔ THE FIRST VERSION ANCHORED EACH SEGMENT TO A QUOTE OR SPACE, so the moment the fix landed
#: (`"${CLAUDE_PROJECT_DIR:-.}/scripts/…"`) the segment sat after a `/` and matched nothing: the
#: parametrized guard SKIPPED all three commands and reported 2 passed, 3 skipped. It would still
#: have caught a revert — but on the good tree it measured NOTHING, which is this repository's most
#: frequently recorded failure, reproduced inside the guard written to close a different one.
#: `printf` and `echo` name no file and stay legitimately out of scope.
_REPO_PATH = re.compile(r"(?:\./|\.claude/|scripts/|research/|systems/)")


def _commands():
    settings = json.loads(SETTINGS.read_text())
    for event, groups in (settings.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks") or []:
                command = hook.get("command") or ""
                if command:
                    yield event, command


def test_settings_actually_registers_hooks():
    """A guard over an empty set passes vacuously — the failure mode this repository names most."""
    assert list(_commands()), "no hook commands found; this suite would pass while measuring nothing"


@pytest.mark.parametrize("event,command", list(_commands()),
                         ids=[f"{e}:{c[:34]}" for e, c in _commands()])
def test_a_hook_that_names_a_repo_file_resolves_independently_of_cwd(event, command):
    """⛔ THE ONE-WAY DOOR. The Bash tool's cwd persists across calls and the agent can move it. A hook
    command that resolves a repo path relatively breaks the moment it does — and for a PreToolUse hook
    on Bash, breaks every command including the one that would fix it."""
    if not _REPO_PATH.search(command):
        pytest.skip("names no repository file, so the working directory cannot break it")
    assert "CLAUDE_PROJECT_DIR" in command or command.lstrip('"').startswith("/"), (
        f"the {event} hook resolves a repository path against the working directory:\n"
        f"    {command}\n"
        "A `cd` in any earlier command relocates it and the hook stops being found. Use "
        '"${CLAUDE_PROJECT_DIR:-.}/..." — measured 2026-08-27, this exact shape bricked a session\'s '
        "Bash tool with no way back, because every recovery command was itself a Bash call."
    )


def test_the_pretooluse_bash_hook_is_the_dangerous_one_and_is_covered():
    """Named explicitly as well as by predicate: the severity is not uniform across events. A broken
    SessionStart hook costs a session's setup; a broken PreToolUse hook on Bash costs the session."""
    dangerous = [c for e, c in _commands() if e == "PreToolUse"]
    assert dangerous, "the anti-detach hook is no longer registered"
    for command in dangerous:
        assert "CLAUDE_PROJECT_DIR" in command or command.lstrip('"').startswith("/")
