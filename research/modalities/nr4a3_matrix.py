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

# DE-NOVO FUNNEL MODE (env-guarded; default = original ChEMBL-library / metad-NR4A3 behaviour):
#  - CANDIDATE_JSON: path to nr4a3-denovo.json -> library = top TOP_N de-novo candidates by denovo_promise.
#  - NR4A3_RECEPTOR: path to the Step-0 druggable-release receptor PDB -> dock NR4A3 into THAT (the
#    thermally-real conformation the candidates were designed against), not the biased-metad conformer.
#    Box residues come from NR4A3_BOX_RES (comma resSeqs), else the Step-0 manifest, else Pocket-5.
CANDIDATE_JSON = os.environ.get("CANDIDATE_JSON")
TOP_N = int(os.environ.get("TOP_N", "20"))
NR4A3_RECEPTOR = os.environ.get("NR4A3_RECEPTOR")
NR4A3_BOX_RES = os.environ.get("NR4A3_BOX_RES", "")


def read_manifest(input_dir):
    """cv_residues + lbd_first from a paralogue's metad manifest (written by nr4a3_metad.py)."""
    p = os.path.join(input_dir, "metad_manifest.json")
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        m = json.load(fh)
    return {"cv_residues": m.get("cv_residues"), "lbd_first": m.get("lbd_first", LBD_FIRST_NR4A3),
            "target": m.get("target")}


def _pdb_resseqs(pdb):
    """Ordered unique CA resSeqs of a protein PDB."""
    seen, out = set(), []
    for line in open(pdb):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                rs = int(line[22:26])
            except ValueError:
                continue
            if rs not in seen:
                seen.add(rs); out.append(rs)
    return out


def _release_box_residues(resseqs):
    """Box residues for the Step-0 release receptor: NR4A3_BOX_RES env, else the Step-0 manifest's
    box_residues for this receptor, else the Pocket-5 lining mapped onto the receptor numbering."""
    if NR4A3_BOX_RES.strip():
        return [int(x) for x in NR4A3_BOX_RES.split(",") if x.strip()]
    man = os.path.join(os.path.dirname(NR4A3_RECEPTOR), "nr4a3-release-druggable.json")
    if os.path.exists(man):
        try:
            m = json.load(open(man))
            want = os.path.basename(NR4A3_RECEPTOR)
            for r in m.get("receptors", []):
                if r.get("pdb") == want and r.get("box_residues"):
                    return list(r["box_residues"])
        except Exception:  # noqa: BLE001 — fall through to Pocket-5
            pass
    pos, _ = rm.resolve_positions(resseqs, range(406, 535), LBD_FIRST_NR4A3)
    return [resseqs[i] for i in pos]


def _use_release_receptor(conf):
    """Copy the Step-0 release receptor to `conf`, read its resSeqs, box on its pocket. Returns
    (receptor_pdb, resseqs, box_center)."""
    import shutil
    shutil.copy(NR4A3_RECEPTOR, conf)
    resseqs = _pdb_resseqs(conf)
    box_res = [rs for rs in _release_box_residues(resseqs) if rs in set(resseqs)]
    if not box_res:
        raise RuntimeError("no NR4A3 box residues resolved on the release receptor")
    center, _ = wh.pocket_box(conf, box_res)
    print(f"  NR4A3 release receptor {os.path.basename(NR4A3_RECEPTOR)}: {len(resseqs)} res, "
          f"box on {len(box_res)} residues", flush=True)
    return conf, resseqs, center


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

    # 1) candidate library. De-novo funnel mode: top-N generated candidates by denovo_promise. Default:
    #    real ChEMBL matter, deduplicated by ChEMBL id + label.
    if os.environ.get("SPECIES_MODE") == "1":
        # pre-FEP species resolution: dock denovo_401's 16 stereoisomers + denovo_111's protonation variants
        # through the identical funnel so MM-GBSA picks the correct 3D species to FEP (no developability filter).
        import denovo_library as dl
        import fep_species as sp
        ligands = dl.top_candidates(sp.species_candidate_json(), 10_000)
        res["candidate_source"] = f"FEP species set ({len(ligands)}: denovo_401 stereoisomers + denovo_111 protonation)"
        print(f"  candidate library: {res['candidate_source']}", flush=True)
    elif os.environ.get("DECOY_MODE") == "1":
        # red-team Tier-1 #2: dock a fixed non-NR4A decoy set through the identical funnel as a specificity
        # NULL. All decoys are docked (no developability filter) to measure the null NR4A3-favourable rate.
        import denovo_library as dl
        import decoy_library as decoys
        ligands = dl.top_candidates(decoys.decoy_candidate_json(), 10_000)
        res["candidate_source"] = f"DECOY negative control ({len(ligands)} non-NR4A marketed drugs)"
        print(f"  candidate library: {res['candidate_source']}", flush=True)
    elif CANDIDATE_JSON and os.path.exists(CANDIDATE_JSON):
        import denovo_library as dl
        denovo = json.load(open(CANDIDATE_JSON))
        if os.environ.get("DEVELOPABLE_ONLY") == "1":
            # red-team Tier-1 #1: advance only DEVELOPABLE generations (no structural-alert liability +
            # aromatic + SA<=4.5) to dock+MM-GBSA, so artifacts (carbamic acid / peroxide / ...) are skipped.
            import structural_alerts as sa
            ligands = dl.top_developable_candidates(denovo, sa.liabilities_from_smiles, TOP_N)
            res["candidate_source"] = (f"de-novo top {len(ligands)} DEVELOPABLE by denovo_promise "
                                       f"({os.path.basename(CANDIDATE_JSON)}; structural-alert filtered)")
        else:
            ligands = dl.top_candidates(denovo, TOP_N)
            res["candidate_source"] = (f"de-novo top {len(ligands)} by denovo_promise "
                                       f"({os.path.basename(CANDIDATE_JSON)})")
        print(f"  candidate library: {res['candidate_source']}", flush=True)
    else:
        ligands, seen = [], set()
        for nm in dock.LIGAND_NAMES:
            hit = dock.chembl_smiles_by_name(nm)
            if hit and (nm, hit[0]) not in seen:
                ligands.append((nm, hit[0], hit[1])); seen.add((nm, hit[0]))
        for label, cid, smi in dock.chembl_nr4a3_actives():
            if (label, cid) not in seen:
                ligands.append((label, cid, smi)); seen.add((label, cid))
        res["candidate_source"] = "ChEMBL NR4A actives"
    if not ligands:
        res["_status"] = "no candidate ligands resolved"
        _write(res); return
    sdf = os.path.join(OUT, "candidates.sdf")
    kept = dock.make_sdf(ligands, sdf)
    res["n_candidates"] = len(kept)

    # 2) per paralogue: extract its opened conformer, box on its own CV, dock the library.
    per = {}
    for tag in PARALOGUES:
        # NR4A3 funnel override: dock into the Step-0 druggable-release receptor instead of a metad conformer.
        if tag == "nr4a3" and NR4A3_RECEPTOR:
            conf = os.path.join(OUT, f"{tag}-opened.pdb")
            try:
                rec, resseqs, center = _use_release_receptor(conf)
                scores, pose = wh.dock_into(rec, center, sdf, tag)
            except Exception as e:  # noqa: BLE001
                res.setdefault("_warnings", []).append(f"NR4A3 release-receptor dock failed: {e}")
                continue
            per[tag] = {"conformer": rec, "resseqs": resseqs, "scores": scores, "pose": pose,
                        "manifest": None}
            res["paralogues"][KEY[tag]] = {"receptor": os.path.basename(NR4A3_RECEPTOR),
                                           "source": "step0-druggable-release", "n_docked": len(scores)}
            continue
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
    _plot_matrix(rows, OUT)
    print(json.dumps({"cell_census": res["matrix"]["cell_census"], "leads": res["leads"],
                      "n_candidates": res.get("n_candidates")}, indent=2), flush=True)


def _plot_matrix(rows, out):
    """Fig 4b: heatmap of the top candidates' docking dG into each opened pocket, annotated with the
    assigned matrix cell. Best-effort (a missing matplotlib never fails the job)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        top = [r for r in rows if r["dG"]["NR4A3"] is not None][:20]
        if not top:
            return
        cols = ("NR4A3", "NR4A1", "NR4A2")
        M = np.array([[(r["dG"][t] if r["dG"][t] is not None else np.nan) for t in cols] for r in top])
        fig, ax = plt.subplots(figsize=(6, max(3, 0.36 * len(top))))
        im = ax.imshow(M, aspect="auto", cmap="viridis_r")
        ax.set_xticks(range(3)); ax.set_xticklabels(cols)
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels([f"{r['label'][:18]} [{r['cell']}]" for r in top], fontsize=7)
        for i, r in enumerate(top):
            for j, t in enumerate(cols):
                v = r["dG"][t]
                if v is not None:
                    ax.text(j, i, f"{v:.1f}", ha="center", va="center", color="w", fontsize=6)
        plt.colorbar(im, label="docking dG (kcal/mol; triage prior, not affinity)")
        ax.set_title("NR4A selectivity matrix — opened-pocket docking dG")
        plt.tight_layout()
        plt.savefig(os.path.join(out, "nr4a3-matrix.png"), dpi=130)
    except Exception as e:  # noqa: BLE001
        print(f"  matrix plot skipped: {e}", file=sys.stderr)


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
