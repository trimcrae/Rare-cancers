#!/usr/bin/env python3
"""SUPERSEDED — GPU driver for ONE alchemical protein point-mutation leg (perses/OpenMM route).

⚠ THIS LANE CANNOT RUN. Retained for the record and because its guards, shim and diagnostics
document a real dead end rather than a hypothetical one. The live engine is `protfep_pmx.py`
(pmx + GROMACS); see `protfep-pmx-plan.md`.

perses 0.10.3 builds the old->new residue ATOM MAP — which *is* the alchemical transformation —
by round-tripping each residue template through an OpenEye OEMol
(PolymerProposalEngine.generate_oemol_from_pdb_template -> createOEMolFromSDF -> oechem), and
OpenEye is commercial and licence-gated. Established 2026-07-24 by running it: the import shim
below satisfies perses' unconditional `from openeye import oechem` and then correctly REFUSES
the real call rather than fabricating a map. Free-CI probes confirmed there is no conditional
and no RDKit alternative on that path.


`nr4a3_protein_fep.py` is the engine's PURE layer — mutation parsing, the charge-consistency and
net-charge guards, wedge arithmetic, and the benchmark plan. It deliberately runs no MD, so its
guards stay testable on CPU. This module is the other half: the thing that actually builds a perses
hybrid topology, samples it with replica exchange, reduces it with MBAR, and writes a leg JSON.

Until this file existed, nr4a3-program-map.md's "engine BUILT 2026-07-24" was true only of the planning
layer: nothing could run a leg, so the rung stayed UNPRICED because there was no rate to price from.

WHAT ONE LEG IS
---------------
One leg = one alchemical mutation (WT side chain -> mutant side chain) in ONE environment, sampled
across `n_states` lambda windows by Hamiltonian replica exchange, reduced to a single dG by MBAR.
Two legs (bound and free) make a cycle; `nr4a3_protein_fep.summarize_wedge` does the subtraction.

DELIBERATE PHYSICS DEVIATION FROM md_settings, DECLARED HERE
------------------------------------------------------------
md_settings' canonical timestep is 4 fs (HMR + HBonds). This lane defaults to **2 fs with a 1 fs
warmup** instead, and that is a documented deviation, not drift. Reason: the alchemical softcore
region of a hybrid topology is exactly where this repo has been bitten before — the ternary lane
NaN'd at 4 fs and needed both a reduced-timestep warmup and plain-MD pre-equilibration to survive
(ternary-rbfe-runbook.md 1b/1c). The ternary lane's diagnosis was explicitly that there is **no
static predictor** for where a softcore region goes unstable; the timestep is empirical. On a first
run of a brand-new engine, a NaN costs the entire rental while 2 fs costs ~2x the iterations of a
sub-dollar leg. Escalate to 4 fs only after this lane has demonstrably survived a full leg — and
record it, do not assume it transfers from another lane.

The mutation itself is charge-conserving in every benchmark here, so no PME finite-size correction
is applied and none is needed; `nr4a3_protein_fep.plan_wedge` refuses charge-changing mutations
without an explicit strategy, and that guard is upstream of this driver.

DEFENSIVE CONSTRUCTION
----------------------
perses' and openmmtools' constructor signatures drift across releases, and this code cannot be
exercised in the dev sandbox (no MD stack — see the repo's dev-sandbox-is-not-your-limit rule: we
build here and validate on a rented GPU). So every third-party constructor is called through
`_call_filtered`, which introspects the real signature and passes only the kwargs that version
accepts, logging what it dropped. A dropped kwarg is visible in the log and in the leg JSON rather
than being an opaque TypeError forty minutes into a rental.
"""

from __future__ import annotations

import inspect
import json
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import md_settings  # noqa: E402
import nr4a3_protein_fep as pf  # noqa: E402
import protfep_bench as bench  # noqa: E402

# ---- lane settings (env-overridable; these defaults ARE the recipe) ------------------------------
# 16 lambda windows, not 11. Y->A deletes an entire phenol ring — a large transformation for a
# modest window count — and a disconnected lambda path yields a converged-LOOKING dG that is
# wrong. The marginal cost is real but small on a sub-dollar leg, and _overlap_diagnostic
# reports the adjacent-overlap bottleneck so the adequacy of this number is MEASURED per leg
# rather than assumed. Raise it if the bottleneck comes back disconnected.
N_STATES = int(os.environ.get("PROTFEP_N_STATES", "16"))
TIMESTEP_FS = float(os.environ.get("PROTFEP_TIMESTEP_FS", "2.0"))
WARMUP_TIMESTEP_FS = float(os.environ.get("PROTFEP_WARMUP_TIMESTEP_FS", "1.0"))
ITER_PS = float(os.environ.get("PROTFEP_ITER_PS", "2.5"))       # ps of MD per replica-exchange iteration
WARMUP_ITERS = int(os.environ.get("PROTFEP_WARMUP_ITERS", "100"))    # 0.25 ns at 2.5 ps/iter
PROD_ITERS = int(os.environ.get("PROTFEP_PROD_ITERS", "2000"))       # 5 ns at 2.5 ps/iter
MIN_STEPS = int(os.environ.get("PROTFEP_MIN_STEPS", "5000"))
CHUNK_ITERS = int(os.environ.get("PROTFEP_CHUNK_ITERS", "50"))       # commit/checkpoint cadence
CHECKPOINT_INTERVAL = int(os.environ.get("PROTFEP_CHECKPOINT_INTERVAL", "50"))
# Run an MBAR reduction every N chunks so a preempted leg leaves a readable partial dG and a
# progress check can see the estimate settle. 0 disables.
RUNNING_DG_EVERY = int(os.environ.get("PROTFEP_RUNNING_DG_EVERY", "4"))
TEMPERATURE_K = float(os.environ.get("PROTFEP_TEMPERATURE_K", str(md_settings.TEMPERATURE_K)))
KT_KCAL = 0.0019872041 * TEMPERATURE_K   # kB*T in kcal/mol; MBAR returns free energies in kT


def _log(msg):
    print(f"[protfep] {time.strftime('%H:%M:%S')} {msg}", flush=True)


def require_cuda_platform():
    """Pin sampling to the CUDA platform and REFUSE to run on CPU unless explicitly allowed.

    A CPU fallback is the expensive silent failure on a rented GPU: the leg still produces a dG, it
    just costs ~50x the rental to get there and nothing in the result says why. conda-forge openmm
    builds can resolve without a usable CUDA runtime, and this repo has already lost hosts to a
    PTX-version mismatch that manifested as a crash rather than a fallback — so the platform is
    asserted at leg start, in the same spirit as OPENMM_REQUIRE_CUDA elsewhere in the repo.

    Returns the platform name actually pinned, which is stamped into the leg JSON.
    """
    from openmm import Platform
    from openmmtools import cache
    names = [Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())]
    if "CUDA" not in names:
        msg = (f"CUDA platform unavailable (OpenMM sees {names}). Refusing to run a rented-GPU leg on "
               f"the CPU platform — it would produce a dG at ~50x the cost with nothing in the result "
               f"to show for it. Set PROTFEP_ALLOW_CPU=1 only for a deliberate CPU test.")
        if os.environ.get("PROTFEP_ALLOW_CPU") != "1":
            raise RuntimeError(msg)
        _log(f"WARNING {msg} — proceeding because PROTFEP_ALLOW_CPU=1")
        return names[-1] if names else "unknown"
    platform = Platform.getPlatformByName("CUDA")
    platform.setPropertyDefaultValue("Precision", os.environ.get("PROTFEP_PRECISION", "mixed"))
    cache.global_context_cache.platform = platform
    _log(f"platform pinned: CUDA (precision {os.environ.get('PROTFEP_PRECISION', 'mixed')})")
    return "CUDA"


# Known spelling drift across perses/openmmtools releases. A kwarg that is not accepted under its
# primary name is retried under these aliases BEFORE being dropped — because silently dropping a
# REQUIRED argument turns a rename into a TypeError forty minutes into a rental, which is the
# expensive version of this failure.
_KWARG_ALIASES = {
    "storage_file": ("storage", "reporter", "storage_path"),
    "storage": ("storage_file", "storage_path"),
    "mcmc_moves": ("mcmc_move",),
    "hybrid_factory": ("factory", "htf", "hybrid_topology_factory"),
    "minimisation_steps": ("minimization_steps", "n_minimization_steps"),
    "n_states": ("n_replicas", "number_of_states"),
    "checkpoint_interval": ("checkpoint_storage_interval",),
    "collision_rate": ("friction",),
}


def _call_filtered(fn, *args, **kwargs):
    """Call `fn` with only the kwargs its signature accepts, retrying known aliases first.

    A version skew in perses/openmmtools should surface as a named, logged rename or omission — not
    as a TypeError discovered after the GPU has been billing for an hour. Anything genuinely dropped
    is logged by name so the leg log says what this version did not understand.
    """
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return fn(*args, **kwargs)
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return fn(*args, **kwargs)
    accepted = set(sig.parameters)
    kept, renamed, dropped = {}, [], []
    for k, v in kwargs.items():
        if k in accepted:
            kept[k] = v
            continue
        alias = next((a for a in _KWARG_ALIASES.get(k, ()) if a in accepted and a not in kwargs), None)
        if alias:
            kept[alias] = v
            renamed.append(f"{k}->{alias}")
        else:
            dropped.append(k)
    name = getattr(fn, "__name__", str(fn))
    if renamed:
        _log(f"NOTE {name}: kwarg rename in this version — {', '.join(renamed)}")
    if dropped:
        _log(f"NOTE {name} does not accept {sorted(dropped)} in this version — dropped")
    return fn(*args, **kept)


def iters_for(ns):
    """Replica-exchange iterations for `ns` nanoseconds at this lane's ps-per-iteration. Pure.

    Deliberately timestep-INDEPENDENT: an iteration is defined by its MD time, not its step count,
    so changing the timestep changes cost, never the amount of sampling. The ternary lane's cost
    base was wrong for months because a partial iteration count was mistaken for a whole leg —
    keeping this conversion explicit is how a leg length stays auditable.
    """
    return int(round(float(ns) * 1000.0 / ITER_PS))


def steps_per_iteration(timestep_fs=None):
    """MD steps per replica-exchange iteration at a given timestep. Pure."""
    return max(1, int(round(ITER_PS * 1000.0 / float(timestep_fs or TIMESTEP_FS))))


# ------------------------------------------------------------------------------------------------
# Hybrid topology
# ------------------------------------------------------------------------------------------------
class _PoisonedOpenEye:
    """Stand-in for an OpenEye submodule that raises loudly on ANY use.

    It satisfies an import and nothing else. If perses ever actually touches OpenEye on our code
    path, this raises immediately with a clear message rather than returning something plausible —
    the failure mode we cannot accept is a number produced by a silently degraded path.
    """

    def __init__(self, name):
        self._name = name

    def __getattr__(self, attr):
        # Dunders are Python's own machinery probing the module (__file__, __path__, __all__,
        # __repr__ during import and introspection), not perses using the toolkit. Those must behave
        # like a normal absent attribute or the import itself blows up — poisoning them would make
        # the shim fail on the very statement it exists to satisfy.
        if attr.startswith("__") and attr.endswith("__"):
            raise AttributeError(attr)
        # LICENCE PROBES MUST ANSWER, NOT RAISE — and the honest answer is False.
        #
        # openff-toolkit builds its GLOBAL_TOOLKIT_REGISTRY at import time and asks
        # OpenEyeToolkitWrapper.is_available(), which calls oechem.OEChemIsLicensed(). With OpenEye
        # genuinely absent the import fails and openff cleanly skips the wrapper. A shim that raises
        # here is WORSE than no shim: it makes OpenEye look present-but-broken, and openff's import
        # dies (observed on the free build-test, 2026-07-24 — which is exactly what that $0 step is
        # for). Returning False puts the stack in the configuration it already supports and that is
        # actually true of us: OpenEye importable, not licensed, so use the RDKit/AmberTools path.
        if attr.endswith("IsLicensed"):
            return lambda *a, **k: False
        raise RuntimeError(
            f"perses tried to USE OpenEye ({self._name}.{attr}), not merely import it. The shim in "
            f"protfep_run only satisfies the unconditional `from openeye import oechem` in "
            f"PointMutationExecutor.__init__, which is dead code for a protein-only leg (OpenEye is "
            f"reached under `if ligand_input:`). A real call means this leg is NOT protein-only, or "
            f"perses changed — either way, stop and re-scope rather than trusting the result.")


def _install_openeye_shim():
    """Satisfy perses' unconditional OpenEye import for protein-only legs. Returns True if installed.

    WHY THIS IS NOT A HACK AROUND A LICENCE. OpenEye is commercial and license-gated, and perses uses
    it for SMALL-MOLECULE handling: `createOEMolFromSDF`, `Molecule.from_openeye`, topology generation
    from an OEMol — all inside `if ligand_input:` in PointMutationExecutor.__init__. Our benchmark
    legs are protein-only (barnase-barstar; no small molecule anywhere), so that branch is never
    taken. The only thing standing between us and the hybrid topology is that the `from openeye
    import oechem` statement sits ABOVE the branch and runs unconditionally — verified 2026-07-24
    from the installed source and from a live traceback at relative_point_mutation_setup.py:236.

    So this makes an import succeed for code that is never executed. It does NOT emulate OpenEye:
    every attribute access raises. If perses genuinely needs the toolkit on this path we find out at
    once, with a message saying so.

    Naturally inert once a real OpenEye is installed — if the module imports, the shim is skipped.
    """
    import types
    try:
        import openeye  # noqa: F401 — a real install wins; never shadow it
        _log("OpenEye is genuinely installed — shim not needed")
        return False
    except ImportError:
        pass
    shim = types.ModuleType("openeye")
    submodules = ("oechem", "oeomega", "oequacpac", "oegraphsim", "oeshape", "oespruce", "oedepict")
    for name in submodules:
        sub = types.ModuleType(f"openeye.{name}")
        sub.__getattr__ = _PoisonedOpenEye(f"openeye.{name}").__getattr__
        setattr(shim, name, sub)
        sys.modules[f"openeye.{name}"] = sub
    sys.modules["openeye"] = shim
    _log("installed OpenEye import shim (protein-only leg; any real USE of the toolkit will raise)")
    return True


def build_htf(structure_path, mutation_spec, charge_method=None, ionic_strength_M=None):
    """Build the perses hybrid topology for one protein point mutation in one environment.

    BOTH of this lane's legs use perses' `get_apo_htf()`. That is not a bug: in perses, "apo" means
    "no SMALL-MOLECULE ligand", and there is no small molecule anywhere in a protein-protein
    benchmark. The bound-vs-free distinction lives entirely in how many protein chains the staged
    PDB contains, which is `protfep_bench.stage_leg`'s job.
    """
    from openmm import app, unit

    m = pf.classify_mutation(mutation_spec)
    # Install the shim BEFORE perses is imported: the offending statement runs at __init__ time, but
    # keeping the order explicit means a future module-level import is covered too.
    shimmed = _install_openeye_shim()
    from perses.app.relative_point_mutation_setup import PointMutationExecutor

    if not m["buildable"]:
        raise pf.MutationError(m["risk"])
    cm = (charge_method or md_settings.CHARGE_METHOD).strip().lower()
    ionic = float(ionic_strength_M if ionic_strength_M is not None else md_settings.IONIC_STRENGTH_M)

    _log(f"building hybrid: {m['spec']} ({m['wt']}->{m['mutant']}) from {structure_path}")
    executor = _call_filtered(
        PointMutationExecutor,
        protein_filename=structure_path,
        mutation_chain_id=m["chain"],
        mutation_residue_id=str(m["resid"]),
        proposed_residue=m["mutant"],
        ionic_strength=ionic * unit.molar,
        forcefield_files=list(md_settings.PROTEIN_FORCEFIELDS),
        small_molecule_forcefields=md_settings.SMALL_MOLECULE_FORCEFIELD,
        # NO hydrogen-mass repartitioning: this lane runs 2 fs, and HMR exists to buy a 4 fs step.
        # Pairing HMR with 2 fs would be an unnecessary mass perturbation for no throughput gain.
        forcefield_kwargs={"constraints": app.HBonds, "rigidWater": md_settings.RIGID_WATER},
        periodic_forcefield_kwargs={"nonbondedMethod": app.PME},
        conduct_endstate_validation=False,
    )
    htf = executor.get_apo_htf()
    n_atoms = htf.hybrid_system.getNumParticles()
    _log(f"hybrid built: {n_atoms} particles")
    return htf, {"charge_method": cm, "mutation": m, "n_particles": int(n_atoms),
                 "ionic_strength_M": ionic, "openeye_shim": shimmed}


# ------------------------------------------------------------------------------------------------
# Sampling
# ------------------------------------------------------------------------------------------------
def _mcmc_move(timestep_fs, n_steps):
    from openmm import unit
    from openmmtools import mcmc
    return _call_filtered(
        mcmc.LangevinSplittingDynamicsMove,
        timestep=timestep_fs * unit.femtoseconds,
        collision_rate=md_settings.FRICTION_PER_PS / unit.picosecond,
        n_steps=int(n_steps),
        reassign_velocities=False,
        constraint_tolerance=1e-6,
    )


def _open_sampler(htf, storage_path, n_states, resume):
    """Create OR restore the replica-exchange sampler. Returns (sampler, reporter, resumed_iters)."""
    from openmm import unit
    from openmmtools.multistate import MultiStateReporter
    from perses.annihilation.lambda_protocol import LambdaProtocol
    from perses.samplers.multistate import HybridRepexSampler

    reporter = _call_filtered(MultiStateReporter, storage=storage_path,
                              checkpoint_interval=CHECKPOINT_INTERVAL)
    if resume and os.path.exists(storage_path) and os.path.getsize(storage_path) > 0:
        try:
            sampler = HybridRepexSampler.from_storage(reporter)
            done = int(sampler.iteration)
            _log(f"RESUMED from {storage_path} at iteration {done}")
            return sampler, reporter, done
        except Exception as e:  # noqa: BLE001 — a corrupt/truncated .nc must not strand the rental
            _log(f"resume failed ({type(e).__name__}: {e}) — starting fresh")
            try:
                os.remove(storage_path)
            except OSError:
                pass
            reporter = _call_filtered(MultiStateReporter, storage=storage_path,
                                      checkpoint_interval=CHECKPOINT_INTERVAL)

    move = _mcmc_move(TIMESTEP_FS, steps_per_iteration(TIMESTEP_FS))
    sampler = _call_filtered(HybridRepexSampler, mcmc_moves=move, hybrid_factory=htf,
                             online_analysis_interval=None)
    _log(f"setup: {n_states} lambda windows, minimisation {MIN_STEPS} steps")
    _call_filtered(sampler.setup, n_states=n_states, temperature=TEMPERATURE_K * unit.kelvin,
                   storage_file=reporter, lambda_protocol=LambdaProtocol(functions="default"),
                   minimisation_steps=MIN_STEPS, endstates=False)
    return sampler, reporter, 0


def _warmup(sampler, n_iters):
    """Reduced-timestep equilibration before production.

    The softcore region of a freshly built hybrid is the least-equilibrated part of the system, and
    a 1 fs warmup is the cheapest insurance against losing a whole rental to a NaN. openmmtools'
    `equilibrate` takes its own moves, which is precisely the hook for a different timestep;
    equilibration iterations are not written into the MBAR data set.
    """
    if n_iters <= 0:
        return 0
    warm_move = _mcmc_move(WARMUP_TIMESTEP_FS, steps_per_iteration(WARMUP_TIMESTEP_FS))
    _log(f"warmup: {n_iters} iterations at {WARMUP_TIMESTEP_FS} fs")
    _call_filtered(sampler.equilibrate, n_iters, mcmc_moves=warm_move)
    _log("warmup complete — no NaN")
    return n_iters


def run_leg(leg_id, structure_path, mutation_spec, out_dir, n_states=None, prod_iters=None,
            warmup_iters=None, resume=True, charge_method=None, meta=None):
    """Run one leg to completion (or resume it), reduce with MBAR, write `leg_<id>.json`.

    Checkpointing is per-chunk and the leg JSON is rewritten after EVERY chunk with the partial
    state — the repo's standing rule is that a partial checkpoint is the deliverable on a timeout,
    so a preempted leg must leave behind something the next dispatch can resume and a human can read.
    """
    os.makedirs(out_dir, exist_ok=True)
    n_states = int(n_states or N_STATES)
    prod_iters = int(prod_iters or PROD_ITERS)
    warmup_iters = int(WARMUP_ITERS if warmup_iters is None else warmup_iters)
    storage = os.path.join(out_dir, f"{leg_id}.nc")
    result_path = os.path.join(out_dir, f"leg_{leg_id}.json")

    record = {
        "leg_id": leg_id,
        "mutation": mutation_spec,
        "structure": os.path.basename(structure_path),
        "n_states": n_states,
        "prod_iters_target": prod_iters,
        "warmup_iters": warmup_iters,
        "timestep_fs": TIMESTEP_FS,
        "warmup_timestep_fs": WARMUP_TIMESTEP_FS,
        "iter_ps": ITER_PS,
        "prod_ns": prod_iters * ITER_PS / 1000.0,
        "temperature_K": TEMPERATURE_K,
        "engine": "perses.PointMutationExecutor + perses.HybridRepexSampler + MBAR",
        "md_settings_deviation": (
            "timestep 2 fs (canonical is 4 fs + HMR). Alchemical softcore regions are where this repo's "
            "ternary lane NaN'd at 4 fs; the timestep is empirical, so a new engine's first leg runs "
            "conservatively. No HMR, since HMR exists to buy the 4 fs step this lane is not taking."),
        "status": "starting",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if meta:
        record["meta"] = meta

    def _commit(**updates):
        record.update(updates)
        record["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(result_path, "w") as fh:
            json.dump(record, fh, indent=2)

    _commit()
    t0 = time.time()
    try:
        record["platform"] = require_cuda_platform()
        _commit()
        htf, build_meta = build_htf(structure_path, mutation_spec, charge_method=charge_method)
        record["charge_method"] = build_meta["charge_method"]
        record["n_particles"] = build_meta["n_particles"]
        _commit(status="built")

        sampler, reporter, done = _open_sampler(htf, storage, n_states, resume)
        if done == 0:
            _commit(status="warmup")
            _warmup(sampler, warmup_iters)
        _commit(status="production", iterations_done=done)

        chunks = 0
        while done < prod_iters:
            chunk = min(CHUNK_ITERS, prod_iters - done)
            it0 = time.time()
            sampler.extend(chunk)
            done = int(getattr(sampler, "iteration", done + chunk))
            chunks += 1
            rate = (time.time() - it0) / max(1, chunk)
            _log(f"iter {done}/{prod_iters} ({rate:.1f} s/iter, {(prod_iters-done)*rate/3600:.1f} h left)")
            update = {"status": "production", "iterations_done": done, "s_per_iter": round(rate, 2),
                      "gpu_hours_so_far": round((time.time() - t0) / 3600.0, 3)}
            # A RUNNING dG every RUNNING_DG_EVERY chunks. Two reasons, both from standing rules:
            # a spot leg that gets preempted must leave a readable partial rather than only a .nc,
            # and a progress check has to show the science ADVANCING, not merely that the process is
            # alive — a dG that is not settling is the signal to look, and a liveness ping hides it.
            if RUNNING_DG_EVERY and chunks % RUNNING_DG_EVERY == 0:
                try:
                    dg_r, ddg_r, _ = analyze(reporter)
                    update.update(dg_running_kcal=round(dg_r, 3), dg_running_mbar_se_kcal=round(ddg_r, 3))
                    _log(f"running dG = {dg_r:.3f} +/- {ddg_r:.3f} kcal/mol at iter {done}")
                except Exception as e:  # noqa: BLE001 — a partial-analysis failure must not kill the leg
                    update["dg_running_error"] = f"{type(e).__name__}: {e}"
            _commit(**update)

        _commit(status="analyzing", iterations_done=done)
        dg, ddg, extra = analyze(reporter)
        _commit(status="done", iterations_done=done, dg_kcal=dg, dg_mbar_se_kcal=ddg,
                analysis=extra, gpu_hours=round((time.time() - t0) / 3600.0, 3))
        _log(f"LEG DONE {leg_id}: dG = {dg:.3f} +/- {ddg:.3f} kcal/mol "
             f"({record['gpu_hours']:.2f} GPU-h)")
    except Exception as e:  # noqa: BLE001 — the partial record IS the deliverable on failure
        salvage = {}
        # Try once to reduce whatever landed on disk. A crashed or preempted leg with 900 usable
        # iterations is worth more than a bare traceback, and the standing rule is that the partial
        # checkpoint is the deliverable. Guarded: if the failure WAS the sampling (a NaN), this
        # reduction will fail too, and that failure is recorded rather than raised.
        try:
            reporter_local = locals().get("reporter")
            if reporter_local is not None:
                dg_p, ddg_p, _ = analyze(reporter_local)
                salvage = {"dg_partial_kcal": round(dg_p, 3), "dg_partial_mbar_se_kcal": round(ddg_p, 3),
                           "partial_note": ("reduced from the iterations completed before the failure — "
                                            "NOT a converged leg result, and not usable in a wedge")}
        except Exception as e2:  # noqa: BLE001
            salvage = {"dg_partial_error": f"{type(e2).__name__}: {e2}"}
        _commit(status="failed", error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc()[-4000:],
                gpu_hours=round((time.time() - t0) / 3600.0, 3), **salvage)
        _log(f"LEG FAILED {leg_id}: {type(e).__name__}: {e}")
        raise
    return record


def _overlap_diagnostic(analyzer):
    """Adjacent-lambda overlap bottleneck for this leg.

    Delegates to `ternary_fep_convergence.overlap_matrix_bottleneck` — the SAME detector the ternary
    lane already uses and tests — rather than writing a second one that can drift from it. The
    connectivity requirement is the same physics in both lanes: one near-zero neighbour pair
    disconnects the thermodynamic path even when the average overlap looks fine, so a converged-
    looking dG across a broken path is exactly the failure this catches.

    A poor bottleneck here has a known remedy: more lambda windows. Y->A deletes a whole phenol ring,
    which is a large transformation for a modest window count, so this diagnostic is what tells us
    whether the default N_STATES is adequate instead of us guessing at it.
    """
    try:
        import ternary_fep_convergence as cv
    except ImportError as e:
        return {"status": f"overlap gate COULD NOT RUN (missing dependency): {e}"}
    matrix = None
    for accessor in ("mbar",):
        obj = getattr(analyzer, accessor, None)
        if obj is None:
            continue
        try:
            ov = obj.compute_overlap()          # pymbar 4
            matrix = ov["matrix"] if isinstance(ov, dict) else ov
            break
        except Exception:  # noqa: BLE001 — try the next shape
            try:
                matrix = obj.computeOverlap()["matrix"]   # pymbar 3 spelling
                break
            except Exception:  # noqa: BLE001
                matrix = None
    if matrix is None:
        return {"status": "overlap matrix not exposed by this analyzer/pymbar version"}
    out = cv.overlap_matrix_bottleneck(matrix)
    out["threshold"] = getattr(cv, "OVERLAP_BOTTLENECK_MIN", None)
    out["remedy_if_disconnected"] = ("raise PROTFEP_N_STATES — a disconnected lambda path is a window-"
                                     "count problem, not a sampling-length problem")
    return out


def analyze(reporter):
    """MBAR reduction of a finished (or partial) leg -> (dG_kcal, MBAR_SE_kcal, diagnostics).

    The SE returned here is the MBAR standard error of THIS leg. It is a within-leg precision
    estimate and is NOT the number the wedge reports: `summarize_wedge` uses a between-replicate SD,
    because setup-to-setup variance dominates a mutation in a large assembly and an MBAR SE
    understates it. Both are recorded so the gap between them stays visible.
    """
    from openmmtools.multistate import MultiStateSamplerAnalyzer
    analyzer = _call_filtered(MultiStateSamplerAnalyzer, reporter)
    f_ij, df_ij = analyzer.get_free_energy()
    dg = float(f_ij[0, -1]) * KT_KCAL
    ddg = float(df_ij[0, -1]) * KT_KCAL
    diagnostics = {"kT_kcal": KT_KCAL, "units": "kcal/mol"}
    diagnostics["overlap"] = _overlap_diagnostic(analyzer)
    try:
        n_eff = analyzer.effective_length_of_trajectory if hasattr(
            analyzer, "effective_length_of_trajectory") else None
        diagnostics["n_equilibration_iterations"] = int(getattr(analyzer, "n_equilibration_iterations", 0))
        diagnostics["statistical_inefficiency"] = float(getattr(analyzer, "statistical_inefficiency", 0.0))
        if n_eff is not None:
            diagnostics["effective_trajectory_length"] = str(n_eff)
    except Exception as e:  # noqa: BLE001 — diagnostics are nice-to-have, dG is not
        diagnostics["diagnostics_error"] = f"{type(e).__name__}: {e}"
    return dg, ddg, diagnostics


# ------------------------------------------------------------------------------------------------
# Entry point (env-driven, so the Vast onstart script stays a one-liner)
# ------------------------------------------------------------------------------------------------
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Run ONE protein-mutation FEP leg (5a-KS engine)")
    ap.add_argument("--benchmark", default=os.environ.get("PROTFEP_BENCHMARK"),
                    help="benchmark name from protfep_bench.BENCHMARKS")
    ap.add_argument("--environment", default=os.environ.get("PROTFEP_ENVIRONMENT", "complex"),
                    choices=["complex", "apo"])
    ap.add_argument("--replicate", type=int, default=int(os.environ.get("PROTFEP_REPLICATE", "0")))
    ap.add_argument("--structure", default=os.environ.get("PROTFEP_STRUCTURE"),
                    help="explicit prepared PDB (bypasses benchmark staging)")
    ap.add_argument("--mutation", default=os.environ.get("PROTFEP_MUTATION"))
    ap.add_argument("--leg-id", default=os.environ.get("LEG_ID"))
    ap.add_argument("--n-states", type=int, default=None)
    ap.add_argument("--prod-iters", type=int, default=None)
    ap.add_argument("--warmup-iters", type=int, default=None)
    ap.add_argument("--in-dir", default=os.environ.get("INPUT_DIR", "/tmp/protfep_in"))
    ap.add_argument("--out-dir", default=os.environ.get("OUTPUT_DIR", "/tmp/protfep_out"))
    ap.add_argument("--no-resume", action="store_true")
    args = ap.parse_args(argv)

    structure, mutation, leg_id, meta = args.structure, args.mutation, args.leg_id, None
    if args.benchmark:
        spec = bench.leg_spec(args.benchmark, args.environment, args.replicate)
        staged = bench.stage_leg(spec, args.in_dir)
        structure = staged.get("structure")
        if not staged["report"].get("prepared"):
            raise SystemExit(f"staging produced no prepared structure "
                             f"({staged['report'].get('pdbfixer_skipped')}) — the MD stack is missing")
        structure = staged["report"]["prepared"]
        mutation = spec["mutation"]
        leg_id = leg_id or spec["leg_id"]
        meta = {"benchmark": args.benchmark, "cycle_role": spec["cycle_role"],
                "environment": spec["environment"], "replicate": spec["replicate"],
                "staging": staged["report"]}
    if not (structure and mutation and leg_id):
        raise SystemExit("need --benchmark, or all of --structure/--mutation/--leg-id")

    run_leg(leg_id, structure, mutation, args.out_dir, n_states=args.n_states,
            prod_iters=args.prod_iters, warmup_iters=args.warmup_iters,
            resume=not args.no_resume, meta=meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
