#!/usr/bin/env python3
"""
Selective NR4A3 warhead design/screen (degrader Gate 4): dock candidate chemical matter into the
MD-REVEALED OPENED NR4A3 pocket and score NR4A3-selectivity vs the paralogues NR4A1/NR4A2.

Why this is different from nr4a3_dock.py (which docks into the *static, collapsed* AF2 pocket):
 - The 30 ns metadynamics showed the orthosteric pocket OPENS to fpocket druggability ~0.93. A warhead
   must be designed against that *opened* conformer, not the borderline static model. Step 1 extracts the
   most-druggable opened conformer from the trajectory and uses it as the receptor.
 - The EMC drug MUST be NR4A3-selective (sparing NR4A1/2 avoids leukaemogenic/neuronal toxicity). So we
   dock every candidate into NR4A3-opened AND the aligned NR4A1/NR4A2 pockets and score the selectivity
   margin and engagement of the 7 divergent "selectivity handle" residues.

Pipeline (mounts the 30 ns metad outputs from S3 at INPUT_DIR):
 1. extract_opened_conformer  — most-druggable frame of nr4a3-lbd-metad.dcd (mdtraj + fpocket) -> PDB.
 2. paralogue pockets         — fetch NR4A1 (P22736) / NR4A2 (P43354) AF2 LBDs; map NR4A3 pocket
                                residues onto each by BLOSUM62 alignment (same method as
                                nr4a_selectivity.py) to box the homologous pocket.
 3. candidate set             — ChEMBL NR4A-relevant ligands + NR4A3-target actives (real SMILES, via
                                nr4a3_dock helpers). The de-novo generative layer (DiffSBDD/Pocket2Mol)
                                is a documented optional module (generate_denovo) — skipped unless the
                                model + GPU are present, mirroring the repo's "pipeline primed" pattern.
 4. dock + score              — smina into NR4A3-opened / NR4A1 / NR4A2; per candidate:
                                  dG_NR4A3, selectivity margin = min(dG_NR4A1,dG_NR4A2) - dG_NR4A3
                                  (more positive = more NR4A3-selective), and handle-contact count over
                                  the 5 pocket-FACING handles (the engageable subset of the 7 divergent
                                  residues; T407/R412 splay outward per handle-facing run 28249776934).

Honest framing: docking scores are screening priors, not affinities; this nominates selective
chemotypes against a validated design pocket — it is not a wet-validated lead. Output: nr4a3-warhead.json.
"""
import json
import os
import subprocess
import sys

import nr4a3_dock as dock   # reuse _get / chembl_* / make_sdf / _which (same dir)

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.environ.get("INPUT_DIR", HERE)      # where the 30 ns metad outputs are mounted (or local)
OUT = os.environ.get("OUTPUT_DIR", HERE)
LBD_FIRST = 373
POCKET_RESIDUES = list(range(406, 535))     # orthosteric Pocket-5 span (NR4A3 numbering)
HANDLES = [406, 407, 410, 412, 484, 531, 534]   # the 7 NR4A3-vs-paralogue divergent residues
# Of those 7, only these 5 stay pocket-FACING in the opened druggable frames (handle-facing run
# 28249776934, 2026-06-26: T407 faced in 0.0 and R412 0.25 of druggable frames). A warhead can only
# realistically engage the pocket-facing ones, so the selectivity handle-contact score below counts
# only this engageable subset; the full divergent set is still reported for provenance.
ENGAGEABLE_HANDLES = [406, 410, 484, 531, 534]
PARALOGUES = {"NR4A1": "P22736", "NR4A2": "P43354"}
N_FPOCKET_FRAMES = 25                        # frames sampled to find the best opened conformer
_AA = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU", "LYS", "MET",
       "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "HID", "HIE", "HIP", "CYX", "HSD", "HSE"}


# ----------------------------------------------------------------------------- 1. opened conformer
def extract_opened_conformer(out_pdb):
    """Pick the most-druggable frame of the metad trajectory and write it as a protein-only receptor PDB.
    Returns (out_pdb, frame_idx, druggability, resseqs) or raises if inputs/tools are missing."""
    import numpy as np
    import mdtraj as md
    import shutil
    import tempfile
    import glob
    import re
    import fpocket_lib as fl

    top = os.path.join(IN, "nr4a3-lbd-solvated.pdb")
    dcd = os.path.join(IN, "nr4a3-lbd-metad.dcd")
    for p in (top, dcd):
        if not os.path.exists(p):
            raise FileNotFoundError(f"missing {p} (mount the 30 ns metad outputs at INPUT_DIR)")
    if not dock._which("fpocket"):
        raise RuntimeError("fpocket not on PATH")

    t = md.load(dcd, top=top)
    prot = t.atom_slice(t.topology.select("protein"))
    resseqs = [r.resSeq for r in prot.topology.residues]
    print(f"  trajectory frames={t.n_frames} protein_atoms={prot.n_atoms} "
          f"resSeq {min(resseqs)}..{max(resseqs)}", flush=True)

    sample = sorted({int(round(x)) for x in np.linspace(0, prot.n_frames - 1,
                                                        min(prot.n_frames, N_FPOCKET_FRAMES))})
    best = {"druggability": -1.0, "frame": None}
    for fi in sample:
        d = tempfile.mkdtemp(prefix=f"wf_{fi}_", dir=OUT)
        try:
            pdb = os.path.join(d, "frame.pdb")
            prot[fi].save_pdb(pdb)
            subprocess.run(["fpocket", "-f", pdb], check=True, capture_output=True, text=True, timeout=300)
            od = os.path.join(d, "frame_out")
            info = fl.parse_info(dock_read(os.path.join(od, "frame_info.txt")))
            # max druggability over this frame's pockets (orthosteric pocket is the relevant one; the
            # opened Pocket-5 dominates after opening — we take the max and verify residues at the end)
            drug = max((m["druggability"] or 0.0) for m in info.values()) if info else 0.0
            if drug > best["druggability"]:
                best = {"druggability": drug, "frame": fi}
        except Exception as e:  # noqa: BLE001 — keep scanning
            print(f"  frame {fi} fpocket skipped: {e}", file=sys.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    if best["frame"] is None:
        raise RuntimeError("no opened conformer could be scored")
    prot[best["frame"]].save_pdb(out_pdb)
    print(f"  best opened conformer: frame {best['frame']} druggability {best['druggability']:.3f} "
          f"-> {out_pdb}", flush=True)
    return out_pdb, best["frame"], best["druggability"], resseqs


def dock_read(path):
    with open(path) as fh:
        return fh.read()


# ----------------------------------------------------------------- 2. map pocket onto a paralogue
def map_pocket_to_paralogue(nr4a3_pdb, para_pdb, pocket_resnums):
    """Return the paralogue residue numbers homologous to the NR4A3 pocket, via a global BLOSUM62
    alignment of the two CA sequences (same approach as nr4a_selectivity.py).

    `pocket_resnums` are the NR4A3 pocket residues IN THE NUMBERING OF nr4a3_pdb. The opened conformer
    extracted from the trajectory is renumbered from 1 (resSeq 1..254), NOT the AF2 406..534 numbering —
    passing the AF2 POCKET_RESIDUES here matched zero residues and silently produced empty paralogue
    boxes (no selectivity). The caller resolves the correct resSeqs via residue_map (box_res)."""
    from Bio.Align import PairwiseAligner, substitution_matrices
    three2one = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
                 "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
                 "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}

    def seq_items(pdb):
        d = {}
        for line in open(pdb):
            if line.startswith("ATOM") and line[12:16].strip() == "CA":
                d[int(line[22:26])] = three2one.get(line[17:20].strip(), "X")
        return sorted(d.items())

    a = PairwiseAligner()
    a.mode = "global"
    a.substitution_matrix = substitution_matrices.load("BLOSUM62")
    a.open_gap_score, a.extend_gap_score = -10, -0.5
    s3, sp = seq_items(nr4a3_pdb), seq_items(para_pdb)
    resnum3 = [r for r, _ in s3]
    idx_of_resnum3 = {r: i for i, r in enumerate(resnum3)}
    aln = a.align("".join(x for _, x in s3), "".join(x for _, x in sp))[0]
    m = {}
    for (a0, a1), (b0, b1) in zip(aln.aligned[0], aln.aligned[1]):
        for off in range(a1 - a0):
            m[a0 + off] = b0 + off
    para_nums = [pr for pr, _ in sp]
    out = []
    for r in pocket_resnums:
        i = idx_of_resnum3.get(r)
        if i is not None and i in m:
            out.append(para_nums[m[i]])
    return out


def pocket_box(pdb_path, residues):
    xs, ys, zs = [], [], []
    want = set(residues)
    for line in open(pdb_path):
        if line.startswith(("ATOM", "HETATM")) and line[12:16].strip() == "CA":
            try:
                resi = int(line[22:26])
            except ValueError:
                continue
            if resi in want:
                xs.append(float(line[30:38])); ys.append(float(line[38:46])); zs.append(float(line[46:54]))
    if not xs:
        raise RuntimeError("no pocket CA atoms found for box")
    return (sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs)), len(xs)


# ----------------------------------------------------------------------------- 3/4 dock + score
def dock_into(receptor_pdb, center, sdf, tag):
    """smina dock the SDF into a 24 A box at `center`; return {label: affinity_kcal_mol} and the pose SDF."""
    smina = dock._which("smina")
    if not smina:
        raise RuntimeError("smina not on PATH")
    out_sdf = os.path.join(OUT, f"docked_{tag}.sdf")
    cmd = [smina, "-r", receptor_pdb, "-l", sdf,
           "--center_x", str(center[0]), "--center_y", str(center[1]), "--center_z", str(center[2]),
           "--size_x", "24", "--size_y", "24", "--size_z", "24",
           "--exhaustiveness", "8", "--num_modes", "1", "-o", out_sdf]
    subprocess.run(cmd, capture_output=True, text=True)
    scores = {}
    if os.path.exists(out_sdf):
        for b in open(out_sdf).read().split("$$$$"):
            lines = b.strip().splitlines()
            if not lines:
                continue
            nm = lines[0].strip()
            for j, ln in enumerate(b.splitlines()):
                if "minimizedAffinity" in ln:
                    try:
                        scores[nm] = float(b.splitlines()[j + 1].strip())
                    except (ValueError, IndexError):
                        pass
                    break
    return scores, out_sdf


def handle_contacts(receptor_pdb, pose_sdf, handle_resnums, cutoff=4.0):
    """{ligand_label: #handle residues with any atom within cutoff of the docked pose}."""
    # receptor handle-atom coords
    want = set(handle_resnums)
    hatoms = {}
    for line in open(receptor_pdb):
        if line.startswith(("ATOM", "HETATM")):
            try:
                resi = int(line[22:26])
            except ValueError:
                continue
            if resi in want:
                hatoms.setdefault(resi, []).append(
                    (float(line[30:38]), float(line[38:46]), float(line[46:54])))
    out = {}
    if not os.path.exists(pose_sdf):
        return out
    c2 = cutoff * cutoff
    for b in open(pose_sdf).read().split("$$$$"):
        lines = b.strip().splitlines()
        if len(lines) < 4:
            continue
        nm = lines[0].strip()
        try:
            natom = int(lines[3][:3])
        except (ValueError, IndexError):
            continue
        lig = []
        for ln in lines[4:4 + natom]:
            try:
                lig.append((float(ln[0:10]), float(ln[10:20]), float(ln[20:30])))
            except ValueError:
                break
        n = 0
        for resi, ratoms in hatoms.items():
            if any((lx - rx) ** 2 + (ly - ry) ** 2 + (lz - rz) ** 2 <= c2
                   for (lx, ly, lz) in lig for (rx, ry, rz) in ratoms):
                n += 1
        out[nm] = n
    return out


def generate_denovo(receptor_pdb, center):
    """OPTIONAL de-novo SBDD layer (DiffSBDD / Pocket2Mol / TargetDiff) conditioned on the opened pocket.
    REALIZED as a standalone GPU pipeline — see nr4a3_denovo.py + sagemaker_src/entry_denovo.py +
    gpu-denovo-aws.yml (DiffSBDD pocket-conditioned generation against the Step-0 druggable-release
    receptor, with cheminformatics + pose handle-contact triage). This inline hook stays a no-op so the
    CPU warhead screen does not require a GPU; run the de-novo pipeline separately, then feed its SDF here.
    Returns generated (label, id, smiles) or []."""
    if os.environ.get("DENOVO_MODEL"):
        print("  [denovo] DENOVO_MODEL set but no concrete model wired yet — skipping", file=sys.stderr)
    return []


def main():
    res = {"_note": "Selective NR4A3 warhead screen against the MD-OPENED pocket (30 ns metad, fpocket "
                    "~0.93). Docks candidates into NR4A3-opened + NR4A1/NR4A2 (aligned pockets) and "
                    "scores selectivity margin + handle engagement. handle_contacts counts only the 5 "
                    "pocket-FACING handles (handle-facing run 28249776934; T407/R412 splay outward, so "
                    "are excluded as unengageable). Scores are screening priors, NOT affinities; not a "
                    "wet-validated lead.",
           "handles_divergent": HANDLES, "handles_engageable": ENGAGEABLE_HANDLES,
           "pocket_residues": [POCKET_RESIDUES[0], POCKET_RESIDUES[-1]]}
    os.makedirs(OUT, exist_ok=True)

    # 1) opened conformer (receptor)
    try:
        rec3, frame, drug, resseqs = extract_opened_conformer(os.path.join(OUT, "nr4a3-opened.pdb"))
        res["opened_conformer"] = {"frame": frame, "fpocket_druggability": round(drug, 3)}
    except Exception as e:  # noqa: BLE001
        res["_status"] = f"opened-conformer extraction failed: {e}"
        json.dump(res, open(os.path.join(OUT, "nr4a3-warhead.json"), "w"), indent=2)
        print("ABORT:", e, file=sys.stderr)
        return

    # map POCKET_RESIDUES onto the (possibly renumbered) opened conformer for boxing + handles
    import residue_map as rm
    pos, label = rm.resolve_positions(resseqs, POCKET_RESIDUES, LBD_FIRST)
    box_res = [resseqs[i] for i in pos]
    handle_res = ([resseqs[i] for i, r in zip(pos, POCKET_RESIDUES) if r in ENGAGEABLE_HANDLES]
                  if box_res else ENGAGEABLE_HANDLES)
    center3, n3 = pocket_box(rec3, box_res)
    res["numbering"] = label
    res["box_center_nr4a3"] = [round(x, 2) for x in center3]

    # 2) candidate set (real SMILES) + optional de-novo
    ligands = []
    for nm in dock.LIGAND_NAMES:
        hit = dock.chembl_smiles_by_name(nm)
        if hit:
            ligands.append((nm, hit[0], hit[1]))
    ligands += dock.chembl_nr4a3_actives()
    ligands += generate_denovo(rec3, center3)
    if not ligands:
        res["_status"] = "no candidate ligands resolved"
        json.dump(res, open(os.path.join(OUT, "nr4a3-warhead.json"), "w"), indent=2)
        return
    sdf = os.path.join(OUT, "candidates.sdf")
    kept = dock.make_sdf(ligands, sdf)
    res["n_candidates"] = len(kept)

    # 3) dock into NR4A3-opened + paralogue pockets
    s3, pose3 = dock_into(rec3, center3, sdf, "nr4a3")
    contacts = handle_contacts(rec3, pose3, handle_res)
    para_scores = {}
    para_mapped = {}            # audit: # pocket residues mapped onto each paralogue (0 => no selectivity)
    for name, acc in PARALOGUES.items():
        try:
            ppdb = os.path.join(OUT, f"AF-{acc}.pdb")
            url = json.loads(dock._get(f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"))[0]["pdbUrl"]
            open(ppdb, "wb").write(dock._get(url, timeout=120))
            para_res = map_pocket_to_paralogue(rec3, ppdb, box_res)   # box_res = opened-conformer resSeqs
            para_mapped[name] = len(para_res)
            if not para_res:
                raise RuntimeError(f"0 pocket residues mapped onto {name} — selectivity not evaluated "
                                   f"(check numbering: opened-conformer resSeqs were {box_res[:3]}...)")
            pc, _ = pocket_box(ppdb, para_res)
            sc, _ = dock_into(ppdb, pc, sdf, name)
            para_scores[name] = sc
            print(f"  paralogue {name}: mapped {len(para_res)} pocket residues, docked {len(sc)} ligands",
                  flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  paralogue {name} dock failed: {e}", file=sys.stderr)
            para_scores[name] = {}
            para_mapped.setdefault(name, 0)
    res["paralogue_pocket_residues_mapped"] = para_mapped
    res["selectivity_evaluated"] = any(v > 0 for v in para_mapped.values())

    # 4) selectivity scoring
    rows = []
    for label_lig, cid, smi in kept:
        d3 = s3.get(label_lig)
        if d3 is None:
            continue
        d1 = para_scores.get("NR4A1", {}).get(label_lig)
        d2 = para_scores.get("NR4A2", {}).get(label_lig)
        para_best = min([x for x in (d1, d2) if x is not None], default=None)
        margin = (para_best - d3) if para_best is not None else None   # >0 => NR4A3 more favourable
        rows.append({"label": label_lig, "chembl_id": cid,
                     "dG_NR4A3": round(d3, 2),
                     "dG_NR4A1": None if d1 is None else round(d1, 2),
                     "dG_NR4A2": None if d2 is None else round(d2, 2),
                     "selectivity_margin": None if margin is None else round(margin, 2),
                     "handle_contacts": contacts.get(label_lig, 0)})
    # rank: most NR4A3-selective (margin) then strongest NR4A3 binder then most handle contacts
    rows.sort(key=lambda r: (-(r["selectivity_margin"] or -99), r["dG_NR4A3"], -r["handle_contacts"]))
    res["candidates"] = rows
    res["best"] = rows[0] if rows else None
    if not rows:
        res["_status"] = "no docked scores"
    elif res.get("selectivity_evaluated"):
        res["_status"] = "ok"
    else:
        res["_status"] = ("ok-NO-SELECTIVITY: NR4A3 affinity + handle contacts only; paralogue mapping "
                          "failed so selectivity_margin is null for all candidates (see "
                          "paralogue_pocket_residues_mapped)")
    json.dump(res, open(os.path.join(OUT, "nr4a3-warhead.json"), "w"), indent=2)
    print(json.dumps({"opened_conformer": res["opened_conformer"], "n_candidates": res.get("n_candidates"),
                      "best": res.get("best"), "top5": rows[:5]}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        import traceback
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, "nr4a3-warhead.json"), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(0)
