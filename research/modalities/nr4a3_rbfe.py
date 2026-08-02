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
# Replicate index / RNG seed. `or "0"` rather than a dict default, because a shell that exports `SEED=` (an
# EMPTY string, which is what `env SEED="$SEED"` produces when the launcher did not set one) makes
# `os.environ.get("SEED", "0")` return `""` and `int("")` raise — a crash on a rented GPU, in the setup
# phase, for a variable this engine had never used. Unset and empty must both mean 0, exactly as
# `rbfe_spot_checkpoint.system_fingerprint_fields` already treats them.
SEED = int((os.environ.get("SEED") or "0").strip() or "0")
# The env var VERBATIM, which is what the resume fingerprint hashes (unset and "" hash the same, "0" does
# NOT hash the same as unset). Kept separate from the int so provenance records what was SET, not what was
# parsed — the two differ exactly at the case that matters.
SEED_ENV_RAW = os.environ.get("SEED")


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
    # ★★ STRIP INHERITED CHARGES AT THE DOOR, not after the molecule has been rebuilt (2026-07-29).
    # This is the ONE place a pose SDF becomes an RDKit mol for both alchemical lanes — the binary
    # (`nr4a3_rbfe._build_components`) and the ternary (`nr4a3_ternary_fep._endpoint_pose`) — so it is the
    # only boundary at which the charges are still in the state the file described. Downstream is too late in
    # a way that matters: `_repair_pose` re-adds hydrogens that cannot inherit a per-atom charge, turning a
    # COMPLETE set (which OpenFF would silently prefer over the protocol's own charge model) into a PARTIAL
    # one (which kills the leg on a rented GPU). Full reasoning: `strip_foreign_partial_charges`.
    recs = []
    for m in rdkit_chem.SDMolSupplier(sdf_path, removeHs=False):
        if m is None:
            continue
        m, n = strip_foreign_partial_charges(m)
        if n:
            print(f"  [rbfe] {os.path.basename(sdf_path)}: dropped {n} inherited partial charge(s) from record "
                  f"{m.GetProp('_Name') if m.HasProp('_Name') else '?'} ({m.GetNumAtoms()} atoms) — a pose file "
                  f"is a COORDINATE carrier; this protocol assigns its own charges.", flush=True)
        recs.append(m)
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


# gufe stores an OpenFF molecule's partial charges on the RDKit mol under exactly this key, and
# `SmallMoleculeComponent._check_partial_charges` reads it back. One name, one home — the forensic
# (`valb_triangle_charge_forensic.py`) and the guard below must never disagree about the spelling.
FOREIGN_CHARGE_PROPS = ("atom.dprop.PartialCharge", "atom.dprop.PartialCharges")

# ⚠ THE SAME CHARGES, AT A SECOND LEVEL, UNDER A DIFFERENT NAME. RDKit's SD parser expands a property list
# named `atom.dprop.<X>` into a per-ATOM property `<X>` on every atom (`processPropertyLists`, on by default),
# and `openff.toolkit.Molecule.to_rdkit()` writes both levels too. `openff`'s `from_rdkit` reads the PER-ATOM
# one — never the molecule-level array — so clearing only the array leaves the charges fully live. Same
# reasoning as above: one name, one home.
PER_ATOM_CHARGE_PROP = "PartialCharge"


def strip_foreign_partial_charges(mol):
    """Drop any partial charges a pose file carried IN — at BOTH levels RDKit stores them — and say how many
    values were dropped. PURE-ish (mutates and returns `mol`), no RDKit-version-specific API.

    ★ WHY THIS EXISTS (measured 2026-07-27, the valB closure triangle). `ternary_preequil._write_relaxed`
    writes its relaxed endpoints via `openff.toolkit.Molecule.to_rdkit()`, which stamps the RELAXATION
    force field's charges onto the mol as `atom.dprop.PartialCharge`; `Chem.SDWriter` then persists that
    into `ligands.sdf`, and `run_ternary_leg.sh` step 2 copies that SDF over the staged one. RDKit COPIES
    molecule-level properties through `RemoveHs` -> element swap -> `AddHs` -> `AssignBondOrdersFromTemplate`
    (reproduced: a 15-value array survives intact onto a 16-atom mol), so the array rides all the way to
    `SmallMoleculeComponent.from_rdkit` describing a molecule that no longer exists.

    ★★ AND CLEARING THE ARRAY ALONE DOES NOT REMOVE THE CHARGES — measured 2026-07-29, after the first
    version of this function did exactly that and the legs went on dying. RDKit's SD parser turns the single
    `atom.dprop.PartialCharge` tag into a per-ATOM `PartialCharge` double on every atom as it reads the file
    (`Chem.SDMolSupplier`, `processPropertyLists` default-on; reproduced on a 9-atom mol: writing the tag,
    reading it back and inspecting `atom.HasProp("PartialCharge")` returns True for all 9). `mol.ClearProp`
    cannot see those. Worse, `_repair_pose`'s `RemoveHs -> AssignBondOrdersFromTemplate -> AddHs` keeps them on
    the heavy atoms it preserved and cannot put them on the hydrogens it re-adds, so the mol that reaches
    OpenFF has SOME atoms charged and some not — which is precisely the exception the ternary legs died on:

        openff/toolkit/utils/rdkit_wrapper.py:2351 in from_rdkit
        ValueError: Some atoms in rdmol have partial charges, but others do not.

    reached from `proto.create` -> `_validate_smcs` -> `SmallMoleculeComponent.to_openff()`. The archive of
    every rented attempt dates the transition exactly: on `calib_hi_to_lo__ternary_vhl` r2 (49 attempts) that
    signature first appears at 2026-07-28T02:12Z and accounts for 37 of them, and it appears in NO attempt
    before the molecule-level strip landed at 2026-07-28T00:54Z. The strip worked; it just moved the failure
    from the level gufe checks to the level OpenFF reads.

    THREE failure modes, and the THIRD is the dangerous one:
      * mol-level count DISAGREES -> gufe raises `ValueError: Incorrect number of partial charges: 109  were
        provided for 110 atoms` at `SmallMoleculeComponent.from_rdkit`. Loud. (Pre-2026-07-28.)
      * per-atom coverage is PARTIAL -> openff raises `Some atoms in rdmol have partial charges, but others do
        not` at `to_openff()`, and the leg dies minutes into a billed rental. Loud. (2026-07-28 onward.)
      * per-atom coverage is COMPLETE -> nothing raises at all, and OpenFF PREFERS user-supplied charges over
        generating its own, so the leg runs on relaxation charges while `_protocol()` reports
        `partial_charge_method = nagl`. A ternary leg and its binary partner could then carry different
        charges, and ΔΔG_coop = ternary − binary only cancels the charge model if BOTH sides used it. Silent,
        and it is the reason this must strip unconditionally rather than only when something is about to break.

    So the charges a pose file arrives with are never this protocol's charges, and the correct handling of all
    three cases is the same: remove them, at every level, and let the protocol assign its own. Returns
    (mol, n_dropped) — the larger of the two levels' counts — so the caller can LOG a non-zero drop; a guard
    that fires silently is how the third failure mode got here.
    """
    dropped = 0
    if mol is None:
        return mol, 0
    for key in FOREIGN_CHARGE_PROPS:
        if mol.HasProp(key):
            try:
                dropped = max(dropped, len(mol.GetProp(key).split()))
            except Exception:  # noqa: BLE001
                dropped = max(dropped, 1)
            mol.ClearProp(key)
    # The per-atom level. Counted separately and folded into the same return value, because a mol whose array
    # was already cleared upstream can still be carrying a full set of per-atom charges — that is exactly the
    # state the 2026-07-28 deaths were in, and reporting 0 for it is how it stayed invisible.
    n_atom = 0
    for atom in mol.GetAtoms():
        if atom.HasProp(PER_ATOM_CHARGE_PROP):
            atom.ClearProp(PER_ATOM_CHARGE_PROP)
            n_atom += 1
    return mol, max(dropped, n_atom)


def foreign_charge_census(mol):
    """(n_mol_level_values, n_atoms_carrying_a_per_atom_charge, n_atoms). PURE, no mutation.

    The measurement `strip_foreign_partial_charges` is graded against, and the one the engine boundary asserts
    on. Separate from the stripper on purpose: a guard that can only be tested through the thing it guards is
    a guard nobody can prove.
    """
    if mol is None:
        return 0, 0, 0
    n_arr = 0
    for key in FOREIGN_CHARGE_PROPS:
        if mol.HasProp(key):
            try:
                n_arr = max(n_arr, len(mol.GetProp(key).split()))
            except Exception:  # noqa: BLE001
                n_arr = max(n_arr, 1)
    n_atom = sum(1 for a in mol.GetAtoms() if a.HasProp(PER_ATOM_CHARGE_PROP))
    return n_arr, n_atom, mol.GetNumAtoms()


def assert_no_foreign_charges(mol, where):
    """Refuse to hand OpenFE a molecule still carrying charges this protocol did not assign.

    ★ WHY AN ASSERTION AND NOT A SECOND STRIP (2026-07-29). The failure this closes was not "we forgot to
    strip" — it was "we stripped the level we knew about and shipped the level we did not", and the shipped
    level was invisible for a day and 84 rented hosts because nothing ever checked the RESULT. A stripper
    verifies its own assumptions; a census taken at the boundary verifies the molecule. If a third storage
    level ever appears, this is what finds it — on a CPU, in CI, instead of on a GPU we are paying for.
    Raises SystemExit (the lane's fail-closed convention) naming the level and the counts.
    """
    n_arr, n_atom, n_tot = foreign_charge_census(mol)
    if n_arr or n_atom:
        raise SystemExit(
            "  ABORT: %s still carries partial charges that this protocol did not assign "
            "(molecule-level array=%d value(s), per-atom `%s`=%d of %d atom(s)). A pose file is a COORDINATE "
            "carrier: OpenFE prefers user-supplied charges over the configured partial_charge_method, so "
            "running this would silently substitute a relaxation force field's charge model — and ΔΔG_coop = "
            "ternary − binary only cancels the charge model if BOTH arms used the same one. "
            "Fix `nr4a3_rbfe.strip_foreign_partial_charges` rather than relaxing this check."
            % (where, n_arr, PER_ATOM_CHARGE_PROP, n_atom, n_tot))


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
    # The last point at which a charge the docked pose carried in can still be caught on a CPU. `_sdf_mol`
    # strips at the door; this proves the rebuild above did not resurrect anything.
    for _nm, _m in (("binary endpoint A", molA), ("binary endpoint B", molB)):
        assert_no_foreign_charges(_m, _nm)
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

    # ★ THE MCS BUDGET IS A CORRECTNESS PARAMETER, NOT A PERFORMANCE ONE (2026-07-26).
    # `time` is LOMAP's MCS timeout in SECONDS, and a timed-out MCS returns the best PARTIAL match it has
    # found — silently. So the atom map, i.e. WHAT THE ALCHEMICAL TRANSFORMATION ACTUALLY IS, depended on how
    # fast the host happened to be. Measured on RUNG 5a-KS: the same edge, whose two ligands differ by ONE
    # ATOM and therefore admit a complete 111-atom 1:1 map, mapped 111 atoms on two hosts and **80 atoms with
    # 31 dummies** on a third — at `element_change` BOTH True and False, which is the signature of a timeout
    # rather than of a chemistry difference (a real element-change asymmetry moves the two settings apart, and
    # that is the entire reason this function computes both). `threed=False` makes the map pose-independent,
    # so neither the MD, nor the platform, nor the conformer can explain it; wall-clock can.
    # A partial map is not a slow answer, it is a DIFFERENT EXPERIMENT: 31 atoms that should have mapped 1:1
    # become dummies that are annihilated and recreated. Left unchecked it converges and returns a confident
    # number for a perturbation nobody designed.
    # Raising the budget cannot make a previously-correct map worse — a longer search can only find an
    # equal-or-larger MCS — and `RBFE_LOMAP_TIME_S` keeps the old value reachable for an exact re-run.
    _t = int(os.environ.get("RBFE_LOMAP_TIME_S", "300"))

    def _suggest(element_change):
        return next(LomapAtomMapper(time=_t, threed=False,
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
            # ⚠ SAY WHEN THE MAP IS DEGENERATE, AT THE POINT IT IS PRODUCED. When both molecules have the same
            # heavy-atom count the edge is an element change or a pure re-pose, and a COMPLETE 1:1 map provably
            # exists — so a short map is a failed search, not a property of the chemistry. Downstream this is
            # only caught by `ternary_endpoint_align.verify_endpoints` (and only on lanes that run it); every
            # other consumer would use the partial map silently.
            try:
                _nA = ligA.to_rdkit().GetNumAtoms()
                _nB = ligB.to_rdkit().GetNumAtoms()
                if _nA == _nB and best[0] < _nA:
                    print(f"[rbfe] ⚠ DEGENERATE MAP: {best[0]} of {_nA} atoms mapped for {nA}->{nB} although "
                          f"both endpoints have {_nA} atoms, so a complete 1:1 map exists. {_nA - best[0]} "
                          f"atom(s) would become dummies and the leg would run a DIFFERENT perturbation from "
                          f"the designed one. Most likely the MCS hit its {_t}s budget "
                          f"(RBFE_LOMAP_TIME_S); re-run with a larger one.", flush=True)
            except Exception:  # noqa: BLE001 — a diagnostic must never break the mapping it describes
                pass
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
            # ★★ A STRICT MAP BELOW ITS PROVABLE FLOOR IS ESCALATED, NOT ACCEPTED (2026-07-27, root-causing
            # the step 1 fan-out's `leg-complex-FAILED-rc1` on s1f-09 cw_bio_nmethyl_amide).
            #
            # WHAT WENT WRONG. The loop above returns the FIRST setting that yields any mapping, and that is
            # element_change=False by design — correct for a pure append. But `zaienne_cmpd19` is a methyl
            # ESTER (`COC(=O)c1c[nH]c2ccc(Br)cc12`) and `cw_bio_nmethyl_amide` is the N-methyl AMIDE
            # (`CNC(=O)…`): one heavy-atom O->N substitution, MID-CHAIN. A strict-element MCS cannot cross it,
            # and severing there also strands everything beyond — the ester O, the methyl C and its 3 H, i.e.
            # exactly 5 atoms. Measured with rdkit alone: element-exact MCS = 17 atoms, element-agnostic = 22,
            # `canceled=False` on both in milliseconds. 22 - 5 = 17, and 17 < the provable floor of 20, so
            # `_check_mapping_sane` aborted the leg rc=1 — on a map this function never had to settle for,
            # because the ec=True branch was never reached at all.
            #
            # ⚠ CORRECTION, REGISTERED RATHER THAN DROPPED (rule 1). The first version of this comment said
            # "element_change=True maps all 22". That was an rdkit-MCS number read as a LOMAP prediction, and
            # it is wrong: measured on the PRODUCTION staged components, LOMAP ec=True reaches **19**, not 22
            # (step1-map-diag.json, 2026-07-27). So this escalation improves the map 17 -> 19 and the edge
            # STILL aborts, correctly, at the floor of 20. The escalation is right and insufficient; what it
            # buys is that the abort is now on the best map LOMAP can produce rather than on an unexamined
            # one. cw_bio_nmethyl_amide is therefore NOT a retry candidate — see the lane record.
            #
            # WHY THIS IS NOT THE TIMEOUT the abort message used to guess at. A timed-out MCS moves BOTH
            # settings together and burns its budget; this separates them and returns instantly. The budget
            # was never binding — `atom_map_audit.maps` measured t20 == t300 in 0.0-1.4 s on all 19 congeneric
            # edges. `step1_map_diag.py` runs the 2x2 {element_change} x {budget} matrix on the PRODUCTION
            # staged components for the record.
            #
            # ⚠ WHY THIS IS SAFE TO LAND UNDER A LIVE FLEET, which is the only reason it is written this way.
            # The clause is reachable ONLY when the strict map is BELOW the provable floor — and any leg that
            # is running has already passed `_check_mapping_sane`, i.e. its map is AT OR ABOVE that same
            # floor. So for every edge currently in flight this is dead code and the returned mapping is
            # byte-identical. Swept across all 19 fan-out edges (2026-07-27): exactly one, this one, has a
            # strict map below its floor. Changing the map of a leg that is mid-flight would be a silent
            # protocol deviation, and this cannot do it.
            if ec is False:
                floor, complete, _n = _provable_map_floor(ligA, ligB)
                if floor is not None and nmap < floor:
                    print(f"[rbfe] element_change=False mapped {nmap} atoms, BELOW the provable floor {floor}"
                          + (f" (a complete map of {complete} atoms exists)" if complete else "")
                          + f" for {nA}->{nB} — a strict-element MCS cannot cross an element substitution, so "
                            f"trying element_change=True before accepting this map", flush=True)
                    try:
                        m_ec = _suggest(True)
                        n_ec = len(m_ec.componentA_to_componentB)
                        print(f"[rbfe] LOMAP element_change=True: {n_ec} mapped atoms for {nA}->{nB} "
                              f"(provable-floor escalation)", flush=True)
                        if n_ec > nmap:
                            print(f"[rbfe] floor escalation -> using the {n_ec}-atom element_change=True map "
                                  f"for {nA}->{nB}", flush=True)
                            return m_ec
                        print(f"[rbfe] element_change=True is no larger ({n_ec} <= {nmap}); keeping the strict "
                              f"map and letting the floor guard judge it", flush=True)
                    except StopIteration:
                        print(f"[rbfe] element_change=True returned NO mapping for {nA}->{nB}; keeping the "
                              f"{nmap}-atom strict map and letting the floor guard judge it", flush=True)
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
    _apply_seed(s)
    return RelativeHybridTopologyProtocol(s)


# ★★ WHAT "SEEDING" CAN AND CANNOT MEAN HERE — MEASURED AGAINST THE ACTUAL LIBRARY SOURCE, 2026-07-31.
#
# The fan-out's replicate axis (`congeneric_fanout.replicate_units`) exports SEED=<replicate index>. Before
# writing anything that LOOKS like seeding, the question "how does OpenFE want a seed set?" was answered by
# reading OpenFE's and openmmtools' source rather than by pattern-matching another lane:
#
#   * openfe `src/openfe/protocols/openmm_utils/omm_settings.py` — `grep -i seed` returns NOTHING. No
#     settings group (IntegratorSettings, MultiStateSimulationSettings, OutputSettings, …) exposes a seed.
#   * openfe `src/openfe/protocols/openmm_rfe/hybridtop_units.py::_get_integrator` builds
#     `openmmtools.mcmc.LangevinDynamicsMove(timestep, collision_rate, n_steps, reassign_velocities,
#     n_restart_attempts, constraint_tolerance)` — no seed argument, and `_get_sampler`'s kwargs carry none
#     either.
#   * openmmtools `mcmc.py::LangevinDynamicsMove._get_integrator` constructs
#     `openmm.LangevinMiddleIntegrator(...)` and never calls `setRandomNumberSeed`, so the integrator keeps
#     OpenMM's default seed 0 — which OpenMM documents as "a unique seed is chosen when a Context is
#     created". The thermostat stream is therefore drawn FROM THE OS, per Context, per run.
#   * openmmtools `multistate/replicaexchange.py` draws its replica-swap moves from the GLOBAL NumPy RNG
#     (`np.random.randint` / `np.random.rand`, lines 324-400).
#
# So, stated plainly rather than papered over:
#   1. There is NO protocol-settings seed field to set. A `hasattr(settings, "random_seed")` probe on this
#      openfe silently sets nothing at all — it is the shape of seeding without the substance, and this
#      function refuses to be that: it PRINTS which mechanisms it reached and which it could not.
#   2. Two runs of the same edge are ALREADY independent draws, because the Langevin/velocity seed is
#      OS-drawn per Context. Independence — the property a replicate SD actually requires — does not depend
#      on anything below. What was missing from this lane was never independence; it was IDENTITY (a
#      replicate had nowhere to land, see `congeneric_fanout.unit_id`) and RESUME ISOLATION.
#   3. What this function CAN control honestly is the global NumPy RNG that openmmtools' replica mixing
#      draws from. Seeding it makes the mixing stream a deterministic function of the replicate index
#      instead of an OS draw, so replicate 1 and replicate 2 are separated by construction and not merely
#      by luck. It does NOT make a run bit-reproducible, and this must never be claimed: the dominant
#      stochastic source (the thermostat) remains OS-seeded and unreachable through the public API.
def _apply_seed(settings):
    """Seed every RNG stream this protocol can actually reach, and SAY which. Returns a report dict.

    Applied only when SEED is non-zero, so the 18 landed n=0 edges keep the exact RNG behaviour they were
    computed with (an unseeded global NumPy RNG). `nr4a3_metad.py` makes the same choice for the same
    reason: SEED=0 keeps legacy behaviour, a non-zero SEED is the deliberate, recorded one."""
    report = {"seed": SEED, "seed_env_raw": SEED_ENV_RAW, "applied": [], "not_available": []}
    # FUTURE-PROOFING, NOT THE MECHANISM. If a future openfe grows a seed field, use it — but never let its
    # absence pass silently, which is the whole failure mode this block is written against.
    for grp in ("simulation_settings", "integrator_settings"):
        sub = getattr(settings, grp, None)
        for attr in ("random_seed", "sampler_seed"):
            if sub is not None and hasattr(sub, attr):
                try:
                    setattr(sub, attr, SEED)
                    report["applied"].append(f"{grp}.{attr}={SEED}")
                except Exception as e:  # noqa: BLE001
                    report["not_available"].append(f"{grp}.{attr} present but not settable ({e})")
            else:
                report["not_available"].append(f"{grp}.{attr}")
    if not SEED:
        print("  [rbfe][seed] SEED=0 (unset) — RNG streams left at library defaults, identical to every "
              "n=0 unit already computed on this map.", flush=True)
        return report
    try:
        import random as _random

        import numpy as _np
        _np.random.seed(SEED)
        _random.seed(SEED)
        report["applied"].append(f"numpy.random.seed({SEED}) + random.seed({SEED})")
    except Exception as e:  # noqa: BLE001 — a seeding failure must never cost a rented leg
        report["not_available"].append(f"numpy/random global seed ({e})")
    print(f"  [rbfe][seed] SEED={SEED} applied: {report['applied'] or 'NOTHING'}", flush=True)
    print("  [rbfe][seed] NOT reachable through the public API (measured against openfe/openmmtools "
          f"source, see the block above): {report['not_available']}", flush=True)
    print("  [rbfe][seed] The Langevin thermostat/velocity stream is seeded BY OPENMM from the OS on every "
          "Context, so replicates are independent draws by construction; this run is NOT bit-reproducible "
          "and must not be described as such.", flush=True)
    return report


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


def _provable_map_floor(ligA, ligB):
    """The PROVABLE minimum map size for this edge, or (None, why) when it cannot be derived.

    Delegates to `atom_map_audit.edge_bounds` so the floor has exactly one home (rule 1) and the audit that
    found the contamination and the guard that prevents the next one cannot drift apart. Returns
    (floor, expected_complete, note)."""
    try:
        from rdkit import Chem
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import atom_map_audit as ama
        smiA = Chem.MolToSmiles(Chem.RemoveHs(Chem.Mol(ligA.to_rdkit())))
        smiB = Chem.MolToSmiles(Chem.RemoveHs(Chem.Mol(ligB.to_rdkit())))
        b = ama.edge_bounds("A", smiA, "B", smiB)
        return b.get("total_floor_enforced"), b.get("expected_n_mapped_atoms"), b.get("floor_note")
    except Exception as e:  # noqa: BLE001 — an underivable floor must be SAID, never silently treated as clean
        return None, None, "floor not derivable: %s: %s" % (type(e).__name__, e)


def _check_mapping_sane(mapping, ligA, ligB, n_mapped):
    """HARD-FAIL before any MD spend if the atom map is degenerate. Two independent floors, both fatal.

    1. THE PROVABLE FLOOR (added 2026-07-26, the atom-map blast-radius audit). `_mapping` ran LOMAP with
       `time=20`, which is the MCS TIMEOUT — a timed-out search returns its best PARTIAL map SILENTLY, so what
       the leg alchemically transformed depended on how fast its rented host was. Raising the budget to 300 s
       makes that rarer; it does NOT make it detectable, and detection is the part that has to survive the next
       slower host. `atom_map_audit.edge_bounds` derives, from the two endpoints alone, the smallest map any
       correct search must return — for endpoints that are the same graph up to k element substitutions that is
       |A| minus those k atoms, the H they carry, and the atom-count difference, so a legitimate STRICT
       (element_change=False) map still clears it and the fan-out's congeneric edges are not false-positived.
       Measured against this floor, three archived observations separate cleanly: valB_mini r0 mapped 109/109
       (CLEAN), the 5a-KS NR4A1 arm 80/111 and the RUNG 2b timestep scan's calib anchor 47/109 (DEGENERATE).
    2. THE FRACTIONAL FLOOR (2026-07-14, the n_mapped=1 solvent-leg forensic). Kept as the fallback for edges
       whose provable floor cannot be derived, and as a second net when it can. Tune with RBFE_MIN_MAPPED_FRAC
       (default 0.4 of the smaller ligand's heavy-atom count) / RBFE_MIN_MAPPED (absolute floor, default 3).

    A FAILURE TO DERIVE THE FLOOR IS REPORTED, NOT SWALLOWED. This repo has twice had a null reading rendered
    as a benign one; an underivable floor prints UNVERIFIABLE and leaves floor 2 in force, it never passes the
    leg silently. Set RBFE_MAP_FLOOR_FATAL=0 to demote floor 1 to a warning — only for a deliberate re-run of a
    known-degenerate map, never to get a leg past a genuine abort."""
    try:
        hA = ligA.to_rdkit().GetNumHeavyAtoms()
        hB = ligB.to_rdkit().GetNumHeavyAtoms()
    except Exception:  # noqa: BLE001
        hA = hB = None

    provable, complete, note = _provable_map_floor(ligA, ligB)
    if provable is None:
        print(f"  [rbfe] ⚠ map floor UNVERIFIABLE for {LIGAND_A}->{LIGAND_B} ({note}) — this is NOT a clean "
              f"reading, only an absent one; the fractional floor below is the sole remaining check.", flush=True)
    elif n_mapped < provable:
        msg = (f"  ABORT: DEGENERATE atom map — mapped {n_mapped} atoms for {LIGAND_A}->{LIGAND_B}, below the "
               f"PROVABLE floor {provable}"
               + (f" (a complete map of {complete} atoms exists)" if complete else "")
               + f". {note} {provable - n_mapped} atom(s) that must map would instead be annihilated and "
                 f"recreated, so this leg would run a DIFFERENT perturbation from the designed one — and it "
                 f"would still converge and still report a confident ΔG. Do NOT spend MD on this map. TWO "
                 f"mechanisms produce this and they need OPPOSITE fixes — run `step1_map_diag.py` (CPU, $0) "
                 f"to tell them apart rather than guessing: (a) the MCS hit its "
                 f"{os.environ.get('RBFE_LOMAP_TIME_S', '300')}s budget (RBFE_LOMAP_TIME_S) — the map then "
                 f"GROWS with the budget and the search burns it; raise it and re-run; (b) an ELEMENT "
                 f"substitution the strict map cannot cross — the two element_change settings then separate "
                 f"and both return instantly, and `_mapping` escalates to element_change=True by itself, so "
                 f"seeing this abort means even that map is short. "
                 f"⚠ THIS MESSAGE USED TO ASSERT (a) AS 'most likely'; on the one edge that ever raised it "
                 f"(zaienne_cmpd19->cw_bio_nmethyl_amide, 2026-07-27) the cause was (b) and the budget was "
                 f"never binding.")
        if os.environ.get("RBFE_MAP_FLOOR_FATAL", "1") == "1":
            raise SystemExit(msg)
        print("  [rbfe] ⚠ (RBFE_MAP_FLOOR_FATAL=0, continuing anyway)" + msg, flush=True)
    else:
        print(f"  [rbfe] map floor OK: {n_mapped} mapped >= provable floor {provable}"
              + (f" (complete = {complete})" if complete else ""), flush=True)

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
           "unc_kcal": float(unc.to("kilocalorie_per_mole").m), "n_mapped_atoms": n_mapped,
           "seed": SEED, "seed_env_raw": SEED_ENV_RAW}
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
    # valA known-answer benchmark (nr4a3-program-map.md RUNG 1 kill-switch): if a valA_manifest.json with a measured
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
           # Which independent draw this leg IS. Without it a collected replicate is a number with no way
           # back to the run that produced it, and a replicate SD assembled from unlabelled draws is not
           # auditable. `seed_env_raw` is null for every n=0 leg, which is exactly how the resume
           # fingerprint sees it (unset != "0").
           "seed": SEED, "seed_env_raw": SEED_ENV_RAW,
           "via": "split(setup|simulate|analyze)"}
    json.dump(out, open(os.path.join(CKPT, f"leg_{RECEPTOR}_{LEG}.json"), "w"), indent=2)
    print(f"  [rbfe][analyze] DONE {RECEPTOR}/{LEG}: ΔG_morph={dg:.2f} ± {out['unc_kcal']:.2f}", flush=True)


def count_unconstrained_alchemical_xh(system):
    """Return (n_xh_total, n_unconstrained, unconstrained_list, hmasses_seen) counting ONLY genuine bond-STRETCH
    terms that are NOT in the constraint set.

    CRITICAL (measured 2026-07-19 via the perses force dump): a CustomBondForce is used by perses for TWO different
    things — (A) alchemical VALENCE bonds (per-bond params length1/K1/length2/K2) and (B) alchemical NONBONDED
    EXCEPTIONS (params chargeProd/sigma/epsilon). Only (A) is a real bond; (B) entries are 1-2/1-3/1-4 exception
    PAIRS, not stretch bonds. An earlier version of this counter scanned every CustomBondForce and so counted the
    (B) exception pairs as "unconstrained X-H bonds" — e.g. it reported the pilot's 14 exception pairs as 14
    unconstrained bonds when the ligand's real C-H are CONSTRAINED (they appear in NO bond force -> they are
    constraints, inside total_constraints). That miscount made the pilot read 2 fs and produced the false "OpenFE
    leaves the whole ligand unconstrained" conclusion. This version counts a CustomBondForce ONLY when its per-bond
    parameter names look like a valence bond ('length' present, 'chargeprod'/'sigma'/'epsilon' absent). Result: the
    only unconstrained X-H are the genuinely ALCHEMICAL stretch bonds (a morphing C-H/N-H whose constraint status
    changes between endpoints, so it cannot be constrained) — which IS a per-edge property and the real timestep
    driver. `unconstrained_list` is [(h_atom_idx, h_mass_amu), ...]."""
    import openmm as _mm
    cons = set()
    for k in range(system.getNumConstraints()):
        i, j, _d = system.getConstraintParameters(k)
        cons.add((min(int(i), int(j)), max(int(i), int(j))))
    mass = [system.getParticleMass(p).value_in_unit(_mm.unit.dalton) for p in range(system.getNumParticles())]
    is_h = lambda m: m < 5.0            # H (1.008) or HMR-repartitioned H (3-4); heavy atoms >= 12
    xh_total = xh_unconstrained = 0
    unc = []
    for f in system.getForces():
        if isinstance(f, _mm.HarmonicBondForce):
            pass                                          # standard valence bonds — always real stretch terms
        elif isinstance(f, _mm.CustomBondForce):
            try:
                names = " ".join(f.getPerBondParameterName(p)
                                 for p in range(f.getNumPerBondParameters())).lower()
            except Exception:  # noqa: BLE001
                names = ""
            # keep only the VALENCE bond force; skip the nonbonded-exception CustomBondForce (chargeProd/sigma/eps)
            if ("length" not in names) or any(t in names for t in ("chargeprod", "sigma", "epsilon")):
                continue
        else:
            continue
        for b in range(f.getNumBonds()):
            p = f.getBondParameters(b)
            i, j = int(p[0]), int(p[1])
            if is_h(mass[i]) ^ is_h(mass[j]):            # X-H stretch bond = exactly one light partner
                xh_total += 1
                hidx = i if is_h(mass[i]) else j
                if (min(i, j), max(i, j)) not in cons:
                    xh_unconstrained += 1
                    unc.append((hidx, round(mass[hidx], 3)))
    hmasses = sorted({round(m, 2) for m in mass if is_h(m)})
    return xh_total, xh_unconstrained, unc, hmasses


def count_morphing_xh(system, tol_nm=1e-4):
    """Count X-H bonds that are ALCHEMICALLY MORPHING — the quantity that actually caps the timestep.

    WHY A SECOND COUNTER (2026-07-24). `count_unconstrained_alchemical_xh` counts X-H bonds absent from the
    constraint set. That number is dominated by the global constraint SETTING, not by the edge:

      * with `constraints=hbonds` FORCED, OpenFE constrains every X-H — including the alchemical ones. Measured
        on both known-answer anchors: the alchemical valence CustomBondForce (params length1/K1/length2/K2)
        holds 11 and 28 bonds respectively and NOT ONE is an X-H, so the count is structurally 0 and every edge
        verdicts "4fs".
      * with OpenFE's default, the ligand's X-H are left unconstrained wholesale, so every edge verdicts "2fs".

    Either way the answer is a property of the setting, not of the perturbation — so it cannot discriminate
    edges, and a gate expecting one anchor to differ from the other can never pass. That is exactly why the
    per-edge scan has never run a designed edge.

    The discriminating quantity is narrower: an X-H bond whose EXISTENCE OR GEOMETRY CHANGES between the two
    alchemical endpoints. Such a bond cannot be given a single constraint length, so it stays flexible whatever
    the setting, and its ~10 fs period is what caps the stable timestep. In OpenFE's hybrid valence
    CustomBondForce (`length1, K1, length2, K2`) that is a bond with K1==0 xor K2==0 (appearing/disappearing) or
    length1 != length2 (re-hybridising) — on a bond with exactly one light partner.

    Must be evaluated on the system the PRODUCTION run builds; forcing constraints first hides the very bonds
    this is trying to find. Returns (n_morphing_xh, details)."""
    import openmm as _mm
    cons = set()
    for k in range(system.getNumConstraints()):
        i, j, _d = system.getConstraintParameters(k)
        cons.add((min(int(i), int(j)), max(int(i), int(j))))
    mass = [system.getParticleMass(p).value_in_unit(_mm.unit.dalton) for p in range(system.getNumParticles())]
    is_h = lambda m: m < 5.0                                     # noqa: E731  (H, or HMR-repartitioned H)
    found = []
    for f in system.getForces():
        if not isinstance(f, _mm.CustomBondForce):
            continue
        try:
            names = [f.getPerBondParameterName(p) for p in range(f.getNumPerBondParameters())]
        except Exception:  # noqa: BLE001
            continue
        low = " ".join(names).lower()
        if "length" not in low or any(t in low for t in ("chargeprod", "sigma", "epsilon")):
            continue                                             # nonbonded-exception force, not valence
        try:
            i_l1, i_k1 = names.index("length1"), names.index("K1")
            i_l2, i_k2 = names.index("length2"), names.index("K2")
        except ValueError:
            continue                                             # unexpected naming -> report nothing, loudly below
        for b in range(f.getNumBonds()):
            p = f.getBondParameters(b)
            i, j = int(p[0]), int(p[1])
            if not (is_h(mass[i]) ^ is_h(mass[j])):
                continue
            prm = p[2]
            l1, k1, l2, k2 = float(prm[i_l1]), float(prm[i_k1]), float(prm[i_l2]), float(prm[i_k2])
            appearing = (k1 == 0.0) != (k2 == 0.0)
            reshaped = abs(l1 - l2) > tol_nm
            if appearing or reshaped:
                found.append({"h_atom": i if is_h(mass[i]) else j,
                              "h_mass": round(mass[i] if is_h(mass[i]) else mass[j], 3),
                              "length1": l1, "K1": k1, "length2": l2, "K2": k2,
                              "appearing_or_vanishing": appearing, "re_hybridising": reshaped,
                              "constrained": (min(i, j), max(i, j)) in cons})
    return len(found), found


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
    LTOL = 1e-4   # nm; a bond is non-alchemical when its two endpoint lengths match to within this
    diag = {"harmonic_xh": 0, "custombond_forces": []}

    # (1) Standard HarmonicBondForce — non-alchemical environment/core bonds (protein etc.). Constrain X-H at r0.
    for f in system.getForces():
        if not isinstance(f, _mm.HarmonicBondForce):
            continue
        for b in range(f.getNumBonds()):
            i, j, length, k = f.getBondParameters(b)
            i, j = int(i), int(j)
            if (is_h(mass[i]) ^ is_h(mass[j])):
                diag["harmonic_xh"] += 1
                key = (min(i, j), max(i, j))
                if key not in cons:
                    system.addConstraint(i, j, length)
                    cons.add(key)
                    added += 1

    # (2) CustomBondForce — perses puts ALL the hybrid LIGAND's valence bonds here (verified 2026-07-19: the pilot's
    # 14 ligand X-H were ALL in the CustomBondForce, none in HarmonicBondForce). Its per-bond params carry BOTH
    # endpoint lengths (e.g. length_old/length_new or length1/length2). A bond is NON-alchemical iff the two lengths
    # match -> constrain it at that length. Alchemical bonds (lengths differ) are left flexible. We introspect the
    # per-bond parameter names to find the two length columns, so this is robust to perses' naming.
    for f in system.getForces():
        if not isinstance(f, _mm.CustomBondForce):
            continue
        try:
            pnames = [f.getPerBondParameterName(p) for p in range(f.getNumPerBondParameters())]
        except Exception as _pe:  # noqa: BLE001
            diag["custombond_forces"].append({"error": "getPerBondParameterName: %s" % _pe})
            continue
        lidx = [p for p, nm in enumerate(pnames) if "length" in nm.lower()]
        if len(lidx) < 2:
            lidx = [p for p, nm in enumerate(pnames) if nm.lower().startswith(("r1", "r2", "r_", "len"))]
        # sample a couple of X-H bonds' raw params so we can SEE the layout if the heuristic misses
        fdiag = {"n_bonds": f.getNumBonds(), "pnames": pnames, "length_cols": lidx, "n_xh": 0,
                 "n_xh_nonalch": 0, "sample_xh": []}
        for b in range(f.getNumBonds()):
            prm = f.getBondParameters(b)
            i, j = int(prm[0]), int(prm[1])
            vals = list(prm[2])
            if not (is_h(mass[i]) ^ is_h(mass[j])):
                continue
            fdiag["n_xh"] += 1
            if len(fdiag["sample_xh"]) < 4:
                fdiag["sample_xh"].append([i, j, [float(v) for v in vals]])
            if len(lidx) < 2:
                continue
            try:
                l_old, l_new = float(vals[lidx[0]]), float(vals[lidx[1]])
            except Exception:  # noqa: BLE001
                continue
            if abs(l_old - l_new) <= LTOL:
                fdiag["n_xh_nonalch"] += 1
                key = (min(i, j), max(i, j))
                if key not in cons:
                    system.addConstraint(i, j, 0.5 * (l_old + l_new))
                    cons.add(key)
                    added += 1
        diag["custombond_forces"].append(fdiag)
    print("  [constrain-lig] added=%d diag=%s" % (added, diag), flush=True)
    return added, diag


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

    # ---- S3 SETUP CACHE (2026-07-25, ADDITIVE — the GCS path below is untouched) -----------------------
    # WHY. This whole block already exists for GCS, and it is the difference between a preempted leg
    # resuming in seconds and re-solvating a ~146k-atom hybrid on a rented GPU that is idle while it does so.
    # The Vast ternary lane had no equivalent, so every resume rebuilt setup (~6-15 min of paid GPU-idle),
    # and — less obviously — the RAM/vCPU floor needed to make that rebuild fast is what narrows the offer
    # pool: the probe's post-preemption resume landed on a $0.2196/hr RTX 4080S where the original host was a
    # $0.1527/hr 4090, because the strict host filter left little to choose from.
    #
    # SAFETY. Selection is by ENV VAR and GCS WINS, so a lane that sets RBFE_SETUP_CACHE_GCS (the GCP ternary
    # lane, running in another session right now) takes byte-identical code paths to before. Both the restore
    # and the save are already wrapped in `except -> non-fatal`, so the worst case of a bug here is
    # "rebuild the setup", which is exactly today's behaviour.
    _S3_CACHE = os.environ.get("RBFE_SETUP_CACHE_S3")

    def _s3_client():
        import boto3
        return boto3.client("s3")

    def _s3_split(uri):
        bkt, _, key = uri[5:].partition("/")
        return bkt, key

    def _obj_exists(uri):
        if uri.startswith("s3://"):
            b, k = _s3_split(uri)
            try:
                _s3_client().head_object(Bucket=b, Key=k)
                return True
            except Exception:  # noqa: BLE001
                return False
        return _gsh("ls", uri).returncode == 0

    def _obj_download(uri, dest):
        if uri.startswith("s3://"):
            b, k = _s3_split(uri)
            _s3_client().download_file(b, k, str(dest))
            return
        r = _gsh("cp", uri, str(dest))
        if r.returncode:
            raise RuntimeError("cp %s: %s" % (uri, (r.stderr or "")[-200:]))

    def _gsh(*args):
        return _sub.run(["gcloud", "storage", *args], capture_output=True, text=True)

    def _gcs_upload(local_path, gs_uri):
        """Upload one file via the google-cloud-storage PYTHON client (clean single resumable upload). The gcloud
        CLI's `storage cp` uses a parallel-composite path for the large hybrid_system.xml.bz2 that fails opaquely
        with GcsApiError('') (empty message, non-retryable) — the python client does a plain upload and sidesteps
        it. Auth is ADC (WIF on the runner / SA on the VM). Returns (ok, err_repr)."""
        try:
            from google.cloud import storage as _gcs
            if not gs_uri.startswith("gs://"):
                return False, "not a gs:// uri: %s" % gs_uri
            bkt, _, key = gs_uri[5:].partition("/")
            _gcs.Client().bucket(bkt).blob(key).upload_from_filename(local_path)
            return True, ""
        except Exception as e:  # noqa: BLE001
            return False, repr(e)

    # GCS WINS when both are set, so no existing lane's behaviour can change by adding the S3 option.
    _cache_root = os.environ.get("RBFE_SETUP_CACHE_GCS") or _S3_CACHE
    _cache_ver = os.environ.get("SETUP_CACHE_VERSION", "v1")
    _charge = os.environ.get("CHARGE_METHOD", "am1bcc")
    cache_dir = ("%s/%s__%s__%s" % (_cache_root.rstrip("/"), tag, _charge, _cache_ver)) if _cache_root else None
    loc = Path(ckpt) / ("setupcache_%s" % tag)
    setup_outputs = None

    if cache_dir and _obj_exists(cache_dir + "/manifest.json"):
        try:
            loc.mkdir(parents=True, exist_ok=True)
            for meta in ("manifest.json", "objs.pkl"):
                _obj_download(cache_dir + "/" + meta, loc / meta)
            manifest = _json.loads((loc / "manifest.json").read_text())
            objs = _pickle.loads((loc / "objs.pkl").read_bytes())
            setup_outputs = {}
            for k, mv in manifest.items():
                if mv[0] == "file":
                    _obj_download(cache_dir + "/" + mv[1], loc / mv[1])
                    setup_outputs[k] = loc / mv[1]   # pathlib.Path — openfe deserialize() calls .parent (not a str)
                else:
                    setup_outputs[k] = objs[k]
            print("  [spot-safe] SETUP RESTORED from cache %s — skipped the ~460s solvate+parameterize "
                  "(the window that kept dying to spot preemption)" % cache_dir, flush=True)
        except Exception as e:  # noqa: BLE001
            print("  [spot-safe] setup-cache restore failed (%s); rebuilding from scratch" % e, flush=True)
            setup_outputs = None

    if setup_outputs is None:
        # ENFORCE THE CPU-PRIME -> GPU PROCESS. A cache-configured REAL run must NOT solvate+parameterize the
        # 146k-atom hybrid system on the (idle) GPU — that ~8-40 min of GPU-idle re-parameterization is the exact
        # anti-pattern ternary-setup-prime-cpu.yml exists to eliminate. If the setup cache is MISSING for this
        # (leg, charge), FAIL FAST and point at the CPU pre-bake instead of silently building on the GPU.
        # Exemptions: the CPU pre-bake itself (RBFE_PRIME_ONLY=1) must build; a lane with no cache configured
        # (cache_dir is None — smoke runs, the binary-RBFE lane) never triggers this; and an explicit
        # RBFE_REQUIRE_PRIMED_SETUP=0 allows an intentional GPU build (e.g. the very first prime of a new leg).
        _prime_only = os.environ.get("RBFE_PRIME_ONLY") == "1"
        if cache_dir and not _prime_only and os.environ.get("RBFE_REQUIRE_PRIMED_SETUP", "1") != "0":
            raise SystemExit(
                "[spot-safe] SETUP CACHE MISSING at %s — refusing to solvate+parameterize on the (idle) GPU. "
                "Pre-bake it on CPU FIRST: dispatch ternary-setup-prime-cpu.yml with charge_method=%s (free, "
                "non-preemptible; it writes THIS exact cache), then re-dispatch the GPU run so it restores the "
                "cache and goes straight to MD. This enforces the CPU-prime->GPU process; a cold cache otherwise "
                "burns ~8-40 min of GPU time. Override with RBFE_REQUIRE_PRIMED_SETUP=0 only for a deliberate "
                "GPU-side build (the very first prime of a brand-new leg/charge)." % (cache_dir, _charge)
            )
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
                # RETRY each upload — a transient GcsApiError('') on the big hybrid_system.xml.bz2 previously
                # aborted the whole save (manifest.json uploads LAST, so a mid-list failure left NO manifest and
                # the leg saw the cache as MISSING -> fail-fast). manifest.json is still written last, so it only
                # appears once every object is safely uploaded (an all-or-nothing cache).
                for f in upload + ["objs.pkl", "manifest.json"]:
                    _last = None
                    # S3 BRANCH (only when this lane is S3-backed). Kept OUT of the retry ladder below,
                    # whose 8 rounds and 403-abort exist for a specific set of GCS pathologies (a
                    # parallel-composite upload failing as GcsApiError(''), a prefix-scoped permission
                    # denial) that have no S3 analogue. boto3 does its own retries; ordering is preserved,
                    # so manifest.json is still written last and the cache stays all-or-nothing.
                    if cache_dir.startswith("s3://"):
                        b_, k_ = _s3_split(cache_dir + "/" + f)
                        _s3_client().upload_file(str(loc / f), b_, k_)
                        continue
                    for _attempt in range(8):
                        # PRIMARY: python GCS client (plain upload, avoids the gcloud parallel-composite path that
                        # fails opaquely with GcsApiError('') on the large hybrid_system.xml.bz2). FALLBACK: gcloud
                        # CLI cp with a fixed content-type. Longer exponential backoff covers a transient 429/503.
                        ok, _perr = _gcs_upload(str(loc / f), cache_dir + "/" + f)
                        if ok:
                            break
                        r = _gsh("cp", "--content-type=application/octet-stream", str(loc / f), cache_dir + "/" + f)
                        if r.returncode == 0:
                            break
                        _last = "pyclient=%s | gcloud=%s" % (_perr, (r.stderr or ""))
                        # A 403 IS NOT TRANSIENT — DO NOT BURN 8 BACKOFF ROUNDS ON IT. `gcloud storage cp`
                        # reports a permission denial as GcsApiError('') with an EMPTY message, which is why
                        # this failure has been labelled "a transient GcsApiError" and retried. It is not
                        # transient: on 2026-07-25 both a fresh fwd build and the rev build died here after 8
                        # retries and ~2 min of pointless backoff, and only the python client's error carried
                        # the truth — 403, gpu-runner@ lacks storage.objects.create on the setupcache/ prefix
                        # (it CAN write stagecache/, so the grant is prefix-limited; every setup cache that
                        # exists was written by a GPU VM under the compute SA, not by the CPU primer).
                        # Fail immediately with the real reason so the next reader is not misdirected.
                        if "403" in _perr or "storage.objects.create" in _perr or "Forbidden" in _perr:
                            print("  [spot-safe] cache upload %s: PERMISSION DENIED (403), not transient — "
                                  "aborting retries. The uploading identity lacks storage.objects.create on "
                                  "this prefix; retrying cannot fix it. Either grant it, or build the setup on "
                                  "the VM (allow_gpu_setup_build=1), whose SA can write. Full: %s"
                                  % (f, _perr), flush=True)
                            raise RuntimeError("cp %s: PERMISSION DENIED (403) — %s" % (f, _perr[-300:]))
                        print("  [spot-safe] cache upload %s attempt %d failed (%s); retrying"
                              % (f, _attempt + 1, _last[-240:]), flush=True)
                        time.sleep(min(60, 5 * (2 ** _attempt)))
                    else:
                        print("  [spot-safe] cache upload %s FULL error:\n%s" % (f, _last), flush=True)
                        raise RuntimeError("cp %s after 8 retries: %s" % (f, _last[-200:]))
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
    _constrain_diag = None
    if os.environ.get("RBFE_CONSTRAIN_LIGAND_CH") == "1":
        try:
            _n0 = system.getNumConstraints()
            _added, _constrain_diag = constrain_nonalchemical_xh(system)
            print("  [constrain-lig] RBFE_CONSTRAIN_LIGAND_CH=1 -> added %d non-alchemical X-H constraints "
                  "(%d -> %d total); enables a larger stable timestep. MUST be on for ALL legs."
                  % (_added, _n0, system.getNumConstraints()), flush=True)
        except Exception as _ce:  # noqa: BLE001
            import traceback as _tb
            _constrain_diag = {"error": "%s: %s" % (type(_ce).__name__, _ce), "tb": _tb.format_exc()[-400:]}
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
            # FORCE CENSUS (2026-07-24). `xh_total == 0` is AMBIGUOUS on its own: it means either (i) every X-H
            # is a CONSTRAINT (so 4 fs is genuinely safe), or (ii) the alchemical valence bonds live in a
            # CustomBondForce this counter's filter did not recognise, and were skipped. The filter keeps a
            # CustomBondForce only when its per-bond parameter names contain 'length' and lack
            # chargeprod/sigma/epsilon — a naming assumption that silently becomes wrong if OpenFE renames its
            # hybrid parameters (r1/K1, length_old/length_new, ...). Both anchors of the timestep scan reported
            # xh_total=0, which trips its known-answer gate, so the census below records the ACTUAL force
            # inventory to tell (i) from (ii) instead of assuming.
            _census = []
            for _f in system.getForces():
                _row = {"class": type(_f).__name__}
                for _attr, _key in (("getNumBonds", "n_bonds"), ("getNumParticles", "n_particles"),
                                    ("getNumAngles", "n_angles")):
                    if hasattr(_f, _attr):
                        try:
                            _row[_key] = int(getattr(_f, _attr)())
                        except Exception:  # noqa: BLE001
                            pass
                if hasattr(_f, "getPerBondParameterName"):
                    try:
                        _row["per_bond_params"] = [_f.getPerBondParameterName(_p)
                                                   for _p in range(_f.getNumPerBondParameters())]
                        _row["counted_as_valence"] = bool(
                            "length" in " ".join(_row["per_bond_params"]).lower()
                            and not any(_t in " ".join(_row["per_bond_params"]).lower()
                                        for _t in ("chargeprod", "sigma", "epsilon")))
                    except Exception:  # noqa: BLE001
                        pass
                _census.append(_row)
            print("  [hmr-diag] FORCE CENSUS: %s" % json.dumps(_census), flush=True)
            # The EDGE-DISCRIMINATING count (see count_morphing_xh): X-H bonds whose existence or geometry
            # changes between the alchemical endpoints. Unlike xh_unconstrained this is a property of the
            # PERTURBATION, not of the global constraint setting — but it is only visible when the ligand X-H
            # have not been constrained away, i.e. on the system production actually builds.
            try:
                _n_morph, _morph = count_morphing_xh(system)
            except Exception as _me:  # noqa: BLE001
                _n_morph, _morph = None, [{"error": "%s: %s" % (type(_me).__name__, _me)}]
            print("  [hmr-diag] MORPHING X-H (edge-discriminating) = %s | %s"
                  % (_n_morph, json.dumps(_morph[:6])), flush=True)
            # ★★ THE SETUP-NaN PROBE (2026-07-27, RBFE_ENERGY_PROBE=1). Step 1 fan-out unit
            # `e_zaienne_cmpd19__cw_bio_primary_amide__neutral__neutral` lost its complex leg to
            # `Particle coordinate is NaN` raised by LocalEnergyMinimizer inside `sampler.setup()`,
            # i.e. before any MD. Deciding whether to BLOCK that unit or RETRY it turns entirely on
            # whether the fault is in the STAGED SYSTEM (deterministic — every host reproduces it) or
            # incidental to the machine, and the only way that had been available to find out was to
            # rent another host and watch. The system is built here on a FREE CPU runner, and this is
            # the same `system`/`positions` pair handed to `drv.run_spot_safe` below, so a per-force
            # single-point energy answers it for $0 and independently of any GPU.
            _eprobe = None
            if os.environ.get("RBFE_ENERGY_PROBE") == "1":
                try:
                    import rbfe_spot_driver as _drv
                    _plog = lambda _m: print("  " + str(_m), flush=True)  # noqa: E731
                    _eprobe_rows = _drv._force_energy_probe(system, positions, _plog, "hmrdiag")
                    _drv._clash_report(positions, system, _plog, "hmrdiag")
                    _etot = sum(r["energy_kj_mol"] for r in _eprobe_rows) if _eprobe_rows else 0.0
                    _grad_before = dict(_drv.LAST_GRADIENT_PROBE)
                    _eprobe = {"rows": _eprobe_rows, "gradient_probe": _grad_before,
                               "verdict": _drv.energy_probe_verdict(_eprobe_rows, _etot, _grad_before)}
                    # ★★ THE CONTROLLED AFTER, IN THE SAME $0 RUN (2026-07-28). A diagnosis that names a
                    # cause and a remedy is still a hypothesis until the remedy is shown to remove the
                    # cause — and here that costs one extra force evaluation, on CPU, with no host. The
                    # de-degenerated coordinates are re-probed and BOTH readings are recorded, so the claim
                    # "the coincident pair carries the 1e17 gradient" is a before/after and not an argument.
                    # ⚠ This does NOT prove the GPU leg now completes. It proves the singular force is gone;
                    # the leg completing is a separate, later observation and must not be reported early.
                    if _grad_before.get("n_coincident_pairs"):
                        _fixed_pos, _ded = _drv._dedegenerate_positions(positions, _plog, "hmrdiag-after")
                        _drv._force_energy_probe(system, _fixed_pos, _plog, "hmrdiag-after")
                        _eprobe["dedegenerate"] = _ded
                        _eprobe["gradient_probe_after"] = dict(_drv.LAST_GRADIENT_PROBE)
                except Exception as _pe:  # noqa: BLE001 — an evidence hook must never break the build
                    _eprobe = {"error": "%s: %s" % (type(_pe).__name__, _pe)}
                print("  [hmr-diag] ENERGY PROBE: %s"
                      % (_eprobe.get("verdict") or _eprobe.get("error")), flush=True)
            print("  [hmr-diag] RBFE_HMRDIAG_ONLY=1 -> exiting after the constraint verdict (no MD).", flush=True)
            return None, None, {"hmrdiag_only": True, "xh_total": _xh_total,
                                "xh_unconstrained": _xh_unconstrained, "unconstrained": _unc, "hmasses": _hmasses,
                                "total_constraints": _tot_cons, "constraints_setting": str(_cons_set),
                                "hydrogen_mass_setting": str(_hmass_set), "constrain_diag": _constrain_diag,
                                "force_census": _census, "n_morphing_xh": _n_morph, "morphing_xh": _morph,
                                "n_particles": (int(system.getNumParticles()) if system is not None else None),
                                "energy_probe": _eprobe}
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
        # VERIFY the cache actually persisted (manifest.json is uploaded LAST, so its presence means the whole
        # cache is complete). A silent 'setup-cache save failed ... non-fatal' would otherwise let the prime
        # falsely report primed=true while the GPU leg fail-fasts on the missing cache. Fail the prime instead.
        if _gsh("ls", cache_dir + "/manifest.json").returncode != 0:
            raise SystemExit("[spot-safe] PRIME_ONLY: cache did NOT persist (no manifest.json at %s) — the "
                             "upload failed (see 'setup-cache save failed' above). Failing the prime so it is "
                             "visible. If the cause was a 403 the re-run will fail identically — a permission denial is NOT transient; build the setup on the VM (allow_gpu_setup_build=1) or grant the uploader storage.objects.create on this prefix." % cache_dir)
        print("  [spot-safe] PRIME_ONLY: setup built + cached to %s (manifest verified in GCS); exiting before MD "
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
    # ⚠ THIRD RETURN VALUE IS A DICT, NOT A LIST — AND THAT IS THE FIX FOR AN UNANSWERABLE IDENTITY CHECK.
    # `nr4a3_ternary_fep` writes the leg record with
    #     _n_particles = _ana_keys.get("n_particles") if isinstance(_ana_keys, dict) else None
    # and this function used to `return dg, unc, list(ana_outputs)`. A list is not a dict, so `n_particles`
    # and `setup_cache_dir` were None on EVERY leg that actually ran MD — only the PRIME branch (which
    # returns a dict and exits before MD) ever populated them. Downstream,
    # `ternary_fep_reduce._system_identity_consistency` reported the field UNRECORDED across the whole cycle
    # and correctly refused to call that agreement, which is exactly what happened to the RUNG 2b 4 fs cycle
    # on 2026-07-26: three legs sharing one protocol_hash, and no system identity recorded at all. The
    # particle count was sitting in `system` the whole time, one line away.
    # The analysis output keys are kept under `ana_output_keys` so nothing that wanted them has lost them.
    try:
        _npart = int(system.getNumParticles())
    except Exception:  # noqa: BLE001
        _npart = None
    return dg, unc, {"ana_output_keys": list(ana_outputs), "n_particles": _npart,
                     "cache_dir": cache_dir, "primed": False}


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
