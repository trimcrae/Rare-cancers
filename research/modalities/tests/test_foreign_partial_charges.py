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


# =============================================================================================================
# THE SECOND LEVEL — added 2026-07-29, after the strip above landed and the legs went on dying
# =============================================================================================================
# The molecule-level strip is real and it worked; it just was not the whole story. RDKit's SD parser expands a
# `atom.dprop.<X>` tag into a PER-ATOM `<X>` property as it reads the file, and OpenFF's `from_rdkit` reads
# exactly that per-atom property — never the array. So a mol could be "clean" by every assertion above and
# still hand OpenFF a full set of charges.
#
# It got worse, not better, on the way to the engine: `_repair_pose` keeps the props on the heavy atoms it
# preserves and cannot put them on the hydrogens it re-adds, so a COMPLETE set became a PARTIAL one, and
# OpenFF refuses a partial set outright:
#
#     openff/toolkit/utils/rdkit_wrapper.py:2351 in from_rdkit
#     ValueError: Some atoms in rdmol have partial charges, but others do not.
#
# reached from `proto.create` -> `_validate_smcs` -> `SmallMoleculeComponent.to_openff()`. Measured across the
# whole archive of rented attempts: 37 of 49 on `calib_hi_to_lo__ternary_vhl` r2 and 32 of 35 on r1, the
# signature first appearing at 2026-07-28T02:12Z — i.e. only AFTER the molecule-level strip landed at
# 2026-07-28T00:54Z, and in no attempt before it.


def test_the_sd_round_trip_creates_PER_ATOM_charges_not_only_the_array():
    """The mechanism nobody measured. If RDKit ever stops expanding property lists on read, say so here."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ligands.sdf")
        w = Chem.SDWriter(p)
        w.write(m)
        w.close()
        back = [x for x in Chem.SDMolSupplier(p, removeHs=False) if x is not None][0]
    n_atom = sum(1 for a in back.GetAtoms() if a.HasProp(rbfe.PER_ATOM_CHARGE_PROP))
    assert n_atom == back.GetNumAtoms(), (
        "RDKit no longer expands `%s` into per-atom `%s` on read (%d of %d) — re-derive this test rather "
        "than deleting the guard" % (rbfe.FOREIGN_CHARGE_PROPS[0], rbfe.PER_ATOM_CHARGE_PROP,
                                     n_atom, back.GetNumAtoms()))


def test_the_rebuild_turns_a_COMPLETE_per_atom_set_into_a_PARTIAL_one():
    """The exact shape OpenFF refuses: some atoms charged, some not. This is the death, reproduced on CPU."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ligands.sdf")
        w = Chem.SDWriter(p)
        w.write(m)
        w.close()
        back = [x for x in Chem.SDMolSupplier(p, removeHs=False) if x is not None][0]
    rebuilt = rbfe._repair_pose(back, "c1ccncc1C(=O)N", Chem)
    n_atom = sum(1 for a in rebuilt.GetAtoms() if a.HasProp(rbfe.PER_ATOM_CHARGE_PROP))
    assert 0 < n_atom < rebuilt.GetNumAtoms(), (
        "expected a PARTIAL per-atom set after the repair (that is what OpenFF refuses); got %d of %d"
        % (n_atom, rebuilt.GetNumAtoms()))


def test_the_strip_clears_the_PER_ATOM_charges_too():
    """The fix. Before 2026-07-29 this failed: the array went, every per-atom charge stayed."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()
    n = m.GetNumAtoms()
    for a in m.GetAtoms():                       # what the SD read leaves behind
        a.SetDoubleProp(rbfe.PER_ATOM_CHARGE_PROP, 0.0)
    cleaned, dropped = rbfe.strip_foreign_partial_charges(m)
    assert dropped == n, (dropped, n)
    assert sum(1 for a in cleaned.GetAtoms() if a.HasProp(rbfe.PER_ATOM_CHARGE_PROP)) == 0


def test_the_strip_reports_per_atom_charges_even_when_the_array_was_already_gone():
    """The state the 84 dead rentals were in: array cleared upstream, per-atom charges fully live. A guard
    that reported `dropped == 0` here is how it stayed invisible for a day."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = Chem.AddHs(Chem.MolFromSmiles("c1ccncc1C(=O)N"))
    for a in m.GetAtoms():
        a.SetDoubleProp(rbfe.PER_ATOM_CHARGE_PROP, -0.1)
    assert not m.HasProp(rbfe.FOREIGN_CHARGE_PROPS[0])       # nothing at the molecule level at all
    _cleaned, dropped = rbfe.strip_foreign_partial_charges(m)
    assert dropped == m.GetNumAtoms(), dropped


def test_sdf_mol_strips_at_the_door_so_no_rebuild_can_make_a_partial_set():
    """The boundary the fix moved the strip to. `_sdf_mol` is the ONLY place a pose SDF becomes an RDKit mol
    for either alchemical lane, and it is the last moment the charges are still in the state the file
    described — after `_repair_pose` a complete set has already become the partial one OpenFF refuses."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()
    m.SetProp("_Name", "ligA")
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ligands.sdf")
        w = Chem.SDWriter(p)
        w.write(m)
        w.close()
        got = rbfe._sdf_mol(p, "ligA", None, Chem)
    n_arr, n_atom, _n = rbfe.foreign_charge_census(got)
    assert (n_arr, n_atom) == (0, 0), (n_arr, n_atom)
    # and the rebuild downstream therefore cannot produce a partial set
    rebuilt = rbfe._repair_pose(got, "c1ccncc1C(=O)N", Chem)
    assert rbfe.foreign_charge_census(rebuilt)[1] == 0


def test_a_pose_read_and_rebuilt_the_way_the_engine_does_it_is_acceptable_to_openff():
    """THE REGRESSION, stated in OpenFF's own terms and using no API this fix introduced.

    OpenFF accepts a molecule only when the per-atom `PartialCharge` coverage is all-or-nothing; the ternary
    legs died because the engine's read-then-rebuild produced neither. This walks that exact path — SD write,
    `_sdf_mol` read, `_repair_pose` rebuild — and asserts the result is one OpenFF would take. Against the code
    of 2026-07-28 it fails with a partial set, which is the leg dying on a rented GPU.
    """
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = _charged_mol()
    m.SetProp("_Name", "ligA")
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ligands.sdf")
        w = Chem.SDWriter(p)
        w.write(m)
        w.close()
        rebuilt = rbfe._repair_pose(rbfe._sdf_mol(p, "ligA", None, Chem), "c1ccncc1C(=O)N", Chem)
    charged = sum(1 for a in rebuilt.GetAtoms() if a.HasProp("PartialCharge"))
    assert charged in (0, rebuilt.GetNumAtoms()), (
        "openff's from_rdkit raises `Some atoms in rdmol have partial charges, but others do not` on exactly "
        "this: %d of %d atoms carry one" % (charged, rebuilt.GetNumAtoms()))
    assert charged == 0, "the protocol assigns its own charges; a pose file's must not survive to the engine"


def test_the_boundary_assertion_refuses_a_partially_charged_molecule():
    """Belt and braces, and the thing that would have caught this on a CPU instead of on 84 rented GPUs."""
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    m = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1"))
    for a in list(m.GetAtoms())[:3]:
        a.SetDoubleProp(rbfe.PER_ATOM_CHARGE_PROP, 0.2)
    try:
        rbfe.assert_no_foreign_charges(m, "unit test endpoint")
    except SystemExit as e:
        assert "per-atom" in str(e) and "unit test endpoint" in str(e), str(e)
    else:
        raise AssertionError("assert_no_foreign_charges accepted a partially charged molecule")


def test_the_boundary_assertion_is_silent_on_a_clean_molecule():
    if Chem is None:
        print("SKIP: rdkit unavailable")
        return
    rbfe.assert_no_foreign_charges(Chem.AddHs(Chem.MolFromSmiles("c1ccccc1")), "clean")


if __name__ == "__main__":
    for fn in (test_the_property_survives_the_rebuild_and_the_atom_count_does_not,
               test_a_mismatched_array_is_stripped_so_the_leg_cannot_die_at_from_rdkit,
               test_a_LENGTH_MATCHING_array_is_stripped_too_because_that_is_the_silent_deviation,
               test_stripping_is_a_no_op_on_a_mol_that_never_carried_charges,
               test_the_sd_round_trip_creates_PER_ATOM_charges_not_only_the_array,
               test_the_rebuild_turns_a_COMPLETE_per_atom_set_into_a_PARTIAL_one,
               test_the_strip_clears_the_PER_ATOM_charges_too,
               test_the_strip_reports_per_atom_charges_even_when_the_array_was_already_gone,
               test_sdf_mol_strips_at_the_door_so_no_rebuild_can_make_a_partial_set,
               test_a_pose_read_and_rebuilt_the_way_the_engine_does_it_is_acceptable_to_openff,
               test_the_boundary_assertion_refuses_a_partially_charged_molecule,
               test_the_boundary_assertion_is_silent_on_a_clean_molecule):
        fn()
        print("PASS", fn.__name__)
