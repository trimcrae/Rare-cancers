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

    # Ground-truth residue identities (UniProt numbering) read straight from the AF2 model. Used below
    # to assert the CV CA atoms in the solvated topology really are residues 406...534 — a count match
    # alone wouldn't catch a contiguity shift (ASSUMPTIONS.md #7) selecting the wrong residues.
    cv_identities = _af2_residue_names(AF2_PDB, CV_RESIDUES)
    missing = [r for r in CV_RESIDUES if r not in cv_identities]
    if missing:
        sys.exit(f"  ABORT: CV residues {missing} absent from the AF2 model {AF2_PDB}")
    print(f"  CV residue identities (AF2, UniProt numbering): {cv_identities}", file=sys.stderr)

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
    plumed_atoms = _cv_ca_plumed_indices(modeller.topology, cv_identities)
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
    minpos = sim.context.getState(getPositions=True).getPositions()
    app.PDBFile.writeFile(modeller.topology, minpos,
                          open(os.path.join(HERE, "nr4a3-lbd-solvated.pdb"), "w"))

    # Pre-flight (ASSUMPTIONS.md #5): the CV's starting Rg must sit inside the wall/grid window, else
    # the bias is mis-scaled or the walls clip the basin before we've spent any GPU time on production.
    rg0 = _rg_nm(minpos, plumed_atoms, unit)
    print(f"  INITIAL CV Rg = {rg0:.3f} nm  (walls 0.6-2.2, grid 0.4-3.0, SIGMA 0.03)", file=sys.stderr)
    if not (0.6 < rg0 < 2.2):
        sys.exit(f"  ABORT: initial Rg {rg0:.3f} nm is outside the wall window [0.6, 2.2] — retune "
                 "walls/grid before committing GPU time.")
    if rg0 < 0.6 + 5 * 0.03 or rg0 > 2.2 - 5 * 0.03:
        print(f"  WARNING: initial Rg {rg0:.3f} nm is within 5*SIGMA of a wall; basin may be clipped.",
              file=sys.stderr)

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


def _af2_residue_names(pdb_path, residues):
    """{resSeq: 3-letter resName} for the requested residues, read from a PDB in its own numbering."""
    want, names = set(residues), {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            try:
                rid = int(line[22:26])
            except ValueError:
                continue
            if rid in want:
                names[rid] = line[17:20].strip()
    return names


def _cv_ca_plumed_indices(topology, cv_identities):
    """CA atom indices (PLUMED 1-based) of the CV residues, via the unit-tested residue resolver
    (handles the solvated PDB being renumbered from 1 vs. preserving AF2 numbering). Asserts each
    selected residue's NAME matches the AF2 ground truth (`cv_identities`), so a contiguity shift
    (ASSUMPTIONS.md #7) that picked the wrong residue is caught here, not discovered in the results."""
    import residue_map as rm
    prot_residues = [r for r in topology.residues() if r.name in _AA]
    # OpenMM topology Residue exposes the PDB residue number as `.id` (a string), not `.resSeq`
    # (that is an mdtraj attribute) — cast to int for the resolver.
    resseqs = [int(r.id) for r in prot_residues]
    positions, label = rm.resolve_positions(resseqs, CV_RESIDUES, LBD_FIRST)
    out = []
    for i in positions:
        # which CV residue is this position supposed to be, under the resolver's chosen scheme?
        cv_res = resseqs[i] if label == "resSeq-preserved" else LBD_FIRST + i
        expected = cv_identities.get(cv_res)
        got = prot_residues[i].name
        # normalise protonation/variant names (HID/HIE/HIP->HIS, CYX->CYS) for the identity check
        norm = {"HID": "HIS", "HIE": "HIS", "HIP": "HIS", "HSD": "HIS", "HSE": "HIS", "CYX": "CYS"}
        if expected is not None and norm.get(got, got) != norm.get(expected, expected):
            sys.exit(f"  ABORT: CV residue {cv_res} ({label}) is {got} in the solvated topology but "
                     f"{expected} in the AF2 model — residue mapping is wrong, not selecting 406...534.")
        ca = next((a for a in prot_residues[i].atoms() if a.name == "CA"), None)
        if ca is not None:
            out.append(ca.index + 1)            # PLUMED indices are 1-based
    return out


def _rg_nm(positions, plumed_atoms, unit):
    """Radius of gyration (nm) of the CV CA atoms, from OpenMM positions. `plumed_atoms` are 1-based."""
    idx = [i - 1 for i in plumed_atoms]
    xyz = [positions[i].value_in_unit(unit.nanometer) for i in idx]
    n = len(xyz)
    cx = sum(p[0] for p in xyz) / n
    cy = sum(p[1] for p in xyz) / n
    cz = sum(p[2] for p in xyz) / n
    msd = sum((p[0] - cx) ** 2 + (p[1] - cy) ** 2 + (p[2] - cz) ** 2 for p in xyz) / n
    return msd ** 0.5


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
