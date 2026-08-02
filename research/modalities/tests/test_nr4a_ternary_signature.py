#!/usr/bin/env python3
"""Guards for the NR4A applier — the module that may only speak once the descriptor has been validated."""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, MOD)

pytest.importorskip("numpy")

import nr4a_ternary_signature as N     # noqa: E402


def _validated(tmp_path, recovered=True, checked=True):
    p = tmp_path / "selcal-interface-signature.json"
    p.write_text(json.dumps({"known_answer": {"checked": checked, "recovered": recovered,
                                              "n_matching_positions": 1 if recovered else 0,
                                              "positions": [{"smarca2": "GLN1469"}],
                                              "sentence": "…", "why": "not run"}}))
    return str(p)


# ---------- the gate ------------------------------------------------------------------------------------------


def test_an_absent_validation_artifact_is_a_refusal(tmp_path):
    ok, why = N.descriptor_is_validated(str(tmp_path / "nope.json"))
    assert ok is False and "has not been put to its known-answer test" in why


def test_a_descriptor_that_failed_its_known_answer_may_not_be_used(tmp_path):
    ok, why = N.descriptor_is_validated(_validated(tmp_path, recovered=False))
    assert ok is False and "did NOT recover" in why


def test_a_check_that_never_ran_is_not_a_pass(tmp_path):
    ok, why = N.descriptor_is_validated(_validated(tmp_path, checked=False))
    assert ok is False and "did not run" in why


def test_a_recovered_known_answer_opens_the_gate(tmp_path):
    ok, detail = N.descriptor_is_validated(_validated(tmp_path))
    assert ok is True and detail["n"] == 1


def test_run_refuses_before_it_reads_any_structure(tmp_path):
    doc = N.run({"NR4A3": "/nowhere/a.cif"}, "A", ["B"], validated_path=str(tmp_path / "absent.json"))
    assert doc["descriptor_validated"] is False
    assert doc["sentence"].startswith("REFUSED")
    assert "signatures" not in doc, "a refusal must not have read structures anyway"


# ---------- discrimination requires EVERY comparator ---------------------------------------------------------


def _sig(seq, polar_positions):
    """A signature whose residue i has a polar contact iff i is in `polar_positions`."""
    keys = [["A", 100 + i, ""] for i in range(len(seq))]
    contacts = {}
    for i, aa in enumerate(seq):
        contacts["%s%d" % (aa * 3, 100 + i)] = {
            "resname": aa * 3, "resseq": 100 + i, "icode": "", "min_dist_A": 3.0, "n_contacts": 2,
            "n_polar_contacts": 1 if i in polar_positions else 0,
            "polar_contacts": ([{"target_atom": "NE2", "distance_A": 2.9}] if i in polar_positions else [])}
    return {"target_sequence": seq, "target_sequence_len": len(seq), "residue_keys": keys,
            "contacts": contacts, "roles": {"target": "A", "e3": ["B"]}}


def test_a_position_must_discriminate_against_every_comparator():
    seq = "ACDEFGHIKL"
    focus = _sig(seq, {2, 5})
    # NR4A1 lacks position 2 and 5; NR4A2 HAS position 5. Only 2 discriminates against both.
    comps = {"NR4A1": _sig(seq, set()), "NR4A2": _sig(seq, {5})}
    res = N.discriminating_positions(focus, comps)
    assert res["n_discriminating"] == 1
    assert res["discriminating"] == ["DDD102"]
    assert "EVERY comparator" in res["_rule"]


def test_no_discriminating_position_is_reported_as_such_not_as_an_error():
    seq = "ACDEFGHIKL"
    focus = _sig(seq, {3})
    res = N.discriminating_positions(focus, {"NR4A1": _sig(seq, {3}), "NR4A2": _sig(seq, {3})})
    assert res["n_discriminating"] == 0 and "error" not in res


def test_a_failed_pairwise_comparison_propagates_rather_than_being_skipped():
    seq = "ACDEFGHIKL"
    res = N.discriminating_positions(_sig(seq, {1}), {"NR4A1": {"error": "unread"}})
    assert res.get("error") and "NR4A1" in res["error"]


# ---------- the whole run -------------------------------------------------------------------------------------


def test_a_missing_arm_is_a_refusal_not_a_comparison(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "signature_of", lambda p, t, e: {"error": "unreadable"})
    doc = N.run({"NR4A3": "a.cif"}, "A", ["B"], validated_path=_validated(tmp_path))
    assert doc["sentence"].startswith("REFUSED")
    assert "Unread is not absent" in doc["sentence"]


def test_the_negative_result_is_stated_plainly(tmp_path, monkeypatch):
    seq = "ACDEFGHIKL"
    monkeypatch.setattr(N, "signature_of", lambda p, t, e: _sig(seq, {3}))
    doc = N.run({"NR4A3": "a.cif", "NR4A1": "b.cif", "NR4A2": "c.cif"}, "A", ["B"],
                validated_path=_validated(tmp_path))
    assert doc["descriptor_validated"] is True
    assert doc["result"]["n_discriminating"] == 0
    assert "cannot be justified from it" in doc["sentence"]
    assert "agrees with the paper" in doc["sentence"]


def test_a_positive_result_is_labelled_a_hypothesis_not_a_demonstration(tmp_path, monkeypatch):
    seq = "ACDEFGHIKL"
    sigs = {"NR4A3": _sig(seq, {4}), "NR4A1": _sig(seq, set()), "NR4A2": _sig(seq, set())}
    monkeypatch.setattr(N, "signature_of", lambda p, t, e: sigs[os.path.basename(p).split(".")[0].upper()])
    doc = N.run({"NR4A3": "nr4a3.cif", "NR4A1": "nr4a1.cif", "NR4A2": "nr4a2.cif"}, "A", ["B"],
                validated_path=_validated(tmp_path))
    assert doc["result"]["n_discriminating"] == 1
    assert "structural HYPOTHESIS" in doc["sentence"]
    assert "not a demonstration of selectivity" in doc["sentence"]
    assert "0.023-0.046" in doc["sentence"], "the structures' own provenance must travel with the claim"


def test_the_structure_provenance_is_always_recorded(tmp_path):
    doc = N.run({}, "A", ["B"], validated_path=_validated(tmp_path))
    assert "0.023-0.046" in doc["structure_provenance"]


def test_the_module_states_the_honest_prior():
    src = open(os.path.join(MOD, "nr4a_ternary_signature.py")).read()
    assert "the expected outcome here is NO discriminating contact" in src
    assert "did not provide evidence for NR4A3-selective ternary geometry" in src


# ---------- structure selection must never hand over the control ----------------------------------------------


def _write(tmp_path, rel):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("data_x\n")
    return p


def test_the_crbn_control_is_never_taken_as_the_nr4a3_ternary(tmp_path, monkeypatch, capsys):
    """`boltz_results_nr4a3-ternary-control` contains the token 'nr4a3'. Handing it over would make every
    number afterwards about the wrong structure."""
    _write(tmp_path, "boltz_results_nr4a3-ternary-control/predictions/c/c_model_0.cif")
    _write(tmp_path, "boltz_results_nr4a3-ternary-protac/predictions/nr4a3/nr4a3_model_0.cif")
    _write(tmp_path, "boltz_results_nr4a3-ternary-protac/predictions/nr4a1/nr4a1_model_0.cif")
    _write(tmp_path, "boltz_results_nr4a3-ternary-protac/predictions/nr4a2/nr4a2_model_0.cif")
    out = tmp_path / "out.json"
    rc = N.main(["--root", str(tmp_path), "--recursive", "--target-chain", "A", "--e3-chains", "B",
                 "--validated", _validated(tmp_path), "--out", str(out)])
    doc = json.loads(out.read_text())
    # The control path must not appear as any paralogue's chosen structure.
    chosen = doc.get("structures") or {}
    assert all("control" not in v for v in chosen.values()), chosen
    assert rc in (0, 5)


def test_zero_or_ambiguous_candidates_is_a_refusal_not_a_preference(tmp_path):
    _write(tmp_path, "boltz_results_nr4a3-ternary-control/predictions/c/c_model_0.cif")
    out = tmp_path / "out.json"
    rc = N.main(["--root", str(tmp_path), "--recursive", "--target-chain", "A", "--e3-chains", "B",
                 "--validated", _validated(tmp_path), "--out", str(out)])
    assert rc == 5
    doc = json.loads(out.read_text())
    assert "not guessing" in doc["error"]
    assert set(doc["unresolved"]) == {"NR4A3", "NR4A1", "NR4A2"}
