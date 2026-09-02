#!/usr/bin/env python3
"""`serves.route` is a JOIN KEY, and nothing refused one that joined to nothing (S51, 2026-09-02).

⛔⛔ THE MEASUREMENT THAT PRODUCED THIS TEST. On 2026-09-02, over the 361 committed ledger rows:

    serves.route      336 rows carry one, 80 distinct ids, 77 exist
                      -> 178 rows unresolvable: RT-AUTONOMY 176, RT-LOOP 1, RT-DEGRADER-TERNARY 1
    serves.strategy   155 rows carry one, 17 distinct ids, 13 exist
                      -> 30 rows unresolvable: ST-RNA 26, ST-DEGRADER 2, ST-PROCESS 1, ST-EVIDENCE 1
    serves.publication 170 rows, 32 distinct ids, all 32 exist -> 0 unresolvable

Every one of the 208 read as GREEN in every instrument. `priority.apply_route_inheritance` and
`priority.route_score_floor` LOOK THE VALUE UP and both are filtered to `_derived` rows, so an id the
graph lacks has no derived sibling, acquires no floor, and the lookup returns nothing with no error
path anywhere. The row keeps whatever number a human typed and ranks below every row the ranker
actually judged.

⛔ AND THE PROOF THAT REPAIRING WITHOUT GUARDING DOES NOT HOLD IS IN THIS FIELD'S OWN HISTORY.
`AUT-PD-177` repaired 18 rows on 2026-08-29; at its commit `6e093294b` the unresolvable set was
`{RT-AUTONOMY: 162, RT-LOOP: 1}` and `RT-DEGRADER-TERNARY` stood at ZERO. It is back today on
`AUT-PD-179`, filed after that commit, and `RT-AUTONOMY` grew 162 -> 176 in four days. Nothing
refused either, because nothing was watching. Separately the same night a session wrote
`RT-TXN-DEPENDENCY` — a route existing nowhere — into a `serves` block from memory and `priority.py`
stored it silently.

★ WHAT IS PINNED HERE, AND WHY THE LAST TWO MATTER MOST. The committed ledger is checked (the
regression), a constructed graph exercises the mechanism (the prospective half), and two tests are
written to go RED IF THE CHECKER STOPS CHECKING — a gate whose only assertion is "the committed file
is clean" passes just as well for a function that has been switched off, which is the vacuous-guard
failure `ledger_schema`'s own suite already names.

⚠ THE ONE THING THIS DOES NOT ASSERT: that `null` is the right value for any particular row. A row
serving no route is legitimate (25 committed rows do) and is deliberately not flagged. The defect is
a value that LOOKS like a join key and joins to nothing, never an absence.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(AUTONOMY))
sys.path.insert(0, AUTONOMY)

import ledger_io  # noqa: E402
import ledger_schema  # noqa: E402

LEDGER = os.path.join(AUTONOMY, "research-ledger.json")
GRAPH = os.path.join(REPO, "systems", "graph")


def _graph(tmp_path, routes=("RT-REAL",), strategies=("ST-REAL",), publications=("PUB-REAL",)):
    """A minimal `systems/graph` the checker can be pointed at. ⚠ Constructed, never the real one:
    the mechanism must stay exercised after the committed ledger is clean."""
    d = tmp_path / "graph"
    d.mkdir(exist_ok=True)
    for name, ids in (("routes.json", routes), ("strategies.json", strategies),
                      ("publications.json", publications)):
        (d / name).write_text(json.dumps([{"id": i} for i in ids]), encoding="utf-8")
    return str(d)


def _row(**serves):
    # ⚠ `score` IS PRESENT DELIBERATELY. `ledger_io.write_ledger` runs `admissibility.check_write`
    # BEFORE `ledger_schema.check_write`, and R5 (`refuse_population_growth`) refuses an appended
    # open row carrying no score — so a scoreless fixture would prove the wrong gate fired.
    return {"id": "AUT-PD-999", "kind": "process_defect", "state": "queued", "score": 1.0,
            "serves": serves}


# --------------------------------------------------------------------------------------------
# the mechanism, against a constructed graph
# --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("key,bad", [("route", "RT-NOPE"), ("strategy", "ST-NOPE"),
                                     ("publication", "PUB-NOPE")])
def test_a_join_key_the_graph_lacks_is_refused(tmp_path, key, bad):
    found = ledger_schema.reference_problems(_row(**{key: bad}), graph_dir=_graph(tmp_path))
    assert len(found) == 1, found
    assert bad in found[0] and f"serves.{key}" in found[0]
    # ⛔ The message must refuse the tempting repair by name, or the next reader takes it.
    assert "NOT TO ADD THE ID TO THE GRAPH" in found[0]


@pytest.mark.parametrize("key,good", [("route", "RT-REAL"), ("strategy", "ST-REAL"),
                                      ("publication", "PUB-REAL")])
def test_a_join_key_the_graph_holds_is_not_refused(tmp_path, key, good):
    assert ledger_schema.reference_problems(_row(**{key: good}),
                                            graph_dir=_graph(tmp_path)) == []


@pytest.mark.parametrize("value", [None, ""])
def test_an_absent_route_is_not_a_broken_one(tmp_path, value):
    """25 committed rows serve no route. 'This row serves no route' is an honest statement and the
    repair S51 applies WRITES it — flagging it would make the guard's own remedy inadmissible."""
    assert ledger_schema.reference_problems(_row(route=value, publication="PUB-REAL"),
                                            graph_dir=_graph(tmp_path)) == []


def test_a_row_with_no_serves_block_is_not_refused(tmp_path):
    assert ledger_schema.reference_problems({"id": "AUT-PD-999"}, graph_dir=_graph(tmp_path)) == []


def test_a_non_string_join_key_is_refused(tmp_path):
    found = ledger_schema.reference_problems(_row(route=["RT-REAL"]), graph_dir=_graph(tmp_path))
    assert len(found) == 1 and "not a string" in found[0]


def test_an_unreadable_graph_fails_closed(tmp_path):
    """⛔ CLAUDE.md §4: an absent reading is not a reading of absence. A checker that answers 'fine'
    because it could not read its own reference data is the defect, not the safe default."""
    d = _graph(tmp_path)
    os.remove(os.path.join(d, "routes.json"))
    found = ledger_schema.reference_problems(_row(route="RT-REAL"), graph_dir=d)
    assert len(found) == 1 and "failing closed" in found[0]

    (tmp_path / "graph" / "routes.json").write_text("{not json", encoding="utf-8")
    found = ledger_schema.reference_problems(_row(route="RT-REAL"), graph_dir=d)
    assert len(found) == 1 and "failing closed" in found[0]


def test_the_cache_does_not_serve_a_stale_graph(tmp_path):
    """A cache in a gate stops the gate measuring the tree it is judging. Keyed on the stat, so a
    rewritten graph file is re-read."""
    d = _graph(tmp_path, routes=("RT-REAL",))
    assert ledger_schema.reference_problems(_row(route="RT-LATER"), graph_dir=d) != []
    p = os.path.join(d, "routes.json")
    os.utime(p, (0, 0))
    with open(p, "w", encoding="utf-8") as fh:
        json.dump([{"id": "RT-REAL"}, {"id": "RT-LATER"}], fh)
    assert ledger_schema.reference_problems(_row(route="RT-LATER"), graph_dir=d) == []


# --------------------------------------------------------------------------------------------
# the wiring — these are the tests that go red if the checker is switched off
# --------------------------------------------------------------------------------------------

def test_the_whole_ledger_check_runs_the_reference_check():
    """`problems()` is what `--check` and the ledger-wide gate call. A `reference_problems` that is
    never called from it is a function, not a gate."""
    bad = {"_schema": "emc-research-ledger/1",
           "entries": [_row(route="RT-NOT-A-ROUTE-ANYWHERE")]}
    found = [f for f in ledger_schema.problems(bad) if "names no id" in f]
    assert len(found) == 1, ledger_schema.problems(bad)


def test_a_write_cannot_land_a_route_the_graph_lacks(tmp_path):
    """`ledger_io.write_ledger` is the one place every programmatic writer passes through, and it is
    where `RT-TXN-DEPENDENCY` was stored silently."""
    p = tmp_path / "research-ledger.json"
    good = {"_schema": "emc-research-ledger/1", "entries": []}
    ledger_io.write_ledger(p, good)          # a clean write still works
    bad = {"_schema": "emc-research-ledger/1",
           "entries": [_row(route="RT-TXN-DEPENDENCY")]}
    with pytest.raises(ledger_schema.SchemaViolation) as exc:
        ledger_io.write_ledger(p, bad)
    assert "RT-TXN-DEPENDENCY" in str(exc.value)
    # ⛔ never a partial file: the clean ledger on disk is untouched by the refused write.
    assert json.loads(p.read_text(encoding="utf-8"))["entries"] == []


# --------------------------------------------------------------------------------------------
# the committed tree
# --------------------------------------------------------------------------------------------

def test_every_serves_join_in_the_committed_ledger_resolves():
    """⛔ SHIPS GREEN ONLY BECAUSE THE 208 ROWS WERE REPAIRED IN THE SAME CHANGE
    (`fix_serves_route.py`, S51). A guard that ships red is a guard someone loosens; a grandfather
    list of 178 ids would have been a permanent tripwire, and the honest target for 177 of them was
    simply `null`."""
    with open(LEDGER, encoding="utf-8") as fh:
        ledger = json.load(fh)
    found = []
    for entry in ledger["entries"]:
        found.extend(ledger_schema.reference_problems(entry))
    assert found == [], f"{len(found)} unresolvable serves reference(s):\n" + "\n".join(found[:10])


def test_the_committed_graph_is_what_the_checker_reads():
    """⚠ A test whose reference data is constructed everywhere would pass with `GRAPH_DIR` pointing
    at nothing. This pins the default path at the real graph and the real counts."""
    assert os.path.isdir(ledger_schema.GRAPH_DIR)
    assert os.path.samefile(ledger_schema.GRAPH_DIR, GRAPH)
    assert set(ledger_schema.SERVES_JOINS) == {"route", "publication", "strategy"}
    for filename in ledger_schema.SERVES_JOINS.values():
        assert len(ledger_schema.graph_ids(filename)) > 0
