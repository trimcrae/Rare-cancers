#!/usr/bin/env python
"""OpenFE/openmmtools RESTART-SEMANTICS probe v2 (CPU, free CI).

Establishes ground truth for the spot-resume fix. v2 fixes: (a) Q2 no longer pre-creates the
.nc (create() owns it); (b) removes the bad write_checkpoint introspection; (c) dumps the
OpenFE MultiState simulation-unit source LAST (so the CI log tail keeps it) and text-greps it
for the equilibration/minimize/restart decision — the one fact the fix hinges on:
    does OpenFE re-equilibrate UNCONDITIONALLY on every job start, or only when the restored
    sampler is at iteration 0 (i.e. only because the checkpoint never became durable)?
"""
import inspect
import os
import re
import shutil
import sys
import tempfile
import traceback


def _hr(t):
    print("\n" + "=" * 92 + f"\n=== {t}\n" + "=" * 92, flush=True)


def q2_openmmtools_resume():
    _hr("Q2  openmmtools resume behaviour on a tiny CPU replica-exchange")
    try:
        from openmmtools import cache, states, testsystems
        from openmmtools.multistate import MultiStateReporter, ReplicaExchangeSampler
        from openmmtools.mcmc import LangevinDynamicsMove
        import openmm
        from openmm import unit
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] imports failed: {e!r}\n{traceback.format_exc()}", flush=True)
        return
    cache.global_context_cache.platform = openmm.Platform.getPlatformByName("CPU")
    ts = testsystems.AlanineDipeptideImplicit()
    thermo = [states.ThermodynamicState(ts.system, temperature=T * unit.kelvin)
              for T in (300.0, 330.0, 360.0)]
    sstate = states.SamplerState(positions=ts.positions)
    tmp = tempfile.mkdtemp(prefix="ommprobe_")
    nc = os.path.join(tmp, "simulation.nc")
    CI = 2

    def _reporter(mode):
        # NOTE: do NOT pre-create with open_mode='w'; let create() own the file.
        return MultiStateReporter(nc, open_mode=mode, checkpoint_interval=CI)

    def _read_iters(path):
        r = MultiStateReporter(path, open_mode="r", checkpoint_storage="checkpoint.chk")
        try:
            ana = r.read_last_iteration(last_checkpoint=False)
            try:
                ck = r.read_last_iteration(last_checkpoint=True)
            except Exception as e:  # noqa: BLE001
                ck = f"RAISED {type(e).__name__}"
        finally:
            r.close()
        return ana, ck

    move = LangevinDynamicsMove(timestep=2.0 * unit.femtosecond, n_steps=25)
    smp = ReplicaExchangeSampler(mcmc_moves=move, number_of_iterations=6)
    smp.create(thermodynamic_states=thermo, sampler_states=sstate, storage=_reporter("w"))
    print(f"[Q2] after create(): _iteration={smp._iteration}", flush=True)
    smp.minimize()
    print(f"[Q2] after minimize(): _iteration={smp._iteration}  "
          f"read={_read_iters(nc)} (analysis,checkpoint)", flush=True)
    smp.run(n_iterations=2)
    print(f"[Q2] after run(2): _iteration={smp._iteration}  read={_read_iters(nc)}", flush=True)

    # snapshot BOTH files after a checkpointed iteration (our sidecar's atomic-copy idea)
    snap = os.path.join(tmp, "snap")
    os.makedirs(snap, exist_ok=True)
    for fn in os.listdir(tmp):
        if fn.endswith((".nc", ".chk")):
            shutil.copy2(os.path.join(tmp, fn), os.path.join(snap, fn))
    print(f"[Q2] snapshot @ iter {smp._iteration}: files={sorted(os.listdir(snap))}", flush=True)

    smp.run(n_iterations=2)  # advance to iter 4 (progress since snapshot)
    print(f"[Q2] after run(4 total): _iteration={smp._iteration}", flush=True)
    del smp

    try:
        rep2 = MultiStateReporter(nc, open_mode="r+", checkpoint_storage="checkpoint.chk")
        s2 = ReplicaExchangeSampler.from_storage(rep2)
        print(f"[Q2] from_storage(LIVE): resumed _iteration={s2._iteration} (expect 4)", flush=True)
        del s2
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] from_storage(LIVE) failed: {e!r}", flush=True)

    try:
        rep3 = MultiStateReporter(os.path.join(snap, "simulation.nc"), open_mode="r+",
                                  checkpoint_storage="checkpoint.chk")
        s3 = ReplicaExchangeSampler.from_storage(rep3)
        print(f"[Q2] from_storage(SNAPSHOT copy): resumed _iteration={s3._iteration} "
              f"(expect 2 -> an atomically-copied checkpoint IS resumable)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] from_storage(SNAPSHOT) failed: {e!r}\n{traceback.format_exc()}", flush=True)

    # .nc only (no .chk): what breaks if only one file is durable
    only = os.path.join(tmp, "onlync")
    os.makedirs(only, exist_ok=True)
    shutil.copy2(nc, os.path.join(only, "simulation.nc"))
    print(f"[Q2] .nc-only (no .chk) read={_read_iters(os.path.join(only, 'simulation.nc'))} "
          f"(checkpoint read should RAISE / be 0 -> .chk MUST be durable too)", flush=True)


def _grep_source(src, keywords, ctx=3):
    lines = src.splitlines()
    hits = []
    for i, ln in enumerate(lines):
        if any(k in ln.lower() for k in keywords):
            lo, hi = max(0, i - ctx), min(len(lines), i + ctx + 1)
            hits.append((i, "\n".join(f"    {j+1:5d}| {lines[j]}" for j in range(lo, hi))))
    return hits


def q1_openfe_source():
    _hr("Q1 (LAST)  OpenFE MultiState simulation-unit: equilibration/minimize/restart logic")
    try:
        import openfe
        print("openfe version:", getattr(openfe, "__version__", "?"), flush=True)
        import importlib
        mod = importlib.import_module("openfe.protocols.openmm_rfe.equil_rfe_methods")
    except Exception as e:  # noqa: BLE001
        print(f"[Q1] import failed: {e!r}", flush=True)
        return
    # dump full module source text once, then grep the decision points
    try:
        modsrc = inspect.getsource(mod)
    except Exception as e:  # noqa: BLE001
        modsrc = ""
        print(f"[Q1] module getsource failed: {e!r}", flush=True)
    kw = ("equilibr", "minimize", "restart", "from_storage", ".run(", "sampler.run",
          "checkpoint", "_check_restart", "last_iteration")
    print(f"\n[Q1] GREP of equil_rfe_methods for {kw}:", flush=True)
    for i, block in _grep_source(modsrc, kw):
        print(block, flush=True)
        print("    ----", flush=True)
    # find the simulation unit class + dump its _execute / run
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and ("SimulationUnit" in name or "ProtocolUnit" in name
                                      or "RFEUnit" in name):
            print(f"\n[Q1] class {name}: {[m for m in dir(obj) if not m.startswith('__')][:40]}",
                  flush=True)
            for meth in ("_execute", "run", "_run_simulation", "_check_restart",
                         "_get_reporter", "_get_sampler", "_get_integrator", "_prepare"):
                m = getattr(obj, meth, None)
                if callable(m):
                    try:
                        s = inspect.getsource(m)
                        print(f"\n----- {name}.{meth} ({len(s.splitlines())} lines) -----\n{s}",
                              flush=True)
                    except Exception as e:  # noqa: BLE001
                        print(f"[Q1] getsource {name}.{meth} failed: {e!r}", flush=True)


if __name__ == "__main__":
    print("[ommprobe v2] python", sys.version, flush=True)
    try:
        q2_openmmtools_resume()
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] fatal: {e!r}\n{traceback.format_exc()}", flush=True)
    q1_openfe_source()   # LAST so the CI log tail keeps the OpenFE decision logic
    print("\n[ommprobe v2] DONE", flush=True)
