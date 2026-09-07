#!/usr/bin/env python3
"""A test that CANNOT FAIL is this repository's signature defect. This looks for the mechanisms.

⛔⛔ WHY THIS EXISTS — FOUR INSTANCES OF ONE SHAPE, FOUND IN ONE NIGHT (2026-09-01).

  a deposit guard asking a git repository that contained exactly one commit;
  a mutation harness that scored 0/8 against code it had never mutated;
  an active budget hold that was never consulted at level 0;
  and the one this file is named after —
  `scripts/tests/test_affected_tests.py::test_the_committed_record_matches_the_committed_gatekeepers`,
  whose file's `autouse` fixture rewrote `affected_tests.VALIDATION_RECORD` to a temp record built
  from the hashes ON DISK. The one test whose subject was the COMMITTED record was therefore handed
  a record that matched by construction. Measured, not reasoned:
  `affected_tests._unvalidated_gatekeepers()` returned `{'scripts/preflight.sh'}` and calling the
  test function directly raised, while `pytest scripts/tests/test_affected_tests.py` reported
  **17 passed**. CLAUDE.md §6 calls that stale record a "permanent tripwire"; the guard written to
  shout about it had been silent for eighteen commits.

★ THE PROPERTY, NOT THE INSTANCE — the same argument `test_no_guard_can_silently_not_run.py` makes
about SKIPS, one level further in. That file asks whether a guard RAN. This one asks whether a
guard that ran could ever have said no.

⛔⛔ WHAT THIS CANNOT SEE, STATED FIRST BECAUSE A META-GUARD THAT OVERSTATES ITS COVERAGE IS THE
SAME DEFECT ONE LEVEL UP.

  "Can this test fail?" is undecidable in general, and nothing here approximates it. This is a
  detector for TWO SYNTACTIC MECHANISMS and nothing else:

    R1  an `autouse` fixture that rebinds a module attribute, read by a test in the same module
        that does not rebind it itself — the mechanism above;
    R2  `@pytest.mark.parametrize` over a literally empty argvalues list, which collects nothing.

  It does NOT see, and a green run here is no evidence about any of them:
    · a fixture that rebinds a DICT KEY, a list element, an env var, or an attribute reached by a
      dotted path (`monkeypatch.setattr(A.sub, "X", …)`) rather than a bare module name;
    · a `conftest.py` fixture whose rewrite reaches a test in a DIFFERENT file — R1 is per-module
      on purpose, because `research/modalities/tests/conftest.py` legitimately neutralises
      `gpu_backend.vast_rental_hold` for a whole suite, and the hold's own test defends itself by
      binding the real function at import (verified 2026-09-01: `_real_hold = gb.vast_rental_hold`
      at `test_vast_account_rental_hold.py:35`);
    · an assertion that is true but about the wrong object — the P.OUT sites audited below are
      exactly that judgement, made by reading, and this file only records that somebody made it;
    · a parametrisation over a COMPUTED list that happens to be empty at run time;
    · a loop whose collection is empty, which is the far larger class and is deliberately NOT
      guarded here. Swept 2026-09-01: 327 tests in the five suites place every failure point inside
      a loop; 7 of those loop over a FILTERED comprehension, a `glob` or a `listdir`, which is the
      subset that can empty while the tree stays healthy; and **every one of the 7 was non-empty
      when counted** (15 `prerequisite_of` rows, 2 `R13-a`/`R14-a` rungs, 5 workflows carrying
      `fleet_branch ||`, 10 files under `archive/`). Three of the seven are additionally
      correct-when-empty by construction, being "no occurrence of X exists" checks. A guard over a
      class with no live instance would be an allowlist of 7 names and no measurement, so the
      finding is written down (`research/autonomy/sprint-2026-09-01/S26-CANNOT-FAIL.md`) rather
      than enforced;
    · a `try/except` that swallows an assertion. Swept the same day: 16 candidates, all 16 read and
      all 16 the deliberate `try: f(); assert False; except ValueError: pass` idiom or a documented
      hand-off to a named sibling test. **The class has no instance here.**

⚠ AND THE AUDITED TABLE IS ITSELF GUARDED. `test_the_detector_still_fires_on_every_audited_site`
re-derives the offenders and demands that each audited key is still among them. A detector quietly
weakened into uselessness would leave the table describing sites it no longer finds, and this file
would go red rather than green — which is the failure mode the whole file is about.
"""
from __future__ import annotations

import ast
import glob
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

#: ⭐ A PATTERN, NOT A LIST, so a suite added tomorrow is covered without anybody enrolling it.
SCOPE_PATTERNS = (
    "scripts/tests/*.py",
    "systems/tests/*.py",
    "research/manuscripts/tests/*.py",
    "research/modalities/tests/*.py",
    "research/autonomy/tests/*.py",
)

#: R1 sites somebody has read and judged correct, each with the reason. An entry is a RECORDED
#: DECISION, never a silencer: the key must still be detected (see the last test) and the reason
#: must say why the rewritten value is the one the test genuinely means to read.
#: ⛔ Do not add a row here to make a red run go away. The question an entry answers is "is the
#: object this test asserts about the object its name says?", and the answer has to come from
#: reading the test.
AUDITED_R1 = {
    "research/manuscripts/tests/test_emc_fusion_partner_pooling_check.py"
    "::test_check_does_not_write_the_artifact":
        "CORRECT. `_artifact` redirects P.OUT at a private tmp copy precisely so no test writes to "
        "the tracked tree, and this test's subject IS that copy: it perturbs the copy, runs "
        "`--check`, and compares the copy's bytes before and after. Reading the committed artifact "
        "here would defeat the redirection the fixture exists to provide.",
    "research/manuscripts/tests/test_emc_fusion_partner_pooling_check.py"
    "::test_check_reports_a_missing_artifact_rather_than_creating_one":
        "CORRECT. It removes P.OUT and asserts `--check` neither passes nor recreates it. The file "
        "removed must be the tmp copy; removing the committed artifact is the incident "
        "CLAUDE.md §6 records.",
    "research/manuscripts/tests/test_emc_systemic_therapy_pooling_check.py"
    "::test_check_does_not_write_the_artifact":
        "CORRECT — the same producer contract and the same redirection as its fusion-partner twin.",
    "research/manuscripts/tests/test_emc_systemic_therapy_pooling_check.py"
    "::test_check_reports_a_missing_artifact_rather_than_creating_one":
        "CORRECT — the same producer contract and the same redirection as its fusion-partner twin.",
}


def _scope_files():
    out = []
    for pattern in SCOPE_PATTERNS:
        out += [p for p in glob.glob(os.path.join(REPO, pattern))
                if os.path.basename(p).startswith(("test_", "conftest"))]
    out = sorted(set(out))
    #: a scope that has silently emptied is this file's own defect class, so it is a hard failure
    assert len(out) >= 500, (
        f"only {len(out)} test file(s) matched {SCOPE_PATTERNS}; the five suites are far larger "
        "than that, so these patterns have stopped matching and every rule below would pass by "
        "finding nothing. Re-derive the scope rather than lowering the floor.")
    return out


def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _module_rebinds(fn):
    """`{"A.NAME": lineno}` for every `monkeypatch.setattr(<bare module name>, "<attr>", …)`."""
    out = {}
    for c in ast.walk(fn):
        if isinstance(c, ast.Call) and (_dotted(c.func) or "").endswith("monkeypatch.setattr") \
                and len(c.args) >= 2 and isinstance(c.args[0], ast.Name) \
                and isinstance(c.args[1], ast.Constant) and isinstance(c.args[1].value, str):
            out[f"{c.args[0].id}.{c.args[1].value}"] = c.lineno
    return out


def _is_autouse_fixture(fn):
    for dec in fn.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if not (_dotted(target) or "").endswith("fixture"):
            continue
        if isinstance(dec, ast.Call) and any(
                kw.arg == "autouse" and isinstance(kw.value, ast.Constant) and kw.value.value
                for kw in dec.keywords):
            return True
    return False


def _r1_offenders():
    """Tests that READ a module attribute an autouse fixture in their own module REWROTE."""
    offenders = {}
    for path in _scope_files():
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError as exc:                     # a suite that will not parse is a finding
            pytest.fail(f"{rel} does not parse, so nothing in it is being checked: {exc}")
        rewritten = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_autouse_fixture(node):
                rewritten.update(_module_rebinds(node))
        if not rewritten:
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name.startswith("test_")):
                continue
            own = set(_module_rebinds(node))
            read = {_dotted(c) for c in ast.walk(node) if isinstance(c, ast.Attribute)}
            hit = (read & set(rewritten)) - own
            if hit:
                offenders[f"{rel}::{node.name}"] = sorted(hit)
    return offenders


def test_no_test_reads_a_module_attribute_its_own_autouse_fixture_rewrote():
    """⛔ THE MECHANISM THAT COST EIGHTEEN COMMITS. The fixture hands the test a value built from
    the tree, so an assertion about the committed value is an assertion about the fixture."""
    unaudited = {k: v for k, v in _r1_offenders().items() if k not in AUDITED_R1}
    assert not unaudited, (
        "these tests read a module attribute that an `autouse` fixture in the same file rewrote, "
        "so whatever they assert about it is a statement about the fixture and not about the "
        "repository:\n  "
        + "\n  ".join(f"{k} -> {v}" for k, v in sorted(unaudited.items()))
        + "\n\nEither re-point the attribute inside the test (capture the real value at MODULE "
          "level, before any fixture can run, and `monkeypatch.setattr` it back — that is what "
          "`scripts/tests/test_affected_tests.py::COMMITTED_RECORD` does), or move the test out of "
          "the fixture's module, or — if the rewritten value really is the object the test means "
          "to assert about — record it in AUDITED_R1 with the reason, which is a decision somebody "
          "has to make by reading the test.")


def test_the_detector_still_fires_on_every_audited_site():
    """⛔⛔ THE GUARD ON THE GUARD. An allowlist whose entries the detector no longer finds is
    indistinguishable from a detector that finds nothing at all — and 'finds nothing at all' is
    exactly how this file would look if somebody narrowed `_r1_offenders` to make a red run pass.
    """
    found = _r1_offenders()
    missing = sorted(k for k in AUDITED_R1 if k not in found)
    assert not missing, (
        "AUDITED_R1 records these sites as audited, and the detector no longer flags them:\n  "
        + "\n  ".join(missing)
        + "\n\nEither the tests were fixed — in which case DELETE the entries, because a stale "
          "exemption is a standing licence for the next test that lands at that name — or the "
          "detector has been weakened and is now reporting on nothing.")
    for key, reason in AUDITED_R1.items():
        assert isinstance(reason, str) and len(reason.strip()) >= 40, (
            f"the AUDITED_R1 entry for {key} carries no reason a reader could check. An exemption "
            "without a reason is an exemption nobody took responsibility for.")


def test_no_parametrisation_collects_nothing():
    """⛔ A `parametrize` over an empty list produces zero test cases and reports as a pass at the
    file level. Zero instances today; this keeps it there, and costs nothing."""
    empty = []
    for path in _scope_files():
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in node.decorator_list:
                if not isinstance(dec, ast.Call):
                    continue
                target = dec.func
                if not (_dotted(target) or "").endswith("parametrize") or len(dec.args) < 2:
                    continue
                argvalues = dec.args[1]
                if isinstance(argvalues, (ast.List, ast.Tuple, ast.Set)) and not argvalues.elts:
                    empty.append(f"{rel}::{node.name}:{dec.lineno}")
    assert not empty, (
        "these parametrisations are over an empty literal, so they collect no test case at all "
        "and the function they decorate never runs:\n  " + "\n  ".join(empty))


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
