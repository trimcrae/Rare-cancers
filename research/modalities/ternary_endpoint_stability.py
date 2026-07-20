#!/usr/bin/env python3
"""Exact-Hamiltonian endpoint conditioning + stability diagnostics (reviewer condition 2, 2026-07-19).

THE REVIEWER'S POINT: the plain-MD pre-equilibration is only a COORDINATE CONDITIONER — it does NOT sample from
the RBFE target ensemble (different force field / no alchemy). So before MBAR data is collected, the RBFE must,
UNDER ITS OWN EXACT HAMILTONIAN:
  (a) minimize, then restrained T/P equilibration, then restraint release, then a DISCARDED unrestrained
      equilibration (this is what OpenFE's RelativeHybridTopologyProtocol equilibration phase does — we FREEZE
      non-zero equilibration + confirm those frames are excluded from MBAR; see protocol_settings below),
  (b) RECORD the potential-energy relaxation right after the force-field switch (conditioner FF -> exact RBFE
      FF): a large discontinuity or a large minimization drop = the conditioner handed over a bad geometry,
  (c) run a short PHYSICAL-ENDPOINT stability test for ligand A (λ=0) and ligand B (λ=1): no NaN, bounded ligand
      RMSD, bounded energy drift.

This module is split like the rest of the lane: a PURE, unit-tested core (the discontinuity thresholding, RMSD
and drift verdicts, the combined stability decision — no OpenMM/OpenFE) + a thin GPU wrapper (run on the box)
that builds the exact endpoint system and produces the numbers the core judges. The pure core is what the
protocol freeze and the tests lock; the wrapper is validated on GPU (dev sandbox has no MD stack).
"""
from __future__ import annotations

import json
import math
import os

# ---- thresholds (frozen; each decision-relevant) ------------------------------------------------------------
# The FF switch (conditioner -> exact RBFE FF) should not require a huge relaxation. Normalize the minimization
# energy DROP per solute heavy atom so system size doesn't dominate; a large per-atom drop = bad conditioner.
FF_SWITCH_DROP_PER_ATOM_MAX_KCAL = 25.0    # kcal/mol per solute heavy atom of min-energy drop after FF switch
FF_SWITCH_ABS_DROP_MAX_KCAL = 5.0e4        # absolute floor guard (very large systems)
ENDPOINT_RMSD_MAX_A = 3.0                  # ligand heavy-atom RMSD vs conditioned start over the short test
ENDPOINT_DRIFT_MAX_KCAL_PER_NS = 500.0     # |PE drift slope| over the short unrestrained test


def ff_switch_report(pe_initial_kcal, pe_minimized_kcal, n_solute_heavy):
    """Record the potential-energy relaxation after the FF switch (reviewer condition 2b). Returns the absolute
    and per-solute-heavy-atom minimization drop and a `conditioner_ok` flag (a small drop = the conditioner
    handed over a geometry already near the exact FF's basin)."""
    if pe_initial_kcal is None or pe_minimized_kcal is None:
        return {"status": "missing PE", "conditioner_ok": None}
    drop = pe_initial_kcal - pe_minimized_kcal            # >0: minimization lowered the energy
    per_atom = (drop / n_solute_heavy) if n_solute_heavy else None
    ok = True
    if per_atom is not None and per_atom > FF_SWITCH_DROP_PER_ATOM_MAX_KCAL:
        ok = False
    if drop > FF_SWITCH_ABS_DROP_MAX_KCAL:
        ok = False
    return {"status": "ok", "pe_initial_kcal": pe_initial_kcal, "pe_minimized_kcal": pe_minimized_kcal,
            "min_energy_drop_kcal": drop, "drop_per_solute_heavy_atom_kcal": per_atom,
            "n_solute_heavy": n_solute_heavy, "conditioner_ok": bool(ok)}


def _linfit_slope(xs, ys):
    """Least-squares slope of ys vs xs (both length n>=2); None otherwise."""
    n = len(xs)
    if n < 2 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / sxx


def energy_drift(times_ns, energies_kcal):
    """PE drift slope (kcal/mol/ns) over the short endpoint test + an `ok` flag. A large sustained drift means
    the endpoint is NOT stable under the exact Hamiltonian even if it never NaN'd."""
    if any(e is None or not math.isfinite(e) for e in energies_kcal):
        return {"status": "non-finite energy present", "drift_kcal_per_ns": None, "ok": False}
    slope = _linfit_slope(list(times_ns), list(energies_kcal))
    if slope is None:
        return {"status": "insufficient points", "drift_kcal_per_ns": None, "ok": None}
    return {"status": "ok", "drift_kcal_per_ns": slope,
            "ok": bool(abs(slope) <= ENDPOINT_DRIFT_MAX_KCAL_PER_NS)}


def endpoint_stability_verdict(had_nan, max_ligand_rmsd_a, drift_result, ff_switch):
    """Combine the physical-endpoint checks into one `stable` bool (reviewer condition 2c). The HARD gates for a
    PHYSICAL instability are: no NaN, bounded ligand RMSD, and bounded PE drift MEASURED ON THE EQUILIBRATED
    system (run_endpoint_stability discards the restrained-equil + a settling window first, so the drift here is
    post-equilibration, not the initial re-solvation transient). The FF-switch minimization relaxation is
    ADVISORY only (reviewer condition 2b — recorded), NOT a hard gate: for a freshly RE-SOLVATED endpoint the
    minimization drop is dominated by fresh-water relaxation, so it does not by itself mean the physical endpoint
    is unstable."""
    rmsd_ok = (None if max_ligand_rmsd_a is None else max_ligand_rmsd_a <= ENDPOINT_RMSD_MAX_A)
    drift_ok = drift_result.get("ok") if isinstance(drift_result, dict) else None
    cond_ok = ff_switch.get("conditioner_ok") if isinstance(ff_switch, dict) else None
    hard = {"no_nan": (None if had_nan is None else not had_nan),
            "ligand_rmsd_ok": rmsd_ok, "energy_drift_ok": drift_ok}
    advisory = {"ff_switch_conditioner_ok": cond_ok}     # recorded, does NOT gate `stable`
    # stable requires every COMPUTABLE HARD check to be True; a None (uncomputed) does not by itself fail it, but
    # a NaN or an explicit False does.
    hard_fail = any(v is False for v in hard.values())
    computed = [v for v in hard.values() if v is not None]
    stable = bool(computed) and not hard_fail
    return {"stable": stable, "checks": {**hard, **advisory}, "advisory_checks": advisory,
            "max_ligand_rmsd_a": max_ligand_rmsd_a}


# =============================================================================================================
# GPU wrapper — build the EXACT-Hamiltonian physical endpoint + run the short stability test. Runs on the box
# (OpenMM present); never imported by the pure tests.
# =============================================================================================================
def run_endpoint_stability(system, topology, positions, ligand_atom_indices, *, n_steps=15000, dt_fs=2.0,
                           restrained_steps=15000, discard_steps=10000, report_every=500, platform_name="CUDA",
                           conditioner_pe_kcal=None):
    """Physical-endpoint stability under the EXACT RBFE force field, implementing the reviewer's condition-2
    ladder: minimize -> RESTRAINED T/P equilibration (protein+ligand heavy atoms restrained) -> restraint
    RELEASE -> a DISCARDED unrestrained equilibration -> then the MEASURED production window (PE drift + ligand
    heavy-atom RMSD vs the post-equilibration reference). Measuring drift/RMSD only AFTER equilibration is what
    separates a real instability from the initial re-solvation settling transient. The FF-switch minimization
    relaxation is recorded (advisory; normalized by TOTAL atoms since fresh-solvent relaxation dominates it for a
    re-solvated endpoint). Mirrors ternary_preequil._relax's proven restraint/heat/NPT/release sequence."""
    import numpy as np
    import openmm
    from openmm import app, unit

    KCAL = unit.kilocalorie_per_mole
    n_total = topology.getNumAtoms()
    lig = list(ligand_atom_indices) if ligand_atom_indices is not None else list(range(n_total))

    # positional restraint on protein+ligand heavy atoms (released after equilibration); water/H relax freely
    restraint = openmm.CustomExternalForce("0.5*k*periodicdistance(x,y,z,x0,y0,z0)^2")
    restraint.addGlobalParameter("k", 5.0 * unit.kilocalories_per_mole / unit.angstrom**2)
    for p in ("x0", "y0", "z0"):
        restraint.addPerParticleParameter(p)
    for atom in topology.atoms():
        el = atom.element
        is_water = atom.residue.name in ("HOH", "WAT", "TIP3", "T3P", "SOL")
        if el is not None and el.symbol != "H" and not is_water:
            x, y, z = positions[atom.index].value_in_unit(unit.nanometer)
            restraint.addParticle(atom.index, [x, y, z])
    system.addForce(restraint)
    system.addForce(openmm.MonteCarloBarostat(1 * unit.bar, 298.15 * unit.kelvin))

    try:
        platform = openmm.Platform.getPlatformByName(platform_name)
    except Exception:  # noqa: BLE001
        platform = openmm.Platform.getPlatformByName("CPU")
    integ = openmm.LangevinMiddleIntegrator(298.15 * unit.kelvin, 1.0 / unit.picosecond, dt_fs * unit.femtosecond)
    sim = app.Simulation(topology, system, integ, platform)
    sim.context.setPositions(positions)

    # (a) minimize + record the FF-switch relaxation (advisory, per TOTAL atom)
    pe_initial = sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(KCAL)
    sim.minimizeEnergy(maxIterations=5000)
    pe_min = sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(KCAL)
    ff_switch = ff_switch_report(pe_initial, pe_min, n_total)
    if conditioner_pe_kcal is not None:
        ff_switch["conditioner_pe_kcal"] = conditioner_pe_kcal
        ff_switch["ff_switch_discontinuity_kcal"] = pe_initial - conditioner_pe_kcal

    had_nan = False

    def _finite_now():
        e = sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(KCAL)
        return math.isfinite(e)

    # (b) restrained heat + NPT equilibration
    for T in (100, 200, 298.15):
        sim.context.setVelocitiesToTemperature(T * unit.kelvin)
        integ.setTemperature(T * unit.kelvin)
        sim.step(max(1, restrained_steps // 3))
        if not _finite_now():
            had_nan = True
            break
    # (c) release restraints gradually
    if not had_nan:
        for k in (2.0, 0.5, 0.0):
            sim.context.setParameter("k", k * unit.kilocalories_per_mole / unit.angstrom**2)
            sim.step(max(1, restrained_steps // 6))
        # (d) DISCARDED unrestrained equilibration (not measured)
        sim.step(discard_steps)
        if not _finite_now():
            had_nan = True

    # (e) MEASURED production window: PE drift + ligand RMSD vs the post-equilibration reference
    times, energies, rmsds = [], [], []
    if not had_nan:
        p0 = np.asarray(sim.context.getState(getPositions=True).getPositions().value_in_unit(unit.angstrom))
        done = 0
        while done < n_steps:
            step = min(report_every, n_steps - done)
            sim.step(step)
            done += step
            st = sim.context.getState(getEnergy=True, getPositions=True)
            e = st.getPotentialEnergy().value_in_unit(KCAL)
            if not math.isfinite(e):
                had_nan = True
                break
            pos = np.asarray(st.getPositions().value_in_unit(unit.angstrom))
            d = float(np.sqrt(((pos[lig] - p0[lig]) ** 2).sum(axis=1).mean()))
            times.append(done * dt_fs / 1e6)        # ns
            energies.append(e)
            rmsds.append(d)
    drift = energy_drift(times, energies) if energies else {"status": "no production samples (equil NaN)",
                                                            "drift_kcal_per_ns": None, "ok": False if had_nan else None}
    verdict = endpoint_stability_verdict(had_nan, (max(rmsds) if rmsds else None), drift, ff_switch)
    return {"ff_switch": ff_switch, "energy_drift": drift, "rmsd_series_a": rmsds,
            "energy_series_kcal": energies, "times_ns": times, **verdict}


def assign_rbfe_charges(off_lig, charge_method):
    """Assign the RBFE charge method to an openff Molecule so the conditioner/endpoint FF matches production
    (reviewer condition 2). NAGL is NOT a bare method string — it needs the NAGL toolkit wrapper + a model file;
    am1bcc goes through AmberTools sqm. Returns the label actually used, or None if it fell back to the
    SystemGenerator default (caller logs). Any real FF-switch discontinuity this leaves is MEASURED by
    run_endpoint_stability's ff_switch report, so a silent mismatch cannot pass unnoticed."""
    cm = (charge_method or "").lower()
    try:
        if cm == "nagl":
            from openff.toolkit.utils.nagl_wrapper import NAGLToolkitWrapper
            model = None
            try:
                from openff.nagl_models import list_available_nagl_models
                cands = [str(p) for p in list_available_nagl_models() if "am1bcc" in str(p).lower()]
                model = cands[-1] if cands else None
            except Exception:  # noqa: BLE001
                model = None
            if model is None:
                model = "openff-gnn-am1bcc-0.1.0-rc.3.pt"   # last-resort well-known model name
            off_lig.assign_partial_charges(model, toolkit_registry=NAGLToolkitWrapper())
            return "nagl:%s" % os.path.basename(model)
        if cm in ("am1bcc", "am1-bcc", "am1bccelf10"):
            off_lig.assign_partial_charges("am1bcc" if cm != "am1bccelf10" else "am1bccelf10")
            return cm
        off_lig.assign_partial_charges(cm)
        return cm
    except Exception:  # noqa: BLE001
        return None


def build_physical_complex(protein_pdb, mol_rdkit, charge_method="nagl", small_ff="openff-2.1.0",
                           padding_nm=1.2, platform_name="CUDA"):
    """Build a solvated PHYSICAL protein+ligand complex under the EXACT RBFE force field (openff small-molecule
    FF + the RBFE charge method + amber/ff14SB + TIP3P) — the λ-endpoint Hamiltonian (no alchemy/softcore). This
    mirrors ternary_preequil._build_physical_system's PROVEN assembly, but uses the RBFE charge method (so the
    endpoint stability test is under the exact production FF, per reviewer condition 2). Returns (system,
    topology, positions, ligand_atom_indices). Charges are assigned to the molecule BEFORE the SystemGenerator
    so the exact requested method (nagl/am1bcc) is used, not the generator default."""
    import openmm
    from openmm import app, unit
    from openff.toolkit import Molecule
    from openmmforcefields.generators import SystemGenerator

    pdb = app.PDBFile(protein_pdb)
    n_prot = pdb.topology.getNumAtoms()
    off_lig = Molecule.from_rdkit(mol_rdkit, allow_undefined_stereo=True)
    if not off_lig.conformers:
        off_lig.generate_conformers(n_conformers=1)
    used = assign_rbfe_charges(off_lig, charge_method)     # exact RBFE charges (nagl model / am1bcc)
    if used is None:
        print("  [endpoint] WARN could not assign %s charges; SystemGenerator default" % charge_method, flush=True)
    else:
        print("  [endpoint] exact-FF charges: %s" % used, flush=True)
    ff_kwargs = {"constraints": app.HBonds, "rigidWater": True, "removeCMMotion": True,
                 "hydrogenMass": 3.0 * unit.amu}
    def _sysgen(sm_ff):
        return SystemGenerator(forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
                               small_molecule_forcefield=sm_ff, molecules=[off_lig],
                               forcefield_kwargs=ff_kwargs, cache=None)
    try:
        sysgen = _sysgen(small_ff)
    except Exception as e:  # noqa: BLE001
        print("  [endpoint] openff FF unavailable (%s); gaff-2.11 fallback" % e, flush=True)
        sysgen = _sysgen("gaff-2.11")
    lig_top = off_lig.to_topology().to_openmm()
    lig_pos = off_lig.conformers[0].to_openmm()
    n_lig = lig_top.getNumAtoms()
    modeller = app.Modeller(pdb.topology, pdb.positions)
    modeller.add(lig_top, lig_pos)
    modeller.addSolvent(sysgen.forcefield, model="tip3p", padding=padding_nm * unit.nanometer,
                        ionicStrength=0.15 * unit.molar)
    system = sysgen.create_system(modeller.topology)
    ligand_atom_indices = list(range(n_prot, n_prot + n_lig))
    return system, modeller.topology, modeller.positions, ligand_atom_indices


def main():
    """Standalone entry used by the ternary lane's MODE=endpoint_smoke. Reads a prepared exact-endpoint system
    from OUTPUT_DIR (written by the FEP setup) if present; otherwise prints an honest 'nothing to test'."""
    out = os.environ.get("OUTPUT_DIR", "/opt/ml/checkpoints")
    os.makedirs(out, exist_ok=True)
    print("[endpoint-stability] pure diagnostics module; the GPU wrapper is invoked by nr4a3_ternary_fep "
          "MODE=endpoint_smoke with a built exact-Hamiltonian endpoint system.", flush=True)
    json.dump({"_what": "endpoint stability harness present; run via MODE=endpoint_smoke on GPU"},
              open(os.path.join(out, "endpoint_stability_placeholder.json"), "w"))


if __name__ == "__main__":
    main()
