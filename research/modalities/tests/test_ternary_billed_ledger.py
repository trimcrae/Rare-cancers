"""WHAT EACH TERNARY RENTAL COST — pinned, in the fan-out's field names, with the orphan case it exists for.

★★ THE HOLE THIS CLOSES. `billed_h` appeared in exactly ONE committed artifact repo-wide
(`step1-fanout-map.json`), so "how long do this lane's hosts live and what did they cost?" had to be
reconstructed from the GIT HISTORY of `ternary-vast-rental-receipt.json` — a file OVERWRITTEN by every
launch, which holds one tick rather than a record.

And the gap is not hypothetical on this lane: the 5a-KS prune smoke rented instance 46459452 at 10:02 PM ET
on 2026-07-31, produced ZERO host-side artifacts (`run.log`, the `attempts/` archive, `status.json` and
`leg.json` all still carried their 2026-07-26 contents the next morning), and the instance was gone. Nothing
recorded that money had been spent.

⚠ THE SEMANTICS ARE INHERITED, NOT RE-DECIDED. `billed_h` is RENTAL time, not LEG time — see
`test_price_ledger_uptime_semantics.py`, where a row read 156.0 h for a leg whose own record says 1.04 h of
production MD. The field was not broken; it was measuring the host's billed life, and the dollars were real.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_billed_ledger as tbl  # noqa: E402

NOW = 1_785_600_000.0
INST = {"id": 46459452, "machine_id": 12976, "gpu_name": "RTX 4090",
        "dph_total": 0.1253111111111111, "start_date": NOW - 3600 * 2.5, "actual_status": "running"}


# ---------------------------------------------------------------------------------------------
# the shared schema — one analysis must work across lanes
# ---------------------------------------------------------------------------------------------
def test_the_row_uses_the_FANOUT_field_names_exactly():
    """`congeneric_fanout_vast.ledger_cost` emits these six. Matching rather than inventing a fourth schema
    is the entire reason this is worth building."""
    r = tbl.row_for(INST, unit_id="u", now_epoch=NOW)
    for k in ("instance", "unit_id", "machine_id", "rate_usd_h", "billed_h", "usd"):
        assert k in r, k


def test_the_arithmetic_matches_the_fanouts():
    r = tbl.row_for(INST, unit_id="u", now_epoch=NOW)
    assert r["billed_h"] == 2.5
    assert r["usd"] == round(0.1253111111111111 * 2.5, 4)
    assert r["rate_usd_h"] == pytest.approx(0.1253111111111111)


def test_billed_h_is_RENTAL_time_from_the_instances_own_start_date():
    """Not leg time, not production wall time. The 150-fold difference between those is what made a
    retrospective row look absurd when it was correct."""
    assert tbl.billed_hours({"start_date": NOW - 3600 * 156}, now_epoch=NOW) == pytest.approx(156.0)


# ---------------------------------------------------------------------------------------------
# holes are counted, never hidden
# ---------------------------------------------------------------------------------------------
def test_an_unreadable_age_is_None_not_zero():
    """A rental whose age cannot be read is a HOLE in the total. Zero would silently shrink the bill."""
    for bad in ({}, {"start_date": None}, {"start_date": "x"}, {"start_date": 0}):
        assert tbl.billed_hours(bad, now_epoch=NOW) is None


def test_an_unpriced_rental_is_flagged_and_excluded_from_the_total_not_counted_as_free():
    doc = {"rentals": [tbl.row_for({"id": 1, "start_date": NOW - 3600}, now_epoch=NOW),
                       tbl.row_for(INST, now_epoch=NOW)]}
    total, n, unpriced, hours = tbl.totals(doc)
    assert unpriced == 1 and n == 2
    assert total == pytest.approx(round(0.1253111111111111 * 2.5, 2))
    assert hours == 2.5, "an unpriced rental must not contribute hours either"


def test_the_render_says_UNPRICED_out_loud():
    doc = {"rentals": [tbl.row_for({"id": 1, "start_date": NOW - 3600}, now_epoch=NOW)]}
    assert "UNPRICED" in tbl.render(doc)


def test_the_rate_is_the_instances_billed_total_not_a_bare_bid():
    """§6: a launcher `dph≈` line is the market floor plus the search's disk line and reads LOW against what
    the instance is actually billed."""
    assert tbl._rate_of({"dph_total": 0.2, "bid": 0.05}) == 0.2
    assert tbl._rate_of({"bid": 0.05}) == 0.05
    assert tbl._rate_of({}) is None


# ---------------------------------------------------------------------------------------------
# recording: idempotent, and it must not be able to break a teardown
# ---------------------------------------------------------------------------------------------
def test_recording_twice_for_one_rental_does_not_double_count(tmp_path):
    p = tmp_path / "l.json"
    tbl.record(INST, unit_id="u", reason="teardown", path=p, now_epoch=NOW)
    tbl.record(INST, unit_id="u", reason="teardown", path=p, now_epoch=NOW)
    doc = json.loads(p.read_text())
    assert len(doc["rentals"]) == 1, "teardown and the guard can both fire for one box"


def test_a_later_observation_of_the_same_rental_keeps_the_LONGER_life(tmp_path):
    p = tmp_path / "l.json"
    tbl.record(INST, unit_id="u", reason="teardown", path=p, now_epoch=NOW)
    tbl.record(INST, unit_id="u", reason="teardown", path=p, now_epoch=NOW + 3600)
    doc = json.loads(p.read_text())
    assert len(doc["rentals"]) == 1 and doc["rentals"][0]["billed_h"] == 3.5


def test_teardown_and_an_idle_guard_destroy_are_separate_rows(tmp_path):
    """A box the guard had to destroy AFTER a failed teardown is a different fact from a clean retirement,
    and that is exactly where a wedged host's cost lands."""
    p = tmp_path / "l.json"
    tbl.record(INST, unit_id="u", reason="teardown", path=p, now_epoch=NOW)
    tbl.record(INST, unit_id="u", reason="idle-guard", path=p, now_epoch=NOW)
    assert len(json.loads(p.read_text())["rentals"]) == 2


def test_a_corrupt_ledger_does_not_stop_the_next_row_being_written(tmp_path):
    """Bookkeeping must never be able to block a teardown — the failure mode would be a box left billing."""
    p = tmp_path / "l.json"
    p.write_text("{not json")
    r = tbl.record(INST, unit_id="u", path=p, now_epoch=NOW)
    assert r["billed_h"] == 2.5 and json.loads(p.read_text())["rentals"]


def test_the_ledger_is_bounded_and_trims_only_the_oldest(tmp_path):
    p = tmp_path / "l.json"
    doc = {"rentals": [{"instance": str(i), "reason": "teardown"} for i in range(tbl.MAX_ROWS + 5)]}
    p.write_text(json.dumps(doc))
    tbl.record(INST, unit_id="u", path=p, now_epoch=NOW)
    out = json.loads(p.read_text())["rentals"]
    assert len(out) == tbl.MAX_ROWS
    assert out[-1]["instance"] == "46459452", "the new row must survive the trim"


# ---------------------------------------------------------------------------------------------
# the wiring: recorded at DESTROY, and BEFORE the DELETE
# ---------------------------------------------------------------------------------------------
def _launch_src():
    import ternary_vast_launch as tv
    return open(tv.__file__).read()


def _destroy_body(src):
    """The `_destroy` funnel's own text. Sliced forward FROM the def — `for i in mine:` also appears
    earlier in the file, and an index() from position 0 gives a backwards (empty) slice that makes every
    assertion below silently vacuous."""
    i = src.index("    def _destroy(iid, why")
    return src[i:src.index("    for i in mine:", i)]


def test_every_teardown_path_records_a_rental():
    """`_destroy` is the funnel every teardown in `collect` goes through, and `retire_host` is the other
    destroyer. Both must record, or the lane keeps the hole this module exists to close."""
    src = _launch_src()
    body = _destroy_body(src)
    assert "_tbl.record(" in body
    rh = src[src.index("def retire_host("):]
    assert "_tbl.record(" in rh[:rh.index("\ndef ")]


def test_the_row_is_written_BEFORE_the_DELETE():
    """A row written only on a successful destroy would miss precisely the boxes whose teardown FAILED —
    the ones still on the meter, which are the expensive ones."""
    src = _launch_src()
    body = _destroy_body(src)
    assert body.index("_tbl.record(") < body.index('_vast_request("DELETE"')


def test_the_ledger_can_never_block_a_teardown():
    src = _launch_src()
    body = _destroy_body(src)
    seg = body[body.index("_tbl.record("):]
    assert "except Exception" in seg[:400], "a bookkeeping failure must not leave a box billing"


def test_the_destroy_calls_pass_the_INSTANCE_not_just_its_id():
    """Without the record, the rate and the start_date are gone the moment the box is — an unpriced row is
    all that could ever be written."""
    src = _launch_src()
    for call in ("_destroy(iid, why, inst=i, unit_id=uid)",
                 "inst=i, unit_id=uid)"):
        assert call in src
