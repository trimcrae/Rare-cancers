"""⛔⛔ THE MANIFEST RECORDS A COMMIT SHA AT A MOMENT THAT IS NOT THE MOMENT IT IS PUBLISHED.

AUT-PD-141, AUT-PD-175 and AUT-PD-195 are one defect written down three times: `git_revision` is
stamped from HEAD at generation time, `git rebase origin/main` before the push rewrites every local
commit, and the manifest reaches the trunk naming a sha that exists only in one container's reflog.
Five deposited PDFs print that sha as their provenance line and the deposit's own step 1 is to
`git checkout` it, so the failure lands at precisely the moment the artifact is supposed to work.

★ WHAT MAKES IT INVISIBLE, AND WHY THESE TESTS DRIVE GIT RATHER THAN A FAKE. An orphaned sha is
still a well-formed forty-character sha, so every field check passes; and `git cat-file -e` still
RESOLVES it, because the reflog holds it in the clone that made it. The single observation that
discriminates is reachability from a REMOTE-tracking ref, and it is a property of a real object
graph — a fake would only assert what its author already believed. Each test below builds two
clones and a bare origin and performs the actual race.

★★ THE DESIGN DECISION THESE TESTS PIN. `_revision_durability` keeps the COMMIT SHA and checks the
moment it was taken, rather than replacing it with a content digest. `test_a_sha_recorded_at_a_pushed_tip_survives_two_racing_rebases`
is the evidence for the half of that decision people doubt: a pushed sha is not defended against the
rebase, it is unreachable by it, because origin's history is append-only. The other half —
`archive_content_digest` already exists and answers a different question — is argued at the
`_revision_durability` definition and is not a thing a test can assert.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
MODULE = os.path.join(MANUSCRIPTS, "aso_archive_manifest.py")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("aso_archive_manifest_under_test", MODULE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(cwd, *args):
    r = subprocess.run(("git",) + args, cwd=str(cwd), capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} failed in {cwd}: {r.stderr}"
    return r.stdout.strip()


def _commit(cwd, name):
    (cwd / name).write_text(name, encoding="utf-8")
    _git(cwd, "add", name)
    _git(cwd, "commit", "-qm", name)
    return _git(cwd, "rev-parse", "HEAD")


def _world(tmp_path):
    """A bare origin plus two clones, A and B, both on `main`. The concurrency this defect needs."""
    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "-q", "--bare", "--initial-branch=main", ".")
    clones = []
    for name in ("A", "B"):
        d = tmp_path / name
        subprocess.run(["git", "clone", "-q", str(origin), str(d)], capture_output=True)
        _git(d, "config", "user.email", "seat@example.invalid")
        _git(d, "config", "user.name", "seat")
        _git(d, "config", "init.defaultBranch", "main")
        clones.append(d)
    a, b = clones
    _git(a, "checkout", "-qb", "main")
    _commit(a, "base")
    _git(a, "push", "-q", "origin", "main")
    _git(b, "fetch", "-q", "origin")
    _git(b, "checkout", "-qB", "main", "origin/main")
    return a, b


def test_a_revision_on_a_remote_tracking_ref_reads_as_published(mod, tmp_path, monkeypatch):
    a, _b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    rev = _git(a, "rev-parse", "HEAD")
    state, detail = mod._revision_durability(rev)
    assert state == "PUBLISHED", (state, detail)
    assert mod._revision_durability_report(rev) is None, (
        "a published revision must produce no report at all, or the generator warns on every "
        "correct run and the warning stops being read")


def test_a_revision_that_was_never_pushed_reads_as_local_only(mod, tmp_path, monkeypatch):
    """⛔ THE DEFECT ITSELF, BEFORE THE REBASE THAT DETONATES IT.

    This is the state `aso_archive_manifest.py` is in every time a session regenerates the manifest
    at a local HEAD. The reading is available HERE, at generation time — which is the whole reason
    the check is not a pre-push hook and not a CI guard.
    """
    a, _b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    rev = _commit(a, "unpushed-content")
    state, _ = mod._revision_durability(rev)
    assert state == "LOCAL_ONLY", (
        f"a commit that exists only in this clone read as {state}. That is the sha the next rebase "
        "orphans, and nothing downstream can tell — an orphaned sha is still a well-formed sha.")
    report = mod._revision_durability_report(rev)
    assert report and report.startswith("⛔"), report
    assert "rebase" in report, "the report must name the mechanism, not just the state"


def test_a_rebased_away_revision_is_caught_although_cat_file_still_resolves_it(
        mod, tmp_path, monkeypatch):
    """⛔⛔ THE REFLOG IS WHY EVERY EXISTENCE CHECK IN THIS REPOSITORY MISSED THIS.

    AUT-PD-141 recorded the reading that made the defect invisible: after the rebase the orphan
    "still resolves through the local reflog", so `git cat-file -e` says yes in the one clone that
    will never need to ask. This test asserts BOTH halves — that it still resolves, and that
    `_revision_durability` calls it anyway — because a guard that agrees with `cat-file` here is a
    guard that has stopped looking.

    ⚠ IT READS `LOCAL_ONLY`, NOT `ORPHANED`, AND THE DISTINCTION IS ABOUT THE OBSERVER RATHER THAN
    THE COMMIT. Both are the defect and both exit non-zero; they differ only in whether this
    particular clone happens to still hold the object. `ORPHANED` is what a colleague's clone, or
    this one after a `gc`, sees.
    """
    a, b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    rev = _commit(a, "content")
    _commit(b, "concurrent")
    _git(b, "push", "-q", "origin", "main")
    _git(a, "fetch", "-q", "origin")
    _git(a, "rebase", "-q", "origin/main")

    resolves = subprocess.run(["git", "cat-file", "-e", f"{rev}^{{commit}}"],
                              cwd=str(a), capture_output=True).returncode == 0
    assert resolves, (
        "the premise of this whole family is that the orphan STILL RESOLVES locally. If git has "
        "stopped keeping it in the reflog, re-derive the defect before trusting this file.")
    state, _ = mod._revision_durability(rev)
    assert state == "LOCAL_ONLY", (
        f"a rebased-away commit read as {state}. `cat-file` says it is here and no clone will ever "
        "have it; only reachability from a remote-tracking ref separates the two.")
    assert mod._revision_durability_report(rev).startswith("⛔")


def test_a_revision_no_clone_holds_reads_as_orphaned(mod, tmp_path, monkeypatch):
    """⛔ THE OTHER OBSERVER: a sha that resolves nowhere, which is what a fabricated one looks like."""
    a, _b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    absent = "0" * 39 + "1"
    state, detail = mod._revision_durability(absent)
    assert state == "ORPHANED", (state, detail)
    assert mod._revision_durability_report(absent).startswith("⛔")


def test_a_sha_recorded_at_a_pushed_tip_survives_two_racing_rebases(mod, tmp_path, monkeypatch):
    """★★ THE EVIDENCE FOR THE DESIGN DECISION: A PUSHED SHA IS NOT DEFENDED, IT IS UNREACHABLE.

    AUT-PD-195 proposed recording a tree hash on the reasoning that it is "the only option immune to
    the mechanism rather than defending against it". This drives the alternative instead of arguing
    it: record the sha at a tip that is already on origin, then let a concurrent session force TWO
    rebases underneath it. Because origin's history is append-only, the recorded commit stays an
    ancestor of every later origin tip — no defence, nothing to remember, and the sha keeps the one
    property a digest cannot have, that a reader can check it out.
    """
    a, b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    _commit(b, "b1")
    _git(b, "push", "-q", "origin", "main")
    _git(a, "fetch", "-q", "origin")
    _git(a, "rebase", "-q", "origin/main")

    rev = _git(a, "rev-parse", "HEAD")            # AUT-PD-175's ordering: a PUSHED tip
    assert mod._revision_durability(rev)[0] == "PUBLISHED"
    _commit(a, "the-manifest-commit")

    for n in ("b2", "b3"):                        # two racing pushes, two forced rebases
        _git(b, "fetch", "-q", "origin")
        _git(b, "rebase", "-q", "origin/main")
        _commit(b, n)
        _git(b, "push", "-q", "origin", "main")
        _git(a, "fetch", "-q", "origin")
        _git(a, "rebase", "-q", "origin/main")
        _git(a, "push", "-q", "origin", "main")

    state, _ = mod._revision_durability(rev)
    assert state == "PUBLISHED", (
        f"a sha that was on origin when it was recorded read as {state} after two racing rebases. "
        "That would falsify the reason this module keeps a commit sha instead of a content digest.")


def test_a_clone_with_no_remote_says_unchecked_rather_than_published(mod, tmp_path, monkeypatch):
    """⛔ AN ABSENT READING IS NOT A READING OF ABSENCE (CLAUDE.md §4).

    A repository with no remote cannot answer "was this published?", and the dangerous answer is the
    reassuring one. UNCHECKED exits 0 — a check that cannot look must not be red — but it must never
    render as PUBLISHED.
    """
    d = tmp_path / "solo"
    d.mkdir()
    _git(d, "init", "-q", "--initial-branch=main", ".")
    _git(d, "config", "user.email", "seat@example.invalid")
    _git(d, "config", "user.name", "seat")
    rev = _commit(d, "only-commit")
    monkeypatch.setattr(mod, "REPO", str(d))
    state, _ = mod._revision_durability(rev)
    assert state == "UNCHECKED", (
        f"a clone with no remote-tracking refs read as {state}; there is nothing here that could "
        "have published anything, so any other answer is invented")
    report = mod._revision_durability_report(rev)
    assert report and report.startswith("⚠"), report


def test_the_check_mode_exits_nonzero_only_on_a_revision_that_will_not_survive(
        mod, tmp_path, monkeypatch):
    """⛔ THE EXIT CODE IS THE PART A PUSH PATH READS, SO IT IS ASSERTED SEPARATELY FROM THE STATE.

    ⚠ AND `UNCHECKED` MUST EXIT 0. A fresh clone, a CI checkout and a remote-less worktree all land
    there; making them red would get this switched off in exactly the places it can never answer,
    which is how the archive gate earned its own cry-wolf history (see `_archive_only`).
    """
    a, b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    out = tmp_path / "manifest.json"
    monkeypatch.setattr(mod, "OUT", str(out))

    published = _git(a, "rev-parse", "HEAD")
    out.write_text(json.dumps({"git_revision": published}), encoding="utf-8")
    assert mod.main(["--check-revision-published"]) == 0

    local_only = _commit(a, "unpushed")
    out.write_text(json.dumps({"git_revision": local_only}), encoding="utf-8")
    assert mod.main(["--check-revision-published"]) == 1, (
        "a revision that only exists in this clone exited 0, so the push path it is meant to gate "
        "would let the orphan through")

    out.write_text(json.dumps({"git_revision": "not-a-sha"}), encoding="utf-8")
    assert mod.main(["--check-revision-published"]) == 1

    out.write_text("{ not json", encoding="utf-8")
    assert mod.main(["--check-revision-published"]) == 1

    solo = tmp_path / "solo2"
    solo.mkdir()
    _git(solo, "init", "-q", "--initial-branch=main", ".")
    _git(solo, "config", "user.email", "seat@example.invalid")
    _git(solo, "config", "user.name", "seat")
    rev = _commit(solo, "x")
    monkeypatch.setattr(mod, "REPO", str(solo))
    out.write_text(json.dumps({"git_revision": rev}), encoding="utf-8")
    assert mod.main(["--check-revision-published"]) == 0, (
        "an UNCHECKED reading exited non-zero, which makes this red in every fresh clone")


def test_the_check_mode_never_rebuilds_the_manifest(mod, tmp_path, monkeypatch):
    """⛔ IT ANSWERS A QUESTION ABOUT THE COMMITTED ARTIFACT, NOT ABOUT THE TREE RIGHT NOW.

    Building would take ~483 hashes to answer a question the recorded field already contains, and —
    worse — it would make the answer depend on the working tree, which is dirty during any ordinary
    commit loop. `build()` is replaced with a bomb here rather than counted, because "it was not
    called" is the property, not "it was called once".
    """
    a, _b = _world(tmp_path)
    monkeypatch.setattr(mod, "REPO", str(a))
    out = tmp_path / "manifest.json"
    monkeypatch.setattr(mod, "OUT", str(out))
    out.write_text(json.dumps({"git_revision": _git(a, "rev-parse", "HEAD")}), encoding="utf-8")

    def _bomb():
        raise AssertionError("--check-revision-published rebuilt the manifest")

    monkeypatch.setattr(mod, "build", _bomb)
    assert mod.main(["--check-revision-published"]) == 0
