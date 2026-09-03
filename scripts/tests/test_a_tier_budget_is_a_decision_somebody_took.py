#!/usr/bin/env python3
"""The tier budgets, and the ways a budget guard can quietly stop being one.

⛔⛔ WHAT THIS PROTECTS, AND WHY A NUMBER RATHER THAN A RULE. The publication gate reached 9.7
minutes to check a 4,695-word paper by pure accretion — gate 13 at 789 -> 1,030 -> 1,119 tests in
ten days, the modalities suite at 8,212 with zero failures across eight committed publication runs,
2,973 tests in the repository for six pages. Every addition was justified by a real incident. That
is exactly why nobody caught the sum: there was no moment at which the total was anybody's decision,
and it took trimcrae reading it and saying "1000 pure logic tests for a 6 page paper seems insane".

★ A PROSE RULE WOULD DECAY THE SAME WAY. This repository's own record is unambiguous on that —
`subagent_width` governed nothing for a fortnight, the fan-out receipt field was agreed in prose and
lost twice, "both hashes are stale" sat in CLAUDE.md as an open diagnosis since 2026-08-25. So the
anti-bloat rule is a committed ceiling that a gate reads.

★★ AND THE GUARD ITSELF IS THE NEXT THING TO ROT, WHICH IS WHAT THESE TESTS ARE FOR. The three ways
it stops working, driven rather than described: the ceilings drift so far above the counts that
nothing can ever hit them; a directory silently leaves the budgeted set and stops being counted at
all; or the counter stops counting.
"""
from __future__ import annotations

import ast
import json
import os
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(SCRIPTS)
BUDGETS = os.path.join(SCRIPTS, "tier-budgets.json")
TOOL = os.path.join(SCRIPTS, "tier_budget.py")


@pytest.fixture(scope="module")
def doc():
    with open(BUDGETS, encoding="utf-8") as fh:
        return json.load(fh)


def _run(*args):
    return subprocess.run(["python3", TOOL, *args], capture_output=True, text=True,
                          cwd=ROOT, timeout=120)


def test_every_tier_is_within_its_budget_today():
    """The live check. When this goes red the answer is in `tier-budgets.json`, and raising the
    ceiling is the LAST of the three options it names."""
    r = _run("--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_counter_counts_and_a_shadowed_test_is_not_a_test(tmp_path, monkeypatch):
    """⛔ A GUARD THAT RETURNS ZERO IS GREEN FOREVER. Point the counter at a directory whose test
    functions are known and require the arithmetic, so a counter that broke — an import change, a
    naming convention shift, a walk that stopped recursing — fails here rather than reporting a
    comfortable number nobody re-derives.

    ⛔⛔ AND THE SECOND HALF IS THE SAME CLAIM, WHICH IS WHY IT IS THE SAME TEST RATHER THAN A NEW
    ONE. A test function whose name is already bound in its namespace does not fail — Python
    replaces it and pytest never sees it — so the counter's number stops being a number of tests
    that RUN. Measured 2026-09-03: `systems/tests/test_autonomy_health.py` held 77 `def test_` and
    `pytest --collect-only -q` reported 75; the two that died were the anti-defeat and
    one-fact-one-place guards on `cycles_are_sized`, shadowed by identically-named tests of
    `fanout_is_governed` a hundred lines below. ★ Both were still being PAID FOR out of a ceiling
    standing at 1400/1400.
    ⚠ Folded in deliberately, and said out loud: the commit-loop tier was AT its ceiling when this
    was written, and `tier-budgets.json` names raising it as the last of three answers — so a guard
    that is genuinely a property of this counter's own number goes where that number is checked,
    not into a new function bought by moving a bar. It is one claim: the count is a count of tests.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("tier_budget", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = tmp_path / "tests"
    d.mkdir()
    (d / "test_a.py").write_text("def test_one():\n    pass\ndef test_two():\n    pass\n"
                                 "def helper():\n    pass\n", encoding="utf-8")
    (d / "test_b.py").write_text("async def test_three():\n    pass\n", encoding="utf-8")
    (d / "not_a_test.py").write_text("def test_ignored():\n    pass\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", str(tmp_path))
    files, functions, shadowed = mod.count_dir("tests")
    assert (files, functions, shadowed) == (2, 3, []), (files, functions, shadowed)

    # The mutation: one name, twice, in one module — and it must be NAMED, not merely counted.
    (d / "test_b.py").write_text("def test_three():\n    pass\n\n\ndef test_three():\n    pass\n",
                                 encoding="utf-8")
    files, functions, shadowed = mod.count_dir("tests")
    assert functions == 4, "the source still defines four; the budget pays for all of them"
    assert [(n, ls) for _, n, ls in shadowed] == [("test_three", [1, 5])], shadowed

    # ⛔ AND DETECTION IS NOT REFUSAL. `--check` must EXIT NON-ZERO on a shadow even when every tier
    # is comfortably under its ceiling, or this is a report nobody acts on.
    monkeypatch.setattr(mod, "measure", lambda: [
        {"tier": "t", "directories": ["tests"], "files": 1, "test_functions": 4, "budget": 9999,
         "over": False, "why": "", "shadowed": [{"file": "tests/test_b.py", "name": "test_three",
                                                 "lines": [1, 5]}]}])
    assert mod.main(["--check"]) == 1, "a shadowed test was detected and then tolerated"


def test_an_unparseable_file_does_not_buy_headroom(tmp_path, monkeypatch):
    """⛔ THE WRONG DIRECTION FOR A BUDGET. A file the counter cannot parse must not count as zero
    tests — that would let a broken file create room under the ceiling."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tier_budget", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = tmp_path / "tests"
    d.mkdir()
    (d / "test_broken.py").write_text("def (\n", encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", str(tmp_path))
    assert mod.count_dir("tests") == (1, 1, [])


def test_every_tests_directory_in_the_repository_is_inside_some_budget(doc):
    """⛔⛔ THE FAILURE THAT WOULD MAKE ALL OF THIS COSMETIC: a new tests directory appears, is
    never added to a tier, and grows without limit while every budgeted tier reads green. The
    budgeted set is checked against what the repository actually has, so a new directory fails
    here on the commit that creates it."""
    budgeted = {d for spec in doc["tiers"].values() for d in spec["directories"]}
    found = set()
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in (".git", "node_modules", "__pycache__")
                   and not x.startswith(".")]
        if os.path.basename(base) != "tests":
            continue
        if any(f.startswith("test_") and f.endswith(".py") for f in files):
            found.add(os.path.relpath(base, ROOT).replace(os.sep, "/"))
    missing = sorted(found - budgeted)
    assert not missing, (
        "these test directories are in no tier budget, so they can grow without anything noticing: "
        "%s. Add each to a tier in scripts/tier-budgets.json with a ceiling and a reason." % missing)


def test_a_ceiling_is_not_so_far_above_the_count_that_it_can_never_fire(doc):
    """⛔ A BUDGET AT 10x THE COUNT IS A COMMENT. Each ceiling must sit within reach of what the
    tier holds — headroom for the guards a real incident demands, not for a year of accretion.
    ⚠ 60 % is deliberately loose: this fires on a ceiling raised to make room rather than on one
    raised for a measured reason, and the second is a legitimate act."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tier_budget", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for row in mod.measure():
        assert row["budget"] <= row["test_functions"] * 1.6 + 50, (
            "tier %r holds %d test function(s) against a ceiling of %d — that much headroom is a "
            "comment, not a budget, and the tier can grow for months before anything fires"
            % (row["tier"], row["test_functions"], row["budget"]))


def test_every_budget_states_the_reason_for_its_number(doc):
    """A ceiling with no reason cannot be argued with, so the next person to meet it will raise it.
    Each must carry the measurement it came from."""
    for name, spec in doc["tiers"].items():
        why = spec.get("why", "")
        assert len(why) > 120, "tier %r has no stated reason for its ceiling" % name
        assert any(ch.isdigit() for ch in why), (
            "tier %r's reason cites no number, so it is an opinion about the ceiling rather than "
            "the measurement behind it" % name)


def test_the_gate_runs_it():
    """The row must be IN preflight. This repository's most repeated defect is a `--check` that
    exists and that nothing runs — the series-mismatch row, the instrument census, the claim
    coverage census, all three found the same way."""
    src = open(os.path.join(SCRIPTS, "preflight.sh"), encoding="utf-8").read()
    assert "tier_budget.py --check" in src, (
        "preflight no longer runs the tier budget, so the ceilings are prose again")
