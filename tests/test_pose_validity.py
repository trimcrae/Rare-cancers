#!/usr/bin/env python3
"""Unit tests for bound-pose strain / conformational-accessibility (nr4a3_pose_validity.py).

Requires RDKit. If RDKit is absent the tests skip (the module is only meaningful with it).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "research", "modalities"))

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    import nr4a3_pose_validity as pv
    HAVE_RDKIT = True
except Exception:  # noqa: BLE001
    HAVE_RDKIT = False


def test_conformational_accessibility_shape():
    if not HAVE_RDKIT:
        print("skip: no rdkit"); return
    r = pv.conformational_accessibility(pv.LEAD["smiles"], n_confs=25)
    assert r["rotatable_bonds"] >= 1
    assert r["n_conformers_scored"] > 0
    assert 0.0 <= r["frac_within_3kcal"] <= 1.0


def test_minimized_conformer_has_low_strain():
    if not HAVE_RDKIT:
        print("skip: no rdkit"); return
    # An MMFF-minimized conformer should sit near its own global min -> small strain, no flag, valid geometry.
    m = Chem.AddHs(Chem.MolFromSmiles(pv.LEAD["smiles"]))
    p = AllChem.ETKDGv3(); p.randomSeed = 0xC0FFEE
    AllChem.EmbedMultipleConfs(m, numConfs=30, params=p)
    AllChem.MMFFOptimizeMoleculeConfs(m, mmffVariant="MMFF94s")
    # pick the lowest-energy optimized conformer as the "bound" pose stand-in
    props = AllChem.MMFFGetMoleculeProperties(m, mmffVariant="MMFF94s")
    energies = [(AllChem.MMFFGetMoleculeForceField(m, props, confId=c).CalcEnergy(), c)
                for c in range(m.GetNumConformers())]
    _, best = min(energies)
    one = Chem.Mol(m); one.RemoveAllConformers(); one.AddConformer(m.GetConformer(best), assignId=True)
    r = pv.strain_from_mol(one)
    assert "strain_kcalmol" in r, r
    assert r["strain_kcalmol"] < pv.STRAIN_FLAG_TOTAL          # a min conformer is not strained
    assert r["strain_flag"] is False
    assert r["validity"]["pass"] is True


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print("ok:", name)
    print("all pose-validity tests passed")
