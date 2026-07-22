#!/usr/bin/env python3
"""Tests for the frozen NR-V04 covalent-panel manifest + per-leg spec builders. Pure stdlib."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nrv04_covalent_panel import (  # noqa: E402
    PANEL, SENSITIVITY_PAIR, enumerate_units, leg_by_id, leg_env, unit_name,
)


def test_panel_has_the_six_frozen_legs():
    ids = [lg.leg_id for lg in PANEL]
    assert ids == ["cov_nr4a1", "noncov_nr4a1", "cov_c551a", "warhead_only",
                   "recruiter_active", "recruiter_epimer"]
    # no paralogue legs (Leg 0: Cys unique to NR4A1 -> nothing covalent to model there)
    assert not any("nr4a2" in i or "nr4a3" in i for i in ids)


def test_covalent_flags_and_mutation():
    assert leg_by_id("cov_nr4a1").covalent is True
    assert leg_by_id("noncov_nr4a1").covalent is False           # the sensitivity partner
    assert leg_by_id("cov_c551a").covalent is False and leg_by_id("cov_c551a").mutation == "C551A"
    assert leg_by_id("warhead_only").ligand == "celastrol" and leg_by_id("warhead_only").covalent is True
    assert leg_by_id("recruiter_epimer").ligand == "nrv04_epimer" and leg_by_id("recruiter_epimer").env == "binary_vhl"


def test_enumerate_units_is_legs_times_seeds():
    units = enumerate_units()
    assert len(units) == 6 * 3
    names = {unit_name(lg, s) for lg, s in units}
    assert len(names) == 18                                       # all unit names distinct (no ckpt collision)
    assert "nrv04cov-cov_nr4a1-s0" in names


def test_leg_env_covalent_carries_restraint_atoms():
    e = leg_env(leg_by_id("cov_nr4a1"), 0)
    assert e["COVALENT"] == "1" and e["COV_LIG_ATOM"] == "C6" and e["COV_RESNUM"] == "551"
    assert e["LEG_ID"] == "cov_nr4a1" and e["SEED"] == "0"
    n = leg_env(leg_by_id("noncov_nr4a1"), 1)
    assert n["COVALENT"] == "0" and "COV_LIG_ATOM" not in n       # noncov: no restraint atoms


def test_sensitivity_pair_points_at_cov_and_noncov():
    assert SENSITIVITY_PAIR == ("cov_nr4a1", "noncov_nr4a1")
    assert leg_by_id(SENSITIVITY_PAIR[0]).covalent != leg_by_id(SENSITIVITY_PAIR[1]).covalent
