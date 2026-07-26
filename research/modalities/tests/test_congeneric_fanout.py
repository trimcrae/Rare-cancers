"""Unit tests for the STEP 1 fan-out core (congeneric_fanout.py) + the Vast launcher's pure jobspec build.

These gate the decisions that a fan-out cannot get wrong silently: which units are launched, which are
deliberately excluded (and why), that no map edge is dropped, that the ligand SMILES the engine parameterizes
match the frozen map, and that the thermodynamic-cycle bookkeeping signs edges correctly.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import congeneric_fanout as cf  # noqa: E402


# ---- unit enumeration -------------------------------------------------------------------------------------

def test_tranche1_covers_every_map_edge_exactly_once():
    units = cf.default_units()
    edges = [e["edge_id"] for e in cf.load_map()["edges"]]
    assert [u["edge_id"] for u in units] == edges
    assert len(units) == len(set(u["unit_id"] for u in units)) == 19


def test_tranche1_is_charge_conserving_only():
    assert all(not u["charge_changing"] for u in cf.default_units())


def test_charge_changing_legs_are_enumerated_but_disjoint_from_tranche1():
    t1 = {u["unit_id"] for u in cf.default_units()}
    t2 = {u["unit_id"] for u in cf.charge_changing_units()}
    assert t2 and not (t1 & t2)
    assert all(u["charge_changing"] for u in cf.charge_changing_units())
    # the map declares 27 microstate legs in total; tranche 1 + tranche 2 must account for all of them
    total = sum(len(e.get("microstate_legs") or []) for e in cf.load_map()["edges"])
    assert len(t1) + len(t2) == total == 27


def test_no_edge_is_silently_dropped(tmp_path):
    """An edge with only charge-changing legs must ABORT enumeration, not vanish from the fan-out."""
    m = cf.load_map()
    m["edges"][0]["microstate_legs"] = [{"leg_id": "neutral__anionic", "state_a": "neutral",
                                         "state_b": "anionic_x", "net_charge_change": -1,
                                         "charge_change": True}]
    p = tmp_path / "map.json"
    p.write_text(json.dumps(m))
    with pytest.raises(ValueError, match="NO charge-conserving"):
        cf.default_units(map_path=str(p))


def test_smiles_registry_fails_closed_on_drift(tmp_path):
    s = cf.load_series()
    s["compounds"][0]["smiles"] = "CCO"
    p = tmp_path / "series.json"
    p.write_text(json.dumps(s))
    with pytest.raises(ValueError, match="SMILES drift"):
        cf.smiles_registry(series_path=str(p))


def test_comparator_scaffolds_are_not_in_the_rbfe_registry():
    """denovo_401 and its analogues are a DIFFERENT scaffold — the common-mode assumption is invalid across
    scaffolds, so they get ABFE, never an RBFE edge into the indole series."""
    reg = cf.smiles_registry()
    assert not [k for k in reg if k.startswith("cw_cmp_")]
    units = cf.default_units()
    assert not [u for u in units if "denovo" in u["ligand_a"] or "denovo" in u["ligand_b"]]


def test_is_charge_changing_detects_charge_from_any_signal():
    assert cf.is_charge_changing({"charge_change": True})
    assert cf.is_charge_changing({"net_charge_change": -1})
    assert cf.is_charge_changing({"state_a": "neutral", "state_b": "cationic_ammonium"})
    assert not cf.is_charge_changing({"state_a": "neutral", "state_b": "neutral_acid",
                                      "net_charge_change": 0, "charge_change": False})


def test_unit_ids_are_stable_for_the_primary_frame_and_qualified_otherwise():
    assert cf.unit_id("e_x", "neutral__neutral") == "e_x__neutral__neutral"
    other = cf.unit_id("e_x", "neutral__neutral", "nr4a1", "nr4a1_antitarget:matched_open_frame")
    assert other == "e_x__neutral__neutral__nr4a1_matched_open_frame"


def test_frame_units_reuse_tranche1_edges_on_another_receptor():
    fu = cf.frame_units("nr4a1", "nr4a1_antitarget:matched_open_frame")
    assert len(fu) == len(cf.default_units())
    assert all(u["receptor"] == "nr4a1" for u in fu)
    assert not ({u["unit_id"] for u in fu} & {u["unit_id"] for u in cf.default_units()})


# ---- engine wiring ----------------------------------------------------------------------------------------

def test_unit_env_shapes_the_two_alchemical_legs():
    u = cf.default_units()[0]
    cx = cf.unit_env(u, "complex")
    assert cx["MODE"] == "splittest" and cx["RBFE_TINY"] == "0" and cx["OPENMM_REQUIRE_CUDA"] == "1"
    assert cx["LIGAND_A"] == u["ligand_a"] and cx["LIGAND_B"] == u["ligand_b"]
    assert cf.unit_env(u, "reduce")["MODE"] == "reduce"
    assert cf.unit_env(u, "reduce")["OPENMM_REQUIRE_CUDA"] == "0"
    with pytest.raises(ValueError):
        cf.unit_env(u, "bogus")


def test_result_and_checkpoint_keys_are_per_unit_and_disjoint():
    units = cf.default_units()
    rk = [cf.result_key(u, "p") for u in units]
    ck = [cf.checkpoint_prefix(u, "p") for u in units]
    assert len(set(rk)) == len(set(ck)) == len(units)
    assert not set(rk) & set(ck)


# ---- cycle bookkeeping ------------------------------------------------------------------------------------

def _closed_ddg():
    """A ddG set in which every declared cycle closes exactly, built from a per-node potential (so the signs
    are right by construction, whichever direction each edge is written in)."""
    pot = {"zaienne_cmpd19": 0.0, "cw_ev_5nh2": 1.5, "cw_ms_5acetamido_ester": -0.4, "cw_ev_5oh": 0.8,
           "cw_ev_5opropargyl": -1.1, "cw_ms_free_acid": 2.2, "cw_bio_primary_amide": 0.3}
    out = {}
    for e in cf.load_map()["edges"]:
        if e["node_a"] in pot and e["node_b"] in pot:
            out[e["edge_id"]] = pot[e["node_b"]] - pot[e["node_a"]]
    return out


def test_cycles_close_for_a_self_consistent_ddg_set():
    res = cf.cycle_closure(_closed_ddg())
    assert len(res) == 3
    for c in res:
        assert c["status"] == "ok", c
        assert abs(c["sum_kcal"]) < 1e-6


def test_a_broken_edge_is_reported_as_a_violation():
    ddg = _closed_ddg()
    ddg["e_cw_ev_5oh__cw_ev_5opropargyl"] += 4.0
    res = {c["cycle_id"]: c for c in cf.cycle_closure(ddg)}
    assert res["cycle_exitvector_ether"]["status"] == "VIOLATION"
    assert res["cycle_3carbonyl"]["status"] == "ok"


def test_missing_edges_report_incomplete_rather_than_a_fabricated_closure():
    ddg = _closed_ddg()
    del ddg["e_zaienne_cmpd19__cw_ev_5oh"]
    res = {c["cycle_id"]: c for c in cf.cycle_closure(ddg)}
    assert res["cycle_exitvector_ether"]["status"] == "incomplete"
    assert res["cycle_exitvector_ether"]["missing"] == ["e_zaienne_cmpd19__cw_ev_5oh"]
    assert "sum_kcal" not in res["cycle_exitvector_ether"]


def test_ranking_uses_anchor_rooted_edges_only_and_sorts_tightest_first():
    rows = cf.rank_by_ddg({"e_zaienne_cmpd19__cw_ev_5nh2": 1.84,
                           "e_zaienne_cmpd19__cw_ev_5oh": -0.5,
                           "e_cw_ev_5oh__cw_ev_5opropargyl": -9.9})
    assert [r["node"] for r in rows] == ["cw_ev_5oh", "cw_ev_5nh2"]      # closure edge excluded
    assert rows[0]["ddg_bind_kcal"] < rows[1]["ddg_bind_kcal"]


# ---- planning ---------------------------------------------------------------------------------------------

def test_plan_states_what_it_does_not_run():
    p = cf.plan()
    assert p["n_units"] == 19
    assert len(p["excluded_tranche_2_charge_changing"]) == 8
    assert p["excluded_tranche_3_frames"]
    assert "not selectivity" in p["claim_ceiling"].lower() or "NOT a selectivity" in p["claim_ceiling"]
    lo, hi = p["cost_usd_est"]
    # ⚠ THIS BOUND WAS A STALE COPY OF A RETIRED NUMBER. It read `5 < lo < hi < 60`, commented "the pinned
    # ~$12-26 band, with measurement slack" — but that band was repriced to **~$36 ($15-80)** when the ~4x
    # cost error was found (wrong molecule 2.6x, wrong bid basis 3x; see step1-fanout-lane.md §5 and
    # STRATEGY.md's ladder entry). plan() correctly reports the corrected band, so the TEST was the thing
    # holding the retired figure, and it went red the moment anyone touched this lane. That is precisely the
    # one-fact-one-place failure the repo's own linter exists for — a number living in two places while a
    # correction reached only one.
    # Assert the SHAPE (ordered, positive, finite) and a generous ceiling that no longer encodes a specific
    # estimate; the band itself has one home, and it is not here.
    assert 0 < lo < hi < 200


def test_wave_plan_matches_the_requested_width():
    assert cf.wave_plan(19, 8)["waves"] == 3
    assert cf.wave_plan(8, 8)["waves"] == 1
    assert cf.wave_plan(1, 8)["waves"] == 1


# ---- launcher jobspec (pure part) -------------------------------------------------------------------------

def test_jobspec_is_resumable_checkpointed_and_per_unit_scoped():
    import congeneric_fanout_vast as fv
    u = cf.default_units()[3]
    spec = fv.build_jobspec(u, "my-branch", "bkt", 3)
    assert spec.resume is True
    assert spec.checkpoint_uri.startswith("s3://bkt/") and u["unit_id"] in spec.checkpoint_uri
    assert spec.name.startswith("s1f-03-") and len(spec.name) <= 64
    assert spec.env["LIGAND_A"] == u["ligand_a"] and spec.env["LIGAND_B"] == u["ligand_b"]
    assert spec.env["GIT_BRANCH"] == "my-branch"
    body = spec.command[-1]
    # both alchemical legs run, each spot-safe, and the branch's own code is what executes
    assert "run_leg complex" in body and "run_leg solvent" in body
    assert "RBFE_SPOT_SAFE=1" in body and "RBFE_SPOT_COMMIT_S3" in body
    assert "$GIT_BRANCH.tar.gz" in body
    # the engine's 401-anchored reduce is deliberately NOT used
    assert "MODE=reduce" not in body
    assert "ddg_bind" in body


def test_every_unit_gets_a_distinct_instance_label():
    import congeneric_fanout_vast as fv
    names = [fv.build_jobspec(u, "b", "bkt", i).name for i, u in enumerate(cf.default_units())]
    assert len(set(names)) == len(names)
