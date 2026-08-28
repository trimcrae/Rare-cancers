"""What is waiting on what — the half of the queue nothing printed.

⛔⛔ THE FINDING (2026-08-27 `/deep-research` pass, against AlabOS's source): its task STATUS is
dashboard-visible and its pending RESOURCE-REQUEST queue is surfaced by NO route. We have the same
split — continuity prints ready rows, stalled_holder prints held rows, and nothing joined them. That
gap is where the 2026-08-27 dead seat hid for 2 h 36 m.

★★ AND THE TEST THAT MATTERS IS `test_a_merely_cited_path_is_not_a_deliverable`. The first version
scanned `depends_on_evidence` — the field naming what a row READS — and flagged 33 ready rows on its
first run, nearly all citing a survey they merely reference. A guard that flags 33 true statements is
turned off within a week. The discriminator is creation-after-filing, not existence.
"""

from __future__ import annotations

import datetime
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import queue_view as Q  # noqa: E402


def test_evidence_is_not_a_deliverable_field():
    """⛔ THE 33-FALSE-POSITIVE FIX, pinned. `depends_on_evidence` names what a row reads."""
    assert "depends_on_evidence" not in Q.DELIVERABLE_FIELDS


def test_a_path_is_extracted_from_prose():
    row = {"what": "builds research/autonomy/thing.py and nothing else"}
    assert Q.named_paths(row) == ["research/autonomy/thing.py"]


def test_a_word_with_a_dot_is_not_a_path():
    """⚠ The matcher is narrow on purpose: prose is full of 'e.g.' and version numbers."""
    row = {"what": "see e.g. version 2.1 of the approach, cf. Smith et al."}
    assert Q.named_paths(row) == []


def test_only_tracked_source_roots_match():
    row = {"what": "wrote /tmp/scratch.py and ~/notes.md and research/autonomy/real.py"}
    assert Q.named_paths(row) == ["research/autonomy/real.py"]


def test_a_merely_cited_path_is_not_a_deliverable(monkeypatch):
    """⭐ THE DISCRIMINATOR. A path that existed BEFORE the row was filed is evidence, not output."""
    monkeypatch.setattr(Q, "on_trunk", lambda p, ref=None, repo=None: True)
    monkeypatch.setattr(Q, "added_after", lambda p, when, ref=None, repo=None: False)
    rows = [{"id": "R", "what": "grounded in research/autonomy/old.py",
             "last_evidence_utc": "2026-08-20"}]
    assert Q.already_landed(rows) == []


def test_a_deliverable_that_landed_after_filing_is_reported(monkeypatch):
    monkeypatch.setattr(Q, "on_trunk", lambda p, ref=None, repo=None: True)
    monkeypatch.setattr(Q, "added_after", lambda p, when, ref=None, repo=None: True)
    rows = [{"id": "R", "what": "build research/autonomy/new.py",
             "last_evidence_utc": "2026-08-20"}]
    assert Q.already_landed(rows) == [("R", ["research/autonomy/new.py"])]


def test_a_row_with_no_filing_date_makes_no_claim(monkeypatch):
    """⛔ No date, no comparison, no claim — never a guess in the direction that suppresses work."""
    monkeypatch.setattr(Q, "on_trunk", lambda p, ref=None, repo=None: True)
    monkeypatch.setattr(Q, "added_after", lambda p, when, ref=None, repo=None: True)
    for bad in (None, "", "   ", "not-a-date"):
        rows = [{"id": "R", "what": "build research/autonomy/new.py", "last_evidence_utc": bad}]
        assert Q.already_landed(rows) == []


def test_an_unreadable_trunk_suppresses_nothing(monkeypatch):
    """⚠ The safe direction: a git error must never manufacture 'already done'."""
    monkeypatch.setattr(Q, "REPO", "/nonexistent-repo-path")
    assert Q.on_trunk("research/autonomy/x.py", repo="/nonexistent-repo-path") is False
    assert Q.added_after("research/autonomy/x.py", datetime.date(2020, 1, 1),
                         repo="/nonexistent-repo-path") is False


def test_it_reports_and_never_closes():
    """⛔⛔ THE LIMIT THAT IS THE POINT. An artifact on the trunk is not the same as the item being
    finished; a row whose deliverable PARTLY landed must stay open. Auto-closing would silently drop
    the unfinished half — and 'the driver cannot be the thing that notices the driver has stalled'."""
    import inspect
    src = inspect.getsource(Q)
    for forbidden in ('"state"] = "done"', "state='done'", 'state="done"', "write_ledger"):
        assert forbidden not in src, f"queue_view mutates the ledger ({forbidden})"


def test_the_turn_end_hook_actually_consults_it():
    """⛔⛔ THE UNREACHABLE-GUARD TEST, AND THIS REPOSITORY HAS PAID FOR IT FOUR TIMES: subagent_width
    governed nothing for a fortnight, the census lane's exempt flag, the watchdog wired to a
    non-existent env var, and stuck_clock.py sitting unread while a session rebuilt it. A detector
    nobody calls is not a detector — it is a file that makes the problem look solved."""
    import os
    repo = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    hook = os.path.join(repo, ".claude", "hooks", "ready-work-at-turn-end.sh")
    with open(hook, encoding="utf-8") as fh:
        body = fh.read()
    live = [ln for ln in body.split("\n") if not ln.lstrip().startswith("#")]
    assert any("queue_view.py" in ln for ln in live), "the turn-end hook does not call queue_view.py"
    assert any("QUEUE_VIEW" in ln and "--check" in ln for ln in live), \
        "the hook does not run queue_view's --check"
