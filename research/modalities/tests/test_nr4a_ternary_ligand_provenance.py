#!/usr/bin/env python3
"""Guards for recovering the co-folded PROTAC. It must refuse rather than emit a guessed molecule."""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import nr4a_ternary_ligand_provenance as P   # noqa: E402


def test_no_bond_loop_is_a_refusal_not_a_perceived_molecule(tmp_path):
    p = tmp_path / "m.cif"
    p.write_text("data_x\n_entry.id x\n")
    bonds, why = P.cif_ligand_bonds(str(p), "LIG")
    assert bonds is None
    assert "would have to be perceived" in why
    assert "paid run" in why


def test_bond_orders_are_read_from_the_models_own_loop(tmp_path):
    p = tmp_path / "m.cif"
    p.write_text(
        "data_x\n"
        "loop_\n"
        "_chem_comp_bond.comp_id\n"
        "_chem_comp_bond.atom_id_1\n"
        "_chem_comp_bond.atom_id_2\n"
        "_chem_comp_bond.value_order\n"
        "LIG C1 C2 SING\n"
        "LIG C2 C3 DOUB\n"
        "OTH X1 X2 SING\n"
        "#\n")
    bonds, why = P.cif_ligand_bonds(str(p), "LIG")
    assert why is None
    assert bonds == {("C1", "C2"): "SING", ("C2", "C3"): "DOUB"}, "the other component must not leak in"


def test_disagreeing_arms_emit_no_smiles_for_a_paid_run(monkeypatch):
    seen = iter([("CCO", {}), ("CCC", {}), ("CCO", {})])
    monkeypatch.setattr(P, "ligand_smiles_from_model", lambda p: next(seen))
    doc = P.recover({"NR4A3": "a.cif", "NR4A1": "b.cif", "NR4A2": "c.cif"})
    assert doc["agree"] is False
    assert "protac_smiles" not in doc
    assert "unsafe" in doc["sentence"]


def test_agreement_across_all_arms_is_what_licenses_the_smiles(monkeypatch):
    monkeypatch.setattr(P, "ligand_smiles_from_model", lambda p: ("CCO", {"component": "LIG"}))
    doc = P.recover({"NR4A3": "a.cif", "NR4A1": "b.cif", "NR4A2": "c.cif"})
    assert doc["agree"] is True and doc["protac_smiles"] == "CCO"
    assert "same degrader" in doc["sentence"]


def test_a_partial_recovery_is_not_agreement(monkeypatch):
    seen = iter([("CCO", {}), (None, {"error": "no loop"}), ("CCO", {})])
    monkeypatch.setattr(P, "ligand_smiles_from_model", lambda p: next(seen))
    doc = P.recover({"NR4A3": "a.cif", "NR4A1": "b.cif", "NR4A2": "c.cif"})
    assert doc["agree"] is False and "protac_smiles" not in doc


def test_nothing_recovered_says_the_molecule_is_unrecorded(monkeypatch):
    monkeypatch.setattr(P, "ligand_smiles_from_model", lambda p: (None, {"error": "x"}))
    doc = P.recover({"NR4A3": "a.cif"})
    assert doc["agree"] is None and "UNRECORDED" in doc["sentence"]


def test_the_provenance_gap_is_named_in_the_module():
    src = open(os.path.join(MOD, "nr4a_ternary_ligand_provenance.py")).read()
    assert "the repo does not record which molecule that was" in src
    assert "PROTAC_SMILES" in src
