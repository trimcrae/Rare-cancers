#!/usr/bin/env python3
"""A pattern nobody records is a pattern nobody can act on — and a count that can block is a blacklist.

Both halves matter. On 2026-07-29 the ternary lane rented four hosts in 36 minutes (machines 29711, 28164,
12227, 41950), every one refused on start, every board read cheap — and there was no trend to bring, because
`vast_machine_blacklist.publish` correctly refuses CLASS_CAPACITY under trimcrae's "a moment, not a property"
ruling. These tests pin the readout that fills that gap AND the boundary that keeps it from becoming the
durable exclusion that ruling struck down.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import capacity_refusal_trend as crt  # noqa: E402

MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "capacity_refusal_trend.py")
LAUNCH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ternary_vast_launch.py")

T0 = 1_800_000_000  # arbitrary fixed epoch; nothing here may read the clock


def _ev(offset_h, machine, unit="u1"):
    import calendar, time  # noqa: E401
    utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(T0 - offset_h * 3600))
    assert calendar.timegm(time.strptime(utc, "%Y-%m-%dT%H:%M:%SZ"))  # the stamp must round-trip
    return {"utc": utc, "machine_id": str(machine), "unit_id": unit, "lane": "ternary"}


# ---------------------------------------------------------------- it measures the real morning
def test_it_reports_the_shape_of_the_2026_07_29_morning():
    # Four hosts, four distinct machines, inside an hour.
    evs = [_ev(0.6, 29711), _ev(0.4, 28164), _ev(0.1, 12227), _ev(0.02, 41950)]
    s = crt.summarize(evs, now_epoch=T0)
    assert s["n_refusals"] == 4
    assert s["n_distinct_machines"] == 4
    assert s["machines"] == sorted(["29711", "28164", "12227", "41950"])


def test_the_readout_says_a_refusal_is_not_a_price():
    line = crt.render(crt.summarize([_ev(0.5, 1), _ev(0.2, 2)], now_epoch=T0))
    assert "CAPACITY-REFUSAL TREND" in line
    assert "not a price" in line, "the whole point is that the board was cheap while hosts refused"
    assert "READOUT, not a gate" in line


def test_no_refusals_reads_as_none_not_as_silence():
    assert "none in the last" in crt.render(crt.summarize([], now_epoch=T0))


# ---------------------------------------------------------------- perishable, three ways
def test_events_age_out_of_the_window():
    old, new = _ev(crt.WINDOW_H + 1, 111), _ev(0.5, 222)
    s = crt.summarize([old, new], now_epoch=T0)
    assert s["n_refusals"] == 1 and s["machines"] == ["222"]


def test_an_undateable_event_is_dropped_not_kept_forever():
    # A bad stamp must not become an immortal entry — that is how a perishable ledger turns durable.
    assert crt.prune([{"utc": "not-a-date", "machine_id": "9"}], now_epoch=T0) == []


def test_no_per_machine_aggregate_is_stored():
    # Only events. A machine that refused once has no standing record — "a moment, not a property".
    src = open(MOD).read()
    for banned in ("machine_counts", "per_machine", "strikes", "offences"):
        assert banned not in src, banned


# ---------------------------------------------------------------- ⛔ it may never gate
def test_the_module_returns_no_verdict_of_any_kind():
    tree = ast.parse(open(MOD).read())
    names = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef,))}
    for banned in ("decide", "gate", "block", "should_rent", "verdict", "exclude"):
        assert not any(banned in n for n in names), f"{banned!r} in {names}"


def test_no_summary_field_could_be_mistaken_for_a_decision():
    s = crt.summarize([_ev(0.1, 1)], now_epoch=T0)
    for banned in ("block", "hold", "refuse", "ok", "allow", "verdict"):
        assert banned not in s, banned
    assert set(s) == {"window_h", "n_refusals", "n_distinct_machines", "machines",
                      "n_units_affected", "units", "span_h", "per_h"}


def test_the_launcher_only_READS_the_trend_it_never_branches_on_it():
    # The exact regression that would recreate the durable exclusion: an `if` on the refusal count.
    src = open(LAUNCH).read()
    i = src.index("capacity_refusal_trend")
    window = src[i:i + 900]
    assert "_crt.record(" in window
    assert "n_refusals" not in window, "the launcher is reading the count — one step from branching on it"
    assert "crt.summarize" not in window


def test_it_is_wired_into_the_refusal_branch_at_all():
    src = open(LAUNCH).read()
    j = src.index('err == "resources_unavailable"')
    assert "capacity_refusal_trend" in src[j:j + 3000], "refusals are still going unrecorded"


# ---------------------------------------------------------------- it must never break a teardown
def test_a_broken_store_returns_None_and_does_not_raise():
    class Boom:
        def get_object(self, **kw): raise RuntimeError("no")
        def put_object(self, **kw): raise RuntimeError("no")
    assert crt.record(Boom(), "b", 1, "u", "ternary") is None


def test_no_s3_is_a_no_op():
    assert crt.record(None, "b", 1, "u", "ternary") is None


def test_load_treats_an_unreadable_ledger_as_empty():
    class Boom:
        def get_object(self, **kw): raise RuntimeError("no")
    assert crt.load(Boom(), "b") == []


def test_the_window_is_not_per_lane_tunable():
    src = open(MOD).read()
    assert src.count("WINDOW_H = ") == 1
