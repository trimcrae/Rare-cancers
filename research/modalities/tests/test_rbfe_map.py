"""Unit tests for rbfe_map.py — the pure congeneric RBFE perturbation-map generator.

Exercises the map topology (two anchor stars + cycle-closure edges), microstate legs, the receptor-state
axis, the pilot edge, comparator exclusion, and the pre-registered abort criteria — all without any
chemistry/MD/GPU/network stack. Runs against the REAL frozen input JSONs (design-time, deterministic)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rbfe_map as rm  # noqa: E402


def _map():
    series, panel = rm.load_inputs()
    return rm.build_map(series, panel)


# ---------------------------------------------------------------------------
# heavy-atom counter (stdlib SMILES sanity metric)
# ---------------------------------------------------------------------------
def test_heavy_atom_count_bracket_and_two_letter():
    # methyl 5-bromoindole-3-carboxylate: C O C(=O) c c n c c c c Br c c c = 14 heavy atoms
    assert rm.heavy_atom_count("COC(=O)c1c[nH]c2ccc(Br)cc12") == 14
    assert rm.heavy_atom_count("c1ccccc1") == 6          # benzene, aromatic lowercase
    assert rm.heavy_atom_count("[nH]") == 1              # bracket aromatic N-H = 1 heavy
    assert rm.heavy_atom_count("Cl") == 1                # two-letter organic
    assert rm.heavy_atom_count("") == 0


def test_species_charge_rule():
    assert rm.species_charge("neutral") == 0
    assert rm.species_charge("anionic_carboxylate") == -1
    assert rm.species_charge("cationic_ammonium") == 1


# ---------------------------------------------------------------------------
# node set
# ---------------------------------------------------------------------------
def test_nodes_cover_series_plus_anchor():
    m = _map()
    nodes = {n["id"]: n for n in m["nodes"]}
    # 19 enumerated compounds + the anchor = 20 node entries
    assert m["summary"]["n_nodes"] == 20
    assert rm.ANCHOR_ID in nodes
    assert nodes[rm.ANCHOR_ID]["class"] == "anchor"
    # comparators are present but excluded from the RBFE map
    comps = [n for n in m["nodes"] if n["is_comparator"]]
    assert len(comps) == 3
    assert all(not n["in_rbfe_map"] for n in comps)
    assert m["summary"]["n_comparator_nodes"] == 3
    assert m["summary"]["n_nodes_in_rbfe_map"] == 17   # anchor + 16 congeneric


def test_ambiguous_nodes_have_two_species():
    m = _map()
    nodes = {n["id"]: n for n in m["nodes"]}
    assert len(rm.MICROSTATE_SPECIES) == 7             # matches the series' n_microstate_ambiguous
    for cid in rm.MICROSTATE_SPECIES:
        assert len(nodes[cid]["microstate_species"]) == 2
    # a clearly-neutral node carries exactly one species
    assert nodes["cw_ev_5oh"]["microstate_species"] == ["neutral"]


# ---------------------------------------------------------------------------
# edge topology: two anchor-rooted stars + cycle-closure edges
# ---------------------------------------------------------------------------
def test_edge_counts_by_class_and_star():
    m = _map()
    bc = m["summary"]["edges_by_class"]
    # one spoke per non-comparator non-anchor compound (8 exit_vector + 5 bioisostere + 3 microstate) + 3 cycles
    assert bc["exit_vector_sub"] == 8
    assert bc["bioisostere"] == 5
    assert bc["microstate_variant"] == 3
    assert bc["cycle_closure"] == 3
    assert m["summary"]["n_edges"] == 19
    bs = m["summary"]["edges_by_star"]
    assert bs[rm._STAR5] == 9 + 2   # 9 five-position spokes + 2 five-position cycle edges
    assert bs[rm._STAR3] == 7 + 1   # 7 three-position spokes + 1 three-position cycle edge


def test_every_congeneric_spoke_roots_at_anchor():
    m = _map()
    star_edges = [e for e in m["edges"] if not e["is_cycle_closure"]]
    assert len(star_edges) == 16
    assert all(e["node_a"] == rm.ANCHOR_ID for e in star_edges)
    assert all(e["single_site"] for e in m["edges"])


def test_bioisostere_edges_need_pose_revalidation():
    m = _map()
    bios = [e for e in m["edges"] if e["class"] == "bioisostere"]
    assert bios and all(e["needs_pose_revalidation"] for e in bios)
    # 5-position exit-vector spokes do NOT force pose revalidation
    ev = [e for e in m["edges"] if e["class"] == "exit_vector_sub"]
    assert all(not e["needs_pose_revalidation"] for e in ev)


def test_no_comparator_edges():
    m = _map()
    comp_ids = {n["id"] for n in m["nodes"] if n["is_comparator"]}
    for e in m["edges"]:
        assert e["node_a"] not in comp_ids and e["node_b"] not in comp_ids
    assert m["denovo401_gets_abfe_not_rbfe"] is True
    assert set(m["comparator_calibration"]["nodes"]) == comp_ids


# ---------------------------------------------------------------------------
# cycle closure
# ---------------------------------------------------------------------------
def test_cycles_are_closed_triangles_of_existing_edges():
    m = _map()
    edge_ids = {e["edge_id"] for e in m["edges"]}
    assert len(m["cycles"]) == 3
    for cyc in m["cycles"]:
        assert len(cyc["edge_ids"]) == 3
        assert all(eid in edge_ids for eid in cyc["edge_ids"])
        assert "~ 0" in cyc["constraint"]
    # the closing edge connects two non-anchor analogues and is flagged
    closers = [e for e in m["edges"] if e["is_cycle_closure"]]
    assert len(closers) == 3
    for e in closers:
        assert e["node_a"] != rm.ANCHOR_ID and e["node_b"] != rm.ANCHOR_ID
        assert e["cycle_id"] is not None


# ---------------------------------------------------------------------------
# microstate legs
# ---------------------------------------------------------------------------
def test_microstate_legs_and_charge_flags():
    m = _map()
    edges = {e["edge_id"]: e for e in m["edges"]}
    # anchor(neutral) -> 5cooh(neutral_acid, anionic_carboxylate): 2 legs, one charge-changing
    e = edges[rm.edge_id(rm.ANCHOR_ID, "cw_ev_5cooh")]
    assert len(e["microstate_legs"]) == 2
    charged = [lg for lg in e["microstate_legs"] if lg["charge_change"]]
    assert len(charged) == 1 and charged[0]["net_charge_change"] == -1
    # a fully-neutral edge -> exactly one leg, no charge change
    e2 = edges[rm.edge_id(rm.ANCHOR_ID, "cw_ev_5oh")]
    assert len(e2["microstate_legs"]) == 1 and not e2["microstate_legs"][0]["charge_change"]


# ---------------------------------------------------------------------------
# receptor-state axis + pilot
# ---------------------------------------------------------------------------
def test_pilot_edge_is_small_neutral_single_frame():
    m = _map()
    edges = {e["edge_id"]: e for e in m["edges"]}
    pe = edges[m["pilot_edge_id"]]
    assert pe["is_pilot"] is True
    assert pe["node_a"] == rm.ANCHOR_ID and pe["node_b"] == "cw_ev_5nh2"
    # both endpoints neutral (unambiguous microstate)
    assert rm.node_species(pe["node_a"]) == ["neutral"]
    assert rm.node_species(pe["node_b"]) == ["neutral"]
    # pilot runs on exactly ONE nr4a3_design frame
    pilot_frames = pe["receptor_frames"]["pilot"]
    assert sum(len(v) for v in pilot_frames.values()) == 1
    assert "nr4a3_design" in pilot_frames["nr4a3"][0]
    # non-pilot edges carry no pilot frame block
    other = edges[rm.edge_id(rm.ANCHOR_ID, "cw_ev_5oh")]
    assert other["receptor_frames"]["pilot"] is None


def test_fleet_axis_has_validation_and_matched_antitargets():
    m = _map()
    e = [e for e in m["edges"] if not e["is_pilot"]][0]
    fleet = e["receptor_frames"]["fleet"]
    assert any("nr4a3_validation" in f for f in fleet["nr4a3"])
    assert "nr4a1" in fleet and "nr4a2" in fleet   # matched anti-targets present


def test_abort_criteria_present_and_pre_registered():
    m = _map()
    ac = m["abort_criteria"]
    for k in ("hysteresis_kcal_max", "mbar_overlap_min", "pocket_survival_frac_min", "cycle_closure_kcal_max"):
        assert k in ac and isinstance(ac[k], (int, float))
    assert "TBD" in ac["all_values_status"]


def test_cost_is_tbd_not_fabricated():
    m = _map()
    for e in m["edges"]:
        assert e["cost"]["n_windows"] is None
        assert e["cost"]["est_gpu_h"] is None
        assert "TBD" in e["cost"]["status"]


def test_feeds_existing_scorer_and_pose_caveat():
    m = _map()
    assert m["feeds_scorer"] == "ensemble_robust_score"
    assert "HYPOTHES" in m["pose_uncertainty_caveat"].upper()


# ---------------------------------------------------------------------------
# whole-map validation
# ---------------------------------------------------------------------------
def test_validate_map_clean():
    m = _map()
    assert rm.validate_map(m) == []


def test_validate_map_catches_comparator_edge():
    m = _map()
    # inject a forbidden RBFE edge into a comparator -> validator must flag it
    m["edges"].append({
        "edge_id": "e_bad", "class": "exit_vector_sub", "star": rm._STAR5,
        "node_a": rm.ANCHOR_ID, "node_b": "cw_cmp_denovo401", "single_site": True,
        "n_atoms_changed": 1, "needs_pose_revalidation": False, "is_cycle_closure": False,
        "cycle_id": None, "is_pilot": False, "microstate_legs": [], "receptor_frames": {"pilot": None},
    })
    assert any("comparator" in p for p in rm.validate_map(m))
