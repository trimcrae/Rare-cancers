#!/usr/bin/env python3
"""MATCHED unbiased "release" MD + frame export for ANY NR4A paralogue — the ensemble half of the
categorical-dynamics test.

WHY THIS EXISTS AND WHY IT IS NOT `nr4a3_md_release.py`. That driver is deliberately pinned to NR4A3: it
resets `M.CV_RESIDUES` to the reference set and fetches AF-Q92570 explicitly, because it reuses the NR4A3
metad checkpoint. The categorical-dynamics question needs the IDENTICAL protocol run on NR4A1 and NR4A2, so
this module is that driver made TARGET-aware, plus the frame export the analysis consumes. NR4A3 behaviour is
reproduced exactly when TARGET=NR4A3, so the paralogue ensembles are matched to the committed NR4A3 one by
construction rather than by claim.

THE PROTOCOL, WHICH IS THE WHOLE POINT (identical to the NR4A3 release run):
  * system + force field come from the metad checkpoint's serialized base System (amber14-all + tip3pfb,
    PME, 1.0 nm cutoff, HBonds constraints, 1.0 nm padding, 0.15 M NaCl) — the SAME object, not a rebuild,
    so nothing can drift between the biased and unbiased halves;
  * seed frame = the metad frame nearest TARGET_RG on the CV (Rg of the HOMOLOGOUS Pocket-5 lining CA
    atoms, mapped by the same BLOSUM62 alignment `nr4a3_metad._resolve_target` uses), then a 5000-step
    local minimisation (an unminimised biased frame NaNs on step 1);
  * N_REP independent velocity seeds x NS ns, LangevinMiddle 1/ps at METAD["temp"], 2 fs, mixed precision,
    forced CUDA; DCD every 25000 steps = 50 ps;
  * per-block Rg trace + atomic state/progress checkpoint every CHECKPOINT_EVERY blocks, so a spot kill
    loses <= that and a re-dispatch RESUMES and extends (the repo's standing checkpoint rule).

FRAME EXPORT. `--export` writes the protein-only all-atom PDBs the analysis reads, in the layout
`nr4a_paralogue_dynamics.py` expects and the NR4A3 reharmonize run already uses:
    <OUT>/frames/{metad,release_rep0,release_rep1,release_rep2}/fp_<frameindex>_<tag>/frame.pdb
`N_EXPORT` frames per ensemble, evenly spaced over the available frames (the NR4A3 ensemble is 25 per
replica out of 100, and 25 of 1200 metad frames, so the default 25 matches it).

A STRIDED HEAVY-ATOM TRAJECTORY IS ALSO PERSISTED (`traj/*_stride.dcd`, ~50 ps stride, protein heavy atoms
only, a few tens of MB per replica). A panel that kept no trajectory is why three correctable analysis
defects cost a full re-run; keeping one means any future re-analysis is free.

Env: TARGET (NR4A3|NR4A1|NR4A2), NS, N_REP, TARGET_RG, RUN_TAG, N_EXPORT, CHECKPOINT_EVERY,
INPUT_DIR (mounted metad outputs), OUTPUT_DIR, RESUME_DIR.
"""
import glob
import json
import os
import shutil
import sys

import nr4a3_metad as M     # CV residues / CA-index selection / Rg helpers / AF model fetch / METAD params

IN = os.environ.get("INPUT_DIR", M.HERE)
OUT = os.environ.get("OUTPUT_DIR", M.HERE)
TARGET = os.environ.get("TARGET", "NR4A3").upper()
NS = float(os.environ.get("NS", "5"))
N_REP = int(os.environ.get("N_REP", "3"))
RUN_TAG = os.environ.get("RUN_TAG", "release")
RESUME_DIR = os.environ.get("RESUME_DIR", OUT)
CHECKPOINT_EVERY = int(os.environ.get("CHECKPOINT_EVERY", "10"))    # blocks (x50 ps)
N_EXPORT = int(os.environ.get("N_EXPORT", "25"))                    # frames exported per ensemble
# The NR4A3 release seeded the low-energy DRUGGABLE state at CV Rg ~0.717 nm. The same absolute value is used
# for the paralogues because the CV is the Rg of the same NUMBER of homologousCa atoms, so it is directly
# comparable — but the realised seed Rg and each paralogue's own sampled Rg range are BOTH recorded, because
# a paralogue whose pocket simply does not open that far is a finding, not a parameter to tune away.
TARGET_RG = float(os.environ.get("TARGET_RG", "0.717"))


def _read_rg_values(path):
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


def _rg_series(xyz, idx0):
    import numpy as np
    sub = xyz[:, idx0, :]
    c = sub.mean(axis=1, keepdims=True)
    return np.sqrt(((sub - c) ** 2).sum(axis=2).mean(axis=1))


def _rg_one(pos, idx0):
    import numpy as np
    sub = np.asarray([pos[i] for i in idx0])
    c = sub.mean(axis=0)
    return float(np.sqrt(((sub - c) ** 2).sum(axis=1).mean()))


def _resolve_cv():
    """Put the module-level CV on the ACTIVE target (reference values for NR4A3; homologous residues by
    alignment for a paralogue) and return the CV residue-name map used to locate the CA atoms."""
    M.TARGET = TARGET
    lbd_first, lbd_last, cv, af2_pdb = M._resolve_target()
    M.LBD_FIRST, M.LBD_LAST, M.CV_RESIDUES, M.AF2_PDB = lbd_first, lbd_last, cv, af2_pdb
    return M._af2_residue_names(af2_pdb, cv), af2_pdb


def export_frames(out_root, topology_pdb, sources, n_export, protein_only=True, stride_dir=None):
    """Write `n_export` evenly-spaced protein-only all-atom frame PDBs per source trajectory group.

    `sources` maps an ensemble NAME to a list of DCD paths (concatenated in order — the release driver
    writes one DCD per resume segment, so a resumed replica has several). The layout mirrors the NR4A3
    reharmonize output exactly: <out_root>/<name>/fp_<index>_<name>/frame.pdb.
    """
    import mdtraj as md
    written = {}
    for name, dcds in sources.items():
        dcds = [p for p in dcds if os.path.exists(p) and os.path.getsize(p) > 0]
        if not dcds:
            continue
        t = None
        for p in dcds:
            seg = md.load_dcd(p, top=topology_pdb)
            t = seg if t is None else t.join(seg)
        if t is None or t.n_frames == 0:
            continue
        if protein_only:
            sel = t.topology.select("protein")
            t = t.atom_slice(sel)
        if stride_dir:
            os.makedirs(stride_dir, exist_ok=True)
            heavy = t.topology.select("protein and not element H")
            t.atom_slice(heavy).save_dcd(os.path.join(stride_dir, f"{name}_stride.dcd"))
            t.atom_slice(heavy)[0].save_pdb(os.path.join(stride_dir, f"{name}_stride_top.pdb"))
        n = t.n_frames
        k = min(n_export, n)
        idx = [int(round(i * (n - 1) / max(1, k - 1))) for i in range(k)] if k > 1 else [0]
        idx = sorted(set(idx))
        d = os.path.join(out_root, name)
        os.makedirs(d, exist_ok=True)
        for i in idx:
            fd = os.path.join(d, f"fp_{i}_{name}")
            os.makedirs(fd, exist_ok=True)
            t[i].save_pdb(os.path.join(fd, "frame.pdb"))
        written[name] = {"n_frames_available": n, "n_exported": len(idx), "frame_indices": idx,
                         "sources": [os.path.basename(p) for p in dcds]}
        print(f"  [export] {name}: {len(idx)} of {n} frames -> {d}", file=sys.stderr, flush=True)
    return written


def main():
    export_only = "--export-only" in sys.argv
    try:
        import openmm as mm
        import openmm.app as app
        from openmm import unit
        import mdtraj as md
    except ImportError as e:  # noqa: BLE001
        print(f"  needs openmm + mdtraj (GPU box): {e}", file=sys.stderr)
        return 1

    system_xml = os.path.join(IN, "metad_system.xml")
    solvated = os.path.join(IN, "nr4a3-lbd-solvated.pdb")   # metad writes this name for every TARGET
    dcd = os.path.join(IN, "nr4a3-lbd-metad.dcd")
    for p in (system_xml, solvated, dcd):
        if not os.path.exists(p):
            sys.exit(f"  ABORT: missing {p} (mount the metad outputs at INPUT_DIR)")
    os.makedirs(OUT, exist_ok=True)

    pdb = app.PDBFile(solvated)
    topology = pdb.topology
    with open(system_xml) as fh:
        system = mm.XmlSerializer.deserialize(fh.read())    # base system, NO PlumedForce = unbiased

    cv_identities, af2_pdb = _resolve_cv()
    print(f"  TARGET={TARGET} CV residues {M.CV_RESIDUES} -> {cv_identities}", file=sys.stderr, flush=True)
    plumed_atoms = M._cv_ca_plumed_indices(topology, cv_identities)
    if len(plumed_atoms) != len(M.CV_RESIDUES):
        sys.exit(f"  ABORT: matched {len(plumed_atoms)}/{len(M.CV_RESIDUES)} CV CA atoms")
    idx0 = [i - 1 for i in plumed_atoms]

    import numpy as np
    t = md.load(dcd, top=solvated)
    rg_traj = _rg_series(t.xyz, idx0)
    if TARGET_RG <= 0:
        seed_frame = int(rg_traj.argmax())
        seed_mode = "max-Rg frontier (legacy)"
    else:
        seed_frame = int(np.abs(rg_traj - TARGET_RG).argmin())
        seed_mode = f"nearest TARGET_RG={TARGET_RG:.3f}"
    rg_seed = float(rg_traj[seed_frame])
    print(f"  seed frame {seed_frame}/{t.n_frames} [{seed_mode}]: CV Rg {rg_seed:.3f} nm "
          f"(metad Rg range {rg_traj.min():.3f}-{rg_traj.max():.3f})", file=sys.stderr, flush=True)
    open_positions = t.xyz[seed_frame] * unit.nanometer

    summary = {"target": TARGET, "seed_mode": seed_mode, "seed_frame": seed_frame,
               "seed_Rg_nm": round(rg_seed, 3), "target_rg_nm": TARGET_RG,
               "metad_Rg_min_nm": round(float(rg_traj.min()), 3),
               "metad_Rg_max_nm": round(float(rg_traj.max()), 3),
               "cv_residues": M.CV_RESIDUES, "cv_identities": cv_identities,
               "ns_per_replica": NS, "n_replicas": N_REP, "replicas": [],
               "_matched_to": "the NR4A3 release run: same System object from the metad checkpoint, same "
                              "integrator/timestep/thermostat, same 50 ps reporting, same seed rule.",
               "_seed_rg_caveat": "TARGET_RG is the NR4A3 druggable-state CV value. If a paralogue's metad "
                                  "never reaches it, the seed is the NEAREST frame and its Rg is recorded "
                                  "here — the ensembles are then NOT matched on realised openness and the "
                                  "analysis must say so."}

    if not export_only:
        try:
            cuda = mm.Platform.getPlatformByName("CUDA")
        except Exception as e:  # noqa: BLE001
            sys.exit(f"  ABORT: CUDA platform unavailable: {e}")

        need_fresh = any(not (os.path.exists(os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{r}.state.xml"))
                              and os.path.exists(os.path.join(RESUME_DIR, f"{RUN_TAG}_rep{r}.progress.json")))
                         for r in range(N_REP))
        if not need_fresh:
            print("  all replicas resume from checkpoint — skipping seed minimization",
                  file=sys.stderr, flush=True)
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
        print(f"  minimized seed frame: CV Rg {rg_seed:.3f} -> {rg_min:.3f} nm", file=sys.stderr, flush=True)

        steps = int(NS * 1e6 / 2)          # 2 fs
        report = 25000                     # 50 ps
        nblocks = max(1, steps // report)
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
            if os.path.exists(r_state) and os.path.exists(r_prog):
                sim.loadState(r_state)
                done = int(json.load(open(r_prog)).get("blocks_done", 0))
                if RESUME_DIR != OUT:
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
                print(f"  [rep{rep}] already at target ({done} >= {nblocks} blocks) — skipping",
                      file=sys.stderr, flush=True)
                rgf.close()
            else:
                traj_dcd = os.path.join(OUT, f"{RUN_TAG}_rep{rep}_from{done}.dcd")
                sim.reporters.append(app.DCDReporter(traj_dcd, report))
                for b in range(done, nblocks):
                    sim.step(report)
                    pos = sim.context.getState(getPositions=True).getPositions(
                        asNumpy=True).value_in_unit(unit.nanometer)
                    rg = _rg_one(pos, idx0)
                    t_ns = (b + 1) * report * 2e-6
                    rgf.write(f"{t_ns:.3f}  {rg:.4f}\n")
                    rgf.flush()
                    if (b + 1) % CHECKPOINT_EVERY == 0 or b + 1 == nblocks:
                        sim.saveState(state_path + ".tmp")
                        os.replace(state_path + ".tmp", state_path)
                        json.dump({"blocks_done": b + 1, "ns_done": round((b + 1) * report * 2e-6, 4),
                                   "rg": round(rg, 4)}, open(prog_path, "w"))
                    print(f"  [rep{rep}] t={t_ns:6.2f} ns  CV Rg {rg:.3f} nm  (seed {rg_seed:.3f})",
                          file=sys.stderr, flush=True)
                rgf.close()
            rgs = np.array(_read_rg_values(rg_path))
            if len(rgs) == 0:
                continue
            within = float((np.abs(rgs - rg_seed) <= 0.1).mean())
            summary["replicas"].append({
                "replica": rep, "seed_Rg": round(rg_seed, 3), "end_Rg": round(float(rgs[-1]), 3),
                "mean_Rg": round(float(rgs.mean()), 3), "min_Rg": round(float(rgs.min()), 3),
                "max_Rg": round(float(rgs.max()), 3), "ns_done": round(len(rgs) * report * 2e-6, 2),
                "frac_time_within_0.1nm_of_seed": round(within, 3)})
            print(f"  replica {rep}: end Rg {rgs[-1]:.3f} nm, mean {rgs.mean():.3f}, "
                  f"frac-near-seed {within:.2f}", file=sys.stderr, flush=True)

    # ---- frame export (also runs on --export-only, so a finished run can be re-exported for $0) --------
    sources = {"metad": [dcd]}
    for rep in range(N_REP):
        segs = sorted(glob.glob(os.path.join(OUT, f"{RUN_TAG}_rep{rep}_from*.dcd")),
                      key=lambda p: int(p.rsplit("from", 1)[1].split(".")[0]))
        if segs:
            sources[f"release_rep{rep}"] = segs
    summary["export"] = export_frames(os.path.join(OUT, "frames"), solvated, sources, N_EXPORT,
                                      stride_dir=os.path.join(OUT, "traj"))
    with open(os.path.join(OUT, "release_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps({k: summary[k] for k in ("target", "seed_Rg_nm", "metad_Rg_min_nm", "metad_Rg_max_nm",
                                              "export") if k in summary}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
