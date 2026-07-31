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



def block_stats(block_ns_day):
    """PURE. Mean / SD / CV over independent timed blocks.

    The CV is the point: a single timed window cannot tell a steady 700 ns/day card from a contended host
    averaging 700 with blocks at 400 and 1000. Callers reject on CV rather than trusting a bare mean."""
    if not block_ns_day:
        return 0.0, 0.0, 0.0
    mean = sum(block_ns_day) / len(block_ns_day)
    if len(block_ns_day) > 1:
        sd = (sum((x - mean) ** 2 for x in block_ns_day) / (len(block_ns_day) - 1)) ** 0.5
    else:
        sd = 0.0
    return mean, sd, (sd / mean if mean else 0.0)


_KB_KJ = 0.00831446261815324   # kJ/mol/K


def health_check(pe, ke, n_atoms, n_constraints):
    """PURE. (final temperature, is-this-valid-MD). A diverged system integrates FAST and reports a large,
    entirely fake ns/day, so a throughput number is only meaningful alongside this."""
    dof = max(1, 3 * n_atoms - n_constraints)
    temp_k = 2 * ke / (dof * _KB_KJ)
    finite = (pe == pe) and (ke == ke) and abs(pe) < 1e12 and abs(ke) < 1e12   # NaN-safe: NaN != NaN
    return temp_k, bool(finite and 150.0 < temp_k < 450.0)


def _bench(edge_nm, steps, warmup, dt_fs, minimize_iters=200):
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

    # A conda-pack'd / baked env can carry a STALE compiled OpenMM plugin dir so NOTHING auto-loads (only the
    # built-in 'Reference' shows, failures=[] because no plugin was even attempted — verified 2026-07-23 on Vast).
    # Mirror nrv04_covalent_md._select_platform: if neither CUDA nor CPU is present, load plugins explicitly from
    # this env's lib/plugins (glob covers /opt/mamba/envs/{md,rbfe}/lib/plugins).
    _names = [mm.Platform.getPlatform(i).getName() for i in range(mm.Platform.getNumPlatforms())]
    if "CUDA" not in _names and "CPU" not in _names:
        import glob
        pref = os.environ.get("CONDA_PREFIX") or os.environ.get("OPENMM_PREFIX") or ""
        cands = [os.path.join(pref, "lib", "plugins")] if pref else []
        try:
            cands.append(mm.Platform.getDefaultPluginsDirectory())
        except Exception:  # noqa: BLE001
            pass
        cands += glob.glob("/opt/mamba/envs/*/lib/plugins") + (glob.glob(os.path.join(pref, "lib*", "plugins")) if pref else [])
        loaded = []
        for d in cands:
            if d and os.path.isdir(d):
                try:
                    mm.Platform.loadPluginsFromDirectory(d); loaded.append(d)
                except Exception as e:  # noqa: BLE001
                    print(f"[bench] plugin load {d} failed: {e}", flush=True)
        print(f"[bench] plugins didn't auto-load; reloaded from {loaded}", flush=True)

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
    sim.minimizeEnergy(maxIterations=minimize_iters)
    sim.context.setVelocitiesToTemperature(300 * u.kelvin)

    sim.step(warmup)                      # exclude JIT + equilibration transient

    # TIME-TARGETED AND REPLICATED, NOT A SINGLE SHORT SHOT. A fixed BENCH_STEPS produced production windows of
    # 0.9-4.5 s (2026-07-24), which cannot rank cards: an RTX 4080 SUPER "beat" a 4090 by 4% over a 2.0 s vs
    # 2.1 s measurement, when its 736 GB/s vs 1008 GB/s bandwidth says the 4090 should lead a PME-bound run by
    # ~35%. At that duration you measure boost-clock ramp, kernel-launch overhead and residual JIT, not
    # steady-state throughput.
    #
    # So the bench must carry its OWN evidence that the number is trustworthy, rather than being asserted to be:
    #   * probe first, then size each timed block to real work (BENCH_TARGET_S total, default 60 s);
    #   * run BENCH_BLOCKS independent timed blocks and report EVERY block plus their spread. A throttled,
    #     shared or contended host shows up as block-to-block scatter, which a single window hides completely;
    #   * report the coefficient of variation so a caller can reject an unstable measurement instead of
    #     averaging it into a ranking;
    #   * check the physics: a run that has blown up returns a fast, meaningless ns/day.
    target_s = float(os.environ.get("BENCH_TARGET_S", "60"))
    blocks = max(1, int(os.environ.get("BENCH_BLOCKS", "3")))
    probe = max(200, steps // 10)
    t0 = time.time()
    sim.step(probe)
    sim.context.getState(getEnergy=True)
    probe_s = max(1e-6, time.time() - t0)
    per_block = max(steps, int(probe * (target_s / blocks) / probe_s))

    block_ns_day, wall_s, total_steps = [], 0.0, 0
    for b in range(blocks):
        t0 = time.time()
        sim.step(per_block)
        sim.context.getState(getEnergy=True)   # force sync so timing includes the last kernel
        dt = max(1e-9, time.time() - t0)
        wall_s += dt
        total_steps += per_block
        block_ns_day.append((per_block * dt_fs * 1e-6) / (dt / 86400.0))
        print(f"[bench] block {b + 1}/{blocks}: {per_block} steps in {dt:.1f}s "
              f"-> {block_ns_day[-1]:.2f} ns/day", flush=True)

    ns_per_day, sd, cv = block_stats(block_ns_day)

    # PHYSICS SANITY. See health_check: a blown-up system is fast and meaningless.
    st = sim.context.getState(getEnergy=True)
    pe = st.getPotentialEnergy().value_in_unit(u.kilojoule_per_mole)
    ke = st.getKineticEnergy().value_in_unit(u.kilojoule_per_mole)
    temp_k, healthy = health_check(pe, ke, n_atoms, system.getNumConstraints())
    print(f"[bench] mean {ns_per_day:.2f} ns/day  sd {sd:.2f}  cv {cv * 100:.1f}%  "
          f"final_T {temp_k:.1f}K  PE {pe:.3e} kJ/mol  healthy={healthy}", flush=True)

    dev = ""
    try:
        dev = (props and platform.getPropertyValue(sim.context, "DeviceName")) or ""
    except Exception:  # noqa: BLE001
        pass
    return dict(atoms=n_atoms, platform=plat_name, device=dev, wall_s=wall_s,
                ns_per_day=ns_per_day, steps=total_steps, blocks=blocks,
                block_ns_day=block_ns_day, sd=sd, cv=cv, temp_k=temp_k, pe=pe, healthy=healthy,
                minimize_iters=minimize_iters)


# ★★ THE NaN RETRY LADDER, AND WHY IT DOES NOT CHANGE THE MEASURED QUANTITY (2026-07-27).
#
# OBSERVED: 5 of ~21 calibration rentals died with `OpenMMException: Particle coordinate is NaN` during
# minimise/warmup, producing no measurement at all — one of them the RTX 5090, the single highest-value
# unbenched card on the board. Each failure costs a whole rental.
#
# ROOT CAUSE, with the observation that DISCRIMINATES rather than a story: machine 117850 NaN'd on one run and
# succeeded on the next, same code, same image, same card. So the failure is STOCHASTIC, not host-specific and
# not card-specific. The stochastic input is `setVelocitiesToTemperature`, which is unseeded — a fresh velocity
# draw each run — landing on a box that has had only 200 minimisation iterations after `addSolvent` and is then
# integrated at 4 fs with HMR. Occasionally a residual clash survives and blows up.
#
# WHY THE FIX IS A RETRY LADDER AND NOT SIMPLY "MINIMISE HARDER":
#   * The first attempt is BYTE-FOR-BYTE the protocol the anchors were measured on. A run that succeeds is
#     therefore unchanged — the protocol only differs where it previously produced NOTHING.
#   * Minimisation is a PREPARATION step. Steady-state ns/day is set by particle count, cutoff, PME grid and
#     integrator, none of which it touches; the timed blocks begin after a further 1000 warmup steps and a
#     probe. A better-minimised box integrates at exactly the same rate.
#   * That neutrality is checkable rather than asserted: `minimize_iters` and `attempt` travel on the result
#     line, so any number produced after a retry is visible and can be compared against the same card's
#     first-attempt cluster.
_MINIMIZE_LADDER = (200, 2000, 20000)


def main():
    edge_nm = float(os.environ.get("BENCH_EDGE_NM", "7.1"))   # ~36k atoms; representative of a complex leg
    steps = int(os.environ.get("BENCH_STEPS", "4000"))
    warmup = int(os.environ.get("BENCH_WARMUP", "1000"))
    dt_fs = float(os.environ.get("BENCH_DT_FS", "4.0"))
    tag = os.environ.get("BENCH_TAG", "bench")
    ladder = _MINIMIZE_LADDER[:max(1, int(os.environ.get("BENCH_MAX_ATTEMPTS", str(len(_MINIMIZE_LADDER)))))]
    r, last, attempt = None, None, 0
    for attempt, mi in enumerate(ladder, start=1):
        try:
            r = _bench(edge_nm, steps, warmup, dt_fs, minimize_iters=mi)
            break
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"[bench] attempt {attempt}/{len(ladder)} at minimize_iters={mi} FAILED "
                  f"({type(e).__name__}: {e}); retrying with a harder minimisation" if attempt < len(ladder)
                  else f"[bench] attempt {attempt}/{len(ladder)} at minimize_iters={mi} FAILED "
                       f"({type(e).__name__}: {e}); no attempts left", flush=True)
    if r is None:
        # ⚠ SPACES MUST BE UNDERSCORED HERE TOO (2026-07-31). The result line is parsed by `line.split()`
        # then `kv.split("=", 1)`, so any value containing a space is truncated at the first one — the file
        # already records that for `device` ('Quadro RTX 8000' -> 'Quadro') and then emitted the ONE field
        # guaranteed to contain spaces without the same treatment. Measured cost: a P100 probe failed all
        # three ladder attempts at both system sizes and reported `err=OpenMMException:Error`, which names
        # the exception type and then throws away the sentence that says WHY — turning a diagnosable
        # environment failure into a 20-minute run with no cause. Newlines collapse for the same reason.
        _msg = " ".join(str(last).split())[:300].replace(" ", "_")
        print(f"BENCH_RESULT tag={tag} status=ERROR attempts={len(ladder)} "
              f"err={type(last).__name__}:{_msg}", flush=True)
        sys.exit(1)
    # Single parsable line the launcher scrapes from the serial console. The launcher parses it by
    # `line.split()` then `kv.split("=", 1)`, so ANY VALUE CONTAINING A SPACE IS SILENTLY TRUNCATED at the first
    # space — `device='Quadro RTX 8000'` arrived as `device='Quadro`, which is how a bench leg's true card went
    # unidentified (2026-07-24). Underscore the device name so it survives the split intact.
    # `healthy` and `cv` travel WITH the number so a consumer can reject it, instead of the number arriving bare
    # and its trustworthiness being asserted separately.
    print(f"BENCH_RESULT tag={tag} status={'OK' if r['healthy'] else 'SUSPECT'} atoms={r['atoms']} "
          f"platform={r['platform']} device={str(r['device']).replace(' ', '_')} "
          f"steps={r['steps']} dt_fs={dt_fs} wall_s={r['wall_s']:.1f} "
          f"ns_per_day={r['ns_per_day']:.2f} sd={r['sd']:.2f} cv={r['cv']:.4f} blocks={r['blocks']} "
          f"blocks_ns_day={','.join('%.2f' % x for x in r['block_ns_day'])} "
          f"attempt={attempt} minimize_iters={r['minimize_iters']} "
          f"final_temp_k={r['temp_k']:.1f} healthy={r['healthy']}", flush=True)


if __name__ == "__main__":
    main()
