#!/usr/bin/env python3
"""Pins for the retention-bid resolver.

The danger this file guards is not that the resolver breaks — it is that it QUIETLY WIDENS. A retention bid is
a deliberate decision to pay above the market floor on one named leg; every test below exists to stop that
turning into a standing raise across the lane, which is the constraint the lever's author set explicitly."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import retention_bid as RB  # noqa: E402


def _cfg(tmp_path, entries):
    p = tmp_path / "retention-bid.json"
    p.write_text(json.dumps({"retention": entries}))
    return str(p)


def _gate(tmp_path, needing):
    p = tmp_path / "gate.json"
    p.write_text(json.dumps({"units_needing_host": needing}))
    return str(p)


# ---- the default is ALWAYS "change nothing" -----------------------------------------------------------------
def test_empty_config_resolves_to_nothing(tmp_path):
    assert RB.resolve(config_path=_cfg(tmp_path, []), gate_path=_gate(tmp_path, ["anything"])) == ""


def test_disabled_entry_resolves_to_nothing(tmp_path):
    c = _cfg(tmp_path, [{"enabled": False, "leg_substring": "abc", "mult": 1.25}])
    assert RB.resolve(config_path=c, gate_path=_gate(tmp_path, ["abc_unit"])) == ""


def test_missing_files_resolve_to_nothing_rather_than_raising(tmp_path):
    """A gate tick must never fail because this file is absent — the lane predates it."""
    assert RB.resolve(config_path=str(tmp_path / "nope.json"), gate_path=str(tmp_path / "nope2.json")) == ""


def test_the_shipped_config_is_retired(tmp_path):
    """T3 landed, so the shipped entry must be disabled. If someone re-enables it without a churning leg,
    this fails and asks them to justify it."""
    with open(RB.CONFIG) as fh:
        entries = json.load(fh)["retention"]
    assert all(not e.get("enabled") for e in entries), "a live retention entry needs a documented churning leg"
    assert all("_retire_when" in e for e in entries), "every entry must carry its own expiry condition"


# ---- scope: ONE named leg, and only when it needs a host ----------------------------------------------------
def test_matches_only_a_unit_that_actually_needs_a_host(tmp_path):
    """A retention bid on a leg whose host is holding buys nothing and costs money. Matching against the
    pending set is what prevents that."""
    c = _cfg(tmp_path, [{"enabled": True, "leg_substring": "t3_leg", "mult": 1.25}])
    assert RB.resolve(config_path=c, gate_path=_gate(tmp_path, ["t3_leg_r0"])) == "1.25"
    assert RB.resolve(config_path=c, gate_path=_gate(tmp_path, ["some_other_leg"])) == ""
    assert RB.resolve(config_path=c, gate_path=_gate(tmp_path, [])) == ""


def test_does_not_apply_to_unnamed_legs(tmp_path):
    """The whole point: every leg not named keeps the lane's default bid policy."""
    c = _cfg(tmp_path, [{"enabled": True, "leg_substring": "t3_leg", "mult": 1.25}])
    assert RB.resolve(config_path=c, gate_path=_gate(tmp_path, ["ternary_a", "binary_b"])) == ""


# ---- precedence: a human aiming by hand is never overridden --------------------------------------------------
def test_explicit_input_wins_over_the_file(tmp_path):
    c = _cfg(tmp_path, [{"enabled": True, "leg_substring": "t3_leg", "mult": 1.25}])
    assert RB.resolve("1.40", config_path=c, gate_path=_gate(tmp_path, ["t3_leg_r0"])) == "1.40"


def test_explicit_input_wins_even_when_the_file_would_not_match(tmp_path):
    c = _cfg(tmp_path, [])
    assert RB.resolve("1.40", config_path=c, gate_path=_gate(tmp_path, ["whatever"])) == "1.40"


# ---- the CLI, which is what the workflow actually calls ------------------------------------------------------
def test_flags_are_not_mistaken_for_an_explicit_bid():
    """`--explain` alone must explain the FILE, not read as an explicit bid of '--explain'. This was a real
    bug caught before the wiring landed."""
    val, why = RB.explain("")
    assert not why.startswith("explicit dispatch input --explain")


def test_explain_names_the_authorisation_when_a_bid_is_applied(tmp_path):
    """Money moving with no line saying why is the reporting defect this repo already fixed once on the
    $/ns board. An applied retention bid must always be able to say who authorised it."""
    c = _cfg(tmp_path, [{"enabled": True, "leg_substring": "t3_leg", "mult": 1.25,
                         "_authorised_by": "trimcrae, test"}])
    val, why = RB.explain("", config_path=c, gate_path=_gate(tmp_path, ["t3_leg_r0"]))
    assert val == "1.25"
    assert "authorised: trimcrae, test" in why


def test_explain_says_why_when_no_bid_is_applied(tmp_path):
    val, why = RB.explain("", config_path=_cfg(tmp_path, []), gate_path=_gate(tmp_path, []))
    assert val == ""
    assert "no retention bid" in why
