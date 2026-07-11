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


def channel(name):
    """Local directory for input channel `name` (Training SM_CHANNEL_* → Processing input path fallback)."""
    env = "SM_CHANNEL_" + name.upper().replace("-", "_")
    return os.environ.get(env) or os.path.join("/opt/ml/processing/input", name)


def out_dir():
    """Directory to write outputs to. Spot Training → /opt/ml/checkpoints (continuous S3 sync); Processing →
    /opt/ml/processing/output. Honours $SM_OUTPUT_DIR override. Created if absent."""
    # Under spot Training with checkpoint_local_path=/opt/ml/checkpoints, SageMaker mounts that dir (so it
    # exists); under Processing it does not. $SM_OUTPUT_DIR overrides both.
    p = os.environ.get("SM_OUTPUT_DIR") or \
        ("/opt/ml/checkpoints" if os.path.isdir("/opt/ml/checkpoints") else "/opt/ml/processing/output")
    os.makedirs(p, exist_ok=True)
    return p
