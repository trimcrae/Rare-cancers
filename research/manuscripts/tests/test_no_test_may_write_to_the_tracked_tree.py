#!/usr/bin/env python3
"""⛔⛔ THE GUARD THAT REFUSES A TEST WRITING TO THE TREE, MUTATION-TESTED LIKE ANY OTHER.

`tracked_tree_guard` is itself an instrument asserted in prose, and `paper-hardening` §6 is explicit
that a guard nobody mutated is a hope. So this file does not read the guard — it drives it, in both
directions: a write that must be refused, and a write that must be permitted.

⛔ EVERY PROBE THAT MUST BE REFUSED USES A THROWAWAY PATH REGISTERED WITH THE GUARD, NEVER A REAL
ARTIFACT. Pointing a truncating write at a committed file to find out whether something stops it is
the same bet this guard exists to refuse — if the guard were broken, the test would BE the incident.
The one probe that does touch a real tracked file opens it for APPEND and writes nothing, so a
broken guard costs an mtime rather than a manuscript.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

sys.path.insert(0, HERE)
import tracked_tree_guard as G  # noqa: E402


@pytest.fixture
def pretend_tracked(tmp_path):
    """A real file the guard believes is tracked, and forgets again afterwards."""
    target = tmp_path / "pretend-artifact.json"
    target.write_text('{"a": 1}\n', encoding="utf-8")
    resolved = os.path.realpath(target)
    G._TRACKED.add(resolved)
    try:
        yield str(target)
    finally:
        G._TRACKED.discard(resolved)


def test_the_guard_is_actually_installed_in_this_session():
    """⛔ THE PRECONDITION, AND IT IS THE ONE THAT DECAYS SILENTLY. Every refusal below is
    conditional on `conftest.py` having installed the hook; if that import is ever dropped, the
    probes still pass on their own registered paths and the SUITE is unguarded. So assert the real
    tracked set is populated and that a genuine committed file is in it.
    """
    assert G._installed, (
        "the tracked-tree guard is not installed — research/manuscripts/tests/conftest.py must "
        "call tracked_tree_guard.install(), or this whole suite can write to the tree again")
    # ⛔ THE IMPLICATION, NOT THE UNCONDITIONAL. The guard is deliberately inert where there is no
    # repository to protect — `claim_ablation` runs witnesses inside a hardlink clone with no
    # `.git`, and writing there is the point. Outside that case an inert guard is a silent disable,
    # so this asserts the only thing that matters: in a real checkout, it must be live.
    inside_a_repo = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).returncode == 0
    if not inside_a_repo:
        assert G._INERT_REASON, "the guard is inert outside a repository and did not say why"
        return
    assert G._INERT_REASON is None, (
        f"this IS a git repository and the guard made itself inert: {G._INERT_REASON}")
    assert len(G._TRACKED) > 1000, (
        f"the guard holds {len(G._TRACKED)} tracked paths, which is not a repository — "
        "`git ls-files` failed and the guard is permitting writes it should refuse")
    conftest = os.path.realpath(os.path.join(HERE, "conftest.py"))
    assert conftest in G._TRACKED, (
        "the suite's own conftest.py is committed and the guard does not know it, so the tracked "
        "set is not the tree")


@pytest.mark.parametrize("mode", ["w", "wb", "a", "r+", "x"])
def test_every_writing_mode_is_refused(pretend_tracked, mode):
    """A membership test on one mode would miss the others, and `a` and `r+` are exactly the modes
    a restore uses."""
    with pytest.raises(RuntimeError, match="opened the git-tracked file"):
        open(pretend_tracked, mode).close()
    assert open(pretend_tracked, encoding="utf-8").read() == '{"a": 1}\n', (
        "the guard raised but the file changed anyway, so it fires too late to protect anything")


def test_reading_is_not_refused(pretend_tracked):
    """⛔ THE OTHER DIRECTION. A guard that refuses reads would be caught in seconds; one that
    refuses nothing would not be. Both halves are asserted so neither can rot."""
    assert open(pretend_tracked, encoding="utf-8").read() == '{"a": 1}\n'


def test_deleting_and_renaming_a_tracked_file_are_refused(pretend_tracked, tmp_path):
    """The two ways to change a file without opening it for writing."""
    with pytest.raises(RuntimeError, match="opened the git-tracked file"):
        os.remove(pretend_tracked)
    with pytest.raises(RuntimeError, match="opened the git-tracked file"):
        os.rename(pretend_tracked, str(tmp_path / "moved.json"))
    with pytest.raises(RuntimeError, match="opened the git-tracked file"):
        shutil.copyfile(str(tmp_path / "source.json"), pretend_tracked)
    assert os.path.exists(pretend_tracked), "a refused operation went through anyway"


def test_copying_a_tracked_file_OUT_of_the_tree_is_permitted(tmp_path):
    """★ THE ISOLATION PATTERN ITSELF, asserted so the guard can never refuse its own remedy.
    `shutil.copyfile(module.OUT, tmp_path / name)` READS a committed artifact; the destination is
    scratch. A guard that checked the source here would refuse every fix it recommends.
    """
    destination = tmp_path / "copy.py"
    shutil.copyfile(os.path.join(HERE, "conftest.py"), destination)
    assert destination.read_text(encoding="utf-8")


def test_writing_outside_the_tree_is_permitted(tmp_path):
    """The pattern every isolated test uses. If this ever fails the guard has become unusable and
    the next session will reach for the allowlist, which is the wrong door."""
    scratch = tmp_path / "copy.json"
    scratch.write_text('{"a": 2}\n', encoding="utf-8")
    assert scratch.read_text(encoding="utf-8") == '{"a": 2}\n'


def test_a_real_committed_file_is_refused():
    """★ THE PROBE ON THE LIVE SET, kept safe by its mode. `a` writes nothing on open, so a broken
    guard costs this file an mtime; every other mode would cost it its contents.
    """
    with pytest.raises(RuntimeError, match="opened the git-tracked file"):
        open(os.path.join(HERE, "conftest.py"), "a").close()


def test_the_allowlist_is_empty_or_every_entry_says_why():
    """⛔ THE ALLOWLIST IS THE ESCAPE HATCH AND THEREFORE THE THING TO WATCH. An entry is a test
    that was not isolated; it may exist, but never anonymously, because a bare path is how "make
    the red run green" enters and is never revisited.
    """
    for path, reason in G.ALLOWED.items():
        assert isinstance(reason, str) and len(reason.split()) >= 5, (
            f"{path} is allowlisted with the reason {reason!r}. Say why it cannot be isolated to "
            "tmp_path — and prefer isolating it, which is what every other case here did")


def test_the_session_end_check_notices_a_tracked_file_that_changed(monkeypatch):
    """⛔ THE LEAK HALF, DRIVEN RATHER THAN TRUSTED.

    `assert_tree_unchanged` exists because the audit hook can only act on ABSOLUTE paths — an audit
    event never reports the `dir_fd` a bare name is relative to, so a write through a relative path
    slips past it. This half asks `git` what changed instead of watching how, so nothing evades it;
    what it cannot do is see the window. Neither half is redundant and neither is asserted in prose
    alone.

    ★ THE SNAPSHOT IS FAKED, NOT THE TREE. Dirtying a real tracked file to find out whether the
    checker notices is the incident it is meant to catch.
    """
    monkeypatch.setattr(G, "_SNAPSHOT", (REPO, " M research/manuscripts/pretend.md\n"))
    monkeypatch.setattr(G, "_tracked_status",
                        lambda repo: " M research/manuscripts/pretend.md\n"
                                     " M research/modalities/aso-parent-null.json\n")
    with pytest.raises(AssertionError, match="CHANGED tracked files"):
        G.assert_tree_unchanged()


def test_the_session_end_check_passes_when_nothing_moved(monkeypatch):
    """The other direction: a change that was ALREADY there when the run started is not this run's,
    and flagging it would make the check fire on every session with a work in progress — which is
    how a check gets turned off."""
    monkeypatch.setattr(G, "_SNAPSHOT", (REPO, " M research/manuscripts/pretend.md\n"))
    monkeypatch.setattr(G, "_tracked_status",
                        lambda repo: " M research/manuscripts/pretend.md\n")
    G.assert_tree_unchanged()


def test_the_session_end_check_is_silent_when_the_guard_is_inert(monkeypatch):
    """No repository, no snapshot, nothing to compare — and no crash, because this runs inside
    `claim_ablation`'s hardlink workspace on every witness invocation."""
    monkeypatch.setattr(G, "_SNAPSHOT", None)
    G.assert_tree_unchanged()
