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


def count_dir(rel):
    """(files, test functions) under a tests directory, by AST. (0, 0) if it is not there."""
    path = os.path.join(ROOT, rel)
    if not os.path.isdir(path):
        return 0, 0
    files = functions = 0
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
    return files, functions


def measure():
    with open(BUDGETS, encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = []
    for name, spec in sorted(doc["tiers"].items()):
        files = functions = 0
        for rel in spec["directories"]:
            f, n = count_dir(rel)
            files += f
            functions += n
        rows.append({
            "tier": name,
            "directories": spec["directories"],
            "files": files,
            "test_functions": functions,
            "budget": spec["max_test_functions"],
            "over": functions > spec["max_test_functions"],
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
            mark = "OVER " if r["over"] else "ok   "
            print("   %s %-22s %5d/%-5d test function(s) in %d file(s)"
                  % (mark, r["tier"], r["test_functions"], r["budget"], r["files"]))
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
