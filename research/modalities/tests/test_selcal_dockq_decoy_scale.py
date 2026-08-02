#!/usr/bin/env python3
"""Guards for the DockQ decoy scale — the ruler that gives 0.023-0.046 a meaning. Offline, no DockQ needed."""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

np = pytest.importorskip("numpy")

import selcal_cofold_validate as V           # noqa: E402
import selcal_dockq_decoy_scale as D         # noqa: E402


def _atom(chain, resseq, name, xyz):
    return V.Atom(chain, resseq, "", "ALA", name, name[0], xyz[0], xyz[1], xyz[2], False)


def test_random_rotation_is_a_proper_rotation_of_the_requested_angle():
    rng = np.random.default_rng(3)
    for ang in (0.1, 0.7, 1.5, 3.0):
        R = D.random_rotation(rng, ang)
        assert abs(np.linalg.det(R) - 1.0) < 1e-9, "a reflection is not a rigid motion"
        assert np.allclose(R.T @ R, np.eye(3), atol=1e-9)
        # trace of a rotation matrix is 1 + 2 cos(theta)
        assert abs(np.trace(R) - (1.0 + 2.0 * np.cos(ang))) < 1e-9


def test_displace_realises_the_requested_rmsd():
    """The swept quantity is MEASURED after the move, not assumed from the parameters."""
    rng = np.random.default_rng(11)
    atoms = [_atom("A", i, "CA", (i * 3.8, 0.0, 0.0)) for i in range(40)]
    for mag in (0.5, 2.0, 8.0, 32.0):
        moved, realised = D.displace(atoms, mag, rng)
        assert abs(realised - mag) < 1e-3, (mag, realised)
        assert len(moved) == len(atoms)
    # and it does not mutate the input
    assert atoms[1].x == 3.8


def test_displace_at_zero_is_the_identity():
    rng = np.random.default_rng(1)
    atoms = [_atom("A", i, "CA", (i * 3.8, 1.0, 2.0)) for i in range(12)]
    moved, realised = D.displace(atoms, 0.0, rng)
    assert realised == 0.0
    assert [(a.x, a.y, a.z) for a in moved] == [(a.x, a.y, a.z) for a in atoms]


def test_displacement_ladder_brackets_both_ends():
    assert D.DISPLACEMENTS_A[0] == 0.0, "an undisplaced native is the top of the scale and must be measured"
    assert max(D.DISPLACEMENTS_A) >= 16.0, "the ladder must reach far enough to leave no interface"


def test_interpret_refuses_when_nothing_was_scored():
    doc = D.interpret({"native": "9DTY", "points": [{"requested_rmsd_A": 4.0, "DockQ": None}]})
    assert "UNMEASURED" in doc["sentence"]
    assert doc.get("displacement_matching_cofolds_A") is None


def test_interpret_says_so_when_the_cofolds_sit_below_the_whole_scale(monkeypatch):
    monkeypatch.setattr(D, "read_cofold_range", lambda path=None: ((0.001, 0.002), None))
    doc = D.interpret({"native": "9DTY", "points": [
        {"requested_rmsd_A": 4.0, "DockQ": {"median": 0.40, "min": 0.3, "max": 0.5}},
        {"requested_rmsd_A": 32.0, "DockQ": {"median": 0.10, "min": 0.0, "max": 0.2}}]})
    assert "BELOW this whole decoy scale" in doc["sentence"]
    assert doc["displacement_matching_cofolds_A"] is None


def test_interpret_names_the_displacement_the_cofolds_match(monkeypatch):
    monkeypatch.setattr(D, "read_cofold_range", lambda path=None: ((0.023, 0.046), None))
    doc = D.interpret({"native": "9DTY", "points": [
        {"requested_rmsd_A": 0.0, "DockQ": {"median": 1.0, "min": 1.0, "max": 1.0}},
        {"requested_rmsd_A": 4.0, "DockQ": {"median": 0.31, "min": 0.2, "max": 0.4}},
        {"requested_rmsd_A": 16.0, "DockQ": {"median": 0.04, "min": 0.0, "max": 0.08}},
        {"requested_rmsd_A": 32.0, "DockQ": {"median": 0.01, "min": 0.0, "max": 0.02}}]})
    assert doc["displacement_matching_cofolds_A"] == 16.0, "the SMALLEST qualifying displacement, not the last"
    assert "16 A" in doc["sentence"]


def test_the_cofold_range_is_read_not_typed(tmp_path):
    p = tmp_path / "selcal-cofold-dockq.json"
    p.write_text(json.dumps({"records": [
        {"dockq": {"DockQ": 0.031}}, {"dockq": {"DockQ": 0.044}}, {"dockq": None}, {}]}))
    rng, err = D.read_cofold_range(str(p))
    assert err is None and rng == (0.031, 0.044)


def test_a_missing_cofold_artifact_is_an_error_not_a_default():
    rng, err = D.read_cofold_range("/definitely/not/here.json")
    assert rng is None and err


def test_the_module_declares_itself_a_negative_control():
    """Half a control is a trap: this must point at the positive one."""
    src = open(os.path.join(MOD, "selcal_dockq_decoy_scale.py")).read()
    assert "NEGATIVE CONTROL" in src
    assert "selcal_deepternary_poscontrol" in src


def test_it_moves_no_verdict():
    src = open(os.path.join(MOD, "selcal_dockq_decoy_scale.py")).read()
    assert "moves no verdict" in src
    for forbidden in ("selcal-verdict", "tier", "prereg"):
        assert forbidden not in src.replace("re-scores no leg", ""), forbidden
