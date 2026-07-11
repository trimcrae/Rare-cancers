"""Unit tests for the pure core of nr4a_af_crystal_rmsd (chain parsing + alignment-based residue map +
AF-vs-crystal RMSD). numpy only; the biopython aligner is stubbed."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nr4a_af_crystal_rmsd as ac  # noqa: E402


def _atom(serial, res3, chain, resseq, x, y, z, alt=" "):
    # columns per PDB spec; CA atom
    return (f"ATOM  {serial:>5} {'CA':<4}{alt}{res3:<3} {chain}{resseq:>4}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C")


def test_parse_ca_chain_filters_to_requested_chain():
    pdb = "\n".join([
        _atom(1, "ALA", "A", 10, 0, 0, 0),
        _atom(2, "GLY", "A", 11, 1, 0, 0),
        _atom(3, "TRP", "B", 10, 9, 9, 9),          # chain B, same resseq -> must be excluded
    ])
    seq, resnums, coords = ac.parse_ca_chain(pdb, chain="A")
    assert seq == "AG" and resnums == [10, 11]
    assert coords[10] == (0.0, 0.0, 0.0) and 10 in coords and coords[11] == (1.0, 0.0, 0.0)
    assert set(coords) == {10, 11}                   # chain B's resseq-10 not present


def test_parse_ca_chain_none_locks_first_chain():
    pdb = "\n".join([
        _atom(1, "ALA", "A", 10, 0, 0, 0),
        _atom(2, "TRP", "B", 20, 9, 9, 9),           # different chain, ignored once A is locked
    ])
    seq, resnums, coords = ac.parse_ca_chain(pdb, chain=None)
    assert seq == "A" and resnums == [10]


def test_parse_ca_chain_first_altloc_wins():
    pdb = "\n".join([
        _atom(1, "SER", "A", 5, 0, 0, 0, alt="A"),
        _atom(2, "SER", "A", 5, 5, 5, 5, alt="B"),   # altloc B dropped
    ])
    _, resnums, coords = ac.parse_ca_chain(pdb)
    assert resnums == [5] and coords[5] == (0.0, 0.0, 0.0)


def _identity_align(seq_a, seq_b):
    """Stub aligner: aligns the longest common prefix as one block (index-for-index)."""
    n = 0
    for ca, cb in zip(seq_a, seq_b):
        if ca == cb or True:            # align positionally regardless of identity (blocks are index runs)
            n += 1
    return ((0, n),), ((0, n),)


def test_resnum_map_positional_with_stub():
    # seq_a residues numbered 100.., seq_b numbered 1.. ; positional alignment -> constant +(-99) map
    seq_a, res_a = "ARND", [100, 101, 102, 103]
    seq_b, res_b = "ARND", [1, 2, 3, 4]
    mapping, ident = ac.resnum_map(seq_a, res_a, seq_b, res_b, align_fn=_identity_align)
    assert mapping == {100: 1, 101: 2, 102: 3, 103: 4}
    assert ident == pytest.approx(1.0)


def test_resnum_map_identity_counts_mismatches():
    seq_a, res_a = "ARND", [1, 2, 3, 4]
    seq_b, res_b = "AKND", [1, 2, 3, 4]              # position 2 differs (R vs K)
    _, ident = ac.resnum_map(seq_a, res_a, seq_b, res_b, align_fn=_identity_align)
    assert ident == pytest.approx(0.75)


def test_compare_paralogue_identity_geometry_is_zero():
    # AF(para) and crystal identical coords, same numbering -> global & pocket RMSD ~0.
    seq = "ARNDCQEGHILKMFPST"                        # 17 residues
    resnums = list(range(400, 400 + len(seq)))
    xyz = {r: (float(i), float(2 * i), float(3 * i)) for i, r in enumerate(resnums)}
    af_para = (seq, resnums, xyz)
    crystal = (seq, resnums, dict(xyz))
    af_nr4a3 = (seq, resnums, dict(xyz))             # same seq -> pocket maps 1:1
    pocket = [402, 405, 410]                         # three residues in range
    res = ac.compare_paralogue(af_para, crystal, af_nr4a3, pocket_nr4a3=pocket, align_fn=_identity_align,
                               min_id_same=0.9, min_id_cross=0.4)
    assert res["global_ca_rmsd"] == pytest.approx(0.0, abs=1e-6)
    assert res["pocket_ca_rmsd"] == pytest.approx(0.0, abs=1e-6)
    assert res["pocket_ca_n"] == 3
    assert res["global_ca_n"] == len(seq)


def test_compare_paralogue_known_pocket_displacement():
    # displace one pocket residue in the crystal by 3 Å along x; 3-atom Kabsch RMSD of a single 3 Å shift.
    seq = "ARNDCQEGHIL"
    resnums = list(range(400, 400 + len(seq)))
    xyz = {r: (0.0, float(i), 0.0) for i, r in enumerate(resnums)}   # collinear so Kabsch can't rotate it out
    cr = dict(xyz); cr[402] = (3.0, xyz[402][1], 0.0)
    res = ac.compare_paralogue((seq, resnums, xyz), (seq, resnums, cr), (seq, resnums, dict(xyz)),
                               pocket_nr4a3=[400, 401, 402], align_fn=_identity_align,
                               min_id_same=0.9, min_id_cross=0.4)
    assert res["pocket_ca_rmsd"] is not None and res["pocket_ca_rmsd"] > 0.5


def test_compare_paralogue_fails_loud_on_low_identity():
    seq = "ARNDCQEGHIL"; resnums = list(range(1, 12))
    xyz = {r: (float(r), 0.0, 0.0) for r in resnums}
    bad = "KKKKKKKKKKK"                              # 0% identity vs seq
    with pytest.raises(ValueError):
        ac.compare_paralogue((seq, resnums, xyz), (bad, resnums, dict(xyz)), (seq, resnums, dict(xyz)),
                             align_fn=_identity_align, min_id_same=0.9, min_id_cross=0.4)
