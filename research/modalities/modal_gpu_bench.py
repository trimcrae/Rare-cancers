#!/usr/bin/env python3
"""Modal GPU ns/$ benchmark — pick the GPU that yields the MOST ns from the fixed $30 Modal credit.

We have a fixed, Modal-locked $30 credit to spend on MD, so the objective is pure: maximize total ns =
maximize ns per Modal-dollar. Theory says L4 wins for classical MD (no tensor-core benefit above it), but Modal
could throttle a given GPU type, so we MEASURE ns/day per GPU on the repo's standard benchmark system
(gpu_md_bench.py: ~36k-atom TIP3P/PME, 4000 steps @ 4 fs HMR, CUDA) and divide by Modal's real $/hr.

Each GPU is its own @app.function (Modal fixes gpu= at decoration time). Cheap: ~2-3 min / GPU, a few cents each.
Driven by modal-rbfe.yml mode=bench. Rates below are Modal's published on-demand $/hr — verify against billing;
the RANKING is what matters and is robust to small rate errors.
"""
import os
import re

import modal

app = modal.App("nr4a3-gpu-bench")
# Use the SAME conda-forge CUDA OpenMM the production RBFE leg runs (driver-matched CUDA that actually works on
# the Modal GPU) — the pip wheel on debian_slim only exposed Reference/CPU. openmm-only (no openfe) keeps it light.
image = (
    modal.Image.micromamba(python_version="3.11")
    .micromamba_install("openmm", "cuda-version=12.6", "ocl-icd-system", "numpy", "git",
                        channels=["conda-forge"])
)

GIT_REF = os.environ.get("GIT_REF", "claude/rung-2-parallel-7asnpk")

# Modal on-demand $/hr (approx; 2024-25 published). Update if Modal changes pricing — ranking is robust.
RATES = {"T4": 0.59, "L4": 0.80, "A10G": 1.10, "L40S": 1.95, "A100": 2.10, "A100-80GB": 2.50, "H100": 3.95}


def _core(tag: str) -> dict:
    import subprocess
    import sys

    subprocess.run(["apt-get", "-qq", "install", "-y", "git"], check=False)
    subprocess.run(["git", "clone", "--depth", "1", "--branch", GIT_REF,
                    "https://github.com/trimcrae/Rare-cancers", "/tmp/repo"], check=True)
    env = os.environ.copy()
    env.update({"BENCH_TAG": tag, "OPENMM_REQUIRE_CUDA": "1"})
    r = subprocess.run([sys.executable, "gpu_md_bench.py"], cwd="/tmp/repo/research/modalities",
                       env=env, capture_output=True, text=True)
    out = (r.stdout or "") + "\n" + (r.stderr or "")[-1500:]
    print(out, flush=True)
    m = re.search(r"ns_per_day=([\d.]+)", out)
    dev = re.search(r"device='([^']*)'", out)
    plat = re.search(r"platform=(\w+)", out)
    return {"tag": tag, "ns_per_day": float(m.group(1)) if m else None,
            "device": dev.group(1) if dev else None, "platform": plat.group(1) if plat else None,
            "cores": os.cpu_count()}


@app.function(image=image, gpu="T4", timeout=600)
def bench_t4():
    return _core("T4")


@app.function(image=image, gpu="L4", timeout=600)
def bench_l4():
    return _core("L4")


@app.function(image=image, gpu="A10G", timeout=600)
def bench_a10g():
    return _core("A10G")


@app.function(image=image, gpu="L40S", timeout=600)
def bench_l40s():
    return _core("L40S")


@app.function(image=image, gpu="A100", timeout=600)
def bench_a100():
    return _core("A100")


@app.function(image=image, gpu="H100", timeout=600)
def bench_h100():
    return _core("H100")


_FNS = {"T4": bench_t4, "L4": bench_l4, "A10G": bench_a10g, "L40S": bench_l40s,
        "A100": bench_a100, "H100": bench_h100}


@app.local_entrypoint()
def main(gpus: str = "T4,L4,A10G,L40S"):
    """Bench each GPU (comma list), then rank by ns/$ = ns_per_day / ($/hr * 24)."""
    results = []
    for g in [x.strip() for x in gpus.split(",") if x.strip()]:
        if g not in _FNS:
            print(f"[bench] skip unknown GPU {g}")
            continue
        try:
            r = _FNS[g].remote()
        except Exception as e:  # noqa: BLE001 — a GPU class may be unavailable; keep going
            print(f"[bench] {g} FAILED: {e}")
            continue
        rate = RATES.get(g)
        nspd = r.get("ns_per_day")
        r["rate_per_hr"] = rate
        r["ns_per_dollar"] = round(nspd / (rate * 24.0), 1) if (nspd and rate) else None
        results.append(r)
        print(f"[bench] {g}: {nspd} ns/day | {r.get('device')} | {r.get('platform')} | ns/$={r['ns_per_dollar']}")

    ranked = sorted([r for r in results if r.get("ns_per_dollar")], key=lambda r: -r["ns_per_dollar"])
    print("\n=== ns/$ RANKING (max ns/$ = max total ns from the fixed $30) ===")
    for r in ranked:
        print(f"  {r['tag']:6s} ns/day={r['ns_per_day']:8.1f}  ${r['rate_per_hr']}/hr  "
              f"ns/$={r['ns_per_dollar']:6.1f}  dev={r.get('device')}")
    if ranked:
        w = ranked[0]
        print(f"\nWINNER: {w['tag']} @ {w['ns_per_dollar']} ns/$  →  use this GPU to maximize ns from $30")
