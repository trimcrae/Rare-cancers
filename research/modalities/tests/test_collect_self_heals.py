"""`collect` must REPAIR the gap it detects, not describe it and wait for the next tick.

Measured 2026-07-30 lunchtime: the closure triangle's T3 ternary leg took two capacity refusals in a row
and sat NO HOST for ~20 minutes across three separate workflow runs. Nothing was broken and nothing was
over the buy line — detection lived in `collect` and repair lived in the gate, so the floor on recovery was
one tick per refusal, and each prompt repair happened only because a human dispatched it. Capacity refusals
are routine on Vast (CLAUDE.md §6), so that is a recovery path that does not work unattended.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import ternary_vast_launch as tv  # noqa: E402


@pytest.mark.parametrize("uid,mode", [
    ("calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle", "triangle"),
    ("calib_hi_to_lo2__ternary_vhl_r0_dt2.0fs_wu1.0_triangle_smoke", "triangle_smoke"),
    ("calib_hi_to_lo__ternary_vhl_r1_dt4.0fs_wu1.0_edge_reps", "edge_reps"),
    ("5aks_d0_to_d__ternary_nr4a3_r0_dt4.0fs_wu1.0_5aks_smoke", "5aks_smoke"),
    ("calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_edge", "edge"),
    ("calib_hi_to_lo__ternary_vhl_r0_dt4.0fs_wu1.0_probe", "probe"),
])
def test_mode_is_the_longest_matching_suffix(uid, mode):
    """A naive rsplit('_') returns 'reps' / 'smoke' for the multi-word modes and would route the repair to
    the wrong lane's gate — which is worse than waiting, because it wakes a launcher for units that are
    not the ones in trouble."""
    assert tv._mode_of_unit(uid) == mode


def test_a_unit_whose_suffix_is_not_a_mode_returns_none():
    assert tv._mode_of_unit("something_r0_dt2.0fs_wu1.0_notamode") is None


def test_none_and_empty_are_not_modes():
    assert tv._mode_of_unit(None) is None
    assert tv._mode_of_unit("") is None


def test_every_declared_mode_round_trips_through_a_real_unit_id():
    """Built with the launcher's own unit_id, so this cannot pass by agreeing with a hand-written string."""
    for m in tv.MODES:
        uid = tv.unit_id("some_leg", 0, "fwd", "2.0", "1.0", m)
        assert tv._mode_of_unit(uid) == m, f"{m} does not round-trip through {uid}"


def test_a_reverse_direction_unit_still_resolves_its_mode():
    uid = tv.unit_id("some_leg", 1, "rev", "4.0", "1.0", "edge_reps")
    assert "dirrev" in uid
    assert tv._mode_of_unit(uid) == "edge_reps"


def test_the_workflow_maps_every_mode_the_gates_actually_own():
    """The self-heal step routes mode -> gate task in shell. An unmapped mode must WARN and skip, never
    fall through to a default — dispatching the wrong gate is a worse failure than waiting for the tick."""
    wf = (Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml").read_text()
    step = wf.split("Re-place any unit this pass found with no host", 1)[1].split("- name: Summary LAST")[0]
    assert "triangle|triangle_smoke) TASK=triangle-gate" in step
    assert "edge_reps)               TASK=market-gate" in step
    assert "NO GATE FOR MODE" in step, "an unmapped mode must be loud"
    assert "min_ns_per_h=28" in step, "the card floor must ride along, or the repair re-places on a slow card"
    # A re-placement is by definition a leg whose last host did not survive — the one case _vast_bid_price
    # documents the escape hatch for. Safe because the charge is min(bid, on-demand) AND the gate still
    # refuses anything over the buy line, so a raised bid lands under the line or is declined on price.
    assert "bid_floor_mult=2.0" in step, "a re-placement must buy retention, not re-buy the same eviction"


def test_the_collect_job_can_actually_dispatch():
    """`actions: write` is the difference between a job that repairs and a job that narrates. Its absence
    is silent — the dispatch just 403s at runtime, long after the change looks done."""
    wf = (Path(__file__).resolve().parents[3] / ".github/workflows/gpu-ternary-fep-vast.yml").read_text()
    job = wf.split("\n  collect:", 1)[1].split("\n  triangle_diag:")[0]
    assert "actions: write" in job


def test_the_board_no_longer_promises_a_tick_will_do_it():
    """The sentence 'the next gate tick re-places it' WAS the gap, and leaving it in the readout would keep
    describing behaviour the code no longer has."""
    src = (Path(__file__).resolve().parents[1] / "ternary_vast_launch.py").read_text()
    assert "the next gate tick re-places it" not in src
    assert "this pass dispatches the gate to re-place it" in src


def test_a_finished_leg_is_never_offered_for_replacement():
    """A teardown because the unit FINISHED is not a gap. Re-placing it would re-rent a completed leg —
    the exact re-purchase the ladder must not make."""
    src = (Path(__file__).resolve().parents[1] / "ternary_vast_launch.py").read_text()
    i = src.index("_done_reason = ")
    window = src[i:i + 500]
    assert "if not _done_reason" in window, "the hostless set must be gated on the leg NOT being done"


def test_an_unreadable_instance_list_never_triggers_a_purchase():
    """When the Vast list does not read, EVERY enabled unit looks hostless. Auto-replacing then would rent
    a second host for legs that already have one — turning a readout failure into a spend."""
    src = (Path(__file__).resolve().parents[1] / "ternary_vast_launch.py").read_text()
    i = src.index("no live host — checkpoint at")
    window = src[i:i + 700]
    assert "if _inst_unreadable is None:" in window
