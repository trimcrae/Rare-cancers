"""Tests for denovo_funnel — the pure triage scoring/ranking/summary for de-novo generated candidates.

Proves the composite promise score, the handle-engagement term, the invalid-molecule handling, ranking
order, and the summary aggregation without RDKit/IO (TESTING.md #3).
"""
import denovo_funnel as df


def _prof(qed=0.6, sa=3.0, pains=0, brenk=0, handles_total=1, mw=350.0):
    return {"QED": qed, "SAscore": sa, "PAINS_alerts": ["x"] * pains,
            "BRENK_alert_count": brenk, "protac_handles": {"total": handles_total}, "MW": mw}


def test_score_rewards_handle_contact():
    p = _prof()
    s0 = df.score_molecule(p, handle_contacts=0)
    s5 = df.score_molecule(p, handle_contacts=5)
    assert s5 > s0
    assert round(s5 - s0, 3) == 0.2          # +0.2 * (5/5) for full handle engagement


def test_score_penalises_pains_and_sa():
    clean = df.score_molecule(_prof(pains=0, sa=2.0), handle_contacts=3)
    dirty = df.score_molecule(_prof(pains=3, sa=8.0), handle_contacts=3)
    assert clean > dirty


def test_size_penalty_demotes_fragments():
    # Same chemistry/handles, only MW differs: a fragment (benzoic acid, MW 122) must score below a
    # lead-sized molecule (MW 350) because of the min_mw=250 size floor.
    lead = df.score_molecule(_prof(mw=350.0), handle_contacts=4)
    frag = df.score_molecule(_prof(mw=122.0), handle_contacts=4)
    assert frag < lead
    assert round(lead - frag, 3) == round(0.002 * (250 - 122), 3)   # exactly the size penalty


def test_no_size_penalty_when_mw_missing():
    # MW absent -> no penalty (don't punish an un-profiled molecule)
    p = {"QED": 0.6, "SAscore": 3.0, "PAINS_alerts": [], "BRENK_alert_count": 0,
         "protac_handles": {"total": 1}}
    assert isinstance(df.score_molecule(p, handle_contacts=4), float)


def test_invalid_molecule_scores_none():
    assert df.score_molecule({"error": "unparseable SMILES"}, handle_contacts=5) is None
    assert df.score_molecule(None, 0) is None


def test_missing_sascore_defaults_not_crash():
    s = df.score_molecule({"QED": 0.5, "PAINS_alerts": [], "BRENK_alert_count": 0,
                           "protac_handles": {"total": 0}}, handle_contacts=2)
    assert isinstance(s, float)


def test_developability_gate_demotes_artifacts():
    # Identical good base chemistry + full handle engagement, differing only in a structural-alert
    # liability: the clean one must outrank the artifact by exactly the developability penalty.
    clean = _prof(); clean["structural_liabilities"] = []; clean["aromatic_rings"] = 2
    dirty = _prof(); dirty["structural_liabilities"] = ["peroxide"]; dirty["aromatic_rings"] = 2
    s_clean = df.score_molecule(clean, handle_contacts=5)
    s_dirty = df.score_molecule(dirty, handle_contacts=5)
    assert s_clean > s_dirty
    assert round(s_clean - s_dirty, 3) == df.DEVELOPABILITY_PENALTY


def test_non_aromatic_is_not_developable():
    p = _prof(); p["structural_liabilities"] = []; p["aromatic_rings"] = 0
    assert df.developability(p)["developable"] is False
    assert "no_aromatic_ring" in df.developability(p)["reasons"]


def test_developability_clean_profile():
    p = _prof(sa=3.0); p["structural_liabilities"] = []; p["aromatic_rings"] = 1
    assert df.developability(p)["developable"] is True


def test_summarize_reports_developable():
    rows = [
        {"smiles": "c1ccccc1O", "denovo_promise": 0.5, "QED": 0.6, "SAscore": 3.0, "PAINS_alerts": [],
         "handle_contacts": 4, "structural_liabilities": [], "aromatic_rings": 1},
        {"smiles": "X", "denovo_promise": 0.2, "QED": 0.5, "SAscore": 3.0, "PAINS_alerts": [],
         "handle_contacts": 2, "structural_liabilities": ["peroxide"], "aromatic_rings": 1},
    ]
    s = df.summarize(rows)
    assert s["n_developable"] == 1
    assert s["frac_developable"] == 0.5


def test_rank_orders_by_promise_invalids_last():
    rows = [
        {"id": "a", "denovo_promise": 0.1},
        {"id": "b", "denovo_promise": 0.8},
        {"id": "c", "denovo_promise": None},   # invalid
        {"id": "d", "denovo_promise": 0.5},
    ]
    order = [r["id"] for r in df.rank(rows)]
    assert order[:3] == ["b", "d", "a"]
    assert order[-1] == "c"


def test_summarize_counts_and_diversity():
    rows = [
        {"smiles": "CCO", "denovo_promise": 0.5, "QED": 0.6, "SAscore": 3.0,
         "PAINS_alerts": [], "handle_contacts": 4},
        {"smiles": "CCO", "denovo_promise": 0.5, "QED": 0.6, "SAscore": 3.0,
         "PAINS_alerts": [], "handle_contacts": 4},   # duplicate SMILES
        {"smiles": "c1ccccc1", "denovo_promise": 0.2, "QED": 0.3, "SAscore": 5.0,
         "PAINS_alerts": ["p"], "handle_contacts": 2},
        {"error": "bad", "denovo_promise": None},     # invalid
    ]
    s = df.summarize(rows)
    assert s["n_generated"] == 4
    assert s["n_valid"] == 3
    assert s["n_unique_smiles"] == 2                  # CCO + benzene
    assert s["max_handle_contacts"] == 4
    assert s["frac_contacts_ge_4_handles"] == round(2 / 3, 3)
    assert s["frac_pains_free"] == round(2 / 3, 3)


def test_summarize_empty():
    s = df.summarize([])
    assert s["n_generated"] == 0
    assert s["frac_valid"] is None
    assert s["max_handle_contacts"] is None
