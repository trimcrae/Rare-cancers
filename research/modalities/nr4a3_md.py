#!/usr/bin/env python3
"""
NR4A3 LBD molecular dynamics — cryptic-pocket detection (GPU experiment #1 from the degrader spec).

GOAL. The "NR4A3 is undruggable" verdict rests on the orthosteric pocket being *collapsed* in one
static AlphaFold model. This runs solvated MD of the NR4A3 ligand-binding domain so a downstream
transient-pocket analysis (mdpocket / PocketMiner) can test whether a **cryptic druggable pocket
opens** — the single strongest result for the degrader paper if positive.

This script is PREPARED to run as-is on a GPU box (OpenMM picks CUDA automatically); it is not run
in the standard CI (no GPU). It is intentionally self-contained boilerplate so GPU time only has to
*execute*. Validate the first short run before committing to a long one.

Pipeline: AF2 LBD -> PDBFixer (add missing atoms/H, cap) -> solvate (TIP3P) + ions -> Amber14 ff ->
minimize -> NVT + NPT equilibration -> production (default 200 ns; set NS env to change) -> save
trajectory (DCD) + topology for mdpocket.

Post-processing (separate, also on the GPU/CPU box, not here): run mdpocket on the DCD to map
transient pocket density at the Pocket-5 site (residues 406-534); a pocket that opens/closes during
the run, absent in the static model, is the cryptic-pocket result.
"""

import os
import sys

LBD_FIRST, LBD_LAST = 373, 626          # NR4A3 LBD (retained in the fusion)
AF2_PDB = os.path.join(os.path.dirname(__file__), "AF-Q92570.pdb")  # fetched by nr4a3_dock.py
NS = float(os.environ.get("NS", "200"))  # production nanoseconds


def main():
    try:
        import openmm as mm
        import openmm.app as app
        from openmm import unit
        from pdbfixer import PDBFixer
    except ImportError as e:  # noqa
        print(f"  needs openmm + pdbfixer (GPU box): {e}", file=sys.stderr)
        print("  install: mamba install -c conda-forge openmm pdbfixer mdtraj fpocket", file=sys.stderr)
        return

    if not os.path.exists(AF2_PDB):
        # fetch the AlphaFold model if the docking step didn't leave it here.
        # Resolve the URL from the AFDB API (version-agnostic) so a model_v* bump
        # doesn't 404 us; fall back to enumerating known file-version suffixes.
        import json
        import urllib.request
        import urllib.error
        acc = "Q92570"  # NR4A3 / NOR-1
        fetched = False
        try:
            api = f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"
            with urllib.request.urlopen(api, timeout=60) as r:
                meta = json.load(r)
            pdb_url = (meta[0] or {}).get("pdbUrl") if meta else None
            if pdb_url:
                urllib.request.urlretrieve(pdb_url, AF2_PDB)
                fetched = True
        except Exception as e:  # noqa: BLE001 — API best-effort; fall through to direct URLs
            print(f"  AFDB API lookup failed ({e}); trying versioned file URLs", file=sys.stderr)
        for v in ("v6", "v5", "v4", "v3", "v2", "v1"):
            if fetched:
                break
            try:
                urllib.request.urlretrieve(
                    f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_{v}.pdb", AF2_PDB)
                fetched = True
            except urllib.error.HTTPError:
                continue
        if not fetched:
            sys.exit(f"  ABORT: could not fetch the AlphaFold model for {acc} from AFDB "
                     "(API + all versioned URLs failed).")

    # --- trim to the LBD (pre-filter the PDB to LBD-only atoms), then repair ----------------------
    lbd_pdb = os.path.join(os.path.dirname(__file__), "nr4a3-lbd.pdb")
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
    fixer.missingResidues = {}          # don't model gaps at the trimmed termini
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)

    modeller = app.Modeller(fixer.topology, fixer.positions)
    ff = app.ForceField("amber14-all.xml", "amber14/tip3pfb.xml")
    modeller.addSolvent(ff, model="tip3p", padding=1.0 * unit.nanometer,
                        ionicStrength=0.15 * unit.molar, neutralize=True)

    system = ff.createSystem(modeller.topology, nonbondedMethod=app.PME,
                             nonbondedCutoff=1.0 * unit.nanometer, constraints=app.HBonds)
    integrator = mm.LangevinMiddleIntegrator(310 * unit.kelvin, 1.0 / unit.picosecond,
                                             2.0 * unit.femtosecond)
    sim = app.Simulation(modeller.topology, system, integrator)  # OpenMM auto-selects fastest platform
    used = sim.context.getPlatform().getName()
    print(f"  OpenMM platform: {used}", file=sys.stderr)
    if used in ("CPU", "Reference"):
        print("  ABORT: no GPU platform (CUDA/OpenCL) selected — refusing to run MD on CPU "
              "(too slow/costly). Check the conda openmm CUDA build vs the GPU driver.",
              file=sys.stderr)
        sys.exit(2)
    sim.context.setPositions(modeller.positions)

    print("  minimizing...", file=sys.stderr)
    sim.minimizeEnergy()
    app.PDBFile.writeFile(modeller.topology, sim.context.getState(getPositions=True).getPositions(),
                          open(os.path.join(os.path.dirname(__file__), "nr4a3-lbd-solvated.pdb"), "w"))

    sim.context.setVelocitiesToTemperature(310 * unit.kelvin)
    print("  NVT/NPT equilibration (100 ps)...", file=sys.stderr)
    sim.step(50000)
    system.addForce(mm.MonteCarloBarostat(1 * unit.bar, 310 * unit.kelvin))
    sim.context.reinitialize(preserveState=True)
    sim.step(50000)

    steps = int(NS * 1e6 / 2)  # 2 fs timestep
    dcd = os.path.join(os.path.dirname(__file__), "nr4a3-lbd-md.dcd")
    sim.reporters.append(app.DCDReporter(dcd, 25000))           # every 50 ps (keeps file size sane)
    sim.reporters.append(app.StateDataReporter(sys.stdout, 50000, step=True,
                         temperature=True, potentialEnergy=True, speed=True))
    print(f"  production {NS} ns ({steps} steps) -> {dcd}", file=sys.stderr)
    sim.step(steps)
    print("  done. next: mdpocket -f nr4a3-lbd-md.dcd -s nr4a3-lbd-solvated.pdb "
          "to map transient pockets at residues 406-534.", file=sys.stderr)


if __name__ == "__main__":
    main()
