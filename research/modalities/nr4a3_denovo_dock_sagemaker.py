#!/usr/bin/env python3
"""
Submit the DE-NOVO selectivity funnel (docking tier) as an AWS SageMaker Processing job.

Mounts four prefixes — nr4a3-denovo (candidates), nr4a3-release-druggable (Step-0 NR4A3 receptor),
nr4a1-metad, nr4a2-metad — runs entry_denovo_dock.py -> nr4a3_matrix.py (candidate mode), and writes
s3://<bucket>/nr4a3-denovo-matrix in the SAME format MM-GBSA consumes (nr4a3-matrix.json +
<tag>-opened.pdb + docked_<tag>.sdf). CPU work (smina docking) — defaults to ml.c5.2xlarge (~$0.3-0.7),
separate quota from the g5. Needs AWS creds + SAGEMAKER_ROLE_ARN. Driven from gpu-denovo-dock-aws.yml.
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
    instance = os.environ.get("INSTANCE", "ml.c5.2xlarge")     # CPU; smina docking
    max_runtime = int(os.environ.get("MAX_RUNTIME", str(4 * 3600)))
    out_prefix = os.environ.get("OUTPUT_PREFIX", "nr4a3-denovo-matrix")
    git_ref = os.environ.get("GIT_REF", "main")
    top_n = os.environ.get("TOP_N", "20")
    developable_only = os.environ.get("DEVELOPABLE_ONLY", "1")     # red-team Tier-1 #1: dock only clean gens
    receptor_mode = os.environ.get("RECEPTOR_MODE", "release")     # release | metad (Tier-1 #3 state-match)
    decoy_mode = os.environ.get("DECOY_MODE", "0")                 # 1 = dock the decoy NULL (Tier-1 #2)
    species_mode = os.environ.get("SPECIES_MODE", "0")            # 1 = dock the pre-FEP species set
    prefixes = {"denovo": os.environ.get("DENOVO_PREFIX", "nr4a3-denovo"),
                "receptor": os.environ.get("RECEPTOR_PREFIX", "nr4a3-release-druggable"),
                "nr4a1": os.environ.get("NR4A1_PREFIX", "nr4a1-metad"),
                "nr4a2": os.environ.get("NR4A2_PREFIX", "nr4a2-metad")}
    # State-matched re-dock (Tier-1 #3): NR4A3 in its metad-opened conformer (like the paralogues), not the
    # unbiased release frame. Mount the nr4a3-metad ensemble at input/nr4a3 so the driver extracts NR4A3's
    # opened conformer there (it does this whenever NR4A3_RECEPTOR is unset, which entry sets per receptor-mode).
    mount_tags = ["denovo", "receptor", "nr4a1", "nr4a2"]
    if receptor_mode == "metad":
        prefixes["nr4a3"] = os.environ.get("NR4A3_METAD_PREFIX", "nr4a3-metad")
        mount_tags.append("nr4a3")
    # LEAD-OPT sentinel: candidates live in git (a committed JSON), not S3 — the job reads them from the
    # cloned git_ref (the SageMaker role writes only the output, so no CI-user PutObject needed, no new
    # workflow). Drop the S3 denovo mount and tell the entry which committed file to dock.
    leadopt_json = ""
    if prefixes["denovo"] == "leadopt":
        leadopt_json = os.environ.get("LEADOPT_JSON", "nr4a3-leadopt-candidates.json")
        mount_tags = [t for t in mount_tags if t != "denovo"]

    sess = sagemaker.Session()
    bucket = sess.default_bucket()
    here = os.path.dirname(os.path.abspath(__file__))

    proc = FrameworkProcessor(
        estimator_cls=PyTorch, framework_version="2.3", py_version="py311", role=role,
        instance_count=1, instance_type=instance, max_runtime_in_seconds=max_runtime,
        base_job_name="nr4a3-denovo-dock", sagemaker_session=sess,
    )
    inputs = [ProcessingInput(source=f"s3://{bucket}/{prefixes[t]}",
                              destination=f"/opt/ml/processing/input/{t}", input_name=t)
              for t in mount_tags]
    print(f"submitting de-novo dock: {instance}, top {top_n}, developable_only={developable_only}, "
          f"receptor_mode={receptor_mode}; inputs " +
          ", ".join(f"{t}=s3://{bucket}/{prefixes[t]}" for t in mount_tags) +
          f" -> s3://{bucket}/{out_prefix}", flush=True)
    proc.run(
        code="entry_denovo_dock.py",
        source_dir=os.path.join(here, "sagemaker_src"),
        inputs=inputs,
        outputs=[ProcessingOutput(source="/opt/ml/processing/output",
                                  destination=f"s3://{bucket}/{out_prefix}")],
        arguments=["--git-ref", git_ref, "--top-n", str(top_n),
                   "--developable-only", developable_only, "--receptor-mode", receptor_mode,
                   "--decoy", decoy_mode, "--species", species_mode]
        + (["--candidate-json", leadopt_json] if leadopt_json else []),
        wait=True, logs=True,
    )
    print(f"done — results in s3://{bucket}/{out_prefix}", flush=True)


if __name__ == "__main__":
    main()
