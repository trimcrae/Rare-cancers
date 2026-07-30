"""`TVAST_ON_DEMAND=1` must rent the UNINTERRUPTIBLE tier — the one thing a bid cannot buy.

Vast's community bid tier is interruptible by design, and `gpu_backend` records the documented rule that
an on-demand renter preempts an interruptible one REGARDLESS of bid. So VAST_BID_FLOOR_MULT buys priority
WITHIN the tier and cannot stop eviction.

That stopped being academic on 2026-07-30: the closure triangle's last ternary leg went through five hosts
in 2.5 hours without one surviving the ~28 min it needs to stage and reach a single 40-iteration commit
boundary. Every rental was correctly priced, correctly gated and correctly re-placed; the census sat at
production/1840 all afternoon anyway. When mean host lifetime is below time-to-first-commit, faster
recovery cannot converge.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ternary_vast_launch as tv  # noqa: E402
from gpu_backend import _vast_offer_query  # noqa: E402

WF = Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml"


def test_default_is_still_the_cheap_interruptible_tier(monkeypatch):
    """OFF BY DEFAULT AND IT MUST STAY OFF — the whole ladder is priced on interruptible rentals plus
    per-unit checkpointing. A standing on-demand default would silently rewrite the cost model."""
    monkeypatch.delenv("TVAST_ON_DEMAND", raising=False)
    assert tv.resource_spec().interruptible is True


@pytest.mark.parametrize("val", ["1", "true", "yes", " 1 ", "TRUE", "Yes"])
def test_the_flag_turns_off_interruptibility(monkeypatch, val):
    monkeypatch.setenv("TVAST_ON_DEMAND", val)
    assert tv.resource_spec().interruptible is False


@pytest.mark.parametrize("val", ["", "0", "false", "no", "off", " "])
def test_anything_that_is_not_an_affirmative_leaves_the_cheap_tier(monkeypatch, val):
    """An unset workflow input arrives as the EMPTY STRING, not as absent — so `if os.environ.get(...)`
    would be false-y and safe, but `"0"` would be TRUTHY and would silently buy the expensive tier."""
    monkeypatch.setenv("TVAST_ON_DEMAND", val)
    assert tv.resource_spec().interruptible is True


def test_the_spec_actually_changes_the_market_query(monkeypatch):
    """The flag has to reach the OFFER QUERY, not just sit on the dataclass. `type` selects the tier."""
    monkeypatch.setenv("TVAST_ON_DEMAND", "1")
    assert _vast_offer_query(tv.resource_spec())["type"] == "on-demand"
    monkeypatch.setenv("TVAST_ON_DEMAND", "0")
    assert _vast_offer_query(tv.resource_spec())["type"] == "bid"


def test_the_buy_line_still_applies_to_an_on_demand_spec(monkeypatch):
    """The point of the flag is to convert 'we cannot keep a host' into a PRICED question, not to buy an
    exemption. max_usd_per_ns must be untouched by it."""
    monkeypatch.setenv("TVAST_ON_DEMAND", "1")
    assert tv.resource_spec(max_usd_per_ns=0.006539).max_usd_per_ns == 0.006539
    assert tv.resource_spec().max_usd_per_ns is None  # the gate still sees expensive offers, to report them


def test_the_card_floor_and_the_tier_are_independent(monkeypatch):
    monkeypatch.setenv("TVAST_ON_DEMAND", "1")
    monkeypatch.setenv("TVAST_MIN_NS_PER_H", "33")
    spec = tv.resource_spec()
    assert spec.interruptible is False and spec.min_ns_per_h == 33.0


def test_the_workflow_exposes_the_input_and_wires_it_everywhere_min_ns_is_wired():
    """A tier flag that reaches the gate but not the launch would price on-demand and then rent bid — the
    worst of both. Every site that carries the card floor must carry the tier."""
    wf = WF.read_text()
    assert "      on_demand:" in wf
    assert wf.count("TVAST_ON_DEMAND: ${{ github.event.inputs.on_demand }}") == \
           wf.count("TVAST_MIN_NS_PER_H: ${{ github.event.inputs.min_ns_per_h }}")


def test_both_gate_self_dispatches_forward_the_tier():
    """The gates dispatch the launch themselves. If they drop on_demand, a gate that cleared ON-DEMAND
    prices would hand the launch back to the interruptible tier and re-buy the eviction."""
    wf = WF.read_text()
    assert wf.count('-f on_demand="${{ github.event.inputs.on_demand }}"') == 2
