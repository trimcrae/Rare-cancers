"""Unit tests for `pose_convergence_401` — the denovo_401 pose-agreement readout.

The load-bearing assertions here are not the arithmetic; they are the two ways this measurement could
silently lie:
  · using a primitive that RE-ALIGNS the ligands, which would report ~0 for two poses in different pockets;
  · dropping an unreadable pose source instead of recording it, which turns "which files survived an S3
    lifecycle rule" into "how well the methods agree".
Both are pinned below.
"""
import math
import os

import pytest

import pose_convergence_401 as P


# ------------------------------------------------------------------ the RMSD primitive must not align

def test_calcrms_does_not_realign_and_getbestrms_would():
    """★ THE WHOLE MEASUREMENT RESTS ON THIS. A translated copy is 10 A away and must read as 10 A."""
    Chem = pytest.importorskip("rdkit.Chem")
    rdMolAlign = pytest.importorskip("rdkit.Chem.rdMolAlign")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    m = Chem.AddHs(Chem.MolFromSmiles("CCOc1ccccc1"))
    assert AllChem.EmbedMolecule(m, randomSeed=11) == 0
    m = Chem.RemoveHs(m)
    moved = P.transformed_copy(m, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], (10.0, 0.0, 0.0))
    rms, why = P.symmetry_rmsd(moved, m)
    assert why is None
    assert abs(rms - 10.0) < 1e-6, "CalcRMS must measure placement, not shape"
    # the wrong primitive, kept as a live demonstration rather than a comment
    assert rdMolAlign.GetBestRMS(Chem.Mol(moved), m) < 1e-3


def test_internal_conformer_rmsd_is_blind_to_placement():
    Chem = pytest.importorskip("rdkit.Chem")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    m = Chem.AddHs(Chem.MolFromSmiles("CCOc1ccccc1"))
    AllChem.EmbedMolecule(m, randomSeed=11)
    m = Chem.RemoveHs(m)
    moved = P.transformed_copy(m, [[1, 0, 0], [0, 1, 0], [0, 0, 1]], (10.0, 0.0, 0.0))
    val, why = P.internal_conformer_rmsd(m, moved)
    assert why is None and val < 1e-3, "a pure translation is zero internal difference"


# ------------------------------------------------------------------ receptor parsing

_PDB = """\
REMARK   1 test
ATOM      1  N   MET A 373      0.000   0.000   0.000  1.00  0.00           N
ATOM      2  CA  MET A 373      1.000   0.000   0.000  1.00  0.00           C
ATOM      3  HA  MET A 373      1.100   0.100   0.000  1.00  0.00           H
ATOM      4  CA  LYS A 374      2.000   0.000   0.000  1.00  0.00           C
ATOM      5  CA  LEU B 999      9.000   0.000   0.000  1.00  0.00           C
HETATM    6  O   HOH A 500      5.000   5.000   5.000  1.00  0.00           O
ENDMDL
ATOM      7  CA  ALA A 375      3.000   0.000   0.000  1.00  0.00           C
"""


def test_parse_receptor_first_chain_no_hydrogens_first_model(tmp_path):
    p = tmp_path / "r.pdb"
    p.write_text(_PDB)
    res, order = P.parse_receptor(str(p))
    assert order == [373, 374], "chain B, HETATM and everything past ENDMDL are excluded"
    assert len(res[373]["heavy"]) == 2, "the hydrogen is dropped"
    assert res[373]["ca"] == (1.0, 0.0, 0.0)


def test_to_uniprot_renumbered_from_373_is_identity_for_these_receptors(tmp_path):
    """The MD receptors are trimmed from the LBD start, so resSeq n <-> UniProt 372+n. Not typed here:
    it comes out of `residue_map.resolve_positions`, the repo's one home for that convention."""
    p = tmp_path / "r.pdb"
    p.write_text(_PDB)
    res, order = P.parse_receptor(str(p))
    mapped, how = P.to_uniprot(res, order, "renumbered-from-373")
    assert mapped is not None and how
    assert sorted(mapped) == [373, 374]


def test_unknown_numbering_scheme_is_a_refusal_not_a_guess():
    mapped, why = P.to_uniprot({1: {"ca": (0, 0, 0), "heavy": [], "resname": "ALA"}}, [1], "invented")
    assert mapped is None and "unknown numbering" in why


# ------------------------------------------------------------------ refusals are recorded, never dropped

def test_missing_source_becomes_a_refusal_with_its_path():
    src = {"id": "x", "kind": "k", "receptor": "/nonexistent/r.pdb", "poses": "/nonexistent/p.sdf",
           "numbering": "renumbered-from-373", "provenance": "test"}
    rec, refusal = P.load_source(src)
    assert rec is None
    assert refusal["stage"] == "receptor"
    assert refusal["path"] == "/nonexistent/r.pdb"
    assert "False" in refusal["evidence"]


def test_fewer_than_two_readable_sources_is_INSUFFICIENT_not_a_number():
    """A convergence figure computed over one pose would be a fabricated agreement."""
    doc = P.measure([{"id": "x", "kind": "k", "receptor": "/nope.pdb", "poses": "/nope.sdf",
                      "numbering": "renumbered-from-373", "provenance": "test"}])
    assert doc["_status"].startswith("INSUFFICIENT")
    assert doc["verdict"]["convergence_measurable"] is False
    assert len(doc["refusals"]) == 1


def test_every_known_source_is_listed_even_when_unreadable():
    """The census is the point: 6 sources are known, and the artifact must name all 6 whatever is on disk."""
    ids = [s["id"] for s in P.SOURCES]
    assert len(ids) == len(set(ids))
    assert any("8XTT" in i for i in ids), "the experimental-geometry legs must be in the census"
    assert P.KNOWN_ABSENT, "sources the program does NOT hold are named, so the census is not mistaken " \
                           "for exhaustive"


# ------------------------------------------------------------------ small pure helpers

def test_spread_reports_a_distribution_not_a_representative_value():
    s = P.spread([3.0, 1.0, 2.0, None])
    assert s == {"n": 3, "min": 1.0, "median": 2.0, "max": 3.0, "mean": 2.0}
    assert P.spread([])["n"] == 0


def test_jaccard():
    assert P.jaccard({1, 2, 3}, {2, 3, 4}) == 0.5
    assert P.jaccard(set(), set()) is None


def test_contacts_uses_the_pipelines_own_cutoff():
    assert P.contact_a() == 4.0, "the pipeline's contact distance, read from nr4a3_warhead.handle_contacts"
    residues = {10: {"resname": "ALA", "ca": (0, 0, 0), "heavy": [(0.0, 0.0, 0.0)]},
                11: {"resname": "GLY", "ca": (99, 0, 0), "heavy": [(99.0, 0.0, 0.0)]}}
    assert P.contacts([(1.0, 0.0, 0.0)], residues, 4.0) == {10}


def test_decompose_does_not_classify_it_reports_numbers():
    """A 2-3 A centroid separation is genuinely ambiguous; a label asserting 'different sub-site' would be
    interpretation the measurement cannot support."""
    s = P._decompose(7.0, 1.1, 2.36, 0.6)
    assert "7.00 A apart" in s and "2.36 A apart" in s and "60% of contacted residues shared" in s
    assert "dominated by PLACEMENT" in s
    assert P._decompose(1.2, 0.4, 0.3, 0.9).startswith("agree")


def test_bands_are_the_fields_numbers_and_are_not_a_gate():
    assert P.SAME_POSE_A == 2.0 and P.SAME_SITE_A == 4.0


# ------------------------------------------------------------------ the real, committed comparison

@pytest.mark.committed_artifact
def test_the_two_committed_metad_poses_are_readable_and_the_receptors_differ():
    """Both in-git sources must load, and they must be DIFFERENT receptors — two docks into the same file
    would make the whole comparison vacuous and would look like perfect agreement."""
    pytest.importorskip("rdkit")
    a, ra = P.load_source(P.SOURCES[0])
    b, rb = P.load_source(P.SOURCES[1])
    if a is None or b is None:
        pytest.skip("committed pose files not present in this checkout: %s %s" % (ra, rb))
    assert a["smiles"] == b["smiles"], "the two sources must hold the same molecule"
    assert a["receptor"] != b["receptor"]
    doc = P.measure([P.SOURCES[0], P.SOURCES[1]])
    assert doc["_status"] == "ok"
    pair = doc["pairs"][0]
    assert pair["pocket"]["ligand_rmsd_A"] is not None
    assert pair["pocket"]["n_fit_used"] >= 3
    # the receptors' POCKETS superpose well — so any ligand disagreement is the ligand, not the fit
    assert pair["pocket"]["receptor_fit_rmsd_A"] < 2.0
    assert doc["verdict"]["n_pairs_cross_method"] == 0, \
        "these two are the same METHOD on different conformers; if that ever changes, the verdict text " \
        "that says so must change with it"


def test_scale_reference_calibrates_the_spread_without_inventing_a_band():
    Chem = pytest.importorskip("rdkit.Chem")
    AllChem = pytest.importorskip("rdkit.Chem.AllChem")
    m = Chem.AddHs(Chem.MolFromSmiles("CCCCCCCCc1ccccc1"))
    assert AllChem.EmbedMolecule(m, randomSeed=5) == 0
    AllChem.MMFFOptimizeMolecule(m)
    m = Chem.RemoveHs(m)
    ref = P.scale_reference(m, n_random=40)
    assert ref["length_A"] > 0
    assert 0.3 * ref["length_A"] < ref["flip_rmsd_A"] < 1.2 * ref["length_A"]
    assert ref["random_reorient_mean_A"] < ref["flip_rmsd_A"] * 1.2
    assert "is a threshold" in ref["_note"]      # "none of these is a threshold"


if __name__ == "__main__":
    raise SystemExit(pytest.main([os.path.abspath(__file__), "-q"]))
