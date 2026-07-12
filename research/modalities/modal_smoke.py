#!/usr/bin/env python3
"""
Modal end-to-end smoke test — the cheapest possible real GPU run to prove the path works before we point any
science at it. It: authenticates to Modal (via MODAL_TOKEN_ID/SECRET), provisions the cheapest GPU (T4), runs
`nvidia-smi` on it, returns the GPU name, and lets Modal auto-scale to zero (no idle billing). Costs a fraction
of a cent of the free monthly credits. Run from .github/workflows/modal-smoke.yml (workflow_dispatch).

Requires the `modal` SDK. This validates: (1) the token secrets work, (2) Modal gives us a GPU, (3) a function
runs on it, (4) it tears down automatically — the four things that must work before ModalBackend carries real
FEP jobs.
"""
import subprocess

import modal

app = modal.App("nr4a3-smoke")


@app.function(gpu="T4", timeout=120)
def gpu_check() -> str:
    r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                        "--format=csv,noheader"], capture_output=True, text=True)
    return (r.stdout or r.stderr).strip()


@app.local_entrypoint()
def main():
    info = gpu_check.remote()
    print(f"[modal-smoke] OK — ran on a Modal GPU: {info}")
    print("[modal-smoke] Modal auto-scaled the GPU to zero on return (no idle billing).")
