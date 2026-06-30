#!/usr/bin/env python3
"""
Single-snapshot, 1-trajectory MM-GBSA endpoint energy of a docked pose (OpenMM + OpenFF/GAFF + GB).

HONEST SCOPE (read before trusting a number): this is **enthalpy + implicit-solvent only** — NO
configurational entropy (no normal-mode / QH term) and NO ensemble average (one minimized snapshot per
pose). It is a *better-than-docking energy model for triage*, not a binding affinity. Its job is exactly
one thing: test whether the docking-level NR4A3-selectivity margins survive a physics-based rescoring
(`mmgbsa_select.verdict`). For defensible ΔΔG you still need the selectivity FEP tier.

Method (1-trajectory MM-GBSA):
  ΔG_bind ≈ E(complex) − E(receptor) − E(ligand), every term evaluated under the SAME amber14/GBn2 model
  at the SAME minimized complex geometry (receptor and ligand coordinates sliced from the minimized
  complex — the standard single-trajectory approximation, which cancels intramolecular strain).

Inputs are the matrix job's own outputs (no re-docking, no MD): a protein-only opened-conformer PDB
(`<tag>-opened.pdb`) and a one-molecule pose SDF (extracted from `docked_<tag>.sdf`, which carries explicit
Hs + bond orders + the in-pocket coordinates).

Heavy deps (openmm, openmmforcefields, openff-toolkit, pdbfixer) are imported lazily and guarded so the
pure logic (`mmgbsa_select`) and the rest of the repo import without them. NOTE: the numerics are validated
on the first cloud run (the `mx`+MM env is built there), mirroring the repo's "launch-ready, GPU-unvalidated"
convention for new pipelines.
"""
import os
import sys

# kcal/mol per kJ/mol
KJ_PER_KCAL = 4.184


def _mm():
    """Lazy import of the MM stack; raises a clear message if the env lacks it."""
    try:
        import openmm
        from openmm import app, unit
        from openmmforcefields.generators import SystemGenerator
        from openff.toolkit import Molecule
        from pdbfixer import PDBFixer
        return openmm, app, unit, SystemGenerator, Molecule, PDBFixer
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "MM-GBSA needs openmm + openmmforcefields + openff-toolkit + pdbfixer "
            f"(conda-forge). Import failed: {e}") from e


def prepare_receptor(receptor_pdb):
    """PDBFixer the opened-conformer PDB: add missing heavy atoms + hydrogens at pH 7. Returns an OpenMM
    (topology, positions). The metad conformers are protein-only with non-standard protonation, so this
    normalises them before parametrisation."""
    openmm, app, unit, _SG, _Mol, PDBFixer = _mm()
    fixer = PDBFixer(filename=receptor_pdb)
    fixer.findMissingResidues()
    fixer.missingResidues = {}                 # don't model long missing loops — keep the resolved pocket
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    # The opened-conformer PDBs carry a periodic box (CRYST1 from the solvated metad). With a box,
    # SystemGenerator treats the system as PERIODIC and applies a periodic nonbonded method, which is
    # illegal with GB implicit solvent ("Illegal nonbonded method for use with implicit solvent"). Strip
    # the box so the implicit-solvent system is unambiguously non-periodic (NoCutoff).
    fixer.topology.setPeriodicBoxVectors(None)
    return fixer.topology, fixer.positions


def load_poses(pose_sdf):
    """Load every pose in a (possibly multi-molecule) docked SDF as OpenFF Molecules, keyed by their _Name
    (the candidate label set by make_sdf). Explicit Hs + bond orders + in-pocket coords come from the SDF.
    `allow_undefined_stereo` because docked ChEMBL matter may carry unspecified centres."""
    _omm, _app, _unit, _SG, Molecule, _PF = _mm()
    mols = Molecule.from_file(pose_sdf, file_format="sdf", allow_undefined_stereo=True)
    if not isinstance(mols, list):
        mols = [mols]
    out = {}
    for m in mols:
        name = (m.name or "").strip()
        if name and name not in out:           # first pose per label (num_modes=1 anyway)
            out[name] = m
    return out


def _generator(offmol, cache=None):
    openmm, app, unit, SystemGenerator, _Mol, _PF = _mm()
    # openmmforcefields requires nonbondedMethod in (non)periodic_forcefield_kwargs, NOT forcefield_kwargs.
    # GBn2 implicit solvent is non-periodic, so NoCutoff goes in nonperiodic_forcefield_kwargs.
    ff_kwargs = {"constraints": app.HBonds, "removeCMMotion": False}
    return SystemGenerator(
        forcefields=["amber14/protein.ff14SB.xml", "implicit/gbn2.xml"],
        small_molecule_forcefield="gaff-2.11",
        molecules=[offmol],
        forcefield_kwargs=ff_kwargs,
        nonperiodic_forcefield_kwargs={"nonbondedMethod": app.NoCutoff},
        cache=cache,
    )


_PLATFORM = None


def _platform(openmm, unit):
    """Best WORKING **GPU** OpenMM platform, cached. **There is deliberately NO CPU fallback** (trimcrae,
    2026-06-28): run 8 proved a ~4000-atom GB minimisation on CPU takes ~48 min/ligand, so a silent CPU
    fallback just burns the whole timeout. If no GPU platform loads we RAISE immediately, so the job fails
    fast (seconds) with a clear message instead of grinding for an hour — then we go fix the GPU/ICD.

    `getPlatformByName` only checks the platform is REGISTERED, not that its kernels load: the conda OpenMM
    is built against a newer CUDA than the g5 driver supports, so CUDA registers yet fails at kernel load
    (`CUDA_ERROR_UNSUPPORTED_PTX_VERSION`). So actually VALIDATE each candidate with a tiny single-particle
    energy eval and pick the first that runs: CUDA -> OpenCL (GPU, no PTX issue). Set MMGBSA_ALLOW_CPU=1 to
    append CPU as an explicit, opt-in last resort (NOT on by default — there is no automatic CPU fallback)."""
    global _PLATFORM
    if _PLATFORM is None:
        candidates = ["CUDA", "OpenCL"]
        if os.environ.get("MMGBSA_ALLOW_CPU") == "1":
            candidates.append("CPU")          # explicit opt-in only; never an automatic fallback
        for name in candidates:
            try:
                plat = openmm.Platform.getPlatformByName(name)
                sys = openmm.System(); sys.addParticle(1.0)
                integ = openmm.VerletIntegrator(1.0 * unit.femtoseconds)
                ctx = openmm.Context(sys, integ, plat)
                ctx.setPositions([openmm.Vec3(0, 0, 0)] * unit.nanometer)
                ctx.getState(getEnergy=True).getPotentialEnergy()   # forces kernel load -> catches bad CUDA
                del ctx, integ
                _PLATFORM = plat
                print(f"[mmgbsa] OpenMM platform: {name}", flush=True)
                break
            except Exception as e:  # noqa: BLE001 — platform registered but unusable; try the next
                print(f"[mmgbsa] platform {name} unavailable: {str(e)[:90]}", flush=True)
                continue
        if _PLATFORM is None:
            raise RuntimeError(
                f"no working GPU OpenMM platform (tried {candidates}); refusing to run on CPU "
                "(run 8: ~48 min/ligand). Fix CUDA/OpenCL on the instance, or set MMGBSA_ALLOW_CPU=1 "
                "to force a (slow) CPU run.")
    return _PLATFORM


def _energy(openmm, unit, system, topology, positions):
    """Single-point potential energy (kcal/mol) of `system` at `positions` on the best platform."""
    integrator = openmm.VerletIntegrator(1.0 * unit.femtoseconds)
    platform = _platform(openmm, unit)
    context = openmm.Context(system, integrator, platform)
    context.setPositions(positions)
    e = context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    del context, integrator
    return e / KJ_PER_KCAL


def endpoint_dG(rec_top, rec_pos, offmol, minimize_iters=250, cache=None):
    """1-trajectory MM-GBSA ΔG_bind (kcal/mol) for one pose, given a PDBFixer-prepared receptor
    (`prepare_receptor`) and a loaded OpenFF pose molecule (`load_poses`). Returns a dict:
        {dG, E_complex, E_receptor, E_ligand, n_receptor_atoms, n_ligand_atoms}  (energies kcal/mol)
    Raises on any hard failure (missing dep, parametrisation/minimisation error) — the driver catches it
    per ligand so one bad candidate never voids the run."""
    openmm, app, unit, _SG, _Mol, _PF = _mm()

    lig_top = offmol.to_topology().to_openmm()
    lig_top.setPeriodicBoxVectors(None)        # implicit solvent must be non-periodic (see prepare_receptor)
    lig_pos = offmol.conformers[0].to_openmm()

    sysgen = _generator(offmol, cache=cache)

    # complex = receptor then ligand (so the first n_rec atoms are receptor, the rest ligand).
    modeller = app.Modeller(rec_top, rec_pos)
    n_rec = modeller.topology.getNumAtoms()
    modeller.add(lig_top, lig_pos)
    cpx_top, cpx_pos = modeller.topology, modeller.positions
    cpx_top.setPeriodicBoxVectors(None)        # belt-and-suspenders: keep the complex non-periodic too
    n_lig = cpx_top.getNumAtoms() - n_rec

    cpx_sys = sysgen.create_system(cpx_top)

    # minimise the complex (relieve docking clashes), then read back the minimised geometry.
    integrator = openmm.VerletIntegrator(1.0 * unit.femtoseconds)
    sim = app.Simulation(cpx_top, cpx_sys, integrator, _platform(openmm, unit))
    sim.context.setPositions(cpx_pos)
    sim.minimizeEnergy(maxIterations=int(minimize_iters))
    state = sim.context.getState(getEnergy=True, getPositions=True)
    e_complex = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole) / KJ_PER_KCAL
    min_pos = state.getPositions(asNumpy=True)
    del sim, integrator

    # component energies at the SAME minimised geometry (single-trajectory: slice, don't re-minimise).
    rec_sys = sysgen.create_system(rec_top)
    lig_sys = sysgen.create_system(lig_top)
    e_receptor = _energy(openmm, unit, rec_sys, rec_top, min_pos[:n_rec])
    e_ligand = _energy(openmm, unit, lig_sys, lig_top, min_pos[n_rec:])

    dG = e_complex - e_receptor - e_ligand
    return {"dG": round(dG, 2), "E_complex": round(e_complex, 2), "E_receptor": round(e_receptor, 2),
            "E_ligand": round(e_ligand, 2), "n_receptor_atoms": n_rec, "n_ligand_atoms": n_lig}


def endpoint_dG_multisnapshot(rec_top, rec_pos, offmol, n_frames=10, frame_interval_ps=10.0,
                              equil_ps=20.0, temperature_K=300.0, timestep_fs=2.0,
                              minimize_iters=250, cache=None):
    """MULTI-snapshot 1-trajectory MM-GBSA: minimise the complex, run short GB-implicit Langevin MD, and
    average ΔG_bind over `n_frames` snapshots — giving a MEAN and a STANDARD DEVIATION instead of one
    noisy number. This is the de-noising tier (red-team 2026-06-30): the single-snapshot margin swung
    several kcal/mol between runs, so a confirmed selectivity claim needs an ensemble average + error bar.
    Still enthalpy + implicit solvent, NO configurational-entropy term — for defensible ΔΔG you still need FEP.

    Returns: {dG (mean), dG_sd, dG_sem, dG_frames:[...], n_frames, n_receptor_atoms, n_ligand_atoms}.
    Single-trajectory: receptor/ligand energies are sliced from each complex frame (cancels intramol strain).
    """
    import statistics
    openmm, app, unit, _SG, _Mol, _PF = _mm()

    lig_top = offmol.to_topology().to_openmm()
    lig_top.setPeriodicBoxVectors(None)
    lig_pos = offmol.conformers[0].to_openmm()
    sysgen = _generator(offmol, cache=cache)

    modeller = app.Modeller(rec_top, rec_pos)
    n_rec = modeller.topology.getNumAtoms()
    modeller.add(lig_top, lig_pos)
    cpx_top, cpx_pos = modeller.topology, modeller.positions
    cpx_top.setPeriodicBoxVectors(None)
    n_lig = cpx_top.getNumAtoms() - n_rec
    cpx_sys = sysgen.create_system(cpx_top)

    # Langevin MD (GB implicit; non-periodic). Minimise to relieve docking clashes, then equilibrate.
    integ = openmm.LangevinMiddleIntegrator(temperature_K * unit.kelvin,
                                            1.0 / unit.picosecond,
                                            timestep_fs * unit.femtoseconds)
    sim = app.Simulation(cpx_top, cpx_sys, integ, _platform(openmm, unit))
    sim.context.setPositions(cpx_pos)
    sim.minimizeEnergy(maxIterations=int(minimize_iters))
    sim.context.setVelocitiesToTemperature(temperature_K * unit.kelvin)
    steps = lambda ps: max(1, int(ps * 1000.0 / timestep_fs))  # noqa: E731
    sim.step(steps(equil_ps))

    rec_sys = sysgen.create_system(rec_top)
    lig_sys = sysgen.create_system(lig_top)

    dgs = []
    for _f in range(int(n_frames)):
        sim.step(steps(frame_interval_ps))
        st = sim.context.getState(getEnergy=True, getPositions=True)
        e_cpx = st.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole) / KJ_PER_KCAL
        pos = st.getPositions(asNumpy=True)
        e_rec = _energy(openmm, unit, rec_sys, rec_top, pos[:n_rec])
        e_lig = _energy(openmm, unit, lig_sys, lig_top, pos[n_rec:])
        dgs.append(e_cpx - e_rec - e_lig)
    del sim, integ

    mean = statistics.fmean(dgs)
    sd = statistics.pstdev(dgs) if len(dgs) > 1 else 0.0
    return {"dG": round(mean, 2), "dG_sd": round(sd, 2),
            "dG_sem": round(sd / (len(dgs) ** 0.5), 2) if dgs else None,
            "dG_frames": [round(x, 2) for x in dgs], "n_frames": len(dgs),
            "n_receptor_atoms": n_rec, "n_ligand_atoms": n_lig}
