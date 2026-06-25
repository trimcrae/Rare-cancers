#!/usr/bin/env python3
"""
Enumerate the exact lining residues of NR4A3 Pocket-5 (the orthosteric/degrader site) by re-running
fpocket on the AF2 model with per-pocket residue output. nr4a3-structure-assessment.json stored only
the pocket's residue min/max + count; the metadynamics collective variable needs the *precise* set.

Identifies the LBD pocket — the one whose lining residues overlap the known 406-534 span (tie-broken
by druggability closest to the recorded 0.495) — and writes its lining residues (restricted to the
ordered LBD, 373-626) as the CV atom set.

INPUT_DIR (default /opt/ml/processing/input) must contain AF-Q92570.pdb (the full AF2 model, as
saved by the MD job to s3://<bucket>/nr4a3-md). OUTPUT_DIR (default /opt/ml/processing/output)
receives pocket5_lining_residues.json. The AF2 model uses UniProt numbering, so resSeq == residue.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

LBD_FIRST, LBD_LAST = 373, 626
KNOWN_POCKET = (406, 534)                      # Pocket-5 span from nr4a3-structure-assessment.json
KNOWN_DRUGGABILITY = 0.495
IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")


def main():
    pdb = os.path.join(IN, "AF-Q92570.pdb")
    if not os.path.exists(pdb):
        sys.exit(f"  ABORT: missing {pdb} (expected the AF2 model mounted at INPUT_DIR)")
    if not shutil.which("fpocket"):
        sys.exit("  ABORT: fpocket binary not on PATH")
    os.makedirs(OUT, exist_ok=True)

    work = os.path.join(OUT, "fpocket_run")
    os.makedirs(work, exist_ok=True)
    local_pdb = os.path.join(work, "AF-Q92570.pdb")
    shutil.copy(pdb, local_pdb)
    print("  running fpocket", flush=True)
    subprocess.run(["fpocket", "-f", local_pdb], check=True)
    out_dir = os.path.join(work, "AF-Q92570_out")
    drug = _druggability(os.path.join(out_dir, "AF-Q92570_info.txt"))

    pockets = []
    for f in sorted(glob.glob(os.path.join(out_dir, "pockets", "pocket*_atm.pdb"))):
        pid = int(re.search(r"pocket(\d+)_atm", f).group(1)) + 1     # files 0-indexed; info.txt 1-indexed
        resids = _residues(f)
        pockets.append({
            "pocket": pid,
            "druggability": drug.get(pid),
            "n_residues": len(resids),
            "residues": resids,
            "n_in_lbd": sum(LBD_FIRST <= r <= LBD_LAST for r in resids),
            "overlap_with_known_406_534": sum(KNOWN_POCKET[0] <= r <= KNOWN_POCKET[1] for r in resids),
        })
    if not pockets:
        sys.exit("  ABORT: fpocket produced no pockets")

    selected = max(pockets, key=lambda p: (p["overlap_with_known_406_534"],
                                            -abs((p["druggability"] or 0) - KNOWN_DRUGGABILITY)))
    cv_residues = sorted(r for r in selected["residues"] if LBD_FIRST <= r <= LBD_LAST)

    result = {
        "selected_pocket": selected["pocket"],
        "selected_druggability": selected["druggability"],
        "cv_residues": cv_residues,
        "n_cv_residues": len(cv_residues),
        "all_pockets": pockets,
    }
    with open(os.path.join(OUT, "pocket5_lining_residues.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"  SELECTED pocket {selected['pocket']} (druggability {selected['druggability']}); "
          f"CV residues ({len(cv_residues)}): {cv_residues}", flush=True)


def _residues(atm_pdb):
    res = set()
    with open(atm_pdb) as fh:
        for line in fh:
            if line.startswith(("ATOM", "HETATM")):
                try:
                    res.add(int(line[22:26]))
                except ValueError:
                    pass
    return sorted(res)


def _druggability(info_path):
    drug, pid = {}, None
    if not os.path.exists(info_path):
        return drug
    with open(info_path) as fh:
        for line in fh:
            m = re.match(r"\s*Pocket\s+(\d+)\s*:", line)
            if m:
                pid = int(m.group(1))
            elif pid is not None and "Druggability Score" in line:
                m2 = re.search(r"([0-9.]+)", line.split(":", 1)[1])
                if m2:
                    drug[pid] = float(m2.group(1))
    return drug


if __name__ == "__main__":
    main()
