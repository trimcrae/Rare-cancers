#!/usr/bin/env python3
"""A REFUSED handoff and an ABSENT handoff mechanism must not read alike (AUT-PD-059).

⛔⛔ THE THREAT MODEL, AND IT IS NOT THE ONE THE LEDGER ROW DESCRIBED. The row said
`cycles_are_sized` "downgrades both to UNMEASURED". Measured 2026-08-28 against the two REAL
receipts on the trunk, it did something worse — it graded them OPPOSITE ways:

    CYC-0030-6be7fd5a  handoff.refused_by            -> UNMEASURED / HANDOFF-REFUSED
    CYC-0058-1ef8c95a  handoff.mechanism_unavailable -> RED        / SESSION-OVERLOADED-NO-HANDOFF

`health.py` read only `handoff.refused_by`, so the absent-mechanism shape fell through to the red
branch and was recorded as the session's own defect. `session_cap.py` had ALREADY accepted the same
field on the same receipt as an earned reason that session MAY STOP — so two modules reading one
receipt disagreed about whether stopping was correct behaviour or a failure, and the shape taking
the punitive reading (a scheduled-Routine session, no `create_session` on the tool surface at all)
is the ordinary launch for an unattended cycle rather than an edge case.

★ WHAT THIS SUITE MUST CATCH, IN BOTH DIRECTIONS:
  * a future edit that merges the two verdicts back into one — the diagnostic loss this row is
    about, because a depth refusal says "start the successor nearer the root" and an absence says
    "spawning cannot help here at all";
  * a future edit that lets EITHER blocked shape reach GREEN — no successor exists in either case,
    and green would assert the rule was satisfied;
  * a future edit that credits a receipt which recorded NOTHING, or recorded it under a name the
    reader does not know. That is the anti-gaming half: otherwise "I could not" is a free pass.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import handoff as HF  # noqa: E402
import health as H  # noqa: E402
import session_cap as SC  # noqa: E402

STATE = {"max_cycles_per_session": 2}

#: The platform's own words, from CYC-0030-6be7fd5a's receipt.
REFUSAL = ("create_session: caller session is at lineage depth 8 (limit 8); cannot spawn or re-arm "
           "further child sessions")
#: A session's own account of a check it ran, from CYC-0058-1ef8c95a's receipt.
ABSENCE = ("create_session/get_session are not present as tools at all inside this scheduled-Routine "
           "session's toolset (AUT-PD-045)")


def _capped(block=None, n=3, sid="sess-A", cycle_prefix="CYC"):
    """`n` receipts from one session, `n` > cap, with `block` on the last one."""
    rs = [{"cycle_id": f"{cycle_prefix}-{i:04d}", "session_id": sid} for i in range(n)]
    if block is not None:
        rs[-1] = {**rs[-1], "handoff": block}
    return rs


# ─────────────────────────────────────────────────────────── the shared reader (AUT-PD-017's shape)

def test_the_field_constant_names_exactly_the_path_the_reader_reads():
    """The constant is what a human is told to write (it is interpolated into the handoff prompt);
    the function is what code reads. Disagreement means a session writes a field nothing sees."""
    assert HF.UNAVAILABLE_FIELD == "handoff.mechanism_unavailable"
    top, leaf = HF.UNAVAILABLE_FIELD.split(".")
    assert HF.mechanism_unavailable_of({top: {leaf: "no create_session on this tool surface"}}) == (
        "no create_session on this tool surface")


def test_absent_blank_and_non_string_all_read_as_none():
    assert HF.mechanism_unavailable_of({}) is None
    assert HF.mechanism_unavailable_of({"handoff": {}}) is None
    assert HF.mechanism_unavailable_of({"handoff": {"mechanism_unavailable": ""}}) is None
    assert HF.mechanism_unavailable_of({"handoff": {"mechanism_unavailable": "   "}}) is None
    assert HF.mechanism_unavailable_of({"handoff": {"mechanism_unavailable": None}}) is None
    assert HF.mechanism_unavailable_of({"handoff": {"mechanism_unavailable": 5}}) is None
    assert HF.mechanism_unavailable_of({"handoff": "not-a-dict"}) is None


def test_session_cap_reads_the_shared_name_rather_than_its_own_copy():
    """⛔ session_cap.py declared the literal AND hand-rolled the two-level lookup — AUT-PD-017's
    finding one field later. Both readers must now resolve to one name and one traversal."""
    assert SC.UNAVAILABLE_FIELD is HF.UNAVAILABLE_FIELD
    assert SC.blocked_handoff({"handoff": {"mechanism_unavailable": ABSENCE}}) == ABSENCE
    assert SC.blocked_handoff({"handoff": {"refused_by": REFUSAL}}) == REFUSAL


# ──────────────────────────────────────────────────────────────────── the discrimination itself

def test_an_absent_mechanism_is_unmeasured_not_red():
    """★ THE ROW'S SUBJECT. Before this fix the same receipt scored SESSION-OVERLOADED-NO-HANDOFF —
    a defect attributed to a session that had no mechanism to use."""
    row = H.c_cycles_are_sized(_capped({"child_session_id": None,
                                        "mechanism_unavailable": ABSENCE}), STATE, None)
    assert row["unmeasured"] is True, "an absent spawn mechanism was graded as the session's defect"
    assert row["needs_attention"] is False
    assert row["verdict"] == "HANDOFF-MECHANISM-ABSENT"


def test_a_refusal_and_an_absence_do_not_share_a_verdict():
    """⛔⛔ THE DEFECT, ASSERTED DIRECTLY. Same over-cap session, same missing successor, two
    different causes — a reader who cannot tell them apart cannot pick a remedy."""
    refused = H.c_cycles_are_sized(_capped({"refused_by": REFUSAL}), STATE, None)
    absent = H.c_cycles_are_sized(_capped({"mechanism_unavailable": ABSENCE}), STATE, None)
    assert refused["verdict"] != absent["verdict"], (
        "a depth-limit refusal and an absent tool now read identically again")
    assert refused["verdict"] == "HANDOFF-REFUSED"
    assert absent["verdict"] == "HANDOFF-MECHANISM-ABSENT"


def test_each_verdict_carries_the_remedy_that_fits_ITS_cause():
    """★ THE DIAGNOSTIC VALUE, WHICH IS THE ONLY REASON TO SPLIT THE VERDICTS. A refusal means the
    tool works nearer the root, so a shallower successor is the move. An absence means nothing can
    be called from this launch shape at all, so a shallower spawn is not the move and the scheduled
    Routine is the successor. Printing one remedy for both sends a future session the wrong way."""
    refused = H.c_cycles_are_sized(_capped({"refused_by": REFUSAL}), STATE, None)["detail"]
    absent = H.c_cycles_are_sized(_capped({"mechanism_unavailable": ABSENCE}), STATE, None)["detail"]
    assert "shallower" in refused, "the refusal branch no longer names the remedy that fits it"
    assert "lineage depth" in refused, (
        "the platform's own words are gone, so a reader cannot tell a real ceiling from an excuse")
    assert "not present as tools" in absent, "the absence branch does not quote what was searched for"
    assert "does not help" in absent or "ONLY one" in absent, (
        "the absence branch does not tell the reader that spawning nearer the root cannot help")
    assert refused != absent


def test_the_payload_separates_the_two_populations_for_a_machine_reader():
    """A verdict line names one shape; the payload must name both, or a consumer that reads JSON
    rather than prose loses whichever shape did not win the line."""
    row = H.c_cycles_are_sized(_capped({"mechanism_unavailable": ABSENCE}), STATE, None)
    assert row["payload"]["over_cap_but_mechanism_absent"] == ["sess-A"]
    # `_row` strips None-valued payload keys, so "absent" is the assertion, not "is None".
    assert "over_cap_but_handoff_refused" not in row["payload"]
    row = H.c_cycles_are_sized(_capped({"refused_by": REFUSAL}), STATE, None)
    assert row["payload"]["over_cap_but_handoff_refused"] == ["sess-A"]
    assert "over_cap_but_mechanism_absent" not in row["payload"]


def test_both_populations_survive_when_both_are_present():
    """⚠ Two over-cap sessions blocked two different ways. The line can only name one — it names the
    refusal, which carries the platform's words — but neither may DISAPPEAR."""
    receipts = (_capped({"refused_by": REFUSAL}, sid="sess-A", cycle_prefix="CYA")
                + _capped({"mechanism_unavailable": ABSENCE}, sid="sess-B", cycle_prefix="CYB"))
    row = H.c_cycles_are_sized(receipts, STATE, None)
    assert row["verdict"] == "HANDOFF-REFUSED"
    assert row["payload"]["over_cap_but_handoff_refused"] == ["sess-A"]
    assert row["payload"]["over_cap_but_mechanism_absent"] == ["sess-B"], (
        "the absent-mechanism session vanished from the board because a refused one outranked it")
    assert "over_cap_but_mechanism_absent" in row["detail"], (
        "a human reading only the line would never learn the other population exists")


def test_a_receipt_recording_both_is_read_as_the_refusal():
    """⛔ REFUSAL WINS A TIE — a call was made and words came back, which is the stronger evidence.
    Reading it as an absence would throw the platform's own answer away."""
    row = H.c_cycles_are_sized(
        _capped({"refused_by": REFUSAL, "mechanism_unavailable": ABSENCE}), STATE, None)
    assert row["verdict"] == "HANDOFF-REFUSED"
    assert "over_cap_but_mechanism_absent" not in row["payload"], (
        "a receipt carrying both fields was counted in BOTH populations")


# ────────────────────────────────────────────────────────────────────────── the anti-gaming half

def test_neither_blocked_shape_can_ever_reach_green():
    """⛔ THE DIRECTION THAT WOULD BE EASIEST AND IS WRONG. No successor exists in either case, so
    the work did NOT continue in a fresh context. `ok` must stay False for both."""
    for block in ({"refused_by": REFUSAL}, {"mechanism_unavailable": ABSENCE}):
        row = H.c_cycles_are_sized(_capped(block), STATE, None)
        assert row["ok"] is False, f"{block} bought a green row"


def test_a_session_that_recorded_nothing_stays_red():
    """The whole integrity of this: "the tool wasn't there" must be a RECORD, not an assumption."""
    row = H.c_cycles_are_sized(_capped(None), STATE, None)
    assert row["verdict"] == "SESSION-OVERLOADED-NO-HANDOFF"
    assert row["needs_attention"] is True


def test_an_ad_hoc_field_name_is_not_credited():
    """⛔ ~20 receipts on the trunk recorded this fact under `_why_not_attempted`, a name nobody
    reads; CYC-0058-1ef8c95a corrected itself to `mechanism_unavailable` for exactly that reason.
    Accepting invented spellings would make the field unfalsifiable — any prose in the handoff block
    would clear the row. The handoff PROMPT now names both fields, so a session has no excuse."""
    for spelling in ("_why_not_attempted", "mechanism_absent", "why", "unavailable"):
        row = H.c_cycles_are_sized(_capped({spelling: ABSENCE}), STATE, None)
        assert row["verdict"] == "SESSION-OVERLOADED-NO-HANDOFF", (
            f"`{spelling}` was silently accepted as a real absent-mechanism record")


def test_a_handed_off_session_is_still_green_regardless():
    """The positive control. A real successor beats both blocked branches — otherwise this suite
    could pass on a checker that never grades anything green."""
    row = H.c_cycles_are_sized(
        _capped({"child_session_id": "session_01ABC", "mechanism_unavailable": ABSENCE}),
        STATE, None)
    assert row["verdict"] == "SIZED"
    assert row["ok"] is True


# ────────────────────────────────────────────────────────── the prompt half: a name nobody knows

def test_the_handoff_prompt_names_both_fields_from_the_constants():
    """★ THE REACHABILITY HALF. A session cannot record a field name it was never told. The prompt
    told the successor only where to put a SUCCESSFUL handoff's child id, which is why the failure
    case was written ~20 different ways. Interpolated from the constants, never typed, so a rename
    cannot leave the instructions pointing at the old name."""
    prompt = HF.build(reason="test", ledger={"entries": []}, state={"max_cycles_per_session": 2})
    assert HF.CHILD_ID_FIELD in prompt
    assert HF.REFUSAL_FIELD in prompt, "a refused handoff has nowhere the reader knows to go"
    assert HF.UNAVAILABLE_FIELD in prompt, "an absent mechanism has nowhere the reader knows to go"
