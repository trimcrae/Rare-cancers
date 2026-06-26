#!/usr/bin/env python3
"""
NR4A family-wide selectivity MATRIX (state-matched).

Docks one candidate library into the metad-OPENED conformer of **NR4A3, NR4A1 AND NR4A2** — each
paralogue's OWN opened pocket (extracted from its `*-metad` trajectory), not a static off-target model —
and classifies every candidate's selectivity fingerprint across the family
(`selectivity_fingerprint.classify`): NR4A3-only (EMC/AciCC lead) / pan-NR4A (ex-vivo immuno) /
NR4A1+NR4A3 (AML anti-target) / ...

WHY state-matched: docking opened-NR4A3 vs *static* NR4A1/2 (what `nr4a3_warhead.py` did) biases toward
false selectivity because the paralogue pockets are likely cryptic too (de Vera 2019; Nur77 MD). Using
each paralogue's own metad-opened pocket removes that confound — the answer to "how do you know it won't
bind the paralogue without MD on it?". Docking dG remain **screening priors, not affinities**; cells are
triage hypotheses to be quantified by MM-GBSA (per-residue) and selectivity FEP.

Inputs — one ProcessingInput dir per paralogue under INPUT_DIR, each a `*-metad` output set
(`nr4a3-lbd-solvated.pdb` + `nr4a3-lbd-metad.dcd` + `metad_manifest.json` carrying that target's
`cv_residues` / `lbd_first`):  <INPUT_DIR>/nr4a3,  <INPUT_DIR>/nr4a1,  <INPUT_DIR>/nr4a2.
Output (OUTPUT_DIR): nr4a3-matrix.json (per-candidate fingerprints + cell census + leads) + the opened
conformer PDBs and pose SDFs.
"""
import json
import os
import sys

import nr4a3_dock as dock
import nr4a3_warhead as wh           # reuse the proven extract/dock/contact helpers
import selectivity_fingerprint as sf
import residue_map as rm

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
wh.OUT = OUT                          # warhead.dock_into / handle_contacts write pose SDFs into OUT

PARALOGUES = ["nr4a3", "nr4a1", "nr4a2"]
KEY = {"nr4a3": "NR4A3", "nr4a1": "NR4A1", "nr4a2": "NR4A2"}
ENGAGEABLE_HANDLES = [406, 410, 484, 531, 534]   # divergent + pocket-facing (NR4A3 numbering)
CONSERVED_CV = [411, 481, 485]                    # Pocket-5 CV residues that are NOT divergent handles
LBD_FIRST_NR4A3 = 373


def read_manifest(input_dir):
    """cv_residues + lbd_first from a paralogue's metad manifest (written by nr4a3_metad.py)."""
    p = os.path.join(input_dir, "metad_manifest.json")
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        m = json.load(fh)
    return {"cv_residues": m.get("cv_residues"), "lbd_first": m.get("lbd_first", LBD_FIRST_NR4A3),
            "target": m.get("target")}


def box_for(conformer_pdb, resseqs, cv_residues, lbd_first):
    """Box center on the CV (pocket-lining) residues, resolved onto the opened conformer's numbering."""
    pos, _ = rm.resolve_positions(resseqs, cv_residues, lbd_first)
    box_res = [resseqs[i] for i in pos]
    if not box_res:
        raise RuntimeError("no CV residues resolved onto the opened conformer for boxing")
    center, _ = wh.pocket_box(conformer_pdb, box_res)
    return center


def main():
    res = {"_note": "NR4A family selectivity matrix: one library docked into the metad-OPENED pocket of "
                    "NR4A3/NR4A1/NR4A2 (state-matched). Cells (selectivity_fingerprint) are triage "
                    "hypotheses from docking priors, NOT affinities; quantify with MM-GBSA/FEP.",
           "engageable_handles": ENGAGEABLE_HANDLES, "paralogues": {}}
    os.makedirs(OUT, exist_ok=True)

    # 1) candidate library (real ChEMBL matter), deduplicated by ChEMBL id + label.
    ligands, seen = [], set()
    for nm in dock.LIGAND_NAMES:
        hit = dock.chembl_smiles_by_name(nm)
        if hit and (nm, hit[0]) not in seen:
            ligands.append((nm, hit[0], hit[1])); seen.add((nm, hit[0]))
    for label, cid, smi in dock.chembl_nr4a3_actives():
        if (label, cid) not in seen:
            ligands.append((label, cid, smi)); seen.add((label, cid))
    if not ligands:
        res["_status"] = "no candidate ligands resolved"
        _write(res); return
    sdf = os.path.join(OUT, "candidates.sdf")
    kept = dock.make_sdf(ligands, sdf)
    res["n_candidates"] = len(kept)

    # 2) per paralogue: extract its opened conformer, box on its own CV, dock the library.
    per = {}
    for tag in PARALOGUES:
        d = os.path.join(IN, tag)
        if not os.path.isdir(d):
            res.setdefault("_warnings", []).append(f"missing input dir {d} ({KEY[tag]} skipped)")
            continue
        man = read_manifest(d)
        if not man or not man.get("cv_residues"):
            res.setdefault("_warnings", []).append(f"missing/empty manifest in {d} ({KEY[tag]} skipped)")
            continue
        wh.IN = d                                   # warhead.extract_opened_conformer reads from wh.IN
        conf = os.path.join(OUT, f"{tag}-opened.pdb")
        try:
            rec, frame, drug, resseqs = wh.extract_opened_conformer(conf)
            center = box_for(rec, resseqs, man["cv_residues"], man["lbd_first"])
            scores, pose = wh.dock_into(rec, center, sdf, tag)
        except Exception as e:  # noqa: BLE001 — record + continue; a missing paralogue just leaves None
            res.setdefault("_warnings", []).append(f"{KEY[tag]} dock failed: {e}")
            continue
        per[tag] = {"conformer": rec, "resseqs": resseqs, "scores": scores, "pose": pose,
                    "manifest": man}
        res["paralogues"][KEY[tag]] = {"opened_frame": frame, "fpocket_druggability": round(drug, 3),
                                       "cv_residues": man["cv_residues"], "n_docked": len(scores)}

    if "nr4a3" not in per:
        res["_status"] = "NR4A3 opened conformer/dock unavailable — cannot build the matrix"
        _write(res); return

    # 3) NR4A3-pose contact scores: divergent engageable handles (selective signal) + conserved CV (pan).
    n3 = per["nr4a3"]
    h_res = [n3["resseqs"][i] for i in rm.resolve_positions(n3["resseqs"], ENGAGEABLE_HANDLES,
                                                            LBD_FIRST_NR4A3)[0]]
    c_res = [n3["resseqs"][i] for i in rm.resolve_positions(n3["resseqs"], CONSERVED_CV,
                                                            LBD_FIRST_NR4A3)[0]]
    handle_contacts = wh.handle_contacts(n3["conformer"], n3["pose"], h_res) if h_res else {}
    conserved_contacts = wh.handle_contacts(n3["conformer"], n3["pose"], c_res) if c_res else {}

    # 4) classify every candidate by its three opened-pocket scores.
    rows = []
    for label, cid, smi in kept:
        dg = {t: per[t]["scores"].get(label) if t in per else None for t in PARALOGUES}
        fp = sf.classify(dg["nr4a3"], dg["nr4a1"], dg["nr4a2"])
        fp.update({"label": label, "chembl_id": cid,
                   "handle_contacts": handle_contacts.get(label, 0),
                   "conserved_contacts": conserved_contacts.get(label, 0)})
        rows.append(fp)
    # rank: NR4A3-selective leads first (by margin, then NR4A3 potency, then handle engagement)
    rows.sort(key=lambda r: (not r["nr4a3_selective"],
                             -((r["margin_vs_NR4A1"] or -99) + (r["margin_vs_NR4A2"] or -99)),
                             (r["dG"]["NR4A3"] if r["dG"]["NR4A3"] is not None else 0),
                             -r["handle_contacts"]))
    res["candidates"] = rows
    res["matrix"] = {k: v for k, v in sf.matrix_summary(rows).items() if k == "cell_census"}
    res["leads"] = {
        "nr4a3_selective": [r["label"] for r in rows if r["nr4a3_selective"]],
        "pan_nr4a": [r["label"] for r in rows if r["pan_nr4a"]],
        "anti_targets": [r["label"] for r in rows if r["anti_target"]],
    }
    res["_status"] = "ok"
    _write(res)
    print(json.dumps({"cell_census": res["matrix"]["cell_census"], "leads": res["leads"],
                      "n_candidates": res.get("n_candidates")}, indent=2), flush=True)


def _write(res):
    with open(os.path.join(OUT, "nr4a3-matrix.json"), "w") as fh:
        json.dump(res, fh, indent=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        import traceback
        with open(os.path.join(OUT, "nr4a3-matrix.json"), "w") as fh:
            json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                      fh, indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(0)
