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


@pytest.fixture(autouse=True)
def _forget_issued_ids():
    """⚠ `ids._ISSUED` IS PROCESS-SCOPED AND PYTEST IS ONE PROCESS. Without this, every test in this
    file would inherit the ordinals the previous test minted, and an assertion about `AUT-PD-204`
    would depend on how many tests ran before it — which is a test nobody can read and a red build
    nobody can diagnose. ⛔ It resets BEFORE each test and never during one: the requirement-1 tests
    below depend on the memory accumulating within a single test body."""
    I.forget_issued_ids()
    yield
    I.forget_issued_ids()


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
    # ⚠ TIGHTENED FOR AUT-085, NOT LOOSENED: the discriminator is now `<session>-<process>`, so this
    # asserts the session half is STILL exactly `discriminator(SESSION_A)` AND that a process half
    # follows it. The old one-sided equality would now pass a fix that dropped the session half.
    assert a[2] != b[2]
    assert a[2].startswith(I.discriminator(SESSION_A) + "-")
    assert b[2].startswith(I.discriminator(SESSION_B) + "-")


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
    # ⚠ TIGHTENED FOR AUT-085 (see above): prefix, ordinal and the SESSION half are all still pinned
    # exactly; the process half is pinned by shape because it is a property of the running process.
    assert got.startswith(f"AUT-PD-204-{I.discriminator(SESSION_B)}-")
    assert I.parse_entry_id(got)[:2] == ("AUT-PD", 204)


def test_the_discriminator_is_the_session_and_the_process_and_not_the_moment():
    """⛔ A CLOCK WOULD PASS ALMOST EVERY OTHER TEST IN THIS FILE AND BE WRONG, and this is where
    that is caught now.

    ⚠ SUPERSEDED, RETAINED (CLAUDE.md rule 1.2). This test used to assert the anti-clock property
    THROUGH `next_entry_id` — *"Two calls by ONE session against ONE state describe one intended
    row, so they must name it identically"* — and on 2026-09-02 that assertion became FALSE ON
    PURPOSE: AUT-086 measured three rows minted in one comprehension all receiving
    `AUT-086-e71cf460`, so the allocator must now advance on every call. ⛔ The old sentence was not
    wrong about clocks; it was reading the anti-clock property off the wrong function. It lives here
    instead, on the DISCRIMINATOR, where a clock would actually enter — and the two properties are
    now independent rather than in tension: the discriminator is stable, the ordinal advances."""
    import time
    first = I.allocator_discriminator(session_id=SESSION_A)
    time.sleep(0.01)
    assert I.allocator_discriminator(session_id=SESSION_A) == first, (
        "the discriminator moved between two calls in one process — it is reading a clock, and a "
        "clock collides whenever two allocators start in the same tick")
    assert first == f"{I.discriminator(SESSION_A)}-{I.process_discriminator()}"


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
    # ⛔ AUT-085 WIDENED `ENTRY_ID` AND THESE FIVE IDS WERE ALREADY COMMITTED WHEN IT DID. A schema
    # change that orphans a committed id is a worse bug than the collision it fixes, so each is
    # pinned to the EXACT tuple it parsed to before the widening — a `require_parseable` reader
    # (`ledger_schema.id_problems`) rejects the row outright if any of them stops matching.
    for rid, want in (("AUT-PD-204-d7df5340", ("AUT-PD", 204, "d7df5340")),
                      ("AUT-082-e71cf460", ("AUT", 82, "e71cf460")),
                      ("AUT-083-e71cf460", ("AUT", 83, "e71cf460")),
                      ("AUT-084-e71cf460", ("AUT", 84, "e71cf460")),
                      ("AUT-085-e71cf460", ("AUT", 85, "e71cf460")),
                      ("AUT-086-e71cf460", ("AUT", 86, "e71cf460")),
                      ("AUT-087-e71cf460", ("AUT", 87, "e71cf460")),
                      ("AUT-088-e71cf460", ("AUT", 88, "e71cf460"))):
        assert I.parse_entry_id(rid) == want, f"{rid} was committed and no longer parses as it did"
    assert I.parse_entry_id("AUT-085-e71cf460-1f6aab97") == ("AUT", 85, "e71cf460-1f6aab97")


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


# ---------------------------------------------------------------------------------------------
# ⛔⛔ AUT-085 / AUT-086 — THREE FAILURE MODES, TWO MECHANISMS, AND NEITHER SUBSTITUTES FOR THE
# OTHER. `ids.__doc__` carries the table; these are its assertions.
#   1  one process, minted twice before appending  -> `_ISSUED`   (AUT-086, three ids in one row set)
#   2  two concurrent seats of one session         -> process half (AUT-085, subagent inherits the
#                                                                   parent's CLAUDE_CODE_SESSION_ID)
#   3  two sessions on one committed ledger        -> session half (AUT-PD-171, five occurrences)
# ---------------------------------------------------------------------------------------------

def test_three_mints_in_one_comprehension_get_three_names():
    """⛔⛔ REQUIREMENT 1, IN THE EXACT SHAPE THAT PRODUCED IT, AND IT IS THE ONLY ONE OF THE THREE
    THIS LEDGER HAS RECORDED A REAL DUPLICATE FOR. On 2026-09-02 three rows were built in one list
    comprehension, each calling `ids.next_entry_id("AUT", entries)`, none appended until the
    comprehension finished — and all three were handed `AUT-086-e71cf460`. `duplicate_ids` returned
    `{'AUT-086-e71cf460': 3}`.
    ⛔ NO CONCURRENCY IS INVOLVED, WHICH IS WHY NO TOKEN FIXES IT: a session id, a subagent id and a
    pid are all CONSTANT within one process. The ordinal is derived from a list that has not grown,
    so the second call re-derives the first call's answer."""
    # ⛔ THE SESSION ID IS PASSED, NOT READ FROM THE ENVIRONMENT. `next_entry_id` raises when
    # `CLAUDE_CODE_SESSION_ID` is unset, and it is unset on a CI runner — so as written this test
    # asserted nothing about the allocator on the one machine that runs it on every push, and
    # failed with a ValueError about the environment instead. ⚠ MEASURED on the trunk 2026-09-02
    # (run 33618666310, `cannot allocate a ledger id: CLAUDE_CODE_SESSION_ID is unset`). The
    # requirement under test is that three mints before any append get three ADVANCING names; the
    # source of the discriminator is not part of it, and the sibling test below already passes one.
    entries = [{"id": "AUT-085"}]
    rows = [{"id": I.next_entry_id("AUT", entries, session_id=SESSION_A)} for _ in range(3)]
    assert I.duplicate_ids(rows) == {}, (
        "a caller that minted three ids before appending any of them was handed one name more than "
        "once — 'append first' is a convention, and this is what conventions are worth")
    assert [I.parse_entry_id(r["id"])[1] for r in rows] == [86, 87, 88], (
        "the allocator must ADVANCE on each call, not merely differ: two rows filed in one batch "
        "have to sort in the order they were created")


def test_the_allocator_advances_even_when_the_caller_never_appends():
    """⭐ THE SAME REQUIREMENT AT THE UNIT LEVEL, and it pins that the advance comes from the
    ALLOCATOR'S OWN MEMORY rather than from anything the caller did. `entries` is never mutated
    here — asserted, because a fix that worked by appending to the caller's list would pass the
    test above while corrupting a real ledger with placeholder rows."""
    entries = [{"id": "AUT-PD-203"}]
    before = list(entries)
    got = [I.next_entry_id("AUT-PD", entries, session_id=SESSION_A) for _ in range(4)]
    assert len(set(got)) == 4, f"the allocator repeated itself within one process: {got}"
    assert [I.parse_entry_id(g)[1] for g in got] == [204, 205, 206, 207]
    assert entries == before, "the allocator mutated the caller's list to make itself safe"


def test_the_memory_is_the_name_and_not_the_ordinal():
    """⚠ THE KEYING IS LOAD-BEARING AND THE OBVIOUS ALTERNATIVE BREAKS A DELIBERATE PROPERTY.
    `_ISSUED` holds full ids, so two SESSIONS minting in one process still both claim ordinal 204 —
    which is the whole "both survive saying so" trade the discriminator exists to make. Keyed on
    `(prefix, ordinal)` instead, the second session would be pushed to 205 and renamed into a lie
    about its place, silently, with every test above still green."""
    entries = [{"id": "AUT-PD-203"}]
    a = I.parse_entry_id(I.next_entry_id("AUT-PD", entries, session_id=SESSION_A))
    b = I.parse_entry_id(I.next_entry_id("AUT-PD", entries, session_id=SESSION_B))
    assert a[1] == b[1] == 204, (
        "a second SESSION was pushed off the ordinal it legitimately shares — the in-process memory "
        "is keyed on the ordinal rather than on the name")


def test_two_subagents_of_one_session_get_different_entry_ids():
    """⛔⛔ REQUIREMENT 2, REPRODUCED WITH REAL PROCESSES BECAUSE THAT IS WHAT THE DEFECT IS.
    Measured 2026-09-02: the driver read discriminator `e71cf460`; a subagent it dispatched read
    `e71cf460`. A subagent inherits `CLAUDE_CODE_SESSION_ID` verbatim, so among the seats of a
    five-wide fan-out — this repository's standing work pattern — the session half is a CONSTANT and
    `next_entry_id` degraded to `max(committed) + 1`, the derivation AUT-PD-171 was closed for
    removing.
    ⚠ TWO REAL SUBPROCESSES, NOT A MONKEYPATCH: `_ISSUED` would mask this defect inside one process,
    so a same-process test of it would pass no matter what the discriminator did."""
    import subprocess
    src = (
        "import json,os,sys;sys.path.insert(0,%r);import ids;"
        "print(ids.next_entry_id('AUT-PD',[{'id':'AUT-PD-203'}]))" % os.path.dirname(HERE))
    env = dict(os.environ, CLAUDE_CODE_SESSION_ID=SESSION_A, CLAUDE_CODE_CHILD_SESSION="1")
    procs = [subprocess.Popen([sys.executable, "-c", src], env=env, stdout=subprocess.PIPE,
                              text=True) for _ in range(2)]
    got = [pr.communicate()[0].strip() for pr in procs]
    assert all(got), f"a seat produced no id at all: {got!r}"
    assert got[0] != got[1], (
        f"two concurrent seats of ONE session were both handed {got[0]} — the discriminator "
        "separates sessions and not the allocators inside one")
    for g in got:
        assert g.startswith(f"AUT-PD-204-{I.discriminator(SESSION_A)}-"), (
            f"{g} lost the session half; an id must still say WHICH SESSION produced it")


def test_the_process_half_separates_two_allocators_carrying_one_session():
    """⭐ THE SAME REQUIREMENT AT THE UNIT LEVEL, with the two process identities named explicitly so
    the failure message says which component stopped mattering."""
    one = I.process_discriminator((4321, "3190737", "79f70063-bdfd-49cf-879d-2fe32e5758c1"))
    two = I.process_discriminator((4322, "3190737", "79f70063-bdfd-49cf-879d-2fe32e5758c1"))
    assert one != two, "two live pids produced one discriminator — the pid is not being read"
    reused_pid = I.process_discriminator((4321, "9999999", "79f70063-bdfd-49cf-879d-2fe32e5758c1"))
    assert reused_pid != one, (
        "a REUSED pid produced the same discriminator. `pid_max` in this container is 32768 and this "
        "session burned ~1180 pids/hour, so a wraparound is ~28h of one session away — the start "
        "time is what makes a reused pid a different identity")
    rebooted = I.process_discriminator((4321, "3190737", "00000000-0000-0000-0000-000000000000"))
    assert rebooted != one, (
        "a (pid, start) pair repeated after a restart produced the same discriminator — the tick "
        "counter restarts at boot, so the pair alone CAN repeat and the boot id is what separates it")


def test_the_process_identity_is_the_running_process():
    """⚠ A POPULATED FIELD IS NOT A MEASURED ONE (CLAUDE.md §4). `process_identity()` must read the
    real `/proc` entry rather than return a plausible-looking constant, so the pid is checked against
    `os.getpid()` and the start time against an independent parse of the same file."""
    pid, start, boot = I.process_identity()
    assert pid == os.getpid()
    with open(f"/proc/{pid}/stat", encoding="utf-8") as fh:
        fields = fh.read().split()
    assert start == fields[21], (
        f"the start time {start!r} is not field 22 of /proc/{pid}/stat ({fields[21]!r})")
    assert start.isdigit() and int(start) > 0
    assert len(boot) == 36, f"the boot id is not a UUID: {boot!r}"


def test_the_process_half_is_refused_rather_than_invented():
    """⛔ THE SAME REFUSAL `discriminator()` MAKES, AT THE NEW COMPONENT — because a component that
    silently degrades to a constant re-introduces the whole defect while LOOKING fixed, which is the
    one outcome worse than the bug.
    ⚠ AND THIS GUARD IS REACHABLE, which is the bar the first draft of `write_receipt` failed: its
    unreachable `os.path.exists` check failed its own test with DID NOT RAISE. A caller passing an
    override is the path."""
    for bad in ((), (None, "1", "b"), ("4321", "1", "b"), (0, "1", "b"), (-1, "1", "b"),
                (True, "1", "b")):
        with pytest.raises(ValueError):
            I.process_discriminator(bad)


def test_the_child_flag_is_not_an_identity(monkeypatch):
    """⛔ `CLAUDE_CODE_CHILD_SESSION` WAS OBSERVED AS THE LITERAL `1` AND MUST NOT BE BUILT ON. It
    separates a child from its parent and never a child from its sibling, so an allocator reading it
    would hand one discriminator to every seat of a fan-out and look fixed doing it.
    ⚠ Measured over the whole environment on 2026-09-02: nothing the harness exports separates one
    seat from another. `CLAUDE_PID` is the shared harness process — every seat's shell is a direct
    child of it — and `CLAUDE_CODE_MESSAGING_SOCKET` names that same pid."""
    a = I.process_discriminator((4321, "1", "b"))
    b = I.process_discriminator((4322, "1", "b"))
    assert a != b, "two seats differing only in pid must not share a discriminator"
    for flag in ("1", "0", ""):
        monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", flag)
        assert I.process_discriminator((4321, "1", "b")) == a, (
            "the discriminator moved when only the child FLAG changed — it is reading a flag as an "
            "identity, and a flag is the same for every seat")


def test_the_session_half_is_kept_and_not_replaced():
    """⭐ THE SHAPE DECISION, PINNED. `<session>-<process>`, session first: the process half could
    have replaced the session half and satisfied uniqueness on its own, and it would have thrown
    away the only provenance an id carries. `e71cf460` greps back to a session; a process hash greps
    back to nothing.
    ⚠ Order is not cosmetic either — session first keeps every row this session mints sorting and
    grepping together with the ones already committed under `AUT-085-e71cf460`."""
    got = I.allocator_discriminator(session_id=SESSION_A)
    head, _, tail = got.partition("-")
    assert head == I.discriminator(SESSION_A), "the session half is gone; the id lost its provenance"
    assert tail == I.process_discriminator()
    assert len(head) == I.DISCRIMINATOR_LEN and len(tail) == I.DISCRIMINATOR_LEN
    minted = I.next_entry_id("AUT", [{"id": "AUT-085"}], session_id=SESSION_A)
    assert minted.startswith(f"AUT-086-{I.discriminator(SESSION_A)}-")


def test_the_ordinal_advances_past_a_two_segment_discriminated_id():
    """⛔ THE ONE-OF-A-PAIR DEFECT AT THE NEW SHAPE — the same one `test_the_ordinal_advances_past_a
    _discriminated_id` pins for the old one. Widening the MINT without widening the SCAN freezes the
    ordinal at the last id the scan can still read, so the allocator re-issues it forever."""
    entries = [{"id": "AUT-PD-203-e71cf460-1f6aab97"}]
    got = I.next_entry_id("AUT-PD", entries, session_id=SESSION_A)
    assert I.parse_entry_id(got)[1] == 204, (
        f"{got}: the scan cannot read a two-segment discriminated id, so the ordinal froze")


def test_the_receipt_half_of_the_pair_is_unfixed_and_fails_loud(tmp_path):
    """⚠ THE PAIR, STATED HONESTLY RATHER THAN QUIETLY FIXED OR QUIETLY IGNORED. `next_receipt`
    takes the SESSION only, so two seats of one session compute the same receipt PATH — the same
    defect AUT-085 names for entry ids. It is left alone here because its blast radius is other
    people's files (`RECEIPT_ID`, `session_reaper`, `receipt_schema`, `health`) and because it fails
    LOUD where the entry-id half failed SILENT: `write_receipt` opens with mode `x`, so the second
    seat gets `FileExistsError` instead of overwriting the first.
    ⛔ This test pins the loudness. If mode `x` is ever relaxed, the receipt half becomes a silent
    overwrite and this goes red — which is the only reason it is safe to leave unfixed."""
    seat_a, path_a = I.next_receipt(str(tmp_path), SESSION_A)
    seat_b, path_b = I.next_receipt(str(tmp_path), SESSION_A)
    assert (seat_a, path_a) == (seat_b, path_b), (
        "the receipt half gained a per-allocator discriminator without this test being updated — "
        "good news, but the pair is then FIXED and this test is describing history, not the trunk")
    # ⭐ The loudness itself is pinned by `test_the_write_refuses_an_existing_path_even_when_the_
    # allocator_is_wrong` at the top of this file, which drives `write_receipt` at a path that
    # already exists. This test's whole content is that the two seats agree on that path.
