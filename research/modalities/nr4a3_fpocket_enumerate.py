#!/usr/bin/env python3
"""
Enumerate the exact lining residues of the NR4A3 LBD pockets by running fpocket on the AF2 model, and
report which pocket is the most druggable LBD cavity and which holds the selectivity handles.

The file<->pocket mapping is DERIVED from the data (alpha-sphere fingerprints; see fpocket_lib) and
asserted bijective — it does NOT assume a 0- or 1-based fpocket file convention. (In this environment
the files are 1-indexed to match info.txt, so the orthosteric Pocket 5 = 0.495, residues 406-534, is
confirmed; deriving the mapping just removes the latent assumption and fails loud if a future build
differs.) The derived mapping is cross-printed against the naive +0/+1 assumptions so the real
convention is auditable in the log.

INPUT_DIR (default /opt/ml/processing/input) must contain AF-Q92570.pdb. OUTPUT_DIR receives
pocket5_lining_residues.json. The AF2 model uses UniProt numbering, so resSeq == residue.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

import fpocket_lib as fl
import pocket_tracking as pt   # harmonized, score-independent orthosteric-pocket tracking

LBD_FIRST, LBD_LAST = 373, 626
POCKET5_LINING = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]  # fixed 10-residue lining set
HANDLES = [406, 407, 410, 412, 484, 531, 534]   # 7 selectivity-divergent handles (nr4a-selectivity.json)


def _ca_by_resnum(pdb_path):
    """{resnum: (x,y,z)} CA coords (Angstrom, UniProt numbering) from the AF2 model PDB."""
    ca = {}
    with open(pdb_path) as fh:
        for line in fh:
            if not line.startswith("ATOM") or line[12:16].strip() != "CA":
                continue
            try:
                ca[int(line[22:26])] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            except ValueError:
                continue
    return ca
IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")


def _read(path):
    with open(path) as fh:
        return fh.read()


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

    info = fl.parse_info(_read(os.path.join(out_dir, "AF-Q92570_info.txt")))
    out_pdb = os.path.join(out_dir, "AF-Q92570_out.pdb")
    out_coords = fl.out_pdb_sphere_coords(_read(out_pdb)) if os.path.exists(out_pdb) else {}

    # Gather per-file (file_index) data from the residue + vertex files.
    file_residues, file_counts, file_coords = {}, {}, {}
    for f in glob.glob(os.path.join(out_dir, "pockets", "pocket*_atm.pdb")):
        fidx = int(re.search(r"pocket(\d+)_atm", f).group(1))
        file_residues[fidx] = fl.parse_atm_residues(_read(f))
        vert = os.path.join(out_dir, "pockets", f"pocket{fidx}_vert.pqr")
        vtext = _read(vert) if os.path.exists(vert) else ""
        file_coords[fidx] = fl.pqr_sphere_coords(vtext)        # for the coordinate tie-break only
        file_counts[fidx] = fl.count_pqr_spheres(vtext)        # TRUE count (raw lines), matches info.txt
    if not file_residues:
        sys.exit("  ABORT: fpocket produced no pocket residue files")

    # DERIVE the file -> info-pocket-number mapping (raises loudly on any ambiguity).
    mapping = fl.map_files_to_pockets(info, file_counts, file_coords, out_coords)

    # Audit: how the data-derived mapping compares to the naive +0 / +1 filename assumptions.
    print("  MAPPING AUDIT (file_idx -> derived pocket | +0 assume | +1 assume):", flush=True)
    for fidx in sorted(mapping):
        print(f"    file {fidx:>2} -> pocket {mapping[fidx]:>2} | +0={fidx} | +1={fidx + 1}",
              flush=True)

    pockets = []
    for fidx, resids in file_residues.items():
        pid = mapping[fidx]
        pockets.append({
            "pocket": pid,
            "druggability": info[pid]["druggability"],
            "alpha_spheres": info[pid]["alpha_spheres"],
            "n_residues": len(resids),
            "residues": resids,
            "n_in_lbd": sum(LBD_FIRST <= r <= LBD_LAST for r in resids),
            "n_handles": sum(r in HANDLES for r in resids),
        })

    selected = fl.select_druggable_lbd_pocket(pockets, LBD_FIRST, LBD_LAST)
    if selected is None:
        sys.exit("  ABORT: no fpocket pocket has residues in the LBD (373-626)")
    cv_residues = sorted(r for r in selected["residues"] if LBD_FIRST <= r <= LBD_LAST)
    handle_pocket = max(pockets, key=lambda p: p["n_handles"])

    print("  FULL POCKET TABLE (pocket | druggability | n_res | n_in_lbd | n_handles | res_range):",
          flush=True)
    for p in sorted(pockets, key=lambda p: (p["druggability"] or 0), reverse=True):
        rr = f"{p['residues'][0]}-{p['residues'][-1]}" if p["residues"] else "-"
        print(f"    pocket {p['pocket']:>2} | drug {p['druggability']} | n {p['n_residues']:>2} | "
              f"lbd {p['n_in_lbd']:>2} | handles {p['n_handles']} | {rr}", flush=True)

    # HARMONIZED, score-INDEPENDENT orthosteric match: identify Pocket-5 by the FIXED lining set + the
    # composite gate, NOT by druggability rank. Additive — the legacy 'selected_druggable_pocket' stays.
    ca = _ca_by_resnum(local_pdb)
    fpocket_version = pt.resolved_fpocket_version()
    harmonized = {"match_mode": pt.match_mode(), "fpocket_version": fpocket_version,
                  "match_params": pt.match_params(), "reference_lining_uniprot": POCKET5_LINING}
    try:
        ref = pt.orthosteric_reference(ca, lining_residues=POCKET5_LINING, span=pt.POCKET5_SPAN)
        cands = [{"residues": p["residues"], "druggability": p["druggability"], "pocket": p["pocket"]}
                 for p in pockets]
        hit = pt.match_pocket(cands, ref, ca_by_resnum=ca, **pt.match_params())
        harmonized["matched_pocket"] = None if hit is None else hit["pocket"]
        harmonized["matched_druggability"] = None if hit is None else hit["druggability"]
        harmonized["match_metrics"] = None if hit is None else hit["_match"]
        matched_scores = [hit["druggability"]] if (hit and hit["druggability"] is not None) else []
        harmonized["detection"] = pt.detection_report(matched_scores, d_star=pt.D_STAR, n_propagated=1)
    except ValueError as e:
        harmonized["error"] = str(e)[:200]
    print(f"  HARMONIZED match: pocket={harmonized.get('matched_pocket')} "
          f"drug={harmonized.get('matched_druggability')} mode={harmonized['match_mode']} "
          f"(fpocket {fpocket_version})", flush=True)

    result = {
        "fpocket_version": fpocket_version,
        "harmonized_orthosteric_match": harmonized,
        "selected_druggable_pocket": selected["pocket"],
        "selected_druggability": selected["druggability"],
        "selection_rule": "highest druggability among LBD pockets (LEGACY; see harmonized_orthosteric_match)",
        "cv_residues_druggable": cv_residues,
        "handle_pocket": handle_pocket["pocket"],
        "handle_pocket_druggability": handle_pocket["druggability"],
        "handle_pocket_residues": sorted(r for r in handle_pocket["residues"]
                                         if LBD_FIRST <= r <= LBD_LAST),
        "handle_pocket_n_handles": handle_pocket["n_handles"],
        "file_to_pocket_mapping": {str(k): v for k, v in mapping.items()},
        "all_pockets": pockets,
    }
    with open(os.path.join(OUT, "pocket5_lining_residues.json"), "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"  DRUGGABLE pocket {selected['pocket']} (druggability {selected['druggability']}); "
          f"LBD residues: {cv_residues}", flush=True)
    print(f"  HANDLE pocket {handle_pocket['pocket']} (druggability {handle_pocket['druggability']}) "
          f"holds {handle_pocket['n_handles']}/{len(HANDLES)} handles; "
          f"residues: {result['handle_pocket_residues']}", flush=True)


if __name__ == "__main__":
    main()
