#!/usr/bin/env python3
"""Tests for the NR-V04 covalent-panel Vast launcher's pure JobSpec construction. Pure stdlib."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_covalent_panel import leg_by_id  # noqa: E402
from nrv04_vast_launch import build_jobspec, cofold_prefix_s3, leg_cost_usd, units_to_run  # noqa: E402

_BUCKET = "sagemaker-us-east-2-123"


def test_leg_cost_measured_from_uptime_and_bid():
    # 45 min on a $0.24/hr interruptible bid = 0.75 h x 0.24 = $0.18
    assert leg_cost_usd(45 * 60, 0.24) == 0.18
    assert leg_cost_usd(3600, 0.30) == 0.30
    assert leg_cost_usd(None, 0.24) is None          # missing uptime -> no fabricated price
    assert leg_cost_usd(3600, None) is None          # missing rate -> no fabricated price


def test_jobspec_targets_ternary_host_and_carries_leg_env():
    spec = build_jobspec(leg_by_id("cov_nr4a1"), 0, "run", "mybranch", _BUCKET)
    assert spec.name == "nrv04cov-cov_nr4a1-s0"
    r = spec.resources
    assert r.gpu == "rtx3090" and r.min_vram_gb == 24 and r.ram_gb == 16 and r.interruptible is True
    assert r.min_cuda >= 12.4 and r.interruptible is True        # new-driver hosts only (PTX), cheap interruptible tier
    assert spec.checkpoint_uri == f"s3://{_BUCKET}/vast/nrv04cov-cov_nr4a1-s0/ckpt"
    e = spec.env
    assert e["LEG_ID"] == "cov_nr4a1" and e["COVALENT"] == "1" and e["COV_RESNUM"] == "551"
    assert e["GIT_BRANCH"] == "mybranch"
    assert e["COFOLD_PREFIX_S3"].endswith("/nr4a1/")             # cov_nr4a1 uses the NR-V04 (nr4a1) co-fold system
    assert spec.command[0] == "bash"
    assert "$ENV_TARBALL_URL" in spec.command[2]                 # pre-packed conda env extract (the boot-time fix)
    assert "archive/refs/heads" in spec.command[2]               # repo code via public codeload tarball (no git)
    assert "nrv04_covalent_md.py" in spec.command[2]             # runs the endpoint-MD driver (NAGL charges in-process)


def test_env_tarball_url_injected_only_when_given():
    base = build_jobspec(leg_by_id("cov_nr4a1"), 0, "run", "b", _BUCKET)
    assert "ENV_TARBALL_URL" not in base.env                     # pure path (unit tests) omits it
    withurl = build_jobspec(leg_by_id("cov_nr4a1"), 0, "run", "b", _BUCKET, env_tarball_url="https://x/y")
    assert withurl.env["ENV_TARBALL_URL"] == "https://x/y"


def test_cofold_prefix_maps_ligand_to_system():
    assert cofold_prefix_s3(leg_by_id("warhead_only"), _BUCKET).endswith("/neg_celastrol/")   # free celastrol
    assert cofold_prefix_s3(leg_by_id("recruiter_epimer"), _BUCKET).endswith("/neg_inactive/")  # epimer
    assert cofold_prefix_s3(leg_by_id("cov_nr4a1"), _BUCKET).endswith("/nr4a1/")


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
