#!/usr/bin/env python3
"""Tests for the NR-V04 covalent panel staging (C551A mutation + covalent-restraint pair). Pure stdlib."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_covalent_stage import find_covalent_pair, mutate_cys_to_ala  # noqa: E402

_PDB = "\n".join([
    "ATOM      1  N   CYS A 551      10.000  10.000  10.000  1.00  0.00           N",
    "ATOM      2  CA  CYS A 551      11.000  10.000  10.000  1.00  0.00           C",
    "ATOM      3  C   CYS A 551      12.000  10.000  10.000  1.00  0.00           C",
    "ATOM      4  O   CYS A 551      13.000  10.000  10.000  1.00  0.00           O",
    "ATOM      5  CB  CYS A 551      11.000  11.000  10.000  1.00  0.00           C",
    "ATOM      6  SG  CYS A 551      11.000  12.500  10.000  1.00  0.00           S",
    "ATOM      7  HG  CYS A 551      11.500  13.000  10.000  1.00  0.00           H",
    "HETATM    8  C6  LIG X   1      11.000  14.300  10.000  1.00  0.00           C",
    "ATOM      9  N   ALA A 552      14.000  10.000  10.000  1.00  0.00           N",
])


def test_c551a_truncates_to_alanine():
    mut = mutate_cys_to_ala(_PDB, "A", 551)
    res = [l for l in mut.splitlines() if l[21] == "A" and l[22:26].strip() == "551"]
    assert res and all(l[17:20] == "ALA" for l in res)                 # renamed CYS -> ALA
    assert sorted(l[12:16].strip() for l in res) == ["C", "CA", "CB", "N", "O"]  # SG + H dropped
    # the rest of the structure is untouched
    assert "C6  LIG" in mut and "N   ALA A 552" in mut


def test_c551a_refuses_non_cys_and_missing():
    for bad in [("A", 552), ("A", 999)]:
        try:
            mutate_cys_to_ala(_PDB, *bad)
            assert False, bad
        except ValueError:
            pass


def test_covalent_pair_locates_sg_and_ligand_carbon():
    pair = find_covalent_pair(_PDB, "A", 551, "LIG", "C6")
    assert pair["cys_sg"]["serial"] == 6 and pair["lig_c"]["serial"] == 8
    assert abs(pair["start_distance_A"] - 1.8) < 0.01                  # SG->C6 geometry
    assert pair["target_bond_A"] == 1.81


def test_covalent_pair_missing_atom_raises():
    for args in [("A", 551, "LIG", "C99"), ("A", 551, "NOPE", "C6")]:
        try:
            find_covalent_pair(_PDB, *args)
            assert False, args
        except ValueError:
            pass
