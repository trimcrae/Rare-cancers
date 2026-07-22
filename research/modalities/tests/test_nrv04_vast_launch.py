#!/usr/bin/env python3
"""Tests for the NR-V04 covalent-panel Vast launcher's pure JobSpec construction. Pure stdlib."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_covalent_panel import leg_by_id  # noqa: E402
from nrv04_vast_launch import build_jobspec, cofold_cif_s3, units_to_run  # noqa: E402

_BUCKET = "sagemaker-us-east-2-123"


def test_jobspec_targets_ternary_host_and_carries_leg_env():
    spec = build_jobspec(leg_by_id("cov_nr4a1"), 0, "run", "mybranch", _BUCKET)
    assert spec.name == "nrv04cov-cov_nr4a1-s0"
    r = spec.resources
    assert r.gpu == "rtx4090" and r.min_vram_gb == 24 and r.ram_gb == 32 and r.interruptible is True
    assert spec.checkpoint_uri == f"s3://{_BUCKET}/vast/nrv04cov-cov_nr4a1-s0/ckpt"
    e = spec.env
    assert e["LEG_ID"] == "cov_nr4a1" and e["COVALENT"] == "1" and e["COV_RESNUM"] == "551"
    assert e["GIT_BRANCH"] == "mybranch"
    assert e["COFOLD_CIF_S3"].endswith("/nrv04/model_0.cif")     # cov_nr4a1 uses the NR-V04 co-fold
    assert spec.command[0] == "bash" and "git clone" in spec.command[2]


def test_cofold_cif_maps_ligand_to_system():
    assert cofold_cif_s3(leg_by_id("warhead_only"), _BUCKET).endswith("/celastrol/model_0.cif")
    assert cofold_cif_s3(leg_by_id("recruiter_epimer"), _BUCKET).endswith("/nrv04_epimer/model_0.cif")


def test_pilot_only_selects_one_high_abort_unit(monkeypatch):
    monkeypatch.setenv("PILOT_ONLY", "1")
    units = units_to_run()
    assert len(units) == 1 and units[0][0].leg_id == "cov_nr4a1" and units[0][1] == 0
    monkeypatch.setenv("PILOT_ONLY", "0")
    assert len(units_to_run()) == 18                             # full fan-out = 6 legs x 3 seeds


def test_checkpoint_prefixes_are_unique_across_units(monkeypatch):
    monkeypatch.setenv("PILOT_ONLY", "0")
    uris = {build_jobspec(lg, s, "run", "b", _BUCKET).checkpoint_uri for lg, s in units_to_run()}
    assert len(uris) == 18                                       # no checkpoint collisions
