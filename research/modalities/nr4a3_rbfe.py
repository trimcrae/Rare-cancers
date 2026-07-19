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
import time

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


def _align_pose(mol_move, mol_ref, rdkit_chem):
    """Rigid-body superimpose mol_move onto mol_ref on their maximum common substructure so the shared scaffold
    COINCIDES in 3D (required for a physically-sensible RBFE morph, and to stop LOMAP's distance filter from
    rejecting an otherwise-valid topological map when the two docked poses were placed in different frames — the
    2026-07-14 n_mapped=1 root cause). Only moves mol_move as a rigid body; its internal geometry is unchanged.
    Falls back to the raw pose on any failure (logged), so it can never make the mapping worse than before."""
    try:
        from rdkit.Chem import rdFMCS, rdMolAlign
        refH = rdkit_chem.RemoveHs(rdkit_chem.Mol(mol_ref))
        movH = rdkit_chem.RemoveHs(rdkit_chem.Mol(mol_move))
        mcs = rdFMCS.FindMCS([refH, movH], completeRingsOnly=True, ringMatchesRingOnly=True, timeout=30)
        if mcs.numAtoms < 3:
            print(f"  [rbfe] align: MCS too small ({mcs.numAtoms}); using raw pose", flush=True)
            return mol_move
        patt = rdkit_chem.MolFromSmarts(mcs.smartsString)
        m_ref = mol_ref.GetSubstructMatch(patt)          # heavy-atom indices in the FULL (with-H) mols
        m_mov = mol_move.GetSubstructMatch(patt)
        if not m_ref or not m_mov or len(m_ref) != len(m_mov):
            print(f"  [rbfe] align: substruct match failed (ref={len(m_ref)} mov={len(m_mov)}); raw pose",
                  flush=True)
            return mol_move
        rmsd = rdMolAlign.AlignMol(mol_move, mol_ref, atomMap=list(zip(m_mov, m_ref)))
        print(f"  [rbfe] aligned {LIGAND_B}->{LIGAND_A} on {len(m_ref)} MCS atoms (RMSD {rmsd:.2f} Å); scaffold "
              f"now co-located for the morph", flush=True)
        return mol_move
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] align WARN ({e}); using raw pose", flush=True)
        return mol_move


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
    # RBFE morph requires the shared scaffold of A and B to be CO-LOCATED (the hybrid topology reuses one set of
    # coordinates for the mapped atoms). The congeneric dock placed zaienne_cmpd19 / cw_ev_5nh2 in DIFFERENT frames
    # (2026-07-14 smoke: LOMAP returned "no mapping after filters" and Kartograf mapped only 1 atom — the signature
    # of spatially-offset scaffolds), collapsing n_mapped to 1. Superimpose B onto A on their MCS so the scaffold
    # coincides -> LOMAP's distance filter passes and the morph shares a frame. Pose-independent 2D MCS still
    # defines the correspondence; this only fixes the geometry.
    molB = _align_pose(molB, molA, rdkit_chem)
    ligA = openfe.SmallMoleculeComponent.from_rdkit(molA)
    ligB = openfe.SmallMoleculeComponent.from_rdkit(molB)
    protein = None
    if LEG == "complex":
        pdb = os.path.join(IN, "receptor", f"{RECEPTOR}-opened.pdb")
        if not os.path.exists(pdb):
            pdb = next(iter(glob.glob(os.path.join(IN, "**", f"{RECEPTOR}-opened.pdb"), recursive=True)), pdb)
        protein = openfe.ProteinComponent.from_pdb_file(pdb)
    return ligA, ligB, protein


def _mapping(openfe, ligA, ligB, prefer_element_change=False):
    """LOMAP atom-map A→B (shared scaffold maps 1:1; the ortho-acetamido is the unique region).

    prefer_element_change=True (the ternary lane's N->CH linker edge): a RING single-atom element change
    (pyridine N -> benzene C) leaves element_change=False able to map the shared scaffold MINUS the whole ring
    region (a degenerate map that is NOT tiny, e.g. 37 atoms, so the <=2 guard below does not catch it), whereas
    element_change=True maps the ring 1:1 with N<->C as the single alchemical atom (~complete). So when asked,
    compute BOTH and return the LARGER map (the correct near-complete one). The binary lane keeps the default
    (strict-first) behaviour, so this cannot change any validated binary result.

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

    # Log the ACTUAL component names being mapped, NOT the module globals LIGAND_A/LIGAND_B. When another engine
    # (e.g. the ternary lane) reuses this mapper with its own SmallMoleculeComponents, the globals are stale
    # RBFE defaults (denovo_401/lo_m0_NCCO_gen) — printing them made a ternary smoke look like it mapped the
    # wrong molecules when it did not. Prefer ligA.name/ligB.name; fall back to the globals only if unnamed.
    nA = getattr(ligA, "name", None) or LIGAND_A
    nB = getattr(ligB, "name", None) or LIGAND_B

    if prefer_element_change:
        # Compute BOTH maps and return the one that maps MORE atoms (a ring element change makes the strict map
        # drop the whole ring region; element_change=True maps it 1:1 with the single N<->C alchemical atom).
        best = None
        for ec in (True, False):
            try:
                m = _suggest(ec)
                n = len(m.componentA_to_componentB)
                print(f"[rbfe] LOMAP element_change={ec}: {n} mapped atoms for {nA}->{nB} (prefer-element-change)",
                      flush=True)
                if best is None or n > best[0]:
                    best = (n, m)
            except StopIteration:
                continue
        if best is not None:
            print(f"[rbfe] prefer_element_change -> using the {best[0]}-atom map for {nA}->{nB}", flush=True)
            return best[1]
        # neither setting mapped -> fall through to the diagnostics + Kartograf path below

    # Prefer the STRICT map (element_change=False): correct for a pure APPEND edge (401->NCCO adds atoms of the
    # same element). But a single-point ELEMENT MUTATION (e.g. the congeneric 5-Br -> 5-NH2) has no same-element
    # map for the 5-substituent, so LOMAP returns an empty generator. Fall back to element_change=True: the
    # shared scaffold still maps 1:1 and Br<->N becomes the mutating atom. threed=False in BOTH cases, so the
    # map stays pose-independent -> the RBFE cycle (same A->B map in solvent + every complex leg) stays valid.
    for ec in (False, True):
        try:
            m = _suggest(ec)
            nmap = len(m.componentA_to_componentB)
            print(f"[rbfe] LOMAP element_change={ec}: {nmap} mapped atoms for {nA}->{nB}", flush=True)
            if ec:
                print(f"[rbfe] LOMAP: element_change=True required for {nA}->{nB} "
                      f"(single-point element mutation; scaffold maps 1:1, pose-independent)", flush=True)
            # A LOMAP map far smaller than the rdFMCS core (see MAPPING DIAG) is degenerate — for a congeneric
            # edge LOMAP should map ~the whole shared scaffold. If element_change=False returns a tiny map (it can
            # collapse to the mutating-atom neighborhood on a single-point element change), try element_change=True
            # which maps the scaffold 1:1 with Br<->N as the mutation. Only accept the small map if BOTH fail.
            if nmap <= 2 and ec is False:
                print(f"[rbfe] LOMAP element_change=False gave a DEGENERATE {nmap}-atom map; trying "
                      f"element_change=True before accepting", flush=True)
                continue
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


def _require_cuda():
    """Whether a validated CUDA platform is MANDATORY (no silent OpenCL fallback). Default ON (trimcrae
    2026-07-16: "require CUDA on all platforms"). Canonical env var OPENMM_REQUIRE_CUDA; BENCH_REQUIRE_CUDA is
    honored as a back-compat alias so the GCP bench workflow keeps working. Set OPENMM_REQUIRE_CUDA=0 to allow
    the OpenCL fallback on a driver that genuinely can't run CUDA."""
    v = os.environ.get("OPENMM_REQUIRE_CUDA", os.environ.get("BENCH_REQUIRE_CUDA", "1")).strip().lower()
    return v not in ("0", "false", "no", "off", "")


def _working_platform_name(preferred="CUDA"):
    """First OpenMM platform that ACTUALLY runs, validated by a 1-particle energy eval that forces kernel/module
    load (registration != usable: the conda CUDA build's PTX can be too new for the g5 driver → CUDA registers
    but fails at module load with CUDA_ERROR_UNSUPPORTED_PTX_VERSION). Try preferred → CUDA → OpenCL; return the
    NAME string (OpenFE's engine_settings.compute_platform wants a string). Mirrors nr4a3_abfe._select_platform.
    Cached so the real run and the DAG build agree."""
    global _PLATFORM_NAME
    if _PLATFORM_NAME:
        return _PLATFORM_NAME
    forced = os.environ.get("RBFE_PLATFORM", "").strip()   # e.g. CPU for the free-CI split shakeout (no GPU)
    if forced:
        _PLATFORM_NAME = forced
        print(f"[rbfe] OpenMM platform FORCED = {forced} (RBFE_PLATFORM)", flush=True)
        return forced
    import openmm
    from openmm import unit as ou
    # REQUIRE-CUDA gate (trimcrae 2026-07-16, "require CUDA on all platforms"): CUDA is ~1.3-2x faster than
    # OpenCL on NVIDIA (measured: L4 CUDA 628 vs OpenCL 485 ns/day; the perses hybrid Context also JIT-compiles
    # pathologically slowly on OpenCL). Silently falling back to OpenCL burns real $ on the slow platform without
    # anyone noticing — so by DEFAULT we hard-fail if CUDA can't validate, forcing a driver/env fix rather than a
    # silent tax. Escape hatch: OPENMM_REQUIRE_CUDA=0 restores the old CUDA→OpenCL soft fallback (use only when a
    # driver genuinely can't run CUDA). The forced (RBFE_PLATFORM) and CPU-preferred paths above are exempt.
    require_cuda = _require_cuda() and preferred != "CPU"
    validated = []
    for name in [preferred] + [p for p in ("CUDA", "OpenCL") if p != preferred]:
        try:
            plat = openmm.Platform.getPlatformByName(name)
            s = openmm.System(); s.addParticle(1.0)
            integ = openmm.VerletIntegrator(1.0 * ou.femtoseconds)
            ctx = openmm.Context(s, integ, plat)
            ctx.setPositions([openmm.Vec3(0, 0, 0)] * ou.nanometer)
            ctx.getState(getEnergy=True).getPotentialEnergy()          # forces kernel load → catches bad PTX
            del ctx, integ
            validated.append(name)
            if require_cuda and name != "CUDA":
                # CUDA required but this (validated) platform is OpenCL — don't accept it; report and fail below.
                print(f"[rbfe] platform {name} works but CUDA is REQUIRED — not accepting the OpenCL fallback",
                      flush=True)
                continue
            print(f"[rbfe] OpenMM platform: {name}", flush=True)
            _PLATFORM_NAME = name
            return name
        except Exception as e:  # noqa: BLE001 — registered but unusable; try the next
            print(f"[rbfe] platform {name} unavailable: {str(e)[:140]}", flush=True)
    if require_cuda:
        raise RuntimeError(
            "CUDA OpenMM platform REQUIRED but did not validate on this host "
            f"(validated non-CUDA platforms: {validated or 'none'}). CUDA is ~1.3-2x faster than OpenCL and the "
            "hybrid Context JIT-compiles far faster on it, so we refuse to silently run on OpenCL. Fix the CUDA "
            "build/driver match (env pins cuda-version<=driver; see environment-rbfe.yml) — or set "
            "OPENMM_REQUIRE_CUDA=0 to explicitly allow the OpenCL fallback for this run.")
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
        if os.environ.get("RBFE_TINY") == "1":
            # free-CI split-plumbing shakeout: a few ps so setup->simulate->analyze runs in minutes on CPU. NOT
            # science — validates the 3-unit hand-off + serialization only.
            # lengths MUST be multiples of the MC-move interval (625 steps × 4 fs = 2.5 ps) or OpenFE's
            # settings validation rejects them. 2.5 ps equil / 10 ps prod = a handful of MBAR iterations.
            s.simulation_settings.equilibration_length = 2.5 * _ou.picosecond
            s.simulation_settings.production_length = 10.0 * _ou.picosecond
            print("  [rbfe] RBFE_TINY=1 — 2.5ps/10ps MD (plumbing shakeout only, not a real result)", flush=True)
        else:
            s.simulation_settings.equilibration_length = 1.0 * _ou.nanosecond
            s.simulation_settings.production_length = 5.0 * _ou.nanosecond
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN could not set MD lengths as Quantity ({e}); using OpenFE defaults", flush=True)
    # CHECKPOINT INTERVAL (2026-07-15, ckptread-corrected). The openmmtools .chk keeps a FULL history of
    # checkpoints (verified: solvent .chk holds every checkpoint at iters 0,20,...,2000, all filled) — it is NOT
    # latest-only, and the mechanism resumes correctly on a clean sync (solvent resume=2000). The complex
    # spot-kill failure was NOT the interval and NOT persistence: it was that the (large) .chk did not reach S3
    # with its recent checkpoints before the 2-min spot-kill window closed (a SYNC problem). So DO NOT chase this
    # with frequency — an every-iteration .chk balloons to GB scale (solvent is 44 MB at interval=20 for 2000
    # iters; interval=1 => ~0.9 GB solvent / multi-GB complex) and makes the continuous S3 sync WORSE. Keep a
    # moderate interval: 20 iters (50 ps) — proven-good size (~44 MB) and resume granularity. The spot-kill sync
    # gap is handled separately (the run_simulate _ckpt_integrity_guard backup + a sync-behaviour check).
    from openff.units import unit as _ou3
    _ck_set = False
    for grp_name in ("simulation_settings", "output_settings"):
        grp = getattr(s, grp_name, None)
        if grp is None or not hasattr(grp, "checkpoint_interval"):
            continue
        for val in (50 * _ou3.picosecond, 20):   # 50 ps == 20 iters (Quantity first, int-iterations fallback)
            try:
                grp.checkpoint_interval = val
                print(f"  [rbfe] checkpoint_interval set via {grp_name} -> {grp.checkpoint_interval} "
                      f"(20 iters / 50 ps — moderate; .chk stays ~44 MB)", flush=True)
                _ck_set = True
                break
            except Exception as e:  # noqa: BLE001
                last = e
        if _ck_set:
            break
    if not _ck_set:
        print("  [rbfe] WARN checkpoint_interval not set (no matching attribute); relying on openmmtools default",
              flush=True)
    # ANALYSIS .nc SIZE (2026-07-16, netCDF-proven): the analysis simulation.nc stores positions AND velocities of
    # the full ~4760-atom solute × 12 replicas EVERY iteration when positions_write_frequency/velocities_write_
    # frequency are set (an OpenFE default that flipped on between env solves) → ~0.5 MB/iter → ~1 GB by 2000 iters,
    # re-uploaded whole each spot commit. MBAR/ΔG needs ONLY energies (always written), so force pos/vel writing
    # OFF → energy-only .nc (~10 MB, matching the earlier known-good run). Optional structural analysis degrades
    # gracefully (analyze reports structural_analysis_error, ΔG unaffected). Guarded: attr names/units vary by
    # openfe version, so try None; never let this block the build.
    oset = getattr(s, "output_settings", None)
    for _attr in ("positions_write_frequency", "velocities_write_frequency"):
        if oset is not None and hasattr(oset, _attr):
            try:
                setattr(oset, _attr, None)
                print(f"  [rbfe] output_settings.{_attr} -> None (energy-only .nc; avoids the ~1 GB trajectory bloat)",
                      flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  [rbfe] WARN could not disable {_attr} ({e}); .nc may store trajectory positions", flush=True)
    try:
        # PROBE CUDA -> OpenCL (mirror nr4a3_abfe._select_platform) instead of hard-forcing OpenCL. The hybrid
        # (perses) complex system JIT-compiles pathologically slowly on OpenCL — the 2026-07-08 complex legs
        # wedged for hours right after "Adding forces" (the Context build), while the small solvent leg finished.
        # CUDA doesn't JIT giant kernels, so if it actually runs on this image (the conda build's PTX must be
        # driver-compatible) the Context build is near-instant. Falls back to OpenCL only if CUDA can't load.
        s.engine_settings.compute_platform = _working_platform_name("CUDA")
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN compute_platform ({e})", flush=True)
    # Partial charges: use the STANDARD am1bcc method (via AmberTools antechamber/sqm, CPU). The RBFE env now
    # ships ambertools>=23 (environment-rbfe.yml) — the earlier antechamber exit-1 was simply that the env had NO
    # ambertools installed, not that am1bcc "doesn't work" here. Running the documented am1bcc method (vs the
    # NAGL surrogate) keeps us on OpenFE's published-benchmark protocol, so we can CITE that validation instead
    # of paying to re-derive it. NAGL is retained in the env as a documented fallback only.
    # CHARGE_METHOD env override lets a shakeout force "nagl" if a specific ligand's sqm ever fails.
    import os as _os
    _charge = _os.environ.get("CHARGE_METHOD", "am1bcc")
    try:
        s.partial_charge_settings.partial_charge_method = _charge
    except Exception as e:  # noqa: BLE001
        print(f"  [rbfe] WARN could not set partial_charge_method={_charge} ({e}); using default", flush=True)
    print(f"  [rbfe] partial_charge_method = {_charge} (am1bcc via AmberTools sqm; set CHARGE_METHOD=nagl to fall back)", flush=True)
    # CONSTRAINTS diagnostic + optional override (2026-07-19). The unconstrained-alchemical-X-H timestep analysis
    # ASSUMES constraints=HBonds (so the ONLY unconstrained X-H bonds are the alchemical ones). Print the effective
    # setting so a run's log proves what it used, and honor RBFE_FORCE_CONSTRAINTS (e.g. "hbonds") so the free
    # per-edge timestep scan can guarantee the HBonds premise regardless of the openfe default. Guarded: the attr
    # name/type varies by openfe version; never let it block the build.
    try:
        _ff = getattr(s, "forcefield_settings", None)
        _force = _os.environ.get("RBFE_FORCE_CONSTRAINTS")
        if _ff is not None and _force:
            try:
                _ff.constraints = _force
            except Exception as _ce:  # noqa: BLE001
                print(f"  [rbfe] WARN could not force constraints={_force} ({_ce})", flush=True)
        _cons_eff = getattr(_ff, "constraints", "N/A") if _ff is not None else "N/A"
        _hmass_eff = getattr(_ff, "hydrogen_mass", "N/A") if _ff is not None else "N/A"
        print(f"  [rbfe] forcefield_settings.constraints = {_cons_eff} | hydrogen_mass = {_hmass_eff}", flush=True)
    except Exception as _e:  # noqa: BLE001
        print(f"  [rbfe] WARN constraints diagnostic failed ({_e})", flush=True)
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
    """Hang-guard: hard-exit a genuinely WEDGED leg so the allocation isn't burned. DISABLED when stall_min <= 0.

    ★ FIX (2026-07-14): the first version false-KILLED a healthy complex leg — openmmtools does NOT write the
    production simulation.nc during the long EQUILIBRATION phase (~2.5 h for the complex), so a watchdog that armed
    the instant the .nc file merely EXISTS saw a static mtime and wrongly declared a stall at 45 min (the solvent
    leg only survived because its equilibration is < 45 min). Correct rule: only start the stall clock once the .nc
    has actually ADVANCED at least once (i.e. PRODUCTION is writing). During equilibration the .nc never advances,
    so the guard stays dormant; once production begins updating it (every checkpoint_interval), a real stall of
    stall_min with no update is caught. Requires `seen_progress` before it can ever fire."""
    if stall_min <= 0:
        print("  [rbfe][watchdog] DISABLED (RBFE_STALL_MIN<=0)", flush=True)
        return
    import glob as _glob
    import threading
    import time

    def _newest_nc_mtime():
        ncs = _glob.glob(os.path.join(ckpt, "**", "simulation*.nc"), recursive=True)
        return max((os.path.getmtime(p) for p in ncs), default=None)

    def _loop():
        last_mtime, last_change, seen_progress = None, None, False
        while True:
            time.sleep(60)
            mt = _newest_nc_mtime()
            if mt is None:
                continue                                  # setup phase: no .nc yet
            now = time.time()
            if last_mtime is None:
                last_mtime, last_change = mt, now
                continue
            if mt > last_mtime + 1:                       # .nc ADVANCED -> production is actively writing
                last_mtime, last_change, seen_progress = mt, now, True
                continue
            if not seen_progress:                         # .nc exists but never advanced (equilibration) -> dormant
                continue
            stalled_min = (now - last_change) / 60.0
            if stalled_min >= stall_min:
                print(f"  [rbfe][watchdog] STALL: production .nc unchanged {stalled_min:.0f} min "
                      f"(>= {stall_min:.0f}) after previously advancing; GPU appears wedged -> hard-exit 42.",
                      flush=True)
                os._exit(42)

    threading.Thread(target=_loop, daemon=True).start()
    print(f"  [rbfe][watchdog] armed: fires only AFTER production .nc starts advancing, then if it stalls "
          f">= {stall_min:.0f} min (equilibration never trips it)", flush=True)


def _build_or_resume_dag(openfe, proto, A, B, mapping):
    """Build the ProtocolDAG. Always a FRESH proto.create().

    ★ FINDING (2026-07-14, spot stress-test on nr4a3-congeneric-rbfe-v2): the deterministic-DAG "resume" (persist
    the DAG, reload it on restart so unit keys are STABLE) DOES NOT WORK and was actively HARMFUL — it caused
    `FileExistsError` in `gufe.protocols.execute_DAG`, which does a plain `shared.mkdir()` (no exist_ok) on the
    per-unit dir `shared_<unit.key>_attempt_0`. With stable keys, a spot restart's dir name collides with the one
    restored from the S3 checkpoint → hard crash. More fundamentally, **gufe.execute_DAG cannot resume a
    partially-completed ProtocolUnit at all**: it re-runs each unit from scratch and REQUIRES a fresh shared dir.
    So there is no supported way to continue a preempted leg via the shared_basedir mechanism. Reverted to fresh
    keys every run (the crash only appears with reused keys). RBFE_RESUME is retained only to `_clear_stale_shared`
    leftover partial dirs before execute_DAG (defensive; prevents disk bloat / any stray collision), NOT to resume.
    Consequence: a leg must COMPLETE IN ONE UNINTERRUPTED ALLOCATION (→ on-demand, or a build+MD that fits a spot
    window). True resumability needs bypassing gufe's dir handling + OpenFE's .nc restart — tracked separately."""
    return proto.create(stateA=A, stateB=B, mapping=mapping)


def _clear_stale_shared(ckpt):
    """Remove leftover OpenFE shared/scratch unit dirs from a preempted prior attempt so a fresh execute_DAG (fresh
    unit keys) starts clean — prevents the checkpoint from accumulating throwaway partial-build dirs across spot
    restarts. Safe because gufe cannot reuse them anyway (see _build_or_resume_dag)."""
    import shutil
    for sub in ("shared", "scratch"):
        d = os.path.join(ckpt, sub)
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
                print(f"  [rbfe] cleared stale {sub}/ from a prior (unresumable) attempt", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  [rbfe] WARN could not clear {sub}/ ({e})", flush=True)


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
    _clear_stale_shared(CKPT)   # remove a preempted attempt's partial dirs so gufe's per-unit mkdir doesn't collide
    _start_watchdog(CKPT, stall_min=float(os.environ.get("RBFE_STALL_MIN", "45")))
    from gufe.protocols import execute_DAG
    from pathlib import Path
    # gufe's execute_DAG does `shared_basedir / f"..."`, so these MUST be pathlib.Path, not str (a str `/` str
    # is the "TypeError: unsupported operand type(s) for /: 'str' and 'str'" that killed the first real-MD legs).
    # NB: gufe's INTERNAL per-unit `shared_<key>_attempt_0` mkdir has no exist_ok — a restored-from-checkpoint dir
    # of the same key crashes it (2026-07-14 FileExistsError); _clear_stale_shared above prevents that.
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
    # valA known-answer benchmark (STRATEGY.md RUNG 1 kill-switch): if a valA_manifest.json with a measured
    # ΔΔG_exp is staged alongside the legs, compare the COMPUTED ΔΔG_bind to it. GO if |Δ| ≲ 1.5-2 kcal/mol —
    # i.e. this exact container/protocol reproduces a public measured ΔΔG. NO-GO ⇒ stop/pivot before NR4A science.
    man = None
    for base in (IN, CKPT):
        for p in glob.glob(os.path.join(base, "**", "valA_manifest.json"), recursive=True):
            try:
                man = json.load(open(p))
            except Exception:  # noqa: BLE001
                man = None
            if man:
                break
        if man:
            break
    if man and man.get("ddG_exp_kcal") is not None:
        ddg_exp = float(man["ddG_exp_kcal"])
        abs_err = abs(ddg - ddg_exp)
        tol = float(os.environ.get("VALA_GO_TOL_KCAL", "2.0"))
        out["valA_benchmark"] = {
            "ddG_exp_kcal": round(ddg_exp, 3), "ddG_computed_kcal": round(ddg, 3),
            "abs_error_kcal": round(abs_err, 3), "go_tol_kcal": tol,
            "verdict": "GO" if abs_err <= tol else "NO-GO",
            "source": man.get("source"), "edge": f"{man.get('source_name_a')}->{man.get('source_name_b')}",
            "note": "GO = this container+protocol reproduced the public measured ΔΔG within tolerance "
                    "(build sound); NO-GO = stop/pivot (RUNG-1 kill-switch).",
        }
        print(f"  [rbfe] valA BENCHMARK: ΔΔG_computed={ddg:.2f} vs ΔΔG_exp={ddg_exp:.2f} "
              f"→ |err|={abs_err:.2f} kcal/mol (tol {tol}) → {out['valA_benchmark']['verdict']}", flush=True)
    os.makedirs(CKPT, exist_ok=True)
    json.dump(out, open(os.path.join(CKPT, f"ddg_{RECEPTOR}.json"), "w"), indent=2)
    print(f"  [rbfe] REDUCE {RECEPTOR}: ΔΔG_bind={ddg:.2f} kcal/mol → B absolute {out['absolute_dg_B']:.2f}",
          flush=True)


# ---- CPU-build / GPU-MD SPLIT (2026-07-14) ---------------------------------------------------------------------
# OpenFE 1.12 already splits the RBFE protocol into three of its OWN ProtocolUnits (verified by introspection):
#   HybridTopologySetupUnit          — CPU: parameterize + build the hybrid OpenMM System, serialize it +
#                                      positions to files (hybrid_system.xml.bz2, hybrid_positions.npy).
#   HybridTopologyMultiStateSimulationUnit — GPU: deserialize system+positions, run the MultiState MD; RESUMES
#                                      from the .nc automatically (its _check_restart looks for the nc+checkpoint
#                                      in the shared dir) -> spot-safe.
#   HybridTopologyMultiStateAnalysisUnit   — CPU: MBAR -> ΔG.
# We run each unit as its OWN job on the right/cheapest hardware (setup on cheap CPU, sim on GPU, analyze on CPU),
# passing each unit's outputs via a small JSON + the shared files (moved through the shared S3 checkpoint prefix).
# This reuses OpenFE's validated machinery verbatim — NO hand-rolled alchemy. Modes: setup | simulate | analyze
# (production, separate jobs) and splittest (all three in one process, RBFE_TINY, for the free-CI plumbing shakeout).
# gufe API: unit.execute(context=Context(shared,scratch), raise_error=True, **dep_results) -> ProtocolUnitResult;
# the sim/analysis units only touch dep_result.outputs, so a light stand-in object carrying .outputs suffices.


class _Res:
    """Minimal stand-in for a gufe ProtocolUnitResult across jobs — sim/analysis units only read `.outputs`
    (a dict of file paths + inline values + the openmm/openfe/gufe versions they verify against)."""
    def __init__(self, outputs):
        self.outputs = outputs


def _prep_units(openfe):
    from rdkit import Chem
    ligA, ligB, protein = _build_components(openfe, Chem)
    mapping = _mapping(openfe, ligA, ligB)
    n_mapped = len(mapping.componentA_to_componentB)
    print(f"  [rbfe] {RECEPTOR}/{LEG}: mapped {n_mapped} atoms A->B ({LIGAND_A}->{LIGAND_B})", flush=True)
    _check_mapping_sane(mapping, ligA, ligB, n_mapped)
    proto = _protocol(openfe)
    A, B = _chemical_systems(openfe, ligA, ligB, protein)
    dag = proto.create(stateA=A, stateB=B, mapping=mapping)
    byname = {}
    for u in dag.protocol_units:
        byname.setdefault(type(u).__name__, []).append(u)
    print(f"  [rbfe] DAG units: {{{', '.join(f'{k}:{len(v)}' for k, v in byname.items())}}}", flush=True)
    return proto, dag, byname, n_mapped


def _mk_ctx(name):
    from pathlib import Path
    from gufe import Context
    sh = Path(CKPT) / f"{name}_shared"
    sc = Path(CKPT) / f"{name}_scratch"
    sh.mkdir(parents=True, exist_ok=True)
    sc.mkdir(parents=True, exist_ok=True)
    try:
        return Context(shared=sh, scratch=sc)
    except TypeError:                                  # older/newer gufe may want more fields
        return Context(shared=sh, scratch=sc, permanent=sh)


def _one_unit(byname, key):
    us = byname.get(key) or []
    if not us:
        sys.exit(f"  ABORT: no {key} in DAG (units: {list(byname)}) — is openfe >= 1.12 (3-unit split)?")
    if len(us) > 1:
        print(f"  [rbfe] NOTE {len(us)} {key} (protocol_repeats>1); using the first", flush=True)
    return us[0]


def _save_outputs(outputs, path):
    def _ser(v):
        if hasattr(v, "__fspath__"):
            return str(v)                    # pathlib.Path -> str
        if hasattr(v, "tolist"):
            return v.tolist()                # numpy array (e.g. selection_indices) -> real list, NOT "[...]" str
        return v
    ser = {k: _ser(v) for k, v in outputs.items()}
    json.dump(ser, open(path, "w"), indent=2, default=str)
    print(f"  [rbfe] wrote {path} (keys: {list(ser)})", flush=True)


# outputs that are FILE PATHS: JSON stores them as str, but OpenFE's deserialize()/readers expect pathlib.Path
# (e.g. deserialize does `filename.parent`). Rehydrate these keys to Path when a downstream unit loads them.
_PATH_KEYS = ("system", "positions", "pdb_structure", "nc", "checkpoint", "trajectory", "structural_analysis")


def _load_outputs(path):
    from pathlib import Path
    d = json.load(open(path))
    for k in _PATH_KEYS:
        if isinstance(d.get(k), str):
            d[k] = Path(d[k])
    return d


def run_setup():
    """CPU job: build + serialize the hybrid system (the ~1 h single-threaded work — belongs on cheap CPU)."""
    os.makedirs(CKPT, exist_ok=True)
    import openfe
    _proto, _dag, byname, _n = _prep_units(openfe)
    res = _one_unit(byname, "HybridTopologySetupUnit").execute(context=_mk_ctx("setup"), raise_error=True)
    _save_outputs(res.outputs, os.path.join(CKPT, f"setup_{RECEPTOR}_{LEG}.json"))
    print(f"  [rbfe][setup] DONE {RECEPTOR}/{LEG}", flush=True)


def _read_last_iters(shared_dir, out_filename="simulation.nc", chk_filename="checkpoint.chk"):
    """Return (analysis_iter, checkpoint_iter) for an openmmtools MultiState storage — the DEFINITIVE resume
    point. from_storage resumes at read_last_iteration(last_checkpoint=True); if that is 0 while the analysis
    iteration is >0, a restart RE-EQUILIBRATES (the root-cause pathology). openmmtools-only; no MD."""
    from pathlib import Path
    from openmmtools.multistate import MultiStateReporter
    sh = Path(shared_dir)
    rep = MultiStateReporter(str(sh / out_filename), open_mode="r", checkpoint_storage=chk_filename)
    try:
        ana = rep.read_last_iteration(last_checkpoint=False)
        ck = rep.read_last_iteration(last_checkpoint=True)
    finally:
        rep.close()
    return ana, ck


def _ckpt_integrity_guard(shared_path, out_filename, chk_filename):
    """Before a restart executes: read the TRUE resume iteration, BACK UP the checkpoint so a re-equilibration
    can never destroy good production data (the self-perpetuating overwrite that made a single failed resume
    corrupt a leg permanently), and loudly flag the corruption signature. Best-effort; never blocks the run."""
    import shutil
    from pathlib import Path
    sh = Path(shared_path)
    try:
        ana, ck = _read_last_iters(sh, out_filename, chk_filename)
        print(f"  [ckpt-integrity] resume point read_last_iteration: checkpoint={ck} analysis={ana}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  [ckpt-integrity] could not read resume point ({e!r}); backing up defensively", flush=True)
        ana = ck = None
    try:
        bak = Path(CKPT) / f"sim_shared_bak_ana{ana}_ck{ck}"
        if not bak.exists():
            shutil.copytree(sh, bak)
            print(f"  [ckpt-integrity] backed up checkpoint set -> {bak} (survives S3 sync; "
                  "re-equilibration can no longer destroy the good checkpoint)", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  [ckpt-integrity] backup failed: {e!r}", flush=True)
    if (ck or 0) == 0 and (ana or 0) > 0:
        print(f"  [ckpt-integrity] ⚠⚠ CORRUPTION SIGNATURE: checkpoint has NO production state (resume=0) but "
              f"analysis reached {ana}. from_storage will RE-EQUILIBRATE and OVERWRITE — the leg's good data "
              "was already lost upstream (torn spot-kill upload). Backup above preserves what remains.",
              flush=True)


def _run_simulate_spot_safe(proto, byname, setup_outputs):
    """SPOT-SAFE simulate (RBFE_SPOT_SAFE=1): bypass OpenFE's _run_simulation (non-resumable
    equilibrate) and drive warmup-as-checkpointed-run() -> production via rbfe_spot_driver, with
    validated versioned snapshots committed to a CommitStore (S3 if RBFE_SPOT_COMMIT_S3 set, at a
    DISTINCT prefix from checkpoint_s3_uri; else local). Root cause + design: infra-gotchas doc."""
    import sys as _sys
    from pathlib import Path
    from urllib.parse import urlparse
    import rbfe_spot_checkpoint as spot
    import rbfe_spot_driver as drv
    unit = _one_unit(byname, "HybridTopologyMultiStateSimulationUnit")
    # deserialize/to_openmm/np/offunit are globals of the module where the unit CLASS is defined
    # (that's what OpenFE's own _execute resolves) — NOT necessarily equil_rfe_methods. Resolve it
    # from the instance so we use the exact same namespace and never guess an import path.
    umod = _sys.modules[type(unit).__module__]
    ctx = _mk_ctx("sim")
    system = umod.deserialize(setup_outputs["system"])
    positions = umod.to_openmm(umod.np.load(setup_outputs["positions"]) * umod.offunit.nm)
    selection_indices = setup_outputs["selection_indices"]
    commit_s3 = os.environ.get("RBFE_SPOT_COMMIT_S3")
    commit_gcs = os.environ.get("RBFE_SPOT_COMMIT_GCS")   # gs://bucket/prefix (GCP provider path)
    if commit_gcs:
        u = urlparse(commit_gcs)
        store = spot.GCSCommitStore(u.netloc, u.path.lstrip("/"))
        print(f"  [spot-safe] commit store: gs://{u.netloc}/{u.path.lstrip('/')}", flush=True)
    elif commit_s3:
        u = urlparse(commit_s3)
        store = spot.S3CommitStore(u.netloc, u.path.lstrip("/"))
        print(f"  [spot-safe] commit store: s3://{u.netloc}/{u.path.lstrip('/')}", flush=True)
    else:
        store = spot.LocalCommitStore(Path(CKPT) / "spot_commits")
        print(f"  [spot-safe] commit store: LOCAL {CKPT}/spot_commits", flush=True)
    wci = int(os.environ.get("RBFE_WARMUP_CKPT_ITERS", "10"))
    pci = int(os.environ.get("RBFE_PROD_CKPT_ITERS", "20"))
    outputs = drv.run_spot_safe(
        unit=unit, protocol=proto, system=system, positions=positions,
        selection_indices=selection_indices, shared_basepath=ctx.shared,
        scratch_basepath=ctx.scratch, commit_store=store,
        warmup_checkpoint_iters=wci, production_checkpoint_iters=pci)
    _save_outputs(outputs, os.path.join(CKPT, f"sim_{RECEPTOR}_{LEG}.json"))
    print(f"  [rbfe][sim][spot-safe] DONE {RECEPTOR}/{LEG}", flush=True)


def run_simulate():
    """GPU job: deserialize the setup system and run the MultiState MD. Resumes from the .nc on spot restart
    (OpenFE's own _check_restart), so this is the ONLY leg that needs the GPU and it is spot-safe."""
    os.makedirs(CKPT, exist_ok=True)
    import openfe
    proto, _dag, byname, _n = _prep_units(openfe)
    setup_outputs = _load_outputs(os.path.join(CKPT, f"setup_{RECEPTOR}_{LEG}.json"))
    _start_watchdog(CKPT, stall_min=float(os.environ.get("RBFE_STALL_MIN", "45")))
    if os.environ.get("RBFE_SPOT_SAFE") == "1":
        return _run_simulate_spot_safe(proto, byname, setup_outputs)
    # === RESTART DIAGNOSTIC (2026-07-14) — authoritative view of what OpenFE _check_restart(shared_path=ctx.shared)
    # will see. _check_restart returns True iff BOTH ctx.shared/output_filename AND ctx.shared/checkpoint_storage_filename
    # exist; else it silently re-equilibrates. Print ctx.shared, its contents, and the two exact files it needs.
    ctx = _mk_ctx("sim")
    try:
        from pathlib import Path as _P
        os_ = __import__("os")
        oset = proto.settings.output_settings if hasattr(proto, "settings") else None
        of = getattr(oset, "output_filename", "simulation.nc")
        cf = getattr(oset, "checkpoint_storage_filename", "checkpoint.chk")
        print(f"  [restart-diag] ctx.shared = {ctx.shared}", flush=True)
        print(f"  [restart-diag] _check_restart needs: output_filename={of!r} checkpoint_storage_filename={cf!r}",
              flush=True)
        sh = _P(ctx.shared)
        listing = sorted(str(p.relative_to(sh)) for p in sh.rglob("*") if p.is_file()) if sh.is_dir() else []
        print(f"  [restart-diag] ctx.shared contents ({len(listing)} files): {listing}", flush=True)
        for fn in (of, cf):
            fp = sh / fn
            print(f"  [restart-diag]   need {fn!r}: is_file={fp.is_file()}"
                  f"{f' size={fp.stat().st_size}B' if fp.is_file() else ''}", flush=True)
        would = (sh / of).is_file() and (sh / cf).is_file()
        print(f"  [restart-diag] => _check_restart WOULD return restart={would} "
              f"({'RESUME production' if would else 'FRESH minimize+equilibrate'})", flush=True)
        if would:
            _ckpt_integrity_guard(sh, of, cf)
    except Exception as e:  # noqa: BLE001
        print(f"  [restart-diag] diag error: {e!r}", flush=True)
    res = _one_unit(byname, "HybridTopologyMultiStateSimulationUnit").execute(
        context=ctx, raise_error=True, setup_results=_Res(setup_outputs))
    _save_outputs(res.outputs, os.path.join(CKPT, f"sim_{RECEPTOR}_{LEG}.json"))
    print(f"  [rbfe][sim] DONE {RECEPTOR}/{LEG}", flush=True)


def run_analyze():
    """CPU job: MBAR over the trajectory -> ΔG_morph. Writes leg_<r>_<leg>.json (same shape run_leg wrote, so the
    existing reduce_receptor forms ΔΔG unchanged)."""
    os.makedirs(CKPT, exist_ok=True)
    import openfe
    proto, _dag, byname, n_mapped = _prep_units(openfe)
    setup_outputs = _load_outputs(os.path.join(CKPT, f"setup_{RECEPTOR}_{LEG}.json"))
    sim_outputs = _load_outputs(os.path.join(CKPT, f"sim_{RECEPTOR}_{LEG}.json"))
    res = _one_unit(byname, "HybridTopologyMultiStateAnalysisUnit").execute(
        context=_mk_ctx("ana"), raise_error=True,
        setup_results=_Res(setup_outputs), simulation_results=_Res(sim_outputs))
    print(f"  [rbfe][analyze] outputs keys={list(res.outputs)}", flush=True)
    # dump raw analysis outputs so a shakeout reveals the exact ΔG key, then extract robustly.
    json.dump({k: str(v) for k, v in res.outputs.items()},
              open(os.path.join(CKPT, f"analysis_raw_{RECEPTOR}_{LEG}.json"), "w"), indent=2, default=str)
    dg = unc = None
    for k in ("unit_estimate", "estimate", "dg", "DG"):
        v = res.outputs.get(k)
        if v is not None:
            try:
                dg = float(v.to("kilocalorie_per_mole").m); break
            except Exception:  # noqa: BLE001
                try:
                    dg = float(v); break
                except Exception:  # noqa: BLE001
                    pass
    for k in ("unit_estimate_error", "uncertainty", "dg_error", "error"):
        v = res.outputs.get(k)
        if v is not None:
            try:
                unc = float(v.to("kilocalorie_per_mole").m); break
            except Exception:  # noqa: BLE001
                try:
                    unc = float(v); break
                except Exception:  # noqa: BLE001
                    pass
    if dg is None:
        print(f"  [rbfe][analyze] WARN could not find ΔG key in {list(res.outputs)}; see analysis_raw_*.json",
              flush=True)
        return
    out = {"receptor": RECEPTOR, "leg": LEG, "ligand_a": LIGAND_A, "ligand_b": LIGAND_B,
           "dg_morph_kcal": dg, "unc_kcal": unc if unc is not None else 0.0, "n_mapped_atoms": n_mapped,
           "via": "split(setup|simulate|analyze)"}
    json.dump(out, open(os.path.join(CKPT, f"leg_{RECEPTOR}_{LEG}.json"), "w"), indent=2)
    print(f"  [rbfe][analyze] DONE {RECEPTOR}/{LEG}: ΔG_morph={dg:.2f} ± {out['unc_kcal']:.2f}", flush=True)


def count_unconstrained_alchemical_xh(system):
    """Return (n_xh_total, n_unconstrained, unconstrained_list, hmasses_seen) for an OpenMM System — i.e. how many
    X-H bonds present in the bonded forces are NOT in the constraint set. NB (measured 2026-07-19): OpenFE's
    HybridTopologyFactory leaves the ENTIRE alchemical ligand's X-H bonds UNCONSTRAINED — `constraints=hbonds`
    rigidifies only water/protein, so on the pilot edge total_constraints=1771 was water-only and all 14 ligand X-H
    were unconstrained. So this count does NOT discriminate edges (every edge has ~all ligand X-H unconstrained);
    the 2 fs vs 4 fs ceiling is a LANE/system-size property (binary warhead RBFE survives 4 fs; large ternary
    assemblies NaN at 4 fs), NOT a per-edge unconstrained-count. Use this as a diagnostic of the constraint STATE
    (all-ligand-unconstrained is expected), not as a per-edge timestep oracle. `unconstrained_list` is
    [(h_atom_idx, h_mass_amu), ...]."""
    import openmm as _mm
    cons = set()
    for k in range(system.getNumConstraints()):
        i, j, _d = system.getConstraintParameters(k)
        cons.add((min(int(i), int(j)), max(int(i), int(j))))
    mass = [system.getParticleMass(p).value_in_unit(_mm.unit.dalton) for p in range(system.getNumParticles())]
    is_h = lambda m: m < 5.0            # H (1.008) or HMR-repartitioned H (3-4); heavy atoms >= 12
    xh_total = xh_unconstrained = 0
    unc = []
    # scan BOTH HarmonicBondForce AND CustomBondForce — OpenFE's hybrid factory puts the alchemically-varying
    # (appearing/disappearing) bonds in a CustomBondForce, so an unconstrained alchemical X-H lives there.
    for f in system.getForces():
        if not isinstance(f, (_mm.HarmonicBondForce, _mm.CustomBondForce)):
            continue
        for b in range(f.getNumBonds()):
            p = f.getBondParameters(b)
            i, j = int(p[0]), int(p[1])
            if is_h(mass[i]) ^ is_h(mass[j]):            # X-H bond = exactly one light partner
                xh_total += 1
                hidx = i if is_h(mass[i]) else j
                if (min(i, j), max(i, j)) not in cons:
                    xh_unconstrained += 1
                    unc.append((hidx, round(mass[hidx], 3)))
    hmasses = sorted({round(m, 2) for m in mass if is_h(m)})
    return xh_total, xh_unconstrained, unc, hmasses


def constrain_nonalchemical_xh(system):
    """Add HBonds-style constraints to the NON-alchemical X-H bonds that OpenFE leaves unconstrained.

    WHY: OpenFE's `constraints=hbonds` reaches only the Amber-built water/protein, NOT the OpenFF-parameterized
    LIGAND (measured 2026-07-19: pilot solvent leg had total_constraints=water-only, all 14 ligand X-H flexible).
    An unconstrained C-H (HMR'd to ~18 fs period) caps the stable timestep at ~2 fs; for a large assembly (the
    ternary lane) the many flexible ligand/complex C-H are what force 2 fs and NaN 4 fs. Constraining the
    NON-alchemical C-H (those in the standard HarmonicBondForce — environment/core bonds that do NOT morph between
    the λ endpoints) removes those fast DOF so a larger timestep is stable, WITHOUT touching the alchemical bonds
    (which live in the CustomBondForce and MUST stay flexible — their length differs between endpoints).

    VALIDITY: constraining C-H is the standard rigid-bond approximation and is exactly what `constraints=hbonds`
    INTENDS but fails to deliver to the ligand. For a RELATIVE free energy the constraint contribution CANCELS when
    applied identically to every leg of the cycle — so this MUST be enabled (RBFE_CONSTRAIN_LIGAND_CH=1) for ALL
    legs of a calculation, or not at all. Only non-alchemical bonds are constrained, so the alchemical transformation
    is unchanged. Returns the number of constraints added. Idempotent (skips already-constrained pairs).
    """
    import openmm as _mm
    cons = set()
    for k in range(system.getNumConstraints()):
        i, j, _d = system.getConstraintParameters(k)
        cons.add((min(int(i), int(j)), max(int(i), int(j))))
    mass = [system.getParticleMass(p).value_in_unit(_mm.unit.dalton) for p in range(system.getNumParticles())]
    is_h = lambda m: m < 5.0
    added = 0
    # ONLY the standard HarmonicBondForce: those are the non-alchemical (environment/core) bonds. The alchemical
    # (appearing/disappearing/parameter-changing) bonds are in the CustomBondForce and are deliberately NOT touched.
    for f in system.getForces():
        if not isinstance(f, _mm.HarmonicBondForce):
            continue
        for b in range(f.getNumBonds()):
            i, j, length, k = f.getBondParameters(b)
            i, j = int(i), int(j)
            if is_h(mass[i]) ^ is_h(mass[j]):            # X-H (exactly one light partner)
                key = (min(i, j), max(i, j))
                if key not in cons:
                    system.addConstraint(i, j, length)   # constrain at the harmonic equilibrium length
                    cons.add(key)
                    added += 1
    return added


def execute_hybrid_dag_spot_safe(proto, dag, ckpt, tag,
                                 warmup_env="RBFE_WARMUP_CKPT_ITERS", prod_env="RBFE_PROD_CKPT_ITERS",
                                 commit_s3_env="RBFE_SPOT_COMMIT_S3", commit_gcs_env="RBFE_SPOT_COMMIT_GCS"):
    """GENERIC spot-safe execution of ANY RelativeHybridTopology DAG (setup -> simulate[commit-per-iteration to a
    versioned CommitStore] -> analyze), returning (dg_kcal, unc_kcal, analysis_keys). This is the SAME resumable
    path RBFE's run_setup/_run_simulate_spot_safe/run_analyze use (rbfe_spot_driver.run_spot_safe), factored out
    so the ternary engine inherits identical resume-on-preemption behaviour — nothing we run should be welded.
    The MD commits to GCS/S3 per interval, so a re-dispatch RESUMES from the last committed iteration (setup is
    cheap-redone on a fresh VM; the expensive sampling never restarts from zero). Caller writes its own leg JSON."""
    import sys as _sys
    from pathlib import Path
    from urllib.parse import urlparse

    from gufe import Context
    import rbfe_spot_checkpoint as spot
    import rbfe_spot_driver as drv

    byname = {}
    for u in dag.protocol_units:
        byname.setdefault(type(u).__name__, []).append(u)

    def _ctx(name):
        sh = Path(ckpt) / ("%s_%s_shared" % (tag, name))
        sc = Path(ckpt) / ("%s_%s_scratch" % (tag, name))
        sh.mkdir(parents=True, exist_ok=True)
        sc.mkdir(parents=True, exist_ok=True)
        try:
            return Context(shared=sh, scratch=sc)
        except TypeError:
            return Context(shared=sh, scratch=sc, permanent=sh)

    def _unit(key):
        us = byname.get(key) or []
        if not us:
            raise SystemExit("  ABORT: no %s in DAG (units=%s); openfe>=1.12?" % (key, list(byname)))
        return us[0]

    # SIMULATE — spot-safe: drive the MultiState unit via rbfe_spot_driver with a durable CommitStore
    sim_unit = _unit("HybridTopologyMultiStateSimulationUnit")
    umod = _sys.modules[type(sim_unit).__module__]
    sctx = _ctx("sim")

    # SETUP with a GCS SETUP CACHE (2026-07-18). The solvate+parameterize step ('SETUP', ~460s for the 146k-atom
    # ternary) is NOT sampling and was rebuilt from scratch on every fresh VM — so on volatile GCP L4 Spot (30s
    # preemption warning, no min-runtime, GPU capacity contended at peak) a preemption during the uncheckpointed
    # setup+minimize window lost ALL of it and the run never reached the first warmup checkpoint. Fix: the setup
    # unit's outputs are deterministic per (leg, charges), so cache the WHOLE setup_outputs dict to GCS right after
    # the build (files copied + a manifest; non-file values pickled), preserving every field the ANALYZE unit reads.
    # A re-dispatch RESTORES it in seconds and skips the rebuild — the setup is now checkpointed too, not just the
    # sampling. Generic so the shared binary-RBFE path benefits identically. Keyed by tag+charge+SETUP_CACHE_VERSION
    # (bump the version if staging/forcefield changes so a stale system is never restored).
    import json as _json
    import pickle as _pickle
    import subprocess as _sub

    def _gsh(*args):
        return _sub.run(["gcloud", "storage", *args], capture_output=True, text=True)

    _cache_root = os.environ.get("RBFE_SETUP_CACHE_GCS")
    _cache_ver = os.environ.get("SETUP_CACHE_VERSION", "v1")
    _charge = os.environ.get("CHARGE_METHOD", "am1bcc")
    cache_dir = ("%s/%s__%s__%s" % (_cache_root.rstrip("/"), tag, _charge, _cache_ver)) if _cache_root else None
    loc = Path(ckpt) / ("setupcache_%s" % tag)
    setup_outputs = None

    if cache_dir and _gsh("ls", cache_dir + "/manifest.json").returncode == 0:
        try:
            loc.mkdir(parents=True, exist_ok=True)
            for meta in ("manifest.json", "objs.pkl"):
                r = _gsh("cp", cache_dir + "/" + meta, str(loc / meta))
                if r.returncode:
                    raise RuntimeError("cp %s: %s" % (meta, (r.stderr or "")[-200:]))
            manifest = _json.loads((loc / "manifest.json").read_text())
            objs = _pickle.loads((loc / "objs.pkl").read_bytes())
            setup_outputs = {}
            for k, mv in manifest.items():
                if mv[0] == "file":
                    r = _gsh("cp", cache_dir + "/" + mv[1], str(loc / mv[1]))
                    if r.returncode:
                        raise RuntimeError("cp %s: %s" % (mv[1], (r.stderr or "")[-200:]))
                    setup_outputs[k] = loc / mv[1]   # pathlib.Path — openfe deserialize() calls .parent (not a str)
                else:
                    setup_outputs[k] = objs[k]
            print("  [spot-safe] SETUP RESTORED from cache %s — skipped the ~460s solvate+parameterize "
                  "(the window that kept dying to spot preemption)" % cache_dir, flush=True)
        except Exception as e:  # noqa: BLE001
            print("  [spot-safe] setup-cache restore failed (%s); rebuilding from scratch" % e, flush=True)
            setup_outputs = None

    if setup_outputs is None:
        print("  [spot-safe] SETUP begin (solvate + parameterize the hybrid system)…", flush=True)
        _t_setup0 = time.time()
        setup_outputs = _unit("HybridTopologySetupUnit").execute(context=_ctx("setup"), raise_error=True).outputs
        print("  [spot-safe] SETUP done in %.0fs" % (time.time() - _t_setup0), flush=True)
        if cache_dir:
            try:
                import shutil as _shutil
                loc.mkdir(parents=True, exist_ok=True)
                manifest, objs, upload = {}, {}, []
                for k, v in dict(setup_outputs).items():
                    fp = None
                    try:
                        if v is not None and os.path.isfile(str(v)):
                            fp = str(v)
                    except (ValueError, OSError):
                        fp = None
                    if fp:
                        bn = "f_%d_%s" % (len(manifest), os.path.basename(fp))
                        _shutil.copyfile(fp, str(loc / bn))
                        manifest[k] = ["file", bn]
                        upload.append(bn)
                    else:
                        manifest[k] = ["obj", None]
                        objs[k] = v
                (loc / "objs.pkl").write_bytes(_pickle.dumps(objs))
                (loc / "manifest.json").write_text(_json.dumps(manifest))
                for f in upload + ["objs.pkl", "manifest.json"]:
                    r = _gsh("cp", str(loc / f), cache_dir + "/" + f)
                    if r.returncode:
                        raise RuntimeError("cp %s: %s" % (f, (r.stderr or "")[-200:]))
                print("  [spot-safe] SETUP cached to %s (a re-dispatch after preemption now skips the rebuild)"
                      % cache_dir, flush=True)
            except Exception as e:  # noqa: BLE001
                print("  [spot-safe] setup-cache save failed (%s); non-fatal" % e, flush=True)

    system = umod.deserialize(setup_outputs["system"])
    positions = umod.to_openmm(umod.np.load(setup_outputs["positions"]) * umod.offunit.nm)
    selection_indices = setup_outputs["selection_indices"]
    try:
        print("  [spot-safe] SOLVATED SYSTEM: %d particles, %d λ-windows (feasibility signal on this GPU)"
              % (system.getNumParticles(), int(os.environ.get("N_WINDOWS", "12"))), flush=True)
    except Exception:  # noqa: BLE001
        pass
    # LIGAND-C-H CONSTRAINT LEVER (2026-07-19, opt-in RBFE_CONSTRAIN_LIGAND_CH=1). OpenFE leaves the alchemical
    # ligand's C-H unconstrained, which caps the timestep at ~2 fs for large assemblies (the ternary lane). Adding
    # constraints to the NON-alchemical C-H (only) lets a larger dt be stable. Applied to the deserialized `system`
    # BEFORE the sampler builds its contexts, so the MD uses the constrained system. MUST be set for every leg of a
    # calculation to keep ΔΔG valid (the constraint cancels in the cycle). No-op unless the env is 1.
    if os.environ.get("RBFE_CONSTRAIN_LIGAND_CH") == "1":
        try:
            _n0 = system.getNumConstraints()
            _added = constrain_nonalchemical_xh(system)
            print("  [constrain-lig] RBFE_CONSTRAIN_LIGAND_CH=1 -> added %d non-alchemical X-H constraints "
                  "(%d -> %d total); enables a larger stable timestep. MUST be on for ALL legs."
                  % (_added, _n0, system.getNumConstraints()), flush=True)
        except Exception as _ce:  # noqa: BLE001
            print("  [constrain-lig] WARN failed to add ligand C-H constraints (%s); running unconstrained"
                  % _ce, flush=True)
    # HMR / UNCONSTRAINED-BOND DIAGNOSTIC (2026-07-18): the ternary warmup NaN at 2 fs is the signature of an
    # UNCONSTRAINED X-H bond (OpenFE cannot constrain a bond whose constraint status changes along λ, so an
    # alchemically-appearing/disappearing C-H is left flexible → ~10 fs period → unstable > ~1 fs). In a system
    # built with constraints=HBonds, the ONLY unconstrained X-H bonds ARE those alchemical ones. This dump names
    # them and reports whether HMR reached their H mass (repartitioned ≈3-4 amu = stable at 2-4 fs; ≈1 amu = the
    # fix: extend HMR to the alchemical H and reclaim the 2-4x we lose by forcing 1 fs). Free, CPU, non-fatal.
    try:
        _xh_total, _xh_unconstrained, _unc, _hmasses = count_unconstrained_alchemical_xh(system)
        print("  [hmr-diag] X-H bonds=%d constrained=%d UNCONSTRAINED=%d | H-mass values seen=%s"
              % (_xh_total, _xh_total - _xh_unconstrained, _xh_unconstrained, _hmasses), flush=True)
        if _unc:
            print("  [hmr-diag] UNCONSTRAINED X-H (the alchemical bonds forcing 1 fs) -> "
                  "[(atom_idx, H_mass_amu)]: %s" % _unc[:20], flush=True)
            _reps = [m for _, m in _unc if m >= 1.5]
            print("  [hmr-diag] of %d unconstrained-H, %d are HMR-repartitioned (mass>=1.5) and %d are at ~1 amu "
                  "(NOT repartitioned -> these are what force 1 fs; extending HMR here should restore 2-4 fs)"
                  % (len(_unc), len(_reps), len(_unc) - len(_reps)), flush=True)
            print("  [hmr-diag] VERDICT: this edge has an unconstrained alchemical X-H -> max stable dt ~2 fs "
                  "(do NOT use 4 fs)", flush=True)
        else:
            print("  [hmr-diag] NO unconstrained X-H bonds found -> 4 fs (OpenFE default) is safe for this edge "
                  "(terminal/dummy-block morph; no H-count change on a mapped atom)", flush=True)
        # RBFE_HMRDIAG_ONLY=1 (2026-07-19): the constraint verdict above is the ENTIRE timestep-ceiling answer and
        # needs NO MD — so a per-edge timestep scan (rbfe_edge_timestep_scan.py) sets this to build the hybrid on a
        # free CPU runner, read the verdict, and exit before any GPU/warmup. Returns the counts so a caller can log.
        if os.environ.get("RBFE_HMRDIAG_ONLY") == "1":
            # extra structured diagnostics so a caller can tell APPLIED-constraints from a broken build without the
            # (truncated) CI log: total system constraints + the effective forcefield constraints/HMR setting.
            try:
                _tot_cons = int(system.getNumConstraints())
            except Exception:  # noqa: BLE001
                _tot_cons = None
            _pset = getattr(proto, "settings", None)
            _ff = getattr(_pset, "forcefield_settings", None) if _pset is not None else None
            _cons_set = getattr(_ff, "constraints", None) if _ff is not None else None
            _hmass_set = getattr(_ff, "hydrogen_mass", None) if _ff is not None else None
            print("  [hmr-diag] system.getNumConstraints()=%s | forcefield constraints=%s hydrogen_mass=%s"
                  % (_tot_cons, _cons_set, _hmass_set), flush=True)
            print("  [hmr-diag] RBFE_HMRDIAG_ONLY=1 -> exiting after the constraint verdict (no MD).", flush=True)
            return None, None, {"hmrdiag_only": True, "xh_total": _xh_total,
                                "xh_unconstrained": _xh_unconstrained, "unconstrained": _unc, "hmasses": _hmasses,
                                "total_constraints": _tot_cons, "constraints_setting": str(_cons_set),
                                "hydrogen_mass_setting": str(_hmass_set)}
    except Exception as _e:  # noqa: BLE001
        print("  [hmr-diag] failed: %s: %s" % (type(_e).__name__, _e), flush=True)
        if os.environ.get("RBFE_HMRDIAG_ONLY") == "1":
            return None, None, {"hmrdiag_only": True, "error": "%s: %s" % (type(_e).__name__, _e)}
    # PRE-BAKE / PRIME (2026-07-18): setup (solvate+parameterize) is 100% CPU — no GPU touched until the MD below.
    # So a free, NON-PREEMPTIBLE CPU runner can build it and write the GCS cache, then a GPU VM RESTORES it and goes
    # straight to minimize+MD — removing the entire (preemption-prone) setup window from GPU/spot exposure. The
    # serialized OpenMM System is platform-agnostic, so a CPU-built cache is valid for the GPU run. RBFE_PRIME_ONLY=1
    # exits here (cache already written above); requires RBFE_SETUP_CACHE_GCS so there IS a cache to leave behind.
    if os.environ.get("RBFE_PRIME_ONLY") == "1":
        if not cache_dir:
            print("  [spot-safe] PRIME_ONLY set but RBFE_SETUP_CACHE_GCS unset — nothing cached; abort", flush=True)
            raise SystemExit("PRIME_ONLY requires RBFE_SETUP_CACHE_GCS")
        print("  [spot-safe] PRIME_ONLY: setup built + cached to %s; exiting before MD "
              "(a GPU run will restore it and skip setup)." % cache_dir, flush=True)
        return None, None, {"primed": True, "cache_dir": cache_dir, "n_particles": system.getNumParticles()}
    commit_gcs = os.environ.get(commit_gcs_env)
    commit_s3 = os.environ.get(commit_s3_env)
    if commit_gcs:
        u = urlparse(commit_gcs)
        store = spot.GCSCommitStore(u.netloc, u.path.lstrip("/"))
        print("  [spot-safe] commit store: gs://%s/%s" % (u.netloc, u.path.lstrip("/")), flush=True)
    elif commit_s3:
        u = urlparse(commit_s3)
        store = spot.S3CommitStore(u.netloc, u.path.lstrip("/"))
        print("  [spot-safe] commit store: s3://%s/%s" % (u.netloc, u.path.lstrip("/")), flush=True)
    else:
        store = spot.LocalCommitStore(Path(ckpt) / ("spot_commits_%s" % tag))
        print("  [spot-safe] commit store: LOCAL (no commit URI set)", flush=True)
    wci = int(os.environ.get(warmup_env, "10"))
    pci = int(os.environ.get(prod_env, "20"))
    sim_outputs = drv.run_spot_safe(
        unit=sim_unit, protocol=proto, system=system, positions=positions,
        selection_indices=selection_indices, shared_basepath=sctx.shared,
        scratch_basepath=sctx.scratch, commit_store=store,
        warmup_checkpoint_iters=wci, production_checkpoint_iters=pci)
    # ANALYZE — MBAR over the trajectory
    ana_outputs = _unit("HybridTopologyMultiStateAnalysisUnit").execute(
        context=_ctx("ana"), raise_error=True,
        setup_results=_Res(setup_outputs), simulation_results=_Res(sim_outputs)).outputs
    dg = unc = None
    for k in ("unit_estimate", "estimate", "dg", "DG"):
        v = ana_outputs.get(k)
        if v is not None:
            try:
                dg = float(v.to("kilocalorie_per_mole").m); break
            except Exception:  # noqa: BLE001
                try:
                    dg = float(v); break
                except Exception:  # noqa: BLE001
                    pass
    for k in ("unit_estimate_error", "uncertainty", "dg_error", "error"):
        v = ana_outputs.get(k)
        if v is not None:
            try:
                unc = float(v.to("kilocalorie_per_mole").m); break
            except Exception:  # noqa: BLE001
                try:
                    unc = float(v); break
                except Exception:  # noqa: BLE001
                    pass
    return dg, unc, list(ana_outputs)


def run_splittest():
    """Free-CI plumbing shakeout: setup -> simulate -> analyze in ONE process (RBFE_TINY + RBFE_PLATFORM=CPU), so
    the 3-unit hand-off + JSON serialization is validated end-to-end for $0 before any GPU spend."""
    run_setup()
    run_simulate()
    run_analyze()


def main():
    mode = os.environ.get("MODE", "smoke")
    if mode == "setup":
        return run_setup()
    if mode == "simulate":
        return run_simulate()
    if mode == "analyze":
        return run_analyze()
    if mode == "splittest":
        return run_splittest()
    if mode == "ckptread":
        # Read-only diagnostic (no MD). Beyond the resume point, dump the RAW iteration COVERAGE of both files so
        # we can answer trimcrae's question: with checkpoint_interval=20, why did a kill at iter 100 restore
        # iteration 0 instead of 80? Reveals (a) whether the .chk keeps a HISTORY of checkpoints [0,20,40,...] or
        # only the LATEST, and (b) whether the large .chk sync LAGS the small .nc (analysis>0 but checkpoint=0).
        # CKPTREAD_SUBDIR overrides "sim_shared" (e.g. a sim_shared_bak_* backup of a corrupted checkpoint).
        subdir = os.environ.get("CKPTREAD_SUBDIR", "sim_shared")
        sh = os.path.join(CKPT, subdir)
        print(f"[ckptread] leg={RECEPTOR}/{LEG} CKPT={CKPT} subdir={subdir} exists={os.path.isdir(sh)}", flush=True)
        try:
            print(f"[ckptread] CKPT dir listing: {sorted(os.listdir(CKPT))}", flush=True)
        except Exception:  # noqa: BLE001
            pass
        try:
            ana, ck = _read_last_iters(sh)
            print(f"[ckptread] read_last_iteration: analysis={ana} checkpoint(resume)={ck} -> a restart would "
                  f"{'RESUME at %d' % ck if (ck or 0) > 0 else 'RE-EQUILIBRATE'}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[ckptread] read_last_iteration failed: {e!r}", flush=True)
        # RAW netCDF coverage of each file.
        try:
            import netCDF4
            import numpy as _np
            for label, fn in (("analysis", "simulation.nc"), ("checkpoint", "checkpoint.chk")):
                fp = os.path.join(sh, fn)
                if not os.path.isfile(fp):
                    print(f"[ckptread]   {label} {fn}: MISSING", flush=True)
                    continue
                ds = netCDF4.Dataset(fp, "r")
                try:
                    dims = {d: (len(ds.dimensions[d]) if not ds.dimensions[d].isunlimited()
                                else f"UNLIM={len(ds.dimensions[d])}") for d in ds.dimensions}
                    # Which iterations actually hold data? Probe a representative per-iteration variable and count
                    # leading iteration-slots that are NOT fully masked/fill — that is the real coverage.
                    cov = "n/a"
                    for vn in ("positions", "box_vectors", "energies", "states"):
                        if vn in ds.variables:
                            v = ds.variables[vn]
                            try:
                                a = v[:]
                                n = a.shape[0]
                                flat = a.reshape(n, -1)
                                if hasattr(flat, "mask") and flat.mask is not _np.ma.nomask:
                                    has = ~flat.mask.all(axis=1)
                                else:
                                    has = _np.isfinite(_np.asarray(flat, dtype=float)).any(axis=1)
                                idx = [int(i) for i in _np.where(has)[0]]
                                head = idx[:6]
                                tail = idx[-3:] if len(idx) > 9 else []
                                cov = (f"var={vn} slots={n} filled={len(idx)} "
                                       f"iters={head}{'...'+str(tail) if tail else ''}")
                                break
                            except Exception as ee:  # noqa: BLE001
                                cov = f"var={vn} probe-failed {ee!r}"
                    print(f"[ckptread]   {label} {fn}: size={os.path.getsize(fp)}B dims={dims} "
                          f"vars={list(ds.variables)[:10]}", flush=True)
                    print(f"[ckptread]   {label} coverage: {cov}", flush=True)
                finally:
                    ds.close()
        except Exception as e:  # noqa: BLE001
            print(f"[ckptread]   raw netCDF probe failed: {e!r}", flush=True)
        return
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
