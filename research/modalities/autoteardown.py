#!/usr/bin/env python3
"""
Auto-teardown wrapper — the provider-agnostic equivalent of "SageMaker auto-kills the instance when the job
ends." On rented-GPU providers (RunPod/Vast) an instance keeps billing until it is EXPLICITLY destroyed, so a
finished (or crashed, or hung) job that doesn't tear itself down bleeds money on an idle GPU. This wrapper
CALLS the backend's release path on completion, failure, OR timeout, on every provider.

⛔ WHAT THIS DOES **NOT** GUARANTEE, corrected 2026-07-27. The header said "GUARANTEES the instance is
released", and CLAUDE.md §6 repeated it as "the auto-teardown wrapper guarantees no idle-GPU billing
anywhere". Two independent reasons that was false on Vast, both measured that day:

  1. **The wrapper is not in the path.** On Vast the release is a bash EXIT trap armed inside the onstart
     script (`gpu_backend._VAST_SELFSTOP`), not this Python. The ternary lane's container runs
     `run_ternary_leg.sh` directly.
  2. **The release path cannot succeed anyway.** An unprivileged container cannot end itself: `poweroff` and
     `shutdown` need an init it does not have, `kill -9 -1` excludes PID 1 and kills the caller, and
     `kill -9 1` returns SUCCESS while being ignored (kernel SIGNAL_UNKILLABLE). Reproduced under
     `unshare -fp --mount-proc`; pinned by `tests/test_vast_idle_guard.py`.

Both failures share one blind spot this wrapper structurally cannot cover: **it fires when the wrapped
process RETURNS.** A container that crash-loops never returns, so nothing here ever runs — which is exactly
what billed two 5a-KS legs for ~53 min at `gpu_util: 0.0`. The guarantee is control-plane
(`vast_idle_guard` + `ternary_vast_launch.collect`), and the honest description of this file is
"stops the job and asks nicely".

Two mechanisms, belt-and-braces:
  1. finally-block teardown  — runs the backend's self_terminate command no matter how the job exits (return,
     nonzero exit, or exception).
  2. watchdog timer          — if the job runs past max_runtime_s (e.g. a hang), fire teardown anyway, so a
     wedged process can never hold the GPU on the meter indefinitely.
Teardown is idempotent (runs exactly once). For managed backends whose self_terminate_cmd is empty (SageMaker,
Slurm), teardown is a no-op — the platform already auto-releases.

Pure stdlib. The core is unit-tested with a mock terminate fn; the real entrypoint runs the terminate argv via
subprocess on the provider.
"""
from __future__ import annotations

import subprocess
import threading


def run_with_teardown(run_fn, terminate_fn, max_runtime_s: float):
    """
    Run `run_fn()` (the real job) and GUARANTEE `terminate_fn(reason)` is called exactly once — on normal
    completion, on failure/exception, or when the watchdog fires at max_runtime_s. Returns run_fn()'s value;
    re-raises its exception AFTER tearing down. `terminate_fn` must be idempotent-safe on its own too, but this
    wrapper already guards against double-calls.
    """
    state = {"done": False}
    lock = threading.Lock()

    def _teardown(reason):
        with lock:
            if state["done"]:
                return
            state["done"] = True
        terminate_fn(reason)                       # release the GPU (outside the lock; may be slow/network)

    watchdog = threading.Timer(max_runtime_s, _teardown, args=("watchdog-timeout",))
    watchdog.daemon = True
    watchdog.start()
    try:
        return run_fn()
    finally:
        watchdog.cancel()
        _teardown("job-exit")                      # normal/failed exit -> release now (no idle GPU)


def make_subprocess_terminator(self_terminate_cmd: list):
    """Build a terminate_fn that runs the backend's self_terminate argv (e.g. `runpodctl remove pod ...`). An
    EMPTY command (managed backends: SageMaker/Slurm) yields a no-op terminator, since the platform already
    releases the instance on exit."""
    def _terminate(reason):
        if not self_terminate_cmd:
            print(f"[teardown] managed backend, platform auto-releases ({reason})", flush=True)
            return
        print(f"[teardown] releasing GPU via {' '.join(self_terminate_cmd)} ({reason})", flush=True)
        try:
            subprocess.run(self_terminate_cmd, timeout=120, check=False)
        except Exception as e:  # noqa: BLE001 — never let teardown failure mask the job result; log loudly
            print(f"[teardown] WARNING self-terminate failed ({e}); instance may idle — check the provider!",
                  flush=True)
    return _terminate


def entrypoint(job_argv: list, self_terminate_cmd: list, max_runtime_s: float) -> int:
    """Real on-provider entrypoint: run the MD/FEP driver as a subprocess and guarantee teardown. The driver is
    expected to checkpoint per-unit to the object store itself, so a mid-run teardown loses <= 1 unit."""
    def _run():
        return subprocess.run(job_argv, check=False).returncode
    rc = run_with_teardown(_run, make_subprocess_terminator(self_terminate_cmd), max_runtime_s)
    return rc if isinstance(rc, int) else 0


if __name__ == "__main__":
    import os
    import sys
    from gpu_backend import get_backend
    be = get_backend(os.environ.get("BACKEND", "mock"))
    cmd = sys.argv[1:] or ["true"]
    sys.exit(entrypoint(cmd, be.self_terminate_cmd(), float(os.environ.get("MAX_RUNTIME_S", "72000"))))
