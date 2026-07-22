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
    # a large solvated system: PE fluctuates by ~hundreds of kcal/mol around a FLAT mean (like the real
    # 147k-atom endpoint) -> stationary -> ok, even though an absolute LSQ slope over the short window is large.
    ener = [-624700 + f for f in (300, -280, 190, -350, 260, -140, 80, -220, 310, -300,
                                  150, -260, 240, -180, 90, -320, 280, -110, 200, -240)]
    times = [0.001 * (i + 1) for i in range(len(ener))]
    r = es.energy_drift(times, ener)
    assert r["ok"] is True, r
    assert r["drift_z"] <= es.ENDPOINT_DRIFT_SIGMA


def test_real_endpoint_fluctuation_is_stable():
    # the ACTUAL first/second-half offset seen on ligB (~150-200 kcal/mol) is within the thermal fluctuation
    # (~300 kcal/mol) -> NOT a significant drift -> stationary/ok.
    import random
    rng = random.Random(0)
    ener = [-624700 - 100 + rng.uniform(-300, 300) if i < 25 else -624700 + 100 + rng.uniform(-300, 300)
            for i in range(50)]   # a ~200 kcal/mol block offset buried in ~300 kcal/mol noise
    times = [0.001 * (i + 1) for i in range(50)]
    r = es.energy_drift(times, ener)
    assert r["ok"] is True, r


def test_energy_drift_steep_is_bad():
    # a genuine heating/exploding endpoint: a strong monotonic climb far exceeding the within-block noise
    ener = [-1000.0 + 500.0 * i for i in range(20)]   # +500 kcal/mol every sample, tiny relative scatter
    times = [0.001 * (i + 1) for i in range(20)]
    r = es.energy_drift(times, ener)
    assert r["ok"] is False, r
    assert r["drift_z"] > es.ENDPOINT_DRIFT_SIGMA


def test_energy_drift_nan_is_bad():
    r = es.energy_drift([0.0, 0.01, 0.02, 0.03], [-1000.0, -1000.0, float("nan"), -1000.0])
    assert r["ok"] is False


def _flat_drift():
    ener = [-1000 + f for f in (3, -3, 2, -2, 4, -4, 1, -1)]
    return es.energy_drift([0.001 * (i + 1) for i in range(len(ener))], ener)


# --- combined verdict -------------------------------------------------------------------------------------
def test_stable_endpoint():
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=1.2, drift_result=_flat_drift(), ff_switch=ff)
    assert v["stable"] is True
    assert all(v["checks"][k] for k in ("no_nan", "ligand_rmsd_ok", "energy_drift_ok", "ff_switch_conditioner_ok"))


def test_nan_endpoint_is_unstable():
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)
    v = es.endpoint_stability_verdict(had_nan=True, max_ligand_rmsd_a=1.0, drift_result=_flat_drift(), ff_switch=ff)
    assert v["stable"] is False
    assert v["checks"]["no_nan"] is False


def test_ligand_escape_is_unstable():
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=9.0, drift_result=_flat_drift(), ff_switch=ff)
    assert v["stable"] is False
    assert v["checks"]["ligand_rmsd_ok"] is False


def test_bad_conditioner_is_advisory_not_a_hard_fail():
    # a large FF-switch minimization drop is ADVISORY (fresh-solvent relaxation dominates it for a re-solvated
    # endpoint) — it is recorded but does NOT by itself mark the physical endpoint unstable.
    ff = es.ff_switch_report(0.0, -60 * 100.0, 60)     # huge drop -> conditioner_ok False
    drift = _flat_drift()
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=1.0, drift_result=drift, ff_switch=ff)
    assert v["stable"] is True                                   # advisory does not gate
    assert v["checks"]["ff_switch_conditioner_ok"] is False      # but it is still reported
    assert v["advisory_checks"]["ff_switch_conditioner_ok"] is False


def test_hard_gates_still_fail_on_real_instability():
    # the HARD gates (NaN / RMSD / post-equilibration drift) still mark an endpoint unstable
    ff = es.ff_switch_report(-1000.0, -1010.0, 60)              # good conditioner
    steep = es.energy_drift([0.001 * (i + 1) for i in range(20)], [-1000.0 + 500.0 * i for i in range(20)])
    v = es.endpoint_stability_verdict(had_nan=False, max_ligand_rmsd_a=1.0, drift_result=steep, ff_switch=ff)
    assert v["stable"] is False
    assert v["checks"]["energy_drift_ok"] is False
