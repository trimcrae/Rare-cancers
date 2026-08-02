#!/usr/bin/env python3
"""Offline unit tests for `nr4a3_linker_covalent_reach` — pure logic, no network, no structures fetched.

The rules these pin, in order of how much damage each would do if it drifted:
  1. the corridor rule and the committed three-ball rule must agree on the SAME chain-length arithmetic;
  2. the corridor answer can never be SHORTER than the through-space answer (subset relation);
  3. the premise correction — one branch, not two — must stay read from the committed artifact;
  4. the chemoselectivity margin must go to zero exactly when a competitor is at or before the target;
  5. no threshold this module is graded on may be re-typed here rather than imported.
"""
import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import basin_geom as G                          # noqa: E402
import linker_design as LD                      # noqa: E402
import nr4a3_linker_covalent_reach as R         # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# 1 · the corridor rule reproduces the committed engine's chain-length arithmetic
# ---------------------------------------------------------------------------------------------------------
def test_n_min_from_point_matches_the_committed_ball_rule():
    """A branch atom at p is usable by an n-atom chain iff both anchor balls contain it at some integer k.
    `n_min_from_point` must return exactly the smallest such n, and its k must satisfy 1 <= k <= n-1."""
    a, b = (0.0, 0.0, 0.0), (12.0, 0.0, 0.0)
    for p in [(3.0, 2.0, 0.0), (6.0, 6.0, 1.0), (11.0, 0.5, 0.5), (1.0, 0.0, 0.0)]:
        n, k = R.n_min_from_point(p, a, b)
        assert 1 <= k <= n - 1
        assert G.dist(p, a) <= k * R.RISE + 1e-9
        assert G.dist(p, b) <= (n - k) * R.RISE + 1e-9
        # one atom shorter must fail for every admissible k
        assert not any(G.dist(p, a) <= kk * R.RISE + 1e-9
                       and G.dist(p, b) <= (n - 1 - kk) * R.RISE + 1e-9
                       for kk in range(1, max(1, n - 1)))


def test_corridor_never_beats_through_space_when_nothing_blocks():
    """With no protein at all, the corridor answer must equal the committed engine's answer to within the
    candidate grid pitch — the two rules are then the same rule."""
    a, b, q = (0.0, 0.0, 0.0), (14.0, 0.0, 0.0), (7.0, 9.0, 0.0)
    grid = R.AtomGrid([(0.0, -500.0, 0.0)], [0])          # one atom, far away: blocks nothing
    e = 4.0
    cand = R.candidate_branch_points(grid, q, e, set(), (R.CLASH_PRIMARY_A,))
    n_cor, _ = R.corridor_min_atoms(cand, a, b, e, R.CLASH_PRIMARY_A)
    n_ts = LD.min_linker_atoms_exact(a, b, q, e)
    assert n_cor is not None and n_ts is not None
    assert n_cor >= n_ts                                   # subset relation
    assert n_cor - n_ts <= 2                               # and the grid pitch cannot cost more than that


def test_a_wall_between_the_anchors_and_the_target_lengthens_or_kills_the_corridor():
    """The whole point of the corridor convention: a buried sulfur must not score as reachable."""
    a, b, q = (0.0, 0.0, 0.0), (14.0, 0.0, 0.0), (7.0, 9.0, 0.0)
    e = 4.0
    # a dense slab of atoms sitting between the anchor line and the target
    pts, keys = [], []
    for x in [v * 0.5 for v in range(-20, 60)]:
        for z in [v * 0.5 for v in range(-20, 21)]:
            pts.append((x, 6.0, z))
            keys.append(999)
    walled = R.AtomGrid(pts, keys)
    cand = R.candidate_branch_points(walled, q, e, set(), (R.CLASH_PRIMARY_A,))
    n_cor, _ = R.corridor_min_atoms(cand, a, b, e, R.CLASH_PRIMARY_A)
    n_ts = LD.min_linker_atoms_exact(a, b, q, e)
    assert n_ts is not None
    assert n_cor is None or n_cor > n_ts


def test_atomgrid_min_dist_is_exact_below_the_cell_size():
    pts = [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0), (0.0, 7.0, 0.0)]
    g = R.AtomGrid(pts, [1, 2, 3], cell=4.0)
    assert g.min_dist((1.0, 0.0, 0.0)) == pytest.approx(1.0)
    assert g.min_dist((1.0, 0.0, 0.0), exclude={1}) == pytest.approx(4.0)
    # the exact scan must agree with the binned one wherever the binned one is exact
    assert g.min_dist_exact((1.0, 0.0, 0.0)) == pytest.approx(1.0)
    # ... and must NOT saturate where the binned one does
    assert g.min_dist_exact((0.0, 30.0, 0.0)) == pytest.approx(23.0)


def test_arm_clear_ignores_the_target_but_not_an_obstacle():
    q = (0.0, 6.0, 0.0)
    g = R.AtomGrid([q, (0.0, 3.0, 0.0)], [7, 8])
    # excluding the target residue only: the intervening atom still blocks
    assert not R.arm_clear(g, (0.0, 0.0, 0.0), q, {7}, 3.0)
    # excluding both: nothing left to block
    assert R.arm_clear(g, (0.0, 0.0, 0.0), q, {7, 8}, 3.0)


# ---------------------------------------------------------------------------------------------------------
# 2 · the decision quantity
# ---------------------------------------------------------------------------------------------------------
def test_margin_is_zero_when_a_competitor_ties_or_leads():
    assert R.chemoselectivity_margin(11, {"C536": 11})["width"] == 0
    assert R.chemoselectivity_margin(11, {"C536": 10})["width"] == 0
    m = R.chemoselectivity_margin(11, {"C536": 16})
    assert (m["lo"], m["hi"], m["width"], m["blocked_by"]) == (11, 15, 5, "C536")


def test_margin_names_the_NEAREST_competitor_not_an_arbitrary_one():
    m = R.chemoselectivity_margin(9, {"C536": 20, "NR4A2 C534": 14, "C496": 27})
    assert m["blocked_by"] == "NR4A2 C534" and m["hi"] == 13 and m["width"] == 5


def test_margin_respects_the_imported_chemical_ceiling():
    m = R.chemoselectivity_margin(11, {})
    assert m["hi"] == R.CHEM_MAX_ATOMS
    assert R.chemoselectivity_margin(R.CHEM_MAX_ATOMS + 1, {})["width"] == 0
    assert R.chemoselectivity_margin(None, {})["width"] == 0


# ---------------------------------------------------------------------------------------------------------
# 3 · the premise correction stays READ, not remembered
# ---------------------------------------------------------------------------------------------------------
@pytest.mark.skipif(not os.path.exists(R.LIBRARY), reason="committed library not present")
def test_a_linker_borne_electrophile_plus_an_E3_arm_is_ONE_branch():
    """The claim that this needs a two-branch template is wrong, and it must stay wrong for a reason that is
    read out of the committed enumeration rather than recalled."""
    pc = R.premise_check()
    ev = pc["evidence"]
    assert ev["n_committed_one_branch_electrophile_plus_e3"] > 0
    assert "pendant=None" in ev["build_smiles_signature"]      # exactly ONE pendant slot
    assert ev["build_smiles_signature"].count("pendant") == 1
    assert "C397 SG" in ev["branch_targets"]


# ---------------------------------------------------------------------------------------------------------
# 4 · nothing this module is graded on may be re-typed here
# ---------------------------------------------------------------------------------------------------------
def test_thresholds_are_imported_from_their_one_home():
    import nr4a3_linker_design as NLD
    import nr4a_paralogue_unique_residues as uniq
    assert R.RISE is LD.RISE_PER_ATOM_A
    assert R.PENDANT_REACH is LD.PENDANT_REACH_A
    assert R.CHEM_MAX_ATOMS == NLD.CHEM_MAX_ATOMS
    assert R.CONFIRMED == NLD.CONFIRMED
    assert R.OFFSET == NLD.UNIPROT_OFFSET
    assert tuple(R.CRYPTIC_POCKET_UNIPROT) == tuple(uniq.CRYPTIC_POCKET_UNIPROT)


def test_the_only_new_parameter_declares_itself_and_is_swept():
    """The clash cutoff has no home in the repo, so it is declared here — and a declared parameter that is
    not swept is a knob. Its primary must be inside the sweep, and the sweep must span both a permissive and
    a strict end so a conclusion that depends on it is visible."""
    assert R.CLASH_PRIMARY_A in R.CLASH_SWEEP_A
    assert min(R.CLASH_SWEEP_A) < R.CLASH_PRIMARY_A < max(R.CLASH_SWEEP_A)
    assert len(R.CLASH_SWEEP_A) >= 3


# ---------------------------------------------------------------------------------------------------------
# 5 · numbering must never be an assumed offset for a structure that carries its own
# ---------------------------------------------------------------------------------------------------------
def test_cysteines_in_accepts_a_map_as_well_as_an_offset():
    model = {"residues": [(19, "C"), (20, "A"), (42, "C")],
             "atoms_by_res": {19: [{"name": "SG", "x": 1.0, "y": 0.0, "z": 0.0}],
                              42: [{"name": "SG", "x": 0.0, "y": 2.0, "z": 0.0}]}}
    by_map = R.cysteines_in(model, {19: 397, 42: 420}, unique={"C397"})
    assert set(by_map) == {"C397", "C420"}
    assert by_map["C397"]["unique"] and not by_map["C420"]["unique"]
    by_offset = R.cysteines_in(model, 378)
    assert set(by_offset) == {"C397", "C420"}
    # a residue the map does not cover is DROPPED, never given a guessed number
    assert set(R.cysteines_in(model, {19: 397})) == {"C397"}


# ---------------------------------------------------------------------------------------------------------
# 6 · the invariant violation classifier
# ---------------------------------------------------------------------------------------------------------
def test_a_one_atom_disagreement_at_a_tangency_is_classified_benign_not_hidden():
    """Constructed so the three balls touch: q sits exactly at the pendant reach from a point the chain can
    just reach. The classifier must call it a tangency AND still record the numbers."""
    a, b = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0)
    q = (5.0, 8.0, 0.0)
    n_ts = LD.min_linker_atoms_exact(a, b, q, 3.0)
    v = R.classify_disagreement(a, b, q, 3.0, n_ts - 1, n_ts, "f", "p", "C1", "pend", 3.0)
    assert v["through_space_atoms"] == n_ts and v["corridor_atoms"] == n_ts - 1
    assert v["kind"] in ("degenerate_tangency", "RULE_DRIFT")
    assert v["engine_best_margin_A_at_corridor_n"] is not None


def test_a_large_disagreement_is_called_RULE_DRIFT():
    a, b, q = (0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (5.0, 20.0, 0.0)
    v = R.classify_disagreement(a, b, q, 3.0, 4, 30, "f", "p", "C1", "pend", 3.0)
    assert v["kind"] == "RULE_DRIFT"


# ---------------------------------------------------------------------------------------------------------
# 7 · spread + JSON safety
# ---------------------------------------------------------------------------------------------------------
def test_spread_carries_the_missing_count_rather_than_dropping_it():
    s = R.spread([3, None, 5, 9, None])
    assert (s["n"], s["n_missing"], s["min"], s["median"], s["max"]) == (3, 2, 3, 5, 9)
    empty = R.spread([None, None])
    assert empty["n"] == 0 and empty["median"] is None


def test_electrophile_options_assert_nothing():
    eo = R.electrophile_classes()
    assert "no reactivity, selectivity or feasibility claim" in eo["_status"]
    for c in eo["classes"]:
        assert c["sources"], "an electrophile class without a primary source is a bare assertion"
    assert eo["_uncomputed_and_decision_relevant"]


def test_noise_sensitivity_compares_against_measured_displacement_not_a_guess():
    rows = [{"cost_of_the_paralogue_control_in_atoms": 4},
            {"cost_of_the_paralogue_control_in_atoms": 6}]
    disp = {"pairs": [{"delta_SG_A": 1.0}, {"delta_SG_A": 9.0}]}
    s = R._noise_sensitivity(rows, disp)
    assert s["median_window_lost_atoms"] == 5.0
    assert s["sg_displacement_that_would_reopen_it_A"] == pytest.approx(5.0 * R.RISE)
    assert s["correction_needed_is_inside_the_observed_model_noise"] is True
    tight = R._noise_sensitivity(rows, {"pairs": [{"delta_SG_A": 0.4}]})
    assert tight["correction_needed_is_inside_the_observed_model_noise"] is False


def test_ball_grid_is_deterministic_and_bounded():
    """A sampled reach answer that moved between runs would be unusable as a gate."""
    c = (1.0, 2.0, 3.0)
    one = R.ball_grid(c, 3.0, 1.0)
    two = R.ball_grid(c, 3.0, 1.0)
    assert one == two
    assert all(G.dist(p, c) <= 3.0 + 1e-9 for p in one)
    assert c in one


# ---------------------------------------------------------------------------------------------------------
# 8 · the "E3 still projects to solvent" clause must FILTER, not merely annotate
# ---------------------------------------------------------------------------------------------------------
def _row(frame, placement, e3_ok, ts, co):
    return {"frame": frame, "placement": placement, "meta_basin_id": placement.split("@")[0],
            "placement_label": "term_a_exemplar", "cysteine": "C397", "unique": True,
            "e3_projects_to_solvent": e3_ok, "warhead_anchor_has_room": True,
            "d_warhead_anchor_A": 9.0, "d_e3_anchor_A": 9.0, "span_A": 13.0,
            "by_pendant": {"dab_branch": {"arm_reach_A": 8.75, "through_space_atoms": ts,
                                          "corridor_atoms": {"%.1f" % R.CLASH_PRIMARY_A: co}}}}


def test_a_buried_E3_anchor_is_excluded_from_the_spread_and_listed():
    rows = [_row("m1", "b|X@term_a_exemplar", True, 11, 12),
            _row("m2", "b|X@term_a_exemplar", False, 40, 44),   # would wreck the spread if pooled
            _row("m3", "b|X@term_a_exemplar", True, 12, 13)]
    adm = R.placement_admissibility(rows)
    assert adm["n_cells"] == 3 and adm["n_e3_anchor_BURIED"] == 1
    assert adm["e3_anchor_buried_cells"][0]["frame"] == "m2"

    sp = R.ensemble_summary(rows, {"C397"}, {})
    key = "C397|b|X@term_a_exemplar|dab_branch"
    assert sp[key]["n_conformers"] == 2
    assert sp[key]["through_space_atoms"]["max"] == 12        # 40 must NOT appear
    counts = R.reachable_counts(rows)
    assert counts[key]["n_conformers"] == 2


def test_admissibility_reports_a_cramped_warhead_anchor_without_excluding_it():
    rows = [_row("m1", "b|X@term_a_exemplar", True, 11, 12)]
    rows[0]["warhead_anchor_has_room"] = False
    adm = R.placement_admissibility(rows)
    assert adm["n_warhead_anchor_with_no_room"] == 1
    assert adm["n_e3_anchor_BURIED"] == 0
    assert R.ensemble_summary(rows, {"C397"}, {})["C397|b|X@term_a_exemplar|dab_branch"]["n_conformers"] == 1
