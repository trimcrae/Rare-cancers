#!/usr/bin/env python3
"""Id allocation, asserted rather than agreed (AUT-PROP-013).

⛔⛔ THE DEFECT FIRED THREE TIMES IN ONE DAY AND ONLY THE THIRD ONE PROVES WHAT IT IS. Two sessions
~50 s apart both derived `CYC-0016`; the same hour, both filed `AUT-PROP-009` and `AUT-PROP-010` for
four different items. Those read as races. Then `AUT-PD-012` turned out to be used twice by two
process defects filed by SEQUENTIAL cycles — so the `max(committed) + 1` derivation collides on its
own, and every session computing it from the same committed state puts concurrency outside the
derivation by construction.

★ THE TWO HALVES DO DIFFERENT JOBS AND BOTH ARE TESTED HERE:
  allocation that cannot collide — because the ad-hoc tiebreak actually used that day ("claimed
  first, landed second, renumber yourself") required a human to NOTICE, and a session that pushes
  cleanly never does;
  a uniqueness assertion — the cheap half, which would have caught all three instances at the commit
  that created them.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import ids as I  # noqa: E402
import receipt_schema as R  # noqa: E402

LEDGER = os.path.join(os.path.dirname(HERE), "research-ledger.json")
RECEIPTS = os.path.join(os.path.dirname(HERE), "receipts")

SESSION_A = "6be7fd5a-28ea-50e3-8f4a-32e755af962a"
SESSION_B = "c1bc9340-1111-2222-3333-444455556666"


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE REGRESSION: two sessions, identical committed state, no negotiation.
# ---------------------------------------------------------------------------------------------

def test_two_sessions_reading_the_same_state_get_different_receipt_paths(tmp_path):
    """⛔⛔ THE COLLISION, REPRODUCED. Both sessions see the same receipts directory, neither can see
    the other, and neither yields. Under the old derivation both were handed `CYC-0016.json` and the
    second would have silently overwritten the first."""
    (tmp_path / "CYC-0015.json").write_text("{}", encoding="utf-8")
    id_a, path_a = I.next_receipt(str(tmp_path), SESSION_A)
    id_b, path_b = I.next_receipt(str(tmp_path), SESSION_B)
    assert path_a != path_b, (
        "two sessions were handed the same receipt path from identical state. A receipt is "
        "immutable committed history; one of them was about to be destroyed.")
    assert id_a != id_b


def test_both_sessions_still_claim_the_same_ordinal(tmp_path):
    """⚠ THE ORDINAL IS SHARED ON PURPOSE, and this pins that it is not an accident. Two concurrent
    cycles ARE both the sixteenth cycle anybody had committed when they started. What the record
    needs is for both to survive saying so — not for one to be renamed into a lie about its place."""
    (tmp_path / "CYC-0015.json").write_text("{}", encoding="utf-8")
    id_a, _ = I.next_receipt(str(tmp_path), SESSION_A)
    id_b, _ = I.next_receipt(str(tmp_path), SESSION_B)
    assert R.cycle_number(id_a) == R.cycle_number(id_b) == 16


def test_the_discriminator_comes_from_the_session_and_nowhere_else():
    """⛔ NOT A CLOCK, NOT A COUNTER. A timestamp collides when two sessions start in the same
    second, and a counter is the exact derivation that failed. A silent fallback to either would
    hand back a collidable id while looking like it had solved the problem."""
    with pytest.raises(ValueError):
        I.next_receipt("/nonexistent", "")
    with pytest.raises(ValueError):
        I.next_receipt("/nonexistent", "----")
    assert I.discriminator(SESSION_A) == "6be7fd5a"
    assert I.discriminator(SESSION_A) != I.discriminator(SESSION_B)


def test_a_receipt_is_never_silently_overwritten(tmp_path):
    """⚠ THIS TEST FAILED FIRST AND THE CODE WAS WRONG, NOT THE TEST. The module's first draft
    guarded `next_receipt()` with `os.path.exists` — unreachable, because the ordinal is max+1 and
    the path it returns can never already exist. The test said DID NOT RAISE, which is the only
    reason anybody saw it. A guard nobody can trigger measures nothing; the guarantee belongs at the
    WRITE, where a caller really can hand over an existing path, and `x` mode makes the filesystem
    enforce it instead of this module promising to."""
    first = I.write_receipt(str(tmp_path), SESSION_A, {"cycle_id": "x"})
    assert os.path.exists(first)
    with pytest.raises(FileExistsError):
        with open(first, "x", encoding="utf-8"):
            pass
    second = I.write_receipt(str(tmp_path), SESSION_A, {"cycle_id": "y"})
    assert second != first, "a second receipt in one session reused the first one's path"
    assert json.load(open(first, encoding="utf-8"))["cycle_id"] == "x", "the first receipt was clobbered"


def test_the_write_refuses_an_existing_path_even_when_the_allocator_is_wrong(tmp_path, monkeypatch):
    """⛔⛔ FOUND SURVIVING A MUTATION: changing `write_receipt`'s mode from `x` to `w` passed every
    other test here. It had to — the allocator advances the ordinal, so the honest flow never asks
    the write to overwrite anything, and the guarantee sat untested behind a correct caller.

    ★ THE POINT OF `x` IS THAT IT HOLDS WHEN THE ALLOCATOR IS WRONG, which is the entire failure
    class this module exists for: two sessions were handed one path by a derivation that could not
    see the other. So the allocator is forced to hand back a colliding path, exactly as the old max+1
    derivation did, and the filesystem is what must refuse.
    """
    monkeypatch.setattr(I, "next_receipt", lambda d, s: ("CYC-9999-fixed",
                                                         os.path.join(d, "CYC-9999-fixed.json")))
    first = I.write_receipt(str(tmp_path), SESSION_A, {"cycle_id": "first session"})
    with pytest.raises(FileExistsError):
        I.write_receipt(str(tmp_path), SESSION_B, {"cycle_id": "second session"})
    assert json.load(open(first, encoding="utf-8"))["cycle_id"] == "first session", (
        "the second session overwrote the first session's receipt — the exact harm measured on "
        "2026-08-27, where only a rebase collision made it visible at all")


# ---------------------------------------------------------------------------------------------
# The assertion half, and the file it was blind to for days.
# ---------------------------------------------------------------------------------------------

def test_the_committed_ledger_has_no_duplicate_ids():
    """⛔⛔ THE ONE THAT WOULD HAVE CAUGHT ALL THREE INSTANCES. `AUT-PD-012` sat duplicated on
    origin/main, filed by two sequential cycles, because nothing in this loop ever read a ledger
    looking for a repeated id. Two different items under one identity make every receipt, claim and
    evidence pointer naming it ambiguous."""
    with open(LEDGER, encoding="utf-8") as fh:
        entries = json.load(fh)["entries"]
    assert I.duplicate_ids(entries) == {}


def test_duplicate_ids_actually_detects_one():
    """The positive control. Without it the assertion above passes on a function that returns {}."""
    assert I.duplicate_ids([{"id": "A"}, {"id": "B"}, {"id": "A"}]) == {"A": 2}


def test_the_ranker_refuses_a_ledger_with_a_duplicated_id(tmp_path, monkeypatch, capsys):
    """⭐ REFUSED, NOT WARNED. If the ranker will read a duplicated ledger, the duplicate survives to
    the next cycle's queue — which is exactly how one lived on the trunk."""
    import priority as P
    monkeypatch.setattr(P, "build_ledger",
                        lambda: {"entries": [{"id": "AUT-PD-012"}, {"id": "AUT-PD-012"}],
                                 "n_clamped": 0})
    assert P.main([]) == 3
    err = capsys.readouterr().err
    assert "AUT-PD-012" in err and "used 2 times" in err


def test_entry_ids_are_allocated_over_the_whole_ledger_not_by_eye():
    """⚠ THIS HALF IS HONESTLY STILL max+1 AND THE TEST SAYS SO. Ledger entries merge through git, so
    a concurrent filing surfaces as a rebase conflict or is caught by the assertion above. The value
    is that the derivation is written down ONCE instead of re-eyeballed by every session — which is
    how `AUT-PD-012` was issued twice by two cycles that never overlapped."""
    entries = [{"id": "AUT-PD-001"}, {"id": "AUT-PD-012"}, {"id": "AUT-PROP-009"}, {"id": "AUT-078"}]
    assert I.next_entry_id("AUT-PD", entries) == "AUT-PD-013"
    assert I.next_entry_id("AUT-PROP", entries) == "AUT-PROP-010"
    assert I.next_entry_id("AUT-COV", entries) == "AUT-COV-001", "an unused prefix must start at 1"


# ---------------------------------------------------------------------------------------------
# History is not renumbered, and the readers still read it.
# ---------------------------------------------------------------------------------------------

def test_both_id_shapes_parse_for_every_reader():
    """⚠ THE NEW SHAPE MUST NOT BLIND THE RECEIPT SCHEMA. `cycle_number` decides which receipts the
    fan-out gate governs; if a discriminated id parsed as None, every new receipt would silently
    fall into the grandfathered set and the gate this repository just built would stop governing
    anything."""
    assert R.cycle_number("CYC-0016") == 16
    assert R.cycle_number("CYC-0024-6be7fd5a") == 24
    assert R.cycle_number("CYC-0000-BOOTSTRAP") == 0


def test_the_receipts_on_the_trunk_are_left_as_they_were():
    """⛔ A receipt is immutable committed history. Rewriting the old ones to LOOK collision-proof
    would be a fiction about what the record actually was — and this module's whole subject is
    records that quietly became something other than what they said."""
    names = sorted(n for n in os.listdir(RECEIPTS) if n.endswith(".json"))
    assert names, "no receipts found; this test would pass vacuously"
    ordinals = I.receipt_ordinals(RECEIPTS)
    assert len(ordinals) == len(names), "a receipt filename stopped carrying a readable ordinal"
