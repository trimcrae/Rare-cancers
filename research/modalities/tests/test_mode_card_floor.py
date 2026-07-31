"""THE CARD FLOOR IS PER-MODE AND HAS ONE HOME — a floor reverted on one dispatcher must not keep running
on the other.

WHAT HAPPENED (2026-07-31). `min_ns_per_h=28` was argued for the valB closure triangle on a direct
observation: `calib_hi_to_lo2__ternary_vhl` sat at production/1720 for over two hours across three hosts and
advanced on the very next cycle once it landed on a 5090. It was then applied to RUNG 5a-KS as well — and
`collect`'s self-heal dispatched `-f min_ns_per_h=28` to WHATEVER gate the mode map returned, so the floor
rode on every 5a-KS re-placement too.

trimcrae reverted the 5a-KS floor on the supervisor tick, on the fan-out's own 208-rental ledger: 3090-class
hosts (<= $0.12/hr) held a **1.50 h median with 62 % over an hour**, against 1.65 h / 67 % for the 4090/5090
class. Card class does not predict host lifetime here, and 3090s were asked to stay in the pool. But the
revert touched ONE dispatcher, and the hardcoded `28` in the workflow went on applying it — two dispatchers
disagreeing about one lane's card policy, which is how a reverted decision keeps running.

So the floor is now DERIVED per mode from `ternary_vast_launch.MODE_MIN_NS_PER_H` (CLAUDE.md §1: one home)
and the shell asks for it instead of typing it.
"""
import os
import pathlib
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ternary_vast_launch as tv  # noqa: E402

WF = pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows" / "gpu-ternary-fep-vast.yml"
SUP = pathlib.Path(__file__).resolve().parents[3] / ".github" / "workflows" / "step1-fanout-supervisor.yml"


@pytest.mark.parametrize("mode,expect", [
    ("triangle", 28.0),
    ("triangle_smoke", 28.0),
    ("5aks", 0.0),
    ("5aks_smoke", 0.0),
    ("edge_reps", 0.0),
])
def test_the_floor_is_per_mode(mode, expect):
    assert tv.mode_min_ns_per_h(mode) == expect


def test_5aks_has_no_card_floor_and_the_reason_is_recorded():
    """The evidence must travel with the decision, or the next agent re-adds the floor from the triangle's
    argument — which is what happened once already."""
    assert tv.mode_min_ns_per_h("5aks") == 0.0
    src = open(tv.__file__).read()
    i = src.index("MODE_MIN_NS_PER_H")
    head = src[max(0, i - 2200):i]
    assert "1.50 h median" in head and "62 %" in head, \
        "the ledger measurement that retired the 5a-KS floor must be recorded beside the map"


def test_the_self_heal_dispatch_derives_the_floor_instead_of_typing_it():
    wf = WF.read_text()
    blk = wf[wf.index("Re-place any unit this pass found with no host"):][:6000]
    # The `gh workflow run` line only — the comment ABOVE it quotes the retired form on purpose (rule 1:
    # never silently drop a superseded value), so matching the whole block would fail on its own history.
    cmd = blk[blk.index("gh workflow run gpu-ternary-fep-vast.yml"):][:400]
    assert "min_ns_per_h=28" not in cmd, \
        "a hardcoded floor here is how the 5a-KS revert kept being overridden by the other dispatcher"
    assert "--min-ns-per-h-for" in blk, "the floor must be asked for, per mode"
    assert '-f min_ns_per_h="$NSF"' in cmd, "and passed through verbatim"
    # and the retention bid, which trimcrae authorised separately, must be untouched by this change
    assert "bid_floor_mult=2.0" in cmd


def test_the_supervisor_keeps_the_triangle_floor_and_not_the_5aks_one():
    sup = SUP.read_text()
    tri = sup[sup.index("-f task=triangle-gate"):][:60]
    ks = sup[sup.index("-f task=5aks-gate"):][:60]
    assert "min_ns_per_h=28" in tri, "the triangle's floor stands on its own direct observation"
    assert "min_ns_per_h" not in ks, "5a-KS's floor was reverted — it must not reappear here"


def test_the_cli_prints_the_floor_for_the_shell(capsys):
    assert tv.main(["--min-ns-per-h-for", "triangle"]) == 0
    assert capsys.readouterr().out.strip() == "28"
    assert tv.main(["--min-ns-per-h-for", "5aks"]) == 0
    assert capsys.readouterr().out.strip() == "0"


def test_every_gated_mode_has_a_floor_decision():
    """Same discipline as `MODE_GATE_TASK`: a mode that can be re-placed must have an ANSWER for its card
    floor, even if the answer is 0. A missing key reads as 0 by accident rather than by decision."""
    for mode in tv.MODE_GATE_TASK:
        assert isinstance(tv.mode_min_ns_per_h(mode), float)
