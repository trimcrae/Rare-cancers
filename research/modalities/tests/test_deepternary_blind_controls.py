"""Tests for the fabrication-risk-free pure logic of the DeepTernary Step-3 leakage audit.

The network paths (RCSB search/data API) run only in CI; here we test the exclusion-set parser and the
PDB-ID recogniser, which are what gate a valid blind-control selection (no candidate may be in the
exclusion set). No network.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import deepternary_blind_controls as m  # noqa: E402


def _tree():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "data/PROTAC"))
    with open(os.path.join(d, "data/PROTAC/protac22.txt"), "w") as f:
        f.write("5T35_H_E_759\n6HR2_B_A_FWZ\n7KHH_C_D_WEP\n")
    os.makedirs(os.path.join(d, "TernaryDB"))
    with open(os.path.join(d, "TernaryDB/train.txt"), "w") as f:
        f.write("6boy 6bn7 1abc\n")
    with open(os.path.join(d, "TernaryDB/meta.json"), "w") as f:
        f.write('{"pdb":"6HAX","junk":"zzzz"}\n')
    return d


def test_pdbid_regex_accepts_valid():
    assert m.PDBID_RE.fullmatch("5T35")
    assert m.PDBID_RE.fullmatch("1ABC")
    assert m.PDBID_RE.fullmatch("6boy".upper())


def test_pdbid_regex_rejects_invalid():
    # PDB IDs start with a digit 1-9 and are exactly 4 chars
    assert not m.PDBID_RE.fullmatch("ABCD")   # starts with a letter
    assert not m.PDBID_RE.fullmatch("0XYZ")   # starts with 0
    assert not m.PDBID_RE.fullmatch("TAF15")  # 5 chars
    assert not m.PDBID_RE.fullmatch("5T3")    # 3 chars


def test_exclusion_set_extracts_from_protac_style_and_lists():
    res = m.build_exclusion_set(_tree())
    for pid in ("5T35", "6HR2", "7KHH", "6BOY", "6BN7", "6HAX", "1ABC"):
        assert pid in res["ids"], (pid, res["ids"])
    # a 4-letter prose token that is NOT a PDB ID must not leak in
    assert "ZZZZ" not in res["ids"]


def test_exclusion_set_provenance_records_source_file():
    res = m.build_exclusion_set(_tree())
    assert res["provenance"]["5T35"] == ["data/PROTAC/protac22.txt"]
    assert res["provenance"]["6BOY"] == ["TernaryDB/train.txt"]
    # every id has at least one provenance file
    assert all(res["provenance"][pid] for pid in res["ids"])


def test_known_e3_map_has_the_matrix_ligases():
    # the E3 interface classifier must cover VHL + CRBN (our matrix's two E3s) with correct accessions
    assert m.E3_INTERFACE_UNIPROT["P40337"] == "VHL"
    assert m.E3_INTERFACE_UNIPROT["Q96SW2"] == "CRBN"
