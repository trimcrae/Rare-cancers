#!/usr/bin/env python3
"""A ROUTE'S CONCLUSION MUST NOT BE BORN AS QUEUED WORK (AUT-PD-075).

⛔⛔ THE DEFECT, MEASURED BEFORE ANY CODE WAS CHANGED. `priority.build_entries` invented the derived
row's `state` from one field, `next.blocked_on`, which 11 of 77 routes carry. Every other route was
therefore born `queued` no matter what the graph recorded about it, and the loop's ready list
offered rows whose own text says there is nothing to do. Counted on the corrected ranking
(2026-08-28, CYC-0053-3217966b, after the additive-score fix a660303) by classifying all 77
`next.best_next_action` texts by hand:

    ACTION        38   a step a session can execute now
    CONCLUSION    23   "Nothing. Cite the closure" · "Report it as a closed line" · "Treat as
                       landscape context; the ex-vivo result is banked and needs no further lookup"
    REGISTRATION  16   "Keep registered for automatic re-grade when EMC expression data lands"

39 of 77 — HALF the derived queue — and 36 of those 39 were `queued`. AUT-013 was the top-scoring
row in the entire ledger at 172.0.

⭐ THE DISCRIMINATOR IS A COMMITTED FIELD, NOT A PHRASE. `state.status` is a closed controlled
vocabulary (systems/CONVENTIONS.md §4.1, enum pinned in systems/schema/research-object.schema.json)
whose own definitions say the route has no takeable step: `parked` = "failed with today's tools;
has a named TECH-* to reopen it", `closed` = "conclusively unworkable", `delegated` = "someone
else's to answer", `superseded` = "replaced by another object, which is named".

⛔ MATCHING THE ENGLISH WAS THE TEMPTING FIX AND IS REFUSED. A `what` grep for "no further lookup"
or "closed line" is a guard the next re-wording defeats in silence — the failure family this
repository has already paid for (AUT-PD-013's fan-out key; AUT-PROP-013's typed ids). Test 7 pins
that no such literal is in the module.

WHAT EACH TEST HOLDS DOWN
  1   the mapping itself, on the real graph: every not-takeable status derives `parked`.
  2   the inverse, on the real graph: a takeable status is NEVER parked. A guard that parks live
      work is worse than the defect it replaces (CLAUDE.md §0).
  3   the state NAMES what it waits on, and says None honestly when the graph names nothing.
  4   `parked_on` is written on EVERY row including as None — the `merge()` resurrection bug.
  5   the clamp cannot re-queue a parked row through the blocked-without-evidence door.
  6   AUT-PD-051: a parked row is never disposed of, and a session's `done` still wins.
  7   the discriminator is a field read, not a prose match.
  8   the ONE-OF-A-PAIR check: every reader of the ledger's offer list excludes `parked`. A writer
      emitting a state the readers do not honour would fix nothing at all.
"""

from __future__ import annotations

import copy
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUTONOMY))
sys.path.insert(0, AUTONOMY)

import priority  # noqa: E402

ROUTES = os.path.join(REPO, "systems", "graph", "routes.json")
OBJECT_SCHEMA = os.path.join(REPO, "systems", "schema", "research-object.schema.json")


@pytest.fixture(scope="module")
def routes():
    with open(ROUTES, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def entries():
    return priority.build_entries()


def _route_of(entries_by_route, route_id):
    return entries_by_route[route_id]


@pytest.fixture(scope="module")
def by_route(entries):
    return {e["serves"]["route"]: e for e in entries}


# ---------------------------------------------------------------------------------------------
# 1-2 · the mapping, both directions, on the committed graph
# ---------------------------------------------------------------------------------------------

def test_the_not_takeable_statuses_are_all_real_values_of_the_graphs_own_enum():
    """⛔ A TYPO WOULD DISABLE THE FIX IN SILENCE. The set is written here as strings; the enum it
    must be a subset of is pinned in the schema. A value that is not in the enum can never match a
    route, so the generator would go back to queueing everything with nothing going red."""
    with open(OBJECT_SCHEMA, encoding="utf-8") as fh:
        schema = json.load(fh)
    ref = schema["$defs"]["state"]["properties"]["status"]["$ref"]
    assert ref == "#/$defs/status", f"the status ref moved to {ref!r}"
    enum = set(schema["$defs"]["status"]["enum"])
    assert priority.NOT_TAKEABLE_STATUSES <= enum, (
        f"{sorted(priority.NOT_TAKEABLE_STATUSES - enum)} is not a value systems/graph can hold — "
        "the discriminator would never fire"
    )


def test_every_route_the_graph_has_stood_down_derives_a_parked_row(routes, by_route):
    """The forward mapping, on real data — not a fixture."""
    offenders = []
    for route in routes:
        status = (route.get("state") or {}).get("status")
        if status not in priority.NOT_TAKEABLE_STATUSES:
            continue
        if (route.get("next") or {}).get("blocked_on"):
            continue  # the named exception, pinned by its own test below
        row = by_route[route["id"]]
        if row["state"] != priority.PARKED_STATE:
            offenders.append(f"{route['id']} status={status} derived state={row['state']}")
    assert not offenders, (
        "a route the graph records as not takeable was still born as queued work:\n  "
        + "\n  ".join(offenders)
    )
    parked = [e for e in by_route.values() if e["state"] == priority.PARKED_STATE]
    assert parked, "no route in the committed graph derived a parked row — the fix is inert"


def test_a_route_with_a_takeable_status_is_never_parked(routes, by_route):
    """⛔ THE DIRECTION THAT MATTERS MOST. A missed row keeps the status quo; a FALSE park hides a
    live route from the queue, which is CLAUDE.md §0's named failure. This is why the discriminator
    is `state.status` alone: adding `timing.recommendation in {monitor, wait, closed}` raised recall
    from 0.72 to 0.87 and doubled the false parks from 4 to 9, measured against the hand
    classification of all 77 next-action texts on 2026-08-28.

    ⚠ AND THE STATUSES ARE WRITTEN OUT HERE RATHER THAN DERIVED FROM
    `priority.NOT_TAKEABLE_STATUSES`. Reading the module's own set would make this test a tautology
    — widening the set would widen the test with it and nothing would go red. Measured: the first
    version of this test did exactly that, and mutation M2 (adding `ready` to the set, which parks
    18 more routes including the top-scoring live one) SURVIVED it. These three literals come from
    systems/CONVENTIONS.md §4.1 and change only when a human changes that table.
    """
    TAKEABLE = {
        "active",   # "being worked on now"
        "ready",    # "nothing blocks it; not yet started"
        "blocked",  # "at least one open BLK-*" — and CLAUDE.md §0: usually a $0 re-test, never dead
    }
    with open(OBJECT_SCHEMA, encoding="utf-8") as fh:
        enum = set(json.load(fh)["$defs"]["status"]["enum"])
    assert TAKEABLE | priority.NOT_TAKEABLE_STATUSES == enum, (
        "the route status vocabulary changed; a new value is neither classified takeable nor "
        f"not-takeable: {sorted(enum ^ (TAKEABLE | priority.NOT_TAKEABLE_STATUSES))}"
    )
    offenders = []
    for route in routes:
        status = (route.get("state") or {}).get("status")
        if status not in TAKEABLE:
            continue
        row = by_route[route["id"]]
        if row["state"] == priority.PARKED_STATE:
            offenders.append(f"{route['id']} status={status} was parked anyway")
    assert not offenders, "\n  ".join(["live routes were parked:"] + offenders)


def test_a_blocker_on_the_next_step_outranks_the_routes_status(routes, by_route):
    """⛔ THE ORDER OF THE TWO INPUTS, AND IT IS NOT THE ONE WRITTEN FIRST. `state.status` describes
    the ROUTE; `next.blocked_on` names a blocker on THE NEXT STEP. Clamp 3 turns an unevidenced
    blocker into a FREE RE-TEST, because CLAUDE.md §0 records that most blocked rows are waiting on
    a $0 observation — and for a route parked pending an external dataset, that re-test IS the
    observation its registration is waiting on. Parking first suppressed it; found by
    systems/tests/test_autonomy_priority.py's clamp-3 test going red on RT-SYNLETH-DEP."""
    both = [r for r in routes
            if (r.get("state") or {}).get("status") in priority.NOT_TAKEABLE_STATUSES
            and (r.get("next") or {}).get("blocked_on")]
    if not both:
        pytest.skip("no route in the committed graph is both stood down and blocked on its next step")
    for route in both:
        row = by_route[route["id"]]
        assert row["state"] != priority.PARKED_STATE, (
            f"{route['id']} names {(route['next'] or {}).get('blocked_on')} on its next step and was "
            "parked anyway — the free re-test of that block is now suppressed"
        )
        assert row["parked_on"] is None and row["parked_by_graph_status"] is None, (
            f"{route['id']} is not parked but carries the park fields"
        )


# ---------------------------------------------------------------------------------------------
# 3-4 · the state NAMES what it waits on, and the field cannot go stale
# ---------------------------------------------------------------------------------------------

def test_a_parked_row_names_what_would_reopen_it_or_says_none_honestly(routes, by_route):
    """⭐ A bare `parked` is the same unanswered question in a new costume (CLAUDE.md §4). The
    condition is read from the two registers the graph already keeps, and a `closed` route that
    legitimately has neither gets None rather than an invented trigger."""
    for route in routes:
        row = by_route[route["id"]]
        if row["state"] != priority.PARKED_STATE:
            continue
        expected = sorted(set(list((route.get("timing") or {}).get("revisit_trigger") or [])
                               + list(route.get("revival_trigger") or []))) or None
        assert row["parked_on"] == expected, (
            f"{route['id']}: parked_on {row['parked_on']!r} is not what the graph records ({expected!r})"
        )
        assert row["parked_by_graph_status"] == (route.get("state") or {}).get("status")
    named = [e for e in by_route.values()
             if e["state"] == priority.PARKED_STATE and e["parked_on"]]
    assert named, "every parked row came back with no reopening condition at all — check parked_on()"


def test_the_park_fields_are_written_on_every_row_so_merge_cannot_resurrect_a_stale_one():
    """⛔⛔ THE BUG THIS PREVENTS IS IN `merge()`, NOT HERE. Its last loop is
    `for key, value in old_entry.items(): entry.setdefault(key, value)` — forward-compat, so a key
    the generator does not know is never dropped. A key the generator OMITS on a later run is
    therefore restored from the stale row, so a route that leaves NOT_TAKEABLE_STATUSES would keep
    a `parked_on` naming a condition that no longer applies. The fields must always be present."""
    entries = priority.build_entries()
    for e in entries:
        assert "parked_on" in e, f"{e['id']} omits parked_on — merge() would resurrect the old value"
        assert "parked_by_graph_status" in e, f"{e['id']} omits parked_by_graph_status"
        if e["state"] != priority.PARKED_STATE:
            assert e["parked_on"] is None and e["parked_by_graph_status"] is None, (
                f"{e['id']} is {e['state']} but carries park fields {e['parked_on']!r}"
            )

    # And the resurrection itself, exercised: a prior ledger carrying park fields must not push
    # them back onto a row the generator has since re-derived as queued.
    fresh = [e for e in entries if e["state"] == "queued"][0]
    stale = copy.deepcopy(fresh)
    stale["_derived"] = True
    stale["state"] = priority.PARKED_STATE
    stale["parked_on"] = ["TECH-NEVER"]
    stale["parked_by_graph_status"] = "parked"
    merged = priority.merge(copy.deepcopy(entries), {"entries": [stale]})
    row = [e for e in merged if e["serves"]["route"] == fresh["serves"]["route"]][0]
    assert row["parked_on"] is None, "merge() resurrected a stale parked_on"
    assert row["state"] == "queued", "merge() resurrected a stale parked state"


# ---------------------------------------------------------------------------------------------
# 5-6 · the two ways a parked row could be undone
# ---------------------------------------------------------------------------------------------

def test_the_blocked_without_evidence_clamp_cannot_re_queue_a_parked_row():
    """That clamp exists because most `blocked` rows wait on a $0 observation (CLAUDE.md §0), and
    it rewrites such a row into a queued free re-test. A parked row is a different animal — the
    graph has stood the route down — and it must not be swept back in through that door."""
    weights = priority.load_weights()
    rows = [
        {"id": "AUT-P", "state": priority.PARKED_STATE, "kind": "negative", "score": 1.0,
         "blocked_by": ["BLK-X"], "blocked_evidence": None, "cost_class": "free",
         "what": "Nothing. Cite the closure.", "score_inputs": {"live": False}},
        {"id": "AUT-B", "state": "blocked", "kind": "negative", "score": 1.0,
         "blocked_by": ["BLK-X"], "blocked_evidence": None, "cost_class": "free",
         "what": "do the thing", "score_inputs": {"live": False}},
    ]
    out = {e["id"]: e for e in priority.apply_clamps(rows, weights)}
    assert out["AUT-P"]["state"] == priority.PARKED_STATE, "the clamp re-queued a parked row"
    assert out["AUT-P"]["what"].startswith("Nothing."), "the clamp rewrote a parked row's text"
    assert out["AUT-B"]["state"] == "queued", "the clamp stopped doing its own job"


def test_a_parked_row_is_stood_down_not_disposed_of(by_route):
    """⛔ AUT-PD-051: an artifact on the trunk is not the same as the item being finished, and a
    report is not a closure. Parking must change the state and NOTHING else — the row keeps its id,
    its score and the route's own words — and a session that actually finished the work still wins.
    """
    parked = [e for e in by_route.values() if e["state"] == priority.PARKED_STATE]
    for e in parked:
        assert e["id"], "a parked row lost its id"
        assert isinstance(e.get("score"), (int, float)), f"{e['id']} lost its score when parked"
        assert str(e.get("what") or "").strip(), f"{e['id']} lost the route's own next-action text"

    sample = copy.deepcopy(parked[0])
    prior = copy.deepcopy(sample)
    prior["state"] = "done"
    merged = priority.merge([copy.deepcopy(sample)], {"entries": [prior]})
    assert merged[0]["state"] == "done", (
        "a re-score un-finished a row a session had marked done — merge() must let a SESSION_STATE "
        "win over the graph's re-derived state"
    )


# ---------------------------------------------------------------------------------------------
# 7-8 · the shape of the fix, and the readers that have to agree with it
# ---------------------------------------------------------------------------------------------

def test_the_discriminator_is_a_field_read_and_not_a_phrase_match():
    """⛔ THE REJECTED ALTERNATIVE, PINNED. Matching the next-action English is a grep the next
    re-wording defeats silently. These literals are the exact phrases the defect was reported
    against; none of them may appear in the module as anything a comparison could consume."""
    with open(os.path.join(AUTONOMY, "priority.py"), encoding="utf-8") as fh:
        source = fh.read()
    banned = ["no further lookup", "closed line", "keep registered", "cite the closure",
              "landscape context", "nothing to build"]
    import re as _re
    # Only executable lines: the docstring and comments MUST be able to quote the defect.
    code = "\n".join(line.split("#", 1)[0] for line in source.splitlines())
    code = _re.sub(r'""".*?"""', "", code, flags=_re.S)
    hits = [phrase for phrase in banned if phrase in code.lower()]
    assert not hits, (
        f"priority.py matches next-action prose {hits} — the discriminator must be a committed "
        "field (state.status), not English that a re-wording defeats"
    )


def test_every_reader_of_the_offer_list_treats_parked_as_not_offerable():
    """⛔⛔ THE ONE-OF-A-PAIR CHECK. A writer that emits a state no reader honours changes nothing:
    the rows would keep appearing in the ready list under a new label. Each of these modules
    decides, independently, which rows are still on offer — and each must exclude `parked`."""
    import continuity  # noqa: PLC0415
    import handoff  # noqa: PLC0415
    import health  # noqa: PLC0415
    import stalled_holder  # noqa: PLC0415

    assert priority.PARKED_STATE not in continuity.OPEN_STATES, (
        "continuity.py would still print a parked row under 'READY TO RUN RIGHT NOW'"
    )
    assert priority.PARKED_STATE not in stalled_holder.OPEN_STATES

    for module, name in ((handoff, "handoff.py"), (health, "health.py")):
        with open(module.__file__, encoding="utf-8") as fh:
            src = fh.read()
        assert '{"queued", "blocked"}' in src, (
            f"{name} no longer selects offerable rows with the literal this test pins; re-check "
            "that it still excludes 'parked' before relaxing this assertion"
        )
        assert f'"{priority.PARKED_STATE}"' not in src.split("def ")[0], name
