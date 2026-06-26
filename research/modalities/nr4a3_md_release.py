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
We pick the opened frame from nr4a3-lbd-metad.dcd by max CV Rg, launch N_REP replicas (different
velocity seeds) of NS ns each, and write per-replica Rg(t) (release_rg_repK.dat) + trajectories.

Output: release_summary.json (per replica: start Rg, end Rg, mean/min/max Rg, fraction of time within
0.1 nm of the opened start) + the Rg traces. Forced CUDA platform, same as the other GPU runs.
"""
import json
import os
import sys

import nr4a3_metad as M     # reuse CV residues / CA-index selection / Rg helper / AF model fetch

IN = os.environ.get("INPUT_DIR", M.HERE)        # mounted metad outputs (system/topology/trajectory)
OUT = os.environ.get("OUTPUT_DIR", M.HERE)
NS = float(os.environ.get("NS", "5"))           # ns per replica (collapse, if any, is fast; 3x5=15 ns
                                                # total ~4 h stays under GitHub's 6 h job cap)
N_REP = int(os.environ.get("N_REP", "3"))       # independent velocity seeds


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

    # CV CA atoms (PLUMED 1-based) on the solvated topology, then 0-based for Rg.
    M._fetch_af_model()
    cv_identities = M._af2_residue_names(M.AF2_PDB, M.CV_RESIDUES)
    plumed_atoms = M._cv_ca_plumed_indices(topology, cv_identities)
    if len(plumed_atoms) != len(M.CV_RESIDUES):
        sys.exit(f"  ABORT: matched {len(plumed_atoms)}/{len(M.CV_RESIDUES)} CV CA atoms")

    # pick the most-OPEN frame (max CV Rg) from the metad trajectory.
    t = md.load(dcd, top=solvated)
    idx0 = [i - 1 for i in plumed_atoms]
    rg_traj = _rg_series(t.xyz, idx0)              # nm (mdtraj xyz already in nm)
    open_frame = int(rg_traj.argmax())
    rg_open = float(rg_traj[open_frame])
    print(f"  opened frame {open_frame}/{t.n_frames}: CV Rg {rg_open:.3f} nm "
          f"(traj Rg range {rg_traj.min():.3f}-{rg_traj.max():.3f})", file=sys.stderr)
    open_positions = t.xyz[open_frame] * unit.nanometer

    summary = {"_note": "Unbiased release MD from the metad-opened pocket. Persistence near the opened "
                        "CV Rg => metastable druggable basin (the 38 kcal/mol metad cost is a "
                        "convergence artifact); fast collapse toward the closed Rg (~0.75 nm) => "
                        "bias-induced strain, not a thermally accessible state.",
               "opened_frame": open_frame, "opened_Rg_nm": round(rg_open, 3),
               "closed_Rg_ref_nm": 0.753, "ns_per_replica": NS, "n_replicas": N_REP, "replicas": []}

    try:
        cuda = mm.Platform.getPlatformByName("CUDA")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"  ABORT: CUDA platform unavailable: {e}")

    steps = int(NS * 1e6 / 2)                       # 2 fs timestep
    report = 25000                                  # every 50 ps
    for rep in range(N_REP):
        integ = mm.LangevinMiddleIntegrator(M.METAD["temp"] * unit.kelvin, 1.0 / unit.picosecond,
                                            2.0 * unit.femtosecond)
        sim = app.Simulation(topology, system, integ, cuda, {"Precision": "mixed"})
        sim.context.setPositions(open_positions)
        sim.context.setVelocitiesToTemperature(M.METAD["temp"] * unit.kelvin, 1234 + rep)
        traj_dcd = os.path.join(OUT, f"release_rep{rep}.dcd")
        sim.reporters.append(app.DCDReporter(traj_dcd, report))
        rg_path = os.path.join(OUT, f"release_rg_rep{rep}.dat")
        rgf = open(rg_path, "w")
        rgf.write("# time_ns  cv_Rg_nm\n")
        rgs = []
        nblocks = max(1, steps // report)
        for b in range(nblocks):
            sim.step(report)
            st = sim.context.getState(getPositions=True)
            pos = st.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
            rg = _rg_one(pos, idx0)
            rgs.append(rg)
            rgf.write(f"{(b + 1) * report * 2e-6:.3f}  {rg:.4f}\n")
        rgf.close()
        import numpy as np
        rgs = np.array(rgs)
        within = float((np.abs(rgs - rg_open) <= 0.1).mean())     # fraction of time still ~open
        summary["replicas"].append({
            "replica": rep, "start_Rg": round(rg_open, 3), "end_Rg": round(float(rgs[-1]), 3),
            "mean_Rg": round(float(rgs.mean()), 3), "min_Rg": round(float(rgs.min()), 3),
            "max_Rg": round(float(rgs.max()), 3),
            "frac_time_within_0.1nm_of_open": round(within, 3)})
        print(f"  replica {rep}: end Rg {rgs[-1]:.3f} nm, mean {rgs.mean():.3f}, "
              f"frac-near-open {within:.2f}", file=sys.stderr, flush=True)

    # verdict heuristic: did it stay open or collapse toward the closed reference?
    ends = [r["end_Rg"] for r in summary["replicas"]]
    means = [r["mean_Rg"] for r in summary["replicas"]]
    closed, opened = 0.753, rg_open
    midpoint = 0.5 * (closed + opened)
    collapsed = sum(1 for m in means if m < midpoint)
    summary["verdict"] = (
        f"{collapsed}/{N_REP} replicas relaxed below the closed/open midpoint ({midpoint:.2f} nm). "
        + ("Predominant COLLAPSE -> opened state is NOT metastable (supports costly/inaccessible)."
           if collapsed > N_REP / 2 else
           "Predominant PERSISTENCE -> opened druggable state is metastable (the 38 kcal/mol metad "
           "cost is a convergence artifact; Gate 3 plausibly accessible)."))
    summary["mean_end_Rg"] = round(sum(ends) / len(ends), 3)
    with open(os.path.join(OUT, "release_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({k: summary[k] for k in ("opened_Rg_nm", "closed_Rg_ref_nm", "mean_end_Rg",
                                              "verdict")}, indent=2), flush=True)


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
