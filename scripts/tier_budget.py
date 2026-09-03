#!/usr/bin/env python3
"""What each preflight tier is allowed to cost, counted rather than hoped.

⛔⛔ THE FAILURE THIS EXISTS FOR IS ACCRETION, AND NOBODY EVER DECIDED IT. On 2026-09-02 the
publication gate took 9.7 minutes to check a 4,695-word paper. Nothing in it was wrong; it had
simply grown, one justified test at a time, until:

    gate 13 (the commit loop)   789 -> 1,030 -> 1,119 tests over ~10 days
    modalities                  8,212 tests, 72 % of every publication run, 0 failures in 8 runs
    the whole repository        2,973 tests for one six-page paper

★ EVERY ONE OF THOSE TESTS WAS JUSTIFIED BY A REAL INCIDENT. That is exactly why the total went
unexamined: each addition was correct, and the sum was never anyone's decision. trimcrae, 2026-09-02:
"1000 pure logic tests for a 6 page paper seems insane" — and it took a human noticing, which is the
definition of a rule nothing measures.

★★ SO THE BUDGET IS A COMMITTED NUMBER AND EXCEEDING IT IS A DECISION SOMEBODY TAKES. Adding a test
is free; adding the 200th test to a tier that already has 1,100 is a change to what every commit
costs, and this makes that visible at the commit that does it rather than at the month that notices.
`scripts/tier-budgets.json` carries each ceiling WITH ITS REASON, and raising one is a governed,
declared act like any other bar change.

⛔ IT COUNTS STATICALLY, SO IT IS FREE AND DETERMINISTIC. `pytest --collect-only` over the modalities
suite is ~20 s — too slow to sit in the loop this file exists to keep fast, and the irony would be
total. An AST walk over the same files is milliseconds and cannot vary with plugins, ordering or
parametrize expansion. ⚠ IT THEREFORE COUNTS TEST FUNCTIONS, NOT COLLECTED TESTS: a parametrized
function is one here and many to pytest. The budget is a ceiling on what the repository ASKS FOR,
which is the thing a human controls.

Usage:
    python3 scripts/tier_budget.py            # report every tier against its budget
    python3 scripts/tier_budget.py --check    # exit 1 if any tier is over
    python3 scripts/tier_budget.py --json
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUDGETS = os.path.join(HERE, "tier-budgets.json")


def _shadowed(tree):
    """Test names defined twice in one namespace — module body, or one class body.

    ⛔⛔ A SHADOWED TEST DOES NOT FAIL, IT CEASES TO EXIST. Python binds a module-level name once, so
    the second `def test_x` silently replaces the first and pytest never sees it. Nothing goes red,
    nothing is reported skipped, and no coverage number moves — the guard is simply gone.
    ⚠ MEASURED 2026-09-03, not reasoned: `systems/tests/test_autonomy_health.py` held 77 `def test_`
    and `pytest --collect-only -q` reported 75. The two that died were the anti-defeat guard and the
    one-fact-one-place guard on `cycles_are_sized` — the row CLAUDE.md §6 added precisely because
    the session-shape rule was governed by nothing — killed by a name collision with the
    `fanout_is_governed` pair a hundred lines below, which guard a different condition entirely.
    ★ THE CHECK BELONGS HERE BECAUSE IT IS THIS TOOL'S OWN NUMBER THAT IS OTHERWISE A LIE. The
    budget counts what the repository ASKS FOR; a shadowed function is paid for out of the ceiling
    and measures nothing, so the tier was standing at 1400/1400 with two of them inside it. This
    file's `_what_this_does_not_measure` says the budget says nothing about whether a test is GOOD,
    and that still holds — whether a test RUNS is a different question, and it is the one that makes
    the count true.
    """
    out = []
    for scope in [tree] + [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        seen = {}
        for node in scope.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name.startswith("test_"):
                seen.setdefault(node.name, []).append(node.lineno)
        out += [(name, lines) for name, lines in seen.items() if len(lines) > 1]
    return out


def count_dir(rel):
    """(files, test functions, shadowed) under a tests directory, by AST. Zeros if it is not there."""
    path = os.path.join(ROOT, rel)
    if not os.path.isdir(path):
        return 0, 0, []
    files = functions = 0
    shadowed = []
    for entry in sorted(os.listdir(path)):
        if not (entry.startswith("test_") and entry.endswith(".py")):
            continue
        files += 1
        try:
            with open(os.path.join(path, entry), encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError):
            # ⛔ AN UNPARSEABLE TEST FILE IS NOT ZERO TESTS. Counting it as zero would let a broken
            # file buy headroom under the ceiling, which is the wrong direction for a budget.
            functions += 1
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name.startswith("test_"):
                functions += 1
        shadowed += [(os.path.join(rel, entry), name, lines) for name, lines in _shadowed(tree)]
    return files, functions, shadowed


def measure():
    with open(BUDGETS, encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = []
    for name, spec in sorted(doc["tiers"].items()):
        files = functions = 0
        shadowed = []
        for rel in spec["directories"]:
            f, n, sh = count_dir(rel)
            files += f
            functions += n
            shadowed += sh
        rows.append({
            "tier": name,
            "directories": spec["directories"],
            "files": files,
            "test_functions": functions,
            "budget": spec["max_test_functions"],
            "over": functions > spec["max_test_functions"],
            "shadowed": [{"file": f, "name": n, "lines": l} for f, n, l in shadowed],
            "why": spec.get("why", ""),
        })
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = measure()
    if a.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            mark = "SHADOW" if r["shadowed"] else ("OVER " if r["over"] else "ok   ")
            print("   %s %-22s %5d/%-5d test function(s) in %d file(s)"
                  % (mark, r["tier"], r["test_functions"], r["budget"], r["files"]))
            for sh in r["shadowed"]:
                print("         %s: %s defined at lines %s — only the LAST one runs"
                      % (sh["file"], sh["name"], sh["lines"]))
    shadowed = [r for r in rows if r["shadowed"]]
    if shadowed and a.check:
        print("", file=sys.stderr)
        for r in shadowed:
            for sh in r["shadowed"]:
                print("::error::%s defines %s at lines %s. Python binds the name once, so every "
                      "definition but the last is REPLACED — it does not fail, it stops existing, "
                      "and it is still paid for out of tier %r's ceiling. Rename it after the thing "
                      "it actually guards."
                      % (sh["file"], sh["name"], sh["lines"], r["tier"]), file=sys.stderr)
        return 1
    over = [r for r in rows if r["over"]]
    if over and a.check:
        print("", file=sys.stderr)
        for r in over:
            print("::error::tier %r is at %d test function(s) against a budget of %d. Adding a test "
                  "is free; adding this one changes what every run of that tier costs. Either it "
                  "belongs in a cheaper tier, or something in the tier has stopped earning its "
                  "place, or the ceiling is genuinely wrong — raise it in scripts/tier-budgets.json "
                  "WITH the measurement that justifies it, and declare it. Budget's stated reason: %s"
                  % (r["tier"], r["test_functions"], r["budget"], r["why"]), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
