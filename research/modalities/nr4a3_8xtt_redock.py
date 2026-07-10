#!/usr/bin/env python3
"""
Re-dock the carried lead denovo_401 into the DRUGGABLE experimental 8XTT conformers and MM-GBSA-rescore,
to test whether the NR4A3-vs-paralogue SELECTIVITY survives on EXPERIMENTAL geometry (not the AF2/metad
frame the whole design was built against).

WHY. The 8XTT benchmark (nr4a3-8xtt-benchmark-findings.md) is a two-part verdict: the experimental apo NMR
ensemble CORROBORATES the cryptic-druggability distribution (4/20 conformers — models 2, 8, 20, 6 — clear
D*=0.53) but the AF2 *atomic* pocket geometry DIVERGES ~3.5 A. denovo_401's pose + selectivity margins were
scored on the AF2/metad receptor, so the reviewer's ask is: dock the lead into the EXPERIMENTAL druggable
conformers and re-check the selectivity margin there.

WHAT (all reuse — no new docking/scoring physics):
  1. extract the >=0.53-druggable 8XTT conformers (default models 2,8,20,6) as protein-only NR4A3 receptors;
  2. box each on the Pocket-5 lining residues, mapped UniProt->8XTT via nr4a3_8xtt_benchmark's alignment;
  3. dock denovo_401 into each with nr4a3_warhead.dock_into (smina), then MM-GBSA-rescore the NR4A3 pose
     with mmgbsa_energy.endpoint_dG (the SAME single-snapshot GBn2 endpoint the matrix/mmgbsa tier uses);
  4. get the denovo_401 PARALOGUE baseline (NR4A1/NR4A2) by REUSING the existing matrix receptors +
     docked poses (mounted from s3://<bucket>/nr4a3-matrix): reuse the already-docked denovo_401 pose if
     present, else dock fresh into <para>-opened.pdb. MM-GBSA-rescore each once (shared baseline);
  5. per conformer: NR4A3-selectivity margins (mmgbsa_select.margins) + a verdict comparing to the
     published (AF2/metad) docking margin; then a summary — does the selectivity SURVIVE on experimental
     geometry (min_margin > band in a majority of the druggable conformers)?

Output: nr4a3-8xtt-redock-denovo401.json (per-conformer selectivity margins + summary), checkpointed after
each conformer (Continuous S3 upload). PURE logic (conformer/PDB text handling + the selectivity summary)
is dependency-free and unit-tested in tests/test_8xtt_redock.py; the heavy dock/MM-GBSA glue is lazy-imported.
"""
import json
import os
import sys
import traceback

import nr4a3_8xtt_benchmark as bm
import nr4a3_8xtt_pocketminer as pm     # reuse select_models (8XTT conformer resolution)
import mmgbsa_select as ms              # reuse margins/verdict (unit-tested selectivity arithmetic)

LIGAND_LABEL = "denovo_401"
LIGAND_SMILES = "COC[C@H](c1ccccc1)[C@@H]1CC[C@H](CC(C)(C)[C@@H](C)O)C1"   # the carried lead
# The >=0.53-druggable 8XTT conformers from the benchmark (models 2, 8, 20, 6). Overridable via env.
DEFAULT_MODELS = "2,8,20,6"
PARALOGUES = ["nr4a1", "nr4a2"]
KEY = {"nr4a3": "NR4A3", "nr4a1": "NR4A1", "nr4a2": "NR4A2"}

IN = os.environ.get("INPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUTPUT_DIR", IN)
MATRIX_DIR = os.environ.get("MATRIX_DIR", os.path.join(IN, "matrix"))   # mounted s3://<bucket>/nr4a3-matrix
REQUESTED_MODELS = os.environ.get("MODELS", DEFAULT_MODELS)
MINIMIZE_ITERS = int(os.environ.get("MMGBSA_MIN_ITERS", "250"))
BAND = float(os.environ.get("SELECT_BAND", str(ms.BAND)))


# ==================================================================================================
# PURE LOGIC — unit-tested in tests/test_8xtt_redock.py (no smina/openmm/rdkit/biopython/network).
# ==================================================================================================

def protein_only_model(model_text):
    """From one split 8XTT NMR-model text, return a protein-only receptor PDB body (ATOM records of the
    chain with the most atoms + END). Drops HETATM/waters/other chains so smina/PDBFixer see a clean
    single-chain receptor. Uses author residue numbering unchanged (so the mapped Pocket-5 author resnums
    box the right site). Pure text transform."""
    by_chain = {}
    for line in model_text.splitlines():
        if not line.startswith("ATOM"):
            continue
        if len(line) < 22:
            continue
        if line[16] not in (" ", "A"):        # keep first altloc only (blank or 'A')
            continue
        chain = line[21]
        by_chain.setdefault(chain, []).append(line)
    if not by_chain:
        raise ValueError("no ATOM records in model text")
    chain = max(by_chain, key=lambda c: len(by_chain[c]))
    return "".join(l if l.endswith("\n") else l + "\n" for l in by_chain[chain]) + "END\n"


def summarize_selectivity(per_conformer, band=ms.BAND):
    """Aggregate the per-conformer NR4A3-selectivity into a distribution + verdict.

    `per_conformer`: list of {"model": int, "mm_min_margin": float|None, ...}. Returns the min-margin
    distribution across the scored conformers (reusing nr4a3_8xtt_benchmark.distribution_stats), the count
    of conformers that are NR4A3-selective (min_margin > band), and a verdict:
      * survives : a MAJORITY of scored conformers are NR4A3-selective (min_margin > band)
      * mixed    : some but not a majority
      * fails    : none selective
      * no-data  : no conformer produced a min_margin
    The threshold used by distribution_stats is `band` so frac_ge_threshold == fraction selective. Pure."""
    margins = [c.get("mm_min_margin") for c in per_conformer if c.get("mm_min_margin") is not None]
    dist = bm.distribution_stats(margins, threshold=band)
    n = dist.get("n", 0)
    n_selective = sum(1 for m in margins if m > band)
    if n == 0:
        verdict = "no-data"
        rationale = "no 8XTT conformer produced an MM-GBSA min-margin (docking/scoring failed)"
    elif n_selective > n / 2:
        verdict = "survives"
        rationale = (f"{n_selective}/{n} druggable 8XTT conformers keep denovo_401 NR4A3-selective "
                     f"(MM-GBSA min-margin > {band} kcal/mol; median {dist.get('median')}); the lead's "
                     "selectivity holds on EXPERIMENTAL geometry, not only the AF2/metad frame.")
    elif n_selective > 0:
        verdict = "mixed"
        rationale = (f"{n_selective}/{n} 8XTT conformers keep denovo_401 NR4A3-selective (median min-margin "
                     f"{dist.get('median')}); selectivity is geometry-sensitive — report the spread honestly.")
    else:
        verdict = "fails"
        rationale = (f"0/{n} 8XTT conformers keep denovo_401 NR4A3-selective (median min-margin "
                     f"{dist.get('median')} <= {band}); the AF2/metad selectivity does NOT reproduce on the "
                     "experimental druggable conformers.")
    return {"n_conformers_scored": n, "n_selective": n_selective, "band": band,
            "min_margin_distribution": dist, "verdict": verdict, "rationale": rationale}


# ==================================================================================================
# I/O + orchestration (AWS-side; NOT unit-tested — smina/openmm/rdkit/biopython/network live here).
# ==================================================================================================

def _read(path):
    with open(path) as fh:
        return fh.read()


def _fetch_af2(dest):
    """Fetch the apo AF2 model for Q92570 (only used to supply the UniProt reference sequence for the
    numbering map — the RECEPTORS are the 8XTT conformers, never AF2)."""
    import json as _json
    import urllib.request
    api = f"https://alphafold.ebi.ac.uk/api/prediction/{bm.UNIPROT}"
    with urllib.request.urlopen(api, timeout=60) as r:
        url = _json.load(r)[0]["pdbUrl"]
    urllib.request.urlretrieve(url, dest)
    return dest


def _pose_from_sdf(pose_sdf, label):
    """Extract the single-molecule OpenFF pose named `label` from a (multi-mol) docked SDF, or None."""
    import mmgbsa_energy as mme
    try:
        poses = mme.load_poses(pose_sdf)
    except Exception as e:  # noqa: BLE001
        print(f"  could not load poses from {pose_sdf}: {e}", file=sys.stderr)
        return None
    return poses.get(label)


def _paralogue_baseline(work_dir):
    """MM-GBSA denovo_401 into the two paralogue comparators, REUSING the matrix receptors + docked poses.

    Returns {"nr4a1": dG|None, "nr4a2": dG|None, "_provenance": {...}}. For each paralogue: reuse the
    already-docked denovo_401 pose from MATRIX_DIR/docked_<tag>.sdf if present (identical comparator to the
    published matrix/mmgbsa run); else dock fresh into <tag>-opened.pdb with a box mapped from the NR4A3
    pocket (nr4a3_warhead.map_pocket_to_paralogue). MM-GBSA once per paralogue (shared across conformers)."""
    import mmgbsa_energy as mme
    out = {}
    prov = {}
    for tag in PARALOGUES:
        rec = os.path.join(MATRIX_DIR, f"{tag}-opened.pdb")
        docked = os.path.join(MATRIX_DIR, f"docked_{tag}.sdf")
        if not os.path.exists(rec):
            out[tag] = None
            prov[tag] = f"missing receptor {rec}"
            continue
        pose = _pose_from_sdf(docked, LIGAND_LABEL) if os.path.exists(docked) else None
        prov[tag] = (f"reused matrix pose docked_{tag}.sdf::{LIGAND_LABEL}" if pose is not None
                     else "no matrix pose; fresh dock into opened receptor")
        try:
            if pose is None:
                pose = _dock_denovo401_into_paralogue(rec, work_dir, tag)
            rec_top, rec_pos = mme.prepare_receptor(rec)
            out[tag] = mme.endpoint_dG(rec_top, rec_pos, pose, minimize_iters=MINIMIZE_ITERS,
                                       cache=os.path.join(work_dir, "sysgen_cache.json"))["dG"]
        except Exception as e:  # noqa: BLE001 — a missing paralogue just leaves the margin one-sided
            out[tag] = None
            prov[tag] += f"; MM-GBSA failed: {str(e)[:160]}"
            print(f"  paralogue {KEY[tag]} baseline failed: {e}", file=sys.stderr)
    out["_provenance"] = prov
    return out


def _dock_denovo401_into_paralogue(para_rec, work_dir, tag):
    """Fresh smina dock of denovo_401 into a paralogue opened receptor (fallback when the matrix pose is
    absent), boxing on the NR4A3 Pocket-5 residues mapped onto the paralogue by BLOSUM62 (reuses
    nr4a3_warhead.map_pocket_to_paralogue + pocket_box + dock_into)."""
    import nr4a3_warhead as wh
    import mmgbsa_energy as mme
    wh.OUT = work_dir
    nr4a3_rec = os.path.join(work_dir, "nr4a3_ref_for_paralogue_map.pdb")
    if not os.path.exists(nr4a3_rec):
        raise RuntimeError("no NR4A3 reference receptor for paralogue mapping")
    nr4a3_pocket = _read(os.path.join(work_dir, "nr4a3_pocket_authnums.json"))
    pocket_auth = json.loads(nr4a3_pocket)
    para_res = wh.map_pocket_to_paralogue(nr4a3_rec, para_rec, pocket_auth)
    if not para_res:
        raise RuntimeError(f"0 pocket residues mapped onto {tag}")
    center, _ = wh.pocket_box(para_rec, para_res)
    sdf = os.path.join(work_dir, "denovo401.sdf")
    _scores, pose_sdf = wh.dock_into(para_rec, center, sdf, tag)
    pose = _pose_from_sdf(pose_sdf, LIGAND_LABEL)
    if pose is None:
        raise RuntimeError(f"fresh dock into {tag} produced no {LIGAND_LABEL} pose")
    return pose


def _matrix_dock_margin(label):
    """denovo_401's published (AF2/metad) docking min-margin from a mounted nr4a3-matrix.json, for the
    per-conformer verdict comparison. None if unavailable."""
    p = os.path.join(MATRIX_DIR, "nr4a3-matrix.json")
    if not os.path.exists(p):
        return None
    try:
        mtx = json.load(open(p))
    except Exception:  # noqa: BLE001
        return None
    for r in mtx.get("candidates", []):
        if r.get("label") == label:
            present = [m for m in (r.get("margin_vs_NR4A1"), r.get("margin_vs_NR4A2")) if m is not None]
            return min(present) if present else None
    return None


def _write(res):
    with open(os.path.join(OUT, "nr4a3-8xtt-redock-denovo401.json"), "w") as fh:
        json.dump(res, fh, indent=2)


def main():
    import nr4a3_warhead as wh
    import nr4a3_dock as dock
    import mmgbsa_energy as mme
    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(OUT, "redock_work")
    os.makedirs(work, exist_ok=True)
    wh.OUT = work

    # Fail FAST if no GPU OpenMM platform loads (MM-GBSA has NO CPU fallback — ~48 min/ligand on CPU), so a
    # broken GPU/ICD dies in seconds, before the (CPU) smina docking, not after burning the timeout.
    omm, _app, ommunit, *_ = mme._mm()
    mme._platform(omm, ommunit)

    res = {"_note": "Re-dock + MM-GBSA of denovo_401 into the DRUGGABLE experimental 8XTT conformers "
                    "(models 2,8,20,6) to test whether NR4A3-vs-paralogue selectivity survives on "
                    "experimental geometry. NR4A3 receptor = 8XTT conformer; NR4A1/NR4A2 baseline reuses "
                    "the matrix receptors/poses. MM-GBSA single-snapshot GBn2 endpoint (enthalpy only) — "
                    "TRIAGE, not affinity, exactly as the matrix/mmgbsa tier.",
           "ligand": {"label": LIGAND_LABEL, "smiles": LIGAND_SMILES},
           "params": {"minimize_iters": MINIMIZE_ITERS, "band": BAND, "requested_models": REQUESTED_MODELS},
           "paralogue_baseline": {}, "per_conformer": []}

    # 1) denovo_401 SDF (RDKit 3D embed) — the docking ligand.
    sdf = os.path.join(work, "denovo401.sdf")
    kept = dock.make_sdf([(LIGAND_LABEL, LIGAND_LABEL, LIGAND_SMILES)], sdf)
    if not kept:
        res["_status"] = "RDKit could not build denovo_401 3D structure"
        _write(res); sys.exit("ABORT: denovo_401 SDF build failed")

    # 2) fetch 8XTT (RCSB) + AF2 (AFDB, reference sequence only) and build the UniProt->8XTT numbering map.
    xtt_path = bm.fetch_rcsb(bm.PDB_ID, os.path.join(work, f"{bm.PDB_ID}.pdb"))
    models = bm.split_models(_read(xtt_path))
    if not models:
        res["_status"] = f"no models parsed from {bm.PDB_ID}"
        _write(res); sys.exit(f"ABORT: no models in {bm.PDB_ID}")
    af2_path = _fetch_af2(os.path.join(work, f"AF-{bm.UNIPROT}.pdb"))
    _af2_ca, af2_resnums, af2_seq = bm.af2_lbd_ca(af2_path)
    _c, xtt_resnums0, xtt_seq0, _ca0 = bm.chain_ca(models[0])
    uni_to_auth, identity = bm.map_uniprot_to_pdb(af2_seq, af2_resnums, xtt_seq0, xtt_resnums0)
    mapped_pocket5 = sorted({uni_to_auth[u] for u in bm.POCKET5 if u in uni_to_auth})
    res["_method"] = {"pdb": bm.PDB_ID, "alignment_identity": round(identity, 4),
                      "mapped_pocket5_8xtt": mapped_pocket5, "n_models": len(models)}
    if not mapped_pocket5:
        res["_status"] = "no Pocket-5 residues mapped onto 8XTT — cannot box"
        _write(res); sys.exit("ABORT: empty Pocket-5 map")
    json.dump(mapped_pocket5, open(os.path.join(work, "nr4a3_pocket_authnums.json"), "w"))

    # 3) choose the druggable conformers actually present.
    chosen = pm.select_models(range(1, len(models) + 1), REQUESTED_MODELS)
    res["_method"]["conformers_scored"] = chosen
    print(f"  8XTT: {len(models)} models; identity {identity:.3f}; docking denovo_401 into models {chosen}",
          flush=True)

    # 4) paralogue baseline (shared across conformers) — reuse the matrix receptors/poses.
    #    Save a NR4A3 reference receptor (first chosen conformer) so the fresh-dock fallback can map it.
    first_rec = os.path.join(work, "nr4a3_ref_for_paralogue_map.pdb")
    with open(first_rec, "w") as fh:
        fh.write(protein_only_model(models[chosen[0] - 1]))
    baseline = _paralogue_baseline(work)
    res["paralogue_baseline"] = {KEY[t]: baseline.get(t) for t in PARALOGUES}
    res["paralogue_baseline"]["_provenance"] = baseline.get("_provenance", {})
    dg1, dg2 = baseline.get("nr4a1"), baseline.get("nr4a2")
    dock_margin = _matrix_dock_margin(LIGAND_LABEL)

    # 5) per druggable conformer: extract receptor, box, dock denovo_401, MM-GBSA, margins, verdict.
    per = []
    for model in chosen:
        rec_info = {"model": model}
        try:
            rec_pdb = os.path.join(work, f"8xtt_model{model}_nr4a3.pdb")
            with open(rec_pdb, "w") as fh:
                fh.write(protein_only_model(models[model - 1]))
            box_res = [r for r in mapped_pocket5]   # author numbering already
            center, nbox = wh.pocket_box(rec_pdb, box_res)
            rec_info["n_box_residues"] = nbox
            _scores, pose_sdf = wh.dock_into(rec_pdb, center, sdf, f"nr4a3_m{model}")
            pose = _pose_from_sdf(pose_sdf, LIGAND_LABEL)
            if pose is None:
                raise RuntimeError("smina produced no denovo_401 pose for this conformer")
            rec_top, rec_pos = mme.prepare_receptor(rec_pdb)
            dg3 = mme.endpoint_dG(rec_top, rec_pos, pose, minimize_iters=MINIMIZE_ITERS,
                                  cache=os.path.join(work, "sysgen_cache.json"))["dG"]
            mar = ms.margins(dg3, dg1, dg2)
            v = ms.verdict(dock_margin, mar["min_margin"], band=BAND)
            rec_info.update({
                "dG_mmgbsa": {"NR4A3": dg3, "NR4A1": dg1, "NR4A2": dg2},
                "mm_margin_vs_NR4A1": mar["margin_vs_NR4A1"], "mm_margin_vs_NR4A2": mar["margin_vs_NR4A2"],
                "mm_min_margin": mar["min_margin"], "dock_min_margin": dock_margin, "verdict": v})
            print(f"  model {model:>2}: mmΔG3={dg3} min-margin={mar['min_margin']} -> {v}", flush=True)
        except Exception as e:  # noqa: BLE001 — record + keep going; one bad conformer never voids the run
            rec_info["error"] = str(e)[:300]
            print(f"  model {model:>2}: ERROR {e}", file=sys.stderr, flush=True)
        per.append(rec_info)
        res["per_conformer"] = per
        res["summary"] = summarize_selectivity(per, band=BAND)
        _write(res)   # checkpoint after EACH conformer (Continuous S3 upload keeps the partial as deliverable)

    res["_status"] = "ok"
    _write(res)
    print(json.dumps({"summary": res["summary"],
                      "paralogue_baseline": res["paralogue_baseline"]}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — always leave a diagnostic
        os.makedirs(OUT, exist_ok=True)
        json.dump({"_status": "error", "error": str(exc), "trace": traceback.format_exc()[-1800:]},
                  open(os.path.join(OUT, "nr4a3-8xtt-redock-denovo401.json"), "w"), indent=2)
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
