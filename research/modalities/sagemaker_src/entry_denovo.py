#!/usr/bin/env python3
"""SageMaker entry for STEP 2 — DiffSBDD pocket-conditioned NR4A3 warhead generation (nr4a3_denovo.py). GPU.

Builds the DiffSBDD environment, clones DiffSBDD + our repo, downloads the pretrained CrossDocked
checkpoint, and runs nr4a3_denovo.py against the Step-0 druggable-release receptor (mounted at
/opt/ml/processing/input/receptor). SageMaker uploads /opt/ml/processing/output (nr4a3-denovo.json + SDF +
plot) on completion.

ENV / DRIVER GOTCHA (the MM-GBSA lesson, inverted). DiffSBDD's pinned stack is torch 1.12.1 / PyG 2.0.9 /
pytorch-lightning 1.7.4 / RDKit 2022.03, built for **CUDA 10.2** — which does NOT support the g5's A10G
(Ampere, sm_86; CUDA 10.2 predates Ampere). So we install those SAME pinned versions but with the **+cu116**
builds (CUDA 11.6 supports sm_86, and 11.6 is OLDER than the instance driver so there is no PTX-version
problem like the newest builds hit). This keeps DiffSBDD's model code on the versions it was written for
while running on the hardware. RDKit + OpenBabel come from conda (RDKit's SA_Score sascorer needs
RDConfig.RDContribDir, which the conda build ships). NO CPU FALLBACK: we probe torch.cuda up front and die
fast if the GPU isn't usable (DiffSBDD on CPU would grind for hours) — mirroring the MM-GBSA no-CPU rule.
"""
import os
import shutil
import subprocess
import sys
import time

OUT = "/opt/ml/processing/output"
CKPT_DIR = "/opt/ckpt"
DIFFSBDD_DIR = "/opt/diffsbdd"
DEFAULT_CKPT_URL = "https://zenodo.org/record/8183747/files/crossdocked_fullatom_cond.ckpt?download=1"


def _run(cmd, timeout, label, **kw):
    """Run a step with a hard timeout + elapsed print; fail loud (never a silent grind)."""
    print(f"[sagemaker] >>> {label} (timeout {timeout}s)", flush=True)
    t0 = time.time()
    r = subprocess.run(cmd, timeout=timeout, **kw)
    print(f"[sagemaker] <<< {label} done in {int(time.time() - t0)}s (exit {r.returncode})", flush=True)
    if r.returncode != 0:
        sys.exit(f"[sagemaker] ABORT: {label} failed (exit {r.returncode})")
    return r


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default="main")
    ap.add_argument("--n-samples", default="200")
    ap.add_argument("--campaign", default="selective")
    ap.add_argument("--ckpt-url", default=DEFAULT_CKPT_URL)
    ap.add_argument("--diffsbdd-ref", default="main", help="DiffSBDD repo ref to clone")
    args = ap.parse_args()

    subprocess.run(["nvidia-smi"], check=False)
    subprocess.run(["bash", "-c", "command -v git || (apt-get update && apt-get install -y git curl)"],
                   check=False)
    _run(["git", "clone", "--depth", "1", "--branch", args.git_ref,
          "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], 600, "clone repo")
    _run(["git", "clone", "--depth", "1", "--branch", args.diffsbdd_ref,
          "https://github.com/arneschneuing/DiffSBDD", DIFFSBDD_DIR], 600, "clone DiffSBDD")
    work = "/tmp/repo/research/modalities"

    conda = shutil.which("conda") or "/opt/conda/bin/conda"
    # conda layer: RDKit (+ SA_Score contrib) + OpenBabel + the non-torch deps; CUDA comes via pip wheels.
    # biopython=1.79: DiffSBDD imports Bio.PDB.Polypeptide.three_to_one, which Biopython >=1.80 REMOVED.
    # 1.79 is the last release with that API (and any sibling three_to_one/one_to_three calls DiffSBDD uses).
    _run([conda, "create", "-y", "-n", "diffsbdd", "-c", "conda-forge", "python=3.10",
          "rdkit=2022.03", "openbabel", "biopython=1.79", "scipy", "numpy<2", "networkx", "pandas",
          "libstdcxx-ng", "pip"],
         1800, "conda create diffsbdd env")

    def pip(pkgs, timeout, label, extra=()):
        _run([conda, "run", "--no-capture-output", "-n", "diffsbdd", "pip", "install", "--no-cache-dir",
              *extra, *pkgs], timeout, label)

    # torch 1.12.1 + cu116 (Ampere-capable; older than the driver so no PTX problem), then the matching
    # PyG companion wheels from the torch-1.12.1+cu116 index, then DiffSBDD's framework deps.
    pip(["torch==1.12.1+cu116"], 1800, "pip torch 1.12.1+cu116",
        extra=("--extra-index-url", "https://download.pytorch.org/whl/cu116"))
    pip(["torch-scatter==2.0.9", "torch-sparse==0.6.15", "torch-cluster==1.6.0"], 1800,
        "pip PyG companion wheels (torch-1.12.1+cu116)",
        extra=("-f", "https://data.pyg.org/whl/torch-1.12.1+cu116.html"))
    # pytorch-lightning 1.7.4 (the version DiffSBDD's code targets) ships legacy "torch (>=1.9.*)" metadata
    # that pip>=24.1 rejects; downgrade pip in-env first so the pinned PL installs (the project README's
    # own "Please use pip<24.1" guidance).
    pip(["pip<24.1"], 300, "downgrade pip <24.1 (legacy PL 1.7.4 metadata)")
    # CRITICAL: re-pin torch (and torchmetrics, which pytorch-lightning pulls) IN THIS command so the
    # resolver does NOT upgrade torch. Run 2 silently bumped torch 1.12.1+cu116 -> 2.12.1+cu130 here
    # (via torchmetrics' newest build), and cu130 needs a CUDA-13 driver the g5 (driver 12.8) lacks ->
    # the GPU probe caught it (cuda_available False, fail-fast). torchmetrics 0.9.3 is the torch-1.12-era
    # build PL 1.7.4 accepts (>=0.7.0); keeping the cu116 index lets torch stay pinned.
    # setuptools<81: v81 (2025) REMOVED the bundled pkg_resources, which pytorch-lightning 1.7.4 imports
    # at startup (ModuleNotFoundError otherwise). 80.9.0 is the last with it.
    pip(["torch==1.12.1+cu116", "torchmetrics==0.9.3", "torch-geometric==2.1.0",
         "pytorch-lightning==1.7.4", "setuptools<81", "wandb", "seaborn", "imageio"],
        1200, "pip DiffSBDD framework deps (torch + torchmetrics + setuptools pinned)",
        extra=("--extra-index-url", "https://download.pytorch.org/whl/cu116"))

    # Fail-fast GPU probe — no CPU grind (the MM-GBSA no-CPU rule).
    _run([conda, "run", "--no-capture-output", "-n", "diffsbdd", "python", "-c",
          "import torch,sys; ok=torch.cuda.is_available(); "
          "print('[probe] torch',torch.__version__,'cuda_available',ok,'dev',"
          "torch.cuda.get_device_name(0) if ok else None); sys.exit(0 if ok else 42)"],
         300, "GPU probe (torch.cuda)")

    # Download the pretrained checkpoint (retry; verify non-trivial size).
    os.makedirs(CKPT_DIR, exist_ok=True)
    ckpt = os.path.join(CKPT_DIR, "crossdocked_fullatom_cond.ckpt")
    _run(["bash", "-c",
          f"for i in 1 2 3 4; do curl -fL --retry 3 -o '{ckpt}' '{args.ckpt_url}' && break || sleep $((2**i)); done; "
          f"test -s '{ckpt}' && [ $(stat -c%s '{ckpt}') -gt 1000000 ]"],
         1800, "download DiffSBDD checkpoint")

    env = os.environ.copy()
    # The SageMaker container puts the BASE conda's older libstdc++ ahead of the env's on the load path,
    # so matplotlib's compiled ext (pulled by seaborn) can't find CXXABI_1.3.15. Prepend the env lib dir
    # so the diffsbdd env's newer libstdc++ wins (propagates to the generate_ligands subprocess too).
    env["LD_LIBRARY_PATH"] = "/opt/conda/envs/diffsbdd/lib:" + env.get("LD_LIBRARY_PATH", "")
    env["RECEPTOR_DIR"] = "/opt/ml/processing/input/receptor"
    env["DIFFSBDD_DIR"] = DIFFSBDD_DIR
    env["CKPT"] = ckpt
    env["OUTPUT_DIR"] = OUT
    env["N_SAMPLES"] = args.n_samples
    env["CAMPAIGN"] = args.campaign
    os.makedirs(OUT, exist_ok=True)
    print(f"[sagemaker] running de-novo generation (campaign={args.campaign}, n={args.n_samples})", flush=True)
    r = subprocess.run([conda, "run", "--no-capture-output", "-n", "diffsbdd",
                        "python", "nr4a3_denovo.py"], cwd=work, env=env)
    for f in sorted(os.listdir(OUT)):
        print(f"[sagemaker] output {f} ({os.path.getsize(os.path.join(OUT, f))} bytes)", flush=True)
    print(f"[sagemaker] de-novo exit={r.returncode}", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
