#!/usr/bin/env python3
"""Tests for the NR4A3 BioEmu cryptic-pocket cross-check — pure JobSpec construction + frame renumbering.
Pure stdlib (no mdtraj/bioemu/torch needed): the renumber test uses a duck-typed topology stub."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nr4a3_bioemu_prepare as P  # noqa: E402
from nr4a3_bioemu_vast_launch import build_jobspec, NR4A3_LBD_SEQ, CHIGNOLIN_SEQ  # noqa: E402


# --- launcher: pure JobSpec construction ---------------------------------------------------------

def test_real_jobspec_carries_full_lbd_and_scorer_chain():
    spec = build_jobspec(mode="real", git_branch="mybranch")
    assert spec.name == "nr4a3-bioemu-crosscheck"
    assert spec.env["SEQUENCE"] == NR4A3_LBD_SEQ and len(NR4A3_LBD_SEQ) == 254  # UniProt 373..626
    assert spec.env["NUM_SAMPLES"] == "200" and spec.env["GIT_BRANCH"] == "mybranch"
    assert spec.image.endswith("bioemu:latest")
    assert spec.resume is False                      # a single ensemble isn't per-unit resumable
    assert spec.resources.gpu in ("rtx4090", "a100") and spec.resources.min_cuda >= 12.4
    body = spec.command[2]
    assert spec.command[0] == "bash"
    # the whole chain must be present and the repo placeholder substituted
    for needle in ("bioemu.sample", "bioemu.sidechain_relax", "nr4a3_bioemu_prepare.py",
                   "nr4a3_bioemu_pocket.py", "archive/refs/heads", "aws s3 cp"):
        assert needle in body, needle
    assert "{repo}" not in body


def test_smoke_jobspec_uses_chignolin_and_is_small():
    spec = build_jobspec(mode="smoke")
    assert spec.name == "nr4a3-bioemu-smoke"
    assert spec.env["SEQUENCE"] == CHIGNOLIN_SEQ and spec.env["NUM_SAMPLES"] == "5"
    assert spec.env["MODE"] == "smoke"


def test_num_samples_and_batch_override():
    spec = build_jobspec(mode="real", num_samples=50, batch_size_100=4)
    assert spec.env["NUM_SAMPLES"] == "50" and spec.env["BATCH_SIZE_100"] == "4"


# --- prepare: residue renumbering (BioEmu 1..254 -> UniProt 373..626) ----------------------------

class _Res:
    def __init__(self, resSeq):
        self.resSeq = resSeq


class _Topo:
    def __init__(self, resseqs):
        self._res = [_Res(r) for r in resseqs]

    @property
    def residues(self):
        return iter(self._res)


def test_renumber_offset_maps_1_to_373_and_254_to_626():
    top = _Topo(range(1, 255))                       # BioEmu numbering 1..254
    lo, hi = P.renumber_topology(top, offset=P.OFFSET)
    assert (lo, hi) == (373, 626)
    seqs = [r.resSeq for r in top.residues]
    assert seqs[0] == 373 and seqs[-1] == 626
    # every Pocket-5 lining residue (UniProt numbering) is now present
    present = set(seqs)
    assert all(r in present for r in (406, 407, 410, 411, 412, 481, 484, 485, 531, 534))


def test_offset_is_lbd_first_minus_one():
    assert P.OFFSET == P.LBD_FIRST - 1 == 372
