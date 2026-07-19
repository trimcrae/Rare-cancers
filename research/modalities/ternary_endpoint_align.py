#!/usr/bin/env python3
"""Endpoint core-transplant + programmatic verification for the ternary RBFE (reviewer condition 1, 2026-07-19).

THE PROBLEM the reviewer flagged: the pre-equilibration relaxes the PHYSICAL complex with ligand A only, then
ligand B was placed by a whole-molecule O3A overlay. An O3A overlay does NOT force B's MAPPED (common-core)
atoms onto A's relaxed coordinates, so the RBFE's hybrid setup emits "mapped atom moved by X Å" warnings and the
two endpoints do not share one relaxed conformer — exactly what must be fixed before any fan-out.

THE FIX (pure RDKit, no OpenFE/OpenMM so it is unit-testable off-GPU): given the SAME atom map the FEP will use
(A_index -> B_index), TRANSPLANT A's relaxed coordinate onto every mapped B atom, then relax ONLY the unmapped
(alchemical dummy) B atoms with the mapped core held FIXED. Result: both endpoints share one relaxed core
conformer, mapped-atom displacement is exactly zero, and the few dummy atoms sit at sane local geometry.

VERIFICATION (verify_endpoints) checks, programmatically, everything the reviewer named:
  - mapped-atom displacement (must be ~0 -> eliminates the OpenFE warnings),
  - connectivity / bond orders / formal charges / stereo TAGS preserved on B (graph unchanged by the move),
  - 3D chirality not inverted at any stereocenter by the transplant,
  - net formal charge of A equals that of B (a valid alchemical morph conserves net charge),
  - dummy-atom bond lengths sane and NO atom-atom clashes (<0.5 Å) — the hybrid/dummy geometry check.

The heavy module (ternary_preequil.py) obtains the map from rbfe._mapping (LOMAP element_change, the map the FEP
re-derives) and calls transplant_and_verify; mcs_mapping() is a pure-RDKit fallback used only for tests / when
OpenFE is unavailable."""
from __future__ import annotations

CLASH_MIN_ANG = 0.5          # any two atoms closer than this = a clash / superposition
DUMMY_BOND_LO, DUMMY_BOND_HI = 0.8, 2.0   # sane covalent bond length window (Å) for a placed dummy atom
MAPPED_DISP_TOL_ANG = 1e-3   # mapped atoms are SET to A's coords (+ fixed during relax) -> displacement ~0


def _conf_xyz(mol, i):
    p = mol.GetConformer().GetAtomPosition(i)
    return (p.x, p.y, p.z)


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def mcs_mapping(molA, molB):
    """Pure-RDKit fallback A->B atom map (rdFMCS, ring-aware, element changes allowed) as {iA: iB}. Used for
    unit tests and if OpenFE's LOMAP is unavailable; production prefers rbfe._mapping so the transplant map is
    IDENTICAL to the one the FEP re-derives."""
    from rdkit import Chem
    from rdkit.Chem import rdFMCS
    res = rdFMCS.FindMCS([molA, molB], completeRingsOnly=True, ringMatchesRingOnly=True,
                         atomCompare=rdFMCS.AtomCompare.CompareAny, bondCompare=rdFMCS.BondCompare.CompareOrderExact,
                         timeout=30)
    patt = Chem.MolFromSmarts(res.smartsString)
    mA = molA.GetSubstructMatch(patt)
    mB = molB.GetSubstructMatch(patt)
    return dict(zip(mA, mB))


def core_transplant(molA_relaxed, molB, a2b, relax_dummies=True):
    """Return a copy of molB whose MAPPED atoms are placed EXACTLY on molA_relaxed's coordinates, and whose
    unmapped (dummy) atoms are relaxed into local geometry with the mapped core held fixed. molA_relaxed and
    molB must each already carry one conformer; a2b maps molA_relaxed atom idx -> molB atom idx."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    molB_out = Chem.Mol(molB)
    confA = molA_relaxed.GetConformer()
    confB = molB_out.GetConformer()
    mapped_B = set()
    for iA, iB in a2b.items():
        p = confA.GetAtomPosition(iA)
        confB.SetAtomPosition(iB, p)
        mapped_B.add(iB)
    unmapped_B = [i for i in range(molB_out.GetNumAtoms()) if i not in mapped_B]

    if unmapped_B and relax_dummies:
        # Re-seed any dummy that ended up far from its nearest mapped bonded neighbor, so MMFF starts sane.
        for i in unmapped_B:
            nbrs = [n.GetIdx() for n in molB_out.GetAtomWithIdx(i).GetNeighbors() if n.GetIdx() in mapped_B]
            if nbrs:
                near = _conf_xyz(molB_out, nbrs[0])
                if _dist(_conf_xyz(molB_out, i), near) > 2.5:
                    confB.SetAtomPosition(i, (near[0] + 1.0, near[1], near[2]))
        # MMFF (fallback UFF) minimize with every mapped atom pinned -> only dummies move; core stays transplanted.
        ff = None
        try:
            props = AllChem.MMFFGetMoleculeProperties(molB_out)
            if props is not None:
                ff = AllChem.MMFFGetMoleculeForceField(molB_out, props)
        except Exception:  # noqa: BLE001
            ff = None
        if ff is None:
            try:
                ff = AllChem.UFFGetMoleculeForceField(molB_out)
            except Exception:  # noqa: BLE001
                ff = None
        if ff is not None:
            for i in mapped_B:
                ff.AddFixedPoint(i)
            try:
                ff.Minimize(maxIts=500)
            except Exception:  # noqa: BLE001
                pass
    return molB_out


def _chiral_signs(mol):
    """Signed tetrahedral volume at each chiral center -> {idx: +/-1}; catches a 3D inversion by the transplant."""
    from rdkit import Chem
    centers = Chem.FindMolChiralCenters(mol, useLegacyImplementation=False, includeUnassigned=False)
    conf = mol.GetConformer()
    out = {}
    for idx, _ in centers:
        nbrs = [n.GetIdx() for n in mol.GetAtomWithIdx(idx).GetNeighbors()]
        if len(nbrs) < 3:
            continue
        pts = [conf.GetAtomPosition(n) for n in nbrs[:3]]
        c = conf.GetAtomPosition(idx)
        v = [(pt.x - c.x, pt.y - c.y, pt.z - c.z) for pt in pts]
        det = (v[0][0] * (v[1][1] * v[2][2] - v[1][2] * v[2][1])
               - v[0][1] * (v[1][0] * v[2][2] - v[1][2] * v[2][0])
               + v[0][2] * (v[1][0] * v[2][1] - v[1][1] * v[2][0]))
        out[idx] = 1 if det >= 0 else -1
    return out


def verify_endpoints(molA_relaxed, molB_in, molB_out, a2b):
    """Programmatic endpoint checks (reviewer condition 1). Returns a dict of metrics + an overall `ok` bool that
    is True only when EVERY critical check passes. Raises nothing — the caller decides to fail-loud on `ok`."""
    from rdkit import Chem

    confA = molA_relaxed.GetConformer()

    # 1. mapped-atom displacement (must be ~0): B's mapped atoms sit exactly on A's relaxed coords.
    disp = [_dist(_conf_xyz(molB_out, iB), (confA.GetAtomPosition(iA).x, confA.GetAtomPosition(iA).y,
            confA.GetAtomPosition(iA).z)) for iA, iB in a2b.items()]
    max_disp = max(disp) if disp else 0.0

    # 2. connectivity / bond orders / formal charges / stereo TAGS unchanged on B (moving coords must not touch
    #    the graph). Canonical isomeric SMILES compares connectivity + bond orders + charges + stereo tags at once.
    smi_in = Chem.MolToSmiles(molB_in)
    smi_out = Chem.MolToSmiles(molB_out)
    graph_identical = smi_in == smi_out

    # 3. 3D chirality not inverted by the transplant
    signs_in, signs_out = _chiral_signs(molB_in), _chiral_signs(molB_out)
    common = set(signs_in) & set(signs_out)
    chirality_ok = all(signs_in[i] == signs_out[i] for i in common)

    # 4. net formal charge conserved A vs B (a valid alchemical morph conserves net charge)
    qA, qB = Chem.GetFormalCharge(molA_relaxed), Chem.GetFormalCharge(molB_out)
    net_charge_conserved = qA == qB

    # 5. dummy-atom geometry sane + NO clashes anywhere (hybrid/dummy geometry check)
    mapped_B = set(a2b.values())
    unmapped_B = [i for i in range(molB_out.GetNumAtoms()) if i not in mapped_B]
    dummy_bond_ok = True
    for i in unmapped_B:
        for n in molB_out.GetAtomWithIdx(i).GetNeighbors():
            d = _dist(_conf_xyz(molB_out, i), _conf_xyz(molB_out, n.GetIdx()))
            if not (DUMMY_BOND_LO <= d <= DUMMY_BOND_HI):
                dummy_bond_ok = False
    # min pairwise distance across ALL atoms (clash guard)
    n = molB_out.GetNumAtoms()
    min_pair = float("inf")
    xyz = [_conf_xyz(molB_out, i) for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = _dist(xyz[i], xyz[j])
            if d < min_pair:
                min_pair = d
    no_clash = min_pair >= CLASH_MIN_ANG

    checks = {
        "mapped_max_displacement_ang": max_disp,
        "mapped_displacement_ok": max_disp <= MAPPED_DISP_TOL_ANG,
        "graph_identical": graph_identical,
        "chirality_not_inverted": chirality_ok,
        "net_charge_A": qA, "net_charge_B": qB, "net_charge_conserved": net_charge_conserved,
        "n_mapped": len(a2b), "n_dummy_B": len(unmapped_B),
        "dummy_bond_lengths_ok": dummy_bond_ok,
        "min_pair_distance_ang": None if min_pair == float("inf") else round(min_pair, 3),
        "no_clash": no_clash,
        "smiles_in": smi_in, "smiles_out": smi_out,
    }
    checks["ok"] = bool(checks["mapped_displacement_ok"] and graph_identical and chirality_ok
                        and net_charge_conserved and dummy_bond_ok and no_clash)
    return checks


def transplant_and_verify(molA_relaxed, molB, a2b):
    """Convenience: transplant then verify. Returns (molB_out, checks). Caller fails loud if not checks['ok']."""
    molB_out = core_transplant(molA_relaxed, molB, a2b)
    checks = verify_endpoints(molA_relaxed, molB, molB_out, a2b)
    return molB_out, checks
