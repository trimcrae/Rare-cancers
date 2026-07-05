import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import nr4a3_fep as fep  # noqa: E402


def _write(path, lines):
    open(path, "w").writelines(lines)


def test_clean_drops_h_hetatm_altloc_and_adds_ter():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "raw.pdb")
    _write(p, [
        "ATOM      1  N   ALA A   1      0.000   0.000   0.000  1.00  0.00           N\n",
        "ATOM      2  CA  ALA A   1      1.000   0.000   0.000  1.00  0.00           C\n",
        "ATOM      3  H   ALA A   1      0.500   0.500   0.000  1.00  0.00           H\n",  # element-H
        "ATOM      4 1HB  ALA A   1      0.500  -0.500   0.000  1.00  0.00            \n",  # name-only H
        "ATOM      5  CA BALA A   1      1.100   0.100   0.000  0.50  0.00           C\n",  # altloc B -> drop
        "HETATM    6  O   HOH A 200      9.000   9.000   9.000  1.00  0.00           O\n",  # water -> drop
        "ATOM      7  CA  GLY B   2      5.000   0.000   0.000  1.00  0.00           C\n",  # new chain -> TER
    ])
    out = fep._clean_pdb_for_leap(p, d)
    got = open(out).readlines()
    atoms = [l for l in got if l.startswith("ATOM")]
    # kept: N, CA(chain A), CA(chain B) = 3 heavy protein atoms; H/1HB/HETATM/altloc-B dropped
    assert len(atoms) == 3, atoms
    assert not any(" H " in l or "1HB" in l for l in atoms), "hydrogens not stripped"
    assert not any("HOH" in l for l in got), "heteroatoms not dropped"
    assert any(l.startswith("TER") for l in got), "no TER emitted"
    # altloc indicator (col 17) blanked on kept atoms
    assert all(l[16] == " " for l in atoms), "altloc indicator not blanked"


def test_clean_ter_between_chains_and_at_end():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "raw.pdb")
    _write(p, [
        "ATOM      1  CA  ALA A   1      0.000   0.000   0.000  1.00  0.00           C\n",
        "ATOM      2  CA  GLY B   2      5.000   0.000   0.000  1.00  0.00           C\n",
    ])
    out = fep._clean_pdb_for_leap(p, d)
    got = open(out).readlines()
    # one TER between the two chains, one TER at the very end
    assert sum(1 for l in got if l.startswith("TER")) == 2, got


def test_clean_empty_returns_input():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "raw.pdb")
    _write(p, ["HETATM    1  O   HOH A 200      9.0   9.0   9.0  1.00  0.00           O\n"])
    out = fep._clean_pdb_for_leap(p, d)     # nothing protein -> fall back to the input path (never silently empty)
    assert out == p
