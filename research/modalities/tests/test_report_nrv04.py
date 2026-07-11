"""Unit tests for report_nrv04 decision logic — the pilot/full verdict gates + ensemble aggregation.

Geometry parsing needs gemmi (GPU/CI); here we test the pure logic that drives the fan-out spend decision by
feeding per-seed dicts directly."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import report_nrv04 as r  # noqa: E402


def _control(seated_flags, lig_iptm):
    per = [{"seed": "seed_%d" % i, "confidence": {"ligand_iptm": v, "iptm": v},
            "geometry": {"seated": s}} for i, (s, v) in enumerate(zip(seated_flags, lig_iptm), 1)]
    return {"system": "control", "kind": "control", "n_seeds": len(per), "per_seed": per,
            "ensemble": r._aggregate(per, "control")}


def _ternary(bridge_flags, lig_iptm, lys_d=None):
    lys_d = lys_d or [10.0] * len(bridge_flags)
    per = [{"seed": "seed_%d" % i, "confidence": {"ligand_iptm": v, "iptm": v},
            "geometry": {"bridges": b, "closest_exposed_lys": {"resnum": 590, "dist_A": d, "counts": {}}}}
           for i, (b, v, d) in enumerate(zip(bridge_flags, lig_iptm, lys_d), 1)]
    return {"system": "nr4a1", "kind": "ternary", "n_seeds": len(per), "per_seed": per,
            "ensemble": r._aggregate(per, "ternary")}


def test_dist_stats():
    d = r._dist([0.4, 0.6, 0.5])
    assert d["n"] == 3 and d["mean"] == 0.5 and d["min"] == 0.4 and d["max"] == 0.6


def test_aggregate_control_seated_fraction():
    c = _control([True, True, False], [0.7, 0.65, 0.2])
    e = c["ensemble"]
    assert e["n_seated"] == 2 and e["n_scored"] == 3
    assert e["seated_fraction"] == round(2 / 3, 3)
    assert e["ligand_iptm"]["mean"] == round((0.7 + 0.65 + 0.2) / 3, 4)


def test_aggregate_ternary_bridged_and_lys():
    t = _ternary([True, True, True], [0.6, 0.55, 0.62], lys_d=[9.0, 11.0, 10.0])
    e = t["ensemble"]
    assert e["n_bridged"] == 3 and e["bridged_fraction"] == 1.0
    assert e["closest_lys_A"]["mean"] == 10.0


def test_pilot_gate_proceed():
    c = _control([True, True, True], [0.7, 0.68, 0.66])
    t = _ternary([True, True, False], [0.6, 0.58, 0.3])  # bridged 2/3 → majority
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "PROCEED"
    assert v["control_ok"] and v["nr4a1_ok"]


def test_pilot_gate_abort_when_control_fails():
    c = _control([False, False, True], [0.2, 0.15, 0.5])  # seated 1/3 → below 0.5
    t = _ternary([True, True, True], [0.6, 0.6, 0.6])
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "ABORT"
    assert v["control_ok"] is False


def test_pilot_gate_abort_when_nr4a1_not_productive():
    c = _control([True, True, True], [0.7, 0.7, 0.7])
    t = _ternary([False, False, True], [0.2, 0.25, 0.5])  # bridged 1/3
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "ABORT"
    assert v["nr4a1_ok"] is False


def test_pilot_gate_abort_when_missing_system():
    c = _control([True, True], [0.7, 0.7])
    v = r.pilot_verdict(c, None)      # NR4A1 leg absent
    assert v["verdict"] == "ABORT"


def test_full_gate_informative_when_nr4a1_highest():
    systems = {
        "nr4a1": _ternary([True, True, True], [0.62, 0.60, 0.64]),
        "nr4a2": _ternary([True, True, True], [0.40, 0.42, 0.38]),
        "nr4a3": _ternary([True, True, True], [0.35, 0.37, 0.36]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "informative"


def test_full_gate_failed_when_wrong_paralogue_wins():
    systems = {
        "nr4a1": _ternary([True], [0.35]),
        "nr4a2": _ternary([True], [0.60]),
        "nr4a3": _ternary([True], [0.58]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "failed"


def test_full_gate_inconclusive_when_tied():
    systems = {
        "nr4a1": _ternary([True], [0.50]),
        "nr4a2": _ternary([True], [0.49]),
        "nr4a3": _ternary([True], [0.48]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "inconclusive"
