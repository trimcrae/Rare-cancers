#!/usr/bin/env python3
"""GPU MD throughput micro-benchmark for the L4-vs-T4 (or any GCE GPU) cost decision.

WHY: the going-forward GPU choice is decided by COST PER FINISHED JOB = spot $/hr x wall-clock. Wall-clock =
work / throughput, so for a fixed workload the deciding quantity is (spot $/hr) / throughput = $ per ns of MD.
This script measures throughput (ns/day) on whatever GPU it lands on, using a PME explicit-solvent system sized
like our RBFE legs (OpenMM is the same engine OpenFE's RelativeHybridTopology protocol runs under), so the
number maps directly to RBFE wall-clock. The workflow combines this with each VM's live Spot price.

Self-contained: builds a TIP3P water box (no external files), runs NVT PME at 4 fs with hydrogen-mass
repartitioning (matches our production MD settings), times production only (excludes JIT/warmup). Prints a
single machine-parsable RESULT line the launcher greps from the serial console.

Representative sizes (approx atom counts): solvent-leg ~ small; complex-leg (TYK2) ~ 30-40k. Default ~36k
edge-length so it stresses PME like a complex leg AND reports whether it fits the GPU's VRAM (the T4=16GB vs
L4=24GB constraint that can override raw $/ns).
"""
import os
import sys
import time


def _bench(edge_nm, steps, warmup, dt_fs):
    import openmm as mm
    import openmm.app as app
    import openmm.unit as u

    # ---- build a cubic TIP3P water box of the requested edge length ----
    ff = app.ForceField("amber14/tip3p.xml")
    modeller = app.Modeller(app.Topology(), [])
    box = edge_nm * u.nanometer
    modeller.addSolvent(ff, boxSize=mm.Vec3(edge_nm, edge_nm, edge_nm) * u.nanometer, model="tip3p")
    n_atoms = modeller.topology.getNumAtoms()

    system = ff.createSystem(modeller.topology, nonbondedMethod=app.PME,
                             nonbondedCutoff=1.0 * u.nanometer, constraints=app.HBonds,
                             hydrogenMass=4.0 * u.amu)   # HMR -> 4 fs, our production setting
    integrator = mm.LangevinMiddleIntegrator(300 * u.kelvin, 1.0 / u.picosecond, dt_fs * u.femtoseconds)

    # pick the platform + report it. CUDA is ~1.5-2x faster than OpenCL on NVIDIA; the CUDA plugin only loads if
    # OpenMM's CUDA build matches the driver — getPluginLoadFailures() says exactly why it didn't if so.
    plats = [mm.Platform.getPlatform(i).getName() for i in range(mm.Platform.getNumPlatforms())]
    fails = [str(f) for f in mm.Platform.getPluginLoadFailures()]
    print(f"[bench] platforms={plats}", flush=True)
    if fails:
        print(f"[bench] plugin_load_failures={fails}", flush=True)
    # canonical OPENMM_REQUIRE_CUDA (shared with the production rbfe/abfe selectors); BENCH_REQUIRE_CUDA alias.
    _rc = os.environ.get("OPENMM_REQUIRE_CUDA", os.environ.get("BENCH_REQUIRE_CUDA", "")).strip().lower()
    require_cuda = _rc in ("1", "true", "yes", "on")
    if require_cuda and "CUDA" not in plats:
        raise RuntimeError(f"CUDA platform REQUIRED but unavailable. platforms={plats}; failures={fails}")
    plat_name = "CUDA" if "CUDA" in plats else ("OpenCL" if "OpenCL" in plats else "CPU")
    platform = mm.Platform.getPlatformByName(plat_name)
    props = {"Precision": "mixed"} if plat_name in ("CUDA", "OpenCL") else {}

    sim = app.Simulation(modeller.topology, system, integrator, platform, props)
    sim.context.setPositions(modeller.positions)
    sim.minimizeEnergy(maxIterations=200)
    sim.context.setVelocitiesToTemperature(300 * u.kelvin)

    sim.step(warmup)                      # exclude JIT + equilibration transient
    t0 = time.time()
    sim.step(steps)
    sim.context.getState(getEnergy=True)  # force sync so timing includes the last kernel
    wall_s = time.time() - t0

    ns = steps * dt_fs * 1e-6             # simulated ns
    ns_per_day = ns / (wall_s / 86400.0)
    dev = ""
    try:
        dev = props and platform.getPropertyValue(sim.context, "DeviceName") or ""
    except Exception:  # noqa: BLE001
        pass
    return n_atoms, plat_name, dev, wall_s, ns_per_day


def main():
    edge_nm = float(os.environ.get("BENCH_EDGE_NM", "7.1"))   # ~36k atoms; representative of a complex leg
    steps = int(os.environ.get("BENCH_STEPS", "4000"))
    warmup = int(os.environ.get("BENCH_WARMUP", "1000"))
    dt_fs = float(os.environ.get("BENCH_DT_FS", "4.0"))
    tag = os.environ.get("BENCH_TAG", "bench")
    try:
        n_atoms, plat, dev, wall_s, ns_day = _bench(edge_nm, steps, warmup, dt_fs)
    except Exception as e:  # noqa: BLE001
        print(f"BENCH_RESULT tag={tag} status=ERROR err={type(e).__name__}:{e}", flush=True)
        sys.exit(1)
    # single parsable line the launcher scrapes from the serial console
    print(f"BENCH_RESULT tag={tag} status=OK atoms={n_atoms} platform={plat} device='{dev}' "
          f"steps={steps} dt_fs={dt_fs} wall_s={wall_s:.1f} ns_per_day={ns_day:.2f}", flush=True)


if __name__ == "__main__":
    main()
