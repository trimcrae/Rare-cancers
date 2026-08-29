#!/usr/bin/env python3
"""A tracked hook in `.claude/` is a file this repository HAS, and K3 must say so — but a name in no
code directory must still be flagged (trunk red 2026-08-29, CYC-0073-d4ccfde4).

⛔⛔ THE DEFECT: `tests.yml` failed on `main` at 264d7a7b1 — "1 failed, 10714 passed" — on one K3
warning naming `merge-debt-at-turn-end.sh`. That file EXISTS: tracked, executable, and wired as a
`Stop` hook by `.claude/settings.json`. It was present at every ref involved, and it landed in the
SAME commit (e9876959e) as the CLAUDE.md sentence citing it, so this was never the "doc landed, file
didn't" split it resembles. `CODE_DIRS` simply had no `.claude`, so `check_code_citations` could not
know any hook existed and reported a followable instruction as a DEAD POINTER.

⚠ WHY IT LAY DORMANT FOR SO LONG, which is the half worth keeping. `CODE_CITE` matches a BARE
backticked filename. CLAUDE.md cites `.claude/hooks/no-detached-background.py` as a backticked PATH,
which the regex never matched — so the same blind spot sat under two other hooks without ever firing.
It surfaced only when someone wrote a markdown link whose backticked text is the bare filename. The
trigger was citation FORMAT, not file existence, which is why "the other hooks are fine" was never
evidence that the directory model was.

⛔ WHY THIS SUITE HAS TWO HALVES AND NEEDS BOTH. Adding a directory to `CODE_DIRS` can only ever
REDUCE warnings, so it is exactly the shape a silencer takes. The first test alone would pass just as
happily if someone disabled K3 outright. The second pins the guard's teeth: a name in no code
directory is still flagged. Together they say "resolve real files, keep catching dead ones", which is
the only reading under which this change is a correctness fix rather than an exemption.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEMS = os.path.dirname(HERE)
REPO = os.path.dirname(SYSTEMS)
sys.path.insert(0, SYSTEMS)

import systems_check as S  # noqa: E402


class _F:
    """The findings sink `check_code_citations` writes into."""

    def __init__(self):
        self.warns, self.errs = [], []

    def warn(self, tag, msg):
        self.warns.append((tag, msg))

    def err(self, tag, msg):
        self.errs.append((tag, msg))


def _k3():
    f = _F()
    S.check_code_citations(None, f)
    return [m for tag, m in f.warns if tag == "[K3]"]


def test_dot_claude_is_a_code_directory():
    """The directory model must include `.claude` — hooks there are tracked, executable and cited."""
    assert ".claude" in S.CODE_DIRS, (
        "`.claude` is not in CODE_DIRS, so every tracked hook under .claude/hooks/ is unknowable to "
        "K3 and any bare backticked citation of one reads as a dead pointer. That redded the trunk "
        "on 2026-08-29.")


def test_the_committed_hooks_are_known_to_the_checker():
    """The real files, by name — not a directory string that might point nowhere."""
    hooks = os.path.join(REPO, ".claude", "hooks")
    assert os.path.isdir(hooks), ".claude/hooks/ is missing — this suite is asserting nothing"
    known = set()
    for d in S.CODE_DIRS:
        p = os.path.join(S.REPO, d)
        if os.path.isdir(p):
            for _root, _dirs, files in os.walk(p):
                known.update(files)
    for name in os.listdir(hooks):
        if os.path.isfile(os.path.join(hooks, name)):
            assert name in known, f"`{name}` is a committed hook the citation checker cannot see"


def test_no_committed_document_names_a_dead_hook():
    """The regression itself: K3 must be silent on the committed tree."""
    assert _k3() == [], (
        "K3 is flagging a name on the committed tree. If the file genuinely does not exist this is a "
        "real dead pointer and the DOCUMENT is what to fix; if it does exist, the directory model in "
        "CODE_DIRS is what to fix. Do NOT add a CODE_CITE_CLEARED phrase to silence a live citation.")


def test_the_guard_actually_fires_on_a_dead_name(monkeypatch):
    """⛔⛔ THE TEETH, AND THE FIRST VERSION OF THIS TEST HAD NONE. It recomputed `known` itself and
    asserted a fabricated name was absent from it — which exercises the SET, not the GUARD. Every
    assertion in this file would have gone on passing if `check_code_citations` were made a no-op,
    because the only test touching the warning path asserts it is EMPTY. Adding a directory to
    CODE_DIRS can only reduce warnings, so a suite that never sees the guard fire cannot tell a
    correctness fix from a silencer — which is the exact thing this fix must prove it is not.

    So: feed the checker a synthetic document and assert it FIRES."""
    docs = [("SYNTHETIC.md", "a sentence naming `definitely-not-a-real-hook-9f3a2b.sh` and nothing else")]
    monkeypatch.setattr(S, "_walk_md", lambda skip: iter(docs))
    warns = _k3()
    assert len(warns) == 1, f"K3 did not fire on a name in no code directory: {warns}"
    assert "definitely-not-a-real-hook-9f3a2b.sh" in warns[0]


def test_the_guard_is_silent_on_a_live_hook(monkeypatch):
    """The other half, through the same door: the identical citation SHAPE, naming a file that really
    is in `.claude/hooks/`, must NOT fire. Together with the test above this pins the fix as
    'resolve real files, keep catching dead ones' rather than 'warn less'."""
    hooks = os.path.join(REPO, ".claude", "hooks")
    live = sorted(n for n in os.listdir(hooks) if os.path.isfile(os.path.join(hooks, n)))
    assert live, ".claude/hooks/ is empty — this test is asserting nothing"
    docs = [("SYNTHETIC.md", f"a sentence naming `{live[0]}` and nothing else")]
    monkeypatch.setattr(S, "_walk_md", lambda skip: iter(docs))
    assert _k3() == [], f"`{live[0]}` is a committed hook and K3 flagged it as a dead pointer"


def test_the_cleared_phrases_did_not_grow_to_cover_this():
    """A citation is cleared only by a human writing a REASON on the line. If the fix for a dead
    pointer ever arrives as a new entry here instead, that is the silencer this guard warns about."""
    assert "hook" not in [p.lower() for p in S.CODE_CITE_CLEARED], (
        "a blanket 'hook' clearing phrase would silence every hook citation, live or dead")
