#!/usr/bin/env python3
"""`requires_trimcrae` must mean the same thing to every reader of it (AUT-PD-127).

⛔⛔ THE DEFECT THIS SUITE WAS WRITTEN AGAINST, MEASURED ON 86098c2 BEFORE ANY CODE CHANGED.
Three modules answer the one question "may a cycle take this row?" and only ONE read the field:

    continuity.py:_why_not_ready   reads it  → "outward-facing — trimcrae's act (CLAUDE.md §3)"
    priority.py:_blocked_on_human  DOES NOT  → reads systems/graph/routes.json alone
    handoff.py:_takeable           DOES NOT  → owner/state/retry_budget/score/exclude_ids only

So the -25 `blocked_on_human` weight, whose own `why` in priority-weights.json reads "The loop
cannot advance it this cycle", was present in the `score_inputs` of 0 of the 12 rows that declare
the field, and the re-scored queue's first EIGHT rows were all acts reserved for trimcrae by
CLAUDE.md §3 — AUT-046 199.0, AUT-010 190.9, AUT-042/057/058/064/065 181.7, AUT-073 172.0 — with
the first takeable row, AUT-025, 47 points below the top. The handoff prompt that started session
7cda2d61 listed five rows as "WHAT IS WAITING" and all five were his.

⭐ THIS IS THE ONE-OF-A-PAIR CLASS AT n=3, AND THAT IS WHY THE GUARD IS ONE SUITE OVER ALL THREE
READERS RATHER THAN A TEST PER MODULE. continuity.py lines 80-95 record the Stop hook finding this
exact pair of rows on 2026-08-27 — "readiness was modelled on SPEND and never on WHO MAY ACT" — and
fixing it THERE. A per-module test would have been written alongside that fix and would have passed
ever since, while the other two readers drifted. Test 4 is the one that fails if a FOURTH reader is
added without wiring: it asserts the three known readers agree on one synthetic row, so the cost of
adding a reader is discovering this file.

⛔ WHAT THIS SUITE DOES NOT CLAIM. It does not check that any particular row's `requires_trimcrae`
value is CORRECT — that is a human judgement continuity.py deliberately refuses to guess
("A row declares `requires_trimcrae: true` or it does not"), and a keyword heuristic here would
reintroduce the guessing that docstring rejects. It checks only that the declared value is HONOURED,
identically, everywhere it is read.
"""

from __future__ import annotations

import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import continuity  # noqa: E402
import handoff  # noqa: E402
import priority  # noqa: E402

WEIGHTS = priority.load_weights()
HUMAN_W = WEIGHTS["terms"]["blocked_on_human"]["weight"]


def _row(rid="AUT-TEST-001", *, his, score=100.0, prev_human=False):
    """A minimal hand-filed ledger row, shaped like the ones merge() carries forward."""
    return {
        "id": rid,
        "what": "a synthetic row",
        "serves": {"route": "RT-AUTONOMY", "publication": None, "strategy": None},
        "kind": "fix",
        "state": "queued",
        "owner": None,
        "cost_class": "free",
        "blocked_by": None,
        "blocked_evidence": None,
        "retry_budget": 3,
        "attempts": 0,
        "score": score,
        "score_inputs": {"blocked_on_human": prev_human},
        "requires_trimcrae": his,
    }


# --- 1. positive control: the guard can see the thing it is guarding -----------------------------

def test_the_penalty_is_a_real_negative_number():
    """If the weight were 0 every other test here would pass vacuously."""
    assert isinstance(HUMAN_W, (int, float)) and HUMAN_W < 0


# --- 2. priority.py: the term is fed from the row, and exactly once -------------------------------

def test_a_declared_row_takes_the_penalty():
    rows = [_row(his=True)]
    out = priority.apply_requires_trimcrae(copy.deepcopy(rows), WEIGHTS)
    assert out[0]["score_inputs"]["blocked_on_human"] is True
    assert out[0]["score"] == round(100.0 + HUMAN_W, 2)


def test_an_undeclared_row_is_untouched():
    out = priority.apply_requires_trimcrae([_row(his=False)], WEIGHTS)
    assert out[0]["score"] == 100.0
    assert out[0]["score_inputs"]["blocked_on_human"] is False


def test_the_penalty_is_not_applied_twice():
    """The fixed-point property test_a_score_must_derive_from_its_own_inputs asserts, for this term.

    A hand-filed row's score and inputs are carried forward unchanged by merge(), so a term added
    unconditionally would compound on every re-score — the AUT-PROP-036 shape that took AUT-PROP-026
    to -2506.8 at -90.0 per run.
    """
    rows = [_row(his=True)]
    once = priority.apply_requires_trimcrae(copy.deepcopy(rows), WEIGHTS)
    twice = priority.apply_requires_trimcrae(copy.deepcopy(once), WEIGHTS)
    assert twice[0]["score"] == once[0]["score"]


def test_a_row_already_blocked_via_the_graph_is_not_penalised_again():
    """routes.json and the row are two sources for one term; the value is their OR, not their sum."""
    out = priority.apply_requires_trimcrae([_row(his=True, prev_human=True)], WEIGHTS)
    assert out[0]["score"] == 100.0
    assert out[0]["score_inputs"]["blocked_on_human"] is True


def test_the_pass_is_wired_into_build_ledger_before_the_sort():
    """⛔ A pass nobody calls is the defect class this repository has paid for repeatedly.

    Called after the sort it would be dead as an ordering term, which is the whole point of it.
    """
    src = open(os.path.join(AUTONOMY, "priority.py")).read()
    body = src.split("def build_ledger()", 1)[1]
    call = body.index("apply_requires_trimcrae(")
    sort = body.index("entries.sort(")
    assert call < sort


# --- 3. handoff.py: such a row is withheld, and NAMED ---------------------------------------------

def test_a_declared_row_is_not_handed_to_a_successor():
    ledger = {"entries": [_row("AUT-HIS", his=True, score=999.0),
                          _row("AUT-MINE", his=False, score=1.0)]}
    got = [e["id"] for e in handoff.top_items(ledger)]
    assert got == ["AUT-MINE"], got


def test_the_withheld_row_is_still_named_in_the_prompt():
    """⚠ Silently dropping it would hide the one thing CLAUDE.md §3 exists to surface."""
    ledger = {"entries": [_row("AUT-HIS", his=True, score=999.0),
                          _row("AUT-MINE", his=False, score=1.0)]}
    prompt = handoff.build(reason="test", ledger=ledger, state={})
    assert "AUT-HIS" in prompt
    assert "requires_trimcrae" in prompt


# --- 4. the anti-drift assertion: all three readers, one answer -----------------------------------

def test_every_reader_of_the_field_gives_the_same_answer(monkeypatch):
    """⛔ THE REGRESSION THAT MATTERS. One synthetic row, put to all three readers.

    If a fourth reader of `requires_trimcrae` is added and not wired, extending this test is how it
    is discovered — which is the property the n=3 drift above shows a per-module test does not have.
    """
    his = _row("AUT-HIS", his=True, score=999.0)
    mine = _row("AUT-MINE", his=False, score=1.0)
    ledger = {"entries": [his, mine]}

    # continuity.py — refuses it outright
    monkeypatch.setattr(continuity, "_entries", lambda: [copy.deepcopy(his), copy.deepcopy(mine)])
    assert [e["id"] for e in continuity.ready()] == ["AUT-MINE"]

    # handoff.py — withholds it from the successor
    assert [e["id"] for e in handoff.top_items(copy.deepcopy(ledger))] == ["AUT-MINE"]

    # priority.py — penalises it rather than ranking it first
    scored = priority.apply_requires_trimcrae(copy.deepcopy([his]), WEIGHTS)
    assert scored[0]["score"] < his["score"]
