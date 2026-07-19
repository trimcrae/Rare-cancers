#!/usr/bin/env python3
"""
Plain-MD PRE-EQUILIBRATION for the ternary RBFE (2026-07-19).

WHY: the ternary alchemical FEP NaNs on the FIRST warmup iteration (v3nagl -> state 4, v3fast -> state 0; both with
the 1 fs reduced-dt warmup override firing, both with 0 real clashes — the close contacts are hybrid/alchemical
dummy pairs). That is the documented OpenFE failure mode: a rough (SMARCA4->SMARCA2 homology) assembled complex fed
STRAIGHT into softcore lambda-states, with no restrained/annealed equilibration. The RelativeHybridTopologyProtocol
does NOT pre-equilibrate; it assumes a stable input. Reduced-dt warmup is insufficient because the instability is in
the alchemical/softcore forces, not the timestep.

FIX (OpenFE's explicit recommendation): relax the assembled, fully-interacting PHYSICAL complex (protein + ligand A +
solvent, NO alchemy) with plain MD FIRST, then build the hybrid from the relaxed structure. This module does that and
writes a relaxed complex.pdb + ligands.sdf that the setup then consumes (cached to GCS like the stage/setup caches, so
it is a one-time cost per leg).

Reads : <INPUT_DIR>/<LEG_ID>/complex.pdb (assembled protein[+E3+target]) and .../ligands.sdf (endpoints; A = mol 0).
Writes: <OUTPUT_DIR>/<LEG_ID>/complex.pdb (relaxed protein) and .../ligands.sdf (ligA relaxed; ligB rigid-aligned to
        the relaxed ligA core so the hybrid map stays consistent). Solvent is DROPPED (the RBFE re-solvates); the
        point is a relaxed protein+ligand scaffold, which is what removes the softcore start instability.

Atom order is under our control (openmmforcefields SystemGenerator builds protein, then ligand, then solvent), so the
relaxed coordinates map back cleanly: protein = first n_prot atoms, ligand = next n_lig atoms.

Env: INPUT_DIR, OUTPUT_DIR, LEG_ID, CHARGE_METHOD (nagl|am1bcc, default nagl), PREEQUIL_NS (production ns after
     restrained relaxation, default 0.5), PREEQUIL_SMOKE=1 (tiny system-build + 200-step check, no full relax),
     PREEQUIL_PADDING_NM (solvent padding, default 1.2), OPENMM_PLATFORM (CUDA|CPU, default CUDA).

Pure OpenMM + openmmforcefields + openff-toolkit + RDKit — the same stack the RBFE env already has.
"""
from __future__ import annotations

import glob
import os
import sys
import time

IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")
LEG_ID = os.environ.get("LEG_ID", "calib_hi_to_lo__ternary_vhl")
CHARGE_METHOD = os.environ.get("CHARGE_METHOD", "nagl")
PREEQUIL_NS = float(os.environ.get("PREEQUIL_NS", "0.5"))
PADDING_NM = float(os.environ.get("PREEQUIL_PADDING_NM", "1.2"))
SMOKE = os.environ.get("PREEQUIL_SMOKE") == "1"
PLATFORM = os.environ.get("OPENMM_PLATFORM", "CUDA")
# SEED (reviewer condition 3, 2026-07-19): each replicate must start from an INDEPENDENT decorrelated
# pre-equilibration snapshot, not one shared cached snapshot. SEED deterministically seeds the conditioner's
# velocities + integrator so mode=preequil run per seed (0/1/2) yields three genuinely independent relaxed
# conformers (the preequilcache key is already seed-scoped). Combined with the stager's per-seed SMARCA2 model
# (model_idx = seed % n_models), the replicates differ in both starting structure and stochastic history.
SEED = int(os.environ.get("SEED", "0"))
# EXACT-FF conditioning (reviewer condition 2 PREFERENCE, 2026-07-19): condition under the SAME force field the
# RBFE uses at its physical endpoints (openff small-molecule FF + the RBFE charge method), so there is NO
# force-field switch between the conditioner and the production Hamiltonian — removing the avoidable
# methodological ambiguity the reviewer named. USE_EXACT_FF=0 falls back to the generator-default charges.
USE_EXACT_FF = os.environ.get("PREEQUIL_EXACT_FF", "1") == "1"


def log(m):
    print(m, flush=True)


def _find_input(name):
    """Locate a staged input file for this leg (mirrors nr4a3_ternary_fep._build_components' lookup)."""
    p = os.path.join(IN, LEG_ID, name)
    if os.path.isfile(p):
        return p
    hits = glob.glob(os.path.join(IN, "**", name), recursive=True)
    if not hits:
        raise SystemExit(f"  [preequil] ABORT: missing staged input {name} under {IN}")
    return hits[0]


def _load_ligands():
    """Return (molA, molB) RDKit mols from ligands.sdf (endpoint A = first record)."""
    from rdkit import Chem
    sdf = _find_input("ligands.sdf")
    mols = [m for m in Chem.SDMolSupplier(sdf, removeHs=False) if m is not None]
    if not mols:
        raise SystemExit(f"  [preequil] ABORT: no valid molecules in {sdf}")
    molA = mols[0]
    molB = mols[1] if len(mols) > 1 else Chem.Mol(mols[0])
    log(f"  [preequil] ligands.sdf: {len(mols)} record(s); ligA={molA.GetNumAtoms()} atoms, "
        f"ligB={molB.GetNumAtoms()} atoms")
    return molA, molB


def _build_physical_system(protein_pdb, molA):
    """Build a solvated protein+ligA OpenMM system with a controlled atom order (protein, ligand, solvent).

    amber14 protein + TIP3P water + a small-molecule template (openff if available, else GAFF via
    openmmforcefields) for ligA. This is a RELAXATION force field: it need only be a reasonable geometry model,
    the RBFE re-parameterizes from scratch. Returns (system, modeller_topology, positions[nm], n_prot, n_lig).
    """
    import openmm
    from openmm import app, unit
    from openff.toolkit import Molecule
    from openmmforcefields.generators import SystemGenerator

    pdb = app.PDBFile(protein_pdb)
    n_prot = pdb.topology.getNumAtoms()

    off_lig = Molecule.from_rdkit(molA, allow_undefined_stereo=True)
    if not off_lig.conformers:
        off_lig.generate_conformers(n_conformers=1)
    # EXACT-FF conditioning (reviewer condition 2 preference): assign the SAME charge method the RBFE uses, so the
    # conditioner Hamiltonian matches the production physical-endpoint Hamiltonian and there is no FF switch.
    if USE_EXACT_FF:
        try:
            off_lig.assign_partial_charges(CHARGE_METHOD)
            log(f"  [preequil] exact-FF conditioning: assigned {CHARGE_METHOD} charges (matches RBFE endpoint FF)")
        except Exception as e:  # noqa: BLE001
            log(f"  [preequil] WARN assign_partial_charges({CHARGE_METHOD}) failed ({e}); generator default charges")
    small_ff = "openff-2.1.0"
    forcefield_kwargs = {"constraints": app.HBonds, "rigidWater": True,
                         "removeCMMotion": True, "hydrogenMass": 3.0 * unit.amu}
    try:
        sysgen = SystemGenerator(
            forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
            small_molecule_forcefield=small_ff, molecules=[off_lig],
            forcefield_kwargs=forcefield_kwargs, cache=None)
    except Exception as e:  # noqa: BLE001 — fall back to GAFF if the openff template is unavailable
        log(f"  [preequil] openff template unavailable ({e}); falling back to gaff-2.11")
        sysgen = SystemGenerator(
            forcefields=["amber/ff14SB.xml", "amber/tip3p_standard.xml"],
            small_molecule_forcefield="gaff-2.11", molecules=[off_lig],
            forcefield_kwargs=forcefield_kwargs, cache=None)

    # ligand OpenMM topology + positions from the off molecule (single conformer already on molA)
    lig_top = off_lig.to_topology().to_openmm()
    lig_pos = off_lig.conformers[0].to_openmm()
    n_lig = lig_top.getNumAtoms()

    modeller = app.Modeller(pdb.topology, pdb.positions)
    modeller.add(lig_top, lig_pos)                      # protein first, ligand appended -> known order
    log(f"  [preequil] protein={n_prot} atoms + ligand={n_lig} atoms; solvating (padding={PADDING_NM} nm, TIP3P)…")
    modeller.addSolvent(sysgen.forcefield, model="tip3p",
                        padding=PADDING_NM * unit.nanometer, ionicStrength=0.15 * unit.molar)

    system = sysgen.create_system(modeller.topology)
    n_total = modeller.topology.getNumAtoms()
    log(f"  [preequil] solvated system: {n_total} atoms (protein {n_prot} + ligand {n_lig} + "
        f"solvent {n_total - n_prot - n_lig})")
    # Return the openff molecule too: its .to_rdkit() has EXACTLY the system ligand's atoms + order (from_rdkit may
    # add explicit Hs, e.g. 59 heavy -> 109 all-atom), so write-back maps cleanly. The raw SDF mol does NOT.
    return system, modeller.topology, modeller.positions, n_prot, n_lig, off_lig


def _relax(system, topology, positions, n_prot, n_lig):
    """Minimize -> NVT heat (heavy-atom restrained, 1 fs) -> NPT equilibrate (restrained) -> release -> short
    unrestrained NPT (production). Restraints on protein+ligand heavy atoms hold the fold while water/H relax; the
    ramp to the production timestep + release avoids the very instability that kills the alchemical warmup.
    Returns final positions (openmm Quantity)."""
    import openmm
    from openmm import app, unit

    # positional restraint (released later by setting k=0) on protein+ligand heavy atoms
    restraint = openmm.CustomExternalForce("0.5*k*periodicdistance(x,y,z,x0,y0,z0)^2")
    restraint.addGlobalParameter("k", 5.0 * unit.kilocalories_per_mole / unit.angstrom**2)
    for p in ("x0", "y0", "z0"):
        restraint.addPerParticleParameter(p)
    heavy = 0
    for atom in topology.atoms():
        if atom.index < n_prot + n_lig and atom.element is not None and atom.element.symbol != "H":
            x, y, z = positions[atom.index].value_in_unit(unit.nanometer)
            restraint.addParticle(atom.index, [x, y, z])
            heavy += 1
    system.addForce(restraint)
    log(f"  [preequil] restrained {heavy} protein+ligand heavy atoms (k=5 kcal/mol/A^2, released after equilibration)")

    integrator = openmm.LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 1.0 * unit.femtosecond)
    integrator.setRandomNumberSeed(SEED + 1)      # per-replicate independence (reviewer condition 3)
    try:
        platform = openmm.Platform.getPlatformByName(PLATFORM)
    except Exception:  # noqa: BLE001
        platform = openmm.Platform.getPlatformByName("CPU")
        log("  [preequil] WARN requested platform unavailable; using CPU")
    sim = app.Simulation(topology, system, integrator, platform)
    sim.context.setPositions(positions)
    log(f"  [preequil] platform={sim.context.getPlatform().getName()}; minimizing…")
    sim.minimizeEnergy(maxIterations=5000)

    steps_ps = 1000  # at 1 fs
    prod_steps = 500 if SMOKE else int(PREEQUIL_NS * 1_000_000 / 4)  # production runs at 4 fs

    # NVT heat 50->300 K, restrained, 1 fs (short)
    n_heat = 100 if SMOKE else 50 * steps_ps  # 50 ps
    log(f"  [preequil] NVT heat (restrained, 1 fs) {n_heat} steps…")
    for T in (50, 150, 250, 300):
        sim.context.setVelocitiesToTemperature(T * unit.kelvin, SEED + 1)   # seeded per replicate (condition 3)
        integrator.setTemperature(T * unit.kelvin)
        sim.step(max(1, n_heat // 4))

    # add a barostat, NPT restrained (100 ps — enough to settle box+solvent around the restrained solute), then
    # RELEASE restraints while ramping dt to 4 fs
    barostat = openmm.MonteCarloBarostat(1 * unit.bar, 300 * unit.kelvin)
    barostat.setRandomNumberSeed(SEED + 1)
    system.addForce(barostat)
    sim.context.reinitialize(preserveState=True)
    n_npt = 200 if SMOKE else 100 * steps_ps
    log(f"  [preequil] NPT equilibrate (restrained) {n_npt} steps…")
    sim.step(n_npt)

    # release restraints gradually
    for k in (2.0, 0.5, 0.0):
        sim.context.setParameter("k", k * unit.kilocalories_per_mole / unit.angstrom**2)
        sim.step(max(1, (100 if SMOKE else 50 * steps_ps)))
    log("  [preequil] restraints released")

    # production at 4 fs (unrestrained); rebuild integrator for the larger dt
    prod_int = openmm.LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 4.0 * unit.femtosecond)
    state = sim.context.getState(getPositions=True, getVelocities=True)
    sim2 = app.Simulation(topology, system, prod_int, sim.context.getPlatform())
    sim2.context.setState(state)
    log(f"  [preequil] production (unrestrained, 4 fs) {prod_steps} steps (~{PREEQUIL_NS if not SMOKE else 0.002} ns)…")
    sim2.step(prod_steps)

    final = sim2.context.getState(getPositions=True).getPositions()
    return final


def _endpoint_map_a2b(molA_r, molB_r):
    """A->B atom map {iA: iB} for the transplant. Prefer the FEP's own LOMAP element-change map (so the map the
    transplant uses is IDENTICAL to the one the RBFE re-derives from the written SDF); fall back to a pure-RDKit
    MCS map only if OpenFE is unavailable. Returns (a2b, source)."""
    import ternary_endpoint_align as align
    try:
        import openfe  # noqa: F401
        from openfe import SmallMoleculeComponent
        import nr4a3_rbfe as rbfe
        cA = SmallMoleculeComponent.from_rdkit(molA_r, name="ligA")
        cB = SmallMoleculeComponent.from_rdkit(molB_r, name="ligB")
        mapping = rbfe._mapping(openfe, cA, cB, prefer_element_change=True)
        return dict(mapping.componentA_to_componentB), "lomap_element_change"
    except Exception as e:  # noqa: BLE001
        log(f"  [preequil] LOMAP map unavailable ({type(e).__name__}: {e}); using rdFMCS fallback map")
        return align.mcs_mapping(molA_r, molB_r), "rdfmcs_fallback"


def _write_relaxed(topology, positions, n_prot, n_lig, off_ligA, molB, protein_out, sdf_out):
    """Write relaxed protein PDB (first n_prot atoms) + relaxed ligands.sdf. BOTH calib endpoints come from the
    SAME relaxed conformer (reviewer condition 1, 2026-07-19): ligA carries the relaxed MD coordinates; ligB's
    MAPPED core atoms are TRANSPLANTED exactly onto ligA's relaxed coords (via the FEP's own atom map) and only
    its dummy atoms are relaxed with the core pinned. verify_endpoints then asserts zero mapped-atom
    displacement + preserved stereo/charge/bonds + sane dummy geometry BEFORE writing — the old whole-molecule
    O3A overlay (which left mapped atoms displaced and produced the FEP's mapped-atom warnings) is removed.
    Solvent dropped (the RBFE re-solvates)."""
    import json as _json
    import numpy as np
    from openff.toolkit import Molecule
    from openmm import app, unit
    from rdkit import Chem
    import ternary_endpoint_align as align

    pos_nm = np.array(positions.value_in_unit(unit.nanometer))

    # ---- relaxed protein PDB: keep only protein atoms (first n_prot) ----
    prot_atoms = [a for a in topology.atoms() if a.index < n_prot]
    modeller = app.Modeller(topology, positions)
    modeller.delete([a for a in topology.atoms() if a.index >= n_prot])
    os.makedirs(os.path.dirname(protein_out), exist_ok=True)
    with open(protein_out, "w") as fh:
        app.PDBFile.writeFile(modeller.topology, modeller.positions, fh, keepIds=True)
    log(f"  [preequil] wrote relaxed protein -> {protein_out} ({len(prot_atoms)} atoms)")

    # ---- relaxed ligA conformer: off_ligA.to_rdkit() has the system ligand's atoms+order (n_lig of them) ----
    molA_r = off_ligA.to_rdkit()
    if molA_r.GetNumAtoms() != n_lig:
        raise SystemExit(f"  [preequil] ABORT: off_ligA rdkit atoms {molA_r.GetNumAtoms()} != system ligand {n_lig}")
    lig_xyz_A = pos_nm[n_prot:n_prot + n_lig] * 10.0                 # nm -> Angstrom
    confA = Chem.Conformer(n_lig)
    for i in range(n_lig):
        confA.SetAtomPosition(i, tuple(float(v) for v in lig_xyz_A[i]))
    molA_r.RemoveAllConformers()
    molA_r.AddConformer(confA, assignId=True)

    # ---- ligB: openff-normalize (all-atom, same toolkit as ligA), seed a conformer, then CORE-TRANSPLANT ----
    try:
        offB = Molecule.from_rdkit(molB, allow_undefined_stereo=True)
        if not offB.conformers:
            offB.generate_conformers(n_conformers=1)
        molB_r = offB.to_rdkit()
    except Exception as e:  # noqa: BLE001
        log(f"  [preequil] WARN could not openff-normalize ligB ({e}); using raw ligB")
        molB_r = Chem.Mol(molB)
    if molB_r.GetNumConformers() == 0:
        from rdkit.Chem import AllChem
        AllChem.EmbedMolecule(Chem.AddHs(molB_r), randomSeed=1)

    a2b, map_src = _endpoint_map_a2b(molA_r, molB_r)
    log(f"  [preequil] endpoint map ({map_src}): {len(a2b)} mapped atoms A->B "
        f"(ligA {molA_r.GetNumAtoms()}, ligB {molB_r.GetNumAtoms()})")
    molB_out, checks = align.transplant_and_verify(molA_r, molB_r, a2b)
    log("  [preequil] endpoint verification: " + _json.dumps(
        {k: checks[k] for k in ("mapped_max_displacement_ang", "graph_identical", "chirality_not_inverted",
                                "net_charge_conserved", "n_mapped", "n_dummy_B", "dummy_bond_lengths_ok",
                                "min_pair_distance_ang", "no_clash", "ok")}))
    if not checks["ok"]:
        raise SystemExit("  [preequil] ABORT: endpoint verification FAILED (reviewer condition 1) — %s" % _json.dumps(checks))

    w = Chem.SDWriter(sdf_out)
    for m in (molA_r, molB_out):
        w.write(m)
    w.close()
    log(f"  [preequil] wrote relaxed ligands.sdf -> {sdf_out} (ligA {molA_r.GetNumAtoms()} relaxed, "
        f"ligB {molB_out.GetNumAtoms()} core-transplanted; max mapped disp {checks['mapped_max_displacement_ang']:.2e} Å)")
    # persist the verification alongside the marker so the reducer/audit can confirm the endpoint conditioning
    with open(os.path.join(os.path.dirname(sdf_out), "endpoint_align_check.json"), "w") as fh:
        _json.dump({"map_source": map_src, **checks}, fh, indent=2)


def main():
    t0 = time.time()
    log(f"=== ternary_preequil leg={LEG_ID} charge={CHARGE_METHOD} ns={PREEQUIL_NS} smoke={SMOKE} ===")
    protein_pdb = _find_input("complex.pdb")
    molA, molB = _load_ligands()
    system, topology, positions, n_prot, n_lig, off_ligA = _build_physical_system(protein_pdb, molA)
    if SMOKE:
        log("  [preequil] SMOKE: system built + parameterized OK; running a short relax sanity then write-back")
    final = _relax(system, topology, positions, n_prot, n_lig)
    out_dir = os.path.join(OUT, LEG_ID)
    _write_relaxed(topology, final, n_prot, n_lig, off_ligA, molB,
                   os.path.join(out_dir, "complex.pdb"), os.path.join(out_dir, "ligands.sdf"))
    # marker so the caller/cache knows the pre-equil completed
    import json
    with open(os.path.join(out_dir, "preequil_marker.json"), "w") as fh:
        json.dump({"leg": LEG_ID, "charge": CHARGE_METHOD, "ns": PREEQUIL_NS, "smoke": SMOKE,
                   "n_protein": n_prot, "n_ligand": n_lig, "seconds": round(time.time() - t0, 1)}, fh)
    log(f"=== PREEQUIL DONE leg={LEG_ID} in {time.time() - t0:.0f}s -> {out_dir}/complex.pdb + ligands.sdf ===")


if __name__ == "__main__":
    main()
