#!/usr/bin/env python3
"""
Modal OpenMM-on-GPU + S3-checkpoint plumbing smoke — the last validation before a real FEP leg runs on Modal.
It proves the three things a real leg needs, cheaply (seconds on a T4, ~free):
  1. the OpenMM image builds on Modal,
  2. OpenMM's **CUDA** platform actually runs on the Modal GPU (a tiny MD),
  3. an OpenMM checkpoint round-trips through the existing S3 bucket AND resumes (the per-unit checkpoint
     contract the real leg relies on).

Driven from .github/workflows/modal-openmm-smoke.yml. Does NOT run a real RBFE leg (that's a substantial GPU
run and gets confirmed first).
"""
import os
import time

import modal

app = modal.App("nr4a3-openmm-smoke")
# openmm is pip-installable with bundled CUDA libs; the Modal GPU host provides the driver.
image = modal.Image.debian_slim().pip_install("openmm", "boto3")

BUCKET = os.environ.get("S3_BUCKET", "sagemaker-us-east-2-646605541856")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
_aws = modal.Secret.from_dict({
    "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", ""),
    "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
    "AWS_DEFAULT_REGION": REGION,
})


@app.function(image=image, gpu="T4", secrets=[_aws], timeout=300)
def openmm_gpu_s3(bucket: str) -> str:
    import boto3
    import openmm as mm
    from openmm import unit

    plats = [mm.Platform.getPlatform(i).getName() for i in range(mm.Platform.getNumPlatforms())]
    if "CUDA" not in plats:
        raise RuntimeError(f"no CUDA platform on the Modal GPU — available: {plats}")

    # tiny 3-particle harmonic system, run a few hundred steps on CUDA
    system = mm.System()
    for _ in range(3):
        system.addParticle(1.0)
    bond = mm.HarmonicBondForce()
    bond.addBond(0, 1, 0.15, 1000.0)
    bond.addBond(1, 2, 0.15, 1000.0)
    system.addForce(bond)
    integ = mm.LangevinMiddleIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 0.002 * unit.picoseconds)
    ctx = mm.Context(system, integ, mm.Platform.getPlatformByName("CUDA"))
    pos = unit.Quantity([mm.Vec3(0, 0, 0), mm.Vec3(0.15, 0, 0), mm.Vec3(0.30, 0, 0)], unit.nanometer)
    ctx.setPositions(pos)
    integ.step(200)
    e = ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)

    # checkpoint -> S3 -> back -> resume (the real per-unit checkpoint path)
    ckpt = ctx.createCheckpoint()
    key = f"nr4a3-modal-smoke/openmm-ckpt-{int(time.time())}.chk"
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=ckpt)
    back = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    ctx.loadCheckpoint(back)                                  # resume from the S3 checkpoint
    s3.delete_object(Bucket=bucket, Key=key)
    return f"CUDA OpenMM ran (E={e:.2f} kJ/mol); {len(ckpt)}-byte checkpoint round-tripped through S3 + resumed"


@app.local_entrypoint()
def main():
    print("[modal-openmm] OK —", openmm_gpu_s3.remote(BUCKET))
    print("[modal-openmm] Modal GPU + OpenMM/CUDA + S3 checkpointing all work — ready to build the real FEP leg.")
