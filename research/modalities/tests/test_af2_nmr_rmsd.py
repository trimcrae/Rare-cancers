"""Unit tests for the pure core of nr4a3_af2_nmr_rmsd (Kabsch RMSD + PDB parsing). numpy only."""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nr4a3_af2_nmr_rmsd as rm  # noqa: E402


def test_kabsch_identity_is_zero():
    P = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], float)
    assert rm.kabsch_rmsd(P, P.copy()) == pytest.approx(0.0, abs=1e-9)


def test_kabsch_invariant_to_rotation_and_translation():
    rng = np.random.default_rng(0)
    P = rng.standard_normal((12, 3))
    theta = 0.7
    R = np.array([[math.cos(theta), -math.sin(theta), 0],
                  [math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
    Q = P @ R.T + np.array([5.0, -2.0, 3.0])          # rigid-body move
    assert rm.kabsch_rmsd(P, Q) == pytest.approx(0.0, abs=1e-6)


def test_kabsch_known_displacement():
    # one atom offset by d along x; after centering, RMSD of a 2-atom set is d/2
    P = np.array([[0, 0, 0], [0, 0, 0]], float)
    Q = np.array([[0, 0, 0], [2.0, 0, 0]], float)
    assert rm.kabsch_rmsd(P, Q) == pytest.approx(1.0, abs=1e-9)


def test_kabsch_shape_guard():
    with pytest.raises(ValueError):
        rm.kabsch_rmsd(np.zeros((3, 3)), np.zeros((4, 3)))


def test_parse_multi_model():
    pdb = (
        "MODEL        1\n"
        "ATOM      1  CA  ALA A 406      1.000   2.000   3.000  1.00\n"
        "ATOM      2  CA  GLY A 407      4.000   5.000   6.000  1.00\n"
        "ENDMDL\n"
        "MODEL        2\n"
        "ATOM      1  CA  ALA A 406      1.100   2.100   3.100  1.00\n"
        "ATOM      2  CA  GLY A 407      4.100   5.100   6.100  1.00\n"
        "ENDMDL\n"
    )
    models = rm.parse_ca_models(pdb)
    assert len(models) == 2
    assert models[0][406] == (1.0, 2.0, 3.0)
    assert models[1][407] == (4.1, 5.1, 6.1)


def test_parse_single_model_no_model_records():
    pdb = ("ATOM      1  CA  ALA A 406      1.000   2.000   3.000  1.00\n"
           "ATOM      2  CA  GLY A 410      4.000   5.000   6.000  1.00\n")
    models = rm.parse_ca_models(pdb)
    assert len(models) == 1 and set(models[0]) == {406, 410}


def test_rmsd_over_residues_needs_three_common():
    a = {1: (0, 0, 0), 2: (1, 0, 0)}
    b = {1: (0, 0, 0), 2: (1, 0, 0)}
    val, n = rm.rmsd_over_residues(a, b, [1, 2])
    assert val is None and n == 2                      # <3 common -> undefined


def test_summarize():
    assert rm.summarize([]) == {}
    s = rm.summarize([1.0, 3.0, 2.0, None])
    assert s == {"n": 3, "min": 1.0, "mean": 2.0, "max": 3.0}


def test_parse_ca_sequence_first_model_only():
    pdb = ("MODEL        1\n"
           "ATOM      1  CA  ALA A 406      1.0   2.0   3.0\n"
           "ATOM      2  CA  TRP A 407      4.0   5.0   6.0\n"
           "ENDMDL\n"
           "MODEL        2\n"
           "ATOM      1  CA  GLY A 406      1.0   2.0   3.0\n"
           "ENDMDL\n")
    seq = rm.parse_ca_sequence(pdb)
    assert seq == {406: "A", 407: "W"}                 # first model only, 3->1 letter


def test_find_registration_offset_recovers_constant_shift():
    # reference = full-length "A R N D C Q E G H" at resSeq 1..9; query = the "D C Q" stretch renumbered 1..3
    ref = dict(zip(range(1, 10), "ARNDCQEGH"))
    qry = {1: "D", 2: "C", 3: "Q"}                      # corresponds to ref 4,5,6 -> offset +3
    o, matched, cov = rm.find_registration_offset(ref, qry)
    assert o == 3 and matched == 3 and cov == 1.0


def test_find_registration_offset_rejects_noncorresponding():
    ref = dict(zip(range(1, 10), "ARNDCQEGH"))
    qry = {1: "K", 2: "K", 3: "K"}                      # no offset matches -> registration must fail
    with pytest.raises(ValueError):
        rm.find_registration_offset(ref, qry, min_identity=0.8)


def test_decompose_flags_within_spread():
    # AF2 sits between two NMR models -> its mean RMSD <= the NMR internal max -> "within spread"
    res = [{r: (0.0, 0.0, 0.0) for r in range(1, 6)},
           {r: (2.0, 0.0, 0.0) for r in range(1, 6)}]      # two NMR models 2 Å apart (translation)
    af2 = {r: (1.0, 0.0, 0.0) for r in range(1, 6)}        # AF2 halfway
    out = rm.decompose(af2, res, list(range(1, 6)), [1, 2, 3])
    # pure translations -> Kabsch removes them -> all RMSDs ~0 -> trivially within spread
    assert out["all_ca"]["af2_within_nmr_spread"] is True
