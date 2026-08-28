#!/usr/bin/env python3
"""AUT-PD-014 — a progress-aware retry budget, ported from research/modalities/work_ledger.py.

⛔⛔ THE DEFECT THIS CLOSES: `priority.py` hardcoded `score_inputs["fruitless_attempts"] = 0` —
never computed — even though `priority-weights.json` already declares a real weight for it.
`research-ledger.json`'s `attempts` (a bare int) counted only EXPIRED LEASES, so a session that
claimed a row, worked it seriously, and released it having learned nothing left `attempts`
untouched. Nothing anywhere decremented or enforced `retry_budget`, so `handoff.py:top_items` and
`health.py:c_queue_is_takeable` were reading a field that was permanently `3`.

★ THE MODEL: `research/modalities/work_ledger.py:Entry.fruitless_attempts()` — a DIFFERENT ledger's
already-correct implementation, ported rather than copied because the schemas differ (that ledger's
`attempts` IS a list of per-dispatch records already; this one's `attempts` means something else, so
a NEW field, `dispatch_log`, carries the history here).

⛔ THE HONEST CAVEAT, PRESERVED RATHER THAN LOST: a progress-aware counter would NOT have penalised
AUT-PROP-002, which moved `last_evidence_utc` every cycle — see
`test_evidence_moving_every_cycle_never_accumulates_a_streak` below. **This defect did not cause the
three-cycle stall CYC-0015 found; it is a separate governance instrument that was inert.**
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
AUTONOMY = os.path.dirname(HERE)
sys.path.insert(0, AUTONOMY)

import priority as P  # noqa: E402
import claim as CL  # noqa: E402

W = json.load(open(os.path.join(AUTONOMY, "priority-weights.json"), encoding="utf-8"))


def _row(dispatch_log=None, last_evidence_utc=None, blocked_evidence=None, state="queued",
         score=100.0, **extra):
    row = {"id": "AUT-X", "state": state, "score": score,
           "last_evidence_utc": last_evidence_utc, "blocked_evidence": blocked_evidence,
           "dispatch_log": dispatch_log or []}
    row.update(extra)
    return row


def _attempt(fp):
    return {"utc": "2026-08-28T00:00:00Z", "fingerprint_at_dispatch": fp}


# ---------------------------------------------------------------------------------------------
# evidence_fingerprint — what "the evidence changed" means for one row
# ---------------------------------------------------------------------------------------------

def test_the_fingerprint_is_last_evidence_utc_and_blocked_evidence():
    row = _row(last_evidence_utc="2026-08-28T00:00:00Z", blocked_evidence="host refused")
    assert P.evidence_fingerprint(row) == "2026-08-28T00:00:00Z|host refused"


def test_two_untouched_rows_share_the_same_baseline_fingerprint():
    """Neither field ever set — the common case for a row nobody has claimed yet."""
    assert P.evidence_fingerprint(_row()) == P.evidence_fingerprint(_row())


# ---------------------------------------------------------------------------------------------
# fruitless_attempts_count — the core progress-aware property
# ---------------------------------------------------------------------------------------------

def test_a_never_dispatched_row_scores_zero():
    assert P.fruitless_attempts_count(_row()) == 0


def test_n_consecutive_dispatches_against_unchanged_evidence_count_as_n():
    """⛔⛔ THE CORE PROPERTY. Three claims, none of them ever changing what is known about the row —
    the exact shape of 'a route retried forever' this ledger item exists to make visible."""
    fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-20"))
    row = _row(last_evidence_utc="2026-08-20",
               dispatch_log=[_attempt(fp), _attempt(fp), _attempt(fp)])
    assert P.fruitless_attempts_count(row) == 3


def test_evidence_moving_every_cycle_never_accumulates_a_streak():
    """★★ THE HONEST CAVEAT, AS A TEST. AUT-PROP-002 moved `last_evidence_utc` every cycle — its
    fingerprint differs from every PRIOR dispatch's, so the streak resets to (at most) the single
    most recent attempt made against the CURRENT fingerprint, never accumulating. A progress-aware
    counter would not have penalised it, and this is why."""
    dates = ["2026-08-20", "2026-08-21", "2026-08-22", "2026-08-23"]
    log = [_attempt(P.evidence_fingerprint(_row(last_evidence_utc=d))) for d in dates[:-1]]
    row = _row(last_evidence_utc=dates[-1], dispatch_log=log)
    assert P.fruitless_attempts_count(row) == 0, (
        "a row whose evidence changes every cycle must never accumulate a fruitless streak")


def test_a_fruitless_run_resets_the_moment_evidence_moves():
    """Two fruitless dispatches, THEN a real advance, then one more dispatch against the NEW
    evidence: the count must reflect only the attempts made since the advance (one), not the two
    that preceded it — 'a dispatch that worked costs nothing' from every attempt before it."""
    old_fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    new_fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-15"))
    row = _row(last_evidence_utc="2026-08-15",
               dispatch_log=[_attempt(old_fp), _attempt(old_fp), _attempt(new_fp)])
    assert P.fruitless_attempts_count(row) == 1


def test_a_malformed_dispatch_log_entry_does_not_crash_the_counter():
    row = _row(last_evidence_utc="2026-08-20",
               dispatch_log=["not-a-dict", None, 42])
    assert P.fruitless_attempts_count(row) == 0


# ---------------------------------------------------------------------------------------------
# apply_fruitless_attempts — the wiring into score_inputs and retry_budget
# ---------------------------------------------------------------------------------------------

def test_a_closed_row_is_never_touched():
    """⛔ Mirrors `test_a_closed_row_never_ages_upward` for the age term. A row that is done,
    abandoned or superseded is not this function's business, however long its dispatch_log."""
    fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    for state in ("done", "abandoned", "superseded"):
        row = _row(state=state, score=10.0, last_evidence_utc="2026-08-01",
                   dispatch_log=[_attempt(fp)] * 5, retry_budget=3)
        P.apply_fruitless_attempts([row], W)
        assert row["score"] == 10.0, f"a {state} row's score moved"
        assert row["retry_budget"] == 3, f"a {state} row's retry_budget was recomputed"
        assert "fruitless_attempts" not in (row.get("score_inputs") or {})


def test_retry_budget_is_the_ceiling_minus_the_fruitless_count():
    fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    row = _row(last_evidence_utc="2026-08-01", dispatch_log=[_attempt(fp), _attempt(fp)])
    P.apply_fruitless_attempts([row], W)
    assert row["retry_budget"] == P.DEFAULT_RETRY_BUDGET - 2


def test_retry_budget_floors_at_zero_rather_than_going_negative():
    fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    row = _row(last_evidence_utc="2026-08-01",
               dispatch_log=[_attempt(fp)] * (P.DEFAULT_RETRY_BUDGET + 5))
    P.apply_fruitless_attempts([row], W)
    assert row["retry_budget"] == 0


def test_retry_budget_recovers_the_moment_evidence_moves():
    """★ Mirrors work_ledger.py's property 2: 'blocked is permanent until something changes, and
    something changes is mechanical'. Raise `last_evidence_utc` after a spent budget and the very
    next re-score must show budget again — nothing needs to clear it by hand."""
    old_fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    row = _row(last_evidence_utc="2026-08-01", dispatch_log=[_attempt(old_fp)] * P.DEFAULT_RETRY_BUDGET)
    P.apply_fruitless_attempts([row], W)
    assert row["retry_budget"] == 0
    row["last_evidence_utc"] = "2026-08-15"  # evidence advanced; no new dispatch yet
    P.apply_fruitless_attempts([row], W)
    assert row["retry_budget"] == P.DEFAULT_RETRY_BUDGET, (
        "an advance must free the row's retry budget without a human clearing anything by hand")


def test_the_input_is_echoed_on_a_derived_style_row():
    """Mirrors `test_the_input_is_echoed_so_a_reader_can_re_derive_the_score` for age_factor. A
    freshly-derived row's score_inputs carries no prior fruitless_attempts, so the full term lands
    once, cleanly."""
    fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    row = _row(last_evidence_utc="2026-08-01", dispatch_log=[_attempt(fp), _attempt(fp)],
               score=100.0, score_inputs={"fruitless_attempts": 0})
    P.apply_fruitless_attempts([row], W)
    w = W["terms"]["fruitless_attempts"]["weight"]
    assert row["score_inputs"]["fruitless_attempts"] == 2
    assert row["score"] == round(100.0 + w * 2, 2)


def test_a_hand_filed_rows_score_does_not_compound_across_re_scores():
    """⛔⛔ THE AUT-PROP-036 SHAPE, POINTED AT THIS TERM. A hand-filed row's `score` and
    `score_inputs` persist across re-scores (unlike a derived row's, which `build_entries` rebuilds
    fresh every time). Running `apply_fruitless_attempts` twice in a row on the SAME unchanged
    dispatch_log must not add the term twice."""
    fp = P.evidence_fingerprint(_row(last_evidence_utc="2026-08-01"))
    row = _row(last_evidence_utc="2026-08-01", dispatch_log=[_attempt(fp)], score=50.0,
               kind="process_defect")  # no score_inputs at all, like a real hand-filed row
    P.apply_fruitless_attempts([row], W)
    once = row["score"]
    P.apply_fruitless_attempts([row], W)  # a second re-score against the identical dispatch_log
    assert row["score"] == once, "re-scoring an unchanged row applied the penalty a second time"


# ---------------------------------------------------------------------------------------------
# wiring: build_ledger actually calls this, before the sort
# ---------------------------------------------------------------------------------------------

def test_the_scorer_actually_calls_apply_fruitless_attempts():
    """⛔⛔ THE UNREACHABLE-GUARD TEST, same shape as `test_the_scorer_actually_calls_it` for
    age_factor. This repository has shipped a governed weight nothing read before."""
    import inspect
    src = inspect.getsource(P.build_ledger)
    assert "apply_fruitless_attempts" in src, "build_ledger never applies the fruitless-attempts term"
    assert src.index("apply_fruitless_attempts") < src.index("entries.sort"), (
        "the term is applied AFTER the sort, so it cannot change the order")


def test_apply_fruitless_attempts_runs_after_merge_so_history_is_visible():
    """The function needs `dispatch_log`, which only exists on a MERGED entry (a freshly-derived one
    from `build_entries` never carries it). Calling it before `merge()` would always see nothing."""
    import inspect
    src = inspect.getsource(P.build_ledger)
    assert src.index("merge(") < src.index("apply_fruitless_attempts"), (
        "apply_fruitless_attempts runs before merge() ever populates dispatch_log")


# ---------------------------------------------------------------------------------------------
# claim.py — the write side: a claim stamps the dispatch at the honest moment
# ---------------------------------------------------------------------------------------------

def _write_ledger(path, entries):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"entries": entries}, fh)


def test_a_claim_stamps_dispatch_log_with_the_fingerprint_at_that_moment(tmp_path):
    path = str(tmp_path / "ledger.json")
    _write_ledger(path, [{"id": "AUT-X", "state": "queued",
                          "last_evidence_utc": "2026-08-20", "blocked_evidence": None}])
    CL.apply_claim(path, "AUT-X", "CYC-TEST", "2026-08-28T00:00:00Z")
    with open(path, encoding="utf-8") as fh:
        row = json.load(fh)["entries"][0]
    assert row["dispatch_log"] == [{
        "utc": "2026-08-28T00:00:00Z",
        "fingerprint_at_dispatch": "2026-08-20|None",
    }]
    assert row["owner"] == "CYC-TEST" and row["state"] == "in_progress"


def test_two_claims_against_unmoved_evidence_both_land_in_the_history(tmp_path):
    """A row claimed, released (by whatever released it — this test does not need to know how), and
    claimed again with nothing having changed: `fruitless_attempts_count` must see two."""
    path = str(tmp_path / "ledger.json")
    _write_ledger(path, [{"id": "AUT-X", "state": "queued",
                          "last_evidence_utc": "2026-08-20", "blocked_evidence": None}])
    CL.apply_claim(path, "AUT-X", "CYC-ONE", "2026-08-28T00:00:00Z")
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    d["entries"][0]["owner"] = None  # simulate a plain release: nothing else changed
    _write_ledger(path, d["entries"])
    CL.apply_claim(path, "AUT-X", "CYC-TWO", "2026-08-28T04:00:00Z")
    with open(path, encoding="utf-8") as fh:
        row = json.load(fh)["entries"][0]
    assert P.fruitless_attempts_count(row) == 2


def test_a_claim_made_after_a_real_advance_does_not_inherit_the_old_streak(tmp_path):
    path = str(tmp_path / "ledger.json")
    _write_ledger(path, [{"id": "AUT-X", "state": "queued",
                          "last_evidence_utc": "2026-08-20", "blocked_evidence": None}])
    CL.apply_claim(path, "AUT-X", "CYC-ONE", "2026-08-28T00:00:00Z")
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    row = d["entries"][0]
    row["owner"] = None
    row["last_evidence_utc"] = "2026-08-27"  # a real advance happened before the next claim
    _write_ledger(path, d["entries"])
    CL.apply_claim(path, "AUT-X", "CYC-TWO", "2026-08-28T04:00:00Z")
    with open(path, encoding="utf-8") as fh:
        row = json.load(fh)["entries"][0]
    assert P.fruitless_attempts_count(row) == 1, (
        "the dispatch made against the OLD evidence must not count toward the streak once the "
        "evidence has moved")
