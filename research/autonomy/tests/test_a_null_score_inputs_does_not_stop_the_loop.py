#!/usr/bin/env python3
"""`apply_age_factor` must survive every shape `score_inputs` is actually written in (AUT-PD-152).

⛔⛔ THE OUTAGE THIS PINS. `AUT-COV-001`, filed by CYC-0011, carries `"score_inputs": null`. The read
two lines above the write was already defensive (`(e.get("score_inputs") or {})`), but the write was
`e.setdefault("score_inputs", {})["age_factor"] = f` — and `setdefault` RETURNS THE EXISTING VALUE
when the key is present, so on that row it evaluated `None["age_factor"] = f`.

★ THE TRIGGER WAS THE CALENDAR, WHICH IS WHY NO COMMIT LOOKS GUILTY. `if not f and not prev:
continue` skipped the row for as long as its age factor rounded to zero. The date rolling to
2026-08-29 made it non-zero for the first time and `priority.py --write` — step 3 of EVERY cycle —
started crashing on state nobody had touched.

⛔ AND IT DEADLOCKED RATHER THAN MERELY FAILED. With the re-score dead, `admissibility.check_write`
refuses every ledger write as `refused_stale_input`, because the stored age factors no longer match
the date. So a cycle could not re-score AND could not claim, and each failure blocked the other's
fix. A test per shape is cheap; an unrankable ledger stops the loop.

⚠ `null` IS NOT `absent`, and that distinction is the whole bug. AUT-PD-050 fixed crashes in this
same function and this one survived it.
"""

from __future__ import annotations

import datetime
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import priority  # noqa: E402

TODAY = datetime.date(2026, 8, 29)


def _row(score_inputs, **kw):
    r = {"id": "AUT-COV-001", "state": "queued", "last_evidence_utc": "2026-08-01", "score": 10.0}
    if score_inputs is not _ABSENT:
        r["score_inputs"] = score_inputs
    r.update(kw)
    return r


_ABSENT = object()


@pytest.fixture()
def weights():
    return priority.load_weights()


def _apply(row, weights):
    return priority.apply_age_factor([row], weights, today=TODAY)[0]


def test_a_null_score_inputs_does_not_crash(weights):
    """⛔ THE REGRESSION. This raised TypeError: 'NoneType' object does not support item assignment."""
    out = _apply(_row(None), weights)
    assert isinstance(out["score_inputs"], dict)
    assert out["score_inputs"]["age_factor"] > 0


def test_an_absent_score_inputs_still_works(weights):
    out = _apply(_row(_ABSENT), weights)
    assert out["score_inputs"]["age_factor"] > 0


def test_an_existing_dict_is_updated_in_place_and_keeps_its_other_keys(weights):
    out = _apply(_row({"other": "kept"}), weights)
    assert out["score_inputs"]["other"] == "kept"
    assert out["score_inputs"]["age_factor"] > 0


@pytest.mark.parametrize("junk", ["", 0, [], "not-a-dict"])
def test_a_score_inputs_that_is_not_a_dict_is_replaced_not_indexed(weights, junk):
    """Any non-dict must be replaced. Indexing a str or a list raises just as surely as None."""
    out = _apply(_row(junk), weights)
    assert isinstance(out["score_inputs"], dict)
    assert out["score_inputs"]["age_factor"] > 0


def test_a_null_score_inputs_is_treated_as_prev_zero_not_as_an_error(weights):
    """⭐ The delta must be the FULL term: a row with no readable previous factor has had none
    applied, exactly like a derived row. Getting this wrong would double-count the bonus."""
    w = weights["age"]["weight"] if "age" in weights else None
    null_row = _apply(_row(None), weights)
    absent_row = _apply(_row(_ABSENT), weights)
    assert null_row["score"] == absent_row["score"]
    assert null_row["score"] > 10.0
    if isinstance(w, (int, float)):
        assert null_row["score"] == round(10.0 + w * null_row["score_inputs"]["age_factor"], 1)


def test_a_closed_row_is_still_never_aged(weights):
    """⛔ Ageing finished work is how a ranker starts recommending things already done."""
    out = _apply(_row(None, state="done"), weights)
    assert out.get("score_inputs") is None
    assert out["score"] == 10.0


def test_the_live_ledger_re_scores_without_crashing():
    """★ The end-to-end property, run against the REAL ledger: it must be rankable whatever the
    date is. A unit test over a synthetic row would not have caught this one, because the row that
    broke the loop was real state nobody had touched."""
    path = os.path.join(os.path.dirname(HERE), "research-ledger.json")
    with open(path, encoding="utf-8") as fh:
        entries = json.load(fh)["entries"]
    for day in (TODAY, TODAY + datetime.timedelta(days=400)):
        priority.apply_age_factor([dict(e) for e in entries], priority.load_weights(), today=day)
