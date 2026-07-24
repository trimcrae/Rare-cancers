"""Offline unit tests for nr4a_differential_atlas (pure stdlib; no network, no big-PDB dependency)."""
import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import nr4a_differential_atlas as atlas  # noqa: E402


def test_blosum_symmetry_and_values():
    assert atlas.blosum("A", "A") == 4
    assert atlas.blosum("W", "W") == 11
    assert atlas.blosum("K", "R") == atlas.blosum("R", "K") == 2
    assert atlas.blosum("D", "V") < 0        # charge->hydrophobic is non-conservative
    assert atlas.blosum("I", "V") > 0        # conservative


def test_nw_affine_identity_and_gap():
    # identical sequences -> full 1:1 diagonal, no gaps
    aln = atlas.nw_align("ACDEFGHIK", "ACDEFGHIK")
    assert aln == [(i, i) for i in range(9)]
    # a clean single deletion in b -> exactly one (i, None) column, rest aligned
    aln2 = atlas.nw_align("ACDEFGHIK", "ACDEGHIK")   # 'F' removed from b
    gaps = [p for p in aln2 if p[1] is None]
    assert len(gaps) == 1
    # every b index is used exactly once and in order
    bs = [j for _, j in aln2 if j is not None]
    assert bs == sorted(bs) and len(set(bs)) == len(bs) == 8


def test_char_change_types():
    assert atlas.char_change("D", "V") in ("charge_lost",)
    assert atlas.char_change("A", "K") == "charge_gained"
    assert atlas.char_change("D", "K") == "charge_reversed"
    assert atlas.char_change("N", "L") == "hbond_lost"
    assert atlas.char_change("I", "V") == "steric_or_neutral"


def test_fib_sphere_count_and_unit_norm():
    pts = atlas._fib_sphere(96)
    assert len(pts) == 96
    # all points on the unit sphere
    for (x, y, z) in pts:
        assert abs(math.sqrt(x*x + y*y + z*z) - 1.0) < 1e-6


def test_shrake_rupley_isolated_atom_matches_sphere_area():
    # a single carbon: full accessible sphere area = 4*pi*(vdw+probe)^2
    atoms = [{"resid": 1, "resname": "ALA", "name": "CA", "elem": "C", "x": 0.0, "y": 0.0, "z": 0.0}]
    sasa = atlas.shrake_rupley(atoms, n_points=200)
    r = atlas.VDW["C"] + atlas.PROBE
    expected = 4.0 * math.pi * r * r
    assert abs(sasa[1] - expected) / expected < 0.02   # within 2% at 200 points


def test_shrake_rupley_buried_atom_less_than_isolated():
    # two carbons 1 A apart in DIFFERENT residues: each atom is partly occluded by the other -> its own
    # per-residue SASA is strictly between 0 and the isolated-atom area.
    r = atlas.VDW["C"] + atlas.PROBE
    iso = 4.0 * math.pi * r * r
    atoms = [
        {"resid": 1, "resname": "ALA", "name": "CA", "elem": "C", "x": 0.0, "y": 0.0, "z": 0.0},
        {"resid": 2, "resname": "ALA", "name": "CA", "elem": "C", "x": 1.0, "y": 0.0, "z": 0.0},
    ]
    sasa = atlas.shrake_rupley(atoms, n_points=200)
    assert 0.0 < sasa[1] < iso
    assert 0.0 < sasa[2] < iso
