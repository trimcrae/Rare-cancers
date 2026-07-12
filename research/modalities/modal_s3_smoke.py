#!/usr/bin/env python3
"""
Modal <-> S3 bridge smoke test — proves a Modal function can read/write the EXISTING AWS S3 bucket using the
AWS creds already in the repo secrets. This is the checkpoint bridge for the cheap-provider path: compute runs
on Modal (or later Salad/RunPod), state lives in S3. No R2 needed.

Runs on CPU (an S3 round-trip needs no GPU) so it costs ~nothing of the free credits. The AWS creds flow
GitHub secret -> GHA env -> modal.Secret.from_dict -> the Modal function's env -> boto3. Driven from
.github/workflows/modal-s3-smoke.yml.
"""
import os
import time

import modal

app = modal.App("nr4a3-s3-smoke")
image = modal.Image.debian_slim().pip_install("boto3")

BUCKET = os.environ.get("S3_BUCKET", "sagemaker-us-east-2-646605541856")   # existing SageMaker default bucket
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

# Ship the AWS creds (present in the GHA runner env) to the Modal function as a secret.
_aws = modal.Secret.from_dict({
    "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", ""),
    "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
    "AWS_DEFAULT_REGION": REGION,
})


@app.function(image=image, secrets=[_aws], timeout=120)
def s3_roundtrip(bucket: str) -> str:
    import boto3
    s3 = boto3.client("s3")
    key = f"nr4a3-modal-smoke/probe-{int(time.time())}.txt"
    s3.put_object(Bucket=bucket, Key=key, Body=b"modal-can-reach-s3")
    got = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()
    s3.delete_object(Bucket=bucket, Key=key)                                # clean up the probe
    return f"wrote+read+deleted s3://{bucket}/{key} -> {got!r}"


@app.local_entrypoint()
def main():
    print("[modal-s3] OK —", s3_roundtrip.remote(BUCKET))
    print("[modal-s3] Modal compute + existing S3 bucket works; this is the checkpoint bridge (no R2 needed).")
