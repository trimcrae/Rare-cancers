"""A bounded wait bonus — nothing starves, and nothing rides age to the top.

⛔⛔ THE FINDING, 3-0 AGAINST ATTEMPTED REFUTATION (the 2026-08-27 `/deep-research` pass): **no
verified orchestrator implements any anti-starvation mechanism.** Every shipped default is
priority-then-FIFO or bare FIFO — no ageing, no quota, no wait-time bound. AlabOS is a two-pass
stable sort on (submitted_at, priority) and greps clean for
`starvation|starve|aging|ageing|fairness|round-robin`. This ledger had the same defect and the same
symptom: 70+ queued rows with several filed weeks earlier and never taken.

★ THE SHAPE IS SLURM'S AND THE BOUND IS THE POINT. An unbounded age term does not fix a starving
queue, it INVERTS it into pure FIFO — a live patient-facing route would sit behind a stale one purely
for being younger. Half these tests exist to hold the ceiling, not the rescue.
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

TODAY = datetime.date(2026, 8, 28)
W = json.load(open(os.path.join(os.path.dirname(HERE), "priority-weights.json"), encoding="utf-8"))


def _row(days_ago, score=100.0, state="queued"):
    d = (TODAY - datetime.timedelta(days=days_ago)).isoformat()
    return {"id": "X", "state": state, "score": score, "last_evidence_utc": d}


def test_a_fresh_row_gains_nothing():
    assert priority.age_factor(_row(0), W, today=TODAY) == 0.0


def test_the_factor_rises_with_the_wait():
    a = priority.age_factor(_row(3), W, today=TODAY)
    b = priority.age_factor(_row(7), W, today=TODAY)
    assert 0 < a < b < 1.0


def test_it_SATURATES_and_that_is_the_whole_design():
    """⛔ The ceiling. Without it the queue becomes FIFO and a live route waits behind a stale one."""
    at = priority.age_factor(_row(14), W, today=TODAY)
    way_past = priority.age_factor(_row(900), W, today=TODAY)
    assert at == 1.0 and way_past == 1.0, "the age factor is unbounded — the queue will invert"


def test_the_bonus_cannot_outrank_a_live_route():
    """⚠ The arithmetic that makes the ceiling meaningful rather than decorative: a fully-aged row
    gains less than the live and patient_path terms can carry, so age BREAKS TIES and rescues the
    forgotten — it never promotes a stale row over a live patient-facing one."""
    age_w = W["terms"]["age"]["weight"]
    live_w = W["terms"]["live"]["weight"]
    # ⚠ `patient_path_scale` carries a `_why` string beside its numbers — the repo's convention for
    # keeping the reasoning next to the weight. Filter to numerics; the first version of this test
    # compared a str to a float and failed for its own reason rather than the code's.
    scale = [v for v in W["patient_path_scale"].values() if isinstance(v, (int, float))]
    patient = max(scale) * W["terms"]["patient_path"]["weight"]
    assert age_w < live_w + patient, (
        f"a fully-aged row gains {age_w}, which is not less than what a live patient-facing route "
        f"carries ({live_w} + {patient}) — age can now outrank relevance")


def test_a_closed_row_never_ages_upward():
    """⛔ Ageing finished work is how a ranker starts recommending things that are already done."""
    for state in ("done", "abandoned", "superseded"):
        rows = [_row(900, score=10.0, state=state)]
        priority.apply_age_factor(rows, W, today=TODAY)
        assert rows[0]["score"] == 10.0, f"a {state} row gained an age bonus"


def test_an_unreadable_date_buys_nothing():
    for bad in (None, "", "   ", "not-a-date", 20260828, {"utc": "2026-08-01"}):
        assert priority.age_factor({"last_evidence_utc": bad}, W, today=TODAY) == 0.0


def test_a_future_date_buys_nothing():
    """A clock skew or a typo must not mint score."""
    assert priority.age_factor(_row(-30), W, today=TODAY) == 0.0


def test_an_unreadable_saturation_disables_the_term_rather_than_dividing_by_zero():
    missing = {k: v for k, v in W.items() if k != "age_saturates_days"}
    assert priority.age_factor(_row(900), missing, today=TODAY) == 0.0, \
        "a weights file with no saturation key still aged a row"
    for bad in ({"value": 0}, {"value": -1}, {"value": "14"}, {"value": None}, {}):
        w = dict(W); w["age_saturates_days"] = bad
        assert priority.age_factor(_row(900), w, today=TODAY) == 0.0, \
            f"age_saturates_days={bad!r} was accepted as a ceiling"


def test_the_input_is_echoed_so_a_reader_can_re_derive_the_score():
    rows = [_row(7, score=100.0)]
    priority.apply_age_factor(rows, W, today=TODAY)
    assert rows[0]["score_inputs"]["age_factor"] == 0.5
    assert rows[0]["score"] == round(100.0 + W["terms"]["age"]["weight"] * 0.5, 1)


def test_the_scorer_actually_calls_it():
    """⛔⛔ THE UNREACHABLE-GUARD TEST. This repository has shipped a governed constant no code read
    for a fortnight, an exempt flag nothing consulted, and a watchdog wired to an env var that does
    not exist. A term the ranker never applies is worse than no term: it looks solved."""
    import inspect
    src = inspect.getsource(priority.build_ledger)
    assert "apply_age_factor" in src, "build_ledger never applies the age factor"
    assert src.index("apply_age_factor") < src.index("entries.sort"), \
        "the age factor is applied AFTER the sort, so it cannot change the order"


def test_the_ceiling_is_read_from_the_weights_not_typed_in_code():
    import inspect
    src = inspect.getsource(priority.age_factor)
    assert "age_saturates_days" in src
    assert "14" not in src.replace("2026-08-2", ""), "the saturation is typed into the code"
