#!/usr/bin/env python3
"""
NR4A3 LBD BioEmu cryptic-pocket cross-check — Vast.ai launcher (method-watch trigger, BioEmu v1.4.0, 2026-07-20).

Rents ONE Vast GPU instance (baked triskit23/bioemu image), which: pulls the repo tarball, samples a BioEmu
equilibrium ensemble of the 254-residue NR4A3 LBD from sequence, reconstructs side chains (HPacker via
bioemu.sidechain_relax), renumbers to UniProt Q92570 numbering, runs the IDENTICAL harmonized Pocket-5 detector
used for the metad/release ensembles (nr4a3_bioemu_pocket.py), uploads the result JSON to S3, and self-destroys
(VastBackend's key-free EXIT trap halts GPU billing; CI reap destroys the instance).

WHY this is a valid cross-check: BioEmu is an ORTHOGONAL generator (a learned diffusion emulator of equilibrium
ensembles — NOT physics-based enhanced sampling), so an independent-method estimate of the fraction of frames
that open the Pocket-5 cryptic site to a druggable state (D*>=0.53) tests the metadynamics result (0.68) and the
unbiased-release corroboration (pooled 0.587). Integrity: BioEmu IS validated on the bioemu-benchmarks cryptic-
pocket set, but its APO recall (~50%) is its weakest regime and it is not quantitatively calibrated on rare
opening populations (JCTC 2026, 10.1021/acs.jctc.6c00135) — so this is a QUALITATIVE independent-method
corroboration of the site's openability, read honestly, not a population estimate and not a replacement for the
physics-based evidence.

PILOT/SMOKE-FIRST (standing rules): MODE=smoke runs the tiny chignolin sequence (10 aa, few samples) through the
WHOLE chain (sample -> sidechain_relax -> prepare -> fpocket -> S3) to prove the image + plumbing on one cheap
host before the real 254-residue run. build_jobspec is PURE + unit-tested; submit() needs live VAST_API_KEY+AWS.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, get_backend, s3_checkpoint_uri  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
VAST_IMAGE = os.environ.get("VAST_IMAGE") or "docker.io/triskit23/bioemu:latest"
RESULT_PREFIX = os.environ.get("BIOEMU_RESULT_PREFIX", "nr4a3-bioemu-crosscheck")

# The NR4A3 LBD construct: UniProt Q92570 residues 373..626 (254 aa), read from the AF2 model AF-Q92570.pdb
# (the pre-metadynamics apo structure — feeding sequence, not the opened structure, keeps this non-circular).
NR4A3_LBD_SEQ = (
    "RLPSKPKSPLQQEPSQPSPPSPPICMMNALVRALTDSTPRDLDYSRYCPTDQAAAGTDAEHVQQFYNLLTASIDVSRSWAEKIPGFTDLPKEDQTLLIE"
    "SAFLELFVLRLSIRSNTAEDKFVFCNGLVLHRLQCLRGFGEWLDSIKDFSLNLQSLNLDIQALACLSALSMITERHGLKEPKRVEELCNKITSSLKDHQ"
    "SKGQALEPTESKVLGALVELRKICTLGLQRIFYLKLEDLVSPPSIIDKLFLDTLPF"
)
CHIGNOLIN_SEQ = "GYDPETGTWG"  # BioEmu README smoke sequence

# 24 GB Ada 4090 (BioEmu README benchmarked A100 80 GB, but v1.4.0's min-batch-1 lets 254 aa fit at small batch;
# fall back to a100 via GPU=a100 if a real run OOMs). We are not racing (one-shot cross-check), interruptible is
# fine — a preemption just re-runs from scratch (cheap, minutes) since a single ensemble isn't per-unit resumable.
RES = ResourceSpec(gpu=os.environ.get("BIOEMU_GPU", "rtx4090"), min_vram_gb=int(os.environ.get("BIOEMU_VRAM", "24")),
                   vcpus=4, ram_gb=24, disk_gb=60, min_cuda=12.4, interruptible=True)

# The onstart pipeline. VastBackend._vast_onstart exports the forwarded AWS creds (S3) + arms the self-destroy
# EXIT trap; this command does the science and uploads. $VARS come from spec.env. Note: no `set -e` on the whole
# script — we want the S3 upload of whatever we produced to run even if a late step warns; the per-step `||exit`
# guards the load-bearing stages explicitly.
_PIPELINE = r"""
set -o pipefail
export HOME=/root
export PATH=/opt/mamba/envs/bioemu/bin:$PATH
echo "[bioemu] $(date -u +%FT%TZ) start mode=$MODE samples=$NUM_SAMPLES seq_len=${#SEQUENCE}"
mark() { echo "$1 $(date -u +%FT%TZ)" | aws s3 cp - "$RESULT_S3/phase.txt" 2>/dev/null || true; }
mark start
# --- repo code (public codeload tarball; scorer + prepare live in research/modalities) ---
cd /root
curl -Ls "{repo}/archive/refs/heads/$GIT_BRANCH.tar.gz" | tar xz || { echo "repo pull failed"; exit 3; }
cd Rare-cancers-*/research/modalities || exit 3
mark cloned
mkdir -p /tmp/be /tmp/frames /tmp/out
# --- 1) BioEmu equilibrium ensemble from sequence (inlined ColabFold retrieves the MSA; AF2 weights auto-cache) ---
python -m bioemu.sample --sequence "$SEQUENCE" --num_samples "$NUM_SAMPLES" \
       --batch_size_100 "$BATCH_SIZE_100" --output_dir /tmp/be || { echo "bioemu.sample failed"; exit 4; }
mark sampled
ls -la /tmp/be || true
# --- 2) side-chain reconstruction (HPacker) -> all-atom topology + trajectory (fpocket needs all-atom) ---
python -m bioemu.sidechain_relax --pdb-path /tmp/be/topology.pdb --xtc-path /tmp/be/samples.xtc \
       --outpath /tmp/be || { echo "sidechain_relax failed"; exit 5; }
mark sidechains
ls -la /tmp/be || true
# resolve the reconstructed topology+trajectory (prefer HPacker rec; naming is samples_sidechain_rec.{pdb,xtc})
REC_PDB=$(ls /tmp/be/*sidechain_rec*.pdb 2>/dev/null | head -1)
REC_XTC=$(ls /tmp/be/*sidechain_rec*.xtc 2>/dev/null | head -1)
[ -z "$REC_XTC" ] && REC_XTC=$(ls /tmp/be/*sidechain_rec*.dcd 2>/dev/null | head -1)
echo "[bioemu] reconstructed topology=$REC_PDB traj=$REC_XTC"
[ -n "$REC_PDB" ] && [ -n "$REC_XTC" ] || { echo "no reconstructed all-atom output found"; ls -la /tmp/be; exit 6; }
# --- 3) renumber 1..254 -> UniProt 373..626 and split into per-frame all-atom PDBs ---
python nr4a3_bioemu_prepare.py --topology "$REC_PDB" --trajectory "$REC_XTC" --out /tmp/frames \
       || { echo "prepare failed"; exit 7; }
mark prepared
# --- 4) IDENTICAL harmonized Pocket-5 detector used for metad/release (POCKET_MATCH_MODE=harmonized forced) ---
META=$(printf '{"model":"bioemu","image":"%s","mode":"%s","num_samples":%s,"batch_size_100":%s,"git_branch":"%s"}' \
       "$VAST_IMAGE_TAG" "$MODE" "$NUM_SAMPLES" "$BATCH_SIZE_100" "$GIT_BRANCH")
python nr4a3_bioemu_pocket.py --frames /tmp/frames --out /tmp/out/bioemu-crosscheck.json --meta "$META" \
       || { echo "scorer failed"; exit 8; }
mark scored
# --- 5) upload results (result JSON + the reconstructed topology for provenance/spot-checks) ---
aws s3 cp /tmp/out/bioemu-crosscheck.json "$RESULT_S3/bioemu-crosscheck.json" || echo "result upload failed"
aws s3 cp "$REC_PDB" "$RESULT_S3/topology_sidechain_rec.pdb" 2>/dev/null || true
mark done
echo "[bioemu] $(date -u +%FT%TZ) DONE"
"""


def build_jobspec(mode="real", num_samples=None, batch_size_100=None, git_branch=None, result_prefix=None):
    """PURE construction of the JobSpec (no network). `mode` in {real, smoke}."""
    smoke = mode == "smoke"
    seq = CHIGNOLIN_SEQ if smoke else NR4A3_LBD_SEQ
    n = num_samples if num_samples is not None else (5 if smoke else 200)
    batch = batch_size_100 if batch_size_100 is not None else (5 if smoke else 10)
    branch = git_branch or os.environ.get("GIT_BRANCH") or "claude/nr4a3-lbd-bioemu-validation-w421nb"
    name = f"nr4a3-bioemu-{'smoke' if smoke else 'crosscheck'}"
    prefix = result_prefix or RESULT_PREFIX
    result_s3 = f"s3://{os.environ.get('VAST_CKPT_BUCKET', 'sagemaker-us-east-2-646605541856')}/{prefix}/{name}"
    command = ["bash", "-lc", _PIPELINE.replace("{repo}", REPO)]
    env = {
        "MODE": mode,
        "SEQUENCE": seq,
        "NUM_SAMPLES": str(n),
        "BATCH_SIZE_100": str(batch),
        "GIT_BRANCH": branch,
        "RESULT_S3": result_s3,
        "VAST_IMAGE_TAG": VAST_IMAGE,
    }
    return JobSpec(
        name=name,
        command=command,
        image=VAST_IMAGE,
        checkpoint_uri=result_s3,     # reused S3 prefix; a single ensemble isn't per-unit resumable, so RESUME off
        resume=False,
        resources=RES,
        max_runtime_s=int(os.environ.get("BIOEMU_MAX_RUNTIME_S", "10800")),  # 3 h anti-idle watchdog cap
        env=env,
    )


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Launch the NR4A3 BioEmu cryptic-pocket cross-check on Vast.ai")
    ap.add_argument("--mode", choices=["real", "smoke"], default=os.environ.get("BIOEMU_MODE", "real"))
    ap.add_argument("--num-samples", type=int, default=None)
    ap.add_argument("--batch-size-100", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true", help="print the JobSpec and exit (no rental)")
    args = ap.parse_args()

    spec = build_jobspec(mode=args.mode, num_samples=args.num_samples, batch_size_100=args.batch_size_100)
    print(f"[launch] mode={args.mode} image={spec.image} result={spec.env['RESULT_S3']}")
    print(f"[launch] seq_len={len(spec.env['SEQUENCE'])} num_samples={spec.env['NUM_SAMPLES']} "
          f"batch_size_100={spec.env['BATCH_SIZE_100']} gpu={spec.resources.gpu}")
    if args.dry_run:
        print(json.dumps({"name": spec.name, "image": spec.image, "env": spec.env,
                          "resources": spec.resources.__dict__, "max_runtime_s": spec.max_runtime_s}, indent=2))
        return
    backend = get_backend("vast")
    handle = backend.submit(spec)
    print(f"[launch] submitted: instance={handle.job_id} offer={handle.extra.get('offer')} "
          f"dph={handle.extra.get('dph')}")
    print(f"[launch] result will land at {spec.env['RESULT_S3']}/bioemu-crosscheck.json")


if __name__ == "__main__":
    main()
