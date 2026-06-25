"""Unit tests for fpocket_lib — the parsing/mapping that the off-by-one bug lived in.

The headline test is `test_mapping_follows_data_not_filename`: it encodes the exact failure mode
(residue-file index disagreeing with the info.txt pocket number) and asserts the mapping follows the
alpha-sphere data, not the filename integer. That test fails on both the original (+0) and the interim
(+1) index assumptions, and passes only for a data-derived mapping.
"""
import pytest

import fpocket_lib as fl

# --- minimal fpocket-format fixtures -----------------------------------------------------------

INFO = """\
Pocket 1 :
\tScore : \t0.300
\tDruggability Score : \t0.495
\tNumber of Alpha Spheres : \t31
Pocket 2 :
\tScore : \t0.100
\tDruggability Score : \t0.026
\tNumber of Alpha Spheres : \t16
Pocket 3 :
\tScore : \t0.050
\tDruggability Score : \t0.016
\tNumber of Alpha Spheres : \t16
"""

# pocket{N}_atm.pdb bodies keyed by FILE INDEX (deliberately not matching pocket numbers below).
ATM = {
    4: "ATOM      1  CA  LEU A 463      0.000   0.000   0.000  1.00  0.00           C\n"
       "ATOM      2  CA  ARG A 547      1.000   1.000   1.000  1.00  0.00           C\n",
    5: "ATOM      1  CA  LEU A 406      0.000   0.000   0.000  1.00  0.00           C\n"
       "ATOM      2  CA  THR A 534      1.000   1.000   1.000  1.00  0.00           C\n",
    6: "ATOM      1  CA  ALA A 449      0.000   0.000   0.000  1.00  0.00           C\n",
}


def test_parse_info():
    info = fl.parse_info(INFO)
    assert info[1] == {"druggability": 0.495, "alpha_spheres": 31}
    assert info[2] == {"druggability": 0.026, "alpha_spheres": 16}
    assert info[3]["druggability"] == 0.016


def test_parse_atm_residues():
    assert fl.parse_atm_residues(ATM[5]) == [406, 534]
    assert fl.parse_atm_residues("garbage\nATOM x") == []


def test_mapping_follows_data_not_filename():
    """File index 5 holds the 16-sphere pocket; info.txt's 16-sphere pocket is Pocket 2 (NOT 6 via
    a +1 assumption, NOT 5 via a +0 assumption). With unique counts the map is by count alone."""
    info = fl.parse_info(INFO)
    # make counts unique so this case needs no coordinates: pocket 3 -> 17 spheres
    info[3]["alpha_spheres"] = 17
    file_counts = {4: 31, 5: 16, 6: 17}
    mapping = fl.map_files_to_pockets(info, file_counts)
    assert mapping == {4: 1, 5: 2, 6: 3}
    # the residues of file 5 (406,534) therefore belong to Pocket 2 (druggability 0.026) — the
    # corrected attribution, the opposite of the original off-by-one.
    assert info[mapping[5]]["druggability"] == 0.026


def test_tie_on_count_disambiguated_by_coordinates():
    """Pockets 2 and 3 both have 16 spheres; resolve by matching vert.pqr coords to out.pdb STP."""
    info = fl.parse_info(INFO)  # pockets 2 and 3 both 16 spheres
    file_counts = {4: 31, 5: 16, 6: 16}
    # out.pdb: pocket 2's sphere at (10,10,10); pocket 3's at (20,20,20); pocket 1 at (0,0,0)
    out_pdb = (
        "HETATM    1 APOL STP   1       0.000   0.000   0.000\n"
        "HETATM    2 APOL STP   2      10.000  10.000  10.000\n"
        "HETATM    3 APOL STP   3      20.000  20.000  20.000\n"
    )
    out_coords = fl.out_pdb_sphere_coords(out_pdb)
    file_coords = {
        4: frozenset({(0.0, 0.0, 0.0)}),
        5: frozenset({(10.0, 10.0, 10.0)}),   # -> pocket 2
        6: frozenset({(20.0, 20.0, 20.0)}),   # -> pocket 3
    }
    mapping = fl.map_files_to_pockets(info, file_counts, file_coords, out_coords)
    assert mapping == {4: 1, 5: 2, 6: 3}


def test_tie_without_coords_raises():
    info = fl.parse_info(INFO)  # pockets 2,3 tie at 16
    with pytest.raises(ValueError, match="coordinate data required"):
        fl.map_files_to_pockets(info, {4: 31, 5: 16, 6: 16})


def test_count_mismatch_raises():
    info = fl.parse_info(INFO)
    with pytest.raises(ValueError, match="pocket-count mismatch"):
        fl.map_files_to_pockets(info, {4: 31, 5: 16})  # only 2 files vs 3 pockets


def test_unmatched_count_raises():
    info = fl.parse_info(INFO)
    info[3]["alpha_spheres"] = 99
    with pytest.raises(ValueError, match="matches no unused pocket"):
        fl.map_files_to_pockets(info, {4: 31, 5: 16, 6: 12})  # 12 matches nothing


def test_pqr_sphere_coords_tolerates_chain_column():
    pqr = (
        "ATOM      1  C   STP 1       1.234   5.678   9.012  0.0  1.5\n"
        "ATOM      2  C   STP A 1     1.234   5.678   9.012  0.0  1.5\n"  # optional chain col
    )
    assert fl.pqr_sphere_coords(pqr) == frozenset({(1.23, 5.68, 9.01)})


def test_count_pqr_spheres_is_raw_lines_not_deduped_coords():
    """The mapping must use the TRUE alpha-sphere count (raw lines), not len(coords): two spheres that
    round to the same xyz dedupe in the coord set and would undercount → spurious mapping failure
    (the bug the regeneration caught)."""
    pqr = (
        "ATOM      1  C   STP 1       1.111   2.222   3.333  0.0  1.5\n"
        "ATOM      2  C   STP 1       1.111   2.222   3.333  0.0  1.5\n"   # same rounded coord
        "ATOM      3  C   STP 1       9.000   9.000   9.000  0.0  1.5\n"
    )
    assert fl.count_pqr_spheres(pqr) == 3                 # raw count — matches info.txt
    assert len(fl.pqr_sphere_coords(pqr)) == 2            # deduped — would undercount
    # mapping must succeed using the raw count
    info = {1: {"alpha_spheres": 3}}
    assert fl.map_files_to_pockets(info, {7: fl.count_pqr_spheres(pqr)}) == {7: 1}


def test_select_druggable_lbd_pocket():
    pockets = [
        {"druggability": 0.495, "residues": [463, 547, 622]},   # in LBD, most druggable
        {"druggability": 0.026, "residues": [406, 534]},        # in LBD, less druggable
        {"druggability": 0.9, "residues": [100, 110]},          # NOT in LBD -> ignored
    ]
    chosen = fl.select_druggable_lbd_pocket(pockets, 373, 626)
    assert chosen["druggability"] == 0.495
    assert fl.select_druggable_lbd_pocket(
        [{"druggability": 0.9, "residues": [10, 20]}], 373, 626) is None
