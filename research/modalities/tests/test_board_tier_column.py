"""EVERY BOARD ROW SAYS WHICH TIER IT IS RENTING ON.

trimcrae, 2026-07-31: *"Update the status table to show on demand / interruptible too."*

WHY IT BECAME LOAD-BEARING THE SAME DAY. The gate now PREFERS the uninterruptible tier whenever it clears
both ceilings (`ternary_vast_launch.choose_tier`), because 25 % of that day's rentals died before their first
checkpoint. A policy that can buy the dearer tier, on a board that cannot show which rows took it, is a rising
ladder spend with no attributable cause — the unreadable-hold failure one level up.

⚠ THE HALF THAT IS EASIEST TO GET WRONG: **absent is not bid.** `is_bid` may be missing from the record, or
the record may never have been read. CLAUDE.md §4 — an absent reading is not a reading of absence. A row that
silently claims "bid" when nobody looked understates exactly the spend this column exists to attribute.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import inflight_board as ib  # noqa: E402
import inflight_usd_per_ns as ifn  # noqa: E402

RATE = 0.13


@pytest.mark.parametrize("is_bid,tier", [
    (True, ifn.TIER_BID), ("true", ifn.TIER_BID), (1, ifn.TIER_BID),
    (False, ifn.TIER_ONDEMAND), ("false", ifn.TIER_ONDEMAND), (0, ifn.TIER_ONDEMAND),
    (None, ifn.TIER_UNKNOWN), ("", ifn.TIER_UNKNOWN), ("garbage", ifn.TIER_UNKNOWN),
])
def test_tier_of_never_collapses_absent_into_bid(is_bid, tier):
    assert ifn.tier_of(is_bid) == tier


def test_absent_renders_UNKNOWN_and_is_not_the_word_bid():
    cell = ifn.row("RTX 4090", 0.16, RATE, tier=ifn.tier_of(None))["cell"]
    assert "[tier?]" in cell
    assert "[bid]" not in cell and "ON-DEMAND" not in cell


def test_the_two_real_tiers_are_distinguishable_at_a_glance():
    """One glyph, one meaning — the same rule as ⚠ PAYING vs ⛔ REFUSED. On-demand rows exist to be noticed,
    because their whole point is that they cost more."""
    bid = ifn.row("RTX 4090", 0.16, RATE, tier=ifn.TIER_BID)["cell"]
    od = ifn.row("RTX 4090", 0.16, RATE, tier=ifn.TIER_ONDEMAND)["cell"]
    assert bid != od
    assert "[bid]" in bid and "[ON-DEMAND]" in od
    assert od.upper().count("ON-DEMAND") == 1


def test_the_tier_does_not_displace_the_drift_flag():
    """The flag must remain the last and most prominent thing on a drifting row — that is why the tag is
    terse and why it is inserted BEFORE it."""
    over = ifn.APPROVED_USD_PER_NS * 2 * 33.5   # comfortably over the line on a 4090
    cell = ifn.row("RTX 4090", over, RATE, tier=ifn.TIER_ONDEMAND)["cell"]
    assert "⚠ PAYING OVER THE" in cell
    assert cell.index("[ON-DEMAND]") < cell.index("⚠ PAYING OVER THE")


def test_a_refused_row_renders_no_tier_by_default():
    """Nothing was rented, so there is no tier we are ON. Claiming one would be a fact about a purchase that
    did not happen."""
    cell = ifn.row("RTX 4090", 0.16, RATE, stance=ifn.REFUSED)["cell"]
    assert "[bid]" not in cell and "[ON-DEMAND]" not in cell and "[tier?]" not in cell


def test_an_unbenched_card_still_carries_its_tier():
    """The attribution must not have a hole exactly where the cost is least predictable."""
    r = ifn.row("RTX PRO 6000 WS", 0.45, RATE, tier=ifn.TIER_ONDEMAND)
    assert r["usd_per_ns"] is None and "[ON-DEMAND]" in r["cell"]


# =============================================================================================================
# the board's own path
# =============================================================================================================
def test_the_board_cell_threads_is_bid_through_and_defaults_to_claiming_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(ib, "planning_usd_per_ref_gpu_h", lambda root=None: RATE)
    assert "[bid]" in ib.usd_per_ns_cell("RTX 4090", 0.16, is_bid=True)
    assert "[ON-DEMAND]" in ib.usd_per_ns_cell("RTX 4090", 0.16, is_bid=False)
    assert "[tier?]" in ib.usd_per_ns_cell("RTX 4090", 0.16, is_bid=None)
    # A caller that does not pass the argument makes NO tier claim — distinct from passing None, which means
    # "we read the record and the field was absent".
    plain = ib.usd_per_ns_cell("RTX 4090", 0.16)
    assert "[" not in plain


def test_the_lane_reads_is_bid_from_the_instance_record_it_already_has():
    """No new API call: `is_bid` is in the record `collect` already lists, and in
    `vast_rate_forensics._FIELDS`."""
    import inspect

    import ternary_vast_launch as tv
    src = inspect.getsource(tv)
    assert '"is_bid": i.get("is_bid")' in src
    assert '_usd_per_ns_cell(_b["gpu"], _b["dph"], _b.get("is_bid"))' in src
    # ...and the lane must NOT decide the tier itself — one home, in `tier_of`.
    assert "_ifn.tier_of(is_bid)" in inspect.getsource(tv._usd_per_ns_cell)
