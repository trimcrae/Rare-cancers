"""Tests for denovo_select — the pure de-novo screen selection/ranking logic (no deps)."""
import denovo_select as ds


def _good_profile(**over):
    """A developable warhead profile (passes every gate by default)."""
    p = {"QED": 0.6, "SAscore": 2.5, "MW": 380.0, "PAINS_alerts": [], "BRENK_alert_count": 0,
         "protac_handles": {"amine": 1, "phenol": 0, "carboxylic_acid": 0, "total": 1}}
    p.update(over)
    return p


# --- novelty ----------------------------------------------------------------------------------
def test_novelty_threshold():
    assert ds.is_novel(0.20) is True
    assert ds.is_novel(0.40) is True          # boundary is inclusive (<=)
    assert ds.is_novel(0.55) is False
    assert ds.is_novel(None) is False         # uncomputable -> conservatively not novel


# --- developability ----------------------------------------------------------------------------
def test_developable_pass():
    ok, reasons = ds.is_developable(_good_profile())
    assert ok is True and reasons == []


def test_developable_rejects_pains_and_unsynthesizable():
    ok, reasons = ds.is_developable(_good_profile(PAINS_alerts=["mannich_A"], SAscore=5.2))
    assert ok is False
    assert "PAINS" in reasons and "SAscore>4.5" in reasons


def test_developable_requires_a_handle():
    p = _good_profile(protac_handles={"amine": 0, "phenol": 0, "carboxylic_acid": 0, "total": 0})
    ok, reasons = ds.is_developable(p)
    assert ok is False and "no_PROTAC_handle" in reasons


def test_developable_missing_profile():
    ok, reasons = ds.is_developable(None)
    assert ok is False and reasons == ["unprofilable"]


# --- row building (the fused screen verdict) ---------------------------------------------------
def test_selective_passer_row():
    gen = {"label": "denovo-sel-001", "smiles": "CCO", "campaign": "selective"}
    # NR4A3 strongly engaged, paralogues weak -> nr4a3_selective; developable; novel; has handle
    row = ds.build_row(gen, dg3=-9.0, dg1=-5.0, dg2=-5.0, profile=_good_profile(),
                       max_tanimoto=0.2, handle_contacts=4)
    assert row["nr4a3_selective"] is True
    assert row["novel"] is True and row["developable"] is True
    assert row["passes_screen"] is True


def test_not_novel_fails_screen_even_if_selective():
    gen = {"label": "denovo-sel-002", "smiles": "CCO", "campaign": "selective"}
    row = ds.build_row(gen, dg3=-9.0, dg1=-5.0, dg2=-5.0, profile=_good_profile(),
                       max_tanimoto=0.9)              # too similar to a known active
    assert row["nr4a3_selective"] is True
    assert row["novel"] is False
    assert row["passes_screen"] is False


def test_pan_campaign_uses_pan_selectivity():
    gen = {"label": "denovo-pan-001", "smiles": "CCO", "campaign": "pan"}
    # engages all three within margin -> pan_nr4a; for a pan campaign that is the pass condition
    row = ds.build_row(gen, dg3=-9.0, dg1=-8.6, dg2=-8.7, profile=_good_profile(), max_tanimoto=0.1)
    assert row["pan_nr4a"] is True
    assert row["passes_screen"] is True


def test_undevelopable_fails_screen():
    gen = {"label": "denovo-sel-003", "smiles": "CCO", "campaign": "selective"}
    row = ds.build_row(gen, dg3=-9.0, dg1=-5.0, dg2=-5.0,
                       profile=_good_profile(SAscore=6.0), max_tanimoto=0.1)
    assert row["nr4a3_selective"] is True
    assert row["developable"] is False
    assert row["passes_screen"] is False


# --- candidate verdict (needs MM-GBSA confirmation) --------------------------------------------
def test_is_candidate_requires_mmgbsa_confirmation():
    gen = {"label": "denovo-sel-001", "smiles": "CCO", "campaign": "selective"}
    row = ds.build_row(gen, dg3=-9.0, dg1=-5.0, dg2=-5.0, profile=_good_profile(), max_tanimoto=0.2)
    assert ds.is_candidate(row, mmgbsa_verdict=None) is False         # CPU screen alone is not enough
    assert ds.is_candidate(row, mmgbsa_verdict="reversed") is False
    assert ds.is_candidate(row, mmgbsa_verdict="confirmed_selective") is True


# --- ranking + summary -------------------------------------------------------------------------
def test_rank_puts_screen_passers_first():
    g = lambda n, c="selective": {"label": n, "smiles": "CCO", "campaign": c}  # noqa: E731
    passer = ds.build_row(g("p"), -9.0, -5.0, -5.0, _good_profile(), 0.1, handle_contacts=5)
    flunk = ds.build_row(g("f"), -6.0, -6.0, -6.0, _good_profile(), 0.1)
    ranked = ds.rank([flunk, passer])
    assert ranked[0]["label"] == "p"        # the screen-passer sorts ahead


def test_summarize_counts_and_shortlists():
    g = lambda n, c="selective": {"label": n, "smiles": "CCO", "campaign": c}  # noqa: E731
    rows = [
        ds.build_row(g("sel"), -9.0, -5.0, -5.0, _good_profile(), 0.1, handle_contacts=4),
        ds.build_row(g("pan", "pan"), -9.0, -8.6, -8.7, _good_profile(), 0.1),
        ds.build_row(g("dud"), -5.0, -5.0, -5.0, _good_profile(), 0.1),
    ]
    s = ds.summarize(rows)
    assert s["n_generated"] == 3
    assert len(s["selective_passers"]) == 1
    assert len(s["pan_passers"]) == 1
    assert s["n_novel"] == 3
