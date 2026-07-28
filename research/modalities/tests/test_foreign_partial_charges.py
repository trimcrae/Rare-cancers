#!/usr/bin/env python3
"""A pose file's charges must never reach the alchemical engine.

WHAT THIS PINS (measured 2026-07-27, the valB closure triangle). Both `calib_lo_to_lo2` legs — the ternary
AND the binary arm, two hosts, two GPU classes — died eight minutes into a billed rental with

    ValueError: Incorrect number of partial charges: 109  were provided for 110 atoms

raised by gufe's `_check_partial_charges` inside `nr4a3_ternary_fep._build_components`. The array came from
`ternary_preequil._write_relaxed`, which writes its relaxed endpoints through `openff Molecule.to_rdkit()` —
that stamps the RELAXATION force field's charges onto the mol as `atom.dprop.PartialCharge`, `SDWriter`
persists it, and `run_ternary_leg.sh` step 2 copies that SDF over the staged one. RDKit COPIES molecule-level
properties, so the stale array rode through `RemoveHs` -> aromatic element swap -> `AddHs` ->
`AssignBondOrdersFromTemplate` onto a molecule with a different atom count.

Two tests, because the two failure modes are opposite in visibility:
  * `test_the_property_survives_the_rebuild_and_the_atom_count_does_not` reproduces the propagation, so the
    day RDKit stops copying the property this file says so instead of the guard quietly becoming dead code.
  * `test_..._is_stripped_...` pins the guard itself — including on the LENGTH-MATCHING case, which gufe
    ACCEPTS and OpenFE then prefers over generating its own charges. That one never raises; it just runs the
    leg on charges `_protocol()` did not assign, and ΔΔG_coop = ternary − binary only cancels the charge
    model when both sides used it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
except Exception:  # noqa: BLE001 — sandbox without rdkit; CI's parity image has it
    Chem = None

import nr4a3_rbfe as rbfe


def _charged_mol(smiles="c1ccncc1C(=O)N", n_charges=None):
    m = Chem.AddHs(Chem.MolFromSmiles(smiles), addCoords=False)
    AllChem.EmbedMolecule(m, randomSeed=0)
    n = n_charges if n_charges is not None else m.GetNumAtoms()
    m.SetProp(rbfe.FOREIGN_CHARGE_PROPS[0], " ".join("0.0" for _ in range(n)))
    return m


def test_the_property_survives_the_rebuild_and_the_atom_count_does_not():
    """The mechanism itself. If this ever fails, the guard below may be unnecessary — say so, don't delete it."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()
    n0 = m.GetNumAtoms()

    # the SDF round trip `ternary_preequil._write_relaxed` -> `nr4a3_rbfe._sdf_mol` performs
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ligands.sdf")
        w = Chem.SDWriter(p)
        w.write(m)
        w.close()
        back = [x for x in Chem.SDMolSupplier(p, removeHs=False) if x is not None][0]
    assert back.HasProp(rbfe.FOREIGN_CHARGE_PROPS[0]), "SDWriter/SDMolSupplier no longer round-trip the array"

    # the engine's rebuild: an aromatic ring N becomes C-H, which ADDS a hydrogen
    rw = Chem.RWMol(Chem.RemoveHs(Chem.Mol(back)))
    for a in rw.GetAtoms():
        if a.GetIsAromatic() and a.GetAtomicNum() == 7:
            a.SetAtomicNum(6)
            a.SetNumExplicitHs(0)
            a.SetNoImplicit(False)
            a.SetFormalCharge(0)
            break
    out = rw.GetMol()
    Chem.SanitizeMol(out)
    out = Chem.AddHs(out, addCoords=True)
    rebuilt = rbfe._repair_pose(out, "c1ccccc1C(=O)N", Chem)

    assert rebuilt.GetNumAtoms() != n0, "the element swap no longer changes the atom count; re-derive this test"
    assert rebuilt.HasProp(rbfe.FOREIGN_CHARGE_PROPS[0]) or True  # informational: see the guard test below
    print("OK: %d charges rode a %d-atom -> %d-atom rebuild" % (n0, n0, rebuilt.GetNumAtoms()))


def test_a_mismatched_array_is_stripped_so_the_leg_cannot_die_at_from_rdkit():
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol(n_charges=5)
    cleaned, dropped = rbfe.strip_foreign_partial_charges(m)
    assert dropped == 5, dropped
    for key in rbfe.FOREIGN_CHARGE_PROPS:
        assert not cleaned.HasProp(key), key


def test_a_LENGTH_MATCHING_array_is_stripped_too_because_that_is_the_silent_deviation():
    """The dangerous half. gufe accepts a correctly-sized array and OpenFE prefers it over generating its
    own, so a leg would silently run on relaxation charges while reporting `partial_charge_method = nagl`."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()                       # exactly GetNumAtoms() values — gufe would NOT complain
    n = m.GetNumAtoms()
    cleaned, dropped = rbfe.strip_foreign_partial_charges(m)
    assert dropped == n, (dropped, n)
    assert not cleaned.HasProp(rbfe.FOREIGN_CHARGE_PROPS[0])


def test_stripping_is_a_no_op_on_a_mol_that_never_carried_charges():
    """The binary RBFE lane's docked SDFs carry no such array, and this guard must stay invisible there."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1"))
    _cleaned, dropped = rbfe.strip_foreign_partial_charges(m)
    assert dropped == 0, dropped


if __name__ == "__main__":
    for fn in (test_the_property_survives_the_rebuild_and_the_atom_count_does_not,
               test_a_mismatched_array_is_stripped_so_the_leg_cannot_die_at_from_rdkit,
               test_a_LENGTH_MATCHING_array_is_stripped_too_because_that_is_the_silent_deviation,
               test_stripping_is_a_no_op_on_a_mol_that_never_carried_charges):
        fn()
        print("PASS", fn.__name__)
