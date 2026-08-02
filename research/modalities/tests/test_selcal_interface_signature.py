#!/usr/bin/env python3
"""Guards for the static paralogue interface signature — the MD-free known-answer test. Offline."""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

np = pytest.importorskip("numpy")

import selcal_cofold_validate as V        # noqa: E402
import selcal_interface_signature as S    # noqa: E402


def _atom(chain, resseq, resname, name, xyz, element=None, hetatm=False):
    return V.Atom(chain, resseq, "", resname, name, element or name[:1], xyz[0], xyz[1], xyz[2], hetatm)


# ---------- the proxy is labelled as one ---------------------------------------------------------------------


def test_polar_contacts_are_never_called_hydrogen_bonds():
    src = open(os.path.join(MOD, "selcal_interface_signature.py")).read()
    assert "polar_contact" in src
    assert '"hydrogen_bond"' not in src and "'hydrogen_bond'" not in src
    assert "no hydrogens" in src.lower()


def test_the_polar_ceiling_is_the_fields_number_and_is_declared():
    assert S.HBOND_MAX_A == 3.5


def test_the_contact_distance_is_imported_not_chosen():
    assert S.contact_a() == V.FNAT_CONTACT_A


# ---------- geometry ------------------------------------------------------------------------------------------


def test_residue_contacts_finds_a_polar_pair_and_ignores_a_carbon_pair():
    atoms = [
        _atom("A", 10, "GLN", "NE2", (0.0, 0.0, 0.0), element="N"),
        _atom("A", 11, "LEU", "CD1", (0.0, 6.0, 0.0), element="C"),
        _atom("B", 90, "ASP", "OD1", (2.8, 0.0, 0.0), element="O"),
        _atom("B", 91, "ALA", "CB", (2.8, 6.0, 0.0), element="C"),
    ]
    out = S.residue_contacts(atoms, "A", {"B"})
    assert "GLN10" in out and out["GLN10"]["n_polar_contacts"] == 1
    assert out["GLN10"]["polar_contacts"][0]["distance_A"] == 2.8
    assert "LEU11" in out, "a carbon-carbon contact is still an interface contact"
    assert out["LEU11"]["n_polar_contacts"] == 0, "but it is not a polar one"


def test_a_polar_pair_beyond_the_ceiling_is_a_contact_but_not_polar():
    atoms = [_atom("A", 10, "GLN", "NE2", (0.0, 0.0, 0.0), element="N"),
             _atom("B", 90, "ASP", "OD1", (4.4, 0.0, 0.0), element="O")]
    out = S.residue_contacts(atoms, "A", {"B"})
    assert out["GLN10"]["n_contacts"] == 1 and out["GLN10"]["n_polar_contacts"] == 0


def test_residues_beyond_the_contact_cutoff_are_absent_not_zero():
    atoms = [_atom("A", 10, "GLN", "NE2", (0.0, 0.0, 0.0), element="N"),
             _atom("B", 90, "ASP", "OD1", (30.0, 0.0, 0.0), element="O")]
    assert S.residue_contacts(atoms, "A", {"B"}) == {}


def test_ligand_and_water_atoms_do_not_enter_the_protein_interface():
    atoms = [_atom("A", 10, "GLN", "NE2", (0.0, 0.0, 0.0), element="N"),
             _atom("B", 900, "A1BB4", "O1", (2.8, 0.0, 0.0), element="O", hetatm=True)]
    assert S.residue_contacts(atoms, "A", {"B"}) == {}, "the degrader is not the E3's protein surface"


# ---------- the comparison ------------------------------------------------------------------------------------


def _sig(seq, keys, contacts, pdb="9XXX"):
    return {"pdb": pdb, "roles": {"target": "A", "e3": ["B"]}, "target_sequence": seq,
            "target_sequence_len": len(seq), "residue_keys": keys, "contacts": contacts,
            "contact_A": 5.0, "polar_max_A": S.HBOND_MAX_A}


def test_comparison_aligns_by_sequence_not_residue_number():
    """SMARCA2/SMARCA4 are numbered in their own full-length proteins; equal numbers are different residues."""
    seq = "ACDEFGQIKL"
    a = _sig(seq, [["A", 1400 + i, ""] for i in range(10)],
             {"GLN1406": {"resname": "GLN", "resseq": 1406, "icode": "", "min_dist_A": 2.8,
                          "n_contacts": 3, "n_polar_contacts": 1,
                          "polar_contacts": [{"target_atom": "NE2", "e3_atom": "OD1", "distance_A": 2.8}]}})
    b = _sig(seq[:6] + "L" + seq[7:], [["A", 1540 + i, ""] for i in range(10)],
             {"LEU1546": {"resname": "LEU", "resseq": 1546, "icode": "", "min_dist_A": 4.2,
                          "n_contacts": 2, "n_polar_contacts": 0, "polar_contacts": []}})
    cmp_doc = S.compare(a, b)
    assert cmp_doc["n_aligned_interface_positions"] == 1
    row = cmp_doc["rows"][0]
    assert row["aa_a"] == "Q" and row["aa_b"] == "L" and row["identical_residue"] is False
    assert row["polar_only_in_a"] is True
    assert cmp_doc["polar_only_in_a"] == ["GLN1406"]


def test_known_answer_recovered_when_a_glutamine_contacts_only_on_the_smarca2_arm():
    cmp_doc = {"rows": [{"a": "GLN1469", "b": "LEU1609", "aa_a": "Q", "aa_b": "L",
                         "polar_only_in_a": True, "polar_only_in_b": False,
                         "polar_detail_a": [{"target_atom": "NE2", "distance_A": 2.9}],
                         "polar_detail_b": []}]}
    k = S.known_answer_check(cmp_doc)
    assert k["recovered"] is True and k["n_matching_positions"] == 1
    assert "KNOWN-ANSWER RECOVERED" in k["sentence"]
    assert "does not validate E1" in k["sentence"] or "it does not validate E1" in k["sentence"]


def test_a_non_glutamine_hit_does_not_count_as_the_published_contact():
    cmp_doc = {"rows": [{"a": "LYS1400", "b": "GLU1540", "aa_a": "K", "aa_b": "E",
                         "polar_only_in_a": True, "polar_only_in_b": False,
                         "polar_detail_a": [{"target_atom": "NZ", "distance_A": 2.9}],
                         "polar_detail_b": []}]}
    k = S.known_answer_check(cmp_doc)
    assert k["recovered"] is False
    assert "NOT RECOVERED" in k["sentence"]
    assert "may NOT be used to argue selectivity" in k["sentence"]


def test_a_failed_known_answer_forbids_use_of_the_descriptor():
    k = S.known_answer_check({"rows": []})
    assert k["recovered"] is False and "including for NR4A3" in k["sentence"]


def test_the_check_does_not_depend_on_the_published_residue_number():
    """A deposit may number its construct however it likes; hinging on 1469 would fail for the wrong reason."""
    src = open(os.path.join(MOD, "selcal_interface_signature.py")).read()
    assert "does not depend on it" in src
    cmp_doc = {"rows": [{"a": "GLN7", "b": "ALA7", "aa_a": "Q", "aa_b": "A",
                         "polar_only_in_a": True, "polar_only_in_b": False,
                         "polar_detail_a": [{"distance_A": 3.0}], "polar_detail_b": []}]}
    assert S.known_answer_check(cmp_doc)["recovered"] is True


def test_an_unread_deposit_propagates_as_an_error_not_an_empty_comparison():
    cmp_doc = S.compare({"error": "9DTX not read"}, {"contacts": {}})
    assert cmp_doc.get("error")
    assert S.known_answer_check(cmp_doc)["checked"] is False


# ---------- what the module claims ----------------------------------------------------------------------------


def test_the_module_refuses_to_claim_it_validates_E1():
    src = open(os.path.join(MOD, "selcal_interface_signature.py")).read()
    assert "does **not** validate E1" in src
    assert "one contact in one pair" in src.lower()


def test_the_reference_quote_is_read_from_the_frozen_panel():
    import selcal_panel as P
    src = open(os.path.join(MOD, "selcal_interface_signature.py")).read()
    assert 'P.REFERENCE.get("pair_mechanism_quote")' in src
    assert P.REFERENCE["pair_mechanism_quote"]
