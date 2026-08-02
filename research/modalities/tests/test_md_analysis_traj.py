#!/usr/bin/env python3
"""Guards for the durable analysis trajectory — nr4a3-program-map.md RUNG 3's adopted requirement, finally wired.

WHAT THESE TESTS ARE ACTUALLY PROTECTING. The NR-V04 covalent panel was re-run from zero because three
POST-HOC ANALYSIS bugs (a positional chain split, a chain-blind cysteine search, an nm-labelled-as-Å readout)
were uncorrectable without coordinates, and the driver had thrown every frame away. So the load-bearing
assertions here are not "does it write a file" — they are:

  * `test_selection_keeps_every_atom_the_three_historical_defects_needed` — the selection is only worth its
    bytes if it can actually re-derive those three readouts. If a future edit narrows it, that test fails.
  * `test_a_torn_final_frame_is_dropped_not_raised` — the file is append-only precisely because the process
    writing it gets killed. A reader that refuses a truncated blob would recreate, one layer up, the
    all-or-nothing loss this module exists to prevent.
  * `test_resume_truncates_so_a_replayed_frame_is_not_duplicated` — a preempted leg re-enters the loop at its
    checkpoint, so without truncation the blob silently grows a duplicate of every post-checkpoint frame.
  * `test_a_write_failure_never_raises_into_the_md_loop` — this rides on a billed GPU leg. A diagnostic that
    can kill the result it is documenting is worse than no diagnostic.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import md_analysis_traj as MT  # noqa: E402


class _El:
    def __init__(self, symbol):
        self.symbol = symbol


class _Chain:
    def __init__(self, cid):
        self.id = cid


class _Res:
    def __init__(self, name, chain):
        self.name, self.chain = name, _Chain(chain)


class _Atom:
    """The subset of an OpenMM Topology atom this module reads. Deliberately a stand-in, so the selection is
    testable in the dev sandbox — the real one needs the MD stack (CLAUDE.md §6: untestable-in-sandbox is not
    untestable, but testable-in-sandbox is strictly better)."""

    def __init__(self, index, name, resname, chain, symbol=None):
        self.index, self.name = index, name
        self.residue = _Res(resname, chain)
        self.element = _El(symbol if symbol is not None else name[0])


def _topology():
    """A miniature of the real thing: target chain A, E3 chain E, waters/ions, and a ligand."""
    return [
        _Atom(0, "N", "CYS", "A"), _Atom(1, "CA", "CYS", "A"), _Atom(2, "CB", "CYS", "A"),
        _Atom(3, "SG", "CYS", "A", "S"), _Atom(4, "HA", "CYS", "A", "H"),
        _Atom(5, "CA", "LYS", "A"), _Atom(6, "NZ", "LYS", "A", "N"), _Atom(7, "CD", "LYS", "A"),
        _Atom(8, "CA", "LEU", "E"), _Atom(9, "SG", "CYS", "E", "S"), _Atom(10, "CA", "CYS", "E"),
        _Atom(11, "O", "HOH", "W", "O"), _Atom(12, "NA", "NA", "W", "NA"),
        _Atom(13, "C1", "LIG", "L"), _Atom(14, "O2", "LIG", "L", "O"), _Atom(15, "H1", "LIG", "L", "H"),
    ]


def test_selection_keeps_every_atom_the_three_historical_defects_needed():
    idx, labels = MT.select_analysis_atoms(_topology())
    by_label = dict(zip(labels, idx))
    # defect 1 (positional chain split): CAs on BOTH chains, so a split can be re-derived from the file alone
    assert {i for i in idx} >= {1, 5, 8, 10}
    assert any(l.startswith("A:") for l in labels) and any(l.startswith("E:") for l in labels)
    # defect 2 (chain-blind reactive-Cys search): every Cys SG, target chain AND E3 chain
    assert by_label["A:CYS:SG"] == 3 and by_label["E:CYS:SG"] == 9
    # defect 3 (R3 nm/Å unit error): every target Lys NZ
    assert by_label["A:LYS:NZ"] == 6
    # the ligand's heavy atoms, since a warhead pose is the other thing nobody could re-check
    assert by_label["L:LIG:C1"] == 13 and by_label["L:LIG:O2"] == 14


def test_selection_drops_hydrogens_solvent_and_ions_and_returns_ascending_indices():
    idx, _ = MT.select_analysis_atoms(_topology())
    assert 4 not in idx and 15 not in idx, "hydrogens are never persisted"
    assert 11 not in idx and 12 not in idx, "bulk water and monatomic ions are not analysis atoms"
    assert 2 not in idx and 7 not in idx, "unselected polymer sidechain atoms are the deliberate saving"
    assert idx == sorted(idx), "ascending order is the contract the manifest's atom_indices relies on"


def test_all_heavy_widens_the_pick_but_still_drops_hydrogens_and_solvent():
    narrow, _ = MT.select_analysis_atoms(_topology())
    wide, _ = MT.select_analysis_atoms(_topology(), all_heavy=True)
    assert set(wide) > set(narrow), "all_heavy must be a strict superset — it is the literal requirement"
    assert 2 in wide and 7 in wide, "sidechain heavy atoms are what the wide policy buys"
    assert 4 not in wide and 15 not in wide and 11 not in wide


def _writer(tmp_path, **kw):
    idx, lab = MT.select_analysis_atoms(_topology())
    return MT.TrajWriter(str(tmp_path / "traj_leg_s0"), idx, lab, **kw)


def _frames(n, n_atoms=16):
    return [[(k + 0.001 * i, k + 0.002 * i, k + 0.003 * i) for i in range(n_atoms)] for k in range(n)]


def test_round_trip_preserves_only_the_selected_atoms_and_their_coordinates(tmp_path):
    w = _writer(tmp_path).start()
    for k, fr in enumerate(_frames(4)):
        assert w.append(fr, k) is True
    man, got = MT.read_frames(str(tmp_path / "traj_leg_s0"))
    assert len(got) == 4 and len(got[0]) == man["n_atoms"] == len(w.indices)
    src = _frames(4)
    for k in range(4):
        for j, atom_i in enumerate(man["atom_indices"]):
            assert got[k][j] == pytest.approx(src[k][atom_i], abs=1e-5)
    assert man["units"] == "nm", "the unit is recorded because a silent unit was defect 3"


def test_stride_frames_writes_only_the_strided_frames(tmp_path):
    w = _writer(tmp_path, stride_frames=3).start()
    written = [w.append(fr, k) for k, fr in enumerate(_frames(7))]
    assert written == [True, False, False, True, False, False, True]
    _, got = MT.read_frames(str(tmp_path / "traj_leg_s0"))
    assert len(got) == 3


def test_resume_truncates_so_a_replayed_frame_is_not_duplicated(tmp_path):
    prefix = str(tmp_path / "traj_leg_s0")
    w = _writer(tmp_path).start()
    for k, fr in enumerate(_frames(5)):
        w.append(fr, k)                       # 5 frames written, but the last checkpoint was at frame 3
    w2 = _writer(tmp_path).start(resume_frames=3)
    _, got = MT.read_frames(prefix)
    assert len(got) == 3, "frames past the checkpoint must be dropped — the loop is about to replay them"
    assert w2.n_written == 3, "the resumed writer's counter continues the file, it does not restart it"
    for k, fr in enumerate(_frames(5)):
        if k >= 3:
            w2.append(fr, k)
    _, got2 = MT.read_frames(prefix)
    assert len(got2) == 5, "and the replay lands exactly once"


def test_a_torn_final_frame_is_dropped_not_raised(tmp_path):
    prefix = str(tmp_path / "traj_leg_s0")
    w = _writer(tmp_path).start()
    for k, fr in enumerate(_frames(3)):
        w.append(fr, k)
    with open(prefix + ".f32", "r+b") as fh:  # a kill -9 mid-write: half a frame on the end
        fh.truncate(os.path.getsize(prefix + ".f32") - (w.frame_bytes // 2))
    _, got = MT.read_frames(prefix)
    assert len(got) == 2, "a partial trailing frame is ignored; refusing the file would recreate the total loss"


def test_a_write_failure_never_raises_into_the_md_loop_and_is_recorded(tmp_path):
    w = _writer(tmp_path).start()
    w.append(_frames(1)[0], 0)
    w.blob_path = str(tmp_path / "no_such_dir" / "x.f32")     # make the next write fail
    assert w.append(_frames(1)[0], 1) is False, "a failed write returns False rather than killing a billed leg"
    assert w.errors and "append@1" in w.errors[0]
    assert w.summary()["errors"], "and the failure is in the RESULT, not only in the log"


def test_disabled_writer_is_a_total_no_op(tmp_path):
    w = _writer(tmp_path, enabled=False).start()
    assert w.append(_frames(1)[0], 0) is False
    assert not os.path.exists(str(tmp_path / "traj_leg_s0.f32"))
    assert w.summary()["enabled"] is False


def test_manifest_states_what_is_NOT_persisted(tmp_path):
    _writer(tmp_path).start()
    man = json.load(open(str(tmp_path / "traj_leg_s0.traj.json")))
    assert "_not_a_full_trajectory" in man, (
        "the manifest must say this is the analysis closure, not every heavy atom — an over-read of this file "
        "as a complete trajectory is the one way it could mislead a future analysis")
    assert man["_format"] == MT.MAGIC and man["dtype"] == "<f4"


def test_budget_is_the_order_of_magnitude_the_requirement_was_costed_at():
    """The requirement was justified as 'tens of MB against the ~112 MB System XML the driver already uploads'.
    A selection that quietly grew to hundreds of MB per leg would be silently declining the trade."""
    n_atoms = 1000                                            # ~this lane's CA + Cys SG + Lys NZ + ligand count
    per_frame = 12 * n_atoms
    assert per_frame * 600 < 15 * 1024 * 1024, "600 frames must stay in single-digit MB"
