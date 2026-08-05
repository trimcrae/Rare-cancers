#!/usr/bin/env python3
"""Unit tests for the three-body cooperative degradation model (nr4a3_degradation_model.py).

Checks the physics is right: conservation-bounded ternary (never > target total), correct monotonic
response to cooperativity and binary affinity, and a hook effect at high PROTAC concentration.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "research", "modalities"))
import nr4a3_degradation_model as dm  # noqa: E402

P = dict(dm.DEFAULTS)


def test_ternary_never_exceeds_target_total():
    # [ternary] <= T_tot and <= E_tot for any PROTAC concentration (the bug the nested solver fixed).
    for logP in range(-11, -1):
        tpe = dm.ternary_concentration(10.0 ** logP, P["T_tot"], P["E_tot"],
                                       P["Kd_target"], P["Kd_e3"], alpha=10.0)
        assert 0.0 <= tpe <= P["T_tot"] + 1e-18
        assert tpe <= P["E_tot"] + 1e-18


def test_dc50_decreases_with_cooperativity():
    sm = dm.sensitivity_map(P, alphas=(1.0, 3.0, 10.0))
    dc = [sm[f"alpha_{a}"]["DC50_M"] for a in (1.0, 3.0, 10.0)]
    assert all(x is not None for x in dc), dc
    assert dc[0] > dc[1] > dc[2]                      # higher alpha -> more potent (lower DC50)


def test_dmax_increases_with_cooperativity_and_affinity():
    sm = dm.sensitivity_map(P, alphas=(0.3, 1.0, 3.0, 10.0))
    dmax = [sm[f"alpha_{a}"]["Dmax"] for a in (0.3, 1.0, 3.0, 10.0)]
    assert dmax[0] < dmax[1] < dmax[2] < dmax[3]
    km = dm.kd_target_map(P, kds=(1e-8, 1e-7, 1e-6, 1e-5), alpha=3.0)
    dmax_kd = [km[f"KdTarget_{kd:.0e}"]["Dmax"] for kd in (1e-8, 1e-7, 1e-6, 1e-5)]
    assert dmax_kd[0] > dmax_kd[1] > dmax_kd[2] > dmax_kd[3]   # tighter Kd -> more degradation


def test_hook_effect_present_at_high_cooperativity():
    curve = dm.hook_curve(P["T_tot"], P["E_tot"], P["Kd_target"], P["Kd_e3"], alpha=10.0)
    w = dm.degradation_window(curve, P["ksyn_over_kdeg"])
    assert w["hook"]["hook_effect_present"] is True
    # ternary peak occurs before the last (highest) PROTAC concentration = the hook
    assert w["hook"]["ternary_peak_P_M"] < curve[-1]["P_M"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("ok:", name)
    print("all degradation-model tests passed")
