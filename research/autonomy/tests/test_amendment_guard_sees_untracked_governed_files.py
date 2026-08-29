"""`amendment_guard.py` must see a brand-new GOVERNED file even if it was never `git add`-ed (AUT-PD-156).

★★ THE INCIDENT. `changed_paths()` ran `git diff --name-only <sha> --`, and `git diff` never lists
untracked files — staged or not. Measured 2026-08-29 (CYC-0074): three new files this session,
including one matching `**/tests/**`, were completely absent from `amendment_guard.py --receipt ...
--diff-from <sha>` until they were `git add`-ed at least once. That means a session could land a
quiet new governed file — a new test, a file that happened to be named CLAUDE.md — and the guard
that exists specifically to catch a governed edit reaching a commit unrefused would never see it,
because it never ran a diff broad enough to.

The fix unions `git status --porcelain --untracked-files=all` into `changed_paths()`, which reports
a new file whether or not it was ever staged.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import amendment_guard as G  # noqa: E402

pytestmark = pytest.mark.skipif(not __import__("shutil").which("git"), reason="git is required")


def _run(cmd, cwd, check=True):
    e = dict(os.environ)
    e.setdefault("GIT_AUTHOR_NAME", "t")
    e.setdefault("GIT_AUTHOR_EMAIL", "t@e")
    e.setdefault("GIT_COMMITTER_NAME", "t")
    e.setdefault("GIT_COMMITTER_EMAIL", "t@e")
    p = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise AssertionError(f"{cmd}\nrc={p.returncode}\n{p.stdout}\n{p.stderr}")
    return p


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """A throwaway git repo, with `amendment_guard.REPO` pointed at it for the duration of the test."""
    d = tmp_path / "repo"
    d.mkdir()
    _run(["git", "init", "-q", "-b", "main"], cwd=str(d))
    (d / "seed.txt").write_text("seed\n")
    _run(["git", "add", "-A"], cwd=str(d))
    _run(["git", "commit", "-qm", "seed"], cwd=str(d))
    base = _run(["git", "rev-parse", "HEAD"], cwd=str(d)).stdout.strip()
    monkeypatch.setattr(G, "REPO", str(d))
    return str(d), base


def test_a_brand_new_untracked_file_is_seen_without_staging(repo):
    """THE REGRESSION, exactly as it happened: a new file, never `git add`-ed, must still appear."""
    d, base = repo
    tests_dir = os.path.join(d, "research", "autonomy", "tests")
    os.makedirs(tests_dir, exist_ok=True)
    new_test = os.path.join(tests_dir, "test_something_new.py")
    with open(new_test, "w") as fh:
        fh.write("def test_x():\n    assert True\n")

    seen = G.changed_paths(base)
    assert "research/autonomy/tests/test_something_new.py" in seen, (
        f"a brand-new untracked file matching **/tests/** was not seen: {seen}")


def test_a_staged_new_file_is_still_seen_and_not_duplicated(repo):
    """The old behaviour (diff sees a STAGED new file) must not regress, and the union must not
    double-list a path that both mechanisms would report."""
    d, base = repo
    new_file = os.path.join(d, "CLAUDE.md")
    with open(new_file, "w") as fh:
        fh.write("staged new governed file\n")
    _run(["git", "add", "-A"], cwd=d)

    seen = G.changed_paths(base)
    assert seen.count("CLAUDE.md") == 1, seen


def test_a_tracked_modified_file_is_still_seen(repo):
    """The pre-existing tracked-diff path must be untouched by the union."""
    d, base = repo
    with open(os.path.join(d, "seed.txt"), "a") as fh:
        fh.write("more\n")

    seen = G.changed_paths(base)
    assert "seed.txt" in seen, seen


def test_an_untouched_file_is_not_reported(repo):
    """The opposite bug would be worse: nothing outside what changed may appear."""
    d, base = repo
    with open(os.path.join(d, "untouched.txt"), "w") as fh:
        fh.write("not part of this diff at all\n")
    _run(["git", "add", "-A"], cwd=d)
    _run(["git", "commit", "-qm", "unrelated commit, now part of history"], cwd=d)

    seen = G.changed_paths(base)
    # committing made it part of history relative to `base`, so it SHOULD appear here — this is a
    # sanity check that the function still measures "differs from base", not "everything on disk".
    assert "untouched.txt" in seen, seen

    # Now diff from the tip that already contains it: nothing should be reported.
    tip = _run(["git", "rev-parse", "HEAD"], cwd=d).stdout.strip()
    assert G.changed_paths(tip) == []


def test_governed_untracked_file_is_refused_end_to_end(repo, tmp_path):
    """The whole point: `evaluate()` must now REFUSE an undeclared, never-staged governed file,
    where before this fix it silently permitted it (governed_paths_touched == 0)."""
    d, base = repo
    tests_dir = os.path.join(d, "research", "autonomy", "tests")
    os.makedirs(tests_dir, exist_ok=True)
    with open(os.path.join(tests_dir, "test_quiet_new_governed_file.py"), "w") as fh:
        fh.write("def test_x():\n    assert True\n")

    receipt = {"cycle_id": "CYC-TEST", "blocked_by": []}
    result = G.evaluate(receipt, base)
    assert result["governed_paths_touched"] == 1, result
    assert not result["permitted"], result
    assert result["findings"][0]["verdict"] == "UNDECLARED", result
