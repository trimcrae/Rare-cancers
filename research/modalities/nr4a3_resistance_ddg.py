#!/usr/bin/env python3
"""
Energetic half of the resistance forecast: computational alanine scan of the denovo_401–NR4A3 warhead pocket
(audit KEEP, high). GPU (reuses the MM-GBSA stack). Pairs with the conservation half (nr4a3_resistance_map.py).

WHY. The conservation map says which pocket residues are *evolutionarily* mutable; this says which ones the
DRUG actually depends on. For each pocket residue we mutate NR4A3 → Ala (PDBFixer), re-score denovo_401 by
MM-GBSA, and report ΔΔG_bind = ΔG(mutant) − ΔG(WT). A large positive ΔΔG = the drug leans hard on that
residue = a candidate escape position. Overlaid with conservation: a drug that anchors on residues that are
BOTH high-ΔΔG AND ortholog-conserved is durable (escape is costly); high-ΔΔG on a variable residue is a
resistance liability. This closes the resistance forecast with an energetic, not just evolutionary, readout.

Runs as a SageMaker Processing job mounting the matrix outputs (nr4a3-opened.pdb + docked_nr4a3.sdf), exactly
like nr4a3_mmgbsa.py. Checkpoints per residue to OUTPUT_DIR (continuous S3 upload) so a timeout never loses
completed mutants. Output: nr4a3-resistance-ddg.json.
"""

import json
import os
import sys
import time

HERE = os.path.dirname(__file__)
IN = os.environ.get("INPUT_DIR", HERE)
OUT = os.environ.get("OUTPUT_DIR", HERE)
POSE_NAME = os.environ.get("POSE_NAME", "denovo_401")
CHAIN = os.environ.get("RECEPTOR_CHAIN", "A")
# three-letter codes for the pocket residues (NR4A3/Q92570 numbering) — used to build PDBFixer mutation strings
POCKET = {406: "LEU", 407: "THR", 410: "THR", 411: "PRO", 412: "ARG",
          481: "ARG", 484: "ILE", 485: "ARG", 531: "ILE", 534: "LEU"}
MULTISNAPSHOT = os.environ.get("MS", "1") == "1"


def rank_ddg(rows):
    """Pure: sort residues by descending ΔΔG (biggest binding loss on mutation = most drug-critical)."""
    scored = [r for r in rows if r.get("ddg") is not None]
    return sorted(scored, key=lambda r: r["ddg"], reverse=True)


def classify(ddg, hot=2.0):
    """Pure: a residue is a drug 'hotspot' if mutating it to Ala costs > `hot` kcal/mol of binding."""
    if ddg is None:
        return "unscored"
    return "drug-critical hotspot" if ddg > hot else "peripheral"


def _prepare_mutant(receptor_pdb, mutation):
    """PDBFixer the receptor AND apply one point mutation (e.g. 'LEU-406-ALA') on CHAIN before adding atoms."""
    import mmgbsa_energy as mme
    openmm, app, unit, _SG, _Mol, PDBFixer = mme._mm()
    fixer = PDBFixer(filename=receptor_pdb)
    if mutation:
        fixer.applyMutations([mutation], CHAIN)      # e.g. LEU-406-ALA
    fixer.findMissingResidues()
    fixer.missingResidues = {}
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)
    fixer.topology.setPeriodicBoxVectors(None)
    return fixer.topology, fixer.positions


def _score(rec_top, rec_pos, pose, mme):
    if MULTISNAPSHOT:
        return mme.endpoint_dG_multisnapshot(rec_top, rec_pos, pose, n_frames=int(os.environ.get("MS_FRAMES", "8")))
    return mme.endpoint_dG(rec_top, rec_pos, pose)


def main():
    import mmgbsa_energy as mme
    rec_pdb = os.path.join(IN, "nr4a3-opened.pdb")
    pose_sdf = os.path.join(IN, "docked_nr4a3.sdf")
    res = {"_title": "denovo_401–NR4A3 warhead-pocket alanine scan (resistance ΔΔG)", "pose": POSE_NAME,
           "multisnapshot": MULTISNAPSHOT, "residues": []}
    outp = os.path.join(OUT, "nr4a3-resistance-ddg.json")

    def _write():
        json.dump(res, open(outp, "w"), indent=2)

    if not (os.path.exists(rec_pdb) and os.path.exists(pose_sdf)):
        res["_status"] = f"missing inputs ({rec_pdb} / {pose_sdf})"; _write(); print(res["_status"]); return
    poses = mme.load_poses(pose_sdf)
    if POSE_NAME not in poses:
        res["_status"] = f"pose {POSE_NAME} not in {list(poses)[:8]}"; _write(); print(res["_status"]); return
    pose = poses[POSE_NAME]

    # 1) wild-type reference
    omm, _app, ommunit, *_ = mme._mm()
    mme._platform(omm, ommunit)                                # force GPU platform up front (fail fast)
    wt_top, wt_pos = _prepare_mutant(rec_pdb, None)
    wt = _score(wt_top, wt_pos, pose, mme)
    res["wt_dG"] = wt["dG"]
    res["wt_dG_sd"] = wt.get("dG_sd")
    _write()
    print(f"[resistance] WT ΔG = {wt['dG']:.2f}", flush=True)

    # 2) per-residue Ala mutants, checkpointing each (crash/timeout-safe)
    for pos, resname in POCKET.items():
        if resname == "ALA":
            continue
        t0 = time.time()
        row = {"position": pos, "wt_residue": resname, "mutation": f"{resname}-{pos}-ALA"}
        try:
            mt, mp = _prepare_mutant(rec_pdb, row["mutation"])
            mut = _score(mt, mp, pose, mme)
            row["mut_dG"] = mut["dG"]
            row["ddg"] = round(mut["dG"] - wt["dG"], 2)          # >0 = binding weakened by the mutation
            row["classification"] = classify(row["ddg"])
        except Exception as e:  # noqa: BLE001 — one bad mutant never voids the scan
            row["_error"] = str(e)[:160]
        res["residues"].append(row)
        _write()                                                # checkpoint after every residue
        print(f"  {row['mutation']:<14} ddg={row.get('ddg')} ({int(time.time()-t0)}s)", flush=True)

    res["ranked"] = rank_ddg(res["residues"])
    res["_note"] = ("ΔΔG>0 = mutation weakens denovo_401 binding (drug-critical residue). Cross-reference with "
                    "nr4a3-resistance-map.json: drug-critical AND ortholog-conserved = durable anchor; "
                    "drug-critical AND ortholog-variable = escape liability.")
    _write()
    print("wrote", outp, file=sys.stderr)


if __name__ == "__main__":
    main()
