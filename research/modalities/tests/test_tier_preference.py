"""PREFER THE UNINTERRUPTIBLE TIER WHENEVER IT CLEARS BOTH CEILINGS.

trimcrae, 2026-07-31: *"fix those issues with the ternary lane then. Maybe add a new rule where if anything
on-demand comes in under the buy line, we just take it to avoid the outage."*

THE EVIDENCE, so nobody re-litigates it from the price alone:
  * 24 rentals across 4 legs in 6.73 h (7:12 AM - 1:56 PM ET, 2026-07-31), reconstructed from the git history
    of `ternary-vast-rental-receipt.json`: median session 60 min, mean 76, min 12, max 270; 25 % under 30 min,
    50 % under 60 min. UPPER bounds — they include the hostless gap — so the true sessions are shorter.
  * Baseline, `step1-fanout-map.json` `realised_rentals` (n = 208): median 1.62 h, 9 % under 0.5 h, 33 % under
    1 h. The ternary lane is churning about twice as fast as the lane we have most experience with.
  * A ternary leg needs ~28 min to stage and reach its first commit boundary, so **25 % of today's rentals
    died before buying a single checkpoint** — they billed and produced nothing. That is the outage.
  * And the tier became affordable: the 1:36 PM ET ablation measured bid best 0.883x basis, on-demand best
    1.778x — BOTH under the 1.9166x line. Earlier the same day on-demand priced 2.13-2.25x and was correctly
    refused, which is the behaviour that must be preserved.

⚠ WHAT THIS RULE IS NOT. It does not move, soften or bypass either ceiling. It changes which tier we PREFER
**among offers that have already cleared both**. An on-demand board over the buy line is refused exactly as
before; a tranche over the rung's dollar band is refused exactly as before.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import inflight_usd_per_ns as iu  # noqa: E402
import ternary_vast_launch as tv  # noqa: E402


def _blk(clears=True, over_dollars=False, over_ratio=False, ratio=1.0, projected=1.0,
         usd_per_ns=0.003, error=None):
    """A priced tier block, shaped as `_price_tier` returns one."""
    return {"clears": clears and not (over_dollars or over_ratio) and not error,
            "fails_dollar_ceiling": over_dollars, "fails_ratio_ceiling": over_ratio,
            "ratio_vs_basis": ratio, "projected_usd": projected, "mean_usd_per_ns": usd_per_ns,
            "board_error": error}


# =============================================================================================================
# the property, and a negative control on each half
# =============================================================================================================
def test_both_under_the_line_picks_ON_DEMAND_even_though_bid_is_cheaper():
    """THE RULE. An uninterruptible host cannot be preempted, and preemption is what is costing us — so a
    dearer host that survives is cheaper than a cheap one that dies before its first checkpoint."""
    bid = _blk(ratio=0.883, usd_per_ns=0.003014)
    od = _blk(ratio=1.778, usd_per_ns=0.006066)
    tier, hold, why = tv.choose_tier(bid, od)
    assert tier == tv.TIER_ONDEMAND and hold is False
    assert "cannot be preempted" in why or "uninterruptible" in why.lower()


def test_on_demand_over_the_RATE_line_falls_back_to_bid():
    """The negative control for the rule's own price guard. This is the 9:09 AM - 12:59 PM state of the same
    day: on-demand at 2.13-2.25x while bid cleared at 1.13-1.54x."""
    bid = _blk(ratio=1.13)
    od = _blk(over_ratio=True, ratio=2.23)
    tier, hold, why = tv.choose_tier(bid, od)
    assert tier == tv.TIER_BID and hold is False
    assert "rate" in why or "$/ns" in why or "drift line" in why


def test_on_demand_over_the_DOLLAR_ceiling_falls_back_to_bid():
    """The other ceiling, separately — CLAUDE.md §1 requires a refusal to NAME which one it hit, and the two
    are refused for different reasons (was this authorised, vs is this a rate we will pay at all)."""
    bid = _blk(ratio=1.10)
    od = _blk(over_dollars=True, ratio=1.20, projected=999.0)
    tier, hold, why = tv.choose_tier(bid, od)
    assert tier == tv.TIER_BID and hold is False
    assert "dollar" in why or "ceiling" in why


def test_both_tiers_over_HOLDS_and_names_which_ceiling_each_hit():
    bid = _blk(over_ratio=True, ratio=2.4)
    od = _blk(over_dollars=True, over_ratio=True, ratio=3.1, projected=999.0)
    tier, hold, why = tv.choose_tier(bid, od)
    assert tier is None and hold is True
    # The unreadable-hold failure is a hold that does not say which ceiling. Both tiers must be named.
    assert "bid" in why and "on-demand" in why
    assert "rate" in why or "drift" in why
    assert "dollar" in why or "ceiling" in why


def test_an_unreadable_on_demand_board_does_not_block_a_clearing_bid_board():
    """An optimisation that can block a launch is a liability — the same discipline the shared-set read used
    to have. An on-demand board we could not read is not an expensive one; it is simply not an option."""
    tier, hold, _ = tv.choose_tier(_blk(ratio=1.0), _blk(error="RuntimeError: 429"))
    assert tier == tv.TIER_BID and hold is False


def test_an_unreadable_BID_board_still_lets_a_clearing_on_demand_board_through():
    tier, hold, _ = tv.choose_tier(_blk(error="RuntimeError: 429"), _blk(ratio=1.5))
    assert tier == tv.TIER_ONDEMAND and hold is False


def test_the_preference_can_be_turned_off_without_touching_either_ceiling():
    """A behaviour change this consequential needs an off switch that is not "edit the gate"."""
    bid, od = _blk(ratio=0.9), _blk(ratio=1.5)
    assert tv.choose_tier(bid, od, prefer_uninterruptible=False)[0] == tv.TIER_BID
    assert tv.choose_tier(bid, od, prefer_uninterruptible=True)[0] == tv.TIER_ONDEMAND


# =============================================================================================================
# the ceilings themselves are untouched — the thing most likely to be broken by accident
# =============================================================================================================
def test_the_buy_line_is_still_the_imported_absolute_rate():
    """CLAUDE.md §1: the line is `$/ns`, the multiple is DERIVED from it, and this rule does not move either.
    A second copy of the number here is the rule-1 bug the repo has already paid for."""
    assert tv.MARKET_MAX_RATIO_VS_BASIS == iu.drift_multiple()
    import congeneric_fanout as cf
    assert abs(tv.MARKET_MAX_RATIO_VS_BASIS * cf.basis_usd_per_ns() - iu.APPROVED_USD_PER_NS) < 1e-9


@pytest.mark.parametrize("over_dollars,over_ratio", [(True, False), (False, True), (True, True)])
def test_a_failing_on_demand_block_is_NEVER_chosen(over_dollars, over_ratio):
    """The one thing this rule must never do: prefer a tier past a ceiling. Exhaustive over the failure
    combinations, because 'prefer on-demand' read carelessly is exactly 'buy the dearer thing'."""
    od = _blk(over_dollars=over_dollars, over_ratio=over_ratio, ratio=3.0)
    assert tv.choose_tier(_blk(ratio=1.0), od)[0] == tv.TIER_BID
    assert tv.choose_tier(_blk(over_ratio=True, ratio=2.0), od)[0] is None


# =============================================================================================================
# the snapshot must carry BOTH boards and the decision between them
# =============================================================================================================
def test_the_readout_shape_carries_both_tiers_and_the_choice():
    """A reader who cannot see the tier we did NOT buy cannot grade why we paid the dearer one."""
    import inspect
    src = inspect.getsource(tv.market_gate)
    for needle in ('out["tiers"]', "chosen_tier", "prefer_uninterruptible"):
        assert needle in src, f"the gate readout must expose {needle}"


def test_collect_no_longer_decides_the_tier_itself():
    """RECONCILED, not duplicated. `TVAST_ESCALATE_AFTER` used to make `collect` dispatch `-f on_demand=1`
    after N host losses. With the gate pricing BOTH tiers on every evaluation that counter can only
    disagree with it — two mechanisms choosing the same thing is the defect, not a belt and braces."""
    import pathlib
    wf = (pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows"
          / "gpu-ternary-fep-vast.yml").read_text()
    blk = wf[wf.index("Re-place any unit this pass found with no host"):][:8000]
    cmd = blk[blk.index("gh workflow run gpu-ternary-fep-vast.yml"):][:400]
    assert "on_demand=1" not in cmd, \
        "collect must not force a tier — the gate prices both and decides, and two deciders can disagree"
    assert 'OD=""' in blk and '[ "${escalate:-0}" = "1" ] && OD=' not in blk, \
        "the escalation counter must be advisory: it may PRINT, it may not choose the tier"


# =============================================================================================================
# the LAUNCH must buy the tier the GATE priced — the projection and the purchase must describe one market
# =============================================================================================================
def test_the_cli_reports_the_chosen_tier_and_fails_closed(tmp_path, capsys):
    import json as _j
    ok = tmp_path / "od.json"
    ok.write_text(_j.dumps({"chosen_tier": tv.TIER_ONDEMAND, "hold": False}))
    assert tv.main(["--gate-chose-on-demand", str(ok)]) == 0
    assert capsys.readouterr().out.strip() == "1"

    bid = tmp_path / "bid.json"
    bid.write_text(_j.dumps({"chosen_tier": tv.TIER_BID, "hold": False}))
    tv.main(["--gate-chose-on-demand", str(bid)])
    assert capsys.readouterr().out.strip() == "0"

    # A HELD snapshot bought nothing, so it cannot have chosen a tier to buy on.
    held = tmp_path / "held.json"
    held.write_text(_j.dumps({"chosen_tier": tv.TIER_ONDEMAND, "hold": True}))
    tv.main(["--gate-chose-on-demand", str(held)])
    assert capsys.readouterr().out.strip() == "0"

    # FAIL CLOSED. An unreadable snapshot must never silently buy the dearer tier.
    tv.main(["--gate-chose-on-demand", str(tmp_path / "nope.json")])
    assert capsys.readouterr().out.strip() == "0"


def test_both_gates_dispatch_the_tier_they_cleared():
    import pathlib
    wf = (pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows"
          / "gpu-ternary-fep-vast.yml").read_text()
    assert wf.count("--gate-chose-on-demand") == 3, "all three gates need it (market / triangle / 5a-KS)"
    assert '-f on_demand="$OD"' in wf
    assert wf.count('-f on_demand="${{ github.event.inputs.on_demand }}"') == 0, (
        "a gate that forwards the operator input can clear on-demand and then launch on bid — pricing one "
        "market and buying another")
