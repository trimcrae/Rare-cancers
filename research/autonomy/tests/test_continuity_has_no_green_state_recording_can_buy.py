#!/usr/bin/env python3
"""The one property that makes continuity.py v2 different from v1, asserted rather than described.

⛔ THE THREAT MODEL IS NOT "the tool miscounts". It is that a session looking for a reason to stop
finds a green tick with a citation attached. v1 had one: it asked whether outstanding work was
WRITTEN DOWN, answered yes, printed

    ✅ every blocking clause has a queued ledger item; the work survives this session.

and the turn then ended with three pieces of free, ready, unblocked work and nothing running. The
check passed over the bug it existed to catch.

★ SO EVERY TEST HERE IS A CASE WHERE FILING WORK MUST NOT BUY A PASS. The invariant: recording an
item is what puts it ON the ready list, never what clears it. A future edit that lets a recorded item
off the list for any reason other than "a human or the outside world has to move first" has rebuilt
v1, and one of these tests will fail.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import continuity as C  # noqa: E402


def _ledger(tmp_path, entries):
    p = tmp_path / "research-ledger.json"
    p.write_text(json.dumps({"entries": entries}), encoding="utf-8")
    return str(p)


def _item(**kw):
    base = {"id": "AUT-X", "state": "queued", "owner": None, "blocked_by": None,
            "cost_class": "free", "score": 10.0, "what": "a free, ready, unblocked thing"}
    base.update(kw)
    return base


@pytest.fixture
def led(tmp_path, monkeypatch):
    def install(entries):
        monkeypatch.setattr(C, "LEDGER", _ledger(tmp_path, entries))
    return install


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE REGRESSION. This is the exact shape v1 called healthy.
# ---------------------------------------------------------------------------------------------

def test_a_perfectly_recorded_backlog_with_nothing_running_fails(led, capsys):
    """⛔⛔ THE BUG, VERBATIM. Three items, all filed, all declaring the clause they close — v1's
    green state — and none of them moving. The whole point of v2 is that this exits 1."""
    led([
        _item(id="A", closes_clause={"paper": "PUB-ASO", "clause": "hardening_converged"}),
        _item(id="B", closes_clause={"paper": "PUB-ASO", "clause": "preflight_full_green"}),
        _item(id="C", closes_clause={"paper": "PUB-ASO", "clause": "independent_adversarial_seat"}),
    ])
    assert C.main(["--check"]) == 1, (
        "a fully recorded, fully unblocked backlog passed the check. That is v1's failure exactly: "
        "the question became 'is it written down' instead of 'is it moving'.")
    out = capsys.readouterr().out
    assert "READY TO RUN RIGHT NOW" in out


def test_declaring_a_closes_clause_does_not_clear_an_item(led):
    """⛔ THE PERMISSION SLIP, TESTED DIRECTLY. `closes_clause` is v1's currency. It must buy nothing
    here — an item that declares it is still an item somebody has to run."""
    plain = _item(id="A")
    declaring = _item(id="A", closes_clause={"paper": "PUB-ASO", "clause": "hardening_converged"})
    led([plain])
    n_plain = len(C.ready())
    led([declaring])
    assert len(C.ready()) == n_plain == 1, (
        "declaring which clause an item closes changed whether it counts as ready work")


def test_there_is_no_output_that_calls_a_ready_backlog_healthy(led, capsys):
    """★ The property stated as a property. v1's defect was a SENTENCE — a green tick a reader could
    quote back. No wording that reads as approval may appear while work is ready."""
    led([_item(id="A")])
    C.main([])
    out = capsys.readouterr().out
    for forbidden in ("✅", "survives this session", "nothing to do", "all clear"):
        assert forbidden not in out, (
            f"the ready-work report contains {forbidden!r}, which reads as permission to stop. "
            "v1's green tick was exactly one sentence long.")


# ---------------------------------------------------------------------------------------------
# The four real stops. Each is a way the outside world, not the session, has to move first.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("field,value,why", [
    ("state", "done", "finished work is not ready work"),
    ("blocked_by", ["AUT-999"], "a declared dependency is a real stop"),
    ("owner", "CYC-0023", "someone else holds the claim lease"),
    ("cost_class", "expensive", "expensive spend needs a human — CLAUDE.md §2"),
])
def test_the_only_ways_off_the_list_are_real_stops(led, field, value, why):
    led([_item(id="A", **{field: value})])
    assert C.ready() == [], f"{field}={value!r} should take the item off the ready list: {why}"


def test_your_own_lease_does_not_hide_your_own_work(led):
    """⚠ THE ONE-WAY DOOR IN THE LEASE CHECK. A cycle that claims an item and then reads this tool
    must still see it. Otherwise claiming work is a way to make it disappear — a permission slip
    wearing a lease."""
    led([_item(id="A", owner="CYC-0024")])
    assert C.ready() == [], "another cycle's lease should hide the item"
    assert len(C.ready(me="CYC-0024")) == 1, (
        "an item you hold the lease on vanished from your own ready list; claiming work must never "
        "be a way to stop seeing it")


def test_an_empty_backlog_is_the_honest_zero(led, capsys):
    """The positive control. Without it the suite would pass on a tool that fails everything."""
    led([_item(id="A", state="done")])
    assert C.main(["--check"]) == 0
    assert "no ledger item is ready to run" in capsys.readouterr().out


def test_everything_blocked_is_the_other_honest_zero(led, capsys):
    led([_item(id="A", blocked_by=["AUT-999"]), _item(id="B", cost_class="expensive")])
    assert C.main(["--check"]) == 0
    out = capsys.readouterr().out
    assert "every one of them blocked" in out
    assert "AUT-999" in out, "the empty state must NAME what each item waits on, or it is unauditable"


# ---------------------------------------------------------------------------------------------
# The demoted v1 question. It still works; it is just no longer the stopping condition.
# ---------------------------------------------------------------------------------------------

def test_the_clause_view_still_catches_unrecorded_work(led, tmp_path, monkeypatch, capsys):
    """v1's check was RIGHT about its own question and wrong about which question mattered. It is
    kept, subordinate, because unrecorded work is still a real defect."""
    monkeypatch.setattr(C, "QUEUE", str(tmp_path / "q.json"))
    (tmp_path / "q.json").write_text(json.dumps({"waiting": {"PUB-ASO": {
        "state": "NOT-READY", "blocking_clauses": ["hardening_converged"],
        "what_he_does": "post it"}}}), encoding="utf-8")
    led([_item(id="A")])  # queued, but declares no clause
    assert C.main(["--clauses"]) == 1
    assert "NO QUEUED LEDGER ITEM CLOSES THIS" in capsys.readouterr().out


def test_the_clause_view_says_filing_is_not_permission_to_stop(led, tmp_path, monkeypatch, capsys):
    """⛔ Even v1's own view must not read as a pass. Its remedy text has to point AT the ready list."""
    monkeypatch.setattr(C, "QUEUE", str(tmp_path / "q.json"))
    (tmp_path / "q.json").write_text(json.dumps({"waiting": {"PUB-ASO": {
        "state": "NOT-READY", "blocking_clauses": ["hardening_converged"],
        "what_he_does": "post it"}}}), encoding="utf-8")
    led([_item(id="A")])
    C.main(["--clauses"])
    assert "does NOT make this session free to stop" in capsys.readouterr().out


# ---------------------------------------------------------------------------------------------
# Survivor of the first mutation run, pinned here.
# ---------------------------------------------------------------------------------------------

def test_work_someone_started_and_did_not_finish_stays_on_the_list(led):
    """⛔⛔ FOUND SURVIVING A MUTATION: dropping "in_progress" from OPEN_STATES passed all twelve
    tests, and it is the single most dangerous edit available here.

    An `in_progress` item is work a session BEGAN and did not finish — a cycle that died, a rate
    limit, a container restart. That is the likeliest way work goes quiet, and treating it as
    finished makes it disappear from the one report that would surface it. ⚠ Every test above built
    its fixtures as the default "queued", so the constant could be narrowed and the suite stayed
    green: a suite that only ever exercises one value of a constant measures nothing about the
    others.
    """
    assert "in_progress" in C.OPEN_STATES, (
        "in_progress left OPEN_STATES. Half-finished work is the MOST important kind to keep "
        "visible, not the least — it is what a dead cycle leaves behind.")
    led([_item(id="A", state="in_progress")])
    assert len(C.ready()) == 1, "an item a previous session started and abandoned fell off the list"
    assert C.main(["--check"]) == 1


def test_the_blocked_report_names_what_each_row_waits_on(led, capsys):
    """⚠ The empty state is the only one that ends a turn, so it is the one that must be auditable.
    A list of ids with no reasons cannot be checked against CLAUDE.md §0 — "'Blocked' is a claim that
    needs evidence, and it is usually wrong"."""
    led([_item(id="A", blocked_by=["AUT-999"]), _item(id="B", owner="CYC-0023")])
    C.main(["--check"])
    out = capsys.readouterr().out
    assert "AUT-999" in out and "CYC-0023" in out, (
        "the blocked report stopped naming what each row waits on, so nobody can tell a real "
        "blocker from a stale one")


# ---------------------------------------------------------------------------------------------
# Found by the Stop hook that reads this module, 2026-08-27.
# ---------------------------------------------------------------------------------------------

def test_an_outward_facing_act_is_not_ready_work(led):
    """⛔⛔ THE TOOL OFFERED WORK IT IS NOT ALLOWED TO DO. The Stop hook's third firing put
    "Publish the assessment…" and "Post the preprint and put the MTAP stain in front of a group…"
    at the top of the ready list — both reserved for trimcrae by CLAUDE.md §3, both offered because
    readiness was modelled on SPEND and never on WHO MAY ACT. An outward-facing act is free in
    dollars and still not mine.
    """
    led([_item(id="A", requires_trimcrae=True)])
    assert C.ready() == [], "an outward-facing act was offered as ready work"
    assert C.main(["--check"]) == 0


def test_an_undeclared_outward_looking_row_is_reported_not_hidden(led, capsys):
    """★ THE TOOL MAY NOT QUIETLY WITHHOLD WORK ON A GUESS, AND MAY NOT PRETEND THE QUESTION IS NOT
    THERE. An undeclared row that reads as outward-facing stays ON the ready list — hiding it would
    lose real work — and is named so somebody decides. Silence either way is the v1 failure: a
    status that is really an unanswered question.
    """
    led([_item(id="A", what="Publish the assessment and pair it with the cell-panel ask.")])
    assert len(C.ready()) == 1, "an undeclared row was hidden on a guess"
    assert [e["id"] for e in C.unclassified_outward()] == ["A"]
    C.main(["--check"])
    assert "declare nothing" in capsys.readouterr().out


def test_declaring_false_silences_the_report_without_hiding_the_work(led):
    """⭐ THE REGEX WAS WRONG ABOUT TWO OF TEN REAL ROWS — one matched 'the paper heading' inside a
    list of already-rewritten sites, the other matched 'deposit artifact' in a row about a file
    ORDERING bug. Declaring false must clear the flag and keep the item startable, or the honest
    answer costs you the work."""
    led([_item(id="A", what="BUILD THE DETECTOR so the paper heading sweep never repeats.",
               requires_trimcrae=False)])
    assert len(C.ready()) == 1, "declaring an item mine removed it from the ready list"
    assert C.unclassified_outward() == []
