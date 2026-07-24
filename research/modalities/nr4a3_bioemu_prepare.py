#!/usr/bin/env python3
"""
Turn a BioEmu (side-chain-reconstructed) NR4A3 LBD ensemble into per-frame ALL-ATOM PDBs numbered in UniProt
Q92570 numbering, ready for nr4a3_bioemu_pocket.py (the harmonized Pocket-5 scorer).

BioEmu samples the 254-residue LBD construct (UniProt Q92570 residues 373..626) as backbone frames; the
companion `bioemu.sidechain_relax` (HPacker) step reconstructs side chains and writes a topology PDB + an XTC
trajectory. BioEmu numbers residues 1..254; the harmonized scorer's fixed Pocket-5 lining set is in UniProt
numbering (406,407,410,411,412,481,484,485,531,534), so we ADD the offset (LBD_FIRST-1 = 372) to every residue
so position 1→373 ... 254→626, exactly matching the metad/release frames. Then we write one PDB per frame.

Pure-ish driver (mdtraj I/O only). No BioEmu dependency — operates on the reconstructed topology+trajectory.
"""
import argparse
import os
import sys

LBD_FIRST = 373                      # UniProt Q92570 LBD start (nr4a3_release_druggable.LBD_FIRST)
OFFSET = LBD_FIRST - 1               # BioEmu residue i (1-based) -> UniProt i + OFFSET
EXPECT_N = 254                       # LBD construct length (373..626 inclusive)


def renumber_topology(top, offset=OFFSET):
    """Add `offset` to every residue's resSeq in an mdtraj Topology (in place). Returns the min/max resSeq."""
    lo = hi = None
    for res in top.residues:
        res.resSeq = res.resSeq + offset
        lo = res.resSeq if lo is None else min(lo, res.resSeq)
        hi = res.resSeq if hi is None else max(hi, res.resSeq)
    return lo, hi


def prepare(topology, trajectory, out_dir, max_frames=None, offset=OFFSET):
    """Load `trajectory` (with `topology`), renumber to UniProt numbering, and write one all-atom PDB per frame.
    Returns the list of written PDB paths."""
    import mdtraj as md

    os.makedirs(out_dir, exist_ok=True)
    traj = md.load(trajectory, top=topology)
    # Keep only protein atoms (drop any waters/ions the MD-equil step may have added) so fpocket sees the receptor.
    prot = traj.atom_slice(traj.topology.select("protein"))
    n_res = prot.topology.n_residues
    if n_res != EXPECT_N:
        print(f"  WARNING: {n_res} residues != expected {EXPECT_N} for the 373..626 LBD construct", file=sys.stderr)
    lo, hi = renumber_topology(prot.topology, offset)
    print(f"  renumbered residues -> UniProt {lo}..{hi} ({n_res} residues, {prot.n_frames} frames)")
    # Sanity: the Pocket-5 lining residues must now be present, or the scorer will (correctly) reject every frame.
    present = {r.resSeq for r in prot.topology.residues}
    missing = [r for r in (406, 407, 410, 411, 412, 481, 484, 485, 531, 534) if r not in present]
    if missing:
        print(f"  WARNING: Pocket-5 lining residues absent after renumber: {missing}", file=sys.stderr)

    n = prot.n_frames if max_frames is None else min(max_frames, prot.n_frames)
    paths = []
    width = len(str(n))
    for i in range(n):
        p = os.path.join(out_dir, f"frame_{str(i).zfill(width)}.pdb")
        prot[i].save_pdb(p)
        paths.append(p)
    print(f"  wrote {len(paths)} frame PDBs to {out_dir}")
    return paths


def main():
    ap = argparse.ArgumentParser(description="BioEmu ensemble -> renumbered per-frame all-atom PDBs")
    ap.add_argument("--topology", required=True, help="side-chain-reconstructed topology PDB (bioemu.sidechain_relax)")
    ap.add_argument("--trajectory", required=True, help="reconstructed trajectory (XTC/DCD)")
    ap.add_argument("--out", required=True, help="output directory for per-frame PDBs")
    ap.add_argument("--max-frames", type=int, default=None, help="cap number of frames (default: all)")
    args = ap.parse_args()
    prepare(args.topology, args.trajectory, args.out, args.max_frames)


if __name__ == "__main__":
    main()
