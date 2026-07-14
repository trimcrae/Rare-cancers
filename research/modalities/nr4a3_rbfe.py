#!/usr/bin/env python3
"""RBFE compute engine — denovo_401 → lo_m0_NCCO relative binding FEP via OpenFE (RelativeHybridTopologyProtocol).

Runs ONE (receptor, leg) alchemical MORPH (A→B): the complex-morph leg (protein + ligand + solvent) or the
shared solvent-morph leg (ligand + solvent). OpenFE supplies the four pieces the repo's ABFE engine lacks —
LOMAP atom-mapping, the perses hybrid topology, the relative λ schedule, and MBAR — turnkey and validated, so
we do NOT hand-roll dual-topology soft-core (the highest-risk piece; see nr4a3-degrader-next-steps.md engine
policy). No Boresch restraint / standard-state correction: both ligands share the pose, so it cancels.

Deliverable per leg: ΔG_morph(A→B) in that environment (+ uncertainty). The reducer forms
ΔΔG_bind = ΔG_complex_morph − ΔG_solvent_morph per receptor (rbfe_edges.ddg_bind), then the selectivity.

**SHAKEOUT-PENDING (standing rule): the OpenFE protocol settings + the env are first-pass; run mode=smoke on a
GPU (maps + builds the hybrid topology, no MD) then ONLY_LEGS=solvent (one real morph leg) before trusting any
number — exactly as every prior GPU pipeline here was shaken out.** Heavy deps (openfe/openmm) are imported
lazily so this file loads on a CPU box.

Env: MODE (smoke|run|reduce), RECEPTOR, LEG (complex|solvent), LIGAND_A, LIGAND_B, N_WINDOWS, N_ITER, SEED,
INPUT_DIR (mounted <r>-opened.pdb + docked_<r>.sdf), OUTPUT_DIR/CKPT_DIR.
"""
import glob
import json
import os
import sys

import rbfe_edges as rb

IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
CKPT = os.environ.get("CKPT_DIR", os.environ.get("OUTPUT_DIR", "/opt/ml/checkpoints"))
LIGAND_A = os.environ.get("LIGAND_A", rb.LIGAND_A)
LIGAND_B = os.environ.get("LIGAND_B", rb.LIGAND_B)
RECEPTOR = os.environ.get("RECEPTOR", "nr4a3")
LEG = os.environ.get("LEG", "complex")
N_WINDOWS = int(os.environ.get("N_WINDOWS", "12"))
N_ITER = int(os.environ.get("N_ITER", "1000"))
SEED = int(os.environ.get("SEED", "0"))


def _canon(m, rdkit_chem):
    """Canonical (stereo-aware) SMILES of a docked-pose mol, Hs stripped — for structural record matching."""
    try:
        return rdkit_chem.MolToSmiles(rdkit_chem.RemoveHs(rdkit_chem.Mol(m)))
    except Exception:  # noqa: BLE001
        return None


def _sdf_mol(sdf_path, name, expected_smiles, rdkit_chem):
    """Resolve the docked pose for ligand `name` from a multi-record docked SDF, robustly and WITHOUT ever
    silently substituting the wrong molecule (a wrong ligand A/B would invalidate the entire ΔΔG). The species
    dock tags the canonical/generated stereoisomer with a `_gen` suffix (e.g. requesting `denovo_401` must
    resolve to the record `denovo_401_gen`), and there are OTHER stereoisomers of the same base in the file, so
    we match on: (1) exact _Name, (2) _Name == name+'_gen', (3) exact stereo-canonical SMILES == expected. If
    none match, HARD-FAIL — never fall back to an arbitrary record."""
    want = None
    if expected_smiles:
        em = rdkit_chem.MolFromSmiles(expected_smiles)
        want = rdkit_chem.MolToSmiles(em) if em is not None else None
    recs = [m for m in rdkit_chem.SDMolSupplier(sdf_path, removeHs=False) if m is not None]
    for target in (name, f"{name}_gen"):
        for m in recs:
            if m.HasProp("_Name") and m.GetProp("_Name") == target:
                return m
    if want is not None:
        for m in recs:
            if _canon(m, rdkit_chem) == want:
                return m
    have = [m.GetProp("_Name") for m in recs if m.HasProp("_Name")]
    raise SystemExit(f"  ABORT: no record for {name} (tried name, {name}_gen, SMILES) in {sdf_path}; "
                     f"records present: {have[:20]}")


def _repair_pose(mol, expected_smiles, rdkit_chem):
    """Repair a docked pose into a clean, closed-shell RDKit mol for OpenFF/NAGL. Docked SDFs come back with
    perceived bond orders/valences that can leave RADICAL electrons (openff raises RadicalsNotSupportedError,
    which killed the charge step). Re-impose bond orders from the known SMILES template and re-add explicit Hs
    with 3D coords — the heavy-atom docked coordinates are preserved. Falls back to the raw pose if repair fails."""
    if not expected_smiles:
        return mol
    try:
        from rdkit.Chem import AllChem
        tmpl = rdkit_chem.MolFromSmiles(expected_smiles)
        if tmpl is None:
            return mol
        heavy = rdkit_chem.RemoveHs(mol)
        fixed = AllChem.AssignBondOrdersFromTemplate(tmpl, heavy)   # correct bond orders → kills radicals
        fixed = rdkit_chem.AddHs(fixed, addCoords=True)             # explicit Hs positioned from geometry
        rdkit_chem.SanitizeMol(fixed)
        if mol.HasProp("_Name"):
            fixed.SetProp("_Name", mol.GetProp("_Name"))
        return fixed
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN pose repair failed ({e}); using raw pose", flush=True)
        return mol


def _build_components(openfe, rdkit_chem):
    """Build the OpenFE ligand A/B SmallMoleculeComponents (+ receptor ProteinComponent for the complex leg),
    from the mounted docked poses. Returns (ligA, ligB, protein_or_None)."""
    # The solvent-morph leg has RECEPTOR="shared" (ligand-in-water, no protein), so its ligand structures don't
    # depend on a receptor — pull them from any real docked SDF (nr4a3). The complex leg uses its own receptor's
    # SDF. (Smoke used the nr4a3/complex defaults, so the "shared" path was first exercised by the solvent leg.)
    sdf_receptor = RECEPTOR if RECEPTOR in ("nr4a3", "nr4a1", "nr4a2") else "nr4a3"
    sdf = os.path.join(IN, "ligand", f"docked_{sdf_receptor}.sdf")
    if not os.path.exists(sdf):
        sdf = next(iter(glob.glob(os.path.join(IN, "**", f"docked_{sdf_receptor}.sdf"), recursive=True)), sdf)
    molA = _repair_pose(_sdf_mol(sdf, LIGAND_A, rb.SMILES.get(LIGAND_A), rdkit_chem),
                        rb.SMILES.get(LIGAND_A), rdkit_chem)
    molB = _repair_pose(_sdf_mol(sdf, LIGAND_B, rb.SMILES.get(LIGAND_B), rdkit_chem),
                        rb.SMILES.get(LIGAND_B), rdkit_chem)
    ligA = openfe.SmallMoleculeComponent.from_rdkit(molA)
    ligB = openfe.SmallMoleculeComponent.from_rdkit(molB)
    protein = None
    if LEG == "complex":
        pdb = os.path.join(IN, "receptor", f"{RECEPTOR}-opened.pdb")
        if not os.path.exists(pdb):
            pdb = next(iter(glob.glob(os.path.join(IN, "**", f"{RECEPTOR}-opened.pdb"), recursive=True)), pdb)
        protein = openfe.ProteinComponent.from_pdb_file(pdb)
    return ligA, ligB, protein


def _mapping(openfe, ligA, ligB):
    """LOMAP atom-map A→B (shared scaffold maps 1:1; the ortho-acetamido is the unique region).

    threed=False (2D topology MCS), NOT threed=True, for TWO reasons:
      1. CORRECTNESS — the RBFE cycle ΔΔG = ΔG_complex − ΔG_solvent is only valid if the A→B atom
         correspondence is IDENTICAL in the shared solvent leg and every complex leg. threed=True makes the
         mapping pose-dependent, so different docked poses per receptor could silently yield different maps and
         break the cycle. The 2D MCS is pose-independent → the same map everywhere.
      2. ROBUSTNESS — threed=True requires the two docked poses to be spatially CLOSE to map atoms; nr4a1's
         401 and lo_m0_NCCO poses were too far apart → empty generator → StopIteration (nr4a1 failed twice).
    For this clean congeneric append the MCS is unambiguous, so 2D gives the correct 1:1 scaffold map."""
    from openfe.setup import LomapAtomMapper

    def _suggest(element_change):
        return next(LomapAtomMapper(time=20, threed=False,
                                    element_change=element_change).suggest_mappings(ligA, ligB))

    # Prefer the STRICT map (element_change=False): correct for a pure APPEND edge (401->NCCO adds atoms of the
    # same element). But a single-point ELEMENT MUTATION (e.g. the congeneric 5-Br -> 5-NH2) has no same-element
    # map for the 5-substituent, so LOMAP returns an empty generator. Fall back to element_change=True: the
    # shared scaffold still maps 1:1 and Br<->N becomes the mutating atom. threed=False in BOTH cases, so the
    # map stays pose-independent -> the RBFE cycle (same A->B map in solvent + every complex leg) stays valid.
    for ec in (False, True):
        try:
            m = _suggest(ec)
            if ec:
                print(f"[rbfe] LOMAP: element_change=True required for {LIGAND_A}->{LIGAND_B} "
                      f"(single-point element mutation; scaffold maps 1:1, pose-independent)", flush=True)
            return m
        except StopIteration:
            continue

    # LOMAP found nothing under either setting. Emit DIAGNOSTICS (the sandbox can't run openfe, so print what
    # the engine actually built) + try Kartograf (a more permissive geometric mapper) before giving up.
    import rdkit.Chem as _C
    from rdkit.Chem import rdFMCS
    rmA, rmB = ligA.to_rdkit(), ligB.to_rdkit()
    smiA, smiB = _C.MolToSmiles(_C.RemoveHs(_C.Mol(rmA))), _C.MolToSmiles(_C.RemoveHs(_C.Mol(rmB)))
    mcs = rdFMCS.FindMCS([_C.RemoveHs(_C.Mol(rmA)), _C.RemoveHs(_C.Mol(rmB))],
                         completeRingsOnly=True, ringMatchesRingOnly=True, timeout=30)
    print(f"[rbfe] MAPPING DIAG: A={LIGAND_A} smiles={smiA} atoms={rmA.GetNumAtoms()} | "
          f"B={LIGAND_B} smiles={smiB} atoms={rmB.GetNumAtoms()} | rdFMCS n_atoms={mcs.numAtoms} "
          f"smarts={mcs.smartsString} canceled={mcs.canceled}", flush=True)
    try:
        from kartograf import KartografAtomMapper
        km = next(KartografAtomMapper().suggest_mappings(ligA, ligB))
        print(f"[rbfe] Kartograf produced a mapping for {LIGAND_A}->{LIGAND_B} "
              f"(LOMAP failed; using Kartograf)", flush=True)
        return km
    except StopIteration:
        pass
    except Exception as e:  # noqa: BLE001 — kartograf missing/other; report + fall through
        print(f"[rbfe] Kartograf unavailable/failed: {type(e).__name__}: {e}", flush=True)

    raise RuntimeError(f"NO atom mapping for {LIGAND_A}->{LIGAND_B} (receptor {RECEPTOR}) via LOMAP "
                       f"(element_change False+True) OR Kartograf; rdFMCS core={mcs.numAtoms} atoms. See "
                       f"MAPPING DIAG above — if the core is large but mappers fail, the docked-pose molecule "
                       f"is likely mis-repaired (check the SDF records / pose repair).")


_PLATFORM_NAME = None


def _working_platform_name(preferred="CUDA"):
    """First OpenMM platform that ACTUALLY runs, validated by a 1-particle energy eval that forces kernel/module
    load (registration != usable: the conda CUDA build's PTX can be too new for the g5 driver → CUDA registers
    but fails at module load with CUDA_ERROR_UNSUPPORTED_PTX_VERSION). Try preferred → CUDA → OpenCL; return the
    NAME string (OpenFE's engine_settings.compute_platform wants a string). Mirrors nr4a3_abfe._select_platform.
    Cached so the real run and the DAG build agree."""
    global _PLATFORM_NAME
    if _PLATFORM_NAME:
        return _PLATFORM_NAME
    import openmm
    from openmm import unit as ou
    for name in [preferred] + [p for p in ("CUDA", "OpenCL") if p != preferred]:
        try:
            plat = openmm.Platform.getPlatformByName(name)
            s = openmm.System(); s.addParticle(1.0)
            integ = openmm.VerletIntegrator(1.0 * ou.femtoseconds)
            ctx = openmm.Context(s, integ, plat)
            ctx.setPositions([openmm.Vec3(0, 0, 0)] * ou.nanometer)
            ctx.getState(getEnergy=True).getPotentialEnergy()          # forces kernel load → catches bad PTX
            del ctx, integ
            print(f"[rbfe] OpenMM platform: {name}", flush=True)
            _PLATFORM_NAME = name
            return name
        except Exception as e:  # noqa: BLE001 — registered but unusable; try the next
            print(f"[rbfe] platform {name} unavailable: {str(e)[:140]}", flush=True)
    print("[rbfe] WARN no GPU platform validated; using OpenCL string", flush=True)
    _PLATFORM_NAME = "OpenCL"
    return _PLATFORM_NAME


def _protocol(openfe):
    from openfe.protocols.openmm_rfe import RelativeHybridTopologyProtocol
    s = RelativeHybridTopologyProtocol.default_settings()
    # first-pass settings (SHAKEOUT-PENDING): each knob guarded independently so a version-specific attribute
    # can't block the rest of the build, and so smoke surfaces the exact offender.
    # SINGLE replicate (trimcrae 2026-07-06): relative FEP is low-variance for a congeneric pair, so one repeat
    # with MBAR/bootstrap error is the field standard for a single edge; escalate to 3 (replicate-SD) ONLY if
    # this comes back marginal. protocol_repeats=3 would silently triple GPU cost/wall and blow past MAX_RUN.
    try:
        s.protocol_repeats = 1
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN protocol_repeats ({e})", flush=True)
    # OpenFE REQUIRES n_replicas == number of lambda windows. Set the lambda-window count FIRST, then match
    # n_replicas; if the attribute differs by openfe version, leave BOTH at the internally-consistent default
    # (smoke #2 failed because n_replicas=12 didn't match the default lambda_settings.lambda_windows=11).
    try:
        s.lambda_settings.lambda_windows = N_WINDOWS
        s.simulation_settings.n_replicas = N_WINDOWS
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN could not set windows to {N_WINDOWS} ({e}); using OpenFE default", flush=True)
    # MD lengths (real run only; smoke does no MD). MUST be openff.units Quantities, NOT strings — a string
    # "1 ns" is stored raw and blows up at RUN time when OpenFE divides length/timestep to get n_steps
    # ("TypeError: str / str"), which the DAG-build-only smoke never triggers (caught by the solvent one-leg).
    try:
        from openff.units import unit as _ou
        s.simulation_settings.equilibration_length = 1.0 * _ou.nanosecond
        s.simulation_settings.production_length = 5.0 * _ou.nanosecond
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN could not set MD lengths as Quantity ({e}); using OpenFE defaults", flush=True)
    # FIX #4 (2026-07-14 forensic — Bug B: a killed leg's simulation.nc never reached S3). Write checkpoints more
    # often so a kill/preemption loses <= one interval of trajectory instead of the whole leg, and so the
    # continuously-synced /opt/ml/checkpoints has a recent .nc to upload. Best-effort: the attribute name/type
    # varies by openfe version, so probe both setting groups and both int/Quantity forms, guarded (smoke reports
    # which one took). Default openmmtools interval can be large; 50 iters (~50 ps at 1 ps/iter) is a cheap floor.
    _ck_set = False
    for grp_name in ("simulation_settings", "output_settings"):
        grp = getattr(s, grp_name, None)
        if grp is None or not hasattr(grp, "checkpoint_interval"):
            continue
        for val in (50, None):
            try:
                if val is None:
                    from openff.units import unit as _ou3
                    grp.checkpoint_interval = 50 * _ou3.picosecond
                else:
                    grp.checkpoint_interval = val
                print(f"  [rbfe] checkpoint_interval set via {grp_name} -> {grp.checkpoint_interval}", flush=True)
                _ck_set = True
                break
            except Exception as e:  # noqa: BLE001
                last = e
        if _ck_set:
            break
    if not _ck_set:
        print("  [rbfe] WARN checkpoint_interval not set (no matching attribute); relying on openmmtools default",
              flush=True)
    try:
        # PROBE CUDA -> OpenCL (mirror nr4a3_abfe._select_platform) instead of hard-forcing OpenCL. The hybrid
        # (perses) complex system JIT-compiles pathologically slowly on OpenCL — the 2026-07-08 complex legs
        # wedged for hours right after "Adding forces" (the Context build), while the small solvent leg finished.
        # CUDA doesn't JIT giant kernels, so if it actually runs on this image (the conda build's PTX must be
        # driver-compatible) the Context build is near-instant. Falls back to OpenCL only if CUDA can't load.
        s.engine_settings.compute_platform = _working_platform_name("CUDA")
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN compute_platform ({e})", flush=True)
    # Partial charges: default am1bcc needs OpenEye or a working AmberTools antechamber (antechamber exit-1'd
    # in this env). Use openff-nagl (GNN am1bcc surrogate) — no antechamber/OpenEye. This is what killed all 4
    # real-MD legs at ligand charging (caught by the one-leg shakeout; smoke never charges).
    try:
        s.partial_charge_settings.partial_charge_method = "nagl"
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN could not set partial_charge_method=nagl ({e}); using default", flush=True)
    return RelativeHybridTopologyProtocol(s)


def _chemical_systems(openfe, ligA, ligB, protein):
    solvent = openfe.SolventComponent()
    if LEG == "complex":
        A = openfe.ChemicalSystem({"protein": protein, "ligand": ligA, "solvent": solvent})
        B = openfe.ChemicalSystem({"protein": protein, "ligand": ligB, "solvent": solvent})
    else:
        A = openfe.ChemicalSystem({"ligand": ligA, "solvent": solvent})
        B = openfe.ChemicalSystem({"ligand": ligB, "solvent": solvent})
    return A, B


def _start_watchdog(ckpt, stall_min):
    """FIX #2 (2026-07-14): the REAL hang-guard. max_run is only a distant runaway-cost backstop; this catches a
    genuinely WEDGED leg (dead/hung GPU) in minutes so it hard-exits and the run is re-dispatched, instead of
    burning the whole allocation on a stalled job (the failure the old 30 h max_run masked). A daemon thread
    watches the newest simulation*.nc mtime under the OpenFE shared dir; it ARMS only after the first .nc appears
    (so the long, .nc-less setup/charge/equilibration phase never trips it), then hard-exits if that mtime stops
    advancing for stall_min minutes. Slow-but-progressing work keeps advancing the .nc, so it is never killed."""
    import glob as _glob
    import threading
    import time

    def _newest_nc_mtime():
        ncs = _glob.glob(os.path.join(ckpt, "**", "simulation*.nc"), recursive=True)
        return max((os.path.getmtime(p) for p in ncs), default=None)

    def _loop():
        last_mtime, last_change = None, None
        while True:
            time.sleep(60)
            mt = _newest_nc_mtime()
            if mt is None:
                continue                                  # setup phase: no MD trajectory yet -> don't arm
            now = time.time()
            if last_mtime is None or mt > last_mtime + 1:
                last_mtime, last_change = mt, now
                continue
            stalled_min = (now - last_change) / 60.0
            if stalled_min >= stall_min:
                print(f"  [rbfe][watchdog] STALL: trajectory .nc unchanged {stalled_min:.0f} min "
                      f"(>= {stall_min:.0f}); GPU appears wedged -> hard-exit 42 to force re-dispatch rather than "
                      f"burn the allocation.", flush=True)
                os._exit(42)

    threading.Thread(target=_loop, daemon=True).start()
    print(f"  [rbfe][watchdog] armed: hard-exit if the trajectory .nc stalls >= {stall_min:.0f} min after MD starts",
          flush=True)


def _build_or_resume_dag(openfe, proto, A, B, mapping):
    """FIX #3 scaffold (2026-07-14 forensic — Bug A: each restart called proto.create(), minting FRESH ProtocolUnit
    UUIDs => a NEW shared_<uuid>/ dir => the job ignored all prior dirs and restarted from iteration 0; the pilot
    accumulated 7 such throwaway dirs). To make a restart CONTINUE the same unit dir (so OpenFE/openmmtools can pick
    up the existing simulation.nc), the DAG's unit identity must be STABLE across dispatches. We persist the created
    DAG to CKPT on first build and reload it on restart, so unit keys — and therefore shared_<key>/ dir names —
    match. OFF by default (RBFE_RESUME=1 to enable): the immediate re-run finishes in ONE uninterrupted allocation
    (no-interruption provider), where resume is never exercised; enable + VALIDATE this on a spot provider (kill
    mid-leg, re-dispatch, confirm it continues the .nc) before trusting it for the A3 spot fleet."""
    if os.environ.get("RBFE_RESUME", "0") != "1":
        return proto.create(stateA=A, stateB=B, mapping=mapping)
    from gufe.protocols import ProtocolDAG
    from gufe.tokenization import JSON_HANDLER
    dag_path = os.path.join(CKPT, f"dag_{RECEPTOR}_{LEG}.json")
    if os.path.exists(dag_path):
        try:
            dag = ProtocolDAG.from_dict(json.load(open(dag_path), cls=JSON_HANDLER.decoder))
            print(f"  [rbfe][resume] reloaded persisted DAG {dag_path} -> STABLE unit keys (restart continues the "
                  f"same shared dirs); OpenFE resumes any existing simulation.nc", flush=True)
            return dag
        except Exception as e:  # noqa: BLE001 — corrupt/incompatible persisted DAG: rebuild fresh (safe fallback)
            print(f"  [rbfe][resume] WARN could not reload {dag_path} ({e}); building a fresh DAG", flush=True)
    dag = proto.create(stateA=A, stateB=B, mapping=mapping)
    try:
        json.dump(dag.to_dict(), open(dag_path, "w"), cls=JSON_HANDLER.encoder)
        print(f"  [rbfe][resume] persisted DAG -> {dag_path} (future restarts reuse these unit keys)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe][resume] WARN could not persist DAG ({e}); restart will rebuild (fresh keys)", flush=True)
    return dag


def _check_mapping_sane(mapping, ligA, ligB, n_mapped):
    """Guard against a DEGENERATE atom map (the 2026-07-14 solvent-leg forensic showed n_mapped_atoms=1 for a
    Br->NH2 congeneric edge whose MCS is ~13 atoms — a map that small alchemically transforms nearly the whole
    molecule, so ΔG_morph is garbage and the whole ΔΔG is invalid). A real relative edge maps most of the smaller
    ligand's heavy atoms. HARD-FAIL before any MD spend if the map is implausibly small; tune with RBFE_MIN_MAPPED_
    FRAC (default 0.4 of the smaller ligand's heavy-atom count) / RBFE_MIN_MAPPED (absolute floor, default 3)."""
    try:
        hA = ligA.to_rdkit().GetNumHeavyAtoms()
        hB = ligB.to_rdkit().GetNumHeavyAtoms()
    except Exception:  # noqa: BLE001
        hA = hB = None
    frac = float(os.environ.get("RBFE_MIN_MAPPED_FRAC", "0.4"))
    floor = int(os.environ.get("RBFE_MIN_MAPPED", "3"))
    need = floor
    if hA and hB:
        need = max(floor, int(frac * min(hA, hB)))
    if n_mapped < need:
        raise SystemExit(f"  ABORT: degenerate atom map — mapped {n_mapped} atoms for {LIGAND_A}->{LIGAND_B} "
                         f"(heavy atoms {hA}/{hB}); expected >= {need}. A map this small makes ΔG_morph (hence "
                         f"ΔΔG) invalid. Fix the mapping/pose before spending on MD (see _mapping diagnostics).")
    print(f"  [rbfe] map sanity OK: {n_mapped} mapped >= {need} (heavy atoms {hA}/{hB})", flush=True)


def run_leg():
    os.makedirs(CKPT, exist_ok=True)
    import openfe
    from rdkit import Chem
    ligA, ligB, protein = _build_components(openfe, Chem)
    mapping = _mapping(openfe, ligA, ligB)
    n_mapped = len(mapping.componentA_to_componentB)
    print(f"  [rbfe] {RECEPTOR}/{LEG}: mapped {n_mapped} atoms A->B ({LIGAND_A}->{LIGAND_B})", flush=True)
    _check_mapping_sane(mapping, ligA, ligB, n_mapped)

    if os.environ.get("MODE") == "smoke":
        # validate env + mapping + hybrid-topology build ONLY (no MD) — the cheap shakeout.
        proto = _protocol(openfe)
        A, B = _chemical_systems(openfe, ligA, ligB, protein)
        dag = proto.create(stateA=A, stateB=B, mapping=mapping)
        json.dump({"smoke": "ok", "receptor": RECEPTOR, "leg": LEG, "n_mapped_atoms": n_mapped,
                   "n_protocol_units": len(getattr(dag, "protocol_units", []) or [])},
                  open(os.path.join(CKPT, "smoke.json"), "w"), indent=2)
        print("  [rbfe] SMOKE ok — env solves, mapping + hybrid topology build.", flush=True)
        return

    proto = _protocol(openfe)
    A, B = _chemical_systems(openfe, ligA, ligB, protein)
    dag = _build_or_resume_dag(openfe, proto, A, B, mapping)
    _start_watchdog(CKPT, stall_min=float(os.environ.get("RBFE_STALL_MIN", "45")))
    from gufe.protocols import execute_DAG
    from pathlib import Path
    # gufe's execute_DAG does `shared_basedir / f"..."`, so these MUST be pathlib.Path, not str (a str `/` str
    # is the "TypeError: unsupported operand type(s) for /: 'str' and 'str'" that killed the first real-MD legs).
    shared = Path(CKPT) / "shared"
    scratch = Path(CKPT) / "scratch"
    shared.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    dagres = execute_DAG(dag, shared_basedir=shared, scratch_basedir=scratch, keep_shared=True)
    est = proto.gather([dagres])
    dg = est.get_estimate()
    unc = est.get_uncertainty()
    out = {"receptor": RECEPTOR, "leg": LEG, "ligand_a": LIGAND_A, "ligand_b": LIGAND_B,
           "dg_morph_kcal": float(dg.to("kilocalorie_per_mole").m),
           "unc_kcal": float(unc.to("kilocalorie_per_mole").m), "n_mapped_atoms": n_mapped}
    json.dump(out, open(os.path.join(CKPT, f"leg_{RECEPTOR}_{LEG}.json"), "w"), indent=2)
    print(f"  [rbfe] LEG DONE {RECEPTOR}/{LEG}: ΔG_morph={out['dg_morph_kcal']:.2f} ± {out['unc_kcal']:.2f}",
          flush=True)


def reduce_receptor():
    """ΔΔG_bind(A→B, receptor) = ΔG_complex_morph − ΔG_solvent_morph. Reads the two legs' checkpoints (mounted)."""
    def _read(kind):
        for base in (IN, CKPT):
            for p in glob.glob(os.path.join(base, "**", f"leg_{RECEPTOR}_*.json"), recursive=True) + \
                     glob.glob(os.path.join(base, "**", "leg_*_%s.json" % kind), recursive=True):
                d = json.load(open(p))
                if d.get("leg") == kind and (kind == "solvent" or d.get("receptor") == RECEPTOR):
                    return d
        return None
    cx, sol = _read("complex"), _read("solvent")
    if not cx or not sol:
        sys.exit(f"  ABORT reduce: missing legs (complex={bool(cx)} solvent={bool(sol)})")
    ddg = rb.ddg_bind(cx["dg_morph_kcal"], sol["dg_morph_kcal"])
    out = {"receptor": RECEPTOR, "ddg_bind_kcal": round(ddg, 3),
           "dg_complex_morph": cx["dg_morph_kcal"], "dg_solvent_morph": sol["dg_morph_kcal"],
           "absolute_dg_B": round(rb.absolute_dg_B(ddg, RECEPTOR), 3),
           "note": "ΔΔG_bind(401->lo_m0_NCCO); negative = lo_m0_NCCO binds tighter. absolute_dg_B anchors on "
                   "401's preliminary ABFE (rbfe_edges.ANCHOR_401_ABFE)."}
    os.makedirs(CKPT, exist_ok=True)
    json.dump(out, open(os.path.join(CKPT, f"ddg_{RECEPTOR}.json"), "w"), indent=2)
    print(f"  [rbfe] REDUCE {RECEPTOR}: ΔΔG_bind={ddg:.2f} kcal/mol → B absolute {out['absolute_dg_B']:.2f}",
          flush=True)


def main():
    mode = os.environ.get("MODE", "smoke")
    if mode == "cudaprobe":
        # Fast, no-MD diagnostic: report the driver's CUDA + which OpenMM GPU platform actually runs on this g5.
        # Decides whether the RBFE can move off the pathologically-slow OpenCL hybrid-Context path onto CUDA.
        import subprocess as _sp
        _sp.run(["nvidia-smi"], check=False)
        try:
            import openmm
            print("[rbfe] openmm", openmm.version.version, "cuda?",
                  "CUDA" in [openmm.Platform.getPlatform(i).getName()
                             for i in range(openmm.Platform.getNumPlatforms())], flush=True)
        except Exception as e:  # noqa: BLE001
            print("[rbfe] openmm import failed:", e, flush=True)
        print(f"[rbfe] SELECTED PLATFORM = {_working_platform_name('CUDA')}", flush=True)
        return
    if mode == "reduce":
        reduce_receptor()
    else:                       # smoke or run both go through run_leg (smoke short-circuits inside)
        run_leg()


if __name__ == "__main__":
    main()
