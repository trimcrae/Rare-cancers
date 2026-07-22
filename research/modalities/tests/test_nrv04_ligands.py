#!/usr/bin/env python3
"""Tests for the frozen NR-V04 ligand definitions + electrophile detection. Needs rdkit."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("rdkit")

from rdkit import Chem  # noqa: E402
from rdkit.Chem import rdMolDescriptors  # noqa: E402

from nrv04_ligands import LIGANDS, electrophile_atom_index  # noqa: E402


def test_all_ligands_parse():
    for name, smi in LIGANDS.items():
        assert Chem.MolFromSmiles(smi) is not None, name


def test_celastrol_identity():
    m = Chem.MolFromSmiles(LIGANDS["celastrol"])
    assert rdMolDescriptors.CalcMolFormula(m) == "C29H38O4"        # literature celastrol, MW 450.6


def test_active_and_epimer_are_stereoisomers():
    a = Chem.MolFromSmiles(LIGANDS["nrv04"])
    e = Chem.MolFromSmiles(LIGANDS["nrv04_epimer"])
    assert rdMolDescriptors.CalcMolFormula(a) == rdMolDescriptors.CalcMolFormula(e)   # same formula
    assert LIGANDS["nrv04"] != LIGANDS["nrv04_epimer"]                                # differ only in stereo
    # the difference is a single Hyp stereocentre: N4C[C@H](O) (active) vs N4C[C@@H](O) (epimer)
    assert "N4C[C@H](O)" in LIGANDS["nrv04"] and "N4C[C@@H](O)" in LIGANDS["nrv04_epimer"]


def test_electrophile_is_ring_fused_sp2_carbon_and_deterministic():
    for name in LIGANDS:
        m = Chem.MolFromSmiles(LIGANDS[name])
        beta, neigh = electrophile_atom_index(m)
        a = m.GetAtomWithIdx(beta)
        assert a.GetSymbol() == "C" and a.IsInRing()
        assert m.GetRingInfo().NumAtomRings(beta) >= 2              # extended quinone-methide ring-fusion terminus
        assert neigh is not None and neigh != beta
    # the shared celastrol warhead -> same relative electrophile site in all three
    idxs = {electrophile_atom_index(Chem.MolFromSmiles(LIGANDS[n]))[0] for n in LIGANDS}
    assert len(idxs) == 1                                           # deterministic + consistent across ligands
