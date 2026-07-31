"""A RENTAL THAT WOULD PRINT `⚠ PAYING OVER THE …× LINE` MUST BE UNSUBMITTABLE.

★★ THE INCIDENT (2026-07-31, 4:02 PM ET). `5aks_d0_to_d__ternary_nr4a1_r0` was rented on machine 34345
(RTX 3090) and the board printed:

    RTX 3090 $0.00891/ns · 2.61× basis [bid]   ⚠ PAYING OVER THE 1.92× LINE ($0.006539/ns)

`⚠ PAYING`, not `⛔ REFUSED` — a live billed rental. CLAUDE.md §1: *"a row that prints `⚠ DRIFT` is a row we
do not buy — the flag and the refusal are the same number"*. They demonstrably were not.

★ THE MECHANISM, by controlled reproduction on that exact offer rather than by inference. `collect`'s
self-heal dispatches every re-placement with `bid_floor_mult=2.0` — the retention bid trimcrae authorised for
churning legs — which sets `VAST_BID_FLOOR_MULT`, and `_vast_bid_price` then returns TWICE the market floor.
But `rank_offers_by_usd_per_ns` scored interruptible offers with `billed_usd_h=None`, so `score_offer`
re-derived a bid from `recommended_bid` (floor + a small staleness tick) and never saw the multiplier:

    offer min_bid/dph_total = $0.08148/hr
    VAST_BID_FLOOR_MULT unset -> scored $0.005338/ns   bid $0.0831/hr   SELECTED
    VAST_BID_FLOOR_MULT=2.0   -> scored $0.005338/ns   bid $0.1630/hr   SELECTED   <- score did not move
    the instance then billed dph_base $0.16 + storage = $0.1711/hr = $0.00891/ns = 2.612× basis

So the ceiling was evaluated against a price we were never going to pay, and it was SYSTEMATIC: every
re-placement on this lane carries `bid_floor_mult=2.0`.

⚠ NOT the leading hypothesis it was mistaken for. The offer-quote-vs-billed gap (`vast_rate_forensics`: a
quote understates by 9-26 % because of the storage line) is real but small; it cannot turn 1.3× into 2.6×.
The doubling did.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gpu_backend as gb  # noqa: E402
import inflight_usd_per_ns as ifn  # noqa: E402
import ternary_vast_launch as tv  # noqa: E402

# The real offer, from `ternary-vast-rental-receipt.json`'s record of the over-line rental.
OFFER = {"id": 1, "machine_id": 34345, "gpu_name": "RTX 3090", "num_gpus": 1, "verified": True,
         "rentable": True, "gpu_ram": 24576, "cpu_ram": 65536, "cpu_cores": 16, "disk_space": 200,
         "reliability2": 0.99, "cuda_max_good": 13.0, "min_bid": 0.08148148148148149,
         "dph_total": 0.08148148148148149, "storage_cost": 0.20}


@pytest.fixture
def mult(monkeypatch):
    """Set VAST_BID_FLOOR_MULT and rebuild the module constant it is read into at import."""
    def _set(v):
        if v is None:
            monkeypatch.delenv("VAST_BID_FLOOR_MULT", raising=False)
            monkeypatch.setattr(gb, "_VAST_BID_FLOOR_MULT", None)
        else:
            monkeypatch.setenv("VAST_BID_FLOOR_MULT", str(v))
            monkeypatch.setattr(gb, "_VAST_BID_FLOOR_MULT", float(v))
    return _set


def _spec():
    return tv.resource_spec(max_usd_per_ns=tv.buy_ceiling_usd_per_ns())


# =============================================================================================================
# THE REGRESSION — the offer that was actually bought must now be refused
# =============================================================================================================
def test_the_offer_that_produced_the_2_61x_rental_is_now_REFUSED(mult):
    mult(2.0)
    measured, capable = gb.rank_offers_by_usd_per_ns([OFFER], _spec())
    assert measured == [], "the ceiling must bind on the bid we will actually pay"
    assert capable == [], "an unpriceable-under-cap board must not fall through to the unmeasured path"
    assert gb._select_cheapest_offer([OFFER], _spec()) is None, "and it must be unselectable end to end"


def test_the_NEGATIVE_CONTROL_the_same_offer_without_a_retention_bid_is_still_bought(mult):
    """The fix must refuse the expensive PURCHASE, not the cheap OFFER. Machine 34345 at $0.0815/hr is
    genuinely good value; refusing it too would be an over-correction that starves the board."""
    mult(None)
    measured, _ = gb.rank_offers_by_usd_per_ns([OFFER], _spec())
    assert measured, "a genuinely cheap offer must still be selectable"
    assert measured[0][0] < tv.buy_ceiling_usd_per_ns()
    assert gb._select_cheapest_offer([OFFER], _spec()) is not None


def test_the_scored_rate_TRACKS_the_multiplier(mult):
    """The defect in one line: the score used to be identical either way. If this ever stops moving, the cap
    has gone blind to the bid again."""
    mult(None)
    cheap = gb.rank_offers_by_usd_per_ns([OFFER], tv.resource_spec())[0][0][0]
    mult(2.0)
    dear = gb.rank_offers_by_usd_per_ns([OFFER], tv.resource_spec())[0][0][0]
    assert dear > cheap * 1.5, (cheap, dear)


# =============================================================================================================
# THE PROPERTY — flag and refusal are ONE number, for any offer
# =============================================================================================================
@pytest.mark.parametrize("floor,mult_v", [
    (0.08148148148148149, 2.0), (0.05, 3.0), (0.12, 2.0), (0.30, 1.0), (0.02, 8.0),
])
def test_anything_selectable_would_NOT_print_the_drift_flag(floor, mult_v):
    """The §1 ruling, as an executable invariant over a grid. For every offer the ranker admits under the cap,
    the board's own renderer must NOT flag it — because the flag and the refusal are the same number."""
    os.environ["VAST_BID_FLOOR_MULT"] = str(mult_v)
    gb._VAST_BID_FLOOR_MULT = float(mult_v)
    try:
        o = dict(OFFER, min_bid=floor, dph_total=floor)
        measured, _ = gb.rank_offers_by_usd_per_ns([o], _spec())
        if not measured:
            return                                     # refused — nothing to check
        billed = gb._vast_bid_price(o) or floor
        row = ifn.row(o["gpu_name"], billed, 0.1143,
                      storage_usd_h=0.20 * 60 / 730.0, tier=ifn.TIER_BID)
        assert not row["paying_over_line"], (
            f"selectable at floor={floor} mult={mult_v} but the board would print "
            f"{row['cell']!r} — the flag and the refusal have diverged again")
    finally:
        os.environ.pop("VAST_BID_FLOOR_MULT", None)
        gb._VAST_BID_FLOOR_MULT = None


def test_the_on_demand_branch_is_unchanged(mult):
    """On-demand offers already passed their own billed price; the fix must not perturb them."""
    mult(2.0)
    import dataclasses
    res = dataclasses.replace(_spec(), interruptible=False)
    # $0.09/hr on a 3090: (0.09 + ~$0.016 storage) / 19.204 ns/h = ~$0.0055/ns, inside the $0.006539 cap.
    # (0.11 would be genuinely over it — the cap is tight on this card, which is the point of the lane's
    # 3090 exposure and is discussed in the session report, not a defect in the fix.)
    o = dict(OFFER, dph_total=0.09)
    measured, _ = gb.rank_offers_by_usd_per_ns([o], res)
    assert measured, "an on-demand offer is priced at dph_total and the multiplier must not touch it"
    mult(None)
    same, _ = gb.rank_offers_by_usd_per_ns([o], res)
    assert abs(same[0][0] - measured[0][0]) < 1e-12, \
        "the bid multiplier must not move an on-demand score at all"
