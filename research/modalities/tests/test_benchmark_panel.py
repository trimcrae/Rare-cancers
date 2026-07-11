"""Validate the Gate-2 published-chemistry benchmark panel (published-chemistry-benchmark-panel.json):
structure integrity always; RDKit SMILES/InChIKey verification when RDKit is present (skipped otherwise so
the pure-logic test suite still runs without the chem stack)."""
import json
import os

import pytest

PANEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "published-chemistry-benchmark-panel.json")


def _panel():
    with open(PANEL) as f:
        return json.load(f)


def test_panel_structure_wellformed():
    p = _panel()
    assert p["ligands"], "panel must have ligands"
    seen = set()
    for lig in p["ligands"]:
        for k in ("label", "smiles", "inchikey", "known_preference", "evidence"):
            assert lig.get(k), f"{lig.get('label')} missing {k}"
        assert lig["label"] not in seen, "duplicate label"
        seen.add(lig["label"])
        # the benchmark's discriminating claim: each ligand has a KNOWN paralogue preference to reproduce
        assert lig["known_preference"] in ("NR4A1", "NR4A2", "NR4A3", "pan-NR4A")


def test_panel_covers_nr4a1_discriminators():
    # the whole point of the verified-SMILES panel is THPN/TMPA (NR4A1) — the ones name-resolution gets wrong
    prefs = {l["label"]: l["known_preference"] for l in _panel()["ligands"]}
    assert any(v == "NR4A1" for v in prefs.values()), "panel must add NR4A1-leaning discriminators"


def test_panel_smiles_match_stated_inchikey():
    Chem = pytest.importorskip("rdkit.Chem")
    for lig in _panel()["ligands"]:
        m = Chem.MolFromSmiles(lig["smiles"])
        assert m is not None, f"{lig['label']} SMILES does not parse"
        ik = Chem.MolToInchiKey(m)
        assert ik.split("-")[0] == lig["inchikey"].split("-")[0], \
            f"{lig['label']} InChIKey skeleton mismatch: {ik} vs {lig['inchikey']}"
