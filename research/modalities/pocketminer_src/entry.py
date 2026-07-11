#!/usr/bin/env python3
"""SageMaker entry — runs the PocketMiner cryptic-pocket GNN on the APO NR4A3 LBD, in-job.

WHY. Our degrader case claims the "undruggable" NR4A3 LBD harbours a cryptic druggable pocket, shown
with OUR OWN metadynamics + fpocket. PocketMiner (Meller et al., Nat Commun 2023; a GVP graph neural
network trained on a SEPARATE cryptic-pocket MD dataset) predicts cryptic-pocket-forming residues from a
SINGLE static structure. If, run on the APO / pre-metadynamics AF2 LBD, it independently flags the same
Pocket-5 site, that is orthogonal corroboration from a method that shares no code or data with our route.

CIRCULARITY GUARD (critical). The input MUST be the apo AF2 model (AFDB AF-Q92570, LBD residues 373-626),
NOT any metadynamics-opened frame — feeding an opened structure would make the corroboration circular.
By default this job FETCHES AF-Q92570 fresh from the AlphaFold DB and trims to the LBD, so the input is
provably the pre-metad apo structure. (A PDB mounted at the input channel is used only if PM_ALLOW_INPUT_PDB=1.)

PIPELINE. (1) obtain apo AF2 LBD PDB -> (2) clone Mickdub/gvp @ pocket_pred (MIT) + its in-repo weights
-> (3) build the TensorFlow/GVP conda env -> (4) run PocketMiner inference (per-residue cryptic scores)
-> (5) map scores back to UniProt numbering, compute overlap vs our fpocket Pocket-5 lining residues ->
(6) write pocketminer_nr4a3_result.json to sm_io.out_dir() (spot Training checkpoint dir, continuous S3 sync).

CPU work (small GNN inference; ~seconds of compute). No GPU needed.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request

import sm_io
OUT = sm_io.out_dir()   # spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing → legacy path
IN = sm_io.channel("input")

# NR4A3 / NOR-1, human canonical. LBD window per UniProt/InterPro (matches nr4a3_structure.py).
UNIPROT = "Q92570"
LBD_FIRST, LBD_LAST = 373, 626
AFDB_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"

# fpocket "Pocket-5" lining residues on the AF2 model (Q92570 numbering). Source of truth:
# nr4a3_resistance_map.py / nr4a3_fpocket_enumerate.py. The 7 selectivity handles are a subset.
POCKET5 = [406, 407, 410, 411, 412, 481, 484, 485, 531, 534]
HANDLES = [406, 407, 410, 412, 484, 531, 534]

# PocketMiner source (published; MIT). Weights ship IN-REPO under models/pocketminer (checkpoint:
# pocketminer.index + pocketminer.data-00000-of-00001), so no separate weights download step.
PM_REPO = os.environ.get("PM_REPO", "https://github.com/Mickdub/gvp")
PM_BRANCH = os.environ.get("PM_BRANCH", "pocket_pred")
# High-confidence probability cutoff for calling a residue "cryptic-pocket-forming". PocketMiner emits a
# per-residue probability in [0,1]; report several cutoffs so the overlap claim isn't threshold-cherry-picked.
HIGH = float(os.environ.get("PM_HIGH_CUTOFF", "0.7"))
MODERATE = float(os.environ.get("PM_MOD_CUTOFF", "0.5"))


def _sh(cmd, **kw):
    print("  $ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, **kw)


def fetch_apo_af2_lbd(dest_full, dest_lbd):
    """Download the apo AF2 model for Q92570 from AFDB and trim to the LBD (residues 373-626), keeping the
    original UniProt residue numbering. This is the pre-metadynamics apo structure (non-circular input)."""
    api = AFDB_API.format(acc=UNIPROT)
    print(f"  resolving AFDB entry {api}", flush=True)
    with urllib.request.urlopen(api, timeout=60) as r:
        data = json.load(r)
    url = data[0]["pdbUrl"]
    print(f"  downloading apo AF2 model {url}", flush=True)
    urllib.request.urlretrieve(url, dest_full)
    _trim_lbd(dest_full, dest_lbd)
    return dest_lbd


def _trim_lbd(src_pdb, dst_pdb):
    """Keep only ATOM records of the single AF chain whose residue number is within the LBD window.
    Preserves original resSeq numbering so predictions map straight back to UniProt positions."""
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
    print(f"  trimmed LBD -> {dst_pdb}: {len(resset)} residues "
          f"({min(resset)}-{max(resset)})", flush=True)


def build_env(conda, repo):
    """Create the PocketMiner conda env. The repo's own pocketminer.yml drops version pins (the authors
    found unpinned worked better across OSes), but TF/numpy compat is fragile — so we pin to a
    known-good combo (TF 2.9.1 is one of the authors' tested versions; numpy<1.24 for TF 2.9). Override
    via PM_TF_VERSION / PM_PY_VERSION if a shakeout run shows a conflict."""
    py = os.environ.get("PM_PY_VERSION", "3.9")
    tf = os.environ.get("PM_TF_VERSION", "2.9.1")
    # TF 2.9 needs numpy<1.24; newer mdtraj (>=1.10) demands numpy>=1.25 — a hard conflict. Pin BOTH
    # mdtraj<1.10 AND numpy<1.24 (plus netCDF4, which mdtraj wants) in the SAME conda solve so nothing gets
    # silently downgraded under mdtraj's compiled extensions (the ABI mismatch the first shakeout exposed).
    # Install TF via pip WITHOUT a numpy pin so it accepts conda's numpy instead of re-resolving it.
    _sh([conda, "create", "-y", "-n", "pm", "-c", "conda-forge",
         f"python={py}", "mdtraj<1.10", "numpy<1.24", "netcdf4", "pip"], check=True)
    _sh([conda, "run", "--no-capture-output", "-n", "pm", "pip", "install", "--quiet",
         "--upgrade-strategy", "only-if-needed",
         f"tensorflow=={tf}", "scipy", "pandas", "tqdm", "pyyaml"], check=True)


DRIVER = r'''
"""Generated in-job driver — runs PocketMiner on ONE structure and dumps preds + residue order.
Must run with cwd=<repo>/src so the relative imports (models, validate_performance_on_xtals) resolve."""
import json, os
import numpy as np
import mdtraj as md
from models import MQAModel
from validate_performance_on_xtals import process_strucs, predict_on_xtals

pdb = os.environ["PM_PDB"]
out = os.environ["PM_OUT"]
nn_path = os.environ.get("PM_NN", "../models/pocketminer")

# Hyperparameters are fixed by the released checkpoint (from xtal_predict.py).
model = MQAModel(node_features=(8, 50), edge_features=(1, 32),
                 hidden_dim=(16, 100), num_layers=4, dropout=0.1)
# process_strucs expects a list of LOADED mdtraj trajectories (it calls s.top on each), NOT path strings —
# passing [pdb] raised "'str' object has no attribute 'top'". Load first, then reuse for residue order.
traj = md.load(pdb)
X, S, mask = process_strucs([traj])
preds = np.asarray(predict_on_xtals(model, nn_path, X, S, mask)).squeeze()
if preds.ndim > 1:
    preds = preds[0]
np.save(os.path.join(out, "nr4a3_lbd-preds.npy"), preds)
np.savetxt(os.path.join(out, "nr4a3_lbd-predictions.txt"), preds, fmt="%.4g", delimiter="\n")

# Residue-order read from the SAME loaded trajectory so scores map exactly to UniProt resSeq.
resseq = [r.resSeq for r in traj.topology.residues]
json.dump({"resSeq": resseq, "n_pred": int(preds.shape[0])},
          open(os.path.join(out, "residue_order.json"), "w"))
print(f"[driver] predicted {preds.shape[0]} residues; topology residues {len(resseq)}", flush=True)
'''


def analyse(preds, resseq):
    """Map per-residue scores to UniProt numbering and compute overlap with our fpocket Pocket-5 site."""
    import statistics as st
    n = min(len(preds), len(resseq))
    if len(preds) != len(resseq):
        print(f"  WARNING: preds ({len(preds)}) != residue order ({len(resseq)}); zipping first {n} "
              "in file order. Inspect residue_order.json before trusting the mapping.", flush=True)
    score = {resseq[i]: float(preds[i]) for i in range(n)}

    def flagged(cut):
        return sorted(r for r, s in score.items() if s >= cut)

    lbd_scores = list(score.values())
    p5_scores = {r: score.get(r) for r in POCKET5 if r in score}
    p5_vals = [v for v in p5_scores.values() if v is not None]
    ranked = sorted(score.items(), key=lambda kv: kv[1], reverse=True)
    top15 = [r for r, _ in ranked[:15]]
    # percentile rank of each Pocket-5 residue among all LBD residues (1.0 = highest-scoring)
    order = [r for r, _ in ranked]
    pct = {r: round(1 - order.index(r) / len(order), 3) for r in p5_scores if r in order}

    hi, mod = flagged(HIGH), flagged(MODERATE)
    lbd_mean = round(st.mean(lbd_scores), 4) if lbd_scores else None
    p5_mean = round(st.mean(p5_vals), 4) if p5_vals else None
    p5_max = round(max(p5_vals), 4) if p5_vals else None
    return {
        "n_residues_scored": n,
        "per_residue_scores": {str(r): round(s, 4) for r, s in sorted(score.items())},
        "score_cutoffs": {"high": HIGH, "moderate": MODERATE},
        "flagged_high": hi,
        "flagged_moderate": mod,
        "top15_residues": top15,
        "pocket5_residues": POCKET5,
        "pocket5_handles": HANDLES,
        "pocket5_scores": {str(r): round(v, 4) for r, v in p5_scores.items()},
        "pocket5_percentile_rank": pct,
        "overlap": {
            "pocket5_in_flagged_high": sorted(set(POCKET5) & set(hi)),
            "pocket5_in_flagged_moderate": sorted(set(POCKET5) & set(mod)),
            "frac_pocket5_high": round(len(set(POCKET5) & set(hi)) / len(POCKET5), 3),
            "frac_pocket5_moderate": round(len(set(POCKET5) & set(mod)) / len(POCKET5), 3),
            "pocket5_mean_score": p5_mean,
            "pocket5_max_score": p5_max,
            "lbd_mean_score": lbd_mean,
            "enrichment_pocket5_over_lbd": (round(p5_mean / lbd_mean, 2)
                                            if p5_mean and lbd_mean else None),
        },
        "_interpretation": (
            "Independent corroboration is supported to the extent PocketMiner's high-confidence "
            "cryptic-pocket residues (flagged_high) overlap Pocket-5 and/or Pocket-5 scores are enriched "
            "over the LBD background (enrichment > ~1). Report the numbers honestly: partial overlap or "
            "modest enrichment is a weaker-but-real signal, not a null. This is a single static-structure "
            "prediction, not a replacement for the metadynamics evidence."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdb-name", default="AF-Q92570.pdb",
                    help="filename to look for at the input channel if PM_ALLOW_INPUT_PDB=1")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    _sh(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git)"], check=False)

    work = os.path.join(OUT, "pm_run")
    os.makedirs(work, exist_ok=True)
    full_pdb = os.path.join(work, "AF-Q92570_full.pdb")
    lbd_pdb = os.path.join(work, "nr4a3_lbd_apo.pdb")

    # Input structure. DEFAULT = fetch fresh apo AF2 (guaranteed pre-metad, non-circular). Only use a
    # mounted PDB if explicitly allowed AND it exists (still trimmed to the LBD window here).
    mounted = os.path.join(IN, a.pdb_name)
    if os.environ.get("PM_ALLOW_INPUT_PDB") == "1" and os.path.exists(mounted):
        print(f"  PM_ALLOW_INPUT_PDB=1: trimming mounted {mounted} (verify it is the APO model!)", flush=True)
        shutil.copy(mounted, full_pdb)
        _trim_lbd(full_pdb, lbd_pdb)
        input_source = f"mounted:{a.pdb_name} (trimmed to {LBD_FIRST}-{LBD_LAST})"
    else:
        fetch_apo_af2_lbd(full_pdb, lbd_pdb)
        input_source = f"AFDB AF-{UNIPROT} apo model, LBD {LBD_FIRST}-{LBD_LAST} (pre-metadynamics)"

    # Clone PocketMiner (repo carries the weights in-tree).
    repo = "/tmp/pocketminer"
    _sh(["git", "clone", "--depth", "1", "--branch", PM_BRANCH, PM_REPO, repo], check=True)
    src = os.path.join(repo, "src")
    weights = os.path.join(repo, "models", "pocketminer.index")
    if not os.path.exists(weights):
        sys.exit(f"  ABORT: PocketMiner weights not found at {weights} — the in-repo checkpoint moved; "
                 "check models/ in the cloned repo and set PM_NN accordingly.")

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    build_env(conda, repo)

    # Write the driver into src/ (relative imports need cwd=src) and run it in the pm env.
    driver_path = os.path.join(src, "nr4a3_pm_driver.py")
    with open(driver_path, "w") as fh:
        fh.write(DRIVER)
    env = os.environ.copy()
    env["PM_PDB"] = os.path.abspath(lbd_pdb)
    env["PM_OUT"] = os.path.abspath(work)
    env["PM_NN"] = "../models/pocketminer"
    r = _sh([conda, "run", "--no-capture-output", "-n", "pm", "python", "nr4a3_pm_driver.py"],
            cwd=src, env=env)
    if r.returncode != 0:
        sys.exit(f"  ABORT: PocketMiner inference failed (exit {r.returncode}) — likely TF/numpy env "
                 "fragility; see run notes, try PM_TF_VERSION / PM_PY_VERSION overrides.")

    import numpy as np
    preds = np.load(os.path.join(work, "nr4a3_lbd-preds.npy")).reshape(-1).tolist()
    resseq = json.load(open(os.path.join(work, "residue_order.json")))["resSeq"]
    analysis = analyse(preds, resseq)

    result = {
        "_title": "PocketMiner cryptic-pocket prediction on the apo NR4A3 LBD (independent cross-check)",
        "_input": {
            "source": input_source,
            "uniprot": UNIPROT,
            "lbd_window": [LBD_FIRST, LBD_LAST],
            "circularity_guard": "apo pre-metadynamics AF2 structure; NOT a metad-opened frame",
        },
        "_method": {
            "tool": "PocketMiner (GVP graph neural network)",
            "citation": "Meller et al., Nat Commun 14:1177 (2023)",
            "repo": PM_REPO, "branch": PM_BRANCH,
            "weights": "in-repo models/pocketminer checkpoint (.index + .data-00000-of-00001)",
            "license": "MIT (Meller/Bowman et al. 2022; bundled GVP + Ingraham code also MIT)",
            "output": "per-residue cryptic-pocket probability in [0,1]",
            "env": f"python={os.environ.get('PM_PY_VERSION','3.9')}, "
                   f"tensorflow=={os.environ.get('PM_TF_VERSION','2.9.1')}, numpy<1.24, mdtraj",
        },
        **analysis,
    }
    out_json = os.path.join(OUT, "pocketminer_nr4a3_result.json")
    with open(out_json, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"  wrote {out_json}", flush=True)
    print(json.dumps({k: result[k] for k in ("overlap",)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
