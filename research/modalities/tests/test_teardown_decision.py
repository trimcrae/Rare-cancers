#!/usr/bin/env python3
"""Teardown is a SWAP, and a swap you cannot complete is just a loss.

The decision these pin: on a capacity refusal, destroying immediately forfeits the instance's disk (the
staged inputs) and buys ~$0.011/hr of storage back. That trade is worth making when a replacement is
actually purchasable, and not when the buy line would refuse one — which is a real state, measured at
8:32 PM ET on 2026-07-27 when the board's cheapest was 1.96x basis and all 12 units were refused.
"""
import os
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import teardown_decision as td  # noqa: E402

LINE = 0.006539          # the absolute buy line; never typed as a multiple (CLAUDE.md §1)


def _d(**kw):
    base = dict(replacement_usd_per_ns=0.004, buy_line_usd_per_ns=LINE,
                stopped_min=5.0, max_stopped_min=45.0)
    base.update(kw)
    return td.decide(**base)


# ---------------------------------------------------------------- the swap is available
def test_a_replacement_under_the_line_means_destroy_and_swap():
    d = _d(replacement_usd_per_ns=0.004)
    assert d["destroy"] is True
    assert d["verdict"] == td.DESTROY_HAVE_REPLACEMENT


def test_a_replacement_exactly_AT_the_line_still_counts_as_available():
    # The line is an inclusive ceiling everywhere else in this repo; it must not become exclusive here.
    assert _d(replacement_usd_per_ns=LINE)["destroy"] is True


# ---------------------------------------------------------------- the swap is NOT available
def test_no_replacement_under_the_line_means_HOLD_not_destroy():
    d = _d(replacement_usd_per_ns=0.00668)          # 1.96x basis — the 8:32 PM board
    assert d["destroy"] is False
    assert d["verdict"] == td.HOLD_NO_REPLACEMENT
    assert d["replacement_clears_buy_line"] is False


def test_an_empty_board_means_HOLD_rather_than_a_blind_teardown():
    # `None` = nothing priceable at all. That is LESS reason to destroy, not more: we would be tearing down
    # into a market we cannot even measure.
    assert _d(replacement_usd_per_ns=None)["destroy"] is False


def test_a_missing_buy_line_never_authorises_a_teardown():
    # Fail CLOSED. A board read that failed (the Vast 403-under-throttling case) must not read as
    # "replacement available".
    assert _d(buy_line_usd_per_ns=None)["destroy"] is False


# ---------------------------------------------------------------- the hold cannot last forever
def test_the_backstop_still_reaps_a_box_nobody_can_replace():
    d = _d(replacement_usd_per_ns=0.00668, stopped_min=46.0, max_stopped_min=45.0)
    assert d["destroy"] is True
    assert d["verdict"] == td.DESTROY_BACKSTOP


def test_the_backstop_does_not_fire_early():
    assert _d(replacement_usd_per_ns=0.00668, stopped_min=44.0)["destroy"] is False


# ---------------------------------------------------------------- the readout
def test_a_held_box_never_renders_like_a_purchase():
    # CLAUDE.md §1: `⚠ PAYING` = money going out on a GPU; a HOLD is not that. Conflating them is what made
    # an earlier round of hold readouts unreadable.
    line = td.render(_d(replacement_usd_per_ns=0.00668), instance_id="1", machine_id="2")
    assert "⛔ HOLDING" in line and "$0 GPU going out" in line
    assert "⚠ PAYING" not in line


def test_a_hold_carries_the_snapshot_that_caused_it():
    # A silent hold is indistinguishable from a lane that finished — the failure mode §6 names explicitly.
    d = _d(replacement_usd_per_ns=0.00668)
    assert d["hold_cost_usd_h"] > 0
    assert "buy line" in d["hold_why"]
    assert d["replacement_usd_per_ns"] == 0.00668 and d["buy_line_usd_per_ns"] == LINE


def test_the_decision_never_consults_gpu_util_or_raises_a_bid():
    # Two standing prohibitions, asserted against the parsed CODE — the module docstring discusses both at
    # length, so a plain substring scan would trip over its own rationale.
    import ast
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "teardown_decision.py")).read()
    tree = ast.parse(src)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {n.arg for n in ast.walk(tree) if isinstance(n, ast.arg)}
    names |= {k.value for k in ast.walk(tree) if isinstance(k, ast.Constant) and isinstance(k.value, str)
              and "\n" not in k.value}
    assert not any("gpu_util" in str(n) for n in names)
    assert not any("bid" in str(n).lower() for n in names)


def test_it_is_pure_no_io_no_clock():
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "teardown_decision.py")).read()
    for banned in ("import boto3", "import requests", "time.time(", "datetime.now("):
        assert banned not in src, banned


# ============================================================================================================
# ★ THE CALL SITE MUST STAY WIRED — a module nothing calls is not a policy.
#
# Why this exists: when this landed, another lane was concurrently editing `ternary_vast_launch.py` from a
# base that PREDATED it. A wholesale commit of that file would revert the conditional teardown silently, and
# the only symptom would be hosts being destroyed into a market that refuses to replace them — invisible
# until someone re-derived the whole argument. Two lanes already reverted each other's edits this way on
# 2026-07-27. A red build is the cheap version of that discovery.
# ============================================================================================================
def _launcher_src():
    return open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "ternary_vast_launch.py")).read()


def test_the_capacity_refusal_path_still_asks_before_destroying():
    src = _launcher_src()
    assert "teardown_decision" in src, "the launcher no longer imports the teardown decision"
    assert "tdd.decide(" in src, "the launcher no longer CALLS the teardown decision"


def test_the_replacement_is_priced_through_the_same_gate_that_would_buy_it():
    # If these diverge, a board we refuse to buy from could still authorise a teardown into it.
    assert "relaunch_market_gate" in _launcher_src()


def test_a_capacity_refusal_can_no_longer_destroy_unconditionally():
    # The old unconditional line. Its return means the decision was bypassed.
    src = _launcher_src()
    assert "picking another host beats queueing on this one" not in src


def test_held_boxes_are_surfaced_not_swallowed():
    # CLAUDE.md §6: every hold must be VISIBLE with the snapshot that caused it.
    src = _launcher_src()
    assert "TVAST-HELD" in src and "held_boxes" in src


# ============================================================================================================
# The hold cost must track the disk we ACTUALLY request, not a stale headline figure.
# bid-strategy.md F4 quotes "~$0.011/hr at the 40 GB the launcher requests" — but no lane requests 40 GB any
# more (ternary 60, step 1 fan-out 80), so the headline understates a real hold by 1.5-2x.
# ============================================================================================================
def test_storage_scales_with_the_disk_requested():
    assert td.storage_usd_h_for(40) == pytest.approx(0.0110, abs=1e-4)
    assert td.storage_usd_h_for(60) == pytest.approx(0.0164, abs=1e-4)
    assert td.storage_usd_h_for(80) == pytest.approx(0.0219, abs=1e-4)


def test_a_hold_prices_itself_off_the_lanes_own_disk():
    ternary = td.decide(replacement_usd_per_ns=0.00668, buy_line_usd_per_ns=LINE,
                        stopped_min=5.0, max_stopped_min=45.0, disk_gb=60)
    fanout = td.decide(replacement_usd_per_ns=0.00668, buy_line_usd_per_ns=LINE,
                       stopped_min=5.0, max_stopped_min=45.0, disk_gb=80)
    assert fanout["hold_cost_usd_h"] > ternary["hold_cost_usd_h"]
    assert ternary["hold_cost_usd_h"] == pytest.approx(td.storage_usd_h_for(60))


def test_the_stale_40gb_headline_is_not_the_default_for_a_lane_that_states_its_disk():
    d = td.decide(replacement_usd_per_ns=0.00668, buy_line_usd_per_ns=LINE,
                  stopped_min=5.0, max_stopped_min=45.0, disk_gb=60)
    assert d["hold_cost_usd_h"] != pytest.approx(0.011, abs=1e-4)
