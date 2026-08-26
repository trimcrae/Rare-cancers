"""⛔ THE STAND-DOWN SWITCH FOR THE STEP 1 FAN-OUT, AND THE THREE WAYS IT COULD FAIL OPEN.

★ WHY THIS LANE HAS A HOLD AT ALL (trimcrae, 2026-08-26: Vast has not been used in a month and this lane
is not to be driven). `congeneric_fanout_vast.py` had no operator hold; `gcp_fanout_rep.py` did, and its
comment names the trap this one would otherwise have walked into:

    "Disabling the workflow's `schedule:` does NOT pause the lane: `step1-fanout-supervisor.yml` dispatches
     ... explicitly on its own tick, so a cron edit would leave the lane feeding and look like a pause.
     The hold therefore lives in the DECISION, not in the trigger."

⛔ FAIL-SAFE IS THE WHOLE PROPERTY, AND IT POINTS AT NOT SPENDING. A hold file that cannot be read is an
instruction to stop that we failed to parse — it is NOT permission to rent a GPU. Every malformed shape
must therefore HOLD, and only an explicit DELETION may resume. That asymmetry is what these tests pin.

★ AND IT MUST PRE-EMPT THE ESCALATED MARKET HOLD. `mode_launch` raises SystemExit(2) when price has blocked
every unit past `MARKET_HOLD_ESCALATE_H`, whose message reads "trimcrae's call now" — a REQUEST FOR A
DECISION. Once the decision is made, continuing to ask is alarm fatigue, which this repository has already
paid for. So the hold is checked before `market_gate()` is ever reached, and a stood-down lane is GREEN.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import congeneric_fanout_vast as cfv  # noqa: E402


def test_the_hold_is_registered_as_a_named_placement_decision():
    """A decision the ledger cannot name is a silent hold, which §6 calls the bug."""
    assert "operator_hold" in cfv.PLACEMENT_DECISIONS, (
        "`operator_hold` is not in PLACEMENT_DECISIONS, so a stood-down tick would write a decision name "
        "no reader can resolve — indistinguishable from the price hold it is meant to replace.")


def test_a_valid_hold_holds_and_carries_its_reason(tmp_path):
    (tmp_path / cfv.OPERATOR_HOLD).write_text(json.dumps({"reason": "stood down for the test"}))
    got = cfv.operator_hold(root=str(tmp_path))
    assert got and "stood down for the test" in got["reason"], (
        "a well-formed hold must hold AND surface its reason — a pause whose cause does not travel with it "
        "is how a lane stays parked after the reason has expired.")


@pytest.mark.parametrize("body,label", [
    ("{ this is not json", "unparseable"),
    ('["not", "an", "object"]', "a list rather than an object"),
    ("", "empty"),
])
def test_a_malformed_hold_still_holds(tmp_path, body, label):
    """⛔ THE ASYMMETRY. Doubt about an instruction to STOP may never resolve to SPEND."""
    (tmp_path / cfv.OPERATOR_HOLD).write_text(body)
    got = cfv.operator_hold(root=str(tmp_path))
    assert got is not None, (
        f"a hold file that is {label} returned None, so the lane would rent. An unreadable instruction to "
        "stop is not permission to spend; every malformed shape must HOLD.")
    assert got.get("reason"), "a holding verdict must still say why it is holding"


def test_only_deleting_the_file_resumes_the_lane(tmp_path):
    """The documented resume path, pinned so it cannot drift into a code edit."""
    assert cfv.operator_hold(root=str(tmp_path)) is None, (
        "with no hold file present the lane must be free to place — otherwise the hold could never be "
        "lifted by the one action its own `_how_to_resume` documents.")


def test_the_hold_is_checked_before_the_market_gate_can_escalate():
    """A held lane must be GREEN, not an escalated red asking for a decision already made."""
    src = open(os.path.join(MOD, "congeneric_fanout_vast.py"), encoding="utf-8").read().split("\n")
    launch = next(i for i, l in enumerate(src) if l.startswith("def mode_launch("))
    hold = next(i for i, l in enumerate(src) if "STOOD DOWN BY OPERATOR" in l)
    gate = [i for i, l in enumerate(src) if "market_gate(" in l and i > launch]
    assert hold > launch, "the hold check must live inside mode_launch"
    assert gate, "no market_gate() call found inside mode_launch — this guard has lost its subject"
    assert all(g > hold for g in gate), (
        "a `market_gate()` call is reachable BEFORE the operator hold returns, so a stood-down lane could "
        "still set _MARKET_HOLD_ESCALATED and exit 2 — re-raising a question that has been answered.")
