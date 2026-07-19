#!/usr/bin/env python3
"""Ternary-COOPERATIVITY compute engine (Track B) — relative-alchemical morph in a binary vs ternary environment.

Runs ONE (leg, replica) alchemical MORPH (A→B) of a PROTAC/degrader analogue pair in ONE environment via OpenFE
(RelativeHybridTopologyProtocol) — the same validated hybrid-topology + LOMAP + MBAR machinery the binary RBFE
engine (nr4a3_rbfe.py) uses, so we do NOT hand-roll dual-topology soft-core. The ONLY differences vs the binary
RBFE are (1) the chemical system is an E3-machinery assembly (VHL + Elongin B/C [+ target LBD]) rather than a
single receptor, and (2) three environments are supported per morph:

    solvent      : ligand in water (the shared morph reference; cancels in the coop cycle but makes each
                   environment's ddG a proper RELATIVE BINDING free energy → the recruitment read-out is defined)
    binary_<e3>  : E3 machinery + PROTAC, NO target  (ddG_alch,binary)
    ternary_<t>  : E3 machinery + target LBD + PROTAC (ddG_alch,ternary)

Cooperativity is then the binary-vs-ternary cycle (ternary_coop.ddg_coop; prereg §1):
    ddG_alch,binary  = ΔG_binary_morph  − ΔG_solvent_morph
    ddG_alch,ternary = ΔG_ternary_morph − ΔG_solvent_morph
    ddG_coop         = ddG_alch,ternary − ddG_alch,binary        (= ΔG_ternary_morph − ΔG_binary_morph)
The reducer (ternary_fep_reduce.py) forms these from the per-leg checkpoints across ≥3 replicas (replicate-SD
error, per prereg — NOT MBAR SE) and emits records the ternary_coop_io schema + ternary_coop_gate consume.

HONESTY / SHAKEOUT (standing rules). This engine cannot run in the dev sandbox (no OpenFE/OpenMM) — heavy deps
import lazily so the file loads on CPU for the pure leg-planning helpers + tests. It is UNVALIDATED until a GPU
`mode=smoke` (env solve + assembly + mapping + hybrid-topology build, no MD) then a single real pilot leg pass.
No α/ΔG/GPU-hour is asserted here. Starting structures (the assembled complex PDBs + posed PROTAC SDFs) are
staged inputs produced upstream by the co-fold benchmark (nrv04_ternary.py); the calibration morph endpoints
stay `pending` until the Layer-1 calib pair is frozen (no fabrication).

Env: MODE (smoke|run|reduce), LEG_ID (a frozen/derived pilot leg id), SEED (replica index), DIRECTION
(fwd|rev), N_WINDOWS, N_ITER, INPUT_DIR (mounts <leg>/complex.pdb + <leg>/ligands.sdf), OUTPUT_DIR/CKPT_DIR.
"""
import glob
import json
import os
import sys

import ternary_coop as tcoop
import ternary_coop_prep as prep

# Reuse the binary RBFE engine's hard-won, GPU-validated low-level helpers (single source of truth for the
# OpenMM platform probe, LOMAP/Kartograf mapping, and docked-pose repair — all pose/engine logic, no ligand
# identity baked in). Importing is CPU-safe: nr4a3_rbfe imports openfe lazily inside its functions.
import nr4a3_rbfe as rbfe

IN = os.environ.get("INPUT_DIR", "/opt/ml/processing/input")
CKPT = os.environ.get("CKPT_DIR", os.environ.get("OUTPUT_DIR", "/opt/ml/checkpoints"))
LEG_ID = os.environ.get("LEG_ID", "nrv04_active_to_epimer__binary_vhl")
SEED = int(os.environ.get("SEED", "0"))
DIRECTION = os.environ.get("DIRECTION", "fwd")        # rev = B→A, for a forward/reverse hysteresis check
N_WINDOWS = int(os.environ.get("N_WINDOWS", "16"))
N_ITER = int(os.environ.get("N_ITER", "1000"))


# =============================================================================================================
# pure leg planning (importable on CPU; used by the submitter, reducer, and tests)
# =============================================================================================================
def _environment_of(leg_id):
    """binary | ternary | solvent, inferred from a leg id suffix."""
    if leg_id.endswith("__solvent"):
        return "solvent"
    spec = tcoop.PILOT_LEG_MAP.get(leg_id)
    return spec["environment"] if spec else ("ternary" if "__ternary" in leg_id else "binary")


def _morph_key(leg_id):
    """The morph prefix shared by a compound pair's solvent/binary/ternary legs (everything before the env
    suffix). e.g. nrv04_active_to_epimer__binary_vhl → nrv04_active_to_epimer."""
    for sep in ("__binary", "__ternary", "__solvent"):
        if sep in leg_id:
            return leg_id.split(sep, 1)[0]
    return leg_id


def solvent_leg_id(leg_id):
    """The shared solvent-morph leg id for a leg's morph pair."""
    return "%s__solvent" % _morph_key(leg_id)


def expand_pilot_legs():
    """The full set of legs the pilot must run: the 4 FROZEN environment legs (ternary_coop.PILOT_LEG_MAP) +
    one shared SOLVENT leg per distinct morph (derived; 'extra' legs, allowed by the gate's required-subset
    rule). The solvent reference makes each environment ddG a relative BINDING free energy → recruitment is
    defined; it cancels in ddG_coop = ternary − binary, so it never distorts the coupling term."""
    frozen = tcoop.load_pilot_legs()                       # fails closed on drift vs the frozen JSON
    ids = [leg["id"] for leg in frozen]
    solvent = sorted({solvent_leg_id(i) for i in ids})
    return ids + solvent


def leg_spec(leg_id):
    """Resolve a leg id (frozen or derived-solvent) to its assembly/morph spec via ternary_coop_prep. For a
    solvent leg we borrow the morph endpoints of any environment leg of the same pair (the ligands are identical;
    only the protein context differs)."""
    env = _environment_of(leg_id)
    if leg_id in tcoop.PILOT_LEG_MAP:
        leg = dict(id=leg_id, **tcoop.PILOT_LEG_MAP[leg_id])
    else:
        # derived solvent leg: clone a sibling environment leg's morph, drop the protein/target
        morph = _morph_key(leg_id)
        sib = next((i for i in tcoop.PILOT_LEG_MAP if _morph_key(i) == morph), None)
        if sib is None:
            raise ValueError("cannot resolve morph for derived leg %r" % leg_id)
        leg = dict(tcoop.PILOT_LEG_MAP[sib], id=leg_id, environment="solvent", target=None,
                   purpose="shared solvent-morph reference for %s (relative-binding denominator)" % morph)
    return leg, env


def _morph_endpoints(leg):
    """(endpoint_a, endpoint_b, smiles_a, smiles_b) for a leg's morph, resolved via the prep layer (network
    only for NR-V04; calib stays pending). DIRECTION=rev swaps A/B for a forward/reverse hysteresis leg."""
    m = prep._morph_endpoints(leg, resolve_smiles=True)
    a, b, sa, sb = m["endpoint_a"], m["endpoint_b"], m["smiles_a"], m["smiles_b"]
    if DIRECTION == "rev":
        a, b, sa, sb = b, a, sb, sa
    if sa is None or sb is None:
        raise SystemExit("  ABORT: unresolved morph endpoints for %s (status=%s). Calibration endpoints are "
                         "PENDING the frozen Layer-1 calib pair; NR-V04 needs network SMILES resolution."
                         % (leg["id"], m.get("status")))
    return a, b, sa, sb


# =============================================================================================================
# OpenFE build (mirrors nr4a3_rbfe; the only new piece is the E3-machinery ChemicalSystem)
# =============================================================================================================
def _canon_smiles(x, rdkit_chem):
    """Canonical isomeric SMILES of an RDKit mol or a SMILES string (None-safe)."""
    m = x if hasattr(x, "GetNumAtoms") else rdkit_chem.MolFromSmiles(x)
    if m is None:
        return None
    try:
        return rdkit_chem.MolToSmiles(rdkit_chem.RemoveHs(m))
    except Exception:  # noqa: BLE001
        return rdkit_chem.MolToSmiles(m)


def _pyridine_to_benzene_pose(mol, rdkit_chem):
    """Mutate the UNIQUE aromatic 6-membered single-N ring (pyridine) N -> CH in place, PRESERVING 3D coords, to
    build the benzene-linker analogue pose (Wurz cmpd1 crystal pose -> cmpd4). This is the ligand-level analogue
    of the SMARCA4->SMARCA2 residue substitution: an N->C element change cannot be done by bond-order repair. The
    ring atom keeps its position (N and C are near-identical size); the added H is placed by AddHs(addCoords).
    Returns None if the molecule does not have exactly one pyridine (so the caller fails closed)."""
    m = rdkit_chem.RWMol(mol)
    try:
        rdkit_chem.SanitizeMol(m)
    except Exception:  # noqa: BLE001
        pass
    ri = m.GetRingInfo()
    cand = []
    for ring in ri.AtomRings():
        if len(ring) != 6:
            continue
        atoms = [m.GetAtomWithIdx(i) for i in ring]
        if not all(a.GetIsAromatic() for a in atoms):
            continue
        ns = [a.GetIdx() for a in atoms if a.GetSymbol() == "N"]
        if len(ns) == 1:
            cand.append(ns[0])
    if len(cand) != 1:
        return None
    at = m.GetAtomWithIdx(cand[0])
    at.SetAtomicNum(6)
    at.SetNumExplicitHs(0)
    at.SetNoImplicit(False)
    out = m.GetMol()
    try:
        rdkit_chem.SanitizeMol(out)
        out = rdkit_chem.AddHs(out, addCoords=True)
    except Exception:  # noqa: BLE001
        return None
    return out


def _endpoint_pose(sdf, name, target_smiles, base_smiles, rdkit_chem):
    """Build the 3D pose for endpoint `name` so it MATCHES target_smiles, starting from the crystal pose (whose
    true identity is base_smiles — the co-crystallized ligand, e.g. Wurz cmpd1). If target == base, bond-order
    repair suffices (e.g. calib_hi = cmpd1). If target differs by an ELEMENT change (calib_lo = cmpd4, linker
    pyridine N->CH), bond-order repair CANNOT convert N->C, so mutate the pose (pyridine->benzene) then repair.
    Verifies the built pose's canonical SMILES equals the target and FAILS CLOSED otherwise — never runs a leg on
    the wrong molecule (this is the bug the 5-part gate's endpoints_match check caught)."""
    base = rbfe._sdf_mol(sdf, name, base_smiles, rdkit_chem)
    clean = rbfe._repair_pose(base, base_smiles, rdkit_chem)
    want = _canon_smiles(target_smiles, rdkit_chem)
    if _canon_smiles(clean, rdkit_chem) == want:
        return clean                                     # target == crystal identity (calib_hi = cmpd1)
    mut = _pyridine_to_benzene_pose(clean, rdkit_chem)   # element-change endpoint (cmpd4 benzene linker)
    if mut is not None:
        mut = rbfe._repair_pose(mut, target_smiles, rdkit_chem)
        if _canon_smiles(mut, rdkit_chem) == want:
            return mut
    raise SystemExit("  ABORT: endpoint %s could not be built to match its target SMILES (element-change pose "
                     "mutation failed) — refusing a wrong-molecule leg." % name)


def _build_components(openfe, rdkit_chem, leg, env, endpoints):
    """Ligand A/B SmallMoleculeComponents (from the posed PROTAC SDF) + the assembled ProteinComponent for a
    binary/ternary leg (None for solvent). The complex PDB is the co-folded/assembled starting structure staged
    at <IN>/<leg_id>/complex.pdb (E3 machinery [+ target]); the two posed PROTAC endpoints at ligands.sdf. BOTH
    endpoints are staged from the SAME crystal pose (the co-crystallized ligand = calib_hi's SMILES sa); each is
    built to match its own target, mutating element changes (e.g. cmpd1->cmpd4 linker N->CH) so neither is a
    wrong-molecule/null endpoint."""
    a, b, sa, sb = endpoints
    lig_dir = os.path.join(IN, leg["id"])
    sdf = os.path.join(lig_dir, "ligands.sdf")
    if not os.path.exists(sdf):
        sdf = next(iter(glob.glob(os.path.join(IN, "**", "ligands.sdf"), recursive=True)), sdf)
    molA = _endpoint_pose(sdf, a, sa, sa, rdkit_chem)    # crystal identity = sa (calib_hi = cmpd1)
    molB = _endpoint_pose(sdf, b, sb, sa, rdkit_chem)    # cmpd1 pose -> cmpd4 (element-change mutation)
    ligA = openfe.SmallMoleculeComponent.from_rdkit(molA)
    ligB = openfe.SmallMoleculeComponent.from_rdkit(molB)
    protein = None
    if env in ("binary", "ternary"):
        pdb = os.path.join(lig_dir, "complex.pdb")
        if not os.path.exists(pdb):
            pdb = next(iter(glob.glob(os.path.join(IN, "**", "%s" % os.path.join(leg["id"], "complex.pdb")),
                                      recursive=True)), pdb)
        if not os.path.exists(pdb):
            raise SystemExit("  ABORT: missing assembled complex PDB for %s at %s (stage the co-folded "
                             "E3%s starting structure first)." % (leg["id"], pdb,
                             "+target" if env == "ternary" else "-only"))
        protein = openfe.ProteinComponent.from_pdb_file(pdb)
    return ligA, ligB, protein


def _protocol(openfe):
    """OpenFE RelativeHybridTopologyProtocol settings for a ternary morph. protocol_repeats=1 PER JOB — the
    prereg's ≥3 replicas come from THREE independent jobs (SEED=0/1/2), each a single repeat, so the reducer
    forms a genuine replicate-SD (not an MBAR SE). Everything else mirrors nr4a3_rbfe._protocol (am1bcc charges
    via AmberTools — MUST match the binary engine for the coop cycle; CUDA→OpenCL platform probe, MD lengths as
    openff Quantities)."""
    from openfe.protocols.openmm_rfe import RelativeHybridTopologyProtocol
    s = RelativeHybridTopologyProtocol.default_settings()
    for setter, why in ((lambda: setattr(s, "protocol_repeats", 1), "protocol_repeats"),):
        try:
            setter()
        except Exception as e:  # noqa: BLE001
            print("  [tfep] WARN %s (%s)" % (why, e), flush=True)
    try:
        s.lambda_settings.lambda_windows = N_WINDOWS
        s.simulation_settings.n_replicas = N_WINDOWS      # OpenFE requires n_replicas == n λ-windows
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN windows→%d (%s); using default" % (N_WINDOWS, e), flush=True)
    # EXACT-HAMILTONIAN EQUILIBRATION LADDER (reviewer condition 2, 2026-07-19). The plain-MD pre-equilibration
    # (ternary_preequil) is only a COORDINATE CONDITIONER — a different (relaxation) force field, no alchemy — so
    # it does NOT sample the RBFE target ensemble and its output is NEVER used as production data. Under THIS
    # exact Hamiltonian, OpenFE's RelativeHybridTopologyProtocol per-window pipeline is: minimize
    # (minimization_steps) -> equilibrate for equilibration_length -> collect production_length for MBAR, with the
    # equilibration frames DISCARDED from MBAR by construction (only production frames enter the estimator). So
    # equilibration_length>0 is the reviewer-required "discarded unrestrained equilibration before MBAR". The
    # pre-equil conditioner is NOT part of protocol_signature equality (it is a starting-coordinate choice, like
    # the per-replica seed) — the physical-endpoint stability of the conditioned coords under this exact FF is
    # verified separately by ternary_endpoint_stability (MODE=endpoint_smoke).
    try:
        from openff.units import unit as _ou
        s.simulation_settings.equilibration_length = EQUILIBRATION_NS * _ou.nanosecond
        s.simulation_settings.production_length = PRODUCTION_NS * _ou.nanosecond
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN MD lengths (%s); using defaults" % e, flush=True)
    # STARTING-STRUCTURE / TIMESTEP ROBUSTNESS (2026-07-18). The warmup NaN is NOT a starting-structure clash —
    # a CPU clash census of the assembled complex (ternary_stage_validate._clash_check) proved it clean (worst
    # protein-protein non-bonded = a 1.33 A peptide bond; worst protein<->ligand = 1.59 A H-bond). The NaN is
    # state-1-specific (first alchemical window), survives 25000 minimization steps, and reproduces at 2 fs — the
    # signature of an UNCONSTRAINED alchemical C-H. The cmpd1->cmpd4 edge is an N->CH change, so the growing C-H
    # bond exists in state B but not A; a bond whose constraint CHANGES between endpoints is left UNCONSTRAINED by
    # OpenFE's hybrid factory, and an unconstrained C-H (period ~10 fs) is unstable at 2 fs once the softcore turns
    # on at state 1. Fix: a 1 fs step (RBFE_TIMESTEP_FS=1.0) is safe for the unconstrained C-H. minimization_steps
    # kept high (cheap insurance). Both env-overridable. (rbfe_spot_driver instruments the NaN: on catch it loads
    # openmmtools' saved nan-error-logs state and names the offending atoms.)
    try:
        s.simulation_settings.minimization_steps = int(os.environ.get("RBFE_MIN_STEPS", "25000"))
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN minimization_steps (%s)" % e, flush=True)
    try:
        from openff.units import unit as _ou2
        _dt_fs = float(os.environ.get("RBFE_TIMESTEP_FS", "2.0"))
        s.integrator_settings.timestep = _dt_fs * _ou2.femtosecond
        print("  [tfep] timestep=%.1f fs, minimization_steps=%s (NaN-robust start)"
              % (_dt_fs, s.simulation_settings.minimization_steps), flush=True)
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN timestep (%s); using default" % e, flush=True)
    try:
        # PRIME (CPU pre-bake) runs on a GPU-less CI runner and never reaches MD — force CPU so the CUDA probe
        # (which would try to create a CUDA context) can't fail. The serialized System is platform-agnostic, so
        # the cache this produces is identical to a GPU-built one and valid for the GPU run.
        _plat = "CPU" if os.environ.get("RBFE_PRIME_ONLY") == "1" else "CUDA"
        s.engine_settings.compute_platform = rbfe._working_platform_name(_plat)
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN compute_platform (%s)" % e, flush=True)
    # Charges MUST match the binary RBFE engine (am1bcc via AmberTools, now that ambertools>=23 is in the env):
    # ddG_coop subtracts the binary and ternary morphs, so a charge-model mismatch between them would break the
    # cycle's cancellation. Same CHARGE_METHOD override as nr4a3_rbfe (set CHARGE_METHOD=nagl to fall back).
    _charge = os.environ.get("CHARGE_METHOD", "am1bcc")
    try:
        s.partial_charge_settings.partial_charge_method = _charge
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN charges=%s (%s); using default" % (_charge, e), flush=True)
    print("  [tfep] partial_charge_method = %s (must match binary RBFE)" % _charge, flush=True)
    # seed the sampler per replica where the attribute exists, so SEED=0/1/2 are genuinely independent
    for path in ("simulation_settings", "integrator_settings"):
        try:
            sub = getattr(s, path)
            for attr in ("random_seed", "sampler_seed"):
                if hasattr(sub, attr):
                    setattr(sub, attr, SEED)
        except Exception:  # noqa: BLE001
            pass
    return RelativeHybridTopologyProtocol(s)


EQUILIBRATION_NS = 1.0
PRODUCTION_NS = 5.0


def protocol_signature():
    """FROZEN protocol signature (reviewer required change #3, 2026-07-17). A sha256 over the PHYSICS knobs that
    must be IDENTICAL across every leg of the coop cycle (binary/ternary/solvent) so ΔΔG_coop's cancellation is
    exact. The per-replica random SEED is DELIBERATELY EXCLUDED — replicas are meant to differ by seed ONLY, so
    the seed is not part of protocol equality. run_leg records this hash on every leg JSON; the reducer asserts
    all legs share one hash (a mismatch = a leg ran under different physics → the cycle is invalid)."""
    import hashlib
    payload = {
        "engine": "RelativeHybridTopologyProtocol",
        "n_windows": N_WINDOWS, "n_replicas": N_WINDOWS, "protocol_repeats": 1,
        "equilibration_ns": EQUILIBRATION_NS, "production_ns": PRODUCTION_NS,
        "charge_method": os.environ.get("CHARGE_METHOD", "am1bcc"),
        "minimization_steps": int(os.environ.get("RBFE_MIN_STEPS", "25000")),
        "timestep_fs": float(os.environ.get("RBFE_TIMESTEP_FS", "2.0")),
        "mapping": "lomap_prefer_element_change",
    }
    h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return h, payload


def _chemical_systems(openfe, ligA, ligB, protein, env):
    solvent = openfe.SolventComponent()
    if env in ("binary", "ternary"):
        A = openfe.ChemicalSystem({"protein": protein, "ligand": ligA, "solvent": solvent})
        B = openfe.ChemicalSystem({"protein": protein, "ligand": ligB, "solvent": solvent})
    else:
        A = openfe.ChemicalSystem({"ligand": ligA, "solvent": solvent})
        B = openfe.ChemicalSystem({"ligand": ligB, "solvent": solvent})
    return A, B


def assert_constitutional_edge(smiles_a, smiles_b):
    """NULL-MAP GUARD (reviewer 2026-07-17 Option-4). Forbid a morph whose two endpoints share the SAME 2D
    constitution — i.e. they differ ONLY by stereochemistry, or are identical. Such an edge is a NULL alchemical
    transformation under a complete single-topology map: the endpoints have identical force-field parameters and
    every atom maps 1:1, so the hybrid Hamiltonian is unchanged and no real ddG can be recovered. This is the
    VERIFIED PROTAC 2 -> cis-PROTAC 2 failure mode. The production RBFE/ternary morph MUST be a genuine
    CONSTITUTIONAL change (e.g. Wurz cmpd1->cmpd4, a linker pyridine N->CH). Stereo-only transformations require a
    bespoke partial/dummy map (future methods-development work), NEVER this production protocol. Raises SystemExit
    if the edge is stereo-only/identity; returns a small dict of evidence otherwise. Pure RDKit — unit-testable."""
    from rdkit import Chem
    ma, mb = Chem.MolFromSmiles(smiles_a), Chem.MolFromSmiles(smiles_b)
    if ma is None or mb is None:
        raise SystemExit("  ABORT (null-map guard): an endpoint SMILES did not parse.")
    flat_a = Chem.MolToSmiles(ma, isomericSmiles=False)
    flat_b = Chem.MolToSmiles(mb, isomericSmiles=False)
    if flat_a == flat_b:
        raise SystemExit(
            "  ABORT (null-map guard): endpoints A and B share the SAME 2D constitution (differ only by "
            "stereochemistry, or identical). A complete-map single-topology RBFE of such an edge is a NULL "
            "transformation (identical FF parameters, every atom mapped) and cannot recover a real ddG — the "
            "verified PROTAC 2->cis-PROTAC 2 failure mode. valB requires a GENUINE constitutional edge "
            "(e.g. Wurz cmpd1->cmpd4). Stereo-only edges need a bespoke partial/dummy map, not this protocol.")
    return {"constitutional_edge": True, "flat_a": flat_a, "flat_b": flat_b}


def _five_part_gate(Chem, leg, env, ligA, ligB, mapping, protein, endpoints, built, endpoints_ok):
    """Record the reviewer's 5-part $0 pre-spend gate (2026-07-17 Option-1) into the smoke artifact so GPU
    execution is authorized only when every item is satisfiable. Items 1/2/5 are fully in-leg; items 3/4 record
    the per-leg evidence (atom-map + E3-construct signature; staging-model manifest) that the reducer/staging
    verify for cross-leg equality. Returns {item_N: {...}, all_pass: bool}."""
    import hashlib

    a, b, sa, sb = endpoints
    built_a, built_b, want_a, want_b = built
    rmA, rmB = ligA.to_rdkit(), ligB.to_rdkit()
    a2b = dict(mapping.componentA_to_componentB)

    def _flat(s):
        m = Chem.MolFromSmiles(s) if s else None
        return Chem.MolToSmiles(m, isomericSmiles=False) if m is not None else None

    # ---- item 1: chemical identity -------------------------------------------------------------------------
    flat_a, flat_b = _flat(built_a), _flat(built_b)
    not_graph_identical = bool(flat_a and flat_b and flat_a != flat_b)
    item1 = {"built_A_matches_published": built_a == want_a, "built_B_matches_published": built_b == want_b,
             "A_and_B_not_graph_identical_after_stereo_removal": not_graph_identical,
             "pass": bool(endpoints_ok and not_graph_identical)}

    # ---- item 2: non-null map (real element/parameter perturbation; no unintended stereocenter change) ------
    elem_changes = sorted({"%s->%s" % (rmA.GetAtomWithIdx(ia).GetSymbol(), rmB.GetAtomWithIdx(ib).GetSymbol())
                           for ia, ib in a2b.items()
                           if rmA.GetAtomWithIdx(ia).GetSymbol() != rmB.GetAtomWithIdx(ib).GetSymbol()})
    n_unmapped_a = rmA.GetNumAtoms() - len(a2b)
    n_unmapped_b = rmB.GetNumAtoms() - len(set(a2b.values()))
    has_real_perturbation = bool(elem_changes) or n_unmapped_a > 0 or n_unmapped_b > 0

    def _nsc(m):
        return len(Chem.FindMolChiralCenters(m, useLegacyImplementation=False, includeUnassigned=True))
    sc_a, sc_b = _nsc(rmA), _nsc(rmB)
    stereocenters_preserved = sc_a == sc_b            # a linker N->CH must NOT add/remove a stereocenter
    n2c = any(set(ec.split("->")) == {"N", "C"} for ec in elem_changes)
    item2 = {"element_changes_in_map": elem_changes, "linker_N_to_C_present": n2c,
             "n_unmapped_A": n_unmapped_a, "n_unmapped_B": n_unmapped_b,
             "has_real_element_or_dummy_perturbation": has_real_perturbation,
             "n_stereocenters_A": sc_a, "n_stereocenters_B": sc_b,
             "no_unintended_stereocenter_change": stereocenters_preserved,
             "pass": bool(has_real_perturbation and stereocenters_preserved)}

    # ---- item 3: environment consistency (same atom map + shared E3/PROTAC construct across binary & ternary)
    map_sig = {"n_mapped": len(a2b), "n_unmapped_A": n_unmapped_a, "n_unmapped_B": n_unmapped_b,
               "element_changes": elem_changes,
               "pairs_hash": hashlib.sha256(repr(sorted(a2b.items())).encode()).hexdigest()[:16]}
    e3 = [c for c in prep._e3_components(with_vbc=True)]
    construct_sig = {"e3_components": e3, "environment": env,
                     "has_target": protein is not None and env == "ternary"}
    item3 = {"atom_map_signature": map_sig, "e3_construct_signature": construct_sig,
             "note": "The reducer MUST verify the atom_map_signature (pairs_hash) and e3_construct_signature are "
                     "IDENTICAL across the binary and ternary legs (reviewer item 3). Recorded per-leg here.",
             "pass": True}   # in-leg record; cross-leg equality enforced at reduce (ternary_fep_reduce)

    # ---- item 4: starting-model declaration (8G1Q -> SMARCA2 substitution + relax; >=2 models; divergence) --
    manifest = None
    for cand in (os.path.join(IN, LEG_ID, "staging_manifest.json"),
                 os.path.join(IN, "staging_manifest.json")):
        if os.path.exists(cand):
            try:
                manifest = json.load(open(cand))
            except Exception:  # noqa: BLE001
                manifest = None
            break
    if env == "ternary":
        n_models = (manifest or {}).get("n_relaxed_models")
        div_ok = (manifest or {}).get("divergence_ok")
        item4 = {"template_pdb": (manifest or {}).get("template_pdb"),
                 "is_smarca2_crystal": (manifest or {}).get("is_smarca2_crystal"),
                 "n_relaxed_models": n_models, "divergence_ok": div_ok,
                 "smarca4_to_smarca2_substituted": (manifest or {}).get("smarca4_to_smarca2_substituted"),
                 "limitation_recorded": bool((manifest or {}).get("limitation")),
                 "pass": bool(manifest and n_models and n_models >= 2 and div_ok
                              and (manifest or {}).get("smarca4_to_smarca2_substituted"))}
    else:
        item4 = {"pass": True, "note": "binary leg — no SMARCA2 target model (item 4 applies to the ternary leg)."}

    # ---- item 5: preregistration correction (alpha_SPR label; +0.94 target; SMARCA2-model limitation) -------
    frozen = prep._load_calib_frozen() or {}
    pt = frozen.get("preregistered_target", {})
    sm = frozen.get("starting_model", {})
    assay_is_spr = "SPR" in (pt.get("assay") or "").upper()
    target_ok = abs((pt.get("ddG_coop_exp_kcal_per_mol") or 0) - 0.94) < 0.05
    item5 = {"assay_label": pt.get("assay"), "assay_is_SPR_not_TRFRET": assay_is_spr,
             "target_kcal": pt.get("ddG_coop_exp_kcal_per_mol"), "target_is_plus_0p94": target_ok,
             "smarca2_model_limitation_recorded": bool(sm.get("limitation")),
             "pass": bool(assay_is_spr and target_ok and sm.get("limitation"))}

    items = {"item1_chemical_identity": item1, "item2_non_null_map": item2,
             "item3_environment_consistency": item3, "item4_starting_model": item4,
             "item5_preregistration": item5}
    items["all_pass"] = all(v["pass"] for v in items.values())   # only item* dicts carry "pass"
    return items


def run_leg():
    os.makedirs(CKPT, exist_ok=True)
    import openfe
    from rdkit import Chem
    leg, env = leg_spec(LEG_ID)
    a, b, sa, sb = _morph_endpoints(leg)
    # NULL-MAP GUARD before any build/spend: fail closed on a stereo-only/identity edge (the retired epimer mode).
    assert_constitutional_edge(sa, sb)
    print("[tfep] LEG=%s env=%s morph=%s->%s dir=%s seed=%d" % (LEG_ID, env, a, b, DIRECTION, SEED), flush=True)
    ligA, ligB, protein = _build_components(openfe, Chem, leg, env, (a, b, sa, sb))
    # prefer_element_change: the calib edge is a single-ring-atom element change (cmpd1 pyridine N -> cmpd4
    # benzene C); take the near-complete element_change=True map (N<->C alchemical), not the degenerate strict map.
    mapping = rbfe._mapping(openfe, ligA, ligB, prefer_element_change=True)
    n_mapped = len(mapping.componentA_to_componentB)
    # Positively confirm the ACTUAL built molecules are the intended endpoints (the LOMAP log alone is
    # unverifiable — the mapper's name string can leak stale globals). Canonicalize the built ligands and the
    # requested SMILES so a smoke definitively shows WHICH chemistry it ran (e.g. PROTAC_2 -> cis-PROTAC_2).
    def _canon(s):
        m = Chem.MolFromSmiles(s) if s else None
        return Chem.MolToSmiles(m) if m is not None else None
    built_a = _canon(Chem.MolToSmiles(Chem.RemoveHs(ligA.to_rdkit())))
    built_b = _canon(Chem.MolToSmiles(Chem.RemoveHs(ligB.to_rdkit())))
    want_a, want_b = _canon(sa), _canon(sb)
    endpoints_ok = (built_a == want_a) and (built_b == want_b)
    print("  [tfep] endpoints: A=%s B=%s | built matches requested SMILES: %s" % (a, b, endpoints_ok), flush=True)
    print("  [tfep] mapped %d atoms A->B" % n_mapped, flush=True)

    if os.environ.get("MODE") == "smoke":
        proto = _protocol(openfe)
        A, B = _chemical_systems(openfe, ligA, ligB, protein, env)
        dag = proto.create(stateA=A, stateB=B, mapping=mapping)
        # EXECUTE the HybridTopologySetupUnit (no MD) so smoke actually reaches OpenMM ForceField.createSystem —
        # the step that failed on valB seed-0 (missing protein H). proto.create() only BUILDS the DAG lazily and
        # never runs a unit, which is why the $0 gate missed it. Running setup here (CPU, cheap) makes the gate
        # validate that the assembled+hydrogenated complex parameterizes before any paid sampling. Fail-loud.
        setup_ok = None
        setup_err = None
        if protein is not None:
            try:
                from pathlib import Path as _P

                from gufe import Context as _Context
                _byname = {}
                for _u in dag.protocol_units:
                    _byname.setdefault(type(_u).__name__, []).append(_u)
                _sh = _P(CKPT) / "smoke_setup_shared"; _sc = _P(CKPT) / "smoke_setup_scratch"
                _sh.mkdir(parents=True, exist_ok=True); _sc.mkdir(parents=True, exist_ok=True)
                try:
                    _ctx = _Context(shared=_sh, scratch=_sc)
                except TypeError:
                    _ctx = _Context(shared=_sh, scratch=_sc, permanent=_sh)
                _su = (_byname.get("HybridTopologySetupUnit") or [None])[0]
                if _su is None:
                    raise SystemExit("no HybridTopologySetupUnit in DAG (openfe>=1.12?)")
                _su.execute(context=_ctx, raise_error=True)
                setup_ok = True
                print("  [tfep] SMOKE setup-unit OK — OpenMM system parameterized (protein hydrogens present).",
                      flush=True)
            except Exception as _e:  # noqa: BLE001
                setup_ok = False
                setup_err = ("%s: %s" % (type(_e).__name__, _e))[:400]
                print("  [tfep] SMOKE setup-unit FAILED — %s" % setup_err, flush=True)
        gate = _five_part_gate(Chem, leg, env, ligA, ligB, mapping, protein,
                               (a, b, sa, sb), (built_a, built_b, want_a, want_b), endpoints_ok)
        gate["item6_openmm_system_built"] = {"ran_setup_unit": protein is not None,
                                             "system_parameterized": setup_ok, "error": setup_err}
        if setup_ok is False:
            gate["all_pass"] = False
        json.dump({"smoke": "ok", "leg": LEG_ID, "environment": env, "n_mapped_atoms": n_mapped,
                   "has_protein": protein is not None,
                   "endpoint_a": a, "endpoint_b": b,
                   "built_smiles_a": built_a, "built_smiles_b": built_b,
                   "requested_smiles_a": want_a, "requested_smiles_b": want_b,
                   "endpoints_match_requested": endpoints_ok,
                   "n_protocol_units": len(getattr(dag, "protocol_units", []) or []),
                   "setup_unit_system_built": setup_ok,
                   "protocol_hash": protocol_signature()[0],
                   "gate": gate, "gate_all_pass": gate["all_pass"]},
                  open(os.path.join(CKPT, "smoke.json"), "w"), indent=2)
        print("  [tfep] SMOKE ok — env solves, %s assembly + mapping + hybrid topology build "
              "(endpoints_match=%s, gate_all_pass=%s)." % (env, endpoints_ok, gate["all_pass"]), flush=True)
        return

    proto = _protocol(openfe)
    A, B = _chemical_systems(openfe, ligA, ligB, protein, env)
    dag = proto.create(stateA=A, stateB=B, mapping=mapping)
    # SPOT-SAFE (trimcrae standing rule: everything we run must be spot-safe). Instead of the welded execute_DAG
    # (which restarts the expensive MD from zero on every spot preemption — the valB ternary leg lost all work
    # TWICE this way), drive the hybrid-topology DAG through rbfe.execute_hybrid_dag_spot_safe, which commits the
    # MultiState sampling per interval to a versioned GCS/S3 CommitStore and RESUMES from the last committed
    # iteration on re-dispatch. Same battle-tested path valA survived 9 preemptions on.
    tag = "%s_%s_r%d" % (LEG_ID, DIRECTION, SEED)
    proto_hash, proto_payload = protocol_signature()
    # starting-model provenance per ternary replicate (reviewer #3): read the model index the stager chose for
    # THIS seed from the leg's staging_manifest.json (ternary_pdb_stage records starting_model_index = SEED % n).
    starting_model = None
    try:
        _man = json.load(open(os.path.join(IN, leg["id"], "staging_manifest.json")))
        starting_model = _man.get("starting_model")
    except Exception:  # noqa: BLE001
        starting_model = None
    dg_kcal, unc_kcal, _ana_keys = rbfe.execute_hybrid_dag_spot_safe(proto, dag, CKPT, tag)
    if isinstance(_ana_keys, dict) and _ana_keys.get("primed"):
        # PRIME (CPU pre-bake): setup was built + cached to GCS and we exited before MD. Write a small marker so the
        # CPU workflow can report success; a GPU run will restore the cache and run the actual leg.
        json.dump({"primed": True, "leg_id": LEG_ID, "environment": env, "direction": DIRECTION, "seed": SEED,
                   "cache_dir": _ana_keys.get("cache_dir"), "n_particles": _ana_keys.get("n_particles"),
                   "protocol_hash": proto_hash},
                  open(os.path.join(CKPT, "prime_%s_%s_r%d.json" % (LEG_ID, DIRECTION, SEED)), "w"), indent=2)
        print("  [tfep] PRIME DONE %s: setup cached to %s (%s particles) — GPU run will skip setup." % (
            LEG_ID, _ana_keys.get("cache_dir"), _ana_keys.get("n_particles")), flush=True)
        return
    out = {"leg_id": LEG_ID, "environment": env, "morph": "%s->%s" % (a, b), "direction": DIRECTION,
           "seed": SEED, "dg_morph_kcal": float(dg_kcal) if dg_kcal is not None else None,
           "mbar_se_kcal": float(unc_kcal) if unc_kcal is not None else None, "n_mapped_atoms": n_mapped,
           "n_windows": N_WINDOWS, "spot_safe": True,
           "protocol_hash": proto_hash, "protocol_settings": proto_payload,
           "starting_model": starting_model}
    json.dump(out, open(os.path.join(CKPT, "leg_%s_%s_r%d.json" % (LEG_ID, DIRECTION, SEED)), "w"), indent=2)
    _dg = out["dg_morph_kcal"]; _se = out["mbar_se_kcal"]
    print("  [tfep] LEG DONE %s: ΔG_morph=%s ± %s (MBAR SE) [spot-safe]" % (
        LEG_ID, ("%.2f" % _dg) if _dg is not None else "None",
        ("%.2f" % _se) if _se is not None else "None"), flush=True)


def main():
    mode = os.environ.get("MODE", "smoke")
    if mode == "reduce":
        import ternary_fep_reduce
        ternary_fep_reduce.reduce_all()
    elif mode == "converge":     # reviewer #1: $0 CPU convergence analysis of committed .nc (before seed1)
        import ternary_fep_convergence
        ternary_fep_convergence.analyze_all()
    elif mode == "endpoint_smoke":   # reviewer condition 2/3 (2026-07-19): one short EXACT-Hamiltonian stability
        endpoint_smoke()             # test per physical endpoint (ligA λ=0, ligB λ=1) — the first gated GPU step
    else:                       # smoke or run both go through run_leg (smoke short-circuits inside)
        run_leg()


def endpoint_smoke():
    """Reviewer condition 2/3 (2026-07-19), execution-order step 3: build each PHYSICAL endpoint (ligand A at
    λ=0, ligand B at λ=1) of THIS leg under the EXACT RBFE force field, from the (pre-equilibrated) staged
    complex, and run a short unrestrained stability test — recording the FF-switch minimization drop, any NaN,
    ligand RMSD, and energy drift. A physical endpoint that NaNs or drifts here is caught BEFORE the 3-replicate
    fan-out. Reads the SAME staged complex.pdb + relaxed ligands.sdf the run leg consumes. Cheap (short MD)."""
    import glob as _glob
    import ternary_endpoint_stability as es
    from rdkit import Chem
    leg, env = leg_spec(LEG_ID)
    charge = os.environ.get("CHARGE_METHOD", "nagl")
    n_steps = int(os.environ.get("ENDPOINT_SMOKE_STEPS", "25000"))
    dt_fs = float(os.environ.get("ENDPOINT_SMOKE_DT_FS", "2.0"))
    platform = "CPU" if os.environ.get("RBFE_PRIME_ONLY") == "1" else os.environ.get("OPENMM_PLATFORM", "CUDA")

    def _find(name):
        p = os.path.join(IN, LEG_ID, name)
        if os.path.isfile(p):
            return p
        hits = _glob.glob(os.path.join(IN, "**", name), recursive=True)
        if not hits:
            raise SystemExit("[endpoint_smoke] ABORT: missing staged %s under %s" % (name, IN))
        return hits[0]

    protein_pdb = _find("complex.pdb")
    mols = [m for m in Chem.SDMolSupplier(_find("ligands.sdf"), removeHs=False) if m is not None]
    if not mols:
        raise SystemExit("[endpoint_smoke] ABORT: no ligands in staged ligands.sdf")
    endpoints = [("ligA_lambda0", mols[0])]
    if len(mols) > 1:
        endpoints.append(("ligB_lambda1", mols[1]))
    print("[endpoint_smoke] LEG=%s env=%s charge=%s steps=%d dt=%.1f platform=%s — testing %d physical endpoint(s)"
          % (LEG_ID, env, charge, n_steps, dt_fs, platform, len(endpoints)), flush=True)
    results = {}
    for name, mol in endpoints:
        print("[endpoint_smoke] building EXACT-FF physical complex for %s (%d atoms)…"
              % (name, mol.GetNumAtoms()), flush=True)
        system, topo, pos, lig_idx = es.build_physical_complex(protein_pdb, mol, charge_method=charge,
                                                               platform_name=platform)
        r = es.run_endpoint_stability(system, topo, pos, lig_idx, n_steps=n_steps, dt_fs=dt_fs,
                                      platform_name=platform)
        results[name] = r
        print("[endpoint_smoke] %s: stable=%s ff_switch_ok=%s max_rmsd=%.2fÅ drift=%s"
              % (name, r["stable"], r["ff_switch"].get("conditioner_ok"), r.get("max_ligand_rmsd_a") or -1,
                 r["energy_drift"].get("drift_kcal_per_ns")), flush=True)
    all_stable = all(v["stable"] for v in results.values())
    out = {"leg_id": LEG_ID, "environment": env, "charge_method": charge, "all_endpoints_stable": all_stable,
           "endpoints": results}
    os.makedirs(CKPT, exist_ok=True)
    json.dump(out, open(os.path.join(CKPT, "endpoint_stability_%s.json" % LEG_ID), "w"), indent=2, default=str)
    print("[endpoint_smoke] DONE leg=%s all_endpoints_stable=%s -> endpoint_stability_%s.json"
          % (LEG_ID, all_stable, LEG_ID), flush=True)


if __name__ == "__main__":
    main()
