#!/usr/bin/env python3
"""GPU driver for ONE alchemical protein point-mutation leg (the 5a-KS wedge engine's execution layer).

`nr4a3_protein_fep.py` is the engine's PURE layer — mutation parsing, the charge-consistency and
net-charge guards, wedge arithmetic, and the benchmark plan. It deliberately runs no MD, so its
guards stay testable on CPU. This module is the other half: the thing that actually builds a perses
hybrid topology, samples it with replica exchange, reduces it with MBAR, and writes a leg JSON.

Until this file existed, STRATEGY.md's "engine BUILT 2026-07-24" was true only of the planning
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
N_STATES = int(os.environ.get("PROTFEP_N_STATES", "11"))
TIMESTEP_FS = float(os.environ.get("PROTFEP_TIMESTEP_FS", "2.0"))
WARMUP_TIMESTEP_FS = float(os.environ.get("PROTFEP_WARMUP_TIMESTEP_FS", "1.0"))
ITER_PS = float(os.environ.get("PROTFEP_ITER_PS", "2.5"))       # ps of MD per replica-exchange iteration
WARMUP_ITERS = int(os.environ.get("PROTFEP_WARMUP_ITERS", "100"))    # 0.25 ns at 2.5 ps/iter
PROD_ITERS = int(os.environ.get("PROTFEP_PROD_ITERS", "2000"))       # 5 ns at 2.5 ps/iter
MIN_STEPS = int(os.environ.get("PROTFEP_MIN_STEPS", "5000"))
CHUNK_ITERS = int(os.environ.get("PROTFEP_CHUNK_ITERS", "50"))       # commit/checkpoint cadence
CHECKPOINT_INTERVAL = int(os.environ.get("PROTFEP_CHECKPOINT_INTERVAL", "50"))
TEMPERATURE_K = float(os.environ.get("PROTFEP_TEMPERATURE_K", str(md_settings.TEMPERATURE_K)))
KT_KCAL = 0.0019872041 * TEMPERATURE_K   # kB*T in kcal/mol; MBAR returns free energies in kT


def _log(msg):
    print(f"[protfep] {time.strftime('%H:%M:%S')} {msg}", flush=True)


def _call_filtered(fn, *args, **kwargs):
    """Call `fn` passing only the kwargs its signature actually accepts; log what was dropped.

    A version skew in perses/openmmtools should surface as a named, logged omission — not as a
    TypeError discovered after the GPU has been billing for an hour.
    """
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return fn(*args, **kwargs)
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return fn(*args, **kwargs)
    accepted = set(sig.parameters)
    kept = {k: v for k, v in kwargs.items() if k in accepted}
    dropped = sorted(set(kwargs) - set(kept))
    if dropped:
        _log(f"NOTE {getattr(fn, '__name__', fn)} does not accept {dropped} in this version — dropped")
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
def build_htf(structure_path, mutation_spec, charge_method=None, ionic_strength_M=None):
    """Build the perses hybrid topology for one protein point mutation in one environment.

    BOTH of this lane's legs use perses' `get_apo_htf()`. That is not a bug: in perses, "apo" means
    "no SMALL-MOLECULE ligand", and there is no small molecule anywhere in a protein-protein
    benchmark. The bound-vs-free distinction lives entirely in how many protein chains the staged
    PDB contains, which is `protfep_bench.stage_leg`'s job.
    """
    from openmm import app, unit
    from perses.app.relative_point_mutation_setup import PointMutationExecutor

    m = pf.classify_mutation(mutation_spec)
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
                 "ionic_strength_M": ionic}


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
        htf, build_meta = build_htf(structure_path, mutation_spec, charge_method=charge_method)
        record["charge_method"] = build_meta["charge_method"]
        record["n_particles"] = build_meta["n_particles"]
        _commit(status="built")

        sampler, reporter, done = _open_sampler(htf, storage, n_states, resume)
        if done == 0:
            _commit(status="warmup")
            _warmup(sampler, warmup_iters)
        _commit(status="production", iterations_done=done)

        while done < prod_iters:
            chunk = min(CHUNK_ITERS, prod_iters - done)
            it0 = time.time()
            sampler.extend(chunk)
            done = int(getattr(sampler, "iteration", done + chunk))
            rate = (time.time() - it0) / max(1, chunk)
            _log(f"iter {done}/{prod_iters} ({rate:.1f} s/iter, {(prod_iters-done)*rate/3600:.1f} h left)")
            _commit(status="production", iterations_done=done, s_per_iter=round(rate, 2),
                    gpu_hours_so_far=round((time.time() - t0) / 3600.0, 3))

        _commit(status="analyzing", iterations_done=done)
        dg, ddg, extra = analyze(reporter)
        _commit(status="done", iterations_done=done, dg_kcal=dg, dg_mbar_se_kcal=ddg,
                analysis=extra, gpu_hours=round((time.time() - t0) / 3600.0, 3))
        _log(f"LEG DONE {leg_id}: dG = {dg:.3f} +/- {ddg:.3f} kcal/mol "
             f"({record['gpu_hours']:.2f} GPU-h)")
    except Exception as e:  # noqa: BLE001 — the partial record IS the deliverable on failure
        _commit(status="failed", error=f"{type(e).__name__}: {e}",
                traceback=traceback.format_exc()[-4000:],
                gpu_hours=round((time.time() - t0) / 3600.0, 3))
        _log(f"LEG FAILED {leg_id}: {type(e).__name__}: {e}")
        raise
    return record


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
