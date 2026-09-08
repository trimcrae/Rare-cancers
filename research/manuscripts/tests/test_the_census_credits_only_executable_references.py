"""A comment or a docstring is not a guard reading a file, and the census must not treat it as one.

⛔⛔ THE DEFECT THIS HOLDS SHUT (2026-09-08, P-AB). `claim_coverage._test_patterns` decided which
document a guard reads by searching that guard's WHOLE SOURCE for the document's basename, and
harvested its regex candidates from every string constant. Both halves inferred executable behaviour
from text Python never evaluates. Measured on the tree that day: one ASO guard names an endpoint
manuscript exactly once, inside its module docstring, narrating a historical mistake — and that one
line was crediting THREE endpoint sentences as covered, one of them the paper's only statement of
the two desmoid cohort sizes. All five guards whose source names that manuscript were re-run against
six perturbations of those quantities and every one stayed green.

★ WHY THE CASES BELOW ARE SYNTHETIC. A test that pinned this behaviour by naming a real manuscript
would itself become a witness for that manuscript in the very census it checks — its literals would
be harvested and credited — which is the defect wearing the costume of its own regression test.
⛔ So no censused document's basename appears in executable code in this module, and none may be
added. The fixtures below build a throwaway `tests/` directory and a document name that exists
nowhere in the repository.

⚠ WHAT THIS CANNOT SHOW. That the census is a measurement. It stays a static screen over harvested
literals: a guard that computes exposes no literal, a credited pattern may bind a sentence's words
while claiming nothing about its digits, and `covered` remains an upper bound. This module holds one
false-positive channel closed; `claim_ablation` is what runs the guards.
"""
from __future__ import annotations

import io
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import claim_coverage as cc  # noqa: E402

#: A document name that is not in this repository, so nothing here can perturb a real reading.
FICTIONAL = "a-document-no-guard-in-this-repository-opens.md"

#: A regex-shaped literal long enough and literal enough to survive harvesting and `is_selective`.
PATTERN = r"thermoluminescent\s+(\d+)\s+quaggas"

#: A second one, always written in code, so an empty harvest cannot pass for a clean one.
EXECUTABLE_PATTERN = r"pyroclastic\s+(\d+)\s+quaggas"


def _module(body):
    return body.replace("<DOC>", FICTIONAL).replace("<PAT>", PATTERN)


CASES = {
    "docstring_only": _module(
        '"""This module once borrowed a bound from `<DOC>`, which it does not open."""\n'
        'def test_x():\n'
        '    assert True, r"<PAT>"\n'),
    "comment_only": _module(
        '# Measured against <DOC>: the count moved and this note records it.\n'
        'def test_x():\n'
        '    assert True, r"<PAT>"\n'),
    "function_docstring_only": _module(
        'def test_x():\n'
        '    """Regression for the reading of `<DOC>`, which lives elsewhere."""\n'
        '    assert True, r"<PAT>"\n'),
    "code_reference": _module(
        'PAPER = "<DOC>"\n'
        'def test_x():\n'
        '    assert PAPER, r"<PAT>"\n'),
}

#: The only case that may credit anything: the name is in a constant the interpreter evaluates.
CREDITED = {"code_reference"}


@pytest.fixture
def census_tests(tmp_path, monkeypatch):
    """Point the census's harvester at a throwaway `tests/` directory."""
    def build(case):
        d = tmp_path / case
        d.mkdir()
        (d / f"test_{case}.py").write_text(CASES[case], encoding="utf-8")
        monkeypatch.setattr(cc, "TESTS", str(d))
        return f"test:test_{case}.py"
    return build


@pytest.mark.parametrize("case", sorted(CASES))
def test_only_an_executable_reference_puts_a_guard_in_scope_for_a_document(case, census_tests):
    witness = census_tests(case)
    harvested = cc._test_patterns(FICTIONAL)
    named = {w for _h, _p, w in harvested}
    if case in CREDITED:
        assert named == {witness}, (
            f"{case}: the document is named in executable code, so this guard must stay in scope — "
            f"dropping it would be coverage lost to where a filename happens to be written")
        assert any(p == PATTERN for _h, p, _w in harvested), (
            f"{case}: the guard is in scope but its executable literal was not harvested")
    else:
        assert not named, (
            f"{case}: the document is named ONLY in prose the interpreter never evaluates, and the "
            f"census credited {sorted(named)} with reading it. A mention in a comment or a docstring "
            f"is how a guard that opens no such file becomes a witness for it.")


def test_a_docstring_is_never_harvested_as_an_executable_pattern(tmp_path, monkeypatch):
    """The harvest half, separately: a regex that IS a docstring binds nothing at runtime.

    ⛔ The module below is in scope by an executable name, so the only question left is whether the
    pattern is credited — and the pattern appears exactly once, as a function's docstring. At HEAD
    it was harvested and could mark a sentence covered; nothing evaluates it.
    """
    d = tmp_path / "harvest"
    d.mkdir()
    (d / "test_harvest.py").write_text(
        f'PAPER = "{FICTIONAL}"\n'
        f'CODE_PATTERN = r"{EXECUTABLE_PATTERN}"\n'
        f'def test_x():\n'
        f'    r"{PATTERN}"\n'
        f'    assert PAPER and CODE_PATTERN\n', encoding="utf-8")
    monkeypatch.setattr(cc, "TESTS", str(d))
    harvested = cc._test_patterns(FICTIONAL)
    # ⚠ The module must be in scope AND yielding, or an empty result would pass the real assertion
    # below for the wrong reason — an absent reading taken for a reading of absence.
    assert any(p == EXECUTABLE_PATTERN and w == "test:test_harvest.py"
               for _h, p, w in harvested), (
        "the fixture module must be in scope by its executable `PAPER` and must yield its executable "
        "literal, or this test proves nothing")
    assert not any(p == PATTERN for _h, p, _w in harvested), (
        "a regex written as a docstring was harvested as coverage; nothing evaluates it, so it "
        "cannot bind a sentence in any document")


def test_the_stripper_blanks_prose_without_moving_any_code_offset():
    """⛔ Blanking rather than deleting is what keeps a name from being spliced out of existence."""
    import ast
    src = ('"""doc with tokens."""\n'
           '# a comment naming things\n'
           'X = "keep-this-literal"  # trailing\n')
    code = cc._executable_source(src, ast.parse(src))
    assert len(code) == len(src), "the stripper changed the source length, so offsets no longer align"
    assert "keep-this-literal" in code, "an executable string literal was stripped"
    assert "doc with tokens" not in code, "a module docstring survived the stripper"
    assert "a comment naming things" not in code, "a comment survived the stripper"
    assert "trailing" not in code, "a trailing comment survived the stripper"
    assert code.count("\n") == src.count("\n"), "the stripper changed the line structure"
