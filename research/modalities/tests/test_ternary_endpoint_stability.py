"""Reviewer condition 2 (2026-07-19) — the PURE core of the exact-Hamiltonian endpoint conditioning/stability
diagnostics (no OpenMM/OpenFE): FF-switch energy relaxation, energy-drift verdict, and the combined stability
decision. The GPU wrapper (run_endpoint_stability) is validated on the box, not here."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ternary_endpoint_stability as es  # noqa: E402


# --- FF-switch conditioner report -------------------------------------------------------------------------
def test_ff_switch_small_drop_is_ok():
    # a good conditioner: minimization barely lowers the energy
    r = es.ff_switch_report(pe_initial_kcal=-1000.0, pe_minimized_kcal=-1050.0, n_solute_heavy=60)
    assert r["conditioner_ok"] is True
    assert abs(r["min_energy_drop_kcal"] - 50.0) < 1e-9
    assert abs(r["drop_per_solute_heavy_atom_kcal"] - 50.0 / 60) < 1e-9


def test_ff_switch_large_per_atom_drop_flags_bad_conditioner():
    # a bad conditioner: huge per-atom relaxation after the FF switch
    r = es.ff_switch_report(pe_initial_kcal=0.0, pe_minimized_kcal=-60 * 100.0, n_solute_heavy=60)
    assert r["conditioner_ok"] is False
    assert r["drop_per_solute_heavy_atom_kcal"] > es.FF_SWITCH_DROP_PER_ATOM_MAX_KCAL


def test_ff_switch_missing_pe():
    assert es.ff_switch_report(None, -1.0, 60)["conditioner_ok"] is None


# --- energy drift -----------------------------------------------------------------------------------------
def test_energy_drift_flat_is_ok():
    times = [0.0, 0.01, 0.02, 0.03]
    ener = [-1000.0, -1000.1, -999.9, -1000.05]      # essentially flat
    r = es.energy_drift(times, ener)
    assert r["ok"] is True
    assert abs(r["drift_kcal_per_ns"]) < es.ENDPOINT_DRIFT_MAX_KCAL_PER_NS


def test_energy_drift_steep_is_bad():
    times = [0.0, 0.01, 0.02, 0.03]
    ener = [-1000.0, -990.0, -980.0, -970.0]          # +1000 kcal/mol/ns climb
    r = es.energy_drift(times, ener)
    assert r["drift_kcal_per_ns"] > es.ENDPOINT_DRIFT_MAX_KCAL_PER_NS
    assert r["ok"] is False


def test_energy_drift_nan_is_bad():
    r = es.energy_drift([0.0, 0.01], [-1000.0, float("nan")])
    assert r["ok"] is False


# --- combined verdict -------------------------------------------------------------------------------------
def test_stable_endpoint():
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)
    drift = es.energy_drift([0.0, 0.01, 0.02], [-1000.0, -1000.1, -999.95])
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=1.2, drift_result=drift, ff_switch=ff)
    assert v["stable"] is True
    assert all(v["checks"][k] for k in ("no_nan", "ligand_rmsd_ok", "energy_drift_ok", "ff_switch_conditioner_ok"))


def test_nan_endpoint_is_unstable():
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)
    drift = es.energy_drift([0.0, 0.01], [-1000.0, -1000.1])
    v = es.endpoint_stability_verdict(had_nan=True, max_ligand_rmsd_a=1.0, drift_result=drift, ff_switch=ff)
    assert v["stable"] is False
    assert v["checks"]["no_nan"] is False


def test_ligand_escape_is_unstable():
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)
    drift = es.energy_drift([0.0, 0.01], [-1000.0, -1000.1])
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=9.0, drift_result=drift, ff_switch=ff)
    assert v["stable"] is False
    assert v["checks"]["ligand_rmsd_ok"] is False


def test_bad_conditioner_makes_endpoint_unstable():
    ff = es.ff_switch_report(0.0, -60 * 100.0, 60)     # huge drop -> conditioner_ok False
    drift = es.energy_drift([0.0, 0.01], [-1000.0, -1000.1])
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=1.0, drift_result=drift, ff_switch=ff)
    assert v["stable"] is False
    assert v["checks"]["ff_switch_conditioner_ok"] is False
