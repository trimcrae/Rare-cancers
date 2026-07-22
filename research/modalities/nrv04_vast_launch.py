#!/usr/bin/env python3
"""
NR-V04 covalent feasibility panel — Vast.ai launcher (prereg §6; runs on CI with VAST_API_KEY + AWS creds).

One Vast instance per (leg, seed) unit → genuinely N-wide parallel (no shared-pool wall). Each instance:
clones the repo, builds the MD env, stages its leg from the co-fold CIF in S3 (nrv04_covalent_assemble),
runs the endpoint-MD driver (nrv04_covalent_md) wrapped by autoteardown, uploads the leg JSON to S3, and
self-destroys. GPU/bid targeting come from ResourceSpec + the tuned VastBackend (RTX-4090-class, >=32 GB host
RAM for the 146k-atom ternary, midpoint spot bid).

PILOT-ONE-LEG-FIRST (standing rule): with PILOT_ONLY=1 we submit ONLY the highest-abort-information unit
(cov_nr4a1 seed 0) to calibrate real GPU-h -> $ before fanning out the other 17. The build_jobspec construction
is pure + unit-tested; submit() needs live creds.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpu_backend import JobSpec, ResourceSpec, get_backend, s3_checkpoint_uri  # noqa: E402
from nrv04_covalent_panel import PANEL, enumerate_units, leg_env, unit_name  # noqa: E402
from nrv04_ligands import LIGANDS  # noqa: E402

REPO = "https://github.com/trimcrae/Rare-cancers"
# co-fold outputs in the reused S3 bucket (nrv04_ternary.py --run --negatives writes one subdir per system).
COFOLD_PREFIX = os.environ.get("NRV04_COFOLD_PREFIX", "nrv04-covalent-cofold")
RESULT_PREFIX = os.environ.get("NRV04_RESULT_PREFIX", "nrv04-covalent-results")

# panel ligand -> the co-fold SYSTEM subdir it comes from (nrv04_ternary.py naming).
_LIGAND_TO_SYSTEM = {"nrv04": "nr4a1", "nrv04_epimer": "neg_inactive", "celastrol": "neg_celastrol"}

# ternary hosts: 4090-class 24 GB (fits 146k atoms), >=32 GB host RAM (setup is RAM-bound), 8 vCPU, 80 GB disk.
TERNARY_RES = ResourceSpec(gpu="rtx4090", min_vram_gb=24, vcpus=8, ram_gb=32, disk_gb=80, interruptible=True)

# The onstart pipeline. $VARS are exported by _vast_onstart (leg env + forwarded AWS creds + CHECKPOINT_URI).
_PIPELINE = r"""
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q && apt-get install -y -q git curl bzip2 ca-certificates
git clone --depth 1 --branch "$GIT_BRANCH" {repo} /work
cd /work/research/modalities
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
export MAMBA_ROOT_PREFIX=/opt/mamba
./bin/micromamba create -y -p /opt/mamba/envs/md -c conda-forge \
    python=3.11 openmm openff-toolkit openmmforcefields ambertools rdkit gemmi numpy boto3 awscli
RUN="./bin/micromamba run -p /opt/mamba/envs/md"
mkdir -p /tmp/in /tmp/out /tmp/cofold
export INPUT_DIR=/tmp/in OUTPUT_DIR=/tmp/out CKPT_DIR=/tmp/out
# stage this leg from its co-fold system in S3 -> INPUT_DIR/<LEG_ID>/{complex.pdb,ligand.sdf}
$RUN aws s3 cp "$COFOLD_PREFIX_S3" /tmp/cofold/ --recursive
export COFOLD_CIF=$(find /tmp/cofold -name '*_model_0.cif' | sort | head -1)
test -n "$COFOLD_CIF" || { echo "no co-fold CIF found under $COFOLD_PREFIX_S3"; exit 3; }
$RUN python -c "import os; from nrv04_covalent_panel import leg_by_id; from nrv04_ligands import LIGANDS; \
from nrv04_covalent_assemble import assemble_leg; lg=leg_by_id(os.environ['LEG_ID']); \
assemble_leg(os.environ['COFOLD_CIF'], lg, LIGANDS[lg.ligand], os.environ['INPUT_DIR'])"
# run the endpoint-MD driver, teardown-guarded
$RUN python autoteardown.py $RUN python nrv04_covalent_md.py
# publish the leg readout JSON
$RUN aws s3 cp /tmp/out/ "$RESULT_S3/" --recursive --exclude '*' --include 'leg_*.json'
"""


def cofold_prefix_s3(leg, bucket):
    """The S3 PREFIX of the co-fold system that feeds this leg (the onstart globs it for *_model_0.cif, robust to
    Boltz's nested predictions/ layout). nrv04->nr4a1, celastrol->neg_celastrol, epimer->neg_inactive."""
    system = _LIGAND_TO_SYSTEM[leg.ligand]
    return f"s3://{bucket}/{COFOLD_PREFIX}/{system}/"


def build_jobspec(leg, seed, mode, branch, bucket):
    """PURE: the JobSpec for one (leg, seed) unit. No I/O -> unit-tested."""
    name = unit_name(leg, seed)
    env = leg_env(leg, seed, mode=mode)
    env.update({
        "GIT_BRANCH": branch,
        "COFOLD_PREFIX_S3": cofold_prefix_s3(leg, bucket),
        "RESULT_S3": f"s3://{bucket}/{RESULT_PREFIX}/{name}",
    })
    pipeline = _PIPELINE.replace("{repo}", REPO)      # not .format(): the bash has literal {a,b} brace-expansion
    return JobSpec(
        name=name,
        command=["bash", "-lc", pipeline],
        image="nvidia/cuda:12.4.1-runtime-ubuntu22.04",
        checkpoint_uri=s3_checkpoint_uri(name, bucket=bucket),
        resume=True,
        resources=TERNARY_RES,
        max_runtime_s=int(os.environ.get("MAX_RUNTIME_S", "43200")),
        env=env,
    )


def units_to_run():
    """Pilot-one-leg-first: PILOT_ONLY=1 -> just cov_nr4a1 seed 0 (highest abort info: it's the primary covalent
    ternary model + the R4 sensitivity numerator). Else the full 18-unit fan-out."""
    if os.environ.get("PILOT_ONLY", "1") == "1":
        pilot = next(lg for lg in PANEL if lg.leg_id == "cov_nr4a1")
        return [(pilot, 0)]
    return enumerate_units()


def discover_cofold(bucket, base=None):
    """List the reused co-fold prefix and report, per panel system, the *_model_0.cif keys already in S3 (so we
    reuse ValB's existing structures instead of regenerating). Prints a per-system found/missing summary."""
    import boto3
    base = base or os.environ.get("NRV04_COFOLD_PREFIX", COFOLD_PREFIX)
    s3 = boto3.client("s3")
    found = {}
    for lig, system in _LIGAND_TO_SYSTEM.items():
        prefix = f"{base}/{system}/"
        keys, tok = [], None
        while True:
            kw = {"Bucket": bucket, "Prefix": prefix}
            if tok:
                kw["ContinuationToken"] = tok
            r = s3.list_objects_v2(**kw)
            keys += [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith("_model_0.cif")]
            if not r.get("IsTruncated"):
                break
            tok = r["NextContinuationToken"]
        found[system] = sorted(keys)
        print(f"[discover] {system:14} ({lig:12}) -> {len(keys)} cif(s)"
              + (f"  e.g. {keys[0]}" if keys else "  MISSING"), flush=True)
    json.dump(found, open("nrv04-cofold-discovery.json", "w"), indent=2)
    return found


def main():
    bucket = os.environ.get("VAST_CKPT_BUCKET")
    if not bucket:
        raise SystemExit("[nrv04-launch] set VAST_CKPT_BUCKET (the reused S3 bucket)")
    if os.environ.get("DISCOVER") == "1":
        discover_cofold(bucket)
        return 0
    branch = os.environ.get("GIT_BRANCH", "claude/alternative-gpu-providers-wx4r2c")
    mode = os.environ.get("MODE", "run")
    dry = os.environ.get("DRY_RUN", "0") == "1"

    be = get_backend("vast")
    units = units_to_run()
    print(f"[nrv04-launch] {len(units)} unit(s), mode={mode}, dry_run={dry}", flush=True)
    handles = []
    for leg, seed in units:
        spec = build_jobspec(leg, seed, mode, branch, bucket)
        if dry:
            print(f"[dry] {spec.name}: gpu={spec.resources.gpu} ram>={spec.resources.ram_gb}GB "
                  f"ckpt={spec.checkpoint_uri} cofold={spec.env['COFOLD_PREFIX_S3']}", flush=True)
            continue
        h = be.submit(spec)
        print(f"[submit] {spec.name} -> instance {h.job_id} dph≈${h.extra.get('dph')}/hr", flush=True)
        handles.append({"unit": spec.name, "instance": h.job_id, "offer": h.extra.get("offer")})
    if handles:
        json.dump(handles, open("nrv04-vast-handles.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
