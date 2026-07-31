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

import contextlib
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


# ⏱ A HARD DEADLINE FOR ONE BLOCKING CALL. `signal.alarm` rather than a thread, because the thing being
# bounded is a C-level socket read inside boto3 and only a signal interrupts that from the main thread. It is
# restored on exit, so nesting or a later use is unaffected; on a non-main thread (tests, a future caller)
# `signal.signal` raises ValueError and this degrades to NOT bounding the call, which is exactly the previous
# behaviour and never worse than it.
@contextlib.contextmanager
def _deadline(seconds, message):
    import signal as _sig
    if not seconds or seconds <= 0:
        yield
        return
    try:
        def _fire(_signum, _frame):
            raise TimeoutError(message)
        prev = _sig.signal(_sig.SIGALRM, _fire)
        prev_left = _sig.alarm(int(seconds))
    except (ValueError, AttributeError):     # not the main thread, or no SIGALRM on this platform
        yield
        return
    try:
        yield
    finally:
        _sig.alarm(0)
        _sig.signal(_sig.SIGALRM, prev)
        if prev_left:
            _sig.alarm(prev_left)


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
    legitimately ~1.0–1.5 A; H–X constraints ~1.0 A).

    ★ CustomBondForce IS COUNTED, AND THE OMISSION WAS MEASURED, NOT SUSPECTED (2026-07-27, unit
    `e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral`, S3 complex.log of the 1:41 PM ET
    failure). That leg's `[clash-diag:initial]` listed pairs (4044,4043) d=1.375 A, (4041,4042)
    d=1.386 A, (4047,4046) d=1.391 A and (4050,4044) d=1.399 A as NON-BONDED. Those are aromatic
    C–C bond lengths on consecutive ligand indices — they are bonds. They were invisible here
    because OpenFE's HybridTopologyFactory moves the alchemically-transforming bonds into a
    **CustomBondForce** (so the interaction can be interpolated between the A and B states), and
    this function only read `HarmonicBondForce`. The consequence was not cosmetic: every one of
    those bonded pairs was then handed to the "is it force-bearing?" test as a candidate contact,
    which is how a report meant to name the offending atoms filled its top-5 with chemistry."""
    import openmm
    pairs = set()
    for f in system.getForces():
        if isinstance(f, openmm.HarmonicBondForce):
            for k in range(f.getNumBonds()):
                p = f.getBondParameters(k)
                i, j = int(p[0]), int(p[1])
                pairs.add((min(i, j), max(i, j)))
        elif isinstance(f, openmm.CustomBondForce):
            for k in range(f.getNumBonds()):
                p = f.getBondParameters(k)
                i, j = int(p[0]), int(p[1])
                pairs.add((min(i, j), max(i, j)))
    for k in range(system.getNumConstraints()):
        i, j, _ = system.getConstraintParameters(k)
        pairs.add((min(int(i), int(j)), max(int(i), int(j))))
    return pairs


def _custom_nb_exclusions(system):
    """(n_custom_nb_forces, pairs_excluded_from_EVERY_CustomNonbondedForce).

    ★ WHY A SECOND EXCLUSION MAP EXISTS (2026-07-27, same failure). `_nonbonded_exceptions` reads
    only `openmm.NonbondedForce`, so a pair carrying a zeroed exception there was reported
    `EXCLUDED-hybrid(benign)` — including a pair at **d=0.000 A**. But an OpenFE hybrid topology
    does its alchemical sterics/electrostatics in `CustomNonbondedForce` objects with their OWN
    exclusion lists, and a pair excluded in the standard force is NOT automatically excluded there.
    A coincident pair still coupled by a custom force is precisely how `LocalEnergyMinimizer` gets
    a non-finite gradient out of coordinates that are themselves finite — so calling it "benign"
    on the strength of the standard force alone is a verdict the data does not support.

    Returned pairs are excluded in EVERY custom nonbonded force (the intersection), because a pair
    that any one of them still sees is still coupled."""
    import openmm
    sets, n = [], 0
    for f in system.getForces():
        if isinstance(f, openmm.CustomNonbondedForce):
            n += 1
            s = set()
            for k in range(f.getNumExclusions()):
                i, j = f.getExclusionParticles(k)
                s.add((min(int(i), int(j)), max(int(i), int(j))))
            sets.append(s)
    if not sets:
        return 0, set()
    inter = sets[0]
    for s in sets[1:]:
        inter = inter & s
    return n, inter


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


def _pair_verdict(ga, gb, exc, n_custom_nb, custom_excl):
    """(is_force_bearing, human_label) for one close pair. PURE — no OpenMM objects, so it is
    unit-testable without a GPU or a built system.

    THE THREE-WAY DISTINCTION THIS RESTORES. The old test was binary and read one force:
    "in NonbondedForce exceptions with cp=eps=0" -> benign, else real. That collapsed two very
    different states into `EXCLUDED-hybrid(benign)`:

      * excluded in the standard force AND in every CustomNonbondedForce -> genuinely uncoupled;
      * excluded in the standard force but STILL SEEN by a custom nonbonded force -> coupled by the
        alchemical sterics/electrostatics, which is exactly the term that goes non-finite at r=0.

    The 1:41 PM ET primary-amide log reported a pair at **d=0.000 A** in the first category's
    wording while the code had never looked at the second, so the report's most alarming number
    came with a reassurance nothing had measured. `n_custom_nb == 0` (a plain, non-alchemical
    system) keeps the original two-way answer, so nothing outside the hybrid path changes."""
    key = (min(int(ga), int(gb)), max(int(ga), int(gb)))
    std = exc.get(key)
    if std is not None and (abs(std[0]) > 1e-6 or abs(std[1]) > 1e-6):
        return True, f"exception(cp={std[0]:.3g} eps={std[1]:.3g})"
    if std is None:
        return True, "FORCE-BEARING(real clash)"
    # zeroed standard exception — the custom nonbonded forces decide.
    if n_custom_nb == 0:
        return False, "EXCLUDED-hybrid(benign)"
    if key in custom_excl:
        return False, "EXCLUDED-everywhere(benign)"
    return True, f"FORCE-BEARING via CustomNonbondedForce (zeroed in NonbondedForce, NOT excluded " \
                 f"in all {n_custom_nb} custom nonbonded force(s))"


def energy_probe_verdict(rows, total_kj_mol, grad=None):
    """The BLOCK-or-RETRY sentence for a per-force energy probe. PURE, so the rule that decides
    whether this lane keeps buying hosts for an edge is unit-tested rather than eyeballed in a log.

    `rows` are `_force_energy_probe`'s dicts ({force, energy_kj_mol, finite}); `total_kj_mol` is
    the summed potential; `grad` is `_gradient_probe`'s dict, or None when no gradient was taken.
    The verdict is deliberately worded as an instruction, because the whole point of the reading is
    that the next person (or tick) must not have to re-derive it."""
    import math
    bad = [r["force"] for r in rows if not r.get("finite", True)]
    if bad:
        return (f"⛔ DETERMINISTIC: {len(bad)} force term(s) are NON-FINITE at the INPUT coordinates, "
                f"before a single minimisation step — {bad}. This is a property of the staged system, "
                f"not of the rented host; a fresh host will reproduce it. BLOCK the unit, do not retry.")
    if not math.isfinite(total_kj_mol):
        return ("⛔ DETERMINISTIC: the TOTAL potential is non-finite while every individual group is "
                "finite — a summation overflow in the staged system. BLOCK the unit, do not retry.")
    if not rows:
        return ("⚠ INCONCLUSIVE: the probe evaluated no force groups, so it says nothing about the "
                "system. Do not read this as either a block or a retry verdict.")
    hi = max(abs(r["energy_kj_mol"]) for r in rows)
    # ★★ A FINITE ENERGY IS NOT A FINITE GRADIENT, AND THE MINIMISER FOLLOWS THE GRADIENT
    # (2026-07-28 — this sentence is here because its absence cost 25 rentals).
    #
    # The verdict below used to end at "every force term is FINITE ... RETRY candidate, not a block
    # candidate", and it said that about `cw_bio_primary_amide` on 2026-07-27. The lane believed it and
    # re-placed that unit twenty-five times across seven distinct card/driver combinations; every single
    # attempt died at the same `LocalEnergyMinimizer.minimize` call with the same message
    # (`step1-nan-forensics.json`). The reading was not wrong — it was INCOMPLETE. "Force term" here means
    # a force OBJECT's potential ENERGY, and `LocalEnergyMinimizer` does not descend energies, it descends
    # their derivative. A system can hold an unremarkable energy at a point whose gradient is unusable: an
    # excluded coincident pair contributes a bounded energy and a derivative set only by how nearly equal
    # two coordinates are — measured here at 4.996e17 kJ/mol/nm, finite, and twelve orders of magnitude
    # above every other atom in the same box.
    #
    # So a "no non-finite energy" reading may no longer be spoken as RETRY on its own. With a gradient
    # reading attached, the verdict is decided by the gradient; without one, the honest answer is that half
    # the question was never asked.
    g = grad or {}
    if g.get("n_nonfinite"):
        return (f"⛔ DETERMINISTIC: every force term's ENERGY is finite (max |E| = {hi:.6g} kJ/mol) but the "
                f"GRADIENT is NON-FINITE on {g['n_nonfinite']} atom(s) at the input coordinates — "
                f"{g.get('top')}. A minimiser cannot step away from a point whose derivative is not a "
                f"number, so this reproduces on every host. Do not rent another one: fix the geometry that "
                f"produces it (`_dedegenerate_positions`) or block the unit.")
    # ★★ AND THE CASE THAT IS FINITE IN DOUBLE AND STILL KILLS EVERY GPU (2026-07-28, the measurement that
    # closed `cw_bio_primary_amide`). Its worst gradient was 4.996e17 kJ/mol/nm — a NUMBER, so `n_nonfinite`
    # was 0 and the CPU minimiser did descend it to completion — while the largest gradient on any atom NOT
    # in a coincident pair was 6.46e5 — a factor of 7.7e11, and the two atoms carrying it were the d=0.000 A
    # pair. Every GPU attempt died there; 25 of them, on 7 distinct cards. Displacing ONE of the two by
    # 0.01 A drops the system maximum to 646013.18 kJ/mol/nm against the 646013.30 that atom already carried
    # before — i.e. the singular force disappears and NOTHING ELSE IN THE BOX MOVES, to six significant
    # figures. That before/after is the whole justification for fixing the geometry rather than blocking the
    # edge, and it is recorded in `step1-setup-energy-probe.json` (`gradient_probe` / `gradient_probe_after`).
    # ⚠ Quote the pair 4.996e17 / 6.46e5 TOGETHER: both come from ONE build. The non-degenerate maximum is a
    # property of that build's water placement and moves between builds (an earlier build read 3.44e5), while
    # the degenerate one is ~1e17 in every build. Mixing the two builds' numbers into one ratio is wrong.
    # SUPERSEDED, retained: "3.44e5", quoted from a different build than the 4.996e17 it was compared with.
    #
    # ⚠ THE TEST IS THE DEGENERACY, NOT A MAGNITUDE. There is no honest cutoff on |F|: a freshly solvated
    # box legitimately carries 1e5-1e6 kJ/mol/nm on its worst atom and a minimiser is exactly the tool for
    # that. What makes this different is not that the number is big but that it has NO PHYSICAL SCALE — it
    # is set by how nearly equal two coordinates happen to be, so the same system re-solvated gives a
    # different one. A threshold here would be a constant nobody could derive; the boolean "are two atoms at
    # the same point, and is that where the force is?" is measurable and is the thing the remedy addresses.
    if g.get("n_coincident_pairs") and g.get("top_atoms_are_coincident"):
        _r = g.get("ratio_over_rest")
        return (f"⛔ DETERMINISTIC: every force term's ENERGY is finite (max |E| = {hi:.6g} kJ/mol) and the "
                f"gradient is finite — but {g['n_coincident_pairs']} pair(s) of atoms sit at the SAME "
                f"coordinates ({g.get('coincident_atoms')}), and they carry the largest gradient in the "
                f"system: {g.get('max_kj_mol_nm'):.6g} kJ/mol/nm against "
                f"{g.get('max_excluding_coincident_kj_mol_nm'):.6g} on every non-degenerate atom"
                + (f" — a factor of {_r:.3g}" if _r else "")
                + f". That force has no physical scale; it is set by how nearly equal two coordinates are. "
                  f"Measured consequence on this lane: the double-precision CPU minimiser descended it to "
                  f"completion, and the GPU minimiser failed on every one of 25 attempts across 7 distinct "
                  f"card/driver combinations. Do not rent another host: de-degenerate the starting "
                  f"coordinates (`_dedegenerate_positions`).")
    if g.get("max_kj_mol_nm") is not None:
        return (f"✅ every force term is FINITE at the input coordinates (max |E| = {hi:.6g} kJ/mol, "
                f"total = {total_kj_mol:.6g} kJ/mol) AND the gradient is finite everywhere "
                f"(max |F| = {g['max_kj_mol_nm']:.6g} kJ/mol/nm on atom {g.get('argmax')}). The NaN was "
                f"produced DURING minimisation, not by the system as built — RETRY candidate.")
    return (f"⚠ HALF-MEASURED: every force term's ENERGY is finite at the input coordinates "
            f"(max |E| = {hi:.6g} kJ/mol, total = {total_kj_mol:.6g} kJ/mol), but NO GRADIENT READING was "
            f"taken and the minimiser follows the gradient, not the energy. This is NOT a retry verdict — "
            f"see `_gradient_probe`.")


# The most recent `_gradient_probe` reading, so a caller that only has `_force_energy_probe`'s row list
# (nr4a3_rbfe's hmr-diag hook, step1_setup_energy_probe) can record the gradient too without every one of
# them changing signature. Emptied and refilled on each probe; empty means "not measured", never "fine".
LAST_GRADIENT_PROBE = {}


def _gradient_probe(ctx, log, tag, top_n=6, positions=None):
    """Per-atom |F| at the probed coordinates — the reading `_force_energy_probe` was missing.

    ★★ WHY IT IS A SEPARATE READING AND NOT A DETAIL OF THE ENERGY ONE. `LocalEnergyMinimizer` descends
    the DERIVATIVE of the potential. An energy that is finite everywhere therefore does not certify that a
    minimiser can take a step: a pair of atoms at exactly coincident coordinates contributes a bounded
    energy (its direct nonbonded term is excluded) and a derivative with no physical scale — measured at
    4.996e17 kJ/mol/nm against 6.46e5 on the largest non-degenerate atom of the same 112,955-atom build.
    The energy-only probe called that state "RETRY candidate" on 2026-07-27 and the lane then bought
    twenty-five hosts to watch it fail identically (`step1-nan-forensics.json`).

    Returns {"n_nonfinite", "max_kj_mol_nm", "argmax", "top"} or {} if the reading could not be taken —
    never a fabricated zero, because "no gradient measured" and "gradient fine" have opposite consequences.
    Non-fatal: only ever called from a diagnostic path."""
    try:
        import math
        import numpy as np
        from openmm import unit as ommunit
        f = ctx.getState(getForces=True).getForces(asNumpy=True).value_in_unit(
            ommunit.kilojoule_per_mole / ommunit.nanometer)
        arr = np.asarray(f, dtype=float).reshape(-1, 3)
        mag = np.sqrt((arr * arr).sum(axis=1))
        finite = np.isfinite(mag)
        n_bad = int((~finite).sum())
        order = np.argsort(-np.where(finite, mag, np.inf))[:top_n]
        top = [{"atom": int(i), "f_kj_mol_nm": (float(mag[i]) if math.isfinite(float(mag[i])) else None)}
               for i in order]
        out = {"n_nonfinite": n_bad,
               "max_kj_mol_nm": (float(mag[finite].max()) if finite.any() else None),
               "argmax": (int(np.argmax(np.where(finite, mag, -1.0))) if finite.any() else None),
               "top": top}
        # ★★ AND WHETHER THAT FORCE BELONGS TO A COORDINATE DEGENERACY (2026-07-28). A large gradient on
        # its own is not diagnostic — a freshly solvated box legitimately carries 1e5-1e6 kJ/mol/nm on its
        # worst atom, which is what a minimiser is FOR. What is diagnostic is a gradient that belongs to a
        # pair of atoms at the same coordinates, because that force has no physical scale at all: it is set
        # by how close to exactly-equal the two coordinates happen to be. Separating the two is what lets
        # the verdict below name a REMEDY instead of a threshold.
        if positions is not None:
            pairs = coincident_pairs(arr_positions(positions))
            deg = {a for p in pairs for a in p}
            rest = [float(mag[i]) for i in range(len(mag))
                    if i not in deg and math.isfinite(float(mag[i]))]
            out["n_coincident_pairs"] = len(pairs)
            out["coincident_atoms"] = sorted(deg)[:16]
            out["max_excluding_coincident_kj_mol_nm"] = max(rest) if rest else None
            out["top_atoms_are_coincident"] = bool(deg) and all(
                t["atom"] in deg for t in top[:len(deg)])
            if deg and rest and max(rest) > 0:
                out["ratio_over_rest"] = float(mag[sorted(deg)[0]]) / max(rest)
        log(f"[grad-diag:{tag}] atoms={arr.shape[0]} non-finite gradient on {n_bad} atom(s); "
            f"max finite |F| = {out['max_kj_mol_nm']!r} kJ/mol/nm on atom {out['argmax']}"
            + (f"; {out.get('n_coincident_pairs')} coincident coordinate pair(s), max |F| over every "
               f"NON-degenerate atom = {out.get('max_excluding_coincident_kj_mol_nm')!r}"
               if positions is not None else ""))
        for t in top:
            log(f"[grad-diag:{tag}]   atom {t['atom']:>7} |F| = {t['f_kj_mol_nm']!r} kJ/mol/nm")
        return out
    except Exception as e:  # noqa: BLE001 — pragma: no cover
        log(f"[grad-diag:{tag}] failed: {type(e).__name__}: {e}")
        return {}


def arr_positions(positions):
    """`positions` as a plain list of [x, y, z] in nm, whether it arrived as a united Quantity, a numpy
    array or a list of Vec3. Trivial, and it exists so `coincident_pairs` never has to know."""
    if hasattr(positions, "value_in_unit"):
        from openmm import unit as ommunit
        positions = positions.value_in_unit(ommunit.nanometer)
    return [[float(c) for c in p] for p in positions]


def coincident_pairs(positions, tol_nm=1e-6):
    """Indices of atom pairs whose coordinates are EQUAL to within `tol_nm`. PURE.

    Separate from `_clash_report`'s KDTree scan on purpose: that one reports the closest pair per atom and
    classifies it as force-bearing or excluded, which is the right question for a steric clash and the
    wrong one here. A coincident pair is not a clash — it is a coordinate degeneracy, and the reason it
    matters is that the derivative of any r-dependent term at r = 0 is not a number regardless of whether
    the pair is excluded. `tol_nm` defaults to a float-comparison epsilon, not a chemical distance: this
    tests coordinate EQUALITY, so the literal bounds precision and does not encode a rule.

    PURE STDLIB ON PURPOSE — no scipy, no numpy, no OpenMM. This function is the precondition of a rule
    that decides whether a leg gets bought, so it has to be exercisable by the same unit suite that gates
    the launcher, and that suite runs in an environment with no MD stack. Cell-hashing on a tol-sized grid
    is also exactly the right algorithm for the question: coordinate equality is a hash lookup, not a
    nearest-neighbour search."""
    tol = float(tol_nm)
    pts = [tuple(float(c) for c in p) for p in positions]
    cells = {}
    for i, (x, y, z) in enumerate(pts):
        cells.setdefault((int(x // tol), int(y // tol), int(z // tol)), []).append(i)
    out = set()
    for (cx, cy, cz) in list(cells):
        near = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    near.extend(cells.get((cx + dx, cy + dy, cz + dz), ()))
        for i in cells[(cx, cy, cz)]:
            xi, yi, zi = pts[i]
            for j in near:
                if j == i:
                    continue
                xj, yj, zj = pts[j]
                if (xi - xj) ** 2 + (yi - yj) ** 2 + (zi - zj) ** 2 <= tol * tol:
                    out.add((min(i, j), max(i, j)))
    return sorted(out)


def _dedegenerate_positions(positions, log, tag, tol_nm=1e-6, nudge_nm=1e-3, seed=20260728):
    """Break exactly-coincident coordinates by a tiny deterministic displacement. Returns (positions, report).

    ★★ WHY THIS IS A LEGITIMATE FIX AND NOT A FUDGE. What follows immediately is
    `sampler.setup()`'s own `LocalEnergyMinimizer` over every lambda state; the coordinates handed to it
    are a STARTING POINT that the minimiser is about to move anyway. Displacing one member of a coincident
    pair by 1e-3 nm (0.01 A — two orders of magnitude below any bond length) changes which point the
    descent starts from and nothing else. No force field parameter, no lambda schedule, no thermodynamic
    state and no estimator is touched, so it cannot bias a free energy: the quantity MBAR reduces is a
    function of the sampled ensemble, and the ensemble is generated after minimisation and equilibration.

    ⚠ IT IS ALSO NOT A CLASH FIXER. It moves ONLY pairs that are coordinate-degenerate to within a float
    epsilon. A genuine 1.6 A contact is left exactly where it is, because that is a chemistry question the
    minimiser is entitled to answer and this function has no business pre-empting.

    Deterministic (fixed seed) so two hosts handed the same system start from the same coordinates —
    a random nudge would make a failing leg irreproducible, which is the opposite of what this lane needs.
    """
    import random
    # OpenMM is imported ONLY when the caller actually handed a united Quantity. The pure-python path is
    # what the launcher's own unit suite exercises, and that suite runs where there is no MD stack — a
    # top-level `from openmm import ...` would make the rule untestable in exactly the environment that
    # gates the spend.
    has_unit = hasattr(positions, "value_in_unit")
    if has_unit:
        from openmm import unit as ommunit
        raw = positions.value_in_unit(ommunit.nanometer)
    else:
        raw = positions
    xyz = [[float(c) for c in p] for p in raw]
    pairs = coincident_pairs(xyz, tol_nm=tol_nm)
    report = {"n_coincident_pairs": len(pairs), "pairs": pairs[:16], "nudge_nm": float(nudge_nm),
              "tol_nm": float(tol_nm), "moved_atoms": []}
    if not pairs:
        log(f"[dedegen:{tag}] no coincident coordinate pairs (tol {tol_nm} nm) — positions unchanged")
        return positions, report
    rng = random.Random(seed)
    moved = []
    for _, b in pairs:                       # move the SECOND member only; the first keeps its position
        if b in moved:
            continue
        v = [rng.gauss(0.0, 1.0) for _ in range(3)]
        n = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5 or 1.0
        xyz[b] = [xyz[b][k] + v[k] / n * float(nudge_nm) for k in range(3)]
        moved.append(b)
    report["moved_atoms"] = moved[:16]
    report["n_moved"] = len(moved)
    log(f"[dedegen:{tag}] {len(pairs)} coincident coordinate pair(s) at tol {tol_nm} nm "
        f"{pairs[:6]}{' ...' if len(pairs) > 6 else ''} -> displaced {len(moved)} atom(s) by "
        f"{nudge_nm} nm each. The pre-MD minimiser runs next and moves them again; this only ensures its "
        f"first gradient is a number.")
    if has_unit:
        from openmm import unit as ommunit
        # Rebuild in the SAME container the caller used. OpenFE hands positions either as a list of Vec3
        # or as a numpy array, and `_get_sampler`/`Context.setPositions` accept both — but handing back the
        # other one would be a silent type change in a hot path, and this function's whole claim is that it
        # changes nothing except two or three coordinates.
        if type(raw).__module__.startswith("numpy"):
            import numpy as np
            return (np.asarray(xyz, dtype=float) * ommunit.nanometer), report
        from openmm import Vec3
        return ([Vec3(*p) for p in xyz] * ommunit.nanometer), report
    return xyz, report


def _force_energy_probe(system, positions, log, tag, platform_name=None):
    """Single-point energy PER FORCE at the given positions. Returns the list of rows it logged.

    ★★ THIS IS THE OBSERVATION THAT DECIDES `BLOCK` vs `RETRY` WITHOUT RENTING A SECOND HOST
    (2026-07-27). When `LocalEnergyMinimizer` raises `Particle coordinate is NaN` inside
    `sampler.setup()`, the question that decides everything is whether the fault is in the STAGED
    SYSTEM (deterministic — a fresh host reproduces it, so the unit must be blocked) or incidental
    to the machine (retry). Counting failures cannot answer that; neither can the clash report,
    which had already certified the input coordinates finite and free of force-bearing contacts.

    A per-force single-point energy at the coordinates handed to `setup()` answers it directly: if
    one force term returns `inf` or `nan` BEFORE any minimisation step has been taken, the defect
    is in the system as built and every host will reproduce it. If every term is finite and the
    total is a sane magnitude, the blow-up happened during the minimisation trajectory and the
    edge is a retry candidate. Either way the log now names the force.

    Non-fatal by construction and only ever called from a failure path, so it can never turn a
    diagnosis into a second outage. Runs on the CPU platform (not CUDA) on purpose: the failing
    context is being torn down, and CPU makes the reading independent of the card."""
    rows = []
    try:
        import copy as _copy
        import math
        import openmm
        from openmm import unit as ommunit
        probe = _copy.deepcopy(system)
        forces = list(probe.getForces())
        # One group per force so the decomposition is unambiguous. OpenMM allows 0..31.
        n = min(len(forces), 32)
        for gi, f in enumerate(forces[:n]):
            f.setForceGroup(gi)
        for f in forces[n:]:                                    # pragma: no cover — >32 forces
            f.setForceGroup(31)
        plat = None
        for name in ([platform_name] if platform_name else ["CPU", "Reference"]):
            try:
                plat = openmm.Platform.getPlatformByName(name)
                break
            except Exception:                                   # pragma: no cover
                continue
        integ = openmm.VerletIntegrator(0.001 * ommunit.picosecond)
        ctx = (openmm.Context(probe, integ, plat) if plat is not None
               else openmm.Context(probe, integ))
        ctx.setPositions(positions)
        for gi, f in enumerate(forces[:n]):
            e = (ctx.getState(getEnergy=True, groups={gi})
                 .getPotentialEnergy().value_in_unit(ommunit.kilojoule_per_mole))
            finite = math.isfinite(e)
            rows.append({"group": gi, "force": type(f).__name__, "energy_kj_mol": e,
                         "finite": finite})
            log(f"[force-diag:{tag}]   group {gi:>2} {type(f).__name__:<28} "
                f"E = {e!r} kJ/mol{'' if finite else '   <-- NON-FINITE'}")
        tot = (ctx.getState(getEnergy=True)
               .getPotentialEnergy().value_in_unit(ommunit.kilojoule_per_mole))
        log(f"[force-diag:{tag}] TOTAL potential energy = {tot!r} kJ/mol")
        # The gradient, on the SAME context and the same coordinates — the reading that decides whether a
        # minimiser can take a step at all. Attached to the verdict rather than logged beside it, so a
        # finite-energy/non-finite-gradient system cannot be read as RETRY.
        grad = _gradient_probe(ctx, log, tag, positions=positions)
        LAST_GRADIENT_PROBE.clear()
        LAST_GRADIENT_PROBE.update(grad or {})
        log(f"[force-diag:{tag}] {energy_probe_verdict(rows, tot, grad)}")
        del ctx, integ
    except Exception as e:                                      # pragma: no cover
        log(f"[force-diag:{tag}] failed: {type(e).__name__}: {e}")
    return rows


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
        try:
            n_cnb, cnb_excl = _custom_nb_exclusions(system)
        except Exception as e:                        # pragma: no cover
            log(f"[clash-diag:{tag}] could not read CustomNonbondedForce exclusions ({e})")
            n_cnb, cnb_excl = 0, set()
        nclash = sum(1 for dd, ga, gb in cand
                     if dd < thresh_nm and _pair_verdict(ga, gb, exc, n_cnb, cnb_excl)[0])
        nexcl = sum(1 for dd, ga, gb in cand
                    if dd < thresh_nm and not _pair_verdict(ga, gb, exc, n_cnb, cnb_excl)[0])
        if cand:
            log(f"[clash-diag:{tag}] non-bonded pairs < {thresh_nm*10:.2f} A: "
                f"{nclash} force-bearing (REAL) + {nexcl} excluded-everywhere (benign); "
                f"closest non-bonded = {cand[0][0]*10:.3f} A "
                f"[{n_cnb} CustomNonbondedForce(s) consulted]")
        else:
            log(f"[clash-diag:{tag}] no non-bonded pairs found")
        for dist, ga, gb in cand[:8]:
            log(f"[clash-diag:{tag}]   non-bonded pair ({ga},{gb}) d={dist*10:.3f} A  "
                f"[{_pair_verdict(ga, gb, exc, n_cnb, cnb_excl)[1]}]")
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

    # ★★ BREAK COORDINATE DEGENERACIES BEFORE ANYTHING READS THE POSITIONS (2026-07-28).
    #
    # THE INCIDENT, IN NUMBERS. Fan-out unit `e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral`
    # burned TWENTY-FIVE container starts across SEVEN distinct card/driver combinations (RTX 4090 and
    # 5090, drivers 580.95 through 595.71); every one died at the same line —
    # `LocalEnergyMinimizer.minimize` inside `sampler.setup()` — with `Particle coordinate is NaN`, before
    # any MD. Counts and hosts: `step1-nan-forensics.json`.
    #
    # WHAT SEPARATED IT FROM THE NINE UNITS THAT REACHED A ddG. One number, from the `[clash-diag:initial]`
    # line every leg logs: its closest non-bonded pair sits at 0.000 A, while the successful units span
    # 0.086-1.601 A. Not a clash — an exact coordinate DEGENERACY, and one the pair-classifier correctly
    # calls benign for sterics, because the pair is excluded from every nonbonded force. Benign for the
    # ENERGY is the whole trap: the minimiser descends the DERIVATIVE, and no r-dependent term has a
    # numerically defined derivative at r = 0. That is why the per-force energy probe found everything
    # finite and reported RETRY, and why the retry then failed twenty-five times.
    #
    # WHY IT IS FIXED HERE RATHER THAN BLOCKED. The alternative was to retire the edge, and the evidence
    # does not support that: the same staged system minimises to completion over every lambda state on the
    # CPU platform (`step1-setup-energy-probe.json`), so the system is sound and only its starting point is
    # degenerate. `_dedegenerate_positions` moves one member of each coincident pair by 0.01 A — two orders
    # of magnitude below a bond length, into a minimiser that is about to move it anyway — and touches no
    # parameter, no lambda schedule and no estimator. A leg with no coincident pair is unchanged, which is
    # every other unit in this lane.
    _dedegen = None
    if os.environ.get("RBFE_DEDEGENERATE", "1") == "1":
        try:
            positions, _dedegen = _dedegenerate_positions(positions, log, "pre-setup")
        except Exception as _de:  # noqa: BLE001 — never let a geometry guard cost a leg
            log(f"[dedegen] WARN skipped ({type(_de).__name__}: {_de}); positions unchanged")

    shared = Path(shared_basepath)
    shared.mkdir(parents=True, exist_ok=True)
    unit._prepare(True, scratch_basepath, shared)
    if _dedegen and _dedegen.get("n_coincident_pairs"):
        import json as _json
        (shared / "dedegenerate.json").write_text(_json.dumps(_dedegen, indent=2))
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

    # BINARY-ARM POCKET RESTRAINT (RBFE_RESTRAIN=1; default OFF, so every existing lane is unchanged).
    # Added HERE, before any integrator or sampler is built, because every λ state's ThermodynamicState is
    # constructed from this System — adding it once up front is exactly what makes the restraint λ-INDEPENDENT,
    # which is the property the cancellation argument rests on (ternary_restraint's docstring, choice 2).
    # Why the binary arm needs it: its ligand left the pocket in 8 of 12 replicas in BOTH cycles, so ΔG_binary
    # was not a free energy of the intended bound state (audit §L.3a–L.3d). It is flat-bottomed, so a leg that
    # behaves like the measured-clean ternary arm never feels it.
    try:
        import ternary_restraint as _restr
        _rrep = _restr.add_flat_bottom_restraint(system, positions, log=log)
        if _rrep.get("applied"):
            import json as _json
            (shared / "restraint.json").write_text(_json.dumps(_rrep, indent=2))
    except Exception as _re:  # noqa: BLE001
        # A restraint failure must never kill a leg mid-flight: unrestrained is a KNOWN state that the
        # convergence gate still catches, whereas an exception here costs the whole 44 h run.
        log(f"[restraint] WARN restraint step failed ({type(_re).__name__}: {_re}); running UNRESTRAINED")

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
    # ★★ THE RESTORE IS INSTRUMENTED AND BOUNDED, BECAUSE THIS IS WHERE TWO 5a-KS LEGS WEDGED
    #    (measured 2026-07-31 — the diagnosis, not a hypothesis).
    #
    # WHAT WAS OBSERVED. `vast_idle_guard` condemned two legs as WEDGED: `run.log` re-uploaded byte-identical
    # for 18 min, committed scalar frozen, GPU at 0 %. `ternary-diag-5aks.json` then showed the discriminating
    # fact — the archived attempt AND the live `run.log` were BOTH exactly 5115 bytes and BOTH ended on the
    # same line, `[spot-driver] warmup_target=... prod_target=...`. That line is printed immediately above
    # this call, and the next output of a healthy leg is `[restore] <phase> iter ...` from inside
    # `restore_latest`. Neither wedged attempt ever printed one. So the process was alive and hung BETWEEN
    # those two prints — i.e. inside the S3 LIST or the first object GET — on two different hosts.
    #
    # That also refutes the alternatives without needing another run: the log was reaching S3 the whole time
    # (it was being re-uploaded, byte-identical), so it is not a write-path failure; and nothing had reached
    # openmmtools yet, so it is not the GPU being taken or throttled — an idle GPU is the CORRECT reading of a
    # process that is downloading a checkpoint, which is exactly why `vast_idle_guard` refuses to condemn on
    # GPU idleness and condemns on write silence instead.
    #
    # TWO CHANGES, and they do different jobs:
    #   1. LOG BEFORE, so the next occurrence is a diagnosis rather than a localisation. A hang in
    #      `list_committed` and a hang in `fetch` are different faults with different fixes, and until now
    #      the log could not tell them apart because the first line either of them prints comes AFTER both.
    #   2. BOUND IT. A hung network call had no timeout at all, so the leg billed at gpu_util 0 until CI
    #      reaped it ~15 min later. CLAUDE.md §6: the host cannot stop its own billing — but it CAN stop its
    #      own job, and a leg that dies loudly is re-placed by the gate within a tick with its checkpoint
    #      intact. Dying beats hanging whenever the durable state is safe, and here it always is.
    _restore_timeout_s = float(os.environ.get("RBFE_RESTORE_TIMEOUT_S") or "900")

    def _restore(phases, ci, label):
        log(f"[spot-driver] restore: trying {label} (ci={ci}, timeout={_restore_timeout_s:g}s) — "
            f"an S3 LIST then a GET per candidate generation; the next line is either a [restore] verdict "
            f"or this leg is wedged in the object store")
        _t0 = time.time()
        try:
            with _deadline(_restore_timeout_s,
                           f"restore of {label} produced no [restore] line within "
                           f"{_restore_timeout_s:g}s — hung in the object store (list or fetch). The "
                           f"committed checkpoint is intact; the gate re-places this unit on a new host."):
                out = commit_store.restore_latest(phases, shared, ci)
        finally:
            log(f"[spot-driver] restore: {label} took {time.time() - _t0:.1f}s")
        return out

    restored = _restore([PRODUCTION], production_checkpoint_iters, "production")
    if restored is None:
        restored = _restore([WARMUP], warmup_checkpoint_iters, "warmup")
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
            # ★★ AND THE ONE READING THAT SEPARATES `BLOCK` FROM `RETRY` (2026-07-27). The clash
            # report above had already run on this exact edge and certified the inputs clean
            # (`nonfinite_atoms=0`, `0 force-bearing` pairs), so it could not say whether a fresh
            # host would reproduce the NaN. A per-force single-point energy AT THESE COORDINATES
            # can: a non-finite term before any minimisation step is a property of the staged
            # system and reproduces everywhere; all-finite terms mean the blow-up happened inside
            # the minimisation trajectory and the edge is retryable. See `_force_energy_probe`.
            _force_energy_probe(system, positions, log, "setup_nan")
            _diagnose_nan_dir(shared, system, log)
        raise
    _set_caches(warmup, platform)
    if os.environ.get("RBFE_SETUP_ONLY") == "1":
        # ★★ THE CONTROLLED REPRODUCTION OF A `setup()` NaN, WITH NO HOST IN THE LOOP (2026-07-27).
        # `_get_sampler` has just returned, which means `sampler.setup()` — and the
        # `LocalEnergyMinimizer.minimize` inside it — completed. That is the ENTIRE question a leg
        # that died at `multistate.py:345` poses, so a free CPU runner can answer it by running this
        # far and stopping: reach here and the minimiser is fine on this system; NaN before here and
        # the instrumented `except` above has already named the force and the geometry.
        #
        # WHY THIS AND NOT THE ENERGY PROBE ALONE. The probe evaluates the system at the coordinates
        # as handed over, with the alchemical global parameters as built. `setup()` minimises EVERY
        # thermodynamic state in the lambda schedule, applying that state's parameters first — so a
        # softcore term that is finite at the built lambda and divergent at an intermediate one is
        # invisible to a single-point reading. All-finite energies therefore rule OUT one mechanism;
        # only running the real minimiser rules out the other.
        raise SystemExit("[spot-driver] RBFE_SETUP_ONLY=1 — sampler.setup() (incl. its pre-MD "
                         "LocalEnergyMinimizer over every lambda state) COMPLETED WITHOUT A NaN on "
                         "this platform. Exiting before any MD; nothing was sampled and nothing "
                         "was committed.")
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
