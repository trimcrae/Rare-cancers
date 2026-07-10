"""Unit tests for pocket_tracking — the harmonized, score-INDEPENDENT orthosteric-pocket tracking that
replaces the reviewer-flagged 'highest-druggability + >=1-shared-residue' site definition.

The load-bearing properties under test:
  * the fixed reference site is defined WITHOUT any fpocket score;
  * a 1-residue-overlap decoy is REJECTED by the composite gate, a high-recovery cavity ACCEPTED;
  * the centroid clause rejects a residue-overlapping cavity that sits too far away;
  * detection_report gives BOTH denominators correctly on a synthetic set;
  * the sensitivity grid recomputes the match and moves the headline as thresholds vary.
All pure — no fpocket, numpy, biopython, or structures.
"""
import math

import pytest

import pocket_tracking as pt


# --- fixtures: a fixed reference and synthetic candidate cavities -----------------------------------

def _ca_line(residues, base=(0.0, 0.0, 0.0), step=1.0):
    """A CA-coord map {resnum:(x,y,z)} placing residues along x from `base` (Angstrom)."""
    return {r: (base[0] + i * step, base[1], base[2]) for i, r in enumerate(sorted(residues))}


REF_LINING = pt.POCKET5_LINING  # [406,407,410,411,412,481,484,485,531,534]


def _reference_at(centroid):
    """A reference dict with the fixed lining set and a chosen centroid (bypasses coord plumbing)."""
    return {"lining_residues": sorted(REF_LINING), "span_residues": sorted(REF_LINING),
            "centroid": centroid, "n_lining_present": len(REF_LINING),
            "n_lining_expected": len(REF_LINING)}


# --- 1. reference is score-independent --------------------------------------------------------------

def test_orthosteric_reference_ignores_druggability():
    ca = _ca_line(REF_LINING + [999], base=(0.0, 0.0, 0.0))
    ref = pt.orthosteric_reference(ca, lining_residues=REF_LINING, span=(406, 534))
    assert ref["lining_residues"] == sorted(REF_LINING)
    assert ref["n_lining_present"] == 10
    # centroid is purely geometric (no score anywhere in the inputs)
    assert len(ref["centroid"]) == 3
    # span picks up every present residue in 406..534 (all lining residues fall inside)
    assert set(REF_LINING).issubset(set(ref["span_residues"]))


def test_orthosteric_reference_fails_loud_on_numbering_miss():
    ca = _ca_line([10, 20, 30])  # none of the reference residues present
    with pytest.raises(ValueError, match="none of the"):
        pt.orthosteric_reference(ca, lining_residues=REF_LINING)


# --- 2. composite match gate ------------------------------------------------------------------------

def test_one_residue_overlap_decoy_is_rejected():
    """A cavity sharing exactly ONE reference residue (the OLD accept rule) must now be REJECTED:
    frac_recovered = 1/10 = 0.1 < 0.30 and Jaccard = 1/(large) < 0.25."""
    ref = _reference_at((0.0, 0.0, 0.0))
    decoy = {"residues": [406] + list(range(700, 725)),  # 1 shared + 25 unrelated
             "centroid": (1.0, 0.0, 0.0), "druggability": 0.95}  # high score must NOT rescue it
    assert pt.match_pocket([decoy], ref) is None


def test_high_recovery_cavity_is_accepted():
    """A cavity recovering 6/10 reference residues and centered on the site is accepted, regardless of
    its (here modest) druggability."""
    ref = _reference_at((0.0, 0.0, 0.0))
    good = {"residues": [406, 407, 410, 411, 412, 481, 601, 602],  # 6 of 10 recovered
            "centroid": (2.0, 0.0, 0.0), "druggability": 0.42}
    hit = pt.match_pocket([good], ref)
    assert hit is not None
    assert hit["_match"]["n_overlap"] == 6
    assert hit["_match"]["frac_recovered"] == pytest.approx(0.6)


def test_high_jaccard_compact_cavity_accepted_via_or_branch():
    """A compact cavity that recovers only 2/10 (< frac_recovered_min) but has Jaccard >= 0.25 passes
    on the OR branch. 2 shared of a 5-residue cavity: inter=2, union=13, jaccard=2/13=0.154 -> still
    below 0.25, so make it tighter: 3 shared, cavity of 4 -> union=11, jaccard=3/11=0.27 >= 0.25 but
    recovery=0.3 which also passes; use 3 shared with cavity==exactly the 3 to force Jaccard branch."""
    ref = _reference_at((0.0, 0.0, 0.0))
    # cavity = {406,407,410}: inter=3, union=10, jaccard=0.30 (>=0.25); recovery=0.3 (borderline).
    # Tighten frac_recovered_min above 0.3 so ONLY the Jaccard branch can accept it.
    compact = {"residues": [406, 407, 410], "centroid": (0.5, 0.0, 0.0), "druggability": 0.5}
    assert pt.match_pocket([compact], ref, frac_recovered_min=0.99) is not None
    # and a cavity with the same recovery but low Jaccard (padded huge) is rejected when only Jaccard
    # can save it:
    padded = {"residues": [406, 407, 410] + list(range(800, 900)),
              "centroid": (0.5, 0.0, 0.0), "druggability": 0.5}
    assert pt.match_pocket([padded], ref, frac_recovered_min=0.99) is None


def test_centroid_clause_rejects_far_but_overlapping_cavity():
    """Even a 6/10-recovery cavity is rejected if its centroid is beyond CENTROID_MAX_ANG of the
    reference centroid — a different site that happens to share residue NUMBERS."""
    ref = _reference_at((0.0, 0.0, 0.0))
    far = {"residues": [406, 407, 410, 411, 412, 481], "centroid": (50.0, 0.0, 0.0),
           "druggability": 0.9}
    assert pt.match_pocket([far], ref) is None                       # 50 A away
    assert pt.match_pocket([far], ref, centroid_max_ang=100.0) is not None  # loosen -> accepted


def test_centroid_missing_fails_centroid_clause():
    ref = _reference_at((0.0, 0.0, 0.0))
    no_cen = {"residues": [406, 407, 410, 411, 412, 481], "druggability": 0.9}  # no centroid, no map
    assert pt.match_pocket([no_cen], ref) is None


def test_match_pocket_picks_best_by_recovery_not_druggability():
    """With several accepted cavities, the winner is the highest-recovery one — druggability is only a
    final deterministic tiebreak, never an acceptance/selection driver."""
    ref = _reference_at((0.0, 0.0, 0.0))
    weak_high_score = {"residues": [406, 407, 410, 411], "centroid": (1.0, 0.0, 0.0),
                       "druggability": 0.99}                       # recovery 0.4
    strong_low_score = {"residues": [406, 407, 410, 411, 412, 481, 484], "centroid": (1.0, 0.0, 0.0),
                        "druggability": 0.10}                      # recovery 0.7
    hit = pt.match_pocket([weak_high_score, strong_low_score], ref)
    assert hit["druggability"] == 0.10
    assert hit["_match"]["frac_recovered"] == pytest.approx(0.7)


def test_pocket_centroid_from_ca_map():
    ca = {406: (0.0, 0.0, 0.0), 407: (2.0, 0.0, 0.0), 410: (4.0, 0.0, 0.0)}
    assert pt.pocket_centroid([406, 407, 410], ca) == pytest.approx((2.0, 0.0, 0.0))
    assert pt.pocket_centroid([999], ca) is None


def test_match_pocket_computes_centroid_from_ca_map_when_absent():
    ref = _reference_at((0.0, 0.0, 0.0))
    ca = {r: (0.0, 0.0, 0.0) for r in [406, 407, 410, 411, 412, 481]}
    cand = {"residues": [406, 407, 410, 411, 412, 481], "druggability": 0.5}  # no centroid key
    assert pt.match_pocket([cand], ref, ca_by_resnum=ca) is not None


# --- 3. detection report: both denominators ---------------------------------------------------------

def test_detection_report_both_denominators():
    # 10 conformers propagated; a matched cavity detected in 8; 3 of the 8 are >= D*.
    detected = [0.60, 0.55, 0.54, 0.40, 0.30, 0.20, 0.10, 0.05]   # 3 at/above 0.53
    rep = pt.detection_report(detected, d_star=0.53, n_propagated=10)
    assert rep["n_propagated"] == 10
    assert rep["n_detected"] == 8
    assert rep["n_ge_dstar"] == 3
    assert rep["detection_fraction"] == pytest.approx(0.8)
    assert rep["frac_ge_among_detected"] == pytest.approx(3 / 8)
    assert rep["frac_ge_among_propagated"] == pytest.approx(3 / 10)


def test_detection_report_defaults_propagated_to_detected():
    rep = pt.detection_report([0.6, 0.4], d_star=0.53)
    assert rep["n_propagated"] == 2
    assert rep["detection_fraction"] == 1.0


def test_detection_report_rejects_impossible_denominator():
    with pytest.raises(ValueError, match="n_propagated"):
        pt.detection_report([0.6, 0.4, 0.3], d_star=0.53, n_propagated=2)


def test_detection_report_ignores_none_scores():
    rep = pt.detection_report([0.6, None, 0.4], d_star=0.53, n_propagated=5)
    assert rep["n_detected"] == 2
    assert rep["n_ge_dstar"] == 1


# --- 4. sensitivity grid ----------------------------------------------------------------------------

def _frame(residues, druggability, centroid=(1.0, 0.0, 0.0)):
    return {"candidates": [{"residues": residues, "druggability": druggability, "centroid": centroid}],
            "reference": _reference_at((0.0, 0.0, 0.0))}


def test_sensitivity_moves_headline_with_thresholds():
    """Construct frames whose match outcome DEPENDS on frac_recovered_min so the sensitivity table is
    non-constant: a frame recovering exactly 3/10 (0.30) matches at fr<=0.30 but not at fr=0.40/0.50."""
    frames = [
        _frame([406, 407, 410], 0.80),                       # recovery 0.3, druggable
        _frame([406, 407, 410, 411, 412, 481], 0.80),        # recovery 0.6, druggable (always matches)
        _frame([700, 701, 702], 0.80),                       # recovery 0.0 -> never matches
    ]
    grid = [
        {"jaccard_min": 0.99, "frac_recovered_min": 0.30, "centroid_max_ang": 8.0},  # only recovery branch
        {"jaccard_min": 0.99, "frac_recovered_min": 0.40, "centroid_max_ang": 8.0},
    ]
    rows = pt.sensitivity(frames, threshold_grid=grid, d_star=0.53)
    r30, r40 = rows
    # at fr=0.30: frames 1 and 2 match (2 detected); at fr=0.40: only frame 2 matches (1 detected)
    assert r30["n_detected"] == 2
    assert r40["n_detected"] == 1
    assert r30["n_propagated"] == 3 and r40["n_propagated"] == 3
    # headline >= D* among ALL propagated drops from 2/3 to 1/3 as the recovery bar tightens
    assert r30["frac_ge_among_propagated"] == pytest.approx(2 / 3)
    assert r40["frac_ge_among_propagated"] == pytest.approx(1 / 3)


def test_default_threshold_grid_contains_default_point_and_is_deduped():
    grid = pt.default_threshold_grid()
    keys = [(g["jaccard_min"], g["frac_recovered_min"], g["centroid_max_ang"]) for g in grid]
    assert (pt.JACCARD_MIN, pt.FRAC_RECOVERED_MIN, pt.CENTROID_MAX_ANG) in keys
    assert len(keys) == len(set(keys))  # no duplicate grid points


# --- 5. consolidation + version parsing -------------------------------------------------------------

def test_consolidated_table():
    ens = [
        {"ensemble": "af2_static", "detection": pt.detection_report([0.495], n_propagated=1)},
        {"ensemble": "8xtt", "detection": pt.detection_report([0.6, 0.4], n_propagated=20)},
    ]
    tbl = pt.consolidated_table(ens)
    assert tbl["rows"][0]["ensemble"] == "af2_static"
    assert tbl["rows"][1]["n_propagated"] == 20
    assert tbl["rows"][1]["n_detected"] == 2
    assert "detection_fraction" in tbl["columns"]


def test_parse_fpocket_version():
    assert pt.parse_fpocket_version("fpocket 4.2.3\n...") == "4.2.3"
    assert pt.parse_fpocket_version("***** POcket FINDER (fpocket) v4.1 *****") == "4.1"
    assert pt.parse_fpocket_version("no version here") is None


def test_match_mode_default_is_legacy():
    assert pt.match_mode({}) == pt.LEGACY
    assert pt.match_mode({pt.MATCH_MODE_ENV: "harmonized"}) == pt.HARMONIZED
    assert pt.match_mode({pt.MATCH_MODE_ENV: "HARMONIZED"}) == pt.HARMONIZED
    assert pt.match_mode({pt.MATCH_MODE_ENV: "legacy"}) == pt.LEGACY
