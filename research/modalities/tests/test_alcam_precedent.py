"""Offline tests for the ALCAM / CD166 precedent record.

⛔ THIS ANTIGEN IS THE ONE POSITIVE ON THE BOARD, WHICH IS EXACTLY WHY IT IS THE MOST DANGEROUS
RECORD IN THE REPOSITORY TO GET WRONG. Four routes are blocked on "a selective surface antigen",
and a record that says "up on both platforms, RESTRICTED normal window, clinical binder exists"
reads like a green light. Three things must therefore be impossible to drop:

  1. **The normal-tissue liability.** HPA returned RESTRICTED; the primary literature puts ALCAM on
     mesenchymal stem cells, in the haematopoietic stem-cell niche, on perichondrium and on the
     CD6 axis of T cells. A bulk RNA atlas cannot see a rare compartment, so the two are not in
     conflict — and that is precisely why the RESTRICTED label must never travel alone.
  2. **The lineage confound.** ALCAM is a mesenchymal-lineage marker and EMC is a mesenchymal
     tumour measured against other sarcomas, so the elevation may be about lineage rather than
     about EWSR1::NR4A3. Nothing measured discriminates them.
  3. **The trial's outcome staying uncharacterised.** The record says a phase I/II trial reached
     patients. It must not drift into saying anything about whether the agent worked.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alcam_precedent as M  # noqa: E402
import cd248_precedent as CD248  # noqa: E402

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def res():
    return M.derive()


# ---------------------------------------------------------------------------------------------
# 1 — THE LIABILITY CANNOT BE DROPPED, AND RESTRICTED CANNOT TRAVEL ALONE
# ---------------------------------------------------------------------------------------------
def test_every_named_normal_tissue_liability_is_present_with_a_citation(res):
    lia = res["normal_tissue_liability"]
    for key in ("hematopoietic_stem_cells_and_the_niche",
                "mesenchymal_stem_cells_and_perichondrium",
                "T_cell_costimulation_via_CD6",
                "dendritic_cell_migration",
                "early_cardiomyocytes"):
        assert key in lia, key
        assert lia[key].get("pmid"), key


def test_the_RESTRICTED_window_is_explicitly_refused_as_a_safety_statement(res):
    why = res["normal_tissue_liability"]["_why_this_does_not_contradict_the_RESTRICTED_window"]
    assert "not be quoted as a safety statement" in why
    assert "rare" in why.lower() and "bulk" in why.lower()
    # and the module header must carry the same refusal, because that is what a reader meets first
    assert "MUST NEVER" in M.__doc__ and "SAFETY STATEMENT" in M.__doc__.upper()


def test_the_T_cell_hazard_is_tied_to_the_modality_it_actually_threatens(res):
    t = res["normal_tissue_liability"]["T_cell_costimulation_via_CD6"]
    hazard = t["⛔_why_it_matters_for_a_T_CELL_modality_specifically"]
    assert "CD6" in hazard and "fratricide" in hazard
    # naming a better-posed modality must not become an efficacy claim about it
    assert "NOT a claim that either works" in hazard


# ---------------------------------------------------------------------------------------------
# 2 — THE LINEAGE CONFOUND IS THE HEADLINE QUALIFICATION AND MUST BE STATED AS SUCH
# ---------------------------------------------------------------------------------------------
def test_the_mesenchymal_lineage_confound_is_recorded_as_the_top_qualification(res):
    msc = res["normal_tissue_liability"]["mesenchymal_stem_cells_and_perichondrium"]
    note = msc["⛔_why_it_matters_TWICE"]
    assert "mesenchymal" in note.lower()
    assert "OTHER SARCOMAS" in note
    assert "single most important qualification" in note
    # and it is repeated where a consumer reading only the unknowns would see it
    unknowns = " ".join(res["⛔_the_three_things_that_would_have_to_be_true_and_are_not_known"])
    assert "MESENCHYMAL LINEAGE" in unknowns


def test_the_surface_localisation_gap_is_named_with_the_field_that_shows_it(res):
    unknowns = " ".join(res["⛔_the_three_things_that_would_have_to_be_true_and_are_not_known"])
    assert "plasma_membrane_confirmed false" in unknowns or "Vesicles" in unknowns
    assert "emc-surface-normal-window.json" in unknowns


# ---------------------------------------------------------------------------------------------
# 3 — THE TRIAL EXISTS; ITS OUTCOME IS NOT CHARACTERISED
# ---------------------------------------------------------------------------------------------
def test_the_clinical_trial_is_recorded_without_any_outcome_claim(res):
    r = res["binder_precedent"]["clinical_adc_praluzatamab_ravtansine"]
    assert r["pmid"] == "35165101" and r["pmcid"] == "PMC9365353"
    assert "no efficacy claim" in " ".join(r).lower() or any(
        "no_efficacy_claim" in k for k in r)
    blob = json.dumps(res).lower()
    for forbidden in ("responded", "response rate", "objective response", "showed activity",
                      "was effective", "efficacious"):
        assert forbidden not in blob, forbidden


def test_the_ladder_never_calls_anything_clinical_in_EMC(res):
    lad = res["modality_ladder"]
    assert lad["anything_at_all_in_EMC"].startswith("NONE")
    assert lad["car_t"].startswith("PRECLINICAL")
    assert lad["immuno_PET"].startswith("PRECLINICAL")
    assert "No outcome is characterised" in lad["antibody_drug_conjugate"]


def test_the_probody_masking_is_read_as_evidence_of_the_liability_not_as_reassurance(res):
    r = res["binder_precedent"]["clinical_adc_praluzatamab_ravtansine"]
    assert "masked" in r["format"].lower()
    assert "normal-tissue distribution" in r["format"]
    corrob = res["normal_tissue_liability"][
        "⭐_the_independent_corroboration_that_this_is_a_real_problem"]
    assert "obstacle" in corrob


# ---------------------------------------------------------------------------------------------
# 4 — THE COUNT, ITS DENOMINATOR, AND THE UNREAD CASE
# ---------------------------------------------------------------------------------------------
def test_the_EMC_count_uses_the_on_topic_denominator_not_the_raw_retrieval(monkeypatch):
    """⛔ A BROAD QUERY MAKES THE RAW DENOMINATOR MEANINGLESS. 'CD166', 'antibody' and 'sarcoma'
    co-occur in papers that never mention this antigen, so '0 of 6,547' would be a much weaker
    statement than it looks. The on-topic subset is what the gap claim rests on."""
    rows = [{"title": "ALCAM in extraskeletal myxoid chondrosarcoma", "abstract": "",
             "pmid": "1", "pmcid": None, "year": 2026},
            {"title": "ALCAM in colorectal cancer", "abstract": "", "pmid": "2"},
            {"title": "Something about sarcoma antibodies", "abstract": "no antigen here",
             "pmid": "3"}]
    monkeypatch.setattr(CD248, "_corpus_index", lambda d=None: (rows, None))
    e = M.emc_specific_evidence()
    assert e["n_records_retrieved"] == 3
    assert e["n_records_actually_about_the_antigen"] == 2, "the off-topic row must not count"
    assert e["n_on_topic_records_mentioning_EMC"] == 1
    assert "Records naming EMC ARE present" in e["verdict"] or "ARE present" in e["verdict"]


def test_an_unreadable_corpus_reports_UNREAD_and_claims_no_count(monkeypatch):
    monkeypatch.setattr(CD248, "_corpus_index", lambda d=None: (None, "⛔ CORPUS UNREAD — test"))
    e = M.emc_specific_evidence()
    assert e["_status"] == "UNREAD"
    assert "n_on_topic_records_mentioning_EMC" not in e
    assert "not a reading of absence" in e["⛔_meaning"]


def test_the_corpus_reader_has_one_home(monkeypatch):
    """⛔ MOCK THE THING UNDER TEST AND YOU TEST THE MOCK (CLAUDE.md §6). This module must call
    the fail-honest reader in cd248_precedent rather than carrying a second copy, so patching
    that one function must be sufficient to control this module's count."""
    called = {}

    def fake(corpus_dir=None):
        called["dir"] = corpus_dir
        return [], None

    monkeypatch.setattr(CD248, "_corpus_index", fake)
    M.emc_specific_evidence()
    assert called["dir"] == M.CORPUS_DIR, "the corpus directory must be passed through, not fixed"


# ---------------------------------------------------------------------------------------------
# 5 — CITATION HYGIENE, SHARED WITH THE CD248 RECORD
# ---------------------------------------------------------------------------------------------
def test_every_cited_record_carries_a_pmid_and_a_verification_tag(res):
    n = 0
    for rec in _leaf_records(res["binder_precedent"]):
        n += 1
        assert rec.get("pmid"), f"no PMID: {rec.get('title')!r}"
        assert rec.get("verification") in ("[FT]", "[API]"), rec.get("title")
    assert n >= 6, f"only {n} citations — the binder record has thinned out"


def test_a_full_text_tag_is_only_used_where_a_pmcid_exists(res):
    for rec in _leaf_records(res):
        if rec.get("verification") == "[FT]":
            assert rec.get("pmcid"), rec.get("title")


def _leaf_records(obj):
    if isinstance(obj, dict):
        if "title" in obj and "verification" in obj:
            yield obj
        for v in obj.values():
            yield from _leaf_records(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _leaf_records(v)


def test_the_emc_figures_are_pointed_at_not_copied(res):
    """The SD/t/percentile numbers have one home in emc-expression-panels.json."""
    assert "emc-expression-panels.json" in res["the_emc_reading_this_rests_on"]["artifact"]
    blob = json.dumps(res)
    for figure in ("7.008", "1.0907", "2.214", "0.7535"):
        assert figure not in blob, f"{figure} belongs to the panel artifact; point at it"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
