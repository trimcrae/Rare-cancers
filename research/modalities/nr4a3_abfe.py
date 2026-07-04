#!/usr/bin/env python3
"""Modern-stack ABFE (independent λ-window) — replaces Yank. See nr4a3_abfe_modern_design.md.

Each λ-window is an INDEPENDENT OpenMM simulation → per-iteration small checkpoints (spot loses ≤1 iter),
trivially parallel, and a per-iteration ΔG convergence trace via incremental MBAR. No monolithic HREX .nc.

This file (build-step 1) implements the PURE, unit-testable glue — the λ schedule and the MBAR reduced-
potential (u_kn) assembly — and STUBS the OpenMM/openmmtools physics (build-steps 2–4). The Boresch
standard-state correction is intentionally NOT hand-rolled: use openmmtools' tested
`restraints.Boresch(...).get_standard_state_correction()` in the physics layer.
"""
import json
import os

# Alchemical λ schedule for one leg: decouple ELECTROSTATICS first (fully coupled sterics), THEN STERICS with
# soft-core. Independent windows → these are absolute λ values, one simulation per entry. Complex leg adds the
# Boresch restraint fully ON at all windows (restraint handled separately, not annihilated here).
LAMBDA_ELEC =    [1.0, 0.75, 0.5, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
LAMBDA_STERICS = [1.0, 1.0,  1.0, 1.0,  1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, 0.0]
assert len(LAMBDA_ELEC) == len(LAMBDA_STERICS), "λ elec/sterics lists must be equal length"
N_WINDOWS = len(LAMBDA_ELEC)


def lambda_schedule():
    """[(elec, sterics)] per window — the alchemical states, one independent simulation each."""
    return list(zip(LAMBDA_ELEC, LAMBDA_STERICS))


def assemble_ukn(window_energies, n_states=None):
    """Assemble pymbar's reduced-potential matrix u_kn + sample counts N_k from per-window logs.

    window_energies[k] = list of samples from window k; each sample = list of reduced potentials u(x; λ_j)
    for ALL states j (length n_states). Returns (u_kn, N_k):
      u_kn : (n_states, N_total) reduced potential of every sample evaluated at every state,
      N_k  : (n_states,) number of samples drawn FROM each state k (in state order).
    Pure array assembly (no MD) → unit-testable; feeds pymbar.MBAR directly.
    """
    K = len(window_energies) if n_states is None else n_states
    N_k = [len(window_energies[k]) if k < len(window_energies) else 0 for k in range(K)]
    N_total = sum(N_k)
    u_kn = [[0.0] * N_total for _ in range(K)]
    col = 0
    for k in range(len(window_energies)):
        for sample in window_energies[k]:
            if len(sample) != K:
                raise ValueError(f"sample from window {k} has {len(sample)} energies, expected {K}")
            for j in range(K):
                u_kn[j][col] = float(sample[j])
            col += 1
    return u_kn, N_k


def append_reduced_potentials(out_dir, window_index, iteration, reduced_potentials):
    """Per-iteration log: append one sample's reduced potentials (at all λ) to a SMALL per-window jsonl that
    syncs to S3 reliably (the whole point vs Yank's monolithic .nc). One line per iteration → per-iteration
    convergence trace after MBAR."""
    os.makedirs(out_dir, exist_ok=True)
    rec = {"w": int(window_index), "iter": int(iteration), "u": [float(x) for x in reduced_potentials]}
    with open(os.path.join(out_dir, f"window_{window_index:02d}.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")


# ---- physics layer (build-step 2 — single independent window; needs openmm/openmmtools) -----------------
def build_alchemical_system(reference_system, alchemical_atoms):
    """openmmtools AbsoluteAlchemicalFactory → (alchemical_system, AlchemicalState). Composes the tested
    primitive; we only choose the region. (Complex leg will additionally add openmmtools restraints.Boresch +
    .get_standard_state_correction() in step 4.)"""
    from openmmtools.alchemy import AbsoluteAlchemicalFactory, AlchemicalRegion, AlchemicalState
    factory = AbsoluteAlchemicalFactory(consistent_exceptions=False)
    region = AlchemicalRegion(alchemical_atoms=sorted(int(a) for a in alchemical_atoms))
    alch_system = factory.create_alchemical_system(reference_system, region)
    return alch_system, AlchemicalState.from_system(alch_system)


def _last_logged_iter(out_dir, window_index):
    p = os.path.join(out_dir, f"window_{window_index:02d}.jsonl")
    if not os.path.exists(p):
        return -1
    last = -1
    for line in open(p):
        line = line.strip()
        if line:
            try:
                last = max(last, int(json.loads(line)["iter"]))
            except Exception:  # noqa: BLE001 — torn last line
                pass
    return last


def run_window(reference_system, positions, alchemical_atoms, window_index, out_dir,
               schedule=None, temperature_K=300.0, n_iter=1000, steps_per_iter=500, timestep_fs=2.0,
               platform_name="CPU", resume=True):
    """Run ONE independent λ-window. Each iteration: propagate MD at THIS window's λ, evaluate the reduced
    potential of the current sample at ALL λ-states (MBAR needs u(x;λ_j) ∀j), append to the small per-window
    jsonl, and checkpoint the OpenMM State — every iteration. Small per-window files → spot loses ≤1 iter and
    the run resumes THIS window alone. Returns the iteration reached."""
    import openmm
    from openmm import unit
    from openmmtools import integrators
    schedule = schedule or lambda_schedule()
    alch_system, alch_state = build_alchemical_system(reference_system, alchemical_atoms)
    T = temperature_K * unit.kelvin
    beta = (1.0 / (unit.MOLAR_GAS_CONSTANT_R * T)).value_in_unit(unit.mole / unit.kilojoule)  # 1/(kJ/mol)
    integrator = integrators.LangevinIntegrator(temperature=T, collision_rate=1.0 / unit.picoseconds,
                                                timestep=timestep_fs * unit.femtoseconds)
    context = openmm.Context(alch_system, integrator, openmm.Platform.getPlatformByName(platform_name))
    elec, sterics = schedule[window_index]

    def _set_lambda(le, ls):
        alch_state.lambda_electrostatics = le
        alch_state.lambda_sterics = ls
        alch_state.apply_to_context(context)

    os.makedirs(out_dir, exist_ok=True)
    ckpt = os.path.join(out_dir, f"window_{window_index:02d}.state.xml")
    start = 0
    if resume and os.path.exists(ckpt):
        context.setState(openmm.XmlSerializer.deserialize(open(ckpt).read()))
        start = _last_logged_iter(out_dir, window_index) + 1
    else:
        context.setPositions(positions)
        _set_lambda(elec, sterics)
        openmm.LocalEnergyMinimizer.minimize(context)

    for it in range(start, n_iter):
        _set_lambda(elec, sterics)                      # propagate at THIS window's state
        integrator.step(steps_per_iter)
        ured = []                                       # reduced potential of this sample at every state
        for le, ls in schedule:
            _set_lambda(le, ls)
            u = context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
            ured.append(beta * u)
        append_reduced_potentials(out_dir, window_index, it, ured)
        st = context.getState(getPositions=True, getVelocities=True)   # tiny checkpoint, every iteration
        with open(ckpt + ".tmp", "w") as f:
            f.write(openmm.XmlSerializer.serialize(st))
        os.replace(ckpt + ".tmp", ckpt)                 # atomic: never leave a torn checkpoint
    return n_iter


def smoke(out_dir=None, n_iter=5, steps_per_iter=20):
    """Tiny CPU smoke of the single-window machinery on an openmmtools testsystem (alanine dipeptide in vacuum,
    the sidechain as the 'alchemical' region). Proves build→MD→reduced-potentials→checkpoint→resume→log without
    any GPU or real receptor. Not a physically meaningful ΔG — a machinery test."""
    import tempfile
    from openmmtools import testsystems
    out_dir = out_dir or tempfile.mkdtemp()
    ts = testsystems.AlanineDipeptideVacuum()
    alch = list(range(0, 5))                              # first few atoms as the alchemical region
    run_window(ts.system, ts.positions, alch, window_index=3, out_dir=out_dir,
               n_iter=n_iter, steps_per_iter=steps_per_iter, platform_name="CPU")
    # exercise RESUME: call again, should continue from the checkpoint (no error, more iters logged)
    run_window(ts.system, ts.positions, alch, window_index=3, out_dir=out_dir,
               n_iter=n_iter + 3, steps_per_iter=steps_per_iter, platform_name="CPU", resume=True)
    last = _last_logged_iter(out_dir, 3)
    print(f"SMOKE_OK window reached iter {last} (checkpoint+resume+per-iter reduced-potential log work) in {out_dir}")
    return last


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        smoke()
    else:
        print(f"[abfe] modern independent-window ABFE — {N_WINDOWS} windows/leg. `--smoke` runs the CPU machinery test.")
