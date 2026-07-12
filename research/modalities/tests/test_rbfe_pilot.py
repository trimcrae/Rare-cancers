"""Unit tests for rbfe_pilot.py — the pure congeneric binary-RBFE pilot core + abort gate + plan.

Exercises the pilot edge resolution (from the frozen map + series), the two morph legs, the pre-registered
abort gate (pass + each failure mode, fail-closed on missing fields), and the MODE=plan forecast — no MD/GPU/
network. Reads the REAL frozen JSONs so a drift in the map is caught here."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rbfe_pilot as rp  # noqa: E402


# --- pilot edge resolution ----------------------------------------------------------------------------------
def test_pilot_edge_resolves_endpoints_and_smiles():
    e = rp.pilot_edge()
    assert e["edge_id"] == "e_zaienne_cmpd19__cw_ev_5nh2"
    assert e["node_a"] == "zaienne_cmpd19" and e["node_b"] == "cw_ev_5nh2"
    # the frozen endpoint SMILES (5-Br indole ester -> 5-amino)
    assert e["smiles_a"] == "COC(=O)c1c[nH]c2ccc(Br)cc12"
    assert e["smiles_b"] == "COC(=O)c1c[nH]c2ccc(N)cc12"
    assert e["single_site"] is True
    assert e["design_frame_role"].startswith("nr4a3_design")
    assert e["receptors"] == ["nr4a3"]


def test_pilot_legs_are_solvent_plus_one_complex():
    legs = rp.pilot_legs()
    kinds = [k for (_n, _r, k) in legs]
    assert kinds == ["solvent", "complex"]      # NO per-paralogue legs (pilot = convergence, not selectivity)
    assert len(legs) == 2


def test_pilot_edge_drift_fails_closed(tmp_path):
    import json
    m = rp.load_map()
    m["pilot_edge_id"] = "e_does_not_exist"
    p = tmp_path / "map.json"
    p.write_text(json.dumps(m))
    try:
        rp.pilot_edge(map_path=str(p))
        assert False, "expected ValueError on unknown pilot_edge_id"
    except ValueError as e:
        assert "not found" in str(e)


# --- abort gate ---------------------------------------------------------------------------------------------
def _passing_result():
    return {"per_leg_hysteresis_kcal": {"solvent": 0.2, "complex-nr4a3_design": 0.4},
            "min_mbar_overlap": 0.05, "cycle_closure_kcal": None,
            "pocket_survival_frac": 0.8, "pocket_volume_below_apo_frac": 0.1}


def test_abort_gate_pass():
    out = rp.evaluate_abort_gate(_passing_result())
    assert out["passed"] is True
    assert "calibrate" in out["decision"]


def test_abort_gate_hysteresis_fail():
    r = _passing_result()
    r["per_leg_hysteresis_kcal"]["complex-nr4a3_design"] = 0.9   # > 0.5
    out = rp.evaluate_abort_gate(r)
    assert out["passed"] is False and any("hysteresis" in x for x in out["failures"])
    assert "HALT" in out["decision"]


def test_abort_gate_low_overlap_fail():
    r = _passing_result()
    r["min_mbar_overlap"] = 0.01   # < 0.03
    assert rp.evaluate_abort_gate(r)["passed"] is False


def test_abort_gate_pocket_collapse_fail():
    r = _passing_result()
    r["pocket_survival_frac"] = 0.3   # < 0.5
    out = rp.evaluate_abort_gate(r)
    assert out["passed"] is False and any("pocket survival" in x for x in out["failures"])


def test_abort_gate_pocket_volume_collapse_fail():
    r = _passing_result()
    r["pocket_volume_below_apo_frac"] = 0.7   # > 0.5 of windows below apo-open
    assert rp.evaluate_abort_gate(r)["passed"] is False


def test_abort_gate_cycle_closure_supplied_but_bad_fails():
    r = _passing_result()
    r["cycle_closure_kcal"] = 1.5   # > 1.0 when present
    assert rp.evaluate_abort_gate(r)["passed"] is False


def test_abort_gate_missing_fields_fail_closed():
    assert rp.evaluate_abort_gate({})["passed"] is False
    # non-finite hysteresis is not silently ignored
    r = _passing_result()
    r["per_leg_hysteresis_kcal"]["solvent"] = float("nan")
    assert rp.evaluate_abort_gate(r)["passed"] is False


# --- plan -------------------------------------------------------------------------------------------------
def test_plan_is_two_legs_and_cheap():
    p = rp.plan(n_windows=12, unit_gpu_h=2.0, spot_hourly=0.50)
    assert p["n_legs"] == 2
    assert abs(p["forecast_gpu_h"] - 2 * 12 * 2.0) < 1e-6
    assert abs(p["forecast_cost_usd"] - p["forecast_gpu_h"] * 0.50) < 1e-6
    # cheap by design (authorized ~$5-15 band at realistic small window counts)
    assert p["forecast_cost_usd"] < 50


def test_plan_labels_stub():
    p = rp.plan()
    assert "unit_gpu_h_STUB" in p and "STUB" in p["honesty"]


# --- docking preflight (reviewer 2026-07-12, Plan C) --------------------------------------------------------
def _passing_prep():
    return {"construct_frozen": True, "residue_numbering": "NR4A3 373-626", "receptor_repairs_documented": True,
            "protonation_documented": True, "ligand_states_a": ["neutral"], "ligand_states_b": ["neutral"],
            "docking_grid_identical": True, "mcs_overlap_frac": 0.9, "atom_map_ok": True,
            "parameterized_ok": True, "net_charge_a": 0, "net_charge_b": 0, "charge_correction": False,
            "min_ok": True, "max_clash_ok": True, "severe_strain": False}


def test_docking_preflight_pass():
    out = rp.docking_preflight(_passing_prep())
    assert out["passed"] is True and "proceed" in out["decision"]
    assert "INPUT STAGING" in out["output_status"]


def test_docking_preflight_low_mcs_aborts():
    p = _passing_prep()
    p["mcs_overlap_frac"] = 0.4
    out = rp.docking_preflight(p)
    assert out["passed"] is False and "ABORT" in out["decision"]


def test_docking_preflight_net_charge_change_needs_correction():
    p = _passing_prep()
    p["net_charge_a"], p["net_charge_b"] = 0, -1
    assert rp.docking_preflight(p)["passed"] is False
    p["charge_correction"] = True
    assert rp.docking_preflight(p)["passed"] is True


def test_docking_preflight_missing_fields_fail_closed():
    assert rp.docking_preflight({})["passed"] is False
    p = _passing_prep(); del p["ligand_states_b"]
    assert rp.docking_preflight(p)["passed"] is False


def test_docking_preflight_severe_strain_aborts():
    p = _passing_prep(); p["severe_strain"] = True
    assert rp.docking_preflight(p)["passed"] is False


def test_docking_preflight_flags_br_nh2_not_gentle():
    assert "NOT a gentle" in rp.docking_preflight(_passing_prep())["perturbation_note"]
