#!/usr/bin/env python3
"""
Submit the PocketMiner cryptic-pocket cross-check on the apo NR4A3 LBD as an AWS SageMaker Processing job.

PocketMiner (Meller et al., Nat Commun 2023) is a GVP graph neural network that predicts cryptic-pocket-
forming residues from a SINGLE static structure, trained on an INDEPENDENT cryptic-pocket MD dataset. Run
on the apo AF2 NR4A3 LBD (AFDB AF-Q92570, residues 373-626 — pre-metadynamics, so NOT circular w.r.t. our
own metad+fpocket route), it is an orthogonal test of the "cryptic druggable pocket" claim.

Same managed, auto-tears-down path as the fpocket job (nr4a3_fpocket_sagemaker.py): SageMaker provisions
the container, entry.py fetches the apo structure + clones PocketMiner (MIT, weights in-repo) + builds a
TensorFlow env + runs inference + writes pocketminer_nr4a3_result.json, then the instance terminates.

CPU work (small GNN inference) — defaults to ml.c5.2xlarge, so it does NOT contend with the GPU quota
(the ABFE fleet). Driven from CI (gpu-pocketminer-aws.yml). Needs env: AWS creds + SAGEMAKER_ROLE_ARN.
"""
import os
import sys


def main():
    try:
        import sagemaker
        from sagemaker.processing import FrameworkProcessor, ProcessingInput, ProcessingOutput
        from sagemaker.pytorch import PyTorch
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    # CPU: PocketMiner inference is a few seconds; c5.2xlarge (8 vCPU, 16 GB) gives headroom for the
    # conda/TF env build. c5.xlarge also works but the env build is slower. No GPU -> no ABFE contention.
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(3600)))   # hard cap; the run itself is minutes
    # Optional: allow trimming a PDB mounted from S3 instead of fetching apo AF2. OFF by default so the
    # non-circular apo input is guaranteed. Only set if you have verified the mounted PDB is the APO model.
    allow_input = os.environ.get("PM_ALLOW_INPUT_PDB", "")
    input_s3 = os.environ.get("PM_INPUT_S3", "")

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch,
        framework_version="2.3",
        py_version="py311",
        role=role,
        instance_count=1,
        instance_type=instance,
        max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-pocketminer",
        sagemaker_session=sess,
    )
    inputs = []
    if allow_input == "1" and input_s3:
        inputs = [ProcessingInput(source=input_s3, destination="/opt/ml/processing/input")]
        print(f"  PM_ALLOW_INPUT_PDB=1: mounting {input_s3} (verify it is the APO model)", flush=True)

    print(f"submitting PocketMiner cross-check: {instance}, max_runtime={max_runtime}s, "
          f"outputs -> s3://{bucket}/nr4a3-pocketminer", flush=True)
    proc.run(
        code="entry.py",
        source_dir=os.path.join(here, "pocketminer_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/nr4a3-pocketminer",
                                  s3_upload_mode="Continuous")],
        arguments=["--pdb-name", os.environ.get("PM_PDB_NAME", "AF-Q92570.pdb")],
        wait=True,
        logs=True,
    )
    print(f"done — results in s3://{bucket}/nr4a3-pocketminer/pocketminer_nr4a3_result.json", flush=True)
    # Cost note: ml.c5.2xlarge on-demand ~ $0.41/hr (us-east-2). Runtime is dominated by the one-off
    # conda/TF env build (~10-20 min), inference is seconds -> well under $0.25 per run. No GPU spend.


if __name__ == "__main__":
    main()
