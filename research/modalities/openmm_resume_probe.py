#!/usr/bin/env python
"""OpenFE/openmmtools RESTART-SEMANTICS probe (CPU, free CI).

Purpose: establish the GROUND TRUTH the spot-resume fix must be built on, without guessing.
Answers, empirically + from source:
  Q1. What EXACT restart logic does OpenFE 1.12's MultiState simulation unit run? (dump source)
       - where it decides re-equilibrate vs resume, what files _check_restart needs, and whether
         equilibration is checkpointed / gated on iteration==0.
  Q2. openmmtools MultiStateSampler resume semantics on a TINY system (CPU):
       - after create(): what does read_last_iteration(last_checkpoint=True/False) return?
       - after run(N) with a small checkpoint_interval: does read_last_iteration advance?
       - from_storage() on that reporter: does _iteration resume >0 (skip re-equilibration)?
       - is a COPIED .nc/.chk (simulating our sidecar snapshot) resumable, and does copying
         only .nc (not .chk), or a torn .chk, break resume? (tells us the durability contract)
  Q3. Can we force a checkpoint to be WRITTEN at an arbitrary point (so a resume lands >0)?

Everything is CPU + tiny; no GPU, no real chemistry. Pure diagnosis.
"""
import inspect
import os
import shutil
import sys
import tempfile
import traceback


def _hr(t):
    print("\n" + "=" * 92 + f"\n=== {t}\n" + "=" * 92, flush=True)


def _dump_source(obj, label, maxlines=220):
    try:
        src = inspect.getsource(obj)
        lines = src.splitlines()
        print(f"\n----- SOURCE {label}  ({getattr(obj,'__module__','?')}) [{len(lines)} lines]"
              f"{'  (TRUNCATED)' if len(lines) > maxlines else ''} -----", flush=True)
        print("\n".join(lines[:maxlines]), flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[dump] could not getsource({label}): {e!r}", flush=True)


def q1_openfe_source():
    _hr("Q1  OpenFE 1.12 MultiState simulation-unit restart logic (source of truth)")
    try:
        import openfe
        print("openfe version:", getattr(openfe, "__version__", "?"), flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[Q1] openfe import failed: {e!r}", flush=True)
        return
    # Locate the RFE protocol units. In 1.12 the MD lives in openfe.protocols.openmm_rfe.
    import importlib
    candidates = [
        "openfe.protocols.openmm_rfe.equil_rfe_methods",
        "openfe.protocols.openmm_rfe",
        "openfe.protocols.openmm_utils.multistate_analysis",
    ]
    seen = set()
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
        except Exception as e:  # noqa: BLE001
            print(f"[Q1] import {modname} failed: {e!r}", flush=True)
            continue
        print(f"\n[Q1] scanning module {modname}:", flush=True)
        for name in dir(mod):
            obj = getattr(mod, name)
            if not isinstance(obj, type):
                continue
            if id(obj) in seen:
                continue
            low = name.lower()
            if any(k in low for k in ("simulationunit", "setupunit", "protocolunit",
                                      "multistate", "hybridtopology")):
                seen.add(id(obj))
                print(f"  class {name}: methods = "
                      f"{[m for m in dir(obj) if not m.startswith('__')][:40]}", flush=True)
                # dump the methods most likely to hold the restart/equilibration decision
                for meth in ("_execute", "run", "_check_restart", "_run_simulation",
                             "execute", "_pre_equilibrate", "equilibrate"):
                    m = getattr(obj, meth, None)
                    if m is not None and callable(m):
                        _dump_source(m, f"{name}.{meth}")
    # openmmtools sampler: the equilibrate + from_storage + iteration handling
    _hr("Q1b  openmmtools MultiStateSampler.equilibrate / from_storage / _iteration semantics")
    try:
        from openmmtools import multistate
        for meth in ("equilibrate", "from_storage", "_restore_sampler_from_reporter",
                     "run", "_report_iteration", "create", "minimize", "extend"):
            m = getattr(multistate.MultiStateSampler, meth, None)
            if m is not None:
                _dump_source(m, f"MultiStateSampler.{meth}", maxlines=120)
        _dump_source(multistate.MultiStateReporter.read_last_iteration,
                     "MultiStateReporter.read_last_iteration", maxlines=80)
        _dump_source(multistate.MultiStateReporter.write_checkpoint,
                     "MultiStateReporter.write_checkpoint", maxlines=60)
    except Exception as e:  # noqa: BLE001
        print(f"[Q1b] openmmtools introspection failed: {e!r}\n{traceback.format_exc()}", flush=True)


def q2_openmmtools_resume():
    _hr("Q2  openmmtools resume behaviour on a tiny CPU replica-exchange")
    try:
        from openmmtools import cache, states, testsystems
        from openmmtools.multistate import MultiStateReporter, ReplicaExchangeSampler
        import openmm
        from openmm import unit
        from openmmtools.mcmc import LangevinDynamicsMove
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] imports failed: {e!r}\n{traceback.format_exc()}", flush=True)
        return
    cache.global_context_cache.platform = openmm.Platform.getPlatformByName("CPU")
    testsystem = testsystems.AlanineDipeptideImplicit()
    n_states = 3
    thermo = [states.ThermodynamicState(testsystem.system, temperature=T * unit.kelvin)
              for T in (300.0, 330.0, 360.0)]
    sampler_state = states.SamplerState(positions=testsystem.positions)

    tmp = tempfile.mkdtemp(prefix="ommprobe_")
    nc = os.path.join(tmp, "simulation.nc")
    chk = "checkpoint.chk"

    def _new_sampler(ci):
        move = LangevinDynamicsMove(timestep=2.0 * unit.femtosecond, n_steps=50)
        return ReplicaExchangeSampler(mcmc_moves=move, number_of_iterations=4,
                                      online_analysis_interval=None), MultiStateReporter(
            nc, open_mode="w", checkpoint_interval=ci)

    def _rep_read(path, ci):
        r = MultiStateReporter(path, open_mode="r", checkpoint_storage=chk)
        try:
            ana = r.read_last_iteration(last_checkpoint=False)
            ck = r.read_last_iteration(last_checkpoint=True)
        finally:
            r.close()
        return ana, ck

    CI = 2  # checkpoint every 2 iterations
    smp, rep = _new_sampler(CI)
    smp.create(thermodynamic_states=thermo, sampler_states=sampler_state, storage=rep)
    print(f"[Q2] after create(): _iteration={smp._iteration}", flush=True)
    ana, ck = _rep_read(nc, CI)
    print(f"[Q2] after create(): read_last_iteration analysis={ana} checkpoint={ck}", flush=True)

    smp.run(n_iterations=2)
    print(f"[Q2] after run(2): _iteration={smp._iteration}", flush=True)
    ana, ck = _rep_read(nc, CI)
    print(f"[Q2] after run(2): read_last_iteration analysis={ana} checkpoint={ck}", flush=True)

    # snapshot BOTH files (our sidecar's atomic-copy idea) after a checkpointed iteration
    snap = os.path.join(tmp, "snap")
    os.makedirs(snap, exist_ok=True)
    for fn in os.listdir(tmp):
        if fn.endswith(".nc") or fn.endswith(".chk"):
            shutil.copy2(os.path.join(tmp, fn), os.path.join(snap, fn))
    print(f"[Q2] snapshot files: {sorted(os.listdir(snap))}", flush=True)

    smp.run(n_iterations=2)  # advance to iter 4 (simulate progress since the snapshot)
    print(f"[Q2] after run(4 total): _iteration={smp._iteration}", flush=True)
    del smp, rep

    # RESUME from the live storage (openmmtools native from_storage)
    try:
        from openmmtools.multistate import ReplicaExchangeSampler as RES
        rep2 = MultiStateReporter(nc, open_mode="r+", checkpoint_storage=chk)
        smp2 = RES.from_storage(rep2)
        print(f"[Q2] from_storage(LIVE): resumed _iteration={smp2._iteration} "
              f"(>0 => production resumes, no re-equilibration)", flush=True)
        del smp2
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] from_storage(LIVE) failed: {e!r}", flush=True)

    # RESUME from the SNAPSHOT copy (does an atomic file copy give a resumable checkpoint?)
    try:
        rep3 = MultiStateReporter(os.path.join(snap, "simulation.nc"), open_mode="r+",
                                  checkpoint_storage=chk)
        from openmmtools.multistate import ReplicaExchangeSampler as RES
        smp3 = RES.from_storage(rep3)
        print(f"[Q2] from_storage(SNAPSHOT copy): resumed _iteration={smp3._iteration} "
              f"(should == snapshot's checkpoint iter, i.e. 2)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] from_storage(SNAPSHOT) failed: {e!r}\n{traceback.format_exc()}", flush=True)

    # RESUME from a copy with ONLY the .nc (no .chk) — the torn/partial-durability case
    try:
        only = os.path.join(tmp, "onlync")
        os.makedirs(only, exist_ok=True)
        shutil.copy2(nc, os.path.join(only, "simulation.nc"))
        rep4 = MultiStateReporter(os.path.join(only, "simulation.nc"), open_mode="r",
                                  checkpoint_storage=chk)
        ana4 = rep4.read_last_iteration(last_checkpoint=False)
        try:
            ck4 = rep4.read_last_iteration(last_checkpoint=True)
        except Exception as e:  # noqa: BLE001
            ck4 = f"RAISED {e!r}"
        rep4.close()
        print(f"[Q2] .nc-only (no .chk): analysis={ana4} checkpoint={ck4} "
              f"(shows what breaks if only one file is durable)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] .nc-only probe failed: {e!r}", flush=True)

    print(f"[Q2] tmp dir (left for inspection): {tmp}", flush=True)


if __name__ == "__main__":
    print("[ommprobe] python", sys.version, flush=True)
    q1_openfe_source()
    try:
        q2_openmmtools_resume()
    except Exception as e:  # noqa: BLE001
        print(f"[Q2] fatal: {e!r}\n{traceback.format_exc()}", flush=True)
    print("\n[ommprobe] DONE", flush=True)
