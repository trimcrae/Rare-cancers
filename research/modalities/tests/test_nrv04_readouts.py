#!/usr/bin/env python3
"""Tests for the frozen NR-V04 covalent-panel readouts + GO/NO-GO verdict. Pure stdlib."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_readouts import (  # noqa: E402
    contact_count, covnoncov_sensitivity, interface_rmsd_stable, lys_presentation, panel_verdict,
    recruitment, rmsd,
)


def test_contact_count_within_cutoff():
    a = [(0, 0, 0), (10, 10, 10)]
    b = [(1, 0, 0), (0, 2, 0)]                      # first a-atom within 4.5 of both b-atoms; second far
    assert contact_count(a, b) == 2
    assert contact_count([(0, 0, 0)], [(100, 0, 0)]) == 0


def test_rmsd_and_interface_stability():
    ref = [(0, 0, 0), (1, 1, 1)]
    assert rmsd(ref, ref) == 0.0
    stable_frames = [[(0.1, 0, 0), (1, 1, 1)]] * 5   # tiny drift -> plateau < 4 A
    r = interface_rmsd_stable(stable_frames, ref)
    assert r["stable"] is True and r["plateau_A"] < 4.0
    drift = [[(10, 0, 0), (11, 1, 1)]] * 5           # big displacement -> not stable
    assert interface_rmsd_stable(drift, ref)["stable"] is False


def test_recruitment_fraction_threshold():
    assert recruitment([5, 3, 4, 0])["recruited"] is True        # 3/4 frames in contact
    assert recruitment([0, 0, 1, 0])["recruited"] is False       # 1/4 -> below 0.5
    assert recruitment([2, 2])["mean_contacts"] == 2.0


def test_lys_presentation_distribution():
    frames = [[(0, 0, 0), (5, 0, 0)], [(3, 0, 0)]]
    out = lys_presentation(frames, catalytic_proxy=(0, 0, 0))
    assert out["min_A"] == 0.0 and out["max_A"] == 3.0
    assert lys_presentation([[]], (0, 0, 0))["min_A"] is None


def test_sensitivity_detects_flip():
    rec = {"recruited": True, "mean_contacts": 40}
    non = {"recruited": True, "mean_contacts": 33}
    assert covnoncov_sensitivity(rec, non)["covalency_swamps"] is False   # both recruited -> no swamp
    non_flip = {"recruited": False, "mean_contacts": 0}
    assert covnoncov_sensitivity(rec, non_flip)["covalency_swamps"] is True


def _passing_panel():
    return {
        "cov_nr4a1": {"interface": {"stable": True}, "recruitment": {"recruited": True, "mean_contacts": 40}},
        "noncov_nr4a1": {"recruitment": {"recruited": True, "mean_contacts": 34}},
        "warhead_only": {"recruitment": {"recruited": False, "mean_contacts": 1}},
        "recruiter_epimer": {"recruitment": {"recruited": False, "mean_contacts": 0}},
        "cov_c551a": {"recruitment": {"recruited": True, "mean_contacts": 22}},   # weaker than cov (40)
        "sensitivity": {"covalency_swamps": False},
    }


def test_panel_verdict_go_when_all_criteria_met():
    v = panel_verdict(_passing_panel())
    assert v["go"] is True


def test_panel_verdict_flags_each_failure():
    p = _passing_panel(); p["sensitivity"] = {"covalency_swamps": True}
    v = panel_verdict(p)
    assert v["go"] is False and any("SWAMPS" in r for r in v["reasons"])

    p = _passing_panel(); p["warhead_only"]["recruitment"]["recruited"] = True
    assert panel_verdict(p)["go"] is False

    p = _passing_panel(); p["cov_c551a"]["recruitment"]["mean_contacts"] = 55   # not weaker than cov (40)
    assert panel_verdict(p)["go"] is False
