#!/usr/bin/env python3
"""
Structural sanity check on the 'opened' NR4A3 LBD frame that underpins the docking / MM-GBSA / (attempted) FEP.

QUESTION. The metadynamics that opened the pocket left the frame ELONGATED (~99 Å for a 254-res LBD; a floppy
N-terminal hinge + splayed pocket helices). Is that a *legitimate induced-fit opening of an intact fold*, or
did the biasing MELT the LBD? Two CPU metrics vs the pre-metad AF2 LBD (Q92570, residues 373-626):

  1. DSSP secondary-structure content (helix / sheet / coil fraction) of the opened frame vs the AF2 LBD
     baseline. An intact induced-fit opening keeps most of its helices; an over-driven / melted frame loses
     them. (mdtraj simplified DSSP — no external binary.)
  2. CA-backbone RMSD of the folded CORE (Kabsch superposition), excluding the floppy/opened runs the geom
     locator flagged (N-hinge 1-22, C-term 253-254, and — reported separately — the opened pocket mouth
     48-60). Low core-RMSD ⇒ the fold is preserved and only the tail + pocket moved; high ⇒ the core distorted.

NUMBERING. The opened frame is renumbered 1-254; the AF2 model is UniProt-numbered, LBD = 373-626. Opened
residue i maps to AF2 residue i+372.

Inputs (argv or env FRAME_PDB / REF_PDB): opened-frame PDB, AF2 model PDB. Output: JSON verdict.
The pure geometry core (kabsch_rmsd, matched-CA extraction) is unit-tested without mdtraj/network.
"""
import json
import os
import sys

OFFSET = 372                     # opened resSeq i  <->  AF2 resSeq i+372  (LBD 373-626)
FLOPPY_RUNS = [(1, 22), (253, 254)]      # N-hinge + C-term: excluded from the "is the fold intact" core RMSD
POCKET_MOUTH = [(48, 60)]                # the metad-opened pocket helices: EXPECTED to move (reported apart)


def kabsch_rmsd(P, Q):
    """Minimal-RMSD (Å) between two (N,3) CA sets after optimal rigid superposition (Kabsch). Pure numpy."""
    import numpy as np
    P = np.asarray(P, float)
    Q = np.asarray(Q, float)
    Pc = P - P.mean(0)
    Qc = Q - Q.mean(0)
    H = Pc.T @ Qc
    U, _S, Vt = np.linalg.svd(H)
    d = 1.0 if np.linalg.det(Vt.T @ U.T) > 0 else -1.0
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
    Pr = Pc @ R.T
    return float(np.sqrt(((Pr - Qc) ** 2).sum() / len(P)))


def _in_runs(resseq, runs):
    return any(lo <= resseq <= hi for lo, hi in runs)


def matched_core_ca(frame_ca, ref_ca, exclude):
    """frame_ca/ref_ca: {resSeq: (x,y,z)} for opened frame (1-254) and AF2 (373-626). Return (P, Q) matched CA
    coordinate lists over opened residues NOT in `exclude` whose AF2 partner (i+OFFSET) exists — same order."""
    P, Q = [], []
    for i in sorted(frame_ca):
        if _in_runs(i, exclude):
            continue
        j = i + OFFSET
        if j in ref_ca:
            P.append(frame_ca[i])
            Q.append(ref_ca[j])
    return P, Q


def _ca_coords(traj):
    """{resSeq: (x,y,z) in Å} for CA atoms of the first frame of an mdtraj trajectory."""
    top = traj.topology
    out = {}
    for a in top.atoms:
        if a.name == "CA":
            out[a.residue.resSeq] = tuple(10.0 * traj.xyz[0, a.index])   # nm -> Å
    return out


def _dssp_fractions(traj):
    import mdtraj as md
    codes = md.compute_dssp(traj, simplified=True)[0]     # 'H' helix, 'E' strand, 'C' coil, 'NA'
    n = sum(1 for c in codes if c != "NA")
    if not n:
        return {"helix": None, "strand": None, "coil": None, "n": 0}
    return {"helix": round(sum(c == "H" for c in codes) / n, 3),
            "strand": round(sum(c == "E" for c in codes) / n, 3),
            "coil": round(sum(c == "C" for c in codes) / n, 3), "n": n}


def main():
    frame_pdb = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FRAME_PDB", "nr4a3-opened.pdb"))
    ref_pdb = (sys.argv[2] if len(sys.argv) > 2 else os.environ.get("REF_PDB", "AF-Q92570.pdb"))
    out_path = os.environ.get("OUT", "nr4a3-frame-sanity.json")
    try:
        import mdtraj as md
    except ImportError:
        json.dump({"_status": "mdtraj missing"}, open(out_path, "w"), indent=2)
        print("mdtraj missing", file=sys.stderr)
        return
    frame = md.load(frame_pdb)
    ref = md.load(ref_pdb)
    # AF2 ref: restrict to the LBD window so DSSP % is the LBD baseline, not the full disordered model.
    ref_lbd_idx = ref.topology.select(f"resSeq {OFFSET + 1} to {OFFSET + 254}")
    ref_lbd = ref.atom_slice(ref_lbd_idx) if len(ref_lbd_idx) else ref

    frame_ca, ref_ca = _ca_coords(frame), _ca_coords(ref)
    P_core, Q_core = matched_core_ca(frame_ca, ref_ca, exclude=FLOPPY_RUNS + POCKET_MOUTH)
    P_wide, Q_wide = matched_core_ca(frame_ca, ref_ca, exclude=FLOPPY_RUNS)   # core + pocket mouth

    core_rmsd = kabsch_rmsd(P_core, Q_core) if len(P_core) >= 4 else None
    wide_rmsd = kabsch_rmsd(P_wide, Q_wide) if len(P_wide) >= 4 else None
    dssp_frame = _dssp_fractions(frame)
    dssp_ref = _dssp_fractions(ref_lbd)

    verdict = "inconclusive"
    if dssp_frame["helix"] is not None and dssp_ref["helix"] is not None and core_rmsd is not None:
        helix_ret = dssp_frame["helix"] / dssp_ref["helix"] if dssp_ref["helix"] else None
        fold_intact = (helix_ret is not None and helix_ret >= 0.75) and core_rmsd <= 4.0
        verdict = ("FOLD INTACT — legitimate opened frame (helices retained, core superimposes); "
                   "elongation is a floppy tail + opened pocket, not a melt"
                   if fold_intact else
                   "FOLD SUSPECT — helix loss and/or high core-RMSD: metad may have over-driven/melted the LBD; "
                   "re-extract a compact opened frame before trusting FEP (and re-examine docking/MM-GBSA)")

    result = {
        "_title": "NR4A3 opened-frame structural sanity (fold intact vs metad-melted?)",
        "frame_pdb": os.path.basename(frame_pdb),
        "ref_pdb": os.path.basename(ref_pdb),
        "dssp_opened_frame": dssp_frame,
        "dssp_af2_lbd_baseline": dssp_ref,
        "helix_retention_vs_af2": (round(dssp_frame["helix"] / dssp_ref["helix"], 2)
                                   if dssp_frame["helix"] and dssp_ref["helix"] else None),
        "core_ca_rmsd_A": round(core_rmsd, 2) if core_rmsd is not None else None,
        "core_plus_pocket_ca_rmsd_A": round(wide_rmsd, 2) if wide_rmsd is not None else None,
        "n_core_residues": len(P_core),
        "excluded_from_core": {"floppy": FLOPPY_RUNS, "opened_pocket_mouth": POCKET_MOUTH},
        "verdict": verdict,
        "_note": "Low core-RMSD + retained helices = the opened frame is an intact fold with a floppy hinge and "
                 "a splayed pocket mouth (fine for an induced-fit ABFE target). The pocket-inclusive RMSD is "
                 "reported separately to size how far the pocket opened, NOT as a fold-integrity failure.",
    }
    json.dump(result, open(out_path, "w"), indent=2)
    print("wrote", out_path, file=sys.stderr)
    print(json.dumps({k: result[k] for k in ("dssp_opened_frame", "dssp_af2_lbd_baseline",
                                             "helix_retention_vs_af2", "core_ca_rmsd_A",
                                             "core_plus_pocket_ca_rmsd_A", "verdict")}, indent=2))


if __name__ == "__main__":
    main()
