#!/usr/bin/env python3
"""The push door, asserted rather than remembered (AUT-PD-144).

⛔⛔ THE DEFECT THIS SUITE PINS. On 2026-08-28 two sessions filed `AUT-PD-140` four minutes apart;
the second had minted the id from state fetched before the first's commit, REBASED onto it and
pushed. The ledger's rows are separate array elements, so the rebase produced no conflict and no
marker, and a duplicate id reached `main`. `priority.py:merge` then refused the duplicated ledger,
so step 3 of the cycle contract — run before any item is taken — crashed for every session until the
row was renamed by hand.

★ THE GUARD THAT WOULD HAVE CAUGHT IT ALREADY EXISTED AND WAS CORRECT
(`test_ids_cannot_collide.py::test_the_committed_ledger_has_no_duplicate_ids`). It was simply not
run at the moment that mattered, because an integration performed AT PUSH TIME creates a third tree
— neither session's gated one — and nothing looks at it. So this suite is not about the assertion;
it is about WHERE the assertion is made, and about the two properties that decide whether such a
guard survives contact: it must refuse with the RIGHT REMEDY, and it must never become unpushable.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import push_guard as G  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
LEDGER = "research/autonomy/research-ledger.json"
HOOK = os.path.join(REPO, "scripts", "git-hooks", "pre-push")
DEV_SETUP = os.path.join(REPO, "scripts", "dev-setup.sh")

GOOD = {"_schema": "emc-research-ledger/1",
        "entries": [{"id": "AUT-PD-140", "state": "queued"},
                    {"id": "AUT-PD-141", "state": "done"}]}

#: The exact shape that landed: one id, two entirely different items, no textual conflict.
COLLIDED = {"_schema": "emc-research-ledger/1",
            "entries": [{"id": "AUT-PD-140", "state": "queued", "what": "session A's defect"},
                        {"id": "AUT-PD-140", "state": "queued", "what": "session B's defect"}]}

#: What `check_write` met mid-merge on 2026-08-29 and correctly called an unreadable baseline.
CONFLICTED = ('{"entries": [\n<<<<<<< HEAD\n  {"id": "AUT-PD-140"}\n=======\n'
              '  {"id": "AUT-PD-141"}\n>>>>>>> origin/main\n]}\n')


def _git(repo, *args, **kw):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True, **kw)


@pytest.fixture()
def repo(tmp_path):
    """A real repository, because every check here reads git objects rather than the filesystem."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "seat@example.invalid")
    _git(tmp_path, "config", "user.name", "seat")
    os.makedirs(tmp_path / "research" / "autonomy", exist_ok=True)
    (tmp_path / LEDGER).write_text(json.dumps(GOOD), encoding="utf-8")
    _git(tmp_path, "add", LEDGER)
    _git(tmp_path, "commit", "-qm", "base")
    return tmp_path


def _commit(repo, path, text, message):
    full = repo / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")
    _git(repo, "add", path)
    _git(repo, "commit", "-qm", message)
    return _git(repo, "rev-parse", "HEAD").stdout.decode().strip()


def _base(repo):
    return _git(repo, "rev-parse", "HEAD").stdout.decode().strip()


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE REGRESSION, at the door it actually came through.
# ---------------------------------------------------------------------------------------------

def test_a_duplicated_ledger_id_refuses_the_push(repo, capsys):
    """⛔⛔ THE MEASURED HARM. Nothing textual is wrong with this file — it is valid JSON and every
    row is well formed — which is exactly why the rebase produced no conflict and no marker."""
    base = _base(repo)
    tip = _commit(repo, LEDGER, json.dumps(COLLIDED), "rebased filing")
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 1
    err = capsys.readouterr().err
    assert "AUT-PD-140 used 2 times" in err, "the refusal must name the id and how often it appears"


def test_a_clean_ledger_passes(repo, capsys):
    base = _base(repo)
    tip = _commit(repo, LEDGER, json.dumps(
        {"entries": GOOD["entries"] + [{"id": "AUT-PD-142"}]}), "an honest filing")
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 0
    assert "REFUSED" not in capsys.readouterr().err


def test_the_positive_control_is_not_vacuous():
    """Without this, the assertion above passes on a checker that never finds anything."""
    with pytest.raises(G.Refusal):
        raise G.Refusal("h", "r")


# ---------------------------------------------------------------------------------------------
# ⭐ THE REMEDY IS PART OF THE VERDICT. A sibling seat's mutation survived on 2026-08-29 because its
# guard refused correctly and named the WRONG REMEDY, and the suite pinned only the exit code.
# ---------------------------------------------------------------------------------------------

def test_the_collision_remedy_says_reallocate_and_re_gate(repo, capsys):
    base = _base(repo)
    tip = _commit(repo, LEDGER, json.dumps(COLLIDED), "rebased filing")
    G.main(["--repo", str(repo), "--rev", tip, "--base", base])
    err = capsys.readouterr().err
    assert "next_entry_id" in err, "the reader must be told which allocator to re-mint from"
    assert "preflight.sh" in err, "an integrated tree has to be re-gated, not merely repaired"
    assert "Do not renumber the row that was already on the trunk" in err, (
        "renumbering the trunk's row instead of your own is the wrong half to move, and it is the "
        "half a session under time pressure reaches for")


def test_an_unparseable_ledger_remedy_says_restore_the_baseline(repo, capsys):
    """⛔ A DIFFERENT FAILURE NEEDS A DIFFERENT REMEDY. Re-minting an id does nothing for a file
    holding conflict markers, and restoring the baseline does nothing for a collision."""
    base = _base(repo)
    tip = _commit(repo, LEDGER, CONFLICTED, "half-applied merge")
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 1
    err = capsys.readouterr().err
    assert "git checkout origin/main -- research/autonomy/research-ledger.json" in err
    assert "OBSERVATIONS only" in err, (
        "carrying a derived score across an integration is what `admissibility` R3 refused on "
        "2026-08-29 — the ranker must re-derive it")


def test_the_two_refusals_do_not_share_a_remedy(repo):
    """⛔ COLLAPSING THEM WOULD PASS BOTH VERDICT TESTS AND LEAVE ONE READER MISDIRECTED."""
    with pytest.raises(G.Refusal) as collided:
        _run_check(repo, COLLIDED)
    with pytest.raises(G.Refusal) as unparseable:
        _run_check(repo, CONFLICTED, raw=True)
    assert collided.value.remedy != unparseable.value.remedy
    assert collided.value.headline != unparseable.value.headline


def _run_check(repo, payload, raw=False):
    tip = _commit(repo, LEDGER, payload if raw else json.dumps(payload), "x")
    G.check_ledger(str(repo), tip)


# ---------------------------------------------------------------------------------------------
# ⚠ THE PROPERTIES THAT DECIDE WHETHER THIS GUARD SURVIVES: it must not brick the repository, and
# it must not claim to have checked what it could not read.
# ---------------------------------------------------------------------------------------------

def test_a_broken_state_file_the_push_does_not_touch_never_blocks_it(repo, capsys):
    """⛔⛔ THE BRICK CASE. If one already-broken file under research/autonomy refuses every push,
    the loop has no channel left to fix it — a guard that cannot be pushed past gets deleted."""
    _commit(repo, "research/autonomy/health.json", "{ not json", "pre-existing breakage")
    base = _base(repo)
    tip = _commit(repo, "research/autonomy/notes.txt", "unrelated", "an unrelated push")
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 0
    assert "REFUSED" not in capsys.readouterr().err


def test_a_state_file_this_push_breaks_is_refused_and_named(repo, capsys):
    base = _base(repo)
    tip = _commit(repo, "research/autonomy/health.json", "{ not json", "breaks it now")
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 1
    assert "research/autonomy/health.json" in capsys.readouterr().err


def test_a_broken_jsonl_line_is_refused(repo, capsys):
    base = _base(repo)
    tip = _commit(repo, "research/autonomy/amendments.jsonl",
                  '{"a": 1}\n<<<<<<< HEAD\n', "half-applied append")
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 1
    assert "amendments.jsonl" in capsys.readouterr().err


def test_a_tree_without_a_ledger_is_not_a_refusal(tmp_path):
    """⚠ AN ABSENT FILE IS NOTHING TO CHECK; AN UNREADABLE ONE IS THE DEFECT. Collapsing the two
    into one `except: pass` is the mutation that makes this whole module silently pass."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "s@e.invalid")
    _git(tmp_path, "config", "user.name", "s")
    tip = _commit(tmp_path, "README.md", "no ledger here", "old branch")
    assert G.main(["--repo", str(tmp_path), "--rev", tip]) == 0


def test_infrastructure_failure_fails_open_and_says_so(repo, monkeypatch, capsys):
    """⛔ FAIL OPEN ON THE MACHINERY, CLOSED ON THE INVARIANT — and LOUDLY, because a silent
    fail-open is indistinguishable from a pass (CLAUDE.md §4)."""
    monkeypatch.setattr(G, "_base", lambda *a, **k: (_ for _ in ()).throw(OSError("git is gone")))
    assert G.main(["--repo", str(repo), "--rev", _base(repo)]) == 0
    err = capsys.readouterr().err
    assert "did NOT check this push" in err and "git is gone" in err


def test_the_live_trunk_ledger_passes_this_guard():
    """⛔ THE GUARD MUST NOT RED THE REPOSITORY IT SHIPS IN. If this ever fails, `main` is carrying
    a duplicated id right now and step 3 of the cycle contract is already crashing."""
    G.check_ledger(REPO, "HEAD")


# ---------------------------------------------------------------------------------------------
# The pre-push protocol itself, which is the only input git will ever hand this.
# ---------------------------------------------------------------------------------------------

def test_the_protocol_line_refuses_a_bad_tip(repo, monkeypatch, capsys):
    base = _base(repo)
    tip = _commit(repo, LEDGER, json.dumps(COLLIDED), "rebased filing")
    monkeypatch.setattr(sys, "stdin", _Stdin(f"refs/heads/main {tip} refs/heads/main {base}\n"))
    assert G.main(["--repo", str(repo)]) == 1
    assert "refs/heads/main" in capsys.readouterr().err


def test_a_ref_being_deleted_carries_no_tree(repo, monkeypatch):
    """⚠ git sends all-zeros for the local sha when a ref is being DELETED. Reading it as a commit
    makes the hook error on a legitimate `git push --delete`, which is how a guard earns a
    `--no-verify` habit."""
    monkeypatch.setattr(sys, "stdin", _Stdin(f"(delete) {G.ZERO} refs/heads/gone {_base(repo)}\n"))
    assert G.main(["--repo", str(repo)]) == 0


def test_empty_input_is_not_an_error(repo, monkeypatch):
    monkeypatch.setattr(sys, "stdin", _Stdin(""))
    assert G.main(["--repo", str(repo)]) == 0


class _Stdin:
    def __init__(self, text): self._text = text
    def read(self): return self._text


# ---------------------------------------------------------------------------------------------
# ⚠ THE NOTICE HALF (AUT-PD-154), which reports and does not refuse — and the suite pins that it
# does not, because a check that quietly grew teeth would block the loop's own claim path.
# ---------------------------------------------------------------------------------------------

def test_a_carried_merge_is_reported_but_never_refused(repo, capsys):
    """⭐ THE LIVE INSTANCE, 2026-08-29: a seat's `claim.py` run merged the driver's unpushed local
    `main` and published it as 818c472f0 — 22 files from its second parent, gated by nobody. Every
    carried commit happened to be green, which is the dangerous half: there was no signal at all."""
    base = _base(repo)
    _git(repo, "checkout", "-q", "-b", "side")
    _commit(repo, "research/autonomy/other.txt", "somebody else's work", "side work")
    _git(repo, "checkout", "-q", "main")
    _commit(repo, "research/autonomy/mine.txt", "my one row", "my claim")
    _git(repo, "merge", "-q", "--no-ff", "side", "-m", "Merge branch 'side'")
    tip = _git(repo, "rev-parse", "HEAD").stdout.decode().strip()
    assert G.main(["--repo", str(repo), "--rev", tip, "--base", base]) == 0, (
        "the notice must not refuse: a hard 'the tip must be a gated tree' rule needs a carve-out "
        "for claim.py, and the carve-out is the hole — that is AUT-PD-154's work, not this file's")
    err = capsys.readouterr().err
    assert "introduces merge" in err and "second parent" in err


def test_a_push_with_no_merge_reports_nothing(repo, capsys):
    base = _base(repo)
    tip = _commit(repo, "research/autonomy/mine.txt", "one row", "ordinary commit")
    G.main(["--repo", str(repo), "--rev", tip, "--base", base])
    assert "introduces merge" not in capsys.readouterr().err


# ---------------------------------------------------------------------------------------------
# ⛔ A HOOK NOBODY INSTALLS IS PROSE. These are the two files that make the guard actually run.
# ---------------------------------------------------------------------------------------------

def test_the_hook_exists_is_executable_and_calls_the_guard():
    assert os.path.exists(HOOK), "scripts/git-hooks/pre-push is what git invokes; without it nothing runs"
    assert os.access(HOOK, os.X_OK), "git silently ignores a non-executable hook — a fail-open with no message"
    assert "push_guard.py" in open(HOOK, encoding="utf-8").read()


def test_dev_setup_arms_the_hook_above_its_own_early_exit():
    """⚠ THE PLACEMENT IS THE POINT, AND THIS FILE HAS PAID FOR IT ONCE ALREADY. `--if-needed` is
    what the SessionStart hook runs and it exits early on a sandbox whose interpreters are complete;
    a step below that exit never runs on the machines that need it most."""
    text = open(DEV_SETUP, encoding="utf-8").read()
    assert "core.hooksPath" in text and "scripts/git-hooks" in text
    arm = text.index("git config core.hooksPath")
    early_exit = text.index('if [ "${1:-}" = "--if-needed" ]')
    assert arm < early_exit, (
        "the hook is armed behind the dependency probe's answer, so a session whose interpreters "
        "were already complete would push unguarded")


# ---------------------------------------------------------------------------------------------
# ⭐ THE MUTANT THAT SURVIVED, AND THE ASSERTION THAT KILLS IT. Deleting the all-zeros skip from
# `main()` passed all 19 tests above (mutation M6): every downstream git call ALSO fails on that
# sha and every one of them swallows the failure, so a deletion passing for the right reason and a
# deletion passing for three unreadable-object errors look identical from outside. Parsing is now
# its own function so the skip is a property a test can see rather than an incidental one.
# ---------------------------------------------------------------------------------------------

def test_the_protocol_parser_drops_a_deleted_ref_and_keeps_a_real_one():
    tip, remote = "a" * 40, "b" * 40
    pairs = G.protocol_pairs(
        f"(delete) {G.ZERO} refs/heads/gone {remote}\n"
        f"refs/heads/main {tip} refs/heads/main {remote}\n")
    assert pairs == [(tip, remote, "refs/heads/main")], (
        "a ref being deleted carries no tree and must never reach a check; a real ref must")


def test_the_protocol_parser_ignores_a_short_line():
    assert G.protocol_pairs("garbage\n\n") == []
