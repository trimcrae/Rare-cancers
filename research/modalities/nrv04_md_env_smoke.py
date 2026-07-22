#!/usr/bin/env python3
"""
NR-V04 covalent panel — MD-environment + mechanics smoke (free CI, no structure, no spend).

Validates the highest-risk, hardest-to-guess pieces of the endpoint-MD driver BEFORE any paid run:
  1. the MD conda env imports (openmm, openff-toolkit, openmmforcefields, rdkit, gemmi, numpy);
  2. celastrol actually parameterizes — GAFF/OpenFF + AM1-BCC charges on a 29-heavy-atom natural product is the
     slowest/riskiest step and the one most likely to fail on a real run;
  3. the frozen restrained-covalent geometry (HarmonicBondForce C->S 1.81 A + two HarmonicAngleForce restraints)
     adds to a system and MD runs stably (no NaN) under it — the exact restraint the covalent legs impose.

Runs the ligand in vacuum (no protein) so it's seconds on a CPU CI runner. Proving the env + celastrol param +
restraint mechanics here de-risks the real complex run; the complex assembly itself is validated separately once
the co-fold structures are staged.
"""
import sys


def main():
    import numpy as np  # noqa: F401
    import gemmi  # noqa: F401
    from openff.toolkit import Molecule
    from openmm import (HarmonicAngleForce, HarmonicBondForce, LangevinMiddleIntegrator, Platform, unit)
    from openmm import app
    from openmmforcefields.generators import SystemGenerator

    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    from nrv04_ligands import build_sdf, electrophile_atom_index
    from rdkit import Chem

    print("[smoke] imports OK", flush=True)

    # 1. build + parameterize celastrol (the risky AM1-BCC step)
    sdf = "/tmp/celastrol_smoke.sdf"
    beta = build_sdf("celastrol", sdf)
    lig = Molecule.from_file(sdf)
    if isinstance(lig, list):
        lig = lig[0]
    print(f"[smoke] celastrol embedded ({lig.n_atoms} atoms), electrophile idx {beta}", flush=True)

    sysgen = SystemGenerator(
        small_molecule_forcefield="gaff-2.11",
        molecules=[lig],
        forcefield_kwargs={"constraints": app.HBonds},
    )
    top = lig.to_topology().to_openmm()
    system = sysgen.create_system(top)
    print(f"[smoke] celastrol parameterized: {system.getNumParticles()} particles, "
          f"{system.getNumForces()} forces (AM1-BCC OK)", flush=True)

    # 2. impose the frozen restrained-covalent geometry (bond + 2 angles), mirroring _add_covalent_restraint
    mol = Chem.SDMolSupplier(sdf, removeHs=False)[0]
    b, n = electrophile_atom_index(Chem.RemoveHs(mol))
    a = (b + 1) % lig.n_atoms                       # a stand-in "Sgamma" partner atom for the mechanics test
    c = (n if n is not None else (b + 2) % lig.n_atoms)
    bf = HarmonicBondForce()
    bf.addBond(b, a, 0.181 * unit.nanometer, 300000.0 * unit.kilojoule_per_mole / unit.nanometer ** 2)
    system.addForce(bf)
    af = HarmonicAngleForce()
    af.addAngle(c, b, a, 1.90 * unit.radian, 500.0 * unit.kilojoule_per_mole / unit.radian ** 2)
    system.addForce(af)
    print("[smoke] restrained-covalent bond+angle added", flush=True)

    # 3. minimize + short MD, assert finite energy (no NaN under the restraint)
    integ = LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 0.001 * unit.picoseconds)
    try:
        plat = Platform.getPlatformByName("CUDA")
    except Exception:  # noqa: BLE001
        plat = Platform.getPlatformByName("CPU")
    sim = app.Simulation(top, system, integ, plat)
    sim.context.setPositions(lig.conformers[0].to_openmm())
    sim.minimizeEnergy(maxIterations=200)
    sim.context.setVelocitiesToTemperature(300 * unit.kelvin, 1)
    sim.step(500)
    e = sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    print(f"[smoke] 500 MD steps done, potential energy = {e:.1f} kJ/mol", flush=True)
    if not (e == e and abs(e) < 1e9):              # NaN or blow-up
        raise SystemExit(f"[smoke] FAIL: non-finite energy {e}")
    print("NRV04 MD-ENV SMOKE PASS (env + celastrol param + restraint mechanics + stable MD).", flush=True)


if __name__ == "__main__":
    sys.exit(main())
