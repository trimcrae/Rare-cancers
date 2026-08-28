#!/usr/bin/env python3
"""A described map edit must still resolve once the edit is applied THE WAY THIS REPO REQUIRES (AUT-068).

⛔⛔ THE DEFECT. `map_edits_required` decides PENDING by asking "is the text I meant to replace still in
the file?". CLAUDE.md rule 1.2 requires a corrected passage to CARRY its superseded wording —
"Superseded, retained: '<the old sentence>'" — so applying an edit correctly leaves `current_text`
findable, and the row reports PENDING forever. Measured 2026-08-28 on the live tree: all four remaining
PENDING rows were false, and one had been applied weeks earlier.

Two more shapes fail the same way and are pinned here because each was found only by fixing the one
before it:

  * AN ADDITIVE EDIT'S ANCHOR SURVIVES ITS OWN APPLICATION. `RT-TCIP.artifacts` proposes
    `"ART-TCIP-REACH"` -> `"ART-TCIP-REACH", "ART-TCIP-EFFECTOR-ARMS"`. The old string is a SUBSTRING of
    the new one, so it is present before and after alike and the row could never reach APPLIED.
  * A MULTI-LINE NEEDLE CANNOT MATCH A LINE-AT-A-TIME SEARCH. That same proposal spans two lines, so the
    applied check could only ever answer no.

⚠ AND THE ORDERING BUG IS PINNED SEPARATELY, because the fix for the last one was written correctly and
still did nothing: `_strip_emphasis` collapses whitespace, newlines included, so a multi-line needle stops
looking multi-line the moment it is normalised. The branch existed, read correctly, and never ran.
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import nr4a3_tcip_reach as T  # noqa: E402


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(T, "REPO", str(tmp_path))
    return tmp_path


def _write(repo, name, text):
    (repo / name).write_text(text, encoding="utf-8")
    return name


# ---------------------------------------------------------------------------------------------
# 1 · the supersession quote is not a live anchor
# ---------------------------------------------------------------------------------------------

def test_live_part_stops_at_the_supersession_marker():
    assert T._live_part("the new claim. Superseded, retained: 'the old claim'") == "the new claim. "
    assert T._live_part("no marker here") == "no marker here"


def test_text_quoted_inside_a_supersession_note_is_not_a_live_anchor(repo):
    f = _write(repo, "doc.md", "R9 and R10 survive unchanged.\n"
                               "Superseded, retained: \"so it retires R9\".\n")
    assert T._anchor_check(f, "so it retires R9", live_only=True)["current_text_found"] is False


def test_the_same_text_OUTSIDE_a_supersession_note_still_is_one(repo):
    """⛔ THE NEGATIVE CONTROL. If this passes vacuously the fix has deleted the check rather than
    narrowed it, and a genuinely owed edit would report as done."""
    f = _write(repo, "doc.md", "the route is bivalent so it retires R9 outright.\n")
    got = T._anchor_check(f, "so it retires R9", live_only=True)
    assert got["current_text_found"] is True and got["line"] == 1


def test_live_only_is_opt_in_so_the_applied_check_still_sees_the_whole_line(repo):
    f = _write(repo, "doc.md", "Superseded, retained: \"so it retires R9\".\n")
    assert T._anchor_check(f, "so it retires R9")["current_text_found"] is True


# ---------------------------------------------------------------------------------------------
# 2 · the multi-line needle
# ---------------------------------------------------------------------------------------------

def test_a_multiline_needle_matches_across_lines_ignoring_indentation(repo):
    f = _write(repo, "g.json", '{\n  "artifacts": [\n      "A-REACH",\n      "A-ARMS"\n  ]\n}\n')
    got = T._anchor_check(f, '"A-REACH",\n    "A-ARMS"', normalise=True)
    assert got["current_text_found"] is True
    assert got["matched_across_lines_ignoring_whitespace"] is True


def test_multiline_is_detected_BEFORE_normalisation(repo):
    """⚠ THE ORDERING BUG ITSELF. `_strip_emphasis` collapses the newline, so a check written after it
    never sees a multi-line needle. This asserts the branch actually runs under `normalise=True`, which
    is the only way the real caller invokes it."""
    assert "\n" not in T._strip_emphasis('"A",\n  "B"'), (
        "_strip_emphasis no longer collapses newlines; this test's premise needs rechecking")
    f = _write(repo, "g.json", '[\n  "A",\n  "B"\n]\n')
    got = T._anchor_check(f, '"A",\n    "B"', normalise=True)
    assert got["current_text_found"] is True, (
        "the multi-line branch did not run under normalise=True — it is being decided on the "
        "already-collapsed needle again")


def test_a_multiline_needle_that_is_genuinely_absent_still_reports_absent(repo):
    f = _write(repo, "g.json", '[\n  "A"\n]\n')
    assert T._anchor_check(f, '"A",\n    "B"', normalise=True)["current_text_found"] is False


# ---------------------------------------------------------------------------------------------
# 3 · the additive anchor, and the row it must NOT break
# ---------------------------------------------------------------------------------------------

def _edit(current, proposed, fname="g.json"):
    return {"file": fname, "anchor": "x", "current_text": current, "proposed_text": proposed}


def _state(repo, monkeypatch, text, current, proposed):
    _write(repo, "g.json", text)
    monkeypatch.setattr(T, "_map_edits", lambda census, summary: [_edit(current, proposed)])
    return T.map_edits_required({}, {})[0]["state"]


def test_an_additive_edit_reads_APPLIED_once_its_addition_is_present(repo, monkeypatch):
    assert _state(repo, monkeypatch, '[\n  "A-REACH",\n  "A-ARMS"\n]\n',
                  '"A-REACH"', '"A-REACH",\n    "A-ARMS"') == "APPLIED"


def test_an_additive_edit_not_yet_applied_is_still_PENDING(repo, monkeypatch):
    assert _state(repo, monkeypatch, '[\n  "A-REACH"\n]\n',
                  '"A-REACH"', '"A-REACH",\n    "A-ARMS"') == "PENDING"


def test_an_uninformative_anchor_with_no_positive_applied_reading_stays_PENDING(repo, monkeypatch):
    """⛔ THE ROW THE FIRST VERSION OF THIS FIX BROKE. `closure_kind` proposes `open — NO EDIT REQUIRED`
    against a current text of `open`, so it is additive too. Ignoring the anchor outright dropped it to
    STALE_ANCHOR — the one state that fails the build — for a row whose whole point is that nothing is
    owed. PENDING is the direction that loses nothing."""
    assert _state(repo, monkeypatch, '{"closure_kind": "open"}\n',
                  'open', 'open — NO EDIT REQUIRED') == "PENDING"


def test_a_genuinely_stale_anchor_is_still_STALE_ANCHOR(repo, monkeypatch):
    """⛔ The state that fails the build must survive all three narrowings, or they have bought a green
    board by deleting the alarm."""
    assert _state(repo, monkeypatch, '{"unrelated": 1}\n', 'gone', 'also gone') == "STALE_ANCHOR"


def test_an_edit_applied_WITH_its_supersession_note_reads_APPLIED_not_PENDING(repo, monkeypatch):
    """⛔⛔ THE END-TO-END CASE, AND THE ONE THE UNIT TESTS ABOVE DO NOT COVER. Found by mutation:
    unwiring `live_only=True` from `map_edits_required`'s PENDING check left every test above green,
    because they all call `_anchor_check` directly and pass the flag themselves. What must be pinned is
    that the STATE MACHINE asks the live-only question — otherwise the helper is correct and unused,
    which is how this repository's guards usually die.

    This is the real shape: the graph note now carries the new claim AND, as rule 1.2 requires, the
    sentence it retired."""
    _write(repo, "g.json",
           '{"note": "they alone carry the paired size comparison. '
           'Superseded, retained: \'no effector arm is staged in this repository.\'"}\n')
    monkeypatch.setattr(T, "_map_edits", lambda census, summary: [
        _edit("no effector arm is staged in this repository",
              "they alone carry the paired size comparison")])
    assert T.map_edits_required({}, {})[0]["state"] == "APPLIED", (
        "an edit applied with its mandated supersession note still reads as owed — the state machine "
        "is not asking the live-only question")
