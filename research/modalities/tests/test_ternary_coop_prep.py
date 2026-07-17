"""Unit tests for ternary_coop_prep.py — the pure ternary assembly/prep layer.

Verifies the component-assembly logic (the part most prone to a silent binary/ternary or missing-component
mistake): VHL+VBC always present, target LBD present iff ternary, NR-V04 endpoints identified, calibration
endpoints correctly flagged PENDING (no fabrication), and construct reuse from nrv04_ternary. No MD/GPU/network
(default resolve_smiles=False keeps it pure)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_coop_prep as pp  # noqa: E402


def _by_id():
    return {a["leg_id"]: a for a in pp.assemble_pilot()}


def test_all_four_pilot_legs_assembled():
    a = _by_id()
    assert set(a) == {"calib_hi_to_lo__binary_vhl", "calib_hi_to_lo__ternary_vhl",
                      "nrv04_active_to_epimer__binary_vhl", "nrv04_active_to_epimer__ternary_nr4a1"}


def test_vhl_plus_vbc_always_present():
    for a in pp.assemble_pilot():
        names = [c["name"] for c in a["protein_components"]]
        assert "VHL" in names and "ElonginB" in names and "ElonginC" in names


def test_binary_legs_have_no_target_ternary_legs_do():
    a = _by_id()
    assert a["nrv04_active_to_epimer__binary_vhl"]["has_target"] is False
    assert a["calib_hi_to_lo__binary_vhl"]["has_target"] is False
    assert a["nrv04_active_to_epimer__ternary_nr4a1"]["has_target"] is True
    assert a["calib_hi_to_lo__ternary_vhl"]["has_target"] is True


def test_nr4a1_ternary_target_is_nr4a1_lbd():
    a = _by_id()["nrv04_active_to_epimer__ternary_nr4a1"]
    tgt = [c for c in a["protein_components"] if c["role"] == "target"][0]
    assert tgt["name"] == "NR4A1"
    assert tgt["acc"] == pp.NR4A_LBD["NR4A1"]["acc"]


def test_calib_ternary_target_is_smarca2():
    a = _by_id()["calib_hi_to_lo__ternary_vhl"]
    tgt = [c for c in a["protein_components"] if c["role"] == "target"][0]
    assert tgt["name"] == "SMARCA2"


def test_nrv04_endpoints_identified_calib_resolved_or_pending():
    a = _by_id()
    nrv04 = a["nrv04_active_to_epimer__binary_vhl"]["morph"]
    assert nrv04["endpoint_a"].startswith("NRV04") and nrv04["endpoint_b"].startswith("NRV04")
    calib = a["calib_hi_to_lo__binary_vhl"]["morph"]
    # The reviewer-approved PROTAC 2 -> cis-PROTAC 2 pair is frozen in ternary-calib-epimer-frozen.json; when it
    # is present the calib endpoints resolve to real (local, non-fabricated) SMILES, else they stay pending.
    if pp._load_calib_frozen() is not None:
        assert calib["status"] == "resolved_calib_epimer"
        assert calib["smiles_a"] and calib["smiles_b"]
        assert calib["smiles_a"] != calib["smiles_b"]           # active vs cis epimer (stereo differs)
    else:
        assert calib["status"] == "pending_calib_pair_freeze"
        assert calib["smiles_a"] is None and calib["smiles_b"] is None


def test_coop_cycle_roles():
    a = _by_id()
    assert "binary arm" in a["nrv04_active_to_epimer__binary_vhl"]["coop_role"]
    assert "ternary arm" in a["nrv04_active_to_epimer__ternary_nr4a1"]["coop_role"]


def test_reuses_frozen_constructs():
    # single-sourced from nrv04_ternary
    import nrv04_ternary as nv
    assert pp.E3_VHL["acc"] == nv.VHL
    assert pp.NR4A_LBD is nv.TARGETS
    assert pp.NR4A_LBD["NR4A3"]["lo"] == 373 and pp.NR4A_LBD["NR4A3"]["hi"] == 626
