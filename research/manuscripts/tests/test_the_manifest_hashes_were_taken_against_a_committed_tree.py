"""⛔ A MANIFEST GENERATED AGAINST A DIRTY TREE HASHES CONTENT THAT IS IN NO COMMIT.

The sibling guard `test_the_manifest_revision_is_a_commit_a_reader_can_resolve.py` asks whether the
revision the deposit names can be resolved. This one asks the question that survives a `yes`: the
revision resolves, and the hash list still does not describe it.

⛔ WHY THIS EXISTS — AUT-PD-016, MEASURED ON `main` 2026-08-27. The manifest committed at ae7930ddb
names `git_revision` 21c733cd and asserts sha256 d6c41c2e… for
`research/manuscripts/submission-metrics.json`. At 21c733cd that file is d971b2f9…. The asserted
bytes were uncommitted working-tree content at generation time and were committed only later, inside
ae7930ddb itself. A reader who does the one thing the artifact invites — check out the named
revision, verify the hashes — gets a mismatch on a file that revision cannot produce.

⚠ AND THE MANIFEST SAID SO ITSELF, TO NOBODY. It recorded
`git_tree_is_clean_apart_from_this_manifest: false`, whose documented meaning is exactly "these
hashes were taken against a dirty tree, do not trust them". `_archive_only` drops that field from
the inventory comparison for a good reason (`--check` cried wolf on every commit and would have been
switched off), and no other caller read it, so the only honest field in the whole defect governed
nothing for as long as it existed.

⭐ WHAT IS TESTED HERE IS THE GUARD, NOT THE ARTIFACT'S CURRENT STATE, AND THAT IS DELIBERATE.
Whether the manifest on disk is presently sound is preflight's generated-artifact gate to answer —
it runs `--check-archive`, which now refuses a `false` flag before it compares anything. Asserting it
a second time here would make one defect produce two unrelated reds in two places, which is the
duplication CLAUDE.md §1 exists to prevent. So these tests stay green whatever state the manifest is
in, and go red only if the guard itself stops discriminating.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MANUSCRIPTS = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MANUSCRIPTS))
sys.path.insert(0, MANUSCRIPTS)
sys.path.insert(0, os.path.join(REPO, "research", "modalities"))

import aso_archive_manifest as m  # noqa: E402

MANIFEST = os.path.join(MANUSCRIPTS, "aso", "fusion-junction-aso-archive-manifest.json")
FLAG = "git_tree_is_clean_apart_from_this_manifest"


def _manifest_text():
    if not os.path.exists(MANIFEST):
        pytest.fail("the archive manifest is missing; there is no deposit provenance to check")
    return io.open(MANIFEST, encoding="utf-8").read()


def _with_flag(text, literal):
    """The real manifest text with the cleanliness flag replaced, asserting the edit LANDED.

    ⛔ THE ASSERTION IS THE TEST'S OWN GUARD. A mutation that silently fails to apply leaves the
    text unchanged, and an unchanged text produces whatever verdict the original would have — which
    is indistinguishable from the guard working. Every mutation below proves it landed before any
    result is read.
    """
    old = None
    for candidate in ('"%s": true,' % FLAG, '"%s": false,' % FLAG, '"%s": null,' % FLAG):
        if text.count(candidate) == 1:
            old = candidate
            break
    assert old is not None, (
        "the manifest does not carry exactly one `%s` line in a form this test recognises, so no "
        "mutation could be applied and nothing below would be measuring anything" % FLAG)
    new = '"%s": %s,' % (FLAG, literal)
    if new == old:
        return text
    mutated = text.replace(old, new)
    assert mutated != text, "MUTATION DID NOT LAND: %r -> %r" % (old, new)
    assert mutated.count(new) == 1, "MUTATION DID NOT LAND CLEANLY: %r" % new
    return mutated


def test_a_manifest_whose_tree_was_dirty_is_refused():
    refusal = m._dirty_tree_refusal(_with_flag(_manifest_text(), "false"))
    assert refusal is not None, (
        "a manifest recording `%s: false` was accepted. Its hash list was taken while tracked "
        "files were uncommitted, so it can assert a sha256 that no commit contains — which is "
        "what shipped on `main` at ae7930ddb." % FLAG)
    assert "REFUSED" in refusal


def test_the_refusal_names_the_ordering_constraint_rather_than_saying_regenerate():
    """⛔ THE GENERIC REMEDY IS THE ONE THAT REPRODUCES THE DEFECT.

    Preflight's staleness line says "rerun the generator and commit the result". Doing that against
    a dirty tree re-hashes the same uncommitted edits and writes `false` again. The refusal has to
    say the fix is an ORDERING — commit everything else first, regenerate last — or the next
    session pays the hour this one did.
    """
    refusal = m._dirty_tree_refusal(_with_flag(_manifest_text(), "false"))
    assert refusal is not None
    low = refusal.lower()
    assert "ordering" in low, "the refusal does not tell the reader the fix is an ordering"
    assert "last commit" in low, "the refusal does not say to regenerate as the last commit"


def test_a_manifest_taken_against_a_clean_tree_is_accepted():
    """⛔ THE HALF THAT KEEPS THE GUARD ALIVE. A guard that refuses everything is removed the first
    time it is inconvenient, and its removal takes the discriminating half with it."""
    assert m._dirty_tree_refusal(_with_flag(_manifest_text(), "true")) is None, (
        "a manifest recording `%s: true` was refused. That is the state a correct deposit is in, "
        "so this guard would go red on every sound manifest and be switched off." % FLAG)


def test_real_committed_clean_manifests_are_accepted():
    """The same acceptance, against manifests this repository actually produced rather than a
    mutation of the current one — so the green half is anchored to real artifacts."""
    checked = 0
    for rev in ("8d4bf8195", "06d2ebd6f", "1db973e72"):
        r = subprocess.run(
            ("git", "cat-file", "-p",
             "%s:research/manuscripts/aso/fusion-junction-aso-archive-manifest.json" % rev),
            cwd=REPO, capture_output=True, text=True)
        if r.returncode != 0:
            continue          # shallow clone: this commit is simply absent, see the sibling guard
        text = r.stdout
        if json.loads(text).get(FLAG) is not True:
            continue
        assert m._dirty_tree_refusal(text) is None, (
            "the manifest committed at %s was taken against a clean tree and is still refused" % rev)
        checked += 1
    if checked == 0:
        print("⚠ none of the reference commits are present (shallow clone), so the real-artifact "
              "acceptance case was NOT checked — the mutation case above still ran.")


def test_unknown_and_absent_provenance_are_refused_too():
    """⛔ `null` MEANS "NO GIT HERE", WHICH IS EXPLICITLY NOT "CLEAN", AND A MISSING FIELD IS THE
    SHAPE THIS DEFECT TAKES IF SOMEONE DELETES THE FIELD TO CLEAR THE RED. Both are hashes whose
    provenance cannot be tied to a commit, which is the only property this guard is about."""
    text = _manifest_text()
    assert m._dirty_tree_refusal(_with_flag(text, "null")) is not None, (
        "`%s: null` was accepted, but the generator documents null as 'unknown, never clean'" % FLAG)

    gone = text.replace("  " + '"%s": false,' % FLAG + "\n", "")
    if gone == text:
        gone = text.replace("  " + '"%s": true,' % FLAG + "\n", "")
    assert FLAG not in gone, "MUTATION DID NOT LAND: the field is still present"
    assert m._dirty_tree_refusal(gone) is not None, (
        "a manifest with no `%s` field at all was accepted, so deleting the field clears the "
        "guard — and deleting the field is the cheapest way to make this red go away" % FLAG)


def test_the_flag_stays_out_of_the_inventory_comparison():
    """⛔ THE CRY-WOLF FIX MUST SURVIVE THIS ONE. `_archive_only` drops the repository-state fields
    so `--check-archive` does not go red merely because a commit happened (2026-08-17). The new
    guard checks the flag SEPARATELY, as a precondition; it must not be smuggled back into the diff,
    or the failure it replaces returns."""
    assert FLAG in m._REPO_STATE_FIELDS
    assert "git_revision" in m._REPO_STATE_FIELDS
    sample = {"git_revision": "a" * 40, FLAG: True, "n_files": 3}
    other = {"git_revision": "b" * 40, FLAG: False, "n_files": 3}
    assert m._archive_only(sample) == m._archive_only(other), (
        "the repository-state fields are back in the inventory comparison, so --check-archive will "
        "go red on every commit again")


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# ⛔ THE CALL SITE IS GUARDED SEPARATELY FROM THE FUNCTION, AND THIS PAIR IS WHY.
#
# ⚠ MEASURED WHILE WRITING THIS FILE (2026-08-27). The tests above were mutation-tested against four
# deliberate defeats of the guard. Three went red. The fourth — replacing the `refusal =
# _dirty_tree_refusal(old_text)` call in `main()` with `refusal = None`, so the checker simply stops
# consulting the guard — left ALL SIX GREEN while `--check-archive` happily accepted the very
# manifest that shipped the defect. A guard that is correct and unreachable is worth nothing, and a
# test suite that only exercises the function cannot tell the two apart. That is the one-of-a-pair
# defect class, and the pair here is `_dirty_tree_refusal` and the checker that must call it.
#
# ⭐ THESE DRIVE `main()` ITSELF, THROUGH A REDIRECTED `OUT`. The manifest under test is a temporary
# file, never the committed artifact — a test that mutates a deposit artifact in the working tree is
# how a mutation window becomes a commit window.
# ⚠ `main()` runs the provenance check BEFORE `build()`, so these cost no re-derivation. If that
# ordering is ever reversed these tests will start hashing 483 files and get slow, which is the
# cheapest possible alarm for a change that also re-opens the suppression hazard `main()` documents.

@pytest.fixture()
def redirected_manifest(tmp_path, monkeypatch):
    """A throwaway manifest `main()` will read instead of the committed one."""
    target = tmp_path / "fusion-junction-aso-archive-manifest.json"
    monkeypatch.setattr(m, "OUT", str(target))
    return target


@pytest.mark.parametrize("mode", ["--check", "--check-archive"])
def test_both_check_modes_refuse_a_dirty_tree_manifest(redirected_manifest, capsys, mode):
    redirected_manifest.write_text(_with_flag(_manifest_text(), "false"), encoding="utf-8")
    rc = m.main([mode])
    err = capsys.readouterr().err
    assert rc == 1, (
        "`%s` accepted a manifest recording `%s: false` and exited %d. The guard function may still "
        "be correct — check that main() actually CALLS it; that exact wiring cut passed every "
        "function-level test in this file." % (mode, FLAG, rc))
    assert "REFUSED" in err, (
        "`%s` exited non-zero without printing the refusal, so preflight's gate row would show a "
        "bare STALE and send the reader to regenerate — the action that reproduces the defect."
        % mode)
    assert "ordering" in err.lower()


@pytest.mark.parametrize("mode", ["--check", "--check-archive"])
def test_both_check_modes_pass_provenance_when_the_flag_is_true(redirected_manifest, capsys, mode):
    """⛔ THE GREEN HALF AT THE CALL SITE. With the flag true the provenance stage must let the run
    THROUGH to the inventory question. It will then almost certainly report STALE — the temporary
    file is not a re-derivation of the current tree — and that is a different verdict from a
    different stage, which is precisely what must be distinguishable."""
    redirected_manifest.write_text(_with_flag(_manifest_text(), "true"), encoding="utf-8")
    m.main([mode])
    err = capsys.readouterr().err
    assert "REFUSED" not in err, (
        "`%s` refused a manifest taken against a clean tree, so every sound deposit would be "
        "rejected and this guard would be switched off." % mode)
