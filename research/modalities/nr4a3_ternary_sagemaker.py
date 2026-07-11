#!/usr/bin/env python3
"""
Submit the NR4A3–PROTAC–E3 ternary Boltz-2 prediction as an AWS SageMaker Processing job.

Same managed, auto-tears-down path as the MD pipeline (nr4a3_md_sagemaker.py): SageMaker provisions a
GPU container, installs boltz_src/requirements.txt, runs entry.py (which runs nr4a3_ternary.py --run),
enforces a HARD MaxRuntime cap, then terminates — nothing to shut off.

Driven from CI (gpu-ternary-aws.yml). Needs env: AWS creds + SAGEMAKER_ROLE_ARN. Optional
PROTAC_SMILES (forwarded to the job) once a warhead exists; absent, only the CRBN+ligand control runs.
"""
import os
import sys


def main():
    try:
        import sagemaker
        import sagemaker_submit
    except ImportError:
        sys.exit("pip install 'sagemaker>=2.200,<3' boto3")

    role = os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        sys.exit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    # ml.g5.xlarge (A10G, 16 GB RAM) — the account has quota for this; ml.g5.2xlarge is 0 instances
    # (2026-07-01 ResourceLimitExceeded). The control ran within 16 GB RAM before its dep crash, so xlarge is fine.
    instance = os.environ.get("INSTANCE", "ml.g5.xlarge")
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(6 * 3600)))   # hard cap
    protac = os.environ.get("PROTAC_SMILES", "")
    mode = os.environ.get("TERNARY_MODE", "ternary")                  # ternary | binary

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    # BINARY co-fold: extract the warhead SMILES from the docked SDF on THIS runner (boto3 + RDKit), then
    # forward it to the GPU job as --binary-smiles. Keeps S3/RDKit out of the GPU container.
    binary_smiles = ""
    if mode == "binary":
        import boto3
        from rdkit import Chem
        sdf_key = os.environ.get("LIGAND_SDF_KEY", "nr4a3-denovo-matrix-v2/docked_nr4a3.sdf")
        lig_name = os.environ.get("LIGAND_NAME", "denovo_401")
        local = "/tmp/docked.sdf"
        boto3.client("s3").download_file(bucket, sdf_key, local)
        mol = next((m for m in Chem.SDMolSupplier(local, sanitize=True, removeHs=False)
                    if m is not None and (m.GetProp("_Name").strip() == lig_name or lig_name == "")), None)
        if mol is None:                                               # fall back to the first valid record
            mol = next((m for m in Chem.SDMolSupplier(local) if m is not None), None)
        if mol is None:
            sys.exit(f"could not read a molecule for {lig_name} from s3://{bucket}/{sdf_key}")
        binary_smiles = Chem.MolToSmiles(Chem.RemoveHs(mol))
        print(f"[binary] {lig_name} SMILES from {sdf_key}: {binary_smiles}", flush=True)

    # Forward the ternary-script config to the GPU container (SageMaker containers do NOT inherit the
    # submitter env, so set it explicitly on the processor). Lets entry.py run the NR-V04/VHL benchmark
    # (TERNARY_SCRIPT=nrv04_ternary.py, TERNARY_EXTRA_ARGS="--pilot", SEEDS, WITH_VBC, NRV04_SMILES).
    job_env = {k: os.environ[k] for k in
               ("TERNARY_SCRIPT", "TERNARY_EXTRA_ARGS", "SEEDS", "WITH_VBC", "NRV04_SMILES", "GIT_REF")
               if os.environ.get(k)}

    # control mode has no PROTAC → pass a benign --control sentinel (argparse store_true) so args is non-empty.
    if mode == "binary":
        args = ["--binary-smiles", binary_smiles]
        dest_prefix = "nr4a3-binary"
    else:
        args = ["--protac-smiles", protac] if protac else ["--control"]
        dest_prefix = "nr4a3-ternary"
    dest_prefix = os.environ.get("OUTPUT_PREFIX", dest_prefix)   # e.g. nrv04-ternary-pilot for the NR-V04 benchmark
    # Managed-SPOT Training (was on-demand Processing): checkpoint_s3_uri = the SAME dest_prefix the readers
    # expect; entry.py writes to sm_io.out_dir() == /opt/ml/checkpoints, synced continuously.
    sagemaker_submit.submit_spot(
        entry_point="entry.py", source_dir=os.path.join(here, "boltz_src"),
        base_job_name="nr4a3-ternary", output_prefix=dest_prefix,
        arguments=args, environment=(job_env or None),
        instance=instance, max_run=max_runtime, sess=sess, role=role, wait=True,
    )


if __name__ == "__main__":
    main()
