"""Unit tests for report_nrv04 decision logic — moiety split, aggregation, and the pilot/full verdict gates.

Geometry parsing from CIFs needs gemmi (GPU/CI); here we test the pure logic by feeding sample dicts + the
moiety-split core directly."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import report_nrv04 as r  # noqa: E402

CUT = ["%.1f" % c for c in r.CUTOFFS]  # ["4.0","4.5","5.0"]


def _control(seated_flags, lig_iptm):
    samples = [{"seed": "seed_%d" % i, "rank": 0, "confidence": {"ligand_iptm": v, "iptm": v},
                "geometry": {"seated": s}} for i, (s, v) in enumerate(zip(seated_flags, lig_iptm), 1)]
    return {"system": "control", "kind": "control", "samples": samples,
            "ensemble": r._aggregate(samples, "control")}


def _ternary(moiety_bridge_flags, lig_iptm, lys_d=None, wrong=None, name="nr4a1"):
    """Build a ternary system from per-sample moiety-bridge flags (assumed same at all cutoffs unless a dict)."""
    n = len(moiety_bridge_flags)
    lys_d = lys_d or [10.0] * n
    wrong = wrong or [False] * n
    samples = []
    for i, (b, v, d, w) in enumerate(zip(moiety_bridge_flags, lig_iptm, lys_d, wrong), 1):
        br = b if isinstance(b, dict) else {c: bool(b) for c in CUT}
        samples.append({"seed": "seed_%d" % i, "rank": 0, "confidence": {"ligand_iptm": v, "iptm": v},
                        "geometry": {"bridges": bool(br[CUT[1]]),
                                     "closest_exposed_lys": {"resnum": 590, "dist_A": d, "counts": {}}},
                        "moiety": {"moiety_bridges": br, "moiety_bridges_default": br[CUT[1]], "wrong_end": w}})
    return {"system": name, "kind": "ternary", "samples": samples, "ensemble": r._aggregate(samples, "ternary")}


# --- moiety split core (no gemmi) ------------------------------------------------------------------------
def test_split_ligand_ends_uses_unique_sulfur():
    # Linear chain: S at one end (VH032 anchor), C's trailing away; farthest C = celastrol terminus.
    atoms = [("S", (0, 0, 0)), ("C", (1, 0, 0)), ("C", (2, 0, 0)), ("C", (9, 0, 0)), ("O", (10, 0, 0))]
    vhl_end, nr4a_end, note = r.split_ligand_ends(atoms)
    assert (0, 0, 0) in vhl_end and (1, 0, 0) in vhl_end          # near S
    assert (10, 0, 0) in nr4a_end and (9, 0, 0) in nr4a_end       # near far terminus
    assert "S-anchor" in note


def test_split_ligand_ends_falls_back_without_one_sulfur():
    atoms = [("C", (0, 0, 0)), ("C", (1, 0, 0)), ("C", (2, 0, 0))]   # zero S
    vhl_end, nr4a_end, note = r.split_ligand_ends(atoms)
    assert vhl_end == nr4a_end and "fallback" in note


def test_dist_stats():
    d = r._dist([0.4, 0.6, 0.5])
    assert d["n"] == 3 and d["mean"] == 0.5


# --- aggregation -----------------------------------------------------------------------------------------
def test_aggregate_control_seated_fraction():
    c = _control([True, True, False], [0.7, 0.65, 0.2])
    e = c["ensemble"]
    assert e["n_seated"] == 2 and e["n_scored"] == 3
    assert e["seated_fraction"] == round(2 / 3, 3)


def test_aggregate_moiety_bridged_and_lys_relabelled():
    t = _ternary([True, True, True], [0.6, 0.55, 0.62], lys_d=[9.0, 11.0, 10.0])
    e = t["ensemble"]
    assert e["moiety_bridged_default"] == 1.0
    assert e["moiety_bridged_fraction"][CUT[1]]["n_bridged"] == 3
    assert e["lys_nz_to_vhl_A"]["mean"] == 10.0        # relabelled field
    assert "closest_lys_A" not in e                     # old name gone
    assert "SASA" in e["lys_caveat"]


def test_aggregate_wrong_end_fraction():
    t = _ternary([True, True, True], [0.6, 0.6, 0.6], wrong=[True, False, False])
    assert t["ensemble"]["wrong_end_fraction"] == round(1 / 3, 3)


# --- pilot gate ------------------------------------------------------------------------------------------
def test_pilot_gate_proceed_on_moiety_bridging():
    c = _control([True, True, True], [0.7, 0.68, 0.66])
    t = _ternary([True, True, False], [0.6, 0.58, 0.3])   # moiety-bridged 2/3
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "PROCEED" and v["control_ok"] and v["nr4a1_ok"]


def test_pilot_gate_abort_when_nr4a1_not_moiety_productive():
    c = _control([True, True, True], [0.7, 0.7, 0.7])
    t = _ternary([False, False, True], [0.2, 0.25, 0.5])  # moiety-bridged 1/3
    v = r.pilot_verdict(c, t)
    assert v["verdict"] == "ABORT" and v["nr4a1_ok"] is False


# --- full verdict (exploratory concordance) --------------------------------------------------------------
def test_full_gate_exploratory_concordance_on_moiety_separation():
    systems = {
        "nr4a1": _ternary([True, True, True], [0.62, 0.60, 0.64], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.40, 0.42, 0.38], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.35, 0.37, 0.36], name="nr4a3"),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "exploratory-concordance"
    assert v["primary_basis"] == "moiety_specific_ternary_geometry"
    assert v["cutoff_robust"] is True
    assert v["leave_one_seed_out_robust"] is True
    assert "not validation" in v["basis"].lower()


def test_full_gate_concordance_holds_even_when_ligand_iptm_inverts():
    # Real NR-V04 shape: moiety-separation clean, but ligand-iPTM higher for a spared paralogue.
    systems = {
        "nr4a1": _ternary([True, True, True], [0.82, 0.91, 0.84], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.91, 0.92, 0.90], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.92, 0.87, 0.84], name="nr4a3"),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "exploratory-concordance"
    assert v["ligand_iptm_note"] and "did not reproduce" in v["ligand_iptm_note"].lower()


def test_full_gate_discordant_when_degraded_does_not_bridge():
    systems = {
        "nr4a1": _ternary([False, False, False], [0.35, 0.4, 0.38], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.60, 0.6, 0.62], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.58, 0.5, 0.55], name="nr4a3"),
    }
    assert r.full_verdict(systems)["verdict"] == "discordant"


def test_full_gate_inconclusive_when_spared_also_bridges():
    systems = {
        "nr4a1": _ternary([True, True, True], [0.5, 0.5, 0.5], name="nr4a1"),
        "nr4a2": _ternary([True, True, False], [0.5, 0.5, 0.4], name="nr4a2"),   # spared also bridges majority
        "nr4a3": _ternary([False, False, False], [0.4, 0.4, 0.4], name="nr4a3"),
    }
    assert r.full_verdict(systems)["verdict"] == "inconclusive"


def test_full_gate_cutoff_not_robust_flagged():
    # Bridged at 4.5/5.0 but not 4.0 for NR4A1 -> cutoff_robust False, still concordant at default.
    perc = {"4.0": False, "4.5": True, "5.0": True}
    systems = {
        "nr4a1": _ternary([perc, perc, perc], [0.6, 0.6, 0.6], name="nr4a1"),
        "nr4a2": _ternary([False, False, False], [0.4, 0.4, 0.4], name="nr4a2"),
        "nr4a3": _ternary([False, False, False], [0.4, 0.4, 0.4], name="nr4a3"),
    }
    v = r.full_verdict(systems)
    assert v["verdict"] == "exploratory-concordance"
    assert v["cutoff_robust"] is False
