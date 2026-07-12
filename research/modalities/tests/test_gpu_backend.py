#!/usr/bin/env python3
"""
Tests for the provider-agnostic GPU harness + the auto-teardown guarantee (no idle GPUs on any provider).
Centerpiece: teardown fires EXACTLY ONCE on success, failure, exception, and watchdog-timeout.

Pure stdlib. Run: python -m pytest research/modalities/tests/test_gpu_backend.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autoteardown import make_subprocess_terminator, run_with_teardown  # noqa: E402
from gpu_backend import (  # noqa: E402
    JobSpec, MockBackend, ResourceSpec, RunPodBackend, SageMakerBackend, SlurmBackend, VastBackend,
    get_backend, pick_cheapest,
)


# ---- the anti-idle-GPU guarantee --------------------------------------------------------------------------

def _recorder():
    calls = []
    return calls, (lambda reason: calls.append(reason))


def test_teardown_fires_on_success():
    calls, term = _recorder()
    rc = run_with_teardown(lambda: 0, term, max_runtime_s=100)
    assert rc == 0 and calls == ["job-exit"]              # released on normal exit


def test_teardown_fires_on_nonzero_exit():
    calls, term = _recorder()
    rc = run_with_teardown(lambda: 1, term, max_runtime_s=100)
    assert rc == 1 and calls == ["job-exit"]              # released even when the job failed


def test_teardown_fires_on_exception_and_reraises():
    calls, term = _recorder()
    try:
        run_with_teardown(lambda: (_ for _ in ()).throw(RuntimeError("boom")), term, max_runtime_s=100)
        assert False, "should have re-raised"
    except RuntimeError:
        pass
    assert calls == ["job-exit"]                          # released even on a crash, exception still propagates


def test_teardown_fires_on_watchdog_timeout():
    calls, term = _recorder()

    def slow():
        time.sleep(0.3)                                   # runs past the 0.05s cap
        return 0
    run_with_teardown(slow, term, max_runtime_s=0.05)
    # watchdog fired first (timeout); the later job-exit is suppressed (idempotent) -> exactly one teardown
    assert calls == ["watchdog-timeout"]


def test_teardown_is_idempotent_single_release():
    calls, term = _recorder()
    run_with_teardown(lambda: 0, term, max_runtime_s=100)
    assert len(calls) == 1                                # GPU released once, never twice (no double-bill logic)


# ---- managed vs marketplace: who must self-terminate ------------------------------------------------------

def test_managed_backends_need_no_self_terminate():
    assert SageMakerBackend().self_terminate_cmd() == []  # SageMaker auto-releases
    assert SlurmBackend().self_terminate_cmd() == []      # scheduler releases the node


def test_marketplace_backends_must_self_terminate():
    assert RunPodBackend().self_terminate_cmd()[:2] == ["runpodctl", "remove"]
    assert VastBackend().self_terminate_cmd()[:2] == ["vastai", "destroy"]


def test_managed_terminator_is_noop_marketplace_runs_cmd(capsys):
    make_subprocess_terminator([])("job-exit")            # empty cmd -> no subprocess, just a log line
    out = capsys.readouterr().out
    assert "auto-releases" in out
    # a marketplace terminator would attempt the argv; we only assert it's built (not run here to avoid a
    # real subprocess), covered by the mock-backend cmd shape above.


# ---- routing / cost ---------------------------------------------------------------------------------------

def test_pick_cheapest_prefers_free_hpc_then_marketplace():
    res = ResourceSpec(gpu="any", min_vram_gb=24)
    # with the free allocation available, ACCESS/Slurm win
    assert pick_cheapest(res, backends=["access", "vast", "runpod", "sagemaker"]) == "access"
    # without free HPC, the cheapest marketplace wins (vast rtx3090/4090 < sagemaker)
    assert pick_cheapest(res, backends=["vast", "runpod", "sagemaker"]) == "vast"


def test_supports_and_hourly_usd():
    be = get_backend("runpod")
    assert be.supports(ResourceSpec(gpu="rtx4090", min_vram_gb=24))
    assert be.hourly_usd(ResourceSpec(gpu="rtx4090", min_vram_gb=24)) is not None
    # a 40 GB requirement excludes a 24 GB-only class match on that gpu
    assert not be.supports(ResourceSpec(gpu="rtx4090", min_vram_gb=48))


def test_mock_backend_lifecycle_and_resume_flag():
    be = MockBackend()
    spec = JobSpec(name="edge1", command=["python", "rbfe.py"], resume=True, checkpoint_uri="s3://x/ckpt")
    h = be.submit(spec)
    assert be.status(h) == "running" and h.extra["resume"] is True
    be.complete(h, ok=True)
    assert be.status(h) == "completed"


def test_get_backend_unknown_raises():
    try:
        get_backend("nope")
        assert False
    except KeyError:
        pass


if __name__ == "__main__":
    calls, term = _recorder()
    run_with_teardown(lambda: 0, term, 100)
    print("teardown on success:", calls)
