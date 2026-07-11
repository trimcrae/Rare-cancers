#!/usr/bin/env python3
"""SageMaker entry — run PocketMiner on the EXPERIMENTAL apo NR4A3 LBD (PDB 8XTT), in-job.

The original entry.py runs PocketMiner on the AF2 apo model. This variant re-runs the SAME orthogonal
cryptic-pocket GNN on the EXPERIMENTAL 8XTT NMR conformers (the review's explicit ask), so the enrichment
claim is rebased off AF2 onto experiment. It reuses:
  * the PocketMiner inference DRIVER + the conda-env recipe from entry.py (adding biopython for the map);
  * nr4a3_8xtt_benchmark for the 8XTT fetch/split + the UniProt<->8XTT numbering map (BLOSUM62);
  * nr4a3_8xtt_pocketminer for the PURE per-conformer analysis + cross-conformer aggregation.

PIPELINE. (1) clone this repo @ --git-ref (for nr4a3_8xtt_benchmark + nr4a3_8xtt_pocketminer) ->
(2) fetch 8XTT (RCSB) + AF-Q92570 (AFDB, reference sequence only) -> (3) split 8XTT + pick the druggable
conformers (default models 2,8,20,6; PM8_MODELS=all for all 20) -> (4) build the PocketMiner TF env
(+biopython) + clone Mickdub/gvp -> (5) run PocketMiner per conformer -> (6) map scores UniProt<->8XTT,
compute per-conformer Pocket-5-over-LBD enrichment + aggregate -> nr4a3-8xtt-pocketminer.json (Continuous
S3 upload). CPU work (small GNN inference). No GPU.
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request

import sm_io
import entry as pm_entry     # reuse DRIVER + build_env recipe (same source_dir)

OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path
REPO = "https://github.com/trimcrae/Rare-cancers"


def _sh(cmd, **kw):
    print("  $ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, **kw)


def _fetch(url, dest):
    print(f"  downloading {url}", flush=True)
    urllib.request.urlretrieve(url, dest)
    return dest


def _fetch_af2(dest):
    api = f"https://alphafold.ebi.ac.uk/api/prediction/Q92570"
    with urllib.request.urlopen(api, timeout=60) as r:
        url = json.load(r)[0]["pdbUrl"]
    return _fetch(url, dest)


def _build_pm_env(conda, repo):
    """PocketMiner TF env (entry.py recipe) PLUS biopython for the UniProt<->8XTT BLOSUM62 map."""
    py = os.environ.get("PM_PY_VERSION", "3.9")
    tf = os.environ.get("PM_TF_VERSION", "2.9.1")
    _sh([conda, "create", "-y", "-n", "pm", "-c", "conda-forge",
         f"python={py}", "mdtraj<1.10", "numpy<1.24", "netcdf4", "biopython", "pip"], check=True)
    _sh([conda, "run", "--no-capture-output", "-n", "pm", "pip", "install", "--quiet",
         "--upgrade-strategy", "only-if-needed",
         f"tensorflow=={tf}", "scipy", "pandas", "tqdm", "pyyaml"], check=True)


# Final in-env analysis driver: builds the numbering map + per-conformer analysis + aggregate. Runs in the
# pm env (biopython present) with PYTHONPATH=<repo modalities> so it imports our pure modules.
ANALYSIS = r'''
import json, os, sys
import numpy as np
import nr4a3_8xtt_benchmark as bm
import nr4a3_8xtt_pocketminer as p8

conf_root = os.environ["PM8_CONF_ROOT"]        # dir holding conf_<m>/ subdirs with preds + residue_order
af2 = os.environ["PM8_AF2"]
xtt = os.environ["PM8_XTT"]
out = os.environ["PM8_OUT"]
models = [int(m) for m in os.environ["PM8_MODEL_LIST"].split(",") if m.strip()]

_ca, af2_resnums, af2_seq = bm.af2_lbd_ca(af2)
model_texts = bm.split_models(open(xtt).read())
_c, xtt_resnums0, xtt_seq0, _ca0 = bm.chain_ca(model_texts[0])
uni_to_auth, identity = bm.map_uniprot_to_pdb(af2_seq, af2_resnums, xtt_seq0, xtt_resnums0)
mapped_pocket5 = sorted({uni_to_auth[u] for u in bm.POCKET5 if u in uni_to_auth})
print(f"[analysis] alignment identity {identity:.3f}; mapped Pocket-5 -> {mapped_pocket5}", flush=True)

per = []
for m in models:
    cdir = os.path.join(conf_root, f"conf_{m}")
    preds_p = os.path.join(cdir, "nr4a3_lbd-preds.npy")
    ro_p = os.path.join(cdir, "residue_order.json")
    if not (os.path.exists(preds_p) and os.path.exists(ro_p)):
        per.append({"model": m, "analysis": {"n_residues_scored": 0, "_status": "inference missing"}})
        continue
    preds = np.load(preds_p).reshape(-1).tolist()
    resseq = json.load(open(ro_p))["resSeq"]
    n = min(len(preds), len(resseq))
    scores_by_auth = {int(resseq[i]): float(preds[i]) for i in range(n)}
    per.append({"model": m, "analysis": p8.analyse_conformer(scores_by_auth, uni_to_auth)})

agg = p8.aggregate_conformers(per)
result = {
    "_title": "PocketMiner cryptic-pocket prediction on the EXPERIMENTAL apo NR4A3 LBD (PDB 8XTT)",
    "_input": {"pdb": bm.PDB_ID, "uniprot": bm.UNIPROT,
               "circularity_guard": "experimental apo NMR ensemble; independent of AF2/metadynamics",
               "alignment_identity": round(identity, 4), "mapped_pocket5_8xtt": mapped_pocket5},
    "_method": {"tool": "PocketMiner (GVP graph neural network)",
                "citation": "Meller et al., Nat Commun 14:1177 (2023)",
                "note": ("Per-conformer PocketMiner scores mapped UniProt<->8XTT; Pocket-5-over-LBD "
                         "enrichment reported as a DISTRIBUTION across the scored 8XTT conformers, mirroring "
                         "the AF2 cross-check (pocketminer_nr4a3_result.json) so the two are comparable.")},
    "models_scored": models,
    "per_conformer": per,
    **agg,
}
with open(os.path.join(out, "nr4a3-8xtt-pocketminer.json"), "w") as fh:
    json.dump(result, fh, indent=2)
print(json.dumps({"verdict": agg["verdict"], "n_conformers_scored": agg["n_conformers_scored"],
                  "enrichment_median": agg["enrichment_distribution"].get("median")}, indent=2), flush=True)
'''


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--models", default=os.environ.get("PM8_MODELS", "2,8,20,6"),
                    help="8XTT conformers to score: '2,8,20,6' (default) or 'all'")
    ap.add_argument("--tf-version", default="", help="override PocketMiner TensorFlow version")
    a = ap.parse_args()
    # Args carry the knobs into the container (runner env vars do NOT propagate to the SageMaker job).
    if a.tf_version:
        os.environ["PM_TF_VERSION"] = a.tf_version
    os.makedirs(OUT, exist_ok=True)

    _sh(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)
    _sh(["git", "clone", "--depth", "1", "--branch", a.git_ref, REPO, "/tmp/repo"], check=True)
    repo_mod = "/tmp/repo/research/modalities"
    sys.path.insert(0, repo_mod)
    import nr4a3_8xtt_benchmark as bm
    import nr4a3_8xtt_pocketminer as p8

    work = os.path.join(OUT, "pm8_run")
    os.makedirs(work, exist_ok=True)
    xtt = _fetch(f"https://files.rcsb.org/download/{bm.PDB_ID}.pdb", os.path.join(work, f"{bm.PDB_ID}.pdb"))
    af2 = _fetch_af2(os.path.join(work, "AF-Q92570.pdb"))

    models = bm.split_models(open(xtt).read())
    if not models:
        sys.exit(f"  ABORT: no models parsed from {bm.PDB_ID}")
    chosen = p8.select_models(range(1, len(models) + 1), a.models)
    print(f"  {bm.PDB_ID}: {len(models)} conformers; scoring models {chosen}", flush=True)
    conf_root = os.path.join(work, "conformers")
    os.makedirs(conf_root, exist_ok=True)
    conf_pdbs = {}
    for m in chosen:
        cdir = os.path.join(conf_root, f"conf_{m}")
        os.makedirs(cdir, exist_ok=True)
        # PocketMiner md.load reads a normal single-model PDB; the split model text is protein ATOM + END.
        pdb = os.path.join(cdir, f"8xtt_m{m}.pdb")
        with open(pdb, "w") as fh:
            fh.write(models[m - 1])
        conf_pdbs[m] = (cdir, pdb)

    # PocketMiner env + repo.
    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    _build_pm_env(conda, None)
    pm_repo = "/tmp/pocketminer"
    _sh(["git", "clone", "--depth", "1", "--branch", pm_entry.PM_BRANCH, pm_entry.PM_REPO, pm_repo],
        check=True)
    src = os.path.join(pm_repo, "src")
    if not os.path.exists(os.path.join(pm_repo, "models", "pocketminer.index")):
        sys.exit("  ABORT: PocketMiner weights not found in the cloned repo")
    driver_path = os.path.join(src, "nr4a3_pm_driver.py")
    with open(driver_path, "w") as fh:
        fh.write(pm_entry.DRIVER)     # reuse the validated inference driver

    # Run PocketMiner per conformer.
    for m, (cdir, pdb) in conf_pdbs.items():
        env = os.environ.copy()
        env["PM_PDB"] = os.path.abspath(pdb)
        env["PM_OUT"] = os.path.abspath(cdir)
        env["PM_NN"] = "../models/pocketminer"
        r = _sh([conda, "run", "--no-capture-output", "-n", "pm", "python", "nr4a3_pm_driver.py"],
                cwd=src, env=env)
        if r.returncode != 0:
            print(f"  WARNING: PocketMiner inference failed on model {m} (exit {r.returncode})",
                  file=sys.stderr, flush=True)

    # Final map + analysis in the pm env (biopython present), importing our pure modules.
    analysis_path = os.path.join(work, "pm8_analysis.py")
    with open(analysis_path, "w") as fh:
        fh.write(ANALYSIS)
    env = os.environ.copy()
    env["PYTHONPATH"] = repo_mod + os.pathsep + env.get("PYTHONPATH", "")
    env["PM8_CONF_ROOT"] = conf_root
    env["PM8_AF2"] = af2
    env["PM8_XTT"] = xtt
    env["PM8_OUT"] = OUT
    env["PM8_MODEL_LIST"] = ",".join(str(m) for m in chosen)
    r = _sh([conda, "run", "--no-capture-output", "-n", "pm", "python", analysis_path], env=env)
    if r.returncode != 0:
        sys.exit(f"  ABORT: 8XTT PocketMiner analysis failed (exit {r.returncode})")
    out_json = os.path.join(OUT, "nr4a3-8xtt-pocketminer.json")
    print(f"  wrote {out_json} ({os.path.getsize(out_json)} bytes)" if os.path.exists(out_json)
          else "  WARNING: no result JSON produced", flush=True)


if __name__ == "__main__":
    main()
