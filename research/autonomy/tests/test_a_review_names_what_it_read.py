#!/usr/bin/env python3
"""`deliverable_digest` — what a review covered, addressed by content instead of by commit.

⛔⛔ WHAT THIS MODULE IS FOR, AND WHAT IT DELIBERATELY IS NOT. `publish_bar`'s clauses 1 and 6 ask
"is this record about the paper under review?" and answer it by comparing a COMMIT SHA. Measured
2026-09-02 over the sixty commits before that date, PUB-ASO's deliverable files took FOUR distinct
digests in eight runs — so the sha comparison discarded a clean review sixty times to track four
real changes, including when the discarding commit was the one filing the review's own record. The
article's own sha256 was byte-identical (`afd60b9e…`) at the pins `7ae3cb518`, `4ae4e9929` and
`e0834faf4`; five blind seats had read exactly those bytes; clause 1 failed at all three.

⛔ AND THE SHA IS ALSO TOO LOOSE. It says WHEN a review happened and never said WHAT it covered: a
seat that read one file and a seat that read fifteen record the same string. A digest over the
deliverable SET has both properties the sha had neither of.

★ THIS MODULE GATES NOTHING TODAY AND THAT IS ON PURPOSE. `publish_bar.py` is a GOVERNED path and
the cycle that wrote this is blocked by the very clause the re-anchoring would relax — the exact
shape `amendment_guard` refuses (architecture §10.4). The instrument is committed, measured and
tested; the re-binding is filed as AUT-PD-205-d7df5340 for a later cycle to land declared. **So
these tests are what stop the instrument rotting in the interval**, which is the thing that
normally happens to a tool nothing runs.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUTONOMY))
PAPER = "PUB-ASO"


def _load():
    spec = importlib.util.spec_from_file_location(
        "deliverable_digest", os.path.join(AUTONOMY, "deliverable_digest.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = _load()


def _git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)


def test_the_set_is_derived_from_the_graph_and_never_hand_listed():
    """⛔ A HAND-LISTED SET ROTS THE MOMENT A DELIVERABLE IS ADDED, AND ROTS SILENTLY. The set is
    the publication's own `document.file` plus the files whose names extend its stem — the naming
    convention this repository already builds renderings under. This asserts the derivation is
    live: the document the graph names is IN the set, and every member sits beside it."""
    paths = D.deliverable_set(PAPER)
    assert paths, "no deliverable set for %s — the publication row or its document.file moved" % PAPER
    pub = D._publication(PAPER)
    doc = pub["document"]["file"]
    assert doc in paths, "the set does not contain the document the graph names"
    directory = os.path.dirname(doc)
    stem = os.path.basename(doc).rsplit(".", 1)[0]
    for rel in paths:
        assert os.path.dirname(rel) == directory
        assert os.path.basename(rel).startswith(stem)
    assert len(paths) > 1, (
        "the set is the document alone, so the stem rule matched no rendering — either the "
        "renderings were renamed away from the convention, or the listing is not being read")


def test_the_digest_is_stable_across_commits_that_change_nothing_it_covers():
    """★★ THE MEASUREMENT THAT THE WHOLE RE-ANCHORING RESTS ON, RUN RATHER THAN QUOTED. Walk the
    recent history and count how many times the sha changed against how many times the deliverable
    content changed. If those two numbers were ever equal the instrument would be pointless — and a
    future edit that widened the set to the whole tree would make them equal without failing
    anything else."""
    shas = _git("log", "--format=%H", "-40").stdout.split()
    if len(shas) < 20:
        pytest.skip("shallow history — nothing to measure over")
    digests = [D.deliverable_digest(PAPER, s)[0] for s in shas]
    seen = [d for d in digests if d]
    assert len(seen) >= 10, "the digest could not be built over most of the recent history"
    assert len(set(seen)) < len(seen) / 2, (
        "the deliverable digest changed on nearly every commit (%d distinct over %d), so it buys "
        "nothing the commit sha did not. Something has widened the set past the paper."
        % (len(set(seen)), len(seen)))


def test_a_renamed_deliverable_is_a_different_deliverable():
    """⛔ THE PATH IS HASHED WITH THE CONTENT. Hashing contents alone would let a file be renamed
    with no change of digest, and a renamed deliverable is a different deliverable to the reader
    who followed a link to it."""
    _, rows = D.deliverable_digest(PAPER)
    acc = hashlib.sha256()
    for rel, digest in rows:
        acc.update(rel.encode() + b"\0" + digest.encode() + b"\n")
    assert acc.hexdigest() == D.deliverable_digest(PAPER)[0]
    swapped = hashlib.sha256()
    for rel, digest in rows:
        swapped.update((rel + "-renamed").encode() + b"\0" + digest.encode() + b"\n")
    assert swapped.hexdigest() != acc.hexdigest()


def test_a_missing_member_yields_no_digest_rather_than_a_partial_one():
    """⛔ A DIGEST THAT SILENTLY COVERS LESS THAN IT NAMES IS THE TOO-LOOSE FAILURE THE SHA ALREADY
    HAD. If any member cannot be read at the commit asked about, there is no digest."""
    assert D.deliverable_digest(PAPER, "0" * 40) == (None, None)
    assert D.deliverable_digest("PUB-DOES-NOT-EXIST") == (None, None)


def test_git_object_paths_accept_windows_separators_and_refuse_missing_files():
    """Native relpath separators must not make an existing committed graph disappear."""
    graph = "systems/graph/publications.json"
    expected = D._read(graph, "HEAD")
    assert expected is not None
    assert D._read(graph.replace("/", "\\"), "HEAD") == expected
    listing = D._listing("systems/graph", "HEAD")
    assert "publications.json" in listing
    assert D._listing("systems\\graph", "HEAD") == listing
    assert D._read("systems\\graph\\absent-digest-fixture.json", "HEAD") is None
    assert D._listing("systems\\absent-digest-fixture", "HEAD") == []


def test_windows_graph_relpath_preserves_committed_digest(monkeypatch):
    expected = D.deliverable_digest(PAPER, "HEAD")
    assert expected[0] is not None
    native_relpath = D.os.path.relpath
    monkeypatch.setattr(D.os.path, "relpath", lambda *args: native_relpath(*args).replace("/", "\\"))
    assert D.deliverable_digest(PAPER, "HEAD") == expected


def test_the_digest_moves_when_the_paper_moves():
    """★ THE OTHER DIRECTION, WHICH IS THE ONE A REVIEWER SHOULD DISTRUST FIRST. An instrument that
    never changes is not stable, it is blind. Perturb one member's bytes and the digest must move.
    ⛔ THE PERTURBATION IS ARITHMETIC ON A COPY OF THE HASH ROWS, NEVER A WRITE TO THE TREE — a test
    that edits a manuscript is one xdist worker away from another test reading an invented number
    (AUT-PD-186)."""
    base, rows = D.deliverable_digest(PAPER)
    assert base
    for i in range(len(rows)):
        acc = hashlib.sha256()
        for j, (rel, digest) in enumerate(rows):
            acc.update(rel.encode() + b"\0" + (digest if j != i else "0" * 64).encode() + b"\n")
        assert acc.hexdigest() != base, (
            "changing member %s left the digest unchanged — it is not covering that file" % rows[i][0])


def test_the_committed_publications_graph_is_what_it_reads():
    """The set comes from `systems/graph/publications.json`, so a reader can check it. If that file
    ever stops being the source, this module's claim to be derived-not-typed goes with it."""
    assert D.PUBLICATIONS.endswith(os.path.join("systems", "graph", "publications.json"))
    rows = json.loads(open(D.PUBLICATIONS, encoding="utf-8").read())
    assert any(r.get("id") == PAPER for r in (rows if isinstance(rows, list) else rows.values()))


def test_the_bar_reads_this_module_and_the_wiring_is_not_silently_removable():
    """⭐ THE TRIPWIRE THAT USED TO LIVE HERE HAS FIRED AND BEEN ANSWERED, SO IT IS NOW ITS OWN
    INVERSE — and that is why this is a REPLACEMENT rather than a deletion.

    ⚠ WHAT IT SAID BEFORE, RETAINED PER RULE 1.2 BECAUSE THE REASONING WAS RIGHT: `publish_bar` did
    NOT import this module, deliberately, because the re-binding is a governed change and the cycle
    that BUILT the instrument was blocked by the clause it would relax. It failed the moment
    `deliverable_digest` appeared in `publish_bar.py`, and its failure message named the four things
    that had to be true first: declare it in amendments.jsonl with the self_serving_check answered,
    check that `amendment_guard` permits it for THAT cycle, close AUT-PD-205-d7df5340, and delete
    this test.

    ★ ALL FOUR HAPPENED ON 2026-09-02 UNDER CYC-0091-91c8e949, on trimcrae's explicit instruction
    after he was shown the measurement — 104 commits between round 32's pin and the change, one
    unchanged deliverable digest throughout, so the sha comparison discarded a clean six-seat round
    104 times to track zero real changes. `amendment_guard --receipt ... --diff-from ...` returned
    PERMITTED over three governed paths.

    ⛔ DELETING IT OUTRIGHT WOULD HAVE LEFT THE WIRING GUARDED BY NOTHING, WHICH IS THE FAILURE THIS
    REPOSITORY KEEPS PAYING FOR: a value connected to no code path (`subagent_width` for a
    fortnight), a rule measured by nothing. The instrument is now load-bearing — clauses 1 and 6 of
    the publication permission compute their answer from it — so the assertion is inverted rather
    than removed, and an edit that quietly unwires it reddens the build instead of passing.
    """
    bar = open(os.path.join(AUTONOMY, "publish_bar.py"), encoding="utf-8").read()
    assert "deliverable_digest" in bar, (
        "publish_bar no longer reads deliverable_digest. Clauses 1 and 6 identify a review by the "
        "DIGEST of what it read rather than by the commit sha it happened at, and unwiring that "
        "silently returns the bar to discarding a clean round on any unrelated commit — the defect "
        "measured in AUT-PD-205-d7df5340. If the re-binding is genuinely being reverted, that is a "
        "governed change in its own right: declare it in amendments.jsonl with the "
        "self_serving_check answered, and rewrite this test to say so.")
