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


# ---------------------------------------------------------------------------------------------
# AUT-PROP-029's stuck_clock, wired in here the same way `handoff.top_items` already reads it.
# ---------------------------------------------------------------------------------------------

def test_a_stalled_row_is_excluded_from_ready(led, monkeypatch):
    """⛔⛔ THE GAP THIS CLOSES, MEASURED THE DAY IT WAS FOUND. `handoff.py`'s ready-work selector
    started excluding a `stalled_needs_human` row (AUT-PROP-029), but THIS tool — the one the Stop
    hook actually calls every turn — kept offering it, because nothing here read the same verdict.
    AUT-PROP-012 sat at the top of this tool's own ready list for a full session after it had
    already gone terminal. Two files agreeing in prose that a stalled row should not be offered as
    work, and disagreeing in code, is the exact defect class this file's own history already
    documents twice above (AUT-PD-013/AUT-PD-017's reader/writer mismatches)."""
    monkeypatch.setattr(C.handoff, "terminal_ids", lambda *a, **k: frozenset({"A"}))
    led([_item(id="A"), _item(id="B")])
    ids = [e["id"] for e in C.ready()]
    assert ids == ["B"], (
        "a row stuck_clock.py reports stalled_needs_human must not appear on the ready list, and "
        "an unaffected row must still appear")


def test_a_stalled_rows_reason_is_named_in_the_blocked_report(led, monkeypatch):
    """CLAUDE.md §0: 'blocked' is a claim that needs evidence, checkable rather than a silent drop.
    A row excluded for being terminal must show up in `blocked()` with a reason naming stuck_clock,
    not just vanish from `ready()`."""
    monkeypatch.setattr(C.handoff, "terminal_ids", lambda *a, **k: frozenset({"A"}))
    led([_item(id="A")])
    [(entry, why)] = C.blocked()
    assert entry["id"] == "A"
    assert "stalled_needs_human" in why and "stuck_clock" in why


def test_terminal_ids_failing_open_still_shows_everything(led, monkeypatch):
    """⚠ THE FAIL-OPEN DIRECTION, PINNED. `handoff.terminal_ids()` already returns an empty set on
    ANY failure (missing git, a shallow clone, a bad repo path) rather than raising — this asserts
    THIS caller doesn't add a second failure mode on top by, say, crashing on an empty set or
    treating 'no verdict' as 'everything is stalled'."""
    monkeypatch.setattr(C.handoff, "terminal_ids", lambda *a, **k: frozenset())
    led([_item(id="A"), _item(id="B")])
    assert {e["id"] for e in C.ready()} == {"A", "B"}


# ---------------------------------------------------------------------------------------------
# AUT-PD-014's progress-aware retry budget — reuses priority.py's own arithmetic (`_retry_budget_spent`
# in continuity.py) so the two files can never disagree about what "budget spent" means.
# ---------------------------------------------------------------------------------------------

def _spent_row(id="A", n=None):
    """A row dispatched `n` times (default: the whole budget) against evidence that never moved."""
    n = C.priority.DEFAULT_RETRY_BUDGET if n is None else n
    fp = C.priority.evidence_fingerprint({"last_evidence_utc": "2026-08-01", "blocked_evidence": None})
    return _item(id=id, last_evidence_utc="2026-08-01", blocked_evidence=None,
                dispatch_log=[{"utc": "x", "fingerprint_at_dispatch": fp}] * n)


def test_a_budget_spent_row_is_excluded_from_ready(led):
    """⛔⛔ THE SAME SHAPE AS THE STALLED-ROW EXCLUSION ABOVE, for a different terminal condition. A
    row dispatched DEFAULT_RETRY_BUDGET times with nothing ever learned is not ready work."""
    led([_spent_row(id="A"), _item(id="B")])
    assert [e["id"] for e in C.ready()] == ["B"], (
        "a row whose progress-aware retry budget is spent must not appear on the ready list, and an "
        "unaffected row must still appear")


def test_a_budget_spent_rows_reason_is_named_in_the_blocked_report(led):
    led([_spent_row(id="A")])
    [(entry, why)] = C.blocked()
    assert entry["id"] == "A"
    assert "retry budget spent" in why


def test_a_row_one_dispatch_short_of_the_budget_is_still_ready(led):
    """The boundary. Spending the budget is `>= DEFAULT_RETRY_BUDGET`, not `> DEFAULT_RETRY_BUDGET`
    — one short must still be offered."""
    led([_spent_row(id="A", n=C.priority.DEFAULT_RETRY_BUDGET - 1)])
    assert [e["id"] for e in C.ready()] == ["A"]


def test_a_budget_spent_row_recovers_the_moment_its_evidence_moves(led):
    """★ Mirrors work_ledger.py's 'returns to open by itself' — nothing here should need a human to
    clear a flag; a fresh `last_evidence_utc` is enough."""
    row = _spent_row(id="A")
    led([row])
    assert C.ready() == []
    row["last_evidence_utc"] = "2026-08-27"  # evidence advanced since the last dispatch
    led([row])
    assert [e["id"] for e in C.ready()] == ["A"]


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


def test_recorded_block_evidence_is_a_stop_even_with_no_blocked_by(led, capsys):
    """⛔⛔ THIS FILE AND `priority.py` READ DIFFERENT FIELDS FOR THE SAME QUESTION (2026-08-27).

    `apply_session_penalties` keys its -90 penalty on a non-empty `blocked_evidence`, and its comment
    says why in as many words: *"KEYED ON THE EVIDENCE, NOT ON `state`. The recorded observation IS
    the block."* This checker keyed on `blocked_by`. So a row carrying evidence and no `blocked_by`
    was PENALISED by the ranker and OFFERED by this checker at the same moment — AUT-PROP-018 sat at
    the top of the ready list for an hour that way, with a recorded reason nobody was reading, while
    the driver described the reason in chat instead. An item whose blocker lives only in somebody's
    reply is an item nothing can check.

    ⚠ THE SAME READER/WRITER MISMATCH FAMILY AS AUT-PD-013 AND AUT-PD-017: two files agreeing in
    prose about which field carries a fact, and disagreeing in code.
    """
    led([_item(id="A", blocked_evidence="the ASO clauses are sha-bound; HEAD is moving")])
    assert C.ready() == [], (
        "a row with recorded block evidence was offered as ready work. The ranker already stands it "
        "down; two tools disagreeing about whether an item is runnable is worse than either answer.")
    assert C.main(["--check"]) == 0
    out = capsys.readouterr().out
    assert "sha-bound" in out, (
        "the row was hidden without its reason being named. CLAUDE.md §0 wants a block CHECKABLE, "
        "not invisible — an unread reason is what this fixes, not what it creates.")


def test_empty_block_evidence_is_not_a_block(led):
    """⚠ The positive control, and it guards the direction that costs work. An empty string, a null
    or whitespace must NOT stand an item down — otherwise the field's mere presence parks a route,
    which is the opposite failure and the more expensive one."""
    for value in (None, "", "   "):
        led([_item(id="A", blocked_evidence=value)])
        assert len(C.ready()) == 1, f"blocked_evidence={value!r} wrongly stood the item down"


# ---------------------------------------------------------------------------------------------
# ⛔ THE CAPACITY BRANCH. It is the only thing in this file that can turn a ready list into exit 0,
# so it is the branch most likely to be quietly widened into v1's permission slip.
# ---------------------------------------------------------------------------------------------

def _cap(monkeypatch, tmp_path, value):
    p = tmp_path / "autonomy-state.json"
    p.write_text(json.dumps({"subagent_width": value}), encoding="utf-8")
    monkeypatch.setattr(C, "STATE", str(p))


def test_the_cap_counts_workers_not_leases(led, monkeypatch, tmp_path):
    """⛔⛔ FOUND IN THE FIRST VERSION OF THIS BRANCH, AND IT IS THE RECEIPT SCHEMA'S UNIT ERROR
    AGAIN. `subagent_width` caps CONCURRENT WORKERS. One seat legitimately holds two items —
    AUT-036 and AUT-037 went to a single seat precisely because both re-curate one corpus — so
    counting LEASES read 5-of-5 while four workers ran and there was room for a fifth.

    ⚠ Counting the wrong unit here is not a miscount, it is a STALL: it manufactures a capacity
    excuse out of good practice, and the excuse grows every time a seat is sensibly given two
    related items.
    """
    _cap(monkeypatch, tmp_path, 2)
    led([_item(id="A", owner="seat-one", state="in_progress"),
         _item(id="B", owner="seat-one", state="in_progress"),
         _item(id="C")])
    assert C.main(["--check"]) == 1, (
        "two leases held by ONE worker were counted as two workers, so a free row was reported as "
        "unstartable while the cap had room")


def test_one_lease_covering_a_fanout_counts_its_AGENTS(led, monkeypatch, tmp_path):
    """⛔⛔ THE THIRD UNIT ERROR IN THIS FAMILY IN ONE DAY, and each was caught only by comparing the
    check against reality rather than reading it.

      1. counted LEASES  → one seat holding two items read as two workers (caught by AUT-036/037)
      2. counted OWNERS  → a FIVE-SEAT fan-out claimed under one owner name read as ONE worker,
                           while ListAgents showed five running (caught here)

    `subagent_width`'s unit is CONCURRENT AGENTS — autonomy-state.json says so in as many words — and
    under-counting is the dangerous direction: it permits a sixth dispatch past the cap the
    architecture records as having failed catastrophically (107 agents, 40 completed, 67 errored,
    the synthesis lost).
    """
    _cap(monkeypatch, tmp_path, 5)
    led([_item(id="FANOUT", owner="one-name-five-seats", state="in_progress", claim_workers=5),
         _item(id="FREE")])
    assert C.main(["--check"]) == 0, (
        "a five-agent fan-out under one owner name read as one worker, so the cap had room it does "
        "not have")


def test_an_undeclared_lease_counts_as_one_agent(led, monkeypatch, tmp_path):
    """⚠ THE HONEST DEFAULT. Most claims are one worker, and only the caller knows it dispatched
    five — so absence means one, not zero and not a guess. ⛔ And that makes `claim_workers` a FLOOR
    ON HONESTY, not a guarantee: an under-declared fan-out still under-counts, which the module says
    out loud rather than leaving a reader to assume the count is measured."""
    _cap(monkeypatch, tmp_path, 2)
    led([_item(id="A", owner="seat-one", state="in_progress"),
         _item(id="B", owner="seat-two", state="in_progress"),
         _item(id="C")])
    assert C.main(["--check"]) == 0, "two undeclared leases should count as two agents"


@pytest.mark.parametrize("bad", [0, -1, True, "5", 2.5, None])
def test_a_nonsense_claim_workers_falls_back_to_one(led, monkeypatch, tmp_path, bad):
    """`True` is an int in Python; a string would raise. A malformed declaration must degrade to the
    honest default rather than crashing the checker or inventing capacity."""
    _cap(monkeypatch, tmp_path, 3)
    led([_item(id="A", owner="seat", state="in_progress", claim_workers=bad), _item(id="B")])
    assert C.main(["--check"]) == 1, f"claim_workers={bad!r} did not degrade to one agent"


def test_a_full_cap_is_a_real_stop_and_names_every_holder(led, monkeypatch, tmp_path, capsys):
    """★ A full cap is the same shape as waiting on a human: a WORKER must finish first. It is
    allowed to end a turn — and only because it is falsifiable. Every holder is named, so a lease
    pointing at a worker that is not running is visible as litter rather than as capacity."""
    _cap(monkeypatch, tmp_path, 2)
    led([_item(id="A", owner="seat-one", state="in_progress"),
         _item(id="B", owner="seat-two", state="in_progress"),
         _item(id="C")])
    assert C.main(["--check"]) == 0
    out = capsys.readouterr().out
    assert "AT CAPACITY" in out
    assert "seat-one" in out and "seat-two" in out, (
        "the capacity claim did not name its holders, so nobody can tell a running worker from a "
        "stale lease — and an unfalsifiable capacity claim IS v1's permission slip")
    assert "NOT PERMISSION TO STOP WORKING" in out


def test_an_unreadable_cap_buys_nothing(led, monkeypatch, tmp_path):
    """⛔ FAIL CLOSED. A dial nobody can read must never excuse a stall — the same direction the
    publish bar fails, and the direction that costs nothing when wrong."""
    monkeypatch.setattr(C, "STATE", str(tmp_path / "does-not-exist.json"))
    led([_item(id="A", owner="seat-one", state="in_progress"), _item(id="B")])
    assert C.width_cap() is None
    assert C.main(["--check"]) == 1, "an unreadable width cap was treated as capacity pressure"


@pytest.mark.parametrize("bad", [0, -1, True, "5", None, 2.5])
def test_a_nonsense_cap_is_unreadable_rather_than_believed(monkeypatch, tmp_path, bad):
    """`True` is an int in Python and would pass a naive check as a cap of 1 — which would declare
    the loop full the moment any single worker existed."""
    _cap(monkeypatch, tmp_path, bad)
    assert C.width_cap() is None, f"subagent_width={bad!r} was accepted as a cap"


def test_a_released_lease_stops_counting(led, monkeypatch, tmp_path):
    """⚠ The recovery path, asserted. If a finished worker's lease kept counting, the cap would
    ratchet shut over a session and the loop would starve itself."""
    _cap(monkeypatch, tmp_path, 1)
    led([_item(id="A", owner="seat-one", state="done"), _item(id="B")])
    assert C.live_leases() == [], "a finished item's lease still counted against the cap"
    assert C.main(["--check"]) == 1


def test_declaring_false_silences_the_report_without_hiding_the_work(led):
    """⭐ THE REGEX WAS WRONG ABOUT TWO OF TEN REAL ROWS — one matched 'the paper heading' inside a
    list of already-rewritten sites, the other matched 'deposit artifact' in a row about a file
    ORDERING bug. Declaring false must clear the flag and keep the item startable, or the honest
    answer costs you the work."""
    led([_item(id="A", what="BUILD THE DETECTOR so the paper heading sweep never repeats.",
               requires_trimcrae=False)])
    assert len(C.ready()) == 1, "declaring an item mine removed it from the ready list"
    assert C.unclassified_outward() == []
