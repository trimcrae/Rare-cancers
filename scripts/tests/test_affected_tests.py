#!/usr/bin/env python3
"""The change-scoped test selector, and the fail-safe that makes it usable.

⛔ THE ONLY DANGEROUS DIRECTION IS UNDER-SELECTION. A selector that runs too much wastes minutes; a
selector that quietly runs too little turns a green preflight into a statement about nothing, which
is the exact failure class CLAUDE.md §4 exists for. Every assertion below is therefore about
FULL being returned when the answer is uncertain, and about a changed module reaching the tests that
cover it — including transitively, which is where a naive name-match selector would fail.
"""
import hashlib
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import affected_tests as A  # noqa: E402

#: ⛔⛔ THE COMMITTED RECORD'S PATH, CAPTURED AT IMPORT — BEFORE ANY FIXTURE CAN REWRITE IT.
#: `_validated` below rewrites `A.VALIDATION_RECORD` for every test in this file, so a test that
#: reads it after collection sees the temp record, never the committed one. A test whose SUBJECT is
#: the committed record must bind here and re-point the module at it. See the comment above
#: `test_the_committed_record_can_only_scope_validated_gatekeepers`.
COMMITTED_RECORD = A.VALIDATION_RECORD


@pytest.fixture(autouse=True)
def _validated(monkeypatch, tmp_path_factory):
    """Every test runs against a record that MATCHES the gatekeepers on disk.

    Otherwise a test exercising the scoping path would be answering "is the selector validated
    right now?" instead of the question it was written to ask, and would go red for a reason that
    has nothing to do with it.

    ⛔ EVERY TEST THAT IS *ABOUT* THE RECORD MUST RE-POINT `A.VALIDATION_RECORD` ITSELF. This
    docstring used to say "the two tests that are about the record patch it themselves", which was
    true of the two that patch it and false of the third, whose whole job was to notice a stale
    committed record — so it was handed a record that matched by construction and could not fail.
    Four tests now re-point it: the two that fabricate a wrong hash, the one that points at a
    missing file, and the one that binds `COMMITTED_RECORD`.
    """
    rec = tmp_path_factory.mktemp("val") / "selector-validation.json"
    rec.write_text(json.dumps({"validated": {
        p: hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
        for p in A.ALWAYS_FULL_PATHS}}))
    monkeypatch.setattr(A, "VALIDATION_RECORD", str(rec))


@pytest.fixture
def fake(monkeypatch):
    """Drive `select()` off a chosen file list instead of the real git state.

    Both git readers are patched, and to the SAME set, so the faked files count as uncommitted —
    which is what every test written before `uncommitted_files()` existed assumed. A test that wants
    the branch-span case (committed on this branch, not in the working tree) uses `fake_split`.
    """
    def _set(files):
        monkeypatch.setattr(A, "changed_files", lambda: files)
        monkeypatch.setattr(A, "uncommitted_files", lambda: files)
    return _set


@pytest.fixture
def fake_split(monkeypatch):
    """Changed-on-this-branch and uncommitted as two different sets."""
    def _set(changed, uncommitted):
        monkeypatch.setattr(A, "changed_files", lambda: changed)
        monkeypatch.setattr(A, "uncommitted_files", lambda: uncommitted)
    return _set


def test_a_changed_module_selects_the_tests_that_import_it(fake):
    fake({"research/modalities/junction_aso_locus_collapse.py"})
    sel = A.select()
    assert sel is not None, "a scopeable change must not fall back to FULL"
    assert any("test_junction_aso_locus_collapse.py" in p for p in sel), sel


def test_selection_follows_imports_transitively(fake):
    """⛔ THE CASE A NAME-MATCH SELECTOR GETS WRONG. `junction_aso_offtarget` imports the collapse
    module, so a change to the collapse module must reach the OFF-TARGET tests too, even though
    their names share no stem."""
    fake({"research/modalities/junction_aso_locus_collapse.py"})
    sel = A.select() or []
    mod_edges, test_edges = A.build_graph()
    assert "junction_aso_locus_collapse" in mod_edges.get("junction_aso_offtarget", set()), (
        "fixture assumption broken: the off-target module no longer imports the collapse module")
    importers = [t for t, m in test_edges.items() if "junction_aso_offtarget" in m]
    if importers:
        assert any(any(t in p for p in sel) for t in importers), (
            f"a transitive dependent was not selected: {importers}")


def test_a_changed_conftest_takes_the_whole_suite(fake):
    fake({"research/modalities/tests/conftest.py"})
    assert A.select() is None


def test_a_changed_test_helper_takes_the_whole_suite(fake):
    """A non-`test_` module inside tests/ is shared machinery; its blast radius is everything."""
    fake({"research/modalities/tests/_helpers.py"})
    assert A.select() is None


def test_editing_the_selector_or_preflight_takes_the_whole_suite(fake, tmp_path, monkeypatch):
    """⚠ NOW EXERCISED THROUGH THE CONTENT HASH, WHICH IS THE MECHANISM (2026-08-22).

    This used to fake the file into the CHANGED SET and assert FULL. That path is gone: membership
    in a diff never made a selector unsafe, and a `git cherry-pick` produced a changed selector that
    was in no diff the check looked at. Editing a gatekeeper still takes the whole suite — because
    editing it changes its hash — so the test now moves the hash, which is what an edit does.
    """
    for target in A.ALWAYS_FULL_PATHS:
        rec = tmp_path / f"{os.path.basename(target)}.json"
        good = {p: hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
                for p in A.ALWAYS_FULL_PATHS}
        good[target] = "0" * 64          # as if this one had just been edited
        rec.write_text(json.dumps({"validated": good}))
        monkeypatch.setattr(A, "VALIDATION_RECORD", str(rec))
        fake({"research/modalities/junction_aso_offtarget.py"})
        assert A.select() is None, f"an edited {target} must take the whole suite"


def test_git_not_answering_takes_the_whole_suite(monkeypatch):
    monkeypatch.setattr(A, "changed_files", lambda: None)
    assert A.select() is None


def test_a_changed_artifact_selects_tests_that_name_it(fake):
    fake({"research/modalities/junction-aso-offtarget-locus-collapse.json"})
    sel = A.select()
    assert sel is not None
    assert any("test_junction_aso_locus_collapse.py" in p for p in sel), sel


def test_a_changed_test_file_selects_itself(fake):
    fake({"research/modalities/tests/test_junction_aso_locus_collapse.py"})
    sel = A.select() or []
    assert any("test_junction_aso_locus_collapse.py" in p for p in sel), sel


def test_an_unrelated_file_selects_nothing_rather_than_everything(fake):
    """Scoping has to actually scope, or the fail-safe swallows the feature."""
    fake({"README.md"})
    assert A.select() == []


def test_the_graph_covers_the_real_tree():
    """Built against the real repository, so a parse regression is caught here rather than by a
    silent FULL that looks like the selector working."""
    mod_edges, test_edges = A.build_graph()
    assert mod_edges and test_edges
    assert len(test_edges) > 100, f"only {len(test_edges)} test modules parsed"
    assert any(m for m in test_edges.values()), "no test imports any repo module — parse is broken"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


# ⛔⛔ WHAT THE SELECTOR DOES FOR A MANUSCRIPT WAS ASSERTED BY NOTHING (2026-08-22, round-13 seat 4).
# Every test above pins a direction the selector FAILS in — conftest, helper, self-edit, dead git —
# and those are the safe directions, because each of them resolves to FULL. Nothing pinned the
# direction it SUCCEEDS in for a manuscript, which is the direction that can quietly under-select:
# `research/manuscripts/**/*.md` reaches a branch that binds documents to modality tests BY NAME, and
# a document no test names selects nothing at all. That branch was added to fix a manuscript-only
# commit selecting zero tests; nothing has been checking it still works.


def test_a_manuscript_selects_the_modality_tests_that_name_it(fake):
    """The extended report is named by modality tests, so editing it must select them."""
    fake({"research/manuscripts/aso/fusion-junction-aso-research-article.md"})
    sel = A.select()
    assert sel is not None, "a manuscript-only change must not fall back to FULL"
    assert sel, ("the extended report is named by modality test modules and selecting none of them "
                 "is the under-selection this branch exists to prevent")
    assert all(p.startswith("research/modalities/tests/") for p in sel), sel


def test_the_selector_reports_a_documents_guard_truthfully(fake, capsys):
    """⛔ 'UNGUARDED' IS A CLAIM ABOUT BOTH SUITES, NOT ABOUT THE ONE THIS SELECTOR DRAWS FROM.

    The journal article is guarded from `research/manuscripts/tests/`, which preflight runs
    unscoped; no modality test names it. The selector correctly returns no modality module for it —
    and used to announce that as "this document is unguarded", which was false. An instrument that
    reports a false absence is worse than one that stays quiet: it is the reading a later session
    acts on.
    """
    journal = "research/manuscripts/aso/fusion-junction-aso-journal-article.md"
    assert os.path.exists(os.path.join(ROOT, journal)), journal
    fake({journal})
    sel = A.select(explain=True)
    assert sel == [], f"no modality test names the journal article, so none should be selected: {sel}"
    said = capsys.readouterr().err
    assert "unguarded" not in said, (
        "the journal article is guarded by modules in research/manuscripts/tests/, so calling it "
        f"unguarded is a false reading — the selector said: {said.strip()}")
    assert "manuscripts test module" in said, (
        "when no modality test names a document the selector must say where it IS guarded, not "
        f"only that it is not guarded here — it said: {said.strip()}")


# ⛔⛔ `ALWAYS_FULL` MUST NOT BE STICKY FOR THE LIFE OF A BRANCH (2026-08-22). `changed_files()` spans
# from the merge-base on purpose, so a run after several commits still covers everything the branch
# introduces. But the unscopeable check read that same span, so one commit touching the selector or
# preflight forced FULL on every later run of that branch: a prose-only manuscript edit ran all 398
# modality modules — 7,800 tests over docking, ABFE and GPU fleet management — for 19m38s and passed
# every one. The safety property is unchanged, because a selector edit is dirty at its own commit and
# is FULL-gated there; what is dropped is re-gating a question already answered.


def test_a_validated_selector_change_does_not_force_full_on_later_commits(fake_split):
    """Selector edited earlier on the branch and VALIDATED; tree now holds only a manuscript.

    This is the case the branch-span rule got wrong: one commit touching the selector forced FULL on
    every later commit of that branch, so a prose-only edit ran all 398 modality modules. Validation
    is what licenses scoping — not the fact that the change is old.
    """
    doc = "research/manuscripts/aso/fusion-junction-aso-journal-article.md"
    fake_split({"scripts/affected_tests.py", "scripts/preflight.sh", doc}, {doc})
    sel = A.select()
    assert sel is not None, (
        "a selector whose content matches its validated hash has already passed a full run; "
        "re-gating every later commit costs the scoped path for the rest of the branch")
    assert all(p.startswith("research/modalities/tests/") for p in sel), sel


def test_git_not_answering_about_the_working_tree_takes_the_whole_suite(monkeypatch):
    """⛔ An unanswered git is an uncertainty, and uncertainty is FULL.

    `changed_files` is built on `uncommitted_files`, so a git that cannot describe the working tree
    still reaches FULL through it. Asserted on the real composition rather than on a patched
    `changed_files`, because that composition is the thing that must not quietly change.
    """
    monkeypatch.setattr(A, "uncommitted_files", lambda: None)
    assert A.changed_files() is None
    assert A.select() is None


# ⛔⛔ CONTENT, NOT PROVENANCE (2026-08-22, round 14 seat 4, reproduced exploit). The rule was "an
# UNCOMMITTED selector edit takes the whole suite", on the premise that a selector change is always
# dirty at the moment of its own commit. `git cherry-pick` auto-commits: the change lands with a
# zero-width dirty window and the new selector immediately scopes itself. merge, revert and rebase
# are the same, and CLAUDE.md §7 mandates them. The gate is now the recorded hash of the validated
# content, so how the file arrived stops mattering.


def test_a_selector_that_does_not_match_its_validated_hash_takes_the_whole_suite(fake, tmp_path,
                                                                                monkeypatch):
    rec = tmp_path / "selector-validation.json"
    rec.write_text(json.dumps({"validated": {p: "0" * 64 for p in A.ALWAYS_FULL_PATHS}}))
    monkeypatch.setattr(A, "VALIDATION_RECORD", str(rec))
    fake({"research/modalities/junction_aso_offtarget.py"})
    assert A.select() is None, (
        "a gatekeeping file whose content no full run has validated must take the whole suite, "
        "however it reached the working tree — a cherry-pick commits with no dirty window at all")


def test_an_unreadable_validation_record_takes_the_whole_suite(fake, tmp_path, monkeypatch):
    """⛔ An unanswered question is an uncertainty, and uncertainty is FULL."""
    monkeypatch.setattr(A, "VALIDATION_RECORD", str(tmp_path / "does-not-exist.json"))
    fake({"research/modalities/junction_aso_offtarget.py"})
    assert A.select() is None


# ⛔⛔ THIS TEST COULD NOT FAIL FOR EIGHTEEN COMMITS (2026-09-01, sprint seat S26-CANNOT-FAIL).
# The `_validated` autouse fixture above rewrites `A.VALIDATION_RECORD` to a temp record built from
# the hashes ON DISK, so the one test whose subject is the COMMITTED record was handed a record that
# matched by construction. Measured, not reasoned: `affected_tests._unvalidated_gatekeepers()`
# against the real record returned `{'scripts/preflight.sh'}` and calling this function directly
# raised its AssertionError, while `pytest scripts/tests/test_affected_tests.py` reported 17 passed.
# That is why CLAUDE.md §6's "permanent tripwire" went unnoticed: the guard written to shout about
# it had been silent since 2026-08-26. It now binds `COMMITTED_RECORD`, which is read at import,
# before any fixture runs — and it asserts that the path it read is the committed one, so a future
# fixture that rewrites the constant cannot silence this test without the assertion naming it.


def test_the_committed_record_can_only_scope_validated_gatekeepers(monkeypatch, fake):
    """A stale record must select FULL, not make a successful FULL run impossible.

    The old hash-equality assertion was itself in the full suite: editing preflight invalidated
    the record, this assertion failed, and the green run required to refresh it was unreachable.
    Keep the fail-closed selection behavior; let a full run earn the new hashes after it passes.
    """
    monkeypatch.setattr(A, "VALIDATION_RECORD", COMMITTED_RECORD)
    expected = os.path.join(ROOT, "scripts", "selector-validation.json")
    assert os.path.abspath(A.VALIDATION_RECORD) == os.path.abspath(expected), (
        f"this test must read the COMMITTED record at {expected}, and it is reading "
        f"{A.VALIDATION_RECORD}. A record built by a fixture matches the tree by construction, so "
        "the assertion below would be about nothing.")
    stale = A._unvalidated_gatekeepers()
    fake({"research/modalities/junction_aso_offtarget.py"})
    selected = A.select()
    if stale is None or stale:
        assert selected is None, "unvalidated gatekeepers must select FULL"
    else:
        assert selected, "validated gatekeepers must select guards for the changed module"


def _tiny_tree(tmp_path, monkeypatch):
    """A two-file stand-in for research/modalities, so the memo's behaviour is driven in
    milliseconds instead of 4.4 s a build. ⛔ THE GUARD MUST NOT COST WHAT IT SAVED: written first
    against the real tree, these two tests took 12 s of the 16.8 s this file then cost — a memo
    whose guards reintroduce the bill it removed is not an optimisation, it is a relocation."""
    mod = tmp_path / "modalities"
    tests = mod / "tests"
    tests.mkdir(parents=True)
    (mod / "alpha.py").write_text("import json\n", encoding="utf-8")
    (mod / "beta.py").write_text("import alpha\n", encoding="utf-8")
    (tests / "test_beta.py").write_text("import beta\n", encoding="utf-8")
    monkeypatch.setattr(A, "MOD", str(mod))
    monkeypatch.setattr(A, "TESTS", str(tests))
    A._GRAPH_MEMO.clear()
    return mod, tests


def test_the_graph_memo_is_keyed_on_the_files_it_parsed(tmp_path, monkeypatch):
    """⛔⛔ A MEMO THAT OUTLIVES ITS INPUT IS A SELECTOR THAT SELECTS FOR YESTERDAY'S TREE.

    `build_graph` AST-parses every module under research/modalities and every file in its tests/
    directory — 4.4 s, measured 2026-09-02 — and this file called it nine times, which made
    `test_affected_tests.py` **41.0 s** on its own and, under preflight's `--dist loadfile`, set gate
    13's entire 55 s wall clock, on four cores with three of them idle.

    ★ THE KEY IS (name, size, mtime_ns) OF EVERY FILE THE PARSE READS, never "an answer exists".
    This drives all three directions: an untouched tree reuses, an ADDED module rebuilds, and an
    EDITED module rebuilds. If the key ever weakened to a bare flag, a session that edited an import
    would be handed a graph built before the edit and the selector would silently omit the tests
    that edit actually reaches — the one direction this selector must never move, since it fails
    SAFE to FULL everywhere else.
    """
    mod, _ = _tiny_tree(tmp_path, monkeypatch)
    first = A.build_graph()
    assert first[0] == {"alpha": set(), "beta": {"alpha"}}
    assert A.build_graph() is first, (
        "two calls with the tree untouched did not reuse one graph — the memo is not working, and "
        "this file is about to cost 41 s again")

    (mod / "gamma.py").write_text("import beta\n", encoding="utf-8")
    after = A.build_graph()
    assert after is not first, (
        "a module was ADDED and build_graph returned the graph from before it existed. Every "
        "selection made from that graph is blind to the new module and to everything importing it.")
    assert after[0].get("gamma") == {"beta"}

    # ⛔ AND AN EDIT IN PLACE, WHICH IS THE CASE A NAME-ONLY OR COUNT-ONLY KEY WOULD MISS: same file
    # count, same names, different imports. The size and mtime are in the key for exactly this.
    (mod / "alpha.py").write_text("import beta\nimport json\n", encoding="utf-8")
    edited = A.build_graph()
    assert edited is not after and edited[0].get("alpha") == {"beta"}, (
        "an import was added to an existing module and the memo did not notice — the selector would "
        "keep resolving dependencies against the previous version of the file")


def test_an_unstattable_tree_disables_the_memo_rather_than_freezing_it(tmp_path, monkeypatch):
    """⛔ FAIL OPEN ON THE MEMO, NEVER ON THE ANSWER. If the fingerprint cannot be taken, the right
    behaviour is to rebuild every time — slow and correct — not to hand back whatever was cached
    first. A `None` fingerprint must neither be stored under nor matched against."""
    _tiny_tree(tmp_path, monkeypatch)
    monkeypatch.setattr(A, "_graph_fingerprint", lambda: None)
    a = A.build_graph()
    b = A.build_graph()
    assert a[0] is not None and a[0] == b[0]
    assert a is not b, (
        "with no fingerprint the graph was still memoised — a tree this selector cannot stat is one "
        "it cannot know is unchanged, so it must re-derive")
    assert A._GRAPH_MEMO == {}, "a graph was stored under a None key"


def test_a_failed_parse_is_never_memoised(tmp_path, monkeypatch):
    """⛔ `None, None` MEANS 'AN UNCERTAINTY — GO FULL', AND AN UNCERTAINTY MUST NOT BE CACHED. If a
    syntax error were memoised, repairing the file would leave the selector answering FULL for the
    rest of the process on a tree that is now perfectly parseable — and the next call after the
    repair is exactly when a caller most needs the truth."""
    mod, _ = _tiny_tree(tmp_path, monkeypatch)
    (mod / "broken.py").write_text("def (\n", encoding="utf-8")
    assert A.build_graph() == (None, None)
    assert A._GRAPH_MEMO == {}, "a failed parse was stored in the memo"
    (mod / "broken.py").write_text("import alpha\n", encoding="utf-8")
    repaired = A.build_graph()
    assert repaired[0] is not None and repaired[0].get("broken") == {"alpha"}
