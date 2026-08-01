"""A GPU row that refuses `$/ns` must STILL show the `$/hr` it is being billed.

★★ WHY THIS TEST EXISTS (2026-08-01). Two lanes run endpoint MD, which `vast_cost_model`'s 84k-atom RBFE
throughput table cannot price. NR-V04 handled that with `inflight_board.unpriceable_usd_cell`, which refuses
the derived rate and quotes the measured one. The sensitivity control hand-wrote its own string instead —
`"— MD leg: no benched ns rate for this lane yet"` — and that string carries **no dollars at all**. It read as
correct restraint, and it was measured on the board while **19 hosts were simultaneously billing**: the lane's
entire live spend was invisible on the one artifact CLAUDE.md §1 requires to carry it.

The defect is not the refusal — the refusal is right, and shared. It is that a second implementation of a
one-home cell dropped the half of the cell that is not optional. So this test does not check any lane's
wording; it checks the PROPERTY that makes the cell useful:

    a board row for a host whose rate we KNOW must contain that rate.

That property is what a third lane would break next, in whatever new words it invented.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
if MOD not in sys.path:
    sys.path.insert(0, MOD)

import inflight_board as IB  # noqa: E402


DPH = 0.2248  # the rate one live sensitivity-control host was actually being billed at, 2026-08-01


def _shows_the_money(cell, dph):
    """Does this cell state the hourly rate? Formatting is the lane's business; the digits are not."""
    return cell is not None and ("%.4f" % dph) in cell and "/hr" in cell


def test_the_shared_cell_quotes_the_rate_it_refuses_to_convert():
    cell = IB.unpriceable_usd_cell(DPH, IB.ENDPOINT_MD_NOT_BENCHED)
    assert _shows_the_money(cell, DPH), cell
    # And it must remain visibly NOT a priced row — a reader must never mistake it for a graded $/ns.
    assert cell.startswith("—"), cell
    assert "no measured ns/h" in cell, cell


def test_an_absent_rate_is_not_rendered_as_free():
    """`None` means we did not read a rate, which is not `$0`. The cell must simply omit it (§4)."""
    cell = IB.unpriceable_usd_cell(None, IB.ENDPOINT_MD_NOT_BENCHED)
    assert "/hr" not in cell, cell
    assert "$0" not in cell, cell


def test_both_endpoint_md_lanes_give_the_same_reason():
    """One fact, one place (CLAUDE.md §1). Two lanes unpriceable for the SAME reason must not drift apart."""
    import inspect

    import nrv04_vast_launch as NV

    src = inspect.getsource(NV)
    assert "ENDPOINT_MD_NOT_BENCHED" in src, (
        "NR-V04 must point at the shared reason string rather than re-typing it")


# =============================================================================================================
# the property, applied to every lane row-builder that is handed live host records
# =============================================================================================================
def _selcal_md_rows_for_a_live_host():
    import selcal_board as B

    handles = [{"unit": "selcal-smarca4-m2-r1", "arm": "selcal_smarca4", "model": 2, "replica": 1,
                "instance": "46541800", "utc": "2026-08-01T22:06:00Z"}]
    hosts = [{"id": "46541800", "actual_status": "running", "dph_total": DPH,
              "label": "selcal-smarca4-m2-r1"}]
    return B.md_rows(handles, hosts=hosts, landed=5, n_units=24)


def test_a_billing_selcal_leg_shows_its_dollars_on_the_board():
    """THE REGRESSION. This row rendered with no money on it while the host was on the meter."""
    rows = _selcal_md_rows_for_a_live_host()
    assert len(rows) == 1, rows
    cell = rows[0]["usd_per_ns"]
    assert _shows_the_money(cell, DPH), (
        "a sensitivity-control leg on a live host rendered its $/ns cell as %r — it refuses the derived rate "
        "correctly, but a row about a host we are PAYING FOR must state what it costs" % (cell,))


def test_the_selcal_cell_is_the_shared_one_not_a_second_implementation():
    """Not just 'contains a dollar figure' — it must BE the shared cell, byte for byte.

    A lane that reproduces the output rather than calling the function passes the property test today and
    diverges the first time the shared cell changes. That divergence is the whole bug being fixed here.
    """
    rows = _selcal_md_rows_for_a_live_host()
    assert rows[0]["usd_per_ns"] == IB.unpriceable_usd_cell(DPH, IB.ENDPOINT_MD_NOT_BENCHED)


def test_a_leg_whose_host_is_gone_does_not_invent_a_rate():
    """An ENDED leg has no live record to read a rate from — and must not imply it was free."""
    import selcal_board as B

    handles = [{"unit": "selcal-smarca4-m2-r1", "instance": "46541800", "arm": "selcal_smarca4",
                "model": 2, "replica": 1, "utc": "2026-08-01T22:06:00Z"}]
    rows = B.md_rows(handles, hosts=[], landed=5, n_units=24)
    cell = rows[0]["usd_per_ns"]
    assert "/hr" not in cell, cell
    assert "$0" not in cell, cell
    assert cell.startswith("—"), cell


def test_the_dead_cross_reference_is_gone():
    """The co-fold rows used to promise that this lane's MD legs 'carry a real $/ns'. They never did.

    A pointer to a number the neighbouring rows do not produce is a rule-1 defect in its own right: it sends
    a reader looking for a figure that does not exist and makes the honest refusal next to it look like a bug.
    """
    import inspect

    import selcal_board as B

    assert "carry a real $/ns from inflight_usd_per_ns" not in inspect.getsource(B)


@pytest.mark.parametrize("dph", [0.0669, 0.1788, 0.2359])
def test_the_property_holds_across_the_rates_this_lane_actually_rented_at(dph):
    """Real rates from the 2026-08-01 fan-out, cheapest to dearest — the spread is exactly why the board
    must show them: $0.0669/hr and $0.2359/hr are the same workload, 3.5× apart."""
    assert _shows_the_money(IB.unpriceable_usd_cell(dph, IB.ENDPOINT_MD_NOT_BENCHED), dph)
