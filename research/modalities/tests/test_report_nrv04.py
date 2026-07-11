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


def test_full_gate_informative_on_productive_geometry():
    # Degraded bridges in a majority; both spared bridge in a minority -> clean geometric separation.
    systems = {
        "nr4a1": _ternary([True, True, True], [0.62, 0.60, 0.64], lys_d=[5.0, 5.5, 6.0]),
        "nr4a2": _ternary([False, False, False], [0.40, 0.42, 0.38], lys_d=[7.0, 7.5, 8.0]),
        "nr4a3": _ternary([False, False, False], [0.35, 0.37, 0.36], lys_d=[9.0, 9.5, 10.0]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "informative"
    assert v["primary_basis"] == "productive_ternary_geometry"
    assert v["lys_supports"] is True


def test_full_gate_informative_even_when_ligand_iptm_inverts():
    # The REAL NR-V04 case: NR4A1 bridges 3/3, spared 0/3, but ligand-iPTM is HIGHER for a spared paralogue.
    # Geometry must drive the verdict (informative) while ligand-iPTM verdict is reported as failed/transparent.
    systems = {
        "nr4a1": _ternary([True, True, True], [0.82, 0.91, 0.84], lys_d=[3.6, 3.3, 9.7]),
        "nr4a2": _ternary([False, False, False], [0.91, 0.92, 0.90], lys_d=[12.5, 4.4, 4.3]),
        "nr4a3": _ternary([False, False, False], [0.92, 0.87, 0.84], lys_d=[12.2, 7.3, 7.7]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "informative"
    assert v["ligand_iptm_verdict"] == "failed"     # naive scalar inverts...
    assert "not the primary basis" in v["ligand_iptm_note"].lower()


def test_full_gate_failed_when_degraded_does_not_bridge():
    systems = {
        "nr4a1": _ternary([False, False, False], [0.35, 0.4, 0.38]),
        "nr4a2": _ternary([False, False, False], [0.60, 0.6, 0.62]),
        "nr4a3": _ternary([False, False, False], [0.58, 0.5, 0.55]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "failed"


def test_full_gate_inconclusive_when_spared_also_bridges():
    systems = {
        "nr4a1": _ternary([True, True, True], [0.50, 0.5, 0.5]),
        "nr4a2": _ternary([True, True, False], [0.49, 0.5, 0.4]),   # spared also bridges majority
        "nr4a3": _ternary([False, False, False], [0.48, 0.4, 0.4]),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "inconclusive"
