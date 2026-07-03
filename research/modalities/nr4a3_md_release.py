#!/usr/bin/env python3
"""
Unbiased "release" MD from the metad-OPENED NR4A3 pocket — does the druggable open state persist
(thermally accessible / metastable) or collapse (bias-induced strain)? This is the Gate-3
disambiguation that does NOT depend on metadynamics convergence.

Why: the 30 ns metad F(Rg) gives a ~38 kcal/mol opening cost, but the profile is monotonic and read at
the edge of the sampled CV range — hallmarks of an under-converged run, so the number is an upper bound,
not a converged cost. A direct test: seed UNBIASED dynamics from the most-open (most-druggable) frame
and watch the CV (Rg of the Pocket-5 lining Cα atoms). Persistence near the opened Rg => a real
metastable druggable basin (38 kcal/mol was a convergence artifact); fast collapse toward the closed Rg
=> the opened geometry was bias-induced strain (corroborates costly/inaccessible).

Reuses the checkpoint artifacts from the metad run (mounted at INPUT_DIR): metad_system.xml is the base
System WITHOUT the PLUMED bias, so an unbiased run is just "load it, seed an opened frame, integrate".
We pick the SEED frame from nr4a3-lbd-metad.dcd by TARGET_RG — default the LOW-ENERGY DRUGGABLE state
(CV Rg ~0.717 nm, fpocket 0.80, ~0.76 kcal/mol per the F(Rg)-vs-druggability reconciliation), NOT the
max-Rg frontier. (Seeding the max-Rg frame — the ~38 kcal/mol opening edge — is the worst case; it
collapsed in run 28339743810. TARGET_RG<=0 restores that legacy max-Rg behaviour.) We launch N_REP
replicas (different velocity seeds) of NS ns each, and write per-replica Rg(t) (release_rg_repK.dat) +
trajectories. Confirm DRUGGABILITY persistence separately by running nr4a3_mdpocket on release_rep*.dcd.

Output: release_summary.json (per replica: seed Rg, end Rg, mean/min/max Rg, fraction of time within
0.1 nm of the seed) + the Rg traces. Forced CUDA platform, same as the other GPU runs.
"""
import json
import os
import shutil
import sys

import nr4a3_metad as M     # reuse CV residues / CA-index selection / Rg helper / AF model fetch

IN = os.environ.get("INPUT_DIR", M.HERE)        # mounted metad outputs (system/topology/trajectory)
OUT = os.environ.get("OUTPUT_DIR", M.HERE)
NS = float(os.environ.get("NS", "5"))           # ns per replica (TARGET, cumulative — a resume extends to this)
N_REP = int(os.environ.get("N_REP", "3"))       # independent velocity seeds
# Namespacing + resume/checkpoint (RUN_TAG lets the SAME harness do the persistence-from-open 'release' run AND
# the opening-from-closed run without colliding). RESUME_DIR is a mount of a prior OUTPUT_PREFIX; if it holds a
# per-replica state.xml + progress marker, the replica CONTINUES that trajectory (extend, don't repeat) instead
# of re-seeding. CHECKPOINT_EVERY blocks: save state.xml + progress so a timeout/spot-kill loses ≤ that, and so
# the run can be EXTENDED later (bump NS + re-dispatch). This is the repo's standing checkpoint rule applied.
RUN_TAG = os.environ.get("RUN_TAG", "release")
RESUME_DIR = os.environ.get("RESUME_DIR", OUT)
CHECKPOINT_EVERY = int(os.environ.get("CHECKPOINT_EVERY", "10"))   # blocks (×50 ps) between state checkpoints


def _read_rg_values(path):
    """Prior Rg(t) values (2nd column) from an existing trace, for the summary on resume; [] if absent."""
    vals = []
    if os.path.exists(path):
        for ln in open(path):
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                try:
                    vals.append(float(ln.split()[1]))
                except (IndexError, ValueError):
                    pass
    return vals


def main():
    try:
        import openmm as mm
        import openmm.app as app
        from openmm import unit
        import mdtraj as md
    except ImportError as e:  # noqa: BLE001
        print(f"  needs openmm + mdtraj (GPU box): {e}", file=sys.stderr)
        return

    system_xml = os.path.join(IN, "metad_system.xml")
    solvated = os.path.join(IN, "nr4a3-lbd-solvated.pdb")
    dcd = os.path.join(IN, "nr4a3-lbd-metad.dcd")
    for p in (system_xml, solvated, dcd):
        if not os.path.exists(p):
            sys.exit(f"  ABORT: missing {p} (mount the metad outputs at INPUT_DIR)")
    os.makedirs(OUT, exist_ok=True)

    pdb = app.PDBFile(solvated)
    topology = pdb.topology
    with open(system_xml) as fh:
        system = mm.XmlSerializer.deserialize(fh.read())   # base system, NO PlumedForce = unbiased

    # CV CA atoms (PLUMED 1-based) on the solvated topology, then 0-based for Rg. This release run is
    # NR4A3-specific (it reuses the NR4A3 metad checkpoint), so pin the NR4A3 reference CV/model
    # explicitly — robust to nr4a3_metad's TARGET being env-driven after the multi-paralogue refactor.
    M.CV_RESIDUES = list(M.REF_CV_RESIDUES)
    M.LBD_FIRST = M.REF_LBD_FIRST
    af2_pdb = os.path.join(M.HERE, f"AF-{M.REF_ACC}.pdb")
    M._fetch_af_model(M.REF_ACC, af2_pdb)
    cv_identities = M._af2_residue_names(af2_pdb, M.CV_RESIDUES)
    plumed_atoms = M._cv_ca_plumed_indices(topology, cv_identities)
    if len(plumed_atoms) != len(M.CV_RESIDUES):
        sys.exit(f"  ABORT: matched {len(plumed_atoms)}/{len(M.CV_RESIDUES)} CV CA atoms")

    import numpy as np
    # Seed frame selection. Default = the LOW-ENERGY DRUGGABLE state (TARGET_RG ~0.717 nm), the realistic
    # design target — NOT the max-Rg frontier (the ~38 kcal/mol edge), whose metastability is the worst
    # case and already failed. TARGET_RG<=0 restores the legacy max-Rg (argmax) seed.
    t = md.load(dcd, top=solvated)
    idx0 = [i - 1 for i in plumed_atoms]
    rg_traj = _rg_series(t.xyz, idx0)              # nm (mdtraj xyz already in nm)
    target_rg = float(os.environ.get("TARGET_RG", "0.717"))
    if target_rg <= 0:
        seed_frame = int(rg_traj.argmax())
        seed_mode = "max-Rg frontier (legacy)"
    else:
        seed_frame = int(np.abs(rg_traj - target_rg).argmin())
        seed_mode = f"nearest TARGET_RG={target_rg:.3f}"
    rg_seed = float(rg_traj[seed_frame])
    print(f"  seed frame {seed_frame}/{t.n_frames} [{seed_mode}]: CV Rg {rg_seed:.3f} nm "
          f"(traj Rg range {rg_traj.min():.3f}-{rg_traj.max():.3f})", file=sys.stderr)
    open_positions = t.xyz[seed_frame] * unit.nanometer

    summary = {"_note": "Unbiased release MD seeded from a chosen metad frame (default: the low-energy "
                        "DRUGGABLE state ~0.717 nm, NOT the max-Rg frontier). Persistence near the seed "
                        "Rg => the druggable conformation is thermally metastable; drift away => not "
                        "metastable. Druggability persistence is confirmed separately by running "
                        "nr4a3_mdpocket on release_rep*.dcd (DCD_NAME=release_rep0.dcd).",
               "seed_mode": seed_mode, "seed_frame": seed_frame, "seed_Rg_nm": round(rg_seed, 3),
               "target_rg_nm": target_rg, "closed_Rg_ref_nm": 0.753, "ns_per_replica": NS,
               "n_replicas": N_REP, "replicas": []}

    try:
        cuda = mm.Platform.getPlatformByName("CUDA")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"  ABORT: CUDA platform unavailable: {e}")

    # Skip the (minutes-long) seed minimization entirely when EVERY replica resumes from a checkpoint — the
    # loaded state is already relaxed, so re-minimizing a seed nobody uses is pure waste (don't repeat work).
    need_fresh = any(not (os.path.exists(os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{r}.state.xml"))
                          and os.path.exists(os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{r}.progress.json")))
                     for r in range(N_REP))
    # The opened frame is a STRAINED, biased metad configuration — seeding unbiased dynamics from it
    # directly explodes on step 1 ("Particle coordinate is NaN"). Relax it with an energy minimization
    # first. A minimizer is LOCAL: it removes bad contacts / steep clashes without crossing conformational
    # barriers, so a genuine open basin stays open while an over-strained frame just sheds the strain. We
    # record the post-minimization Rg so a reader can tell "minimization collapsed it" (open_Rg -> min_Rg
    # already near the closed 0.753) from "dynamics collapsed it" (min_Rg open, but replicas drift closed).
    if not need_fresh:
        print("  all replicas resume from checkpoint — skipping seed minimization", file=sys.stderr, flush=True)
        rg_min = rg_seed
    else:
        _mi = mm.LangevinMiddleIntegrator(M.METAD["temp"] * unit.kelvin, 1.0 / unit.picosecond,
                                          2.0 * unit.femtosecond)
        _ms = app.Simulation(topology, system, _mi, cuda, {"Precision": "mixed"})
        _ms.context.setPositions(open_positions)
        _ms.minimizeEnergy(maxIterations=5000)
        open_positions = _ms.context.getState(getPositions=True).getPositions(asNumpy=True)
        rg_min = _rg_one(open_positions.value_in_unit(unit.nanometer), idx0)
        del _ms, _mi
    summary["minimized_Rg_nm"] = round(float(rg_min), 3)
    print(f"  minimized seed frame: CV Rg {rg_seed:.3f} -> {rg_min:.3f} nm "
          f"(closed ref 0.753)", file=sys.stderr, flush=True)

    import numpy as np
    steps = int(NS * 1e6 / 2)                       # 2 fs timestep
    report = 25000                                  # every 50 ps
    nblocks = max(1, steps // report)               # target cumulative blocks (a resume extends TO this)
    for rep in range(N_REP):
        integ = mm.LangevinMiddleIntegrator(M.METAD["temp"] * unit.kelvin, 1.0 / unit.picosecond,
                                            2.0 * unit.femtosecond)
        sim = app.Simulation(topology, system, integ, cuda, {"Precision": "mixed"})
        state_path = os.path.join(OUT, f"{RUN_TAG}_rep{rep}.state.xml")
        prog_path = os.path.join(OUT, f"{RUN_TAG}_rep{rep}.progress.json")
        rg_path = os.path.join(OUT, f"{RUN_TAG}_rg_rep{rep}.dat")
        r_state = os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{rep}.state.xml")
        r_prog = os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{rep}.progress.json")
        r_rg = os.path.join(RESUME_DIR, f"{RUN_TAG}_rg_rep{rep}.dat")
        # RESUME this replica from its last checkpoint (continue the trajectory) or SEED it fresh.
        if os.path.exists(r_state) and os.path.exists(r_prog):
            sim.loadState(r_state)                  # positions + velocities → exact continuation
            done = int(json.load(open(r_prog)).get("blocks_done", 0))
            if RESUME_DIR != OUT:                   # carry prior trace/state into this job's OUT to keep growing
                for src, dst in ((r_rg, rg_path), (r_state, state_path), (r_prog, prog_path)):
                    if os.path.exists(src):
                        shutil.copy(src, dst)
            rgf = open(rg_path, "a")
            print(f"  [rep{rep}] RESUME from {done} blocks ({done * report * 2e-6:.2f} ns); target "
                  f"{nblocks} blocks ({NS:.1f} ns)", file=sys.stderr, flush=True)
        else:
            sim.context.setPositions(open_positions)
            sim.context.setVelocitiesToTemperature(M.METAD["temp"] * unit.kelvin, 1234 + rep)
            done = 0
            rgf = open(rg_path, "w")
            rgf.write("# time_ns  cv_Rg_nm\n")
        if done >= nblocks:
            print(f"  [rep{rep}] already at target ({done} ≥ {nblocks} blocks) — skipping", file=sys.stderr)
            rgf.close()
        else:
            # DCD per resume-segment (append-safe); analysis concatenates segments.
            traj_dcd = os.path.join(OUT, f"{RUN_TAG}_rep{rep}_from{done}.dcd")
            sim.reporters.append(app.DCDReporter(traj_dcd, report))
            for b in range(done, nblocks):
                sim.step(report)
                pos = sim.context.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(
                    unit.nanometer)
                rg = _rg_one(pos, idx0)
                t_ns = (b + 1) * report * 2e-6
                rgf.write(f"{t_ns:.3f}  {rg:.4f}\n")
                rgf.flush()
                # CONTINUOUS CHECKPOINT: atomically save state + progress every CHECKPOINT_EVERY blocks so a
                # timeout/spot-kill loses ≤ that and a re-dispatch resumes/extends. tmp+replace = never a torn file.
                if (b + 1) % CHECKPOINT_EVERY == 0 or b + 1 == nblocks:
                    sim.saveState(state_path + ".tmp")
                    os.replace(state_path + ".tmp", state_path)
                    json.dump({"blocks_done": b + 1, "ns_done": round((b + 1) * report * 2e-6, 4),
                               "rg": round(rg, 4)}, open(prog_path, "w"))
                # Stream Rg(t) LIVE to CloudWatch each block (~50 ps) so opening/collapse is visible in real time.
                print(f"  [rep{rep}] t={t_ns:6.2f} ns  CV Rg {rg:.3f} nm  (seed {rg_seed:.3f}, closed ref 0.753)",
                      file=sys.stderr, flush=True)
            rgf.close()
        rgs = np.array(_read_rg_values(rg_path))
        if len(rgs) == 0:
            continue
        within = float((np.abs(rgs - rg_seed) <= 0.1).mean())     # fraction of time still near the seed
        summary["replicas"].append({
            "replica": rep, "seed_Rg": round(rg_seed, 3), "end_Rg": round(float(rgs[-1]), 3),
            "mean_Rg": round(float(rgs.mean()), 3), "min_Rg": round(float(rgs.min()), 3),
            "max_Rg": round(float(rgs.max()), 3), "ns_done": round(len(rgs) * report * 2e-6, 2),
            "frac_time_within_0.1nm_of_seed": round(within, 3)})
        print(f"  replica {rep}: end Rg {rgs[-1]:.3f} nm, mean {rgs.mean():.3f}, "
              f"frac-near-seed {within:.2f}", file=sys.stderr, flush=True)

    # Verdict (Rg proxy): did the replicas stay near the DRUGGABLE SEED conformation, or drift away?
    # Direction-agnostic on purpose — the seed (default ~0.717 nm) can sit BELOW the 0.753 closed ref, so
    # the old "collapse below the open/closed midpoint" logic is invalid here. The DEFINITIVE
    # druggability-persistence call comes from nr4a3_mdpocket on release_rep*.dcd, not from Rg alone.
    means = np.array([r["mean_Rg"] for r in summary["replicas"]])
    fracs = np.array([r["frac_time_within_0.1nm_of_seed"] for r in summary["replicas"]])
    ends = np.array([r["end_Rg"] for r in summary["replicas"]])
    drift = float(np.abs(means - rg_seed).mean())
    near = int((fracs >= 0.5).sum())
    summary["mean_end_Rg"] = round(float(ends.mean()), 3)
    summary["mean_abs_drift_from_seed_nm"] = round(drift, 3)
    summary["verdict"] = (
        f"{near}/{N_REP} replicas spent >=50% of the time within 0.1 nm of the seed Rg ({rg_seed:.3f} nm); "
        f"mean |drift from seed| {drift:.3f} nm. "
        + ("PERSISTENCE near the seed -> the druggable conformation looks thermally metastable. CONFIRM "
           "druggability with nr4a3_mdpocket on release_rep*.dcd before trusting it."
           if near > N_REP / 2 else
           "DRIFT away from the seed -> not obviously metastable. Check WHERE it drifted (a low-Rg drift "
           "toward ~0.573 may still be druggable; a high-Rg drift is the frontier) + run nr4a3_mdpocket."))
    with open(os.path.join(OUT, "release_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({k: summary[k] for k in ("seed_Rg_nm", "closed_Rg_ref_nm", "mean_end_Rg",
                                              "mean_abs_drift_from_seed_nm", "verdict")}, indent=2),
          flush=True)


def _rg_series(xyz, idx0):
    """Rg (nm) of atom subset idx0 for every frame of an mdtraj xyz array (frames, atoms, 3)."""
    import numpy as np
    sub = xyz[:, idx0, :]
    c = sub.mean(axis=1, keepdims=True)
    return np.sqrt(((sub - c) ** 2).sum(axis=2).mean(axis=1))


def _rg_one(pos, idx0):
    import numpy as np
    sub = np.asarray([pos[i] for i in idx0])
    c = sub.mean(axis=0)
    return float(np.sqrt(((sub - c) ** 2).sum(axis=1).mean()))


if __name__ == "__main__":
    main()
