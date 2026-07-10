"""Unit tests for the PURE logic of nr4a3_8xtt_conformer_scoring (the 8XTT conformer-ensemble endpoint
scoring + per-conformer decoy null).

No smina / openmm / rdkit / biopython / network — favourability, _row_scores, conformer_null_verdict, and
summarize_conformer_scoring are dependency-free (the heavy dock/MM-GBSA glue is validated only in the AWS
job). All ΔG numbers below are CONSTRUCTED scenario INPUTS to the ranking functions, not fabricated results
(mirrors tests/test_8xtt_decoy_null.py, which feeds synthetic margins through the same right-tail machinery).

Sign convention under test: MM-GBSA endpoint ΔG is more-NEGATIVE = more favourable; the module works in
favourability space (= -ΔG, higher = better) so denovo_401 "clears the null" when its ΔG is MORE negative
than the q-th-percentile decoy bar.
"""
import pytest

import nr4a3_8xtt_conformer_scoring as cs


# A decoy null: 10 decoys, ΔG in kcal/mol (more negative = stronger). favourabilities = -ΔG.
DECOY_DGS = [-10.0, -12.0, -15.0, -8.0, -20.0, -11.0, -9.0, -13.0, -14.0, -7.0]
# sorted favourabilities [7,8,9,10,11,12,13,14,15,20]; linear 95th-pct favourability = 17.75 (ΔG bar -17.75)


def _dG_dict(denovo_dG, decoy_dgs=DECOY_DGS):
    d = {cs.LIGAND_LABEL: denovo_dG}
    for i, v in enumerate(decoy_dgs):
        d[f"decoy_{i}"] = v
    return d


# ------------------------------------------------------------------ favourability

def test_favourability_negates_and_passes_none():
    assert cs.favourability(-25.0) == 25.0
    assert cs.favourability(5.0) == -5.0
    assert cs.favourability(None) is None


# ------------------------------------------------------------------ _row_scores (both row shapes)

def test_row_scores_checkpoint_shape_drops_none_decoys():
    row = {"model": 2, "dG": {cs.LIGAND_LABEL: -25.0, "decoy_a": -10.0, "decoy_b": None, "decoy_c": -12.0}}
    denovo, decoys = cs._row_scores(row)
    assert denovo == -25.0
    assert sorted(decoys) == [-12.0, -10.0]          # None dropped, denovo excluded


def test_row_scores_explicit_shape():
    row = {"model": 8, "denovo_dG": -18.0, "decoy_dGs": [-10.0, None, -14.0]}
    denovo, decoys = cs._row_scores(row)
    assert denovo == -18.0
    assert sorted(decoys) == [-14.0, -10.0]


# ------------------------------------------------------------------ conformer_null_verdict

def test_verdict_clears_when_denovo_is_best_binder():
    v = cs.conformer_null_verdict(-25.0, DECOY_DGS, q=95.0)
    assert v["verdict"] == "clears"
    assert v["clears_null"] is True
    assert v["rank"] == 1                            # strongest (most negative ΔG) of denovo + 10 decoys
    assert v["n_ligands_ranked"] == 11
    assert v["percentile_rank"] == 100.0             # more favourable than every decoy
    assert v["decoy_pct_bar_dG"] == pytest.approx(-17.75)
    # add-one p: nothing in the null is at least as favourable -> (0+1)/(10+1)
    assert v["empirical_p_add_one"] == pytest.approx(1.0 / 11.0, abs=1e-4)


def test_verdict_within_null_when_denovo_is_mid_pack():
    v = cs.conformer_null_verdict(-11.0, DECOY_DGS, q=95.0)   # fav 11, bar 17.75
    assert v["verdict"] == "within-null"
    assert v["clears_null"] is False
    # decoys strictly more favourable than 11: {12,15,13,14,20} = 5 -> rank 6
    assert v["rank"] == 6
    assert 0.0 < v["empirical_p_add_one"] <= 1.0


def test_verdict_no_data_on_empty_null():
    v = cs.conformer_null_verdict(-20.0, [], q=95.0)
    assert v["verdict"] == "no-data"
    assert v["n_decoys"] == 0
    assert v["clears_null"] is None
    assert v["rank"] is None


def test_verdict_no_data_on_missing_denovo():
    v = cs.conformer_null_verdict(None, DECOY_DGS, q=95.0)
    assert v["verdict"] == "no-data"
    assert v["percentile_rank"] is None
    assert v["rank"] is None


def test_verdict_reports_decoy_dg_distribution():
    v = cs.conformer_null_verdict(-25.0, DECOY_DGS, q=95.0)
    d = v["decoy_dG_distribution"]
    assert d["n"] == 10
    assert d["min"] == -20.0 and d["max"] == -7.0    # ΔG space (min = strongest decoy)


# ------------------------------------------------------------------ summarize_conformer_scoring

def test_summarize_robust_when_majority_clear():
    # 5 conformers: denovo clears (ΔG -25) in 3, within (ΔG -11) in 2 -> majority -> robust.
    rows = [{"model": m, "dG": _dG_dict(dg)}
            for m, dg in zip([1, 2, 3, 4, 5], [-25.0, -25.0, -25.0, -11.0, -11.0])]
    s = cs.summarize_conformer_scoring(rows, q=95.0)
    assert s["n_conformers_scored"] == 5
    assert s["n_conformers_clear"] == 3
    assert s["frac_conformers_clear"] == pytest.approx(0.6)
    assert s["verdict"] == "robust"
    # rank distribution across conformers: three rank-1, two rank-6
    rd = s["denovo401_rank_distribution"]
    assert rd["n"] == 5 and rd["min"] == 1 and rd["max"] == 6
    assert set(s["per_conformer"].keys()) == {"1", "2", "3", "4", "5"}


def test_summarize_fragile_when_none_clear():
    rows = [{"model": m, "dG": _dG_dict(-11.0)} for m in (1, 2, 3)]
    s = cs.summarize_conformer_scoring(rows, q=95.0)
    assert s["n_conformers_clear"] == 0
    assert s["verdict"] == "fragile"
    assert "does NOT survive" in s["rationale"]


def test_summarize_mixed_when_minority_clear():
    # clears in 2 of 5 -> not a majority -> mixed.
    rows = [{"model": m, "dG": _dG_dict(dg)}
            for m, dg in zip([1, 2, 3, 4, 5], [-25.0, -25.0, -11.0, -11.0, -11.0])]
    s = cs.summarize_conformer_scoring(rows, q=95.0)
    assert s["n_conformers_clear"] == 2
    assert s["verdict"] == "mixed"


def test_summarize_no_data_when_empty():
    s = cs.summarize_conformer_scoring([], q=95.0)
    assert s["verdict"] == "no-data"
    assert s["n_conformers_scored"] == 0


def test_summarize_skips_conformers_without_a_null():
    # a conformer where denovo scored but NO decoy scored is not counted as "scored" (no usable null).
    rows = [
        {"model": 1, "dG": _dG_dict(-25.0)},                         # full null -> clears
        {"model": 2, "dG": {cs.LIGAND_LABEL: -25.0}},                # denovo only, no decoys -> skipped
        {"model": 3, "dG": {cs.LIGAND_LABEL: None, "decoy_0": -10.0}},  # denovo failed -> no-data
    ]
    s = cs.summarize_conformer_scoring(rows, q=95.0)
    assert s["n_conformers_scored"] == 1
    assert s["n_conformers_clear"] == 1
    assert s["per_conformer"]["2"]["verdict"] == "no-data"
    assert s["per_conformer"]["3"]["verdict"] == "no-data"
