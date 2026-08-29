#!/usr/bin/env python3
"""The pre-push half of AUT-PD-144's fix: refuse to push a ledger with a duplicate id.

⛔⛔ WHY THIS EXISTS. AUT-PD-144 measured that `priority.py --write` — step 3 of every cycle's
contract, run before any item can be taken — crashed on the committed trunk with
`ValueError: duplicate ledger ids: AUT-PD-140` because a REBASE performed at push time built a third
tree that no preflight run ever saw: two sessions each allocated the same id from state fetched
before the other's commit, each was individually gated, and the rebase that reconciled them produced
no conflict (the ledger's rows are separate array elements) and no marker. The row's own diagnosis:
"the cheap fix is a pre-push check, not a new test: after any rebase that touched
research-ledger.json, re-run the id guard (0.04 s) and refuse the push on a duplicate."

★ THE CHECK ITSELF ALREADY EXISTED (`ids.duplicate_ids`, exercised by
`tests/test_ids_cannot_collide.py`) and was already correct — AUT-PD-144's own words: "THE GUARD WAS
CORRECT AND WAS SIMPLY NOT RUN AT THE MOMENT THAT MATTERED." What was missing was a check bound to
the PUSH itself rather than to a preflight run that a rebase can outrun. This file is that binding,
kept separate from `ids.py` so it can be invoked as a script from a git hook without importing test
infrastructure.

⚠ THIS CHECKS THE WORKING TREE'S CURRENT `research-ledger.json`, NOT A SPECIFIC REF. A pre-push hook
fires after any local rebase has already rewritten the tree and before the push leaves the machine,
so the file on disk at that moment IS the tree about to be pushed — no ref parsing needed, and this
stays correct across a merge, a rebase or a plain fast-forward alike.

USAGE
    python3 research/autonomy/prepush_ledger_guard.py --check   # exit 0 = clean, 1 = duplicate found
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ids  # noqa: E402

LEDGER = os.path.join(HERE, "research-ledger.json")


def check(ledger_path: str = LEDGER) -> dict:
    """Read `ledger_path` and report any duplicated id. Never raises on a readable file."""
    try:
        with open(ledger_path, encoding="utf-8") as fh:
            entries = json.load(fh).get("entries") or []
    except (OSError, ValueError) as exc:
        # An unreadable ledger buys nothing (CLAUDE.md §4): fail closed, name the cause.
        return {"ok": False, "duplicates": {}, "error": f"cannot read {ledger_path}: {exc}"}
    dupes = ids.duplicate_ids(entries)
    return {"ok": not dupes, "duplicates": dupes, "error": None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 on a duplicate id, 0 if clean")
    parser.add_argument("--ledger", default=LEDGER, help="path to research-ledger.json")
    args = parser.parse_args(argv)

    result = check(args.ledger)
    if result["error"]:
        print(f"[prepush-ledger-guard] {result['error']} — failing closed", file=sys.stderr)
        return 1
    if not result["ok"]:
        print("[prepush-ledger-guard] REFUSED: duplicate ledger id(s) would be pushed: "
              f"{result['duplicates']}", file=sys.stderr)
        print("  This is the exact AUT-PD-144 failure — a rebase at push time built a tree no "
              "preflight run saw. Rename the later row (ids.next_entry_id) and re-run.",
              file=sys.stderr)
        return 1
    if args.check:
        print("[prepush-ledger-guard] OK: no duplicate ledger ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
