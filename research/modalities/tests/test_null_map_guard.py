"""Regression test for the NULL-MAP GUARD (reviewer 2026-07-17 Option-4 disposition).

The verified failure mode: a pair differing ONLY by stereochemistry (identical 2D constitution) is a NULL
alchemical transformation under a complete single-topology map — identical force-field parameters, every atom
mapped 1:1 — so no real ddG can be recovered. This test freezes that finding permanently: any such pair MUST
fail setup, while a genuine constitutional edge (Wurz cmpd1->cmpd4, a linker pyridine N->CH) MUST pass. Reads the
REAL frozen JSONs so a drift in either edge is caught here.

Keeps PROTAC 2 -> cis-PROTAC 2 (the retired epimer edge) as the canonical stereo-only fixture.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nr4a3_ternary_fep as eng  # noqa: E402

pytest.importorskip("rdkit")

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _frozen(name):
    return json.load(open(os.path.join(MOD, name)))


def test_epimer_stereo_only_edge_is_forbidden():
    """PROTAC 2 -> cis-PROTAC 2 (pure hydroxyproline stereocenter inversion) MUST abort setup."""
    d = _frozen("ternary-calib-epimer-frozen.json")
    sa, sb = d["calib_hi"]["smiles"], d["calib_lo"]["smiles"]
    with pytest.raises(SystemExit):
        eng.assert_constitutional_edge(sa, sb)


def test_identity_edge_is_forbidden():
    """A trivially identical A==B edge is also a null morph and must abort."""
    with pytest.raises(SystemExit):
        eng.assert_constitutional_edge("c1ccccc1", "c1ccccc1")


def test_wurz_constitutional_edge_is_allowed():
    """Wurz cmpd1 -> cmpd4 (pyridine linker N -> CH) is a genuine constitutional edge and MUST pass the guard."""
    d = _frozen("wurz-calib-frozen.json")
    sa, sb = d["calib_hi"]["smiles"], d["calib_lo"]["smiles"]
    r = eng.assert_constitutional_edge(sa, sb)
    assert r["constitutional_edge"] is True
    assert r["flat_a"] != r["flat_b"]        # differ even with stereo removed => constitutional


def test_wurz_frozen_edge_is_a_single_N_to_C_swap():
    """Guard against silent drift of the frozen Wurz edge away from the reviewer-specified N->CH transform."""
    d = _frozen("wurz-calib-frozen.json")
    v = d["validation"]
    assert v["genuine_constitutional_edge"] is True
    assert v["single_N_to_C_swap"] is True
    assert v["delta_N"] == -1 and v["delta_C"] == 1
    assert d["preregistered_target"]["assay"].upper().find("SPR") >= 0
    assert abs(d["preregistered_target"]["ddG_coop_exp_kcal_per_mol"] - 0.94) < 0.05
