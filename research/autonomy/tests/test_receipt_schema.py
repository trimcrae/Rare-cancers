#!/usr/bin/env python3
"""The receipt schema, asserted rather than described (AUT-PD-013).

⛔ THE THREAT MODEL IS NOT "the validator miscounts". It is the CHEAP FIX — teaching the checker to
accept every spelling a receipt has ever used. That fix is available, it looks like tolerance, and it
silently changes the QUANTITY being measured: `launched` is the serial total over a cycle, and the cap
governs CONCURRENCY. Six agents run one at a time under a cap of 5 would read as a violation; five
launched in one message would read the same as five run in sequence. autonomy-state.json's
`_subagent_width_means` settles the unit in writing, and the 107-agent incident (40 completed, 67
errored, the synthesis lost) was ONE fan-out of width 107.

★ SO THE TESTS THAT MATTER MOST HERE ARE THE ONES THAT REFUSE A SYNONYM. A future edit that makes the
validator or the reader accept `launched` or `dispatched` as the width has rebuilt the defect with a
green board on top, and one of these fails.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import health as H  # noqa: E402
import receipt_schema as R  # noqa: E402


def _write(tmp_path, name, block, **extra):
    # ⛔ DEFAULTS TO A VALID `route_advanced` SO THESE FIXTURES STAY FOCUSED ON THE WIDTH SCHEMA
    # (AUT-PD-017). `problems()` now checks both keys unconditionally; a test in this file that is
    # about `subagents.*` and does not care about `route_advanced` should not have to say so. Pass
    # `route_advanced=...` explicitly (including `None` to omit it) to override.
    doc = {"cycle_id": name, "route_advanced": "RT-TEST"}
    if block is not None:
        doc["subagents"] = block
    doc.update(extra)
    if doc.get("route_advanced") is None:
        doc.pop("route_advanced", None)
    p = tmp_path / f"{name}.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return doc


GOVERNED = f"CYC-{R.FIRST_GOVERNED_CYCLE:04d}"
PRE = f"CYC-{R.FIRST_GOVERNED_CYCLE - 1:04d}"


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE REGRESSION. A synonym must never satisfy the width.
# ---------------------------------------------------------------------------------------------

@pytest.mark.parametrize("key", ["launched", "dispatched"])
def test_the_serial_total_does_not_satisfy_the_concurrency_cap(tmp_path, key):
    """⛔⛔ THE ONE THAT MUST NEVER GO GREEN. `launched`/`dispatched` count agents over the whole
    cycle; `subagent_width` caps how many run AT ONCE. Accepting either measures the wrong thing in
    both directions, and it is the fix a hurried session reaches for first."""
    doc = _write(tmp_path, GOVERNED, {key: 5, "cap": 5})
    assert R.width_of(doc) is None, (
        f"`{key}` was read as the governed width. It is the serial total: five sequential agents "
        "under a cap of 5 are legal, five concurrent are the cap exactly, and this key cannot tell "
        "them apart.")
    probs = R.problems(doc, str(tmp_path / f"{GOVERNED}.json"))
    assert probs and key in probs[0]
    assert R.main(["--check", "--dir", str(tmp_path)]) == 1


def test_a_rename_is_named_as_a_rename_and_still_fails(tmp_path):
    """`concurrent_max` IS the same number — and it still fails, because the reader does not read it.
    The remedy text has to say 'rename', not 'add', or the fix costs a second round."""
    doc = _write(tmp_path, GOVERNED, {"concurrent_max": 3})
    assert R.width_of(doc) is None
    probs = R.problems(doc, "x")
    assert len(probs) == 1 and "rename" in probs[0]
    assert R.DRIFTED_KEYS["concurrent_max"]["same_quantity"] is True


def test_the_same_number_may_not_be_recorded_twice_under_two_names(tmp_path):
    """CLAUDE.md §1 inside one file. Two copies of one fact can disagree, and then a future reader
    believes whichever it happened to read."""
    ok = _write(tmp_path, GOVERNED, {"max_concurrent": 5, "concurrent_max": 5})
    assert R.problems(ok, "x") == [], "an agreeing duplicate is untidy, not a defect"
    bad = _write(tmp_path, GOVERNED, {"max_concurrent": 5, "concurrent_max": 2})
    probs = R.problems(bad, "x")
    assert probs and "contradicts" in probs[0]


# ---------------------------------------------------------------------------------------------
# Recording restraint, and the absence that must never be green.
# ---------------------------------------------------------------------------------------------

def test_a_cycle_that_spawned_nobody_records_zero_and_passes(tmp_path):
    """⭐ RESTRAINT MUST BE RECORDABLE. If zero were awkward to write, the honest cycle would omit the
    block — and omission is the one thing that must not pass."""
    doc = _write(tmp_path, GOVERNED, {"max_concurrent": 0, "why_none": "one coherent edit"})
    assert R.width_of(doc) == 0
    assert R.problems(doc, "x") == []
    assert R.main(["--check", "--dir", str(tmp_path)]) == 0


def test_omitting_the_block_entirely_fails(tmp_path):
    """⛔ IF OMISSION WERE GREEN, THE CHEAPEST CLEAN BOARD WOULD BE TO STOP RECORDING DISPATCHES —
    a gate whose easiest defeat is withholding data measures compliance with itself."""
    _write(tmp_path, GOVERNED, None)
    assert R.main(["--check", "--dir", str(tmp_path)]) == 1


@pytest.mark.parametrize("value", [True, False, "5", 5.0, None, -1])
def test_a_width_that_is_not_a_whole_count_is_not_a_width(tmp_path, value):
    """`True` is an `int` in Python and would sail through a naive isinstance check as width 1."""
    doc = _write(tmp_path, GOVERNED, {"max_concurrent": value})
    assert R.width_of(doc) is None, f"{value!r} was accepted as a subagent count"
    assert R.problems(doc, "x") != []


def test_an_unreadable_receipt_is_reported_not_skipped(tmp_path):
    """A receipt nobody can parse is a cycle nobody can grade. A loader that swallows it turns a
    broken writer into a clean board."""
    (tmp_path / f"{GOVERNED}.json").write_text("{not json", encoding="utf-8")
    r = R.audit(str(tmp_path))
    assert r["unparsed"] and GOVERNED in r["unparsed"][0]
    assert R.main(["--check", "--dir", str(tmp_path)]) == 1


# ---------------------------------------------------------------------------------------------
# The anti-latching cutoff. This is the half that keeps the gate usable.
# ---------------------------------------------------------------------------------------------

def test_receipts_written_before_the_schema_never_fail_the_gate(tmp_path):
    """⛔⛔ THE LATCHING FAILURE, PRE-EMPTED. A receipt is immutable committed history. Failing the
    gate on CYC-0014's spelling would make it red forever with no action in any future session able
    to clear it — the defect that wedged the autonomy loop on 2026-08-27, where fifty consecutive
    well-behaved sessions still left the rows red."""
    _write(tmp_path, PRE, {"concurrent_max": 5})
    _write(tmp_path, "CYC-0014", {"launched": 5})
    assert R.main(["--check", "--dir", str(tmp_path)]) == 0
    assert R.audit(str(tmp_path))["failures"] == []


def test_the_grandfathered_drift_is_reported_rather_than_hidden(tmp_path, capsys):
    """★ THE TICKET WAS FILED AGAINST A CHECKER THAT HID WHAT IT COULD NOT READ. Silently dropping
    the pre-schema receipts would rebuild that defect one file over."""
    _write(tmp_path, PRE, {"concurrent_max": 5})
    R.main(["--dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert PRE in out and "concurrent_max" in out and "grandfathered" in out


def test_the_cutoff_cannot_be_raised_to_grandfather_a_live_receipt(tmp_path):
    """⛔⛔ FOUND BY MUTATION: raising `FIRST_GOVERNED_CYCLE` to 999 grandfathers EVERYTHING and every
    other test here still passed, because they build their fixtures from the constant itself. A suite
    that only ever exercises one value of a constant measures nothing about the others — the same
    finding that pinned `in_progress` in the continuity suite.

    ★ So the cutoff is bound to the record instead of to itself: it may be at most one past the
    newest receipt on the trunk. That is exactly enough to grandfather history and not one cycle
    more, and it means the only way to widen the exemption is to stop writing receipts.
    """
    newest = max(n for n in (R.cycle_number(os.path.basename(p)[:-5])
                             for p in __import__("glob").glob(os.path.join(R.RECEIPT_DIR, "*.json")))
                 if n is not None)
    assert R.FIRST_GOVERNED_CYCLE <= newest + 1, (
        f"the schema governs from CYC-{R.FIRST_GOVERNED_CYCLE:04d} but the newest receipt on the "
        f"trunk is CYC-{newest:04d}. Every cycle in between is exempt from a gate that exists, which "
        "is an exemption nobody declared.")


def test_the_cutoff_is_a_number_and_not_a_list_of_exemptions(tmp_path):
    """⚠ A hand-kept exemption list rots: every future receipt that fails invites an append. The
    cutoff must be a scalar so there is nowhere to add 'just this one'."""
    assert isinstance(R.FIRST_GOVERNED_CYCLE, int)
    assert R.cycle_number("CYC-0000-BOOTSTRAP") == 0
    assert R.cycle_number("CYC-0023") == 23
    assert R.cycle_number("not-a-cycle") is None


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE ACTUAL AUT-PD-013 REGRESSION: the reader and the writer must share ONE constant.
# ---------------------------------------------------------------------------------------------

def test_health_reads_the_key_the_schema_owns(tmp_path):
    """⛔⛔ THE BUG ITSELF. health.py spelled `max_concurrent` in its own source while the receipts
    spelled something else, and the row guarding the width dial printed a FALSE ABSENCE for cycles
    whose fan-out was recorded plainly. The two sides now share a constant; this asserts that a
    receipt written to the schema is one health.py can actually measure."""
    state = {"subagent_width": 5}
    good = {"cycle_id": GOVERNED, "subagents": {R.WIDTH_KEY: 4}}
    row = H.c_fanout_is_governed([good], state, None)
    assert not row["unmeasured"] and not row["needs_attention"], row["detail"]
    assert row["payload"]["worst"] == 4


def test_health_names_the_drifted_key_instead_of_claiming_nothing_was_recorded(tmp_path):
    """⭐ CLAUDE.md §4: name the cause, do not just count the absence. 'records no subagents block'
    was printed about receipts that plainly had one — an instrument reporting a false absence while
    wearing the costume of the restraint it could not see."""
    drifted = {"cycle_id": GOVERNED, "subagents": {"concurrent_max": 5}}
    row = H.c_fanout_is_governed([drifted], {"subagent_width": 5}, None)
    assert row["unmeasured"]
    assert "concurrent_max" in row["detail"], (
        "the diagnostic still reads as a plain absence; the drifted spelling is the one observation "
        "that discriminates between 'nobody recorded it' and 'the reader cannot see it'")
    assert row["payload"]["recorded_under_a_drifted_key"] == {GOVERNED: {"concurrent_max": 5}}


def test_an_over_cap_fanout_is_still_red(tmp_path):
    """The positive control for the whole point of the dial. Without it this suite would pass on a
    checker that has forgotten how to fail."""
    over = {"cycle_id": GOVERNED, "subagents": {R.WIDTH_KEY: 107}}
    row = H.c_fanout_is_governed([over], {"subagent_width": 5}, None)
    assert row["needs_attention"] and "107" in row["detail"]


# ---------------------------------------------------------------------------------------------
# ⛔⛔ THE SECOND KEY (AUT-PD-017): `route_advanced`, generalising AUT-PD-013's fix rather than
# re-deriving it. Same failure mode -- an absent value must fail the gate, not read as a pass -- and
# the same regression that matters most: the reader must use the constant, not its own spelling.
# ---------------------------------------------------------------------------------------------

def test_a_governed_receipt_missing_route_advanced_fails_the_gate(tmp_path):
    """⛔⛔ THE ONE THAT MUST NEVER GO GREEN. An omitted `route_advanced` is a broken writer, not a
    cycle that advanced nothing -- and before this fix nothing at the commit gate caught it."""
    doc = _write(tmp_path, GOVERNED, {R.WIDTH_KEY: 0}, route_advanced=None)
    assert R.route_advanced_of(doc) is None
    probs = R.problems(doc, str(tmp_path / f"{GOVERNED}.json"))
    assert probs and R.ROUTE_ADVANCED_KEY in probs[0]
    assert R.main(["--check", "--dir", str(tmp_path)]) == 1


@pytest.mark.parametrize("value", ["", "   ", 5, None, ["RT-X"], True])
def test_a_route_advanced_that_is_not_a_real_string_is_not_read(tmp_path, value):
    """Empty, blank or non-string values must not satisfy the schema -- an empty string is exactly
    as unreadable as an absent key, and reading `True` as a route id would be the bool-is-an-int trap
    `WIDTH_KEY`'s own tests already guard against, one type over."""
    doc = _write(tmp_path, GOVERNED, {R.WIDTH_KEY: 0}, route_advanced=value)
    assert R.route_advanced_of(doc) is None, f"{value!r} was accepted as a route"
    assert R.problems(doc, "x") != []


def test_a_governed_receipt_missing_both_keys_is_told_about_both(tmp_path):
    """⚠ THE EARLY-RETURN TRAP. A first draft of this check ran after the `subagents`-block-missing
    early return, so a receipt missing BOTH keys was only ever told about one. A receipt failing two
    independent checks must be told about both, not whichever the code happened to check first."""
    doc = {"cycle_id": GOVERNED}
    probs = R.problems(doc, "x")
    assert len(probs) == 2, f"expected one complaint per missing key, got {probs!r}"
    assert any(R.ROUTE_ADVANCED_KEY in p for p in probs)
    assert any(R.BLOCK_KEY in p for p in probs)


def test_health_reads_route_advanced_via_the_schema_constant(tmp_path):
    """⛔⛔ THE ACTUAL REGRESSION THIS ITEM EXISTS TO PREVENT: `health.py` must not spell
    `route_advanced` itself. This receipt is written under `R.ROUTE_ADVANCED_KEY`, not the literal
    string, so if a future edit renames the constant without updating `health.py`'s read, this test
    starts writing under the NEW name while `health.py` keeps reading the OLD one -- and fails."""
    receipts = [{"cycle_id": f"CYC-{n:04d}", "_file": f"CYC-{n:04d}.json",
                 R.ROUTE_ADVANCED_KEY: "none", "ended_utc": ts}
                for n, ts in enumerate(["2026-08-27T09:00:00Z", "2026-08-27T10:00:00Z",
                                        "2026-08-27T11:00:00Z"], start=1)]
    row = H.c_advancing_live_work(receipts, None)
    assert not row["unmeasured"], row["detail"]
    assert row["needs_attention"], "three genuine `none`s must still trip the row"
    assert row["payload"]["route_advanced"] == ["none", "none", "none"]


def test_a_receipt_spelling_route_advanced_differently_is_unmeasured_not_silently_green():
    """★ THE THREAT MODEL, DIRECTLY: a receipt that used a different spelling must not read as if the
    field were simply blank-and-fine, nor must the whole row read `ok` by accident. It must read
    UNMEASURED, with the absent receipt named -- exactly what `ROUTE-ADVANCED-ABSENT` already does,
    now proven against the shared constant rather than a hand-typed literal."""
    receipts = [{"cycle_id": "CYC-1", "_file": "CYC-1.json", "routes_advanced": "RT-X",
                 "ended_utc": "2026-08-27T09:00:00Z"},
                {"cycle_id": "CYC-2", "_file": "CYC-2.json", "route_advanced": "none",
                 "ended_utc": "2026-08-27T10:00:00Z"},
                {"cycle_id": "CYC-3", "_file": "CYC-3.json", "route_advanced": "none",
                 "ended_utc": "2026-08-27T11:00:00Z"}]
    row = H.c_advancing_live_work(receipts, None)
    assert row["unmeasured"] and not row["ok"] and not row["needs_attention"]
    assert row["verdict"] == "ROUTE-ADVANCED-ABSENT"


# ---------------------------------------------------------------------------------------------
# ⛔⛔ AUT-PD-155: A SESSION WITH NO `get_session` TOOL AT ALL MUST STILL BE ABLE TO PASS THIS GATE.
# ---------------------------------------------------------------------------------------------

def _ccr_doc(name, **extra):
    n = R.cycle_number(name)
    assert n is not None and n >= R.FIRST_CCR_GOVERNED_CYCLE, "fixture must be CCR-governed"
    doc = {"cycle_id": name, "route_advanced": "RT-TEST", "subagents": {R.WIDTH_KEY: 0}}
    doc.update(extra)
    return doc


def _ccr_id():
    return f"CYC-{R.FIRST_CCR_GOVERNED_CYCLE:04d}"


def test_a_valid_ccr_session_id_passes(tmp_path):
    doc = _ccr_doc(_ccr_id(), ccr_session_id="session_01ABCDEFGHIJ")
    (tmp_path / f"{doc['cycle_id']}.json").write_text(json.dumps(doc))
    assert R.problems(doc, str(tmp_path)) == []


def test_missing_both_ccr_fields_fails(tmp_path):
    doc = _ccr_doc(_ccr_id())
    problems = R.problems(doc, str(tmp_path))
    assert any(R.CCR_ID_KEY in p and R.CCR_UNAVAILABLE_FIELD in p for p in problems), problems


def test_ccr_unavailable_with_a_named_reason_passes(tmp_path):
    """★ THE ESCAPE VALVE. A session whose tool surface has no `get_session` at all (verified via
    ToolSearch, not merely a field the writer forgot) may name that instead of the id."""
    doc = _ccr_doc(_ccr_id(), ccr_session_id_unavailable=(
        "ToolSearch for get_session/create_session returned no match on this scheduled-Routine "
        "session's tool surface"))
    assert R.problems(doc, str(tmp_path)) == []


@pytest.mark.parametrize("value", ["", "   ", None, 0, False])
def test_an_empty_or_non_string_unavailable_reason_does_not_satisfy_the_valve(tmp_path, value):
    doc = _ccr_doc(_ccr_id(), ccr_session_id_unavailable=value)
    problems = R.problems(doc, str(tmp_path))
    assert any(R.CCR_ID_KEY in p for p in problems), (
        "an unnamed or blank 'unavailable' reason must not be treated as a declaration -- the same "
        "rigor `handoff.mechanism_unavailable` already applies")


def test_a_ccr_id_wins_over_an_unavailable_claim_if_both_are_present(tmp_path):
    """Both fields present is not a contradiction worth failing on -- a real id is simply the
    stronger of the two and is what matters to session_reaper.py."""
    doc = _ccr_doc(_ccr_id(), ccr_session_id="session_01ABCDEFGHIJ",
                   ccr_session_id_unavailable="stale note from an earlier draft")
    assert R.problems(doc, str(tmp_path)) == []


# ---------------------------------------------------------------------------------------------
# The trunk, as it stands.
# ---------------------------------------------------------------------------------------------

def test_every_receipt_on_the_trunk_passes_the_gate_today():
    """⚠ The gate must be green the moment it lands, or it is a tripwire nobody can clear — and this
    repository has already paid for one of those."""
    assert R.audit()["failures"] == []
