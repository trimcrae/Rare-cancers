#!/usr/bin/env python3
"""Tests for the NR-V04 co-fold ligand-pose extractor (template-transfer kernel). Needs rdkit."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("rdkit")

from rdkit import Chem  # noqa: E402
from rdkit.Chem import AllChem, rdMolDescriptors  # noqa: E402

from nrv04_covalent_assemble import ligand_mol_from_coords  # noqa: E402
from nrv04_ligands import LIGANDS  # noqa: E402


def _coords_from_smiles(smi):
    m = Chem.AddHs(Chem.MolFromSmiles(smi))
    AllChem.EmbedMolecule(m, AllChem.ETKDGv3())
    m = Chem.RemoveHs(m)
    conf = m.GetConformer()
    els = [a.GetSymbol() for a in m.GetAtoms()]
    xyz = [tuple(conf.GetAtomPosition(i)) for i in range(m.GetNumAtoms())]
    return els, xyz


@pytest.mark.parametrize("name", list(LIGANDS))
def test_template_transfer_recovers_chemistry_from_coords(name):
    smi = LIGANDS[name]
    els, xyz = _coords_from_smiles(smi)
    posed = ligand_mol_from_coords(els, xyz, smi)
    # exact heavy-atom formula recovered from coordinates alone (bond orders from the template)
    assert rdMolDescriptors.CalcMolFormula(Chem.RemoveHs(posed)) == \
        rdMolDescriptors.CalcMolFormula(Chem.RemoveHs(Chem.MolFromSmiles(smi)))
    # coordinates are preserved on the matched atoms (a heavy atom sits at an input coordinate)
    posed_pts = {(round(p.x, 3), round(p.y, 3), round(p.z, 3))
                 for p in (posed.GetConformer().GetAtomPosition(i) for i in range(posed.GetNumAtoms()))}
    assert (round(xyz[0][0], 3), round(xyz[0][1], 3), round(xyz[0][2], 3)) in posed_pts


def test_atom_count_mismatch_raises():
    els, xyz = _coords_from_smiles(LIGANDS["celastrol"])
    with pytest.raises(ValueError):
        ligand_mol_from_coords(els[:-1], xyz[:-1], LIGANDS["celastrol"])   # drop an atom -> template mismatch
