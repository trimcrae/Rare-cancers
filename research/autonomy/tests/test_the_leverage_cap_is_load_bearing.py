"""`blocker_leverage_cap` is the only thing standing between this ranker and "most-blocked wins".

⛔ THE GAP THIS CLOSES, MEASURED 2026-09-02. `grep -rn blocker_leverage_cap --include=*.py` over the
whole repository returned ONE hit — `priority.py:318`, the line that reads it — and no test anywhere
asserted anything about it. That is the `subagent_width` shape CLAUDE.md §1 records verbatim: a
constant that governs a real behaviour with nothing measuring it, so compliance is luck.

★ AND IT IS LOAD-BEARING RATHER THAN COSMETIC, measured on the committed graph the same day.
`_blocker_leverage`'s RAW counts span 0-48 across the 77 routes (`BLK-NO-EMC-DATA` alone is inherited
by 38 of them). Capped at 6 the distribution is {0: 12, 2: 2, 4: 1, 6: 62} — 62 of 77 routes sit at
the ceiling and the term reads as a near-binary flag. Removing the cap moves 295 of the 361 ledger
rows by more than five places and lifts `AUT-053` from #268 to #30 on score alone: the queue inverts
toward whichever route inherits the most widely-shared blocker, which is the opposite of a priority.
⚠ So the weights file's `why` — "the count does the work" — describes the UNCAPPED term. The cap is
what makes the small per-route weight safe, and these tests hold it.

⭐ THE COUNT DELIBERATELY INCLUDES PEERS NOTHING CAN TAKE, AND THE OBVIOUS "FIX" IS REFUSED HERE.
Restricting the peer set to live, takeable routes was measured on the committed tree the same day:
it changes the score of 18 of 361 rows, every one of them a DEMOTION, every one already ranked
#250-#316 of 361 — the top 20 is byte-identical — and among the demoted is `AUT-019`, a
`blocked_without_evidence_becomes_a_check` re-test row whose whole purpose is retiring a blocker.
An inert correction that points the wrong way on the one row class the term exists to promote is not
a correction. `test_every_peer_counts_including_the_ones_nothing_can_take` pins that reading so a
future session has to confront the measurement rather than re-derive the tempting edit.
"""

from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import priority  # noqa: E402

W = json.load(open(os.path.join(os.path.dirname(HERE), "priority-weights.json"), encoding="utf-8"))


def _route(rid, blockers, **state):
    """A route skeleton carrying only what `_blocker_leverage` and `build_entries` read."""
    return {
        "id": rid,
        "blockers_inherited": list(blockers),
        "state": dict(state) or {},
        "closure_kind": "open",
        "publication": {},
        "next": {},
        "timing": {},
        "grade": {},
        "readiness": {},
    }


def test_the_cap_binds_on_the_committed_graph():
    """A ceiling nothing reaches is decoration. On the committed graph this one is reached."""
    routes = priority._load("routes.json")
    raw = priority._blocker_leverage(routes)
    cap = W["blocker_leverage_cap"]
    over = [rid for rid, n in raw.items() if n > cap]
    assert over, (
        f"no route's raw blocker leverage exceeds blocker_leverage_cap={cap}, so the cap governs "
        "nothing on the committed graph — either the graph collapsed or the cap was raised past "
        "the point where it is doing any work"
    )
    assert max(raw.values()) > 2 * cap, (
        "the cap is meant to be the thing that stops a widely-inherited blocker dominating the "
        f"term; max raw leverage is {max(raw.values())} against a cap of {cap}"
    )


def test_the_cap_is_applied_to_the_score_and_not_merely_read():
    """Raising the cap must move a real score, or `min(..., cap)` has been dropped."""
    routes = priority._load("routes.json")
    raw = priority._blocker_leverage(routes)
    cap = W["blocker_leverage_cap"]
    target = max(raw, key=lambda rid: raw[rid])
    assert raw[target] > cap

    tight = copy.deepcopy(W)
    tight["blocker_leverage_cap"] = 1
    loose = copy.deepcopy(W)
    loose["blocker_leverage_cap"] = raw[target]

    def _lever_of(weights):
        for entry in priority.build_entries(weights):
            if entry["serves"]["route"] == target:
                return entry["score_inputs"]["blocker_leverage"], entry["score"]
        raise AssertionError(f"{target} produced no derived entry")

    tight_lever, tight_score = _lever_of(tight)
    loose_lever, loose_score = _lever_of(loose)
    assert tight_lever == 1, f"cap=1 should clamp {target} to 1, got {tight_lever}"
    assert loose_lever == raw[target], (
        f"cap={raw[target]} should let {target} through uncapped, got {loose_lever}"
    )
    weight = W["terms"]["blocker_leverage"]["weight"]
    assert round(loose_score - tight_score, 2) == round(weight * (raw[target] - 1), 2), (
        "the capped count does not reach the weighted sum — the term is read and discarded"
    )


def test_a_route_does_not_count_itself():
    routes = [_route("RT-A", ["BLK-X"]), _route("RT-B", ["BLK-X"])]
    assert priority._blocker_leverage(routes) == {"RT-A": 1, "RT-B": 1}


def test_leverage_counts_peer_routes_not_the_blockers_they_share():
    """Three blockers, no peers, is leverage 0 — the term measures reach, not blockedness."""
    routes = [_route("RT-A", ["BLK-X", "BLK-Y", "BLK-Z"]), _route("RT-B", [])]
    assert priority._blocker_leverage(routes)["RT-A"] == 0


def test_two_shared_blockers_do_not_double_count_one_peer():
    routes = [_route("RT-A", ["BLK-X", "BLK-Y"]), _route("RT-B", ["BLK-X", "BLK-Y"])]
    assert priority._blocker_leverage(routes)["RT-A"] == 1


def test_every_peer_counts_including_the_ones_nothing_can_take():
    """⛔ DELIBERATE, AND THE REFUTATION OF THE OBVIOUS FIX IS IN THIS MODULE'S DOCSTRING."""
    routes = [
        _route("RT-LIVE", ["BLK-X"]),
        _route("RT-DEAD", ["BLK-X"], work_state="dead", status="closed"),
        _route("RT-PARKED", ["BLK-X"], status="parked"),
    ]
    assert priority._blocker_leverage(routes)["RT-LIVE"] == 2, (
        "a peer that is dead or parked still counts: the term prices the blocker's reach across "
        "the graph, and a route's recorded status is not evidence it can never move"
    )
