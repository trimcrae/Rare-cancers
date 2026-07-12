"""Data-integrity tests for the FROZEN Layer-1 VHL calibration values (reviewer 2026-07-12, Req 1 & 4).

Verifies the transcribed Supplementary Table 1 numbers against internal consistency: P5's alpha recomputed
from its binary/ternary IC50 columns, the complete five-PDB mapping (incl P2=7Z77), the alpha_TR-FRET
observable labeling + P5 text discrepancy record, and the archived SI checksum. Reads the REAL frozen JSON."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FROZEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nr4a3-ternary-coop-prereg.json")


def _panel():
    d = json.load(open(FROZEN))
    return d["calibration"]["layer1_vhl_panel"]


def _by_id():
    return {s["id"]: s for s in _panel()["candidate_systems"]}


def test_p5_alpha_recomputed_from_ic50_columns():
    # reviewer Req 1: recompute the central alpha from the two IC50 columns. alpha_TR-FRET = IC50(binary)/IC50(ternary)
    p5 = _by_id()["smarca2_p5"]
    recomputed = p5["ic50_binary_nM"] / float(p5["ic50_ternary_nM"])
    assert abs(recomputed - p5["measured_alpha"]) <= 0.1        # 98/160 = 0.61 ~ 0.6 (table)


def test_all_five_smarca2_verified_with_pdb():
    b = _by_id()
    expected_pdb = {"smarca2_p1": "9HYN", "smarca2_p2": "7Z77", "smarca2_p3": "9HYB",
                    "smarca2_p4": "9HYO", "smarca2_p5": "9HYP"}
    for sid, pdb in expected_pdb.items():
        assert b[sid]["pdb"] == pdb                            # complete five-PDB panel incl P2=7Z77
        assert b[sid]["verified"] is True
        assert isinstance(b[sid]["measured_alpha"], (int, float))


def test_frozen_numeric_alpha_values():
    b = _by_id()
    assert b["smarca2_p1"]["measured_alpha"] == 93.0
    assert b["smarca2_p2"]["measured_alpha"] == 4.1
    assert b["smarca2_p3"]["measured_alpha"] == 5.0
    assert b["smarca2_p4"]["measured_alpha"] == 1.3
    assert b["smarca2_p5"]["measured_alpha"] == 0.6


def test_alpha_ordering_matches_prespecified_tiers():
    b = _by_id()
    # P1 > {P2,P3} > P4 > P5 on the point estimates (P2,P3 close/tied within uncertainty)
    a = {k: b["smarca2_%s" % k]["measured_alpha"] for k in ("p1", "p2", "p3", "p4", "p5")}
    assert a["p1"] > max(a["p2"], a["p3"]) > a["p4"] > a["p5"]


def test_observable_is_labelled_apparent_tr_fret():
    obs = _panel()["observable"]
    assert "TR-FRET" in obs["name"]
    assert "IC50(binary) / IC50(ternary)" in obs["definition"]
    assert "NOT a direct equilibrium Kd" in obs["definition"]


def test_p5_text_discrepancy_recorded():
    p5 = _by_id()["smarca2_p5"]
    assert "0.2" in p5["text_discrepancy"] and "0.6" in p5["text_discrepancy"]


def test_si_checksum_archived():
    cs = _panel()["curation_status"]["si_archive"]
    assert len(cs["sha256"]) == 64 and cs["bytes"] > 0
    assert "Supplementary Table 1" in cs["table_locator"]


def test_prespecified_tie_is_p2_p3():
    tiers = _panel()["prespecified_ordinal_tiers"]
    assert ["smarca2_p2", "smarca2_p3"] in tiers["tie_groups"]


# --- panel completion: MZ1 (independent control) + inactive control + frozen expected_system_ids ------------
def test_mz1_alpha_frozen_from_gadd_2017():
    mz1 = _by_id()["mz1_brd4bd2_vhl"]
    assert mz1["measured_alpha"] == 18.0          # Gadd 2017 Table 1, Brd4 BD2
    assert mz1["independent_vhl"] is True and mz1["is_mz1"] is True and mz1["verified"] is True
    assert mz1["primary_ref"]["pmcid"] == "PMC5392356"
    assert "18" in mz1["primary_ref"]["quote"]


def test_inactive_control_present_and_knockout():
    ic = _by_id()["vhl_cis_hyp_inactive_control"]
    assert ic["measured_class"] == "inactive_control"
    assert ic["measured_alpha"] is None           # knockout — no measured cooperative alpha
    assert ic["verified"] is True


def test_expected_system_ids_populated_with_seven():
    ids = _panel()["expected_system_ids"]
    assert set(ids) == {"smarca2_p1", "smarca2_p2", "smarca2_p3", "smarca2_p4", "smarca2_p5",
                        "mz1_brd4bd2_vhl", "vhl_cis_hyp_inactive_control"}


def test_panel_composition_valid():
    b = _by_id()
    # >=2 strong cooperative (alpha >= 2): P1,P2,P3,MZ1 ; >=2 weak/negative (alpha < 2 here): P4,P5 ;
    # >=1 inactive control ; >=1 independent VHL (MZ1)
    coop = [k for k in b if b[k].get("measured_alpha") not in (None,) and b[k]["measured_alpha"] >= 2.0]
    weak = [k for k in b if b[k].get("measured_alpha") not in (None,) and b[k]["measured_alpha"] < 2.0]
    assert len(coop) >= 2 and len(weak) >= 2
    assert any(b[k].get("measured_class") == "inactive_control" for k in b)
    assert any(b[k].get("independent_vhl") for k in b)
