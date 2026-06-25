#!/usr/bin/env python3
"""
NR4A3 LBD well-tempered metadynamics — cryptic-pocket opening (GPU experiment #1, enhanced sampling).

Unbiased 10 ns MD showed Pocket-5 only breathing (max +3.3 nm^2 SASA, no clear opening). Metadynamics
actively biases a collective variable that tracks the pocket opening, so a cryptic opening that would
take microseconds of plain MD is reached in tens of ns — and yields a FREE-ENERGY profile (the cost of
opening), a stronger druggability argument than a single spontaneous event.

CV: radius of gyration of the Calpha atoms of the Pocket-5 lining residues enumerated by fpocket on
the AF2 model (nr4a3_fpocket_enumerate.py -> pocket5_lining_residues.json):
    406, 407, 410, 411, 412, 481, 484, 485, 531, 534   (incl. all 7 selectivity handles)
Opening the collapsed pocket spreads these residues apart -> Rg rises. Well-tempered metadynamics fills
the closed basin and drives Rg outward, bounded by walls to prevent unfolding artifacts.

Same validated stack as nr4a3_md.py (conda-forge CUDA OpenMM, forced CUDA platform). Adds openmm-plumed.
Outputs: COLVAR (CV + bias vs time), HILLS (deposited Gaussians), the trajectory, the solvated PDB, and
fes.dat (free energy vs Rg, via plumed sum_hills). Post-process opened-state frames with the existing
fpocket/SASA analysis.
"""
import os
import subprocess
import sys

LBD_FIRST, LBD_LAST = 373, 626
CV_RESIDUES = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]   # from pocket5_lining_residues.json
AF2_PDB = os.path.join(os.path.dirname(__file__), "AF-Q92570.pdb")
NS = float(os.environ.get("NS", "30"))           # production nanoseconds of biased MD
HERE = os.path.dirname(os.path.abspath(__file__))

# Amino-acid residue names (for identifying the protein chain after solvation).
_AA = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
       "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE", "HIP", "CYX", "HSD", "HSE"}


def main():
    try:
        import openmm as mm
        import openmm.app as app
        from openmm import unit
        from pdbfixer import PDBFixer
        from openmmplumed import PlumedForce
    except ImportError as e:  # noqa: BLE001
        print(f"  needs openmm + pdbfixer + openmm-plumed (GPU box): {e}", file=sys.stderr)
        return

    _fetch_af_model()

    lbd_pdb = os.path.join(HERE, "nr4a3-lbd.pdb")
    with open(AF2_PDB) as fh, open(lbd_pdb, "w") as out:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                try:
                    rid = int(line[22:26])
                except ValueError:
                    continue
                if LBD_FIRST <= rid <= LBD_LAST:
                    out.write(line)
        out.write("END\n")

    fixer = PDBFixer(filename=lbd_pdb)
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)

    modeller = app.Modeller(fixer.topology, fixer.positions)
    ff = app.ForceField("amber14-all.xml", "amber14/tip3pfb.xml")
    modeller.addSolvent(ff, model="tip3p", padding=1.0 * unit.nanometer,
                        ionicStrength=0.15 * unit.molar, neutralize=True)

    system = ff.createSystem(modeller.topology, nonbondedMethod=app.PME,
                             nonbondedCutoff=1.0 * unit.nanometer, constraints=app.HBonds)

    # --- PLUMED well-tempered metadynamics on Rg of the CV-residue CA atoms -----------------------
    plumed_atoms = _cv_ca_plumed_indices(modeller.topology)
    if len(plumed_atoms) != len(CV_RESIDUES):
        sys.exit(f"  ABORT: matched {len(plumed_atoms)}/{len(CV_RESIDUES)} CV CA atoms "
                 "(residue numbering mismatch in the solvated topology)")
    print(f"  CV: Rg of {len(plumed_atoms)} CA atoms (PLUMED 1-based idx): {plumed_atoms}",
          file=sys.stderr)
    hills = os.path.join(HERE, "HILLS")
    colvar = os.path.join(HERE, "COLVAR")
    plumed_script = "\n".join([
        "UNITS LENGTH=nm ENERGY=kj/mol TIME=ps",
        f"cv: GROUP ATOMS={','.join(str(i) for i in plumed_atoms)}",
        "rg: GYRATION TYPE=RADIUS ATOMS=cv",
        # well-tempered: small Gaussians every 1 ps, bias factor 10 at 310 K
        f"metad: METAD ARG=rg SIGMA=0.03 HEIGHT=1.0 PACE=500 BIASFACTOR=10 TEMP=310 "
        f"GRID_MIN=0.4 GRID_MAX=3.0 GRID_BIN=260 FILE={hills}",
        # walls keep the CV physical: don't collapse below ~closed, don't unfold beyond ~open
        "lwall: LOWER_WALLS ARG=rg AT=0.6 KAPPA=2000",
        "uwall: UPPER_WALLS ARG=rg AT=2.2 KAPPA=2000",
        f"PRINT ARG=rg,metad.bias STRIDE=500 FILE={colvar}",
    ])
    system.addForce(PlumedForce(plumed_script))

    integrator = mm.LangevinMiddleIntegrator(310 * unit.kelvin, 1.0 / unit.picosecond,
                                             2.0 * unit.femtosecond)
    # Force CUDA (no silent CPU fallback) — same rule as nr4a3_md.py.
    try:
        cuda = mm.Platform.getPlatformByName("CUDA")
        sim = app.Simulation(modeller.topology, system, integrator, cuda, {"Precision": "mixed"})
    except Exception as e:  # noqa: BLE001
        print(f"  ABORT: CUDA platform unavailable/uninitializable: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"  OpenMM platform: {sim.context.getPlatform().getName()}", file=sys.stderr)
    sim.context.setPositions(modeller.positions)

    print("  minimizing...", file=sys.stderr)
    sim.minimizeEnergy()
    app.PDBFile.writeFile(modeller.topology, sim.context.getState(getPositions=True).getPositions(),
                          open(os.path.join(HERE, "nr4a3-lbd-solvated.pdb"), "w"))

    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
    print("  NVT/NPT equilibration (100 ps)...", file=sys.stderr)
    sim.step(50000)
    system.addForce(mm.MonteCarloBarostat(1 * unit.bar, 310 * unit.kelvin))
    sim.context.reinitialize(preserveState=True)
    sim.step(50000)

    steps = int(NS * 1e6 / 2)
    dcd = os.path.join(HERE, "nr4a3-lbd-metad.dcd")
    sim.reporters.append(app.DCDReporter(dcd, 25000))            # every 50 ps
    sim.reporters.append(app.StateDataReporter(sys.stdout, 50000, step=True,
                         temperature=True, potentialEnergy=True, speed=True))
    print(f"  metadynamics production {NS} ns ({steps} steps) -> {dcd}", file=sys.stderr)
    sim.step(steps)

    _sum_hills(hills)
    print("  done. next: fpocket/SASA on opened-state frames; inspect fes.dat (free energy vs Rg).",
          file=sys.stderr)


def _cv_ca_plumed_indices(topology):
    """CA atom indices (PLUMED 1-based) of the CV residues, via the unit-tested residue resolver
    (handles the solvated PDB being renumbered from 1 vs. preserving AF2 numbering)."""
    import residue_map as rm
    prot_residues = [r for r in topology.residues() if r.name in _AA]
    resseqs = [r.resSeq for r in prot_residues]
    positions, _ = rm.resolve_positions(resseqs, CV_RESIDUES, LBD_FIRST)
    out = []
    for i in positions:
        ca = next((a for a in prot_residues[i].atoms() if a.name == "CA"), None)
        if ca is not None:
            out.append(ca.index + 1)            # PLUMED indices are 1-based
    return out


def _sum_hills(hills):
    """Reconstruct the free-energy profile F(Rg) with `plumed sum_hills` (best-effort)."""
    import shutil
    if not shutil.which("plumed") or not os.path.exists(hills):
        return
    try:
        subprocess.run(["plumed", "sum_hills", "--hills", hills,
                        "--outfile", os.path.join(HERE, "fes.dat")], cwd=HERE, check=False, timeout=600)
    except Exception as e:  # noqa: BLE001
        print(f"  sum_hills skipped: {e}", file=sys.stderr)


def _fetch_af_model():
    if os.path.exists(AF2_PDB):
        return
    import json
    import urllib.request
    import urllib.error
    acc = "Q92570"
    try:
        with urllib.request.urlopen(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}", timeout=60) as r:
            meta = json.load(r)
        pdb_url = (meta[0] or {}).get("pdbUrl") if meta else None
        if pdb_url:
            urllib.request.urlretrieve(pdb_url, AF2_PDB)
            return
    except Exception as e:  # noqa: BLE001
        print(f"  AFDB API lookup failed ({e}); trying versioned URLs", file=sys.stderr)
    for v in ("v6", "v5", "v4", "v3", "v2", "v1"):
        try:
            urllib.request.urlretrieve(
                f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{v}.pdb", AF2_PDB)
            return
        except urllib.error.HTTPError:
            continue
    sys.exit(f"  ABORT: could not fetch the AlphaFold model for {acc}.")


if __name__ == "__main__":
    main()
