"""THE BUY LINE AND THE ⚠ DRIFT FLAG ARE ONE NUMBER, AND THAT NUMBER IS AN ABSOLUTE $/ns.

★ WHY THIS FILE EXISTS (trimcrae, 2026-07-27, two rulings that have to hold at once).

RULING 1 — the flag and the refusal are the same number: *"Why are there so many high $/ns rows that are
flagged but you're still paying for them? The whole point is to pause the test if it gets that expensive."*
A row that prints ⚠ DRIFT must be a row the launcher refuses to rent.

RULING 2 — re-express, don't move: the throughput table was re-anchored, the ladder basis fell 22 %
($0.004359 → $0.003412/ns) **with no price changing**, and a buy line typed as a MULTIPLE of that basis
silently became a far stricter rule than the one agreed — every board that day failed a line it had been
passing. The invariant is therefore the ABSOLUTE rate that was approved, and the multiple is derived from it.

The trap these two rulings create together is the reason for this file: if the buy line is re-expressed to
≈1.92× and the drift flag stays at 1.5×, rows print ⚠ DRIFT **and get bought** — which is precisely ruling 1's
complaint, recreated by the fix for ruling 2. So the two must move together, and that is asserted here rather
than left to review.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

import congeneric_fanout as cf  # noqa: E402
import inflight_usd_per_ns as inf  # noqa: E402
import relaunch_market_gate as rmg  # noqa: E402


def test_the_approved_absolute_rate_is_preserved_exactly():
    """The one thing that must not change: the dollars per nanosecond trimcrae agreed to pay."""
    assert inf.APPROVED_USD_PER_NS == pytest.approx(0.006539, abs=5e-7)


def test_the_approved_rate_is_derived_from_the_constants_that_defined_it_not_typed():
    assert inf.APPROVED_USD_PER_NS == (
        inf._APPROVAL_MULTIPLE * (inf._APPROVAL_PLAN_USD_PER_REF_GPU_H / inf._APPROVAL_REFERENCE_NS_PER_H))


def test_the_multiple_is_derived_from_the_current_basis_never_typed():
    """A future basis correction must RE-DERIVE the multiple, not silently change the rule."""
    assert inf.drift_multiple() == pytest.approx(inf.APPROVED_USD_PER_NS / cf.basis_usd_per_ns())


def test_re_expression_is_not_a_loosening_it_is_the_same_dollars():
    """1.5 × the old basis and ≈1.92 × the new one are the same absolute rate."""
    old_basis = 0.1372 / (755.36 / 24.0)
    assert 1.5 * old_basis == pytest.approx(inf.drift_multiple() * cf.basis_usd_per_ns(), rel=1e-9)


# =============================================================================================================
# THE IDENTITY — the flag and the refusal
# =============================================================================================================
def test_the_drift_flag_and_the_buy_line_are_the_same_number():
    assert cf.unit_rate_line_usd_per_ns() == inf.APPROVED_USD_PER_NS
    assert cf.drift_buy_line_x_basis() == inf.drift_multiple()


def test_the_relaunch_gate_uses_the_same_line_as_the_flag():
    """A single-host relaunch is a NEW PURCHASE and faces the same ceiling; if it did not, the cheapest way
    to buy above the line would be to let a host die and relaunch."""
    assert rmg.RELAUNCH_MAX_RATIO_VS_BASIS == pytest.approx(inf.drift_multiple(), rel=1e-9)


def test_a_row_that_prints_DRIFT_is_a_row_the_gate_REFUSES():
    """The identity, exercised end to end rather than asserted on constants.

    Sweeps the rate axis across the line and requires the two verdicts to agree at every point. If anyone
    ever re-types either threshold, this fails on the rows between the two values."""
    plan = cf._usd_per_ref_gpu_h()[1]
    basis = cf.basis_usd_per_ns()
    ns_h = 804.06 / 24.0                       # any benched card; the identity is rate-only
    for mult in (0.5, 0.9, 1.0, 1.4, 1.5, 1.8, 1.9, 1.92, 2.0, 3.0):
        target = mult * basis
        dph = target * ns_h                    # a host whose all-in rate lands exactly at `target`
        r = inf.row("RTX 4090", dph, plan, storage_usd_h=0.0)
        flagged = "⚠" in r["cell"]
        refused = rmg.verdict(target)[0]
        assert flagged == refused, (
            f"at {mult}x basis the board says flagged={flagged} but the gate says refused={refused} — "
            f"the flag and the refusal have diverged, which is exactly what ruling 1 forbids")


def test_the_flag_fires_at_the_approved_rate_and_not_before():
    plan = cf._usd_per_ref_gpu_h()[1]
    ns_h = 804.06 / 24.0
    just_under = inf.row("RTX 4090", inf.APPROVED_USD_PER_NS * 0.999 * ns_h, plan, storage_usd_h=0.0)
    just_over = inf.row("RTX 4090", inf.APPROVED_USD_PER_NS * 1.001 * ns_h, plan, storage_usd_h=0.0)
    assert "⚠" not in just_under["cell"]
    assert "⚠" in just_over["cell"]


def test_the_row_text_states_the_absolute_rate_so_nobody_reads_it_as_a_loosening():
    plan = cf._usd_per_ref_gpu_h()[1]
    ns_h = 804.06 / 24.0
    over = inf.row("RTX 4090", inf.APPROVED_USD_PER_NS * 1.2 * ns_h, plan, storage_usd_h=0.0)
    # The invariant is that the ABSOLUTE rate appears, so a reader cannot take the multiple for a loosening
    # of the rule. The line below already asserts exactly that. A companion assertion on the words
    # "approved rate" was dropped on 2026-07-31: it pinned the LABEL rather than the fact, and it failed
    # when the flag was shortened — a change that removed a per-row restatement of the §1 ruling (rule-1
    # duplication, and it had pushed the board past 250 characters) while keeping the number intact.
    assert f"{inf.APPROVED_USD_PER_NS:.6f}" in over["cell"]
    assert "×" in over["cell"], "the multiple is still shown beside the absolute rate"


def test_the_effective_ceiling_names_which_constraint_binds_with_both_expressions():
    _dollar, _rate, _eff, which = cf.unit_ceiling_components()
    assert "$" in which and "basis" in which, which
