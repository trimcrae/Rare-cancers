"""THE BOARD QUERY MUST ASK FOR THE WHOLE BOARD — an unset `limit` silently hid 72 % of the market.

★ WHY THIS FILE EXISTS (measured 2026-07-27, run 30294964932).

`gpu_backend._vast_offer_query` is the ONE query behind every market gate and every `submit` in this repo. It
set no `limit`, and Vast's `/search/asks/` defaults to **64 rows**. Measured against the same board in the same
second, with paired reads: `limit=512` returns **225** offers, the default returns **64**.

The damage is not "a smaller sample". The query is ordered by `dph_total asc` while `rank_offers_by_usd_per_ns`
ranks by **$/ns** — different orderings — so truncation drops gradeable offers preferentially (priceable
143-147 full vs 28-29 default) and the surviving best-4 mean was **+26.3 %** more expensive on every paired
read. Every rental this repo has made was approved against a board it could not see.

It also fabricated the volatility that prompted the whole investigation. trimcrae asked whether hourly polling
was too slow because the gate read 1.261x basis at 9:13:04 AM ET and 2.436x at 9:16:28 AM. Across the committed
snapshots, the verdict is perfectly predicted by the ROW COUNT: every 64-row read cleared (8/8) and, in the
morning window where the bench table was unchanged, every shorter read held (0/10). The board had not moved.

So the limit is pinned here. A regression to the default is not a style question — it is a ~26 % price rise and
a return of phantom market noise, and neither announces itself.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import gpu_backend as gb  # noqa: E402


def test_the_board_query_sets_an_explicit_limit():
    q = gb._vast_offer_query(gb.ResourceSpec())
    assert "limit" in q, "no `limit` => Vast returns its default 64 rows of a ~225-offer board"


def test_the_limit_is_large_enough_for_the_measured_board():
    # The board measured 222-227 qualifying offers. A limit at or below that is truncation again, just at a
    # less obvious threshold — which would be worse, because it would look deliberate.
    q = gb._vast_offer_query(gb.ResourceSpec())
    assert q["limit"] >= 256
    assert q["limit"] == gb._VAST_SEARCH_LIMIT


def test_the_limit_has_exactly_one_home():
    # CLAUDE.md rule 1. The on-demand price lookup used to carry its own hard-coded 512 while the query that
    # decides what we BUY carried none; a second literal is how the two drift apart again.
    import inspect
    src = inspect.getsource(gb._vast_offer_query)
    assert "_VAST_SEARCH_LIMIT" in src
    assert "512" not in src.split('"limit"')[-1][:40], "the limit must reference the constant, not a literal"


@pytest.mark.parametrize("interruptible", [True, False])
def test_both_tiers_get_the_full_board(interruptible):
    # The bid tier is what the lanes rent on, but the on-demand query feeds the bid CAP. A truncated
    # on-demand board would under-read the cap and let a bid run past the machine's real ceiling.
    spec = gb.ResourceSpec(interruptible=interruptible)
    assert gb._vast_offer_query(spec)["limit"] == gb._VAST_SEARCH_LIMIT


def test_the_limit_does_not_disturb_the_hard_filters():
    # Widening the board must not widen what QUALIFIES. Every safety filter is unchanged, which is why this
    # change can only make the price better: any newly visible offer already passed all of them.
    q = gb._vast_offer_query(gb.ResourceSpec())
    assert q["verified"] == {"eq": True}
    assert q["rentable"] == {"eq": True}
    assert q["num_gpus"] == {"eq": 1}
    assert q["reliability2"]["gte"] == pytest.approx(0.90)
    assert q["order"] == [["dph_total", "asc"]]


# =============================================================================================================
# MULTI-SAMPLE MERGE — the endpoint returns a rotating sample, so one read is not the board
# =============================================================================================================
def test_sample_board_defaults_to_one_read_and_changes_nothing():
    # The default must be a no-op. `submit` already bursts ~8 searches for a 4-unit launch and the Vast edge
    # throttle fires on bursts, so doubling that by default would trade a ~5 % price gain for launches that
    # rent nothing. Opting in is a caller's decision, made where the burst maths is known.
    import inspect
    sig = inspect.signature(gb.sample_board)
    assert sig.parameters["samples"].default == 1


def test_sample_board_keeps_the_cheapest_sighting_per_machine(monkeypatch):
    # Merging must be monotone: a merged board can only be cheaper than either read alone, never worse.
    reads = [{"offers": [{"machine_id": 1, "min_bid": 0.30}, {"machine_id": 2, "min_bid": 0.10}]},
             {"offers": [{"machine_id": 1, "min_bid": 0.20}, {"machine_id": 3, "min_bid": 0.50}]}]
    calls = {"n": 0}

    def fake(_m, _p, _k, params=None, body=None, _hops=0, **_kw):
        calls["n"] += 1
        return reads[min(calls["n"] - 1, len(reads) - 1)]

    monkeypatch.setattr(gb, "_vast_request", fake)
    offers, n = gb.sample_board("k", gb.ResourceSpec(), samples=2, gap_s=0)
    assert n == 2
    by = {str(o["machine_id"]): o["min_bid"] for o in offers}
    assert by == {"1": 0.20, "2": 0.10, "3": 0.50}, "machine 1 must keep its CHEAPER sighting"


def test_sample_board_keeps_what_it_has_when_a_later_read_fails(monkeypatch):
    # A failed EXTRA read must not discard a board already in hand — that would turn an optimisation into an
    # outage, failing a gate that had a perfectly good board.
    state = {"n": 0}

    def flaky(_m, _p, _k, params=None, body=None, _hops=0, **_kw):
        state["n"] += 1
        if state["n"] == 1:
            return {"offers": [{"machine_id": 7, "min_bid": 0.11}]}
        raise RuntimeError("vast API GET /search/asks/ -> 403")

    monkeypatch.setattr(gb, "_vast_request", flaky)
    offers, n = gb.sample_board("k", gb.ResourceSpec(), samples=3, gap_s=0)
    assert n == 1 and len(offers) == 1


def test_sample_board_raises_if_the_very_first_read_fails(monkeypatch):
    # No board at all is a HOLD, not an empty market. CLAUDE.md §6: an unreadable market is not a cheap one.
    def dead(_m, _p, _k, params=None, body=None, _hops=0, **_kw):
        raise RuntimeError("403")

    monkeypatch.setattr(gb, "_vast_request", dead)
    with pytest.raises(RuntimeError):
        gb.sample_board("k", gb.ResourceSpec(), samples=2, gap_s=0)
