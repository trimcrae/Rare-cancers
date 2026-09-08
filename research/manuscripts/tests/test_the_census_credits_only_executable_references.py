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
literals: a guard that computes exposes no literal, a guard reaching its document through an import
is not credited at all, and a credited pattern may bind a sentence's words while claiming nothing
about its digits. Those miss in opposite directions, so `covered` is not a bound on actual coverage
either way (corrected 2026-09-08, P-AB2; this docstring used to call it an upper bound). This module
holds one false-positive channel closed; `claim_ablation` is what runs the guards.

⛔⛔ AND THE ENCODING HALF (2026-09-08, P-AB2). The stripper converted BOTH kinds of column offset
with one rule. AST `col_offset` really is a UTF-8 byte offset, but `tokenize` comment columns are
CHARACTER offsets, so on a line with non-ASCII text the comment span slid left: root's deterministic
counterexample blanked 24 characters out of an executable Unicode literal and left the comment's
manuscript basename standing — the ghost witness reopened by an encoding bug. The non-ASCII cases
below hold both halves shut, and the docstring half is there so that "just use characters
everywhere" cannot pass either.
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

#: ⛔ NON-ASCII PADDING, AND ITS LENGTH IS THE POINT. Each `é` is one character and two UTF-8 bytes,
#: so a column offset read under the wrong convention drifts one position left per character of
#: padding. Eighty is comfortably more than the width of anything asserted below, so a drift of that
#: size cannot land back inside its own span by accident.
PAD = "é" * 80

CASES.update({
    #: The counterexample's own shape, and its geometry is load-bearing: the comment must be SHORT
    #: enough relative to the padding that the whole mis-converted span lands inside the literal.
    #: A longer note would drag the span back across the `#` and blank part of the basename, which
    #: passes this case for the wrong reason — a ghost witness that got away with less.
    "comment_only_non_ascii": _module(
        f'X = "{PAD}" # <DOC>\n'
        'def test_x():\n'
        '    assert X, r"<PAT>"\n'),
    #: The same channel through a single-line module docstring whose non-ASCII runs to its END, so
    #: the closing quote sits far past its character column. This one fails the opposite way: treat
    #: the AST's byte offsets as characters and the docstring's tail survives the stripper.
    "docstring_only_non_ascii": _module(
        f'"""{PAD} borrowed a bound from `<DOC>`, which it does not open. {PAD}"""\n'
        'def test_x():\n'
        '    assert True, r"<PAT>"\n'),
    #: And the credited direction on a non-ASCII line, so a stripper that simply blanked more could
    #: not pass the two above by destroying real coverage.
    "code_reference_non_ascii": _module(
        f'PAD = "{PAD}"  # a trailing note\n'
        'PAPER = "<DOC>"\n'
        'def test_x():\n'
        '    assert PAPER and PAD, r"<PAT>"\n'),
})

#: The only cases that may credit anything: the name is in a constant the interpreter evaluates.
CREDITED = {"code_reference", "code_reference_non_ascii"}


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


def test_a_comment_after_non_ascii_code_is_blanked_and_the_code_is_not():
    """⛔ `tokenize` comment columns are CHARACTERS; the AST's are BYTES. One rule cannot serve both.

    This is root's deterministic counterexample in fixture form (2026-09-08, P-AB2). At the frozen
    HEAD the comment span was converted with the AST's byte rule, slid 80 positions left, blanked a
    stretch of the executable Unicode literal, and left the comment — manuscript basename included —
    entirely intact. That is the ghost-witness path this module exists to hold shut, reopened.
    """
    import ast
    src = f'X = "{PAD}"  # naming {FICTIONAL} in a comment\n'
    code = cc._executable_source(src, ast.parse(src))
    assert len(code) == len(src), "the stripper changed the source length, so offsets no longer align"
    assert PAD in code, (
        "a comment span converted with byte logic ate part of an executable non-ASCII literal; the "
        "census would then miss code it must read")
    assert FICTIONAL not in code, (
        "the document name survived in a COMMENT on a non-ASCII line, so a guard that opens no such "
        "file becomes a witness for it")
    assert "naming" not in code and "in a comment" not in code, "the comment survived the stripper"


def test_a_non_ascii_docstring_is_blanked_to_its_last_character():
    """⛔ The other convention, held from the other side: AST columns really are UTF-8 bytes.

    A docstring whose non-ASCII runs to the closing quote ends at a byte column far past its
    character column. Convert it as characters and the tail survives — which would let a document
    named late in a docstring keep crediting a guard that never opens it.
    """
    import ast
    src = (f'"""{PAD} borrowed a bound from {FICTIONAL}, not opened. tail-marker-{PAD}"""\n'
           f'Y = "{PAD}"  # trailing\n')
    code = cc._executable_source(src, ast.parse(src))
    assert len(code) == len(src), "the stripper changed the source length, so offsets no longer align"
    assert FICTIONAL not in code, "a document named inside a docstring survived the stripper"
    assert "tail-marker" not in code, (
        "the tail of a non-ASCII docstring survived, so the AST's byte columns were read as "
        "characters and the span stopped short")
    assert code.splitlines()[0].strip() == "", "the docstring line was not fully blanked"
    assert PAD in code.splitlines()[1], "the executable non-ASCII literal on the next line was eaten"
    assert "trailing" not in code, "a trailing comment survived the stripper"
