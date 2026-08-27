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
    doc = {"cycle_id": name}
    if block is not None:
        doc["subagents"] = block
    doc.update(extra)
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
# The trunk, as it stands.
# ---------------------------------------------------------------------------------------------

def test_every_receipt_on_the_trunk_passes_the_gate_today():
    """⚠ The gate must be green the moment it lands, or it is a tripwire nobody can clear — and this
    repository has already paid for one of those."""
    assert R.audit()["failures"] == []
