#!/usr/bin/env python3
"""The open-unscored population may only SHRINK, and the write path is what makes that true
(AUT-PD-145, entry condition 1; the defect is AUT-PD-050's).

⛔⛔ THE DEFECT: THE FILING REQUIREMENT WAS WRITTEN IN THREE PLACES AND ENFORCED IN NONE.
`research-ledger.json`'s own `_role` says an entry a session adds must carry a `score` and a
`_score_basis` (or a `prerequisite_of`); `admissibility.py --report`'s closing sentence says the
same; AUT-PD-050 measured the cost. Nothing checked it. Measured on the committed ledger
2026-08-28 across all 32 ledger commits in the observable trunk history (17:26-20:34): total
236 -> 260, unscored 73 -> 97, **24 of the 24 rows filed in that window carried no score, and no
pre-existing unscored row has ever acquired one.** Re-measured 2026-08-29 by CYC-0073-d4ccfde4 on
286 rows: 108 unscored, 85 of them open. This is the agreement-in-prose class this repository keeps
paying for — AUT-PD-013's fan-out key, AUT-PROP-013's ids, AUT-PD-037's serialization — and the
remedy is the same one every time: put the predicate on the write path, not in a sentence.

⭐⭐ WHY A RATCHET AND NOT A CEILING, WHICH IS THE HALF THAT HELD AUT-PD-050's GUARD BACK FOR A DAY.
`MAX_UNSCORED_OPEN` was written, mutation-tested and then deliberately NOT merged, because the
population (82) had already passed the proposed ceiling (80): landing it would have turned the trunk
RED for whichever session committed next, on a gate it did not cause. A ceiling on a population
nothing stops from growing is not reachable — it is an outage with a deadline. So this suite
enforces the DERIVATIVE instead: membership is grandfathered, entry is refused, and the set can only
fall. That is what makes a pinned ceiling land green later rather than red immediately.

⛔ ENTRY HAS THREE DOORS AND THE RULE CLOSES ALL THREE. A row can be APPENDED unscored; a committed
row's `score` can be REMOVED; a committed unscored row that was CLOSED — and so exempt — can be
REOPENED. Each ends with one more row nothing can rank. Closing only the first would be the
one-of-a-pair defect class `paper-hardening` names, of which this repository has now found seven.

⚠ WHAT THIS SUITE CANNOT SEE, said rather than left to be discovered: it does not shrink the 85 rows
already on the trunk, and it cannot. Those are cleared by scoring them, one row at a time, and
`n_unscored_open` is the number that says whether that is happening.
"""

from __future__ import annotations

import copy
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import admissibility as A  # noqa: E402
import ledger_io  # noqa: E402

LEDGER = os.path.join(AUTONOMY, "research-ledger.json")
CLOSED = ("done", "abandoned", "superseded")


def _committed() -> dict:
    with open(LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture()
def baseline(tmp_path):
    """A real committed ledger on disk, so every write below is checked against a real baseline."""
    data = _committed()
    path = tmp_path / "research-ledger.json"
    ledger_io.write_ledger(path, data, check=False)
    return path, data


def _write(path, data):
    ledger_io.write_ledger(path, data)


def _refusal_ids(exc) -> set:
    return {ln.split()[1] for ln in str(exc).splitlines()
            if ln.strip().startswith(A.REFUSED_UNSCORED_NEW)}


def _refusal_reason(exc, rid: str) -> str:
    """The `why` line the gate printed for one row.

    ⛔ ASSERTED SEPARATELY FROM THE VERDICT BECAUSE A MUTANT SURVIVED ON EXACTLY THAT GAP.
    Measured 2026-08-29 (CYC-0073-d4ccfde4): disabling the score-removal branch left the write
    still REFUSED — it fell through to the reopened-exemption message — so a suite asserting only
    that the row was refused passed while the gate handed back the wrong remedy. The two doors
    prescribe different fixes ("re-derive the score" vs "give it a score in the same write"), so
    the reason is part of the behaviour, not decoration.
    """
    lines = str(exc).splitlines()
    for i, ln in enumerate(lines):
        parts = ln.split()
        if len(parts) >= 2 and parts[0] == A.REFUSED_UNSCORED_NEW and parts[1] == rid:
            return lines[i + 1].strip() if i + 1 < len(lines) else ""
    raise AssertionError(f"{rid} was not refused by {A.REFUSED_UNSCORED_NEW}:\n{exc}")


# ---------------------------------------------------------------------------------------------
# The rule fires on all three doors.
# ---------------------------------------------------------------------------------------------

def test_an_appended_row_with_no_score_is_refused(baseline):
    path, data = baseline
    after = copy.deepcopy(data)
    after["entries"].append({"id": "AUT-TEST-APPEND", "state": "queued", "what": "x"})
    with pytest.raises(A.InadmissibleWrite) as exc:
        _write(path, after)
    assert "AUT-TEST-APPEND" in _refusal_ids(exc.value)
    assert "appended with no `score`" in _refusal_reason(exc.value, "AUT-TEST-APPEND")


def test_removing_a_committed_score_is_refused(baseline):
    """⛔ The bypass a rule written only against APPENDS would have left wide open."""
    path, data = baseline
    after = copy.deepcopy(data)
    victim = next(e for e in after["entries"]
                  if e.get("score") is not None and (e.get("state") or "queued") not in CLOSED)
    victim["score"] = None
    with pytest.raises(A.InadmissibleWrite) as exc:
        _write(path, after)
    assert victim["id"] in _refusal_ids(exc.value)
    assert "is removed by this write" in _refusal_reason(exc.value, victim["id"])


def test_reopening_a_closed_unscored_row_is_refused(baseline):
    """⛔ The second bypass: file it unscored-and-done today, flip it to queued tomorrow."""
    path, data = baseline
    after = copy.deepcopy(data)
    victim = next(e for e in after["entries"]
                  if e.get("score") is None and (e.get("state") or "queued") in CLOSED)
    victim["state"] = "queued"
    with pytest.raises(A.InadmissibleWrite) as exc:
        _write(path, after)
    assert victim["id"] in _refusal_ids(exc.value)
    assert "ends that exemption" in _refusal_reason(exc.value, victim["id"])


# ---------------------------------------------------------------------------------------------
# The three documented ways to file are all still admitted — the rule must not become a wall.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("extra", [
    {"score": 42.0, "_score_basis": "hand-filed against AUT-PD-145"},
    {"prerequisite_of": "AUT-025"},
    {"state": "done"},
], ids=["scored", "prerequisite_of", "closed"])
def test_the_documented_filings_are_admitted(baseline, extra):
    path, data = baseline
    after = copy.deepcopy(data)
    row = {"id": "AUT-TEST-OK", "state": "queued", "what": "x"}
    row.update(extra)
    after["entries"].append(row)
    _write(path, after)  # must not raise
    assert json.loads(path.read_text(encoding="utf-8"))["entries"][-1]["id"] == "AUT-TEST-OK"


def test_the_committed_ledger_still_writes_through_the_gate(baseline):
    """⛔⛔ THE ONE THAT DECIDES WHETHER THIS SHIPS AT ALL. 85 open rows on the trunk carry no
    score. A rule that refused them would red the commit loop for whichever session committed next,
    on a gate it did not cause — which is exactly why AUT-PD-050's ceiling was held back. Membership
    is grandfathered; only entry is refused."""
    path, data = baseline
    _write(path, data)


#: The id of the unscored row the two grandfathering tests below inject into their own baseline.
GRANDFATHERED_FIXTURE_ID = "AUT-GRANDFATHERED-FIXTURE"


@pytest.fixture()
def grandfathered(tmp_path):
    """A baseline that CONTAINS one unscored open row — constructed, never found.

    ⛔⛔ THIS FIXTURE EXISTS BECAUSE THE BACKLOG HIT ZERO AND TOOK TWO TESTS WITH IT (2026-09-02).
    Both tests used to do `next(e for e in after["entries"] if e.get("score") is None and ...)`,
    searching the LIVE ledger for a grandfathered row. `n_unscored_open` is now 0, so both raised
    `StopIteration` — the ratchet succeeding broke the tests that guard it.

    ★ AND DELETING THEM WOULD HAVE BEEN THE WRONG FIX, THOUGH THE SUITE ITSELF SUGGESTED IT. R5 is
    live code in `admissibility.py`: an existing unscored row must stay editable, and giving it a
    score must be admitted, or the gate is a trap rather than a ratchet. A rule whose test is deleted
    because its subject got rare is a rule that ships unguarded. Constructing the row keeps R5 under
    test at every population size, zero included.

    ⚠ The baseline is written with `check=False` precisely so it may hold a state the gate would
    refuse to CREATE — which is the definition of a grandfathered row. `n_unscored_open` is bumped
    to match so the fixture is self-consistent rather than describing itself wrongly.
    """
    data = copy.deepcopy(_committed())
    donor = next(e for e in data["entries"]
                 if e.get("score") is not None and (e.get("state") or "queued") not in CLOSED)
    row = copy.deepcopy(donor)
    row["id"] = GRANDFATHERED_FIXTURE_ID
    for field in ("score", "_score_basis", "score_inputs"):
        row.pop(field, None)
    data["entries"].append(row)
    data["n_unscored_open"] = (data.get("n_unscored_open") or 0) + 1
    path = tmp_path / "research-ledger.json"
    ledger_io.write_ledger(path, data, check=False)
    return path, data


def _the_grandfathered_row(data):
    return next(e for e in data["entries"] if e.get("id") == GRANDFATHERED_FIXTURE_ID)


def test_a_grandfathered_row_may_still_be_edited(grandfathered):
    """An existing unscored row is not frozen — it is simply not allowed to have COMPANY."""
    path, data = grandfathered
    after = copy.deepcopy(data)
    row = _the_grandfathered_row(after)
    # ⚠ `what` ONLY. Touching `last_evidence_utc` here trips R4 (the echoed `score_inputs.age_factor`
    # stops matching the row's own date) — a real, separate rule, and letting it fire in this test
    # would make a green run mean "R4 is quiet" rather than "R5 grandfathers this row".
    row["what"] = (row.get("what") or "") + " (edited)"
    _write(path, after)


def test_scoring_a_grandfathered_row_is_admitted(grandfathered):
    """The remedy has to be reachable, or the gate is a trap rather than a ratchet."""
    path, data = grandfathered
    after = copy.deepcopy(data)
    row = _the_grandfathered_row(after)
    row["score"] = 37.0
    row["_score_basis"] = "hand-filed while clearing the unscored backlog"
    after["n_unscored_open"] = (after.get("n_unscored_open") or 1) - 1
    _write(path, after)


# ---------------------------------------------------------------------------------------------
# The edges the rule must NOT fire on.
# ---------------------------------------------------------------------------------------------

def test_a_first_write_with_no_baseline_is_not_refused(tmp_path):
    """⛔ THE ONE PLACE THIS RULE STAYS SILENT, AND IT IS DELIBERATE. With no committed ledger every
    row reads as newly appended, so the rule cannot tell growth from the population it exists to
    grandfather. It defers rather than refusing the whole file — the opposite of the stance the
    unreadable-baseline case takes, because there the baseline exists and is being ignored."""
    ledger_io.write_ledger(tmp_path / "research-ledger.json", _committed())


def test_a_closed_row_may_be_appended_unscored(baseline):
    """A row filed already-done is never offered to a session and never ranked, so it is not part
    of the population and never was."""
    path, data = baseline
    after = copy.deepcopy(data)
    after["entries"].append({"id": "AUT-TEST-DONE", "state": "done", "what": "already finished"})
    _write(path, after)


# ---------------------------------------------------------------------------------------------
# The gate and the number it is pinned to must agree.
# ---------------------------------------------------------------------------------------------

def test_the_predicate_matches_the_number_priority_publishes():
    """⛔ ONE FACT, ONE PLACE. `priority.py` publishes `n_unscored_open` into the artifact and this
    gate decides membership; if the two ever disagree, the ratchet is guarding a different set from
    the one the ceiling will be pinned to. They are computed differently on purpose — the counter
    does not test `prerequisite_of`, because no unscored row has ever carried one — so this asserts
    the agreement rather than assuming it, and goes red the day that stops being true."""
    ledger = _committed()
    entries = [e for e in ledger["entries"] if isinstance(e, dict)]
    mine = {e["id"] for e in entries if A.is_unscored_open(e)}
    assert len(mine) == ledger["n_unscored_open"], (
        f"the gate counts {len(mine)} open-unscored rows, the artifact publishes "
        f"{ledger['n_unscored_open']}. A row carrying BOTH `prerequisite_of` and no `score` would "
        "do this — decide which definition is right and make the other follow it.")


def test_the_refusal_is_a_refusal():
    """A verdict that is not in `REFUSALS` is a label, not a gate: `refuse_inadmissible_write`
    reports it and `check_write` writes the file anyway."""
    assert A.REFUSED_UNSCORED_NEW in A.REFUSALS


def test_the_population_is_empty_and_stays_empty():
    """⭐ THE RATCHET REACHED ITS TERMINAL VALUE ON 2026-09-02 AND THIS NOW HOLDS IT THERE.

    ⚠ SUPERSEDED, RETAINED — this test used to read `assert _committed()["n_unscored_open"] > 0`,
    under the docstring: *"VACUITY. Every refusal test above builds its own row, so this suite would
    keep passing on an empty ledger — but the grandfathering tests, which are the ones that decide
    whether the rule can ship, assert nothing at all once the population is gone. When this goes red
    the backlog is CLEARED: delete the grandfathering tests and assert `n_unscored_open == 0`
    instead."* It went red as designed. `MAX_UNSCORED_OPEN` was 69 when the ratchet shipped; the
    measured population is now 0 across 344 entries.

    ⛔ THE VACUITY WARNING IT CARRIED IS NOT DISCHARGED BY THE BACKLOG CLEARING — it is discharged by
    the grandfathering tests now CONSTRUCTING their row instead of finding one, so they still decide
    whether R5 can ship. Had they simply been deleted as that docstring suggested, this suite would
    have become exactly the vacuous thing it warned about: every remaining test builds its own row,
    and nothing would exercise the live grandfathering branch at all.

    ⛔ AND `== 0` IS STRICTLY STRONGER THAN `> 0` WAS. Any regression — a row appended with no score,
    a score removed from an open row — moves the number off zero and fails here immediately, rather
    than being absorbed silently under a ceiling.
    """
    assert _committed()["n_unscored_open"] == 0, (
        "the unscored population is no longer empty. A row was appended without a score or had its "
        "score removed; find it with `python3 research/autonomy/priority.py` and score it, and do "
        "NOT raise a ceiling to admit it.")
