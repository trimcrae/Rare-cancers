#!/usr/bin/env python3
"""
Re-seed unbiased "release-style" MD from a representative EXPERIMENTAL 8XTT conformer, so the dynamics
claim (the orthosteric pocket is a breathing/induced-fit site that is druggable in ~20-24% of frames) can
be anchored on the experimental structure rather than only on the AF2/metadynamics ensemble.

WHY. The persistence + per-frame druggability evidence (nr4a3_md_release.py + nr4a3_mdpocket.py) all seeds
from the METAD-opened AF2 conformer. The 8XTT benchmark showed the AF2 atomic pocket geometry diverges
~3.5 A from experiment, so the reviewer's third ask is to seed the SAME unbiased-MD + per-frame-fpocket
readout from an experimental druggable 8XTT conformer (default model 8; model 2 is the peak-druggability
0.925 conformer) and confirm the breathing/druggability behaviour reproduces.

SCOPE / BUILD-STATUS FLAG (read before dispatching). Unlike nr4a3_md_release.py — which RESUMES an existing
solvated `metad_system.xml` (no system build) — 8XTT is a bare protein-only NMR conformer, so this job must
BUILD a fresh solvated system from it (PDBFixer -> TIP3P + 0.15 M ions -> amber14 -> minimize -> short
equil), exactly the nr4a3_md.py preparation but seeded from the chosen 8XTT conformer instead of AF2. That
system-build is the one genuinely NEW piece of code here; everything downstream (the replica loop with
per-interval checkpoint/resume + live Rg streaming, and the per-frame fpocket druggability readout via
nr4a3_mdpocket on the emitted DCD) REUSES the release machinery unchanged. The pure conformer-selection is
unit-tested; the MD/build glue is validated only on the first cloud run (repo "launch-ready" convention).
Per-frame fpocket is produced by running nr4a3_mdpocket (DCD_NAME=<this run's DCD>) on the output — the
SAME two-step split the release run uses (release MD emits Rg + DCD; mdpocket emits druggability).

Outputs (mirroring the release run): 8xtt_release_summary.json (per-replica seed/end/mean Rg + fraction
near seed) + 8xtt_release_rep*.dcd trajectories + per-block Rg traces. Forced CUDA. Checkpoint + continuous
upload per the standing rule so a spot kill / timeout loses <= one checkpoint interval and re-dispatch
resumes.
"""
import json
import os
import sys
import traceback

import nr4a3_8xtt_benchmark as bm
import nr4a3_8xtt_pocketminer as pm     # reuse select_models

# The representative seed conformer. Default 8 (a >=0.53-druggable experimental conformer per the
# benchmark: model 8 drugg 0.744); model 2 is the peak (0.925). Overridable via SEED_MODEL.
SEED_MODEL = os.environ.get("SEED_MODEL", "8")
NS = float(os.environ.get("NS", "5"))          # ns per replica (cumulative target; a resume extends to this)
N_REP = int(os.environ.get("N_REP", "3"))
RUN_TAG = os.environ.get("RUN_TAG", "8xtt_release")
CHECKPOINT_EVERY = int(os.environ.get("CHECKPOINT_EVERY", "10"))   # blocks (x50 ps) between checkpoints
TEMP_K = float(os.environ.get("TEMP_K", "310"))

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
RESUME_DIR = os.environ.get("RESUME_DIR", OUT)


# ==================================================================================================
# PURE LOGIC — unit-tested in tests/test_8xtt_redock.py (no openmm/mdtraj/network).
# ==================================================================================================

def pick_seed_model(n_models, requested=SEED_MODEL):
    """Resolve the single seed-conformer index against the 8XTT models present. Reuses
    nr4a3_8xtt_pocketminer.select_models and takes the first (a single-model request like '8' -> 8; 'all'
    -> the lowest-index model). Fails loud if none present. Pure."""
    chosen = pm.select_models(range(1, n_models + 1), requested)
    return chosen[0]


# ==================================================================================================
# I/O + orchestration (AWS-side; NOT unit-tested — openmm/mdtraj/fpocket live here).
# ==================================================================================================

def _read(path):
    with open(path) as fh:
        return fh.read()


def _write_protein_pdb(model_text, dest):
    """Protein-only receptor PDB of the chosen 8XTT conformer (reuse the redock text transform)."""
    import nr4a3_8xtt_redock as rd
    with open(dest, "w") as fh:
        fh.write(rd.protein_only_model(model_text))
    return dest


def _build_solvated_system(conformer_pdb, work):
    """Build a solvated OpenMM system from the bare 8XTT conformer — the ONE new piece vs the release run.
    Mirrors nr4a3_md.py preparation (PDBFixer add atoms/H -> TIP3P + 0.15 M ions -> amber14 -> minimize).
    Returns (topology, system, minimized_positions, solvated_pdb_path)."""
    import openmm as mm
    import openmm.app as app
    from openmm import unit
    from pdbfixer import PDBFixer

    fixer = PDBFixer(filename=conformer_pdb)
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
    integ = mm.LangevinMiddleIntegrator(TEMP_K * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtosecond)
    cuda = mm.Platform.getPlatformByName("CUDA")
    sim = app.Simulation(modeller.topology, system, integ, cuda, {"Precision": "mixed"})
    sim.context.setPositions(modeller.positions)
    print("  minimizing solvated 8XTT conformer...", file=sys.stderr, flush=True)
    sim.minimizeEnergy()
    solvated_pdb = os.path.join(OUT, "8xtt-lbd-solvated.pdb")
    app.PDBFile.writeFile(modeller.topology,
                          sim.context.getState(getPositions=True).getPositions(), open(solvated_pdb, "w"))
    minpos = sim.context.getState(getPositions=True).getPositions(asNumpy=True)
    del sim, integ
    return modeller.topology, system, minpos, solvated_pdb


def _cv_ca_indices(topology, mapped_pocket5_auth):
    """0-based atom indices of the Pocket-5 lining CA atoms in the solvated topology, matched by author
    resSeq (the 8XTT numbering the mapped Pocket-5 uses). The CV Rg is computed over these."""
    idx = []
    want = set(mapped_pocket5_auth)
    for atom in topology.atoms():
        if atom.name == "CA" and atom.residue.chain.index == 0:
            try:
                rs = int(atom.residue.id)
            except (TypeError, ValueError):
                continue
            if rs in want:
                idx.append(atom.index)
    return idx


def main():
    import numpy as np
    import mdtraj as md
    import openmm as mm
    import openmm.app as app
    from openmm import unit
    import nr4a3_md_release as R     # reuse _rg_series / _rg_one / _read_rg_values

    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(OUT, "seed_work")
    os.makedirs(work, exist_ok=True)

    # 1) fetch 8XTT, pick + write the seed conformer, build the map (for the CV residues).
    xtt = bm.fetch_rcsb(bm.PDB_ID, os.path.join(work, f"{bm.PDB_ID}.pdb"))
    models = bm.split_models(_read(xtt))
    if not models:
        sys.exit(f"ABORT: no models in {bm.PDB_ID}")
    seed_model = pick_seed_model(len(models), SEED_MODEL)
    conformer_pdb = _write_protein_pdb(models[seed_model - 1], os.path.join(work, f"8xtt_m{seed_model}.pdb"))
    print(f"  seed conformer: 8XTT model {seed_model}", file=sys.stderr, flush=True)

    # map Pocket-5 (UniProt) -> 8XTT author numbering for the CV (fetch AF2 for the reference sequence).
    import nr4a3_8xtt_redock as rd
    af2 = rd._fetch_af2(os.path.join(work, f"AF-{bm.UNIPROT}.pdb"))
    _ca, af2_resnums, af2_seq = bm.af2_lbd_ca(af2)
    _c, xtt_resnums0, xtt_seq0, _ca0 = bm.chain_ca(models[0])
    uni_to_auth, _identity = bm.map_uniprot_to_pdb(af2_seq, af2_resnums, xtt_seq0, xtt_resnums0)
    mapped_pocket5 = sorted({uni_to_auth[u] for u in bm.POCKET5 if u in uni_to_auth})

    # 2) build the solvated system from the experimental conformer (the one new step).
    topology, system, minpos, solvated_pdb = _build_solvated_system(conformer_pdb, work)
    idx0 = _cv_ca_indices(topology, mapped_pocket5)
    if len(idx0) < 3:
        sys.exit(f"ABORT: only {len(idx0)} Pocket-5 CA atoms matched for the CV Rg")
    rg_seed = R._rg_one(minpos.value_in_unit(unit.nanometer), idx0)
    print(f"  CV Pocket-5 CA atoms {len(idx0)}; seed Rg {rg_seed:.3f} nm", file=sys.stderr, flush=True)

    summary = {"_note": "Unbiased release-style MD seeded from an EXPERIMENTAL 8XTT conformer (fresh "
                        "solvated system). Persistence near the seed Rg => the experimental druggable "
                        "conformation is thermally metastable. Confirm DRUGGABILITY per-frame by running "
                        "nr4a3_mdpocket on the emitted DCD (DCD_NAME=8xtt_release_rep0.dcd), as the release "
                        "run does.", "seed_model": seed_model, "seed_Rg_nm": round(rg_seed, 3),
               "ns_per_replica": NS, "n_replicas": N_REP, "cv_pocket5_ca": len(idx0), "replicas": []}

    cuda = mm.Platform.getPlatformByName("CUDA")
    steps = int(NS * 1e6 / 2)
    report = 25000                                  # 50 ps
    nblocks = max(1, steps // report)
    for rep in range(N_REP):
        integ = mm.LangevinMiddleIntegrator(TEMP_K * unit.kelvin, 1.0 / unit.picosecond,
                                            2.0 * unit.femtosecond)
        sim = app.Simulation(topology, system, integ, cuda, {"Precision": "mixed"})
        state_path = os.path.join(OUT, f"{RUN_TAG}_rep{rep}.state.xml")
        prog_path = os.path.join(OUT, f"{RUN_TAG}_rep{rep}.progress.json")
        rg_path = os.path.join(OUT, f"{RUN_TAG}_rg_rep{rep}.dat")
        r_state = os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{rep}.state.xml")
        r_prog = os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{rep}.progress.json")
        if os.path.exists(r_state) and os.path.exists(r_prog):
            sim.loadState(r_state)
            done = int(json.load(open(r_prog)).get("blocks_done", 0))
            rgf = open(rg_path, "a")
            print(f"  [rep{rep}] RESUME from {done} blocks", file=sys.stderr, flush=True)
        else:
            sim.context.setPositions(minpos)
            sim.context.setVelocitiesToTemperature(TEMP_K * unit.kelvin, 1234 + rep)
            done = 0
            rgf = open(rg_path, "w")
            rgf.write("# time_ns  cv_Rg_nm\n")
        if done < nblocks:
            traj_dcd = os.path.join(OUT, f"{RUN_TAG}_rep{rep}_from{done}.dcd")
            sim.reporters.append(app.DCDReporter(traj_dcd, report))
            for b in range(done, nblocks):
                sim.step(report)
                pos = sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(
                    unit.nanometer)
                rg = R._rg_one(pos, idx0)
                t_ns = (b + 1) * report * 2e-6
                rgf.write(f"{t_ns:.3f}  {rg:.4f}\n"); rgf.flush()
                if (b + 1) % CHECKPOINT_EVERY == 0 or b + 1 == nblocks:
                    sim.saveState(state_path + ".tmp"); os.replace(state_path + ".tmp", state_path)
                    json.dump({"blocks_done": b + 1, "ns_done": round((b + 1) * report * 2e-6, 4),
                               "rg": round(rg, 4)}, open(prog_path, "w"))
                print(f"  [rep{rep}] t={t_ns:6.2f} ns  CV Rg {rg:.3f} nm (seed {rg_seed:.3f})",
                      file=sys.stderr, flush=True)
        rgf.close()
        rgs = np.array(R._read_rg_values(rg_path))
        if len(rgs):
            within = float((np.abs(rgs - rg_seed) <= 0.1).mean())
            summary["replicas"].append({"replica": rep, "seed_Rg": round(rg_seed, 3),
                                        "end_Rg": round(float(rgs[-1]), 3),
                                        "mean_Rg": round(float(rgs.mean()), 3),
                                        "frac_time_within_0.1nm_of_seed": round(within, 3)})
        with open(os.path.join(OUT, "8xtt_release_summary.json"), "w") as fh:
            json.dump(summary, fh, indent=2)
    print(json.dumps({"seed_model": seed_model, "seed_Rg_nm": summary["seed_Rg_nm"],
                      "replicas": summary["replicas"]}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        os.makedirs(OUT, exist_ok=True)
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, "8xtt_release_summary.json"), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
