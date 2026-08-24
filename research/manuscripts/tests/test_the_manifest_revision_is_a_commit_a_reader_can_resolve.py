"""⛔ THE ARCHIVE MANIFEST NAMES THE COMMIT IT WAS TAKEN AT, AND FIVE PDFs PRINT IT.

`git_revision` is how a reader of the deposit answers "which state of the repository is this?", and
`build_submission_pdf.py` puts it on the title page of every built PDF. A revision nobody can
resolve turns that provenance line into decoration.

⛔ WHY THIS EXISTS (round 15 seat 5, 2026-08-22). The committed manifest recorded `ac37c982…`, and
`git branch -a --contains ac37c982` returned NOTHING: the manifest was regenerated, the branch was
then rebased onto a moved `main`, and the rebase rewrote that commit into a different sha. Three
deposited PDFs shipped with a provenance line pointing at a commit no clone would ever have.
The rule the incident produced is one line long: **regenerate the manifest AFTER the final rebase,
never before it.**

⚠ AND IT MUST NOT CRY WOLF IN CI. `actions/checkout@v4` makes a depth-1 clone, so the parent commit
this manifest legitimately names is simply not present there — an unconditional ancestor check would
go red on a correct tree, which is how a gate gets switched off. So the check asks the clone what it
can answer: in a full clone the revision must be reachable, and in a shallow one the guard says out
loud that it could not look rather than passing quietly.
"""
from __future__ import annotations

import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(MANUSCRIPTS, "..", ".."))
MANIFEST = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-archive-manifest.json")


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def test_the_recorded_revision_is_a_commit_this_clone_can_resolve():
    if not os.path.exists(MANIFEST):
        pytest.fail("the archive manifest is missing; the deposit records no revision at all")
    rev = json.load(open(MANIFEST, encoding="utf-8")).get("git_revision") or ""
    assert len(rev) == 40 and all(c in "0123456789abcdef" for c in rev), (
        f"the manifest's git_revision is not a full sha: {rev!r}")

    if _git("rev-parse", "--git-dir").returncode != 0:
        pytest.fail("git cannot answer here, so the deposit's provenance line is UNCHECKED — a "
                    "guard that cannot run is not a guard that passed")

    shallow = _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true"
    known = _git("cat-file", "-e", rev + "^{commit}").returncode == 0
    if shallow and not known:
        # Announce the weakening rather than pass quietly — the same choice `tests.yml` makes in its
        # "EMC systems map — registry invariants" step, whose `git fetch origin main || echo "could
        # not fetch origin/main …"` lets the check degrade to the working tree and say so out loud.
        # ⚠ Cited by STEP NAME, not by line: this was `tests.yml:83` until 2026-08-24, when that
        # file was split into two jobs and line 83 became an unrelated comment. A `:NNNN` citation
        # still RESOLVES after the target moves — it just points at a sentence that no longer says
        # what it is cited for, which is the silent rot CLAUDE.md §1 and `line_citations.py` exist
        # to catch, and which nothing was checking here because this is a test comment.
        print(f"⚠ shallow clone: {rev[:8]} is not present, so its reachability was NOT checked. "
              "Run this in a full clone before depositing.")
        return
    assert known, (
        f"the manifest records git_revision {rev[:8]}…, which is not a commit in this repository. "
        "The manifest was regenerated and the branch was then rebased, so that sha no longer "
        "exists — and every built PDF prints it as its provenance line. Regenerate the manifest "
        "AFTER the final rebase: `python3 research/manuscripts/aso_archive_manifest.py`.")

    reachable = _git("branch", "-a", "--contains", rev).stdout.strip()
    if not reachable:
        reachable = _git("tag", "--contains", rev).stdout.strip()
    assert reachable, (
        f"the manifest records git_revision {rev[:8]}…, which exists in this clone but is on no "
        "branch and no tag — so it is unreachable to anyone who clones the repository, and the "
        "deposit's provenance line points nowhere. This is what a rebase after regeneration looks "
        "like. Regenerate the manifest AFTER the final rebase.")
