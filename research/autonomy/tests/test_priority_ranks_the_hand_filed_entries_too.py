#!/usr/bin/env python3
"""The ranker must survive the ledger it actually ranks (AUT-PD-019).

⛔⛔ THE DEFECT: `priority.py` — the thing that decides what the loop works on next — exited 1 on
every invocation against the committed ledger. `KeyError: 'score_inputs'`, at the line that records
the evidenced-block penalty. `build_entries` writes `score_inputs` only for the rows it DERIVES from
`systems/graph`; `merge()` deliberately carries hand-filed rows through untouched, because the
ledger's own `_role` says a session may add an entry the graph cannot express. Forty-seven of 124
entries are hand-filed, and the penalty loop indexed the key on all of them.

⭐ NOTHING CAUGHT IT BECAUSE NOTHING RAN IT. `priority.py` appears in no preflight gate and no
workflow, so a dead ranker looked exactly like a quiet one — the same finding as AUT-PD-018 the same
day, and as `scripts/tests` before that. These tests are that wiring: they are the only thing that
executes the ranker on the real committed ledger.

★ THE INVARIANT: a hand-filed entry is HAND-SCORED, not unscorable. It carries a `score` its filer
typed and a `_score_basis` in prose; what it does not carry is the derived scorer's audit trail. So
the fix may never fabricate one — an entry with a full set of zeroed inputs looks computed, and the
arithmetic printed beside it would be arithmetic nobody did (CLAUDE.md §4).
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import priority as P  # noqa: E402

LEDGER = os.path.join(os.path.dirname(HERE), "research-ledger.json")


def _weights():
    return P.load_weights() if hasattr(P, "load_weights") else None


@pytest.fixture
def weights():
    w = _weights()
    if w is None:
        pytest.skip("priority.py exposes no weights loader under this name")
    return w


def test_the_ranker_runs_against_the_committed_ledger():
    """⛔⛔ THE REGRESSION, AT FULL SCALE AND ON REAL DATA. Not a fixture: the defect was a property
    of the ledger this repository actually carries, and a synthetic two-row ledger would have passed
    on the broken code because both rows would have been derived."""
    assert P.main([]) == 0, (
        "priority.py exited non-zero on the committed ledger. It is the ranker the cycle contract "
        "uses at step 3 to choose what to work on; when it dies, the loop picks work by hand and "
        "nothing says so.")


def test_a_hand_filed_entry_with_an_evidenced_block_does_not_kill_the_ranker(weights):
    """⛔ THE EXACT CRASH. A hand-filed row — no `score_inputs`, because nothing derived it — that
    also records the evidence for its own block. That combination is what reached line 423."""
    hand = {"id": "AUT-PROP-999", "score": 100.0, "blocked_evidence": "measured: the host refused",
            "serves": {"route": "RT-X"}, "kind": "process_defect"}
    out = P.apply_session_penalties([hand], weights)
    assert out[0]["score"] < 100.0, "the evidenced-block penalty did not fire"
    assert out[0]["score_inputs"] == {"blocked_with_evidence": True}, (
        "the fix fabricated a full inputs dict for a row nothing computed. An entry that LOOKS "
        "scored by the deriver, and is not, is a populated field that is not a measured one.")


def test_a_hand_filed_prerequisite_of_a_hand_filed_parent_does_not_kill_it_either(weights):
    """⚠ THE SIBLING LINE, WHICH WOULD HAVE BEEN THE NEXT CRASH. `paper-hardening` §8b.2 measured six
    of eleven list-scoped fixes missing a sibling, three of them named in the fix's own comment."""
    parent = {"id": "AUT-PROP-998", "score": 80.0, "serves": {"route": "RT-X"}, "kind": "fix"}
    child = {"id": "AUT-PROP-997", "score": 10.0, "prerequisite_of": "AUT-PROP-998",
             "serves": {"route": "RT-X"}, "kind": "fetch"}
    out = P.apply_session_penalties([parent, child], weights)
    by = {e["id"]: e for e in out}
    assert by["AUT-PROP-997"]["score"] > by["AUT-PROP-998"]["score"], (
        "a prerequisite must sort immediately above what it unblocks, or the work that would clear "
        "a block is invisible to the driver")


def test_the_ledger_still_holds_hand_filed_entries_without_score_inputs():
    """★ THE PRECONDITION, PINNED. If a later change starts writing `score_inputs` onto every entry,
    the two tests above stop exercising the branch they were written for and go green for the wrong
    reason — the same trap that let `in_progress` be dropped from the continuity suite's OPEN_STATES
    while all twelve tests passed."""
    with open(LEDGER, encoding="utf-8") as fh:
        entries = json.load(fh)["entries"]
    without = [e["id"] for e in entries if "score_inputs" not in e]
    assert without, (
        "every ledger entry now carries `score_inputs`, so the hand-filed branch this suite guards "
        "is no longer reachable from real data. Either the deriver now writes them (then say so "
        "here and drop this file) or the fixtures above are the only coverage left.")
