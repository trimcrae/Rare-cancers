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


_PLATFORM_CACHE = {}


def _select_platform(preferred="CUDA", allow_cpu_fallback=False):
    """Return the first WORKING OpenMM platform, validated by a tiny single-particle energy eval that forces
    kernel/module load. `getPlatformByName` only checks REGISTRATION — the conda-forge OpenMM CUDA build is
    compiled against a newer CUDA than the g5 driver supports, so CUDA registers yet fails at module load with
    CUDA_ERROR_UNSUPPORTED_PTX_VERSION. So try preferred → CUDA → OpenCL (GPU, runtime-compiled, no PTX issue)
    and pick the first that actually runs (same approach as mmgbsa_energy._platform; needs the OpenCL vendor ICD
    written by entry_abfe.py / the image). CPU only if explicitly the preferred or allow_cpu_fallback=True —
    never a silent GPU→CPU fallback."""
    import openmm
    from openmm import unit
    if preferred in _PLATFORM_CACHE:
        return _PLATFORM_CACHE[preferred]
    order = [preferred] + [p for p in ("CUDA", "OpenCL") if p != preferred]
    if preferred == "CPU" or allow_cpu_fallback:
        order.append("CPU")
    last = None
    for name in order:
        try:
            plat = openmm.Platform.getPlatformByName(name)
            s = openmm.System(); s.addParticle(1.0)
            integ = openmm.VerletIntegrator(1.0 * unit.femtoseconds)
            ctx = openmm.Context(s, integ, plat)
            ctx.setPositions([openmm.Vec3(0, 0, 0)] * unit.nanometer)
            ctx.getState(getEnergy=True).getPotentialEnergy()          # forces kernel load → catches bad PTX
            del ctx, integ
            _PLATFORM_CACHE[preferred] = plat
            print(f"[abfe] OpenMM platform: {name}", flush=True)
            return plat
        except Exception as e:  # noqa: BLE001 — registered but unusable; try the next
            print(f"[abfe] platform {name} unavailable: {str(e)[:90]}", flush=True)
            last = e
    raise RuntimeError(f"no working OpenMM platform (tried {order}); last error: {last}")


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
    context = openmm.Context(alch_system, integrator, _select_platform(platform_name))
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


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _nrm(a):
    return _dot(a, a) ** 0.5


def _cross(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def _ang3(a, b, c):
    """Angle a-b-c (rad) from 3 coordinate tuples."""
    import math
    v1, v2 = _sub(a, b), _sub(c, b)
    return math.acos(max(-1.0, min(1.0, _dot(v1, v2) / (_nrm(v1) * _nrm(v2)))))


def _dih4(a, b, c, d):
    """Dihedral a-b-c-d (rad) from 4 coordinate tuples."""
    import math
    b0, b1, b2 = _sub(a, b), _sub(c, b), _sub(d, c)
    n = _nrm(b1)
    b1n = (b1[0] / n, b1[1] / n, b1[2] / n)
    v = tuple(b0[i] - _dot(b0, b1n) * b1n[i] for i in range(3))
    w = tuple(b2[i] - _dot(b2, b1n) * b1n[i] for i in range(3))
    return math.atan2(_dot(_cross(b1n, v), w), _dot(v, w))


def select_boresch_anchors(coords_nm, ligand_atoms, receptor_atoms,
                           r_min_nm=0.3, r_max_nm=0.8, ang_lo_deg=30.0, ang_hi_deg=150.0):
    """Pick 3 ligand + 3 receptor anchor atoms and the reference geometry for a WELL-DEFINED Boresch restraint,
    from a pose's coordinates (nm). Returns a dict:
        {receptor_anchors:[R2,R1,R0], ligand_anchors:[L0,L1,L2],
         r0_A, thetaA0_rad, thetaB0_rad, phiA0_rad, phiB0_rad, phiC0_rad}
    matching add_boresch_restraint's bond order [R2,R1,R0,L0,L1,L2] (distance R0–L0; angles R1-R0-L0 &
    R0-L0-L1; dihedrals R2-R1-R0-L0, R1-R0-L0-L1, R0-L0-L1-L2).

    Selection (pragmatic, standard heuristics): ligand L0 = atom nearest the ligand centroid; L1 = ligand atom
    farthest from L0; L2 = ligand atom maximising distance off the L0–L1 line (non-collinear). Receptor R0 =
    atom nearest L0 within [r_min,r_max] nm (avoids a degenerate r0≈0 and keeps the anchor pocket-local); R1,R2
    chosen greedily for separation while keeping BOTH new angles (thetaA, and R2-R1-R0) inside [ang_lo,ang_hi]°
    so no angle sits near the 0/π sin-singularity that makes the standard-state correction blow up. Raises
    ValueError if no non-degenerate set exists (caller should widen the receptor atom pool)."""
    import math
    ang_lo, ang_hi = math.radians(ang_lo_deg), math.radians(ang_hi_deg)
    c = coords_nm

    def _far(cands, ref):
        return sorted(cands, key=lambda a: -_nrm(_sub(c[a], c[ref])))

    def _ok(a, b, d):                                        # angle a-b-d inside the safe window
        return ang_lo <= _ang3(c[a], c[b], c[d]) <= ang_hi

    lig = list(ligand_atoms)
    if len(lig) < 3:
        raise ValueError("need ≥3 ligand atoms for a Boresch restraint")
    cen = tuple(sum(c[a][k] for a in lig) / len(lig) for k in range(3))
    L0 = min(lig, key=lambda a: _nrm(_sub(c[a], cen)))
    # R0: nearest receptor atom to L0 within the distance window (avoids r0≈0; keeps the anchor pocket-local).
    cand = [a for a in receptor_atoms if r_min_nm <= _nrm(_sub(c[a], c[L0])) <= r_max_nm]
    if not cand:
        raise ValueError(f"no receptor anchor within [{r_min_nm},{r_max_nm}] nm of the ligand — widen the pool")
    R0 = min(cand, key=lambda a: _nrm(_sub(c[a], c[L0])))
    # L1 (chosen AFTER R0): farthest ligand atom keeping thetaB = angle(R0,L0,L1) non-degenerate — thetaB
    # enters the SSC as sin, so R0/L0/L1 must NOT be collinear (the bug the round-trip smoke caught).
    L1 = next((a for a in _far([x for x in lig if x != L0], L0) if _ok(R0, L0, a)), None)
    if L1 is None:
        raise ValueError("no ligand L1 giving a non-degenerate thetaB — widen the ligand/receptor pools")
    # R1: farthest receptor atom keeping thetaA = angle(R1,R0,L0) non-degenerate (also enters the SSC as sin).
    R1 = next((a for a in _far([x for x in receptor_atoms if x != R0], R0) if _ok(a, R0, L0)), None)
    if R1 is None:
        raise ValueError("no receptor R1 giving a non-degenerate thetaA — widen the pool")
    # L2: farthest ligand atom off the L0–L1 line (largest perpendicular distance → phiC dihedral well-defined).
    d01 = _sub(c[L1], c[L0])
    n01 = _nrm(d01) or 1.0
    u01 = (d01[0] / n01, d01[1] / n01, d01[2] / n01)

    def _perp(a):
        v = _sub(c[a], c[L0])
        proj = _dot(v, u01)
        return _nrm(tuple(v[i] - proj * u01[i] for i in range(3)))
    L2 = max((a for a in lig if a not in (L0, L1)), key=_perp)
    # R2: farthest receptor atom keeping angle(R2,R1,R0) non-degenerate (well-defined phiA dihedral).
    R2 = next((a for a in _far([x for x in receptor_atoms if x not in (R0, R1)], R1) if _ok(a, R1, R0)), None)
    if R2 is None:
        raise ValueError("no receptor R2 giving a non-degenerate angle — widen the pool")
    return {
        "receptor_anchors": [int(R2), int(R1), int(R0)], "ligand_anchors": [int(L0), int(L1), int(L2)],
        "r0_A": _nrm(_sub(c[R0], c[L0])) * 10.0,
        "thetaA0_rad": _ang3(c[R1], c[R0], c[L0]), "thetaB0_rad": _ang3(c[R0], c[L0], c[L1]),
        "phiA0_rad": _dih4(c[R2], c[R1], c[R0], c[L0]), "phiB0_rad": _dih4(c[R1], c[R0], c[L0], c[L1]),
        "phiC0_rad": _dih4(c[R0], c[L0], c[L1], c[L2]),
    }


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


# ---- system prep (build-step 4→5 — explicit-solvent complex & solvent legs; needs openff/pdbfixer) --------
def _sysprep_imports():
    """Lazy import of the heavier prep stack (only in the ECR image, not the free CPU smoke). Mirrors the
    proven mmgbsa_energy parameterisation (amber14SB + gaff-2.11 via OpenFF) but for EXPLICIT solvent."""
    try:
        import openmm
        from openmm import app, unit
        from openmmforcefields.generators import SystemGenerator
        from openff.toolkit import Molecule
        from pdbfixer import PDBFixer
        return openmm, app, unit, SystemGenerator, Molecule, PDBFixer
    except Exception as e:  # noqa: BLE001
        raise RuntimeError("ABFE system prep needs openmm + openmmforcefields + openff-toolkit + pdbfixer "
                           f"(the modern ECR env). Import failed: {e}") from e


def _explicit_generator(offmol, app):
    """SystemGenerator for EXPLICIT-solvent ABFE: amber14SB protein + TIP3P water + gaff-2.11 ligand, PME.
    (mmgbsa uses gbn2 implicit + NoCutoff; ABFE double-decoupling needs real water + PME.)"""
    from openmmforcefields.generators import SystemGenerator
    ff_kwargs = {"constraints": app.HBonds, "removeCMMotion": False, "rigidWater": True}
    periodic_kwargs = {"nonbondedMethod": app.PME, "nonbondedCutoff": 1.0 * _explicit_generator._nm,
                       "ewaldErrorTolerance": 5e-4}
    return SystemGenerator(
        forcefields=["amber14/protein.ff14SB.xml", "amber14/tip3p.xml"],
        small_molecule_forcefield="gaff-2.11", molecules=[offmol],
        forcefield_kwargs=ff_kwargs, periodic_forcefield_kwargs=periodic_kwargs)


def prepare_leg(leg, ligand_sdf, receptor_pdb=None, padding_nm=1.2, ionic_molar=0.15,
                pose_name=None, restraint_K=20.0):
    """Build one ABFE leg's explicit-solvent OpenMM system. Returns a dict:
        {system, positions, alchemical_atoms, n_receptor_atoms, n_ligand_atoms,
         boresch (complex only): {anchors + geometry}, restraint_standard_state_dg (complex only)}.

    leg='complex' : PDBFixer'd receptor + docked ligand, solvated + neutralised (0.15 M NaCl), with a Boresch
                    restraint added (anchors auto-selected from the docked pose) + its analytic SSC. The ligand
                    (last n_lig atoms) is the alchemical region.
    leg='solvent' : ligand alone in a water box (identical across receptors → cancels in ΔΔG). No restraint.

    The system is the REFERENCE (non-alchemical) system + (complex) the Boresch force; run_window turns the
    ligand alchemical via AbsoluteAlchemicalFactory. Heavy deps are lazy-imported (ECR image only)."""
    openmm, app, unit, _SG, Molecule, PDBFixer = _sysprep_imports()
    _explicit_generator._nm = unit.nanometer
    mols = Molecule.from_file(ligand_sdf, file_format="sdf", allow_undefined_stereo=True)
    mols = mols if isinstance(mols, list) else [mols]
    offmol = next((m for m in mols if (m.name or "").strip() == pose_name), mols[0]) if pose_name else mols[0]
    sysgen = _explicit_generator(offmol, app)
    lig_top = offmol.to_topology().to_openmm()
    lig_pos = offmol.conformers[0].to_openmm()

    if leg == "solvent":
        modeller = app.Modeller(lig_top, lig_pos)
        modeller.addSolvent(sysgen.forcefield, model="tip3p", padding=padding_nm * unit.nanometer,
                            ionicStrength=ionic_molar * unit.molar, neutralize=True)
        system = sysgen.create_system(modeller.topology)
        n_lig = lig_top.getNumAtoms()
        return {"system": system, "positions": modeller.positions,
                "alchemical_atoms": list(range(n_lig)), "n_receptor_atoms": 0, "n_ligand_atoms": n_lig}

    if leg != "complex":
        raise ValueError(f"leg must be 'complex' or 'solvent', got {leg!r}")
    if not receptor_pdb:
        raise ValueError("complex leg needs receptor_pdb")
    fixer = PDBFixer(filename=receptor_pdb)
    fixer.findMissingResidues(); fixer.missingResidues = {}     # keep resolved pocket; don't model long loops
    fixer.findMissingAtoms(); fixer.addMissingAtoms(); fixer.addMissingHydrogens(7.0)
    modeller = app.Modeller(fixer.topology, fixer.positions)
    n_rec = modeller.topology.getNumAtoms()
    modeller.add(lig_top, lig_pos)                               # receptor first, ligand last
    n_lig = modeller.topology.getNumAtoms() - n_rec
    modeller.addSolvent(sysgen.forcefield, model="tip3p", padding=padding_nm * unit.nanometer,
                        ionicStrength=ionic_molar * unit.molar, neutralize=True)
    system = sysgen.create_system(modeller.topology)

    # Boresch anchors from the docked pose: ligand atoms = [n_rec, n_rec+n_lig); receptor candidates = protein
    # heavy atoms (skip H and solvent). Coordinates in nm.
    # index (c[0..2]) not attributes (.x/.y/.z): value_in_unit here yields numpy arrays, not Vec3 — both
    # support indexing, Vec3 alone supports .x. (The complex-leg shakeout on 2026-07-05 caught this.)
    pos_nm = [(c[0], c[1], c[2]) for c in modeller.positions.value_in_unit(unit.nanometer)]
    lig_atoms = list(range(n_rec, n_rec + n_lig))
    rec_heavy = [a.index for a in modeller.topology.atoms()
                 if a.index < n_rec and a.element is not None and a.element.symbol != "H"]
    sel = select_boresch_anchors(pos_nm, ligand_atoms=lig_atoms, receptor_atoms=rec_heavy)
    add_boresch_restraint(system, receptor_atoms=sel["receptor_anchors"], ligand_atoms=sel["ligand_anchors"],
                          r0_A=sel["r0_A"], thetaA0_rad=sel["thetaA0_rad"], thetaB0_rad=sel["thetaB0_rad"],
                          phiA0_rad=sel["phiA0_rad"], phiB0_rad=sel["phiB0_rad"], phiC0_rad=sel["phiC0_rad"],
                          K_r=restraint_K, K_thetaA=restraint_K, K_thetaB=restraint_K,
                          K_phiA=restraint_K, K_phiB=restraint_K, K_phiC=restraint_K)
    ssc = boresch_standard_state_correction(sel["r0_A"], sel["thetaA0_rad"], sel["thetaB0_rad"],
                                            restraint_K, restraint_K, restraint_K,
                                            restraint_K, restraint_K, restraint_K)
    return {"system": system, "positions": modeller.positions, "alchemical_atoms": lig_atoms,
            "n_receptor_atoms": n_rec, "n_ligand_atoms": n_lig, "boresch": sel,
            "restraint_standard_state_dg": ssc}


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


def run_shard(leg, ligand_sdf, out_dir, receptor_pdb=None, window_start=0, window_end=None,
              n_iter=1000, steps_per_iter=500, temperature_K=300.0, platform_name="CUDA",
              pose_name=None, padding_nm=1.2, restraint_K=20.0):
    """Prepare one leg's system once, then run its assigned λ-windows [window_start, window_end) — each an
    independent, per-iteration-checkpointed OpenMM sim (run_window). Writes a small meta.json (atom counts +,
    for the complex leg, the restraint standard-state ΔG) alongside the per-window logs so the reducer can
    combine legs without re-prepping. window_end=None → all N_WINDOWS. Returns the meta dict."""
    prep = prepare_leg(leg, ligand_sdf, receptor_pdb=receptor_pdb, pose_name=pose_name,
                       padding_nm=padding_nm, restraint_K=restraint_K)
    we = window_end if window_end is not None else N_WINDOWS
    os.makedirs(out_dir, exist_ok=True)
    meta = {"leg": leg, "n_receptor_atoms": prep["n_receptor_atoms"], "n_ligand_atoms": prep["n_ligand_atoms"],
            "temperature_K": temperature_K, "n_windows": N_WINDOWS}
    if leg == "complex":
        meta["restraint_standard_state_dg"] = prep["restraint_standard_state_dg"]
        meta["boresch"] = prep["boresch"]
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f)
    for w in range(window_start, we):
        run_window(prep["system"], prep["positions"], prep["alchemical_atoms"], window_index=w, out_dir=out_dir,
                   temperature_K=temperature_K, n_iter=n_iter, steps_per_iter=steps_per_iter,
                   platform_name=platform_name)
    return meta


def reduce_and_report(complex_dir, solvent_dir, out_json=None, temperature_K=300.0, emit_trace=False):
    """Combine the two legs into ΔG_bind: MBAR-reduce each leg → combine_legs with the complex-leg restraint
    SSC (read from complex_dir/meta.json). Returns {dg_bind, se, complex_dg, complex_se, solvent_dg,
    solvent_se, restraint_standard_state_dg}. Pure CPU (numpy+pymbar) → runs as a light step, no GPU.
    With emit_trace=True, also attaches "trace": a per-iteration ΔG_bind(n) convergence series (combining each
    leg's per-iteration MBAR estimate at matching iteration counts) for the convergence plot."""
    cdg, cse = reduce_leg(complex_dir, temperature_K=temperature_K)
    sdg, sse = reduce_leg(solvent_dir, temperature_K=temperature_K)
    meta = json.load(open(os.path.join(complex_dir, "meta.json")))
    ssc = meta["restraint_standard_state_dg"]
    dg_bind, se = combine_legs(cdg, cse, sdg, sse, ssc)
    out = {"dg_bind": dg_bind, "se": se, "complex_dg": cdg, "complex_se": cse,
           "solvent_dg": sdg, "solvent_se": sse, "restraint_standard_state_dg": ssc}
    if emit_trace:
        ctrace = reduce_leg(complex_dir, temperature_K=temperature_K, per_iteration=True)  # [(n, dg, se), ...]
        strace = reduce_leg(solvent_dir, temperature_K=temperature_K, per_iteration=True)
        sdict = {n: (dg, se) for n, dg, se in strace}
        smax = max(sdict) if sdict else None
        tr = []
        for n, cdg_n, cse_n in ctrace:
            sn = n if n in sdict else smax                          # align solvent leg; fall back to its last
            if sn is None:
                continue
            sdg_n, sse_n = sdict[sn]
            db, dbse = combine_legs(cdg_n, cse_n, sdg_n, sse_n, ssc)
            tr.append({"iter": n, "dg_bind": db, "se": dbse, "complex_dg": cdg_n, "solvent_dg": sdg_n})
        out["trace"] = tr
    if out_json:
        with open(out_json, "w") as f:
            json.dump(out, f, indent=2)
    return out


def molecule_sdf_from_smiles(smiles, name, out_path):
    """Write a 3D SDF (one conformer, ELF10/AM1-BCC-ready) for `smiles` labelled `name`, so prepare_leg can
    load it. Uses OpenFF (in the modern env). Returns out_path."""
    from openff.toolkit import Molecule
    m = Molecule.from_smiles(smiles, allow_undefined_stereo=True)
    m.name = name
    m.generate_conformers(n_conformers=1)
    m.to_file(out_path, file_format="sdf")
    return out_path


def run_hydration_validation(smiles, name, out_dir, known_dg_hyd=None, tol=1.5,
                             n_iter=1000, steps_per_iter=500, temperature_K=300.0, platform_name="CUDA",
                             padding_nm=1.2):
    """ACCURACY GATE for the decoupling+MBAR engine (design doc validation §1). Runs the SOLVENT leg for a
    small molecule and compares the hydration free energy to a KNOWN value. Hydration ΔG = −ΔG_dec (decoupling
    the molecule from water is the reverse of solvation). No restraint, no receptor → isolates the alchemical
    decoupling + MBAR from the Boresch machinery. Returns {dg_dec, se, dg_hydration, known_dg_hyd, error, pass}.
    A pass (|error| ≤ tol vs a published GAFF/TIP3P or experimental value) means the engine reproduces standard
    FEP; a large miss means a real bug (schedule, soft-core, reduced-potential, MBAR sign)."""
    import tempfile
    sdf = molecule_sdf_from_smiles(smiles, name, os.path.join(tempfile.mkdtemp(), f"{name}.sdf"))
    run_shard("solvent", sdf, out_dir, window_start=0, window_end=N_WINDOWS, n_iter=n_iter,
              steps_per_iter=steps_per_iter, temperature_K=temperature_K, platform_name=platform_name,
              pose_name=name, padding_nm=padding_nm)
    dg_dec, se = reduce_leg(out_dir, temperature_K=temperature_K)
    dg_hyd = -dg_dec
    out = {"molecule": name, "smiles": smiles, "dg_dec": dg_dec, "se": se, "dg_hydration": dg_hyd,
           "known_dg_hyd": known_dg_hyd, "n_iter": n_iter}
    if known_dg_hyd is not None:
        out["error"] = dg_hyd - known_dg_hyd
        out["pass"] = abs(out["error"]) <= tol
    with open(os.path.join(out_dir, "hydration_validation.json"), "w") as f:
        json.dump(out, f, indent=2)
    return out


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
    # A geometry with r0=5 Å — coordinates (nm) chosen to realise it. Reuse the tuple geometry helpers
    # (_ang3/_dih4) that select_boresch_anchors uses, so the restraint reference matches the selector's.
    c = [(-0.2, 0.1, 0.0), (-0.1, 0.1, 0.0), (0.0, 0.0, 0.0),
         (0.5, 0.0, 0.0), (0.5, 0.1, 0.0), (0.5, 0.1, 0.1)]
    pos = [openmm.Vec3(*p) for p in c]
    r0 = _nrm(_sub(c[3], c[2])) * 10.0                        # |L0-R0| in Å = 5.0
    thetaA = _ang3(c[1], c[2], c[3]); thetaB = _ang3(c[2], c[3], c[4])
    phiA = _dih4(c[0], c[1], c[2], c[3]); phiB = _dih4(c[1], c[2], c[3], c[4])
    phiC = _dih4(c[2], c[3], c[4], c[5])
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
    _check_anchor_selection_roundtrip()
    return ssc


def _check_anchor_selection_roundtrip():
    """End-to-end: select_boresch_anchors on a non-degenerate point cloud → build that restraint → its energy is
    ~0 at the SAME coordinates (the selector reports the pose's actual geometry as the reference)."""
    import openmm
    from openmm import unit
    # 4 ligand atoms (cluster near origin) + 5 receptor atoms (~0.5 nm away, well spread, non-collinear).
    coords = [(0.0, 0.0, 0.0), (0.15, 0.0, 0.0), (0.0, 0.15, 0.0), (0.05, 0.05, 0.12),   # ligand 0-3
              (0.50, 0.00, 0.00), (0.60, 0.30, 0.00), (0.55, -0.20, 0.20),               # receptor 4-6
              (0.70, 0.10, -0.20), (0.50, 0.25, 0.25)]                                    # receptor 7-8
    sel = select_boresch_anchors(coords, ligand_atoms=[0, 1, 2, 3], receptor_atoms=[4, 5, 6, 7, 8])
    assert sel["ligand_anchors"][0] == 0 and sel["receptor_anchors"][-1] in (4, 5, 6, 7, 8)
    system = openmm.System()
    for _ in coords:
        system.addParticle(12.0 * unit.amu)
    add_boresch_restraint(system, receptor_atoms=sel["receptor_anchors"], ligand_atoms=sel["ligand_anchors"],
                          r0_A=sel["r0_A"], thetaA0_rad=sel["thetaA0_rad"], thetaB0_rad=sel["thetaB0_rad"],
                          phiA0_rad=sel["phiA0_rad"], phiB0_rad=sel["phiB0_rad"], phiC0_rad=sel["phiC0_rad"])
    integ = openmm.VerletIntegrator(1.0 * unit.femtosecond)
    ctx = openmm.Context(system, integ, openmm.Platform.getPlatformByName("CPU"))
    ctx.setPositions([openmm.Vec3(*p) for p in coords])
    e = ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilocalorie_per_mole)
    assert abs(e) < 1e-3, f"selector→restraint round-trip energy not ~0 at the pose: {e}"


def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="modern independent-window ABFE")
    ap.add_argument("--smoke", action="store_true", help="CPU machinery test (no GPU/receptor)")
    ap.add_argument("--run-shard", action="store_true", help="prepare a leg + run its λ-windows")
    ap.add_argument("--reduce", action="store_true", help="combine complex+solvent legs → ΔG_bind json")
    ap.add_argument("--validate-hydration", action="store_true", help="hydration-FE accuracy gate (solvent leg)")
    ap.add_argument("--smiles", default=None)
    ap.add_argument("--mol-name", default="mol")
    ap.add_argument("--known-dg", type=float, default=None)
    ap.add_argument("--leg", choices=["complex", "solvent"])
    ap.add_argument("--ligand-sdf")
    ap.add_argument("--receptor-pdb", default=None)
    ap.add_argument("--pose-name", default=None)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--complex-dir", default=None)
    ap.add_argument("--solvent-dir", default=None)
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--emit-trace", action="store_true", help="attach per-iteration ΔG_bind convergence trace")
    ap.add_argument("--window-start", type=int, default=0)
    ap.add_argument("--window-end", type=int, default=None)
    ap.add_argument("--n-iter", type=int, default=1000)
    ap.add_argument("--steps-per-iter", type=int, default=500)
    ap.add_argument("--temperature-k", type=float, default=300.0)
    ap.add_argument("--platform", default="CUDA")
    a = ap.parse_args()
    if a.smoke:
        smoke(); return
    if a.validate_hydration:
        out = run_hydration_validation(a.smiles, a.mol_name, a.out_dir, known_dg_hyd=a.known_dg,
                                       n_iter=a.n_iter, steps_per_iter=a.steps_per_iter,
                                       temperature_K=a.temperature_k, platform_name=a.platform)
        verdict = ("PASS" if out.get("pass") else "CHECK") if a.known_dg is not None else "no-ref"
        print(f"[abfe] HYDRATION {a.mol_name}: ΔG_hyd = {out['dg_hydration']:.2f} ± {out['se']:.2f} kcal/mol "
              f"(known {a.known_dg}, error {out.get('error')}, {verdict})")
        return
    if a.run_shard:
        meta = run_shard(a.leg, a.ligand_sdf, a.out_dir, receptor_pdb=a.receptor_pdb, pose_name=a.pose_name,
                         window_start=a.window_start, window_end=a.window_end, n_iter=a.n_iter,
                         steps_per_iter=a.steps_per_iter, temperature_K=a.temperature_k, platform_name=a.platform)
        print(f"[abfe] SHARD_DONE leg={a.leg} windows [{a.window_start},{a.window_end}) meta={meta}")
        return
    if a.reduce:
        out = reduce_and_report(a.complex_dir, a.solvent_dir, out_json=a.out_json,
                                temperature_K=a.temperature_k, emit_trace=a.emit_trace)
        if a.emit_trace:
            tr = out.get("trace", [])
            ds = tr if len(tr) <= 60 else tr[:: max(1, len(tr) // 60)]
            if tr and ds[-1] is not tr[-1]:
                ds = ds + [tr[-1]]                                  # always keep the final (converged) point
            print("[abfe] TRACE_JSON " + json.dumps([[p["iter"], round(p["dg_bind"], 3), round(p["se"], 3)]
                                                     for p in ds]))
            print(f"[abfe] TRACE points={len(tr)}")
        print(f"[abfe] DG_BIND {out['dg_bind']:.3f} ± {out['se']:.3f} kcal/mol "
              f"(complex {out['complex_dg']:.2f}±{out['complex_se']:.2f}, "
              f"solvent {out['solvent_dg']:.2f}±{out['solvent_se']:.2f}, SSC {out['restraint_standard_state_dg']:.2f})")
        return
    print(f"[abfe] modern independent-window ABFE — {N_WINDOWS} windows/leg. "
          f"Modes: --smoke | --run-shard | --reduce.")


if __name__ == "__main__":
    _cli()
