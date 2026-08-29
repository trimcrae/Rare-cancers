#!/usr/bin/env python3
"""The pre-push half of AUT-PD-144's fix (research/autonomy/prepush_ledger_guard.py).

⛔⛔ THE DEFECT THIS GUARDS AGAINST: a rebase performed at push time can build a tree that no
preflight run ever saw. Two sessions each allocated ledger id `AUT-PD-140` from state fetched before
the other's commit; the rebase that reconciled them produced no conflict (the ledger's rows are
separate array elements in a JSON array, so a rebase merges the file cleanly) and no marker, and the
duplicate reached `origin/main`. `priority.py --write` — step 3 of every cycle's contract — then
crashed for every session until a human renamed the row. The row's own diagnosis named the fix: "a
pre-push check... re-run the id guard and refuse the push on a duplicate."

★ THIS FILE TESTS THE GUARD LOGIC DIRECTLY (`check()`), NOT THE GIT HOOK MECHANISM ITSELF. Whether
`core.hooksPath` is actually wired up is an environment fact `scripts/dev-setup.sh` sets and this
suite cannot observe portably (CI's checkout may not share the sandbox's git config) — what it CAN
pin, offline and deterministically, is that the check function correctly distinguishes a clean
ledger from a duplicated one, on the same `ids.duplicate_ids` the rest of the loop already trusts.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import prepush_ledger_guard as G  # noqa: E402

LEDGER = os.path.join(os.path.dirname(HERE), "research-ledger.json")


def _write_ledger(tmp_path, entries):
    path = os.path.join(str(tmp_path), "research-ledger.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"entries": entries}, fh)
    return path


def test_the_guard_runs_clean_against_the_committed_ledger():
    """⛔⛔ THE REGRESSION, AT FULL SCALE. The committed ledger must never itself carry a duplicate
    id — that is precisely the invariant `priority.py --write` needs to run at all."""
    result = G.check(LEDGER)
    assert result["ok"], f"the committed ledger has a duplicate id: {result['duplicates']}"


def test_a_clean_two_row_ledger_passes(tmp_path):
    path = _write_ledger(tmp_path, [{"id": "AUT-001"}, {"id": "AUT-002"}])
    result = G.check(path)
    assert result["ok"] is True
    assert result["duplicates"] == {}


def test_the_exact_aut_pd_144_shape_is_refused(tmp_path):
    """Two sessions' rebase-then-push landed the SAME id twice as separate array elements — no JSON
    merge conflict, no marker. Reproduce that shape directly."""
    path = _write_ledger(tmp_path, [
        {"id": "AUT-PD-140", "what": "filed by session A"},
        {"id": "AUT-PD-140", "what": "filed by session B, from stale state"},
        {"id": "AUT-PD-141", "what": "unrelated, unaffected"},
    ])
    result = G.check(path)
    assert result["ok"] is False
    assert result["duplicates"] == {"AUT-PD-140": 2}


def test_an_unreadable_ledger_fails_closed(tmp_path):
    """CLAUDE.md §4: an absent reading is not a reading of absence. A guard that cannot read the
    ledger must refuse, not wave the push through."""
    missing = os.path.join(str(tmp_path), "does-not-exist.json")
    result = G.check(missing)
    assert result["ok"] is False
    assert result["error"]


def test_main_exits_nonzero_on_a_duplicate(tmp_path, capsys):
    path = _write_ledger(tmp_path, [{"id": "AUT-X"}, {"id": "AUT-X"}])
    rc = G.main(["--check", "--ledger", path])
    assert rc == 1
    out = capsys.readouterr()
    assert "REFUSED" in out.err
    assert "AUT-X" in out.err


def test_main_exits_zero_on_a_clean_ledger(tmp_path, capsys):
    path = _write_ledger(tmp_path, [{"id": "AUT-X"}, {"id": "AUT-Y"}])
    rc = G.main(["--check", "--ledger", path])
    assert rc == 0
