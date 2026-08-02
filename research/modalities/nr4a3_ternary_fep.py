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
CRYSTAL_SMILES = None   # identity of the ligand actually in the crystal SDF; set by _morph_endpoints,
                        # direction-INDEPENDENT (see the note there). Never infer it from a swapped sa.
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


def _extra_leg_map():
    """Leg registries belonging to experiments OUTSIDE the frozen pilot bundle.

    ⚠ WHY NOT JUST ADD THEM TO `ternary_coop.PILOT_LEG_MAP`. That map is the PREREGISTERED pilot bundle and
    `load_pilot_legs` cross-checks it against `ternary-coop-frozen.json`, failing closed on any drift. Adding
    a leg there would either break that guard or silently enlarge a preregistered experiment with legs it
    never declared — and the guard exists precisely because a bundle that can quietly grow is not frozen.
    A later experiment therefore brings its OWN registry and this function unions them, read-only.

    Import failures are swallowed on purpose: the pilot legs must keep resolving even if a newer rung's
    module is missing or broken. A leg id that resolves nowhere still fails closed in `leg_spec`.
    """
    out = {}
    for mod in ("nr4a3_5aks_cofold", "valb_triangle_legs"):
        try:
            out.update(__import__(mod).LEG_MAP)
        except Exception:  # noqa: BLE001
            pass
    return out


def leg_spec(leg_id):
    """Resolve a leg id (frozen or derived-solvent) to its assembly/morph spec via ternary_coop_prep. For a
    solvent leg we borrow the morph endpoints of any environment leg of the same pair (the ligands are identical;
    only the protein context differs)."""
    env = _environment_of(leg_id)
    if leg_id in tcoop.PILOT_LEG_MAP:
        leg = dict(id=leg_id, **tcoop.PILOT_LEG_MAP[leg_id])
    elif leg_id in _extra_leg_map():
        leg = dict(id=leg_id, **_extra_leg_map()[leg_id])
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
    # Which molecule is actually IN the crystal SDF is a fact about the structure, not about the direction we
    # happen to be morphing in. It is the UNSWAPPED endpoint A (calib_hi = Wurz cmpd1 = 8G1Q CCD YHB); cmpd4 is
    # derived and exists in no crystal. Stash it so _build_components cannot infer it from the (possibly swapped)
    # sa. Getting this wrong is what broke the first rev leg: with base_smiles=sa, DIRECTION=rev told _repair_pose
    # the crystal ligand was cmpd4, so bond orders were assigned against a template whose linker ring differs by
    # N->CH, the thiazole lost its aromatic C-H, and NAGL rejected the molecule with
    # RadicalsNotSupportedError ("Found 1 radical electrons") ~30 s into charge assignment.
    # ⛔ ...AND IT IS NOT ALWAYS ENDPOINT A EITHER. Taking the UNSWAPPED `smiles_a` fixes the DIRECTION half
    # of the bug above, and it is right for every leg whose morph HAPPENS to start at the co-crystallised
    # compound — which every calib leg did, until the closure triangle. Its T2 edge is
    # `calib_lo -> calib_lo2`: it STARTS at cmpd4, a DERIVED molecule that exists in no crystal. Under the
    # old rule `_repair_pose` would have received cmpd4 as the bond-order template for cmpd1's coordinates —
    # the IDENTICAL failure above, reached by a different route, and it would have taken out both T2 legs.
    # The crystal ligand is a property of the STAGED STRUCTURE, so it is resolved from there
    # (`prep.crystal_ligand_smiles`); endpoint A stays the fallback for the families where it is genuinely
    # correct (5a-KS stages from a co-fold whose ligand IS endpoint A), so no existing leg changes.
    global CRYSTAL_SMILES
    CRYSTAL_SMILES = prep.crystal_ligand_smiles(leg) or m["smiles_a"]
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


def _pose_matches_target(mol, target_smiles, rdkit_chem):
    """Does this built pose really BE the target molecule? Two questions, not one.

    Plain canonical-SMILES equality was the original test, and it is right whenever the target SMILES
    specifies every stereocentre — which the calibration pair does. It is WRONG when the target leaves one
    open. RUNG 5a-KS's construct is exactly that case: the design draws the glutarimide C-H unassigned (the
    thalidomide-class centre, drawn unassigned throughout the IMiD literature because it epimerises), while
    a 3D pose necessarily HAS a configuration and RDKit reads it back off the coordinates. Measured on the
    real staged ligand: the pose canonicalised to `N([C@H]3CCC(=O)NC3=O)` against the design's
    `N(C3CCC(=O)NC3=O)`, and the equality test rejected a chemically correct endpoint.

    So:
      1. CONSTITUTION must be identical — stereo-stripped canonical SMILES.
      2. Every stereocentre the TARGET SPECIFIES must agree. A chirality-aware substructure match does this
         exactly: a specified centre must match, an unspecified one matches either configuration.
    For a fully-specified target the pair is equivalent to the old test, so no existing leg's acceptance
    changes. WHICH configuration a partly-specified pose resolved to is not lost — the stager records it and
    REFUSES to stage the two 5a-KS legs unless both resolved it the same way, because a diastereomer
    difference between the arms would land inside S.
    """
    want = _canon_smiles(target_smiles, rdkit_chem)
    if want is not None and _canon_smiles(mol, rdkit_chem) == want:
        return True
    tmpl = rdkit_chem.MolFromSmiles(target_smiles)
    if tmpl is None or mol is None:
        return False
    try:
        a = rdkit_chem.RemoveHs(rdkit_chem.Mol(mol))
        b = rdkit_chem.RemoveHs(rdkit_chem.Mol(tmpl))
        rdkit_chem.RemoveStereochemistry(a)
        rdkit_chem.RemoveStereochemistry(b)
        if rdkit_chem.MolToSmiles(a) != rdkit_chem.MolToSmiles(b):
            return False
        return bool(rdkit_chem.RemoveHs(rdkit_chem.Mol(mol)).HasSubstructMatch(tmpl, useChirality=True))
    except Exception:  # noqa: BLE001
        return False


def _single_aromatic_element_swap_pose(mol, target_smiles, rdkit_chem):
    """Build `target_smiles`'s pose from `mol` by changing the element of exactly ONE aromatic ring atom,
    preserving every coordinate. Returns (pose, n_equivalent_sites) or (None, 0).

    WHY A SEARCH RATHER THAN A RULE. `_pyridine_to_benzene_pose` above encodes one specific, hand-identified
    perturbation (the calibration edge's linker N->CH) and only works in that direction. RUNG 5a-KS is the
    mirror image — an aza-scan, phenyl C-H -> 3-pyridyl N — and no third rule should be written for the next
    one. So instead of naming the atom, this TRIES each aromatic ring atom in turn and keeps the ones whose
    swap reproduces the target's canonical SMILES exactly. The verification IS the rule: a swap that does not
    canonicalise to the target is discarded, so the method cannot invent a molecule.

    N-TO-C AND C-TO-N BOTH, because a forward leg and its reverse hysteresis partner morph in opposite
    directions and must be able to build the same two endpoints.

    TIES ARE REAL AND ARE NOT AN ERROR. A 3-pyridyl can be made from a phenyl at EITHER meta carbon: the two
    give the identical molecule and differ only in which face of the ring the nitrogen sits on. They are
    interconverted by a 180-degree flip of a freely rotating benzylic ring, which the MD samples, so the
    choice is not a physical commitment — but it must be DETERMINISTIC or two replicates would silently
    start from different structures. Lowest atom index wins, and the count is returned so the leg record can
    say how many equivalent sites there were rather than leaving a reader to assume there was only one.
    """
    if mol is None or rdkit_chem.MolFromSmiles(target_smiles) is None:
        return None, 0
    # ⚠ STRIP EXPLICIT HYDROGENS FIRST — this is not tidiness, it is the difference between pyridine and
    # pyrrole. `_repair_pose` hands back a mol carrying explicit H atoms, and turning an aromatic C into an
    # N while its explicit H is still bonded produces an aromatic N-H: a pyrrole-type nitrogen, which does
    # not kekulize in a 6-ring and is a different molecule from the 3-pyridyl the design specifies. Measured
    # on the real construct: every candidate site failed with "Can't kekulize mol" until the Hs came off.
    # RemoveHs preserves the heavy-atom conformer, and AddHs(addCoords=True) rebuilds the hydrogens after.
    try:
        base = rdkit_chem.RWMol(rdkit_chem.RemoveHs(rdkit_chem.Mol(mol)))
        rdkit_chem.SanitizeMol(base)
    except Exception:  # noqa: BLE001
        try:
            base = rdkit_chem.RWMol(mol)
            rdkit_chem.SanitizeMol(base)
        except Exception:  # noqa: BLE001
            return None, 0
    ring_atoms = {i for ring in base.GetRingInfo().AtomRings() for i in ring}
    hits = []
    for idx in sorted(ring_atoms):
        a0 = base.GetAtomWithIdx(idx)
        if not a0.GetIsAromatic():
            continue
        z0, nh0 = a0.GetAtomicNum(), a0.GetTotalNumHs()
        for z1 in (6, 7):
            if z1 == z0:
                continue
            # C->N only at a ring C-H, and N->C only at a hydrogen-free (pyridine-type) N. A substituted
            # ring carbon or an N-H would change the substitution pattern as well as the element, which is
            # a different perturbation from an aza-scan; skipping them also drops ~40 guaranteed-failing
            # kekulization attempts per call, whose RDKit warnings otherwise bury the real log.
            if z1 == 7 and nh0 != 1:
                continue
            if z1 == 6 and nh0 != 0:
                continue
            m = rdkit_chem.RWMol(base)
            at = m.GetAtomWithIdx(idx)
            at.SetAtomicNum(z1)
            at.SetNumExplicitHs(0)
            at.SetNoImplicit(False)
            at.SetFormalCharge(0)
            try:
                out = m.GetMol()
                rdkit_chem.SanitizeMol(out)
                out = rdkit_chem.AddHs(out, addCoords=True)
            except Exception:  # noqa: BLE001
                continue
            # `_pose_matches_target`, not canonical-SMILES equality: the pose carries a resolved
            # glutarimide stereocentre that the design's SMILES leaves open, so equality rejects the
            # correct swap. See that function for the measurement.
            if _pose_matches_target(out, target_smiles, rdkit_chem):
                hits.append((idx, z0, z1, out))
    if not hits:
        return None, 0
    idx, z0, z1, out = hits[0]
    print("  [tfep] endpoint pose built by a single aromatic element swap: atom %d %d->%d "
          "(%d equivalent site(s) matched the target; lowest index taken — they differ only by a ring "
          "flip the MD samples)" % (idx, z0, z1, len(hits)), flush=True)
    return out, len(hits)


def _double_aromatic_element_swap_pose(mol, target_smiles, rdkit_chem, max_pairs=4000):
    """The same search as `_single_aromatic_element_swap_pose`, over PAIRS of aromatic ring atoms.

    WHY A SECOND SWAP IS NEEDED AT ALL, AND WHY IT IS NOT A LOOSENING. The valB closure triangle's third
    vertex, cmpd4", differs from the crystal ligand cmpd1 by a nitrogen 1,2-SHIFT within the linker ring:
    the ring N becomes a C-H and a neighbouring C-H becomes an N. Both endpoints of every leg are built from
    the SAME cmpd1 crystal pose (`_build_components`), so the closing edge T3 (cmpd1 -> cmpd4") cannot be
    built by any single-atom swap, and `_endpoint_pose` would raise "refusing a wrong-molecule leg" — which
    is the correct behaviour of the old code and exactly the gap this fills.

    IT CANNOT INVENT A MOLECULE, for the same structural reason the single-swap search cannot: a candidate is
    kept ONLY if it reproduces `target_smiles` under `_pose_matches_target`. The search is a way of FINDING a
    construction of a molecule that is already specified; the verification is the rule. Widening from one
    swap to two therefore widens what can be BUILT, never what can be ACCEPTED.

    ORDERED PAIRS, DISTINCT ATOMS, AND THE SAME PER-ATOM ELIGIBILITY as the single-swap search: C->N only at
    a ring C-H (an aza-substitution at a substituted position would make a quaternary aromatic N+ and change
    the formal charge) and N->C only at a hydrogen-free pyridine-type N. `max_pairs` bounds the work; the
    Wurz ligand has ~25 aromatic ring atoms, so the real cost is a few hundred sanitize calls, but an
    unbounded double loop on a larger ligand is the kind of thing that silently turns into a stall on a
    rented host.

    Returns (pose, n_equivalent_pairs) or (None, 0). Deterministic: lowest (i, j) index pair wins, and the
    count is returned so the leg record can say how many equivalent constructions existed.
    """
    if mol is None or rdkit_chem.MolFromSmiles(target_smiles) is None:
        return None, 0
    try:
        base = rdkit_chem.RWMol(rdkit_chem.RemoveHs(rdkit_chem.Mol(mol)))
        rdkit_chem.SanitizeMol(base)
    except Exception:  # noqa: BLE001
        return None, 0
    ring_atoms = sorted({i for ring in base.GetRingInfo().AtomRings() for i in ring})

    def _targets(idx):
        """Which element this ring atom may legally become, under the aza-scan eligibility rule."""
        a = base.GetAtomWithIdx(idx)
        if not a.GetIsAromatic():
            return ()
        z, nh = a.GetAtomicNum(), a.GetTotalNumHs()
        if z == 6 and nh == 1:
            return (7,)
        if z == 7 and nh == 0:
            return (6,)
        return ()

    cand = [(i, z) for i in ring_atoms for z in _targets(i)]
    hits = []
    tried = 0
    for ai in range(len(cand)):
        for bi in range(ai + 1, len(cand)):
            i, zi = cand[ai]
            j, zj = cand[bi]
            if i == j:
                continue
            tried += 1
            if tried > max_pairs:
                break
            m = rdkit_chem.RWMol(base)
            for idx, z in ((i, zi), (j, zj)):
                at = m.GetAtomWithIdx(idx)
                at.SetAtomicNum(z)
                at.SetNumExplicitHs(0)
                at.SetNoImplicit(False)
                at.SetFormalCharge(0)
            try:
                out = m.GetMol()
                rdkit_chem.SanitizeMol(out)
                out = rdkit_chem.AddHs(out, addCoords=True)
            except Exception:  # noqa: BLE001
                continue
            if _pose_matches_target(out, target_smiles, rdkit_chem):
                hits.append((i, j, out))
        if tried > max_pairs:
            break
    if not hits:
        return None, 0
    i, j, out = hits[0]
    print("  [tfep] endpoint pose built by a DOUBLE aromatic element swap: atoms %d and %d "
          "(%d equivalent pair(s) matched the target; lowest index pair taken). This is the closure "
          "triangle's ring-nitrogen 1,2-shift — two atoms, one ring, zero heavy dummies."
          % (i, j, len(hits)), flush=True)
    return out, len(hits)


def _endpoint_pose(sdf, name, target_smiles, base_smiles, rdkit_chem):
    """Build the 3D pose for endpoint `name` so it MATCHES target_smiles, starting from the crystal pose (whose
    true identity is base_smiles — the co-crystallized ligand, e.g. Wurz cmpd1). If target == base, bond-order
    repair suffices (e.g. calib_hi = cmpd1). If target differs by an ELEMENT change (calib_lo = cmpd4, linker
    pyridine N->CH), bond-order repair CANNOT convert N->C, so mutate the pose (pyridine->benzene) then repair.
    Verifies the built pose's canonical SMILES equals the target and FAILS CLOSED otherwise — never runs a leg on
    the wrong molecule (this is the bug the 5-part gate's endpoints_match check caught)."""
    base = rbfe._sdf_mol(sdf, name, base_smiles, rdkit_chem)
    clean = rbfe._repair_pose(base, base_smiles, rdkit_chem)
    if _pose_matches_target(clean, target_smiles, rdkit_chem):
        return clean                                     # target == crystal identity (calib_hi = cmpd1)
    mut = _pyridine_to_benzene_pose(clean, rdkit_chem)   # element-change endpoint (cmpd4 benzene linker)
    if mut is not None:
        mut = rbfe._repair_pose(mut, target_smiles, rdkit_chem)
        if _pose_matches_target(mut, target_smiles, rdkit_chem):
            return mut
    # GENERAL single-aromatic-atom swap (RUNG 5a-KS: phenyl C-H -> 3-pyridyl N, i.e. the calibration edge's
    # perturbation run backwards). Tried LAST so it can never change how an existing leg is built.
    swapped, _n = _single_aromatic_element_swap_pose(clean, target_smiles, rdkit_chem)
    if swapped is not None:
        swapped = rbfe._repair_pose(swapped, target_smiles, rdkit_chem)
        if _pose_matches_target(swapped, target_smiles, rdkit_chem):
            return swapped
    # DOUBLE aromatic swap, tried after the single one so it can never change how any existing leg is built.
    # This is the closure triangle's closing edge: cmpd1 -> cmpd4" is a ring-nitrogen 1,2-SHIFT, and both
    # endpoints are built from the same cmpd1 crystal pose, so one swap cannot reach it.
    swapped2, _n2 = _double_aromatic_element_swap_pose(clean, target_smiles, rdkit_chem)
    if swapped2 is not None:
        swapped2 = rbfe._repair_pose(swapped2, target_smiles, rdkit_chem)
        if _pose_matches_target(swapped2, target_smiles, rdkit_chem):
            return swapped2
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
    # base_smiles = the identity of the molecule IN the SDF (the co-crystallised ligand), which is
    # direction-independent. It was `sa`, which is only the crystal ligand in the FORWARD direction --
    # _morph_endpoints swaps sa/sb for DIRECTION=rev, so a rev leg claimed the crystal held cmpd4.
    base = CRYSTAL_SMILES or sa
    molA = _endpoint_pose(sdf, a, sa, base, rdkit_chem)   # target sa, built from the crystal pose
    molB = _endpoint_pose(sdf, b, sb, base, rdkit_chem)   # target sb, same crystal pose (element change if needed)
    # ★ THE POSE FILE'S CHARGES ARE NOT THIS PROTOCOL'S CHARGES. `ligands.sdf` is a COORDINATE carrier: the
    # relaxed one written by `ternary_preequil` comes through `openff Molecule.to_rdkit()` and so arrives
    # stamped with the RELAXATION force field's `atom.dprop.PartialCharge`, which RDKit then copies through
    # every step of `_endpoint_pose` onto a molecule whose atom count has CHANGED. Full reasoning and the
    # measurement in `nr4a3_rbfe.strip_foreign_partial_charges`; the loud log line is here because this is the
    # boundary where it would otherwise become either a dead rental or a silent protocol deviation.
    #
    # ⚠ AND THE STRIP IS NOT THE GUARD — THE CENSUS AFTER IT IS (2026-07-29). This block used to be the only
    # protection, and it passed while the legs kept dying: it cleared the molecule-level array, logged
    # "109 INHERITED partial charges ... dropped", and shipped a molecule whose ATOMS were still individually
    # charged, because `_endpoint_pose` above had already re-added hydrogens that could not inherit one.
    # OpenFF then refused the partial set inside `proto.create` (`Some atoms in rdmol have partial charges,
    # but others do not`) on 37 of one unit's 49 rented hosts. `_sdf_mol` now strips at the door so nothing
    # partial can be built in the first place; this stays as the boundary re-check, and `assert_no_foreign_
    # charges` is what makes it a check rather than a hope.
    for _nm, _m in (("A", molA), ("B", molB)):
        _m, _n = rbfe.strip_foreign_partial_charges(_m)
        if _n:
            print("  [tfep] endpoint %s arrived with %d INHERITED partial charges for %d atoms — dropped; "
                  "this protocol assigns its own (partial_charge_method), and a pose file's charges are a "
                  "relaxation artefact, never the alchemical charge model."
                  % (_nm, _n, _m.GetNumAtoms()), flush=True)
        rbfe.assert_no_foreign_charges(_m, "ternary endpoint %s" % _nm)
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
    # STARTING-STRUCTURE / TIMESTEP ROBUSTNESS. ** SETTLED 2026-07-19 — this comment previously carried a REFUTED
    # root cause; see ternary-rbfe-runbook.md 1b/1c for the authoritative account. **
    # What is confirmed: the warmup NaN is NOT a starting-structure clash. A CPU clash census of the assembled
    # complex (ternary_stage_validate._clash_check) proved it clean (worst protein-protein non-bonded = a 1.33 A
    # peptide bond; worst protein<->ligand = 1.59 A H-bond). The NaN hits at a softcore lambda-state on warmup
    # iteration 1 and survives 25000 minimization steps.
    # What was REFUTED (do not reinstate either story): (i) "the cmpd1->cmpd4 N->CH change grows a C-H whose
    # constraint changes between endpoints, so OpenFE leaves it unconstrained" (2026-07-18), and (ii) its own
    # correction, "the whole alchemical ligand's C-H are unconstrained". A perses force-layout dump
    # (rbfe_edge_timestep_scan.py -> constrain_diag, 2026-07-19) showed the hybrid carries TWO CustomBondForces --
    # an alchemical valence-bond force and an alchemical nonbonded-EXCEPTION force -- and the [hmr-diag] counter
    # was counting the exception PAIRS as "unconstrained X-H bonds". Counting only genuine valence stretch terms
    # gives 0 unconstrained on BOTH the pilot and calib edges, i.e. the ligand C-H ARE constrained -- yet calib
    # still NaN'd at 4 fs while the pilot runs fine at 4 fs. So the instability is the softcore alchemical
    # (dis)appearing region in a large, rough homology-built assembly, and there is NO static predictor of the
    # ternary timestep. constrain_nonalchemical_xh() is confirmed a no-op (it adds 0).
    # The fix that WORKS is NOT a smaller timestep: relax the fully-interacting physical complex with plain MD
    # BEFORE the alchemy (ternary_preequil.py, use_preequil=1). With the relaxed structure the calib leg ran
    # warmup 48/48 at 1 fs -> production 40/40 at 4 fs with zero NaN, where every prior run died at warmup iter 1.
    # So: determine the ternary timestep EMPIRICALLY by a warmup-survival test (2 fs is the known-safe fallback),
    # and run validation and production at the SAME one. minimization_steps kept high (cheap insurance). Both
    # env-overridable. (rbfe_spot_driver instruments the NaN: on catch it loads openmmtools' saved nan-error-logs
    # state and names the offending atoms.)
    try:
        s.simulation_settings.minimization_steps = int(os.environ.get("RBFE_MIN_STEPS", "25000"))
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN minimization_steps (%s)" % e, flush=True)
    # ===== STRIDED HEAVY-ATOM TRAJECTORY — A REQUIREMENT, NOT AN OPTION (2026-07-25) =====================
    # WHAT THIS FIXES. The NR-V04 covalent panel was reduced in-loop with positions discarded, and its
    # committed output was censused read-only on 2026-07-25: 72 objects, 19 units, ZERO trajectory objects.
    # Everything that survived was a single pre-minimisation frame, a 1.35 GB System (forces + parameters, no
    # coordinates over time), or scalars already reduced against the WRONG chain split. Three separate
    # analysis defects in that panel — a positional chain split that measured the wrong interface, a
    # chain-blind reactive-cysteine search, and an R3 reporting nanometres under an Angstrom label — were all
    # correctable in principle and NONE correctable in practice, because nothing survived to re-derive from.
    # The panel now has to be re-run or abandoned. A trajectory that survives makes an analysis bug found next
    # month cost $0 instead of another rental.
    #
    # WHY A STRIDE, AND NOT SIMPLY "ON". OpenFE's default writes positions EVERY iteration for all 12 replicas,
    # which nr4a3_rbfe measured (netCDF-proven, 2026-07-16) at ~0.5 MB/iter -> ~1 GB by 2000 iterations — and
    # this lane re-uploads the WHOLE .nc at every spot commit, so an every-iteration trajectory is paid for
    # tens of times over. That cost is why the binary lane turned positions OFF entirely, which is the other
    # extreme and the one that destroyed the NR-V04 panel's re-analysability. A 50 ps stride is 20 iterations
    # at the 2.5 ps time_per_iteration, i.e. ~1/20th the bytes: ~50 MB over a full leg, against the ~112 MB
    # System XML the driver already uploads without anyone objecting. Tens of MB buys back every future
    # re-analysis.
    #
    # VELOCITIES STAY OFF. They roughly double the size and no structural re-analysis needs them; the
    # trajectory exists to recompute geometry (interfaces, RMSDs, contacts), not to restart dynamics — restarts
    # come from the checkpoint .chk, which carries its own velocities.
    #
    # Coordinates are `output_indices`-filtered (OpenFE's default excludes water), so this is a solute
    # trajectory, not a box dump. Guarded attribute-by-attribute because names and units vary by openfe
    # version, and a settings write must never be able to abort a leg.
    _pos_ps = os.environ.get("RBFE_POSITIONS_WRITE_PS", "50")
    _vel_ps = os.environ.get("RBFE_VELOCITIES_WRITE_PS", "")
    _oset = getattr(s, "output_settings", None)
    for _attr, _val in (("positions_write_frequency", _pos_ps), ("velocities_write_frequency", _vel_ps)):
        if _oset is None or not hasattr(_oset, _attr):
            print("  [tfep] WARN output_settings.%s absent in this openfe — cannot control trajectory "
                  "persistence" % _attr, flush=True)
            continue
        try:
            if not _val or _val.lower() in ("0", "none", "off"):
                setattr(_oset, _attr, None)
                print("  [tfep] output_settings.%s -> None (not written)" % _attr, flush=True)
            else:
                from openff.units import unit as _ou3
                setattr(_oset, _attr, float(_val) * _ou3.picosecond)
                print("  [tfep] output_settings.%s -> %s ps  (STRIDED TRAJECTORY: %s ps / %s = every %.0f "
                      "iterations; solute only via output_indices=%r). This is the re-analysability "
                      "requirement — see the NR-V04 zero-trajectory census, 2026-07-25."
                      % (_attr, _val, _val, "2.5 ps/iter",
                         max(1.0, float(_val) / 2.5), getattr(_oset, "output_indices", "?")), flush=True)
        except Exception as e:  # noqa: BLE001
            print("  [tfep] WARN output_settings.%s=%r failed (%s); trajectory persistence is whatever "
                  "openfe defaults to — CHECK THE .nc SIZE" % (_attr, _val, e), flush=True)
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
    # CHARGES — read this before trusting the default below. ddG_coop subtracts this lane's own binary and ternary
    # morphs, so WITHIN this lane the charge model cancels and any consistent choice is safe. The default here is
    # am1bcc, but **every real dispatch overrides it to nagl** (gpu-ternary-fep-gcp.yml:34,74 default `nagl`;
    # md_settings.CHARGE_METHOD = "nagl"), because AM1-BCC via AmberTools sqm is intractable on PROTAC-sized
    # ligands on CPU (>85 min without converging, measured 2026-07-22) and nagl has the warm primed setup cache.
    # So in practice THIS LANE RUNS NAGL and the binary RBFE lane runs am1bcc -- they are a documented LANE SPLIT,
    # not a match. That is fine for ddG_coop; it is NOT fine for any quantity that subtracts a binary-lane leg
    # from a ternary-lane leg (the 5a-KS wedge cycle), which MUST pin one CHARGE_METHOD across both legs and
    # record it in both result JSONs. See md_settings.py and nr4a3-program-map.md RUNG 5.
    _charge = os.environ.get("CHARGE_METHOD", "am1bcc")
    try:
        s.partial_charge_settings.partial_charge_method = _charge
    except Exception as e:  # noqa: BLE001
        print("  [tfep] WARN charges=%s (%s); using default" % (_charge, e), flush=True)
    # NAGL must NOT drag in the AmberTools backend. OpenFE's charge_generation constructs a ToolkitRegistry for
    # the configured off_toolkit_backend REGARDLESS of method; the default 'ambertools' raises
    # ToolkitUnavailableException when AmberTools isn't in the env (confirmed on the CPU prime + the GPU setup
    # deaths). For nagl the charges come from the GNN model and only a conformer is needed, so point the backend
    # at RDKit (always present). am1bcc is genuinely computed via AmberTools sqm, so leave it on 'ambertools'.
    if _charge == "nagl":
        for _fld in ("off_toolkit_backend", "toolkit_backend", "nagl_toolkit_backend"):
            try:
                if hasattr(s.partial_charge_settings, _fld):
                    setattr(s.partial_charge_settings, _fld, "rdkit")
                    print("  [tfep] nagl: set partial_charge_settings.%s = rdkit (avoid AmberTools dependency)" % _fld,
                          flush=True)
                    break
            except Exception as e:  # noqa: BLE001
                print("  [tfep] WARN could not set %s=rdkit (%s)" % (_fld, e), flush=True)
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


def expected_heavy_map_size(Chem, molA, molB, timeout_s=300):
    """The number of HEAVY atoms an atom map for this edge MUST contain, derived from the two endpoint
    molecules themselves. PURE (RDKit only) — unit-testable, no OpenFE.

    ★ WHY THIS EXISTS (2026-07-26). `LomapAtomMapper(time=N)` — `N` is LOMAP's MCS timeout in SECONDS — does
    not raise when it runs out of time. It returns the best PARTIAL match found so far, silently. That makes
    the atom map, i.e. WHAT THE ALCHEMICAL TRANSFORMATION ACTUALLY IS, a function of how fast the rented host
    happened to be. Measured on RUNG 5a-KS: one edge whose endpoints differ by ONE atom mapped 111 atoms on
    two hosts and 80 atoms with 31 dummies on a third. A short map is not a slow answer — it is a DIFFERENT
    EXPERIMENT: the atoms that should have mapped 1:1 become dummies that are annihilated and recreated, and
    the leg then converges and returns a confident ΔG for a perturbation nobody designed.
    Nothing downstream catches it. `protocol_hash` covers the OpenFE SETTINGS, not the map.
    `system_identity_consistency` covers particle counts, which a dummy-ised map leaves unchanged. And the
    5-part gate's item 2 asks for a "real perturbation", which unmapped atoms SATISFY — so a degenerate map
    makes the pre-spend gate greener, not redder.

    THE EXPECTATION IS DERIVED, NOT TYPED. The maximum common substructure of the two endpoints is computed
    here with RDKit under deliberately permissive atom comparison (`CompareAny`, so a ring N↔C element change
    is a MATCH rather than a mismatch) and conservative bond/ring rules, which is exactly the correspondence
    the production mapper is asked to find with `element_change=True`. For the frozen valB_mini edge (Wurz
    cmpd1 → cmpd4, a linker pyridine N → benzene CH) both endpoints carry 59 heavy atoms and this returns
    **59** — a complete 1:1 heavy-atom map with the single N↔C as the alchemical atom. Anything less from
    LOMAP is a failed search, not a property of the chemistry.

    Returns (n_heavy_expected, detail). `n_heavy_expected` is None when the MCS itself timed out — an
    unreliable expectation must never be used to abort a leg."""
    from rdkit.Chem import rdFMCS
    a, b = Chem.RemoveHs(Chem.Mol(molA)), Chem.RemoveHs(Chem.Mol(molB))
    res = rdFMCS.FindMCS(
        [a, b],
        atomCompare=rdFMCS.AtomCompare.CompareAny,      # a ring N->CH element change is a MATCH, not a break
        bondCompare=rdFMCS.BondCompare.CompareOrderExact,
        ringMatchesRingOnly=True,
        completeRingsOnly=False,
        timeout=int(timeout_s),
    )
    detail = {"mcs_smarts": res.smartsString, "mcs_num_atoms": res.numAtoms, "mcs_num_bonds": res.numBonds,
              "mcs_timed_out": bool(res.canceled), "heavy_atoms_A": a.GetNumAtoms(),
              "heavy_atoms_B": b.GetNumAtoms(), "mcs_timeout_s": int(timeout_s)}
    return (None if res.canceled else int(res.numAtoms)), detail


def atom_map_audit(Chem, ligA, ligB, mapping):
    """Everything about the atom map that a later reader needs in order to know WHICH perturbation a leg ran.

    Recorded on every leg (`out["atom_map"]`), because if an earlier replicate turns out to have run under a
    short map then that replicate is not comparable to the others, and the only way anyone can tell is if
    each leg says what its map was and what budget produced it."""
    molA, molB = ligA.to_rdkit(), ligB.to_rdkit()
    a2b = dict(mapping.componentA_to_componentB)
    heavy = sum(1 for ia, ib in a2b.items()
                if molA.GetAtomWithIdx(ia).GetAtomicNum() > 1 and molB.GetAtomWithIdx(ib).GetAtomicNum() > 1)
    exp, detail = expected_heavy_map_size(Chem, molA, molB)
    rec = {
        "n_mapped_atoms": len(a2b),
        "n_heavy_mapped": heavy,
        "expected_heavy_mapped": exp,
        "n_atoms_A": molA.GetNumAtoms(), "n_atoms_B": molB.GetNumAtoms(),
        # The MCS budget the map was produced under. `nr4a3_rbfe._mapping` reads this env var; recording the
        # RESOLVED value (default included) rather than the raw env is the same lesson as charge_method.
        "lomap_time_s": int(os.environ.get("RBFE_LOMAP_TIME_S", "300")),
        "degenerate": (exp is not None and heavy < exp),
        **detail,
    }
    return rec


def assert_map_not_degenerate(audit, leg_id, hard=None):
    """Fail CLOSED on a short atom map, before any sampling is paid for.

    `hard` defaults to ON for the frozen calibration legs (`calib_*`), whose expectation is a complete 1:1
    heavy-atom map and is verified at $0 in CI before launch. It defaults to a LOUD WARNING elsewhere,
    deliberately: this engine is shared with legs another lane has in flight right now, and introducing a new
    hard abort underneath a running leg — on an expectation that has not been checked for that edge — would
    trade a silent wrong answer for a silent lost rental. Override either way with `RBFE_MAP_ASSERT=1|0`."""
    if hard is None:
        env = os.environ.get("RBFE_MAP_ASSERT")
        hard = (env == "1") if env in ("0", "1") else str(leg_id).startswith("calib_")
    if not audit.get("degenerate"):
        if audit.get("mcs_timed_out"):
            print("  [tfep] ⚠ atom-map expectation UNAVAILABLE: the RDKit MCS hit its %ss budget, so the "
                  "%d-atom LOMAP map (%d heavy) could not be checked against a derived expectation."
                  % (audit.get("mcs_timeout_s"), audit.get("n_mapped_atoms"), audit.get("n_heavy_mapped")),
                  flush=True)
        else:
            print("  [tfep] atom map OK: %d heavy atoms mapped, %d expected from the endpoint MCS "
                  "(LOMAP budget %ss)." % (audit["n_heavy_mapped"], audit["expected_heavy_mapped"],
                                           audit["lomap_time_s"]), flush=True)
        return audit
    msg = ("DEGENERATE ATOM MAP on leg %s: LOMAP mapped %d heavy atoms but the endpoints' own MCS says %d "
           "MUST map (A has %d heavy, B has %d). The %d unmapped heavy atom(s) become dummies that are "
           "annihilated and recreated, so this leg would run a DIFFERENT perturbation from the designed one "
           "and would still converge and still return a confident ΔG. Most likely the MCS hit its %ss budget "
           "(RBFE_LOMAP_TIME_S) — raise it and re-run."
           % (leg_id, audit["n_heavy_mapped"], audit["expected_heavy_mapped"], audit["heavy_atoms_A"],
              audit["heavy_atoms_B"], audit["expected_heavy_mapped"] - audit["n_heavy_mapped"],
              audit["lomap_time_s"]))
    if hard:
        raise SystemExit("  ABORT (degenerate-map guard): " + msg)
    print("  [tfep] ⚠ " + msg, flush=True)
    return audit


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
    # ★ THE MAP IS THE EXPERIMENT — CHECK IT BEFORE ANY SAMPLING IS PAID FOR. A timed-out LOMAP MCS returns
    # its best PARTIAL match silently, and no other check in this pipeline can see it: protocol_hash covers
    # the settings, system-identity covers particle counts (unchanged by dummies), and the 5-part gate's
    # item 2 actively READS unmapped atoms as evidence of "a real perturbation". See expected_heavy_map_size.
    map_audit = assert_map_not_degenerate(atom_map_audit(Chem, ligA, ligB, mapping), LEG_ID)
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
                   "atom_map": map_audit,
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
    # SYSTEM IDENTITY IN THE LEG RECORD (2026-07-25). ΔΔG_coop is a DIFFERENCE of legs and |ΔG_fwd + ΔG_rev| is a
    # SUM of them, so both are meaningless unless the legs describe the SAME system. The record carried
    # protocol_hash, n_windows and starting_model but NOT the particle count or which setup cache was used --
    # so the reduce's per-leg forensic table, whose entire purpose is auditing cross-leg comparability, was
    # missing the most basic system-identity number. Answering "did fwd and rev use the same system?" today meant
    # excavating a five-day-old CI log belonging to a DIFFERENT workflow (the setup prime), and the answer
    # mattered: the four failed rev attempts ran a 146,020-particle v1 build against fwd's 141,968-particle v2pe
    # one. Both values are already in hand here -- printed one line away in the prime branch above.
    _setup_cache = _ana_keys.get("cache_dir") if isinstance(_ana_keys, dict) else None
    _n_particles = _ana_keys.get("n_particles") if isinstance(_ana_keys, dict) else None
    out = {"leg_id": LEG_ID, "environment": env, "morph": "%s->%s" % (a, b), "direction": DIRECTION,
           "seed": SEED, "dg_morph_kcal": float(dg_kcal) if dg_kcal is not None else None,
           "mbar_se_kcal": float(unc_kcal) if unc_kcal is not None else None, "n_mapped_atoms": n_mapped,
           # WHICH PERTURBATION THIS LEG ACTUALLY RAN. `n_mapped_atoms` alone cannot answer that — it has no
           # expectation to be read against, so a short map and a complete one look identical in the record.
           # Carrying the derived expectation and the MCS budget alongside it means that if an EARLIER
           # replicate is later found to have run under a degenerate map, anyone can tell which legs are
           # comparable to which without re-deriving anything.
           "atom_map": map_audit,
           "n_windows": N_WINDOWS, "spot_safe": True,
           "protocol_hash": proto_hash, "protocol_settings": proto_payload,
           "starting_model": starting_model,
           "n_particles": _n_particles, "setup_cache_dir": _setup_cache,
           # ⚠ RECORD THE **RESOLVED** CHARGE METHOD, NOT THE RAW ENV. The protocol payload above hashes
           # `os.environ.get("CHARGE_METHOD", "am1bcc")` — WITH the default — while this line used to write the
           # bare env, so a run that did not set the variable produced a leg whose protocol_hash commits to
           # am1bcc and whose identity record says `null`. `ternary_fep_reduce._system_identity_consistency`
           # then reports the field as UNRECORDED across the whole cycle and, correctly, refuses to call that
           # agreement — which is exactly what happened to the 4 fs cycle on 2026-07-26: three legs sharing one
           # protocol hash but with no system identity recorded at all, so comparability rested on a hash that
           # by construction does not cover the system. One resolved value, written in both places.
           "charge_method": os.environ.get("CHARGE_METHOD", "am1bcc"),
           # Same defect, same fix: `nr4a3_rbfe` keys its setup cache on
           # `os.environ.get("SETUP_CACHE_VERSION", "v1")`, so a leg that ran without the variable used **v1**
           # — while this line recorded `null` and the reduce reported the field UNRECORDED across the cycle.
           # Record what the run RESOLVED, not what happened to be exported.
           "setup_cache_version": os.environ.get("SETUP_CACHE_VERSION", "v1")}
    # ⚠ SAY SO AT WRITE TIME. A missing identity field is only discoverable at reduce time otherwise — which is
    # how the 4 fs cycle reached a verdict with `system_identity_consistency` UNKNOWN across all three legs and
    # nobody noticing until the reduction was read by hand. `n_particles` comes from the analysis keys and is
    # None unless the setup was primed, so it is the one that can still go missing.
    for _k in ("n_particles", "charge_method", "setup_cache_version"):
        if out.get(_k) in (None, ""):
            print(f"  [tfep] ⚠ IDENTITY FIELD MISSING: {_k} is unset on leg {LEG_ID}. ddG_coop is a DIFFERENCE "
                  f"of legs, and protocol_hash does NOT cover the system — a cycle built from legs that cannot "
                  f"be identity-checked is comparable only by assumption.", flush=True)
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
