"""Tests for ensemble_robust_score -- the worst-case ensemble-robust candidate scorer for the NR4A3
selective-degrader redesign. Pure logic; no docking/scoring stack required."""
import math

import ensemble_robust_score as ers


# ---------------------------------------------------------------------------
# helpers / conventions
# ---------------------------------------------------------------------------
def test_favourability_is_neg_dG_and_none_safe():
    assert ers.favourability(-8.0) == 8.0
    assert ers.favourability(2.5) == -2.5
    assert ers.favourability(None) is None


def test_favourabilities_from_dG_maps_and_preserves_none():
    out = ers.favourabilities_from_dG({"m1": -8.0, "m2": -6.0, "m3": None})
    assert out == {"m1": 8.0, "m2": 6.0, "m3": None}
    assert ers.favourabilities_from_dG(None) == {}


def test_population_sd_and_mean_ignore_none():
    assert ers._mean([2.0, 4.0, None]) == 3.0
    assert ers._population_sd([1.0, 1.0, 1.0]) == 0.0
    assert math.isclose(ers._population_sd([2.0, 4.0]), 1.0)      # ddof=0: sqrt(((-1)^2+1^2)/2)=1
    assert ers._population_sd([None, None]) is None
    assert ers._population_sd([]) is None


# ---------------------------------------------------------------------------
# per_conformer_margins
# ---------------------------------------------------------------------------
def _panel_scores():
    # NR4A3 favoured everywhere; NR4A1/NR4A2 weaker. Favourability units (higher = tighter).
    return {
        "3": {"cA": 9.0, "cB": 8.0, "cC": 7.0},
        "1": {"cA": 4.0, "cB": 3.0, "cC": 5.0},
        "2": {"cA": 3.0, "cB": 4.0, "cC": 2.0},
    }


def test_per_conformer_margins_uses_worst_paralogue_per_conformer():
    m = ers.per_conformer_margins(_panel_scores())
    # cA: 9 - max(4,3)=9-4=5 ; cB: 8 - max(3,4)=8-4=4 ; cC: 7 - max(5,2)=7-5=2
    assert m == {"cA": 5.0, "cB": 4.0, "cC": 2.0}


def test_per_conformer_margins_skips_conformer_missing_nr4a3_or_all_paralogues():
    sc = {"3": {"cA": 9.0, "cB": None, "cD": 6.0},
          "1": {"cA": 4.0, "cB": 3.0, "cD": None},
          "2": {"cA": 3.0, "cB": 4.0, "cD": None}}
    m = ers.per_conformer_margins(sc)
    assert set(m) == {"cA"}                       # cB: no NR4A3 score ; cD: no paralogue score


# ---------------------------------------------------------------------------
# robust_score  (S = min_c M - lam*SD - gamma*max B)
# ---------------------------------------------------------------------------
def test_robust_score_core_objective():
    rs = ers.robust_score(_panel_scores(), lam=1.0, gamma=1.0)
    assert rs["worst_nr4a3"] == 7.0               # min(9,8,7)
    assert math.isclose(rs["mean_nr4a3"], 8.0)
    assert math.isclose(rs["sensitivity"], ers._population_sd([9.0, 8.0, 7.0]))
    assert rs["worst_paralogue"] == 5.0           # max over all paralogue-conformer cells (NR4A1 cC)
    assert rs["worst_paralogue_at"] == ("1", "cC")
    assert rs["min_margin"] == 2.0                # worst per-conformer margin (cC)
    # S = 7.0 - 1.0*sd - 1.0*5.0
    assert math.isclose(rs["S"], 7.0 - ers._population_sd([9.0, 8.0, 7.0]) - 5.0)
    assert rs["sensitivity_assessable"] is True
    assert rs["n_nr4a3"] == 3


def test_robust_score_weights_apply():
    sc = _panel_scores()
    base = ers.robust_score(sc, lam=1.0, gamma=1.0)["S"]
    heavier_sd = ers.robust_score(sc, lam=3.0, gamma=1.0)["S"]
    heavier_par = ers.robust_score(sc, lam=1.0, gamma=2.0)["S"]
    assert heavier_sd < base                       # more SD penalty -> lower S
    assert heavier_par < base                      # more paralogue penalty -> lower S


def test_robust_score_single_conformer_flags_sd_not_assessable():
    sc = {"3": {"cA": 9.0}, "1": {"cA": 4.0}, "2": {"cA": 3.0}}
    rs = ers.robust_score(sc)
    assert rs["sensitivity"] == 0.0                # SD of one value
    assert rs["sensitivity_assessable"] is False   # ...but we FLAG it as untrustworthy
    assert rs["min_margin"] == 5.0


def test_robust_score_missing_paralogue_leaves_S_none():
    sc = {"3": {"cA": 9.0, "cB": 8.0}, "1": {}, "2": {}}
    rs = ers.robust_score(sc)
    assert rs["worst_paralogue"] is None
    assert rs["S"] is None                          # cannot penalise leakage we never measured
    assert rs["min_margin"] is None


def test_robust_score_none_scores_never_coerced_to_zero():
    sc = {"3": {"cA": 9.0, "cB": None}, "1": {"cA": 4.0, "cB": 4.0}, "2": {"cA": 3.0, "cB": 3.0}}
    rs = ers.robust_score(sc)
    assert rs["worst_nr4a3"] == 9.0                 # None dropped, not treated as 0
    assert rs["n_nr4a3"] == 1


# ---------------------------------------------------------------------------
# receptor_vs_conformer  (|receptor effect| > |conformer effect|)
# ---------------------------------------------------------------------------
def test_receptor_dominates_when_selective_and_stable():
    rc = ers.receptor_vs_conformer(_panel_scores())
    # receptor_effect = mean_nr4a3(8) - max(mean NR4A1=4, mean NR4A2=3) = 4.0 ; conformer_effect = sd(9,8,7)~0.816
    assert math.isclose(rc["receptor_effect"], 4.0)
    assert rc["criterion_met"] is True
    assert rc["assessable"] is True


def test_conformer_dominates_flags_geometry_artefact():
    # NR4A3 swings wildly across frames (provenance failure mode); paralogues close on average.
    sc = {"3": {"cA": 12.0, "cB": 2.0}, "1": {"cA": 6.0, "cB": 6.0}, "2": {"cA": 6.0, "cB": 6.0}}
    rc = ers.receptor_vs_conformer(sc)
    # receptor_effect = 7 - 6 = 1 ; conformer_effect = sd(12,2)=5 -> conformer dominates
    assert math.isclose(rc["receptor_effect"], 1.0)
    assert math.isclose(rc["conformer_effect"], 5.0)
    assert rc["criterion_met"] is False


def test_receptor_vs_conformer_not_assessable_with_one_conformer():
    sc = {"3": {"cA": 9.0}, "1": {"cA": 4.0}, "2": {"cA": 3.0}}
    rc = ers.receptor_vs_conformer(sc)
    assert rc["assessable"] is False
    assert rc["criterion_met"] is None


# ---------------------------------------------------------------------------
# panel_split_report  (design / validation / stress)
# ---------------------------------------------------------------------------
def _split_scores():
    return {
        "3": {"d1": 9.0, "d2": 8.5, "v1": 8.0, "v2": 7.5, "s1": 6.0, "s2": 9.5},
        "1": {"d1": 4.0, "d2": 4.0, "v1": 4.5, "v2": 5.0, "s1": 4.0, "s2": 4.0},
        "2": {"d1": 3.0, "d2": 3.5, "v1": 3.0, "v2": 3.5, "s1": 3.0, "s2": 3.0},
    }


ROLES = {"design": ["d1", "d2"], "validation": ["v1", "v2"], "stress": ["s1", "s2"]}


def test_panel_split_generalises_when_favoured_on_held_out():
    rep = ers.panel_split_report(_split_scores(), ROLES)
    assert rep["favoured_all_design"] is True
    assert rep["favoured_all_validation"] is True
    assert rep["generalises"] is True
    assert rep["stress_survives"] is True
    assert "generalises" in rep["rationale"]


def test_panel_split_detects_validation_overfit():
    sc = _split_scores()
    sc["1"]["v1"] = 9.0                             # a paralogue out-binds NR4A3 in a held-out frame
    rep = ers.panel_split_report(sc, ROLES)
    assert rep["favoured_all_design"] is True
    assert rep["favoured_all_validation"] is False  # v1 margin now negative
    assert rep["generalises"] is False
    assert "overfit" in rep["rationale"]


def test_panel_split_stress_reversal_flagged():
    sc = _split_scores()
    sc["2"]["s1"] = 8.0                             # paralogue beats NR4A3 in the occluded stress frame
    rep = ers.panel_split_report(sc, ROLES)
    assert rep["stress_survives"] is False
    assert rep["generalises"] is True              # design+validation still fine; stress is separate


def test_panel_split_no_validation_scored_is_not_generalises():
    sc = _split_scores()
    roles = {"design": ["d1", "d2"], "validation": ["vX"], "stress": []}  # vX unscored
    rep = ers.panel_split_report(sc, roles)
    assert rep["generalises"] is False
    assert rep["stress_survives"] is None
    assert "untested" in rep["rationale"]


# ---------------------------------------------------------------------------
# beats_benchmark  (must win on BOTH worst-case axes)
# ---------------------------------------------------------------------------
def test_beats_benchmark_requires_both_axes():
    bench = _panel_scores()                         # S from earlier test, min_margin 2.0
    better = {"3": {"cA": 10.0, "cB": 9.5, "cC": 9.0},   # tighter + tighter worst case
              "1": {"cA": 4.0, "cB": 3.0, "cC": 4.0},
              "2": {"cA": 3.0, "cB": 4.0, "cC": 2.0}}
    out = ers.beats_benchmark(better, bench)
    assert out["beats_S"] is True
    assert out["beats_min_margin"] is True
    assert out["beats"] is True


def test_single_frame_win_does_not_beat_benchmark():
    bench = _panel_scores()
    # Big score in ONE frame but a paralogue counterexample tanks worst-case margin + S.
    flashy = {"3": {"cA": 20.0, "cB": 8.0, "cC": 7.0},
              "1": {"cA": 4.0, "cB": 3.0, "cC": 9.0},    # NR4A1 out-binds in cC
              "2": {"cA": 3.0, "cB": 4.0, "cC": 2.0}}
    out = ers.beats_benchmark(flashy, bench)
    assert out["beats"] is False                    # worst-case margin/S not improved
    assert "does not beat" in out["rationale"]


def test_beats_benchmark_incomparable_when_S_none():
    bench = {"3": {"cA": 9.0, "cB": 8.0}, "1": {}, "2": {}}   # no paralogue -> S None
    cand = _panel_scores()
    out = ers.beats_benchmark(cand, bench)
    assert out["beats"] is None
    assert "incomparable" in out["rationale"]


# ---------------------------------------------------------------------------
# advancement_verdict
# ---------------------------------------------------------------------------
def test_advancement_pending_when_external_flags_unset():
    v = ers.advancement_verdict(_split_scores(), ROLES)
    # energetic criteria pass, but C7-C10 externals are None -> pending, not advance
    assert v["advance"] is None
    assert "C7_clears_generation_matched_null" in v["pending"]
    assert v["criteria"]["C3_worst_case_selective"] is True
    assert v["criteria"]["C4_receptor_gt_conformer"] is True


def test_advancement_advances_when_all_assessed_pass():
    # Benchmark scored on the SAME 6-conformer panel but uniformly weaker NR4A3 -> candidate beats it.
    bench = _split_scores()
    bench["3"] = {c: v - 2.0 for c, v in bench["3"].items()}
    v = ers.advancement_verdict(
        _split_scores(), ROLES, benchmark_scores=bench,
        protonation_robust=True, stereo_robust=True,
        abfe_direction_consistent=True, clears_generation_matched_null=True)
    assert v["criteria"]["C6_beats_benchmark"] is True
    assert v["advance"] is True
    assert v["unmet"] == []
    assert v["pending"] == []


def test_advancement_holds_on_any_failure():
    v = ers.advancement_verdict(
        _split_scores(), ROLES,
        protonation_robust=False,                   # one hard fail
        stereo_robust=True, abfe_direction_consistent=True,
        clears_generation_matched_null=True)
    assert v["advance"] is False
    assert "C8_protonation_robust" in v["unmet"]


# ---------------------------------------------------------------------------
# rank_candidates
# ---------------------------------------------------------------------------
def test_rank_candidates_orders_by_worst_case_S_and_puts_none_last():
    cands = {
        "strong": {"3": {"cA": 10.0, "cB": 9.5}, "1": {"cA": 3.0, "cB": 3.0}, "2": {"cA": 3.0, "cB": 3.0}},
        "weak":   {"3": {"cA": 7.0, "cB": 6.5}, "1": {"cA": 5.0, "cB": 5.0}, "2": {"cA": 5.0, "cB": 5.0}},
        "nodata": {"3": {"cA": 9.0}, "1": {}, "2": {}},   # S None -> last
    }
    ranked = ers.rank_candidates(cands)
    assert ranked[0]["name"] == "strong"
    assert ranked[1]["name"] == "weak"
    assert ranked[2]["name"] == "nodata"
    assert ranked[2]["S"] is None
    assert [r["rank"] for r in ranked] == [1, 2, 3]
