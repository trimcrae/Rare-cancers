"""A job that authenticates to GCP must carry `id-token: write`, or it dies before it does anything.

★ CAUGHT THE HARD WAY, 2026-07-30. `triangle-reduce` — the task that computes the closure residual R —
failed on its FIRST REAL invocation, in the minute the fourth triangle leg finally landed after a day of
host churn:

    google-github-actions/auth failed with: GitHub Actions did not inject
    $ACTIONS_ID_TOKEN_REQUEST_TOKEN or $ACTIONS_ID_TOKEN_REQUEST_URL into this job.

The workflow-level default is `contents: write`, which does not include `id-token`. Nothing had ever
exercised it because `reduce_triangle` refuses a partial cycle by construction, so the job had never run
past its own guard — the permission was latent for exactly as long as the science was. That is the worst
possible time to discover it: the moment a result is finally available.

This is a whole class, not one job, so the test checks every workflow rather than that one line.
"""
from pathlib import Path

import pytest
import yaml

WF_DIR = Path(__file__).resolve().parents[3] / ".github/workflows"
WORKFLOWS = sorted(WF_DIR.glob("*.yml"))

WIF_ACTION = "google-github-actions/auth"


def _jobs(path):
    try:
        d = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        pytest.fail(f"{path.name} is not parseable YAML: {e}")
    return (d or {}).get("jobs") or {}


def _effective_id_token(workflow, job):
    """Job-level permissions REPLACE the workflow-level block wholesale — they do not merge. So a job that
    declares any `permissions:` at all and omits id-token does NOT inherit one."""
    if "permissions" in job:
        p = job["permissions"]
        return (p or {}).get("id-token") if isinstance(p, dict) else p
    p = workflow.get("permissions")
    return (p or {}).get("id-token") if isinstance(p, dict) else p


@pytest.mark.parametrize("wf", WORKFLOWS, ids=[w.name for w in WORKFLOWS])
def test_every_job_that_authenticates_to_gcp_can_get_a_token(wf):
    d = yaml.safe_load(wf.read_text()) or {}
    for name, job in (d.get("jobs") or {}).items():
        steps = job.get("steps") or []
        if not any(WIF_ACTION in str(s.get("uses", "")) for s in steps):
            continue
        assert _effective_id_token(d, job) == "write", (
            f"{wf.name}:{name} uses {WIF_ACTION} but has no effective `id-token: write`. It will fail at "
            f"the auth step with 'did not inject $ACTIONS_ID_TOKEN_REQUEST_TOKEN' — before running any of "
            f"its own logic. Note job-level `permissions:` REPLACES the workflow-level block rather than "
            f"merging with it, so adding one to a job silently drops whatever it did not restate.")


def test_the_closure_residual_job_specifically_is_covered():
    """Named explicitly because this is the one that failed at the worst possible moment — with the result
    finally computable and the fourth leg's GPU already torn down."""
    d = yaml.safe_load((WF_DIR / "gpu-ternary-fep-vast.yml").read_text())
    job = d["jobs"]["triangle_reduce"]
    assert job["permissions"]["id-token"] == "write"
    assert job["permissions"]["contents"] == "write", \
        "job-level permissions REPLACE the workflow default, so contents:write must be restated too"
