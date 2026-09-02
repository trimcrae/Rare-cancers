#!/usr/bin/env python3
"""Offline unit tests for `nr4a3_monovalent_reach` — pure logic, no network, no structures fetched.

The rules these pin, in order of how much damage each would do if it drifted:
  1. the monovalent length rule is EXACTLY the bivalent rule with the second anchor term dropped —
     if those two ever stop agreeing at the degenerate limit, the paired comparison is measuring the
     implementation rather than the configuration;
  2. MONOTONICITY: dropping a term can only shorten a chain, so monovalent <= bivalent everywhere. The
     module refuses on a violation, so this test is what stops that refusal being silently reinterpreted;
  3. the through-space closed form must reproduce the engine's answer in the limit where the E3 anchor is
     placed on top of the warhead anchor (the only configuration in which the two are the same question);
  4. the PAIRED TRANSITION counter must classify each direction correctly — a `closed -> open` miscount
     would invert the verdict;
  5. the ten-placement -> five-anchor collapse must be exact, and must refuse rather than merge if one
     pose id ever carried two anchors;
  6. no threshold is re-typed here; every constant is imported from the lane that owns it.
"""
import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import basin_geom as G                          # noqa: E402
import linker_design as LD                      # noqa: E402
import nr4a3_linker_covalent_reach as CR        # noqa: E402
import nr4a3_monovalent_reach as M              # noqa: E402


# ---------------------------------------------------------------------------------------------------------
# 1 · the monovalent rule IS the bivalent rule minus one term
# ---------------------------------------------------------------------------------------------------------
def test_mono_rule_is_the_bivalent_rule_without_the_second_term():
    a, b = (0.0, 0.0, 0.0), (12.0, 0.0, 0.0)
    for p in [(3.0, 2.0, 0.0), (6.0, 6.0, 1.0), (11.0, 0.5, 0.5), (1.0, 0.0, 0.0), (0.2, 0.0, 0.0)]:
        n_bi, k = CR.n_min_from_point(p, a, b)
        n_mo = M.mono_min_from_point(p, a)
        assert n_mo == k, "the monovalent count must equal the bivalent rule's warhead-side term"
        assert n_mo <= n_bi
        # the chain really can place an atom at p
        assert G.dist(p, a) <= n_mo * M.RISE + 1e-9
        # one atom shorter cannot
        if n_mo > 1:
            assert G.dist(p, a) > (n_mo - 1) * M.RISE + 1e-9


def test_mono_rule_floors_at_one_atom_exactly_as_the_bivalent_rule_does():
    """The floor is a CONVENTION shared with the bivalent rule so the two are comparable. A zero-atom
    (warhead-borne) electrophile would be a different claim and this module does not make it."""
    a = (0.0, 0.0, 0.0)
    assert M.mono_min_from_point((0.0, 0.0, 0.0), a) == 1
    assert M.mono_min_from_point((0.01, 0.0, 0.0), a) == 1


# ---------------------------------------------------------------------------------------------------------
# 2 · monotonicity — the property the whole comparison rests on
# ---------------------------------------------------------------------------------------------------------
def test_monovalent_never_exceeds_bivalent_over_a_grid():
    a, b = (0.0, 0.0, 0.0), (9.0, 4.0, -2.0)
    for x in range(-6, 7, 3):
        for y in range(-6, 7, 3):
            for z in range(-6, 7, 3):
                p = (float(x), float(y), float(z))
                n_bi, _ = CR.n_min_from_point(p, a, b)
                assert M.mono_min_from_point(p, a) <= n_bi


def test_monotonicity_check_flags_a_planted_violation():
    mono = [{"frame": "f", "anchor": "p1", "cysteine": "C397",
             "by_pendant": {"amide_direct": {"through_space_atoms": 9, "corridor_atoms": 9}}}]
    bival = [{"frame": "f", "anchor": "p1", "cysteine": "C397",
              "by_pendant": {"amide_direct": {"through_space_atoms": 7, "corridor_atoms": 7}}}]
    out = M.monotonicity_check(mono, bival)
    assert out["status"] == "VIOLATED"
    assert out["n_violations"] == 2


def test_monotonicity_check_flags_unreachable_monovalent_where_bivalent_reaches():
    """`None` monovalent against a real bivalent answer is a violation, not a missing value — a shorter
    chain cannot lose a branch position the longer one had."""
    mono = [{"frame": "f", "anchor": "p1", "cysteine": "C397",
             "by_pendant": {"amide_direct": {"through_space_atoms": None, "corridor_atoms": None}}}]
    bival = [{"frame": "f", "anchor": "p1", "cysteine": "C397",
              "by_pendant": {"amide_direct": {"through_space_atoms": 12, "corridor_atoms": 12}}}]
    assert M.monotonicity_check(mono, bival)["status"] == "VIOLATED"


# ---------------------------------------------------------------------------------------------------------
# 3 · the through-space closed form against the committed engine, at the only shared limit
# ---------------------------------------------------------------------------------------------------------
def test_engine_with_a_fabricated_b_is_exactly_twice_the_monovalent_answer():
    """★ THE TEST THAT JUSTIFIES THE CLOSED FORM INSTEAD OF REUSING THE ENGINE.

    Setting b = a does NOT turn the engine into the monovalent question. The three-ball rule still spends
    a return arm: it needs some k with min(k, n-k)*rise >= |p-a|, so the shortest admissible n is exactly
    TWICE the monovalent answer. Reusing `min_linker_atoms_exact` with a fabricated second anchor would
    therefore have doubled every monovalent chain length and flipped the verdict — which is why this
    module carries its own closed form and this test pins the factor."""
    a = (0.0, 0.0, 0.0)
    for d in (2.0, 5.0, 9.0, 14.0, 19.0):
        q = (d, 0.0, 0.0)
        for e in sorted(LD.PENDANT_REACH_A.values()):
            engine = LD.min_linker_atoms_exact(a, a, q, e, n_max=80)
            closed = M.mono_through_space_atoms(q, a, e)
            assert engine is not None and closed is not None
            assert engine == 2 * closed, (d, e, engine, closed)


def test_through_space_closed_form_is_exact_at_its_own_boundary():
    a = (0.0, 0.0, 0.0)
    e = 4.0
    # exactly on the boundary of an n-atom chain's reach
    for n in (1, 3, 7):
        q = (n * M.RISE + e, 0.0, 0.0)
        assert M.mono_through_space_atoms(q, a, e) == n
        q_over = (n * M.RISE + e + 1e-3, 0.0, 0.0)
        assert M.mono_through_space_atoms(q_over, a, e) == n + 1


def test_target_inside_the_arm_needs_the_floor_only():
    a = (0.0, 0.0, 0.0)
    assert M.mono_through_space_atoms((1.0, 0.0, 0.0), a, 5.0) == 1


# ---------------------------------------------------------------------------------------------------------
# 4 · the corridor variant shares the bivalent candidate set and only changes the length rule
# ---------------------------------------------------------------------------------------------------------
def test_mono_corridor_uses_the_same_candidate_filter_as_the_bivalent_corridor():
    a, b = (0.0, 0.0, 0.0), (14.0, 0.0, 0.0)
    cands = [{"p": (4.0, 1.0, 0.0), "d_q": 3.0, "clear_at": (2.0, 3.0)},
             {"p": (5.0, 0.0, 0.0), "d_q": 6.0, "clear_at": (2.0, 3.0)},      # outside a 4 A arm
             {"p": (2.0, 0.0, 0.0), "d_q": 2.0, "clear_at": (2.0,)}]          # fails the 3.0 cutoff
    mono = M.mono_corridor_min_atoms(cands, a, 4.0, 3.0)
    bi, _ = CR.corridor_min_atoms(cands, a, b, 4.0, 3.0)
    # only the first candidate survives BOTH filters in either configuration
    assert mono == M.mono_min_from_point((4.0, 1.0, 0.0), a)
    assert bi == CR.n_min_from_point((4.0, 1.0, 0.0), a, b)[0]
    assert mono < bi


def test_mono_corridor_returns_none_when_no_candidate_survives():
    cands = [{"p": (4.0, 1.0, 0.0), "d_q": 9.0, "clear_at": (2.0, 3.0)}]
    assert M.mono_corridor_min_atoms(cands, (0.0, 0.0, 0.0), 4.0, 3.0) is None


# ---------------------------------------------------------------------------------------------------------
# 5 · the paired-transition counter
# ---------------------------------------------------------------------------------------------------------
def _row(cell, pendant, width, closed_by=None):
    return {"cell": cell, "pendant": pendant, "width": width, "closed_by": closed_by}


def test_paired_transitions_classifies_all_four_directions():
    bival = [_row("B1@rep", "amide_direct", 5), _row("B2@rep", "amide_direct", 0),
             _row("B3@rep", "amide_direct", 4), _row("B4@rep", "amide_direct", 0)]
    mono = [_row("p1", "amide_direct", 3), _row("p2", "amide_direct", 2),
            _row("p3", "amide_direct", 0, "NR4A1 C505"), _row("p4", "amide_direct", 0)]
    anchor_of = {"B1@rep": "p1", "B2@rep": "p2", "B3@rep": "p3", "B4@rep": "p4"}
    t = M.paired_transitions(mono, bival, anchor_of)
    assert (t["open_to_open"], t["closed_to_open"], t["open_to_closed"], t["closed_to_closed"]) == \
           (1, 1, 1, 1)
    assert t["n_paired"] == 4 and t["unpaired"] == 0
    assert t["cells_that_gained_a_window"] == [{"bivalent_cell": "B2@rep", "pendant": "amide_direct",
                                                "monovalent_width": 2}]
    assert t["cells_that_lost_a_window"][0]["monovalent_closed_by"] == "NR4A1 C505"


def test_paired_transitions_counts_an_unmatched_cell_rather_than_dropping_it():
    """A bivalent cell whose anchor has no monovalent counterpart must be COUNTED as unpaired. Silently
    dropping it would shrink the denominator and flatter whichever configuration lost it."""
    t = M.paired_transitions([], [_row("B1@rep", "amide_direct", 5)], {"B1@rep": "p1"})
    assert t["unpaired"] == 1 and t["n_paired"] == 0


# ---------------------------------------------------------------------------------------------------------
# 6 · the placement -> anchor collapse
# ---------------------------------------------------------------------------------------------------------
def test_anchor_collapse_is_exact_and_records_what_each_anchor_subsumes():
    pls = [{"pose_id": "e7", "_a": (1.0, 0.0, 0.0), "a_warhead_anchor": [1.0, 0.0, 0.0],
            "meta_basin_id": "vhl|M2", "placement_label": "term_a_exemplar"},
           {"pose_id": "e7", "_a": (1.0, 0.0, 0.0), "a_warhead_anchor": [1.0, 0.0, 0.0],
            "meta_basin_id": "vhl|M3", "placement_label": "term_a_exemplar"},
           {"pose_id": "e9", "_a": (2.0, 0.0, 0.0), "a_warhead_anchor": [2.0, 0.0, 0.0],
            "meta_basin_id": "vhl|M14", "placement_label": "representative"}]
    out = M.monovalent_anchors(pls)
    assert [a["pose_id"] for a in out] == ["e7", "e9"]
    assert out[0]["subsumes_bivalent_placements"] == ["vhl|M2@term_a_exemplar", "vhl|M3@term_a_exemplar"]


def test_anchor_collapse_refuses_two_anchors_under_one_pose_id():
    pls = [{"pose_id": "e7", "_a": (1.0, 0.0, 0.0), "a_warhead_anchor": [1.0, 0.0, 0.0],
            "meta_basin_id": "vhl|M2", "placement_label": "term_a_exemplar"},
           {"pose_id": "e7", "_a": (9.0, 0.0, 0.0), "a_warhead_anchor": [9.0, 0.0, 0.0],
            "meta_basin_id": "vhl|M3", "placement_label": "term_a_exemplar"}]
    with pytest.raises(SystemExit):
        M.monovalent_anchors(pls)


# ---------------------------------------------------------------------------------------------------------
# 7 · the window arithmetic is the committed one, not a second copy
# ---------------------------------------------------------------------------------------------------------
def test_the_margin_function_is_the_committed_one():
    assert M.CR.chemoselectivity_margin is CR.chemoselectivity_margin


def test_no_threshold_is_re_typed():
    assert M.RISE is LD.RISE_PER_ATOM_A
    assert M.PENDANT_REACH is LD.PENDANT_REACH_A
    assert M.CHEM_MAX_ATOMS == CR.CHEM_MAX_ATOMS
    assert M.CLASH_PRIMARY_A == CR.CLASH_PRIMARY_A
    assert M.CLASH_SWEEP_A == CR.CLASH_SWEEP_A


def test_window_summary_counts_rank_and_closer_kind_separately():
    rows = [
        {"width": 0, "closed_by": "NR4A1 C505", "closer_is_a_PARALOGUE_cysteine": True,
         "rank_of_target": 2, "tied_with": [], "intra_nr4a3_width": 3},
        {"width": 2, "closed_by": "NR4A3 C536", "closer_is_a_PARALOGUE_cysteine": False,
         "rank_of_target": 1, "tied_with": ["NR4A3 C536"], "intra_nr4a3_width": 2},
    ]
    s = M.window_summary(rows)
    assert s["n_cells"] == 2 and s["n_open"] == 1
    assert s["n_closed_by_a_PARALOGUE_cysteine"] == 1
    assert s["n_closed_by_an_NR4A3_conserved_cysteine"] == 1
    assert s["n_target_not_first"] == 1 and s["n_target_tied_first"] == 1


# ---------------------------------------------------------------------------------------------------------
# 8 · the verdict may not be collapsed to one word across two disagreeing conventions
# ---------------------------------------------------------------------------------------------------------
def test_verdict_reports_per_convention_and_never_merges_them():
    d = {
        "summary": {
            "monovalent": {c: {"n_open": 0, "n_cells": 30, "median_intra_nr4a3_width": 1,
                               "closers_by_count": {}, "n_target_not_first": 28}
                           for c in ("corridor", "through_space")},
            "bivalent": {c: {"n_open": 37, "n_cells": 60, "median_intra_nr4a3_width": 7,
                             "closers_by_count": {}, "n_target_not_first": 13}
                         for c in ("corridor", "through_space")},
        },
        "paired_transitions": {"by_convention": {
            "corridor": {"open_to_open": 0, "open_to_closed": 37, "closed_to_open": 0,
                         "closed_to_closed": 23, "cells_that_gained_a_window": []},
            "through_space": {"open_to_open": 24, "open_to_closed": 24, "closed_to_open": 8,
                              "closed_to_closed": 4,
                              "cells_that_gained_a_window": [{"monovalent_width": 2}]},
        }},
    }
    v = M.verdict(d)
    assert v["answer_by_convention"] == {"corridor": "WORSE", "through_space": "MIXED"}
    assert v["answer_on_the_conservative_convention"] == "WORSE"
    assert v["cells_that_gained_a_window"]["max_width_gained"]["corridor"] == 0
    assert v["cells_that_gained_a_window"]["max_width_gained"]["through_space"] == 2
    # the verdict must never claim a refutation of monovalent modulation as such
    assert "not a refutation of monovalent pocket modulation" in v["_what_this_verdict_is_not"]


# ---------------------------------------------------------------------------------------------------------
# 7 · THE REACTIVITY-WEIGHTED ACCESSIBILITY CRITERION (`BLK-REACH-CATEGORICAL`'s retiring action)
#
# What these pin, and why each matters more than it looks:
#   a. the criterion's DIRECTIONS are read from `nr4a3-thiol-environment.json`, never typed in the module —
#      a re-typed sign is exactly the "one fact, two homes" defect that lets a criterion drift into being
#      tuned;
#   b. control recovery is BY CONSTRUCTION for any score vector whatsoever. This is the test that stops a
#      later session reporting "the criterion passes its positive control" as evidence of anything;
#   c. the score is rank-based, so it is invariant to any strictly monotone rescaling of a determinant —
#      the property that makes "equal weights" meaningful across incommensurable units;
#   d. `admissible=None` must reproduce the unfiltered enumeration EXACTLY. The criterion is an addition
#      beside the committed geometry result, never a correction to it;
#   e. an all-admitting criterion must give the unfiltered board back — the degenerate case that shows
#      discrimination, not control recovery, is the load-bearing test;
#   f. the target is NOT exempt: a fixture where C397 scores last must report the route refuted by its own
#      criterion rather than silently returning a window.
# ---------------------------------------------------------------------------------------------------------
def _cys_rows(labels, atoms, key_field="anchor", frame="f", key="A"):
    """Minimal reach rows: {protein-less label -> atom count} in every pendant, both conventions."""
    out = []
    for lab in labels:
        by = {p: {"arm_reach_A": e, "through_space_atoms": atoms[lab], "corridor_atoms": atoms[lab]}
              for p, e in M.PENDANT_REACH.items()}
        out.append({"frame": frame, key_field: key, "cysteine": lab, "unique": False, "by_pendant": by})
    return out


def _determinant_rows():
    """Three cysteines, one determinant, unambiguous order: C397 > C551 (control) > C505."""
    def r(prot, lab, rsa, hb, q):
        return {"protein": prot, "label": lab, "rsa": rsa,
                "n_hbond_capable_donors_within_4A_of_SG": hb, "net_formal_charge_within_8A": q,
                "nearest_cationic_group_A": 7.0, "sg_heavy_neighbours_within_6A": 30}
    return [r("NR4A3", "C397", 0.40, 4, 2), r("NR4A1", "C551", 0.16, 1, 1), r("NR4A1", "C505", 0.00, 0, 0)]


def test_criterion_directions_are_read_from_the_artifact_and_never_typed_in_the_module():
    rows, dirs, meta = M.load_thiol_determinants()
    assert meta["status"] == "READ", meta
    # every ranked determinant's sign came from the artifact, not from this module
    for f in ("rsa", "n_hbond_capable_donors_within_4A_of_SG", "net_formal_charge_within_8A",
              "nearest_cationic_group_A"):
        assert f in meta["directions_read_from_artifact"], f
    assert set(meta["directions_declared_in_this_module"]) == set(M.RWA_EXTRA_DIRECTIONS)
    assert dirs["nearest_cationic_group_A"] is False, "nearer cation argues for a LOWER pKa"
    assert dirs["rsa"] is True


def test_control_recovery_is_by_construction_for_ANY_scores_so_it_is_not_evidence():
    for scores in ({"NR4A1 C551": 0.0, "x": 1.0}, {"NR4A1 C551": 1.0, "x": 0.0},
                   {"NR4A1 C551": 0.5, "x": 0.5, "y": 0.49}):
        floor, admitted, st = M.rwa_admitted(scores)
        assert st["status"] == "OK"
        assert M.POSITIVE_CONTROL in admitted, "the floor IS the control, so it can never be excluded"
        assert floor == scores[M.POSITIVE_CONTROL]


def test_criterion_refuses_when_the_positive_control_is_absent():
    floor, admitted, st = M.rwa_admitted({"NR4A9 C1": 1.0})
    assert st["status"] == "REFUSED" and floor is None and admitted == []


def test_scores_are_rank_based_so_a_monotone_rescale_of_a_determinant_changes_nothing():
    rows, dirs, _ = M.load_thiol_determinants()
    base = M.rwa_scores(rows, dirs, M.RWA_VARIANTS[M.RWA_PRIMARY])
    squashed = [dict(r, rsa=math.sqrt(r["rsa"]) * 3.0) for r in rows]
    assert M.rwa_scores(squashed, dirs, M.RWA_VARIANTS[M.RWA_PRIMARY]) == base


def test_admissible_none_reproduces_the_unfiltered_enumeration_exactly():
    tgt = _cys_rows(["C397", "C420"], {"C397": 5, "C420": 9})
    par = {"NR4A1": _cys_rows(["C505"], {"C505": 7})}
    unfiltered = M.family_window(tgt, par, "anchor", "corridor")
    allowed = M.family_window(tgt, par, "anchor", "corridor",
                              admissible={"NR4A3 C397", "NR4A3 C420", "NR4A1 C505"})
    for a, b in zip(unfiltered, allowed):
        assert {k: v for k, v in a.items() if k != "competitors_dropped_by_criterion"} == \
               {k: v for k, v in b.items() if k != "competitors_dropped_by_criterion"}
        assert a["competitors_dropped_by_criterion"] == []


def test_filtering_drops_exactly_the_named_competitors_and_records_them():
    tgt = _cys_rows(["C397", "C420"], {"C397": 5, "C420": 9})
    par = {"NR4A1": _cys_rows(["C505"], {"C505": 4})}
    closed = M.family_window(tgt, par, "anchor", "corridor")
    assert all(r["width"] == 0 for r in closed), "a competitor at 4 atoms closes a target at 5"
    opened = M.family_window(tgt, par, "anchor", "corridor",
                             admissible={"NR4A3 C397", "NR4A3 C420"})
    assert all(r["competitors_dropped_by_criterion"] == ["NR4A1 C505"] for r in opened)
    assert all(r["width"] > 0 for r in opened), "dropping the only closer must open the window"
    assert all("NR4A1 C505" not in r["all_competitors_atoms"] for r in opened)


def test_a_criterion_that_admits_everything_is_the_unfiltered_board_and_R1_fires():
    rows = _determinant_rows()
    dirs = {"rsa": True, "n_hbond_capable_donors_within_4A_of_SG": True,
            "net_formal_charge_within_8A": True, "nearest_cationic_group_A": False,
            "sg_heavy_neighbours_within_6A": False}
    # put the control LAST: every cysteine then clears a floor set at the bottom
    flat = [dict(r) for r in rows]
    for r in flat:
        if r["label"] == "C551":
            r.update(rsa=0.0, n_hbond_capable_donors_within_4A_of_SG=0, net_formal_charge_within_8A=0)
    sc = M.rwa_scores(flat, dirs, M.RWA_VARIANTS[M.RWA_PRIMARY])
    _, admitted, _ = M.rwa_admitted(sc)
    assert len(admitted) == len(flat), "a bottom-ranked control admits the whole set"
    # and the non-discrimination guard is what catches that, not the control
    assert (len(admitted) > M.RWA_NON_DISCRIMINATION_CEILING) is (len(flat) >
                                                                  M.RWA_NON_DISCRIMINATION_CEILING)


def test_the_target_is_not_exempt_from_its_own_criterion():
    rows = _determinant_rows()
    dirs = {"rsa": True, "n_hbond_capable_donors_within_4A_of_SG": True,
            "net_formal_charge_within_8A": True, "nearest_cationic_group_A": False,
            "sg_heavy_neighbours_within_6A": False}
    sunk = [dict(r) for r in rows]
    for r in sunk:
        if r["label"] == "C397":
            r.update(rsa=0.0, n_hbond_capable_donors_within_4A_of_SG=0, net_formal_charge_within_8A=0)
    sc = M.rwa_scores(sunk, dirs, M.RWA_VARIANTS[M.RWA_PRIMARY])
    _, admitted, _ = M.rwa_admitted(sc)
    assert "NR4A3 C397" not in admitted, "the target must be able to fail the criterion it is judged by"


def test_the_committed_criterion_block_reports_every_variant_and_grades_R1():
    rows, dirs, meta = M.load_thiol_determinants()
    blk = M.reactivity_weighted_criterion(rows, dirs, meta)
    assert set(blk["variants"]) == set(M.RWA_VARIANTS)
    for name, v in blk["variants"].items():
        assert M.POSITIVE_CONTROL in v["admitted"], name
        assert v["n_scored"] == len(rows)
        assert v["R1_non_discrimination_FIRES"] is (v["n_admitted"] > M.RWA_NON_DISCRIMINATION_CEILING)
    assert blk["primary"] == M.RWA_PRIMARY


# ---------------------------------------------------------------------------------------------------------
# 8 · THE SIZE-MATCHED DECOY NULL — the guard that separates SELECTION from ATTRITION
#
# ⛔ Without this, "the window opened once the criterion was applied" and "the window opened because 14 of
#    17 competitors were discarded" are the same number. These tests pin that the null is size-matched, that
#    it fires on a criterion that only discards, and that it does NOT fire on one that genuinely selects.
# ---------------------------------------------------------------------------------------------------------
def _window_rows(target_atoms, competitors, n_cells=4):
    """Minimal `family_window`-shaped rows: same target count, same competitor board, in every cell."""
    return [{"cell": "c%d" % i, "target_atoms": target_atoms,
             "all_competitors_atoms": dict(competitors)} for i in range(n_cells)]


def test_decoy_null_is_size_matched_and_exhaustive_when_it_can_be():
    rows = _window_rows(5, {"NR4A1 A": 9, "NR4A1 B": 9, "NR4A2 C": 9, "NR4A2 D": 9})
    null = M.rwa_decoy_null(rows, ["NR4A3 C397", "NR4A1 A", "NR4A1 B"])
    assert null["status"] == "OK"
    assert null["k_competitors_retained"] == 2 and null["n_competitors_available"] == 4
    assert null["exhaustive"] is True and null["n_subsets_evaluated"] == 6   # C(4,2)
    assert null["_reading"].startswith("if a size-matched random subset")


def test_decoy_null_FIRES_when_the_window_came_from_attrition_alone():
    # every competitor is equally far away, so WHICH ones are kept cannot matter — only how many
    rows = _window_rows(5, {"NR4A1 A": 9, "NR4A1 B": 9, "NR4A2 C": 9, "NR4A2 D": 9})
    null = M.rwa_decoy_null(rows, ["NR4A3 C397", "NR4A1 A", "NR4A1 B"])
    assert null["observed_n_open"] == null["null_median_n_open"] == null["null_max"]
    assert null["R6_attrition_not_selection_FIRES"] is True
    assert null["fraction_of_size_matched_subsets_at_or_above_observed"] == 1.0


def test_decoy_null_does_NOT_fire_when_the_criterion_really_selected():
    # one competitor closes the window and the criterion is the only 2-subset that drops it
    rows = _window_rows(5, {"NR4A1 CLOSER": 4, "NR4A1 B": 9, "NR4A2 C": 9, "NR4A2 D": 9})
    good = M.rwa_decoy_null(rows, ["NR4A3 C397", "NR4A1 B", "NR4A2 C"])
    assert good["observed_n_open"] == len(rows)
    assert good["observed_n_open"] > good["null_median_n_open"]
    assert good["R6_attrition_not_selection_FIRES"] is False
    bad = M.rwa_decoy_null(rows, ["NR4A3 C397", "NR4A1 CLOSER", "NR4A1 B"])
    assert bad["observed_n_open"] == 0 and bad["R6_attrition_not_selection_FIRES"] is True


def test_decoy_null_target_is_never_counted_as_its_own_competitor():
    rows = _window_rows(5, {"NR4A1 A": 9, "NR4A1 B": 9})
    null = M.rwa_decoy_null(rows, ["NR4A3 C397", "NR4A1 A"])
    assert null["n_competitors_available"] == 2, "the target must not enter the competitor pool"
    assert null["k_competitors_retained"] == 1
