"""The molecular-glue watch must stay paired: a searchable trigger AND a prose row.

⛔ WHAT WAS MISSING (roadmap §10.1a `Q15`). `method-watch-triggers.json` carried
`TRG-GLUE-PROSPECTIVE-DESIGN` and the scanner was running it -- but `research/method-watch.md`, the
HUMAN-facing capability→action table, had no molecular-glue row at all. `target-route-options.md`'s
Route 10 says in its own words that *"the right action is a `method-watch.md` row"*, and that row did
not exist until 2026-08-07.

⚠ WHY THAT HALF-STATE IS THE EXPENSIVE ONE, AND WHY THE TRIGGER FILE'S OWN CHECKER COULD NOT SEE IT.
`method-watch-triggers.json`'s `_role` says it is *"NOT the one home for what each trigger would unlock
in prose (that is research/method-watch.md's capability->action table)"*, and the map checker's `[Z5]`
was deliberately taught to accept a machine query AS evidence a capability is watched -- correctly, for
its own purpose. So a trigger with a query and no prose row reads as fully covered by every automated
check, while a person opening the watch list finds nothing about glues and re-litigates the route from
scratch. That re-litigation is the exact cost `Q15` names.

⚠ THIS TEST IS DELIBERATELY NARROW. It does NOT require every trigger to cite its id in the prose table
-- measured 2026-08-07, 30 of 31 `external_capability` triggers describe their capability in words rather
than by id, and that is a reasonable style. It pins the ONE pairing `Q15` is about.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TRIGGERS = os.path.join(ROOT, "research", "method-watch-triggers.json")
WATCH = os.path.join(ROOT, "research", "method-watch.md")
ROUTES = os.path.join(ROOT, "research", "manuscripts", "program", "target-route-options.md")

TRIGGER_ID = "TRG-GLUE-PROSPECTIVE-DESIGN"


def _trigger():
    d = json.load(open(TRIGGERS, encoding="utf-8"))
    return next((t for t in d["triggers"] if t["id"] == TRIGGER_ID), None)


def test_the_searchable_trigger_still_exists_and_is_scanned():
    t = _trigger()
    assert t is not None, "%s was removed from method-watch-triggers.json" % TRIGGER_ID
    assert t["trigger_kind"] == "external_capability", t["trigger_kind"]
    assert t["scan_enabled"] is True, "the glue trigger is registered but not scanned"
    assert t["search"]["europepmc"] and t["search"]["arxiv"], "no query, so nothing is looking"


def test_the_prose_row_exists_and_names_the_trigger():
    """⭐ THE Q15 DELIVERABLE. Not "a glue is mentioned somewhere" -- a row in the capability→action
    table that a reader of the watch list will actually hit."""
    body = open(WATCH, encoding="utf-8").read()
    assert "## Capability → action trigger table" in body
    table = body.split("## Capability → action trigger table", 1)[1].split("\n## ", 1)[0]
    rows = [l for l in table.split("\n") if l.startswith("|")]
    glue = [l for l in rows if "molecular-glue" in l or "molecular glue" in l]
    assert glue, ("research/method-watch.md's capability→action table has no molecular-glue row. "
                  "target-route-options.md Route 10 names that row as the right action for the route.")
    joined = "\n".join(glue)
    assert TRIGGER_ID in joined, (
        "the glue row does not name %s, so a reader cannot get from the prose to the query that "
        "actually searches for it" % TRIGGER_ID)


def test_the_row_keeps_the_prospective_test_that_makes_it_meaningful():
    """⛔ THE ONE CLAUSE THAT CANNOT BE DROPPED. The programme's thesis is that glue selectivity has
    ALWAYS been discovered then rationalised. A row that fired on a retrospective rationalisation would
    fire on business as usual, which is worse than no row."""
    body = open(WATCH, encoding="utf-8").read()
    table = body.split("## Capability → action trigger table", 1)[1].split("\n## ", 1)[0]
    glue = "\n".join(l for l in table.split("\n") if "molecular-glue" in l or "molecular glue" in l)
    assert "prospective" in glue.lower(), glue[:300]
    assert "retrospective" in glue.lower(), (
        "the row must say a retrospective rationalisation does NOT fire it")
    t = _trigger()
    assert "prospective" in t["on_fire"].lower() and "retrospective" in t["on_fire"].lower(), t["on_fire"]


def test_the_row_states_what_firing_does_not_license():
    """A watch row that reads as an endorsement is how a route gets re-litigated in the other
    direction. A glue has no linker: no covalent axis, no designed exit vector."""
    body = open(WATCH, encoding="utf-8").read()
    table = body.split("## Capability → action trigger table", 1)[1].split("\n## ", 1)[0]
    glue = "\n".join(l for l in table.split("\n") if "molecular-glue" in l or "molecular glue" in l)
    assert "covalent axis" in glue, "the row does not say the covalent axis vanishes without a linker"
    assert "route" in glue.lower(), "the row must say firing reopens a ROUTE, never a result"


def test_route_10_still_asks_for_exactly_this_row():
    """If Route 10 ever stops naming a method-watch row as its action, this pairing needs rethinking
    rather than preserving."""
    body = open(ROUTES, encoding="utf-8").read()
    assert "Route 10 — a molecular glue instead of a PROTAC" in body
    seg = body.split("Route 10 — a molecular glue instead of a PROTAC", 1)[1].split("### Route 11", 1)[0]
    assert "method-watch.md" in seg, "Route 10 no longer points at a method-watch row"
    assert "watch, do not build" in seg, seg[-400:]


def test_the_trigger_names_what_it_reopens():
    """A hit that does not carry its consequence makes a reader re-derive the mapping by hand -- the
    exact gap trigger_scan.py's own docstring says it exists to close."""
    t = _trigger()
    r = t["reopens"]
    assert "RT-GLUE" in r["registry_routes"], r
    assert r["roadmap_rows"], r
    assert r["registry_blockers"], r
    assert t.get("registry_trigger_ids"), "no registry counterpart, so the map and this file cannot join"
