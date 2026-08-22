#!/usr/bin/env python3
"""The change-scoped test selector, and the fail-safe that makes it usable.

⛔ THE ONLY DANGEROUS DIRECTION IS UNDER-SELECTION. A selector that runs too much wastes minutes; a
selector that quietly runs too little turns a green preflight into a statement about nothing, which
is the exact failure class CLAUDE.md §4 exists for. Every assertion below is therefore about
FULL being returned when the answer is uncertain, and about a changed module reaching the tests that
cover it — including transitively, which is where a naive name-match selector would fail.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import affected_tests as A  # noqa: E402


@pytest.fixture
def fake(monkeypatch):
    """Drive `select()` off a chosen file list instead of the real git state."""
    def _set(files):
        monkeypatch.setattr(A, "changed_files", lambda: files)
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


def test_editing_the_selector_or_preflight_takes_the_whole_suite(fake):
    for p in ("scripts/affected_tests.py", "scripts/preflight.sh"):
        fake({p})
        assert A.select() is None, p


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
