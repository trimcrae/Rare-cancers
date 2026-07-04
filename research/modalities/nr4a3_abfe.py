#!/usr/bin/env python3
"""Modern-stack ABFE (independent λ-window) — replaces Yank. See nr4a3_abfe_modern_design.md.

Each λ-window is an INDEPENDENT OpenMM simulation → per-iteration small checkpoints (spot loses ≤1 iter),
trivially parallel, and a per-iteration ΔG convergence trace via incremental MBAR. No monolithic HREX .nc.

Build state (see nr4a3_abfe_modern_design.md → "Build order"):
  1. PURE glue — λ schedule + MBAR u_kn assembly + per-window jsonl log  (unit-tested)          [done]
  2. single independent window — build→MD→reduced-potentials-at-all-λ→per-iter checkpoint/resume [done]
  3. MBAR reducer per leg + per-iteration convergence trace                                       [done]
  4. Boresch 6-DOF restraint + analytic standard-state correction + ΔG_bind leg-combination       [done]
  5. SageMaker per-window spot fan-out + pre-baked modern ECR image                               [in progress]
  6. run NR4A3/NR4A1/NR4A2 → ΔΔG                                                                   [pending]

The Boresch standard-state correction IS hand-rolled here (`boresch_standard_state_correction`, unit-tested
against a hand-computed value + monotonicity) rather than pulled from openmmtools, so the modern env stays
minimal (openmm + openmmtools + pymbar) and the formula is transparent; the whole chain (restraint + both legs
+ combination) is validated end-to-end on a known host–guest ΔG benchmark.
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


def boresch_standard_state_correction(r0_A, thetaA0_rad, thetaB0_rad,
                                      K_r, K_thetaA, K_thetaB, K_phiA, K_phiB, K_phiC,
                                      temperature_K=300.0):
    """Analytical standard-state free energy of the Boresch orientational restraint (Boresch et al. 2003,
    J Phys Chem B, eq. 32) — the correction added to the double-decoupling ΔG so the result is at the 1 M
    standard state. PURE math (no openmm) → unit-testable. Force constants: K_r in kcal/mol/Å², all angular
    K in kcal/mol/rad²; r0 in Å; angles in rad; radians treated as dimensionless (standard convention).

        ΔG° = −RT ln [ (8π²·V°·√(K_r K_θA K_θB K_φA K_φB K_φC)) / (r0²·sinθA0·sinθB0·(2πRT)³) ]

    V° = 1660.5395 Å³ (1 M). A stronger restraint (larger K, smaller r0) → more negative correction."""
    import math
    RT = 0.0019872041 * temperature_K                        # kcal/mol
    V0 = 1660.5395                                            # Å³ (standard-state volume, 1 M)
    num = 8.0 * math.pi ** 2 * V0 * math.sqrt(K_r * K_thetaA * K_thetaB * K_phiA * K_phiB * K_phiC)
    den = (r0_A ** 2) * math.sin(thetaA0_rad) * math.sin(thetaB0_rad) * (2.0 * math.pi * RT) ** 3
    return -RT * math.log(num / den)


def combine_legs(complex_decouple_dg, complex_decouple_se,
                 solvent_decouple_dg, solvent_decouple_se,
                 restraint_standard_state_dg):
    """Double-decoupling ΔG_bind (kcal/mol) at the 1 M standard state, from the two legs' decoupling ΔGs and
    the Boresch restraint's analytic standard-state term. Returns (dG_bind, SE). Pure arithmetic → unit-tested;
    the SIGN convention is validated end-to-end on the host–guest benchmark.

    Inputs are the leg free energies as `reduce_leg` returns them: RT·Δf[0,K-1] = ΔG(coupled → decoupled),
    positive when decoupling costs energy (favourable interactions turned off). In our independent-window
    design the Boresch restraint is held ON and IDENTICAL across ALL complex-leg windows (NOT annihilated
    along λ), so its confinement is removed here ANALYTICALLY.

    Thermodynamic cycle (each step's ΔG; `SSC` = restraint_standard_state_dg = boresch_standard_state_correction
    = −RT ln(...) < 0, the FAVOURABLE release of the non-interacting ligand from the restrained volume to V°):
        solv,coupled,free  --(+ΔG_dec_solv)-->  solv,decoupled,free  ==  gas,decoupled,free @1M
        gas,decoupled,free @1M  --(restrain: −SSC)-->  cplx,decoupled,restrained
        cplx,decoupled,restrained  --(−ΔG_dec_cplx)-->  cplx,coupled,restrained  ≈  bound
      ⇒  ΔG_bind = ΔG_dec_solv − ΔG_dec_cplx − SSC
    Adding −SSC (>0) removes the artificial stabilisation the restraint lent the complex leg (it held the
    ligand in place during decoupling), i.e. correctly makes binding WEAKER — the standard-state penalty.
    A strong binder (ΔG_dec_cplx ≫ ΔG_dec_solv) → negative ΔG_bind.

    The analytical SSC carries no sampling error, so the SE propagates from the two legs only."""
    dg = solvent_decouple_dg - complex_decouple_dg - restraint_standard_state_dg
    se = (complex_decouple_se ** 2 + solvent_decouple_se ** 2) ** 0.5
    return dg, se


def selectivity_ddg(dg_bind_target, se_target, dg_bind_offtarget, se_offtarget):
    """Selectivity ΔΔG (kcal/mol) = ΔG_bind(target) − ΔG_bind(off-target). NEGATIVE ⇒ tighter binding to the
    target (the degrader-selectivity headline: ΔG_bind(NR4A3) − ΔG_bind(NR4A1 or NR4A2)). SE adds in quadrature
    (independent per-receptor ABFE runs). Returns (ddg, se)."""
    return dg_bind_target - dg_bind_offtarget, (se_target ** 2 + se_offtarget ** 2) ** 0.5


def add_boresch_restraint(system, receptor_atoms, ligand_atoms, r0_A, thetaA0_rad, thetaB0_rad,
                          phiA0_rad, phiB0_rad, phiC0_rad,
                          K_r=20.0, K_thetaA=20.0, K_thetaB=20.0, K_phiA=20.0, K_phiB=20.0, K_phiC=20.0):
    """Add a Boresch 6-DOF orientational restraint (1 distance, 2 angles, 3 dihedrals) between 3 receptor
    anchor atoms [R2,R1,R0] and 3 ligand anchor atoms [L0,L1,L2] as a CustomCompoundBondForce. Returns the
    force. Pair with boresch_standard_state_correction() for the standard-state term. (Self-contained — does
    not depend on Yank; the energy expression is the standard Boresch form.)"""
    import openmm
    from openmm import unit
    kcal = unit.kilocalorie_per_mole
    energy = ("0.5*K_r*(distance(p3,p4)-r0)^2"
              "+0.5*K_thetaA*(angle(p2,p3,p4)-thetaA0)^2"
              "+0.5*K_thetaB*(angle(p3,p4,p5)-thetaB0)^2"
              "+0.5*K_phiA*(dphiA)^2+0.5*K_phiB*(dphiB)^2+0.5*K_phiC*(dphiC)^2;"
              "dphiA=dA-floor(dA/(2*pi)+0.5)*2*pi; dA=dihedral(p1,p2,p3,p4)-phiA0;"
              "dphiB=dB-floor(dB/(2*pi)+0.5)*2*pi; dB=dihedral(p2,p3,p4,p5)-phiB0;"
              "dphiC=dC-floor(dC/(2*pi)+0.5)*2*pi; dC=dihedral(p3,p4,p5,p6)-phiC0;"
              "pi=3.14159265358979")
    f = openmm.CustomCompoundBondForce(6, energy)
    for name, val, u in [("K_r", K_r, kcal / unit.angstrom ** 2),
                         ("K_thetaA", K_thetaA, kcal / unit.radian ** 2),
                         ("K_thetaB", K_thetaB, kcal / unit.radian ** 2),
                         ("K_phiA", K_phiA, kcal / unit.radian ** 2),
                         ("K_phiB", K_phiB, kcal / unit.radian ** 2),
                         ("K_phiC", K_phiC, kcal / unit.radian ** 2),
                         ("r0", r0_A, unit.angstrom),
                         ("thetaA0", thetaA0_rad, unit.radian), ("thetaB0", thetaB0_rad, unit.radian),
                         ("phiA0", phiA0_rad, unit.radian), ("phiB0", phiB0_rad, unit.radian),
                         ("phiC0", phiC0_rad, unit.radian)]:
        f.addGlobalParameter(name, (val * u))
    R2, R1, R0 = receptor_atoms[-3], receptor_atoms[-2], receptor_atoms[-1]
    L0, L1, L2 = ligand_atoms[0], ligand_atoms[1], ligand_atoms[2]
    f.addBond([int(R2), int(R1), int(R0), int(L0), int(L1), int(L2)], [])
    system.addForce(f)
    return f


def reduce_leg(out_dir, schedule=None, temperature_K=300.0, per_iteration=False):
    """Read all windows' per-iteration jsonl → MBAR → leg ΔG (kcal/mol) + SE. With per_iteration=True, return
    the CONVERGENCE TRACE [(n_samples_per_window, dg, se)] by re-running MBAR on the first-n samples for
    increasing n — the every-iteration ΔG curve, straight from the small synced logs (no monolithic .nc)."""
    import numpy as np
    from pymbar import MBAR
    schedule = schedule or lambda_schedule()
    K = len(schedule)
    RT = (0.0019872041 * temperature_K)                       # kcal/mol per kT
    we = [[] for _ in range(K)]
    for k in range(K):
        p = os.path.join(out_dir, f"window_{k:02d}.jsonl")
        if not os.path.exists(p):
            continue
        rows = sorted((json.loads(l) for l in open(p) if l.strip()), key=lambda r: r["iter"])
        we[k] = [r["u"] for r in rows]

    def _dg(trunc):
        wk = [(w[:trunc] if trunc else w) for w in we]
        if any(len(w) == 0 for w in wk):                      # MBAR needs samples from every state
            return None
        u_kn, N_k = assemble_ukn(wk, n_states=K)
        res = MBAR(np.array(u_kn), np.array(N_k)).compute_free_energy_differences()
        return RT * float(res["Delta_f"][0, K - 1]), RT * float(res["dDelta_f"][0, K - 1])

    if not per_iteration:
        return _dg(None)
    trace, maxlen = [], max((len(w) for w in we), default=0)
    for n in range(2, maxlen + 1):
        r = _dg(n)
        if r:
            trace.append((n, r[0], r[1]))
    return trace


def smoke(out_dir=None, n_iter=5, steps_per_iter=20):
    """Tiny CPU smoke of the single-window machinery on an openmmtools testsystem (alanine dipeptide in vacuum,
    the sidechain as the 'alchemical' region). Proves build→MD→reduced-potentials→checkpoint→resume→log without
    any GPU or real receptor. Not a physically meaningful ΔG — a machinery test."""
    import tempfile
    from openmmtools import testsystems
    out_dir = out_dir or tempfile.mkdtemp()
    ts = testsystems.AlanineDipeptideVacuum()
    alch = list(range(0, 5))                              # first few atoms as the alchemical region
    sched = lambda_schedule()
    for w in range(len(sched)):                           # run every window (independent) → MBAR needs all states
        run_window(ts.system, ts.positions, alch, window_index=w, out_dir=out_dir,
                   n_iter=n_iter, steps_per_iter=steps_per_iter, platform_name="CPU")
    # exercise RESUME on one window: re-run → should continue from its checkpoint (more iters logged)
    run_window(ts.system, ts.positions, alch, window_index=3, out_dir=out_dir,
               n_iter=n_iter + 3, steps_per_iter=steps_per_iter, platform_name="CPU", resume=True)
    assert _last_logged_iter(out_dir, 3) == n_iter + 2, "resume did not extend the window"
    # step 3: MBAR reduce → leg ΔG + per-iteration convergence trace (the every-iteration monitoring, e2e)
    dg, se = reduce_leg(out_dir)
    trace = reduce_leg(out_dir, per_iteration=True)
    # step 4: validate the Boresch restraint builds + is physical (0 at reference geom, +ve when displaced)
    r_dg = _check_boresch_restraint()
    print(f"SMOKE_OK all {len(sched)} windows ran; checkpoint+resume OK; MBAR leg ΔG = {dg:.3f} ± {se:.3f} "
          f"kcal/mol; convergence trace has {len(trace)} points (per-iteration); Boresch restraint OK "
          f"(standard-state ΔG° = {r_dg:.3f} kcal/mol). dir {out_dir}")
    return dg


def _check_boresch_restraint():
    """Build a minimal 6-particle system, add the Boresch restraint at a chosen reference geometry, and verify
    the restraint energy is ~0 there and strictly positive when the ligand is displaced. Returns the analytic
    standard-state correction (also asserted finite). Physics check for build-step 4 — CPU, no MD."""
    import math
    import openmm
    from openmm import unit
    # 6 particles: receptor anchors R2,R1,R0 (0,1,2) then ligand anchors L0,L1,L2 (3,4,5).
    system = openmm.System()
    for _ in range(6):
        system.addParticle(12.0 * unit.amu)
    # A geometry with r0=5 Å, both anchor angles 90°, dihedrals 0 — coordinates (nm) chosen to realise it.
    pos = [openmm.Vec3(-0.2, 0.1, 0.0), openmm.Vec3(-0.1, 0.1, 0.0), openmm.Vec3(0.0, 0.0, 0.0),
           openmm.Vec3(0.5, 0.0, 0.0), openmm.Vec3(0.5, 0.1, 0.0), openmm.Vec3(0.5, 0.1, 0.1)]
    import math as _m
    r0 = _m.sqrt((0.5) ** 2) * 10.0                          # |L0-R0| in Å = 5.0
    thetaA = _angle(pos[1], pos[2], pos[3]); thetaB = _angle(pos[2], pos[3], pos[4])
    phiA = _dihedral(pos[0], pos[1], pos[2], pos[3]); phiB = _dihedral(pos[1], pos[2], pos[3], pos[4])
    phiC = _dihedral(pos[2], pos[3], pos[4], pos[5])
    add_boresch_restraint(system, receptor_atoms=[0, 1, 2], ligand_atoms=[3, 4, 5],
                          r0_A=r0, thetaA0_rad=thetaA, thetaB0_rad=thetaB,
                          phiA0_rad=phiA, phiB0_rad=phiB, phiC0_rad=phiC)
    integ = openmm.VerletIntegrator(1.0 * unit.femtosecond)
    ctx = openmm.Context(system, integ, openmm.Platform.getPlatformByName("CPU"))
    ctx.setPositions(pos)
    e0 = ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilocalorie_per_mole)
    assert abs(e0) < 1e-3, f"restraint energy not ~0 at reference geometry: {e0}"
    disp = list(pos); disp[3] = openmm.Vec3(0.8, 0.0, 0.0)   # pull ligand anchor L0 away → stretch r
    ctx.setPositions(disp)
    e1 = ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilocalorie_per_mole)
    assert e1 > 0.5, f"restraint did not penalise displacement: {e1}"
    ssc = boresch_standard_state_correction(r0, thetaA, thetaB, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0)
    assert math.isfinite(ssc), ssc
    return ssc


def _angle(a, b, c):
    import math
    v1 = (a.x - b.x, a.y - b.y, a.z - b.z); v2 = (c.x - b.x, c.y - b.y, c.z - b.z)
    dot = sum(i * j for i, j in zip(v1, v2))
    n1 = math.sqrt(sum(i * i for i in v1)); n2 = math.sqrt(sum(i * i for i in v2))
    return math.acos(max(-1.0, min(1.0, dot / (n1 * n2))))


def _dihedral(a, b, c, d):
    import math
    b0 = (a.x - b.x, a.y - b.y, a.z - b.z); b1 = (c.x - b.x, c.y - b.y, c.z - b.z)
    b2 = (d.x - c.x, d.y - c.y, d.z - c.z)
    def cross(u, v):
        return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    def norm(u):
        n = math.sqrt(sum(i * i for i in u)); return (u[0] / n, u[1] / n, u[2] / n)
    b1n = norm(b1)
    v = [b0[i] - sum(b0[j] * b1n[j] for j in range(3)) * b1n[i] for i in range(3)]
    w = [b2[i] - sum(b2[j] * b1n[j] for j in range(3)) * b1n[i] for i in range(3)]
    x = sum(v[i] * w[i] for i in range(3))
    y = sum(cross(b1n, v)[i] * w[i] for i in range(3))
    return math.atan2(y, x)


if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        smoke()
    else:
        print(f"[abfe] modern independent-window ABFE — {N_WINDOWS} windows/leg. `--smoke` runs the CPU machinery test.")
