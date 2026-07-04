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


# ---- physics layer (build-steps 2–4; STUBS) -------------------------------------------------------------
def build_alchemical_system(*args, **kwargs):  # noqa: D401
    """TODO(step 2/4): openmmtools AbsoluteAlchemicalFactory → alchemical System for one leg; complex leg adds
    openmmtools restraints.Boresch (+ .get_standard_state_correction()). Compose tested primitives; own glue."""
    raise NotImplementedError("physics layer — see nr4a3_abfe_modern_design.md build order")


def run_window(*args, **kwargs):
    """TODO(step 2): run ONE independent λ-window: minimize → equilibrate → per-iteration MD, checkpointing the
    OpenMM State to S3 each iteration and logging reduced potentials at all λ (append_reduced_potentials)."""
    raise NotImplementedError("physics layer — see nr4a3_abfe_modern_design.md build order")


def reduce_leg(*args, **kwargs):
    """TODO(step 3): pull all windows' jsonl → assemble_ukn → pymbar.MBAR (incremental for the per-iteration
    convergence trace) → per-leg ΔG + SE."""
    raise NotImplementedError("physics layer — see nr4a3_abfe_modern_design.md build order")


if __name__ == "__main__":
    print(f"[abfe] modern independent-window ABFE scaffold — {N_WINDOWS} windows/leg. Physics stubbed; see "
          f"nr4a3_abfe_modern_design.md.")
