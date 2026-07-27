"""The step-1 fan-out's cumulative REALISED-spend cap.

WHY IT EXISTS. Until 2026-07-27 the only thing gating this lane was the per-unit rate line
($0.006539/ns). Realised spend was measured and printed on every tick, and nothing ever refused on it.
That gap became acute when placement turned self-replenishing under `always()`: the tick re-rents to
target width on every pass, and a per-unit rate check is passed *individually* by every cheap host.
Fifteen hosts each comfortably under the line is exactly the shape that drains a budget while every row
reads green.

The three properties that make the cap trustworthy, each pinned below:
  1. the ceiling is DERIVED from the cost model, never typed (CLAUDE.md rule 1);
  2. the realised total counts rentals that are IN FLIGHT BUT NOT YET RECONCILED — `billed_min` is 0
     until a later collect writes it, so a cap fed `ledger_cost` alone would read green while over;
  3. a breach HOLDS and never destroys — the gate acts at the moment of renting and has no reach over a
     live host.
"""
import calendar
import time

import pytest

import congeneric_fanout as cf
import congeneric_fanout_vast as cfv


def _utc(epoch):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


NOW = calendar.timegm((2026, 7, 27, 20, 0, 0, 0, 0, 0))


def test_ceiling_is_derived_from_the_cost_model_not_typed():
    """A ladder re-anchor must move the cap with it. Same function the per-tick gate already prices on."""
    _r, ceiling, _h, _b, detail = cfv.spend_cap_state({"rentals": {}}, n_units=19, now_epoch=NOW)
    assert ceiling == round(float(cf.market_ceiling_usd(19)), 2)
    assert detail["n_units_authorised"] == 19
    # and it is not accidentally equal to some other rung's number
    assert ceiling != round(float(cf.market_ceiling_usd(18)), 2)


def test_an_unreconciled_rental_still_counts():
    """THE POINT OF THE WHOLE THING. `billed_min` is 0 until a collect reconciles it.

    A box rented two hours ago by a tick that has not been followed by a collect contributes $0 to
    `ledger_cost`. If the cap read that, it would authorise more renting on the strength of spend it
    simply had not looked at yet.
    """
    doc = {"rentals": {"1": {"bid": 0.20, "billed_min": 0, "launched_utc": _utc(NOW - 2 * 3600),
                             "last_seen_utc": None, "unit_id": "u1"}}}
    plain, _n, _rows, _unpriced = cfv.ledger_cost(doc)
    assert plain == 0.0, "the old accounting is blind to it — this is the bug being fixed"
    accrued, rows, n_accruing = cfv.ledger_cost_accrued(doc, live_ids=["1"], now_epoch=NOW)
    assert accrued == pytest.approx(0.40, abs=0.01), "2 h at $0.20/hr must be counted"
    assert n_accruing == 1 and rows[0]["open"] is True


def test_a_closed_rental_is_frozen_and_does_not_run_away():
    """Reconciled + no longer live -> `billed_min` is authoritative.

    Without this a finished fleet would inflate forever and wedge the lane against its own ceiling, which
    is its own bug: §6 names a hold nobody can clear as a failure mode, not a safety property.
    """
    doc = {"rentals": {"1": {"bid": 0.20, "billed_min": 30, "launched_utc": _utc(NOW - 10 * 3600),
                             "last_seen_utc": _utc(NOW - 9 * 3600), "unit_id": "u1"}}}
    total, rows, n_accruing = cfv.ledger_cost_accrued(doc, live_ids=[], now_epoch=NOW)
    assert total == pytest.approx(0.10, abs=0.001), "30 min at $0.20/hr, frozen — not 10 hours"
    assert n_accruing == 0 and rows[0]["open"] is False


def test_accrual_is_bounded_by_the_lane_runtime_cap():
    """A rental whose box died without ever being reconciled must not accrue without bound."""
    doc = {"rentals": {"1": {"bid": 1.0, "billed_min": 0, "launched_utc": _utc(NOW - 500 * 3600),
                             "last_seen_utc": None, "unit_id": "u1"}}}
    total, _rows, _n = cfv.ledger_cost_accrued(doc, live_ids=[], now_epoch=NOW)
    assert total == pytest.approx(cfv.MAX_RUNTIME_S / 3600.0, abs=0.01)


def test_the_recorded_figure_wins_when_it_is_larger():
    """Accrual may never REDUCE a measured total — `max`, not `replace`."""
    doc = {"rentals": {"1": {"bid": 0.20, "billed_min": 600, "launched_utc": _utc(NOW - 1 * 3600),
                             "last_seen_utc": None, "unit_id": "u1"}}}
    total, _rows, _n = cfv.ledger_cost_accrued(doc, live_ids=["1"], now_epoch=NOW)
    assert total == pytest.approx(2.0, abs=0.01), "10 recorded hours beat 1 accrued hour"


def test_breach_is_detected_on_the_accrued_total_not_the_recorded_one():
    """The whole failure mode in one assertion: green on the old total, breached on the honest one."""
    ceiling = float(cf.market_ceiling_usd(19))
    # Fifteen live hosts, none reconciled, together past the ceiling. Held to 12 h each — comfortably
    # inside the lane's MAX_RUNTIME_S accrual bound, so this test exercises the BREACH and not the bound
    # (an earlier draft picked ~21 h and was silently clamped, which made a working cap look broken).
    hours_each = 12.0
    rate = (ceiling / (15.0 * hours_each)) * 1.2
    doc = {"rentals": {str(i): {"bid": rate, "billed_min": 0,
                                "launched_utc": _utc(NOW - int(hours_each * 3600)),
                                "last_seen_utc": None, "unit_id": f"u{i}"} for i in range(15)}}
    assert cfv.ledger_cost(doc)[0] == 0.0, "every row reads green under the old accounting"
    realised, ceil2, headroom, breached, _d = cfv.spend_cap_state(
        doc, live_ids=[str(i) for i in range(15)], n_units=19, now_epoch=NOW)
    assert breached is True
    assert realised > ceil2 and headroom < 0


def test_headroom_is_reported_when_under():
    doc = {"rentals": {"1": {"bid": 0.20, "billed_min": 60, "launched_utc": _utc(NOW - 3600),
                             "last_seen_utc": _utc(NOW), "unit_id": "u1"}}}
    realised, ceiling, headroom, breached, _d = cfv.spend_cap_state(
        doc, live_ids=[], n_units=19, now_epoch=NOW)
    assert breached is False
    assert headroom == pytest.approx(ceiling - realised, abs=0.01)


def test_spend_cap_hold_is_a_named_decision_distinct_from_price_hold():
    """A cap breach and a thin market are different problems with opposite remedies.

    A price hold clears by itself when the board improves; this one never does. Rendering them alike is
    exactly the readout defect CLAUDE.md §1 legislates against.
    """
    assert "spend_cap_hold" in cfv.PLACEMENT_DECISIONS
    assert cfv.PLACEMENT_DECISIONS["spend_cap_hold"] != cfv.PLACEMENT_DECISIONS["price_hold"]
    assert "REALISED" in cfv.PLACEMENT_DECISIONS["spend_cap_hold"]


def test_an_unreadable_ledger_fails_closed():
    """A gate that opens when its evidence disappears is worse than no gate.

    `_load_ledger` swallows every S3 error into an empty doc, so realised spend would read $0 and the cap
    would report full headroom during an outage. Measured for real while verifying the cap: an
    `InvalidAccessKeyId` on the lane's bucket produced a confident "realised $0.0, headroom $74.91,
    breached=False". `load_ledger_strict` must raise instead — the caller holds.
    """
    class _Boom:
        def get_object(self, **_kw):
            raise RuntimeError("An error occurred (InvalidAccessKeyId) when calling GetObject")

    with pytest.raises(RuntimeError, match="unreadable"):
        cfv.load_ledger_strict(_Boom(), "some-bucket")

    # …but a genuinely ABSENT ledger is not an error: a lane that never rented has none.
    class _Missing:
        def get_object(self, **_kw):
            e = RuntimeError("nope")
            e.response = {"Error": {"Code": "NoSuchKey"}}
            raise e

    assert cfv.load_ledger_strict(_Missing(), "b") == {"rentals": {}}


def test_the_cap_never_destroys_anything():
    """STRUCTURAL: the breach branch must hold and return, never reach a teardown path.

    Asserted against the source rather than by mocking a fleet, because the property being protected is
    'this code path cannot reach a destroy', and the cheapest honest proof of that is that no destroy
    call appears between the breach and its return. Work already executing is never touched — the gate
    acts at the moment of renting.
    """
    import inspect
    src = inspect.getsource(cfv.mode_launch)
    i = src.index("if _cap_breached:")
    branch = src[i:src.index("# ⛔ THE $/ns MARKET GUARD", i)]
    for forbidden in ("destroy", "_reap", "DELETE", ".stop("):
        assert forbidden not in branch, f"the spend cap must not {forbidden!r} — it holds, it does not kill"
    assert "record_no_placement(" in branch and "return" in branch


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
