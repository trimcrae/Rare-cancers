#!/usr/bin/env python3
"""Tests for the NR-V04 covalent-MD driver's pure geometry helpers (kabsch superposition + interface
selection). The OpenMM build/run is validated on CI, not here. Needs numpy."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("numpy")

from nrv04_covalent_md import (  # noqa: E402
    _aligned_iface_rmsd,
    _built_paths,
    _ckpt_paths,
    _load_built_system,
    _load_resume,
    interface_atom_indices,
    kabsch_rmsd,
)

_REF = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]


def test_kabsch_is_rotation_translation_invariant():
    assert abs(kabsch_rmsd(_REF, _REF)) < 1e-9
    rot = [(-y, x, z) for (x, y, z) in _REF]                 # 90deg about z
    rot = [(x + 5, y - 3, z + 2) for (x, y, z) in rot]       # + translation
    assert kabsch_rmsd(rot, _REF) < 1e-6                     # superposition removes it


def test_kabsch_sensitive_to_real_displacement():
    assert kabsch_rmsd([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 5)], _REF) > 0.5


def test_kabsch_rejects_bad_shapes():
    for bad in ([], [(0, 0, 0)]):
        with pytest.raises(ValueError):
            kabsch_rmsd(bad, _REF)


def test_aligned_iface_rmsd_returns_nan_on_nonfinite():
    """A covalent-pull blow-up produces NaN coordinates; the R1 helper must return NaN (so the caller's
    finite guard records a 'blew_up' outcome) instead of raising LinAlgError and crashing the whole leg."""
    import math
    ca = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    nan_ca = [(float("nan"), 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    assert math.isnan(_aligned_iface_rmsd(nan_ca, ca, nan_ca, ca))
    assert math.isnan(_aligned_iface_rmsd(ca, nan_ca, ca, nan_ca))
    # finite input still yields a real number (0 for identical frames)
    assert abs(_aligned_iface_rmsd(ca, ca, ca, ca)) < 1e-6


def test_ckpt_resume_roundtrip_and_validation(tmp_path):
    """The resume gate must accept a VALID in-progress production checkpoint and reject stale/mismatched/finished
    ones — so a spot-preempted leg resumes, but a completed or wrong-leg checkpoint never spuriously resumes."""
    import json

    d = str(tmp_path)
    state_path, cj_path = _ckpt_paths(d, "cov_nr4a1", 0)
    assert state_path.endswith("ckpt_cov_nr4a1_s0.state.xml")
    assert cj_path.endswith("ckpt_cov_nr4a1_s0.ckpt.json")

    # nothing on disk (and no S3) -> no resume
    assert _load_resume(state_path, cj_path, None, "cov_nr4a1", 0) is None

    def _write(done, frames, leg="cov_nr4a1", seed=0, phase="production"):
        open(state_path, "w").write("<State/>")               # loadState content is irrelevant to the gate
        json.dump({"leg_id": leg, "seed": seed, "phase": phase, "done_frames": done, "frames": frames},
                  open(cj_path, "w"))

    _write(30, 100)                                            # valid mid-production checkpoint
    got = _load_resume(state_path, cj_path, None, "cov_nr4a1", 0)
    assert got is not None and got["done_frames"] == 30

    _write(100, 100)                                           # finished (done == frames) -> do NOT resume
    assert _load_resume(state_path, cj_path, None, "cov_nr4a1", 0) is None

    _write(30, 100, seed=1)                                    # wrong seed -> do NOT resume
    assert _load_resume(state_path, cj_path, None, "cov_nr4a1", 0) is None

    _write(30, 100, phase="equil")                            # not yet in production -> do NOT resume
    assert _load_resume(state_path, cj_path, None, "cov_nr4a1", 0) is None


def test_built_paths_names():
    bp = _built_paths("/x", "cov_nr4a1", 2)
    assert bp["system"].endswith("built_cov_nr4a1_s2.system.xml")
    assert bp["cif"].endswith("built_cov_nr4a1_s2.solv.cif")
    assert bp["meta"].endswith("built_cov_nr4a1_s2.built.json")


def test_load_built_system_returns_none_without_snapshot(tmp_path):
    """The poisoned-leg fallback: a checkpoint with NO matching built-system snapshot must return None so the
    driver restarts the leg cleanly instead of resuming into a re-solvated (wrong atom count) system. This path
    runs BEFORE any OpenMM import, so it works in the CI-lite env with no MD stack installed."""
    bp = _built_paths(str(tmp_path), "cov_nr4a1", 0)
    assert _load_built_system(bp, None) is None               # nothing on disk, no S3
    # a partial snapshot (system XML present, cif/meta missing) is still un-resumable -> None
    open(bp["system"], "w").write("<System/>")
    assert _load_built_system(bp, None) is None


def test_interface_selection_respects_cutoff():
    pos = [(0, 0, 0), (0.5, 0, 0), (0.9, 0, 0), (5, 0, 0)]
    chains = ["A", "A", "B", "B"]
    e3, tg = interface_atom_indices(pos, chains, {"A"}, {"B"}, cutoff_nm=0.8)
    assert e3 == [1] and tg == [2]                           # atom 0 is 0.9 nm away -> excluded
    e3w, _ = interface_atom_indices(pos, chains, {"A"}, {"B"}, cutoff_nm=1.0)
    assert e3w == [0, 1]                                     # widening the cutoff pulls atom 0 in
