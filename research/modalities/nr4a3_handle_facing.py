#!/usr/bin/env python3
"""
Gate-2 handle-facing confirmation for the NR4A3 cryptic pocket (post-processing of the 30 ns metad run).

WHY. The per-frame fpocket analysis (nr4a3_mdpocket.py) showed the opened orthosteric pocket reaches
druggability ~0.93 — Gate 2 "the opened state is druggable" PASSES on volume. But the *registered*
Gate-2 pass condition (nr4a3-druggability-prereg.md) has a second clause not yet closed: the pocket must
still line residues 406-534 with the **7 selectivity handles pocket-facing** (not a splayed/unfolded
artifact). This is also the precondition for the selective-warhead screen, whose ranking scores
handle-contact count: if the handles point away in the druggable frames, that score is meaningless. This
script closes that clause, on the trajectory already in S3 — no new GPU run.

WHAT. For a sample of trajectory frames it (1) runs fpocket to find the orthosteric pocket (the detected
pocket overlapping residues 406-534 most) and its druggability — the SAME pocket selection as
nr4a3_mdpocket.py, via the tested nr4a3_structure/fpocket_lib mapping; (2) takes the cavity centroid as
the centroid of that detected pocket's lining-residue CA atoms (faithful to the *opened* cavity; falls
back to the static 406-534 lining centroid if fpocket is unavailable); (3) for each of the 7 handles,
decides pocket-facing via the pure, unit-tested handle_facing_geom; (4) aggregates over the DRUGGABLE
frames (fpocket >= D*=0.53) and reports the registered criterion's verdict. Geometry is screening-grade
(a designability check on an MD ensemble of an AF2 model), not an affinity claim.

Inputs (env INPUT_DIR, default /opt/ml/processing/input): nr4a3-lbd-solvated.pdb + the trajectory
(DCD_NAME, default the metad run nr4a3-lbd-metad.dcd). Output (env OUTPUT_DIR): handle_facing_summary.json
(+ per-frame series and a plot).
"""
import json
import os
import shutil
import subprocess
import sys

import handle_facing_geom as hf

LBD_FIRST = 373                               # AF2 LBD start (the trim used in nr4a3_md.py)
POCKET_FIRST, POCKET_LAST = 406, 534          # orthosteric lining span (nr4a3-degrader-design-spec.md)
HANDLES = [406, 407, 410, 412, 484, 531, 534]  # the 7 NR4A3-vs-NR4A1/NR4A2 divergent residues (AF2 #)
D_STAR = 0.53                                  # calibrated druggable threshold (Gate 0; reconciliation)
MIN_HANDLES_FACING = 4                         # majority of 7 must face in for a frame to "keep" them
NS_PER_FRAME = 0.05                            # DCDReporter wrote every 25000 steps * 2 fs = 50 ps
N_FPOCKET_FRAMES = 25                          # frames sampled (matches nr4a3_mdpocket.py)
BACKBONE = {"N", "CA", "C", "O", "OXT"}
IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")


def main():
    import numpy as np
    import mdtraj as md
    import residue_map as rm

    top = os.path.join(IN, "nr4a3-lbd-solvated.pdb")
    dcd = os.path.join(IN, os.environ.get("DCD_NAME", "nr4a3-lbd-metad.dcd"))
    for p in (top, dcd):
        if not os.path.exists(p):
            sys.exit(f"  ABORT: missing input {p} (expected the metad outputs mounted at INPUT_DIR)")
    os.makedirs(OUT, exist_ok=True)

    print(f"  loading {dcd}", flush=True)
    t = md.load(dcd, top=top)
    prot = t.atom_slice(t.topology.select("protein"))
    residues = list(prot.topology.residues)
    resseqs = [r.resSeq for r in residues]
    print(f"  frames={t.n_frames} protein_atoms={prot.n_atoms} resSeq {min(resseqs)}..{max(resseqs)}",
          flush=True)

    pocket_pos, numbering = rm.resolve_positions(resseqs, range(POCKET_FIRST, POCKET_LAST + 1), LBD_FIRST)
    # Map each handle INDIVIDUALLY so a missing handle resolves to None rather than silently shifting
    # the others (resolve_positions only returns matched positions, not which targets they correspond to).
    handle_pos_map = {}
    for h in HANDLES:
        pos, _ = rm.resolve_positions(resseqs, [h], LBD_FIRST)
        handle_pos_map[h] = pos[0] if pos else None
    print(f"  numbering={numbering}; pocket residues matched={len(pocket_pos)}; "
          f"handles resolved={sum(v is not None for v in handle_pos_map.values())}/{len(HANDLES)}",
          flush=True)
    if not pocket_pos:
        sys.exit(f"  ABORT: could not map Pocket-5 residues onto the {len(residues)} protein residues")

    target_resseqs = {resseqs[i] for i in pocket_pos}
    static_ca_idx = _ca_indices(residues, pocket_pos)            # fallback cavity reference
    handle_atoms = {h: _handle_atoms(residues, i) for h, i in handle_pos_map.items()}

    n = prot.n_frames
    sample = sorted({int(round(x)) for x in np.linspace(0, n - 1, min(n, N_FPOCKET_FRAMES))})
    have_fpocket = bool(shutil.which("fpocket"))
    if not have_fpocket:
        print("  WARN: fpocket not on PATH — geometric-only (no druggable subset)", file=sys.stderr)

    frames = []
    for fi in sample:
        xyz = prot.xyz[fi]                                       # (n_atoms, 3) in nm
        drug, cavity_resseqs = _orthosteric_pocket(prot, fi, target_resseqs) if have_fpocket else (None, None)
        cavity_idx = (_ca_indices(residues, [j for j, rs in enumerate(resseqs) if rs in cavity_resseqs])
                      if cavity_resseqs else static_ca_idx)
        rec = {"frame": fi, "time_ns": round(float(fi) * NS_PER_FRAME, 3),
               "druggability": drug, "facing": {}, "detail": {}}
        for h in HANDLES:
            ca_i, sc_i = handle_atoms[h]
            if ca_i is None:
                rec["facing"][h] = None
                continue
            ca = tuple(float(c) for c in xyz[ca_i])
            sc_pts = [tuple(float(c) for c in xyz[a]) for a in sc_i]
            # cavity centroid EXCLUDING this handle's own CA (avoid self-bias)
            cav = hf.centroid([tuple(float(c) for c in xyz[a]) for a in cavity_idx if a != ca_i])
            res = hf.facing(ca, sc_pts, cav)
            rec["facing"][h] = (res["facing"] if res else None)
            rec["detail"][h] = res
        frames.append(rec)

    summary = hf.summarize(frames, HANDLES, d_star=D_STAR, min_handles_facing=MIN_HANDLES_FACING)
    summary.update({
        "trajectory": os.path.basename(dcd),
        "biased_sampling": "metad" in os.path.basename(dcd),
        "residue_numbering": numbering,
        "fpocket_available": have_fpocket,
        "cavity_reference": ("detected orthosteric-pocket lining CA centroid (per frame)"
                             if have_fpocket else "static 406-534 lining CA centroid (fpocket absent)"),
        "handles": HANDLES,
        "note": ("Confirms the registered Gate-2 sub-condition (nr4a3-druggability-prereg.md): in the "
                 "OPENED, DRUGGABLE frames, do the 7 selectivity handles stay pocket-facing? Geometry is "
                 "a designability check on an MD ensemble of an AF2 model — a screening prior, not an "
                 "affinity. Frame 0 is the post-equilibration production frame, not the static AF2 model."),
        "series": frames,
    })
    with open(os.path.join(OUT, "handle_facing_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)

    print(f"  VERDICT: {summary['verdict']}", flush=True)
    print(f"  druggable frames={summary['n_druggable_frames']}/{summary['n_frames']}; "
          f"mean handles facing (druggable)={summary['mean_handles_facing_druggable']}; "
          f"frac keeping >= {MIN_HANDLES_FACING}={summary['frac_druggable_frames_keeping_handles']}",
          flush=True)
    for h in HANDLES:
        ph = summary["per_handle"][h]
        print(f"    handle {h}: facing(druggable)={ph['frac_facing_druggable']} "
              f"facing(all)={ph['frac_facing_all']}", flush=True)
    _plot(summary, HANDLES)


def _ca_indices(residues, positions):
    """CA atom indices for the given residue positions (skips residues with no CA)."""
    out = []
    for i in positions:
        ca = next((a.index for a in residues[i].atoms if a.name == "CA"), None)
        if ca is not None:
            out.append(ca)
    return out


def _handle_atoms(residues, pos):
    """(CA index, [side-chain heavy-atom indices]) for a handle residue position, or (None, []) if
    unresolved. Side chain = heavy atoms excluding backbone N/CA/C/O/OXT."""
    if pos is None:
        return None, []
    res = residues[pos]
    ca = next((a.index for a in res.atoms if a.name == "CA"), None)
    sc = [a.index for a in res.atoms
          if a.name not in BACKBONE and getattr(a.element, "symbol", "X") != "H"]
    return ca, sc


def _orthosteric_pocket(prot, fi, target_resseqs):
    """Run fpocket on frame `fi`; return (druggability, set(lining resSeqs)) for the detected pocket
    that overlaps the target 406-534 residues most. (None, None) on any failure (best-effort)."""
    import tempfile
    import nr4a3_structure as ns
    d = tempfile.mkdtemp(prefix=f"hf_{fi}_", dir=OUT)
    try:
        pdb = os.path.join(d, "frame.pdb")
        prot[fi].save_pdb(pdb)
        subprocess.run(["fpocket", "-f", pdb], check=True, capture_output=True, text=True, timeout=300)
        resids_by_num, info = ns.pocket_residues_by_number(os.path.join(d, "frame_out"), "frame")
        best_num, best_ov = None, 0
        for num, resids in resids_by_num.items():
            ov = len(target_resseqs.intersection(resids))
            if ov > best_ov:
                best_num, best_ov = num, ov
        if best_num is None:
            return None, None
        return info[best_num]["druggability"], set(resids_by_num[best_num])
    except Exception as e:  # noqa: BLE001 — best-effort per frame
        print(f"  frame {fi} fpocket skipped: {e}", file=sys.stderr)
        return None, None
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _plot(summary, handles):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labels = [str(h) for h in handles]
        dr = [summary["per_handle"][h]["frac_facing_druggable"] or 0 for h in handles]
        al = [summary["per_handle"][h]["frac_facing_all"] or 0 for h in handles]
        x = range(len(handles))
        plt.figure(figsize=(8, 4))
        plt.bar([i - 0.2 for i in x], dr, width=0.4, label="druggable frames")
        plt.bar([i + 0.2 for i in x], al, width=0.4, label="all sampled frames")
        plt.axhline(0.5, color="r", ls="--", lw=0.7)
        plt.xticks(list(x), labels)
        plt.ylim(0, 1)
        plt.xlabel("selectivity handle (NR4A3 residue)")
        plt.ylabel("fraction of frames pocket-facing")
        plt.title("NR4A3 selectivity handles — pocket-facing in the opened pocket")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "handle_facing.png"), dpi=130)
    except Exception as e:  # noqa: BLE001 — plot is a nicety
        print(f"  plot skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
