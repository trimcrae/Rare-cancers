#!/usr/bin/env python3
"""⛔⛔ NO TEST MAY WRITE TO A GIT-TRACKED FILE. ENFORCED AT THE OPEN, NOT AFTER THE FACT.

⚠ WHY THIS EXISTS, MEASURED 2026-08-29 (AUT-PD-186). Seven tests across three modules mutated LIVE
tracked artifacts and undid it in a `finally`. That is safe only while nothing else reads the file,
and these suites run under `xdist`. Reproduced 3 of 3 runs at `-n 3`:

  · another worker read `endpoint-regime-map.json` mid-window and raised
    `KeyError: 'G4_what_the_map_reads'` — the section a tamper test had just deleted;
  · a module-scoped fixture reading the same file took its WHOLE module down as a collection ERROR,
    which is the intermittent shape AUT-PD-085 filed and could not attribute;
  · the parametrized cases raced each other, so a restore can lose.

⛔ AND THE LOSS ESCAPES THE RUN. After one reproduction the working tree carried
`"conditions_placed": 45` against the committed 44 — a value invented by a tamper test, sitting in a
tracked artifact, with the suite reporting only a flake. A `git add -A` on top of that commits a
falsified number, which is the mutation-window incident CLAUDE.md §6 records reaching `origin/main`
on 2026-08-27.

★★ WHY AN AUDIT HOOK RATHER THAN A TIDINESS CHECK AT THE END. A `git status` after the suite catches
the LEAK — a restore that lost — and says nothing about the WINDOW, which is the actual defect: a
test that mutates and successfully restores still exposed every concurrent reader. `sys.addaudithook`
fires at the moment the file is opened for writing, so the window is refused rather than measured,
and the traceback names the test that opened it.

★ THE FIX A FIRING GUARD IS ASKING FOR is always the same one, and it is three lines: copy the
artifact to `tmp_path`, point the producer's `OUT` at the copy with `monkeypatch.setattr`, and
mutate the copy. Every producer's `--check` reads `OUT` and nothing else, so what is under test does
not change; and the redirection is self-verifying, because `--check` on an unmutated artifact returns
0 while every such assertion demands non-zero.

⛔ THE ALLOWLIST IS NOT AN OFF SWITCH. It is keyed by repo-relative path and every entry carries a
reason. A test that needs to write to the tree is a test that has not been isolated yet; adding a
path here to make a red run green is the failure this guard exists to prevent.
"""
from __future__ import annotations

import os
import subprocess
import sys

#: Repo-relative paths a test is permitted to write, each with the reason it cannot be isolated.
#: Empty on purpose — every known case was isolated rather than declared (AUT-PD-186).
ALLOWED: dict[str, str] = {}

#: Audit events that can change a file. `open` covers every write mode; the rest are the paths that
#: reach the filesystem without one.
_WRITE_EVENTS = frozenset((
    "open", "os.remove", "os.rename", "os.truncate", "os.link", "os.symlink",
    "shutil.copyfile", "shutil.copymode", "shutil.copystat", "shutil.move",
))

#: Bits that mean "this open can modify the file". Checked because `open`'s audit event reports
#: `flags` (an int) for the os-level path and `mode` (a string) for the builtin.
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC

_installed = False

#: Set when `install` deliberately did nothing, with the reason. Never set inside a git repository —
#: `test_no_test_may_write_to_the_tracked_tree` asserts exactly that.
_INERT_REASON: str | None = None

#: The tracked set the live hook reads. Module-level rather than a closure variable so
#: `test_no_test_may_write_to_the_tracked_tree.py` can register a THROWAWAY path and prove the guard
#: raises without ever pointing a write at a real artifact to find out.
_TRACKED: set[str] = set()
_ALLOWED: set[str] = set()

#: (repo, `git status --porcelain -uno` at install). The second half of the guard — see
#: `assert_tree_unchanged`.
_SNAPSHOT: tuple | None = None


def repo_root(start: str) -> str | None:
    """The repository's top level, asked of `git` rather than counted in `dirname`s.

    ⚠ THE FIRST VERSION COUNTED, AND MISCOUNTED — three `dirname`s from a conftest two directories
    deep lands on `research/`, not the repository. `git ls-files` run there lists only what is under
    it, so the guard installed cleanly, reported a four-figure tracked set, and was blind to
    `scripts/`, `.github/` and `systems/` without a single symptom. A guard with a silent hole is
    worse than none, because it is also an assurance.

    ⛔⛔ AND None IS A REAL ANSWER, NOT AN ERROR — `claim_ablation` IS WHY (measured 2026-08-29).
    That gate makes a hardlink clone of the repo in `/tmp`, deliberately WITHOUT `.git`, mutates a
    sentence there and runs each witness with `cwd=<workspace>`. Those witnesses are pytest, so they
    load this suite's `conftest.py`, so they install this guard — in a directory `git` does not
    recognise. The first version raised `CalledProcessError`, which failed the conftest IMPORT,
    which made every witness process exit 4, which `_baseline_reds` correctly subtracted as red
    before the mutation, which reported EVERY censused sentence BLIND. Four documents' ablation
    gates went red and the report said the paper was unguarded. It is not: the guard was.

    ★ THE HONEST ANSWER OUTSIDE A REPOSITORY IS THAT THERE IS NOTHING TO PROTECT. A disposable clone
    has no tracked tree, and writing to it is the whole point. So this returns None and `install`
    makes the guard inert, recording WHY — and `test_no_test_may_write_to_the_tracked_tree` asserts
    the implication that matters: if this IS a git repository, the guard must be live. A silent
    disable inside the real tree therefore still fails the build.
    """
    done = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        return None
    return done.stdout.strip() or None


def tracked_files(repo: str) -> set[str]:
    """Every path `git` is tracking, absolute and real, as a set for O(1) lookup.

    ⛔ A FAILURE HERE DISABLES THE GUARD, so it is loud rather than silent: an empty set would make
    every write permitted and nothing would say so.
    """
    out = subprocess.run(["git", "-C", repo, "ls-files", "-z"],
                         capture_output=True, text=True, check=True).stdout
    names = [n for n in out.split("\0") if n]
    if not names:
        raise RuntimeError(
            f"`git ls-files` returned nothing in {repo}; the tracked-tree guard would permit every "
            "write, so it refuses to install rather than pass silently")
    return {os.path.realpath(os.path.join(repo, n)) for n in names}


#: Which argument of each event names a file the call would CHANGE.
#:
#: ⛔ THE SOURCE MATTERS FOR A MOVE AND MUST NOT FOR A COPY, AND GETTING THAT BACKWARDS BREAKS THE
#: GUARD IN BOTH DIRECTIONS AT ONCE. `os.rename` and `shutil.move` DESTROY their source, so both
#: ends are checked. `shutil.copyfile` only READS its source — and reading a committed artifact to
#: copy it into `tmp_path` is precisely the isolation pattern this guard exists to push people
#: toward, so checking the source there would refuse the fix and leave only the allowlist.
#: ⚠ The first version of this file checked the destination alone for all three, and its own
#: mutation test caught it: `os.rename(tracked, tmp)` moved a tracked file out of the tree and the
#: guard permitted it.
_CHANGED_ARGS = {
    "os.rename": (0, 1),
    "shutil.move": (0, 1),
    "shutil.copyfile": (1,),
    "shutil.copymode": (1,),
    "shutil.copystat": (1,),
    "os.link": (1,),
    "os.symlink": (1,),
}


def _writes(event: str, args) -> tuple:
    """Every path this event would change. Empty when it changes nothing."""
    if event == "open":
        path, mode, flags = args
        if path is None:
            return ()
        if isinstance(mode, str):
            if not any(c in mode for c in "wxa+"):
                return ()
        elif isinstance(flags, int) and not flags & _WRITE_FLAGS:
            return ()
        return (path,)
    positions = _CHANGED_ARGS.get(event, (0,))
    return tuple(args[i] for i in positions if i < len(args) and args[i] is not None)


def install(repo: str) -> None:
    """Refuse, for the life of this process, any write to a file `git` tracks.

    `repo` may be any path inside the repository; the top level is resolved from it.

    ⚠ AN AUDIT HOOK CANNOT BE REMOVED once added, which is why this is idempotent and why the
    tracked set is captured once at install rather than re-read per write.
    """
    global _installed, _INERT_REASON
    if _installed:
        return
    resolved = repo_root(repo)
    _installed = True
    if resolved is None:
        _INERT_REASON = (
            f"{repo} is not inside a git repository, so there is no tracked tree to protect. "
            "This is the disposable-clone case (claim_ablation's hardlink workspace), where writing "
            "is the point.")
        return
    repo = resolved

    _TRACKED.update(tracked_files(repo))
    _ALLOWED.update(os.path.realpath(os.path.join(repo, p)) for p in ALLOWED)

    global _SNAPSHOT
    _SNAPSHOT = (repo, _tracked_status(repo))

    def hook(event, args):
        if event not in _WRITE_EVENTS:
            return
        hit = None
        for path in _writes(event, args):
            try:
                given = os.fspath(path)
            except TypeError:      # a file descriptor, not a path
                continue
            # ⛔⛔ ABSOLUTE PATHS ONLY, AND THIS IS A REAL LIMIT RATHER THAN A CONVENIENCE.
            # An audit event reports the path AS GIVEN and never the `dir_fd` it is relative to, so
            # a bare name is ambiguous. ⚠ Measured 2026-08-29: `shutil.rmtree`'s `_rmtree_safe_fd`
            # deletes entries of pytest's own old `/tmp/pytest-of-root/...` directories by NAME
            # against a directory descriptor. Resolving those against the cwd — the repository —
            # turned `.gitignore` in a temp directory into `<repo>/.gitignore`, and the guard
            # refused pytest's routine teardown. Both files exist, so no stat or inode check can
            # tell the two apart from inside the hook.
            # ★ THE RESIDUAL HOLE IS CLOSED ELSEWHERE, NOT WISHED AWAY: a test that writes a
            # tracked file through a relative path escapes this hook and is caught by
            # `assert_tree_unchanged` at session end, which compares `git status` against the
            # snapshot taken at install. The hook owns the WINDOW; the snapshot owns the LEAK.
            if not os.path.isabs(given):
                continue
            resolved = os.path.realpath(given)
            if resolved in _TRACKED and resolved not in _ALLOWED:
                hit = resolved
                break
        if hit is None:
            return
        relative = os.path.relpath(hit, repo)
        raise RuntimeError(
            f"a test opened the git-tracked file {relative} for writing ({event}).\n"
            "\n"
            "No test may write to the tree. Under xdist another worker reads that file while it is "
            "mutated, and a restore that loses leaves an invented value in a tracked artifact with "
            "the suite reporting only a flake (AUT-PD-186, measured 2026-08-29).\n"
            "\n"
            "THE FIX: copy it to `tmp_path`, point the producer's OUT at the copy with "
            "`monkeypatch.setattr(module, \"OUT\", str(copy))`, and mutate the copy. See "
            "research/manuscripts/tests/test_endpoint_producers_check.py for the pattern.\n"
            "\n"
            "Do NOT add the path to tracked_tree_guard.ALLOWED to make this green — that is the "
            "failure this guard exists to prevent.")

    sys.addaudithook(hook)


def _tracked_status(repo: str) -> str:
    """What `git` says about TRACKED files right now. Untracked ones are excluded on purpose —
    a test writing scratch output into the tree is untidy, not a corruption, and failing on it would
    make this check the thing everyone turns off."""
    return subprocess.run(["git", "-C", repo, "status", "--porcelain", "-uno"],
                          capture_output=True, text=True, check=True).stdout


def assert_tree_unchanged() -> None:
    """⛔ THE SECOND HALF: no test run may leave the tracked tree different from how it found it.

    ★ WHY BOTH HALVES EXIST, AND WHY NEITHER IS REDUNDANT. The audit hook refuses a write at the
    moment it happens, which is the only way to catch the WINDOW — the interval in which a
    concurrent reader sees a half-mutated artifact, and the actual defect behind AUT-PD-186. But the
    hook can only act on absolute paths, because an audit event never reports the `dir_fd` a bare
    name is relative to. This check has the opposite shape: it cannot see the window at all, and it
    cannot be evaded, because it asks `git` what changed rather than watching how it changed.

    ⚠ IT IS DELIBERATELY NOT A TIDY-UP. It reports and fails; it does not restore. A run that
    corrupted an artifact should end with the corruption visible in `git diff`, where a person can
    read it, rather than silently reverted by the thing that noticed.
    """
    if _SNAPSHOT is None:          # inert: no repository, nothing to compare
        return
    repo, before = _SNAPSHOT
    after = _tracked_status(repo)
    if after == before:
        return
    changed = sorted(set(after.splitlines()) - set(before.splitlines()))
    raise AssertionError(
        "the test run CHANGED tracked files that it did not find changed:\n  "
        + "\n  ".join(changed)
        + "\n\nNo test may write to the tree (AUT-PD-186). Inspect `git diff` before reverting — "
          "the change is evidence, and a tamper value restored quietly is how a falsified number "
          "reaches a commit. The fix is to mutate a copy under `tmp_path`; see "
          "research/manuscripts/tests/test_endpoint_producers_check.py."
    )
