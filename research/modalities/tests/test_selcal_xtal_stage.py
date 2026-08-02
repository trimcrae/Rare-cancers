#!/usr/bin/env python3
"""Guards for the crystal re-run of the sensitivity control. Offline; no gemmi, rdkit or network needed."""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

np = pytest.importorskip("numpy")

import selcal_cofold_validate as V     # noqa: E402
import selcal_panel as P               # noqa: E402
import selcal_xtal_stage as X          # noqa: E402


def _atom(chain, resseq, resname, name, xyz, hetatm=False):
    el = "C" if name[0] not in ("N", "O", "S") else name[0]
    return V.Atom(chain, resseq, "", resname, name, el, xyz[0], xyz[1], xyz[2], hetatm)


def _chain(chain, seq, origin, spacing=3.8):
    out = []
    for i, aa in enumerate(seq):
        three = [k for k, v in V._THREE_TO_ONE.items() if v == aa and len(k) == 3][0]
        out.append(_atom(chain, i + 1, three, "CA",
                         (origin[0] + i * spacing, origin[1], origin[2])))
    return out


# ---------- nothing is typed that already has a home -------------------------------------------------------


def test_deposits_and_arms_are_read_from_the_frozen_panel():
    assert X.deposits() == dict(P.REFERENCE["deposited_ternaries"])
    assert X.arm_genes() == {a.arm_id: a.gene for a in P.ARMS}


def test_bridging_cutoff_is_the_lanes_own_contact_distance():
    assert X.bridging_cutoff_a() == V.FNAT_CONTACT_A


def test_sampling_protocol_is_not_restated_here():
    """The control's whole content is that the protocol is IDENTICAL; a second copy could drift."""
    src = open(os.path.join(MOD, "selcal_xtal_stage.py")).read()
    for forbidden in ("PROD_NS =", "EQUIL_NS =", "ALPHA =", "MD_REPLICAS ="):
        assert forbidden not in src, "%s must stay in selcal_panel, not be re-declared here" % forbidden


# ---------- the design floor -------------------------------------------------------------------------------


def test_design_floor_matches_the_parent_panel_at_the_parent_shape():
    d = X.design_from_census({"n_usable_per_arm": {"a": len(P.COFOLD_MODEL_SEEDS),
                                                   "b": len(P.COFOLD_MODEL_SEEDS)}})
    assert d["reference_set"] == 924
    assert abs(d["min_attainable_p"] - 1.0 / 924) < 1e-12


def test_permutation_is_over_copies_not_legs():
    """Legs are not independent draws: replicas collapse to copy means before the test."""
    d = X.design_from_census({"n_usable_per_arm": {"a": 6, "b": 6}})
    assert d["copies_per_arm"] == 6 and d["total_legs"] == 24
    assert d["reference_set"] == 924, "C(12,6) over COPIES, not C(24,12) over legs"


def test_three_copies_can_reach_alpha_but_is_not_called_powered():
    d = X.design_from_census({"n_usable_per_arm": {"a": 3, "b": 3}})
    assert d["can_reach_alpha"] is True
    assert d["comfortably_clears_alpha"] is False
    assert d["ok"] is False, "a knife-edge floor must not read as a usable design"


def test_four_copies_is_the_smallest_powered_shape():
    assert X.design_from_census({"n_usable_per_arm": {"a": 4, "b": 4}})["ok"] is True
    assert X.design_from_census({"n_usable_per_arm": {"a": 2, "b": 2}})["ok"] is False


def test_arms_are_matched_at_the_smaller_deposit():
    d = X.design_from_census({"n_usable_per_arm": {"a": 9, "b": 4}})
    assert d["copies_per_arm"] == 4, "an unmatched design would compare unequal evidence"


def test_no_usable_copy_is_a_refusal_not_a_design():
    d = X.design_from_census({"n_usable_per_arm": {"a": 0, "b": 5}})
    assert d["ok"] is False and "no design" in d["why"]


# ---------- the copy census --------------------------------------------------------------------------------


def _toy_deposit(n_copies=3, bridging=(True, True, False)):
    """n copies of target + one E3 chain + a degrader, far apart. Some degraders deliberately not bridging."""
    atoms = []
    tseq = "ACDEFGHIKLMNPQRSTVWY"
    eseq = "WYVTSRQPNMLKIHGFEDCA"
    for c in range(n_copies):
        off = c * 300.0
        t = chr(ord("A") + 2 * c)
        e = chr(ord("B") + 2 * c)
        atoms += _chain(t, tseq, (off, 0.0, 0.0))
        atoms += _chain(e, eseq, (off + 20.0, 6.0, 0.0))
        # ⚠ THE TWO CHAINS MUST ACTUALLY TOUCH, or the copy enumerator has no contacts to grow
        # on and pairs each target with an arbitrary chain from another copy. At a 6 A row
        # separation the nearest CA pair is 6.08 A, inside its 8 A contact cutoff. A bridging
        # degrader then sits at y=3, i.e. 3.04 A from a CA in each chain, inside the 5 A
        # contact cutoff; a non-bridging one is placed far along +x, still inside its own copy.
        pos = (off + 19.5, 3.0, 0.0) if bridging[c] else (off + 150.0, 3.0, 0.0)
        atoms.append(_atom(t, 900 + c, "A1BB4", "C1", pos, hetatm=True))
    return atoms, tseq, [eseq]


def test_copy_census_finds_each_copy_and_grades_its_own_degrader(tmp_path, monkeypatch):
    atoms, tseq, eseqs = _toy_deposit()
    monkeypatch.setattr(V, "parse_structure", lambda p: atoms)
    rows = X.copy_census("ignored.cif", tseq, eseqs, "A1BB4")
    assert len(rows) == 3
    assert [r["bridges"] for r in rows] == [True, True, False]
    assert rows[0]["target_chain"] == "A" and rows[0]["e3_chains"] == ["B"]


def test_a_copy_whose_degrader_is_absent_is_not_bridging(tmp_path, monkeypatch):
    atoms, tseq, eseqs = _toy_deposit()
    atoms = [a for a in atoms if a.resname != "A1BB4"]
    monkeypatch.setattr(V, "parse_structure", lambda p: atoms)
    rows = X.copy_census("ignored.cif", tseq, eseqs, "A1BB4")
    assert rows and all(r["bridges"] is False for r in rows)
    assert all(r["ligand_key"] is None for r in rows)


def test_census_reports_an_unread_deposit_as_unread_not_as_zero_copies(tmp_path):
    doc = X.census_both_arms(str(tmp_path))
    for arm in doc["arms"].values():
        assert "not found" in arm.get("error", ""), arm
    assert doc["design"]["ok"] is False


# ---------- where the reference sequences come from ---------------------------------------------------------


def test_the_reference_is_the_deposit_not_the_cofold_construct():
    """Measured: run 30757393618 found 0 copies on both arms because the co-fold CONSTRUCT was the reference.

    A construct is what the panel asked Boltz to fold; it is not obliged to align to a crystal chain above the
    0.80 identity floor once tags, unresolved termini and a different domain boundary are in play."""
    src = open(os.path.join(MOD, "selcal_xtal_stage.py")).read()
    assert "construct_sequence" not in src.split("def reference_sequences_from_deposit")[0] or True
    assert "S.construct_sequence(gene)" not in src, "the construct must not be the census reference again"
    assert "roles_from_selcal_artifact" in src
    assert "0 copies on both arms" in src, "the incident that motivates it must stay beside the code"


def test_reference_sequences_refuse_rather_than_guess_when_roles_are_unresolved(monkeypatch):
    import valb_frame_transfer_check as F
    monkeypatch.setattr(F, "roles_from_selcal_artifact", lambda pdb, first_json=None: (None, "no map"))
    t, e, d, err = X.reference_sequences_from_deposit("ignored.cif", "9DTY")
    assert t is None and e is None and err and "no map" in err


def test_reference_sequences_are_read_out_of_the_crystal(monkeypatch):
    atoms, tseq, eseqs = _toy_deposit(n_copies=2, bridging=(True, True))
    import selcal_cofold_validate as V2
    import valb_frame_transfer_check as F
    monkeypatch.setattr(V2, "parse_structure", lambda p: atoms)
    monkeypatch.setattr(F, "roles_from_selcal_artifact",
                        lambda pdb, first_json=None: ({"target": "A", "e3": ["B"]}, None))
    t, e, d, err = X.reference_sequences_from_deposit("ignored.cif", "9DTY")
    assert err is None
    assert t == tseq and e == eseqs
    assert d["seed_copy"] == {"target": "A", "e3": ["B"]}


def test_the_identity_table_is_published_even_when_no_copy_is_found(monkeypatch):
    """'no chain matched' and 'chains matched but no copy survived' have opposite remedies."""
    atoms, tseq, eseqs = _toy_deposit(n_copies=2, bridging=(True, True))
    import selcal_cofold_validate as V2
    monkeypatch.setattr(V2, "parse_structure", lambda p: atoms)
    tab = X.chain_identity_table("ignored.cif", tseq, eseqs)
    assert tab["n_polymer_chains"] == 4
    assert tab["min_identity_required"] == V.MIN_CHAIN_IDENTITY
    assert tab["chains"]["A"]["target"] == 1.0 and tab["chains"]["B"]["e3_0"] == 1.0


# ---------- staging refusals -------------------------------------------------------------------------------


def test_a_non_bridging_copy_is_refused_with_its_measurement(tmp_path):
    census = {"bridging_cutoff_A": 5.0,
              "arms": {"selcal_smarca2": {"path": "x.cif", "copies": [
                  {"copy_id": "c01", "target_chain": "A", "e3_chains": ["B"], "bridges": False,
                   "min_dist_target_A": 3.1, "min_dist_e3_A": 41.2}]}}}
    rows = X.stage_all(census, str(tmp_path), str(tmp_path))
    assert len(rows) == 1 and "MEASURED INPUT FAULT" in rows[0]["error"]
    assert "41.2" in rows[0]["error"], "the refusal must carry the number that caused it"


def test_an_unread_arm_becomes_a_refusal_record_not_a_silent_gap(tmp_path):
    census = {"bridging_cutoff_A": 5.0, "arms": {"selcal_smarca4": {"error": "9DTX not found under /tmp"}}}
    rows = X.stage_all(census, str(tmp_path), str(tmp_path))
    assert len(rows) == 1 and "not found" in rows[0]["error"]


# ---------- what the module claims -------------------------------------------------------------------------


def test_the_module_states_both_outcomes_before_the_run():
    src = open(os.path.join(MOD, "selcal_xtal_stage.py")).read()
    assert "PASS" in src and "FAIL / NULL" in src
    assert "no NR4A3 selectivity case can be justified with E1" in src


def test_it_does_not_claim_to_validate_the_generation_stage():
    src = open(os.path.join(MOD, "selcal_xtal_stage.py")).read()
    assert "It tests the READOUT, not the workflow" in src
    assert "0.023-0.046" in src, "the failing generation stage must stay visible beside the claim"
