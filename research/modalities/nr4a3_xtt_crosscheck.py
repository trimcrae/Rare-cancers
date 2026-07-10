#!/usr/bin/env python3
"""
Experimental cross-check of the AF2 NR4A3 LBD model against PDB 8XTT (the released NR4A3/NOR-1 LBD
solution-NMR ensemble) — the "primary experimental structural control" the manuscript now adopts.

WHY. The whole degrader pipeline starts from an AlphaFold2 model of the NR4A3 LBD (AFDB AF-Q92570),
because until recently NR4A3 had no experimental structure. RCSB 8XTT (solution NMR, "Nuclear receptor
Nor1 ligand binding domain"; deposited 2024-01-11, released 2025-01-15) is now that experimental
structure. This job asks the three questions that a reviewer will ask, and that the manuscript can now
answer with data instead of a promise:

  Q1  Does the AF2 *starting fold* actually match the experimental LBD?  -> backbone (Cα) RMSD of each
      NMR model to the AF2 LBD, over sequence-aligned residues; reported as a distribution (min/median/
      max) plus a "core" RMSD that excludes the ensemble's flexible termini/loops (so fold agreement is
      not masked by disordered-region spread).
  Q2  Does the *experimental resting ensemble* also show the orthosteric (Pocket-5) cavity as
      borderline/closed — i.e. is our static AF2 fpocket 0.495 corroborated, not an artifact?  ->
      per-NMR-model fpocket at the Pocket-5 site (same metric/pipeline as the static 0.495), as a
      distribution, run in the SAME job (same fpocket build) as a fresh fpocket on the AF2 LBD.
  Q3  Are the 7 paralogue-selectivity handles experimentally resolved, and at the expected positions?
      -> map POCKET5 / HANDLES (Q92570 numbering) onto 8XTT via the alignment; report identity + author
      numbering.

HONEST SCOPE (kept explicit in the output). 8XTT is a resting-state ensemble of the *isolated apo* LBD.
It anchors the AF2 STARTING fold and the resting pocket. It does NOT contain our designed warhead and
does NOT populate the metadynamics-opened induced-fit cavity on demand — so it can neither confirm nor
refute the OPENED pocket, the docked pose, or the ABFE selectivity. Those still require a *ligand-bound*
experimental structure. Q1/Q2 narrow the load-bearing uncertainty to the opened state; they do not close it.

Numbering is established by a global BLOSUM62 alignment (NOT by assuming 8XTT uses UniProt numbering),
so a construct offset or a partially-resolved LBD is handled correctly and reported transparently.

Output: nr4a3-xtt-crosscheck.json (machine-readable; consumed by the manuscript). CPU only (fpocket +
Biopython). Run via gpu-xtt-crosscheck-aws.yml -> SageMaker (the container has open internet, unlike the
authoring container where RCSB is egress-blocked).
"""
import json
import os
import subprocess
import sys
import urllib.request

import numpy as np

import fpocket_lib as fl
from nr4a3_structure import fetch_pdb as fetch_afdb   # AFDB API resolver (reused)

OUT = os.path.join(os.path.dirname(__file__), "nr4a3-xtt-crosscheck.json")
WORK = os.environ.get("RUNNER_TEMP", "/tmp")

PDB_ID = "8XTT"
UNIPROT = "Q92570"          # NR4A3 / NOR-1, human canonical
LBD_FIRST, LBD_LAST = 373, 626

# fpocket "Pocket-5" lining residues on the AF2 model (Q92570 numbering); the 7 handles are a subset.
# Source of truth: nr4a3_fpocket_enumerate.py / pocketminer_src/entry.py (kept identical here).
POCKET5 = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
HANDLES = [406, 407, 410, 412, 484, 531, 534]

# NMR ensembles resolve flexible regions as high-spread; exclude those + chain ends from the "core" RMSD.
CORE_RMSF_CUTOFF_A = 2.0    # matched residue is "core" if its cross-ensemble Cα RMSF <= this (Å)
CORE_TRIM_ENDS = 5         # also drop this many matched residues at each terminus of the matched span

THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
    "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
    "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V", "MSE": "M", "SEC": "U", "PYL": "O",
}


def fetch_rcsb(pdb_id, dest):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    print(f"  downloading {url}", flush=True)
    urllib.request.urlretrieve(url, dest)
    return dest


def _trim_lbd(src_pdb, dst_pdb):
    """Keep only ATOM records within the LBD window (single AF chain), preserving UniProt resSeq."""
    kept, resset = [], set()
    with open(src_pdb) as fh:
        for line in fh:
            if line.startswith(("ATOM", "TER")):
                try:
                    resseq = int(line[22:26])
                except ValueError:
                    continue
                if LBD_FIRST <= resseq <= LBD_LAST:
                    kept.append(line)
                    if line.startswith("ATOM"):
                        resset.add(resseq)
    kept.append("END\n")
    with open(dst_pdb, "w") as fh:
        fh.writelines(kept)
    print(f"  trimmed AF2 LBD -> {dst_pdb}: {len(resset)} residues "
          f"({min(resset)}-{max(resset)})", flush=True)
    return dst_pdb


def main_chain_residues(model, chain_id):
    """Ordered [(resSeq, one_letter, has_CA)] for standard amino acids of one chain in one Biopython model."""
    out = []
    chain = model[chain_id]
    for res in chain:
        if res.id[0] != " ":            # skip HETATM/water
            continue
        aa = THREE_TO_ONE.get(res.resname.strip().upper())
        if aa is None:
            continue
        out.append((res.id[1], aa, "CA" in res))
    return out


def pick_chain(model):
    """Chain id with the most standard-AA residues (the LBD)."""
    best, best_n = None, -1
    for chain in model:
        n = sum(1 for r in chain if r.id[0] == " " and r.resname.strip().upper() in THREE_TO_ONE)
        if n > best_n:
            best, best_n = chain.id, n
    return best


def align_map(af2_res, xtt_res):
    """Global BLOSUM62 alignment of the AF2 LBD sequence to the 8XTT chain sequence. Returns
    (correspondence, identity, coverage) where correspondence = [(af2_resSeq, xtt_resSeq, same_aa)] for
    every aligned column with a residue on both sides."""
    from Bio.Align import PairwiseAligner, substitution_matrices
    aligner = PairwiseAligner()
    aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
    aligner.open_gap_score = -11
    aligner.extend_gap_score = -1
    aligner.mode = "global"
    a_seq = "".join(x[1] for x in af2_res)
    b_seq = "".join(x[1] for x in xtt_res)
    aln = aligner.align(a_seq, b_seq)[0]
    corr, same = [], 0
    for (a0, a1), (b0, b1) in zip(*aln.aligned):      # gapless aligned blocks, equal length
        for k in range(a1 - a0):
            ai, bi = a0 + k, b0 + k
            is_same = af2_res[ai][1] == xtt_res[bi][1]
            corr.append((af2_res[ai][0], xtt_res[bi][0], is_same))
            same += int(is_same)
    identity = round(same / len(corr), 3) if corr else 0.0
    coverage = round(len(corr) / len(af2_res), 3) if af2_res else 0.0
    return corr, identity, coverage


def ca_coords(model, chain_id):
    """{resSeq: np.array([x,y,z])} of Cα atoms for one chain of one model."""
    out = {}
    for res in model[chain_id]:
        if res.id[0] == " " and "CA" in res:
            out[res.id[1]] = res["CA"].get_coord().astype(float)
    return out


def af2_ca_coords(pdb_path):
    out = {}
    with open(pdb_path) as fh:
        for line in fh:
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                out[int(line[22:26])] = np.array(
                    [float(line[30:38]), float(line[38:46]), float(line[46:54])])
    return out


def superpose(ref_xyz, mov_xyz):
    """SVD superposition; returns (rms, rot, tran) mapping mov -> ref frame. Arrays are Nx3, paired."""
    from Bio.SVDSuperimposer import SVDSuperimposer
    sup = SVDSuperimposer()
    sup.set(np.asarray(ref_xyz), np.asarray(mov_xyz))
    sup.run()
    rot, tran = sup.get_rotran()
    return float(sup.get_rms()), rot, tran


def write_model_pdb(model, chain_id, dst):
    """Write one NMR model's chain as a single-model, heavy-atom-only PDB (author numbering preserved)."""
    from Bio.PDB import PDBIO, Select

    class Sel(Select):
        def accept_model(self, m):
            return m.id == model.id

        def accept_chain(self, c):
            return c.id == chain_id

        def accept_residue(self, r):
            return r.id[0] == " " and r.resname.strip().upper() in THREE_TO_ONE

        def accept_atom(self, a):
            return a.element != "H" and (a.get_altloc() in (" ", "A"))

    io = PDBIO()
    io.set_structure(model.get_parent())
    io.save(dst, select=Sel())
    return dst


def fpocket_at(pdb_path, target_resnums):
    """Run fpocket; return (druggability_at_target, max_druggability, n_overlap, n_pockets). The
    target pocket = the fpocket pocket whose lining residues overlap `target_resnums` most (>=2)."""
    try:
        subprocess.run(["fpocket", "-f", pdb_path], check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"  fpocket failed on {os.path.basename(pdb_path)}: {e}", file=sys.stderr, flush=True)
        return None, None, 0, 0
    import glob
    import re
    stem = pdb_path[:-4] if pdb_path.endswith(".pdb") else pdb_path
    out_dir, base = stem + "_out", os.path.basename(stem)
    info_path = os.path.join(out_dir, base + "_info.txt")
    if not os.path.exists(info_path):
        return None, None, 0, 0
    info = fl.parse_info(_read(info_path))
    out_pdb = os.path.join(out_dir, base + "_out.pdb")
    out_coords = fl.out_pdb_sphere_coords(_read(out_pdb)) if os.path.exists(out_pdb) else {}
    file_res, counts, coords = {}, {}, {}
    for f in glob.glob(os.path.join(out_dir, "pockets", "pocket*_atm.pdb")):
        fidx = int(re.search(r"pocket(\d+)_atm", f).group(1))
        file_res[fidx] = fl.parse_atm_residues(_read(f))
        vert = os.path.join(out_dir, "pockets", f"pocket{fidx}_vert.pqr")
        vtext = _read(vert) if os.path.exists(vert) else ""
        coords[fidx] = fl.pqr_sphere_coords(vtext)
        counts[fidx] = fl.count_pqr_spheres(vtext)
    mapping = fl.map_files_to_pockets(info, counts, coords, out_coords)
    tset = set(target_resnums)
    max_drug = max((info[n]["druggability"] or 0.0) for n in info) if info else None
    best_num, best_overlap = None, 0
    for fidx, num in mapping.items():
        overlap = len(set(file_res[fidx]) & tset)
        if overlap > best_overlap:
            best_num, best_overlap = num, overlap
    drug = info[best_num]["druggability"] if (best_num is not None and best_overlap >= 2) else None
    return drug, max_drug, best_overlap, len(info)


def _read(path):
    with open(path) as fh:
        return fh.read()


def _stats(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return {"n": 0}
    v.sort()
    n = len(v)
    med = v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
    return {"n": n, "min": round(v[0], 3), "median": round(med, 3), "max": round(v[-1], 3),
            "mean": round(sum(v) / n, 3)}


def main():
    from Bio.PDB import PDBParser
    os.makedirs(WORK, exist_ok=True)
    result = {
        "_title": "AF2 NR4A3 LBD model vs experimental PDB 8XTT (solution-NMR ensemble) — cross-check",
        "_control": {
            "pdb": PDB_ID, "method": "solution NMR", "entity": "NR4A3 / NOR-1 ligand-binding domain",
            "deposited": "2024-01-11", "released": "2025-01-15", "doi": "10.2210/pdb8XTT/pdb",
            "role": "primary experimental structural control for the LBD fold",
        },
        "_scope": ("8XTT is a resting-state ensemble of the isolated apo LBD: it tests the AF2 STARTING "
                   "fold (Q1) and whether the RESTING orthosteric pocket is borderline/closed (Q2), and "
                   "confirms the selectivity handles are experimentally resolved (Q3). It does NOT contain "
                   "the designed warhead and does NOT populate the metadynamics-opened induced-fit cavity, "
                   "so it neither confirms nor refutes the OPENED pocket, the docked pose, or the ABFE "
                   "selectivity — those still need a ligand-bound experimental structure."),
        "uniprot": UNIPROT, "lbd_window": [LBD_FIRST, LBD_LAST],
        "pocket5": POCKET5, "handles": HANDLES,
    }
    try:
        # --- structures ---
        af2_full = os.path.join(WORK, f"AF-{UNIPROT}.pdb")
        af2_lbd = os.path.join(WORK, "nr4a3_af2_lbd.pdb")
        fetch_afdb(UNIPROT, af2_full)
        _trim_lbd(af2_full, af2_lbd)
        xtt_pdb = os.path.join(WORK, f"{PDB_ID}.pdb")
        fetch_rcsb(PDB_ID, xtt_pdb)

        parser = PDBParser(QUIET=True)
        af2_struct = parser.get_structure("af2", af2_lbd)
        xtt_struct = parser.get_structure("xtt", xtt_pdb)
        af2_model0 = next(af2_struct.get_models())
        xtt_models = list(xtt_struct.get_models())
        af2_chain = pick_chain(af2_model0)
        xtt_chain = pick_chain(xtt_models[0])
        result["n_nmr_models"] = len(xtt_models)
        result["af2_chain"], result["xtt_chain"] = af2_chain, xtt_chain

        # --- alignment / numbering map ---
        af2_res = main_chain_residues(af2_model0, af2_chain)
        xtt_res = main_chain_residues(xtt_models[0], xtt_chain)
        corr, identity, coverage = align_map(af2_res, xtt_res)
        af2_to_xtt = {a: b for a, b, _ in corr}
        result["alignment"] = {
            "af2_lbd_residues": len(af2_res),
            "xtt_residues": len(xtt_res),
            "xtt_resSeq_span": [xtt_res[0][0], xtt_res[-1][0]] if xtt_res else None,
            "aligned_columns": len(corr),
            "sequence_identity_over_aligned": identity,
            "af2_lbd_coverage_by_xtt": coverage,
            "numbering_note": ("8XTT author resSeq is mapped to Q92570 numbering by this alignment; "
                               "high identity confirms same protein/region. If identity is low the rest "
                               "of the cross-check should be treated with caution."),
        }
        print(f"  alignment: {len(corr)} cols, identity {identity}, coverage {coverage}, "
              f"8XTT span {result['alignment']['xtt_resSeq_span']}", flush=True)

        # matched Cα pairs present in every model
        af2_ca = af2_ca_coords(af2_lbd)
        matched = [(a, b) for a, b in ((x[0], x[1]) for x in corr)
                   if a in af2_ca and all(b in ca_coords(m, xtt_chain) for m in xtt_models)]
        matched.sort(key=lambda p: p[0])
        result["matched_ca_pairs"] = len(matched)
        if len(matched) < 10:
            raise RuntimeError(f"only {len(matched)} matched Cα pairs — alignment/parse problem")

        # --- Q1: per-model backbone RMSD (all matched) + core RMSD ---
        af2_all = np.array([af2_ca[a] for a, _ in matched])
        model_ca = [ {b: ca_coords(m, xtt_chain)[b] for _, b in matched} for m in xtt_models ]
        full_rms, transformed = [], []
        for mc in model_ca:
            mov = np.array([mc[b] for _, b in matched])
            rms, rot, tran = superpose(af2_all, mov)
            full_rms.append(rms)
            transformed.append(np.dot(mov, rot) + tran)
        transformed = np.stack(transformed)                       # (n_models, n_matched, 3)
        mean_pos = transformed.mean(axis=0)
        rmsf = np.sqrt(((transformed - mean_pos) ** 2).sum(axis=2).mean(axis=0))   # per matched residue

        keep = [i for i in range(len(matched))
                if rmsf[i] <= CORE_RMSF_CUTOFF_A and CORE_TRIM_ENDS <= i < len(matched) - CORE_TRIM_ENDS]
        core_rms = []
        if len(keep) >= 10:
            af2_core = af2_all[keep]
            for mc in model_ca:
                mov = np.array([mc[matched[i][1]] for i in keep])
                core_rms.append(superpose(af2_core, mov)[0])
        result["q1_backbone_rmsd_to_af2"] = {
            "all_matched_ca": _stats(full_rms),
            "core_ca": _stats(core_rms),
            "n_core_residues": len(keep),
            "core_definition": f"matched Cα with cross-ensemble RMSF<= {CORE_RMSF_CUTOFF_A} Å, "
                               f"excluding {CORE_TRIM_ENDS} residues at each terminus",
            "flexible_residues_q92570": sorted(matched[i][0] for i in range(len(matched))
                                               if i not in keep)[:40],
            "_interpretation": ("Low core RMSD => the AF2 starting fold matches the experimental LBD, so "
                                "the model that seeds all downstream MD is experimentally supported. High "
                                "all-matched vs low core RMSD is the expected NMR signature (flexible "
                                "termini/loops), not a fold disagreement."),
        }
        print(f"  Q1 RMSD all={_stats(full_rms)} core={_stats(core_rms)} (core n={len(keep)})", flush=True)

        # --- Q2: fpocket at Pocket-5, AF2 (same build) + per NMR model ---
        pocket5_xtt = sorted(af2_to_xtt[r] for r in POCKET5 if r in af2_to_xtt)
        af2_drug, af2_max, af2_ov, af2_np = fpocket_at(af2_lbd, POCKET5)
        model_drugs, model_maxes = [], []
        for i, m in enumerate(xtt_models):
            mp = os.path.join(WORK, f"xtt_model_{i + 1}.pdb")
            write_model_pdb(m, xtt_chain, mp)
            d, mx, ov, npk = fpocket_at(mp, pocket5_xtt)
            model_drugs.append(d)
            model_maxes.append(mx)
        n_detected = sum(1 for d in model_drugs if d is not None)
        result["q2_fpocket_pocket5"] = {
            "af2_static_reference_literature": 0.495,
            "af2_static_this_job": {"druggability": af2_drug, "max_anywhere": af2_max,
                                    "pocket5_overlap": af2_ov, "n_pockets": af2_np},
            "pocket5_resnums_in_8xtt": pocket5_xtt,
            "nmr_ensemble_pocket5_druggability": _stats(model_drugs),
            "nmr_ensemble_max_anywhere": _stats(model_maxes),
            "n_models_with_pocket5_detected": n_detected,
            "n_models": len(xtt_models),
            "metad_opened_peak_for_context": 0.931,
            "_interpretation": ("If the experimental resting ensemble scores at/below the AF2 static "
                                "0.495 (and the pocket is often not even detected), that CORROBORATES the "
                                "'static orthosteric pocket is borderline/occluded' claim from an "
                                "experimental structure — strengthening, not weakening, the cryptic-pocket "
                                "rationale. It does NOT probe the metadynamics-opened state (0.931), which "
                                "no apo ensemble can populate on demand."),
        }
        print(f"  Q2 AF2-in-job druggability={af2_drug} (max {af2_max}); NMR Pocket-5 "
              f"{_stats(model_drugs)}; detected in {n_detected}/{len(xtt_models)}", flush=True)

        # --- Q3: selectivity handles in the experimental structure ---
        xtt_seq = {r[0]: r[1] for r in xtt_res}
        af2_seq = {r[0]: r[1] for r in af2_res}
        handles = {}
        for h in HANDLES:
            xh = af2_to_xtt.get(h)
            handles[str(h)] = {
                "resolved_in_8xtt": xh is not None,
                "xtt_resSeq": xh,
                "af2_aa": af2_seq.get(h),
                "xtt_aa": xtt_seq.get(xh) if xh is not None else None,
                "identical": (xh is not None and af2_seq.get(h) == xtt_seq.get(xh)),
            }
        result["q3_selectivity_handles"] = {
            "handles": handles,
            "n_resolved": sum(1 for v in handles.values() if v["resolved_in_8xtt"]),
            "n_total": len(HANDLES),
            "_interpretation": ("Handles resolved with matching identity in 8XTT are experimentally real "
                                "residues at the expected positions — the selectivity argument rests on "
                                "residues that exist in the experimental structure, not only in the model."),
        }
        print(f"  Q3 handles resolved {result['q3_selectivity_handles']['n_resolved']}/{len(HANDLES)}",
              flush=True)

        result["_ok"] = True
    except Exception as e:  # noqa: BLE001 — record the failure, still write partial JSON
        import traceback
        result["_ok"] = False
        result["_error"] = str(e)[:500]
        result["_traceback"] = traceback.format_exc()[-1500:]
        print("  ERROR:", e, file=sys.stderr, flush=True)

    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2)
    print("wrote", OUT, flush=True)
    # compact summary to the log (streamed to the dispatch workflow via wait=True/logs=True)
    for k in ("alignment", "q1_backbone_rmsd_to_af2", "q2_fpocket_pocket5", "q3_selectivity_handles"):
        if k in result:
            print(f"\n== {k} ==\n{json.dumps(result[k], indent=2)}", flush=True)
    if not result.get("_ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
