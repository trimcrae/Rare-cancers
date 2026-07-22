#!/usr/bin/env python3
"""
Vast.ai one-instance smoke — confirm the live REST endpoint shapes the in-repo unit tests can't exercise.

Runs on a GitHub Actions runner where VAST_API_KEY is a secret (the dev sandbox's egress proxy 403s many hosts;
CI runners have open internet). Exercises the REAL adapter code paths in gpu_backend.py, not a reimplementation.

Two phases:
  PHASE 1 (default, $0 — read-only): auth check (GET /instances/) + the real offer search
           (_vast_offer_query -> GET /bundles/ -> _select_cheapest_offer). Confirms the key works and that the
           marketplace has a rentable RTX-4090-class offer, and prints what we'd rent. No spend.
  PHASE 2 (only if VAST_SMOKE_LAUNCH=1 — costs a few cents): actually submit() the cheapest instance with an
           onstart that runs `nvidia-smi` then SELF-DESTROYS, polls status() until it leaves 'queued', then
           calls stop() as a teardown backstop. Confirms submit/status/stop end-to-end + the anti-idle guard.

Pure stdlib (urllib via the adapter). Exit non-zero on any failed assertion so CI goes red.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modalities"))

from gpu_backend import (  # noqa: E402
    JobSpec, ResourceSpec, VastBackend, _select_cheapest_offer, _vast_offer_query, _vast_request,
)


def phase1_readonly(key: str, res: ResourceSpec) -> dict:
    import hashlib
    print("== PHASE 1: read-only (auth + offer search, $0) ==", flush=True)
    # Safe fingerprint (NOT the key): proves whether the secret value actually changed between runs, so a
    # repeat 401 tells us "old key still in the secret" vs "new key lacks the permission".
    fp = hashlib.sha256(key.strip().encode()).hexdigest()[:8]
    print(f"[key] len={len(key)} sha256_8={fp} (fingerprint only — not the key)", flush=True)

    inst = _vast_request("GET", "/instances/", key, params={"owner": "me"})
    running = inst.get("instances", [])
    print(f"[auth OK] account reachable; {len(running)} instance(s) currently up", flush=True)

    q = _vast_offer_query(res)
    print(f"[query] {q}", flush=True)

    # Endpoint DISCOVERY: Vast's search path/verb has drifted across API versions and the CLI-source summary
    # was unreliable (/offers/ 404s). Probe the plausible candidates in ONE run and report which returns offers,
    # so we wire the adapter to the confirmed one instead of redispatching per guess.
    candidates = [
        ("GET",  "/bundles/",     {"q": json.dumps(q)}, None),
        ("GET",  "/bundles",      {"q": json.dumps(q)}, None),
        ("PUT",  "/bundles/",     None,                 q),
        ("PUT",  "/search/asks/", None,                 q),
        ("POST", "/search/asks/", None,                 q),
        ("GET",  "/search/asks/", {"q": json.dumps(q)}, None),
        ("POST", "/offers/",      None,                 q),
    ]
    offers, winner = [], None
    for verb, path, params, body in candidates:
        try:
            resp = _vast_request(verb, path, key, params=params, body=body)
            keys = list(resp.keys()) if isinstance(resp, dict) else type(resp).__name__
            got = resp.get("offers") or resp.get("asks") or resp.get("bundles") or []
            print(f"[probe] {verb:4} {path:16} -> OK keys={keys} n={len(got)}", flush=True)
            if got and winner is None:
                offers, winner = got, (verb, path, "params" if params else "body")
        except Exception as e:  # noqa: BLE001
            msg = str(e).split(" -> ", 1)[-1][:120]
            print(f"[probe] {verb:4} {path:16} -> {msg}", flush=True)
    if winner is None:
        raise SystemExit("FAIL: no search endpoint returned offers — see [probe] lines above")
    print(f"[search] WINNER {winner} -> {len(offers)} offer(s)", flush=True)

    chosen = _select_cheapest_offer(offers, res)
    if chosen is None:
        raise SystemExit(f"FAIL: {len(offers)} offers but none met {res} (single-GPU, >= {res.min_vram_gb} GB)")
    print(f"[pick] id={chosen['id']} gpu={chosen.get('gpu_name')} "
          f"vram={chosen.get('gpu_ram')}MB dph_total=${chosen.get('dph_total')}/hr "
          f"host={chosen.get('geolocation','?')}", flush=True)
    print("PHASE 1 OK — key valid, marketplace has a rentable RTX-4090-class offer.\n", flush=True)
    return chosen


def phase2_launch(res: ResourceSpec):
    print("== PHASE 2: launch cheapest, run nvidia-smi, self-destroy (spends a few cents) ==", flush=True)
    be = VastBackend()
    spec = JobSpec(
        name="vast-smoke",
        command=["bash", "-lc", "nvidia-smi && echo VAST_SMOKE_GPU_OK"],
        image="nvidia/cuda:12.4.1-base-ubuntu22.04",
        resources=res,
        max_runtime_s=900,
    )
    handle = be.submit(spec)
    print(f"[submit] instance id={handle.job_id} offer={handle.extra.get('offer')} "
          f"dph=${handle.extra.get('dph')}/hr", flush=True)
    try:
        for i in range(20):                                  # ~5 min: wait for it to leave 'queued'
            st = be.status(handle)
            print(f"[poll {i}] status={st}", flush=True)
            if st in ("running", "completed", "failed", "stopped"):
                break
            time.sleep(15)
        print(f"PHASE 2 reached status={st}", flush=True)
    finally:
        # backstop teardown (the onstart self-destroys, but never leave a rented GPU up on a smoke).
        try:
            be.stop(handle)
            print(f"[cleanup] stop() issued for instance {handle.job_id}", flush=True)
        except Exception as e:                               # noqa: BLE001
            print(f"[cleanup] stop() raised (instance may already be self-destroyed): {e}", flush=True)


def main():
    key = os.environ.get("VAST_API_KEY")
    if not key:
        raise SystemExit("FAIL: VAST_API_KEY not set (add it as a repo Actions secret).")
    res = ResourceSpec(gpu="rtx4090", min_vram_gb=24, interruptible=True)
    phase1_readonly(key, res)
    if os.environ.get("VAST_SMOKE_LAUNCH") == "1":
        phase2_launch(res)
    else:
        print("PHASE 2 skipped (set VAST_SMOKE_LAUNCH=1 to actually rent+destroy a GPU).", flush=True)
    print("\nVAST SMOKE DONE.", flush=True)


if __name__ == "__main__":
    main()
