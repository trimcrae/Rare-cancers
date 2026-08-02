#!/usr/bin/env python3
"""Guards for the native-frame input builder and the positive control. Offline, no network, no RDKit."""
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
import selcal_deepternary_frame as FR        # noqa: E402
import selcal_deepternary_poscontrol as PC   # noqa: E402


def _atom(chain, resseq, resname, name, xyz, hetatm=False, element=None):
    return V.Atom(chain, resseq, "", resname, name, element or name[0], xyz[0], xyz[1], xyz[2], hetatm)


def _chain_atoms(chain, seq, origin=(0.0, 0.0, 0.0), spacing=3.8):
    """One CA per residue along +x, so a sequence alignment has something to superpose."""
    out = []
    for i, aa in enumerate(seq):
        three = [k for k, v in V._THREE_TO_ONE.items() if v == aa and len(k) == 3][0]
        out.append(_atom(chain, i + 1, three, "CA",
                         (origin[0] + i * spacing, origin[1], origin[2]), element="C"))
    return out


# ---------- geometry --------------------------------------------------------------------------------------


def test_kabsch_recovers_a_known_rigid_motion():
    rng = np.random.default_rng(7)
    P = rng.normal(size=(30, 3)) * 10.0
    theta = 0.7
    Rtrue = np.array([[np.cos(theta), -np.sin(theta), 0.0],
                      [np.sin(theta), np.cos(theta), 0.0],
                      [0.0, 0.0, 1.0]])
    ttrue = np.array([4.0, -2.0, 7.0])
    Q = (Rtrue @ P.T).T + ttrue
    R, t = FR.kabsch(P, Q)
    assert FR.rmsd([(R @ p + t) for p in P], Q) < 1e-8
    assert np.linalg.det(R) > 0            # a proper rotation, never a reflection


def test_kabsch_does_not_solve_a_reflection():
    """A mirrored point set must NOT superpose to zero — a reflection would fake a perfect fit."""
    P = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1]], dtype=float)
    Q = P.copy()
    Q[:, 2] *= -1.0
    R, t = FR.kabsch(P, Q)
    assert np.linalg.det(R) > 0
    assert FR.rmsd([(R @ p + t) for p in P], Q) > 0.1


def test_copy_atom_leaves_the_original_untouched():
    a = _atom("A", 1, "ALA", "CA", (1.0, 2.0, 3.0))
    b = FR.copy_atom(a, chain="Z", x=9.0)
    assert (a.chain, a.x) == ("A", 1.0)
    assert (b.chain, b.x, b.y) == ("Z", 9.0, 2.0)


def test_apply_rt_is_not_in_place():
    atoms = [_atom("A", 1, "ALA", "CA", (0.0, 0.0, 0.0))]
    moved = FR.apply_rt(atoms, np.eye(3), np.array([5.0, 0.0, 0.0]))
    assert atoms[0].x == 0.0 and moved[0].x == 5.0


def test_min_dist_counts_uses_the_models_own_1A_window():
    assert FR.SNAP_WINDOW_A == 1.0, "the window is READ from replace_to_unbound_coords, not chosen here"
    probe = [_atom("A", 1, "LIG", "C1", (0.0, 0.0, 0.0), hetatm=True),
             _atom("A", 1, "LIG", "C2", (5.0, 0.0, 0.0), hetatm=True)]
    ref = [_atom("B", 1, "FRG", "C1", (0.5, 0.0, 0.0), hetatm=True)]
    n, closest = FR.min_dist_counts(probe, ref)
    assert n == 1 and closest == 0.5


def test_min_dist_counts_reports_zero_rather_than_crashing_on_an_empty_side():
    assert FR.min_dist_counts([], []) == (0, None)


# ---------- moving a file instead of rebuilding it ----------------------------------------------------------


def test_transform_pdb_coordinates_moves_only_coordinates(tmp_path):
    """The measured fix: a file already verified readable is MOVED, never rebuilt."""
    src = tmp_path / "lig.pdb"
    src.write_text(
        "REMARK   1 provenance line that must survive\n"
        "HETATM    1  C1  LIG A 301       1.000   2.000   3.000  1.00 11.11           C\n"
        "HETATM    2  C2  LIG A 301       2.500   2.000   3.000  1.00 22.22           C\n"
        "CONECT    1    2\n"
        "END\n")
    dst = tmp_path / "moved.pdb"
    n = FR.transform_pdb_coordinates(str(src), str(dst), np.eye(3), np.array([10.0, 0.0, 0.0]))
    assert n == 2
    out = dst.read_text().splitlines()
    assert out[0] == "REMARK   1 provenance line that must survive"
    assert out[3] == "CONECT    1    2" and out[4] == "END"
    assert out[1].startswith("HETATM    1  C1  LIG A 301")
    assert out[1][30:54] == "%8.3f%8.3f%8.3f" % (11.0, 2.0, 3.0)
    assert out[1][54:].strip() == "1.00 11.11           C".strip()   # occupancy/B/element untouched
    assert out[1][54:] == src.read_text().splitlines()[1][54:]       # byte-identical past the coordinates


def test_transform_pdb_coordinates_works_in_place(tmp_path):
    """src == dest is the ONLY way this is called. Streaming truncated all four files on run 30755624681."""
    p = tmp_path / "lig.pdb"
    p.write_text(
        "HETATM    1  C1  LIG A 301       1.000   2.000   3.000  1.00  0.00           C\n"
        "HETATM    2  C2  LIG A 301       2.500   2.000   3.000  1.00  0.00           C\n"
        "CONECT    1    2\nEND\n")
    n = FR.transform_pdb_coordinates(str(p), str(p), np.eye(3), np.array([5.0, 0.0, 0.0]))
    assert n == 2, "in-place rewrite must not lose the source"
    out = p.read_text().splitlines()
    assert len(out) == 4 and out[2] == "CONECT    1    2"
    assert out[0][30:54] == "%8.3f%8.3f%8.3f" % (6.0, 2.0, 3.0)


def test_transform_pdb_coordinates_refuses_an_empty_file(tmp_path):
    p = tmp_path / "empty.pdb"
    p.write_text("REMARK nothing here\nEND\n")
    with pytest.raises(ValueError):
        FR.transform_pdb_coordinates(str(p), str(p), np.eye(3), np.zeros(3))
    assert p.read_text().startswith("REMARK"), "a refusal must not have destroyed the input"


def test_transform_preserves_every_interatomic_distance():
    """Why readability cannot change: a rigid motion is an isometry."""
    import math
    th = 0.7
    R = np.array([[math.cos(th), -math.sin(th), 0.0], [math.sin(th), math.cos(th), 0.0], [0.0, 0.0, 1.0]])
    P = np.array([[0.0, 0, 0], [1.5, 0, 0], [0, 2.5, 0]])
    Q = (R @ P.T).T + np.array([7.0, -3.0, 2.0])
    for i in range(3):
        for j in range(3):
            assert abs(np.linalg.norm(P[i] - P[j]) - np.linalg.norm(Q[i] - Q[j])) < 1e-9


def test_rdkit_readable_reports_a_refusal_not_a_crash(tmp_path):
    pytest.importorskip("rdkit")
    bad = tmp_path / "empty.pdb"
    bad.write_text("END\n")
    ok, why = FR.rdkit_readable(str(bad))
    assert ok is False and why


def test_this_module_writes_no_conect_records():
    """CONECT is the defect here, not an omission: re-declaring a bond RDKit already inferred by proximity
    raises its order, and `get_lig_coords` then gets None back."""
    src = open(os.path.join(MOD, "selcal_deepternary_frame.py")).read()
    assert "conect_for=" not in src, "a CONECT-writing call came back; see transform_pdb_coordinates"


# ---------- native decomposition --------------------------------------------------------------------------


def _toy_native(degrader_resname="A1BB4", n_copies=3):
    """Three copies of a target+E3+degrader assembly, far apart, so copy choice is testable."""
    atoms = []
    for c in range(n_copies):
        off = c * 200.0
        atoms += _chain_atoms(chr(ord("A") + 3 * c), "ACDEFGHIKLMNPQRSTVWY", origin=(off, 0.0, 0.0))
        atoms += _chain_atoms(chr(ord("B") + 3 * c), "WYVTSRQPNMLKIHGFEDCA", origin=(off, 30.0, 0.0))
        atoms.append(_atom(chr(ord("A") + 3 * c), 900 + c, degrader_resname, "C1",
                           (off + 35.0, 15.0, 0.0), hetatm=True, element="C"))
    return atoms


def test_native_copy_picks_the_degrader_belonging_to_the_named_chains():
    atoms = _toy_native()
    roles = {"target": "D", "e3": ["E"]}          # the SECOND copy
    tgt, e3, deg, err = FR.native_copy(atoms, roles, "A1BB4")
    assert err is None
    assert {a.chain for a in tgt} == {"D"} and {a.chain for a in e3} == {"E"}
    assert len(deg) == 1 and abs(deg[0].x - 235.0) < 1e-6


def test_native_copy_refuses_when_the_degrader_is_absent():
    atoms = _toy_native(degrader_resname="SO4")
    _, _, _, err = FR.native_copy(atoms, {"target": "A", "e3": ["B"]}, "A1BB4")
    assert err and "A1BB4" in err


def test_native_copy_refuses_an_unknown_chain_rather_than_falling_back():
    _, _, _, err = FR.native_copy(_toy_native(), {"target": "Z", "e3": ["B"]}, "A1BB4")
    assert err and "target chain Z" in err


# ---------- superposition ---------------------------------------------------------------------------------


def test_superpose_onto_recovers_the_frame_and_reports_it():
    native = _chain_atoms("A", "ACDEFGHIKLMNPQRSTVWY", origin=(0.0, 0.0, 0.0))
    unbound = _chain_atoms("Q", "ACDEFGHIKLMNPQRSTVWY", origin=(100.0, 50.0, -20.0))
    R, t, detail, err = FR.superpose_onto(unbound, native, "p1")
    assert err is None, err
    assert detail["unbound_chain"] == "Q" and detail["native_chain"] == "A"
    assert detail["identity"] == 1.0 and detail["ca_rmsd_A"] < 1e-6
    moved = FR.apply_rt(unbound, R, t)
    assert abs(moved[0].x - 0.0) < 1e-6


def test_superpose_onto_refuses_a_different_protein():
    native = _chain_atoms("A", "ACDEFGHIKLMNPQRSTVWY")
    unbound = _chain_atoms("Q", "WWWWWWWWWWWWWWWWWWWW", origin=(100.0, 0.0, 0.0))
    R, t, _, err = FR.superpose_onto(unbound, native, "p1")
    assert R is None and err and "identity" in err


def test_superpose_onto_refuses_too_few_pairs():
    native = _chain_atoms("A", "ACDEF")
    unbound = _chain_atoms("Q", "ACDEF", origin=(50.0, 0.0, 0.0))
    R, _, _, err = FR.superpose_onto(unbound, native, "p1")
    assert R is None and err and "Cα pairs" in err


def test_superposition_rmsd_ceiling_is_declared_not_implicit():
    assert FR.MAX_SUPERPOSITION_RMSD_A == 5.0


# ---------- refusals over the whole arm --------------------------------------------------------------------


def test_prepare_arm_refuses_a_missing_native_rather_than_writing_something(tmp_path):
    cfg = {"name": "arm", "native_pdb": "9XXX", "degrader_comp": "A1BB4",
           "warhead_comp": "W", "anchor_comp": "N"}
    row = FR.prepare_arm(cfg, str(tmp_path), str(tmp_path), str(tmp_path))
    assert row["ok"] is False and "not found" in row["why"]
    assert not list(tmp_path.glob("**/ligand.pdb"))


# ---------- the positive control ---------------------------------------------------------------------------


def test_poscontrol_refuses_to_choose_among_several_interfaces():
    doc = {"best_result": {"AB": {"DockQ": 0.9, "fnat": 1.0}, "CD": {"DockQ": 0.1, "fnat": 0.0}}}
    iface, err = PC.single_interface(doc)
    assert iface is None and err and "refuses to choose" in err


def test_poscontrol_takes_the_single_interface():
    doc = {"best_result": {"AB": {"DockQ": 0.87, "fnat": 0.71, "iRMSD": 1.2}}}
    iface, err = PC.single_interface(doc)
    assert err is None and iface["DockQ"] == 0.87


def test_poscontrol_records_no_predictions_as_unrun_never_as_zero(tmp_path):
    native = tmp_path / "gt_complex.pdb"
    native.write_text("ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C\n")
    doc = PC.score_predictions(str(tmp_path), str(native))
    assert doc.get("summary") is None
    assert doc.get("positive_control_passes") is None
    assert "Unrun is not a run that scored zero" in doc["sentence"]


def test_poscontrol_missing_reference_is_unread_not_failed(tmp_path):
    doc = PC.score_predictions(str(tmp_path), str(tmp_path / "nope.pdb"))
    assert "UNREAD control" in doc["sentence"]
    assert doc.get("positive_control_passes") is None


def test_poscontrol_bars_are_dockqs_own_class_boundaries():
    assert (PC.ACCEPTABLE_DOCKQ, PC.POSITIVE_CONTROL_DOCKQ) == (0.23, 0.49)


def test_poscontrol_never_claims_generalisation():
    src = open(os.path.join(MOD, "selcal_deepternary_poscontrol.py")).read()
    assert "case_is_in_set" in src
    assert "generalisation" in src


# ---------- the correction this module carries ---------------------------------------------------------------


def test_the_selcal_arms_are_not_described_as_blind_anywhere_in_this_lane():
    """The published unbound protocol is native-framed; any surviving 'blind' claim is a false one."""
    for fname in ("selcal_deepternary_frame.py", "selcal_deepternary_score.py"):
        src = open(os.path.join(MOD, fname)).read()
        for line in src.splitlines():
            low = line.lower()
            if "blind" not in low:
                continue
            # A line may say the word only to retire it, or to name a module/file that carries it.
            assert any(k in low for k in ("not blind", "not_blind", "not available", "blind prep",
                                          "blind_prep", "as if it were", "not a blind", "no longer",
                                          "until", "must never", "was used here")), \
                "unretired 'blind' claim in %s: %s" % (fname, line.strip())
