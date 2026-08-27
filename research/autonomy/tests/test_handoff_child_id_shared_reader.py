#!/usr/bin/env python3
"""`handoff.child_session_id`, the second name AUT-PD-017 fixed (AUT-PD-013's fix, generalised).

⛔⛔ THE THREAT MODEL. `health.py`'s `c_cycles_are_sized` used to re-derive the two-level lookup
(`receipt.get("handoff", {}).get("child_session_id")`) directly in its own source — the field name
AND the traversal, spelled a second time, agreed with `handoff.py`'s own `CHILD_ID_FIELD` constant
only by never being touched. That is the exact AUT-PD-013 shape one level deeper: a NESTED field
name agreed in prose (and in a hand-copied dict literal) between a writer and a reader is not agreed
at all. `handoff.py` now owns both the name (`CHILD_ID_FIELD`) and the read (`child_session_id_of`);
`health.py` calls the function instead of re-deriving it.

★ WHAT THIS MUST CATCH: a future edit that changes `child_session_id_of`'s lookup without updating
`CHILD_ID_FIELD` (or vice versa), or a future edit to `health.py` that goes back to hand-rolling the
lookup instead of calling the shared function — both would let an over-cap session with a real
handoff read as SESSION-OVERLOADED-NO-HANDOFF, a false positive on the exact row CLAUDE.md §6
measures the session-shape rule by.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import handoff as HF  # noqa: E402
import health as H  # noqa: E402


def _capped(n=3, sid="sess-A", extra_handoff=None):
    """`n` receipts from one over-cap session, optionally with a handoff recorded on the last one."""
    out = []
    for i in range(n):
        r = {"cycle_id": f"CYC-{i:04d}", "session_id": sid, "_file": f"CYC-{i:04d}.json"}
        if i == n - 1 and extra_handoff is not None:
            r["handoff"] = extra_handoff
        out.append(r)
    return out


# ---------------------------------------------------------------------------------------------
# `CHILD_ID_FIELD` / `child_session_id_of` agree with each other by construction.
# ---------------------------------------------------------------------------------------------

def test_the_field_constant_names_exactly_the_path_the_reader_reads():
    """The constant is documentation for a HUMAN filling in a receipt (it appears, interpolated, in
    the handoff prompt itself); the function is what code actually reads. They must describe the
    same two-level path or a human following the prompt writes something the code cannot see."""
    assert HF.CHILD_ID_FIELD == "handoff.child_session_id"
    top, leaf = HF.CHILD_ID_FIELD.split(".")
    assert HF.child_session_id_of({top: {leaf: "session_01ABC"}}) == "session_01ABC"


def test_absent_blank_and_non_string_all_read_as_none():
    assert HF.child_session_id_of({}) is None
    assert HF.child_session_id_of({"handoff": {}}) is None
    assert HF.child_session_id_of({"handoff": {"child_session_id": ""}}) is None
    assert HF.child_session_id_of({"handoff": {"child_session_id": "   "}}) is None
    assert HF.child_session_id_of({"handoff": {"child_session_id": None}}) is None
    assert HF.child_session_id_of({"handoff": {"child_session_id": 5}}) is None
    assert HF.child_session_id_of({"handoff": "not-a-dict"}) is None


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE ACTUAL REGRESSION: health.py must call the shared function, not its own lookup.
# ---------------------------------------------------------------------------------------------

def test_health_credits_a_handoff_recorded_under_the_shared_constant():
    """An over-cap session that recorded its handoff correctly must read GREEN (SIZED), not RED —
    this is the positive control AUT-PD-017 exists to keep from silently flipping back to red."""
    receipts = _capped(n=3, extra_handoff={"child_session_id": "session_01XYZ"})
    row = H.c_cycles_are_sized(receipts, {"max_cycles_per_session": 2}, None)
    assert row["verdict"] == "SIZED", row["detail"]
    assert row["payload"]["handed_off"] == ["sess-A"]


def test_health_still_reds_an_over_cap_session_with_no_handoff():
    """The positive control for the other direction — without it this suite could pass on a checker
    that credits every session as handed off."""
    receipts = _capped(n=3, extra_handoff=None)
    row = H.c_cycles_are_sized(receipts, {"max_cycles_per_session": 2}, None)
    assert row["verdict"] == "SESSION-OVERLOADED-NO-HANDOFF"


def test_health_does_not_credit_a_handoff_recorded_under_a_different_spelling():
    """★ THE THREAT MODEL, DIRECTLY. If a receipt records the child id under `child_id` or
    `handoff_child_session_id` instead of `handoff.child_session_id`, health.py must NOT silently
    treat the session as handed off — that would be the false-GREEN direction, worse than the
    false-RED `c_fanout_is_governed` already guards against for the sibling key."""
    receipts = _capped(n=3, extra_handoff={"child_id": "session_01XYZ"})
    row = H.c_cycles_are_sized(receipts, {"max_cycles_per_session": 2}, None)
    assert row["verdict"] == "SESSION-OVERLOADED-NO-HANDOFF", (
        "a differently-spelled handoff field was silently accepted as a real one")


def test_the_message_names_the_field_from_the_constant_not_a_hand_typed_literal():
    """The remedy text health.py prints must interpolate `handoff.CHILD_ID_FIELD` rather than
    spelling the field a third time — otherwise a rename of the constant leaves the human-facing
    instructions telling the reader to write the OLD name."""
    receipts = _capped(n=3, extra_handoff=None)
    row = H.c_cycles_are_sized(receipts, {"max_cycles_per_session": 2}, None)
    assert HF.CHILD_ID_FIELD in row["detail"]
