#!/usr/bin/env python
"""Spot-safe two-phase driver for an OpenFE 1.12 HybridTopology MultiState (RBFE) leg.

Replaces OpenFE's HybridTopologyMultiStateSimulationUnit._run_simulation (which does
minimize()+equilibrate()+run() with a NON-resumable equilibration gated on _iteration==0) with:

  WARMUP  : run the equilibration as ordinary CHECKPOINTED run() iterations in a SEPARATE
            storage pair (equilibration.nc/.chk, small checkpoint interval). A spot kill in
            warmup resumes from the last committed warmup checkpoint instead of restarting.
  PRODUCTION: create() a FRESH production storage pair (simulation.nc/checkpoint.chk) from the
            final warmup sampler states + replica<->state assignments, then run to the requested
            production iterations. OpenFE's AnalysisUnit then sees a clean production trajectory.
  BARRIER : advance in checkpoint-aligned chunks; at each quiescent boundary snapshot+validate+
            commit to a versioned CommitStore (rbfe_spot_checkpoint) with the manifest LAST.
  RESTORE : on startup, restore the newest VALID committed snapshot (production first, else
            warmup) into the shared dir BEFORE opening any reporter — never trust size/mtime/yaml.

Reuses OpenFE's own builders (via the unit instance): _get_settings, _get_integrator,
_get_sampler (fresh warmup + restart), _check_restart-equivalent logic, and the platform build.
Only the run orchestration is replaced. Returns {"nc":..., "checkpoint":...} pointing at the
PRODUCTION storage, i.e. the same contract _run_simulation's caller expects.

GPU-only-testable end-to-end (needs a real hybrid system); the barrier/commit/restore + the
warmup->production transition mechanics are already CPU-validated in rbfe_spot_checkpoint_test.py.
"""
from __future__ import annotations

import os
from pathlib import Path

import rbfe_spot_checkpoint as spot

# phase constants + default filenames (production names match OpenFE output_settings so the
# AnalysisUnit reads them unchanged).
WARMUP = "warmup"
PRODUCTION = "production"
WARMUP_NC, WARMUP_CHK = "equilibration.nc", "equilibration.chk"


def _iters_from_time(sim_settings, integrator, sim_length):
    """iterations = get_simsteps(sim_length)/steps_per_iteration, mirroring OpenFE."""
    from openfe.protocols.openmm_utils import settings_validation
    from openff.units.openmm import from_openmm
    steps_per_iter = integrator.n_steps
    timestep = from_openmm(integrator.timestep)
    total_steps = settings_validation.get_simsteps(
        sim_length=sim_length, timestep=timestep, mc_steps=steps_per_iter)
    return int(total_steps / steps_per_iter)


def _build_reporter(shared, nc_name, chk_name, selection_indices, chk_interval_iters,
                    pos_interval, vel_interval):
    """Mirror OpenFE _get_reporter but with explicit filenames + checkpoint interval (iters)."""
    from openmmtools import multistate
    return multistate.MultiStateReporter(
        storage=str(Path(shared) / nc_name),
        analysis_particle_indices=selection_indices,
        checkpoint_interval=int(chk_interval_iters),
        checkpoint_storage=chk_name,
        position_interval=pos_interval,
        velocity_interval=vel_interval,
    )


def _prod_sampler_kwargs(integrator, system, positions, sim_settings, thermo_settings,
                         production_iters):
    """Reproduce _get_sampler's kwargs for a repex sampler we create() ourselves."""
    from openfe.protocols.openmm_utils import settings_validation
    rta_its, rta_min_its = settings_validation.convert_real_time_analysis_iterations(
        simulation_settings=sim_settings)
    early_err = settings_validation.convert_target_error_from_kcal_per_mole_to_kT(
        thermo_settings.temperature, sim_settings.early_termination_target_error)
    return {
        "mcmc_moves": integrator,
        "hybrid_system": system,
        "hybrid_positions": positions,
        "online_analysis_interval": rta_its,
        "online_analysis_target_error": early_err,
        "online_analysis_minimum_iterations": rta_min_its,
        "number_of_iterations": production_iters,
        "replica_mixing_scheme": "swap-all",
    }


def _set_caches(sampler, platform):
    import openmmtools
    sampler.energy_context_cache = openmmtools.cache.ContextCache(
        capacity=None, time_to_live=None, platform=platform)
    sampler.sampler_context_cache = openmmtools.cache.ContextCache(
        capacity=None, time_to_live=None, platform=platform)


def _pos_vel_intervals(output_settings, sim_settings):
    from openfe.protocols.openmm_utils import settings_validation
    pos = 0
    if output_settings.positions_write_frequency is not None:
        pos = settings_validation.divmod_time_and_check(
            numerator=output_settings.positions_write_frequency,
            denominator=sim_settings.time_per_iteration,
            numerator_name="positions_write_frequency", denominator_name="time_per_iteration")
    vel = 0
    if output_settings.velocities_write_frequency is not None:
        vel = settings_validation.divmod_time_and_check(
            numerator=output_settings.velocities_write_frequency,
            denominator=sim_settings.time_per_iteration,
            numerator_name="velocities_write_frequency", denominator_name="time_per_iteration")
    return pos, vel


def run_spot_safe(*, unit, protocol, system, positions, selection_indices, shared_basepath,
                  scratch_basepath, commit_store,
                  warmup_checkpoint_iters=10, production_checkpoint_iters=20, log=print):
    """Drive the leg spot-safely. `unit` is a HybridTopologyMultiStateSimulationUnit (used only
    for its static/instance builders); `protocol` is the OpenFE protocol (for .settings).
    `commit_store` is an rbfe_spot_checkpoint CommitStore. Builds settings/lambdas/platform via
    OpenFE's own module globals (no guessed import paths). Returns {"nc","checkpoint"} for the
    production pair."""
    import sys
    from openmmtools.multistate import MultiStateReporter
    # _rfe_utils + omm_compute are globals of the module where the unit CLASS (and its run()) live —
    # that's the exact namespace OpenFE's run() resolves; resolve it from the instance, don't guess.
    umod = sys.modules[type(unit).__module__]

    shared = Path(shared_basepath)
    shared.mkdir(parents=True, exist_ok=True)
    unit._prepare(True, scratch_basepath, shared)
    settings = unit._get_settings(protocol.settings)
    sim_s = settings["simulation_settings"]
    out_s = settings["output_settings"]
    integ_s = settings["integrator_settings"]
    thermo_s = settings["thermo_settings"]
    alchem_s = settings["alchemical_settings"]

    # lambda schedule + compute platform, exactly as OpenFE's run() builds them (reuse its globals)
    lambdas = umod._rfe_utils.lambdaprotocol.LambdaProtocol(
        functions=settings["lambda_settings"].lambda_functions,
        windows=settings["lambda_settings"].lambda_windows)
    restrict_cpu = settings["forcefield_settings"].nonbonded_method.lower() == "nocutoff"
    platform = umod.omm_compute.get_openmm_platform(
        platform_name=settings["engine_settings"].compute_platform,
        gpu_device_index=settings["engine_settings"].gpu_device_index,
        restrict_cpu_count=restrict_cpu)

    integrator = unit._get_integrator(integrator_settings=integ_s, simulation_settings=sim_s,
                                      system=system)
    # iteration targets from settings; env overrides (RBFE_WARMUP_ITERS/RBFE_PROD_ITERS) let a
    # GPU SMOKE run a handful of iters to validate the machinery without the full ~15 h science.
    warmup_iters = int(os.environ.get("RBFE_WARMUP_ITERS", "0")) or \
        _iters_from_time(sim_s, integrator, sim_s.equilibration_length)
    prod_iters = int(os.environ.get("RBFE_PROD_ITERS", "0")) or \
        _iters_from_time(sim_s, integrator, sim_s.production_length)
    # round targets down to a checkpoint multiple so run_to_target lands exactly on a boundary.
    warmup_target = (warmup_iters // warmup_checkpoint_iters) * warmup_checkpoint_iters or \
        warmup_checkpoint_iters
    prod_target = (prod_iters // production_checkpoint_iters) * production_checkpoint_iters or \
        production_checkpoint_iters
    # optional forced-crash after N committed boundaries (GPU smoke restore test); hard-exit so
    # nothing flushes — the next dispatch must recover purely from the committed snapshot.
    kill_after = int(os.environ.get("RBFE_SPOT_KILL_AFTER", "0"))
    _commits = [0]
    pos_iv, vel_iv = _pos_vel_intervals(out_s, sim_s)
    prod_nc, prod_chk = out_s.output_filename, out_s.checkpoint_storage_filename
    log(f"[spot-driver] warmup_target={warmup_target} (ci={warmup_checkpoint_iters}) "
        f"prod_target={prod_target} (ci={production_checkpoint_iters})")

    # ---- RESTORE newest valid committed snapshot (production first, else warmup) ------------
    restored = commit_store.restore_latest([PRODUCTION, WARMUP], shared, production_checkpoint_iters)
    if restored is None:
        # try a warmup-only restore with the warmup checkpoint interval (validate uses its CI)
        restored = commit_store.restore_latest([WARMUP], shared, warmup_checkpoint_iters)
    restored_phase = restored[0] if restored else None
    log(f"[spot-driver] restore -> {('%s@iter %d' % (restored[0], restored[1])) if restored else 'none (fresh)'}")

    def _commit(phase, nc_name, chk_name, ci):
        def _cb(it):
            commit_store.commit(phase, it, shared / nc_name, shared / chk_name, ci)
            _commits[0] += 1
            if kill_after and _commits[0] >= kill_after:
                log(f"[spot-driver] RBFE_SPOT_KILL_AFTER={kill_after} reached "
                    f"({phase}@iter {it}) -> hard exit to simulate a spot kill")
                os._exit(137)
        return _cb

    # ================= PRODUCTION already underway: resume it and finish ======================
    if restored_phase == PRODUCTION:
        rep = MultiStateReporter(str(shared / prod_nc), open_mode="r+", checkpoint_storage=prod_chk)
        sampler = unit._get_sampler(system=system, positions=positions, lambdas=lambdas,
                                    integrator=integrator, reporter=rep, simulation_settings=sim_s,
                                    thermo_settings=thermo_s, alchem_settings=alchem_s,
                                    platform=platform, restart=True, dry=False)
        _set_caches(sampler, platform)
        log(f"[spot-driver] resume PRODUCTION at iter {spot._sampler_iteration(sampler)}")
        spot.run_to_target(sampler, rep, prod_target, production_checkpoint_iters,
                           _commit(PRODUCTION, prod_nc, prod_chk, production_checkpoint_iters), log=log)
        return {"nc": shared / prod_nc, "checkpoint": shared / prod_chk}

    # ================= WARMUP (fresh, or resume a partial warmup) =============================
    wrep = _build_reporter(shared, WARMUP_NC, WARMUP_CHK, selection_indices,
                           warmup_checkpoint_iters, pos_iv, vel_iv)
    warmup_restart = restored_phase == WARMUP and (shared / WARMUP_NC).is_file()
    warmup = unit._get_sampler(system=system, positions=positions, lambdas=lambdas,
                               integrator=integrator, reporter=wrep, simulation_settings=sim_s,
                               thermo_settings=thermo_s, alchem_settings=alchem_s,
                               platform=platform, restart=warmup_restart, dry=False)
    _set_caches(warmup, platform)
    if not warmup_restart and spot._sampler_iteration(warmup) == 0:
        # the big minimization (setup() already did a tiny 100-step one); still fast/non-resumable.
        log("[spot-driver] warmup minimize")
        warmup.minimize(max_iterations=sim_s.minimization_steps)
    log(f"[spot-driver] WARMUP from iter {spot._sampler_iteration(warmup)} -> {warmup_target}")
    spot.run_to_target(warmup, wrep, warmup_target, warmup_checkpoint_iters,
                       _commit(WARMUP, WARMUP_NC, WARMUP_CHK, warmup_checkpoint_iters), log=log)

    # snapshot final warmup state for the transition, then release the warmup sampler
    import copy
    import numpy as np
    final = {
        "thermodynamic_states": copy.deepcopy(warmup._thermodynamic_states),
        "sampler_states": copy.deepcopy(warmup._sampler_states),
        "replica_state_indices": np.asarray(warmup._replica_thermodynamic_states, dtype=int),
        "unsampled": copy.deepcopy(getattr(warmup, "_unsampled_states", []) or []),
        "metadata": copy.deepcopy(getattr(warmup, "_metadata", {}) or {}),
    }
    wrep.close()
    del warmup

    # ================= PRODUCTION create() from the warmup state ==============================
    from openfe.protocols.openmm_rfe._rfe_utils.multistate import HybridRepexSampler
    prep = _build_reporter(shared, prod_nc, prod_chk, selection_indices,
                           production_checkpoint_iters, pos_iv, vel_iv)
    kwargs = _prod_sampler_kwargs(integrator, system, positions, sim_s, thermo_s, prod_iters)
    prod = HybridRepexSampler(**kwargs)
    prod.create(
        thermodynamic_states=final["thermodynamic_states"],
        sampler_states=final["sampler_states"],
        storage=prep,
        initial_thermodynamic_states=final["replica_state_indices"],
        unsampled_thermodynamic_states=final["unsampled"] or None,
        metadata=final["metadata"] or None,
    )
    _set_caches(prod, platform)
    log(f"[spot-driver] PRODUCTION created from warmup; run -> {prod_target}")
    spot.run_to_target(prod, prep, prod_target, production_checkpoint_iters,
                       _commit(PRODUCTION, prod_nc, prod_chk, production_checkpoint_iters), log=log)
    return {"nc": shared / prod_nc, "checkpoint": shared / prod_chk}
