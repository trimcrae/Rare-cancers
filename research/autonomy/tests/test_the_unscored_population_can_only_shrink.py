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


# ⭐⭐ THE TWO GRANDFATHERING TESTS WERE DELETED 2026-09-01 BECAUSE THE BACKLOG THEY GUARDED IS GONE,
# AND THAT IS THIS RATCHET SUCCEEDING RATHER THAN BEING SWITCHED OFF. They asserted that an existing
# unscored row may still be edited, and that scoring one is admitted — both of which need a row with
# `score: None` to operate on. `n_unscored_open` is now 0, so each began raising StopIteration on its
# own `next(...)`: not a failure of the rule, an empty search.
# ⚠ THE REMEDY IS THE ONE WRITTEN AT THE SITE, NOT ONE INVENTED HERE. `test_the_population_is_not_
# already_empty` said in terms what to do when it went red: "the backlog is CLEARED: delete the
# grandfathering tests and assert `n_unscored_open == 0` instead." It is doing exactly that, so the
# deletion is the prescribed step rather than a convenience.
# ⛔ AND THE RULE ITSELF IS UNTOUCHED. R5 still refuses a NEW unscored row — every refusal test above
# builds its own row and still runs. What is gone is the allowance for pre-existing ones, which is
# the direction a ratchet is supposed to move: it can only tighten.


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


def test_the_population_is_empty_and_may_not_grow_again():
    """⭐ THE RATCHET'S END STATE, REACHED 2026-09-01. This asserted `n_unscored_open > 0` — a
    VACUITY guard, because every refusal test above builds its own row and would keep passing on an
    empty ledger, while the grandfathering tests assert nothing once the population is gone.

    ⚠ ITS OWN REMEDY IS WHAT WAS FOLLOWED: "When this goes red the backlog is CLEARED: delete the
    grandfathering tests and assert `n_unscored_open == 0` instead." It went red because the count
    reached zero, which is the outcome the rule existed to produce.
    ⛔ SO THE ASSERTION IS INVERTED, NOT REMOVED. Zero is now the required state, and a row that
    reappears unscored fails HERE as well as at R5 — the vacuity this test guarded against is
    replaced by a floor, so the suite still cannot pass on a ledger that quietly regrew a backlog.
    """
    n = _committed()["n_unscored_open"]
    assert n == 0, (
        f"the unscored-open population is back to {n}. R5 refuses a NEW unscored row, so this is "
        "either a row that slipped in before the rule, or the header is stale — regenerate with "
        "`python3 research/autonomy/priority.py --write` and, if it persists, score the row. The "
        "count only goes down.")
