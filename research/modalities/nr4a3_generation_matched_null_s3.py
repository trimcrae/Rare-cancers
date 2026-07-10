#!/usr/bin/env python3
"""S3 glue for the generation-matched decoy null (driven by generation-matched-null-aws.yml).

Isolates all AWS/S3 IO from the pure driver (nr4a3_generation_matched_null.py): it derives the SageMaker
default bucket, downloads the inputs each MODE needs to a local scratch dir, points the driver's env at the
local paths, runs it, and uploads the result. NO SageMaker / NO GPU — this is CPU work on the GitHub runner
($0). The driver + the pure logic it calls are what carry the tested behaviour; this file only moves bytes.

MODE (env): prep-scramble | prep-manifest | reduce  (see the driver docstring for what each control is).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nr4a3_generation_matched_null as drv     # noqa: E402


def _s3():
    import boto3
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")
    s3 = boto3.client("s3")
    acct = boto3.client("sts").get_caller_identity()["Account"]
    bucket = os.environ.get("BUCKET") or f"sagemaker-{region}-{acct}"
    return s3, bucket


def _dl(s3, bucket, key, dest):
    print(f"  s3://{bucket}/{key} -> {dest}", flush=True)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    s3.download_file(bucket, key, dest)


def _ul(s3, bucket, key, src):
    print(f"  {src} -> s3://{bucket}/{key}", flush=True)
    s3.upload_file(src, bucket, key)


def prep_scramble(s3, bucket, scratch):
    denovo_prefix = os.environ.get("DENOVO_PREFIX", "nr4a3-denovo")
    control_prefix = os.environ["CONTROL_GEN_PREFIX"]
    local = os.path.join(scratch, "real-denovo.json")
    _dl(s3, bucket, f"{denovo_prefix}/nr4a3-denovo.json", local)
    out = os.path.join(scratch, "scr")
    os.environ.update({"MODE": "prep-scramble", "DENOVO_JSON": local, "OUTPUT_DIR": out})
    drv.prep_scramble()
    _ul(s3, bucket, f"{control_prefix}/nr4a3-denovo.json", os.path.join(out, "nr4a3-denovo.json"))
    print(f"prep-scramble done -> s3://{bucket}/{control_prefix} (feed to gpu-denovo-dock-aws.yml "
          f"denovo_prefix={control_prefix})", flush=True)


def prep_manifest(s3, bucket, scratch):
    pocket_prefix = os.environ.get("CONTROL_POCKET_PREFIX", "nr4a3-matrix")
    control_prefix = os.environ["CONTROL_GEN_PREFIX"]
    pdb = os.environ["CONTROL_PDB"]
    local_pdb = os.path.join(scratch, pdb)
    _dl(s3, bucket, f"{pocket_prefix}/{pdb}", local_pdb)
    out = os.path.join(scratch, "man")
    os.environ.update({"MODE": "prep-manifest", "OUTPUT_DIR": out})
    drv.prep_manifest()
    os.makedirs(out, exist_ok=True)
    # the generation job needs BOTH the manifest and the receptor PDB at the control prefix.
    import shutil
    shutil.copy(local_pdb, os.path.join(out, pdb))
    _ul(s3, bucket, f"{control_prefix}/nr4a3-release-druggable.json",
        os.path.join(out, "nr4a3-release-druggable.json"))
    _ul(s3, bucket, f"{control_prefix}/{pdb}", os.path.join(out, pdb))
    print(f"prep-manifest done -> s3://{bucket}/{control_prefix} (feed to gpu-denovo-aws.yml "
          f"input_prefix={control_prefix})", flush=True)


def reduce_(s3, bucket, scratch):
    real_prefix = os.environ.get("REAL_MMGBSA_PREFIX", "nr4a3-mmgbsa")
    real_local = os.path.join(scratch, "real-mmgbsa.json")
    _dl(s3, bucket, f"{real_prefix}/nr4a3-mmgbsa.json", real_local)
    env = {"MODE": "reduce", "REAL_MMGBSA": real_local, "OUTPUT_DIR": os.path.join(scratch, "red")}

    control_specs = []
    for tok in os.environ.get("CONTROL_MMGBSA_PREFIXES", "").split(","):
        tok = tok.strip()
        if not tok:
            continue
        name, prefix = tok.split(":", 1)
        local = os.path.join(scratch, f"control-{name.strip()}.json")
        _dl(s3, bucket, f"{prefix.strip()}/nr4a3-mmgbsa.json", local)
        control_specs.append(f"{name.strip()}:{local}")
    if control_specs:
        env["CONTROL_MMGBSA"] = ",".join(control_specs)

    decoy_prefix = os.environ.get("DECOY_MMGBSA_PREFIX", "").strip()
    if decoy_prefix:
        decoy_local = os.path.join(scratch, "decoy-mmgbsa.json")
        _dl(s3, bucket, f"{decoy_prefix}/nr4a3-mmgbsa.json", decoy_local)
        env["DECOY_MMGBSA"] = decoy_local

    for passthru in ("NGEN", "REAL_NGEN", "REAL_SURVIVORS", "SUBTRACT_SD", "NULL_Q", "BAND"):
        if os.environ.get(passthru):
            env[passthru] = os.environ[passthru]
    os.environ.update(env)
    drv.reduce_()

    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-generation-matched-null")
    _ul(s3, bucket, f"{out_prefix}/nr4a3-generation-matched-null.json",
        os.path.join(env["OUTPUT_DIR"], "nr4a3-generation-matched-null.json"))
    print(f"reduce done -> s3://{bucket}/{out_prefix}/nr4a3-generation-matched-null.json", flush=True)


def main():
    if not os.environ.get("AWS_ACCESS_KEY_ID"):
        sys.exit("AWS creds not set")
    s3, bucket = _s3()
    mode = os.environ.get("MODE", "reduce").strip()
    scratch = tempfile.mkdtemp(prefix="genmatched-")
    print(f"bucket=s3://{bucket}  mode={mode}  scratch={scratch}", flush=True)
    if mode == "prep-scramble":
        prep_scramble(s3, bucket, scratch)
    elif mode == "prep-manifest":
        prep_manifest(s3, bucket, scratch)
    elif mode == "reduce":
        reduce_(s3, bucket, scratch)
    else:
        sys.exit(f"unknown MODE={mode!r}")


if __name__ == "__main__":
    main()
