#!/usr/bin/env python3
"""Fan-out submitter for the spot-priced, parallel selectivity FEP.

Launches K concurrent SageMaker managed-**SPOT Training** jobs (Processing jobs can't do spot), one per shard
of (receptor, leg, λ-window) units, each with continuous checkpoint sync for spot-interruption resume. Spot
draws on a SEPARATE quota from the 1× on-demand g5, so the shards run in parallel (bounded by the spot quota).

MODE (env MODE):
  plan  : DRY RUN — print the shard plan, the exact jobs that WOULD launch, and the cost estimate. No AWS spend.
  smoke : launch ONE tiny spot job (2 units, --smoke, no MD) to validate the spot+checkpoint+resume path and
          surface a spot-quota-0 (ResourceLimitExceeded) if the Service Quotas increase is still pending.
  run   : launch the full fleet (one spot job per shard). **Only on explicit trimcrae go-ahead.**

Resume: existing per-unit result files under s3://<bucket>/<TAG>/ckpt/**/ are read as done_ids, so a re-dispatch
only re-plans + re-launches the PENDING units.
"""
import io
import json
import os
import sys

TAG = os.environ.get("FEP_TAG", "nr4a3-fep")
MODE = os.environ.get("MODE", "plan")
N_WINDOWS = int(os.environ.get("N_WINDOWS", "12"))
N_SHARDS = int(os.environ.get("N_SHARDS", "8"))
INSTANCE = os.environ.get("INSTANCE", "ml.g5.xlarge")
MAX_WAIT_H = float(os.environ.get("MAX_WAIT_HOURS", "20"))
MAX_RUN_H = float(os.environ.get("MAX_RUN_HOURS", "12"))
LIGAND = os.environ.get("FEP_LIGAND", "denovo_401")
GIT_REF = os.environ.get("GIT_REF", "main")
SPOT = os.environ.get("SPOT", "1") == "1"
RECEPTOR_PREFIX = os.environ.get("RECEPTOR_PREFIX", "nr4a3-denovo-matrix-v2")   # has <r>-opened.pdb + docked_<r>.sdf
POSE_PREFIX = os.environ.get("POSE_PREFIX", RECEPTOR_PREFIX)
SPOT_HOURLY = float(os.environ.get("SPOT_HOURLY", "0.50"))                      # ~ g5.xlarge spot, us-east-2
UNIT_GPU_H = float(os.environ.get("UNIT_GPU_H", "1.0"))                         # planning assumption / window


def _s3():
    import boto3
    return boto3.client("s3")


def _done_ids(bucket):
    """Per-unit result ids already in S3 (resume). Result filename stem == unit id."""
    ids = set()
    try:
        p = _s3().get_paginator("list_objects_v2")
        for page in p.paginate(Bucket=bucket, Prefix=f"{TAG}/ckpt/"):
            for o in page.get("Contents", []):
                k = o["Key"]
                if k.endswith(".json"):
                    ids.add(os.path.basename(k)[:-5])
    except Exception as e:  # noqa: BLE001
        print(f"  (resume scan skipped: {e})", flush=True)
    return ids


def _upload_shard(bucket, i, units):
    key = f"{TAG}/shards/{i}/shard.json"
    _s3().upload_fileobj(io.BytesIO(json.dumps(units).encode()), bucket, key)
    return f"s3://{bucket}/{TAG}/shards/{i}/"


def _cost_note(plan):
    units = plan["n_units_pending"]
    k = max(plan["n_shards"], 1)
    total_gpu_h = units * UNIT_GPU_H
    wall_h = (max(plan["per_shard_sizes"]) if plan["per_shard_sizes"] else 0) * UNIT_GPU_H
    return (f"~{units} pending units × ~{UNIT_GPU_H:g} GPU-h = ~{total_gpu_h:.0f} GPU-h; "
            f"{k} parallel spot shards → wall-clock ~{wall_h:.1f} h; "
            f"spot ≈ ${total_gpu_h * SPOT_HOURLY:.0f} (vs on-demand ${total_gpu_h * 1.4:.0f}).")


def main():
    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if MODE != "plan" and not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set")
    import sagemaker
    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    import fep_sharding as fs
    done = _done_ids(bucket) if MODE != "plan" or os.environ.get("AWS_ACCESS_KEY_ID") else set()
    plan = fs.shard_plan(n_windows=N_WINDOWS, n_shards=N_SHARDS, done_ids=done)
    print(f"[fep] TAG={TAG} mode={MODE} spot={SPOT} instance={INSTANCE}")
    print(f"[fep] units total {plan['n_units_total']}, pending {plan['n_units_pending']} "
          f"(resume: {len(done)} done), shards {plan['n_shards']} sizes {plan['per_shard_sizes']}")
    print(f"[fep] COST {_cost_note(plan)}")

    if MODE == "plan":
        for i, shard in enumerate(plan["shards"]):
            ids = [u["id"] for u in shard]
            print(f"  WOULD launch shard {i}: {len(ids)} units e.g. {ids[:3]}{'…' if len(ids) > 3 else ''} "
                  f"→ spot Training job {TAG}-{i}, checkpoint s3://{bucket}/{TAG}/ckpt/{i}/")
        print("[fep] plan only — no jobs launched. Re-dispatch with mode=smoke (validate wiring) or "
              "mode=run (full fleet; requires go-ahead).")
        return

    from sagemaker.pytorch import PyTorch
    from sagemaker.inputs import TrainingInput

    # FEP_IMAGE_URI (ECR) = the PRE-BAKED image (build-fep-image.yml) with the fep env already installed, so the
    # shard skips the ~15-min conda build on every start (spot resume OR re-dispatch). Empty → the stock PyTorch
    # DLC (framework_version/py_version), which builds the env at runtime (entry_fep.py). Either works; the image
    # just makes starts fast + interruption-cheap.
    image_uri = os.environ.get("FEP_IMAGE_URI", "").strip()

    def make_estimator(i):
        kw = dict(
            entry_point="entry_fep.py", source_dir=os.path.join(here, "sagemaker_src"),
            role=role, instance_count=1, instance_type=INSTANCE, sagemaker_session=sess,
            base_job_name=f"{TAG}-{i}",
            use_spot_instances=SPOT,
            max_run=int(MAX_RUN_H * 3600),
            max_wait=int(MAX_WAIT_H * 3600) if SPOT else None,     # must be >= max_run when spot
            checkpoint_s3_uri=f"s3://{bucket}/{TAG}/ckpt/{i}/",
            checkpoint_local_path="/opt/ml/checkpoints",
            hyperparameters={"git-ref": GIT_REF, "smoke": "1" if MODE == "smoke" else "0",
                             "ligand": LIGAND, "prod-ps": os.environ.get("FEP_PROD_PS", "1000"),
                             "equil-ps": os.environ.get("FEP_EQUIL_PS", "200"),
                             "phase": os.environ.get("FEP_PHASE", "full"),
                             "bootstrap-iter": os.environ.get("FEP_BOOTSTRAP_ITER", "60")},
        )
        if image_uri:
            kw["image_uri"] = image_uri                            # pre-baked env; framework_version omitted
        else:
            kw["framework_version"] = "2.3"
            kw["py_version"] = "py311"
        return PyTorch(**kw)

    if MODE == "smoke":
        units = fs.enumerate_units(receptors=("nr4a3",), n_windows=2)      # 1 trivial per-receptor unit
        chan = _upload_shard(bucket, "smoke", units)
        est = make_estimator("smoke")
        print(f"[fep] launching SMOKE spot job ({len(units)} units) → validating spot+checkpoint path…")
        est.fit({"shard": TrainingInput(chan)}, wait=True, logs=True)     # wait so quota errors surface here
        print("[fep] SMOKE complete — spot + checkpoint + resume path works. Safe to run the fleet on go-ahead.")
        return

    # mode == run : full fan-out, one concurrent spot job per shard.
    # ONLY_RECEPTORS (comma-sep receptor names, e.g. "nr4a1") relaunches JUST those receptors — used to
    # restart a single Failed shard (e.g. one bricked by a spot-kill-corrupted trailblaze checkpoint) WITHOUT
    # re-launching the in-flight shards, which would collide on their checkpoint prefixes. Selecting by
    # RECEPTOR NAME over the CANONICAL full enumeration (not the resume-filtered plan) keeps each receptor's
    # shard INDEX — and thus its ckpt/{i}/ prefix with the preserved LEaP setup — stable regardless of which
    # other receptors happen to be pending. Empty = launch the resume-filtered plan as usual.
    only = os.environ.get("ONLY_RECEPTORS", "").strip()
    only_set = {x.strip() for x in only.split(",") if x.strip()} if only else None
    if only_set is not None:
        canon = fs.shard_plan(n_windows=N_WINDOWS, n_shards=N_SHARDS, done_ids=set())  # stable canonical indices
        shards_to_iter = canon["shards"]
    else:
        shards_to_iter = plan["shards"]
    inputs_common = {"receptor": TrainingInput(f"s3://{bucket}/{RECEPTOR_PREFIX}/"),
                     "poses": TrainingInput(f"s3://{bucket}/{POSE_PREFIX}/")}
    launched = []
    for i, shard in enumerate(shards_to_iter):
        if only_set is not None and not any(u["receptor"] in only_set for u in shard):
            print(f"[fep] skip shard {i} ({[u['receptor'] for u in shard]} not in ONLY_RECEPTORS={sorted(only_set)})")
            continue
        chan = _upload_shard(bucket, i, shard)
        est = make_estimator(i)
        try:
            est.fit({"shard": TrainingInput(chan), **inputs_common}, wait=False)   # wait=False → parallel
        except Exception as e:  # noqa: BLE001 — SageMaker training does NOT queue on quota; excess -> error
            msg = str(e)
            if "ResourceLimitExceeded" in msg or "quota" in msg.lower():
                print(f"[fep] shard {i}: spot quota reached after {len(launched)} concurrent jobs "
                      f"({e.__class__.__name__}). Stopping fan-out — RE-DISPATCH mode=run later and resume will "
                      f"pick up the remaining shards. Raise the 'ml.g5.xlarge for spot training job usage' quota "
                      f"(or lower n_shards) to widen parallelism.", flush=True)
                break
            raise
        launched.append(est.latest_training_job.name)
        print(f"[fep] launched spot shard {i} ({len(shard)} units): {launched[-1]}")
    print(f"[fep] {len(launched)} spot jobs launched (parallel; bounded by spot quota). Poll fep_monitor.py "
          f"for early-stop; reduce with report_fep.py when complete; re-dispatch to resume any un-launched "
          f"shards. Jobs: {launched}")


if __name__ == "__main__":
    main()
