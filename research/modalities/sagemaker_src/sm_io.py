"""Mode-agnostic input/output path helpers for SageMaker entry scripts.

Lets one entry script run under BOTH a managed-spot Training job (the new default — cheaper, resumable) and a
legacy Processing job, so the Processing→spot-Training conversion needs only a path-helper swap in each entry,
not a rewrite:

  * `channel(name)` — the local dir for an input channel. Under Training, SageMaker mounts each `fit()` channel
    at `SM_CHANNEL_<NAME>` (== /opt/ml/input/data/<name>); under Processing the submitter mounts it at
    /opt/ml/processing/input/<name>. Prefer the Training env var, fall back to the Processing path. A missing
    channel therefore points at a nonexistent path and fails LOUDLY (never silently reads the wrong data).

  * `out_dir()` — where to write results. Under spot Training we write to the checkpoint dir
    (/opt/ml/checkpoints) so `checkpoint_s3_uri` syncs it to S3 CONTINUOUSLY (a spot interruption or re-dispatch
    then resumes/extends); under Processing we write to /opt/ml/processing/output. Auto-created.

Zero third-party deps so it ships inside any `source_dir`.
"""
import os

# The spot-Training checkpoint mount (submit_spot sets checkpoint_local_path here). Module-level so tests can
# repoint it at a tmp dir; production always uses /opt/ml/checkpoints.
_CKPT_DIR = "/opt/ml/checkpoints"


def channel(name):
    """Local directory for input channel `name` (Training SM_CHANNEL_* → Processing input path fallback)."""
    env = "SM_CHANNEL_" + name.upper().replace("-", "_")
    return os.environ.get(env) or os.path.join("/opt/ml/processing/input", name)


def out_dir():
    """Directory to write outputs to. Spot Training → /opt/ml/checkpoints (continuously synced to
    checkpoint_s3_uri, so a spot interruption / re-dispatch resumes); Processing → /opt/ml/processing/output.

    ALWAYS prefer /opt/ml/checkpoints when it is mounted. Do NOT honor $SM_OUTPUT_DIR: SageMaker Training sets
    that to /opt/ml/output automatically, which is uploaded only at END-OF-JOB and to the job's default
    output_path — NOT the checkpoint prefix readers use — so a timeout/interruption loses partial work and the
    reader finds nothing (the 2026-07-11 ternary smoke wrote CIFs to /opt/ml/output and they never reached the
    prefix). $OUT_DIR_OVERRIDE (a non-SageMaker name) forces a path for local testing. Created if absent."""
    if os.path.isdir(_CKPT_DIR):
        p = _CKPT_DIR
    else:
        p = os.environ.get("OUT_DIR_OVERRIDE") or "/opt/ml/processing/output"
    os.makedirs(p, exist_ok=True)
    return p
