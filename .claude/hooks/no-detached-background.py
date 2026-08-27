#!/usr/bin/env python3
"""Refuse a Bash command that backgrounds itself with a shell `&`.

⛔⛔ THE FAILURE THIS EXISTS FOR, MEASURED 2026-08-27 AND TWICE IN ONE SESSION. There are two ways to
run something in the background from here and they are NOT equivalent:

    run_in_background: true   the HARNESS tracks the job, and wakes the session when it exits
    ... &                     the shell detaches it. Nothing tracks it. NOTHING EVER WAKES.

A turn that ends after `... &` ends with the work orphaned. The session reports "in flight", goes
idle, and never returns — a stall that looks exactly like progress, which is the shape CLAUDE.md §4
and `stall_alarm.py` both exist to attack. Cost that day: two preflight runs abandoned mid-flight (one
died at 35 lines with no exit marker) and one user having to notice the silence and say so.

⚠ AND IT IS SPECIFICALLY THE SHAPE THAT LOOKS RESPONSIBLE. `&` FEELS like the careful move — it keeps
the foreground free, which CLAUDE.md §1 demands. It satisfies the letter of that rule and breaks the
thing the rule is for.

★ THE TEST A READER SHOULD APPLY: after this command, is there anything that will bring the session
back? `run_in_background: true` answers yes. A bare `&` answers no.

Blocks only genuine detachment. `&&`, `2>&1`, `&>`, `>&` and `&` inside a quoted string are untouched
— a hook that reds on true input is one that gets switched off (`paper-hardening` §8b.1).
"""

from __future__ import annotations

import json
import re
import sys

#: Substrings that contain a literal `&` and mean nothing like backgrounding. Removed before the
#: scan so they cannot manufacture a false positive.
_NOT_BACKGROUNDING = (r"&&", r"2>&1", r"1>&2", r"&>>", r"&>", r">&")

#: ⚠ ONCE QUOTES AND EVERY REDIRECT FORM ARE STRIPPED, A BARE `&` IS THE SHELL'S BACKGROUND
#: OPERATOR — there is no other meaning left for it. An earlier version matched only `&` at the end
#: of a command or line and MISSED `cmd & other`, which backgrounds `cmd` just as thoroughly. Caught
#: by its own case table before the hook was registered; a pattern that is nearly right is the one
#: that gets trusted.
_DETACH = re.compile(r"&")


#: ⛔⛔ A HEREDOC BODY IS DATA, NOT SHELL — AND THIS HOOK BLOCKED ITS OWN COMMIT OVER IT.
#: Caught on the FIRST LIVE USE, 2026-08-27, one minute after registration: the
#: `git commit -F - <<'MSG' ... MSG` carrying this hook into the repository was refused, because the
#: commit message EXPLAINS what a trailing ampersand does and therefore contains one. That command
#: backgrounds nothing. It then blocked the patch fixing it, for the same reason.
#: ★ THIS IS EXACTLY THE FAILURE THE MODULE DOCSTRING NAMES — a gate that reds on TRUE input — and
#: the module produced it against itself within a minute. It is also why the repair went HERE and not
#: into a workaround at the call site: the first person to meet a gate that refuses correct work is
#: the person who switches it off (`paper-hardening` §8b.1). A guard is only allowed to survive its
#: own false positive by being fixed.
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")


def _strip_heredocs(cmd: str) -> str:
    """Blank every heredoc BODY, keeping line structure so nothing else shifts."""
    lines, out, i = cmd.split("\n"), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        match = _HEREDOC.search(line)
        i += 1
        if not match:
            continue
        terminator = match.group(2)
        while i < len(lines) and lines[i].strip() != terminator:
            out.append("")           # body is data; drop it entirely
            i += 1
        if i < len(lines):
            out.append(lines[i])     # the terminator line itself
            i += 1
    return "\n".join(out)


def _strip_quoted(cmd: str) -> str:
    """Blank out quoted spans so an `&` inside a string literal is never read as an operator."""
    out, quote = [], None
    for ch in cmd:
        if quote:
            out.append(" " if ch != quote else ch)
            if ch == quote:
                quote = None
        else:
            out.append(ch)
            if ch in "'\"":
                quote = ch
    return "".join(out)


def detaches(command: str) -> bool:
    """True when the command backgrounds itself with a shell `&`."""
    scan = _strip_quoted(_strip_heredocs(command or ""))
    for token in _NOT_BACKGROUNDING:
        scan = scan.replace(token, " ")
    return bool(_DETACH.search(scan))


REASON = (
    "⛔ BLOCKED: this command backgrounds itself with a shell `&`, which DETACHES it from the "
    "harness. Nothing tracks a detached job and nothing will ever wake this session when it "
    "finishes — the turn ends, the work is orphaned, and the session reports 'in flight' and goes "
    "silent. Measured 2026-08-27: two preflight runs abandoned that way, one dead at 35 lines with "
    "no exit marker.\n"
    "⭐ USE THE TOOL'S OWN BACKGROUNDING INSTEAD: pass run_in_background: true. It returns a task id "
    "and the harness notifies this session on exit, which is the only form that keeps the foreground "
    "free AND comes back.\n"
    "⚠ If you genuinely want fire-and-forget with no result, say so in the command's description and "
    "write the `&` inside a quoted string — but ask first whether anything downstream needs the "
    "result, because twice today the answer was yes."
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                      # ⚠ Fail OPEN on an unreadable payload: a hook that blocks every
                                      # Bash call because the harness changed shape is worse than the
                                      # defect it guards.
    if payload.get("tool_name") != "Bash":
        return 0
    command = (payload.get("tool_input") or {}).get("command", "")
    if not detaches(command):
        return 0
    print(REASON, file=sys.stderr)
    return 2                          # PreToolUse: exit 2 denies the call and returns stderr.


if __name__ == "__main__":
    sys.exit(main())
