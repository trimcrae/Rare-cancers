"""Shared helper: submit a job as a managed-SPOT SageMaker Training job (the repo default per the standing
"default every GPU run to managed spot" directive), replacing the on-demand `FrameworkProcessor` (Processing)
pattern. Spot is ~60-70% cheaper and draws on the spot-Training quota (8) rather than the on-demand Processing
quota (1); it is safe because `checkpoint_s3_uri` syncs the output/checkpoint dir to S3 CONTINUOUSLY (a spot
interruption or a re-dispatch resumes/extends), so a job loses at most what it computed since the last sync.

Drop-in for `FrameworkProcessor(...).run(code=, source_dir=, inputs=[ProcessingInput...], outputs=[Processing
Output...], arguments=[...])`:
  * `inputs`  {channel: s3_uri}      → TrainingInput channels (entry reads via sm_io.channel(name))
  * outputs   (ProcessingOutput)     → `checkpoint_s3_uri = s3://bucket/<output_prefix>` (entry writes via
    sm_io.out_dir() == /opt/ml/checkpoints). We point the checkpoint URI at the SAME prefix the Processing job
    wrote to, so every downstream reader (report_*/reduce) keeps finding outputs unchanged.
  * `arguments` ["--k","v",...] or {"k":"v"} → estimator `hyperparameters` (SageMaker passes them to the entry
    as `--k v`, so the entry's existing argparse is unchanged).
  * `environment`                    → estimator env.

Env knobs: SPOT (default 1; 0 = on-demand fallback for a type with no spot quota), MAX_RUNTIME, MAX_WAIT.
"""
import os


def _to_hyperparameters(arguments):
    if not arguments:
        return {}
    if isinstance(arguments, dict):
        return {str(k).lstrip("-"): str(v) for k, v in arguments.items()}
    hp, i = {}, 0
    args = list(arguments)
    while i < len(args):
        tok = str(args[i])
        if tok.startswith("--"):
            key = tok[2:]
            if i + 1 < len(args) and not str(args[i + 1]).startswith("--"):
                hp[key] = str(args[i + 1]); i += 2
            else:
                hp[key] = "true"; i += 1          # boolean/store_true flag
        else:
            i += 1
    return hp


def submit_spot(*, entry_point, source_dir, base_job_name, output_prefix,
                inputs=None, arguments=None, environment=None,
                instance="ml.g5.xlarge", framework_version="2.3", py_version="py311",
                max_run=None, spot=None, max_wait=None, wait=True, role=None, sess=None,
                checkpoint_s3_uri=None):
    """Build + fit a spot PyTorch Training job. Returns the estimator. `inputs` = {channel_name: s3_uri}."""
    import sagemaker
    from sagemaker.pytorch import PyTorch
    from sagemaker.inputs import TrainingInput

    role = role or os.environ.get("SAGEMAKER_ROLE_ARN")
    if not role:
        raise SystemExit("SAGEMAKER_ROLE_ARN not set (the SageMaker execution-role ARN)")
    sess = sess or sagemaker.Session()
    bucket = sess.default_bucket()
    instance = os.environ.get("INSTANCE", instance)
    spot = (os.environ.get("SPOT", "1") == "1") if spot is None else spot
    max_run = int(os.environ.get("MAX_RUNTIME", str(max_run if max_run else 6 * 3600)))
    # max_wait must be >= max_run for spot (time budget incl. capacity waits); generous so a job finishes in one.
    max_wait = (int(os.environ.get("MAX_WAIT", str(int(max_run * 1.6)))) if spot else None) if max_wait is None else max_wait
    ckpt = checkpoint_s3_uri or f"s3://{bucket}/{output_prefix}"

    est = PyTorch(
        entry_point=entry_point, source_dir=source_dir, role=role,
        framework_version=framework_version, py_version=py_version,
        instance_count=1, instance_type=instance, sagemaker_session=sess,
        base_job_name=base_job_name,
        use_spot_instances=spot, max_run=max_run, max_wait=max_wait,
        checkpoint_s3_uri=ckpt, checkpoint_local_path="/opt/ml/checkpoints",
        hyperparameters=_to_hyperparameters(arguments),
        environment=(environment or None),
    )
    channels = {name: TrainingInput(uri) for name, uri in (inputs or {}).items()}
    print(f"submitting SPOT Training '{base_job_name}': {instance} spot={spot} max_run={max_run}s "
          f"channels={list(channels)} → outputs/checkpoints s3://{bucket}/{output_prefix}", flush=True)
    est.fit(channels or None, wait=wait, logs=wait)
    print(f"submitted; outputs in s3://{bucket}/{output_prefix}", flush=True)
    return est
