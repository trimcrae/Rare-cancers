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
import time
from pathlib import Path

import rbfe_spot_checkpoint as spot

# phase constants + default filenames (production names match OpenFE output_settings so the
# AnalysisUnit reads them unchanged).
WARMUP = "warmup"
PRODUCTION = "production"
WARMUP_NC, WARMUP_CHK = "equilibration.nc", "equilibration.chk"


class _ConvergedEarly(Exception):
    """Raised from a production checkpoint boundary when the committed trajectory has met the convergence
    criteria (RBFE_AUTOSTOP_CONVERGENCE=1) — caught by the driver to end production early and save GPU."""

    def __init__(self, iteration):
        self.iteration = iteration
        super().__init__("production converged early at iter %d" % iteration)


def _autostop_enabled():
    return os.environ.get("RBFE_AUTOSTOP_CONVERGENCE") == "1"


def _live_converged(reporter, iteration, prod_target, ci, log):
    """Convergence subset for an early-STOP decision (opt-in, RBFE_AUTOSTOP_CONVERGENCE=1): from the LIVE
    (quiescent, just-synced) production reporter, require a CONNECTED MBAR overlap matrix (no adjacent-state
    bottleneck) AND a plateaued dG(t) (|full − final-half| ≤ 0.5 AND |Q3 − Q4| ≤ 0.5) — the reviewer's
    condition-4 convergence signals. Conservative: only checked after a minimum fraction of the production cap,
    and ANY un-computable metric or error ⇒ NOT converged (keep sampling). Never stops before real evidence, so
    the worst case is running the full 5 ns cap (identical to autostop-off)."""
    try:
        min_frac = float(os.environ.get("RBFE_AUTOSTOP_MIN_FRAC", "0.4"))
    except ValueError:
        min_frac = 0.4
    if iteration < max(2 * ci, int(prod_target * min_frac)):
        return False
    try:
        import ternary_fep_convergence as cv
        from openmmtools.multistate import MultiStateSamplerAnalyzer
        analyzer = MultiStateSamplerAnalyzer(reporter)
        ov = cv._overlap(analyzer)
        if not ov.get("connected"):
            log("[autostop] iter %d: overlap NOT connected (min_adj=%s) -> keep sampling"
                % (iteration, ov.get("min_adjacent_overlap")))
            return False
        bp = cv._block_plateau(analyzer)
        ok = bool(bp.get("plateau_full_vs_half_ok") and bp.get("quarter_block_ok"))
        log("[autostop] iter %d: overlap_connected=%s plateau_full_half=%s q3q4=%s -> %s"
            % (iteration, ov.get("connected"), bp.get("plateau_full_vs_half_ok"),
               bp.get("quarter_block_ok"), "CONVERGED" if ok else "keep sampling"))
        return ok
    except Exception as e:  # noqa: BLE001
        log("[autostop] convergence check failed @ %d (%s: %s); continue sampling"
            % (iteration, type(e).__name__, e))
        return False


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


# --------------------------------------------------------------------------------------------
# NaN / clash diagnostics — a state-1 SimulationNaNError that survives 25k minimization steps is
# almost always a coincident-atom clash the minimizer can't escape (degenerate gradient), i.e. a
# bad *starting structure* rather than a compute problem. These helpers name the offending atoms
# in the (uploaded) run log so the fix targets the real defect instead of guessing.
# --------------------------------------------------------------------------------------------
def _bonded_pairs(system):
    """Atom pairs joined by a bond or constraint — excluded from the clash search (bonds are
    legitimately ~1.0–1.5 A; H–X constraints ~1.0 A)."""
    import openmm
    pairs = set()
    for f in system.getForces():
        if isinstance(f, openmm.HarmonicBondForce):
            for k in range(f.getNumBonds()):
                p = f.getBondParameters(k)
                i, j = int(p[0]), int(p[1])
                pairs.add((min(i, j), max(i, j)))
    for k in range(system.getNumConstraints()):
        i, j, _ = system.getConstraintParameters(k)
        pairs.add((min(int(i), int(j)), max(int(i), int(j))))
    return pairs


def _nonbonded_exceptions(system):
    """Map atom pair -> (chargeProd_e2, epsilon_kJ/mol) for every NonbondedForce exception.

    In an OpenFE hybrid topology the *old* and *new* copies of a mapped atom sit ~0.4 A apart but
    are given a zeroed exception (chargeProd=0, epsilon=0) so they never see each other — that pair
    is a HARMLESS artifact of the alchemical construction, NOT a real clash. A close pair that is
    absent from the exceptions (or present with non-zero epsilon/chargeProd) IS force-bearing and a
    genuine bad contact. This lets the clash report tell the two apart definitively."""
    import openmm
    exc = {}
    for f in system.getForces():
        if isinstance(f, openmm.NonbondedForce):
            for k in range(f.getNumExceptions()):
                p = f.getExceptionParameters(k)
                i, j = int(p[0]), int(p[1])
                cp = p[2].value_in_unit(openmm.unit.elementary_charge ** 2)
                eps = p[4].value_in_unit(openmm.unit.kilojoule_per_mole)
                exc[(min(i, j), max(i, j))] = (float(cp), float(eps))
    return exc


def _clash_report(positions, system, log, tag, thresh_nm=0.09):
    """Log the closest NON-bonded atom pairs + any blown-up coordinates. Non-fatal.

    For each flagged close pair we also report whether it is a zeroed NonbondedForce exception (an
    excluded hybrid old/new pair = red herring) or a force-bearing contact (a real clash)."""
    try:
        import numpy as np
        from openmm import unit as ommunit
        if hasattr(positions, "value_in_unit"):
            xyz = np.asarray(positions.value_in_unit(ommunit.nanometer), dtype=float)
        else:
            xyz = np.asarray(positions, dtype=float)
        xyz = xyz.reshape(-1, 3)
        n = xyz.shape[0]
        finite_mask = np.isfinite(xyz).all(axis=1)
        nonfinite = int((~finite_mask).sum())
        big = int((np.abs(xyz) > 1e3).any(axis=1).sum())
        log(f"[clash-diag:{tag}] atoms={n} nonfinite_atoms={nonfinite} coords>1000nm_atoms={big}")
        if finite_mask.sum() < 2:
            return
        try:
            from scipy.spatial import cKDTree
        except Exception as e:                       # pragma: no cover
            log(f"[clash-diag:{tag}] scipy unavailable ({e}); skipping KDTree")
            return
        idx = np.where(finite_mask)[0]
        tree = cKDTree(xyz[idx])
        d, nn = tree.query(xyz[idx], k=2)            # col 0 is self
        bonded = _bonded_pairs(system)
        seen, cand = set(), []
        for a_local in range(len(idx)):
            ga, gb = int(idx[a_local]), int(idx[nn[a_local, 1]])
            key = (min(ga, gb), max(ga, gb))
            if key in bonded or key in seen:
                continue
            seen.add(key)
            cand.append((float(d[a_local, 1]), ga, gb))
        cand.sort()
        try:
            exc = _nonbonded_exceptions(system)
        except Exception as e:                        # pragma: no cover
            log(f"[clash-diag:{tag}] could not read NB exceptions ({e})")
            exc = {}
        # A real clash = a close pair that is NOT a zeroed exception. Count only those.
        def _forcebearing(ga, gb):
            key = (min(ga, gb), max(ga, gb))
            if key not in exc:
                return True                            # sees full nonbonded -> real contact
            cp, eps = exc[key]
            return abs(cp) > 1e-6 or abs(eps) > 1e-6   # non-zero exception -> still force-bearing
        nclash = sum(1 for dd, ga, gb in cand if dd < thresh_nm and _forcebearing(ga, gb))
        nexcl = sum(1 for dd, ga, gb in cand if dd < thresh_nm and not _forcebearing(ga, gb))
        if cand:
            log(f"[clash-diag:{tag}] non-bonded pairs < {thresh_nm*10:.2f} A: "
                f"{nclash} force-bearing (REAL) + {nexcl} zeroed-exception (hybrid A/B, benign); "
                f"closest non-bonded = {cand[0][0]*10:.3f} A")
        else:
            log(f"[clash-diag:{tag}] no non-bonded pairs found")
        for dist, ga, gb in cand[:8]:
            key = (min(ga, gb), max(ga, gb))
            if key in exc:
                cp, eps = exc[key]
                kind = ("EXCLUDED-hybrid(benign)" if abs(cp) <= 1e-6 and abs(eps) <= 1e-6
                        else f"exception(cp={cp:.3g} eps={eps:.3g})")
            else:
                kind = "FORCE-BEARING(real clash)"
            log(f"[clash-diag:{tag}]   non-bonded pair ({ga},{gb}) d={dist*10:.3f} A  [{kind}]")
    except Exception as e:                           # pragma: no cover
        log(f"[clash-diag:{tag}] failed: {type(e).__name__}: {e}")


def _diagnose_nan_dir(shared, system, log):
    """openmmtools saved the pre-error State to a nan-error-logs dir; load it and clash-report so
    the post-mortem names the offending atoms."""
    import glob
    import openmm
    from pathlib import Path
    hits = sorted(glob.glob(str(Path(shared) / "**" / "nan-error-logs" / "*"), recursive=True))
    log(f"[nan-diag] nan-error-logs artifacts ({len(hits)}): {[Path(h).name for h in hits]}")
    for f in hits:
        if not f.endswith(".xml"):
            continue
        try:
            obj = openmm.XmlSerializer.deserialize(open(f).read())
        except Exception as e:
            log(f"[nan-diag] {Path(f).name}: not deserializable ({e})")
            continue
        if hasattr(obj, "getPositions"):
            try:
                pos = obj.getPositions(asNumpy=True)
                log(f"[nan-diag] analyzing saved State from {Path(f).name}")
                _clash_report(pos, system, log, "nan_state")
            except Exception as e:
                log(f"[nan-diag] {Path(f).name}: no positions ({e})")


def _flushing_log(*args, **kwargs):
    """`print` with flush=True, and the default for this module's `log` for a measured reason.

    THE BUG THIS FIXES (2026-07-26). The default was bare `print`. On the VM the driver runs as
    `( ... python nr4a3_ternary_fep.py ) | tee /tmp/tfep_run.log`, and Python's stdout is BLOCK-buffered when it
    is a pipe rather than a tty — while openmmtools' per-iteration progress goes through the `logging` module,
    whose StreamHandler flushes every record. Two differently-buffered writers into one pipe, so the driver's own
    lines land in the log THOUSANDS of iterations late while openmmtools' lines are current.

    MEASURED, on the live rev leg (gcp-ternary-30177970643, GH run 30202433547): GCS held warmup complete at
    800/800 and production at 320/2000, and the log held 938 timing lines — consistent with the ~920 iterations
    that implies — yet the newest [barrier] line said `iteration 640/800` and there was NO
    "PRODUCTION created from warmup" line at all. The production phase had been running for 320 iterations and
    the log did not say so.

    WHY IT MATTERS BEYOND TIDINESS: every phase/lifecycle statement in that log is on the lagging stream, so
    anything that reads it to decide WHICH PHASE a leg is in gets a stale answer that looks current. It made the
    iteration-timing profile split its output at iteration 448 and label it "pre-warmup vs warmup" — a boundary
    that was purely the buffer lag, with the real phase change invisible. A diagnostic reporting a confident
    phase attribution from unflushed output is the same defect class as the direction-blind keys in
    ternary-lane-guard-audit-2026-07-25.md: a reading that ignores a dimension the data varies along.
    """
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)


def run_spot_safe(*, unit, protocol, system, positions, selection_indices, shared_basepath,
                  scratch_basepath, commit_store,
                  warmup_checkpoint_iters=10, production_checkpoint_iters=20, log=_flushing_log):
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
    # REDUCED-TIMESTEP WARMUP (2026-07-19). A large, rough (homology-built) ternary assembly can NaN during the
    # alchemical WARMUP at the production dt (e.g. 4 fs) — a softcore-state integration blow-up on the rough start —
    # while PRODUCTION at that dt from a CLEAN equilibrated structure is fine. Equilibration is DISCARDED (it never
    # enters the MBAR free-energy estimate), so we may run WARMUP at a smaller dt and hand the equilibrated
    # sampler states to a full-dt production. RBFE_WARMUP_TIMESTEP_FS sets the warmup dt (unset -> same as
    # production). This is the standard "equilibrate small-dt, produce large-dt" trick and does NOT affect ΔG.
    warmup_integrator = integrator
    _wdt = os.environ.get("RBFE_WARMUP_TIMESTEP_FS")
    if _wdt:
        try:
            import openmm as _mm_w
            # `unit._get_integrator` returns an openmmtools MCMC MOVE (LangevinDynamicsMove), NOT a raw OpenMM
            # Integrator (so no setStepSize) and NOT a frozen OpenFE Settings (so integ_s mutation is out). The move
            # stores its own `.timestep` attribute — the SAME one `_iters_from_time` reads via `integrator.timestep`,
            # so it provably exists and is settable, and the move rebuilds its integrator with it when applied. Build
            # a SEPARATE move for warmup and set its timestep; production keeps its own move at the protocol dt.
            warmup_integrator = unit._get_integrator(integrator_settings=integ_s, simulation_settings=sim_s,
                                                     system=system)
            warmup_integrator.timestep = float(_wdt) * _mm_w.unit.femtoseconds
            log(f"[spot-driver] WARMUP timestep overridden to {_wdt} fs "
                f"(move.timestep now {warmup_integrator.timestep}); production dt unchanged; "
                f"equilibration is discarded so this does NOT affect ΔG")
        except Exception as _we:  # noqa: BLE001
            warmup_integrator = integrator
            log(f"[spot-driver] WARN could not build reduced-dt warmup integrator ({_we}); warmup uses production dt")
    # STRUCTURE-SANITY (always-on, ~free): a coincident-atom clash in the *starting* structure is
    # the classic cause of a state-1 warmup NaN that survives minimization. Log it before any MD.
    _clash_report(positions, system, log, "initial")
    # iteration targets from settings; env overrides (RBFE_WARMUP_ITERS/RBFE_PROD_ITERS) let a
    # GPU SMOKE run a handful of iters to validate the machinery without the full ~15 h science.
    # warmup_iters uses the WARMUP integrator's dt so it covers the intended equilibration_length (more iters at a
    # smaller dt); prod_iters uses the production integrator.
    warmup_iters = int(os.environ.get("RBFE_WARMUP_ITERS") or "0") or \
        _iters_from_time(sim_s, warmup_integrator, sim_s.equilibration_length)
    prod_iters = int(os.environ.get("RBFE_PROD_ITERS") or "0") or \
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
    # MAKE TRAJECTORY PERSISTENCE OBSERVABLE. pos_iv is the write stride in ITERATIONS, derived from
    # positions_write_frequency; 0 means NO coordinates are stored over time and the committed .nc cannot be
    # re-analysed for anything geometric. That is not a hypothetical loss — the NR-V04 covalent panel's census
    # found zero trajectory objects across 19 units, which made three known analysis defects permanently
    # uncorrectable. Logging it here means the answer is in every run log rather than inferred later from a
    # file size.
    log(f"[spot-driver] trajectory persistence: positions every {pos_iv} iteration(s), velocities every "
        f"{vel_iv} — output_indices={getattr(out_s, 'output_indices', '?')!r}"
        + ("  ** NO POSITIONS WILL BE STORED — this leg will not be re-analysable **" if not pos_iv else ""))
    prod_nc, prod_chk = out_s.output_filename, out_s.checkpoint_storage_filename
    log(f"[spot-driver] warmup_target={warmup_target} (ci={warmup_checkpoint_iters}) "
        f"prod_target={prod_target} (ci={production_checkpoint_iters})")

    # ---- RESTORE newest valid committed snapshot (production first, else warmup) ------------
    # Validate EACH phase with ITS OWN checkpoint interval. Production snapshots commit every
    # production_checkpoint_iters; warmup every (finer) warmup_checkpoint_iters. A single combined
    # restore_latest([PRODUCTION, WARMUP], ..., production_checkpoint_iters) wrongly validates WARMUP
    # snapshots against the PRODUCTION interval, so any warmup checkpoint that is not a multiple of
    # the production interval (e.g. warmup iter 48/56 vs prod interval 40) is REJECTED — discarding
    # the newest warmup progress and forcing a resume from a staler warmup boundary (iter 40). On a
    # long, preemption-heavy warmup that redoes up to (prod_ci - warmup_ci) extra iters every spot
    # kill. Split the call so warmup is validated at warmup_checkpoint_iters and the newest warmup
    # snapshot is accepted. Semantics preserved: production first (resume production if any), else
    # warmup. The committed .nc/.chk data is unchanged — only which snapshot restore accepts widens.
    restored = commit_store.restore_latest([PRODUCTION], shared, production_checkpoint_iters)
    if restored is None:
        restored = commit_store.restore_latest([WARMUP], shared, warmup_checkpoint_iters)
    restored_phase = restored[0] if restored else None
    log(f"[spot-driver] restore -> {('%s@iter %d' % (restored[0], restored[1])) if restored else 'none (fresh)'}")

    # ★ A FAILED COMMIT STILL KILLS THIS DRIVER — DELIBERATELY. It just no longer does it SILENTLY.
    #
    # This callback had no try/except at all, and on 2026-07-27 that was the proximate cause of two 5a-KS
    # legs billing for ~53 min while producing nothing: an exposed key was rotated, the boto3 client (built
    # once at process start and never re-reading the environment) kept the dead credential, and the first
    # commit after 7:27 AM ET raised and killed the driver mid-leg.
    #
    # THE CASE FOR CATCHING AND CONTINUING WAS CONSIDERED AND REJECTED. A leg that keeps sampling after its
    # commits stop is computing into a void: nothing is durable, a preemption or the end of the rental
    # discards every iteration since the last good commit, and the loudest possible symptom — the process
    # dying — is replaced by a green-looking run that produces no result. Swallowing here would convert a
    # 53-minute loss into a 15-hour one. Crashing on a failed commit is right.
    #
    # WHAT WAS ACTUALLY WRONG WAS THAT THE CRASH WAS INVISIBLE, and the fix is aimed at exactly that:
    #   1. RETRY FIRST, so a transient blip cannot end a 15 h leg. boto3 retries 5xx/throttling internally
    #      but does NOT retry a credential rejection, and the two are indistinguishable from here — so a
    #      short bounded retry costs ~15 s in the permanent case and saves the whole leg in the transient
    #      one. `engineering is free; only GPU dollars are a cost`.
    #   2. NAME THE RESUME POINT IN THE DEATH MESSAGE. The durable state is intact up to the last committed
    #      boundary, and that boundary is the only thing a relaunch needs. On 2026-07-27 it had to be
    #      reconstructed from an S3 listing after the fact; it should be the last line the driver prints.
    #   3. RECORD IT OFF THE CHANNEL THAT JUST FAILED. `status.json` is itself an object in the store that
    #      just refused a write, so it cannot be the record — which is why `fail()` could not report this
    #      either. The channels that survive are the local log (`/tmp/run.log`, tee'd, and archived to
    #      `attempts/` by the next container start if the store ever comes back), a local breadcrumb, and —
    #      the one that needs nothing from the host at all — the host going QUIET, which is precisely the
    #      WEDGED signal `vast_idle_guard` reaps on from CI. The independent record is the CI destroy line.
    _COMMIT_RETRIES = int(os.environ.get("RBFE_COMMIT_RETRIES") or "3")
    # The last boundary the store ACCEPTED. Seeded from the RESTORED snapshot so the resume point is
    # correct even when the very first commit of this attempt is the one that fails — which is exactly
    # the 2026-07-27 shape (the host resumed fine, then lost the credential before its next boundary).
    _last_ok = [restored[0] if restored else None, restored[1] if restored else 0]

    def _commit(phase, nc_name, chk_name, ci):
        def _cb(it):
            for attempt in range(1, _COMMIT_RETRIES + 1):
                try:
                    commit_store.commit(phase, it, shared / nc_name, shared / chk_name, ci)
                    break
                except Exception as e:  # noqa: BLE001 — re-raised below; this exists to make it legible
                    last = f"{type(e).__name__}: {e}"
                    log(f"[spot-driver] COMMIT FAILED ({phase}@iter {it}) attempt {attempt}/"
                        f"{_COMMIT_RETRIES}: {last}")
                    if attempt == _COMMIT_RETRIES:
                        resume = (f"{_last_ok[0]}@{_last_ok[1]}" if _last_ok[0]
                                  else (f"{restored[0]}@{restored[1]}" if restored else "nothing committed"))
                        msg = (f"[spot-driver] ABORT: the commit store rejected {_COMMIT_RETRIES} writes of "
                               f"{phase}@iter {it} ({last}). Durable state is INTACT up to {resume} — that "
                               f"is the resume point. Every iteration after it is lost, so continuing "
                               f"without a durable store would only make the loss bigger. This host cannot "
                               f"record the failure in the store that just refused it; the CI idle guard "
                               f"will see the log go silent and destroy the instance.")
                        log(msg)
                        try:
                            with open("/tmp/commit-failure.txt", "w") as fh:
                                fh.write(msg + "\n")
                        except Exception:  # noqa: BLE001 — a breadcrumb must never mask the real error
                            pass
                        raise
                    time.sleep(2 ** attempt)
            _last_ok[0], _last_ok[1] = phase, it
            _commits[0] += 1
            if kill_after and _commits[0] >= kill_after:
                log(f"[spot-driver] RBFE_SPOT_KILL_AFTER={kill_after} reached "
                    f"({phase}@iter {it}) -> hard exit to simulate a spot kill")
                os._exit(137)
        return _cb

    def _prod_commit(reporter, nc_name, chk_name, ci):
        """Production boundary callback: commit as usual, then (if RBFE_AUTOSTOP_CONVERGENCE=1) check the live
        trajectory for convergence and raise _ConvergedEarly to stop before the 5 ns cap. The reporter is
        quiescent + synced here, so building an analyzer on it is safe."""
        base = _commit(PRODUCTION, nc_name, chk_name, ci)

        def _cb(it):
            base(it)
            if _autostop_enabled() and _live_converged(reporter, it, prod_target, ci, log):
                raise _ConvergedEarly(it)
        return _cb

    # ================= PRODUCTION already underway: resume it and finish ======================
    if restored_phase == PRODUCTION:
        # SINGLE-INTERVAL INVARIANT (2026-07-21 root-cause fix). The .chk holds full checkpoint frames
        # ONLY on the interval baked into the .nc when it was CREATED (by whichever VM first ran
        # production). Driving run_to_target/commit off `production_checkpoint_iters` (the env value,
        # which can differ across VMs — RBFE_PROD_CKPT_ITERS unset on a VM => default 20 while the file
        # was made at 40) stops on off-grid boundaries where the .chk lags the .nc, and
        # validate_reporter_pair raises `resume iteration N-int != expected N`, permanently blocking
        # re-dispatch. Derive the ONE true interval from the committed file and use it for the resume
        # reporter, run_to_target AND commit; the file wins for an existing production, the env only
        # seeds a FRESH one.
        _file_pci = spot.read_checkpoint_interval(shared / prod_nc, shared / prod_chk)
        eff_pci = _file_pci or production_checkpoint_iters
        if _file_pci and _file_pci != production_checkpoint_iters:
            log(f"[spot-driver] RESUME production: committed-file checkpoint_interval={_file_pci} OVERRIDES "
                f"env production_checkpoint_iters={production_checkpoint_iters} (single-interval invariant)")
        elif not _file_pci:
            log(f"[spot-driver] RESUME production: could NOT read file checkpoint_interval; "
                f"falling back to env {production_checkpoint_iters} (reporter inherits file's own)")
        eff_prod_target = (prod_iters // eff_pci) * eff_pci or eff_pci
        # Pass checkpoint_interval EXPLICITLY only when we read it FROM the file (so it provably matches the
        # baked value and the reporter never silently inherits). If it couldn't be read, omit it and let
        # openmmtools inherit the file's own — passing a possibly-wrong env value would make openmmtools
        # raise a checkpoint-interval mismatch on an existing store.
        _rep_kw = {"checkpoint_interval": _file_pci} if _file_pci else {}
        rep = MultiStateReporter(str(shared / prod_nc), open_mode="r+", checkpoint_storage=prod_chk,
                                 **_rep_kw)
        try:
            sampler = unit._get_sampler(system=system, positions=positions, lambdas=lambdas,
                                        integrator=integrator, reporter=rep, simulation_settings=sim_s,
                                        thermo_settings=thermo_s, alchem_settings=alchem_s,
                                        platform=platform, restart=True, dry=False)
        except ValueError as e:
            # An UNRESUMABLE committed checkpoint (OpenFE: "Sampler in checkpoint does not match Protocol
            # settings, cannot resume") must NOT be fatal. It happens when the frozen protocol hash shifts
            # between spot attempts (e.g. code changed on the branch the VM re-clones). Discard the stale
            # production checkpoint and fall back to a FRESH warmup — spot-safe resilience, not a crash.
            if "does not match Protocol settings" not in str(e):
                raise
            log(f"[spot-driver] PRODUCTION checkpoint UNRESUMABLE ({e}); discarding it + restarting from warmup "
                f"(spot-safe fallback, not a crash)")
            for _f in (prod_nc, prod_chk):
                try:
                    (shared / _f).unlink()
                except FileNotFoundError:
                    pass
            restored_phase = None   # fall through to the warmup path below, fresh
        else:
            _set_caches(sampler, platform)
            log(f"[spot-driver] resume PRODUCTION at iter {spot._sampler_iteration(sampler)} "
                f"(interval={eff_pci}, target={eff_prod_target})")
            try:
                spot.run_to_target(sampler, rep, eff_prod_target, eff_pci,
                                   _prod_commit(rep, prod_nc, prod_chk, eff_pci), log=log)
            except _ConvergedEarly as ce:
                log(f"[spot-driver] AUTOSTOP: production converged at iter {ce.iteration} "
                    f"(< target {eff_prod_target}); stopping early (saves GPU)")
            return {"nc": shared / prod_nc, "checkpoint": shared / prod_chk}

    # ================= WARMUP (fresh, or resume a partial warmup) =============================
    warmup_restart = restored_phase == WARMUP and (shared / WARMUP_NC).is_file()
    # FRESH warmup, but a stale equilibration.nc/.chk survived on the shared dir — happens on a spot
    # restart when restore() decided 'fresh' (the prior warmup .chk was incomplete/unreadable after the
    # kill) yet the partial .nc file is still there. OpenFE's create() then does "Storage file ...
    # already exists; cowardly refusing to overwrite" and CRASHES the whole leg (observed on the firm
    # ternary, 2026-07-24). restore() already rejected these as unresumable, so clear them and let the
    # fresh warmup create cleanly. (Mirrors the unresumable-checkpoint cleanup in the except branch below,
    # applied proactively rather than only after a create() failure.)
    if not warmup_restart:
        for _f in (WARMUP_NC, WARMUP_CHK):
            _p = shared / _f
            if _p.exists():
                log(f"[spot-driver] FRESH warmup: removing stale {_f} (restore rejected it as unresumable; "
                    f"prevents 'cowardly refusing to overwrite')")
                try:
                    _p.unlink()
                except FileNotFoundError:
                    pass
    # Same single-interval invariant as production: on a RESUME the .chk frames live on the interval
    # baked into the existing warmup .nc (e.g. 8, set by RBFE_WARMUP_CKPT_ITERS), not necessarily the
    # env of THIS VM (default 10 when unset). Derive it from the file so the reporter/run/commit agree;
    # a FRESH warmup uses the env/default interval.
    eff_wci = warmup_checkpoint_iters
    if warmup_restart:
        eff_wci = spot.read_checkpoint_interval(shared / WARMUP_NC, shared / WARMUP_CHK) or warmup_checkpoint_iters
        if eff_wci != warmup_checkpoint_iters:
            log(f"[spot-driver] RESUME warmup: committed-file checkpoint_interval={eff_wci} OVERRIDES "
                f"env warmup_checkpoint_iters={warmup_checkpoint_iters} (single-interval invariant)")
    eff_warmup_target = (warmup_iters // eff_wci) * eff_wci or eff_wci
    wrep = _build_reporter(shared, WARMUP_NC, WARMUP_CHK, selection_indices,
                           eff_wci, pos_iv, vel_iv)
    try:
        warmup = unit._get_sampler(system=system, positions=positions, lambdas=lambdas,
                                   integrator=warmup_integrator, reporter=wrep, simulation_settings=sim_s,
                                   thermo_settings=thermo_s, alchem_settings=alchem_s,
                                   platform=platform, restart=warmup_restart, dry=False)
    except ValueError as e:
        # Same spot-safe fallback as production: an unresumable warmup checkpoint (protocol-hash shift across
        # attempts) is discarded and warmup restarts FRESH, rather than crashing the leg.
        if not (warmup_restart and "does not match Protocol settings" in str(e)):
            raise
        log(f"[spot-driver] WARMUP checkpoint UNRESUMABLE ({e}); discarding it + starting warmup FRESH "
            f"(spot-safe fallback, not a crash)")
        for _f in (WARMUP_NC, WARMUP_CHK):
            try:
                (shared / _f).unlink()
            except FileNotFoundError:
                pass
        warmup_restart = False
        # discarded the stale checkpoint -> genuinely fresh: revert to the env/default interval.
        eff_wci = warmup_checkpoint_iters
        eff_warmup_target = (warmup_iters // eff_wci) * eff_wci or eff_wci
        wrep = _build_reporter(shared, WARMUP_NC, WARMUP_CHK, selection_indices,
                               eff_wci, pos_iv, vel_iv)
        warmup = unit._get_sampler(system=system, positions=positions, lambdas=lambdas,
                                   integrator=warmup_integrator, reporter=wrep, simulation_settings=sim_s,
                                   thermo_settings=thermo_s, alchem_settings=alchem_s,
                                   platform=platform, restart=False, dry=False)
    except Exception as e:  # noqa: BLE001 — diagnose then RE-RAISE; this never swallows a failure
        # ★★ THE SETUP MINIMISER CAN NaN TOO, AND UNTIL NOW THAT PATH PRODUCED NO EVIDENCE AT ALL
        #    (2026-07-27, unit e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral).
        #
        # The leg died with `openmm.OpenMMException: Particle coordinate is NaN` raised INSIDE
        # `_get_sampler` -> `sampler.setup()` -> `multistate.minimize()` — i.e. before any MD, in the small
        # minimisation `setup()` performs. The NaN instrumentation 40 lines below covers only
        # `SimulationNaNError` from the WARMUP MD loop, so this failure surfaced as a bare rc=1 traceback
        # with no clash report and no saved-state analysis. The one question that decides whether the edge
        # is retryable — is there a real force-bearing contact, or did a coordinate blow up? — had no
        # answer, and CLAUDE.md §4 forbids guessing it.
        #
        # ⚠ RE-RAISE IS MANDATORY. This is an evidence hook, NOT a recovery path: a leg that NaNs during
        # setup has produced nothing and must still fail loudly. Swallowing it would turn a hard failure
        # into a silent one, which is the defect class this repo keeps paying for.
        if "NaN" in str(e) or type(e).__name__ == "SimulationNaNError":
            log(f"[nan-diag] caught {type(e).__name__} during SAMPLER SETUP (pre-MD minimisation): {e}")
            log("[nan-diag] the positions below are the ones handed to setup(), so a force-bearing contact "
                "here is a STAGING/geometry fault (retry on a fresh host will reproduce it), whereas clean "
                "contacts point at a parameterisation or coordinate fault.")
            _clash_report(positions, system, log, "setup_nan")
            _diagnose_nan_dir(shared, system, log)
        raise
    _set_caches(warmup, platform)
    if not warmup_restart and spot._sampler_iteration(warmup) == 0:
        # the big minimization (setup() already did a tiny 100-step one); still fast/non-resumable.
        log("[spot-driver] warmup minimize")
        warmup.minimize(max_iterations=sim_s.minimization_steps)
    log(f"[spot-driver] WARMUP from iter {spot._sampler_iteration(warmup)} -> {eff_warmup_target} "
        f"(interval={eff_wci})")
    try:
        spot.run_to_target(warmup, wrep, eff_warmup_target, eff_wci,
                           _commit(WARMUP, WARMUP_NC, WARMUP_CHK, eff_wci), log=log)
    except Exception as e:
        if type(e).__name__ == "SimulationNaNError":
            log(f"[nan-diag] caught {type(e).__name__} during WARMUP: {e}")
            _diagnose_nan_dir(shared, system, log)
        raise

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
    # Reaching here always means a FRESH production create from the warmup state — the resume-production
    # path returns at the top of this function, so any prod_nc/prod_chk on disk now is a stale leftover
    # from an earlier attempt that never validly resumed. Clear it, else create() below hits the same
    # "cowardly refusing to overwrite" crash the warmup path guards against.
    for _f in (prod_nc, prod_chk):
        _p = shared / _f
        if _p.exists():
            log(f"[spot-driver] FRESH production: removing stale {_f} (never validly resumed; "
                f"prevents 'cowardly refusing to overwrite')")
            try:
                _p.unlink()
            except FileNotFoundError:
                pass
    prod.create(
        thermodynamic_states=final["thermodynamic_states"],
        sampler_states=final["sampler_states"],
        storage=prep,
        initial_thermodynamic_states=final["replica_state_indices"],
        unsampled_thermodynamic_states=final["unsampled"] or None,
        metadata=final["metadata"] or None,
    )
    _set_caches(prod, platform)
    log(f"[spot-driver] PRODUCTION created from warmup; run -> {prod_target}"
        f"{' (autostop-on-convergence enabled)' if _autostop_enabled() else ''}")
    try:
        spot.run_to_target(prod, prep, prod_target, production_checkpoint_iters,
                           _prod_commit(prep, prod_nc, prod_chk, production_checkpoint_iters), log=log)
    except _ConvergedEarly as ce:
        log(f"[spot-driver] AUTOSTOP: production converged at iter {ce.iteration} "
            f"(< target {prod_target}); stopping early (saves GPU)")
    return {"nc": shared / prod_nc, "checkpoint": shared / prod_chk}
