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


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE OTHER HALF OF THE PAIR (AUT-PD-171). `next_receipt` carried the discriminator from
# 2026-08-27; `next_entry_id`, the next allocator in the same file, did not, and it collided FIVE
# MEASURED TIMES on 2026-08-29 across three sessions — AUT-PD-169, 176, 177/178, 178, 179.
# ---------------------------------------------------------------------------------------------

def test_two_sessions_reading_the_same_ledger_get_different_entry_ids():
    """⛔⛔ THE COLLISION, REPRODUCED — the entry-id twin of the receipt test at the top of this file.
    Both sessions read one committed ledger, neither can see the other, neither yields. Under the
    old `max+1` derivation both were handed `AUT-PD-204`, and `priority.py` refuses a ledger with a
    duplicated id, so the loser's whole commit was blocked until it renumbered every reference by
    hand — measured five times on 2026-08-29, twice for the SAME two rows in one cycle."""
    entries = [{"id": "AUT-PD-203"}]
    id_a = I.next_entry_id("AUT-PD", entries, session_id=SESSION_A)
    id_b = I.next_entry_id("AUT-PD", entries, session_id=SESSION_B)
    assert id_a != id_b, (
        "two sessions were handed the same ledger id from identical committed state. Whoever "
        "pushes second is blocked and must renumber across five files and re-run a ~13.5-minute "
        "gate — which is the whole of what this defect cost.")
    assert I.duplicate_ids([{"id": id_a}, {"id": id_b}]) == {}, (
        "the two rows still collide once both land, so nothing was fixed")


def test_both_sessions_still_claim_the_same_entry_ordinal():
    """⚠ THE ORDINAL IS SHARED ON PURPOSE, exactly as it is for receipts, and this pins that it is a
    decision rather than an accident. Two cycles reading the same ledger ARE both the 204th filing
    anybody had committed when they started. What the record needs is for both to survive saying
    so — not for one to be renamed into a lie about its place."""
    entries = [{"id": "AUT-PD-203"}]
    a = I.parse_entry_id(I.next_entry_id("AUT-PD", entries, session_id=SESSION_A))
    b = I.parse_entry_id(I.next_entry_id("AUT-PD", entries, session_id=SESSION_B))
    assert a[:2] == b[:2] == ("AUT-PD", 204)
    assert a[2] != b[2] and a[2] == I.discriminator(SESSION_A)


def test_the_ordinal_advances_past_a_discriminated_id():
    """⛔⛔ THE ONE-OF-A-PAIR DEFECT THIS FIX COULD TRIVIALLY HAVE SHIPPED, and it is worse than the
    bug it replaces. Widening the MINT without widening the SCAN leaves the allocator's ordinal
    frozen at the last bare id forever, because a discriminated id no longer matches the pattern it
    counts — so the very next call, IN THE SAME SESSION, returns the id it just issued. That is not
    a cross-session race a rebase would catch: it is one session silently naming two different rows
    the same thing, in one file, with no second pusher to notice."""
    entries = [{"id": "AUT-PD-203"}]
    first = I.next_entry_id("AUT-PD", entries, session_id=SESSION_A)
    entries.append({"id": first})
    second = I.next_entry_id("AUT-PD", entries, session_id=SESSION_A)
    assert second != first, (
        f"the allocator issued {first} twice to one session — it cannot see its own last id")
    assert I.parse_entry_id(second)[1] == I.parse_entry_id(first)[1] + 1


def test_an_entry_id_is_refused_rather_than_minted_without_a_session(monkeypatch):
    """⛔ NOT A CLOCK, NOT A COUNTER, AND NOT A SILENT BARE ID — the same refusal `discriminator()`
    already makes for receipts. An allocator that quietly drops the discriminator when it cannot
    find a session hands back a collidable id while LOOKING like it solved the problem, and the
    collision then surfaces ~13.5 minutes later as somebody else's blocked push.
    ⚠ BOTH ENV FAULTS ARE TESTED SEPARATELY because they are different bugs in different places
    (AUT-PROP-034): unset is a sandbox or a bare `python3 -c`; exported-empty is a harness that set
    the variable to nothing, and `os.environ.get(X, default)` would hand back that empty string."""
    entries = [{"id": "AUT-PD-203"}]
    for bad in ("", "----"):
        with pytest.raises(ValueError):
            I.next_entry_id("AUT-PD", entries, session_id=bad)
    monkeypatch.delenv(I.SESSION_ENV, raising=False)
    with pytest.raises(ValueError) as unset:
        I.next_entry_id("AUT-PD", entries)
    assert "unset" in str(unset.value)
    monkeypatch.setenv(I.SESSION_ENV, "   ")
    with pytest.raises(ValueError) as empty:
        I.next_entry_id("AUT-PD", entries)
    assert "EXPORTED AND EMPTY" in str(empty.value), (
        "an exported-empty session id must not be reported as an absent one — the person who has "
        "to fix it needs to know which fault it is")


def test_the_session_is_read_from_the_environment_when_it_is_not_passed(monkeypatch):
    """⭐ THE DOCUMENTED CALL SITE IS TWO-ARGUMENT AND MUST GAIN THE FIX WITHOUT BEING REWRITTEN.
    `.claude/skills/research-loop/SKILL.md` §2 step 10 tells every cycle to call
    `ids.next_entry_id("AUT-PD", entries)`. Requiring a third argument would have left every cycle
    following the contract EXACTLY minting the old collidable id until the contract was edited —
    the writer/reader gap this repository has now lost four times (AUT-PD-146)."""
    monkeypatch.setenv(I.SESSION_ENV, SESSION_B)
    got = I.next_entry_id("AUT-PD", [{"id": "AUT-PD-203"}])
    assert got == f"AUT-PD-204-{I.discriminator(SESSION_B)}"


def test_the_discriminator_is_the_session_and_not_the_moment():
    """⛔ A CLOCK WOULD PASS EVERY OTHER TEST IN THIS FILE AND BE WRONG. Two calls by ONE session
    against ONE state describe one intended row, so they must name it identically; a timestamp or a
    counter would hand back two different ids for the same row and re-introduce, inside a single
    session, the ambiguity the discriminator exists to remove."""
    entries = [{"id": "AUT-PD-203"}]
    assert (I.next_entry_id("AUT-PD", entries, session_id=SESSION_A)
            == I.next_entry_id("AUT-PD", entries, session_id=SESSION_A))


def test_entry_ids_are_allocated_over_the_whole_ledger_not_by_eye():
    """The derivation is written down ONCE instead of being re-eyeballed by every session — which is
    how `AUT-PD-012` was issued twice by two cycles that never overlapped. ⛔ AND A PREFIX MUST NOT
    BLEED: `AUT`, `AUT-PD`, `AUT-PROP`, `AUT-BIX`, `AUT-COV`, `AUT-RT` and `AUT-INC` all live on the
    committed ledger, so an `AUT-PD` row must not advance the `AUT` counter."""
    entries = [{"id": "AUT-PD-001"}, {"id": "AUT-PD-012"}, {"id": "AUT-PROP-009"}, {"id": "AUT-078"}]
    def ordinal(prefix):
        return I.parse_entry_id(I.next_entry_id(prefix, entries, session_id=SESSION_A))[1]
    assert ordinal("AUT-PD") == 13
    assert ordinal("AUT-PROP") == 10
    assert ordinal("AUT") == 79, "an AUT-PD row advanced the AUT counter — the prefixes bled"
    assert ordinal("AUT-COV") == 1, "an unused prefix must start at 1"


def test_every_id_on_the_committed_ledger_still_parses():
    """⚠ THE NEW SHAPE MUST NOT BLIND A READER, which is the failure the receipt half already paid
    for: `session_reaper` carried its own `^CYC-\\d+\\.json$` and stopped seeing every new receipt.
    Both shapes are parsed by one regex, and the 344 committed rows are the corpus."""
    with open(LEDGER, encoding="utf-8") as fh:
        entries = json.load(fh)["entries"]
    assert entries, "no ledger entries found; this test would pass vacuously"
    unparsed = [e["id"] for e in entries if I.parse_entry_id(e.get("id")) is None]
    assert unparsed == [], f"ids on the committed ledger that no reader can parse: {unparsed}"
    assert I.parse_entry_id("AUT-PD-169") == ("AUT-PD", 169, None)
    assert I.parse_entry_id("AUT-PD-169-6b009680") == ("AUT-PD", 169, "6b009680")
    assert I.parse_entry_id("not-an-id") is None


def test_two_concurrent_filings_merge_without_a_renumber(monkeypatch):
    """⭐ THE HARM, END TO END. On 2026-08-29 both rows existed, both were correct, and the ledger
    that resulted was UNRANKABLE — `priority.py` refuses a duplicated id — so the second pusher
    renumbered across five files and re-ran the gate. Here the same two filings land in one ledger
    and the ranker reads it."""
    import priority as P
    real = P.build_ledger()
    committed = real["entries"]
    row_a = {"id": I.next_entry_id("AUT-PD", committed, session_id=SESSION_A)}
    row_b = {"id": I.next_entry_id("AUT-PD", committed, session_id=SESSION_B)}
    merged = committed + [row_a, row_b]
    assert I.duplicate_ids(merged) == {}, (
        "two concurrent filings against the REAL committed ledger still collide")
    monkeypatch.setattr(P, "build_ledger", lambda: dict(real, entries=merged))
    assert P.main(["--limit", "1"]) == 0, (
        "the ranker refused a ledger holding two concurrent filings — exit 3 is the duplicate-id "
        "refusal, and it is what blocked the loser's whole commit on 2026-08-29")


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
