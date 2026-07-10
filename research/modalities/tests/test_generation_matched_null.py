"""Tests for generation_matched_null — the generation-matched decoy null (winner's-curse control) logic."""
import math

import generation_matched_null as gmn
import selectivity_calibration as sc


DECOY = sc.DECOY_2026_06_30                       # 95th pct ~13.1, max 16.46


# ---------------------------------------------------------------------------
# scramble_promise / scrambled_denovo_json (control b)
# ---------------------------------------------------------------------------
def _gens():
    return [
        {"name": "denovo_0", "smiles": "C1", "denovo_promise": 0.9, "handle_contacts": 4},
        {"name": "denovo_1", "smiles": "C2", "denovo_promise": 0.5, "handle_contacts": 1},
        {"name": "denovo_2", "smiles": "C3", "denovo_promise": 0.1, "handle_contacts": 0},
        {"name": "denovo_3", "error": "bad", "denovo_promise": None},          # invalid
    ]


def test_scramble_preserves_multiset_and_keeps_invalids_none():
    rows = _gens()
    out = gmn.scramble_promise(rows, seed=1)
    valid_in = sorted(r["denovo_promise"] for r in rows if r["denovo_promise"] is not None)
    valid_out = sorted(r["denovo_promise"] for r in out if r["denovo_promise"] is not None)
    assert valid_in == valid_out                     # same promise values, permuted
    assert out[3]["denovo_promise"] is None          # invalid stays unselectable
    # smiles / other fields untouched (only the promise moves)
    assert [r.get("smiles") for r in out] == [r.get("smiles") for r in rows]


def test_scramble_is_deterministic_and_nonmutating():
    rows = _gens()
    a = gmn.scramble_promise(rows, seed=7)
    b = gmn.scramble_promise(rows, seed=7)
    assert [r["denovo_promise"] for r in a] == [r["denovo_promise"] for r in b]
    assert rows[0]["denovo_promise"] == 0.9          # input not mutated


def test_scramble_actually_reorders_for_some_seed():
    rows = _gens()
    # at least one seed must change the promise ordering of the valid rows (else it is a no-op null)
    orig = [r["denovo_promise"] for r in rows[:3]]
    assert any([r["denovo_promise"] for r in gmn.scramble_promise(rows, seed=s)[:3]] != orig
               for s in range(10))


def test_scrambled_denovo_json_tags_campaign():
    out = gmn.scrambled_denovo_json({"candidates": _gens(), "campaign": "selective"}, seed=3)
    assert out["campaign"] == "genmatched-null-scramble"
    assert out["_genmatched_null"]["control"] == "scrambled-objective"
    assert len(out["candidates"]) == 4


# ---------------------------------------------------------------------------
# is_survivor / survivor_report (the identical bar)
# ---------------------------------------------------------------------------
def test_is_survivor_needs_both_confirmed_and_above_null():
    thr = sc.decoy_threshold(DECOY, 95)              # ~13.12
    # above the null AND confirmed_selective -> survivor
    good = {"label": "x", "mm_min_margin": thr + 2, "verdict": "confirmed_selective"}
    assert gmn.is_survivor(good, DECOY) is True
    # above the null but NOT confirmed (rescued: docking-nonselective) -> not a survivor
    resc = {"label": "y", "mm_min_margin": thr + 2, "verdict": "rescued"}
    assert gmn.is_survivor(resc, DECOY) is False
    # confirmed but BELOW the null -> not a survivor
    below = {"label": "z", "mm_min_margin": 2.0, "verdict": "confirmed_selective"}
    assert gmn.is_survivor(below, DECOY) is False


def test_is_survivor_subtract_sd_bar():
    thr = sc.decoy_threshold(DECOY, 95)
    # margin clears the null but margin-SD does not -> denovo_401 bar rejects it
    row = {"label": "n", "mm_min_margin": thr + 1.0, "mm_min_margin_sd": 3.0,
           "verdict": "confirmed_selective"}
    assert gmn.is_survivor(row, DECOY, subtract_sd=False) is True
    assert gmn.is_survivor(row, DECOY, subtract_sd=True) is False


def test_is_survivor_missing_margin_or_empty_null_fail_closed():
    assert gmn.is_survivor({"label": "a"}, DECOY) is False
    assert gmn.is_survivor({"label": "a", "mm_min_margin": 99}, []) is False


def test_survivor_report_counts_and_best_of_n():
    thr = sc.decoy_threshold(DECOY, 95)
    rows = [
        {"label": "s1", "mm_min_margin": thr + 3, "verdict": "confirmed_selective"},   # survivor
        {"label": "s2", "mm_min_margin": thr + 1, "verdict": "confirmed_selective"},   # survivor
        {"label": "c1", "mm_min_margin": 5.0, "verdict": "confirmed_selective"},       # conf, below null
        {"label": "r1", "mm_min_margin": thr + 5, "verdict": "rescued"},               # above null, not conf
        {"label": "x1", "mm_min_margin": None, "verdict": "incomplete"},
    ]
    rep = gmn.survivor_report(rows, DECOY, n_generated=200)
    assert rep["n_generated"] == 200
    assert rep["n_rescored"] == 5
    assert rep["n_confirmed_selective"] == 3
    assert rep["n_survivors"] == 2
    assert set(rep["survivors"]) == {"s1", "s2"}
    assert rep["best_margin"] == round(thr + 5, 3)   # best-of-N pick is the strongest effective margin
    assert rep["manufactured"] is True


def test_survivor_report_defaults_ngen_to_rescored():
    rep = gmn.survivor_report([{"label": "a", "mm_min_margin": 1.0}], DECOY)
    assert rep["n_generated"] == 1


# ---------------------------------------------------------------------------
# binom_sf / false_positive_rate / compare_campaigns
# ---------------------------------------------------------------------------
def test_binom_sf_edges():
    assert gmn.binom_sf(0, 10, 0.3) == 1.0
    assert gmn.binom_sf(11, 10, 0.3) == 0.0
    assert gmn.binom_sf(1, 10, 0.0) == 0.0
    assert gmn.binom_sf(0, 10, 0.0) == 1.0
    assert gmn.binom_sf(3, 10, 1.0) == 1.0


def test_binom_sf_known_value():
    # P(X>=1) = 1 - (1-p)^n
    p, n = 0.1, 5
    assert math.isclose(gmn.binom_sf(1, n, p), 1 - (1 - p) ** n, rel_tol=1e-9)
    # P(X>=2) for n=4,p=0.5 = 11/16
    assert math.isclose(gmn.binom_sf(2, 4, 0.5), 11 / 16, rel_tol=1e-9)


def test_false_positive_rate_pooling():
    reports = [
        {"n_generated": 100, "n_survivors": 0},
        {"n_generated": 200, "n_survivors": 1},
    ]
    fp = gmn.false_positive_rate(reports)
    assert fp["n_controls"] == 2
    assert fp["n_control_campaigns_with_survivor"] == 1
    assert fp["campaign_manufacture_rate"] == 0.5
    assert fp["pooled_generated"] == 300
    assert fp["pooled_survivors"] == 1
    assert math.isclose(fp["per_molecule_fp_rate"], 1 / 300, abs_tol=1e-6)


def test_compare_campaigns_zero_control_survivors_means_exceeds():
    real = {"n_generated": 200, "n_survivors": 1}
    controls = [{"n_generated": 200, "n_survivors": 0}, {"n_generated": 200, "n_survivors": 0}]
    cmp = gmn.compare_campaigns(real, controls)
    assert cmp["control_fp"]["per_molecule_fp_rate"] == 0.0
    assert cmp["exceeds_chance"] is True
    assert "NEVER manufactured" in cmp["verdict"]


def test_compare_campaigns_within_manufactured_rate_not_excluded():
    # controls manufacture survivors at a high rate; one real survivor in 200 does not beat it.
    real = {"n_generated": 200, "n_survivors": 1}
    controls = [{"n_generated": 50, "n_survivors": 5}, {"n_generated": 50, "n_survivors": 5}]
    cmp = gmn.compare_campaigns(real, controls)
    assert cmp["control_fp"]["per_molecule_fp_rate"] == 0.1
    assert cmp["exceeds_chance"] is False
    assert cmp["p_value"] is not None and cmp["p_value"] > 0.05


def test_compare_campaigns_real_survivors_override():
    real = {"n_generated": 200, "n_survivors": 3}
    controls = [{"n_generated": 200, "n_survivors": 0}]
    cmp = gmn.compare_campaigns(real, controls, real_survivors=1)
    assert cmp["real_n_survivors"] == 1


# ---------------------------------------------------------------------------
# manifest + decoy extraction glue
# ---------------------------------------------------------------------------
def test_build_control_receptor_manifest_shape():
    man = gmn.build_control_receptor_manifest("nr4a1-opened.pdb", [406, 410, 484], "NR4A1", "nr4a1-metad")
    assert man["docking_primary_receptor"] == "nr4a1-opened.pdb"
    assert man["receptors"][0]["box_residues"] == [406, 410, 484]
    assert man["druggable_subensemble"] == ["nr4a1-opened.pdb"]
    assert man["_genmatched_null"]["target"] == "NR4A1"


def test_build_control_receptor_manifest_requires_pdb():
    try:
        gmn.build_control_receptor_manifest("", [1, 2], "x", "y")
    except ValueError:
        return
    raise AssertionError("expected ValueError for empty pdb_name")


def test_decoy_margins_from_mmgbsa():
    mm = {"candidates": [{"label": "d1", "mm_min_margin": 3.0},
                         {"label": "d2", "mm_min_margin": None},
                         {"label": "d3", "mm_min_margin": -1.5}]}
    assert gmn.decoy_margins_from_mmgbsa(mm) == [3.0, -1.5]
