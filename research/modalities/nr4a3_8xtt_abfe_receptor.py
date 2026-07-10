#!/usr/bin/env python3
"""
Build the ABFE RECEPTOR PREFIX for an 8XTT-EXPERIMENTALLY-ANCHORED NR4A3 ABFE complex leg.

WHY. The modern independent-window ABFE (nr4a3_abfe.py / nr4a3_abfe_sagemaker.py) consumes a RECEPTOR_PREFIX
S3 prefix holding, per receptor, `<receptor>-opened.pdb` (the receptor structure) + `docked_<receptor>.sdf`
(the docked lead pose). Until now the NR4A3 complex leg's receptor was a DRUGGABLE frame of the AF2/metad
release trajectory (nr4a3_release_druggable.py → nr4a3-denovo-matrix-v2). The 8XTT benchmark showed the AF2
*atomic* pocket geometry diverges ~3.5 A from the experimental apo NMR ensemble (PDB 8XTT), so the reviewer's
ask is to re-run the NR4A3 leg from an EXPERIMENTALLY-anchored frame. nr4a3_8xtt_seed_md.py already ran an
unbiased release-style MD seeded from an 8XTT-derived opened conformer (it held Rg ~0.73-0.78,
frac_time_within_0.1nm_of_seed = 1.0 — the experimental druggable conformation is thermally metastable).

WHAT (CPU: fpocket + smina + RDKit; no GPU, no MM-GBSA — this only PREPARES the ABFE inputs):
  1. Load the 8xtt-release trajectory (8xtt_release_rep*_from*.dcd) + its solvated topology
     (8xtt-lbd-solvated.pdb), both from s3://<bucket>/nr4a3-8xtt-release.
  2. Map orthosteric Pocket-5 (UniProt 406-534) onto the trajectory's 8XTT construct numbering by REUSING the
     BLOSUM62 global alignment in nr4a3_8xtt_benchmark (the plain residue_map heuristic FAILS on the 8XTT
     numbering — the whole reason this is a bespoke script). The alignment runs against the SOLVATED TOPOLOGY's
     protein chain directly, so the mapped author numbers match the trajectory's mdtraj resSeq exactly.
  3. Per frame: CV Rg over the mapped Pocket-5 CA atoms + fpocket druggability of the pocket overlapping the
     mapped Pocket-5 site (the same 8XTT-aware fpocket path the benchmark/redock use). Checkpoint the growing
     manifest after each frame (Continuous S3 upload → a timeout keeps the last partial as the deliverable).
  4. Select the MOST-DRUGGABLE PERSISTENT frame with the pure, unit-tested select_abfe_frame:
     druggability >= D* (0.53, relax to 0.5 with a flag if none) AND within RG_TOL (0.1 nm) of the seed Rg
     (the metastability band the release run held) — max druggability, tie-broken by closeness to the seed Rg.
  5. Write `nr4a3-opened.pdb` (protein-only chosen frame), then dock denovo_401 into its mapped Pocket-5 box
     with smina (nr4a3_warhead.dock_into) → `docked_nr4a3.sdf` (pose _Name = denovo_401, so the ABFE engine's
     --ligand-name denovo_401 / --pose-name selects it). Both upload to s3://<bucket>/nr4a3-abfe-8xtt-receptor.

DESIGN. The selection/parse logic (select_abfe_frame, seed_rg_from_summary, _rep_index) is pure and
dependency-free — tests/test_8xtt_abfe_receptor.py exercises it without mdtraj/fpocket/smina/rdkit/network.
The heavy dock/pocket/MD glue is lazy-imported and validated only on the cloud run (repo convention).

Inputs (mounted by nr4a3_8xtt_abfe_receptor_sagemaker.py):
  RELEASE_DIR (env, default /opt/ml/processing/input/release): 8xtt_release_rep*_from*.dcd +
      8xtt-lbd-solvated.pdb (+ optional 8xtt_release_summary.json for the seed Rg).
Output (env OUTPUT_DIR): nr4a3-opened.pdb + docked_nr4a3.sdf + nr4a3-8xtt-abfe-receptor.json (manifest) +
  a Rg/druggability scatter plot.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback

import nr4a3_8xtt_benchmark as bm    # BLOSUM62 8XTT alignment + fpocket-site + distribution stats (stdlib-only import)

LIGAND_LABEL = "denovo_401"
LIGAND_SMILES = "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"   # the carried lead (as-generated diastereomer)

D_STAR = float(os.environ.get("D_STAR", "0.53"))          # calibrated drug-bound band lower edge
RELAX_TO = float(os.environ.get("RELAX_TO", "0.5"))       # conventional cutoff to relax to if none clear D*
RG_TOL = float(os.environ.get("RG_TOL", "0.1"))           # nm; persistence band around the seed Rg (release held 1.0 within 0.1)
SEED_RG_ENV = os.environ.get("SEED_RG", "")               # override the seed Rg (else read from summary / first frame)
MAX_FRAMES_PER_DCD = int(os.environ.get("MAX_FRAMES_PER_DCD", "0"))   # 0 = every frame; >0 = evenly subsample

RELEASE_DIR = os.environ.get("RELEASE_DIR", "/opt/ml/processing/input/release")
OUT = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")
MANIFEST = "nr4a3-8xtt-abfe-receptor.json"


# ==================================================================================================
# PURE LOGIC — unit-tested in tests/test_8xtt_abfe_receptor.py (no mdtraj/fpocket/smina/rdkit/network).
# ==================================================================================================

def _rep_index(path):
    """`8xtt_release_rep2_from0.dcd` -> 2. Parses the rep index SPECIFICALLY (a plain digit-join would fold
    the '8' of 8xtt and the '_from0' offset into the number). 0 if no rep token."""
    m = re.search(r"rep(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0


def seed_rg_from_summary(summary):
    """Seed Rg (nm) from a parsed 8xtt_release_summary.json dict, or None. Prefers the top-level
    'seed_Rg_nm'; falls back to the first replica's 'seed_Rg'. Pure."""
    if not isinstance(summary, dict):
        return None
    v = summary.get("seed_Rg_nm")
    if v is not None:
        return float(v)
    for rep in summary.get("replicas", []) or []:
        if rep.get("seed_Rg") is not None:
            return float(rep["seed_Rg"])
    return None


def select_abfe_frame(records, seed_rg, d_star=D_STAR, rg_tol=RG_TOL, relax_to=RELAX_TO):
    """Choose the ABFE receptor frame: the MOST-DRUGGABLE PERSISTENT release frame.

    records: [{"dcd": str, "rep": int, "frame": int, "rg": float|None, "druggability": float|None}].
             Records missing druggability or rg are ignored.
    seed_rg: the metastable seed Rg (nm) the release run held; None → skip the persistence filter.

    Rule (documented so the receptor choice is reproducible):
      1. DRUGGABLE = druggability >= d_star (default 0.53). If none clear it, relax to `relax_to` (0.5) and
         flag it. If still none → primary=None (the driver aborts loudly rather than anchoring to a
         non-druggable frame).
      2. PERSISTENT = |rg - seed_rg| <= rg_tol (the band the release run held). If no druggable frame is
         within the band, take the druggable set anyway and flag rg_relaxed (so we still return the best
         druggable frame, honestly labelled).
      3. PRIMARY = highest druggability among the persistent+druggable candidates; tie-break: closest Rg to
         the seed, then lowest (rep, frame).
    Returns {"primary": rec|None, "d_star_used", "relaxed", "rg_relaxed", "n_usable", "n_druggable",
             "n_candidates", "seed_rg", "rg_tol", "reason"}.
    """
    usable = [r for r in records
              if r.get("druggability") is not None and r.get("rg") is not None]
    relaxed = False
    thr = d_star
    druggable = [r for r in usable if r["druggability"] >= thr]
    if not druggable and relax_to is not None and relax_to < d_star:
        thr, relaxed = relax_to, True
        druggable = [r for r in usable if r["druggability"] >= thr]

    base = {"d_star_used": thr, "relaxed": relaxed, "rg_relaxed": False,
            "n_usable": len(usable), "n_druggable": len(druggable), "n_candidates": 0,
            "seed_rg": seed_rg, "rg_tol": rg_tol}
    if not druggable:
        base.update({"primary": None,
                     "reason": (f"no release frame reached druggability >= {d_star} (nor the relaxed "
                                f"{relax_to}); ABFE receptor cannot be anchored on this trajectory set")})
        return base

    if seed_rg is None:
        candidates = list(druggable)
    else:
        candidates = [r for r in druggable if abs(r["rg"] - seed_rg) <= rg_tol]
    if not candidates:
        candidates = list(druggable)          # none inside the band — keep the best druggable, flag it
        base["rg_relaxed"] = True

    def _key(r):
        return (int(r.get("rep", 0)), int(r["frame"]))

    def _dist(r):
        return abs(r["rg"] - seed_rg) if seed_rg is not None else 0.0

    # max druggability; tie-break closest Rg to seed (smaller better → negate), then lowest (rep, frame).
    primary = max(candidates,
                  key=lambda r: (r["druggability"], -_dist(r), -_key(r)[0], -_key(r)[1]))
    base.update({
        "primary": primary,
        "n_candidates": len(candidates),
        "reason": (f"{len(druggable)} druggable frame(s) at threshold {thr}"
                   f"{' (relaxed from %.2f)' % d_star if relaxed else ''}; "
                   f"{len(candidates)} within {rg_tol} nm of seed Rg {seed_rg}"
                   f"{' (band RELAXED — none persistent)' if base['rg_relaxed'] else ''}; primary = most "
                   f"druggable ({primary['druggability']}) at Rg {primary['rg']}"),
    })
    return base


# ==================================================================================================
# I/O + orchestration (AWS-side; NOT unit-tested — mdtraj/fpocket/smina/rdkit/network live here).
# ==================================================================================================

def _read(path):
    with open(path) as fh:
        return fh.read()


def _cv_ca_indices(prot_top, want_resseqs):
    """0-based atom indices (into the protein-sliced trajectory) of the mapped Pocket-5 lining CA atoms,
    matched by author resSeq — the 8XTT numbering the mapped Pocket-5 uses (identical to seed_md's CV)."""
    want = set(want_resseqs)
    return [a.index for a in prot_top.atoms if a.name == "CA" and a.residue.resSeq in want]


def _fpocket_druggability(prot, fi, mapped_pocket5, work):
    """fpocket on one frame; druggability of the pocket overlapping the mapped Pocket-5 site (author
    numbering), via the 8XTT-aware nr4a3_8xtt_benchmark path. (None, 0) on any failure (best-effort)."""
    d = tempfile.mkdtemp(prefix=f"af_{fi}_", dir=work)
    try:
        pdb = os.path.join(d, "frame.pdb")
        prot[fi].save_pdb(pdb)
        pockets = bm.fpocket_pockets_with_residues(pdb)
        site, nov = bm.pocket_overlapping_site(pockets, mapped_pocket5)
        if site is None:
            return None, 0
        return site["druggability"], nov
    except Exception as e:  # noqa: BLE001 — keep scanning
        print(f"  frame {fi} fpocket skipped: {e}", file=sys.stderr, flush=True)
        return None, 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _write_manifest(res):
    with open(os.path.join(OUT, MANIFEST), "w") as fh:
        json.dump(res, fh, indent=2)


def _plot(records, primary, seed_rg, d_star):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        rg = [r["rg"] for r in records if r.get("rg") is not None and r.get("druggability") is not None]
        dr = [r["druggability"] for r in records if r.get("rg") is not None and r.get("druggability") is not None]
        if not rg:
            return
        plt.figure(figsize=(7, 4))
        plt.scatter(rg, dr, s=18, c="0.6", label="8XTT-release frames")
        plt.axhline(d_star, color="r", ls="--", lw=0.7, label=f"D*={d_star}")
        if seed_rg is not None:
            plt.axvline(seed_rg, color="b", ls=":", lw=0.7, label=f"seed Rg {seed_rg}")
        if primary:
            plt.scatter([primary["rg"]], [primary["druggability"]], s=110, c="g", marker="*",
                        zorder=5, label="chosen ABFE frame")
        plt.xlabel("CV Pocket-5 Rg (nm)")
        plt.ylabel("Pocket-5 fpocket druggability")
        plt.title("NR4A3 ABFE receptor from the 8XTT-seeded release MD")
        plt.ylim(0, 1)
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "nr4a3-8xtt-abfe-receptor.png"), dpi=130)
    except Exception as e:  # noqa: BLE001 — plot is a nicety
        print(f"  plot skipped: {e}", file=sys.stderr)


def main():
    import numpy as np
    import mdtraj as md
    import nr4a3_md_release as R           # reuse _rg_series (the CV Rg used to define persistence)
    import nr4a3_8xtt_redock as rd         # reuse _fetch_af2 (AFDB reference sequence)
    import nr4a3_dock as dock              # reuse make_sdf / _which
    import nr4a3_warhead as wh             # reuse pocket_box / dock_into (smina)

    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(OUT, "abfe_receptor_work")
    os.makedirs(work, exist_ok=True)

    top = os.path.join(RELEASE_DIR, "8xtt-lbd-solvated.pdb")
    if not os.path.exists(top):
        sys.exit(f"  ABORT: missing topology {top} (mount nr4a3-8xtt-release at RELEASE_DIR)")
    dcds = sorted(glob.glob(os.path.join(RELEASE_DIR, "8xtt_release_rep*.dcd")),
                  key=lambda p: (_rep_index(p), os.path.basename(p)))
    if not dcds:
        sys.exit(f"  ABORT: no 8xtt_release_rep*.dcd in {RELEASE_DIR} (mount nr4a3-8xtt-release at RELEASE_DIR)")
    if not dock._which("fpocket"):
        sys.exit("  ABORT: fpocket not on PATH (needed for per-frame druggability)")
    print(f"  topology={top}; trajectories: {[os.path.basename(d) for d in dcds]}", flush=True)

    res = {"_note": "ABFE receptor prefix (nr4a3-opened.pdb + docked_nr4a3.sdf) built from the 8XTT-seeded "
                    "unbiased release MD, so the NR4A3 ABFE COMPLEX leg is anchored on EXPERIMENTAL (8XTT) "
                    "geometry rather than the AF2/metad frame. Receptor = the most-druggable PERSISTENT "
                    "release frame (fpocket >= D* near the seed Rg); ligand = denovo_401 docked (smina) into "
                    "its mapped Pocket-5 box. Pocket-5 is mapped onto the 8XTT construct numbering by the "
                    "nr4a3_8xtt_benchmark BLOSUM62 alignment (the plain residue_map heuristic fails here).",
           "ligand": {"label": LIGAND_LABEL, "smiles": LIGAND_SMILES},
           "params": {"d_star": D_STAR, "relax_to": RELAX_TO, "rg_tol_nm": RG_TOL,
                      "max_frames_per_dcd": MAX_FRAMES_PER_DCD},
           "topology": os.path.basename(top), "trajectories": [os.path.basename(d) for d in dcds]}
    _write_manifest(res)

    # --- 1) map Pocket-5 (UniProt) onto the SOLVATED TOPOLOGY's 8XTT author numbering ---------------
    #     Align the solvated topology's protein chain directly to the AFDB reference so the mapped author
    #     numbers match the trajectory's mdtraj resSeq exactly (robust to any PDBFixer renumber).
    _chain, xtt_resnums, xtt_seq, _ca = bm.chain_ca(_read(top))
    af2_path = rd._fetch_af2(os.path.join(work, f"AF-{bm.UNIPROT}.pdb"))
    _af2_ca, af2_resnums, af2_seq = bm.af2_lbd_ca(af2_path)
    uni_to_auth, identity = bm.map_uniprot_to_pdb(af2_seq, af2_resnums, xtt_seq, xtt_resnums)
    mapped_pocket5 = sorted({uni_to_auth[u] for u in bm.POCKET5 if u in uni_to_auth})
    res["alignment"] = {"identity": round(identity, 4), "mapped_pocket5_8xtt": mapped_pocket5,
                        "n_pocket5_mapped": len(mapped_pocket5)}
    if len(mapped_pocket5) < 3:
        res["_status"] = "too few Pocket-5 residues mapped onto the 8XTT numbering — cannot box/CV"
        _write_manifest(res)
        sys.exit(f"  ABORT: only {len(mapped_pocket5)} Pocket-5 residues mapped onto 8XTT")
    print(f"  alignment identity {identity:.3f}; mapped Pocket-5 (8XTT numbering) = {mapped_pocket5}", flush=True)

    # --- 2) seed Rg (the metastability anchor): summary → env → first frame -------------------------
    seed_rg = None
    summ_path = os.path.join(RELEASE_DIR, "8xtt_release_summary.json")
    if os.path.exists(summ_path):
        try:
            seed_rg = seed_rg_from_summary(json.load(open(summ_path)))
        except Exception as e:  # noqa: BLE001
            print(f"  could not read {summ_path}: {e}", file=sys.stderr)
    if seed_rg is None and SEED_RG_ENV:
        seed_rg = float(SEED_RG_ENV)
    res["seed_rg_source"] = ("8xtt_release_summary.json" if os.path.exists(summ_path) and seed_rg is not None
                             else ("SEED_RG env" if SEED_RG_ENV else "first release frame (fallback)"))

    # --- 3) per-frame CV Rg + fpocket druggability across every replica -----------------------------
    records = []
    cv_idx = None
    for dcd in dcds:
        rep = _rep_index(dcd)
        t = md.load(dcd, top=top)
        prot = t.atom_slice(t.topology.select("protein"))
        if cv_idx is None:
            cv_idx = _cv_ca_indices(prot.topology, mapped_pocket5)
            if len(cv_idx) < 3:
                res["_status"] = f"only {len(cv_idx)} Pocket-5 CA atoms matched for the CV Rg"
                _write_manifest(res)
                sys.exit(f"  ABORT: {res['_status']}")
            print(f"  CV Pocket-5 CA atoms: {len(cv_idx)}", flush=True)
        rg_series = R._rg_series(prot.xyz, cv_idx)     # nm, per frame
        if seed_rg is None:
            seed_rg = round(float(rg_series[0]), 4)     # fallback: the first frame's Rg
            res["seed_rg_source"] = "first release frame (fallback)"
        n = prot.n_frames
        frames = range(n)
        if MAX_FRAMES_PER_DCD and n > MAX_FRAMES_PER_DCD:
            frames = sorted({int(round(x)) for x in np.linspace(0, n - 1, MAX_FRAMES_PER_DCD)})
        print(f"  [{os.path.basename(dcd)}] rep{rep}: {n} frames, scoring {len(list(frames))}", flush=True)
        for fi in frames:
            drug, nov = _fpocket_druggability(prot, fi, mapped_pocket5, work)
            records.append({"dcd": os.path.basename(dcd), "rep": rep, "frame": int(fi),
                            "rg": round(float(rg_series[fi]), 4), "druggability": drug,
                            "pocket5_overlap": nov})
            res["seed_rg"] = seed_rg
            res["n_frames_scored"] = len(records)
            res["per_frame"] = records
            _write_manifest(res)     # checkpoint after EACH frame (Continuous S3 upload ships the partial)

    # --- 4) select the most-druggable persistent frame ---------------------------------------------
    sel = select_abfe_frame(records, seed_rg, d_star=D_STAR, rg_tol=RG_TOL, relax_to=RELAX_TO)
    res["selection"] = {k: sel[k] for k in ("d_star_used", "relaxed", "rg_relaxed", "n_usable",
                                            "n_druggable", "n_candidates", "seed_rg", "rg_tol", "reason")}
    primary = sel["primary"]
    if primary is None:
        res["_status"] = "no druggable release frame — ABFE receptor cannot be anchored"
        _write_manifest(res)
        _plot(records, None, seed_rg, D_STAR)
        sys.exit(f"  ABORT: {sel['reason']}")
    res["chosen_frame"] = primary
    print(f"  CHOSEN: {primary['dcd']} rep{primary['rep']} frame {primary['frame']} "
          f"Rg={primary['rg']} druggability={primary['druggability']} (seed Rg {seed_rg})", flush=True)

    # --- 5a) write the receptor PDB (protein-only chosen frame) -------------------------------------
    chosen_dcd = os.path.join(RELEASE_DIR, primary["dcd"])
    tsel = md.load(chosen_dcd, top=top)
    prot_sel = tsel.atom_slice(tsel.topology.select("protein"))
    rec_pdb = os.path.join(OUT, "nr4a3-opened.pdb")
    prot_sel[primary["frame"]].save_pdb(rec_pdb)
    resseqs = [r.resSeq for r in prot_sel.topology.residues]
    res["receptor_pdb"] = {"file": "nr4a3-opened.pdb", "resseq_range": [int(min(resseqs)), int(max(resseqs))]}
    print(f"  wrote receptor {rec_pdb} (resSeq {min(resseqs)}..{max(resseqs)})", flush=True)

    # --- 5b) dock denovo_401 into the mapped Pocket-5 box -> docked_nr4a3.sdf -----------------------
    wh.OUT = OUT                     # dock_into writes docked_<tag>.sdf here → docked_nr4a3.sdf
    lig_sdf = os.path.join(work, "denovo401.sdf")
    kept = dock.make_sdf([(LIGAND_LABEL, LIGAND_LABEL, LIGAND_SMILES)], lig_sdf)   # _Name = denovo_401
    if not kept:
        res["_status"] = "RDKit could not build the denovo_401 3D structure"
        _write_manifest(res)
        sys.exit("  ABORT: denovo_401 SDF build failed")
    center, nbox = wh.pocket_box(rec_pdb, mapped_pocket5)
    if not dock._which("smina"):
        res["_status"] = "smina not on PATH — cannot dock denovo_401"
        _write_manifest(res)
        sys.exit("  ABORT: smina missing")
    scores, pose_sdf = wh.dock_into(rec_pdb, center, lig_sdf, "nr4a3")   # -> OUT/docked_nr4a3.sdf
    if not os.path.exists(pose_sdf) or LIGAND_LABEL not in scores:
        res["_status"] = f"smina produced no {LIGAND_LABEL} pose in docked_nr4a3.sdf"
        res["docking"] = {"box_center": [round(x, 2) for x in center], "n_box_ca": nbox, "scores": scores}
        _write_manifest(res)
        sys.exit(f"  ABORT: {res['_status']}")
    res["docking"] = {"pose_sdf": "docked_nr4a3.sdf", "pose_name": LIGAND_LABEL,
                      "box_center": [round(x, 2) for x in center], "n_box_ca": nbox,
                      "smina_affinity_kcal_mol": round(scores[LIGAND_LABEL], 2),
                      "box_residues_8xtt": mapped_pocket5}
    print(f"  docked {LIGAND_LABEL}: smina affinity {scores[LIGAND_LABEL]:.2f} kcal/mol -> docked_nr4a3.sdf",
          flush=True)

    res["receptor_prefix_contents"] = ["nr4a3-opened.pdb", "docked_nr4a3.sdf"]
    res["_status"] = "ok"
    _write_manifest(res)
    _plot(records, primary, seed_rg, D_STAR)
    print("  DONE: ABFE receptor prefix ready (nr4a3-opened.pdb + docked_nr4a3.sdf). Point the ABFE complex "
          "leg's RECEPTOR_PREFIX at s3://<bucket>/nr4a3-abfe-8xtt-receptor with ABFE_RECEPTORS=nr4a3.",
          flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic (checkpoint rule)
        os.makedirs(OUT, exist_ok=True)
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, MANIFEST), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
