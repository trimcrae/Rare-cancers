#!/usr/bin/env python3
"""Selectivity-FEP compute for ONE shard of (receptor, leg, λ-window) units — spot-priced, resumable.

Runs inside a SageMaker managed-**spot** Training job (see nr4a3_fep_sagemaker.py). The shard (a JSON list of
units from fep_sharding) is read from $FEP_SHARD_FILE; each unit is computed independently and its per-window
reduced-potential output is written to $FEP_OUTPUT_DIR, with a checkpoint marker in $FEP_CHECKPOINT_DIR. On
(re)start — including after a spot interruption — any unit whose checkpoint already exists is SKIPPED, so a
reclaimed instance resumes from the last completed window (the checkpoint standing rule, spot-native).

TWO modes:
  --smoke : trivial per-unit work (no MD) that writes a stub result + checkpoint. Validates the spot +
            checkpoint + resume + fan-in plumbing end-to-end for cents. Used by gpu-fep-aws.yml mode=smoke.
  (real)  : openmmtools absolute-alchemical λ-window sampling, reusing mmgbsa_energy's validated OpenFF/GAFF
            system build. **First-pass protocol — window count / sampling time / restraint / soft-core choices
            are defaults that need a shakeout run before the ΔΔG numbers are trusted** (like every prior
            pipeline here). GPU only.

Reduced potentials are written per unit so report_fep.py can run MBAR across windows per leg (fan-in).
"""
import glob
import json
import os
import sys
import time

SHARD_FILE = os.environ.get("FEP_SHARD_FILE", "")
# Per-unit results are written into the CHECKPOINT dir, which SageMaker syncs continuously to
# checkpoint_s3_uri. So (1) they survive a spot interruption, (2) the reducer reads them directly (no
# model.tar untar), and (3) each result file's existence IS the completion marker used for resume.
CKPT_DIR = os.environ.get("FEP_CHECKPOINT_DIR", "/opt/ml/checkpoints")
LIGAND = os.environ.get("FEP_LIGAND", "denovo_401")
# Real-protocol defaults (SHAKEOUT-CALIBRATED LATER — not trusted numbers yet):
PROD_PS = float(os.environ.get("FEP_PROD_PS", "1000"))       # production per window (ps)
EQUIL_PS = float(os.environ.get("FEP_EQUIL_PS", "200"))      # equilibration per window (ps)
PILOT_PS = float(os.environ.get("FEP_PILOT_PS", "100"))      # short PILOT per window (ps) → early-stop signal


def _phase_of(unit_id):
    """Return the phase ('pilot'|'prod') of an existing result, or None if absent/torn."""
    p = os.path.join(CKPT_DIR, unit_id + ".json")
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p)).get("phase")
    except Exception:  # noqa: BLE001 — torn spot write
        return None


def _write(unit, payload):
    os.makedirs(CKPT_DIR, exist_ok=True)
    rec = {**unit, **payload}
    tmp = os.path.join(CKPT_DIR, unit["id"] + ".json.tmp")
    json.dump(rec, open(tmp, "w"))
    os.replace(tmp, os.path.join(CKPT_DIR, unit["id"] + ".json"))   # atomic: result file == completion marker
    print(f"  [fep] wrote {unit['id']}", flush=True)


def _smoke_per_residue(receptor):
    """Synthetic per-residue ligand-interaction map for the smoke path (lets the monitor's stop-gating +
    attribution be tested end-to-end without MD). NR4A3 stabilized more at handle 410; residue 600 favours NR4A1."""
    base = {406: -1.0, 410: -3.0, 484: -2.0, 531: -1.5, 600: -0.5}
    if receptor == "nr4a1":
        base = {406: -0.9, 410: -0.6, 484: -1.8, 531: -1.4, 600: -3.0}
    elif receptor == "nr4a2":
        base = {406: -1.0, 410: -2.8, 484: -2.1, 531: -1.5, 600: -0.4}
    return {str(k): v for k, v in base.items()}


def run_smoke(unit, phase="prod"):
    """Trivial, deterministic per-unit stub — proves orchestration/spot/checkpoint/resume without MD."""
    lam = unit["lambda"]
    u_self = 10.0 * lam
    payload = {"mode": "smoke", "phase": phase, "reduced_potential_self": round(u_self, 4),
               "u_neighbors": {"prev": round(10.0 * max(lam - 0.09, 0), 4),
                               "next": round(10.0 * min(lam + 0.09, 1), 4)},
               "_t": 0.0}
    # coupled endpoint of the complex leg carries the per-residue "why" map (see run_real)
    if unit["leg"] == "complex" and unit["window"] == 0:
        payload["per_residue"] = _smoke_per_residue(unit["receptor"])
    _write(unit, payload)


def run_real(unit, phase="prod"):
    """openmmtools absolute-alchemical sampling for one (receptor, leg, window). FIRST-PASS PROTOCOL.
    phase='pilot' runs a short PILOT_PS pass (fast early-stop signal); 'prod' runs the full PROD_PS."""
    t0 = time.time()
    prod_ps = PILOT_PS if phase == "pilot" else PROD_PS
    import numpy as np
    import mmgbsa_energy as mm            # reuse the validated OpenFF/GAFF system build
    try:
        import openmm
        from openmm import unit as ou
        from openmmtools import alchemy, states
    except Exception as e:  # noqa: BLE001
        sys.exit(f"[fep] real mode needs openmm + openmmtools (+ pymbar for reduce): {e}")

    receptor = unit["receptor"]; leg = unit["leg"]; lam = unit["lambda"]
    # --- build the (solvated) system: complex leg = receptor+ligand; solvent leg = ligand only ---
    #   Reuse mmgbsa_energy: prepare_receptor + _generator build an OpenFF/GAFF system for these exact
    #   receptors/ligand. The ligand offmol is loaded from the docked pose SDF for the receptor.
    offmol = mm.load_poses(os.path.join(os.environ["FEP_POSE_DIR"], f"docked_{receptor}.sdf"))[LIGAND]
    if leg == "complex":
        rec_top, rec_pos = mm.prepare_receptor(os.path.join(os.environ["FEP_RECEPTOR_DIR"], f"{receptor}-opened.pdb"))
        system, topology, positions, lig_atoms = mm.build_complex_for_alchemy(rec_top, rec_pos, offmol)
        restraint_corr = mm.boresch_restraint_and_correction(system, topology, positions, lig_atoms)
    else:
        system, topology, positions, lig_atoms = mm.build_ligand_in_solvent(offmol)
        restraint_corr = 0.0

    # --- alchemically soft-core the ligand; map linear window λ -> (elec, sterics) standard schedule ---
    factory = alchemy.AbsoluteAlchemicalFactory(consistent_exceptions=False)
    region = alchemy.AlchemicalRegion(alchemical_atoms=lig_atoms)
    alch_system = factory.create_alchemical_system(system, region)
    alch_state = alchemy.AlchemicalState.from_system(alch_system)
    # electrostatics off over λ 0->0.5, then sterics off over 0.5->1 (decoupling; interactions ON at λ=0)
    alch_state.lambda_electrostatics = max(0.0, 1.0 - 2.0 * lam)
    alch_state.lambda_sterics = min(1.0, max(0.0, 2.0 - 2.0 * lam))

    integrator = openmm.LangevinMiddleIntegrator(300 * ou.kelvin, 1.0 / ou.picosecond, 2.0 * ou.femtosecond)
    ctx = openmm.Context(alch_system, integrator, mm._platform(openmm, ou)[0])
    ctx.setPositions(positions)
    openmm.LocalEnergyMinimizer.minimize(ctx, maxIterations=500)
    ctx.setVelocitiesToTemperature(300 * ou.kelvin)
    integrator.step(int(EQUIL_PS / 0.002))
    # production: collect this state's reduced potential + reduced potentials at neighbour λ (for BAR/MBAR)
    n_samples = 100
    step_per = max(1, int(prod_ps / 0.002 / n_samples))
    kT = (ou.MOLAR_GAS_CONSTANT_R * 300 * ou.kelvin)
    neighbours = {"self": lam, "prev": max(lam - 1.0 / 11, 0.0), "next": min(lam + 1.0 / 11, 1.0)}
    u = {k: [] for k in neighbours}
    frames = []                                          # positions kept for the per-residue "why" map
    want_decomp = (leg == "complex" and unit["window"] == 0)   # coupled endpoint = the physical bound state
    for i in range(n_samples):
        integrator.step(step_per)
        for k, lv in neighbours.items():
            alch_state.lambda_electrostatics = max(0.0, 1.0 - 2.0 * lv)
            alch_state.lambda_sterics = min(1.0, max(0.0, 2.0 - 2.0 * lv))
            alch_state.apply_to_context(ctx)
            e = ctx.getState(getEnergy=True).getPotentialEnergy()
            u[k].append(float(e / kT))
        # restore sampling state
        alch_state.lambda_electrostatics = max(0.0, 1.0 - 2.0 * lam)
        alch_state.lambda_sterics = min(1.0, max(0.0, 2.0 - 2.0 * lam))
        alch_state.apply_to_context(ctx)
        if want_decomp and i % 20 == 0:                 # a few frames are plenty for a relative attribution
            frames.append(ctx.getState(getPositions=True).getPositions(asNumpy=True).value_in_unit(ou.nanometer))
    payload = {"mode": "real", "phase": phase, "restraint_corr_kJ": restraint_corr,
               "reduced_potentials": {k: [round(x, 5) for x in v] for k, v in u.items()},
               "neighbours": {k: round(v, 6) for k, v in neighbours.items()},
               "_t": round(time.time() - t0, 1)}
    if want_decomp:
        try:                                            # best-effort; a decomp failure must not kill the window
            payload["per_residue"] = _per_residue_ligand_interaction(system, topology, frames, lig_atoms)
        except Exception as e:  # noqa: BLE001
            payload["per_residue_error"] = str(e)[:200]
    _write(unit, payload)


def _per_residue_ligand_interaction(system, topology, frames, lig_atoms):
    """Per-receptor-residue ligand interaction energy (kcal/mol; more negative = more stabilizing), averaged
    over `frames` (nm coords). Direct pairwise Coulomb+LJ (Lorentz-Berthelot) using the NonbondedForce
    parameters — a decomposition APPROXIMATION for *relative* per-residue attribution (the "why" map), not an
    absolute energy. FIRST-PASS (shakeout-pending like the rest of the FEP compute)."""
    import numpy as np
    import openmm
    nb = next(f for f in system.getForces() if isinstance(f, openmm.NonbondedForce))
    q = np.zeros(system.getNumParticles()); sig = np.zeros_like(q); eps = np.zeros_like(q)
    for i in range(system.getNumParticles()):
        c, s, e = nb.getParticleParameters(i)
        q[i] = c.value_in_unit(openmm.unit.elementary_charge)
        sig[i] = s.value_in_unit(openmm.unit.nanometer)
        eps[i] = e.value_in_unit(openmm.unit.kilojoule_per_mole)
    lig = set(int(a) for a in lig_atoms)
    # map each protein atom -> (resid) using the topology residues (skip the ligand + solvent/ions)
    res_atoms = {}
    aa = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", "LEU",
          "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"}
    for res in topology.residues():
        if res.name not in aa:
            continue
        idxs = [a.index for a in res.atoms() if a.index not in lig]
        if idxs:
            res_atoms[int(res.id)] = idxs
    ONE_4PI = 138.935456  # kJ*nm/(mol*e^2)
    KJ2KCAL = 1.0 / 4.184
    ligi = sorted(lig)
    acc = {r: 0.0 for r in res_atoms}
    for pos in frames:
        pos = np.asarray(pos)
        for r, idxs in res_atoms.items():
            e_kj = 0.0
            for j in idxs:
                for i in ligi:
                    d = pos[i] - pos[j]
                    r_ij = float(np.sqrt(d @ d)) or 1e-6
                    e_kj += ONE_4PI * q[i] * q[j] / r_ij
                    s_ij = 0.5 * (sig[i] + sig[j]); e_ij = (eps[i] * eps[j]) ** 0.5
                    if e_ij > 0 and s_ij > 0:
                        sr6 = (s_ij / r_ij) ** 6
                        e_kj += 4.0 * e_ij * (sr6 * sr6 - sr6)
            acc[r] += e_kj
    n = max(len(frames), 1)
    return {str(r): round(v / n * KJ2KCAL, 3) for r, v in acc.items()}


def main():
    smoke = "--smoke" in sys.argv
    run = run_smoke if smoke else run_real
    if not SHARD_FILE or not os.path.exists(SHARD_FILE):
        sys.exit(f"[fep] FEP_SHARD_FILE not found: {SHARD_FILE}")
    units = json.load(open(SHARD_FILE))
    # PASS 1 — PILOT every window first (short), so the central monitor gets an early ΔΔG signal across ALL
    # windows fast and can StopTrainingJob the fleet before the long production burns the spot budget.
    pilot_todo = [u for u in units if _phase_of(u["id"]) is None]      # neither pilot nor prod yet
    print(f"[fep] PASS 1 pilot: {len(pilot_todo)}/{len(units)} windows (mode={'smoke' if smoke else 'real'})",
          flush=True)
    for u in pilot_todo:
        run(u, phase="pilot")
    # PASS 2 — full PRODUCTION, overwriting pilots. Resume/interruption: skip windows already at prod.
    prod_todo = [u for u in units if _phase_of(u["id"]) != "prod"]
    print(f"[fep] PASS 2 production: {len(prod_todo)}/{len(units)} windows", flush=True)
    for u in prod_todo:
        run(u, phase="prod")
    print(f"[fep] shard complete: pilots {len(pilot_todo)}, productions {len(prod_todo)}", flush=True)


if __name__ == "__main__":
    main()
