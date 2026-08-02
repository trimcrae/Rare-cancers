#!/usr/bin/env python3
"""Guards for the crystal control's panel: it must share the science and share NOTHING that identifies it."""
from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

import selcal_panel as P          # noqa: E402
import selcal_xtal_panel as XP    # noqa: E402


# ---------- everything scientific is the parent panel's ----------------------------------------------------


def test_protocol_is_imported_never_restated():
    assert XP.protocol() == (P.PROD_NS, P.EQUIL_NS, P.MD_REPLICAS)
    src = open(os.path.join(MOD, "selcal_xtal_panel.py")).read()
    for forbidden in ("PROD_NS =", "EQUIL_NS =", "ALPHA =", "MD_REPLICAS ="):
        assert forbidden not in src, "%s must have one home, in selcal_panel" % forbidden


def test_arms_and_direction_are_the_parent_panels():
    assert [a.arm_id for a in XP.arms()] == [a.arm_id for a in P.ARMS]
    assert XP.predicted_more_stable_arm() == P.PREDICTED_MORE_STABLE_ARM


def test_leg_env_carries_the_parent_protocol_verbatim():
    e = XP.leg_env(XP.arms()[0], "c02", 1)
    assert (e["PROD_NS"], e["EQUIL_NS"]) == (str(P.PROD_NS), str(P.EQUIL_NS))
    assert e["COVALENT"] == "0", "no arm of this pair forms an adduct; setting it would fabricate chemistry"
    assert e["TARGET"] == XP.arms()[0].gene


# ---------- and nothing that identifies the lane is shared --------------------------------------------------


def test_panel_name_and_label_prefix_are_disjoint_from_the_parent():
    assert XP.PANEL != P.PANEL if hasattr(P, "PANEL") else True
    assert XP.LABEL_PREFIX != P.LABEL_PREFIX
    assert not XP.LABEL_PREFIX.startswith(P.LABEL_PREFIX)
    assert not P.LABEL_PREFIX.startswith(XP.LABEL_PREFIX)


def test_a_crystal_leg_declares_its_own_provenance():
    e = XP.leg_env(XP.arms()[0], "c02", 1)
    assert e["PANEL"] == XP.PANEL
    assert e["MODEL_SOURCE"] == XP.MODEL_SOURCE
    assert e["CRYSTAL_COPY_ID"] == "c02"


def test_the_gate_key_is_the_copy_index_and_is_reversible():
    """The frozen gate collapses on COFOLD_MODEL_SEED; the copy id becomes that integer, losslessly."""
    e = XP.leg_env(XP.arms()[0], "c07", 0)
    assert e["COFOLD_MODEL_SEED"] == "7"
    assert XP.copy_id(XP.copy_index("c07")) == "c07"


def test_a_malformed_copy_id_raises_rather_than_defaulting():
    with pytest.raises(ValueError):
        XP.copy_index("seed_3")


def test_leg_id_names_the_copy_not_a_seed():
    e = XP.leg_env(XP.arms()[1], "c04", 1)
    assert e["LEG_ID"] == "selcal_smarca4__c04"


# ---------- units -------------------------------------------------------------------------------------------


def test_units_come_only_from_the_census_counts():
    u = XP.enumerate_units({"selcal_smarca2": 4, "selcal_smarca4": 4})
    assert len(u) == 4 * 2 * len(P.MD_REPLICAS)
    assert {c for _, c, _ in u} == {"c01", "c02", "c03", "c04"}


def test_an_arm_with_no_usable_copy_contributes_no_units():
    u = XP.enumerate_units({"selcal_smarca2": 3, "selcal_smarca4": 0})
    assert {a.arm_id for a, _, _ in u} == {"selcal_smarca2"}


def test_unit_names_and_prefixes_are_unique_per_unit():
    arm = XP.arms()[0]
    names = {XP.unit_name(arm, c, r) for c in ("c01", "c02") for r in P.MD_REPLICAS}
    assert len(names) == 2 * len(P.MD_REPLICAS)
    assert XP.unit_prefix_s3(arm, "b", "c01") != XP.unit_prefix_s3(arm, "b", "c02")


def test_the_unit_prefix_is_pinned_not_globbed():
    assert "*" not in XP.unit_prefix_s3(XP.arms()[0], "b", "c01")


# ---------- foreign records ----------------------------------------------------------------------------------


def test_a_foreign_record_is_returned_not_dropped():
    ours, foreign = XP.partition_legs([{"PANEL": XP.PANEL}, {"PANEL": "selcal_sensitivity_control"}, {}])
    assert len(ours) == 1 and len(foreign) == 2, "a silently dropped foreign record hides a prefix collision"


def test_provenance_is_read_from_the_record_not_a_filename():
    assert XP.is_crystal_leg({"model_source": XP.MODEL_SOURCE}) is True
    assert XP.is_crystal_leg({"leg_id": "selxtal-smarca2-c01-r0"}) is False
